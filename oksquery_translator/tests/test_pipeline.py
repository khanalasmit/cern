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


class TestPipelineIntentIntegration:
    """Test the end-to-end intent classification and routing inside OksPipeline."""

    @pytest.fixture
    def mock_pipeline(self):
        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        pipeline = OksPipeline(repo_root=repo_root)
        pipeline.translator.translate = MagicMock(return_value={
            "status": "success",
            "target_class": "Computer",
            "oks_query": '(all (object-id "" !=))',
            "attempts": 1
        })
        pipeline.executor.execute = MagicMock(return_value=MagicMock(
            success=True,
            objects=[{"id": "lxplus001", "attributes": {}}],
            count=1,
            message=""
        ))
        pipeline.interpreter.interpret = MagicMock(return_value="Found 1 Computer object: lxplus001")
        return pipeline

    def test_current_query_execution_path(self, mock_pipeline):
        """OKS_CURRENT_QUERY should call translator and executor with current config."""
        res = mock_pipeline.answer("List all computers.")
        assert res["status"] == "success"
        assert res["intent"] == "OKS_CURRENT_QUERY"
        assert res["run_number"] is None
        assert res["version_used"] == "current"
        assert "Configuration: Current / Default (HEAD)" in res["answer"]
        mock_pipeline.translator.translate.assert_called_once()
        assert mock_pipeline.translator.translate.call_args[0][0] == "List all computers."
        mock_pipeline.executor.execute.assert_called_once()
        assert mock_pipeline.executor.execute.call_args[1]["version"] is None

    def test_structured_result_skips_interpretation(self, mock_pipeline):
        """MCP mode returns structured results without a second LLM call."""
        res = mock_pipeline.answer("List all computers.", interpret=False)
        assert res["status"] == "success"
        assert res["answer"] == ""
        assert res["version_used"] == "current"
        assert res["results"] == [{"id": "lxplus001", "attributes": {}}]
        mock_pipeline.interpreter.interpret.assert_not_called()

    def test_historical_query_with_run_number(self, mock_pipeline):
        """OKS_HISTORICAL_QUERY with valid run number resolves version and executes."""
        mock_pipeline.run_resolver.validate_run_number = MagicMock(return_value=True)
        res = mock_pipeline.answer("What was InitTimeout in run 380689?")
        assert res["status"] == "success"
        assert res["intent"] == "OKS_HISTORICAL_QUERY"
        assert res["run_number"] == 380689
        assert res["partition"] == "all_hosts"
        assert res["version_used"] == "tag:r380689@all_hosts"
        mock_pipeline.translator.translate.assert_called_once()
        mock_pipeline.executor.execute.assert_called_once()
        assert mock_pipeline.executor.execute.call_args[1]["version"] == "tag:r380689@all_hosts"

    def test_historical_query_uses_recorded_release_and_data_file(self, mock_pipeline):
        mock_pipeline.run_resolver.validate_run_number = MagicMock(return_value=True)
        mock_pipeline.run_resolver.resolve_version = MagicMock(
            return_value="hash:c85894a53e0e17911015fbefdfce33679f41e2ff"
        )
        mock_pipeline.run_resolver.get_run_info = MagicMock(return_value={
            "partition": "part_TGC_FillTest",
            "release": "tdaq-11-02-01",
            "version": "hash:c85894a53e0e17911015fbefdfce33679f41e2ff",
            "config_name": "muons/partitions/part_TGC_FillTest.data.xml",
        })

        res = mock_pipeline.answer("List all Computer objects in run no 468836")

        assert res["status"] == "success"
        kwargs = mock_pipeline.executor.execute.call_args.kwargs
        assert kwargs["release"] == "tdaq-11-02-01"
        assert kwargs["data_file"] == "muons/partitions/part_TGC_FillTest.data.xml"


    def test_legacy_run_stops_before_translation_or_execution(self, mock_pipeline):
        """Unsupported archive revisions must never fall through to HEAD."""
        mock_pipeline.run_resolver.validate_run_number = MagicMock(return_value=True)
        mock_pipeline.run_resolver.resolve_version = MagicMock(return_value=None)
        mock_pipeline.run_resolver.get_run_info = MagicMock(return_value={
            "version": "46.97", "partition": "all_hosts",
            "config_name": "daq/segments/setup.data.xml",
        })

        res = mock_pipeline.answer("give me all objects of run no 45567")

        assert res["status"] == "error"
        assert "legacy archive revision '46.97'" in res["answer"]
        mock_pipeline.translator.translate.assert_not_called()
        mock_pipeline.executor.execute.assert_not_called()

    def test_all_objects_enumerates_classes_without_llm_class_guess(self, mock_pipeline):
        mock_pipeline.schema_retriever.get_class_list = MagicMock(
            return_value=["Computer", "Application"]
        )
        mock_pipeline.executor.execute = MagicMock(side_effect=[
            MagicMock(success=True, count=1, objects=[{"id": "pc01", "class": "Computer", "attributes": {}}]),
            MagicMock(success=True, count=1, objects=[{"id": "app01", "class": "Application", "attributes": {}}]),
        ])

        res = mock_pipeline.answer("give me all objects")

        assert res["status"] == "success"
        assert res["target_class"] == "*"
        assert res["result_count"] == 2
        assert {obj["class"] for obj in res["results"]} == {"Computer", "Application"}
        mock_pipeline.translator.translate.assert_not_called()
        assert mock_pipeline.executor.execute.call_count == 2

    def test_historical_query_missing_run_number(self, mock_pipeline):
        """OKS_HISTORICAL_QUERY with missing run stops before translation/execution."""
        res = mock_pipeline.answer("What configuration was used in the previous run?")
        assert res["status"] == "error"
        assert res["intent"] == "OKS_HISTORICAL_QUERY"
        assert res["run_number"] is None
        assert "did not specify a run number" in res["answer"]
        mock_pipeline.translator.translate.assert_not_called()
        mock_pipeline.executor.execute.assert_not_called()

    def test_historical_query_invalid_run_number(self, mock_pipeline):
        """OKS_HISTORICAL_QUERY with invalid run number is rejected and halts."""
        mock_pipeline.run_resolver.validate_run_number = MagicMock(return_value=False)
        res = mock_pipeline.answer("What was X in run 9999999?")
        assert res["status"] == "error"
        assert res["intent"] == "OKS_HISTORICAL_QUERY"
        assert res["run_number"] == 9999999
        assert "not found in the CERN Run Number Database or Git tags" in res["answer"]
        mock_pipeline.translator.translate.assert_not_called()
        mock_pipeline.executor.execute.assert_not_called()

    def test_general_out_of_scope_bypasses_pipeline(self, mock_pipeline):
        """GENERAL_OUT_OF_SCOPE exits immediately without calling translator/executor."""
        res = mock_pipeline.answer("What is the recipe for chocolate cake?")
        assert res["status"] == "error"
        assert res["intent"] == "GENERAL_OUT_OF_SCOPE"
        assert "cannot help with general questions" in res["answer"]
        mock_pipeline.translator.translate.assert_not_called()
        mock_pipeline.executor.execute.assert_not_called()

    def test_cern_out_of_scope_bypasses_pipeline(self, mock_pipeline):
        """CERN_OUT_OF_SCOPE exits immediately without calling translator/executor."""
        res = mock_pipeline.answer("Restart the ATLAS DAQ partition.")
        assert res["status"] == "error"
        assert res["intent"] == "CERN_OUT_OF_SCOPE"
        assert "cannot execute DAQ control commands" in res["answer"]
        mock_pipeline.translator.translate.assert_not_called()
        mock_pipeline.executor.execute.assert_not_called()

    def test_version_conflict_detection(self, mock_pipeline):
        """Conflict between question run number and caller's explicit version parameter is caught."""
        res = mock_pipeline.answer("What was InitTimeout in run 380689?", version="tag:r380700@all_hosts")
        assert res["status"] == "error"
        assert "Version conflict detected" in res["answer"]
        mock_pipeline.translator.translate.assert_not_called()
        mock_pipeline.executor.execute.assert_not_called()

    def test_run_number_appears_in_final_output_explicit_run(self, mock_pipeline):
        """Historical answer MUST contain 'Run Number: 380689' in the answer text and metadata."""
        mock_pipeline.run_resolver.validate_run_number = MagicMock(return_value=True)
        res = mock_pipeline.answer("What was InitTimeout in run 380689?")
        assert res["status"] == "success"
        assert res["run_number"] == 380689
        assert "Run Number: 380689" in res["answer"]
        assert "Partition: all_hosts" in res["answer"]
        assert res["version"] == "tag:r380689@all_hosts"

    def test_run_number_appears_in_final_output_git_tag(self, mock_pipeline):
        """Historical answer with r<run>@<part> MUST contain Run Number and Partition in text and metadata."""
        mock_pipeline.run_resolver.validate_run_number = MagicMock(return_value=True)
        res = mock_pipeline.answer("What was X using r380689@all_hosts?")
        assert res["status"] == "success"
        assert res["run_number"] == 380689
        assert res["partition"] == "all_hosts"
        assert "Run Number: 380689" in res["answer"]
        assert "Partition: all_hosts" in res["answer"]

    def test_run_number_recovered_from_internally_resolved_version(self, mock_pipeline):
        """If resolver returns tag:r380689@all_hosts, final response exposes run_number and header."""
        mock_pipeline.run_resolver.validate_run_number = MagicMock(return_value=True)
        mock_pipeline.run_resolver.resolve_version = MagicMock(return_value="tag:r380689@all_hosts")
        res = mock_pipeline.answer("What was X in run 380689?")
        assert res["status"] == "success"
        assert res["run_number"] == 380689
        assert "Run Number: 380689" in res["answer"]

    def test_no_accidental_head_fallback_missing_run(self, mock_pipeline):
        """CRITICAL: Historical query without run number NEVER calls translator or executor."""
        res = mock_pipeline.answer("What was the configuration in the previous run?")
        assert res["status"] == "error"
        assert res["version_used"] is None
        mock_pipeline.translator.translate.assert_not_called()
        mock_pipeline.executor.execute.assert_not_called()

    def test_no_accidental_head_fallback_invalid_run(self, mock_pipeline):
        """CRITICAL: Historical query with invalid run number NEVER calls translator or executor."""
        mock_pipeline.run_resolver.validate_run_number = MagicMock(return_value=False)
        res = mock_pipeline.answer("What was X in run 9999999?")
        assert res["status"] == "error"
        assert res["version_used"] is None
        mock_pipeline.translator.translate.assert_not_called()
        mock_pipeline.executor.execute.assert_not_called()
