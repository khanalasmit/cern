# Historical Query Development Log

This log records the implementation work for querying historical OKS run configurations through Git revisions.

The related implementation playbook is [HISTORICAL_QUERY_GUIDE.md](HISTORICAL_QUERY_GUIDE.md).

## 2026-08-23 — Initial development slice

### Scope

Implemented the first isolated foundation slice from the guide:

- Revision request and provenance data models.
- Immutable OKS snapshot contract.
- Read-only filesystem source abstraction.
- Working-tree source implementation.
- Unit tests that do not require an LLM, network access, FAISS, or Git history.

### Files created

- `translator_module/revision/__init__.py`
- `translator_module/revision/models.py`
- `translator_module/revision/source.py`
- `translator_module/tests/test_historical_query.py`
- `HISTORICAL_QUERY_DEVELOPMENT_LOG.md`

### Design decisions

1. The revision layer is isolated under `translator_module/revision/`.
2. `RevisionRequest` represents user intent; it does not resolve Git references.
3. `ResolvedRevision` stores the full commit SHA and provenance fields.
4. `OksSnapshot` keeps schema paths and data paths associated with one revision.
5. `FileSource` is the dependency boundary that will later allow the RAG and execution layers to read either the working tree or Git objects.
6. The first source implementation is `WorkingTreeSource`; Git access will be added separately.
7. Paths are validated as repository-relative paths and cannot use absolute paths or `..` traversal.

### Existing behavior preserved

- No current CLI behavior was changed.
- No RAG behavior was changed.
- No serializer behavior was changed.
- No dependency was added.
- The existing `HISTORICAL_QUERY_GUIDE.md` remains unchanged.

### Verification pending

Run:

```bash
python -m unittest translator_module.tests.test_historical_query -v
python -m unittest discover -s translator_module/tests -v
```

### Verification results

Syntax compilation:

```text
python -m py_compile translator_module/agent/ir_validator.py translator_module/agent/translator.py translator_module/execution/context.py translator_module/execution/executor.py
Passed
```

Historical-query tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 34 tests in 6.455s
OK (skipped=2)
```

Full suite using the documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 55 tests in 6.482s
OK (skipped=2)
```

The standalone `test_translator` command without `PYTHONPATH=translator_module` failed during discovery because the existing tests import `agent` as a top-level package. The full documented suite passed, including the new target-class test.

### Current status

`QueryIR` can now carry a target class, and historical execution has a backend adapter contract. A native OKS backend is still required before real historical query execution can occur.

### Verification results

Focused historical-query tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 11 tests in 2.149s
OK
```

Full suite using the documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 25 tests in 2.205s
OK
```

### Current status

The read-only Git source is implemented and verified. The next slice is revision resolution: converting a commit hash, tag, or date request into a deterministic `ResolvedRevision`.

## 2026-08-23 — Revision resolution

### Scope

Implemented deterministic resolution of Git revision requests:

- Short or full commit hash to full commit SHA.
- Git tag to tagged commit.
- Timezone-aware date to the newest commit at or before that time on a selected ref.
- No selector to current `HEAD`.
- Explicit rejection of ambiguous selectors.
- Explicit rejection of run IDs until a run-to-commit registry is implemented.

### Safety decisions

1. Resolution uses read-only `git rev-parse`, `git rev-list`, and `git show` commands.
2. The resolver never changes the active branch or working tree.
3. Date requests must carry an explicit timezone offset.
4. Date selection is deterministic and limited to the requested Git ref.
5. A missing historical range is an error; it never falls back to the current revision.

### Files created or modified

- Created: `translator_module/revision/resolver.py`
- Modified: `translator_module/revision/__init__.py`
- Modified: `translator_module/tests/test_historical_query.py`
- Updated: `HISTORICAL_QUERY_DEVELOPMENT_LOG.md`

### Verification pending

Run:

```bash
python -m unittest translator_module.tests.test_historical_query -v
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
```

### Verification results

Syntax compilation:

```text
python -m py_compile translator_module/agent/translator.py translator_module/cli.py
Passed
```

CLI tests:

```text
python -m unittest translator_module.tests.test_cli -v
Ran 6 tests in 0.020s
OK
```

Historical-query tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 26 tests in 5.664s
OK (skipped=2)
```

Full suite using the documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 46 tests in 5.698s
OK (skipped=2)
```

### Current status

`OksTranslator` now accepts source-backed schemas directly, and the CLI no longer materializes a temporary historical schema file. The next integration boundary is historical data-path discovery and execution context; current translation still uses the existing few-shot file and does not execute OKS queries. (Superseded by the continuation entries below.)

## Continuation checkpoint — 2026-08-23

The following implementation slices were completed and pushed to `origin/feat/eval-dataset-and-rag-v2` after the earlier translator integration entry:

1. `beb14be` — added safe source materialization and the `oks_dump` subprocess adapter.
2. `19c9ca4` — added opt-in CLI historical execution with `--execute`, repeatable `--data-path`, `--target-class`, executable, and timeout options.
3. `fbd85d0` — loaded historical few-shot examples from the selected Git revision with no current-tree fallback.
4. `63182cb` — added auditable `revision_provenance` to successful historical translations.

The final verification for this continuation is:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 40 tests in 6.161s
OK (skipped=2)

$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 63 tests in 6.234s
OK (skipped=2)
```

The two skips are the existing RAG tests because the local environment does not have `rank_bm25`. The native `oks_dump` executable is also not installed locally; its adapter is covered with mocked subprocess tests and reports a clear runtime error until OKS is available.

The working tree was clean after the push. The next implementation decision is whether the deployment can provide a stable machine-readable `oks_dump` output mode; until then, historical execution intentionally exposes raw stdout and does not guess at a row parser.

## OksDump subprocess adapter

### Scope

The historical snapshot can now be handed to the native OKS query runtime without checking out the requested revision. This slice adds a subprocess adapter for the documented `oks_dump` command and makes both working-tree and Git-backed sources materializable as temporary directories.

### Implementation

- Added `FileSource.materialize()` as the common context-manager boundary for runtime tools that require filesystem paths.
- `WorkingTreeSource.materialize()` yields its existing root without copying files.
- `GitRevisionSource.materialize()` creates a temporary directory from `git archive` at the resolved commit. It validates archive members and rejects unsafe paths or links before extraction.
- Added `translator_module/execution/oks_dump.py` with `OksDumpExecutor`, `OksDumpResult`, and `OksDumpError`.
- The adapter invokes `oks_dump --class <target_class> --query <query> <data files>` with argument lists rather than shell strings, applies a timeout, preserves stdout/stderr, and reports documented native exit-code meanings.
- The adapter returns the native text output unchanged. Result normalization is intentionally deferred until the OKS output format and target-class semantics are confirmed.
- Schema paths are not passed as separate command arguments because the existing OKS usage documents the data file(s) as the runtime input; the snapshot still retains both schema and data paths for validation and future backends.

### Tests and verification

- Added a Git-source materialization test proving historical files are available from a temporary directory while the working tree remains unchanged.
- Added mocked subprocess tests for safe command construction, missing `oks_dump`, timeout/error behavior, and native failure codes.
- The local environment does not provide an `oks_dump` executable, so native-runtime tests are mocked. The adapter will fail clearly with `OksDumpError` until the OKS runtime is installed and discoverable on `PATH`.
- Focused historical-query suite: 38 tests passed, 2 dependency-based tests skipped.
- Full suite: 59 tests passed, 2 dependency-based tests skipped.

### Current status

Historical sources can now safely cross the boundary into a native execution tool. The next integration slice should decide how the CLI requests execution and how native `oks_dump` output is represented in the public query result, while preserving the current translation-only behavior by default.

## CLI execution integration

### Scope

The interactive CLI can now opt into executing translated historical queries. Translation-only behavior remains the default, so selecting a past revision does not require historical data files unless `--execute` is supplied.

### Implementation

- Added repeatable `--data-path` arguments for explicit repository-relative data files. When omitted, execution discovers `test_data/**/*.data.xml` in the selected revision.
- Added `--execute`, which requires one historical selector (`--commit-hash`, `--tag`, `--date`, or `--run-id`).
- Added `--target-class` as an execution-time override when the LLM does not emit a usable `target_class`.
- Added `--oks-dump-executable` and `--execution-timeout` for deployment-specific runtime configuration.
- Historical initialization now builds an `OksSnapshot` only for execution, keeping schema-only historical translation compatible with commits that do not contain data files.
- The CLI constructs `HistoricalExecutionContext` from the translated query and invokes `OksDumpExecutor` against the selected snapshot. Git-backed execution materializes only inside the adapter's temporary-directory context.

### Tests and verification

- Added parser coverage for repeatable data paths, target-class overrides, executable configuration, and timeout configuration.
- Added a guard test proving `--execute` cannot silently run against the current working tree.
- `python -m py_compile translator_module/cli.py translator_module/tests/test_cli.py` passed.
- Full suite: 61 tests passed, 2 dependency-based tests skipped because `rank_bm25` is not installed locally.

### Current status

The end-to-end CLI boundary is now present: historical revision selection -> source-backed schema RAG -> translation/validation/serialization -> optional historical `oks_dump` execution. Native output is still displayed as raw text because `oks_dump` is human-readable and its exact deployment-specific output format has not yet been standardized.

## Historical few-shot source integration

### Scope

Historical schema retrieval must not be paired with current-working-tree prompt examples. The few-shot loader now supports reading `gold_pairs.jsonl` through the same `FileSource` as the selected schema revision.

### Implementation

- Added `FewShotManager.from_source(source, source_path, encoder=...)`.
- The loader decodes JSONL bytes from the revision source and preserves the existing semantic-selection and random-fallback behavior.
- Missing historical examples produce `No examples available.` without falling back to a current file.
- `OksTranslator` accepts `few_shot_source` and `few_shot_path` while preserving existing path-based callers.
- Historical CLI initialization now reads `--gold-pairs` from the selected Git revision. Current-mode CLI initialization continues to read the working-tree path.
- The optional `sentence_transformers` import is now safe in minimal test environments; source-backed loading can operate without embeddings and use the existing fallback selection.

### Tests and verification

- Added tests for loading revision-backed examples and for the no-fallback behavior when the historical file is absent.
- `python -m py_compile translator_module/agent/few_shot.py translator_module/agent/translator.py translator_module/cli.py translator_module/tests/test_historical_query.py` passed.
- Full suite: 63 tests passed, 2 dependency-based tests skipped because `rank_bm25` is not installed locally.

### Current status

The historical schema and few-shot prompt inputs now come from one selected Git revision. The remaining user-facing correctness work is to validate that serialized queries reference identifiers available in the historical schema and to make runtime output auditable and machine-readable where the native OKS tool permits it.

## Historical result provenance

### Scope

Successful historical translations now carry enough metadata to identify the exact source selection that produced them. The existing `revision` SHA field remains available for compatibility.

### Implementation

- `OksTranslator` accepts the resolved `ResolvedRevision` as optional `revision_metadata`.
- The CLI passes the resolved revision object into the translator.
- Historical success results now include `revision_provenance` with repository, full commit SHA, selection method, ref, commit timestamp when available, and run ID when applicable.
- A mismatch between the legacy `revision` string and `revision_metadata.commit` fails during initialization instead of producing misleading provenance.
- Current working-tree callers remain compatible and do not receive historical provenance fields.

### Verification

- The provenance implementation is syntax-checked with the existing translator/CLI compile check.
- Existing historical and full test suites remain the required regression checks; no runtime LLM call is made by the tests.

### Current status

Historical schema, few-shot inputs, serialized query, and result metadata now share one revision identity. The next validation step is to add a schema-aware identifier check before execution so a query that passed the generic IR validator cannot silently target a class or attribute absent from the old schema.

## 2026-08-23 — Target class and execution adapter boundary

### Scope

Implemented the next execution contract:

- Added optional `target_class` to `QueryIR` for backward-compatible evaluation rows.
- Updated the translator IR prompt to request `target_class` for executable queries.
- Added `HistoricalExecutionContext.require_target_class()`.
- Added the `OksExecutionBackend` protocol.
- Added `HistoricalOksExecutor` and provenance-bearing `ExecutionResult`.
- Added tests for missing backends, missing target classes, and backend context forwarding.
- Kept serialization unchanged.

### Safety decisions

1. `target_class` is optional during migration so existing dataset rows do not break.
2. Historical execution rejects contexts without a target class.
3. No fake OKS parser or query semantics were invented.
4. The native backend receives the complete historical snapshot, serialized query, and target class together.
5. The executor raises a clear error until a native OKS backend is configured.

### Files created or modified

- Modified: `translator_module/agent/ir_validator.py`
- Modified: `translator_module/agent/translator.py`
- Modified: `translator_module/execution/context.py`
- Created: `translator_module/execution/executor.py`
- Modified: `translator_module/execution/__init__.py`
- Modified: `translator_module/tests/test_historical_query.py`
- Modified: `translator_module/tests/test_translator.py`
- Updated: `HISTORICAL_QUERY_DEVELOPMENT_LOG.md`

### Verification pending

Run:

```bash
python -m py_compile translator_module/agent/ir_validator.py translator_module/agent/translator.py translator_module/execution/context.py translator_module/execution/executor.py
python -m unittest translator_module.tests.test_historical_query -v
python -m unittest translator_module.tests.test_translator -v
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
```

## 2026-08-23 — Historical snapshot and execution context

### Scope

Implemented the historical data boundary without inventing an OKS runtime:

- Added `SnapshotBuilder` and configurable schema/data glob patterns.
- Extended `OksSnapshot` to retain its source object.
- Added required schema and data path discovery from one revision.
- Added `HistoricalDataLoader` for standalone and embedded data XML.
- Added immutable `HistoricalExecutionContext` containing snapshot, serialized query, and optional target class.
- Added tests for discovery, missing files, data parsing, and source consistency.

### Safety decisions

1. A snapshot owns both schema and data paths and the source that serves them.
2. By default, historical execution requires at least one schema and one data file.
3. Missing required files fail snapshot construction instead of silently using current files.
4. The execution context does not execute queries yet; it provides the boundary for a future OKS adapter.
5. The future executor will receive the same snapshot used for translation, preventing schema/data revision mixing.

### Files created or modified

- Modified: `translator_module/revision/models.py`
- Created: `translator_module/revision/snapshot.py`
- Modified: `translator_module/revision/__init__.py`
- Created: `translator_module/execution/__init__.py`
- Created: `translator_module/execution/data_loader.py`
- Created: `translator_module/execution/context.py`
- Modified: `translator_module/tests/test_historical_query.py`
- Updated: `HISTORICAL_QUERY_DEVELOPMENT_LOG.md`

### Verification results

Syntax compilation:

```text
python -m py_compile translator_module/revision/models.py translator_module/revision/snapshot.py translator_module/execution/data_loader.py translator_module/execution/context.py
Passed
```

Historical-query tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 31 tests in 6.393s
OK (skipped=2)
```

Full suite using the documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 51 tests in 6.489s
OK (skipped=2)
```

### Current status

Historical schemas and data can now be discovered and loaded from one source-backed snapshot. The next step is to pass that snapshot through translation and add a real OKS execution adapter, including a target class in the IR.

### Verification results

Historical-query and loader tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 26 tests in 6.361s
OK (skipped=2)
```

CLI tests:

```text
python -m unittest translator_module.tests.test_cli -v
Ran 6 tests in 0.014s
OK
```

Full suite using the documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 46 tests in 6.494s
OK (skipped=2)
```

The two skips are the dependency-heavy `HybridIndexer` tests; they report that `rank_bm25` is not installed in the current environment. The source-loader tests and every existing test pass.

### Current status

The RAG layer can now ingest source-backed scraped or standalone schema XML without requiring a checkout. The next integration step is to make `OksTranslator` accept the source/index context directly and remove the CLI’s temporary schema-file bridge.

### Verification results

CLI tests:

```text
python -m unittest translator_module.tests.test_cli -v
Ran 6 tests in 0.036s
OK
```

Historical-query tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 21 tests in 7.579s
OK
```

Full suite using the documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 41 tests in 7.620s
OK
```

The CLI negative tests intentionally exercise argparse failures for a naive timestamp and mutually exclusive selectors; their usage/error output is expected.

### Current status

The branch has been pushed to `origin/feat/eval-dataset-and-rag-v2`. CLI revision selection is implemented and tested. The next source-integration slice should replace the temporary schema-file bridge with a source-aware RAG loader and begin handling historical schema/data paths together.

## 2026-08-23 — Source-aware RAG schema loading

### Scope

Started replacing the path-only RAG boundary:

- Added `SchemaLoader` for the scraped wrapper format and standalone OKS schema XML.
- Added `SchemaDocument` and source-path metadata.
- Added `HybridIndexer.ingest_source(source, paths, revision=...)`.
- Preserved `HybridIndexer.ingest_xml(path)` for existing callers.
- Added revision and source-path metadata to generated schema chunks.
- Added malformed XML errors that include source and parser location.
- Added tests for scraped schemas, standalone schemas, and source-based index ingestion.

### Safety decisions

1. The old path-based ingestion API remains available.
2. Source-based ingestion resets the index before building it, preventing schema chunks from multiple revisions being mixed.
3. Historical source paths are read through `FileSource`; the indexer does not know whether the bytes came from Git or the working tree.
4. Malformed XML is no longer silently ignored.
5. The current chunking behavior is preserved; inheritance and metadata expansion remain future work described in `rag.md`.

### Verification note

The first loader test run could not import `HybridIndexer` because `rank_bm25` is not installed in the current environment, although it is declared in `translator_module/requirements.txt`. The dependency-heavy indexer tests are now skipped with an explicit reason when the RAG dependencies are unavailable; source-loader tests remain independent and runnable.

### Files created or modified

- Created: `translator_module/rag/schema_loader.py`
- Modified: `translator_module/rag/ingest.py`
- Modified: `translator_module/tests/test_historical_query.py`
- Updated: `HISTORICAL_QUERY_DEVELOPMENT_LOG.md`

### Verification pending

Run:

```bash
python -m unittest translator_module.tests.test_historical_query -v
python -m unittest translator_module.tests.test_cli -v
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
```

### Verification results

Focused historical-query tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 21 tests in 6.398s
OK
```

Full suite using the documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 35 tests in 6.515s
OK
```

The first run had one failure in the new run-ID test because the selector control flow overwrote the registered commit with `HEAD`. That was corrected before the successful verification above.

### Current status

Explicit run-ID resolution is implemented, tested, documented, and ready for CLI integration.

## 2026-08-23 — CLI revision selection

### Scope

Pushed the completed revision work and started CLI integration:

- Added mutually exclusive `--commit-hash`, `--tag`, `--date`, and `--run-id` options.
- Added `--repo`, `--ref`, `--run-map`, `--schema-path`, and `--gold-pairs` options.
- Added timezone-aware ISO-8601 date parsing.
- Added CLI helpers for constructing `RevisionRequest` objects.
- Kept default behavior on the current working-tree schema.
- Added a temporary historical schema-blob bridge for the current path-based `OksTranslator` API.
- Added parser tests that do not start an LLM or access the network.

### Safety decisions

1. The CLI resolves a historical revision before constructing the translator.
2. Historical schema bytes are read through `GitRevisionSource` and written only to a temporary file because the current translator still requires a filesystem path.
3. The active Git checkout is never changed.
4. The temporary schema file is deleted immediately after translator initialization; the in-memory index is retained.
5. The current `gold_pairs.jsonl` remains a working-tree source until historical few-shot source injection is implemented.
6. A run ID requires an explicit `--run-map` path.

### Files created or modified

- Modified: `translator_module/cli.py`
- Created: `translator_module/tests/test_cli.py`
- Updated: `HISTORICAL_QUERY_DEVELOPMENT_LOG.md`

### Verification pending

Run:

```bash
python -m unittest translator_module.tests.test_cli -v
python -m unittest translator_module.tests.test_historical_query -v
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
```

### Verification results

Focused historical-query tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 18 tests in 5.371s
OK
```

Full suite using the documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 32 tests in 5.304s
OK
```

### Current status

Commit, tag, date, and current-HEAD resolution are implemented and verified. Run-ID resolution remains intentionally blocked until the explicit run-to-commit registry slice is implemented next.

## 2026-08-23 — Run-ID registry

### Scope

Implemented explicit run-to-commit resolution using JSON:

- Added `RunRevisionRegistry` and `RunRevision` data objects.
- Added validation for missing commits, malformed entries, empty IDs, and whitespace in commit references.
- Added support for string entries and metadata objects containing `commit` and optional `timestamp`.
- Connected `GitRevisionResolver` to an optional registry.
- Added a sample file at `run_revisions.example.json` using placeholder commits.
- Updated the implementation guide to record JSON as the selected format.

### Safety decisions

1. Run IDs are resolved only through an explicit registry.
2. A missing run ID fails instead of falling back to a date or current `HEAD`.
3. A registered but invalid commit is still verified by Git before resolution succeeds.
4. Registry timestamps are metadata only; the authoritative timestamp remains the Git commit timestamp.
5. JSON was selected to avoid adding a YAML dependency at this stage.

### Verification note

The first test run exposed a selector-control-flow bug: the run-ID branch resolved the registered commit, but the later no-selector fallback overwrote it with `HEAD`. The resolver was corrected to use one mutually exclusive `if`/`elif` chain for run-ID, date, commit, tag, and current resolution.

### Files created or modified

- Created: `translator_module/revision/run_registry.py`
- Created: `run_revisions.example.json`
- Modified: `translator_module/revision/resolver.py`
- Modified: `translator_module/revision/__init__.py`
- Modified: `translator_module/tests/test_historical_query.py`
- Updated: `HISTORICAL_QUERY_GUIDE.md`
- Updated: `HISTORICAL_QUERY_DEVELOPMENT_LOG.md`

### Verification pending

Run:

```bash
python -m unittest translator_module.tests.test_historical_query -v
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
```

### Verification note

The first test run exposed one implementation issue: passing the nested glob directly to `git ls-tree` returned no match, although the equivalent working-tree glob matched. The implementation was corrected to list the historical tree and apply `PurePosixPath.match()` in Python, keeping `GitRevisionSource` and `WorkingTreeSource` consistent.

The results will be appended below after execution.

### Verification results

Focused foundation tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 6 tests in 0.029s
OK
```

Full suite using the repository’s documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 20 tests in 0.079s
OK
```

An initial full-suite invocation without `PYTHONPATH=translator_module` failed during test discovery because the pre-existing tests import `agent` as a top-level package. This is an invocation issue, not a regression. The documented invocation passed all 20 tests.

### Current status

Completed the first development slice. No Git resolver, RAG integration, CLI flags, or execution behavior has been added yet. The next slice is the read-only `GitRevisionSource` backed by temporary repositories in tests.

## 2026-08-23 — Git revision source

### Scope

Started the next implementation slice from the guide:

- Added `GitRevisionSource` using read-only Git object commands.
- Added historical blob reads with `git show`.
- Added historical existence checks with `git cat-file`.
- Added historical file discovery with `git ls-tree`.
- Added temporary-repository tests across two commits.
- Exported the new source and its exception from the revision package.

### Safety decisions

1. Git commands use `subprocess.run` with argument lists and `shell=False`.
2. No command performs checkout, reset, fetch, pull, or another working-tree mutation.
3. The source normalizes a supplied revision to a full commit SHA during initialization.
4. Historical paths pass through the existing repository-relative path validation.
5. Missing historical files raise `GitSourceError` when read and return `False` from `exists()`.

### Files created or modified

- Created: `translator_module/revision/git_source.py`
- Modified: `translator_module/revision/__init__.py`
- Modified: `translator_module/tests/test_historical_query.py`
- Updated: `HISTORICAL_QUERY_DEVELOPMENT_LOG.md`

### Verification pending

Run:

```bash
python -m unittest translator_module.tests.test_historical_query -v
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
```

## 2026-08-23 — Translator source integration

### Scope

Started the translator integration slice:

- Extended `OksTranslator` with `schema_source`, `schema_paths`, and `revision` parameters.
- Preserved the existing path-based constructor behavior.
- Added mutual-exclusion and missing-source validation.
- Added historical revision context to the LLM system prompt.
- Added revision provenance to successful translation results.
- Removed the CLI temporary schema-file bridge.
- The CLI now passes `GitRevisionSource` directly to `OksTranslator`.

### Safety decisions

1. Historical schema bytes remain outside the working tree.
2. The RAG index is built directly from the selected `FileSource`.
3. A translator cannot silently use both a filesystem schema path and a source-backed schema.
4. Existing callers using `OksTranslator(schema_xml_path, gold_pairs_path, ...)` remain supported.
5. The serializer remains revision-independent; revision metadata stays around the query result.

### Files created or modified

- Modified: `translator_module/agent/translator.py`
- Modified: `translator_module/cli.py`
- Updated: `HISTORICAL_QUERY_DEVELOPMENT_LOG.md`

### Verification pending

Run:

```bash
python -m py_compile translator_module/agent/translator.py translator_module/cli.py
python -m unittest translator_module.tests.test_cli -v
python -m unittest translator_module.tests.test_historical_query -v
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
```

### Verification results

Syntax compilation:

```text
python -m py_compile translator_module/agent/translator.py translator_module/cli.py
Passed
```

CLI tests:

```text
python -m unittest translator_module.tests.test_cli -v
Ran 6 tests in 0.020s
OK
```

Historical-query tests:

```text
python -m unittest translator_module.tests.test_historical_query -v
Ran 26 tests in 5.664s
OK (skipped=2)
```

Full suite using the documented `PYTHONPATH` setup:

```text
$env:PYTHONPATH='translator_module'
python -m unittest discover -s translator_module/tests -v
Ran 46 tests in 5.698s
OK (skipped=2)
```

### Current status

`OksTranslator` now accepts source-backed schemas directly, and the CLI no longer materializes a temporary historical schema file. The next integration boundary is historical data-path discovery and execution context; current translation still uses the existing few-shot file and does not execute OKS queries.

## Final continuation checkpoint — 2026-08-23

Pushed implementation commits after the earlier translator integration entry:

- `beb14be` — safe source materialization and the `oks_dump` subprocess adapter.
- `19c9ca4` — opt-in CLI historical execution with repeatable data paths and runtime options.
- `fbd85d0` — historical few-shot loading with no current-tree fallback.
- `63182cb` — auditable revision provenance on successful historical translations.

Final verification for this continuation: focused historical tests passed 40/40 with 2 optional skips; the full suite passed 63 tests with 2 optional skips. The skips are due to missing local `rank_bm25`. `oks_dump` is not installed locally, so native execution remains covered by mocked subprocess tests and reports a clear error until the OKS runtime is available.

The working tree is clean and the branch is synchronized with `origin/feat/eval-dataset-and-rag-v2`.

## Historical schema preflight validation — 2026-08-23

### Scope

Added a conservative validation gate immediately before native historical execution. It prevents a translated query from invoking `oks_dump` with a target class that does not exist in the selected revision.

### Implementation

- Added `translator_module/execution/schema_preflight.py` with `HistoricalSchemaPreflight`, `SchemaPreflightResult`, and `SchemaPreflightError`.
- The validator loads the snapshot's schema paths through `SchemaLoader` and checks exact target-class presence.
- It intentionally does not validate direct attribute or relationship membership. OKS inheritance can supply those members, and the native runtime remains responsible for complete schema semantics.
- The CLI runs preflight only in `--execute` mode and reports failures as historical execution errors.

### Verification

- Added tests for an existing target class, a missing target class, and a class whose inherited members are not declared directly.
- `python -m py_compile translator_module/execution/schema_preflight.py translator_module/execution/__init__.py translator_module/cli.py translator_module/tests/test_historical_query.py` passed.
- Focused historical suite: 43 tests passed, 2 dependency-based tests skipped.
- Full suite: 66 tests passed, 2 dependency-based tests skipped.

## CLI execution handoff testability — 2026-08-23

Extracted `_execute_historical_result(args, result, snapshot)` from the interactive loop. The helper now owns target-class selection, schema preflight, immutable execution-context construction, and `OksDumpExecutor` invocation.

Added CLI tests proving that the helper passes the selected snapshot and serialized query to the executor, and that a missing historical target class is rejected before the native executor is called.

Verification after this slice: CLI tests passed 10/10; the full suite passed 68 tests with 2 optional `rank_bm25` skips. No native OKS binary is required for these tests.
