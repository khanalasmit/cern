"""
Minimal in-process model of an OKS repository: schema (classes / attributes /
relationships / inheritance) plus data (objects, attribute values, references),
and a reference implementation of the OksQuery evaluator.

This module exists so that the evaluation dataset can be *machine-checked*
without a compiled OKS installation:

  * every gold query is validated against the real schema (no invented class,
    attribute or relationship names), and
  * every gold query is executed against the real test data so the dataset can
    carry the expected result set -- which is what the project specification
    asks for ("M3's accuracy is measured by executing the generated query and
    comparing results to the ground-truth query's results, not by comparing
    query text").

Semantics implemented here follow ``src/query.cpp`` /
``OksObject::SatisfiesQueryExpression`` as documented in
``docs/OKS_Grammar_Query_CppAPI_Reference.pdf``.  Where the documentation is
silent, the choice is recorded in ``SEMANTIC_NOTES`` below and mirrored in the
dataset README, so results stay reproducible and auditable.
"""

from __future__ import annotations

import glob
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SEMANTIC_NOTES = {
    "multi_value_attribute": (
        "A comparison against a multi-value attribute succeeds when at least "
        "one element satisfies the comparator."
    ),
    "missing_attribute": (
        "An object that does not store a value for an attribute is evaluated "
        "against the schema init-value, which is what OKS materialises."
    ),
    "relationship_all_on_empty": (
        "('rel' all <expr>) is treated as false when the relationship holds no "
        "reference, so 'every referenced object matches' is never satisfied "
        "vacuously. Verify against oks_dump before relying on this edge case."
    ),
    "unresolved_reference": (
        "A reference pointing at an object that is not present in the loaded "
        "data files does not satisfy the nested expression."
    ),
    "regex": (
        "'~=' uses boost::regex_match in OKS, i.e. the pattern must match the "
        "whole value; re.fullmatch is used here."
    ),
    "empty_numeric": (
        "An empty or unparseable value on a numeric attribute is read as 0, "
        "which is the typed default OksData materialises; likewise an empty "
        "value on a bool attribute is read as false."
    ),
}

NUMERIC_TYPES = {
    "s8", "u8", "s16", "u16", "s32", "u32", "s64", "u64", "float", "double",
}
BOOL_TRUE = {"1", "true", "yes", "on"}
BOOL_FALSE = {"0", "false", "no", "off"}


# --------------------------------------------------------------------------
# Schema model
# --------------------------------------------------------------------------
@dataclass
class Attribute:
    name: str
    type: str = "string"
    description: str = ""
    range: str = ""
    format: str = "dec"
    is_multi_value: bool = False
    init_value: str = ""
    is_not_null: bool = False
    ordered: bool = False
    owner: str = ""

    @classmethod
    def from_xml(cls, el: ET.Element, owner: str) -> "Attribute":
        return cls(
            name=el.get("name", ""),
            type=el.get("type", "string"),
            description=el.get("description", "") or "",
            range=el.get("range", "") or "",
            format=el.get("format", "dec") or "dec",
            is_multi_value=el.get("is-multi-value", "no") == "yes",
            init_value=el.get("init-value", "") or "",
            is_not_null=el.get("is-not-null", "no") == "yes",
            ordered=el.get("ordered", "no") == "yes",
            owner=owner,
        )


@dataclass
class Relationship:
    name: str
    class_type: str = ""
    description: str = ""
    low_cc: str = "zero"
    high_cc: str = "one"
    is_composite: bool = False
    is_exclusive: bool = False
    is_dependent: bool = False
    ordered: bool = False
    owner: str = ""

    @classmethod
    def from_xml(cls, el: ET.Element, owner: str) -> "Relationship":
        return cls(
            name=el.get("name", ""),
            class_type=el.get("class-type", "") or "",
            description=el.get("description", "") or "",
            low_cc=el.get("low-cc", "zero") or "zero",
            high_cc=el.get("high-cc", "one") or "one",
            is_composite=el.get("is-composite", "no") == "yes",
            is_exclusive=el.get("is-exclusive", "no") == "yes",
            is_dependent=el.get("is-dependent", "no") == "yes",
            ordered=el.get("ordered", "no") == "yes",
            owner=owner,
        )


@dataclass
class Method:
    name: str
    description: str = ""
    implementations: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class OksClass:
    name: str
    description: str = ""
    is_abstract: bool = False
    superclasses: List[str] = field(default_factory=list)
    attributes: Dict[str, Attribute] = field(default_factory=dict)
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    methods: List[Method] = field(default_factory=list)
    source_file: str = ""


class Schema:
    """The union of every ``*.schema.xml`` file in a directory tree."""

    def __init__(self) -> None:
        self.classes: Dict[str, OksClass] = {}
        self._all_supers: Dict[str, List[str]] = {}
        self._all_subs: Dict[str, List[str]] = {}

    # -- loading ---------------------------------------------------------
    def load_dir(self, directory: str, repo_root: str) -> List[str]:
        loaded = []
        pattern = os.path.join(directory, "**", "*.schema.xml")
        for path in sorted(glob.glob(pattern, recursive=True)):
            self.load_file(path, repo_root)
            loaded.append(_relpath(path, repo_root))
        self._resolve()
        return loaded

    def load_file(self, path: str, repo_root: str) -> None:
        root = ET.parse(path).getroot()
        rel = _relpath(path, repo_root)
        for el in root.findall(".//class"):
            name = el.get("name", "")
            cls = OksClass(
                name=name,
                description=(el.get("description", "") or "").strip(),
                is_abstract=el.get("is-abstract", "no") == "yes",
                superclasses=[s.get("name", "") for s in el.findall("superclass")],
                source_file=rel,
            )
            for a in el.findall("attribute"):
                cls.attributes[a.get("name", "")] = Attribute.from_xml(a, name)
            for r in el.findall("relationship"):
                cls.relationships[r.get("name", "")] = Relationship.from_xml(r, name)
            for m in el.findall("method"):
                cls.methods.append(
                    Method(
                        name=m.get("name", ""),
                        description=(m.get("description", "") or "").strip(),
                        implementations=[dict(i.attrib) for i in m.findall("method-implementation")],
                    )
                )
            self.classes[name] = cls

    def _resolve(self) -> None:
        self._all_supers = {}
        for name in self.classes:
            self._all_supers[name] = self._compute_supers(name, [], set())
        self._all_subs = {name: [] for name in self.classes}
        for name, supers in self._all_supers.items():
            for s in supers:
                if s in self._all_subs:
                    self._all_subs[s].append(name)

    def _compute_supers(self, name: str, order: List[str], seen: set) -> List[str]:
        for s in self.classes.get(name, OksClass(name)).superclasses:
            if s in seen:
                continue
            seen.add(s)
            order.append(s)
            self._compute_supers(s, order, seen)
        return order

    # -- queries over the schema ----------------------------------------
    def has(self, class_name: str) -> bool:
        return class_name in self.classes

    def all_superclasses(self, class_name: str) -> List[str]:
        return list(self._all_supers.get(class_name, []))

    def all_subclasses(self, class_name: str) -> List[str]:
        return list(self._all_subs.get(class_name, []))

    def all_attributes(self, class_name: str) -> Dict[str, Attribute]:
        out: Dict[str, Attribute] = {}
        for s in reversed(self.all_superclasses(class_name)):
            out.update(self.classes[s].attributes if s in self.classes else {})
        if class_name in self.classes:
            out.update(self.classes[class_name].attributes)
        return out

    def all_relationships(self, class_name: str) -> Dict[str, Relationship]:
        out: Dict[str, Relationship] = {}
        for s in reversed(self.all_superclasses(class_name)):
            out.update(self.classes[s].relationships if s in self.classes else {})
        if class_name in self.classes:
            out.update(self.classes[class_name].relationships)
        return out

    def find_attribute(self, class_name: str, attr: str) -> Optional[Attribute]:
        return self.all_attributes(class_name).get(attr)

    def find_relationship(self, class_name: str, rel: str) -> Optional[Relationship]:
        return self.all_relationships(class_name).get(rel)


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------
@dataclass
class OksObject:
    class_name: str
    id: str
    attributes: Dict[str, Any] = field(default_factory=dict)   # str | List[str]
    relationships: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)
    source_file: str = ""


class Database:
    """Objects loaded from every ``*.data.xml`` file in a directory tree."""

    def __init__(self, schema: Schema) -> None:
        self.schema = schema
        self.objects: List[OksObject] = []
        self.by_class: Dict[str, List[OksObject]] = {}
        self.by_uid: Dict[Tuple[str, str], OksObject] = {}
        self.by_id: Dict[str, List[OksObject]] = {}

    def load_dir(self, directory: str, repo_root: str) -> List[str]:
        loaded = []
        pattern = os.path.join(directory, "**", "*.data.xml")
        for path in sorted(glob.glob(pattern, recursive=True)):
            self.load_file(path, repo_root)
            loaded.append(_relpath(path, repo_root))
        self._index()
        return loaded

    def load_file(self, path: str, repo_root: str) -> None:
        root = ET.parse(path).getroot()
        rel = _relpath(path, repo_root)
        for el in root.findall(".//obj"):
            obj = OksObject(
                class_name=el.get("class", ""),
                id=el.get("id", ""),
                source_file=rel,
            )
            for at in el.findall("attr"):
                data = at.findall("data")
                if data:
                    obj.attributes[at.get("name", "")] = [d.get("val", "") for d in data]
                else:
                    obj.attributes[at.get("name", "")] = at.get("val", "")
            for rl in el.findall("rel"):
                refs = [(x.get("class", ""), x.get("id", "")) for x in rl.findall("ref")]
                if not refs and rl.get("id"):
                    refs = [(rl.get("class", ""), rl.get("id", ""))]
                obj.relationships[rl.get("name", "")] = refs
            self.objects.append(obj)

    def _index(self) -> None:
        self.by_class = {}
        self.by_uid = {}
        self.by_id = {}
        for o in self.objects:
            self.by_class.setdefault(o.class_name, []).append(o)
            self.by_uid[(o.class_name, o.id)] = o
            self.by_id.setdefault(o.id, []).append(o)

    def scope_objects(self, class_name: str, subclasses: bool) -> List[OksObject]:
        names = [class_name]
        if subclasses:
            names.extend(self.schema.all_subclasses(class_name))
        out: List[OksObject] = []
        for n in names:
            out.extend(self.by_class.get(n, []))
        return out

    def resolve(self, ref: Tuple[str, str]) -> Optional[OksObject]:
        cls, oid = ref
        if (cls, oid) in self.by_uid:
            return self.by_uid[(cls, oid)]
        candidates = self.by_id.get(oid, [])
        if len(candidates) == 1:
            return candidates[0]
        for cand in candidates:
            if cls and (cand.class_name == cls or cls in self.schema.all_superclasses(cand.class_name)):
                return cand
        return None


# --------------------------------------------------------------------------
# IR helpers: validation, serialisation, evaluation
# --------------------------------------------------------------------------
OPERATORS = {"=", "!=", "~=", "<", "<=", ">", ">="}


class IRError(ValueError):
    """Raised when a gold IR does not match the loaded schema or the grammar."""


def serialize(ir: Dict[str, Any]) -> str:
    """Serialise a QueryIR dict to an OksQuery string.

    Byte-for-byte identical to ``oksquery_translator/ast/compiler.py`` so the
    dataset's ``query_oks`` field can be compared to pipeline output directly.
    """
    scope = ir["scope"]
    return f"({scope} {_serialize_expr(ir['expression'])})"


def _serialize_expr(e: Dict[str, Any]) -> str:
    t = e["type"]
    if t == "attribute_compare":
        return f'("{e["attribute"]}" "{e["value"]}" {e["operator"]})'
    if t == "object_id":
        return f'(object-id "{e["object_id"]}" =)'
    if t == "relationship":
        return f'("{e["name"]}" {e["quantifier"]} {_serialize_expr(e["expression"])})'
    if t == "and":
        return "(and " + " ".join(_serialize_expr(o) for o in e["operands"]) + ")"
    if t == "or":
        return "(or " + " ".join(_serialize_expr(o) for o in e["operands"]) + ")"
    if t == "not":
        return f"(not {_serialize_expr(e['operand'])})"
    raise IRError(f"unknown expression type: {t!r}")


def validate(ir: Dict[str, Any], class_name: str, schema: Schema) -> None:
    """Grammar + schema validation. Raises IRError on the first problem."""
    if ir.get("scope") not in {"this", "all"}:
        raise IRError(f"scope must be 'this' or 'all', got {ir.get('scope')!r}")
    if not schema.has(class_name):
        raise IRError(f"unknown class {class_name!r}")
    _validate_expr(ir["expression"], class_name, schema)


def _validate_expr(e: Dict[str, Any], class_name: str, schema: Schema) -> None:
    t = e.get("type")
    if t == "attribute_compare":
        if e.get("operator") not in OPERATORS:
            raise IRError(f"bad operator {e.get('operator')!r}")
        if schema.find_attribute(class_name, e["attribute"]) is None:
            raise IRError(f"class {class_name!r} has no attribute {e['attribute']!r}")
        if not isinstance(e.get("value"), str):
            raise IRError("attribute_compare.value must be a quoted string")
    elif t == "object_id":
        if e.get("operator") != "=":
            raise IRError("object-id supports '=' only")
    elif t == "relationship":
        rel = schema.find_relationship(class_name, e["name"])
        if rel is None:
            raise IRError(f"class {class_name!r} has no relationship {e['name']!r}")
        if e.get("quantifier") not in {"some", "all"}:
            raise IRError(f"bad quantifier {e.get('quantifier')!r}")
        if not schema.has(rel.class_type):
            raise IRError(f"relationship {e['name']!r} targets unknown class {rel.class_type!r}")
        _validate_expr(e["expression"], rel.class_type, schema)
    elif t in {"and", "or"}:
        ops = e.get("operands") or []
        if len(ops) < 2:
            raise IRError(f"'{t}' needs at least two operands")
        for o in ops:
            _validate_expr(o, class_name, schema)
    elif t == "not":
        _validate_expr(e["operand"], class_name, schema)
    else:
        raise IRError(f"unknown expression type {t!r}")


def schema_elements(ir: Dict[str, Any], class_name: str, schema: Schema) -> Dict[str, List[str]]:
    """The gold retrieval set for M2, derived by walking the ground-truth IR."""
    classes: List[str] = [class_name]
    attributes: List[str] = []
    relationships: List[str] = []

    def walk(e: Dict[str, Any], cn: str) -> None:
        t = e["type"]
        if t == "attribute_compare":
            attr = schema.find_attribute(cn, e["attribute"])
            owner = attr.owner if attr else cn
            _add(classes, owner)
            _add(attributes, f"{owner}.{e['attribute']}")
        elif t == "relationship":
            rel = schema.find_relationship(cn, e["name"])
            owner = rel.owner if rel else cn
            _add(classes, owner)
            _add(relationships, f"{owner}.{e['name']}")
            if rel:
                _add(classes, rel.class_type)
                walk(e["expression"], rel.class_type)
        elif t in {"and", "or"}:
            for o in e["operands"]:
                walk(o, cn)
        elif t == "not":
            walk(e["operand"], cn)

    walk(ir["expression"], class_name)
    return {
        "classes": sorted(classes),
        "attributes": sorted(attributes),
        "relationships": sorted(relationships),
    }


def _add(seq: List[str], value: str) -> None:
    if value and value not in seq:
        seq.append(value)


# -- execution -------------------------------------------------------------
def execute(ir: Dict[str, Any], class_name: str, db: Database) -> List[str]:
    """Return the sorted object IDs matching ``ir`` when run on ``class_name``."""
    subclasses = ir["scope"] == "all"
    matched = [
        o.id
        for o in db.scope_objects(class_name, subclasses)
        if _satisfies(o, ir["expression"], db)
    ]
    return sorted(set(matched))


def _satisfies(obj: OksObject, e: Dict[str, Any], db: Database) -> bool:
    t = e["type"]
    if t == "and":
        return all(_satisfies(obj, o, db) for o in e["operands"])
    if t == "or":
        return any(_satisfies(obj, o, db) for o in e["operands"])
    if t == "not":
        return not _satisfies(obj, e["operand"], db)
    if t == "object_id":
        return obj.id == e["object_id"]
    if t == "attribute_compare":
        return _compare_attribute(obj, e, db)
    if t == "relationship":
        refs = obj.relationships.get(e["name"], [])
        targets = [db.resolve(r) for r in refs]
        results = [
            False if target is None else _satisfies(target, e["expression"], db)
            for target in targets
        ]
        if e["quantifier"] == "some":
            return any(results)
        return bool(results) and all(results)
    raise IRError(f"unknown expression type {t!r}")


def _compare_attribute(obj: OksObject, e: Dict[str, Any], db: Database) -> bool:
    attr = db.schema.find_attribute(obj.class_name, e["attribute"])
    if attr is None:
        return False
    raw = obj.attributes.get(e["attribute"], None)
    if raw is None:
        raw = attr.init_value
    values = raw if isinstance(raw, list) else [raw]
    return any(_compare_one(str(v), e["value"], e["operator"], attr.type) for v in values)


def _compare_one(left: str, right: str, op: str, oks_type: str) -> bool:
    if op == "~=":
        try:
            return re.fullmatch(right, left) is not None
        except re.error:
            return False
    if oks_type == "bool":
        # An unset or unrecognised bool reads as false, the typed default.
        lb = _as_bool(left) or False
        rb = _as_bool(right) or False
        return _apply(int(lb), int(rb), op)
    if oks_type in NUMERIC_TYPES:
        # An unset or unparseable number reads as 0, the typed default.
        lf = _as_float(left)
        rf = _as_float(right)
        return _apply(0.0 if lf is None else lf, 0.0 if rf is None else rf, op)
    return _apply(left, right, op)


def _apply(a: Any, b: Any, op: str) -> bool:
    if op == "=":
        return a == b
    if op == "!=":
        return a != b
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    raise IRError(f"bad operator {op!r}")


def _as_bool(v: str) -> Optional[bool]:
    lowered = v.strip().lower()
    if lowered in BOOL_TRUE:
        return True
    if lowered in BOOL_FALSE:
        return False
    return None


def _as_float(v: str) -> Optional[float]:
    try:
        return float(v.strip())
    except (TypeError, ValueError):
        return None


def _relpath(path: str, root: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def load_repository(repo_root: str,
                    schema_dir: str = "test_schema/xml",
                    data_dir: str = "test_data") -> Tuple[Schema, Database, List[str], List[str]]:
    schema = Schema()
    schema_files = schema.load_dir(os.path.join(repo_root, *schema_dir.split("/")), repo_root)
    db = Database(schema)
    data_files = db.load_dir(os.path.join(repo_root, *data_dir.split("/")), repo_root)
    return schema, db, schema_files, data_files
