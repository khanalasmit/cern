"""
test_validator.py — Unit tests for validator module
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from oksquery_translator.validator import (
    syntax_precheck,
    SExpressionTokenizer,
    ValidationResult,
)


class TestSExpressionTokenizer:
    """Test the S-expression tokenizer."""

    def test_simple_query(self):
        tokens = SExpressionTokenizer().tokenize('(all ("InitTimeout" "2" >))')
        assert tokens == ['(', 'all', '(', '"InitTimeout"', '"2"', '>', ')', ')']

    def test_nested_query(self):
        tokens = SExpressionTokenizer().tokenize(
            '(all (and ("InitTimeout" "30" =) ("ExitTimeout" "5" =)))'
        )
        assert '(' in tokens
        assert 'and' in tokens
        assert '"InitTimeout"' in tokens
        assert '"ExitTimeout"' in tokens

    def test_object_id(self):
        tokens = SExpressionTokenizer().tokenize(
            '(all (object-id "test_dummy" =))'
        )
        assert 'object-id' in tokens
        assert '"test_dummy"' in tokens

    def test_relationship(self):
        tokens = SExpressionTokenizer().tokenize(
            '(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))'
        )
        assert '"RunsOn"' in tokens
        assert 'some' in tokens

    def test_unterminated_string_raises(self):
        from oksquery_translator.validator import SyntaxCheckError
        with pytest.raises(SyntaxCheckError, match="Unterminated"):
            SExpressionTokenizer().tokenize('(all ("Name "test" =))')


class TestSyntaxPrecheck:
    """Test the local syntax pre-check."""

    def test_valid_simple_query(self):
        result = syntax_precheck('(all ("InitTimeout" "2" >))')
        assert result.valid

    def test_valid_and_query(self):
        result = syntax_precheck(
            '(all (and ("InitTimeout" "30" =) ("ExitTimeout" "5" =)))'
        )
        assert result.valid

    def test_valid_or_query(self):
        result = syntax_precheck(
            '(all (or ("Name" "app1" =) ("Name" "app2" =)))'
        )
        assert result.valid

    def test_valid_not_query(self):
        result = syntax_precheck('(all (not ("Name" "test" =)))')
        assert result.valid

    def test_valid_relationship(self):
        result = syntax_precheck(
            '(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))'
        )
        assert result.valid

    def test_valid_this_scope(self):
        result = syntax_precheck('(this ("Name" "test" =))')
        assert result.valid

    def test_empty_query(self):
        result = syntax_precheck("")
        assert not result.valid
        assert "Empty" in result.message

    def test_unbalanced_open_paren(self):
        result = syntax_precheck('(all ("InitTimeout" "2" >)')
        assert not result.valid
        assert "Unbalanced" in result.message

    def test_unbalanced_close_paren(self):
        result = syntax_precheck('(all ("InitTimeout" "2" >)))')
        assert not result.valid
        assert "Unbalanced" in result.message

    def test_missing_scope(self):
        result = syntax_precheck('("InitTimeout" "2" >)')
        assert not result.valid
        assert "scope" in result.message.lower()

    def test_wrong_scope_token(self):
        result = syntax_precheck('(every ("InitTimeout" "2" >))')
        assert not result.valid
        assert "scope" in result.message.lower()

    def test_and_with_one_operand(self):
        result = syntax_precheck('(all (and ("InitTimeout" "2" >)))')
        assert not result.valid
        assert "and" in result.message.lower()

    def test_not_with_two_operands(self):
        result = syntax_precheck(
            '(all (not ("Name" "a" =) ("Name" "b" =)))'
        )
        assert not result.valid
        assert "not" in result.message.lower()

    def test_valid_nested_relationship_query(self):
        """Test a complex nested relationship query."""
        result = syntax_precheck(
            '(all ("Configurations" some ("SourceServers" some (object-id "DF_IS" =))))'
        )
        assert result.valid

    def test_valid_regex_query(self):
        result = syntax_precheck('(all ("Name" ".*lxplus.*" ~=))')
        assert result.valid

    def test_valid_match_all_pattern(self):
        result = syntax_precheck('(all (object-id "" !=))')
        assert result.valid


class TestValidationResult:
    """Test the ValidationResult dataclass."""

    def test_valid_result(self):
        r = ValidationResult(valid=True)
        assert r.valid
        assert r.error_type == ""
        assert r.message == ""

    def test_invalid_result(self):
        r = ValidationResult(
            valid=False, error_type="syntax", message="bad parens"
        )
        assert not r.valid
        assert r.error_type == "syntax"
        assert "bad parens" in r.message


class TestAlignQueryToSchema:
    """Test automatic schema alignment and case-correction."""

    def test_format_tokens(self):
        from oksquery_translator.validator import format_tokens
        tokens = ['(', 'all', '(', '"SubDetector"', '"PMT"', '=', ')', ')']
        assert format_tokens(tokens) == '(all ("SubDetector" "PMT" =))'

    def test_align_query_casing_with_mock_schema(self):
        from oksquery_translator.validator import align_query_to_schema
        from unittest.mock import MagicMock

        mock_retriever = MagicMock()
        mock_retriever.get_class_list.return_value = ["ReadoutApplication", "BaseApplication"]
        mock_retriever.get_class_info.return_value = {
            "name": "ReadoutApplication",
            "attributes": [
                {"name": "SubDetector", "type": "enum", "range": "PMT,WireChamber"},
                {"name": "Id", "type": "u16"},
            ],
            "relationships": [
                {"name": "RunsOn", "target_class": "Computer"}
            ]
        }

        # Query with lowercase 'd' in Subdetector and lowercase 'pmt'
        target_cls, aligned_q = align_query_to_schema(
            "readoutapplication", '(all ("Subdetector" "pmt" =))', mock_retriever
        )

        assert target_cls == "ReadoutApplication"
        assert aligned_q == '(all ("SubDetector" "PMT" =))'

