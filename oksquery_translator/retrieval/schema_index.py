"""
retrieval/schema_index.py — Module 4: Fingerprint-Scoped Schema Search Index
=============================================================================

Implements version-isolated schema indexing and retrieval keyed strictly by
schema_fingerprint (conforming to Section 19 & 20 of Architecture Specification).

Key Invariants:
  1. All indexed documents are partition-isolated by schema_fingerprint.
  2. Cross-version schema search is strictly forbidden.
  3. Index construction is idempotent per unique schema_fingerprint.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from ..schema.oks_schema_provider import OksSchemaProvider

logger = logging.getLogger("oksquery_translator.retrieval.index")


@dataclass
class ClassSearchDocument:
    """
    Search document representation for an OKS class in a versioned schema context.
    Conforms to Architecture Specification Section 19 (Listing 4).
    """
    schema_fingerprint: str
    class_name: str
    tokens: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    relationship_targets: List[str] = field(default_factory=list)
    description: str = ""
    git_revision: str = ""


class SchemaSearchIndex:
    """
    In-memory schema search index partitioned strictly by schema_fingerprint.
    """

    def __init__(self):
        # Maps schema_fingerprint -> list of ClassSearchDocument
        self._index: Dict[str, List[ClassSearchDocument]] = {}

    def has_fingerprint(self, schema_fingerprint: str) -> bool:
        """Check if a schema fingerprint is already indexed."""
        return bool(schema_fingerprint and schema_fingerprint in self._index)

    def build_from_schema_provider(self, schema_provider: OksSchemaProvider) -> str:
        """
        Build and cache the index for the schema provider's bound OksContext.
        Idempotent: skips building if already indexed.

        Parameters
        ----------
        schema_provider : OksSchemaProvider
            Context-bound schema access provider.

        Returns
        -------
        str
            The schema_fingerprint that was indexed.
        """
        fingerprint = schema_provider.oks_context.schema_fingerprint or "0000000000000000"

        if fingerprint in self._index:
            logger.debug(f"Schema index already exists for fingerprint '{fingerprint}'. Reusing.")
            return fingerprint

        class_names = schema_provider.get_all_class_names()
        git_rev = schema_provider.oks_context.git_revision or ""
        documents: List[ClassSearchDocument] = []

        for name in class_names:
            cls_def = schema_provider.get_effective_members(name)
            if cls_def is None:
                cls_def = schema_provider.get_class(name)

            tokens = self._tokenize_class(name, cls_def.description if cls_def else "")
            attrs = cls_def.attribute_names() if cls_def else []
            rels = cls_def.relationship_names() if cls_def else []
            rel_targets = [
                r.target_class for r in (cls_def.relationships if cls_def else [])
                if r.target_class
            ]

            doc = ClassSearchDocument(
                schema_fingerprint=fingerprint,
                class_name=name,
                tokens=tokens,
                attributes=attrs,
                relationships=rels,
                relationship_targets=rel_targets,
                description=cls_def.description if cls_def else "",
                git_revision=git_rev,
            )
            documents.append(doc)

        self._index[fingerprint] = documents
        logger.info(
            f"SchemaSearchIndex: Indexed fingerprint '{fingerprint}' "
            f"({len(documents)} classes)."
        )
        return fingerprint

    def search(self, query: str, schema_fingerprint: str, top_k: int = 5) -> List[ClassSearchDocument]:
        """
        Search for relevant OKS classes strictly within the given schema_fingerprint partition.

        Parameters
        ----------
        query : str
            Search query tokens or natural language phrase.
        schema_fingerprint : str
            Authoritative fingerprint isolating the schema scope.
        top_k : int
            Number of top candidates to return.

        Returns
        -------
        list of ClassSearchDocument
            Ranked candidates matching the query.
        """
        if not schema_fingerprint or schema_fingerprint not in self._index:
            logger.warning(
                f"Search requested for unindexed schema_fingerprint '{schema_fingerprint}'. "
                f"Returning empty results to prevent cross-version pollution."
            )
            return []

        partition_docs = self._index[schema_fingerprint]
        if not partition_docs or not query:
            return []

        query_tokens = [
            t.lower() for t in re.findall(r"[a-zA-Z0-9_]+", query)
            if len(t) >= 2
        ]
        if not query_tokens:
            return partition_docs[:top_k]

        scored_docs: List[tuple[float, ClassSearchDocument]] = []

        for doc in partition_docs:
            score = self._score_document(doc, query_tokens, query.strip().lower())
            if score > 0.0:
                scored_docs.append((score, doc))

        # Sort descending by score
        scored_docs.sort(key=lambda item: item[0], reverse=True)
        results = [doc for score, doc in scored_docs[:top_k]]
        match_summary = [f"{item[1].class_name} (score={item[0]:.1f})" for item in scored_docs[:top_k]]
        logger.info(
            f"SchemaSearchIndex: query={query!r}, fingerprint={schema_fingerprint!r} → "
            f"Top matches: [{', '.join(match_summary)}]"
        )
        return results

    def get_document(self, class_name: str, schema_fingerprint: str) -> Optional[ClassSearchDocument]:
        """Lookup a specific document by class name and fingerprint."""
        if not schema_fingerprint or schema_fingerprint not in self._index:
            return None
        for doc in self._index[schema_fingerprint]:
            if doc.class_name.lower() == class_name.lower():
                return doc
        return None

    # ------------------------------------------------------------------
    # Scoring & Tokenization helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenize_class(class_name: str, description: str) -> List[str]:
        """Split CamelCase words, snake_case, and extract lowercase keywords."""
        tokens: Set[str] = set()

        # 1. CamelCase splitting (e.g. "RunControlApplication" -> "Run", "Control", "Application")
        camel_parts = re.findall(r'[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z][a-z]|\b)', class_name)
        for part in camel_parts:
            if len(part) >= 2:
                tokens.add(part.lower())

        # 2. Entire class name lowercased
        tokens.add(class_name.lower())

        # 3. Description words
        if description:
            desc_words = re.findall(r'[a-zA-Z0-9_]+', description)
            for w in desc_words:
                if len(w) >= 3:
                    tokens.add(w.lower())

        return list(tokens)

    @staticmethod
    def _score_document(doc: ClassSearchDocument, query_tokens: List[str], query_lower: str) -> float:
        """
        Score relevance:
          - Exact class name match: +10.0
          - Token match in class name tokens: +5.0
          - Exact attribute / relationship name match: +3.0
          - Partial / description match: +1.0
        """
        score = 0.0
        cls_lower = doc.class_name.lower()

        # Exact class name match
        if cls_lower == query_lower or cls_lower in query_tokens:
            score += 10.0

        # Token match in class name
        for q in query_tokens:
            if q in doc.tokens:
                score += 5.0
            elif any(q in t for t in doc.tokens):
                score += 2.0

        # Attribute / relationship matches
        attr_lowers = {a.lower(): a for a in doc.attributes}
        rel_lowers = {r.lower(): r for r in doc.relationships}

        for q in query_tokens:
            if q in attr_lowers:
                score += 3.0
            if q in rel_lowers:
                score += 3.0

        # Description matches
        if doc.description:
            desc_lower = doc.description.lower()
            for q in query_tokens:
                if q in desc_lower:
                    score += 1.0

        return score
