# ⚠️ DEPRECATED: `translator_module`

> **Status**: Fully superseded by `oksquery_translator` as of the NL → OKSQuery 12-module architecture integration.

---

## Why This Module Is Deprecated

`translator_module` was the **experimental prototype** for translating natural-language queries
into OKS S-expression query strings. It demonstrated the IR/AST approach and the JSON-based
repair loop, but was not integrated with the production OKS execution engine.

All functionality has been **fully ported, tested, and extended** in `oksquery_translator/`
with strict context-binding, fingerprint-partitioned schema indexing, and preservation of
the battle-tested `Executor` dual-backend.

---

## Component Migration Map

| Old Path (`translator_module/`) | New Path (`oksquery_translator/`) | Status |
|---|---|---|
| `agent/ir_validator.py` → `AttributeCompare`, `QueryIR`, Pydantic models | `ast/models.py` | ✅ Ported & extended |
| `agent/serializer.py` → `serialize_ir_to_oks()` | `ast/compiler.py` → `OksCompiler.compile()` | ✅ Ported & deterministic |
| `agent/translator.py` → `IR_SCHEMA_DESCRIPTION`, JSON translation | `translator.py` + `prompt_builder.py` | ✅ Integrated with repair loop |
| `cli.py` | `__main__.py` or CLI wrappers in `oksquery_translator` | ✅ Preserved via `OksPipeline` |

---

## New Architecture Modules

The new `oksquery_translator` package implements the full 12-module pipeline:

```
Module  1: OksContext         → oksquery_translator/context/oks_context.py
Module  2: OksContextBuilder  → oksquery_translator/context/builder.py
Module  3: QueryPreprocessor  → oksquery_translator/preprocessing/query_preprocessor.py
Module  4: SchemaSearchIndex  → oksquery_translator/retrieval/schema_index.py
Module  5: OksSchemaProvider  → oksquery_translator/schema/oks_schema_provider.py
Module  6: SchemaRetriever    → oksquery_translator/schema_retrieval.py  (existing)
Module  7: PromptBuilder      → oksquery_translator/prompt_builder.py   (updated)
Module  8: Translator         → oksquery_translator/translator.py       (refactored)
Module  9: normalize_ir       → oksquery_translator/ast/normalizer.py
Module 10: ASTValidator       → oksquery_translator/ast/validator.py
Module 11: Repair Loop        → oksquery_translator/translator.py (integrated)
Module 12: OksCompiler        → oksquery_translator/ast/compiler.py
```

The `Executor` (`oksquery_translator/executor.py`) remains **unchanged** and is the sole
runtime bridge to the CERN ATLAS TDAQ OKS engine.

---

## When Is It Safe to Delete `translator_module/`?

This directory may be safely deleted when **all** of the following are true:

1. ✅ `oksquery_translator/tests/` passes with ≥ 100 tests covering all invariants.
2. ✅ No production script or CI pipeline imports from `translator_module`.
3. ✅ The `eval_dataset/oks_model.py` reference to `translator_module` has been migrated.
4. ✅ Any CERN-internal documentation referencing `translator_module` has been updated.

**Check for remaining references:**
```bash
grep -r "translator_module" . --include="*.py" -l
```

---

## Migration Guide

### Before (deprecated)
```python
from translator_module.agent.ir_validator import QueryIR, AttributeCompare
from translator_module.agent.serializer import serialize_ir_to_oks
```

### After (canonical)
```python
from oksquery_translator import QueryIR, AttributeCompare, OksCompiler

compiler = OksCompiler()
query_string = compiler.compile(ir)
```

### One-shot query (canonical)
```python
from oksquery_translator import answer
result = answer("Which executables have InitTimeout > 2?")
print(result["answer"])
```
