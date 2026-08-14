import unittest
from agent.ir_validator import validate_ir, QueryIR
from agent.serializer import serialize_ir_to_oks


class TestIRValidation(unittest.TestCase):
    def test_simple_attribute_compare(self):
        valid_ir_dict = {
            "scope": "all",
            "expression": {
                "type": "attribute_compare",
                "attribute": "Timeout",
                "operator": ">",
                "value": "25"
            }
        }

        ir = validate_ir(valid_ir_dict)
        self.assertIsInstance(ir, QueryIR)

        oks_str = serialize_ir_to_oks(ir)
        self.assertEqual(oks_str, '(all ("Timeout" "25" >))')

    def test_complex_and_with_relationship(self):
        complex_ir_dict = {
            "scope": "all",
            "expression": {
                "type": "and",
                "operands": [
                    {
                        "type": "attribute_compare",
                        "attribute": "Name",
                        "operator": "=",
                        "value": "fake"
                    },
                    {
                        "type": "relationship",
                        "name": "RunsOn",
                        "quantifier": "some",
                        "expression": {
                            "type": "object_id",
                            "operator": "=",
                            "object_id": "hostA"
                        }
                    }
                ]
            }
        }

        ir = validate_ir(complex_ir_dict)
        oks_str = serialize_ir_to_oks(ir)
        self.assertEqual(oks_str, '(all (and ("Name" "fake" =) ("RunsOn" some (object-id "hostA" =))))')

    def test_not_expression(self):
        ir_dict = {
            "scope": "all",
            "expression": {
                "type": "not",
                "operand": {
                    "type": "attribute_compare",
                    "attribute": "Status",
                    "operator": "=",
                    "value": "Stopped"
                }
            }
        }
        ir = validate_ir(ir_dict)
        oks_str = serialize_ir_to_oks(ir)
        self.assertEqual(oks_str, '(all (not ("Status" "Stopped" =)))')

    def test_or_expression(self):
        ir_dict = {
            "scope": "all",
            "expression": {
                "type": "or",
                "operands": [
                    {
                        "type": "attribute_compare",
                        "attribute": "Name",
                        "operator": "=",
                        "value": "app1"
                    },
                    {
                        "type": "attribute_compare",
                        "attribute": "Name",
                        "operator": "=",
                        "value": "app2"
                    }
                ]
            }
        }
        ir = validate_ir(ir_dict)
        oks_str = serialize_ir_to_oks(ir)
        self.assertEqual(oks_str, '(all (or ("Name" "app1" =) ("Name" "app2" =)))')

    def test_and_requires_at_least_two_operands(self):
        ir_dict = {
            "scope": "all",
            "expression": {
                "type": "and",
                "operands": [
                    {
                        "type": "attribute_compare",
                        "attribute": "Name",
                        "operator": "=",
                        "value": "only_one"
                    }
                ]
            }
        }
        with self.assertRaises(Exception):
            validate_ir(ir_dict)

    def test_explanation_field_optional(self):
        """The 'explanation' field is optional and should not break validation."""
        ir_dict = {
            "scope": "all",
            "expression": {
                "type": "attribute_compare",
                "attribute": "Timeout",
                "operator": ">",
                "value": "25"
            },
            "explanation": "Find all objects where Timeout exceeds 25."
        }
        ir = validate_ir(ir_dict)
        self.assertIsInstance(ir, QueryIR)
        self.assertEqual(ir.explanation, "Find all objects where Timeout exceeds 25.")

    def test_this_scope(self):
        ir_dict = {
            "scope": "this",
            "expression": {
                "type": "attribute_compare",
                "attribute": "Name",
                "operator": "=",
                "value": "rc_trigger_1"
            }
        }
        ir = validate_ir(ir_dict)
        oks_str = serialize_ir_to_oks(ir)
        self.assertEqual(oks_str, '(this ("Name" "rc_trigger_1" =))')

    def test_nested_relationship(self):
        """Test deeply nested relationship + object-id pattern."""
        ir_dict = {
            "scope": "all",
            "expression": {
                "type": "relationship",
                "name": "ApplicationsControlled",
                "quantifier": "some",
                "expression": {
                    "type": "object_id",
                    "operator": "=",
                    "object_id": "rc-readout-1"
                }
            }
        }
        ir = validate_ir(ir_dict)
        oks_str = serialize_ir_to_oks(ir)
        self.assertEqual(oks_str, '(all ("ApplicationsControlled" some (object-id "rc-readout-1" =)))')


if __name__ == '__main__':
    unittest.main()
