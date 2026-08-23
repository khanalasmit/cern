from typing import List, Literal, Optional, Union, Annotated
from pydantic import BaseModel, Field, model_validator, TypeAdapter


class AttributeCompare(BaseModel):
    type: Literal["attribute_compare"]
    attribute: str
    operator: Literal["=", "!=", "~=", "<", "<=", ">", ">="]
    value: str


class ObjectIdCompare(BaseModel):
    type: Literal["object_id"]
    operator: Literal["="]
    object_id: str


class RelationshipCompare(BaseModel):
    type: Literal["relationship"]
    name: str
    quantifier: Literal["some", "all"]
    expression: "Expression"


class AndExpression(BaseModel):
    type: Literal["and"]
    operands: List["Expression"]

    @model_validator(mode="before")
    @classmethod
    def check_operands(cls, values):
        ops = values.get('operands', []) if isinstance(values, dict) else []
        if len(ops) < 2:
            raise ValueError("'and' expression must have at least two operands")
        return values


class OrExpression(BaseModel):
    type: Literal["or"]
    operands: List["Expression"]

    @model_validator(mode="before")
    @classmethod
    def check_operands(cls, values):
        ops = values.get('operands', []) if isinstance(values, dict) else []
        if len(ops) < 2:
            raise ValueError("'or' expression must have at least two operands")
        return values


class NotExpression(BaseModel):
    type: Literal["not"]
    operand: "Expression"


# Recursive type alias
Expression = Union[
    AndExpression, OrExpression, NotExpression,
    RelationshipCompare, AttributeCompare, ObjectIdCompare
]

# Rebuild models to resolve forward references (Pydantic v2)
AndExpression.model_rebuild()
OrExpression.model_rebuild()
NotExpression.model_rebuild()
RelationshipCompare.model_rebuild()


class QueryIR(BaseModel):
    target_class: Optional[str] = None
    scope: Literal["this", "all"]
    expression: Expression
    explanation: Optional[str] = None


class SemanticValidationError(ValueError):
    """Raised when an IR expression violates schema semantics (e.g. invalid attribute, bad rel target)."""
    pass


def validate_ir(ir_json: dict) -> QueryIR:
    """Validates the parsed JSON against the IR schema and returns a Pydantic model."""
    return QueryIR.model_validate(ir_json)


def validate_ir_semantics(ir: QueryIR, indexer) -> None:
    """
    Recursively validates that:
    1. target_class exists in the schema (if provided).
    2. Attributes exist on the target_class (or its superclasses).
    3. Relationships exist on the target_class, and any nested expression
       is valid on the relationship's target class-type.
    """
    if not hasattr(indexer, 'resolved_classes') or not indexer.resolved_classes:
        return  # Indexer not loaded or no classes

    root_class = ir.target_class
    if not root_class:
        # Best-effort fallback if target_class was omitted by LLM
        return

    class_def = indexer.get_class(root_class)
    if not class_def:
        known_classes = list(indexer.resolved_classes.keys())
        close = [c for c in known_classes if root_class.lower() in c.lower()][:5]
        hint = f" Did you mean one of: {close}?" if close else ""
        raise SemanticValidationError(
            f"Target class '{root_class}' does not exist in schema.{hint}"
        )

    def _validate_expr(expr: Expression, current_class_name: str, path: str = ""):
        c_def = indexer.get_class(current_class_name)
        if not c_def:
            return

        attrs = c_def.get("attributes", {})
        rels = c_def.get("relationships", {})

        if isinstance(expr, AttributeCompare):
            if expr.attribute not in attrs:
                avail = list(attrs.keys())[:12]
                raise SemanticValidationError(
                    f"Attribute '{expr.attribute}' does not exist on class '{current_class_name}' "
                    f"(relationship path: '{path or 'root'}'). Available attributes on '{current_class_name}': {avail}"
                )
        elif isinstance(expr, ObjectIdCompare):
            pass
        elif isinstance(expr, RelationshipCompare):
            if expr.name not in rels:
                avail = list(rels.keys())
                raise SemanticValidationError(
                    f"Relationship '{expr.name}' does not exist on class '{current_class_name}' "
                    f"(relationship path: '{path or 'root'}'). Available relationships on '{current_class_name}': {avail}"
                )
            target_type = rels[expr.name]
            if not target_type:
                raise SemanticValidationError(
                    f"Relationship '{expr.name}' on '{current_class_name}' has no defined target class."
                )
            new_path = f"{path}.{expr.name}" if path else expr.name
            _validate_expr(expr.expression, target_type, new_path)
        elif isinstance(expr, (AndExpression, OrExpression)):
            for op in expr.operands:
                _validate_expr(op, current_class_name, path)
        elif isinstance(expr, NotExpression):
            _validate_expr(expr.operand, current_class_name, path)

    _validate_expr(ir.expression, root_class)
