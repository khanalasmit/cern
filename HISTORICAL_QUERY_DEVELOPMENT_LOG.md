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
