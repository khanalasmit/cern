"""
oks_ast/normalizer.py — Module 9: AST Normalizer
==============================================

Normalizes a raw LLM-produced IR dictionary before Pydantic validation.
All normalization is deterministic (zero LLM calls).

Responsibilities:
  1. Standardize operator synonyms: "eq" → "=", "gt" → ">", "regex" → "~=", etc.
  2. Standardize scope: "ALL" → "all", "THIS" → "this", invalid → "all".
  3. Strip unwanted quotes and whitespace from class, attribute, and relationship names.
  4. Ensure all attribute comparison values are coerced to strings (e.g. 2 → "2").
  5. Standardize relationship quantifiers: "SOME" → "some", "ALL" → "all".
"""
from __future__ import annotations

from typing import Any, Dict

# Canonical operator synonym lookup map
_OPERATOR_NORMALIZATIONS = {
    "eq": "=", "equals": "=", "equal": "=", "==": "=", "=": "=",
    "ne": "!=", "neq": "!=", "not equal": "!=", "<>": "!=", "!=": "!=",
    "gt": ">", "greater": ">", ">": ">",
    "lt": "<", "less": "<", "<": "<",
    "gte": ">=", "ge": ">=", "greater_equal": ">=", ">=": ">=",
    "lte": "<=", "le": "<=", "less_equal": "<=", "<=": "<=",
    "regex": "~=", "match": "~=", "like": "~=", "contains": "~=", "~=": "~=",
}

_VALID_SCOPES = {"all", "this"}
_VALID_QUANTIFIERS = {"some", "all"}


class NormalizerError(ValueError):
    """Raised when the raw IR dict is malformed and cannot be normalized."""
    pass


def normalize_ir(raw_dict: Any) -> Dict[str, Any]:
    """
    Normalize a raw LLM-produced IR dictionary in-place and return the sanitized dict.

    Parameters
    ----------
    raw_dict : Any
        Parsed JSON dictionary from LLM output.

    Returns
    -------
    dict
        Cleaned dictionary ready for Pydantic V2 validation.

    Raises
    ------
    NormalizerError
        If raw_dict is not a dictionary or missing required root elements.
    """
    if not isinstance(raw_dict, dict):
        raise NormalizerError(f"Expected dict at top-level, got {type(raw_dict).__name__}")

    result = dict(raw_dict)

    # 1. Normalize Scope
    scope_raw = str(result.get("scope", "all")).lower().strip()
    if scope_raw not in _VALID_SCOPES:
        scope_raw = "all"
    result["scope"] = scope_raw

    # 2. Normalize Target Class
    if "target_class" in result and result["target_class"] is not None:
        tc = str(result["target_class"]).strip().strip('"').strip("'")
        result["target_class"] = tc if tc else None

    # 3. Normalize Expression
    if "expression" not in result or result["expression"] is None:
        raise NormalizerError("IR dictionary missing 'expression' field")

    result["expression"] = _normalize_expression(result["expression"])

    return result


def _normalize_expression(expr: Any) -> Dict[str, Any]:
    """Recursively clean and normalize an expression node."""
    if not isinstance(expr, dict):
        raise NormalizerError(f"Expression node must be a dict, got {type(expr).__name__}: {expr!r}")

    result = dict(expr)
    expr_type = str(result.get("type", "")).lower().strip()
    result["type"] = expr_type

    if expr_type == "attribute_compare":
        # Attribute name
        if "attribute" in result:
            result["attribute"] = str(result["attribute"]).strip().strip('"').strip("'")

        # Operator
        if "operator" in result:
            result["operator"] = _normalize_operator(str(result["operator"]))

        # Value coerced to string
        if "value" in result:
            result["value"] = str(result["value"]).strip().strip('"').strip("'") if isinstance(result["value"], str) else str(result["value"]).strip()

    elif expr_type == "object_id":
        # Exact IDs use "="; the documented match-all expression uses
        # object-id "" !=. Preserve the operator supplied by the LLM so the
        # deterministic compiler does not silently turn match-all into an
        # empty result set.
        if "operator" in result:
            result["operator"] = _normalize_operator(str(result["operator"]))
        else:
            result["operator"] = "="
        if result["operator"] not in {"=", "!="}:
            raise NormalizerError(
                f"object_id operator must be '=' or '!=', got {result['operator']!r}"
            )
        if "object_id" in result:
            result["object_id"] = str(result["object_id"]).strip().strip('"').strip("'")

    elif expr_type == "relationship":
        if "name" in result:
            result["name"] = str(result["name"]).strip().strip('"').strip("'")

        quantifier = str(result.get("quantifier", "some")).lower().strip()
        if quantifier not in _VALID_QUANTIFIERS:
            quantifier = "some"
        result["quantifier"] = quantifier

        if "expression" in result:
            result["expression"] = _normalize_expression(result["expression"])

    elif expr_type in ("and", "or"):
        operands = result.get("operands", [])
        if not isinstance(operands, list):
            raise NormalizerError(f"'{expr_type}' operands must be a list")
        result["operands"] = [_normalize_expression(op) for op in operands]

    elif expr_type == "not":
        operand = result.get("operand")
        if operand is None:
            raise NormalizerError("'not' expression missing 'operand'")
        result["operand"] = _normalize_expression(operand)

    return result


def _normalize_operator(op: str) -> str:
    """Normalize operator string to canonical symbol."""
    cleaned = op.strip().lower()
    return _OPERATOR_NORMALIZATIONS.get(cleaned, op.strip())
