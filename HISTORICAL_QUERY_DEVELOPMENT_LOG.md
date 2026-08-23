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
