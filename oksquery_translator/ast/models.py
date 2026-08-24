"""
ast/models.py — Strongly-Typed Pydantic V2 OKSQuery IR Models
=============================================================

Defines the Intermediate Representation (IR) schema for OKS queries.
The IR is the structured contract between LLM generation and deterministic compilation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator


class AttributeCompare(BaseModel):
    """Expression comparing an object attribute against a value."""
    type: Literal["attribute_compare"] = "attribute_compare"
    attribute: str
    operator: Literal["=", "!=", "~=", "<", "<=", ">", ">="]
    value: str


class ObjectIdCompare(BaseModel):
    """Expression filtering by object identifier."""
    type: Literal["object_id"] = "object_id"
    # ``object-id "" !=`` is the documented OKS match-all expression.
    operator: Literal["=", "!="] = "="
    object_id: str


class RelationshipCompare(BaseModel):
    """Expression traversing a relationship to another object/class."""
    type: Literal["relationship"] = "relationship"
    name: str
    quantifier: Literal["some", "all"] = "some"
    expression: "Expression"


class AndExpression(BaseModel):
    """Logical conjunction (AND) of two or more expressions."""
    type: Literal["and"] = "and"
    operands: List["Expression"]

    @model_validator(mode="before")
    @classmethod
    def check_operands(cls, values):
        ops = values.get("operands", []) if isinstance(values, dict) else []
        if len(ops) < 2:
            raise ValueError("'and' expression must have at least two operands")
        return values


class OrExpression(BaseModel):
    """Logical disjunction (OR) of two or more expressions."""
    type: Literal["or"] = "or"
    operands: List["Expression"]

    @model_validator(mode="before")
    @classmethod
    def check_operands(cls, values):
        ops = values.get("operands", []) if isinstance(values, dict) else []
        if len(ops) < 2:
            raise ValueError("'or' expression must have at least two operands")
        return values


class NotExpression(BaseModel):
    """Logical negation (NOT) of an expression."""
    type: Literal["not"] = "not"
    operand: "Expression"


# Recursive union type alias
Expression = Union[
    AndExpression,
    OrExpression,
    NotExpression,
    RelationshipCompare,
    AttributeCompare,
    ObjectIdCompare,
]

# Rebuild Pydantic models to resolve recursive forward references
AndExpression.model_rebuild()
OrExpression.model_rebuild()
NotExpression.model_rebuild()
RelationshipCompare.model_rebuild()


class QueryIR(BaseModel):
    """Top-level query container matching the full IR grammar."""
    target_class: Optional[str] = None
    scope: Literal["this", "all"] = "all"
    expression: Expression
    explanation: Optional[str] = None


class SemanticValidationError(ValueError):
    """Raised when an IR expression violates schema semantics."""
    pass


@dataclass
class ValidationResult:
    """Result of validating a QueryIR AST."""
    valid: bool
    error_type: str = ""       # e.g. "structural", "class_not_found", "schema_mismatch", "case_error"
    message: str = ""          # human-readable diagnostic message for repair prompt
    class_name: str = ""       # target class where error occurred
    attribute: str = ""        # problematic attribute name
    relationship: str = ""     # problematic relationship name
