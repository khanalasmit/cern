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
    scope: Literal["this", "all"]
    expression: Expression
    # Optional during migration so existing evaluation rows remain valid.
    # Historical execution requires this field to be present.
    target_class: Optional[str] = None
    explanation: Optional[str] = None


def validate_ir(ir_json: dict) -> QueryIR:
    """Validates the parsed JSON against the IR schema and returns a Pydantic model."""
    return QueryIR.model_validate(ir_json)
