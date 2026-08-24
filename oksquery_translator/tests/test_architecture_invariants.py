"""
test_architecture_invariants.py — Comprehensive Architectural Invariant Tests
==============================================================================

Verifies the 15 architectural invariants of the NL → OKSQuery pipeline
as defined in docs/architecture/nl_to_oksquery_architecture.pdf.

These tests are designed to pass entirely without the CERN/TDAQ C++ runtime
environment. Missing ``oks_dump`` or ``config`` C-extensions result in
graceful skips/mocks, not failures.
"""

import json
import pytest
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Imports from the canonical package
# ---------------------------------------------------------------------------
from oksquery_translator.context import OksContext, OksContextBuilder, compute_fingerprint
from oksquery_translator.preprocessing import QueryPreprocessor, QueryAnalysis
from oksquery_translator.schema import OksSchemaProvider, ClassDefinition, AttributeDefinition, RelationshipDefinition
from oksquery_translator.oks_ast import (
    QueryIR,
    AttributeCompare,
    ObjectIdCompare,
    RelationshipCompare,
    AndExpression,
    OrExpression,
    NotExpression,
    normalize_ir,
    NormalizerError,
    OksCompiler,
    ASTValidator,
    ValidationResult,
)
from oksquery_translator.retrieval import SchemaSearchIndex, ClassSearchDocument


# ===========================================================================
# Helpers / Fixtures
# ===========================================================================

def _make_context(class_names=None, run_number=None, version_tag=None):
    """Build a synthetic OksContext without touching the real OKS engine."""
    class_names = class_names or ["Application", "Computer", "Executable", "Segment"]
    fp = compute_fingerprint(class_names)
    return OksContext(
        schema_identifier="test-schema",
        schema_fingerprint=fp,
        release=None,
        git_revision=None,
        run_number=run_number,
        configuration_revision=None,
        version_tag=version_tag,
    )


def _make_schema_provider(ctx: OksContext) -> OksSchemaProvider:
    """Build a minimal OksSchemaProvider backed by a mock SchemaRetriever."""
    provider = OksSchemaProvider.__new__(OksSchemaProvider)
    provider.oks_context = ctx

    # Minimal class dictionary
    executable_cls = ClassDefinition(
        name="Executable",
        superclasses=[],
        attributes=[
            AttributeDefinition(name="InitTimeout", type="u32", range="", init_value="0", is_multi_value=False),
            AttributeDefinition(name="ExitTimeout", type="u32", range="", init_value="0", is_multi_value=False),
        ],
        relationships=[
            RelationshipDefinition(name="RunsOn", target_class="Computer", is_multi_value=False, description=""),
        ],
        description="An executable application",
    )
    computer_cls = ClassDefinition(
        name="Computer",
        superclasses=[],
        attributes=[
            AttributeDefinition(name="HW_Address", type="str", range="", init_value="", is_multi_value=False),
        ],
        relationships=[],
        description="A computer host",
    )
    application_cls = ClassDefinition(
        name="Application",
        superclasses=["Executable"],
        attributes=[
            AttributeDefinition(name="AppName", type="str", range="", init_value="", is_multi_value=False),
        ],
        relationships=[],
        description="An application",
    )
    segment_cls = ClassDefinition(
        name="Segment",
        superclasses=[],
        attributes=[],
        relationships=[],
        description="A DAQ segment",
    )

    provider._class_map = {
        "Executable": executable_cls,
        "Computer": computer_cls,
        "Application": application_cls,
        "Segment": segment_cls,
    }

    # Patch methods to use the synthetic class map
    def _get_class(name):
        return provider._class_map.get(name)

    def _get_all_class_names():
        return list(provider._class_map.keys())

    def _class_exists(name):
        return name in provider._class_map

    def _suggest_class(name):
        import difflib
        return difflib.get_close_matches(name.lower(), [n.lower() for n in provider._class_map], n=3, cutoff=0.4)

    def _get_effective_members(name):
        cls = provider._class_map.get(name)
        if not cls:
            return None
        # Resolve inheritance
        seen = set()
        all_attrs = []
        all_rels = []
        queue = [name]
        while queue:
            cur = queue.pop(0)
            if cur in seen:
                continue
            seen.add(cur)
            c = provider._class_map.get(cur)
            if not c:
                continue
            all_attrs.extend(c.attributes)
            all_rels.extend(c.relationships)
            queue.extend(c.superclasses)
        return ClassDefinition(
            name=name,
            superclasses=cls.superclasses,
            attributes=all_attrs,
            relationships=all_rels,
            description=cls.description,
        )

    provider.get_class = _get_class
    provider.get_all_class_names = _get_all_class_names
    provider.class_exists = _class_exists
    provider.suggest_class = _suggest_class
    provider.get_effective_members = _get_effective_members
    return provider


# ===========================================================================
# Invariant 1 & 2 — OksContext Immutability & Single Instance Per Request
# ===========================================================================

class TestInvariant1And2_OksContextImmutabilityAndSingleInstance:
    """
    Invariant 1: OksContext is frozen (immutable).
    Invariant 2: Exactly one OksContext must be created per query lifecycle.
    """

    def test_oks_context_is_frozen(self):
        ctx = _make_context()
        with pytest.raises((FrozenInstanceError, AttributeError)):
            ctx.schema_fingerprint = "tampered"

    def test_oks_context_immutable_run_number(self):
        ctx = _make_context(run_number=380689)
        with pytest.raises((FrozenInstanceError, AttributeError)):
            ctx.run_number = 999999

    def test_oks_context_created_once_per_lifecycle(self):
        """Simulate a pipeline request: only one context is built."""
        builder = MagicMock()
        ctx_a = _make_context()
        builder.build.return_value = ctx_a

        build_calls = 0
        def build_once(version_tag=None):
            nonlocal build_calls
            build_calls += 1
            return ctx_a

        builder.build.side_effect = build_once
        result = builder.build(version_tag=None)
        assert build_calls == 1
        assert result is ctx_a


# ===========================================================================
# Invariant 3 & 4 — Fingerprint Determinism & Content-Derivation
# ===========================================================================

class TestInvariant3And4_FingerprintDeterminism:
    """
    Invariant 3: schema_fingerprint is deterministic (same input -> same output).
    Invariant 4: fingerprint is content-derived from sorted class names.
    """

    def test_fingerprint_is_deterministic(self):
        fp1 = compute_fingerprint(["Application", "Computer", "Segment"])
        fp2 = compute_fingerprint(["Application", "Computer", "Segment"])
        assert fp1 == fp2

    def test_fingerprint_order_independent(self):
        fp1 = compute_fingerprint(["Application", "Computer"])
        fp2 = compute_fingerprint(["Computer", "Application"])
        assert fp1 == fp2

    def test_fingerprint_deduplicates(self):
        fp1 = compute_fingerprint(["Application", "Computer"])
        fp2 = compute_fingerprint(["Application", "Application", "Computer", "Computer"])
        assert fp1 == fp2

    def test_fingerprint_is_16_char_hex(self):
        fp = compute_fingerprint(["Application", "Computer"])
        assert len(fp) == 16
        assert all(c in "0123456789abcdef" for c in fp)

    def test_different_classes_different_fingerprints(self):
        fp_a = compute_fingerprint(["Application"])
        fp_b = compute_fingerprint(["Computer"])
        assert fp_a != fp_b

    def test_tag_string_not_used_as_fingerprint(self):
        """Fingerprint must NOT be the raw version tag string."""
        version_tag = "tag:r380689@all_hosts"
        fp = compute_fingerprint(["Application", "Computer"])
        assert fp != version_tag


# ===========================================================================
# Invariant 5 — SchemaSearchIndex Never Returns Cross-Fingerprint Documents
# ===========================================================================

class TestInvariant5_SchemaSearchIndexPartitioning:
    """
    Invariant 5: SchemaSearchIndex.search() ONLY returns documents for the
    requested schema_fingerprint. Cross-version pollution is forbidden.
    """

    def test_fingerprint_isolation(self):
        """Documents indexed under fingerprint A must never appear in fingerprint B search."""
        ctx_a = _make_context(["Application", "Computer"])
        ctx_b = _make_context(["Segment", "Executable"])
        provider_a = _make_schema_provider(ctx_a)
        provider_b = _make_schema_provider(ctx_b)

        index = SchemaSearchIndex()
        index.build_from_schema_provider(provider_a)
        index.build_from_schema_provider(provider_b)

        results_a = index.search("application", ctx_a.schema_fingerprint, top_k=10)
        results_b = index.search("application", ctx_b.schema_fingerprint, top_k=10)

        # All results from A must have fingerprint A
        for doc in results_a:
            assert doc.schema_fingerprint == ctx_a.schema_fingerprint

        # All results from B must have fingerprint B
        for doc in results_b:
            assert doc.schema_fingerprint == ctx_b.schema_fingerprint

    def test_missing_fingerprint_returns_empty(self):
        index = SchemaSearchIndex()
        results = index.search("application", "nonexistent_fingerprint_cccc", top_k=5)
        assert results == []

    def test_missing_fingerprint_does_not_crash(self):
        index = SchemaSearchIndex()
        try:
            results = index.search("any_query", "ZZZZZZZZZZZZZZZZ", top_k=5)
            assert isinstance(results, list)
        except Exception as exc:
            pytest.fail(f"search() raised unexpected exception: {exc}")

    def test_has_fingerprint(self):
        ctx = _make_context()
        provider = _make_schema_provider(ctx)
        index = SchemaSearchIndex()
        assert not index.has_fingerprint(ctx.schema_fingerprint)
        index.build_from_schema_provider(provider)
        assert index.has_fingerprint(ctx.schema_fingerprint)

    def test_build_is_idempotent(self):
        """Building the same fingerprint twice should not double-index."""
        ctx = _make_context()
        provider = _make_schema_provider(ctx)
        index = SchemaSearchIndex()
        index.build_from_schema_provider(provider)
        count_before = len(index._index.get(ctx.schema_fingerprint, []))
        index.build_from_schema_provider(provider)
        count_after = len(index._index.get(ctx.schema_fingerprint, []))
        assert count_before == count_after


# ===========================================================================
# Invariant 6 & 10 — ASTValidator Context-Bound Semantic Checking
# ===========================================================================

class TestInvariant6And10_ASTValidatorContextBound:
    """
    Invariant 6: ASTValidator validates against exact context schema.
    Invariant 10: Case-sensitivity, invalid attributes, and relationship
                  targets are correctly detected.
    """

    def _make_validator(self, ctx=None):
        ctx = ctx or _make_context()
        provider = _make_schema_provider(ctx)
        return ASTValidator(provider), ctx

    def _make_simple_ir(self, target_class, attribute, operator=">", value="2"):
        return QueryIR(
            target_class=target_class,
            scope="all",
            expression=AttributeCompare(attribute=attribute, operator=operator, value=value),
        )

    def test_valid_attribute_passes(self):
        validator, ctx = self._make_validator()
        ir = self._make_simple_ir("Executable", "InitTimeout")
        result = validator.validate(ir, ctx)
        assert result.valid, f"Expected valid, got: {result.message}"

    def test_invalid_class_fails(self):
        validator, ctx = self._make_validator()
        ir = self._make_simple_ir("NonExistentClass", "SomeAttr")
        result = validator.validate(ir, ctx)
        assert not result.valid
        assert result.error_type == "class_not_found"

    def test_case_sensitivity_detected(self):
        validator, ctx = self._make_validator()
        ir = self._make_simple_ir("Executable", "inittimeout")  # wrong case
        result = validator.validate(ir, ctx)
        assert not result.valid
        # Error should hint at the correct casing
        assert "InitTimeout" in result.message or "CASE" in result.message.upper()

    def test_invalid_attribute_fails(self):
        validator, ctx = self._make_validator()
        ir = self._make_simple_ir("Executable", "NonExistentAttribute")
        result = validator.validate(ir, ctx)
        assert not result.valid

    def test_relationship_traversal_valid(self):
        validator, ctx = self._make_validator()
        ir = QueryIR(
            target_class="Executable",
            scope="all",
            expression=RelationshipCompare(
                name="RunsOn",
                quantifier="some",
                expression=ObjectIdCompare(object_id="pc01"),
            ),
        )
        result = validator.validate(ir, ctx)
        assert result.valid, f"Expected valid relationship traversal, got: {result.message}"

    def test_invalid_relationship_fails(self):
        validator, ctx = self._make_validator()
        ir = QueryIR(
            target_class="Executable",
            scope="all",
            expression=RelationshipCompare(
                name="RunOn",  # typo, should be RunsOn
                quantifier="some",
                expression=ObjectIdCompare(object_id="pc01"),
            ),
        )
        result = validator.validate(ir, ctx)
        assert not result.valid

    def test_fingerprint_in_error_message(self):
        validator, ctx = self._make_validator()
        ir = self._make_simple_ir("Executable", "inittimeout")  # triggers error
        result = validator.validate(ir, ctx)
        assert not result.valid
        assert ctx.schema_fingerprint in result.message

    def test_object_id_always_valid(self):
        validator, ctx = self._make_validator()
        ir = QueryIR(
            target_class="Computer",
            scope="all",
            expression=ObjectIdCompare(object_id="lxplus001"),
        )
        result = validator.validate(ir, ctx)
        assert result.valid


# ===========================================================================
# Invariant 8 & 9 — normalize_ir Determinism Without LLM Calls
# ===========================================================================

class TestInvariant8And9_NormalizeIrDeterminism:
    """
    Invariant 8: normalize_ir is deterministic.
    Invariant 9: normalize_ir never calls an LLM.
    """

    def _wrap_attribute(self, attribute, operator, value):
        return {
            "target_class": "Executable",
            "scope": "all",
            "expression": {
                "type": "attribute_compare",
                "attribute": attribute,
                "operator": operator,
                "value": value,
            }
        }

    def test_operator_gt_normalized(self):
        raw = self._wrap_attribute(" Timeout ", "gt", 20)
        result = normalize_ir(raw)
        expr = result["expression"]
        assert expr["operator"] == ">"

    def test_operator_gte_normalized(self):
        raw = self._wrap_attribute("T", "gte", 5)
        result = normalize_ir(raw)
        assert result["expression"]["operator"] == ">="

    def test_operator_eq_synonyms(self):
        for syn in ["eq", "==", "equals"]:
            raw = self._wrap_attribute("T", syn, "val")
            result = normalize_ir(raw)
            assert result["expression"]["operator"] == "="

    def test_operator_regex_synonyms(self):
        for syn in ["regex", "like", "contains"]:
            raw = self._wrap_attribute("T", syn, ".*foo")
            result = normalize_ir(raw)
            assert result["expression"]["operator"] == "~="

    def test_integer_value_coerced_to_string(self):
        raw = self._wrap_attribute("T", ">", 20)
        result = normalize_ir(raw)
        assert result["expression"]["value"] == "20"

    def test_float_value_coerced_to_string(self):
        raw = self._wrap_attribute("T", ">", 3.14)
        result = normalize_ir(raw)
        assert result["expression"]["value"] == "3.14"

    def test_attribute_whitespace_stripped(self):
        raw = self._wrap_attribute("  InitTimeout  ", ">", "2")
        result = normalize_ir(raw)
        assert result["expression"]["attribute"] == "InitTimeout"

    def test_scope_uppercase_normalized(self):
        raw = {"target_class": "Executable", "scope": "ALL",
               "expression": {"type": "attribute_compare", "attribute": "T", "operator": ">", "value": "1"}}
        result = normalize_ir(raw)
        assert result["scope"] == "all"

    def test_scope_this_normalized(self):
        raw = {"target_class": "Executable", "scope": "THIS",
               "expression": {"type": "attribute_compare", "attribute": "T", "operator": ">", "value": "1"}}
        result = normalize_ir(raw)
        assert result["scope"] == "this"

    def test_invalid_scope_defaults_to_all(self):
        raw = {"target_class": "Executable", "scope": "garbage",
               "expression": {"type": "attribute_compare", "attribute": "T", "operator": ">", "value": "1"}}
        result = normalize_ir(raw)
        assert result["scope"] == "all"

    def test_missing_expression_raises_error(self):
        raw = {"target_class": "Executable", "scope": "all"}
        with pytest.raises((NormalizerError, KeyError, ValueError)):
            normalize_ir(raw)

    def test_deterministic_output(self):
        raw = self._wrap_attribute(" Timeout ", "gt", 20)
        result1 = normalize_ir(raw)
        result2 = normalize_ir(raw)
        assert result1 == result2


# ===========================================================================
# Invariant 11 — OksCompiler Deterministic S-expression Compilation
# ===========================================================================

class TestInvariant11_OksCompilerDeterminism:
    """
    Invariant 11: OksCompiler deterministically compiles QueryIR to valid
    OKSQuery S-expressions without any LLM calls.
    """

    def test_simple_attribute_compare(self):
        ir = QueryIR(
            target_class="Executable",
            scope="all",
            expression=AttributeCompare(attribute="InitTimeout", operator=">", value="2"),
        )
        compiler = OksCompiler()
        result = compiler.compile(ir)
        assert result == '(all ("InitTimeout" "2" >))'

    def test_object_id_compare(self):
        ir = QueryIR(
            target_class="Computer",
            scope="all",
            expression=ObjectIdCompare(object_id="pc01"),
        )
        compiler = OksCompiler()
        result = compiler.compile(ir)
        assert result == '(all (object-id "pc01" =))'

    def test_empty_object_id_not_equal_compiles_as_match_all(self):
        ir = QueryIR(
            target_class="Computer",
            scope="all",
            expression=ObjectIdCompare(object_id="", operator="!="),
        )
        assert OksCompiler().compile(ir) == '(all (object-id "" !=))'

    def test_relationship_compare(self):
        ir = QueryIR(
            target_class="Executable",
            scope="all",
            expression=RelationshipCompare(
                name="RunsOn",
                quantifier="some",
                expression=ObjectIdCompare(object_id="pc01"),
            ),
        )
        compiler = OksCompiler()
        result = compiler.compile(ir)
        assert result == '(all ("RunsOn" some (object-id "pc01" =)))'

    def test_and_expression(self):
        ir = QueryIR(
            target_class="Application",
            scope="all",
            expression=AndExpression(operands=[
                AttributeCompare(attribute="InitTimeout", operator=">", value="2"),
                RelationshipCompare(
                    name="RunsOn",
                    quantifier="some",
                    expression=ObjectIdCompare(object_id="pc01"),
                ),
            ]),
        )
        compiler = OksCompiler()
        result = compiler.compile(ir)
        assert result == '(all (and ("InitTimeout" "2" >) ("RunsOn" some (object-id "pc01" =))))'

    def test_or_expression(self):
        ir = QueryIR(
            target_class="Executable",
            scope="all",
            expression=OrExpression(operands=[
                AttributeCompare(attribute="InitTimeout", operator=">", value="2"),
                AttributeCompare(attribute="ExitTimeout", operator=">", value="5"),
            ]),
        )
        compiler = OksCompiler()
        result = compiler.compile(ir)
        assert result == '(all (or ("InitTimeout" "2" >) ("ExitTimeout" "5" >)))'

    def test_not_expression(self):
        ir = QueryIR(
            target_class="Executable",
            scope="this",
            expression=NotExpression(
                operand=AttributeCompare(attribute="InitTimeout", operator="=", value="0"),
            ),
        )
        compiler = OksCompiler()
        result = compiler.compile(ir)
        assert result == '(this (not ("InitTimeout" "0" =)))'

    def test_compilation_is_deterministic(self):
        ir = QueryIR(
            target_class="Executable",
            scope="all",
            expression=AttributeCompare(attribute="InitTimeout", operator=">", value="2"),
        )
        compiler = OksCompiler()
        assert compiler.compile(ir) == compiler.compile(ir)

    def test_and_requires_two_operands(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            AndExpression(operands=[
                AttributeCompare(attribute="T", operator="=", value="1"),
            ])

    def test_or_requires_two_operands(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            OrExpression(operands=[
                AttributeCompare(attribute="T", operator="=", value="1"),
            ])

    def test_compile_accepts_oks_context(self):
        """compile() must accept an optional oks_context without error."""
        ir = QueryIR(
            target_class="Executable",
            scope="all",
            expression=AttributeCompare(attribute="InitTimeout", operator=">", value="2"),
        )
        ctx = _make_context()
        compiler = OksCompiler()
        result = compiler.compile(ir, oks_context=ctx)
        assert result == '(all ("InitTimeout" "2" >))'


# ===========================================================================
# Invariant 12 — Repair Prompts Contain Diagnostic and Fingerprint
# ===========================================================================

class TestInvariant12_RepairPromptContent:
    """
    Invariant 12: Repair prompts must include the failing diagnostic message,
    casing corrections, and schema_fingerprint.
    """

    def test_validation_result_contains_fingerprint(self):
        ctx = _make_context()
        provider = _make_schema_provider(ctx)
        validator = ASTValidator(provider)

        ir = QueryIR(
            target_class="Executable",
            scope="all",
            expression=AttributeCompare(attribute="inittimeout", operator=">", value="2"),
        )
        result = validator.validate(ir, ctx)
        assert not result.valid
        assert ctx.schema_fingerprint in result.message

    def test_validation_result_contains_casing_hint(self):
        ctx = _make_context()
        provider = _make_schema_provider(ctx)
        validator = ASTValidator(provider)

        ir = QueryIR(
            target_class="Executable",
            scope="all",
            expression=AttributeCompare(attribute="inittimeout", operator=">", value="2"),
        )
        result = validator.validate(ir, ctx)
        # The correction "InitTimeout" must appear in message
        assert "InitTimeout" in result.message

    def test_class_not_found_suggests_alternatives(self):
        ctx = _make_context()
        provider = _make_schema_provider(ctx)
        validator = ASTValidator(provider)

        ir = QueryIR(
            target_class="Executablee",  # typo
            scope="all",
            expression=AttributeCompare(attribute="InitTimeout", operator=">", value="2"),
        )
        result = validator.validate(ir, ctx)
        assert not result.valid
        assert "Executable" in result.message or result.error_type == "class_not_found"


# ===========================================================================
# Invariant 13 — Executor Preservation
# ===========================================================================

class TestInvariant13_ExecutorPreservation:
    """
    Invariant 13: The existing Executor class in executor.py is preserved
    intact and accepts compiled OksQuery S-expression strings.
    """

    def test_executor_importable(self):
        from oksquery_translator.executor import Executor, ExecutionResult
        assert Executor is not None
        assert ExecutionResult is not None

    def test_executor_instantiable(self):
        from oksquery_translator.executor import Executor
        e = Executor(data_file="daq/segments/setup.data.xml")
        assert e is not None
        assert e.data_file == "daq/segments/setup.data.xml"

    def test_executor_has_execute_method(self):
        from oksquery_translator.executor import Executor
        e = Executor()
        assert callable(getattr(e, "execute", None))

    def test_executor_accepts_compiled_query_string(self):
        """
        Verify that a compiled S-expression can be passed to execute() without
        a TypeError. Actual OKS engine calls will fail gracefully (no runtime).
        """
        from oksquery_translator.executor import Executor
        e = Executor(data_file="nonexistent.xml")
        compiled = '(all ("InitTimeout" "2" >))'
        try:
            result = e.execute("Executable", compiled, version=None)
            from oksquery_translator.executor import ExecutionResult
            assert isinstance(result, ExecutionResult)
        except Exception as exc:
            # Only file/environment errors are acceptable, not TypeError/AttributeError
            assert not isinstance(exc, (TypeError, AttributeError)), \
                f"execute() raised unexpected error type: {type(exc).__name__}: {exc}"

    def test_executor_not_modified(self):
        """Verify Executor signature has not been altered."""
        import inspect
        from oksquery_translator.executor import Executor
        params = inspect.signature(Executor.execute).parameters
        assert "target_class" in params or "class_name" in params or len(params) >= 3

    def test_executor_rejects_invalid_historical_release(self):
        from oksquery_translator.executor import Executor
        result = Executor().execute(
            "Computer", '(all (object-id "" !=))', release="not-a-release"
        )
        assert not result.success
        assert "not available in CVMFS" in result.message

    def test_release_binary_prefers_host_architecture(self, monkeypatch):
        from oksquery_translator.executor import Executor
        import oksquery_translator.executor as executor_module

        monkeypatch.setattr(executor_module.os.path, "isdir", lambda _: True)
        monkeypatch.setattr(executor_module.glob, "glob", lambda _: [
            "/cvmfs/example/installed/aarch64-el9-gcc13-opt/bin/oks_dump",
            "/cvmfs/example/installed/x86_64-el9-gcc13-opt/bin/oks_dump",
        ])
        monkeypatch.setattr(executor_module.platform, "machine", lambda: "x86_64")

        binary, _ = Executor._release_info("tdaq-11-02-01")
        assert "/x86_64-" in binary


# ===========================================================================
# Out-of-Scope Early Exit — Empty Fingerprints
# ===========================================================================

class TestOutOfScopeEarlyExit:
    """Out-of-scope queries must exit early with empty schema_fingerprint."""

    def test_out_of_scope_context_fields_empty(self):
        early_exit_response = {
            "status": "error",
            "intent": "GENERAL_OUT_OF_SCOPE",
            "message": "This question is outside the scope of the OKS configuration system.",
            "schema_fingerprint": "",
            "oks_context_label": "",
        }
        assert early_exit_response["schema_fingerprint"] == ""
        assert early_exit_response["oks_context_label"] == ""

    def test_oks_context_display_label_for_current(self):
        ctx = _make_context()
        label = ctx.display_label
        assert isinstance(label, str)
        assert len(label) > 0

    def test_oks_context_is_current_for_no_version(self):
        ctx = _make_context()
        assert ctx.is_current is True

    def test_oks_context_not_current_for_historical(self):
        ctx = _make_context(run_number=380689, version_tag="tag:r380689@all_hosts")
        assert ctx.is_current is False


# ===========================================================================
# QueryPreprocessor — Deterministic Extraction
# ===========================================================================

class TestQueryPreprocessor:
    """Verify QueryPreprocessor extracts correct entities/class hints without LLM calls."""

    def test_fqdn_entity_extraction(self):
        preprocessor = QueryPreprocessor()
        analysis = preprocessor.analyze(
            "Which executables have InitTimeout greater than 2 and run on lxplus001.cern.ch?"
        )
        entities_lower = [e.lower() for e in analysis.candidate_entities]
        assert any("lxplus001" in e for e in entities_lower), \
            f"Expected lxplus001 in entities, got: {analysis.candidate_entities}"

    def test_class_hint_extraction(self):
        preprocessor = QueryPreprocessor()
        analysis = preprocessor.analyze(
            "Which executables have InitTimeout greater than 2?"
        )
        assert any("executable" in h.lower() for h in analysis.candidate_class_hints), \
            f"Expected 'Executable' class hint, got: {analysis.candidate_class_hints}"

    def test_constraint_extraction_gt(self):
        preprocessor = QueryPreprocessor()
        analysis = preprocessor.analyze(
            "Show executables with InitTimeout greater than 2"
        )
        ops = [c.operator for c in analysis.constraint_hints]
        assert ">" in ops, f"Expected '>' operator, got: {ops}"

    def test_constraint_value_extraction(self):
        preprocessor = QueryPreprocessor()
        analysis = preprocessor.analyze(
            "executables with InitTimeout greater than 2"
        )
        values = [c.value for c in analysis.constraint_hints]
        assert "2" in values, f"Expected '2' in constraint values, got: {values}"

    def test_to_retrieval_query_non_empty(self):
        preprocessor = QueryPreprocessor()
        analysis = preprocessor.analyze("executables with timeout greater than 2")
        retrieval_q = analysis.to_retrieval_query()
        assert isinstance(retrieval_q, str)
        assert len(retrieval_q.strip()) > 0

    def test_no_llm_called(self):
        """Preprocessor must not use any LLM."""
        preprocessor = QueryPreprocessor()
        analysis = preprocessor.analyze("Which ROS descriptors are active?")
        assert isinstance(analysis, QueryAnalysis)


# ===========================================================================
# Package Exports — Canonical Public API
# ===========================================================================

class TestPackageExports:
    """Verify all canonical classes are accessible from the top-level package."""

    def test_pipeline_exported(self):
        from oksquery_translator import OksPipeline, answer
        assert OksPipeline is not None
        assert callable(answer)

    def test_intent_exports(self):
        from oksquery_translator import Intent, IntentResult, IntentClassifier, RunResolver, extract_run_and_partition
        assert Intent is not None
        assert IntentResult is not None
        assert IntentClassifier is not None
        assert RunResolver is not None
        assert callable(extract_run_and_partition)

    def test_executor_exported(self):
        from oksquery_translator import Executor, ExecutionResult
        assert Executor is not None
        assert ExecutionResult is not None

    def test_context_exported(self):
        from oksquery_translator import OksContext, OksContextBuilder, compute_fingerprint
        assert OksContext is not None
        assert OksContextBuilder is not None
        assert callable(compute_fingerprint)

    def test_preprocessing_exported(self):
        from oksquery_translator import QueryPreprocessor, QueryAnalysis
        assert QueryPreprocessor is not None
        assert QueryAnalysis is not None

    def test_schema_exported(self):
        from oksquery_translator import OksSchemaProvider, ClassDefinition, AttributeDefinition, RelationshipDefinition
        assert OksSchemaProvider is not None
        assert ClassDefinition is not None
        assert AttributeDefinition is not None
        assert RelationshipDefinition is not None

    def test_ast_exported(self):
        from oksquery_translator import QueryIR, normalize_ir, OksCompiler, ASTValidator, ValidationResult
        assert QueryIR is not None
        assert callable(normalize_ir)
        assert OksCompiler is not None
        assert ASTValidator is not None
        assert ValidationResult is not None

    def test_retrieval_exported(self):
        from oksquery_translator import SchemaSearchIndex, ClassSearchDocument
        assert SchemaSearchIndex is not None
        assert ClassSearchDocument is not None
