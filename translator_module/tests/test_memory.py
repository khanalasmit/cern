import json
import tempfile
import unittest
from pathlib import Path

from memory import ConversationMemory


class TestConversationMemory(unittest.TestCase):
    def test_histories_are_bounded_and_conversation_scoped(self):
        memory = ConversationMemory(max_turns=3)

        memory.add_user_turn("first", "one")
        memory.add_assistant_turn("first", "answer one")
        memory.add_user_turn("first", "two")
        memory.add_assistant_turn("first", "answer two")
        memory.add_user_turn("second", "unrelated")

        self.assertEqual(memory.get_history("first"), [
            {"role": "assistant", "content": "answer one"},
            {"role": "user", "content": "two"},
            {"role": "assistant", "content": "answer two"},
        ])
        self.assertEqual(memory.get_history("second"), [
            {"role": "user", "content": "unrelated"},
        ])
        self.assertEqual(memory.get_history("missing"), [])
        self.assertEqual(memory.get_history("first", limit=1), [
            {"role": "assistant", "content": "answer two"},
        ])

    def test_persistence_and_clear(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.json"
            first = ConversationMemory(path, max_turns=4)
            first.add_exchange("conversation", "What is Timeout?", "An attribute.")

            second = ConversationMemory(path, max_turns=4)
            self.assertEqual(second.get_history("conversation"), [
                {"role": "user", "content": "What is Timeout?"},
                {"role": "assistant", "content": "An attribute."},
            ])

            second.clear("conversation")
            self.assertEqual(second.get_history("conversation"), [])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["conversations"], {})

    def test_history_is_returned_as_a_copy(self):
        memory = ConversationMemory()
        memory.add_user_turn(None, "original")

        history = memory.get_history()
        history[0]["content"] = "mutated"

        self.assertEqual(memory.get_history(), [
            {"role": "user", "content": "original"},
        ])


if __name__ == "__main__":
    unittest.main()
