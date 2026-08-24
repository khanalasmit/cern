# 02 — OKS Architecture (new release: `tdaq-13-00-00`)

Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Nothing in this document is taken from the `tdaq-09-03-00` investigation.

All paths below are relative to `Materials/tdaq-cmake-tdaq-13-00-00/` unless prefixed
`tdaq-common:`, which means `Materials/tdaq-common-cmake-13-00-00/`.

---

## 1. Executive summary

The release implements a **three-layer configuration stack**, and the layering is
demonstrable by tracing calls, not merely by package names:

1. **`config`** — a backend-neutral API (`config::Configuration`). It knows about classes,
   objects, attributes and relationships in the abstract, and it **passes query strings
   through as opaque text**. It loads backends as `dlopen`'d plugins.
2. **`oksconfig`** — the OKS backend. This is the layer that **turns a query string into an
   `OksQuery`** and executes it.
3. **`oks`** — the kernel: `OksKernel` (files, schema, Git), `OksClass`/`OksObject` (model),
   `OksQuery` (query language and execution).

The single most important architectural fact for this project:

> **`OksQuery` is constructed and executed inside `oksconfig`, one layer below the public
> `config::Configuration` API — and the query string that reaches it comes unmodified from
> the caller, including from Python.**

The second most important:

> **`config` ships a maintained Boost.Python binding whose `get_objs(class_name, query)`
> accepts an OKS query string directly.** A Python MCP server therefore does not need a new
> binding to issue OksQuery. (Detail in document `05`.)

The third, which corrects a likely assumption:

> **"WebDAQ" is not an OKS system.** `webdaq` is a stand-alone HTTP/JSON *client library* in
> tdaq-common for the **Information Service**. It has an `oks::` namespace, but that
> namespace offers exactly two read-only calls — get one object, list a class — with **no
> query parameter and no revision parameter**, served from a **live running partition**.

## 2. Release-specific architecture

Evidence-backed flow for a query issued through the supported API:

```
Application  (C++ / Python / Java)
    │
    │  Configuration::get(class_name, objects, query, ...)
    ▼
config::Configuration                     config/config/Configuration.h:698
    │  dlopen("lib<backend>.so"), symbol _<backend>_creator_
    │                                      config/src/Configuration.cpp:127-147
    ▼
ConfigurationImpl  (abstract)              config/config/ConfigurationImpl.h:144
    │
    ├──► OksConfiguration        (backend "oksconfig")   ── reads XML files directly
    │        │
    │        │  new OksQuery(cl, query)   oksconfig/src/OksConfiguration.cpp:705
    │        │  cl->execute_query(qe)     oksconfig/src/OksConfiguration.cpp:711
    │        ▼
    │    OksClass::execute_query()         oks/src/query.cpp:431
    │        │
    │        ▼
    │    OksObject::SatisfiesQueryExpression()  oks/src/query.cpp:630
    │        (backed by OksKernel: schema, data, Git)     oks/oks/kernel.h
    │
    └──► RdbConfiguration        (backend "rdbconfig")   ── CORBA to a running RDB server
```

**Confidence: Confirmed** for every arrow, with the citations given in §4–§9.

### Backend selection is a connection string

`config::Configuration`'s constructor parses `<backend>:<spec>`, then loads
`lib<backend>.so` and calls `_<backend>_creator_`:

> `config/src/Configuration.cpp:119–154`
> ```cpp
> m_impl_name = m_impl_spec.substr(0, idx);
> std::string plugin_name  = std::string("lib") + m_impl_name + ".so";
> std::string impl_creator = std::string("_") + m_impl_name + "_creator_";
> m_shlib_h = dlopen(plugin_name.c_str(), RTLD_LAZY | RTLD_GLOBAL);
> ... dlsym(m_shlib_h, impl_creator.c_str());
> ```

The two creators exist:

- `oksconfig/src/OksConfiguration.cpp:30` — `extern "C" ConfigurationImpl * _oksconfig_creator_(const std::string& spec, Configuration * db)`
- `rdbconfig/src/RdbConfiguration.cpp:28` — `extern "C" ConfigurationImpl * _rdbconfig_creator_(...)`

If no connection string is given, `TDAQ_DB` is consulted
(`config/src/Configuration.cpp:104`).

**What this proves:** the choice between "read OKS XML files myself" (`oksconfig`) and "ask
the running RDB server" (`rdbconfig`) is a *runtime string*, not a compile-time decision.
That is the single most useful lever the MCP has, and it is why the same query text can be
aimed at either a live partition or a checked-out historical revision.
**Confidence: Confirmed.**

## 3. Component responsibility table

| Component | Package | Responsibility, as evidenced | Key citation |
|---|---|---|---|
| `config::Configuration` | `config` | Backend-neutral façade; object/class access; schema introspection; version access; commit/rollback. Passes `query` through untouched. | `config/config/Configuration.h:698` |
| `ConfigurationImpl` | `config` | Abstract backend contract; declares the `get(class, objects, query, ...)` that backends must implement. | `config/config/ConfigurationImpl.h:144` |
| `OksConfiguration` | `oksconfig` | OKS backend. **Builds and runs `OksQuery`.** Owns an `OksKernel`. | `oksconfig/src/OksConfiguration.cpp:693–729` |
| `ROksConfiguration` | `oksconfig` | Variant of the OKS backend holding an explicit `m_schema_file` / `m_data_file` pair. | `oksconfig/oksconfig/ROksConfiguration.h:19–33` |
| `RdbConfiguration` | `rdbconfig` | Remote backend; talks to the RDB server of a **running partition**. | `rdbconfig/src/RdbConfiguration.cpp:28` |
| `OksKernel` | `oks` | Loads/saves schema and data XML; owns classes and objects; **drives Git** for repository checkout/update/commit/tag/log/diff. | `oks/oks/kernel.h:604`, `:1586–1700` |
| `OksClass` | `oks` | Schema for one class (attributes, relationships, inheritance) **and** `execute_query()`. | `oks/oks/class.h:851` |
| `OksObject` | `oks` | One instance; attribute/relationship read **and write**; `SatisfiesQueryExpression()`. | `oks/oks/object.h`, `oks/src/query.cpp:630` |
| `OksQuery` | `oks` | Query parse tree + schema validation at construction. Execution is read-only. | `oks/oks/query.h:33`, `oks/src/query.cpp:182` |
| DAL | `dal` | Typed C++/Java accessors generated over the schema, plus the **core schema XML** and `get_config_version()`. | `dal/data/schema/core.schema.xml`, `dal/src/algorithms.cpp:3292` |
| `webdaq` | tdaq-common | HTTP/JSON **client** for the Information Service; small read-only `oks::` helper. | `tdaq-common:webdaq/webdaq/webdaq-curl.hpp:235–251` |
| `webis_server` | `webis_server` | HTTP/JSON **server**; its OKS endpoint proxies to `rdbconfig` for a live partition. | `webis_server/src/oks_handler.cpp:265–305` |

## 4. A1 — Complete configuration access workflow

**Question.** What is the complete workflow from an application to a query result?

**Repository finding.** For the OKS-file path, the workflow is:

1. **Kernel construction and (optionally) repository checkout.** `OksKernel`'s constructor
   reads `TDAQ_DB_VERSION`, parses it as `param:value`, creates a temporary user repository
   directory, and checks the OKS Git repository out at that revision.
   > `oks/src/kernel.cpp:925–958` —
   > ```cpp
   > if (!version) version = getenv("TDAQ_DB_VERSION");
   > parse_config_version(version, param, val);
   > std::string tmp_dirname = OksKernel::create_user_repository_dir();
   > set_user_repository_root(tmp_dirname);
   > k_checkout_repository(param, val, branch_name);
   > ```
2. **Schema and data loading.** `load_schema()` / `load_data()` populate `OksClass` and
   `OksObject` instances (`oks/oks/kernel.h:561` documents the method set).
3. **Query construction, schema-validated.** `new OksQuery(cl, query)` parses the string
   *against the class* — see A3 and document `04`.
4. **Execution.** `OksClass::execute_query()` walks candidate objects (or an index) and
   collects matches.
5. **Result presentation.** Results are `OksObject*`; through `config` they are wrapped as
   `ConfigObject`, and through the Python binding as `config.ConfigObject`.

**Confidence: Confirmed** for steps 1–5 as *mechanism*.

**Missing information.** The workflow above is the *software* workflow. The **operational**
workflow — how a shifter identifies which run and which revision to ask for — is not
implemented in this release. See document `03`.

**Implication for the MCP prototype.** Steps 1–4 are exactly the operations the MCP must
orchestrate, and every one of them is reachable from Python (document `05`). Step 1 is the
one that makes historical access possible at all, and it is driven by a single environment
variable plus a `git` binary.

## 5. A2 — Exact relationships between the named components

**Repository finding.** The prompt's candidate chain is **substantially correct for this
release, with two corrections**: there is no distinct `OksConfiguration` layer *between*
`oksconfig` and `OksKernel` (`OksConfiguration` **is** the oksconfig backend class), and
`WebDAQ` is not in this chain at all.

Established relationships:

| Relationship | Established? | Evidence |
|---|---|---|
| `config::Configuration` → `ConfigurationImpl` | Yes | `config/src/Configuration.cpp:147` (`dlsym` creator returns a `ConfigurationImpl*`) |
| `ConfigurationImpl` ← `OksConfiguration` | Yes | `oksconfig/src/OksConfiguration.cpp:30` |
| `OksConfiguration` → `OksKernel` | Yes | `OksConfiguration` holds `m_kernel`, used at `oksconfig/src/OksConfiguration.cpp:695` (`m_kernel->find_class(class_name)`) |
| `OksConfiguration` → `OksQuery` | **Yes** | `oksconfig/src/OksConfiguration.cpp:705` |
| `OksQuery` → `OksClass::execute_query` | Yes | `oksconfig/src/OksConfiguration.cpp:711`; `oks/src/query.cpp:431` |
| DAL → `config::Configuration` | Yes | DAL accessors are generated over `config`; `dal/dal/util.h` and `dal/src/algorithms.cpp` operate on `Configuration&` |
| DAL → `OksQuery` | **No** | See A3 |
| `webdaq` → OKS kernel | **No** | `webdaq` is an HTTP client; it reaches OKS only via `webis_server` (§9) |

**Confidence: Confirmed.**

## 6. A3 — Does DAL or `config::Configuration` internally use `OksQuery`?

**Repository finding.** **`config::Configuration` does not construct `OksQuery`; `oksconfig`
does.** DAL does not construct `OksQuery` either — it forwards an optional query string to
`config`.

**Evidence.**

`config` declares the query as an opaque string and never parses it:

> `config/config/Configuration.h:698`
> ```cpp
> void get(const std::string& class_name, std::vector<ConfigObject>& objects,
>          const std::string& query = "", unsigned long rlevel = 0,
>          const std::vector<std::string> * rclasses = nullptr);
> ```

The template DAL accessor forwards the same string:

> `config/config/Configuration.h:1780–1786`
> ```cpp
> Configuration::_get(std::vector<const T*>& result, bool init_children, bool init_object,
>                     const std::string& query, ...)
>   { ... get(T::s_class_name, objs, query, rlevel, rclasses); ... }
> ```

`oksconfig` is where the string becomes a query object:

> `oksconfig/src/OksConfiguration.cpp:693–712`
> ```cpp
> void OksConfiguration::get(const std::string& class_name, std::vector<ConfigObject>& objects,
>                            const std::string& query, ...)
> {
>   if(OksClass * cl = m_kernel->find_class(class_name)) {
>     objects.clear();
>     OksObject::List * objs = 0;
>     if(query.empty()) {
>       objs = cl->create_list_of_all_objects();
>     } else {
>       std::unique_ptr<OksQuery> qe(new OksQuery(cl, query.c_str()));
>       if(qe->good() == false) { ... throw daq::config::Generic(... "bad query syntax ..."); }
>       objs = cl->execute_query(qe.get());
>     }
> ```

**What this proves, precisely.** Three things that matter for the MCP:

- An **empty** query is not "a query that matches everything" — it takes a different code
  path (`create_list_of_all_objects()`). The MCP should treat "no filter" as a distinct
  case rather than synthesising a tautological query.
- A **bad** query is rejected *before* execution and surfaces as
  `daq::config::Generic("bad query syntax ... in scope of class ...")` — a usable
  validation signal, and it names the class scope.
- The query is **scoped to one class**. There is no cross-class "SELECT ... FROM" form; the
  class is a separate argument. Any NL-to-query design must produce **(class, query)**, not
  a query alone.

**Confidence: Confirmed.**

**Value of generating OksQuery directly.** Because `oksconfig` is the only place the string
is interpreted, generating OksQuery text is equivalent in power to whatever the C++ API can
express through `get()`. Nothing is lost by going through the string interface — this is
the same path the C++ and Java APIs use.

## 7. A4 — What does `config::Configuration` actually understand about OKS?

**Repository finding.** `config::Configuration` is **primarily a generic configuration
interface**, but it is *not* OKS-agnostic: it carries an OKS-shaped schema model and an
OKS-Git-shaped version model.

**Evidence for "generic".**
- The query string is opaque (§6).
- Backends are interchangeable plugins (§2); `rdbconfig` is not file-based OKS at all.

**Evidence for "OKS-shaped anyway".**
- `config/config/Schema.h` defines `daq::config::class_t`, `attribute_t`, `relationship_t` —
  the OKS meta-model (used by `webis_server/src/oks_handler.cpp:299–302`).
- `config/config/ConfigVersion.h:47–52` documents the version id as **a Git SHA**:
  > "The version unique ID is a repository hash (GIT SHA)."
  A truly backend-neutral API would not name Git.

**Confidence: Confirmed** (both halves).

**Implication for the MCP prototype.** The MCP can rely on `config`-level schema
introspection (`class_t`/`attribute_t`/`relationship_t`, and their Python equivalents)
rather than parsing schema XML. See document `07`.

## 8. A5 — Does WebDAQ exist, and how does it interact with OKS?

**Repository finding.** A package named exactly `WebDAQ` **does not exist**. What exists is:

| Thing | Where | What it is |
|---|---|---|
| `webdaq` | **tdaq-common**, pin `a6a461b6…` | Stand-alone HTTP/JSON **client library** (curl + nlohmann/json) for the Information Service |
| `webis_server` | tdaq, pin `75dbfcf7…` | The HTTP/JSON **server** it talks to |
| `webdbe`, `webemon` | tdaq | Other web packages, not examined in depth here |

**`webdaq` is an IS client, and says so.**

> `tdaq-common:webdaq/README.md:1–6` — "# Stand-alone HTTP based interface for ATLAS TDAQ
> Information Service … a stand-alone library depending only on curl and nlohmann/json to
> read and write data from and to the Information Service of the ATLAS TDAQ system."

It is configured by `TDAQ_WEBDAQ_BASE`, pointing at a `webis_server`
(`tdaq-common:webdaq/README.md:26–32`).

**Its OKS surface is exactly two read-only calls.**

> `tdaq-common:webdaq/webdaq/webdaq-curl.hpp:235–251`
> ```cpp
> namespace oks {
>     /// Retrieve TDAQ OKS object as JSON object
>     bool get(CURL *handle, const std::string& partition, const std::string& class_name,
>              const std::string& name, nlohmann::json& result);
>     /// List TDAQ OKS objects as JSON object
>     bool list(CURL *handle, const std::string& partition, const std::string& class_name,
>               nlohmann::json& results);
> }
> ```
> `tdaq-common:webdaq/src/webdaq-curl.cpp:471,479` — the URLs are
> `"<partition>/oks/<class>/<name>?format=compact"` and `"<partition>/oks/<class>?format=json"`.

**Server side: it proxies to a live partition's RDB server, with no query support.**

> `webis_server/src/oks_handler.cpp:275–286`
> ```cpp
> Configuration db((partition == "initial" ? "rdbconfig:RDB_INITIAL@" : "rdbconfig:RDB@") + partition);
> ...
> } else if(name.empty()) { // we ask for a list of objects
>     std::vector<ConfigObject> objs;
>     db.get(class_, objs);        // <-- no query argument
> ```

**What this proves.** Four limits, all Confirmed:

1. The HTTP OKS interface is **read-only** (`get`/`list` only).
2. It **cannot take an OksQuery** — `db.get(class_, objs)` is called without the query
   parameter that `Configuration::get` offers.
3. It is bound to a **live, named, running partition** via `rdbconfig:RDB@<partition>`.
4. It offers **no revision or version parameter** — the URL grammar
   (`webis_server/src/oks_handler.cpp:15–29`) is `/…/<partition>/oks/<class>/<name>` and
   has no slot for one.

**Confidence: Confirmed.**

**Implication for the MCP prototype.** The HTTP path cannot serve this project: it drops
exactly the two capabilities the project is about — arbitrary queries and historical
revisions. This is a repository fact, not a preference.

## 9. A6 — Which external access interfaces actually exist in this release?

| Interface | Exists | Query support | Historical support | Evidence |
|---|---|---|---|---|
| C++ `config::Configuration` | Yes | Yes (`query` arg) | Yes (via `OksKernel` checkout / `get_versions`) | `config/config/Configuration.h:698,1283` |
| **Python (Boost.Python)** | **Yes** | **Yes** (`get_objs(class, query)`) | See document `05` | `config/src/python/config.cpp`, `config/python/config/Configuration.py:117` |
| Java (JNI) | Yes | Yes (`config/jsrc/config/Query.java`) | Not examined here | `config/jsrc/config/` |
| CLI `oks_dump` | Yes | **Yes** — takes a query string | Yes, via `TDAQ_DB_VERSION` | `oks/bin/oks_dump.cpp:263–266` |
| CLI `config_dump`, `config_export_schema`, `config_export_data` | Yes | Partly | — | `config/bin/` |
| HTTP (`webdaq` ⇄ `webis_server`) | Yes | **No** | **No** | §8 |
| GUI `dbe` | Yes | — (editor; see document `04`) | — | `dbe` pin `3dd750d2…` |

**Confidence: Confirmed** for existence and query support. **"Officially supported" is a
separate claim** and is *not* established by any of this — see document `05` §E.

## 10. Call graph (query path, verified)

```
config.Configuration.get_objs(class, query)      config/python/config/Configuration.py:117
    └─ super().get_objs(...)                     Boost.Python: config/src/python/config.cpp
        └─ config::Configuration::get(class, objects, query, ...)
                                                 config/config/Configuration.h:698
            └─ ConfigurationImpl::get(...)       config/config/ConfigurationImpl.h:144   [virtual]
                └─ OksConfiguration::get(...)    oksconfig/src/OksConfiguration.cpp:693
                    ├─ OksKernel::find_class()   oksconfig/src/OksConfiguration.cpp:695
                    ├─ new OksQuery(cl, query)   oksconfig/src/OksConfiguration.cpp:705
                    │    └─ OksQuery::create_expression()   oks/src/query.cpp:182
                    │         ├─ OksClass::find_attribute()     oks/src/query.cpp:379
                    │         ├─ OksClass::find_relationship()  oks/src/query.cpp:341
                    │         └─ OksKernel::find_class()        oks/src/query.cpp:363
                    └─ OksClass::execute_query(qe)              oks/src/query.cpp:431
                        ├─ OksIndex::find_all()  (indexed fast path)  oks/src/query.cpp:452,478
                        └─ OksObject::SatisfiesQueryExpression()      oks/src/query.cpp:630
```

## 11. DAL analysis

**Repository finding.** DAL in this release is (a) generated typed accessors over `config`,
(b) the **authoritative core schema XML**, and (c) a set of algorithms — including the one
that reads and writes the *configuration version in use by a partition*.

- Core schema: `dal/data/schema/core.schema.xml`, 753 lines, 83 classes including
  `Partition`, `Segment`, `OnlineSegment`, `Application`, `Computer`, `Resource`,
  `RunControlApplication`, `TriggerConfiguration`. (Document `07` analyses it.)
- `dal/data/is/oks-version.schema.xml` defines an **IS** class `ConfigVersion`:
  > "The class is used to store GIT version of the OKS database used for given partition."
  > attribute `Version`: "OKS GIT SHA key used for given partition".
- `dal/src/algorithms.cpp:3289–3327` implements `daq::core::get_config_version(partition)`,
  reading IS object `RunParams.ConfigVersion`, falling back to `TDAQ_DB_VERSION`.

**DAL does not use `OksQuery`.** Searched `dal/` for `OksQuery`, `execute_query`: no hits.
**Confidence: Confirmed.**

## 12. `config::Configuration` analysis

Beyond §6–§7, the API surface relevant here:

- Object access: `get(class, id, object, ...)`, `get(class, objects, query, ...)`,
  `get(obj_from, query, objects, ...)` — the last is the **path query** form
  (`config/config/Configuration.h:716`), matching OKS `path-to` (document `04`).
- Schema: `get_class_info()`, `superclasses()` (used by `webis_server/src/oks_handler.cpp:281`).
- Versions: `get_versions(since, until, QueryType, skip_irrelevant)` — documented
  *"Access historical versions"* — and `get_changes()`
  (`config/config/Configuration.h:1258–1283`).
- Mutation: `commit(log_message, credentials)`, `set_commit_credentials()`, rollback
  (`config/config/Configuration.h:1203–1223`) — analysed in document `04`.

## 13. `OksKernel` analysis

`OksKernel` is the component that makes historical access possible. Its constructor already
accepts a version:

> `oks/oks/kernel.h:604`
> ```cpp
> OksKernel(bool silence_mode = false, bool verbose_mode = false, bool profiling_mode = false,
>           bool allow_repository = true, const char * version = nullptr,
>           std::string branch_name = "");
> ```

and it exposes a Git-shaped repository API (`oks/oks/kernel.h:1586–1700+`):
`commit_repository()`, `update_repository(param, val, update_type)` with
`param ∈ {"tag","date","hash"}`, `tag_repository()`, `get_repository_versions()`,
`get_repository_versions_diff()`, `get_repository_version()`, plus the
`OksRepositoryVersion` record (`m_commit_hash`, `m_user`, `m_date`, `m_comment`, `m_files`)
at `oks/oks/kernel.h:516–531`.

Full analysis in document `03`; Git mechanics in document `06`.

## 14. `OksQuery` analysis

Summarised here, detailed in document `04`.

- Grammar keywords are string constants at `oks/src/query.cpp:15–31`:
  `or`, `and`, `not`, `some`, `this`, `all`, `object-id`, and comparators
  `=`, `!=`, `~=`, `<=`, `>=`, `<`, `>`, plus `path-to`, `direct`, `nested`.
- Expression types (`oks/oks/query.h:51–58`): comparator, relationship, not, and, or.
- **Parsing is schema-validated** (`oks/src/query.cpp:341,363,379`).
- **Execution does not mutate**: `OksClass::execute_query()` only reads and collects
  (`oks/src/query.cpp:431–535`).

## 15. Confirmed vs inferred

**Confirmed**
- The `config` → `oksconfig` → `oks` layering, by call trace (§10).
- `oksconfig` is where `OksQuery` is built and executed (§6).
- Backends are `dlopen` plugins chosen by connection string (§2).
- `webdaq`/`webis_server` expose OKS read-only, without query or revision (§8).
- `config` version identity is a Git SHA (§7).
- A Boost.Python binding exists and exposes a query parameter (§9, document `05`).

**Strongly indicated**
- `oksconfig` (files) vs `rdbconfig` (live server) is the intended
  historical-vs-operational split. Indicated by `rdbconfig:RDB@<partition>` being used
  *only* for live partitions (`webis_server/src/oks_handler.cpp:275`) while the Git/version
  machinery sits entirely in `oks`/`config`. No document in the release states this split
  as a rule.

**Not established from the new-release repository**
- Which of these interfaces is *officially supported* for external consumers. Nothing in
  the release declares a support policy.
- Whether `webdbe` or `webemon` add OKS capabilities beyond `webis_server` — not examined
  in depth.

## 16. Unknowns

1. Support status of the Python binding (existence ≠ endorsement).
2. Whether `rdbconfig` can be pointed at a historical revision at all, or only at a live
   partition. Searched `rdbconfig/` for version/revision parameters; the connection spec is
   `RDB@<partition>`. **Not established from the new-release repository.**
3. Whether `webis_server`'s OKS endpoint is deployed in production or is a convenience for
   monitoring. `etc/systemd/system/webis@.service` shows it is *deployable*; that is not
   proof of production use.

## 17. Evidence index

| File | Symbols / lines used |
|---|---|
| `config/config/Configuration.h` | `get()` :698, :716; `_get()` :1780–1786; versions :1258–1283; commit :1203–1223 |
| `config/config/ConfigurationImpl.h` | `get(...)` pure virtual :140–148, :178 |
| `config/config/ConfigVersion.h` | `daq::config::Version`, `QueryType` :33–37, id-is-SHA :47–52 |
| `config/src/Configuration.cpp` | plugin load :104, :119–154 |
| `config/python/config/Configuration.py` | `get_objs` :117; `attributes`/`relations`/`superclasses`/`subclasses`/`classes` :137–211 |
| `config/src/python/config.cpp` | Boost.Python module header :1–20 |
| `oksconfig/src/OksConfiguration.cpp` | `_oksconfig_creator_` :30; `get()` :693–729 (query :705, execute :711) |
| `oksconfig/oksconfig/ROksConfiguration.h` | `m_schema_file`, `m_data_file` :19–33 |
| `rdbconfig/src/RdbConfiguration.cpp` | `_rdbconfig_creator_` :28 |
| `oks/oks/query.h` | `OksQuery` :33; `QueryType` :51–58; keywords :62–77; `QueryPath` :~390 |
| `oks/src/query.cpp` | keywords :15–31; `create_expression` :182–425; `execute_query` :431–535; `SatisfiesQueryExpression` :630 |
| `oks/oks/kernel.h` | ctor :604; `OksRepositoryVersion` :516–531; repository API :1586–1700 |
| `oks/src/kernel.cpp` | `get_repository_root` :330–373; `parse_config_version` :757; ctor version handling :925–958; `k_checkout_repository` :5937–5998 |
| `oks/bin/oks_dump.cpp` | query execution :263–266 |
| `dal/data/schema/core.schema.xml` | DTD :6–78; 83 classes |
| `dal/data/is/oks-version.schema.xml` | IS class `ConfigVersion` |
| `dal/src/algorithms.cpp` | `get_config_version` :3292–3327; `set_config_version` :3330+ |
| `webis_server/src/oks_handler.cpp` | URL grammar :15–29; handler :265–305 |
| `tdaq-common:webdaq/webdaq/webdaq-curl.hpp` | `oks::get`/`oks::list` :235–251 |
| `tdaq-common:webdaq/src/webdaq-curl.cpp` | endpoint URLs :463–481 |
| `tdaq-common:webdaq/README.md` | purpose :1–6; `TDAQ_WEBDAQ_BASE` :26–32 |
