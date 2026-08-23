"""
test_pipeline.py — Integration tests for the pipeline
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from oksquery_translator.translator import Translator
from oksquery_translator.pipeline import OksPipeline


class TestTranslatorParsing:
    """Test the LLM response parsing logic."""

    def test_parse_clean_response(self):
        """Standard CLASS/QUERY format should parse correctly."""
        text = "CLASS: Executable\nQUERY: (all (\"InitTimeout\" \"2\" >))"
        cls, query = Translator._parse_response(text)
        assert cls == "Executable"
        assert query == '(all ("InitTimeout" "2" >))'

    def test_parse_with_extra_whitespace(self):
        """Extra whitespace/blank lines should be handled."""
        text = "\n  CLASS:  BaseApplication  \n\n  QUERY:  (all (\"Name\" \"test\" =))  \n"
        cls, query = Translator._parse_response(text)
        assert cls == "BaseApplication"
        assert query == '(all ("Name" "test" =))'

    def test_parse_with_markdown_fences(self):
        """Markdown code fences should be stripped."""
        text = "```\nCLASS: Executable\nQUERY: (all (\"InitTimeout\" \"2\" >))\n```"
        cls, query = Translator._parse_response(text)
        assert cls == "Executable"
        assert query == '(all ("InitTimeout" "2" >))'

    def test_parse_case_insensitive_labels(self):
        """Should handle Class: and Query: (different case)."""
        text = "Class: Executable\nQuery: (all (\"InitTimeout\" \"2\" >))"
        cls, query = Translator._parse_response(text)
        assert cls == "Executable"
        assert query == '(all ("InitTimeout" "2" >))'

    def test_parse_missing_class(self):
        """Missing CLASS line should return None for class."""
        text = "QUERY: (all (\"InitTimeout\" \"2\" >))"
        cls, query = Translator._parse_response(text)
        assert cls is None
        assert query is not None

    def test_parse_garbage(self):
        """Complete garbage should return None for both."""
        text = "I'm an AI and I can't do that."
        cls, query = Translator._parse_response(text)
        assert cls is None
        assert query is None


class TestPipelineInit:
    """Test that the pipeline can initialise."""

    def test_pipeline_creates(self):
        """Pipeline should initialise without errors."""
        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        # This should not raise, even without TDAQ env
        pipeline = OksPipeline(repo_root=repo_root)
        assert pipeline is not None
        assert pipeline.few_shot_manager.get_example_count() > 0
