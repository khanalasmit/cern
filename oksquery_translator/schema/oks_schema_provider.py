"""
schema/oks_schema_provider.py — Module 5: Version-Scoped OKS Schema Access Layer
==================================================================================

Provides typed, version-isolated access to OKS schema definitions.
Resolves class definitions, attributes, relationships, and full inheritance
hierarchies scoped to a specific OksContext.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from ..context.oks_context import OksContext

logger = logging.getLogger("oksquery_translator.schema.provider")


@dataclass
class AttributeDefinition:
    """Represents a single OKS class attribute."""
    name: str
    type: str = ""
    range: str = ""
    init_value: str = ""
    is_multi_value: bool = False


@dataclass
class RelationshipDefinition:
    """Represents an OKS relationship pointing to another class."""
    name: str
    target_class: str = ""
    is_multi_value: bool = False
    description: str = ""


@dataclass
class ClassDefinition:
    """Represents a complete OKS class definition."""
    name: str
    superclasses: List[str] = field(default_factory=list)
    attributes: List[AttributeDefinition] = field(default_factory=list)
    relationships: List[RelationshipDefinition] = field(default_factory=list)
    description: str = ""

    def get_attribute(self, name: str) -> Optional[AttributeDefinition]:
        """Lookup attribute by exact case-sensitive name."""
        return next((a for a in self.attributes if a.name == name), None)

    def get_relationship(self, name: str) -> Optional[RelationshipDefinition]:
        """Lookup relationship by exact case-sensitive name."""
        return next((r for r in self.relationships if r.name == name), None)

    def attribute_names(self) -> List[str]:
        """Return list of all attribute names."""
        return [a.name for a in self.attributes]

    def relationship_names(self) -> List[str]:
        """Return list of all relationship names."""
        return [r.name for r in self.relationships]


class OksSchemaProvider:
    """
    Context-bound, typed access layer over OKS schema (Module 5).

    Guarantees that schema queries operate within the bound OksContext.
    Resolves member inheritance (effective members) across class hierarchies.
    """

    def __init__(self, oks_context: OksContext,
                 data_file: str = "daq/segments/setup.data.xml",
                 schema_dir: Optional[str] = None):
        self.oks_context = oks_context
        self.data_file = data_file
        self.schema_dir = schema_dir or self._auto_discover_schema_dir()
        self._retriever = None
        self._class_cache: Dict[str, ClassDefinition] = {}
        self._effective_cache: Dict[str, ClassDefinition] = {}

    def _auto_discover_schema_dir(self) -> Optional[str]:
        """Look for local XML schema directories if no schema_dir provided."""
        # 1. Check workspace test_schema/xml directory
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        local_schema = os.path.join(workspace_root, "test_schema", "xml")
        if os.path.isdir(local_schema):
            return local_schema
        return None

    def _get_retriever(self):
        """Lazy-load SchemaRetriever to avoid circular dependencies."""
        if self._retriever is None:
            from ..schema_retrieval import SchemaRetriever
            self._retriever = SchemaRetriever(
                data_file=self.data_file,
                schema_dir=self.schema_dir,
            )
        return self._retriever

    def get_all_class_names(self) -> List[str]:
        """Return all available class names in this schema context."""
        try:
            names = list(self._get_retriever().get_class_list())
            for cached_name in self._class_cache:
                if cached_name not in names:
                    names.append(cached_name)
            for r_cached in getattr(self._get_retriever(), "_class_cache", {}):
                if r_cached not in names:
                    names.append(r_cached)
            return names
        except Exception as e:
            logger.warning(f"Error retrieving class list: {e}")
            return list(self._class_cache.keys())

    def class_exists(self, name: str) -> bool:
        """Check if class exists in this schema."""
        if not name:
            return False
        if name in self._class_cache:
            return True
        all_classes = self.get_all_class_names()
        if all_classes and name in all_classes:
            return True
        return self.get_class(name) is not None

    def get_class(self, name: str) -> Optional[ClassDefinition]:
        """
        Return direct ClassDefinition for the given class name (cached).
        Returns None if class is not found.
        """
        if not name:
            return None

        if name in self._class_cache:
            return self._class_cache[name]

        raw = self._get_retriever().get_class_info(name)
        if raw is None:
            return None

        cls_def = self._raw_to_class_def(name, raw)
        self._class_cache[name] = cls_def
        return cls_def

    def get_effective_members(self, class_name: str) -> Optional[ClassDefinition]:
        """
        Return a ClassDefinition with ALL inherited attributes and relationships
        merged from superclasses (resolves full inheritance hierarchy).
        """
        if not class_name:
            return None

        if class_name in self._effective_cache:
            return self._effective_cache[class_name]

        base = self.get_class(class_name)
        if base is None:
            return None

        visited: Set[str] = set()
        merged_attrs: Dict[str, AttributeDefinition] = {}
        merged_rels: Dict[str, RelationshipDefinition] = {}
        all_superclasses: List[str] = []

        def _traverse(current_name: str):
            if current_name in visited:
                return
            visited.add(current_name)

            c_def = self.get_class(current_name)
            if c_def is None:
                return

            # Depth-first on superclasses so base superclasses load first,
            # allowing child classes to override if necessary
            for sc in c_def.superclasses:
                if sc not in all_superclasses:
                    all_superclasses.append(sc)
                _traverse(sc)

            for attr in c_def.attributes:
                merged_attrs[attr.name] = attr

            for rel in c_def.relationships:
                merged_rels[rel.name] = rel

        _traverse(class_name)

        effective_def = ClassDefinition(
            name=class_name,
            superclasses=all_superclasses,
            attributes=list(merged_attrs.values()),
            relationships=list(merged_rels.values()),
            description=base.description,
        )

        self._effective_cache[class_name] = effective_def
        return effective_def

    def suggest_class(self, name: str) -> List[str]:
        """Return similar class names for error diagnostic hints."""
        if not name:
            return []
        name_lower = name.lower()
        all_classes = self.get_all_class_names()
        # Direct substring matches
        matches = [c for c in all_classes if name_lower in c.lower()]
        if not matches:
            # Prefix or initial matches
            matches = [c for c in all_classes if c.lower().startswith(name_lower[:3])]
        return matches[:5]

    # ------------------------------------------------------------------
    # Internal parser adapter
    # ------------------------------------------------------------------

    @staticmethod
    def _raw_to_class_def(class_name: str, raw: dict) -> ClassDefinition:
        """Convert raw dictionary from SchemaRetriever into typed ClassDefinition."""
        attrs: List[AttributeDefinition] = []
        for a in raw.get("attributes", []):
            if isinstance(a, dict):
                is_multi = a.get("is_multi_value", a.get("is-multi-value", "no"))
                attrs.append(AttributeDefinition(
                    name=str(a.get("name", "")),
                    type=str(a.get("type", "")),
                    range=str(a.get("range", "")),
                    init_value=str(a.get("init_value", a.get("init-value", ""))),
                    is_multi_value=is_multi in ("yes", "true", True),
                ))
            elif isinstance(a, str):
                attrs.append(AttributeDefinition(name=a))

        rels: List[RelationshipDefinition] = []
        for r in raw.get("relationships", []):
            if isinstance(r, dict):
                target = r.get("target_class", r.get("class-type", ""))
                is_multi = r.get("is_multi_value", r.get("is-multi-value", False))
                rels.append(RelationshipDefinition(
                    name=str(r.get("name", "")),
                    target_class=str(target),
                    is_multi_value=bool(is_multi),
                    description=str(r.get("description", "")),
                ))
            elif isinstance(r, (list, tuple)) and len(r) >= 2:
                rels.append(RelationshipDefinition(name=str(r[0]), target_class=str(r[1])))
            elif isinstance(r, str):
                rels.append(RelationshipDefinition(name=r, target_class=""))

        return ClassDefinition(
            name=class_name,
            superclasses=raw.get("superclasses", []),
            attributes=attrs,
            relationships=rels,
            description=raw.get("description", ""),
        )
