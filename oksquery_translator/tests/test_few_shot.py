"""
test_few_shot.py — Unit tests for few_shot module
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from oksquery_translator.few_shot import FewShotManager, _BUILTIN_EXAMPLES


class TestFewShotDiscovery:
    """Test example discovery and loading."""

    @pytest.fixture
    def manager(self):
        """Create a FewShotManager pointed at the repo root."""
        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        return FewShotManager(repo_root=repo_root)

    def test_examples_loaded(self, manager):
        """At least some examples should be loaded."""
        assert manager.get_example_count() > 0

    def test_examples_have_question_and_query(self, manager):
        """Each example should have question and query_oks fields."""
        for ex in manager.examples[:10]:
            assert "question" in ex and ex["question"]
            assert "query_oks" in ex and ex["query_oks"]

    def test_get_examples_returns_string(self, manager):
        """get_examples should return a formatted string."""
        result = manager.get_examples("Which executables have timeout > 2?")
        assert isinstance(result, str)
        assert "Q:" in result
        assert "A:" in result

    def test_get_examples_respects_top_k(self, manager):
        """Should return at most top_k examples."""
        result = manager.get_examples("test", top_k=2)
        # Count the number of "Q:" lines
        q_count = result.count("Q:")
        assert q_count <= 2


class TestFewShotBuiltinFallback:
    """Test that built-in examples work when no files found."""

    def test_builtin_examples_valid(self):
        """Built-in examples should have the required fields."""
        for ex in _BUILTIN_EXAMPLES:
            assert "question" in ex
            assert "query_oks" in ex
            assert "target_class" in ex

    def test_fallback_when_no_repo(self):
        """When pointed at a non-existent directory, should use built-ins."""
        manager = FewShotManager(repo_root="/nonexistent/path/xyz")
        assert manager.get_example_count() == len(_BUILTIN_EXAMPLES)

    def test_fallback_get_examples(self):
        """Fallback examples should still return formatted output."""
        manager = FewShotManager(repo_root="/nonexistent/path/xyz")
        result = manager.get_examples("test")
        assert "Q:" in result
