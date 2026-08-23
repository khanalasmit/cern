# Historical Query Feature: Vibe Coding Guide

This document is a step-by-step implementation guide for adding historical OKS configuration queries to this repository.

It is written so that another developer can give each small step to an AI coding assistant, review the result, run the tests, and then continue to the next step.

The implementation should remain incremental. Each vibe should make one focused change, preserve existing behavior, and finish with a test or verification command.

---

## 1. Feature Overview

The feature will allow a user to ask the OKS Intelligent Query Agent about the configuration as it existed in a past run or at a past point in Git history.

Example requests:

```text
Query run 48192: find applications whose Timeout is greater than 50
```

```bash
python -m translator_module.cli --commit-hash 5751a75
```

```bash
python -m translator_module.cli --date 2026-08-01T12:00:00+05:45
```

The important design rule is:

> Resolve one immutable Git revision, read both schema and configuration files from that revision, and use that same snapshot for retrieval, validation, serialization, and execution.

The implementation must not run `git checkout` in the user’s working tree. Historical files should be read with `git show <commit>:<path>` or materialized into a temporary directory with `git archive` when an external OKS loader requires real filesystem paths.

### Current repository behavior

Before changing code, understand these facts about the current implementation:

- [`translator_module/cli.py`](translator_module/cli.py) hard-codes `oks_scraped/oks_schema_examples.xml` and `oks_scraped/gold_pairs.jsonl`.
- [`translator_module/agent/translator.py`](translator_module/agent/translator.py) constructs the RAG index in `OksTranslator.__init__()`.
- [`translator_module/rag/ingest.py`](translator_module/rag/ingest.py) uses `xml.etree.ElementTree` and currently expects the scraped wrapper format containing `<example>` and `<schema-file>` elements.
- [`translator_module/rag/retrieve.py`](translator_module/rag/retrieve.py) only retrieves schema chunks; it does not load configuration data.
- [`translator_module/agent/ir_validator.py`](translator_module/agent/ir_validator.py) validates the IR shape, but does not yet verify that names and values exist in the selected schema.
- [`translator_module/agent/serializer.py`](translator_module/agent/serializer.py) only converts a validated IR object to an `OksQuery` string. It does not read files or execute queries.
- The current `QueryIR` has no `target_class`, which will likely be needed for actual query execution.

The feature therefore has two related parts:

1. Historical schema-aware translation.
2. Historical configuration loading and query execution.

The first part can be implemented without an OKS runtime. The second part requires an execution adapter around the project’s eventual OKS API or command-line tool.

---

### Implemented status

The repository now contains the initial implementation described by this
guide. The working CLI supports `--commit-hash`, `--tag`, `--date`, and
`--run-id`; historical schema and few-shot files are read from a Git-backed
source without checkout. Add `--execute` to build a same-revision schema/data
snapshot, run target-class preflight, and invoke the native `oks_dump`
adapter. Use `--data-path` repeatedly for explicit data files, or let the
snapshot discover `test_data/**/*.data.xml`.

The native executable is intentionally optional during development. Its
adapter returns raw output because the repository does not establish a stable
machine-readable output contract for every OKS deployment. See
[`HISTORICAL_QUERY_DEVELOPMENT_LOG.md`](HISTORICAL_QUERY_DEVELOPMENT_LOG.md)
for the implementation history and current verification results.

---

## 2. Prerequisites

### Runtime prerequisites

- Python 3.10 or newer.
- Git installed and available as `git` on `PATH`.
- A local clone containing the historical commits.
- The existing dependencies in [`translator_module/requirements.txt`](translator_module/requirements.txt).
- A configured OpenAI-compatible LLM endpoint for end-to-end translation tests.

### Git access implementation choice

The recommended first implementation uses Python’s standard-library `subprocess` module:

```text
Advantages: no new dependency, direct access to git show/git archive, easy to isolate.
```

GitPython is also acceptable if the team prefers an object-oriented Git API. If GitPython is selected, add this dependency:

```text
GitPython>=3.1.40
```

Do not implement both GitPython and subprocess paths in the first version. Select one abstraction and keep the rest of the application independent of that choice.

### Development commands

From the repository root:

```bash
python -m unittest discover -s translator_module/tests -v
```

After dependency changes:

```bash
pip install -r translator_module/requirements.txt
```

Before every vibe, check the baseline:

```bash
git status --short
python -m unittest discover -s translator_module/tests -v
```

---

## 3. Step-by-Step Implementation Plan

Each step below is intentionally small. Give only one AI prompt to the coding assistant at a time. Review the diff and run the stated verification before moving on.

### Vibe 0 — Establish a safe baseline

#### The Goal

Record the current behavior and protect the existing translator before adding revision support.

#### The Files to Create/Modify

- Create or modify: `translator_module/tests/test_historical_query.py`
- Do not modify production code in this step.

#### The AI Prompt

```text
You are working in the repository root. Add a new test file at
translator_module/tests/test_historical_query.py.

Do not change production code. Add a small smoke test that verifies
serialize_ir_to_oks still serializes a valid QueryIR using the existing
models. Follow the unittest style already used in
translator_module/tests/test_translator.py.

Keep the test independent of a live LLM, FAISS, or network access. Show the
diff and explain how to run only this test.
```

#### Verification

```bash
python -m unittest translator_module.tests.test_historical_query -v
```

---

### Vibe 1 — Add revision request and provenance models

#### The Goal

Create typed objects for user input and resolved revision metadata. This gives every later component a stable contract.

#### The Files to Create/Modify

- Create: `translator_module/revision/__init__.py`
- Create: `translator_module/revision/models.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Create translator_module/revision/__init__.py and
translator_module/revision/models.py.

Define dataclasses for:

1. RevisionRequest: optional commit_hash, tag, date, run_id, and ref.
2. ResolvedRevision: repository path, full commit SHA, requested_as,
   optional commit date, optional run_id, and ref.
3. OksSnapshot: a ResolvedRevision plus schema_paths and data_paths.

Use Python 3.10-compatible type hints. Make the resolved objects immutable
with frozen dataclasses. Do not add Git logic yet.

Add unit tests for construction, equality, and immutability. Do not require
network access, an LLM, or a real Git repository.
```

#### Design rule

Always store the full commit SHA in `ResolvedRevision`, even when the user enters a short hash or tag.

---

### Vibe 2 — Implement a filesystem-source abstraction

#### The Goal

Allow the RAG and data layers to read from either the current working tree or a historical Git snapshot without knowing the difference.

#### The Files to Create/Modify

- Create: `translator_module/revision/source.py`
- Modify: `translator_module/revision/__init__.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Create translator_module/revision/source.py with a small FileSource
abstraction.

Define a protocol or base class with:

- read_bytes(relative_path) -> bytes
- exists(relative_path) -> bool
- list_files(pattern) -> list[str]
- open_binary(relative_path) -> BinaryIO

Implement WorkingTreeSource rooted at a repository directory. It must
reject absolute paths and paths containing .. so callers cannot escape the
repository root.

Do not implement Git access yet. Add tests using a temporary directory to
verify reading bytes, checking existence, listing files, and rejecting unsafe
paths.
```

---

### Vibe 3 — Implement Git blob access without checkout

#### The Goal

Read exact historical file contents using `git show` while leaving the current checkout untouched.

#### The Files to Create/Modify

- Create: `translator_module/revision/git_source.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Create translator_module/revision/git_source.py.

Implement GitRevisionSource(FileSource) using subprocess.run with
shell=False. It must:

- Accept a repository path and a full commit SHA.
- Implement read_bytes(relative_path) by calling:
  git -C <repo> show --format= <commit>:<relative_path>
- Implement exists(relative_path) using git cat-file or git ls-tree.
- Implement list_files(pattern) using git ls-tree -r --name-only.
- Provide open_binary() using io.BytesIO.
- Convert missing files and Git failures into clear custom exceptions.
- Never call git checkout, git reset, or any command that changes the
  working tree.
- Never use shell=True.

Validate repository-relative paths and reject absolute paths and .. path
components. Add tests that create a temporary Git repository with two
commits, change a file between commits, and verify that each source returns
the correct historical bytes. Also verify that the original working-tree
branch and files are unchanged.
```

#### Important implementation detail

Use the full SHA after resolution. Cache keys should use `(repository, full_sha, path)` rather than a user-entered short hash.

---

### Vibe 4 — Add commit, tag, and date resolution

#### The Goal

Convert a `RevisionRequest` into a deterministic `ResolvedRevision`.

#### The Files to Create/Modify

- Create: `translator_module/revision/resolver.py`
- Modify: `translator_module/revision/__init__.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Create translator_module/revision/resolver.py with GitRevisionResolver.

The resolver must accept RevisionRequest and support:

- commit_hash: verify and resolve it to a full commit SHA.
- tag: resolve the tag to a commit.
- date: select the newest commit on request.ref at or before the requested
  timestamp using Git history.
- current/no selector: resolve HEAD, or return a clearly documented current
  working-tree mode if that is the chosen design.

Reject requests containing more than one selector. Do not silently fall back
to the current revision when a requested selector cannot be resolved.

Use subprocess with shell=False. Include the repository, full SHA, ref,
selection method, and commit date in ResolvedRevision. Add unit tests using a
temporary repository with at least two commits and controlled commit dates.
```

#### Date semantics

Document timezone handling. ISO 8601 timestamps with offsets should be preferred. A date without a timezone should be interpreted using the CLI’s documented default timezone.

---

### Vibe 5 — Add run-ID mapping

#### The Goal

Resolve a domain run number through an explicit run-to-commit registry rather than guessing from Git messages.

#### The Files to Create/Modify

- Create: `translator_module/revision/run_registry.py`
- Create: `run_revisions.example.yaml`
- Modify: `translator_module/revision/resolver.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Implement an explicit run-ID registry in
translator_module/revision/run_registry.py.

Support a small YAML or JSON mapping from run IDs to commit hashes and
optional timestamps. Add a loader that validates the mapping and rejects
duplicate or malformed entries.

Update GitRevisionResolver so RevisionRequest.run_id uses this registry.
If a run ID is missing, raise a clear error; do not infer a commit from a
commit message or from an approximate timestamp.

Add run_revisions.example.yaml with fake values only. Add tests for valid
lookup, missing run IDs, malformed files, and provenance in ResolvedRevision.
```

This implementation selects JSON to avoid adding another dependency. The example registry is `run_revisions.example.json`. If the team later selects YAML, add `PyYAML` to `translator_module/requirements.txt` and preserve the same validation contract.

---

### Vibe 6 — Add historical snapshot discovery

#### The Goal

Discover the schema and data files that exist in the selected revision.

#### The Files to Create/Modify

- Create: `translator_module/revision/snapshot.py`
- Modify: `translator_module/revision/models.py`
- Modify: `translator_module/revision/tests` or `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Create translator_module/revision/snapshot.py.

Implement snapshot discovery for a resolved Git revision. Use the historical
tree, not the current filesystem, to find files. Identify schema files using
the configured schema patterns and data files using configured data patterns.

Return an OksSnapshot containing the resolved revision and repository-relative
schema_paths/data_paths.

Distinguish required files from optional files. Raise a clear error when no
schema files are found. Do not assume that paths present in the current
working tree existed in the historical commit.

Add tests with two temporary Git commits where files are added, removed, and
renamed between revisions.
```

Keep the path patterns configurable. The current scraped wrapper file and the standalone files under `test_schema/` should be treated as different input formats.

---

### Vibe 7 — Refactor schema loading to accept sources

#### The Goal

Make RAG ingestion work with bytes or a `FileSource`, not only current filesystem paths.

#### The Files to Create/Modify

- Modify: `translator_module/rag/ingest.py`
- Create: `translator_module/rag/schema_loader.py`
- Modify: `translator_module/tests/test_eval_dataset.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Refactor the schema ingestion path so it can read from a FileSource.

Preserve the existing HybridIndexer.ingest_xml(path) API for backward
compatibility, but add a source-based method such as ingest_source(source,
paths).

Create translator_module/rag/schema_loader.py with loaders for:

1. The existing oks_scraped/oks_schema_examples.xml wrapper format, where
   schema XML is embedded inside schema-file elements.
2. Standalone OKS schema XML files such as test_schema/**/*.schema.xml.

Normalize both formats into the existing SchemaChunk representation without
changing retrieval behavior yet.

Use ElementTree with BytesIO/fromstring. Preserve source_path and revision in
chunk metadata when available. Do not silently swallow malformed historical
XML; raise an error containing the source path and parser location.

Update tests so the existing eval_dataset corpus still parses exactly as
before, and add a test for a standalone schema file from a FileSource.
```

Do not attempt to solve inheritance or relationship expansion in this vibe. Keep the change focused on source injection.

---

### Vibe 8 — Inject the snapshot into `OksTranslator`

#### The Goal

Make translation use the selected historical schema while preserving the current constructor behavior where possible.

#### The Files to Create/Modify

- Modify: `translator_module/agent/translator.py`
- Modify: `translator_module/agent/few_shot.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Update OksTranslator so it can receive an OksSnapshot or FileSource.

Preserve compatibility with the existing path-based constructor if practical,
but make the new source-based path the preferred API.

When a snapshot is supplied:

- Build the HybridIndexer from snapshot schema files.
- Keep the LLM client behavior unchanged.
- Keep few-shot examples separate from historical schema unless an explicit
  historical examples source is supplied.
- Include the resolved full commit SHA in translator state and result
  provenance.

Do not rebuild the index for every query. The index must be tied to one
revision context. Add tests with a fake FileSource or temporary Git repository
that prove two revisions create different schema contexts.
```

If a CLI session needs multiple revisions, cache translators or RAG contexts by `(repository, full_commit_sha)`.

---

### Vibe 9 — Add revision-aware prompt context

#### The Goal

Prevent the LLM from confusing current schema identifiers with identifiers from the historical revision.

#### The Files to Create/Modify

- Modify: `translator_module/agent/translator.py`
- Create: `translator_module/agent/prompt_profile.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Add a small prompt-profile layer for historical translation.

When a revision context is present, add a clearly labeled provenance block to
the system prompt containing the full commit SHA and selected source files.

Tell the model that all identifiers must come from the supplied historical
schema context and that it must not use current-working-tree identifiers.

Keep the existing IR schema prompt unchanged unless a capability profile
explicitly says a historical schema cannot support a feature. Add tests that
inspect the generated prompt or prompt-builder output and verify that the
historical commit is included.
```

The commit hash is provenance, not a replacement for schema context. The LLM still needs the actual retrieved schema chunks.

---

### Vibe 10 — Add CLI flags and revision selection

#### The Goal

Let users select a historical revision before the translator is initialized.

#### The Files to Create/Modify

- Modify: `translator_module/cli.py`
- Modify: `translator_module/revision/resolver.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Refactor translator_module/cli.py to use argparse while preserving the
existing interactive query loop.

Add mutually exclusive options:

- --commit-hash
- --tag
- --date
- --run-id

Also add --repo, --ref, and --run-map options. Resolve the requested revision
before constructing OksTranslator. If no selector is supplied, preserve the
current default behavior.

Do not call git checkout, reset, pull, or fetch. Print the selected full
commit SHA and source mode at startup. Add CLI parsing tests without starting
an LLM or network connection.
```

The CLI should fail early with a useful message if a requested revision cannot be resolved.

---

### Vibe 11 — Add schema-aware historical validation

#### The Goal

Ensure that the generated IR is valid for the selected historical schema, not merely structurally valid JSON.

#### The Files to Create/Modify

- Create: `translator_module/agent/schema_validator.py`
- Modify: `translator_module/agent/translator.py`
- Modify: `translator_module/agent/ir_validator.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Create a schema-aware validation layer that runs after Pydantic QueryIR
validation and before serialization.

It must verify, using the selected revision’s SchemaCatalog:

- target class, once target_class is present;
- attribute names;
- relationship names;
- relationship target classes for nested expressions;
- valid enum values where available;
- basic cardinality and type constraints where available.

Return clear validation errors that identify the historical revision and the
invalid identifier. Do not silently replace invalid historical identifiers
with current identifiers.

Keep the existing structural validate_ir function usable independently.
Add tests for a valid old-schema query and for attributes or enum values that
exist only in a newer schema.
```

This is where the historical schema becomes an enforcement boundary rather than merely prompt text.

---

### Vibe 12 — Add `target_class` to the IR

#### The Goal

Give the eventual executor enough information to know which OKS class should receive the query.

#### The Files to Create/Modify

- Modify: `translator_module/agent/ir_validator.py`
- Modify: `translator_module/agent/serializer.py` only if needed; normally no change is required.
- Modify: `translator_module/agent/translator.py`
- Modify: `translator_module/tests/test_translator.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Add an optional or required target_class field to QueryIR, using the least
disruptive migration strategy supported by the existing tests.

Update the embedded IR schema prompt so the LLM returns target_class.
Preserve the serialized OksQuery string format; target_class is execution
metadata and should not be inserted into the serialized expression unless the
existing OKS syntax requires it.

Update existing tests and add tests proving that target_class survives
validation and is returned in translator results.
```

Whether `target_class` is optional during migration or required immediately should be decided by the team. It must be required before execution can be considered reliable.

---

### Vibe 13 — Add temporary historical materialization

#### The Goal

Support OKS loaders or executors that require a real directory containing schema and data files.

#### The Files to Create/Modify

- Modify: `translator_module/revision/git_source.py`
- Create: `translator_module/revision/materialize.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Implement a context-manager API that materializes a Git revision into a
TemporaryDirectory without changing the current working tree.

Use git archive for the resolved commit, extract it safely, and return the
temporary root path. Ensure path traversal cannot escape the temporary
directory. Clean up automatically on success and exceptions.

Add tests that verify historical files are present, current working-tree files
are unchanged, and the temporary directory is removed after the context exits.
```

Use byte-based `git show` for parsing a small number of files. Use temporary materialization when includes, data-file relationships, or native OKS APIs require a directory.

---

### Vibe 14 — Add historical data loading and execution boundary

#### The Goal

Create the component that will eventually execute the serialized query against the historical configuration.

#### The Files to Create/Modify

- Create: `translator_module/execution/__init__.py`
- Create: `translator_module/execution/historical_executor.py`
- Create: `translator_module/execution/data_loader.py`
- Modify: `translator_module/agent/translator.py` only to expose the serialized query and snapshot.
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Create an execution boundary for historical OKS queries.

Do not invent an OKS runtime. Define interfaces for:

- loading schema and data files from an OksSnapshot;
- executing a serialized OksQuery against a target class;
- returning normalized results plus revision provenance.

Implement a deterministic fake executor for tests. It should accept a small
fixture data set, prove that the selected revision’s data is used, and make no
network calls. Leave a clear TODO or adapter interface for the real OKS API or
oks_dump integration.

The executor must never silently combine schema from one revision with data
from another revision.
```

This vibe creates a safe seam for the runtime integration without pretending that the current repository already contains a complete OKS execution engine.

---

### Vibe 15 — Add provenance and user-facing errors

#### The Goal

Make historical results auditable and failures understandable.

#### The Files to Create/Modify

- Modify: `translator_module/agent/translator.py`
- Modify: `translator_module/cli.py`
- Modify: `translator_module/revision/models.py`
- Create: `translator_module/revision/errors.py`
- Modify: `translator_module/tests/test_historical_query.py`

#### The AI Prompt

```text
Add typed revision-related exceptions and consistent provenance reporting.

Errors should distinguish:

- repository not found;
- commit/tag/date/run ID not resolvable;
- historical file missing;
- malformed XML;
- incompatible schema;
- query execution failure.

Every successful historical result must include repository, full commit SHA,
selection method, optional run ID, and schema/data paths. The CLI should show
the selected revision before accepting queries.

Add tests for each error category and verify that no error causes an implicit
fallback to the current revision.
```

---

## 4. Testing Strategy

Testing should not depend entirely on the live LLM or the real project Git history. Use small temporary Git repositories to make each historical behavior deterministic.

### A. Unit-test the Git layer with mock commits

Create a temporary repository in a test:

```text
commit A:
  schema.xml: Timeout enum = 10, 20
  config.data.xml: AppA timeout = 10

commit B:
  schema.xml: Timeout enum = 10, 20, 50
  config.data.xml: AppA timeout = 50
```

Verify:

- Commit A reads only the older bytes.
- Commit B reads only the newer bytes.
- The current branch is not moved.
- The current working-tree files are not modified.
- Missing files produce typed errors.
- A short hash and full hash resolve to the same commit.
- Date resolution selects the expected commit.

### B. Test snapshot consistency

Add a test that attempts to load a schema from commit A and data from commit B. The snapshot or executor should reject this unless the mismatch is explicitly allowed.

### C. Reuse `eval_dataset/`

The existing evaluation tests are useful for regression protection:

- `eval_dataset/oks_schema_corpus.xml` should still be consumable by the RAG loader.
- `eval_dataset/oks_eval_queries.jsonl` should still validate and serialize.
- Existing serializer tests should remain unchanged wherever possible.

Add historical copies of the evaluation corpus to temporary Git commits and verify that the same question produces revision-specific schema context.

### D. Avoid LLMs in most tests

Mock the OpenAI client or test these layers independently:

```text
Git resolver       → exact commit
Git source         → exact file bytes
Schema loader      → canonical schema
RAG indexer        → chunks from selected revision
IR validator       → historical identifiers accepted/rejected
Serializer         → deterministic OksQuery
Executor           → selected historical data
```

Only one small integration test needs to exercise the complete translator pipeline, and it should use a mocked LLM response.

### E. Required regression commands

```bash
python -m unittest discover -s translator_module/tests -v
```

If the project later adopts pytest, keep the existing unittest tests runnable until the migration is deliberate.

---

## 5. Known Limitations and RAG Context

Read [`rag.md`](rag.md) before changing the retrieval layer. The historical feature must not hide or amplify the existing retrieval limitations.

### Inherited attributes are currently incomplete

The current indexer chunks each class using direct children. Inherited attributes may be absent from a historical schema chunk even though they are valid for the class.

Historical querying should eventually resolve the full superclass chain and include inherited members in the retrieved schema context.

### Metadata constraints are currently dropped

Current chunks often include only:

```text
Attribute: Timeout (type: int)
```

They may omit:

- Enum values.
- Numeric ranges.
- Initial values.
- Required or nullable status.
- Multi-value/cardinality constraints.

Do not assume that an attribute name alone is enough to validate a historical query.

### Relationship targets are not fully followed

Relationship chunks currently include the target class name, but the retriever does not necessarily include the target class’s attributes. Nested historical queries may therefore be generated with the wrong attribute scope.

The long-term solution is graph expansion:

```text
candidate class
  → superclass chain
  → declaring class of each attribute
  → relationship target class
  → target class attributes
```

### Retrieval is hybrid but shallow

The current system combines BM25 and FAISS retrieval, but the default `top_k` is small. Increasing historical correctness should not be attempted by changing only the Git source. A historical snapshot still needs sufficient recall and a closed schema slice.

### Few-shot examples may be incompatible

Current `gold_pairs.jsonl` may contain identifiers or syntax that did not exist in older revisions. Filter examples against the selected historical schema or use revision-tagged examples.

### The current validator is structural

Pydantic confirms that the JSON has the expected shape. It does not fully prove that a name, enum, relationship, or value is valid for the selected historical schema. Add schema-aware validation before execution.

### The serializer is not the execution engine

`serialize_ir_to_oks()` produces text. It does not select a class, load data, or execute a query. Do not put Git logic into `serializer.py`.

### Schema and data must be revision-consistent

Never use:

```text
historical schema + current data
```

or:

```text
current schema + historical data
```

The resolver should produce one snapshot that owns both sets of files.

### The project repository may not be the configuration repository

Confirm where production OKS schemas and run data actually live. The Git history of this project repository may contain only examples and test data. If the run configuration lives in another repository, make the repository path explicit through `--repo` or configuration.

---

## 6. Definition of Done

The feature is ready for review when:

- A user can select a commit, tag, date, or mapped run ID.
- The resolver records the full commit SHA.
- Historical files are read without changing the active checkout.
- Schema and data paths come from the same revision.
- Existing current-working-tree behavior still works.
- The RAG loader can consume the selected historical schema format.
- The translator receives historical schema context.
- Validation rejects identifiers unavailable in that historical schema.
- Serialization remains deterministic and revision-independent.
- Historical execution has a clear adapter boundary.
- Results include revision provenance.
- Missing files and incompatible schemas produce explicit errors.
- Existing tests and the evaluation dataset continue to pass.

The final implementation should make the revision visible at every boundary, but should keep Git-specific code confined to the revision/source modules.
