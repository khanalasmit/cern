# 07 — OKS Schema and XML (new release: `tdaq-13-00-00`)

Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Paths relative to `Materials/tdaq-cmake-tdaq-13-00-00/`.

---

## 1. Executive summary

**The authoritative, useful schema representation in this release is not the XML — it is the
in-memory model, exposed through two structured APIs.** The prompt warns against reasoning
"OKS stores schema in XML, therefore use XML". The evidence supports the opposite:

| Representation | Where | Structured? | Reachable from Python? |
|---|---|---|---|
| Schema **XML** files | `*.schema.xml`, 103 in-release | Text + a DTD | only by writing a parser |
| `OksClass` / `OksAttribute` / `OksRelationship` | `oks/oks/class.h`, `attribute.h`, `relationship.h` | **Yes** | via `config` |
| **`daq::config::class_t` / `attribute_t` / `relationship_t`** | `config/config/Schema.h` | **Yes** — plain structs | **Yes, directly** |

`config/config/Schema.h` is the decisive find. It is a complete, backend-neutral,
machine-readable description of a class — name, description, abstractness, direct
super/subclasses, all attributes and all relationships, each with types, ranges, cardinality,
multi-valuedness, nullability, defaults and human descriptions — and its structs carry
constructors annotated *"Default constructor for Python binding"*
(`config/config/Schema.h:77, :133, :174`).

So the MCP does not need to parse OKS XML. It can ask `config` for the schema and receive
typed data — in Python.

## 2. Schema architecture

```
*.schema.xml  ──parse──►  OksClass / OksAttribute / OksRelationship   (oks)
                                    │
                                    │  OksConfiguration::get(class_name, direct_only)
                                    ▼
                          daq::config::class_t                        (config)
                            ├── p_attributes    : vector<attribute_t>
                            ├── p_relationships : vector<relationship_t>
                            ├── p_superclasses  : vector<string>
                            └── p_subclasses    : vector<string>
                                    │
                                    │  Boost.Python
                                    ▼
                     Configuration.attributes() / relations()
                     / superclasses() / subclasses() / classes()
```

## 3. Schema vs data XML

Both are OKS XML, distinguished by their `oks-format` and root element.

**Schema files** — root `<oks-schema>`, `oks-format` fixed to `"schema"`:

> `dal/data/schema/core.schema.xml:6–14`
> ```xml
> <!DOCTYPE oks-schema [
>   <!ELEMENT oks-schema (info, (include)?, (comments)?, (class)+)>
>   <!ELEMENT info EMPTY>
>   <!ATTLIST info
>       ...
>       oks-format CDATA #FIXED "schema"
>       oks-version CDATA #REQUIRED
> ```

**Data files** — `*.data.xml`, referenced separately by the kernel
(`load_data()` vs `load_schema()`, `oks/oks/kernel.h:543, :552`) and separately by
`ROksConfiguration`, which holds `m_schema_file` and `m_data_file` as distinct members
(`oksconfig/oksconfig/ROksConfiguration.h:30–32`).

**Counts in this release** (excluding `test/`): **103** `*.schema.xml`, **219** `*.data.xml`.

**They share one Git revision** — one repository, one checkout (document `03` §7).

**Confidence: Confirmed.**

## 4. The schema DTD — the exact vocabulary

Every schema file embeds its own DTD, so the vocabulary is self-describing. From
`dal/data/schema/core.schema.xml:35–68`:

```xml
<!ELEMENT class (superclass | attribute | relationship | method)*>
<!ATTLIST class
    name CDATA #REQUIRED
    description CDATA ""
    is-abstract (yes|no) "no"
>
<!ELEMENT superclass EMPTY>
<!ATTLIST superclass name CDATA #REQUIRED>
<!ELEMENT attribute EMPTY>
<!ATTLIST attribute
    name CDATA #REQUIRED
    description CDATA ""
    type (bool|s8|u8|s16|u16|s32|u32|s64|u64|float|double|date|time|string|uid|enum|class) #REQUIRED
    range CDATA ""
    format (dec|hex|oct) "dec"
    is-multi-value (yes|no) "no"
    init-value CDATA ""
    is-not-null (yes|no) "no"
    ordered (yes|no) "no"
>
<!ELEMENT relationship EMPTY>
<!ATTLIST relationship
    name CDATA #REQUIRED
    description CDATA ""
    class-type CDATA #REQUIRED
    low-cc (zero|one) #REQUIRED
    high-cc (one|many) #REQUIRED
    is-composite (yes|no) #REQUIRED
    is-exclusive (yes|no) #REQUIRED
    is-dependent (yes|no) #REQUIRED
    ordered (yes|no) "no"
>
```

**What this proves.** The complete type vocabulary and every schema property an OksQuery
could reference are fixed and enumerable. Cardinality is expressed as the pair
(`low-cc` ∈ {zero, one}, `high-cc` ∈ {one, many}). **Confidence: Confirmed.**

**Note a discrepancy worth recording.** The DTD's attribute types include **`uid`**, but
`daq::config::type_t` (`config/config/Schema.h:20–37`) does **not** have a `uid` member — its
seventeen values are `bool`, `s8`…`u64`, `float`, `double`, `date`, `time`, `string`, `enum`,
`class`. So the `config`-level model is not a perfect superset of the XML vocabulary.
*What was searched:* `config/config/Schema.h` for `uid`. *What is missing:* how a `uid`
attribute surfaces through `config`. **Not established from the new-release repository.**

## 5. Loading mechanism

| Step | API | Evidence |
|---|---|---|
| Load a schema file | `OksKernel::load_schema()` | `oks/oks/kernel.h:543` |
| Load a data file | `OksKernel::load_data()` | `oks/oks/kernel.h:552` |
| Resolve includes | `OksKernel::get_includes(file, set, use_repository_name)` | `oks/oks/kernel.h:1016` |
| XML parsing | `oks/src/xml.cpp`, `oks/oks/xml.h` | package layout |
| Data reading | `oks/src/data.cpp` | package layout |
| Active file for new items | `set_active_schema()` / `set_active_data()` | `oks/oks/kernel.h:1228, :1504` |

Files may `include` other files (`<!ELEMENT include (file)+>`,
`core.schema.xml:22–26`), and include cycles are a checked error condition —
`oks_validate_repository` reports `__IncludesCircularDependencyError__`
(`oks/bin/oks_validate_repository.cpp:36, :190–195`).

**Confidence: Confirmed.**

## 6. Schema APIs

### 6.1 At the `oks` level

`OksClass` (`oks/oks/class.h`):

| Method | Line | Returns |
|---|---|---|
| `get_name()` | :367 | class name |
| `get_description()` | :372 | description |
| `all_attributes()` | :479 | `const std::list<OksAttribute*>*` — including inherited |
| `direct_attributes()` | :484 | direct only |
| `find_attribute(name)` | :496 | one attribute or null |
| `all_relationships()` | :589 | including inherited |
| `direct_relationships()` | :594 | direct only |
| `find_relationship(name)` | :606 | one relationship or null |
| `number_of_all_attributes()` etc. | :564–680 | counts |

`OksAttribute` (`oks/oks/attribute.h`): `get_name()` :167, `get_type()` :194,
`get_range()` :235, `get_format()` :314, `get_is_multi_values()` :365,
`get_init_value()` :388, `get_description()` :421, `get_is_no_null()` :442, plus enumeration
helpers `get_enum_index()` :487 and `get_enum_value()` :515–541.

`OksRelationship` (`oks/oks/relationship.h`): `get_name()` :167, `get_class_type()` :185,
`get_type()` :190, `get_description()` :210, `get_low_cardinality_constraint()` :232,
`get_high_cardinality_constraint()` :258, `get_is_composite()` :278, with
`str2card()`/`card2str()` :349–354.

### 6.2 At the `config` level — the structured representation

> `config/config/Schema.h:155–163`
> ```cpp
> struct class_t {
>   std::string p_name;                                  /*!< the class name */
>   std::string p_description;                           /*!< the description text of class */
>   bool p_abstract;                                     /*!< if true, the class is abstract and has no objects */
>   const std::vector<std::string> p_superclasses;       /*!< the names of direct superclasses */
>   const std::vector<std::string> p_subclasses;         /*!< the names of direct subclasses */
>   const std::vector<attribute_t> p_attributes;         /*!< the all attributes of the class */
>   const std::vector<relationship_t> p_relationships;   /*!< the all relationships of the class */
> ```
> `config/config/Schema.h:52–61`
> ```cpp
> struct attribute_t {
>   std::string p_name;
>   type_t p_type;
>   std::string p_range;           /*!< the attribute range in UML syntax (e.g.: "A,B,C..D,*..F,G..*" ...) */
>   int_format_t p_int_format;
>   bool p_is_not_null;
>   bool p_is_multi_value;
>   std::string p_default_value;
>   std::string p_description;
> ```
> `config/config/Schema.h:113–119`
> ```cpp
> struct relationship_t {
>   std::string p_name;
>   std::string p_type;           /*!< the relationship class type */
>   cardinality_t p_cardinality;
>   bool p_is_aggregation;        /*!< if true, the relationship is an aggregation (composite) ... */
>   std::string p_description;
> ```

Enumerations: `type_t` (17 values, `:20–37`), `int_format_t` (`:42–47`), and
`cardinality_t` — **`zero_or_one`, `zero_or_many`, `only_one`, `one_or_many`** (`:103–108`),
which flattens the XML's `low-cc`/`high-cc` pair into one value.

Conversion helpers `attribute_t::type(type_t)` (:93) and `format2str()` (:96) turn the enums
back into strings — directly useful for rendering schema to an LLM.

### 6.3 In Python

`Configuration.attributes()`, `relations()`, `superclasses()`, `subclasses()`, `classes()`
(`config/python/config/Configuration.py:137–211`), implemented over `class_t` in
`config/src/python/config.cpp:172–186`, which builds a dict of dicts with `type`, `range`
and further properties per attribute.

**The Python route requires no XML parsing at all. Confidence: Confirmed.**

### 6.4 Export tool

`config_export_schema` (`config/bin/config_export_schema.cpp`,
built at `config/CMakeLists.txt:11`) exports the schema — a batch route to the same
information.

## 7. DAL / generated representation

`dal` ships the **authoritative core schema** as XML and generated typed accessors over it:

- `dal/data/schema/core.schema.xml` — 753 lines, **83 classes**, including `Partition`,
  `Segment`, `OnlineSegment`, `Application`, `BaseApplication`, `Computer`, `ComputerSet`,
  `Resource`, `ResourceSet`, `ResourceSetAND`, `ResourceSetOR`, `RunControlApplication`,
  `TriggerConfiguration`, `Rack`, `Crate`, `Module`, `Network`, `Variable`, `Tag`.
- Generated headers: `dal/dal/app-config.h`, `application-config.h`, `seg-config.h`,
  `disabled-components.h`.
- `dal/data/is/oks-version.schema.xml` — the IS `ConfigVersion` class (document `03`).

**Does generated DAL contain schema information?** It contains the schema *as C++ types* —
useful for compiled code, not as data an LLM can read. The machine-readable form is
`class_t` (§6.2), not the generated headers. **Confidence: Confirmed.**

**Is `core.schema.xml` the whole schema?** **No.** It is the *core*; packages contribute
their own (103 schema files in-release, e.g. `ResourceManager`, `dqmf`, `siom`), and the
production configuration will include more. The set of classes available to a query is
whatever the loaded configuration includes — determined at runtime, not from `dal` alone.
**Confidence: Confirmed.**

## 8. G1–G5

### G1 — Authoritative schema location, and schema↔data relationship

**Repository finding.** The authoritative *content* is the schema XML in the OKS repository
(`dal/data/schema/core.schema.xml` plus per-package and configuration-specific files); the
authoritative *representation for programmatic use* is `daq::config::class_t`. Schema and
data are separate files, loaded by separate calls, sharing one Git revision.

**Confidence: Confirmed.**

### G2 — Does the schema provide what OksQuery generation needs?

**Yes — completely.** Mapping each requirement to a schema field:

| OksQuery needs | Provided by | Evidence |
|---|---|---|
| Valid class name | `class_t::p_name`, `Configuration.classes()` | `Schema.h:157` |
| Valid attribute name | `attribute_t::p_name` | `Schema.h:54` |
| Whether a value is type-compatible | `attribute_t::p_type` (17 types) | `Schema.h:55, :20–37` |
| Legal values for enums / bounds | `attribute_t::p_range` (UML syntax) | `Schema.h:56` |
| Integer literal format (hex/oct/dec) | `attribute_t::p_int_format` | `Schema.h:57` |
| Multi-value semantics | `attribute_t::p_is_multi_value` | `Schema.h:59` |
| Valid relationship name | `relationship_t::p_name` | `Schema.h:115` |
| Target class of a relationship (for nested queries) | `relationship_t::p_type` | `Schema.h:116` |
| Whether `some` or `all` is meaningful | `relationship_t::p_cardinality` | `Schema.h:117, :103–108` |
| Whether `this` or `all` (subclasses) is right | `class_t::p_subclasses`, `p_superclasses` | `Schema.h:160–161` |
| Human meaning, for LLM grounding | `p_description` on all three structs | `Schema.h:61, :119, :158` |

**Confidence: Confirmed.** The one thing the schema does *not* give is the **query grammar**
itself (operand order, the `this|all` prefix) — that comes from the parser
(document `04` §2.2, document `05` §3.5).

### G3 — Schema-inspection API vs manual XML parsing?

**A full inspection API exists at both levels, and in Python. Manual XML parsing is
unnecessary and would be a mistake** — it would re-implement include resolution, inheritance
flattening (`all_attributes()` vs `direct_attributes()`), and range parsing that the library
already performs.

**Confidence: Confirmed.**

### G4 — Evidence-backed schema source for retrieval

**`Configuration.attributes()/relations()/superclasses()/subclasses()/classes()` in Python,
against the same `Configuration` object used to run the query.**

Rationale from evidence: it is the same loaded schema the query parser validates against
(`oks/src/query.cpp:341, :363, :379`), so schema shown to the LLM and schema enforced on the
query cannot drift. Reading `core.schema.xml` from disk instead would risk exactly that
drift, because the loaded configuration includes more than `core`.

**Confidence: Strongly indicated** (engineering recommendation on Confirmed facts).

### G5 — Existing structured, machine-readable schema representation to reuse

**Yes: `daq::config::class_t` / `attribute_t` / `relationship_t`
(`config/config/Schema.h`), already surfaced as Python dicts.** The structs are explicitly
Python-binding-aware (`:77, :133, :174`).

**Confidence: Confirmed.**

## 9. Does the schema change across configuration revisions?

**It can, and the release is built to expect it.**

- Schema files live in the same Git repository as data, so a revision may change either
  (document `03` §7).
- `OksKernel` explicitly tracks schema files changed by external processes:
  `get_updated_repository_files(updated, added, removed)` (`oks/oks/kernel.h:1300`) and
  *"repository modified schema files"* (`oks/oks/kernel.h:1283–1285`).
- OKS advertises **"schema evolution, data migration"** as core features
  (`oks/README.md:3`).
- `get_repository_versions_diff(sha1, sha2)` returns the files that differ between two
  revisions (`oks/oks/kernel.h:1680`), which would include schema files.

**Confidence: Confirmed** that schema can differ between revisions.
**Not established from the new-release repository:** how *often* it changes in practice, or
whether ATLAS constrains schema changes to release boundaries. Expert question.

**Implication for the MCP prototype.** Schema shown to the LLM **must** come from the same
revision as the data being queried. Caching one global schema across revisions is incorrect.

## 10. Recommended schema source

For the prototype, in priority order:

1. **`Configuration` schema methods in Python**, on the same object used for the query
   (§8 G4). Structured, revision-correct, no parsing.
2. `config_export_schema` — for offline snapshots or debugging.
3. Raw `*.schema.xml` — **only** if the Python route proves unavailable; requires
   re-implementing includes and inheritance.

## 11. Unknowns

1. How a `uid`-typed attribute appears through `config` (§4).
2. The exact grammar of `p_range` beyond the docstring example
   `"A,B,C..D,*..F,G..*"` (`Schema.h:56`) — no parser for it was located in `config`.
   **Not established from the new-release repository.**
3. Whether `class_t::p_attributes` is genuinely *all* (inherited included) — the comment says
   *"the all attributes of the class"* (`Schema.h:162`) while `get_class_info()` takes a
   `direct_only` flag (`config/config/ConfigurationImpl.h:178`). The two must be reconciled
   experimentally. **Partially established.**
4. Whether the production configuration's schema differs materially from `core.schema.xml`.
   Not established — the production database is not in this release (document `01` §9).
5. Regex semantics for `~=` (document `04` §12).

## 12. Evidence index

| File | Symbols / lines |
|---|---|
| `config/config/Schema.h` | `type_t` :20–37; `int_format_t` :42–47; `attribute_t` :52–61, py-ctor :77, `type()` :93, `format2str()` :96; `cardinality_t` :103–108; `relationship_t` :113–119, py-ctor :133; `class_t` :155–163, py-ctor :174 |
| `config/config/ConfigurationImpl.h` | `get(class_name, direct_only)` :178 |
| `config/python/config/Configuration.py` | `attributes` :137; `relations` :155; `superclasses` :173; `subclasses` :191; `classes` :209 |
| `config/src/python/config.cpp` | `attributes()` dict build :172–186 |
| `config/bin/config_export_schema.cpp` | schema export tool |
| `oks/oks/class.h` | `get_name` :367; `get_description` :372; `all_attributes` :479; `direct_attributes` :484; `find_attribute` :496; `all_relationships` :589; `direct_relationships` :594; `find_relationship` :606; counts :564–680; `execute_query` :851 |
| `oks/oks/attribute.h` | `get_name` :167; `get_type` :194; `get_range` :235; `get_format` :314; `get_is_multi_values` :365; `get_init_value` :388; `get_description` :421; `get_is_no_null` :442; enum helpers :487–541 |
| `oks/oks/relationship.h` | `CardinalityConstraint` :105; `get_name` :167; `get_class_type` :185; `get_type` :190; `get_description` :210; low/high cc :232, :258; `get_is_composite` :278; `str2card`/`card2str` :349–354 |
| `oks/oks/kernel.h` | `load_schema`/`load_data` doc :543, :552; `get_includes` :1016; modified schema files :1283–1300; `set_active_schema` :1228; `set_active_data` :1504; versions diff :1680 |
| `oks/README.md` | schema evolution / data migration :3 |
| `dal/data/schema/core.schema.xml` | DTD :6–78 (class :35–40, attribute :42–55, relationship :56–67); 83 classes |
| `dal/data/is/oks-version.schema.xml` | IS class `ConfigVersion` |
| `oksconfig/oksconfig/ROksConfiguration.h` | `m_schema_file` / `m_data_file` :30–32 |
| `oks/bin/oks_validate_repository.cpp` | circular includes :36, :190–195 |
