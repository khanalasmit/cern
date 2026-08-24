# 09 — Natural Language to OksQuery Pipeline (new release: `tdaq-13-00-00`)

Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Paths relative to `Materials/tdaq-cmake-tdaq-13-00-00/`.

---

## 1. Executive summary

Mapping the proposed pipeline onto the release gives a clear split. **Six of the ten stages
already exist as working code; four must be built.** Nothing in the "must build" column is
architecturally hard — the hard parts (query parsing, schema-aware validation, execution,
revision checkout) are the ones that already exist.

| # | Stage | Status | Where it lives |
|---|---|---|---|
| 1 | Natural language input | **Build** (MCP) | — |
| 2 | Intent / request interpretation | **Build** (LLM) | — |
| 3 | Historical configuration resolution | **Partly exists** | Revision *checkout* exists (`oks`); run→revision *lookup* must be built |
| 4 | Relevant schema retrieval | **Exists** (selection logic to build) | `Configuration.attributes()` etc. |
| 5 | OksQuery generation | **Build** (LLM) | — |
| 6 | OksQuery validation | **Exists** | `OksQuery` ctor + `good()` |
| 7 | Configuration loading | **Exists** | `OksKernel` / `oksconfig` |
| 8 | OksQuery execution | **Exists** | `OksClass::execute_query()` |
| 9 | Result serialization | **Partly exists** | JSON pattern exists in `webis_server`; not reusable as a library |
| 10 | Natural-language answer | **Build** (LLM) | — |

The single most valuable existing asset is **stage 6**: validation is performed by the same
parser that executes the query, against the same loaded schema, with no side effects
(document `04` §2.3). This makes the LLM's output checkable exactly, not heuristically.

## 2. Existing repository pipeline

There is no NL pipeline in the release. What exists is the machine-facing half:

```
(caller supplies class + query string)
        │
        ▼
config::Configuration::get(class, objects, query)     config/config/Configuration.h:698
        ▼
OksConfiguration::get(...)                            oksconfig/src/OksConfiguration.cpp:693
        ├── m_kernel->find_class(class_name)          :695
        ├── new OksQuery(cl, query)  → validate       :705   (good() checked :706)
        └── cl->execute_query(qe)                     :711
                ▼
        OksObject::List → ConfigObject vector         :719-723
```

*What was searched for pre-existing NL/query-generation components:* all 220 packages for
LLM/retrieval terms (document `08` §6) — **none**. Also searched for a run-number-keyed
configuration lookup (document `03` §6) — **none**.

**Confidence: Confirmed.**

## 3. Existing vs new components, stage by stage

### Stage 3 — Historical configuration resolution: **partly exists**

| Sub-step | Status | Evidence |
|---|---|---|
| run → revision **lookup** | **Build** | Written by `rn` (`rn/src/lib.cpp:251–274`), but nothing reads it back (document `03` §4) |
| revision → checkout | **Exists** | `TDAQ_DB_VERSION` + `k_checkout_repository()` (`oks/src/kernel.cpp:930–958, :5937`) |
| listing revisions | **Exists** | `Configuration::get_versions(since, until, QueryType, skip_irrelevant)` (`config/config/Configuration.h:1283`) |
| revision provenance (author/date/comment/files) | **Exists** | `OksRepositoryVersion` (`oks/oks/kernel.h:516–531`) |

Two resolution routes are available to build (document `03` §4): the derivable Git tag
`r<run>@<partition>`, or the run-number database column `CONFIGVERSION`.

### Stage 4 — Schema retrieval: **exists**

`Configuration.classes()/attributes()/relations()/superclasses()/subclasses()`
(`config/python/config/Configuration.py:137–211`) over
`daq::config::class_t` (`config/config/Schema.h:155–163`). Only the *selection* logic is new
(document `08`).

### Stage 6 — Validation: **exists, and is exact**

> `oksconfig/src/OksConfiguration.cpp:705–710`
> ```cpp
> std::unique_ptr<OksQuery> qe(new OksQuery(cl, query.c_str()));
> if(qe->good() == false) {
>   std::ostringstream text;
>   text << "bad query syntax \"" << query << "\" in scope of class \"" << class_name << '\"';
>   throw daq::config::Generic( ERS_HERE, text.str().c_str());
> }
> ```

Checks class/attribute/relationship existence and comparator validity
(`oks/src/query.cpp:341, :363, :379, :415`). **Confidence: Confirmed.**

### Stage 8 — Execution: **exists, read-only**

`OksClass::execute_query()` (`oks/src/query.cpp:431–535`), `const`, no mutation
(document `04` §2.4).

### Stage 9 — Result serialization: **partly exists**

The release demonstrates OKS→JSON, but **inside a server binary, not as a reusable library**:

> `webis_server/src/oks_handler.cpp:292–303`
> ```cpp
> result[0] = obj.UID();
> result[1] = obj.class_name();
> auto cl = db.get_class_info(obj.class_name());
> for(auto& attr : cl.p_attributes)  result[2][attr.p_name] = get_oks_attr(obj, attr);
> for(auto& rel  : cl.p_relationships) result[3][rel.p_name] = get_oks_rel(obj, rel);
> ```

with per-type conversion helpers `get_oks_attr()` (:33–237) and `get_oks_rel()` (:238–264).

**What this proves.** The *pattern* — iterate `class_t::p_attributes`/`p_relationships`,
convert per type — is demonstrated and can be reproduced in Python from `ConfigObject` plus
the schema methods. But the code itself is a positional-array JSON encoding
(`result[0..3]`) inside an HTTP handler, not a reusable serializer.
**Confidence: Confirmed** that a reusable serializer must be written.

`config_export_data` (`config/bin/config_export_data.cpp`) also exports data, format not
examined.

## 4. Proposed MCP pipeline

```
 Natural language question
     │
     ▼
 [1] MCP server: parse intent                                       NEW
     │  extract: run number / time range, partition, subject
     ▼
 [2] Resolve run → (config name, revision)                          NEW
     │  tag "r<run>@<partition>"  OR  rn DB column CONFIGVERSION      (doc 03)
     ▼
 [3] Open configuration at that revision                            EXISTS
     │  os.environ["TDAQ_DB_VERSION"] = "tag:..." ; Configuration("oksconfig:<CONFIGNAME>")
     ▼
 [4] Retrieve schema for candidate classes                          EXISTS (+ selection NEW)
     │  classes(), attributes(), relations(), subclasses()
     ▼
 [5] LLM generates (class_name, oks_query)                          NEW
     │  grammar: ( this|all ( <attr> <value> <op> ) )                 (doc 08 §2.1)
     ▼
 [6] Validate                                                       EXISTS
     │  get_objs(class, query) raises on bad syntax; retry loop       NEW
     ▼
 [7] Execute                                                        EXISTS
     │  get_objs → list[ConfigObject]
     ▼
 [8] Serialize to structured JSON                                   NEW (pattern exists)
     ▼
 [9] LLM composes the answer, citing run, revision SHA, class, query NEW
```

## 5. Validation flow

Three gates, only one of which the project must build:

| Gate | Catches | Provided by |
|---|---|---|
| **Pre-flight (proposed)** | class name not in `classes()`; attribute not in `attributes(class)` | build — cheap, gives better model feedback than a raw parser error |
| **Parser** | syntax, arity, unknown attribute/relationship/comparator, unknown target class | **exists** — `OksQuery` + `good()` |
| **Semantic** | right class, right partition, right revision, sensible comparison | **nobody** — see §7 |

The recommended loop: generate → validate with the real parser → on failure feed the parser's
message (which names the element and the class scope) back to the model → retry, bounded.
This is supported by the fact that validation is free and side-effect-free.

## 6. Error handling

Error styles the MCP must handle, all Confirmed:

| Source | Style | Evidence |
|---|---|---|
| `OksQuery` string parsing | **status flag** — `good()` false, message to `Oks::error_msg` | `oks/src/query.cpp:85, :113–176` |
| `oksconfig` wrapping it | **exception** `daq::config::Generic` | `oksconfig/src/OksConfiguration.cpp:706–710` |
| Class not found | **exception** `daq::config::NotFound` | `oksconfig/src/OksConfiguration.cpp:726` |
| Query execution failure | **exception** `oks::QueryFailed` | `oks/src/query.cpp:501–504` |
| `QueryPath` parsing | **exception** `oks::bad_query_syntax` | `oks/oks/query.h:~305–320` |
| Repository checkout failure | **exception** `oks::RepositoryOperationFailed` | `oks/src/kernel.cpp:5941`, `oks/oks/kernel.h:114–124` |
| Python layer | all of the above surface as `RuntimeError` | `config/src/python/config.cpp:36–38` — `PyErr_SetString(PyExc_RuntimeError, ...)` |

**Note the loss of type information at the Python boundary.** A single translator is
registered for the whole `daq::config` exception hierarchy:

> `config/src/python/config.cpp:363`
> ```cpp
> register_exception_translator<daq::config::Exception>(&translate_ers_issue);
> ```
> `config/src/python/config.cpp:35–38`
> ```cpp
> static void translate_ers_issue(ers::Issue const& e)
> {
>   PyErr_SetString(PyExc_RuntimeError, make_ers_message(e).c_str());
> }
> ```

So **every** `daq::config` error — bad query syntax, class not found, checkout failure —
arrives in Python as a plain `RuntimeError` whose only distinguishing feature is its message
text. An MCP cannot branch on exception type; it must match on message text, or pre-validate
(§5). **Confidence: Confirmed.** This is a concrete limitation and it is the main argument
for the pre-flight gate.

## 7. I1–I4

### I1 — Suitability of the proposed pipeline

**Suitable, with one structural correction.** The pipeline as drawn treats "OksQuery
generation" as the central act; the evidence shows the **output must be a pair
`(class_name, query)`**, because the class is a separate argument at every layer
(`Configuration::get(class_name, objects, query)`, `OksQuery(cl, str)`) and the query is
parsed *in the scope of that class* (document `02` §6). A pipeline that generates a query
string alone cannot be executed.

Secondly, "Historical configuration resolution" is drawn as one box but is **two** facts —
*which configuration* (`CONFIGNAME`) and *which revision* (`CONFIGVERSION`) — plus the
partition (document `03` §10).

**Confidence: Confirmed** for both corrections.

### I2 — Existing TDAQ components vs components this project must implement

**Exists (reuse):** revision checkout; configuration loading; schema introspection; query
parsing; **schema-aware query validation**; query execution; revision listing with
provenance; Python bindings for all of it.

**Must implement:** run→revision lookup; schema selection/rendering; NL→(class, query)
generation; validation retry loop; result serialization; answer composition; caching of
checkouts (document `06` §4).

**Confidence: Confirmed.**

### I3 — Should the LLM generate only OksQuery, or also run/configuration/revision?

**Repository-grounded answer: the LLM should generate the query and *name* the run and
partition; it must not generate the revision.**

The reasoning rests on repository boundaries, not on generic LLM practice:

- The **revision is a lookup, not a judgement.** It is a Git SHA recorded by `rn`
  (`rn/src/lib.cpp:255`) or a tag derived arithmetically as `r<run>@<partition>`
  (`rn/src/lib.cpp:104`). There is exactly one right answer, obtainable deterministically. A
  generated SHA would be a hallucination with no validation gate — nothing would reject a
  well-formed but wrong SHA; `oks-checkout.sh` would happily check out a real-but-wrong
  commit, or fail opaquely.
- The **configuration name is also a lookup** — `CONFIGNAME` from the run row
  (`rn/src/lib.cpp:274`).
- The **query is genuinely a generation task**, and — critically — it is the **only** stage
  with an exact validator (§5). Generation is appropriate where verification exists.
- The **run number and partition** are what the user actually says ("run 452123",
  "the ATLAS partition"), so extracting them is an NL task.

So: LLM produces `{run, partition, class_name, query}`; deterministic code produces
`{revision, config_name}`.

**Confidence: Strongly indicated** — an engineering conclusion resting on the Confirmed facts
that revision is recorded data with no validator, while queries have one.

### I4 — Existing reusable query-validation mechanism, and where validation should occur

**Exists**: `OksQuery(cl, query)` + `good()`, run inside `oksconfig`
(`oksconfig/src/OksConfiguration.cpp:705–710`), reachable from Python by calling
`get_objs()` and catching `RuntimeError`.

**Where validation should occur:** in the MCP server, *before* answering, using the real
parser — with an optional cheap pre-flight check against `classes()`/`attributes()` to
produce better model feedback and to work around the exception-type flattening (§6).

Validation must run **against the historical revision's schema**, not a cached current one
(document `08` §5).

**Confidence: Confirmed** for the mechanism; the placement is an engineering proposal.

## 8. Responsibility boundaries

| Concern | Owner | Why |
|---|---|---|
| Understanding the question | LLM | NL task |
| Run/partition extraction | LLM | stated by the user |
| Revision + config-name resolution | **MCP code, deterministically** | recorded data; no validator for a guess (§I3) |
| Checkout and loading | **OKS library** | already implemented |
| Schema selection and rendering | MCP code | new |
| Query generation | LLM | has an exact validator |
| Query validation | **OKS library**, invoked by MCP | exact and free |
| Execution | **OKS library** | read-only |
| Serialization | MCP code | pattern exists, library does not |
| Answer + provenance citation | LLM, from MCP-supplied facts | must cite run, SHA, class, query |

## 9. Unknowns

1. Run→revision reader API — none exists (document `03` §14).
2. Result-set sizes for realistic queries; whether truncation/pagination is needed. No
   benchmarks in the release.
3. Whether `config_export_data`'s format is reusable for serialization — not examined.
4. Whether `webis_server`'s positional JSON encoding is a convention worth matching, or an
   internal detail. **Not established from the new-release repository.**
5. Reliability of LLM adherence to the `( this|all ( … ) )` grammar (document `08` §9).

## 10. Evidence index

| File | Symbols / lines |
|---|---|
| `oksconfig/src/OksConfiguration.cpp` | `get()` :693–729; validation :705–710; execution :711; result copy :719–723; `NotFound` :726 |
| `oks/src/query.cpp` | ctor :85, :113–176; schema checks :341, :363, :379, :415; `execute_query` :431–535; `QueryFailed` :501–504 |
| `oks/oks/query.h` | `bad_query_syntax`, `QueryPath` :~305–400 |
| `oks/oks/kernel.h` | `RepositoryOperationFailed` :114–124; `OksRepositoryVersion` :516–531 |
| `oks/src/kernel.cpp` | checkout failure :5941; ctor/version :930–958; `k_checkout_repository` :5937 |
| `config/config/Configuration.h` | `get()` :698; `get_versions()` :1283 |
| `config/config/Schema.h` | `class_t` :155–163 |
| `config/src/python/config.cpp` | ERS→`RuntimeError` :22–38; `get_objs` :161–170 |
| `config/python/config/Configuration.py` | schema methods :137–211; `get_objs` :117 |
| `webis_server/src/oks_handler.cpp` | `get_oks_attr` :33–237; `get_oks_rel` :238–264; JSON assembly :292–303 |
| `rn/src/lib.cpp` | tag construction :104; `CONFIGVERSION` :255; `CONFIGNAME` :274 |
