# NL → OKSQuery Architecture: Rewritten Integration Prompts

# Architectural Corrections

Before executing the integration prompts, the following architectural principles, existing layer reuses, and corrections to earlier plans must be understood:

1. **Reuse of the Existing OKS Execution Layer (`oksquery_translator/executor.py`)**:
   - The existing `Executor` class in `oksquery_translator/executor.py` is the battle-tested runtime bridge to the CERN ATLAS TDAQ OKS engine. It supports a dual-backend execution model:
     1. **Primary**: Python `config` C++ extension (`config.Configuration("oksconflibs:" + data_file)` calling `db.get_objs(target_class, query)`).
     2. **Secondary/Fallback**: CLI subprocess execution (`oks_dump -c <class> -q '<query>' <data-file>`) with exit-code handling (0=OK, 5=OK with warnings, 3=bad query syntax, 4=class not found) and stdout parsing.
     3. **Temporal Environment Sandboxing**: Safely manages `TDAQ_DB_PATH` (CVMFS snapshots) and `TDAQ_DB_VERSION` (git hash, date, or tag like `tag:r380689@all_hosts`) with backup and restoration in `finally:` blocks.
   - **Crucial Rule**: **DO NOT REWRITE OR REPLACE THE EXECUTION LAYER.** The new AST compiler compiles valid ASTs directly into S-expression query strings (e.g. `(all ("InitTimeout" "2" >))`), which are handed directly to `self.executor.execute(target_class, oks_query, version=...)`.

2. **Exact Schema-to-Fingerprint Binding (No Siloed HEAD Hashing)**:
   - *Correction*: `OksContextBuilder` must compute the `schema_fingerprint` from the schema loaded for the *exact requested version*. If a user requests historical run `380689` or release `tdaq-13-00-00`, the context builder must inspect that specific versioned configuration. If the environment cannot load the requested historical schema, it must fail explicitly with a clear diagnostic instead of silently calculating the fingerprint of the local HEAD XML files.

3. **Strict Separation of Pipeline Concerns**:
   - **Preprocessor** (`preprocessing/query_preprocessor.py`): Deterministic query tokenization, entity extraction (FQDNs, IDs), and constraint extraction. No LLM.
   - **Context & Schema Provider** (`context/oks_context.py`, `schema/oks_schema_provider.py`): Immutable context, version-scoped class definitions, diamond-inheritance resolution.
   - **AST & Normalizer** (`ast/models.py`, `ast/normalizer.py`): Pydantic V2 IR schema + deterministic operator/type sanitization before schema checking.
   - **Context-Bound Validator** (`ast/validator.py`): Semantic checking against `OksSchemaProvider` for the specific context fingerprint (case-sensitivity checks, attribute vs relationship disambiguation).
   - **Deterministic Compiler** (`ast/compiler.py`): Pure deterministic AST -> OksQuery S-expression generation. Zero LLM involvement.
   - **Execution & Interpretation** (`executor.py`, `interpreter.py`): Executes compiled query via existing `Executor` and formats final user response.

---

# Prompt 1 — OksContext Dataclass & Exact Version-Bound Context Builder

```text
## Repository
- Root: /home/rhythm/Projects/cern_daq/cern
- Target Package: oksquery_translator

## Current state
The repository has an existing `oksquery_translator` package with `intent.py` (classifies queries into 4 intents and extracts run numbers/partitions via `RunResolver`) and `executor.py` (executes queries with temporal version management). Currently, version resolution stops at producing a string tag or version label, and downstream components operate directly against whatever default data file is loaded without an immutable context container.

## Objective
Implement an immutable, frozen `OksContext` dataclass and an `OksContextBuilder` factory in `oksquery_translator/context/`. This creates a version-isolated, fingerprinted context for each query request, serving as the single source of truth for all downstream stages (retrieval, prompt building, validation, repair, compilation, and execution).

## Required repository inspection
Before writing any code, inspect:
1. `oksquery_translator/intent.py`: Inspect `RunResolver`, `IntentResult`, and `extract_run_and_partition` to understand how run numbers and version tags (e.g. `tag:r380689@all_hosts`, `hash:...`, `tdaq-...`) are resolved.
2. `oksquery_translator/schema_retrieval.py`: Inspect `SchemaRetriever.__init__`, `get_class_list()`, and how schema directories and data files are discovered or passed.
3. `oksquery_translator/executor.py`: Inspect `_set_version_env()` and `_restore_env()` to see how temporal environment variables (`TDAQ_DB_PATH`, `TDAQ_DB_VERSION`) configure the OKS runtime.

## Implementation requirements
Create the package `oksquery_translator/context/`:

1. `oksquery_translator/context/oks_context.py`:
   - Define a frozen (immutable `dataclass(frozen=True)`) `OksContext` with fields:
     - `schema_identifier`: str (human-readable release/version label, e.g. "tdaq-13-00-00", "run-380689", or "current")
     - `schema_fingerprint`: str (canonical deterministic hash of the exact resolved schema)
     - `release`: Optional[str] (e.g. "tdaq-13-00-00")
     - `git_revision`: Optional[str] (Git commit SHA)
     - `run_number`: Optional[int] (ATLAS run number)
     - `configuration_revision`: Optional[str]
     - `version_tag`: Optional[str] (the raw resolved version string, e.g. "tag:r380689@all_hosts")
   - Properties:
     - `is_current`: bool (True if HEAD/default configuration)
     - `display_label`: str (Human-readable representation for logging and UI headers)
   - Methods:
     - `to_prompt_metadata()`: Returns formatted string metadata (Module 7 Component C in the architecture specification) explicitly warning the LLM that only terms in this schema fingerprint are authoritative.
   - Implement a standalone helper `compute_fingerprint(class_names: Iterable[str]) -> str`:
     - Deduplicates class names
     - Sorts alphabetically
     - Joins deterministically (e.g., "|")
     - Computes SHA-256 and returns a 16-character hexadecimal prefix

2. `oksquery_translator/context/builder.py`:
   - Define `OksContextBuilder`:
     - Initializer accepts base configuration (e.g. default `data_file`, `schema_dir`).
     - Method `build(version_tag: Optional[str] = None) -> OksContext`:
       - Parses the `version_tag` (handling `tag:r<run>@<partition>`, `hash:<sha>`, `tdaq-<release>`, or None).
       - Resolves the exact schema environment corresponding to that version.
       - IMPORTANT: If a historical version is requested, it must attempt to obtain the class list from that specific versioned environment (or data file). If exact version resolution is unsupported in the current local environment, it must raise a descriptive `VersionResolutionError` or record an explicit unresolvable status rather than silently fingerprinting the current local HEAD schema.
       - Obtains the canonical class list for that schema and computes the `schema_fingerprint`.
       - Returns the frozen `OksContext`.

3. `oksquery_translator/context/__init__.py`:
   - Export `OksContext`, `compute_fingerprint`, and `OksContextBuilder`.

## Integration requirements
- Do not modify existing pipeline, translator, or executor logic in this step.
- Ensure `OksContextBuilder` can be instantiated independently.

## Version/schema requirements
- Never use the requested tag string itself as the fingerprint.
- The fingerprint must be content-derived from the sorted class names of the resolved schema.
- Fail explicitly if a requested version cannot be resolved to an actual schema.

## Files to create
- `oksquery_translator/context/__init__.py`
- `oksquery_translator/context/oks_context.py`
- `oksquery_translator/context/builder.py`

## Files that may be modified
- None

## Files that must NOT be modified
- `oksquery_translator/executor.py` (Must remain intact)
- `oksquery_translator/pipeline.py`
- `oksquery_translator/intent.py`
- `oksquery_translator/translator.py`
- `oksquery_translator/validator.py`

## Backward compatibility
- Existing code remains untouched and functioning.

## Testing and verification
Execute behavioral verification tests:
1. Verify fingerprint determinism:
   - `compute_fingerprint(["Application", "Computer"])` must equal `compute_fingerprint(["Computer", "Application", "Application"])`.
   - Fingerprint must be a 16-character hex string.
2. Verify default context construction:
   - Instantiate `OksContextBuilder()` and call `build()`.
   - Verify `ctx.is_current` is True, `ctx.schema_fingerprint` is non-empty, and `ctx.to_prompt_metadata()` returns the formatted block.
3. Verify immutability:
   - Attempting to mutate `ctx.schema_fingerprint` or any field must raise a `FrozenInstanceError` (or `AttributeError`).

## Failure handling
- If `SchemaRetriever` cannot load classes in the environment (e.g. missing C++ libraries), verify whether it falls back to XML schema directory parsing. Fix path discovery if needed.

## Final report
Report:
- Files created
- Test execution outputs
- Verification that `OksContext` is immutable and fingerprint is deterministic
```

---

# Prompt 2 — Integrate OksContext into Pipeline Lifecycle & Preserve Executor Contract

```text
## Repository
- Root: /home/rhythm/Projects/cern_daq/cern
- Target Package: oksquery_translator

## Current state
`OksContext` and `OksContextBuilder` exist in `oksquery_translator/context/`. `OksPipeline` in `oksquery_translator/pipeline.py` currently orchestrates intent classification, execution via `Executor`, and interpretation, passing loose string parameters (`version`, `effective_version`).

## Objective
Wire `OksContextBuilder` into `OksPipeline` so that every query lifecycle builds exactly one `OksContext` instance early in `answer()`. Downstream components and early exit points must receive and report context metadata (fingerprint and label) consistently, while preserving the existing `Executor` integration intact.

## Required repository inspection
Inspect:
1. `oksquery_translator/pipeline.py`: Look at `OksPipeline.__init__`, all return dictionaries in `answer()`, early error exit branches (out-of-scope, missing run, version conflict), and where `self.executor.execute()` is called.
2. `oksquery_translator/executor.py`: Verify that `Executor.execute(target_class, query, version=...)` expects a version string and returns an `ExecutionResult`.
3. `oksquery_translator/__init__.py`: Look at public exports.

## Implementation requirements
Modify `oksquery_translator/pipeline.py`:
1. In `OksPipeline.__init__`:
   - Initialize `self.context_builder = OksContextBuilder(...)`, forwarding configured `data_file` and `schema_dir`.
   - Preserve `self.executor = Executor(data_file=data_file)` exactly as it is.
2. In `OksPipeline.answer(question, version=None)`:
   - Perform intent classification and version validation as currently implemented.
   - For early exits that occur *before* schema resolution (e.g. general out-of-scope), ensure return dictionaries include consistent context fields (`schema_fingerprint`: "", `oks_context_label`: "").
   - Once `effective_version` is resolved (or defaulted), call `self.context_builder.build(version_tag=effective_version)` to obtain `oks_context`.
   - Log the resolved `schema_identifier` and `schema_fingerprint`.
   - When executing the query in Step 2:
     - Continue calling `self.executor.execute(target_class, oks_query, version=oks_context.version_tag or effective_version)`.
   - Ensure the final success and error return dicts include:
     - `"schema_fingerprint"`: `oks_context.schema_fingerprint`
     - `"oks_context_label"`: `oks_context.display_label`
3. Update `oksquery_translator/__init__.py`:
   - Export `OksContext` and `OksContextBuilder`.

## Integration requirements
- Do not alter the public signature or return structure of `self.executor.execute()`.
- All existing return keys (`status`, `answer`, `oks_query`, `target_class`, `result_count`, `results`, `attempts`, `message`, `intent`, `run_number`, `partition`, `version`, `version_used`) must continue to be present.

## Version/schema requirements
- Exactly one `OksContext` must be created per request lifecycle.
- Out-of-scope questions that exit before context creation must return empty metadata strings rather than crashing.

## Files to create
- None

## Files that may be modified
- `oksquery_translator/pipeline.py`
- `oksquery_translator/__init__.py`

## Files that must NOT be modified
- `oksquery_translator/executor.py` (Keep fully intact)
- `oksquery_translator/translator.py`
- `oksquery_translator/validator.py`
- `oksquery_translator/intent.py`

## Backward compatibility
- Existing `answer()` and `translate_only()` calls must remain backward-compatible and return the same structure with the addition of the new metadata fields.

## Testing and verification
Run:
1. Out-of-scope query test:
   - Call `pipeline.answer("What is the capital of France?")`.
   - Verify `status == "error"`, `intent == "GENERAL_OUT_OF_SCOPE"`, `schema_fingerprint == ""`.
2. In-scope current query test:
   - Call `pipeline.answer("Which executables have InitTimeout > 2?")` (or use mocked translation if LLM credentials are not configured).
   - Verify `schema_fingerprint` is present and matches a 16-char hex string.
   - Verify `oks_context_label` is present.
3. Execution layer contract test:
   - Verify `pipeline.executor` is an instance of `Executor` from `oksquery_translator.executor`.
4. Test `translate_only()`:
   - Ensure `pipeline.translate_only(...)` continues to work without error.

## Failure handling
- If unit tests fail due to missing keys in expected dictionary assertions, check that every return path in `pipeline.py` contains the new keys.

## Final report
Report:
- Modified files
- Verification that all return paths maintain dictionary shape
- Test results for both out-of-scope and in-scope queries
```

---

# Prompt 3 — Deterministic Query Preprocessor (Module 3) & Typed OksSchemaProvider (Module 5)

```text
## Repository
- Root: /home/rhythm/Projects/cern_daq/cern
- Target Package: oksquery_translator

## Current state
`OksContext` is built in `pipeline.py`. Query tokens are matched loosely inside `schema_retrieval.py` without structured preprocessing, and schema information is returned as raw dictionary structures without strict typing or inheritance encapsulation.

## Objective
Implement:
1. `QueryPreprocessor` (Module 3): A deterministic natural-language query analyzer that extracts meaningful tokens, candidate OKS class hints, entities (hostnames, IDs), and comparison constraints without calling any LLM.
2. `OksSchemaProvider` (Module 5): A typed, context-bound schema access layer that wraps schema inspection, resolves class inheritance/effective members, and guarantees access is scoped to the bound `OksContext`.

## Required repository inspection
Inspect:
1. `oksquery_translator/schema_retrieval.py`:
   - Inspect `_KEYWORD_TO_CLASSES` dictionary.
   - Inspect `_load_class_info()` and how attributes and relationships are parsed from `config` or XML (look at attribute dict keys: `name`, `type`, `range`, `init_value` vs `init-value`, `is_multi_value`).
   - Inspect superclass resolution.
2. `oksquery_translator/context/oks_context.py`:
   - Verify how `OksContext` holds fingerprint and version information.

## Implementation requirements

### Part 1: Query Preprocessor (`oksquery_translator/preprocessing/`)
Create `oksquery_translator/preprocessing/query_preprocessor.py` and `__init__.py`:
- Data structures:
  - `ConstraintHint`: Dataclass containing `raw_text`, `operator` (`=`, `!=`, `<`, `>`, `<=`, `>=`, `~=`), `value` (string), and optional `attribute_hint`.
  - `QueryAnalysis`: Dataclass containing `original_query`, `normalized_query`, `meaningful_tokens` (list of non-stopword tokens), `candidate_entities` (hostnames, quoted strings, object IDs), `candidate_class_hints` (mapped OKS class names), `constraint_hints` (list of `ConstraintHint`), and `numeric_values`.
  - Method `QueryAnalysis.to_retrieval_query() -> str`: Combines class hints and meaningful tokens into a prioritized token string for schema search.
- Class `QueryPreprocessor`:
  - `analyze(question: str) -> QueryAnalysis`:
    - Deterministically tokenizes and cleans text.
    - Strips OKS domain stopwords ("query", "database", "find", "show", "tell", "which", etc.).
    - Extracts entity patterns (FQDNs like `lxplus001.cern.ch`, quoted strings, camelCase IDs).
    - Maps keywords to OKS candidate classes (e.g. "application" -> "Application", "host" -> "Computer", "segment" -> "Segment", "controller" -> "RunControlApplication").
    - Maps comparison phrases ("greater than", "less than", "at least", "equals", "contains", "matches", etc.) to canonical OKSQuery operators and extracts associated values.
    - Must NOT invoke any LLM API.

### Part 2: OKS Schema Provider (`oksquery_translator/schema/`)
Create `oksquery_translator/schema/oks_schema_provider.py` and `__init__.py`:
- Data structures:
  - `AttributeDefinition`: `name`, `type`, `range`, `init_value`, `is_multi_value: bool`.
  - `RelationshipDefinition`: `name`, `target_class`, `is_multi_value: bool`, `description: str`.
  - `ClassDefinition`: `name`, `superclasses: list[str]`, `attributes: list[AttributeDefinition]`, `relationships: list[RelationshipDefinition]`, `description: str`.
    - Methods: `get_attribute(name)`, `get_relationship(name)`, `attribute_names()`, `relationship_names()`.
- Class `OksSchemaProvider`:
  - `__init__(oks_context: OksContext, data_file: str = "...", schema_dir: str = None)`:
    - Binds strictly to `oks_context`.
    - Instantiates or wraps the underlying schema access mechanism.
  - `get_all_class_names() -> list[str]`: Returns available class names in this context.
  - `get_class(name: str) -> Optional[ClassDefinition]`: Returns direct class definition.
  - `get_effective_members(class_name: str) -> Optional[ClassDefinition]`:
    - Recursively resolves all inherited attributes and relationships from superclasses (handling diamond/multiple inheritance correctly without infinite loops).
    - Subclass attributes/relationships take precedence or merge appropriately.
  - `class_exists(name: str) -> bool`: Fast existence check.
  - `suggest_class(name: str) -> list[str]`: Returns close matches for error diagnostic hints.

## Integration requirements
- Package exports in `oksquery_translator/preprocessing/__init__.py` and `oksquery_translator/schema/__init__.py`.
- Do not replace existing `SchemaRetriever` callers yet; `OksSchemaProvider` will be used by the AST validator and context builder in upcoming prompts.

## Version/schema requirements
- `OksSchemaProvider` must hold its bound `OksContext` and ensure all lookups reflect the schema corresponding to that context.

## Files to create
- `oksquery_translator/preprocessing/__init__.py`
- `oksquery_translator/preprocessing/query_preprocessor.py`
- `oksquery_translator/schema/__init__.py`
- `oksquery_translator/schema/oks_schema_provider.py`

## Files that may be modified
- None

## Files that must NOT be modified
- `oksquery_translator/executor.py`
- `oksquery_translator/schema_retrieval.py`
- `oksquery_translator/pipeline.py`
- `oksquery_translator/translator.py`

## Backward compatibility
- Existing `SchemaRetriever` functionality remains intact.

## Testing and verification
Write and execute test assertions:
1. `QueryPreprocessor` test:
   - Analyze: `"Which executables have InitTimeout greater than 2 and run on lxplus001.cern.ch?"`
   - Assert `class_hints` contains `"Executable"`.
   - Assert `candidate_entities` contains `"lxplus001.cern.ch"`.
   - Assert `constraint_hints` contains a constraint with operator `">"` and value `"2"`.
2. `OksSchemaProvider` test:
   - Instantiate provider with default `OksContext`.
   - Retrieve `ClassDefinition` for a known class (e.g. `"Application"` or `"Executable"`).
   - Test `get_effective_members()` to confirm inherited attributes from superclasses (e.g., `BaseApplication` or `RunControlApplicationBase`) are present.
   - Assert `class_exists("NonExistentClass123")` is False, and `suggest_class("execut")` returns candidate suggestions.

## Failure handling
- If XML parsing or schema attribute extraction fails on certain types, inspect `schema_retrieval.py`'s parsing logic and match the dictionary keys it produces.

## Final report
Report:
- Created files
- Preprocessor extraction test results
- Schema provider inheritance resolution test results
```

---

# Prompt 4 — AST Models, Deterministic Normalizer & OKSQuery Compiler (Modules 9 & 12)

```text
## Repository
- Root: /home/rhythm/Projects/cern_daq/cern
- Target Package: oksquery_translator

## Current state
`translator_module/agent/ir_validator.py` and `translator_module/agent/serializer.py` contain an initial Pydantic JSON IR model and serializer. However, `oksquery_translator/` still operates on raw string regex parsing (`CLASS: ... \n QUERY: ...`) rather than a structured AST.

## Objective
Port and refine the AST/IR architecture into `oksquery_translator/ast/`:
1. `models.py`: Strongly-typed Pydantic V2 models for the OKSQuery Intermediate Representation (Attribute comparison, Object ID comparison, Relationships, Logical AND/OR/NOT, QueryIR).
2. `normalizer.py` (Module 9): Deterministic normalization pipeline that cleans raw LLM output before validation (normalizing operator synonyms, coercing numeric values to strings, standardizing scopes).
3. `compiler.py` (Module 12): Deterministic compiler that transforms a validated `QueryIR` AST into a canonical OKSQuery S-expression string ready to be fed directly into `Executor`.

## Required repository inspection
Inspect:
1. `translator_module/agent/ir_validator.py`: Inspect all Pydantic models (`AttributeCompare`, `ObjectIdCompare`, `RelationshipCompare`, `AndExpression`, `OrExpression`, `NotExpression`, `QueryIR`) and their validators (e.g., `operands >= 2`).
2. `translator_module/agent/serializer.py`: Inspect how each AST node type is serialized to OksQuery S-expression syntax.
3. `oksquery_translator/prompt_builder.py`: Inspect `OKSQUERY_SYNTAX_RULES` to ensure full compliance with OksQuery grammar (quoting rules, operator symbols: `=`, `!=`, `<`, `>`, `<=`, `>=`, `~=`).
4. `oksquery_translator/executor.py`: Inspect how `Executor.execute()` accepts query strings to ensure the compiled output is byte-compatible.

## Implementation requirements
Create `oksquery_translator/ast/`:

1. `oksquery_translator/ast/models.py`:
   - Port Pydantic models for the IR schema:
     - `AttributeCompare`: `type="attribute_compare"`, `attribute: str`, `operator: Literal["=", "!=", "~=", "<", "<=", ">", ">="]`, `value: str`.
     - `ObjectIdCompare`: `type="object_id"`, `operator: Literal["="]`, `object_id: str`.
     - `RelationshipCompare`: `type="relationship"`, `name: str`, `quantifier: Literal["some", "all"]`, `expression: Expression`.
     - `AndExpression`: `type="and"`, `operands: list[Expression]` (validator: minimum 2 operands).
     - `OrExpression`: `type="or"`, `operands: list[Expression]` (validator: minimum 2 operands).
     - `NotExpression`: `type="not"`, `operand: Expression`.
     - `Expression` recursive Union alias.
     - `QueryIR`: `target_class: Optional[str]`, `scope: Literal["this", "all"]`, `expression: Expression`, `explanation: Optional[str]`.
   - Define dataclass `ValidationResult`:
     - `valid: bool`, `error_type: str`, `message: str`, `class_name: str`, `attribute: str`, `relationship: str`.

2. `oksquery_translator/ast/normalizer.py`:
   - Function `normalize_ir(raw_dict: dict) -> dict`:
     - Must be deterministic, zero LLM calls.
     - Normalizes operator synonyms: e.g. `"eq"`, `"=="`, `"equals"` -> `"="`; `"gt"`, `"greater"` -> `">"`; `"gte"`, `">="` -> `">="`; `"regex"`, `"like"`, `"contains"` -> `"~="`.
     - Standardizes `scope`: `"ALL"` -> `"all"`, `"THIS"` -> `"this"`, invalid/missing -> `"all"`.
     - Normalizes values: converts integer/float values to strings (e.g., `2` -> `"2"`), strips unwanted whitespace/quotes from class/attribute names.
     - Normalizes relationship quantifiers: `"SOME"` -> `"some"`, default to `"some"`.
     - Raises `NormalizerError` if structure is fundamentally unparseable (e.g. missing `expression`).

3. `oksquery_translator/ast/compiler.py`:
   - Class `OksCompiler`:
     - Method `compile(ir: QueryIR, oks_context: Optional[OksContext] = None) -> str`:
       - Transforms the `QueryIR` tree into a canonical OKS S-expression: `(<scope> <expression>)`.
       - `AttributeCompare` -> `("<attribute>" "<value>" <operator>)`
       - `ObjectIdCompare` -> `(object-id "<object_id>" =)`
       - `RelationshipCompare` -> `("<name>" <quantifier> <nested_expression>)`
       - `AndExpression` -> `(and <expr1> <expr2> ...)`
       - `OrExpression` -> `(or <expr1> <expr2> ...)`
       - `NotExpression` -> `(not <expr>)`
     - CRITICAL RULE: The compiler is 100% deterministic code. It must NEVER call an LLM. Output must be consumable by `oksquery_translator.executor.Executor`.
   - Maintain `serialize_ir_to_oks(ir)` as a compatibility function.

4. `oksquery_translator/ast/__init__.py`:
   - Export all models, `normalize_ir`, `NormalizerError`, `OksCompiler`, `serialize_ir_to_oks`.

## Integration requirements
- Do not delete `translator_module/agent/` files yet.
- Ensure Pydantic V2 compatibility (`model_validator`, `model_rebuild`, `TypeAdapter`).

## Version/schema requirements
- Compilation syntax is universal for OKS S-expressions; `oks_context` is accepted by `compile()` for provenance tracking.

## Files to create
- `oksquery_translator/ast/__init__.py`
- `oksquery_translator/ast/models.py`
- `oksquery_translator/ast/normalizer.py`
- `oksquery_translator/ast/compiler.py`

## Files that may be modified
- None

## Files that must NOT be modified
- `oksquery_translator/executor.py` (Must remain intact)
- `translator_module/agent/ir_validator.py`
- `translator_module/agent/serializer.py`
- `oksquery_translator/translator.py`

## Backward compatibility
- Existing code continues to run without modification.

## Testing and verification
Execute tests:
1. Normalization test:
   - Pass dictionary with non-canonical operator `{"operator": "gt", "value": 20, "attribute": " Timeout "}`.
   - Verify `normalize_ir()` returns `operator == ">"`, `value == "20"`, `attribute == "Timeout"`.
2. AST compilation test:
   - Construct a complex nested `QueryIR` (e.g. `scope="all"`, `target_class="Application"`, `expression=AndExpression` containing `AttributeCompare` and `RelationshipCompare`).
   - Call `OksCompiler().compile(ir)`.
   - Verify generated OKSQuery string matches expected S-expression: `(all (and ("InitTimeout" "2" >) ("RunsOn" some (object-id "pc01" =))))`.
3. Validation failure test:
   - Ensure `AndExpression` with < 2 operands raises `ValidationError`.

## Failure handling
- If Pydantic throws recursion or forward reference errors on `Expression`, ensure `model_rebuild()` is called on all composite expression models.

## Final report
Report:
- Created files
- Normalization test results
- Compilation test outputs for primitive, relationship, and logical expressions
```

---

# Prompt 5 — Version-Aware AST Semantic Validator (Module 10)

```text
## Repository
- Root: /home/rhythm/Projects/cern_daq/cern
- Target Package: oksquery_translator

## Current state
`oksquery_translator/ast/` has the Pydantic models, normalizer, and compiler. `oksquery_translator/schema/` has `OksSchemaProvider`.

## Objective
Implement `ASTValidator` (Module 10) in `oksquery_translator/ast/validator.py`.
The validator performs deterministic semantic validation of a `QueryIR` against the exact schema provided by `OksSchemaProvider` for a specific `OksContext`. It catches schema mismatches (invalid class, non-existent attribute, wrong casing, invalid relationship target) and generates rich, context-aware diagnostic feedback for the repair loop.

## Required repository inspection
Inspect:
1. `translator_module/agent/ir_validator.py`: Inspect `validate_ir_semantics()` to see how relationship traversal was checked.
2. `oksquery_translator/validator.py`: Inspect the existing regex-based validation error patterns (`can't find relationship`, `can't find attribute`, case-sensitivity hints) to understand the failure modes encountered during real OKS execution.
3. `oksquery_translator/schema/oks_schema_provider.py`: Inspect `get_effective_members()`, `get_class()`, and member lookup methods.

## Implementation requirements
Create `oksquery_translator/ast/validator.py`:

Class `ASTValidator`:
- `__init__(schema_provider: OksSchemaProvider)`:
  - Stores the schema provider bound to the request's context.

- `validate(ir: QueryIR, oks_context: OksContext) -> ValidationResult`:
  - **Check 1: Target Class Validation**:
    - `ir.target_class` must not be null/empty.
    - `target_class` must exist in `self.schema_provider`.
    - If missing: generate `ValidationResult(valid=False, error_type="class_not_found")` with suggestions from `schema_provider.suggest_class(target_class)` and schema fingerprint info.
  - **Check 2: Recursive Expression Semantic Validation**:
    - Recursively traverses `ir.expression` starting at `current_class = ir.target_class`.
    - `AttributeCompare`:
      - Resolves effective attributes of `current_class` (including superclasses).
      - If attribute does not exist:
        - Check for exact case mismatch (e.g. `inittimeout` vs `InitTimeout`). If found, report a specific `CASE_ERROR` diagnostic giving the exact valid casing.
        - Check if the name is actually a relationship on `current_class`. If found, report a diagnostic suggesting relationship traversal instead.
        - Otherwise, report invalid attribute error listing available valid attributes on `current_class` and the `oks_context.schema_fingerprint`.
    - `RelationshipCompare`:
      - Resolves effective relationships on `current_class`.
      - If relationship does not exist:
        - Check case mismatch and report exact casing.
        - Otherwise, report invalid relationship error listing available relationships.
      - If relationship exists:
        - Retrieve the `target_class` of the relationship.
        - If `target_class` is defined, recursively validate `expr.expression` against `target_class` (tracking traversal path, e.g. `Application.RunsOn`).
    - `AndExpression` / `OrExpression`:
      - Recursively validate every operand; return first failure encountered.
    - `NotExpression`:
      - Recursively validate operand.
    - `ObjectIdCompare`:
      - Valid on all classes (all OKS objects have object IDs).
  - Returns `ValidationResult(valid=True)` when all checks pass.

- Export `ASTValidator` in `oksquery_translator/ast/__init__.py`.

## Integration requirements
- The validator must work purely on AST structures and `OksSchemaProvider` without requiring external subprocess calls.
- Validation feedback must include the `schema_fingerprint` to reinforce the schema-context invariant in repair prompts.

## Version/schema requirements
- Validate ONLY against the `OksSchemaProvider` bound to the supplied `oks_context`.
- Never validate against a default or global schema provider if `oks_context` specifies a different schema.

## Files to create
- `oksquery_translator/ast/validator.py`

## Files that may be modified
- `oksquery_translator/ast/__init__.py`

## Files that must NOT be modified
- `oksquery_translator/executor.py` (Must remain intact)
- `oksquery_translator/validator.py` (Legacy validator remains as runtime fallback)
- `oksquery_translator/pipeline.py`

## Backward compatibility
- Existing validator in `oksquery_translator/validator.py` remains untouched.

## Testing and verification
Write test cases to verify:
1. Valid query passes:
   - Target class `Executable`, attribute `InitTimeout > 2`.
   - Assert `validator.validate(ir, ctx).valid` is True.
2. Case-sensitivity error detection:
   - Target class `Executable`, attribute `inittimeout > 2`.
   - Assert `valid` is False and error message contains `"InitTimeout"` and `"CASE"`.
3. Relationship error detection:
   - Target class `Application`, relationship `RunsOn` pointing to nested attribute on `Computer`.
   - Test invalid relationship name (e.g. `RunOn` -> suggests `RunsOn`).
   - Test attribute on wrong class (attribute of `Application` checked inside `RunsOn` on `Computer`).
4. Fingerprint presence:
   - Verify all validation error messages contain `ctx.schema_fingerprint`.

## Failure handling
- If superclass traversal misses attributes, verify `OksSchemaProvider.get_effective_members()` resolves inheritance depth completely.

## Final report
Report:
- Created file
- Test results for valid expressions, case mismatches, relationship target checks, and unknown attributes
```

---

# Prompt 6 — Refactor Translator to Use AST Pipeline with Context-Bound Repair Loop

```text
## Repository
- Root: /home/rhythm/Projects/cern_daq/cern
- Target Package: oksquery_translator

## Current state
`oksquery_translator/translator.py` currently instructs the LLM to generate plain text `CLASS: ... \n QUERY: ...` and parses it with regular expressions. `oksquery_translator/prompt_builder.py` constructs text prompts. The AST models, normalizer, context-bound validator, and compiler are now available in `oksquery_translator/ast/`. `oksquery_translator/executor.py` is ready to receive compiled queries.

## Objective
Refactor `Translator` (Module 8 + Module 11) to adopt the structured JSON IR/AST pipeline:
1. Update prompts to instruct the LLM to produce valid JSON matching the `QueryIR` schema and embed `OksContext` metadata.
2. Route LLM output through: Raw response -> Strip fences -> JSON parse -> `normalize_ir` -> `QueryIR` validation -> `ASTValidator` -> `OksCompiler.compile()`.
3. Implement the context-bound Repair Loop (Module 11): When normalization, IR validation, or semantic validation fails, feed the exact validation diagnostic (including schema fingerprint and schema hints) back to the LLM for up to `max_retries` attempts (default 2).

## Required repository inspection
Inspect:
1. `oksquery_translator/translator.py`: Inspect `_call_llm()`, error handling (HTTP status codes, OpenAI client), retry loops, and how return dicts are formatted.
2. `translator_module/agent/translator.py`: Inspect `IR_SCHEMA_DESCRIPTION`, system prompt phrasing, and how JSON was parsed and validated in the experimental module.
3. `oksquery_translator/prompt_builder.py`: Inspect `PromptBuilder.build()` and `build_repair_prompt()`.
4. `oksquery_translator/ast/`: Inspect `QueryIR`, `normalize_ir`, `ASTValidator`, and `OksCompiler`.
5. `oksquery_translator/executor.py`: Confirm that the compiled string format output by `OksCompiler` directly satisfies what `Executor.execute()` expects.

## Implementation requirements
Modify `oksquery_translator/translator.py` (and `prompt_builder.py` if necessary):

1. **System Prompt & IR Schema Specification**:
   - Embed the `IR_SCHEMA_DESCRIPTION` into the translation prompt.
   - Include `oks_context.to_prompt_metadata()` when `oks_context` is provided so the LLM is informed of the authoritative schema fingerprint.
   - Include the retrieved schema context slice and few-shot examples.
   - Instruct the LLM: Output ONLY valid JSON matching `QueryIR`. No markdown code fences, no commentary.

2. **Translator Implementation**:
   - Update `Translator.__init__`:
     - Maintain existing LLM configuration parameters (`llm_api_key`, `llm_base_url`, `llm_model`, `max_retries`).
     - Initialize `self.compiler = OksCompiler()`.
   - Update `Translator.translate(question: str, oks_context: Optional[OksContext] = None, retrieval_query: Optional[str] = None) -> Dict`:
     - If `oks_context` is omitted, build a default current context.
     - Prepare prompt using `retrieval_query or question` for schema retrieval.
     - Execute the generation + repair loop (max 1 + `max_retries` attempts):
       1. Call LLM (`_call_llm`).
       2. Strip markdown fences from content.
       3. Attempt `json.loads()`.
       4. Apply `normalize_ir()`.
       5. Validate against Pydantic `QueryIR`.
       6. Validate against `ASTValidator(schema_provider).validate(ir, oks_context)`.
       7. If valid: call `self.compiler.compile(ir, oks_context)` to produce `oks_query`. Return success dictionary:
          - `"status"`: `"success"`
          - `"target_class"`: `ir.target_class`
          - `"oks_query"`: `oks_query`
          - `"ir"`: `ir.model_dump()`
          - `"attempts"`: `attempt + 1`
          - `"explanation"`: `ir.explanation or ""`
       8. If invalid at any stage (JSON parse, normalization, Pydantic, or semantic validation):
          - Capture the error diagnostic message.
          - Construct a repair prompt containing:
            - The candidate AST/output that failed
            - The exact diagnostic message (including `schema_fingerprint`, missing attributes, casing corrections)
            - Targeted schema slice from `schema_provider`
          - Append assistant response and user repair prompt to message history and retry.
     - If all retries exhausted, return:
       - `"status"`: `"error"`
       - `"message"`: Error summary including the last diagnostic
       - `"attempts"`: `1 + max_retries`

## Integration requirements
- Maintain exact return dictionary keys expected by `pipeline.py` (`status`, `target_class`, `oks_query`, `attempts`, `message`).
- Preserve existing OpenAI client exception handling (401, 403, 404, 429, APIConnectionError).

## Version/schema requirements
- The repair prompt must reinforce the same `OksContext` and schema fingerprint; never introduce examples or schema definitions from a different version during repair.

## Files to create
- None

## Files that may be modified
- `oksquery_translator/translator.py`
- `oksquery_translator/prompt_builder.py`

## Files that must NOT be modified
- `oksquery_translator/executor.py` (Must remain intact)
- `oksquery_translator/pipeline.py` (Will be connected in Prompt 7)

## Backward compatibility
- `Translator.translate("query")` can still be called with just a string query.
- The return dictionary contains all previously standard keys plus the new optional `"ir"` key.

## Testing and verification
Execute tests:
1. Mocked LLM JSON response test:
   - Mock `_call_llm` to return `{"target_class": "Executable", "scope": "all", "expression": {"type": "attribute_compare", "attribute": "InitTimeout", "operator": ">", "value": "2"}}`.
   - Call `translator.translate(...)`.
   - Verify `status == "success"`, `target_class == "Executable"`, and `oks_query == '(all ("InitTimeout" "2" >))'`.
2. Repair loop simulation test:
   - Mock `_call_llm` to return invalid JSON on attempt 1, and valid JSON on attempt 2.
   - Verify `attempts == 2` and final `status == "success"`.
3. Semantic failure repair test:
   - Mock `_call_llm` to return attribute with wrong case `{"attribute": "inittimeout", ...}` on attempt 1, and corrected case `{"attribute": "InitTimeout", ...}` on attempt 2.
   - Verify repair message sent to attempt 2 contained the case correction diagnostic.

## Failure handling
- If JSON parsing fails due to LLM preamble or conversational text, ensure markdown fence stripping and raw JSON extraction regex cleanly isolate the outer `{ ... }` block.

## Final report
Report:
- Modified files
- Verification of JSON IR translation path
- Repair loop test results on simulated validation errors
```

---

# Prompt 7 — Complete End-to-End Pipeline Wiring with Executor Preservation

```text
## Repository
- Root: /home/rhythm/Projects/cern_daq/cern
- Target Package: oksquery_translator

## Current state
All core modules exist:
- `context`: `OksContext`, `OksContextBuilder`
- `preprocessing`: `QueryPreprocessor`
- `schema`: `OksSchemaProvider`
- `ast`: `QueryIR`, `normalize_ir`, `ASTValidator`, `OksCompiler`
- `translator`: AST-based translation with context-bound repair
- `executor`: Battle-tested dual-backend execution layer

## Objective
Update `OksPipeline` in `oksquery_translator/pipeline.py` to seamlessly connect the entire 12-module lifecycle:
1. Intent Classification & Run Resolution ->
2. `OksContext` Construction ->
3. `QueryPreprocessor` Analysis ->
4. Schema Retrieval (using enriched retrieval query) ->
5. AST Translation (`Translator` with bound `OksContext`) ->
6. Query Execution (`Executor` with version derived from `OksContext`) ->
7. Interpretation & Provenance Header Attachment.

## Required repository inspection
Inspect:
1. `oksquery_translator/pipeline.py`: Trace `OksPipeline.__init__` and `OksPipeline.answer()`.
2. `oksquery_translator/preprocessing/query_preprocessor.py`: Look at `QueryAnalysis.to_retrieval_query()`.
3. `oksquery_translator/executor.py`: Verify how `Executor.execute(target_class, query, version=...)` executes the compiled S-expression and handles `TDAQ_DB_VERSION` / `TDAQ_DB_PATH`.

## Implementation requirements
Modify `oksquery_translator/pipeline.py`:

1. In `OksPipeline.__init__`:
   - Initialize `self.query_preprocessor = QueryPreprocessor()`.
   - Ensure `self.context_builder`, `self.schema_retriever`, `self.translator`, `self.executor`, and `self.interpreter` are properly instantiated and share consistent configurations.
   - Ensure `self.executor = Executor(data_file=data_file)` is preserved.

2. In `OksPipeline.answer(question: str, version: Optional[str] = None) -> Dict`:
   - Step 0a-0c: Intent classification, out-of-scope early exit, historical run validation (preserve existing logic).
   - Step 0d: Context construction:
     - `oks_context = self.context_builder.build(version_tag=effective_version)`
   - Step 0e: Query Preprocessing:
     - `query_analysis = self.query_preprocessor.analyze(question)`
     - `retrieval_query = query_analysis.to_retrieval_query()`
   - Step 1: Translation:
     - Pass `oks_context` and `retrieval_query` into `self.translator.translate(question, oks_context=oks_context, retrieval_query=retrieval_query)`.
     - If translation fails, return error dict with context provenance fields populated.
   - Step 2: Execution:
     - Derive execution version string from `oks_context.version_tag or effective_version`.
     - Execute query via `self.executor.execute(target_class=target_class, query=oks_query, version=exec_version)`.
     - If execution fails, return error dict with context provenance.
   - Step 3: Interpretation:
     - Call `self.interpreter.interpret(...)`.
     - Ensure provenance headers (Run Number, Partition, Schema Fingerprint, or Current Configuration) are cleanly formatted.
   - Final return:
     - Include `status`, `answer`, `oks_query`, `target_class`, `result_count`, `results`, `attempts`, `intent`, `run_number`, `partition`, `version`, `version_used`, `"schema_fingerprint"`, `"oks_context_label"`, and optional `"ir"`.

## Integration requirements
- Maintain complete compatibility with `answer()` and `translate_only()`.
- Do not break existing CLI tools or test scripts that import `OksPipeline`.

## Version/schema requirements
- Enforce the Schema-Context Invariant: The same `oks_context` instance created in Step 0d must govern translation, validation, and execution.

## Files to create
- None

## Files that may be modified
- `oksquery_translator/pipeline.py`

## Files that must NOT be modified
- `oksquery_translator/executor.py` (Must remain intact)
- `oksquery_translator/intent.py`
- `oksquery_translator/ast/*`

## Backward compatibility
- CLI commands (`python -m oksquery_translator ...`) and convenience function `answer()` must work without breaking changes.

## Testing and verification
Run end-to-end integration checks:
1. Out-of-scope check:
   - Query: `"How do I cook pasta?"`
   - Verify early exit with `intent == "GENERAL_OUT_OF_SCOPE"`.
2. Translate-only check:
   - Call `pipeline.translate_only("Which computers have RAM > 16?")`
   - Verify translation returns target class and valid OksQuery string.
3. Full pipeline answer check (with mocked or real executor):
   - Verify `schema_fingerprint` in return dictionary matches `OksContext`.
   - Verify interpretation output contains appropriate header.
   - Verify execution was handled by `pipeline.executor`.

## Failure handling
- If `translate()` encounters missing attributes during validation, verify the repair cycle triggers and attempts recovery before failing.

## Final report
Report:
- Modified files
- Pipeline execution trace
- Test results for current and historical queries
```

---

# Prompt 8 — Fingerprint-Scoped Schema Indexing & Caching (Module 4)

```text
## Repository
- Root: /home/rhythm/Projects/cern_daq/cern
- Target Package: oksquery_translator

## Current state
Schema slices are currently retrieved through keyword matching against the active schema. The architecture specification (PDF Section 19 & 20) defines a version-scoped `ClassSearchDocument` index where all retrieval documents and BM25/FTS indices are strictly keyed by `schema_fingerprint`.

## Objective
Implement `SchemaSearchIndex` in `oksquery_translator/retrieval/`:
1. Define `ClassSearchDocument` conforming to Section 19 of the architecture specification.
2. Build an in-memory or persisted index keyed by `schema_fingerprint`.
3. Provide `search(query, schema_fingerprint, top_k)` that guarantees schema candidates are returned ONLY from the matching fingerprint.
4. Integrate the index with `OksPipeline` and `SchemaRetriever` to prevent cross-version schema pollution.

## Required repository inspection
Inspect:
1. `docs/architecture/nl_to_oksquery_architecture.pdf`: Review Section 19 (Listing 4) for `ClassSearchDocument` schema.
2. `oksquery_translator/schema_retrieval.py`: Inspect `_match_classes()` and how class names and keyword boosts are computed.
3. `oksquery_translator/schema/oks_schema_provider.py`: Inspect how `OksSchemaProvider` provides class definitions and members.

## Implementation requirements
Create `oksquery_translator/retrieval/`:

1. `oksquery_translator/retrieval/schema_index.py`:
   - Data structure `ClassSearchDocument`:
     - `schema_fingerprint: str`
     - `class_name: str`
     - `tokens: list[str]` (CamelCase-split tokens + description keywords)
     - `attributes: list[str]` (exact attribute names)
     - `relationships: list[str]` (exact relationship names)
     - `relationship_targets: list[str]` (target class names)
     - `description: str`
     - `git_revision: str`
   - Class `SchemaSearchIndex`:
     - Maintain an internal store mapping `schema_fingerprint -> list[ClassSearchDocument]`.
     - Method `build_from_schema_provider(schema_provider: OksSchemaProvider) -> str`:
       - Extracts `schema_fingerprint` from `schema_provider.oks_context`.
       - If fingerprint is already indexed, returns immediately (idempotent caching).
       - Iterates over all classes from `schema_provider`, building a `ClassSearchDocument` for each.
       - Tokenizes class names (splitting CamelCase words: e.g. `"RunControlApplication"` -> `["run", "control", "application"]`).
       - Indexes attributes and relationship names.
       - Returns `schema_fingerprint`.
     - Method `search(query: str, schema_fingerprint: str, top_k: int = 5) -> list[ClassSearchDocument]`:
       - **CRITICAL INVARIANT**: Look up documents ONLY within `self._index[schema_fingerprint]`.
       - If `schema_fingerprint` is not indexed, log a warning and return an empty list (never fall back to another version's index).
       - Scores matching documents based on:
         - Exact class name match (+10.0)
         - Token match in class name (+5.0)
         - Attribute/relationship name match (+3.0)
         - Partial/description match (+1.0)
       - Returns top `top_k` documents sorted by relevance.
     - Method `has_fingerprint(schema_fingerprint: str) -> bool`.

2. `oksquery_translator/retrieval/__init__.py`:
   - Export `SchemaSearchIndex`, `ClassSearchDocument`.

3. Integrate into `oksquery_translator/pipeline.py`:
   - In `OksPipeline.__init__`, instantiate `self.schema_index = SchemaSearchIndex()`.
   - In `OksPipeline.answer()`, after `oks_context` is constructed, ensure `self.schema_index.has_fingerprint(oks_context.schema_fingerprint)` is checked, calling `build_from_schema_provider` if not present.

## Integration requirements
- Provide an adapter method so `SchemaRetriever` or `PromptBuilder` can query `SchemaSearchIndex` using `oks_context.schema_fingerprint`.

## Version/schema requirements
- The index MUST be partitioned by `schema_fingerprint`.
- Cross-version schema search is strictly forbidden.

## Files to create
- `oksquery_translator/retrieval/__init__.py`
- `oksquery_translator/retrieval/schema_index.py`

## Files that may be modified
- `oksquery_translator/pipeline.py`
- `oksquery_translator/schema_retrieval.py`

## Files that must NOT be modified
- `oksquery_translator/executor.py` (Must remain intact)
- `oksquery_translator/ast/*`
- `oksquery_translator/intent.py`

## Backward compatibility
- Existing fallback retrieval mechanisms must continue to operate when no versioned index is explicitly requested.

## Testing and verification
Write test cases:
1. Index construction & fingerprint partitioning:
   - Build index for Context A (fingerprint `AAAA`).
   - Build index for Context B (fingerprint `BBBB`).
   - Verify `index.search(query, "AAAA")` only returns documents tagged with `AAAA`.
   - Verify searching for non-existent fingerprint `"CCCC"` returns empty list and does not crash.
2. Ranking test:
   - Query: `"timeout"` -> verify classes with `InitTimeout` or `ExitTimeout` score higher than unrelated classes.
3. CamelCase tokenization test:
   - Verify `"ROSDescriptor"` matches query token `"ros"`.

## Failure handling
- If class count is large, ensure index building is only executed once per unique `schema_fingerprint`.

## Final report
Report:
- Created files
- Index partitioning test results
- Search ranking benchmark results
```

---

# Prompt 9 — End-to-End Test Suite, Migration Cleanup & Deprecation Notice

```text
## Repository
- Root: /home/rhythm/Projects/cern_daq/cern
- Target Package: oksquery_translator

## Current state
All 12 modules of the NL -> OKSQuery architecture have been implemented, connected, and fingerprint-scoped across `oksquery_translator/`. `oksquery_translator/executor.py` executes queries against the real OKS engine. The experimental `translator_module/` directory still exists as a reference.

## Objective
1. Run the full pytest test suite and write comprehensive integration tests verifying the 15 architectural invariants.
2. Verify that the execution layer (`Executor`) is intact, functional, and correctly receives compiled OksQuery strings.
3. Ensure clean public package exports in `oksquery_translator/__init__.py`.
4. Add a clear deprecation and migration notice in `translator_module/DEPRECATED.md`.
5. Create an architectural verification report in `docs/architecture/implementation_status.md`.

## Required repository inspection
Inspect:
1. `oksquery_translator/tests/`: Inspect existing test files and pytest configurations.
2. `oksquery_translator/executor.py`: Confirm `Executor` remains unchanged and operational.
3. Check for any remaining external imports of `translator_module` across the codebase using `grep -r "translator_module" .`.
4. Review the 15 Architectural Invariants listed in the architecture guide.

## Implementation requirements

1. **New Integration Test Suite (`oksquery_translator/tests/test_architecture_invariants.py`)**:
   Write tests explicitly verifying:
   - **Invariant 1 & 2**: `OksContext` is immutable and created once per request.
   - **Invariant 3 & 4**: `schema_fingerprint` is deterministic and content-derived from the resolved schema.
   - **Invariant 5**: `SchemaSearchIndex` never returns documents across different fingerprints.
   - **Invariant 6 & 10**: `ASTValidator` validates expressions against the exact context schema (verifying case-sensitivity, invalid attributes, and relationship targets).
   - **Invariant 8 & 9**: `normalize_ir` deterministically normalizes operators/values without LLM calls.
   - **Invariant 11**: `OksCompiler` deterministically compiles `QueryIR` to valid OKSQuery S-expressions without LLM calls.
   - **Invariant 12**: Repair prompts contain the failing diagnostic, casing correction, and `schema_fingerprint`.
   - **Invariant 13 (Executor Preservation)**: `Executor` successfully accepts and processes the compiled query string.
   - Out-of-scope queries exit early with empty fingerprints.

2. **Package Exports (`oksquery_translator/__init__.py`)**:
   Ensure all canonical classes and functions are exported:
   - `OksPipeline`, `answer`
   - `Intent`, `IntentResult`, `IntentClassifier`, `RunResolver`, `extract_run_and_partition`
   - `Executor`, `ExecutionResult`
   - `OksContext`, `OksContextBuilder`, `compute_fingerprint`
   - `QueryPreprocessor`, `QueryAnalysis`
   - `OksSchemaProvider`, `ClassDefinition`, `AttributeDefinition`, `RelationshipDefinition`
   - `QueryIR`, `normalize_ir`, `OksCompiler`, `ASTValidator`, `ValidationResult`
   - `SchemaSearchIndex`, `ClassSearchDocument`

3. **Deprecation Notice (`translator_module/DEPRECATED.md`)**:
   Document that `translator_module` has been fully superseded by `oksquery_translator`. Map old component paths to new component paths and provide instructions on when it is safe to delete.

4. **Implementation Status Report (`docs/architecture/implementation_status.md`)**:
   Document the completed 12-module pipeline, module map, and the status of all 15 invariants.

## Integration requirements
- All tests in `oksquery_translator/tests/` must pass.

## Files to create
- `oksquery_translator/tests/test_architecture_invariants.py`
- `translator_module/DEPRECATED.md`
- `docs/architecture/implementation_status.md`

## Files that may be modified
- `oksquery_translator/__init__.py`

## Files that must NOT be modified
- `oksquery_translator/executor.py` (Must remain intact)

## Backward compatibility
- All existing public interfaces must pass regression checks.

## Testing and verification
Execute:
1. `pytest oksquery_translator/tests/ -v`
2. Run a full smoke test script validating the complete pipeline without LLM (using mocked responses or non-LLM components).
3. Check for lingering references to deprecated modules.

## Failure handling
- Distinguish between:
  - Code defects (must be fixed)
  - Missing CERN/TDAQ C++ runtime environment (e.g. `oks_dump` or `config` C-extensions not in path — tests must handle gracefully with informative skip/mock warnings).

## Final report
Report:
- Full list of created and modified files
- Pytest execution summary (passed, failed, skipped)
- Verification checklist for all 15 architectural invariants
```
