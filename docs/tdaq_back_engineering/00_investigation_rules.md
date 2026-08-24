# 00 — Investigation Rules (new release: `tdaq-13-00-00`)

**Scope of this document set:** a fresh, evidence-based investigation of the ATLAS/TDAQ
release identified in this repository as `tdaq-13-00-00` (with `tdaq-common-13-00-00`),
for the Text-to-OksQuery MCP project.

**Status of the previous investigation:** the documents under
`docs/investigation/tdaq-09-03-00/` were produced against an older release
(`tdaq-09-03-00` / `tdaq-common-04-03-00`). They are **not evidence** for
`tdaq-13-00-00` and must not be used to fill gaps in this document set.
A comparison may be performed later, in a separate document
(`docs/investigation/comparison/old_vs_new.md`), only after this investigation is complete.

---

## 1. Authoritative sources for this investigation

Only these paths are evidence for the new release:

| Path | What it is |
|---|---|
| `Materials/tdaq-cmake-tdaq-13-00-00/` | Source archive of the `tdaq-cmake` superproject at ref `tdaq-13-00-00` |
| `Materials/tdaq-common-cmake-13-00-00/` | Source archive of the `tdaq-common-cmake` superproject at ref `tdaq-common-13-00-00` |

Anything under `Materials/tdaq-09-03-00/`, `Materials/tdaq-common-04-03-00/`, or
`docs/investigation/tdaq-09-03-00/` is **out of scope** as evidence.

External knowledge about ATLAS/TDAQ (from documentation on the web, prior experience,
or the `Materials/GPT conversation.txt` file) is **not repository evidence** and must never
be presented as such. Where it is used at all, it must be explicitly labelled as an
assumption or as a question for TDAQ experts.

## 2. Investigate before claiming

Search source, headers, implementations, build files, documentation, scripts,
configuration, tests, examples and comments. Trace callers and callees where practical.
Cite a **file and symbol**, not a directory, whenever possible.

A name, a file's presence, or an include relationship is **not** proof that a component is:

- used,
- externally supported,
- the recommended interface,
- authoritative, or
- part of the production workflow.

Each of those relationships requires its own evidence.

**A submodule declaration is weaker still.** In this release the two source trees are
git superprojects whose package contents are not present (see `01_release_inventory.md`).
A line in `.gitmodules` proves only that *a repository of that name is declared as part of
the superproject*. It proves nothing about that package's contents, API, behaviour, or
version.

## 3. Confidence levels

Every finding is classified as exactly one of:

- **Confirmed** — directly demonstrated by code or documentation in the new-release trees.
- **Strongly indicated** — supported by several new-release repository facts, but not directly stated.
- **Partially established** — some behaviour is evidenced, but an important part is missing.
- **Not established from the new-release repository** — insufficient evidence was found.

## 4. Evidence requirements

Every important claim states:

1. repository-relative path,
2. file name,
3. class / function / symbol, where applicable,
4. line number or approximate line range, where possible,
5. a short explanation of **what the evidence actually proves** (and, where useful, what it does not).

## 5. No assumptions

When the new-release trees do not contain enough information to establish something,
write exactly:

> Not established from the new-release repository.

Then state what was searched and what is missing. Do not replace an unknown with a guess,
with a conclusion from the old investigation, or with general ATLAS/TDAQ knowledge.
Preserve ambiguity; a document that looks complete but is partly invented is worse than
one that is openly incomplete.

## 6. Per-question document structure

Whenever a prompt asks for numbered answers (A1–A6, B1–B8, C1–C4, D1–D4, E1–E6,
F1–F4, G1–G5, H1–H5, I1–I4, J1–J6), use this structure:

1. **Question**
2. **Repository finding**
3. **Evidence**
4. **Execution / data flow**
5. **Confidence**
6. **Missing information**
7. **Implication for the MCP prototype**

Include an MCP implication only when it logically follows from new-release evidence.
Label engineering proposals and expert-meeting questions clearly; never present them as
repository facts.

## 7. Working rules

- Write each document as investigation progresses; do not wait for every answer.
- Do **not** modify production source code under `Materials/`.
- Distinguish, in every recommendation, between:
  - *technically possible*,
  - *demonstrated as an existing interface*, and
  - *officially supported*.
  The repository may establish the first two and still say nothing about the third.

## 8. Canonical technical questions

These identifiers have a fixed meaning across all documents in this set.

### A — OKS architecture
- **A1** Complete real-world historical configuration access workflow, from shifter request / run identification to loading, querying, and presenting a result.
- **A2** Relationship and responsibilities of DAL, `config::Configuration`, `oksconfig`, `OksKernel`, `OksQuery`, and WebDAQ.
- **A3** Whether DAL or `config::Configuration` internally uses `OksQuery`, and the value of direct OksQuery generation.
- **A4** Whether `config::Configuration` understands OKS schema or is primarily a generic configuration interface.
- **A5** Whether WebDAQ is an HTTP/JSON OKS interface, and the mechanism it uses internally.
- **A6** Recommended and officially supported Python MCP integration interface, if the repository establishes one.

### B — Historical configuration and runs
- **B1** How a run number maps to an exact OKS configuration and Git commit/tag/revision.
- **B2** Whether an OKS database contains one configuration, multiple configurations/runs, or another structure, and how these are distinguished.
- **B3** Whether schema/data XML are stored in Git, and whether the Git revision is authoritative for a historical configuration.
- **B4** The supported mechanism for accessing a historical configuration.
- **B5** The actual schema/data loading workflow into `OksKernel` and subsequent query execution.
- **B6** Whether historical configurations are read-only in practice, and how modification/versioning occurs.
- **B7** Whether multiple configurations can coexist in one loaded database.
- **B8** What prevents accidental modification of historical configurations.

### C — OksQuery and mutation
- **C1** OksQuery capabilities, including whether it can mutate objects.
- **C2** APIs or mechanisms that create, modify, and delete OKS objects.
- **C3** Architectural separation, if any, between querying and modifying a configuration.
- **C4** Whether a first MCP prototype should be read/query-only, based on evidence.

### D — Modification tooling
- **D1** Existing GUI, CLI, API, or other tools for creating/modifying configurations.
- **D2** How a modification becomes a Git revision, if established.
- **D3** The existing API/tool a future natural-language modification system should call, if established.
- **D4** Validation performed before a changed configuration is accepted or used for a run.

### E — Integration boundary
- **E1** Whether an existing WebDAQ interface covers historical access and read-only querying.
- **E2** Repository-evidenced advantages and limits of WebDAQ versus native C++.
- **E3** Existing supported Python bindings and exposed APIs.
- **E4** Evidence for a new thin binding versus WebDAQ, without assuming either is recommended.
- **E5** Existing C++ executables/services that accept OksQuery and return results.
- **E6** Best first-prototype path based on release evidence.

### F — Git and configuration repositories
- **F1** Git hosting provider evidenced for configuration repositories.
- **F2** Whether the configuration system uses provider APIs, ordinary Git, a Git library, or another mechanism.
- **F3** Whether a provider abstraction exists or is justified by repository evidence.
- **F4** Git operations required for historical configuration access.

### G — OKS schema
- **G1** Authoritative OKS schema location and relationship between schema and data XML.
- **G2** Whether the schema provides the information needed for OksQuery generation.
- **G3** Existing OKS schema-inspection API versus manual XML parsing.
- **G4** Evidence-backed schema source for retrieval.
- **G5** Existing structured, machine-readable schema representation to reuse.

### H — Schema retrieval for the LLM
- **H1** Supplying relevant schema information to an LLM.
- **H2** Exact/keyword, semantic/vector, or hybrid retrieval as an engineering choice, not a repository fact unless documented.
- **H3** Schema representation needed by the LLM.
- **H4** Relationship representation needed for semantically valid queries.
- **H5** Schema consistency across revisions, and whether the matching historical revision must be used.

### I — NL → OksQuery pipeline
- **I1** Suitability of the proposed NL-to-OksQuery pipeline.
- **I2** Existing TDAQ components versus components this MCP project must implement.
- **I3** Whether the LLM should generate only OksQuery, or also select configuration/revision.
- **I4** Existing reusable query-validation mechanism, and where validation should occur.

### J — Prototype scope
- **J1** Minimum useful six-week prototype scope.
- **J2** Evidence-backed read-only boundary and deferred mutation scope.
- **J3** Safest maintainable MCP integration boundary.
- **J4** Existing components to reuse.
- **J5** Security, operational, deployment, and historical-data constraints.
- **J6** Recommended initial architecture and explicitly excluded work.

## 9. Planned documents

| Document | Subject |
|---|---|
| `00_investigation_rules.md` | This document |
| `01_release_inventory.md` | Release identification and inventory |
| `02_oks_architecture.md` | A1–A6 |
| `03_historical_configuration.md` | B1–B8 |
| `04_oksquery_read_write.md` | C1–C4, D1–D4 |
| `05_python_integration.md` | E1–E6 |
| `06_git_configuration_access.md` | F1–F4 |
| `07_oks_schema.md` | G1–G5 |
| `08_schema_retrieval.md` | H1–H5 |
| `09_nl_to_oksquery.md` | I1–I4 |
| `10_prototype_architecture.md` | J1–J6 |
| `11_technical_questions_matrix.md` | Full A–J evidence matrix |

> **Blocking note.** As established in `01_release_inventory.md`, the new-release material
> currently in this repository contains **no package source code**. Documents 02–11 cannot be
> completed against `tdaq-13-00-00` until the submodule contents are obtained. See
> `01_release_inventory.md` §7 for exactly what is missing.

---

## Addendum — source availability (supersedes earlier status)

When this document set was started, both new-release trees contained only the
superproject scaffolding: the ~200 package directories declared in `.gitmodules` were
empty, so document `01` originally concluded that no package source was available.

That is no longer the case. The submodule revisions **are** recorded — not in
`.gitmodules` (which stores only `path` and `url`), but as gitlinks in this repository's
own index, and they have since been checked out from `https://gitlab.cern.ch/atlas-tdaq-software/`
at exactly those pinned commits:

- `Materials/tdaq-cmake-tdaq-13-00-00/` — 202 of 203 packages checked out
- `Materials/tdaq-common-cmake-13-00-00/` — 18 of 18 packages checked out

**Therefore documents `02`–`11` are written against real package source at the exact
pinned revisions of `tdaq-13-00-00`.** A pinned SHA is quoted for every package cited.

One package could not be obtained and is a standing gap:

| Package | Pinned SHA | Status |
|---|---|---|
| `felix-interface` | `git ls-files -s` in this repo | `HTTP Basic: Access denied` — repository is not anonymously readable |

Any claim that would depend on `felix-interface` must be recorded as
**Not established from the new-release repository.**
