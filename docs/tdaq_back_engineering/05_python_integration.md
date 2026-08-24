# 05 — Python, WebDAQ, Native C++, and the MCP Boundary (new release: `tdaq-13-00-00`)

Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Paths relative to `Materials/tdaq-cmake-tdaq-13-00-00/`, except `tdaq-common:` prefixes.

---

## 1. Executive summary

**An existing, built, tested Python binding already exposes everything a Text-to-OksQuery MCP
server needs: query execution with an OKS query string, and full schema introspection.**

> `config/python/config/Configuration.py:117`
> ```python
> def get_objs(self, class_name, query=''):
> ```

This is not a wrapper the project would have to write — it is shipped by the `config`
package, built as a CMake target, exercised by the package's own tests, and *used internally
by the package's own Python code*, which itself emits an OKS query string
(`config/python/config/Configuration.py:563–564`).

The other candidate paths do not compete:

- **WebDAQ/HTTP** cannot take a query and cannot select a revision (document `02` §8).
- **A new binding** would duplicate `pyconfig`.
- **CLI** (`oks_dump`) works and takes a query, but returns text meant for humans.

The recommendation is therefore: **Python MCP → existing `config` Python binding →
`oksconfig` → OKS**, with the historical revision passed **in the connection string**
(`oksconfig:<file>&version=tag:<tag>`, §3.3.1) — which, unlike the `TDAQ_DB_VERSION`
environment variable, is safe under concurrent requests.

The one thing the repository does **not** establish is whether this binding is *officially
supported for external consumers*. That distinction is maintained throughout §8.

## 2. WebDAQ

Fully analysed in document `02` §8. Summary of what exists:

| Item | Finding | Evidence |
|---|---|---|
| Package named `WebDAQ` in tdaq | Does not exist | `.gitmodules` (203 packages) |
| `webdaq` in tdaq-common | Exists — HTTP/JSON **client** library for the **Information Service** | `tdaq-common:webdaq/README.md:1–6` |
| Server | `webis_server` (libmicrohttpd + nlohmann/json) | `webis_server/src/` |
| OKS endpoints | `GET <partition>/oks/<class>` and `GET <partition>/oks/<class>/<name>` | `tdaq-common:webdaq/src/webdaq-curl.cpp:471,479` |
| Query support | **None** — server calls `db.get(class_, objs)` with no query | `webis_server/src/oks_handler.cpp:284` |
| Historical support | **None** — URL grammar has no revision slot; backend is `rdbconfig:RDB@<partition>` | `webis_server/src/oks_handler.cpp:15–29, :275` |
| Write support | **None** on the OKS path (`get`/`list` only) | `tdaq-common:webdaq/webdaq/webdaq-curl.hpp:235–251` |
| Authentication | `TDAQ_WEBDAQ_COOKIEFILE` for libcurl cookies | `tdaq-common:webdaq/README.md:36–37` |
| API specification | `webis_server/doc/openapi.yaml` exists | — |

**Confidence: Confirmed.** WebDAQ is a live-monitoring interface, not a configuration-history
interface.

## 3. Python bindings

### 3.1 Technology and build

**Boost.Python**, not pybind11 and not SWIG (for `config`):

> `config/src/python/config.cpp:1–8`
> ```cpp
> /**
>  * @file src/python/config.cpp
>  * @brief Boost.Python interface to the "config" namespace
>  */
> #include <boost/python.hpp>
> ```
> `config/CMakeLists.txt:18`
> ```cmake
> tdaq_add_library(pyconfig src/python/config.cpp LINK_LIBRARIES PRIVATE config Python::Development Boost::python)
> ```
> `config/CMakeLists.txt:22`
> ```cmake
> tdaq_add_python_package(config)
> ```

Release-wide survey (searched all 220 packages): `boost/python` appears in 10 files,
`Python.h` in 16, SWIG in 20, **`pybind11` in 0**. Python packaging is widespread —
`tdaq_add_python_package` is used by at least 20 packages including `config`, `dal`,
`PartitionMaker`, `ResourceManager`, `webis_server`.

**Confidence: Confirmed.**

### 3.2 The exposed API

Exported methods (`config/src/python/config.cpp:392, :442–447`):

```cpp
.def("get_objs",     &get_objs)
.def("attributes",   &attributes)
.def("relations",    &relations)
.def("superclasses", &superclasses)
.def("classes",      &classes)
```

**Query execution — the query string is passed straight through to C++:**

> `config/src/python/config.cpp:161–170`
> ```cpp
> static boost::python::list get_objs(python::ConfigurationPointer& conf,
>     const std::string& class_name, const std::string& query="")
> {
>   std::vector<ConfigObject> objs;
>   conf->get(class_name, objs, query);
>   boost::python::list retval;
>   for (unsigned i=0; i < objs.size(); ++i)
>     if(!objs[i].is_null()) retval.append(objs[i]);
>   return retval;
> }
> ```

`conf->get(class_name, objs, query)` is `config::Configuration::get()`
(`config/config/Configuration.h:698`) — the same entry point the C++ API uses, which reaches
`OksConfiguration::get()` and `new OksQuery(...)` (document `02` §6).

**Schema introspection is also exposed, and it is structured, not text:**

> `config/src/python/config.cpp:172–186` — `attributes()` builds a `boost::python::dict`
> from `daq::config::class_t::p_attributes`, filling per-attribute `properties["type"]`,
> `properties["range"]`, …

The Python-side wrappers with their documented signatures
(`config/python/config/Configuration.py`):

| Method | Line | Purpose |
|---|---|---|
| `get_objs(class_name, query='')` | :117 | **Query execution** — docstring: *"This is specific OKS query you may want to perform to reduce the returned subset."* |
| `attributes(class_name, all=False)` | :137 | direct or inherited attributes |
| `relations(class_name, all=False)` | :155 | direct or inherited relationships |
| `superclasses(class_name, all=False)` | :173 | inheritance upward |
| `subclasses(class_name, all=False)` | :191 | inheritance downward |
| `classes()` | :209 | all loaded classes |
| `get_obj(class_name, uid)` | :324 | single object |
| `get_dal` / `get_dals` / `get_all_dals` | :497–542 | typed DAL access |
| `get_includes` / `add_include` / `remove_include` | :240–271 | file structure |
| `create_obj`, `destroy_obj`, `create_db`, `add_dal`, `update_dal`, `destroy_dal` | :213–590 | **mutation** — see §7 |

### 3.3 Backend selection from Python

> `config/python/config/Configuration.py:52–68`
> ```python
> def __init__(self, connection='oksconfig:'):
>     """...
>     connection -- A connection string, in the form of <backend>:<database>
>     name, where <backend> may be set to be 'oksconfig' or 'rdbconfig' and
>     <database> is either the name of the database XML file (in the case of
>     'oksconfig') or the name of a database associated with an RDB server
>     (in the case of 'rdbconfig').
>     ...
>     If the parameter 'connection' is empty, the default is whatever is the
>     default for the config::Configuration C++ class, which at this time boils
>     down to look if TDAQ_DB is set and take that default.
>     """
> ```

**This is the decisive capability for the MCP.** From Python, one string chooses between
reading OKS XML files directly (`oksconfig:<file>`) and talking to a live partition
(`rdbconfig:RDB@<partition>`).

### 3.3.1 The revision can also go in the connection string

Historical access does **not** have to go through the `TDAQ_DB_VERSION` environment variable.
`oksconfig` parses an optional parameter section from the spec:

> `oksconfig/src/OksConfiguration.cpp:150, :191–202`
> ```cpp
> const char s_version_str[] = "version=";
> ...
> Oks::Tokenizer t(params, ";");
> while (!(token = t.next()).empty())
>   {
>     if (token == "norepo")                                   m_oks_kernel_no_repo = true;
>     else if (auto idx = token.find(s_version_str); idx == 0)  m_version = token.substr(sizeof(s_version_str)-1);
>   }
> m_kernel = new OksKernel(m_oks_kernel_silence, false, false, !m_oks_kernel_no_repo,
>                          m_version.empty() ? nullptr : m_version.c_str());
> ```

The spec grammar, from `OksConfiguration::open_db()` (`oksconfig/src/OksConfiguration.cpp:153–205`):

```
oksconfig:<file>[:<file>...][&<param>[;<param>...]]
    param ::= "norepo" | "version=" <tag|hash|date> ":" <value>
```

The `version=` value is handed straight to the `OksKernel` `version` constructor argument —
the same argument `TDAQ_DB_VERSION` feeds (`oks/oks/kernel.h:604`). So from Python:

```python
cfg = config.Configuration("oksconfig:atlas.data.xml&version=tag:r452123@ATLAS")
```

**Why this matters, concretely.** Environment variables are **process-global**. An MCP server
answering concurrent requests about *different runs* cannot safely mutate `os.environ` —
two requests would race. The connection-string form makes revision selection
**per-`Configuration` object**, so concurrent historical queries are safe, revision becomes a
function argument rather than ambient state, and the cache key is simply the connection
string.

**This is the recommended form**; the environment variable remains a working fallback.

**Confidence: Confirmed** that the parameter is parsed and reaches the kernel's version
argument. **Not established from the new-release repository:** whether `version=` is
documented or supported for external use — *searched:* `oksconfig/doc/RELEASE_NOTES.md` and
`oksconfig/CMakeLists.txt`; *missing:* any mention of the parameter. Added to §10.

**Confidence: Confirmed** (backend selection and revision parameter).

### 3.4 Evidence the binding is maintained, not vestigial

- It is built as a first-class CMake target (`config/CMakeLists.txt:18`).
- It has its own test suite: `config/python/tests/test_all.py`,
  `test_configuration.py`, `test_configobject.py`, `test_dal.py`, plus
  `config/test/pytest.sh` and a style check `config/test/pystyle.sh` wired in as a CTest
  (`config/CMakeLists.txt:30`).
- `config/python/tests/test_configuration.py` exercises the real API through
  `test01`–`test15`, including `db.get_objs("Dummy")` (:75).
- **`config`'s own Python code calls `get_objs` with an OKS query string:**
  > `config/python/config/Configuration.py:562–564`
  > ```python
  > for k in super(Configuration, self).get_objs(class_name,
  >                                              '(this (object-id \"\" !=))'):
  > ```
  This is the strongest available evidence that the Python query path works: the package
  depends on it internally.
- `dal` links `pyconfig` for its own Python helpers (`dal/CMakeLists.txt:21–26`) and ships
  Python CLI tools `dal_dump_app_config`, `dal_dump_apps` (`dal/CMakeLists.txt:64–68`).

**Confidence: Confirmed** that it is built, tested and internally depended upon.
**Support status: see §8.**

### 3.5 A grammar requirement the binding makes visible

The internal call above also reveals the **mandatory top-level query form**, which the
constructor enforces:

> `oks/src/query.cpp:127–137`
> ```cpp
> if(s.substr(0, p) == OksQuery::ALL_SUBCLASSES)      p_sub_classes = true;
> else if(s.substr(0, p) == OksQuery::THIS_CLASS)     p_sub_classes = false;
> else {
>   Oks::error_msg(fname) << "Can't parse query expression ...
>      "the first token must be \'"<< OksQuery::ALL_SUBCLASSES
>      << "\' or \'"<< OksQuery::THIS_CLASS << "\'\n";
>   return;
> }
> ```

So every query string must be **`( this|all ( <expression> ) )`** — `this` searches only the
named class, `all` includes subclasses. **Confidence: Confirmed.** Carried into document `08`.

## 4. Native C++

| Aspect | Finding | Evidence |
|---|---|---|
| Public headers | `config/config/*.h` (`Configuration.h`, `ConfigObject.h`, `Schema.h`, `ConfigVersion.h`), `oks/oks/*.h` (`kernel.h`, `class.h`, `object.h`, `query.h`, `attribute.h`, `relationship.h`) | package layout |
| Libraries | `config`, `pyconfig`, `oksconfig`, `rdbconfig`, `oks`, `daq-core-dal` | `*/CMakeLists.txt` |
| CMake targets | `tdaq_add_library(pyconfig ...)`, `tdaq_add_executable(config_dump ...)` etc. | `config/CMakeLists.txt:9–18` |
| Runtime environment | `TDAQ_DB`, `TDAQ_DB_REPOSITORY`, `TDAQ_DB_USER_REPOSITORY`, `TDAQ_DB_VERSION`, `TDAQ_DB_BRANCH`, `TDAQ_DB_DATA`, `TDAQ_DB_PATH`, `OKS_GIT_PROTOCOL`, `OKS_REPOSITORY_MAPPING_DIR` | `oks/src/kernel.cpp:337, :403, :932, :951, :2327–2339`; `config/src/Configuration.cpp:104, :312–314` |
| Runtime dependency on `git` | **Yes** — OKS shells out to `oks-*.sh`, which run `git` | `oks/src/kernel.cpp:5945`, `oks/scripts/*.sh` |
| Backend loading | `dlopen("lib<backend>.so")` | `config/src/Configuration.cpp:127–147` |

**Important operational consequence.** Because backends are `dlopen`'d and OKS shells out to
scripts, a working deployment needs `LD_LIBRARY_PATH` to find `liboksconfig.so` **and**
`PATH` to find `oks-checkout.sh` and `oks_git_repository`. This is a **TDAQ release
environment** requirement, not merely a "pip install". **Confidence: Confirmed** from the
mechanism; the exact setup procedure is **Not established from the new-release repository**
(searched `doc/BUILDING.md`, `doc/INSTALL.md`, which cover building, not runtime setup).

## 5. Existing executables and services

| Tool | Loads OKS | Takes a query | Structured output | Evidence |
|---|---|---|---|---|
| `oks_dump` | Yes | **Yes** | No — human-readable text | `oks/bin/oks_dump.cpp:262–270` |
| `config_dump` | Yes (via `config`) | Partly | No | `config/bin/config_dump.cpp` |
| `config_export_schema` | Yes | n/a | **Yes** — exports schema | `config/bin/config_export_schema.cpp` |
| `config_export_data` | Yes | n/a | Yes | `config/bin/config_export_data.cpp` |
| `dal_dump_apps`, `dal_dump_app_config` | Yes | No | No | `dal/CMakeLists.txt:64–65` |
| `oks_validate_repository` | Yes | No | Exit codes | `oks/bin/oks_validate_repository.cpp` |
| `webis_server` | Yes (via `rdbconfig`) | **No** | **Yes** — JSON | `webis_server/src/oks_handler.cpp` |
| RDB server (`rdb`) | Yes | Yes (via `rdbconfig`) | CORBA | package `rdb` |

**No existing executable both accepts an OksQuery and returns structured (JSON) results.**
`oks_dump` has the query but not the structure; `webis_server` has the structure but not the
query. **Confidence: Confirmed.** This gap is precisely what the MCP server fills.

## 6. Interface comparison

| Interface | Exists | Evidence | Query access | Historical access | Python integration | Limitations |
|---|---|---|---|---|---|---|
| **`config` Python binding (`pyconfig`)** | **Yes** | `config/CMakeLists.txt:18`; `config/python/config/Configuration.py:117` | **Yes** — `get_objs(class, query)` | **Yes** — `oksconfig:` + `TDAQ_DB_VERSION` | **Native** | Needs TDAQ release env; also exposes mutation; support status unstated |
| C++ `config::Configuration` | Yes | `config/config/Configuration.h:698` | Yes | Yes | via a new binding | Would duplicate `pyconfig` |
| Java binding | Yes | `config/jsrc/config/Query.java` | Yes | Unknown | No | Irrelevant to a Python MCP |
| CLI `oks_dump` | Yes | `oks/bin/oks_dump.cpp:262` | Yes | Yes (`TDAQ_DB_VERSION`) | subprocess + text parsing | Output not machine-readable; fragile |
| CLI `config_export_schema` | Yes | `config/bin/` | n/a | Yes | subprocess | Schema only |
| HTTP `webdaq`/`webis_server` | Yes | §2 | **No** | **No** | trivial (HTTP) | Cannot express the use case |
| RDB server via `rdbconfig` | Yes | `rdbconfig/src/RdbConfiguration.cpp:28` | Yes | **Unknown** | via `pyconfig` | Live partitions; needs IPC/CORBA; historical use not established |
| New pybind11/SWIG binding | No | — | — | — | — | Unnecessary given `pyconfig` |

## 7. E1–E6

### E1 — Does an existing WebDAQ interface cover historical access and read-only querying?

**No.** Read-only: yes. Querying: no. Historical: no. §2.
**Confidence: Confirmed.**

### E2 — Repository-evidenced advantages and limits of WebDAQ vs native C++

**Advantages of WebDAQ (evidenced):** no TDAQ release environment needed — it is
*"stand-alone … can be compiled as stand-alone software"* and depends only on curl and
nlohmann/json (`tdaq-common:webdaq/README.md:8–22`); returns JSON directly; trivially
callable from Python over HTTP.

**Limits (evidenced):** no query parameter; no revision parameter; bound to a live named
partition via `rdbconfig:RDB@<partition>`; only `get` and `list`. §2.

**Advantages of native/`pyconfig` (evidenced):** full query support; revision selection;
full schema introspection; structured Python objects.

**Limits (evidenced):** requires the TDAQ release environment, `dlopen`-able backends, and a
`git` binary on `PATH` (§4).

**Confidence: Confirmed** on both sides.

### E3 — Existing supported Python bindings and exposed APIs

**A Python binding exists and is substantial** — §3. Exposed: `get_objs` (with query),
`attributes`, `relations`, `superclasses`, `subclasses`, `classes`, object access, DAL
access, includes management, and mutation.

The word **"supported"** cannot be answered from the repository — see §8.
**Confidence: Confirmed** for existence and API surface;
**Not established from the new-release repository** for support status.

### E4 — Evidence for a new thin binding versus WebDAQ

Neither is indicated. The evidence points to a **third** option the prompt's list frames as
secondary: **use the existing binding**.

- Against a new binding: `pyconfig` already exposes the exact call needed
  (`config/src/python/config.cpp:161–170`), is built, tested, and internally relied upon
  (§3.4). A new binding would re-expose the same `Configuration::get()`.
- Against WebDAQ: it structurally cannot express query or revision (§2).

**Confidence: Strongly indicated** (this is an engineering judgement resting on Confirmed
facts, not a repository recommendation).

### E5 — Existing C++ executables/services that accept OksQuery and return results

`oks_dump` accepts a query and prints results (`oks/bin/oks_dump.cpp:262–270`). The RDB
server serves queries through `rdbconfig`. **No executable returns structured results for a
query** (§5). **Confidence: Confirmed.**

### E6 — Best first-prototype path based on release evidence

**Python MCP → `config` Python binding (`oksconfig:` backend) → `oksconfig` → `oks`**, with
the revision passed **in the connection string** —
`oksconfig:<config>&version=tag:r<run>@<partition>` (or `version=hash:<sha>`) — which is
concurrency-safe, unlike the `TDAQ_DB_VERSION` environment variable (§3.3.1).

Grounded in: the binding exposes query and schema (§3.2); backend and revision are both
strings (§3.3, document `03` §5); the query is validated by the same code that executes it
(document `04` §2.3); and no HTTP or CLI path offers query + revision + structure (§5, §6).

**Confidence: Strongly indicated** as an engineering recommendation.

## 8. "Technically possible" vs "demonstrated" vs "officially supported"

The prompt requires these be kept apart. For the recommended path:

| Claim | Verdict | Basis |
|---|---|---|
| **Technically possible** | **Yes** | The call chain is traced end to end (document `02` §10) |
| **Demonstrated as an existing interface** | **Yes** | Built target, own test-suite, and `config`'s own Python code issues an OKS query through it (§3.4) |
| **Officially supported** | **Not established from the new-release repository** | *Searched:* `config/README`(absent), `config/doc/RELEASE_NOTES.md`, `config/CMakeLists.txt`, `doc/BUILDING.md`, `doc/INSTALL.md`, superproject `README.md`, and every `.gitlab-ci.yml` in `config`. *Missing:* any statement of a support policy, API stability guarantee, or intended-audience declaration for **any** interface in this release — including the C++ one. Nothing declares support status, so the absence is not evidence against the Python binding specifically. |

**This is the single most important question to put to the TDAQ experts** (§10).

## 9. Recommended prototype boundary

```
   MCP client (LLM)
        │  MCP tools:  resolve_run · get_schema · validate_query · run_query
        ▼
   Python MCP server                                   ← NEW CODE
        │  Configuration(f"oksconfig:{config_name}&version=tag:r<run>@<partition>")
        │  (env-var TDAQ_DB_VERSION is an equivalent fallback)
        ▼
   config.Configuration  (pyconfig, Boost.Python)      ← EXISTS  config/python/config/Configuration.py:117
        │  get_objs(class, query) · classes() · attributes() · relations() · superclasses()
        ▼
   config::Configuration → OksConfiguration            ← EXISTS  oksconfig/src/OksConfiguration.cpp:693
        │  new OksQuery(cl, query); cl->execute_query(qe)
        ▼
   OksKernel  (checkout via oks-checkout.sh → git)     ← EXISTS  oks/src/kernel.cpp:5937
```

Everything below the MCP server exists. The prototype's new code is the MCP server itself.

## 10. Questions for TDAQ experts

1. **Is the `config` Python binding supported for external consumers**, and is `get_objs`'s
   signature stable across releases? (§8 — the repository is silent.)
2. Is there a **supported way to run OKS code outside the TDAQ release environment**, given
   the `dlopen` + `git`-on-`PATH` requirements (§4)?
3. Can `rdbconfig` be pointed at a **historical** revision, or is it live-only?
   (Not established — §6.)
4. Is `webis_server`'s OKS endpoint **deployed in production**, and would adding a
   query parameter to it be acceptable as an alternative to a Python service?
5. Is there an existing service that returns **structured** query results that we missed?
6. Is the `oksconfig` **`version=` connection parameter** (§3.3.1) documented and supported
   for external use? It is the cleanest historical-access route but appears undocumented.

## 11. Unknowns

1. Support status of every interface (§8).
2. Whether `rdbconfig` supports historical revisions (§6).
3. Runtime setup procedure for the TDAQ environment (§4).
4. Whether `webis_server`'s OpenAPI spec (`webis_server/doc/openapi.yaml`) documents OKS
   endpoints beyond those in `oks_handler.cpp` — the spec file was noted but not parsed.
   **Not established from the new-release repository.**
5. Performance of `get_objs` over a full ATLAS partition — no benchmarks in the release
   (`config/test/config_time_test.cpp` exists but was not run).

## 12. Evidence index

| File | Symbols / lines |
|---|---|
| `config/python/config/Configuration.py` | ctor/connection string :52–68; `get_objs` :117–135; `attributes` :137; `relations` :155; `superclasses` :173; `subclasses` :191; `classes` :209; includes :240–271; mutation :213–590; internal OKS query :562–564 |
| `config/src/python/config.cpp` | Boost.Python header :1–8; `get_objs` :161–170; `attributes` :172–186; exports :392, :442–447 |
| `config/CMakeLists.txt` | executables :9–11; `pyconfig` :18; python package :22; pystyle test :30 |
| `config/python/tests/test_configuration.py` | `test01`–`test15`; `get_objs` :75 |
| `config/config/Configuration.h` | `get()` :698 |
| `config/src/Configuration.cpp` | `TDAQ_DB` :104; plugin load :127–147; `TDAQ_DB_NAME`/`TDAQ_DB_DATA` :312–314 |
| `oks/src/query.cpp` | mandatory `this`/`all` prefix :127–137 |
| `oks/src/kernel.cpp` | env vars :337, :403, :932, :951, :2327–2339; `system()` script call :5945 |
| `oks/bin/oks_dump.cpp` | query execution :262–270 |
| `dal/CMakeLists.txt` | `pyconfig` link :21–26; python package :61–62; scripts :64–68 |
| `oksconfig/src/OksConfiguration.cpp` | `get()` :693–729 |
| `rdbconfig/src/RdbConfiguration.cpp` | creator :28 |
| `webis_server/src/oks_handler.cpp` | URL grammar :15–29; handler :265–305 (no-query `get` at :284) |
| `tdaq-common:webdaq/README.md` | purpose :1–6; stand-alone :8–22; cookies :36–37 |
| `tdaq-common:webdaq/webdaq/webdaq-curl.hpp` | `oks::get`/`oks::list` :235–251 |
