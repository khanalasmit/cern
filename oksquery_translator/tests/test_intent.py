"""
test_intent.py — Unit tests for intent classification and run extraction
"""
import os
import sys
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from oksquery_translator.intent import (
    Intent,
    IntentResult,
    IntentClassifier,
    extract_run_and_partition,
    MSG_GENERAL_OUT_OF_SCOPE,
    MSG_CERN_OUT_OF_SCOPE,
    MSG_HISTORICAL_MISSING_RUN,
)


class TestRunNumberAndPartitionExtraction:
    """Test deterministic run number and partition extraction regexes."""

    def test_r_tag_with_partition(self):
        run, part, tag = extract_run_and_partition("What was the configuration for r380689@all_hosts?")
        assert run == 380689
        assert part == "all_hosts"
        assert tag == "tag:r380689@all_hosts"

    def test_r_tag_with_atlas_partition(self):
        run, part, tag = extract_run_and_partition("Check settings in r380689@ATLAS")
        assert run == 380689
        assert part == "ATLAS"
        assert tag == "tag:r380689@ATLAS"

    def test_standalone_r_tag(self):
        run, part, tag = extract_run_and_partition("Check r380689 parameters")
        assert run == 380689
        assert part == "all_hosts"
        assert tag == "tag:r380689@all_hosts"

    def test_run_keyword_lower(self):
        run, part, tag = extract_run_and_partition("What was InitTimeout in run 380689?")
        assert run == 380689
        assert part == "all_hosts"
        assert tag == "tag:r380689@all_hosts"

    def test_run_keyword_capitalized(self):
        run, part, tag = extract_run_and_partition("What host did ROS run on in Run 380689?")
        assert run == 380689
        assert part == "all_hosts"
        assert tag == "tag:r380689@all_hosts"

    def test_run_number_phrase(self):
        run, part, tag = extract_run_and_partition("Show computers for run number 380689")
        assert run == 380689
        assert part == "all_hosts"
        assert tag == "tag:r380689@all_hosts"

    def test_run_number_assignment(self):
        run, part, tag = extract_run_and_partition("Find config with run_number=380689")
        assert run == 380689
        assert part == "all_hosts"
        assert tag == "tag:r380689@all_hosts"

    def test_run_number_with_partition_suffix(self):
        run, part, tag = extract_run_and_partition("Find config in run 380689@ATLAS")
        assert run == 380689
        assert part == "ATLAS"
        assert tag == "tag:r380689@ATLAS"

    def test_negative_ram_question(self):
        """Should NOT extract '32' as a run number."""
        run, part, tag = extract_run_and_partition("Which host has 32 GB RAM?")
        assert run is None
        assert tag is None

    def test_negative_verb_run_question(self):
        """Should NOT treat 'run on host' as a run number."""
        run, part, tag = extract_run_and_partition("Which applications run on host lxplus001?")
        assert run is None
        assert tag is None

    def test_negative_vague_historical(self):
        """Vague temporal questions have no extracted run number."""
        run, part, tag = extract_run_and_partition("What configuration was used in the previous run?")
        assert run is None
        assert tag is None


class TestIntentClassifierWithMockLLM:
    """Test IntentClassifier with mocked OpenAI responses."""

    @pytest.fixture
    def classifier(self):
        return IntentClassifier(llm_api_key="test_key")

    def _mock_llm_response(self, intent: str, run_number=None, partition=None):
        mock_resp = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = f'{{"intent": "{intent}", "run_number": {("null" if run_number is None else run_number)}, "partition": {("\"" + partition + "\"" if partition else "null")}}}'
        mock_resp.choices = [mock_choice]
        return mock_resp

    def test_current_query_ros(self, classifier):
        with patch.object(classifier.client.chat.completions, "create",
                          return_value=self._mock_llm_response("OKS_CURRENT_QUERY")):
            res = classifier.classify("Which hosts run ROSDescriptor?")
            assert res.intent == Intent.OKS_CURRENT_QUERY
            assert res.run_number is None
            assert res.version_tag is None
            assert res.message is None

    def test_current_query_computers(self, classifier):
        with patch.object(classifier.client.chat.completions, "create",
                          return_value=self._mock_llm_response("OKS_CURRENT_QUERY")):
            res = classifier.classify("List all computers.")
            assert res.intent == Intent.OKS_CURRENT_QUERY
            assert res.run_number is None
            assert res.version_tag is None

    def test_current_query_ram(self, classifier):
        with patch.object(classifier.client.chat.completions, "create",
                          return_value=self._mock_llm_response("OKS_CURRENT_QUERY")):
            res = classifier.classify("Which host has 32 GB RAM?")
            assert res.intent == Intent.OKS_CURRENT_QUERY
            assert res.run_number is None
            assert res.version_tag is None

    def test_historical_query_with_run_number(self, classifier):
        with patch.object(classifier.client.chat.completions, "create",
                          return_value=self._mock_llm_response("OKS_HISTORICAL_QUERY", 380689, "all_hosts")):
            res = classifier.classify("What was InitTimeout in run 380689?")
            assert res.intent == Intent.OKS_HISTORICAL_QUERY
            assert res.run_number == 380689
            assert res.partition == "all_hosts"
            assert res.version_tag == "tag:r380689@all_hosts"
            assert res.message is None

    def test_historical_query_with_partition(self, classifier):
        with patch.object(classifier.client.chat.completions, "create",
                          return_value=self._mock_llm_response("OKS_HISTORICAL_QUERY", 380689, "all_hosts")):
            res = classifier.classify("What was the configuration for r380689@all_hosts?")
            assert res.intent == Intent.OKS_HISTORICAL_QUERY
            assert res.run_number == 380689
            assert res.partition == "all_hosts"
            assert res.version_tag == "tag:r380689@all_hosts"

    def test_historical_query_missing_run_number(self, classifier):
        with patch.object(classifier.client.chat.completions, "create",
                          return_value=self._mock_llm_response("OKS_HISTORICAL_QUERY", None, None)):
            res = classifier.classify("What configuration was used in the previous run?")
            assert res.intent == Intent.OKS_HISTORICAL_QUERY
            assert res.run_number is None
            assert res.version_tag is None
            assert res.message == MSG_HISTORICAL_MISSING_RUN

    def test_cern_out_of_scope_cm_setup(self, classifier):
        with patch.object(classifier.client.chat.completions, "create",
                          return_value=self._mock_llm_response("CERN_OUT_OF_SCOPE")):
            res = classifier.classify("How do I run cm_setup?")
            assert res.intent == Intent.CERN_OUT_OF_SCOPE
            assert res.message == MSG_CERN_OUT_OF_SCOPE

    def test_cern_out_of_scope_restart_partition(self, classifier):
        with patch.object(classifier.client.chat.completions, "create",
                          return_value=self._mock_llm_response("CERN_OUT_OF_SCOPE")):
            res = classifier.classify("Restart the ATLAS DAQ partition.")
            assert res.intent == Intent.CERN_OUT_OF_SCOPE
            assert res.message == MSG_CERN_OUT_OF_SCOPE

    def test_general_out_of_scope_cake(self, classifier):
        with patch.object(classifier.client.chat.completions, "create",
                          return_value=self._mock_llm_response("GENERAL_OUT_OF_SCOPE")):
            res = classifier.classify("What is the recipe for chocolate cake?")
            assert res.intent == Intent.GENERAL_OUT_OF_SCOPE
            assert res.message == MSG_GENERAL_OUT_OF_SCOPE


class TestHeuristicFallback:
    """Test heuristic fallback when LLM call encounters exception."""

    @pytest.fixture
    def classifier(self):
        return IntentClassifier(llm_api_key="test_key")

    def test_general_out_of_scope_fallback(self, classifier):
        with patch.object(classifier.client.chat.completions, "create", side_effect=Exception("API down")):
            res = classifier.classify("What is the recipe for chocolate cake?")
            assert res.intent == Intent.GENERAL_OUT_OF_SCOPE
            assert res.message == MSG_GENERAL_OUT_OF_SCOPE

    def test_cern_out_of_scope_fallback(self, classifier):
        with patch.object(classifier.client.chat.completions, "create", side_effect=Exception("API down")):
            res = classifier.classify("How do I run cm_setup?")
            assert res.intent == Intent.CERN_OUT_OF_SCOPE
            assert res.message == MSG_CERN_OUT_OF_SCOPE

    def test_historical_with_run_fallback(self, classifier):
        with patch.object(classifier.client.chat.completions, "create", side_effect=Exception("API down")):
            res = classifier.classify("What was InitTimeout in run 380689?")
            assert res.intent == Intent.OKS_HISTORICAL_QUERY
            assert res.run_number == 380689
            assert res.version_tag == "tag:r380689@all_hosts"

    def test_historical_missing_run_fallback(self, classifier):
        with patch.object(classifier.client.chat.completions, "create", side_effect=Exception("API down")):
            res = classifier.classify("What configuration was used in the previous run?")
            assert res.intent == Intent.OKS_HISTORICAL_QUERY
            assert res.run_number is None
            assert res.message == MSG_HISTORICAL_MISSING_RUN

    def test_current_query_fallback(self, classifier):
        with patch.object(classifier.client.chat.completions, "create", side_effect=Exception("API down")):
            res = classifier.classify("Which applications are configured?")
            assert res.intent == Intent.OKS_CURRENT_QUERY
            assert res.run_number is None
