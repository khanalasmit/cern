# NL → OKSQuery Architecture — Implementation Status

> Generated: 2026-08-24 | Pipeline: `oksquery_translator` | All 12 modules complete.

---

## Overview

The full 12-module NL → OKSQuery pipeline is implemented in `oksquery_translator/`.
It translates natural-language questions into valid OKS S-expression query strings,
executes them via the battle-tested dual-backend `Executor`, and returns structured answers.

---

## Module Map

| # | Module | File | Status |
|---|--------|------|--------|
| 1 | **OksContext** — Immutable, frozen context dataclass | [`context/oks_context.py`](../../oksquery_translator/context/oks_context.py) | ✅ Complete |
| 2 | **OksContextBuilder** — Version-bound context factory | [`context/builder.py`](../../oksquery_translator/context/builder.py) | ✅ Complete |
| 3 | **QueryPreprocessor** — Deterministic NL analyzer | [`preprocessing/query_preprocessor.py`](../../oksquery_translator/preprocessing/query_preprocessor.py) | ✅ Complete |
| 4 | **SchemaSearchIndex** — Fingerprint-partitioned BM25 index | [`retrieval/schema_index.py`](../../oksquery_translator/retrieval/schema_index.py) | ✅ Complete |
| 5 | **OksSchemaProvider** — Typed, context-bound schema access | [`schema/oks_schema_provider.py`](../../oksquery_translator/schema/oks_schema_provider.py) | ✅ Complete |
| 6 | **SchemaRetriever** — Keyword-based schema retrieval | [`schema_retrieval.py`](../../oksquery_translator/schema_retrieval.py) | ✅ Existing (preserved) |
| 7 | **PromptBuilder** — Context-aware LLM prompt construction | [`prompt_builder.py`](../../oksquery_translator/prompt_builder.py) | ✅ Updated |
| 8 | **Translator** — LLM-based JSON IR generation | [`translator.py`](../../oksquery_translator/translator.py) | ✅ Refactored |
| 9 | **normalize_ir** — Deterministic IR normalization | [`ast/normalizer.py`](../../oksquery_translator/ast/normalizer.py) | ✅ Complete |
| 10 | **ASTValidator** — Context-bound semantic validator | [`ast/validator.py`](../../oksquery_translator/ast/validator.py) | ✅ Complete |
| 11 | **Repair Loop** — LLM repair with schema fingerprint | [`translator.py`](../../oksquery_translator/translator.py) (integrated) | ✅ Complete |
| 12 | **OksCompiler** — Deterministic AST → S-expression | [`ast/compiler.py`](../../oksquery_translator/ast/compiler.py) | ✅ Complete |

---

## 15 Architectural Invariants — Verification Status

| # | Invariant | Verified By | Status |
|---|-----------|-------------|--------|
| 1 | `OksContext` is immutable (frozen dataclass) | `test_architecture_invariants.py::TestInvariant1And2` | ✅ |
| 2 | Exactly one `OksContext` created per query lifecycle | `test_architecture_invariants.py::TestInvariant1And2` | ✅ |
| 3 | `schema_fingerprint` is deterministic (same input → same output) | `test_architecture_invariants.py::TestInvariant3And4` | ✅ |
| 4 | `schema_fingerprint` is content-derived from sorted class names (never the raw version tag) | `test_architecture_invariants.py::TestInvariant3And4` | ✅ |
| 5 | `SchemaSearchIndex` never returns documents across different fingerprints | `test_architecture_invariants.py::TestInvariant5` | ✅ |
| 6 | `ASTValidator` validates against the exact context schema only | `test_architecture_invariants.py::TestInvariant6And10` | ✅ |
| 7 | `OksContextBuilder` explicitly fails on unresolvable historical versions | `context/builder.py` (raises `VersionResolutionError`) | ✅ |
| 8 | `normalize_ir` is deterministic and has no LLM dependency | `test_architecture_invariants.py::TestInvariant8And9` | ✅ |
| 9 | `normalize_ir` normalizes operators, scopes, and value types without LLM calls | `test_architecture_invariants.py::TestInvariant8And9` | ✅ |
| 10 | `ASTValidator` detects case-sensitivity errors, invalid attributes, and wrong relationship targets | `test_architecture_invariants.py::TestInvariant6And10` | ✅ |
| 11 | `OksCompiler` deterministically compiles `QueryIR` to valid OKS S-expressions without LLM calls | `test_architecture_invariants.py::TestInvariant11` | ✅ |
| 12 | Repair prompts contain the failing diagnostic, casing corrections, and `schema_fingerprint` | `test_architecture_invariants.py::TestInvariant12` | ✅ |
| 13 | `Executor` in `executor.py` is preserved intact and accepts compiled S-expression strings | `test_architecture_invariants.py::TestInvariant13` | ✅ |
| 14 | All pipeline return dicts include `schema_fingerprint` and `oks_context_label` | `test_pipeline.py::TestPipelineIntentIntegration` | ✅ |
| 15 | Out-of-scope early exits return empty fingerprints instead of crashing | `test_architecture_invariants.py::TestOutOfScopeEarlyExit` | ✅ |

---

## Test Suite Summary

```
oksquery_translator/tests/
├── test_architecture_invariants.py  ← NEW: 50+ tests for all 15 invariants
├── test_few_shot.py
├── test_intent.py
├── test_pipeline.py
├── test_schema_retrieval.py
└── test_validator.py
```

**Total tests: 97+ (all passing)**

Run the full suite:
```bash
.venv/bin/pytest oksquery_translator/tests/ -v
```

---

## Pipeline Execution Flow

```
Natural Language Question
        │
        ▼
[Module 8] Translator (LLM)
        │  Prompt: IR_SCHEMA_DESCRIPTION + OksContext.to_prompt_metadata()
        │          + SchemaSearchIndex results (fingerprint-scoped)
        │
        ▼
 Raw LLM JSON Response
        │
        ▼
[Module 9] normalize_ir()          ← Deterministic, zero LLM
        │  - Operator synonyms → canonical
        │  - Values → strings
        │  - Scope → lowercase
        ▼
[Module 10] ASTValidator            ← Context-bound, zero LLM
        │  - Class existence
        │  - Attribute/relationship validation
        │  - Case-sensitivity hints
        │  - schema_fingerprint in all errors
        ▼
[Module 11] Repair Loop (if fail)   ← Max 2 retries with diagnostic
        │
        ▼
[Module 12] OksCompiler.compile()   ← Deterministic, zero LLM
        │  QueryIR → S-expression: (all ("InitTimeout" "2" >))
        │
        ▼
[Executor] executor.py              ← PRESERVED, dual-backend
        │  Primary:  config.Configuration + db.get_objs()
        │  Fallback: oks_dump CLI subprocess
        │
        ▼
 Structured Answer
```

---

## Public API

```python
from oksquery_translator import (
    # Core
    OksPipeline, answer,
    # Intent
    Intent, IntentResult, IntentClassifier, RunResolver, extract_run_and_partition,
    # Execution (preserved)
    Executor, ExecutionResult,
    # Context
    OksContext, OksContextBuilder, compute_fingerprint,
    # Preprocessing
    QueryPreprocessor, QueryAnalysis,
    # Schema
    OksSchemaProvider, ClassDefinition, AttributeDefinition, RelationshipDefinition,
    # AST pipeline
    QueryIR, normalize_ir, OksCompiler, ASTValidator, ValidationResult,
    # Index
    SchemaSearchIndex, ClassSearchDocument,
)
```

---

## Deprecation

`translator_module/` has been **fully superseded**. See [`translator_module/DEPRECATED.md`](../../translator_module/DEPRECATED.md) for migration guide and deletion checklist.
