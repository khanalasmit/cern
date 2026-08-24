# 11 — Technical Evidence Matrix (new release: `tdaq-13-00-00`)

Meeting-ready summary for the ATLAS/TDAQ technical discussion.
Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Paths relative to `Materials/tdaq-cmake-tdaq-13-00-00/`; `tdaq-common:` = `Materials/tdaq-common-cmake-13-00-00/`.

Confidence values used: **Confirmed** · **Strongly indicated** · **Partially established** ·
**Not established from repository**.

---

## Matrix

### A — Architecture

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| A1 | Complete historical configuration access workflow | Revision selected via `oksconfig` `&version=` or `TDAQ_DB_VERSION` → kernel ctor → git checkout → `load_schema`/`load_data` → `OksQuery` → `execute_query` → results wrapped as `ConfigObject`. Software workflow complete; the *operational* shifter workflow is not in the release | `oks/src/kernel.cpp:930–958`; `oks/oks/kernel.h:543,552`; `oksconfig/src/OksConfiguration.cpp:705,711` | Confirmed (software) / Not established (operational) | Yes |
| A2 | Responsibilities of DAL, `config::Configuration`, `oksconfig`, `OksKernel`, `OksQuery`, WebDAQ | Three layers: `config` (neutral façade, opaque query string) → `oksconfig` (`OksConfiguration`, builds `OksQuery`) → `oks` (kernel/model/query). DAL = generated accessors + core schema. WebDAQ is **not** in this chain | doc `02` §3, §5; `config/src/Configuration.cpp:127–147` | Confirmed | No |
| A3 | Does DAL or `config::Configuration` internally use `OksQuery`? | **Neither.** `config` passes the string through; `oksconfig` constructs `OksQuery`. DAL has no `OksQuery` reference | `config/config/Configuration.h:698`; `oksconfig/src/OksConfiguration.cpp:705`, `:711`; searched `dal/` — no hits | Confirmed | No |
| A4 | What does `config::Configuration` understand about OKS? | Primarily generic (opaque query, `dlopen` backends) **but** carries an OKS-shaped schema model and a Git-SHA version model | `config/config/Schema.h:52–163`; `config/config/ConfigVersion.h:47–52` | Confirmed | No |
| A5 | Is WebDAQ an HTTP/JSON OKS interface, and what does it use internally? | `webdaq` is an HTTP/JSON client for the **Information Service**. It has an `oks::` namespace with exactly two read-only calls (`get`, `list`). Server `webis_server` serves them from `rdbconfig:RDB@<partition>` — a **live** partition, **no query**, **no revision** | `tdaq-common:webdaq/README.md:1–6`; `tdaq-common:webdaq/webdaq/webdaq-curl.hpp:235–251`; `webis_server/src/oks_handler.cpp:15–29, :275, :284` | Confirmed | Yes |
| A6 | Recommended/officially supported Python MCP integration interface | A Boost.Python binding **exists**, is built, tested and internally used, and exposes `get_objs(class, query)` plus schema introspection. **No support policy is stated anywhere in the release — for any interface** | `config/CMakeLists.txt:18,22`; `config/python/config/Configuration.py:117`; `config/src/python/config.cpp:161–170` | Confirmed (exists) / **Not established** (support status) | **Yes** |

### B — Historical configuration

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| B1 | How does a run number map to a configuration and revision? | At run-number allocation the OKS **Git SHA** is read from IS and written to the run DB as `CONFIGVERSION`, with `CONFIGNAME` (entry data file) and `PARTITIONNAME`; **and** the OKS repo is tagged `r<run>@<partition>`. Nothing in the release *reads* this back | `rn/src/lib.cpp:148–150, :251–256, :258–274, :100–107, :313–318`; `dal/src/algorithms.cpp:3292`; `dal/data/is/oks-version.schema.xml` | Confirmed (write side) / Not established (read API) | **Yes** |
| B2 | Does an OKS database hold one configuration or several? | Several. A kernel holds a set of files and classes; files may `include` others; the ATLAS "configuration" unit is the `Partition` object. Release ships multiple `Partition`-declaring files | `oks/oks/kernel.h:1016, :1504–1573`; `dal/data/schema/core.schema.xml`; doc `01` §9 | Confirmed | No |
| B3 | Are schema/data in Git, and is the Git revision authoritative? | Yes to both — with the five sub-claims separated in doc `03` §6. Files in Git ✔; history in Git ✔; revisions = configuration versions ✔; run→revision recorded ✔; **automatic run→revision resolution ✘** | `config/config/ConfigVersion.h:47–52`; `oks/scripts/oks-checkout.sh:155–233`; `oks/scripts/oks-log.sh:90–91` | Confirmed (4 of 5) / Not established (5th) | Yes |
| B4 | Supported mechanism for accessing a historical configuration | Two equivalent routes to the same `OksKernel` version argument: (a) the **`oksconfig` connection parameter** `oksconfig:<files>&version=<tag\|hash\|date>:<value>` — per-object, concurrency-safe; (b) the **`TDAQ_DB_VERSION`** environment variable — process-global. Both drive `oks-checkout.sh` (`git clone` + `git checkout`) | `oksconfig/src/OksConfiguration.cpp:150, :153–205`; `oks/src/kernel.cpp:757–773, :930–958, :5937–5997`; `oks/scripts/oks-checkout.sh:155–233` | Confirmed (mechanism) / Not established (whether `version=` is documented/supported) | Yes (support status) |
| B5 | Actual schema/data loading workflow and query execution | Ordinary `load_schema()`/`load_data()` from the checked-out user repository; then `OksQuery` + `execute_query()`. No separate "historical" load path | `oks/oks/kernel.h:543, :552`; `oks/src/kernel.cpp:776–796`; `oks/src/query.cpp:431` | Confirmed | No |
| B6 | Are historical configurations read-only in practice? | **No API-level protection.** Protection is structural: per-kernel temporary clone, and publishing needs an explicit `commit_repository()` behind a token/AccessManager gate | `oks/src/kernel.cpp:945–948, :6001, :6117–6127`; `oks/oks/object.h:601, :937` | Confirmed | Yes |
| B7 | Can multiple configurations coexist in one loaded database? | Yes — multiple data files and multiple `Partition` objects | `oks/oks/kernel.h:1504–1573`, `:1016` | Confirmed | No |
| B8 | What prevents accidental modification? | See B6. Additionally a checkout at a tag/hash leaves the branch not tracking origin | `oks/scripts/oks-checkout.sh:172` | Confirmed (B6) / Strongly indicated (branch state) | No |

### C — OksQuery and mutation

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| C1 | OksQuery capabilities; can it mutate? | Attribute comparison (`=`,`!=`,`~=`,`<=`,`>=`,`<`,`>`), `object-id`, `and`/`or`/`not`, relationship nesting (`some`/`all`), subclass inclusion, plus a `path-to` form. **Cannot mutate** — `execute_query()` is `const` and only collects matches | `oks/src/query.cpp:15–31, :431–535`; `oks/oks/query.h:169` | Confirmed | No |
| C2 | APIs that create/modify/delete OKS objects | `OksObject::SetValue/SetValues/Set·Add·RemoveRelationshipValue`, `OksObject::destroy()`; `Configuration::create()/destroy_obj()`; `ConfigObject::set_*()`; all re-exported in Python | `oks/oks/object.h:601,607,937,1155–1310`; `config/config/Configuration.h:568,632`; `config/config/ConfigObject.h:302–468` | Confirmed | No |
| C3 | Architectural separation between query and mutation | Real and structural — different classes, `const` vs non-`const`, disjoint entry points; disk and Git each require a separate explicit call | doc `04` §7 | Confirmed | No |
| C4 | Should the first prototype be read/query-only? | **Yes** — the query API cannot mutate; mutation is a disjoint API; publishing needs credentials + authorization; historical checkouts have no write protection | doc `04` §8 | Confirmed | No |

### D — Modification tooling

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| D1 | Existing tools to create/modify configurations | GUI `dbe`; CLIs `oks_dump`, `oks_validate_repository`, `oks_clone_repository`, `config_dump`, `config_export_*`; 11 `oks-*.sh`; `PartitionMaker`; C++/Python/Java APIs | `oks/CMakeLists.txt:14–18`; `config/CMakeLists.txt:9–11`; package `dbe` | Confirmed (existence) / Not established (which is recommended) | Yes |
| D2 | How does a modification become a Git revision? | `Configuration::commit()` → `OksKernel::commit_repository()` → `oks-commit.sh`: temp branch, commit, `git pull -r origin`, with rollback paths | `config/config/Configuration.h:1217`; `oks/src/kernel.cpp:6127`; `oks/scripts/oks-commit.sh:43–88, :172–179` | Confirmed | No |
| D3 | Which API should a future NL modification system call? | `config::Configuration` — `create`/`destroy_obj`/`set_*` then `commit()`. It is the layer the Python, Java and HTTP paths all already use, and the layer owning `commit()` | `config/config/Configuration.h:568–645, :1203–1217` | Strongly indicated (engineering proposal) | Yes |
| D4 | Validation before a changed configuration is accepted | `oks_validate_repository` combines DAQ-token authentication, AccessManager XACML authorization, consistency and circular-include checks. **It is not called from `oks-commit.sh`** — so whether it is enforced server-side is unknown | `oks/bin/oks_validate_repository.cpp:19–24, :31–41, :190–195, :303`; searched `oks-commit.sh` — no call | Confirmed (tool) / Not established (enforcement) | **Yes** |

### E — Integration boundary

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| E1 | Does WebDAQ cover historical access and read-only querying? | Read-only ✔; querying ✘; historical ✘ | `webis_server/src/oks_handler.cpp:15–29, :284`; `tdaq-common:webdaq/webdaq/webdaq-curl.hpp:235–251` | Confirmed | No |
| E2 | WebDAQ vs native C++ — advantages and limits | WebDAQ: stand-alone (curl + nlohmann/json only), JSON, trivial from Python — but no query, no revision, live-partition only. Native: full query + revision + schema — but needs the TDAQ runtime env, `dlopen`-able backends and `git` on `PATH` | `tdaq-common:webdaq/README.md:8–22`; doc `05` §4 | Confirmed | No |
| E3 | Existing supported Python bindings and exposed APIs | Boost.Python `pyconfig`: `get_objs(class, query)`, `attributes`, `relations`, `superclasses`, `subclasses`, `classes`, object/DAL access, mutation. Tested; `config`'s own Python emits an OKS query through it | `config/src/python/config.cpp:392, :442–447`; `config/python/config/Configuration.py:117–211, :563–564` | Confirmed (exists) / **Not established** (supported) | **Yes** |
| E4 | New thin binding vs WebDAQ | **Neither.** Use the existing binding — a new one would duplicate `pyconfig`; WebDAQ structurally cannot express the use case | doc `05` §E4 | Strongly indicated | No |
| E5 | Existing C++ executables/services accepting OksQuery and returning results | `oks_dump` accepts a query but prints human-readable text; `webis_server` returns JSON but accepts no query. **No tool does both** | `oks/bin/oks_dump.cpp:262–270`; `webis_server/src/oks_handler.cpp:284` | Confirmed | No |
| E6 | Best first-prototype path | Python MCP → `config` Python binding (`oksconfig:`) → `oksconfig` → `oks`, with `TDAQ_DB_VERSION` set before construction | doc `05` §E6, doc `10` §7 | Strongly indicated | Yes |

### F — Git

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| F1 | Which Git hosting provider is evidenced? | **None in the configuration-access code.** Zero hits for `gitlab\|gitea\|github\|bitbucket` in `oks`, `config`, `dal`, `rn` source. The `gitlab.cern.ch` reference in `README.md` is the **software** repository, not the OKS configuration repository | searched `oks/{src,oks,bin,scripts}`, `config/{src,config}`, `dal/src`, `rn/src`; `README.md:8–11` | Confirmed | Yes (production URL) |
| F2 | Ordinary Git, provider REST API, SDK, or Git library? | **Ordinary `git` CLI**, via `system()` calls to `oks-*.sh`. No Git library linked (`oks` links `daq_tokens osw ers Boost tbbmalloc stdc++fs pam`), no HTTP client | `oks/src/kernel.cpp:5945, :5978–5980`; `oks/CMakeLists.txt:9–12`; `oks/scripts/*.sh` | Confirmed | No |
| F3 | How are historical revisions accessed? | `git clone` then `git checkout` of `tags/<tag>`, a hash, or `git rev-list -1 --before=<date>`; resulting SHA read back from script stdout | `oks/scripts/oks-checkout.sh:155–233`; `oks/src/kernel.cpp:5991–5997` | Confirmed | No |
| F4 | Does a provider abstraction exist, or is one justified? | **No provider abstraction.** `TDAQ_DB_REPOSITORY` is a `\|`-separated URL list; `OKS_GIT_PROTOCOL` selects by **URL prefix** — a transport switch, not a provider layer. Building one is **not** justified | `oks/src/kernel.cpp:337–369`; `oks/bin/oks_git_repository.cpp:26` | Confirmed | No |

### G — Schema

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| G1 | Authoritative schema location; schema↔data relationship | Content: schema XML in the OKS repository (`dal/data/schema/core.schema.xml`, 83 classes, + 103 in-release schema files). Programmatic authority: `daq::config::class_t`. Schema and data are separate files sharing one Git revision | `dal/data/schema/core.schema.xml`; `config/config/Schema.h:155–163`; `oksconfig/oksconfig/ROksConfiguration.h:30–32` | Confirmed | No |
| G2 | Does the schema provide what OksQuery generation needs? | **Yes, completely** — class/attribute/relationship names, 17 types, ranges, integer format, multi-value, nullability, cardinality, inheritance, descriptions. It does **not** provide the query grammar | `config/config/Schema.h:20–163`; doc `07` §8 G2 | Confirmed | No |
| G3 | Schema-inspection API vs manual XML parsing | Full inspection API at `oks` and `config` levels and in Python. Manual XML parsing is unnecessary and would re-implement includes, inheritance flattening and range handling | `oks/oks/class.h:479–606`; `config/python/config/Configuration.py:137–211` | Confirmed | No |
| G4 | Evidence-backed schema source for retrieval | Python `Configuration` schema methods on the **same object** used for the query — guaranteeing schema shown and schema enforced cannot drift | `oks/src/query.cpp:341, :363, :379` | Strongly indicated | No |
| G5 | Existing structured machine-readable schema representation | **Yes** — `class_t`/`attribute_t`/`relationship_t`, explicitly Python-binding-aware | `config/config/Schema.h:52–163` (py-ctors :77, :133, :174) | Confirmed | No |

### H — Schema retrieval for the LLM

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| H1 | Supplying schema information to an LLM | Retrieve via Python schema methods on the query's own `Configuration`; render class + attributes + relationships + inheritance + descriptions; supply the grammar separately | doc `08` §7 | Confirmed (availability) / proposal (rendering) | No |
| H2 | Exact/keyword vs semantic vs hybrid retrieval | **The repository contains no LLM or retrieval code at all** — zero matches for `vector search`, `semantic search`, `rag`, `language model`; the `llm`/`embedding` hits are false positives (`FullModeBuilder`; Python-interpreter embedding). Purely an engineering choice | doc `08` §6 | **Not established from repository** | No |
| H3 | Schema representation needed by the LLM | The prompt's {name, type, multiplicity, target, inheritance} is **necessary but not sufficient** — also needs `range`, `int_format`, `is_not_null`, `is_abstract`, cardinality, subclasses and descriptions | doc `08` §4 | Confirmed (fields needed) / proposal (layout) | No |
| H4 | Relationship representation for semantically valid queries | Must carry name, **target class** and cardinality — the nested sub-expression is parsed in the scope of the target class | `oks/src/query.cpp:363–376` | Confirmed | No |
| H5 | Schema consistency across revisions | Consistent within a revision (one repo, one checkout); **may differ across** revisions (OKS supports schema evolution); the matching historical revision **must** be used | `oks/README.md:3`; `oks/oks/kernel.h:1283–1300`; doc `03` §7 | Confirmed | Yes (frequency) |

### I — Pipeline

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| I1 | Suitability of the proposed NL→OksQuery pipeline | Suitable with two corrections: the generated artefact must be a **`(class_name, query)` pair**, and "historical resolution" is **two** facts (`CONFIGNAME` + `CONFIGVERSION`) plus the partition | `config/config/Configuration.h:698`; `oks/src/query.cpp:85`; `rn/src/lib.cpp:255, :274` | Confirmed | No |
| I2 | Existing components vs components to implement | Exists: checkout, loading, schema introspection, query parsing, **validation**, execution, revision listing, Python bindings. To build: run→revision lookup, schema selection, query generation, retry loop, serialization, answer composition, checkout caching | doc `09` §3 | Confirmed | No |
| I3 | Should the LLM generate only the query, or also run/config/revision? | LLM emits `{run, partition, class_name, query}`; **deterministic code** derives `{revision, config_name}` — the revision is recorded data with **no validator** for a guess, whereas the query has an exact one | `rn/src/lib.cpp:104, :255`; `oksconfig/src/OksConfiguration.cpp:705–710` | Strongly indicated | No |
| I4 | Existing reusable validation mechanism, and where validation belongs | `OksQuery(cl, query)` + `good()` — schema-aware, side-effect-free, the same code that executes. Should run in the MCP before answering, against the historical revision's schema, ideally with a cheap pre-flight check because all errors flatten to `RuntimeError` in Python | `oks/src/query.cpp:341–420`; `config/src/python/config.cpp:363` | Confirmed | No |

### J — Prototype

| ID | Question | New-release repository finding | Evidence | Confidence | Expert? |
|---|---|---|---|---|---|
| J1 | Minimum useful six-week scope | Six tools: `resolve_run`, `open`, `describe_schema`, `validate_query`, `run_query`, `list_revisions`, plus the NL front end — answering "what was configured for run N?" end to end | doc `10` §5 | Strongly indicated | Yes |
| J2 | Read-only boundary; deferred mutation | Strictly read-only. Must not expose `create_obj`, `destroy_obj`, `create_db`, `add_dal`, `update_dal`, `destroy_dal`, `add_include`, `remove_include`, `commit`, `set_commit_credentials` — all reachable from the same Python object | `config/python/config/Configuration.py:213–590`; doc `04` §8 | Confirmed | No |
| J3 | Safest maintainable integration boundary | The `config` Python binding with the `oksconfig` backend | doc `10` §7 | Strongly indicated | Yes |
| J4 | Components to reuse | Checkout, version parsing, revision listing/provenance, XML loading, schema meta-model, schema introspection, **query parsing + validation**, execution, Python bindings, backend selection | doc `10` §8 | Confirmed | No |
| J5 | Security / operational / deployment / historical-data constraints | Writes are gated by JWT (`daq_tokens`), PAM and AccessManager XACML; **no auth found on the read path**. Full `git clone` per kernel. `git` + `oks-*.sh` on `PATH`. `OKS_GIT_DEBUG` unset dumps `printenv` into `.git/oks_proc_info`. `CONFIGVERSION` may be NULL; tagging is best-effort | `oks/src/kernel.cpp:6167, :6736–6759`; `oks/bin/oks_validate_repository.cpp:21–24`; `oks/scripts/oks-checkout.sh:155, :214–223`; `rn/src/lib.cpp:108–111, :252` | Confirmed | Yes |
| J6 | Recommended architecture; explicitly excluded work | Architecture per doc `10` §3. Excluded: all mutation, commit/tag, provider API client, provider abstraction, new binding, vector retrieval, `path-to` queries, `rdbconfig` live access, CORAL archive, extending `webis_server`, cross-revision joins | doc `10` §10 | Strongly indicated | Yes |

---

## 1. Top confirmed facts

1. **`OksQuery` is built and executed in `oksconfig`, not in `config` or DAL.**
   `oksconfig/src/OksConfiguration.cpp:705, :711`.
2. **Query parsing is schema-validated** against the loaded classes — attributes,
   relationships, target classes and comparators are all resolved.
   `oks/src/query.cpp:341, :363, :379, :415`.
3. **Query execution is read-only.** `OksClass::execute_query()` is `const` and only
   collects matches. `oks/src/query.cpp:431–535`.
4. **A top-level query must be `( this|all ( … ) )`, and comparators are
   `(attribute value operator)`** — reversed from most query languages.
   `oks/src/query.cpp:127–137, :377–420`.
5. **A Python binding already exposes `get_objs(class_name, query)`** plus full schema
   introspection. `config/python/config/Configuration.py:117–211`.
6. **Historical access is one string** — either the `oksconfig` connection parameter
   `&version=<tag|hash|date>:<value>` (`oksconfig/src/OksConfiguration.cpp:150, :191–202`)
   or the `TDAQ_DB_VERSION` environment variable
   (`oks/src/kernel.cpp:757–773, :930–958`). The connection parameter is per-`Configuration`
   and therefore safe under concurrency; the environment variable is not.
7. **Retrieval is plain Git via shell scripts** — `git clone` + `git checkout`, no provider
   API, no Git library. `oks/scripts/oks-checkout.sh:155–233`; `oks/CMakeLists.txt:9–12`.
8. **The configuration version is a Git SHA**, so documented at the `config` layer.
   `config/config/ConfigVersion.h:47–52`.
9. **The run→revision mapping is recorded at run start, twice** — DB column `CONFIGVERSION`
   and Git tag `r<run>@<partition>`. `rn/src/lib.cpp:104, :255, :274`.
10. **Schema and data share one revision** — one repository, one checkout.
11. **A structured schema meta-model exists** and is Python-binding-aware.
    `config/config/Schema.h:52–163`.
12. **WebDAQ is not an OKS query interface** — two read-only calls, no query, no revision,
    live partitions only. `webis_server/src/oks_handler.cpp:15–29, :284`.
13. **Writes are gated by JWT, PAM and AccessManager; reads are not gated in code.**
    `oks/src/kernel.cpp:6167, :6736–6759`.
14. **All `daq::config` errors flatten to Python `RuntimeError`.**
    `config/src/python/config.cpp:363`.

## 2. Changes from the old release

**Not included.** The old-vs-new comparison had not been performed at the time this document
was written, and this document set may not assume differences or similarities. The comparison
is a separate deliverable: `docs/investigation/comparison/old_vs_new.md`.

## 3. Critical unknowns

| # | Unknown | What was searched | What is missing |
|---|---|---|---|
| 1 | **Programmatic run → revision lookup** | `rn/`, `config/`, `dal/`, `oks/` for run-number-keyed reads | A client API; `TDAQ_RUN_NUMBER_CONNECT` endpoint and credentials |
| 2 | **Production `TDAQ_DB_REPOSITORY`** | all `oks-*.sh`, `oks/src/kernel.cpp`, all CMake, for a default | Any default or example value |
| 3 | **Support status of any interface** | `config/doc/RELEASE_NOTES.md`, CMake, CI, `doc/BUILDING.md`, `doc/INSTALL.md`, superproject `README.md` | Any support policy or API-stability statement for **any** interface |
| 4 | **Is `oks_validate_repository` enforced server-side?** | `oks-commit.sh` for a call to it | A server hook or CI gate |
| 5 | **Whether `r<run>@<partition>` tags actually exist/persist** | `rn/src/lib.cpp` | Production repository state |
| 6 | **Deployed `RunNumber` DDL** | `rn/src/create_db*.sql` | The `.sql` lacks `CONFIGVERSION`/`CONFIGNAME` that the code writes |
| 7 | **Is the CORAL "OKS Archive" still populated?** | `oks2coral/` | Any statement of current status |
| 8 | **Can `rdbconfig` serve historical revisions?** | `rdbconfig/` for version parameters | Any revision parameter; spec is `RDB@<partition>` |
| 9 | **Production schema size and churn** | `dal/data/schema/`, 103 schema files | The production configuration itself |
| 10 | **Read-path access control** | query/config/oksconfig sources for auth calls | Whether Git permissions are the only control |
| 11 | **Regex semantics of `~=`** | `oks/oks/query.h:172`, `oks/src/query.cpp` | `boost::regex` construction flags |
| 12 | **`felix-interface` package** | — | Not anonymously readable (`HTTP Basic: Access denied`) |
| 13 | **Is `oksconfig`'s `version=` parameter supported?** | `oksconfig/doc/RELEASE_NOTES.md`, `oksconfig/CMakeLists.txt` | Any mention of the parameter |

## 4. Questions for ATLAS/TDAQ experts

1. How should **run number → OKS Git SHA** be resolved? Are the `r<run>@<partition>` tags
   reliably present and retained, or should we query the run-number database directly — and
   if so, what are the endpoint and credentials?
2. What is **`TDAQ_DB_REPOSITORY`** in production, which `OKS_GIT_PROTOCOL` should a
   read-only service use, and can we get clone access?
3. Is the **`config` Python binding supported** for external consumers, with a stable
   `get_objs` signature? If not, what is the supported interface?
4. How should a service **provision the TDAQ runtime environment** (`dlopen`-able backends,
   `oks-*.sh` and `git` on `PATH`)?
5. Are **read operations access-controlled** beyond Git repository permissions?
6. Is **`oks_validate_repository` enforced** on the server side for commits?
7. Is the **CORAL "OKS Archive"** (`oks2coral`) still in use, or superseded by the Git scheme?
8. For runs where **`CONFIGVERSION` is NULL**, is there any other way to recover the
   configuration?
9. How many classes does a real ATLAS configuration expose, and **how often does the schema
   change** across revisions?
10. Would **extending `webis_server`** with a query endpoint be preferable to a separate
    Python service?
11. Can `rdbconfig` be pointed at a **historical** revision?
12. Is `felix-interface` relevant to configuration access, and can we get read access?
13. Is the `oksconfig` **`version=` connection parameter** documented and supported for
    external use? It is the cleanest historical-access route but appears undocumented
    (searched `oksconfig/doc/RELEASE_NOTES.md`, `oksconfig/CMakeLists.txt`).

## 5. Proposed prototype boundary

Read-only Python MCP server → existing `config` Python binding (`oksconfig:` backend) →
`oksconfig` → `oks`, with the revision passed in the connection string:
`Configuration("oksconfig:<config>&version=tag:r<run>@<partition>")`.

Six tools: `resolve_run`, `open`, `describe_schema`, `validate_query`, `run_query`,
`list_revisions`. New code is limited to run resolution, schema selection/rendering, query
generation, validation retry, serialization and answer composition. Detail: doc `10` §5.

## 6. Architecture decisions still pending expert confirmation

| Decision | Depends on |
|---|---|
| Run-resolution route: Git tag vs run-number DB | Q1 |
| Whether the Python binding is the integration boundary | Q3 |
| Deployment model for the TDAQ runtime environment | Q4 |
| Whether checkout caching is acceptable vs per-request clone | Q2, repository size |
| Whether to build a separate service or extend `webis_server` | Q10 |
| Whether any retrieval machinery is needed at all | Q9 (schema size) |
| Whether the CORAL archive must be supported | Q7 |

## 7. Source evidence index

**Packages examined with source at pinned revisions** (SHAs in doc `01` §3): `oks`,
`config`, `oksconfig`, `rdbconfig`, `dal`, `rn`, `oks2coral`, `webis_server`, `oks_utils`,
`dbe`, `daq_tokens`, `RunControl`, and `tdaq-common:webdaq`.

| File | Symbols / lines |
|---|---|
| `oks/src/query.cpp` | keywords :15–31; ctor + `this`/`all` :85–176 (:127–137); `create_expression` :182–425; schema resolution :341, :363, :379; comparator table :392–401; `execute_query` :431–535; `CheckSyntax` :543–620; `SatisfiesQueryExpression` :630–770 |
| `oks/oks/query.h` | `OksQuery` :33–95; `OksComparator` :134–172; relationship/not/and/or :190–300; `QueryPath` :~340–400 |
| `oks/src/kernel.cpp` | `get_repository_root` + `OKS_GIT_PROTOCOL` :337–369; `parse_config_version` :757–773; ctor version/checkout :930–958; `k_checkout_repository` :5937–5997; `commit_repository` :6117, token :6167; `tag_repository` :6278; `get_repository_versions` :6395–6484; PAM :6736–6759 |
| `oks/oks/kernel.h` | exceptions :109–124; `OksRepositoryVersion` :516–531; load doc :543, :552; `get_includes` :1016; schema-file tracking :1283–1300; save/new data :1365–1399; repository API :1586–1700 |
| `oks/oks/object.h` | setters :601–607; `destroy` :926–937; relationship mutators :1155–1310 |
| `oks/oks/class.h` | attributes :479–496; relationships :589–606; `execute_query` :851 |
| `oks/oks/attribute.h`, `relationship.h` | schema accessors (doc `07` §6.1) |
| `oks/scripts/oks-checkout.sh` | `oks_git_repository` :16; branch :30; `git clone` :155; checkout/tag/date :172–206; `OKS_GIT_DEBUG` :214–223; version echo :233 |
| `oks/scripts/oks-commit.sh`, `oks-log.sh`, `oks-update.sh` | commit/rollback :43–88, :172–179; log format :90–91; update :138–181 |
| `oks/bin/oks_dump.cpp`, `oks_validate_repository.cpp`, `oks_git_repository.cpp` | query :262–270; auth/consistency :19–41, :190–195, :303; repo root :26 |
| `oks/CMakeLists.txt` | link list :9–12; executables :14–17; scripts :18 |
| `config/config/Configuration.h` | `get()` :698, :716; create/destroy :568–645; commit/credentials :1203–1223; versions :1258–1283; `_get` :1780–1786 |
| `config/config/ConfigurationImpl.h` | pure-virtual `get` :140–148; `get_class_info` :178 |
| `config/config/Schema.h` | `type_t` :20–37; `attribute_t` :52–61; `cardinality_t` :103–108; `relationship_t` :113–119; `class_t` :155–163 |
| `config/config/ConfigVersion.h` | `QueryType` :33–37; SHA-is-id :47–52 |
| `config/config/ConfigObject.h` | setters :302–468 |
| `config/src/Configuration.cpp` | `TDAQ_DB` :104; plugin load :119–154 |
| `config/src/python/config.cpp` | translator :35–38, :363; `get_objs` :161–170; `attributes` :172–186; exports :392, :442–447 |
| `config/python/config/Configuration.py` | ctor :52–68; `get_objs` :117; schema methods :137–211; mutation :213–590; internal query :563–564 |
| `config/CMakeLists.txt` | `pyconfig` :18; python package :22; tests :30 |
| `oksconfig/src/OksConfiguration.cpp` | creator :30; `get()` :693–729 |
| `oksconfig/oksconfig/ROksConfiguration.h` | schema/data files :30–32 |
| `rdbconfig/src/RdbConfiguration.cpp` | creator :28 |
| `dal/data/schema/core.schema.xml` | DTD :6–78; 83 classes |
| `dal/data/is/oks-version.schema.xml` | IS `ConfigVersion` |
| `dal/src/algorithms.cpp` | `get_config_version` :3289–3327; `set_config_version` :3330+ |
| `dal/CMakeLists.txt` | `pyconfig` link :21–26; python :61–68 |
| `rn/src/lib.cpp` | columns :80–85; `TagRepository` :87–113; capture :148–150; DB write :251–256; `CONFIGNAME` :258–274; tag thread :313–318 |
| `rn/src/create_db.sql` | `RunNumber` table :5–17 (stale) |
| `oks2coral/oks2coral/ConfigVersions.h`, `src/oks2coral.cpp` | archive versions :15–30; run number :217–233; filename convention :238–258; IS check-in :776–792 |
| `webis_server/src/oks_handler.cpp` | URL grammar :15–29; `get_oks_attr` :33; `get_oks_rel` :238; handler :265–305 (no-query :284) |
| `tdaq-common:webdaq/README.md`, `webdaq-curl.hpp`, `webdaq-curl.cpp` | purpose :1–22; `oks::` API :235–251; URLs :463–481 |
| `daq_tokens/README.md` | JWT API :1–25 |
| `CMakeLists.txt`, `.gitlab-ci.yml`, `README.md` (superproject) | version placeholder :3; externals :13–21; `CI_COMMIT_REF_NAME` :110; tdaq-common ref :217; repository :8–11 |
