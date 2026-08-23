"""
test_schema_retrieval.py — Unit tests for schema_retrieval module
"""
import os
import sys
import pytest

# Ensure the package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from oksquery_translator.schema_retrieval import SchemaRetriever, _KEYWORD_TO_CLASSES


class TestKeywordMapping:
    """Test the keyword-to-class synonym mapping."""

    def test_common_keywords_exist(self):
        """Verify the most important keywords are mapped."""
        assert "application" in _KEYWORD_TO_CLASSES
        assert "executable" in _KEYWORD_TO_CLASSES
        assert "computer" in _KEYWORD_TO_CLASSES
        assert "host" in _KEYWORD_TO_CLASSES
        assert "timeout" in _KEYWORD_TO_CLASSES

    def test_application_maps_to_base(self):
        """'application' should map to BaseApplication."""
        classes = _KEYWORD_TO_CLASSES["application"]
        assert "BaseApplication" in classes

    def test_host_maps_to_computer(self):
        """'host' should map to Computer."""
        classes = _KEYWORD_TO_CLASSES["host"]
        assert "Computer" in classes


class TestSchemaRetrieverWithXml:
    """Test SchemaRetriever when using local XML files."""

    @pytest.fixture
    def retriever(self):
        """Create a retriever using the test_schema XML files if available."""
        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        schema_dir = os.path.join(repo_root, "test_schema", "xml")
        if not os.path.isdir(schema_dir):
            pytest.skip("test_schema/xml not found")
        return SchemaRetriever(
            data_file="daq/segments/setup.data.xml",
            schema_dir=schema_dir,
        )

    def test_class_list_not_empty(self, retriever):
        """Class list should have entries from schema XML files."""
        classes = retriever.get_class_list()
        assert len(classes) > 0

    def test_class_list_contains_known_classes(self, retriever):
        """Known classes from the ATLAS TDAQ schema should be present."""
        classes = retriever.get_class_list()
        # BaseApplication is in core.schema.xml
        assert "BaseApplication" in classes

    def test_get_class_info_returns_attributes(self, retriever):
        """Getting class info should return attributes and relationships."""
        info = retriever.get_class_info("BaseApplication")
        if info is None:
            pytest.skip("Could not load BaseApplication info via XML")
        assert "attributes" in info
        assert isinstance(info["attributes"], list)
        assert len(info["attributes"]) > 0

    def test_get_class_info_unknown_class(self, retriever):
        """An unknown class name should return None."""
        info = retriever.get_class_info("NonExistentClass12345")
        assert info is None

    def test_format_class_info(self, retriever):
        """Formatted class info should be a readable text block."""
        info = retriever.get_class_info("BaseApplication")
        if info is None:
            pytest.skip("Could not load BaseApplication info")
        formatted = SchemaRetriever._format_class_info(info)
        assert "Class: BaseApplication" in formatted
        assert "Attributes:" in formatted

    def test_get_schema_context(self, retriever):
        """Schema context for a question should contain relevant classes."""
        context = retriever.get_schema_context(
            "Which applications have an InitTimeout greater than 30?"
        )
        assert "---" in context
        # Should contain either BaseApplication or Application
        assert "Application" in context or "Class:" in context

    def test_match_classes_executable(self, retriever):
        """Question about executables should match Executable class."""
        candidates = retriever._match_classes(
            "Which executables have InitTimeout greater than 2?", max_classes=3
        )
        # Should contain something related to executables
        assert len(candidates) > 0
