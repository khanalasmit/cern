"""
ast/compiler.py — Module 12: Deterministic OKSQuery Compiler
=============================================================

Deterministically compiles a validated QueryIR AST into a canonical
OKSQuery S-expression string ready for execution by Executor.

CRITICAL ARCHITECTURAL INVARIANT:
  The compiler NEVER calls the LLM. It is 100% pure deterministic code.
"""
from __future__ import annotations

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
)
from ..context.oks_context import OksContext


class OksCompiler:
    """
    Deterministically transforms a validated QueryIR AST into an OksQuery S-expression.
    """

    def compile(self, ir: QueryIR, oks_context: Optional[OksContext] = None) -> str:
        """
        Compile QueryIR to an OksQuery string.

        Parameters
        ----------
        ir : QueryIR
            Validated QueryIR instance.
        oks_context : OksContext, optional
            Context under which the query was validated (recorded for provenance).

        Returns
        -------
        str
            Canonical OksQuery S-expression (e.g. '(all ("InitTimeout" "2" >))').
        """
        expr_str = self._compile_expression(ir.expression)
        return f"({ir.scope} {expr_str})"

    def _compile_expression(self, expr: Expression) -> str:
        """Recursively compile an AST Expression node to S-expression syntax."""
        if isinstance(expr, AttributeCompare):
            # Format: ("<attribute>" "<value>" <operator>)
            # Escape quotes in value if present
            safe_val = expr.value.replace('"', '\\"')
            return f'("{expr.attribute}" "{safe_val}" {expr.operator})'

        elif isinstance(expr, ObjectIdCompare):
            # Format: (object-id "<id>" =|!=)
            safe_id = expr.object_id.replace('"', '\\"')
            return f'(object-id "{safe_id}" {expr.operator})'

        elif isinstance(expr, RelationshipCompare):
            # Format: ("<rel-name>" <some|all> <nested-expression>)
            nested_str = self._compile_expression(expr.expression)
            return f'("{expr.name}" {expr.quantifier} {nested_str})'

        elif isinstance(expr, AndExpression):
            # Format: (and <expr1> <expr2> ...)
            operands_str = " ".join(self._compile_expression(op) for op in expr.operands)
            return f'(and {operands_str})'

        elif isinstance(expr, OrExpression):
            # Format: (or <expr1> <expr2> ...)
            operands_str = " ".join(self._compile_expression(op) for op in expr.operands)
            return f'(or {operands_str})'

        elif isinstance(expr, NotExpression):
            # Format: (not <expr>)
            operand_str = self._compile_expression(expr.operand)
            return f'(not {operand_str})'

        else:
            raise ValueError(f"Unknown expression type during compilation: {type(expr).__name__}")


def serialize_ir_to_oks(ir: QueryIR) -> str:
    """Backward-compatible alias for OksCompiler.compile()."""
    return OksCompiler().compile(ir)
