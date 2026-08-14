from .ir_validator import (
    QueryIR, Expression, AttributeCompare, ObjectIdCompare,
    RelationshipCompare, AndExpression, OrExpression, NotExpression
)

class OksSerializer:
    @staticmethod
    def serialize(ir: QueryIR) -> str:
        """Serializes a validated QueryIR object into an OksQuery string."""
        expr_str = OksSerializer._serialize_expression(ir.expression)
        return f"({ir.scope} {expr_str})"

    @staticmethod
    def _serialize_expression(expr: Expression) -> str:
        if isinstance(expr, AttributeCompare):
            # Format: ("attr-name" "value" op)
            # Ensure proper escaping if needed
            return f'("{expr.attribute}" "{expr.value}" {expr.operator})'
        elif isinstance(expr, ObjectIdCompare):
            # Format: (object-id "id" =)
            return f'(object-id "{expr.object_id}" =)'
        elif isinstance(expr, RelationshipCompare):
            # Format: ("rel-name" some/all expr)
            nested_expr = OksSerializer._serialize_expression(expr.expression)
            return f'("{expr.name}" {expr.quantifier} {nested_expr})'
        elif isinstance(expr, AndExpression):
            # Format: (and expr1 expr2 ...)
            operands_str = " ".join([OksSerializer._serialize_expression(op) for op in expr.operands])
            return f'(and {operands_str})'
        elif isinstance(expr, OrExpression):
            # Format: (or expr1 expr2 ...)
            operands_str = " ".join([OksSerializer._serialize_expression(op) for op in expr.operands])
            return f'(or {operands_str})'
        elif isinstance(expr, NotExpression):
            # Format: (not expr)
            operand_str = OksSerializer._serialize_expression(expr.operand)
            return f'(not {operand_str})'
        else:
            raise ValueError(f"Unknown expression type: {type(expr)}")

def serialize_ir_to_oks(ir: QueryIR) -> str:
    return OksSerializer.serialize(ir)
