# 10 — Six-Week Prototype Architecture (new release: `tdaq-13-00-00`)

Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Based on documents `01`–`09`, with conclusions re-verified against source.
Paths relative to `Materials/tdaq-cmake-tdaq-13-00-00/`.

---

## 1. Executive recommendation

**Build a read-only Python MCP server on top of the existing `config` Python binding, with
`oksconfig` as the backend and the revision passed in the connection string
(`oksconfig:<config>&version=tag:r<run>@<partition>`) as the historical lever.**

The investigation found the release to be substantially *more* accommodating than the
project's framing assumed:

- Query execution from Python **already exists** with a query-string parameter
  (`config/python/config/Configuration.py:117`).
- Historical checkout **already exists** and is driven either by a **connection-string
  parameter** — `oksconfig/src/OksConfiguration.cpp:150, :191–202` — or by the
  `TDAQ_DB_VERSION` environment variable (`oks/src/kernel.cpp:930–958`). The
  connection-string form is per-`Configuration` and therefore concurrency-safe.
- Query validation **already exists**, is schema-aware and exact, and is the same code that
  executes the query (`oks/src/query.cpp:341–420`).
- The run→revision mapping **is already recorded** at run start, twice — as a database column
  and as a derivable Git tag `r<run>@<partition>` (`rn/src/lib.cpp:104, :255`).

Against that, two findings narrow the design:

- **The HTTP path cannot work.** `webdaq`/`webis_server` expose OKS without a query parameter
  and without a revision parameter (`webis_server/src/oks_handler.cpp:284`, URL grammar
  `:15–29`).
- **Nothing reads the run→revision mapping back.** The MCP must implement that lookup
  (document `03` §4).

The prototype's genuinely new code is therefore small: run resolution, schema rendering,
query generation, serialization, and the MCP surface. Everything below that is reuse.

## 2. Repository-confirmed architecture (what exists)

```
Python  config.Configuration("oksconfig:<file>")        config/python/config/Configuration.py:52
   │        get_objs(class, query) · classes() · attributes() · relations() · subclasses()
   ▼
Boost.Python  pyconfig                                  config/src/python/config.cpp:161-170
   ▼
config::Configuration::get(class, objects, query)       config/config/Configuration.h:698
   │   dlopen("liboksconfig.so"), _oksconfig_creator_    config/src/Configuration.cpp:127-147
   ▼
OksConfiguration::get(...)                              oksconfig/src/OksConfiguration.cpp:693
   ├─ new OksQuery(cl, query)  → schema validation      :705   (oks/src/query.cpp:341,363,379)
   └─ cl->execute_query(qe)    → read-only walk         :711   (oks/src/query.cpp:431)
   ▼
OksKernel  ── ctor reads TDAQ_DB_VERSION ──► oks-checkout.sh ──► git clone + git checkout
                                             oks/src/kernel.cpp:930-958, :5937
```

## 3. Proposed MCP architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  MCP / API layer                                          NEW        │
│    tools:  resolve_run · describe_schema · validate_query            │
│            run_query   · list_revisions                              │
└───────────────┬──────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────┐   ┌──────────────────────────────┐
│ Historical configuration resolver │   │ Schema retriever             │
│                          NEW      │   │              NEW (selection) │
│  run + partition                  │   │  classes()                   │
│    → tag "r<run>@<partition>"     │   │  attributes(cls, all=True)   │
│    → or rn DB CONFIGVERSION       │   │  relations(cls, all=True)    │
│    → CONFIGNAME (entry file)      │   │  subclasses/superclasses     │
│  doc 03 §4                        │   │  EXISTS: Configuration.py    │
└───────────────┬───────────────────┘   │         :137-211            │
                │                       └──────────────┬───────────────┘
                │  &version=tag:…                       │  rendered schema
                ▼                                      ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Configuration session cache                              NEW        │
│    keyed by (revision, config_name) — clone is per-kernel and full   │
│    doc 06 §4                                                         │
└───────────────┬──────────────────────────────────────────────────────┘
                │
                │            ┌─────────────────────────────────────────┐
                │            │ Query generator (LLM)          NEW      │
                │            │  emits (class_name, oks_query)          │
                │            │  grammar: ( this|all ( a v op ) )       │
                │            └──────────────┬──────────────────────────┘
                │                           │
                ▼                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Query validator                                                     │
│    pre-flight: class in classes(); attrs in attributes()   NEW       │
│    authoritative: OksQuery ctor + good()                   EXISTS    │
│      oksconfig/src/OksConfiguration.cpp:705-710                      │
└───────────────┬──────────────────────────────────────────────────────┘
                │  bounded retry with parser message
                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  OKS execution adapter                                     EXISTS    │
│    get_objs(class, query) → list[ConfigObject]                       │
│    read-only: OksClass::execute_query() is const  (oks/src/query.cpp:431) │
└───────────────┬──────────────────────────────────────────────────────┘
                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Result serializer                                         NEW       │
│    iterate class_t::p_attributes / p_relationships                   │
│    pattern demonstrated: webis_server/src/oks_handler.cpp:292-303    │
└───────────────┬──────────────────────────────────────────────────────┘
                ▼
      Structured result + provenance (run, SHA, config name, class, query)
                ▼
      Natural-language answer (LLM)                          NEW
```

**No component appears in this diagram merely because it is common in AI systems.** There is
no vector store, no embedding index, no agent framework — because document `08` §6 found no
repository basis for them and §6.1 there argues the schema may simply fit in context.

## 4. Boundary-by-boundary analysis

| Boundary | Repository evidence | Existing component | New code | Unresolved dependency | Expert confirmation |
|---|---|---|---|---|---|
| NL → intent | — | none | yes | — | — |
| run → revision | `rn/src/lib.cpp:104, :255, :274` (write side) | none for reading | **yes** | rn DB endpoint/credentials; tag reliability | **Yes** — doc 03 §14 |
| revision → checkout | `oks/src/kernel.cpp:930–958`, `oks-checkout.sh:155–233` | `OksKernel` | no | `TDAQ_DB_REPOSITORY` value; read access | **Yes** — doc 06 §8 |
| open configuration | `config/python/config/Configuration.py:52–68` | `config` + `oksconfig` | no | TDAQ runtime env | Yes — doc 05 §10 |
| schema retrieval | `Configuration.py:137–211`; `config/config/Schema.h:155–163` | `config` | selection/rendering only | schema size in production | Partly |
| query generation | grammar in `oks/src/query.cpp:127–137, :377–420` | none | yes | — | — |
| query validation | `oksconfig/src/OksConfiguration.cpp:705–710` | **`OksQuery` + `good()`** | thin wrapper + retry | exception-type flattening (doc 09 §6) | No |
| execution | `oks/src/query.cpp:431–535` | `execute_query` | no | result-size limits | No |
| serialization | pattern at `webis_server/src/oks_handler.cpp:292–303` | none reusable | **yes** | — | No |
| answer + provenance | `oks/oks/kernel.h:516–531` (`OksRepositoryVersion`) | version metadata exists | yes | — | No |

## 5. J1 — Minimum useful six-week scope

**In scope:**

1. **`resolve_run(run, partition) → {revision, config_name}`** — via the derivable tag
   `r<run>@<partition>` first, with the run-number DB as the authoritative fallback.
2. **`open(revision, config_name)`** — construct
   `Configuration(f"oksconfig:{config_name}&version={revision}")`, cache per
   `(revision, config_name)`. (`TDAQ_DB_VERSION` is an equivalent but process-global
   fallback and must not be used concurrently.)
3. **`describe_schema(classes?)`** — class list; full detail for selected classes plus one
   relationship hop.
4. **`validate_query(class, query)`** — pre-flight + real parser, returning the parser message.
5. **`run_query(class, query) → JSON`** — execute and serialize, with a result cap.
6. **NL front end** — generate `(class, query)`, validate, retry bounded, answer citing run,
   SHA, config name, class and query text.

**Why this is the minimum that is useful:** it answers "what was configured for run N?"
end to end, which is the project's actual purpose, and every step below the MCP is existing,
tested code.

**Confidence: Strongly indicated** (engineering scope proposal on Confirmed facts).

## 6. J2 — Read-only vs read/write boundary

**Read-only, strictly. Deferred: all mutation.**

Evidence-backed reasons (document `04` §C4): the query API cannot mutate; mutation is a
disjoint API; publishing requires credentials and passes a token + AccessManager gate; and
historical checkouts have **no** library-level write protection (document `03` §11).

**Concretely, the prototype must not expose or call:** `create_obj`, `destroy_obj`,
`create_db`, `add_dal`, `update_dal`, `destroy_dal`, `add_include`, `remove_include`,
`commit`, `set_commit_credentials`
(`config/python/config/Configuration.py:213–590`; `config/config/Configuration.h:1203–1217`).
Note these **are** reachable from the same Python object the prototype uses — read-only is a
property of the MCP tool surface, not of the library.

**Confidence: Confirmed.**

## 7. J3 — Best integration boundary

**The `config` Python binding (`pyconfig`), backend `oksconfig`, revision via the
`&version=` connection parameter.**

| Candidate | Verdict | Basis |
|---|---|---|
| **`config` Python binding** | **Chosen** | Query + schema + revision, all present; built, tested, internally used (doc 05 §3.4) |
| WebDAQ / `webis_server` HTTP | Rejected | No query, no revision (doc 02 §8) |
| New pybind11/SWIG binding | Rejected | Duplicates `pyconfig` (doc 05 §E4) |
| `oks_dump` subprocess | Rejected | Output is human-readable text (doc 05 §5) |
| Direct `OksKernel` via new binding | Rejected | Bypasses `config`'s version API; more surface |
| Shelling out to `oks-*.sh` | Rejected | OKS parses script stdout itself; re-doing it is fragile (doc 06 §2) |

**Confidence: Strongly indicated.**

## 8. J4 — Components to reuse

| Reused | Package | Citation |
|---|---|---|
| Repository checkout at a revision | `oks` | `oks/src/kernel.cpp:5937–5997` |
| Version parsing (`param:value`) | `oks` | `oks/src/kernel.cpp:757–773` |
| Revision listing + provenance | `oks`, `config` | `oks/oks/kernel.h:516–531`; `config/config/Configuration.h:1283` |
| Schema/data XML loading, includes | `oks` | `oks/oks/kernel.h:543, :552, :1016` |
| Schema meta-model | `config` | `config/config/Schema.h:52–163` |
| Schema introspection in Python | `config` | `config/python/config/Configuration.py:137–211` |
| **Query parsing + schema validation** | `oks` | `oks/src/query.cpp:182–425` |
| Query execution | `oks` | `oks/src/query.cpp:431–535` |
| Python bindings | `config` | `config/src/python/config.cpp` |
| Backend selection by connection string | `config` | `config/src/Configuration.cpp:127–147` |

## 9. J5 — Security, operational, deployment and historical-data constraints

**Security (Confirmed from source):**

- **JWT authentication.** `daq_tokens` provides `acquire()`/`verify()`
  (`daq_tokens/README.md:1–25`); `oks` links it (`oks/CMakeLists.txt:10`) and
  `commit_repository()` verifies a token: `auto token = daq::tokens::verify(credentials);`
  (`oks/src/kernel.cpp:6167`).
- **PAM.** `OksKernel::validate_credentials(user, passwd)` runs `pam_start()` /
  `pam_authenticate()` (`oks/src/kernel.cpp:6736–6759`).
- **AccessManager (XACML) authorization** on database resources in
  `oks_validate_repository` (`oks/bin/oks_validate_repository.cpp:21–24, :37–38`).

**All three sit on the *write* path.** No authentication or authorization was found on the
read/query path. *Searched:* `oks/src/query.cpp`, `oksconfig/src/OksConfiguration.cpp`,
`config/src/Configuration.cpp` for token/PAM/AccessManager calls — **none**.
**This does not mean reading is unrestricted** — access is presumably controlled by Git
repository permissions, which are outside this release. **Not established from the
new-release repository**; expert question.

**Operational (Confirmed):**

- `oks-checkout.sh` performs a **full `git clone` per kernel** into a fresh temporary
  directory (`oks-checkout.sh:155`; `oks/src/kernel.cpp:945`) — caching is required, not
  optional.
- `git` and the `oks-*.sh` scripts must be on `PATH`; backends must be `dlopen`-able
  (document `05` §4).
- A debug side-effect: unless `OKS_GIT_DEBUG=no`, the checkout writes `printenv`, `ps xuww`
  and `pstree` output into `.git/oks_proc_info` (`oks-checkout.sh:214–223`). **`printenv`
  dumps the full environment to disk**, which for a service holding credentials in
  environment variables is a real leak. Set `OKS_GIT_DEBUG=no`.
- Repository operations are threaded: `rn` tags on a background `std::thread`
  (`rn/src/lib.cpp:317`); `OksKernel` guards output with `p_parallel_out_mutex`
  (`oks/src/kernel.cpp:5972`).

**Historical-data constraints (Confirmed):**

- `CONFIGVERSION` may be **NULL** for runs taken without a pinned version or from a user
  repository (`rn/src/lib.cpp:148, :252`) — such runs are unresolvable by DB lookup.
- Tagging is **best-effort** on a detached thread; failures only raise an ERS error
  (`rn/src/lib.cpp:108–111`) — the tag may be absent.
- Schema may differ between revisions (document `07` §9) — schema must be read from the same
  checkout as the data.
- Historical configurations have **no write protection** (document `03` §11).

## 10. J6 — Recommended architecture and explicitly excluded work

**Recommended:** §3, with the six tools of §5, read-only per §6, integrated per §7.

**Explicitly out of scope for the six-week prototype:**

| Excluded | Why |
|---|---|
| Any configuration mutation | J2; needs credentials and passes an authorization gate |
| Commit / tag operations | Same |
| A GitLab (or other provider) API client | No provider API is used anywhere (document `06` §F1–F2) |
| A provider abstraction layer | Not justified by evidence (document `06` §F4) |
| A new pybind11/SWIG binding | `pyconfig` already suffices (document `05` §E4) |
| Vector/embedding retrieval | No repository basis; measure schema size first (document `08` §6.1) |
| `path-to` / `QueryPath` queries | Second grammar; not needed for the core use case |
| `rdbconfig` / live-partition access | Historical use not established (document `05` §6) |
| CORAL "OKS Archive" integration | Superseded-status unclear (document `03` §12) |
| Extending `webis_server` with a query endpoint | Larger change to a deployed service; ask experts first |
| Multi-partition or cross-revision joins | Not expressible in one OksQuery |

## 11. Risks

| Risk | Severity | Basis | Mitigation |
|---|---|---|---|
| Run→revision lookup unavailable (no API, DB access unknown) | **High** | doc 03 §14 | Use derivable tag; confirm DB access with experts early |
| Tag missing / `CONFIGVERSION` NULL for some runs | **High** | `rn/src/lib.cpp:108–111, :252` | Two independent routes; report honestly when unresolvable |
| Cannot obtain read access to the OKS config repository | **High** | doc 06 §7 | Blocking dependency — raise in the first meeting |
| TDAQ runtime environment hard to provision for a service | Medium | doc 05 §4 | Confirm deployment target early |
| LLM violates `( this\|all ( … ) )` grammar or operand order | Medium | doc 08 §9 | Exact validator + bounded retry; few-shot the grammar |
| Full clone per request is too slow | Medium | `oks-checkout.sh:155` | Cache per revision |
| Schema too large for context | Medium | doc 08 §6.1 | Measure first; keyword selection |
| Semantically wrong but valid queries | **High** | doc 08 §3 | Always cite run, SHA, class and query text so a human can check |
| Python binding unsupported / unstable | Medium | doc 05 §8 | Expert question; boundary is thin enough to swap |
| Environment leak via `.git/oks_proc_info` | Medium | `oks-checkout.sh:214–223` | Set `OKS_GIT_DEBUG=no` |

## 12. Questions for ATLAS/TDAQ experts

1. How should run → OKS Git SHA be resolved — the `r<run>@<partition>` tags, the run-number
   database, or something else? Are the tags reliably present?
2. What is `TDAQ_DB_REPOSITORY` in production, and can a read-only service get clone access?
3. Is the `config` Python binding supported, with a stable `get_objs` signature?
4. How should a service provision the TDAQ runtime environment?
5. Are read operations access-controlled beyond Git permissions?
6. Is the CORAL "OKS Archive" still in use?
7. How many classes does a real ATLAS configuration expose, and how often does the schema
   change across revisions?
8. Would extending `webis_server` with a query endpoint be preferable to a separate service?

## 13. Evidence index

| File | Symbols / lines |
|---|---|
| `config/python/config/Configuration.py` | ctor/connection :52–68; `get_objs` :117; schema methods :137–211; mutation surface :213–590 |
| `config/src/python/config.cpp` | `get_objs` :161–170; exception translator :35–38, :363 |
| `config/config/Configuration.h` | `get()` :698; credentials/commit :1203–1217; `get_versions` :1283 |
| `config/config/Schema.h` | meta-model :52–163 |
| `config/src/Configuration.cpp` | plugin load :127–147 |
| `oksconfig/src/OksConfiguration.cpp` | `get()` :693–729; validation :705–710 |
| `oks/src/query.cpp` | `this`/`all` prefix :127–137; parser :182–425; schema checks :341, :363, :379; `execute_query` :431–535 |
| `oks/src/kernel.cpp` | `parse_config_version` :757–773; ctor/version :930–958; temp repo :945; `k_checkout_repository` :5937–5997; parallel-out mutex :5972; `commit_repository` :6117, token verify :6167; PAM :6736–6759 |
| `oks/oks/kernel.h` | `OksRepositoryVersion` :516–531; load doc :543, :552; `get_includes` :1016 |
| `oks/scripts/oks-checkout.sh` | `git clone` :155; checkout :172–206; `OKS_GIT_DEBUG` block :214–223; version echo :233 |
| `oks/CMakeLists.txt` | `daq_tokens`/`pam` link :10 |
| `oks/bin/oks_validate_repository.cpp` | AccessManager :21–24, :37–38; token :303 |
| `daq_tokens/README.md` | JWT purpose and API :1–25 |
| `rn/src/lib.cpp` | tag :104; conditional capture :148; NULL case :252; `CONFIGVERSION` :255; `CONFIGNAME` :274; background thread :317; ERS error :108–111 |
| `webis_server/src/oks_handler.cpp` | URL grammar :15–29; no-query `get` :284; JSON assembly :292–303 |
