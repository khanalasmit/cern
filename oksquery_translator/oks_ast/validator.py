"""
oks_ast/validator.py — Module 10: Version-Aware Deterministic AST Validator
=========================================================================

Validates a QueryIR AST against the OksSchemaProvider bound to the exact OksContext.

Two-layer validation:
  Layer 1 — Structural (via Pydantic V2 models, already verified by QueryIR)
  Layer 2 — Semantic (via OksSchemaProvider):
    2a. target_class exists in the resolved schema context
    2b. All attributes exist on the class (or its inherited superclasses)
    2c. Strict case-sensitivity enforcement with diagnostic corrections
    2d. Relationship vs attribute disambiguation
    2e. Relationship traversal typing (nested expressions validated on target class)

Returns a ValidationResult with rich diagnostics including the schema fingerprint.
"""
from __future__ import annotations

import logging
from typing import Optional

from .models import (
    AndExpression,
    AttributeCompare,
    Expression,
    NotExpression,
    ObjectIdCompare,
    OrExpression,
    QueryIR,
    RelationshipCompare,
    ValidationResult,
)
from ..context.oks_context import OksContext
from ..schema.oks_schema_provider import OksSchemaProvider

logger = logging.getLogger("oksquery_translator.oks_ast.validator")


class ASTValidator:
    """
    Context-bound semantic validator for QueryIR ASTs (Module 10).

    Usage::
        validator = ASTValidator(schema_provider)
        result = validator.validate(ir, oks_context)
        if not result.valid:
            print(result.message)  # Feed directly into repair loop
    """

    def __init__(self, schema_provider: OksSchemaProvider):
        self.schema_provider = schema_provider

    def validate(self, ir: QueryIR, oks_context: OksContext) -> ValidationResult:
        """
        Validate a QueryIR AST against the schema bound to oks_context.

        Parameters
        ----------
        ir : QueryIR
            Pydantic-validated QueryIR instance.
        oks_context : OksContext
            The immutable context this query was constructed for.

        Returns
        -------
        ValidationResult
        """
        target_class = ir.target_class
        if not target_class:
            return ValidationResult(
                valid=False,
                error_type="structural",
                message="Target class is missing in QueryIR. You must specify the exact OKS class name.",
            )

        # Check 1: Target Class Existence
        if not self.schema_provider.class_exists(target_class):
            suggestions = self.schema_provider.suggest_class(target_class)
            hint = f" Did you mean one of: {', '.join(suggestions)}?" if suggestions else ""
            return ValidationResult(
                valid=False,
                error_type="class_not_found",
                message=(
                    f"Target class '{target_class}' does not exist in schema "
                    f"(fingerprint: {oks_context.schema_fingerprint}).{hint}"
                ),
                class_name=target_class,
            )

        # Check 2: Recursive Expression Semantic Validation
        error = self._validate_expr(ir.expression, target_class, oks_context, path="root")
        if error is not None:
            return error

        return ValidationResult(valid=True)

    def _validate_expr(
        self,
        expr: Expression,
        current_class: str,
        oks_context: OksContext,
        path: str,
    ) -> Optional[ValidationResult]:
        """
        Recursively validate an expression node against current_class.
        Returns a ValidationResult on failure, or None on success.
        """
        cls_def = self.schema_provider.get_effective_members(current_class)
        if cls_def is None:
            # Class exists in schema list but no detailed definition available
            return None

        if isinstance(expr, AttributeCompare):
            attr_name = expr.attribute
            valid_attrs = cls_def.attribute_names()

            if attr_name not in valid_attrs:
                # 1. Check for exact case mismatch
                case_match = next((a for a in valid_attrs if a.lower() == attr_name.lower()), None)
                if case_match:
                    return ValidationResult(
                        valid=False,
                        error_type="case_error",
                        message=(
                            f"CRITICAL CASE ERROR at {path}: You specified attribute '{attr_name}', "
                            f"but the exact casing on class '{current_class}' is '{case_match}'. "
                            f"OKS names are case-sensitive. Use EXACTLY '{case_match}'. "
                            f"[Schema Fingerprint: {oks_context.schema_fingerprint}]"
                        ),
                        class_name=current_class,
                        attribute=attr_name,
                    )

                # 2. Check if name is actually a relationship on this class
                rel_match = next((r for r in cls_def.relationship_names() if r.lower() == attr_name.lower()), None)
                if rel_match:
                    return ValidationResult(
                        valid=False,
                        error_type="schema_mismatch",
                        message=(
                            f"SCHEMA ERROR at {path}: '{attr_name}' is NOT an attribute on class '{current_class}', "
                            f"it is a RELATIONSHIP named '{rel_match}'. "
                            f"Use relationship traversal instead: ('{rel_match}' some <nested-expression>). "
                            f"[Schema Fingerprint: {oks_context.schema_fingerprint}]"
                        ),
                        class_name=current_class,
                        attribute=attr_name,
                        relationship=rel_match,
                    )

                # 3. Unknown attribute
                available_preview = valid_attrs[:12]
                return ValidationResult(
                    valid=False,
                    error_type="schema_mismatch",
                    message=(
                        f"SCHEMA ERROR at {path}: Attribute '{attr_name}' does not exist on class '{current_class}'. "
                        f"Available attributes on '{current_class}': {available_preview}. "
                        f"Use ONLY attribute names defined in the schema. "
                        f"[Schema Fingerprint: {oks_context.schema_fingerprint}]"
                    ),
                    class_name=current_class,
                    attribute=attr_name,
                )

        elif isinstance(expr, ObjectIdCompare):
            # object-id comparisons are universal across all OKS objects
            return None

        elif isinstance(expr, RelationshipCompare):
            rel_name = expr.name
            valid_rels = cls_def.relationship_names()

            if rel_name not in valid_rels:
                # Check case mismatch
                case_match = next((r for r in valid_rels if r.lower() == rel_name.lower()), None)
                if case_match:
                    return ValidationResult(
                        valid=False,
                        error_type="case_error",
                        message=(
                            f"CRITICAL CASE ERROR at {path}: You specified relationship '{rel_name}', "
                            f"but the exact casing on class '{current_class}' is '{case_match}'. "
                            f"Use EXACTLY '{case_match}'. "
                            f"[Schema Fingerprint: {oks_context.schema_fingerprint}]"
                        ),
                        class_name=current_class,
                        relationship=rel_name,
                    )

                available_rels = valid_rels[:12]
                return ValidationResult(
                    valid=False,
                    error_type="schema_mismatch",
                    message=(
                        f"SCHEMA ERROR at {path}: Relationship '{rel_name}' does not exist on class '{current_class}'. "
                        f"Available relationships on '{current_class}': {available_rels}. "
                        f"[Schema Fingerprint: {oks_context.schema_fingerprint}]"
                    ),
                    class_name=current_class,
                    relationship=rel_name,
                )

            # Recurse into relationship target class
            rel_def = cls_def.get_relationship(rel_name)
            target_type = rel_def.target_class if rel_def else ""
            if target_type:
                new_path = f"{path}.{rel_name}" if path != "root" else rel_name
                return self._validate_expr(expr.expression, target_type, oks_context, path=new_path)

        elif isinstance(expr, (AndExpression, OrExpression)):
            for operand in expr.operands:
                err = self._validate_expr(operand, current_class, oks_context, path)
                if err is not None:
                    return err

        elif isinstance(expr, NotExpression):
            return self._validate_expr(expr.operand, current_class, oks_context, path)

        return None
