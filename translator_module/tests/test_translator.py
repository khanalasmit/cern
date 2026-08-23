import unittest
from types import SimpleNamespace

from agent.ir_validator import validate_ir, QueryIR
from agent.serializer import serialize_ir_to_oks
from agent.translator import OksTranslator
from memory import ConversationMemory


class _FakeCompletions:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content=next(self.responses))
            )]
        )


class _FakeClient:
    def __init__(self, responses):
        self.chat = SimpleNamespace(completions=_FakeCompletions(responses))


class _StaticContext:
    def get_schema_context(self, _query):
        return ""

    def get_examples(self, _query):
        return ""


class TestTranslatorMemory(unittest.TestCase):
    def test_follow_up_query_receives_previous_exchange(self):
        translator = OksTranslator.__new__(OksTranslator)
        translator.retriever = _StaticContext()
        translator.few_shot_manager = _StaticContext()
        translator.llm_model = "test-model"
        translator.memory = ConversationMemory()
        translator.client = _FakeClient([
            '{"scope":"all","expression":{"type":"attribute_compare",'
            '"attribute":"Timeout","operator":">","value":"25"}}',
            '{"scope":"all","expression":{"type":"attribute_compare",'
            '"attribute":"Timeout","operator":"<","value":"50"}}',
        ])

        first = translator.translate("Find objects with Timeout over 25")
        second = translator.translate("Now make it less than 50")

        self.assertEqual(first["status"], "success")
        self.assertEqual(second["status"], "success")
        second_messages = translator.client.chat.completions.calls[1]["messages"]
        self.assertEqual(
            second_messages[1:],
            [
                {"role": "user", "content": "Find objects with Timeout over 25"},
                {
                    "role": "assistant",
                    "content": (
                        '{"scope":"all","expression":{"type":"attribute_compare",'
                        '"attribute":"Timeout","operator":">","value":"25"}}'
                    ),
                },
                {"role": "user", "content": "Now make it less than 50"},
            ],
        )


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
