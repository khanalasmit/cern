# 08 — Schema Retrieval for Text-to-OksQuery (new release: `tdaq-13-00-00`)

Rules: `docs/investigation/tdaq-13-00-00/00_investigation_rules.md`.
Paths relative to `Materials/tdaq-cmake-tdaq-13-00-00/`.

**Read this document's two halves separately.** §2–§5 are **repository facts** — what the
implementation requires for a query to be valid. §6–§8 are **engineering choices** that the
repository does not decide and does not endorse.

---

## 1. Executive summary

To generate a valid OksQuery, a model needs three things, and only the first two come from
the schema:

1. **Class and member vocabulary** — which classes exist, and per class which attributes and
   relationships, with types, ranges, cardinality and multi-valuedness. Fully available as
   structured data (document `07` §8 G2).
2. **The relationship graph** — because a query may nest into a relationship, and the nested
   sub-expression is validated against the *target class*
   (`oks/src/query.cpp:363`).
3. **The query grammar** — which is **not** in the schema. It is in the parser, and it has
   two properties an LLM will very likely get wrong:
   - the mandatory top-level prefix **`( this|all ( … ) )`**;
   - the comparator operand order **`(attribute value operator)`**.

The strongest engineering conclusion the repository supports is not about retrieval strategy
at all — it is that **validation is free and exact**. `OksQuery(cl, text)` + `good()` runs
the same parser that execution uses, checking every class, attribute, relationship and
operator against the loaded schema (document `04` §2.3). A generate-and-validate loop is
therefore cheap and reliable, which materially reduces how much schema must be retrieved
up front.

## 2. Required information to generate a valid OksQuery

### 2.1 The grammar (repository fact, from the parser)

**Top-level form — mandatory:**

> `oks/src/query.cpp:127–137`
> ```cpp
> if(s.substr(0, p) == OksQuery::ALL_SUBCLASSES)   p_sub_classes = true;
> else if(s.substr(0, p) == OksQuery::THIS_CLASS)  p_sub_classes = false;
> else { Oks::error_msg(fname) << ... "the first token must be \'"<< OksQuery::ALL_SUBCLASSES
>          << "\' or \'"<< OksQuery::THIS_CLASS << "\'\n"; return; }
> ```

```
query      ::= "(" ("this" | "all") "(" expression ")" ")"
```

`this` = search the named class only; `all` = include subclasses.

**Expression forms** (`oks/src/query.cpp:182–425`):

```
expression ::= "(" attribute value comparator ")"          -- note the order
             | "(" "object-id" value comparator ")"
             | "(" relationship ("some"|"all") "(" expression ")" ")"
             | "(" "not" "(" expression ")" ")"
             | "(" "and" "(" expr ")" "(" expr ")" ... ")"   -- two or more
             | "(" "or"  "(" expr ")" "(" expr ")" ... ")"   -- two or more

comparator ::= "=" | "!=" | "~=" | "<=" | ">=" | "<" | ">"
```

Sources: keywords `oks/src/query.cpp:15–31`; `and`/`or` arity check `:280–288`; `not` arity
check `:312–316`; relationship form `:339–376`; comparator form `:377–420`; tokenisation and
quoting (`"`, `'`, `` ` ``) `:208–228`; bracket matching `:231–257`.

A worked example taken from the release itself — `config`'s own Python code:

> `config/python/config/Configuration.py:563–564` — `'(this (object-id \"\" !=))'`
> — "every object of this class whose object-id is not empty".

**A separate path-query form** exists (`path-to` / `direct` / `nested`,
`oks/oks/query.h:~340–400`), reached through
`Configuration::get(obj_from, query, objects, ...)` (`config/config/Configuration.h:716`).
It is out of scope for a first prototype.

**Confidence: Confirmed.**

### 2.2 The schema facts (repository facts)

Per document `07` §8 G2, all available from `daq::config::class_t`:

| Needed for | Field |
|---|---|
| class name; `this` vs `all` decision | `p_name`, `p_subclasses`, `p_superclasses` |
| attribute name | `attribute_t::p_name` |
| value literal type and format | `p_type` (17 types), `p_int_format` |
| legal values / bounds | `p_range` (UML syntax) |
| list semantics | `p_is_multi_value` |
| nullability | `p_is_not_null` |
| relationship name | `relationship_t::p_name` |
| target class for nesting | `relationship_t::p_type` |
| `some` vs `all` sensibility | `relationship_t::p_cardinality` |
| grounding NL terms in domain meaning | `p_description` on class, attribute, relationship |

## 3. Three levels of validity

The prompt requires these be kept distinct. The implementation distinguishes them too:

| Level | Definition | Enforced where | Failure mode |
|---|---|---|---|
| **Syntactically valid** | Balanced brackets; correct `this`/`all` prefix; correct arity for `and`/`or`/`not`; a recognised comparator | `OksQuery` ctor `oks/src/query.cpp:113–176`; `create_expression` bracket/arity checks `:231–257, :280–288, :312–316`; comparator lookup `:392–401, :415–417` | `good() == false` |
| **Schema-valid** | Every class, attribute and relationship named exists on the class in scope; relationship target class exists | `create_expression` — `find_attribute` `:379`, `find_relationship` `:341`, `find_class` `:363` | `good() == false`, with a message naming the class |
| **Semantically meaningful** | The query expresses what the user actually asked — right class, right partition, right revision, sensible comparison | **Nowhere** | Silently wrong answers |

**The first two are checked by the library at zero cost. The third is entirely the MCP's
problem** — and it is where the real risk lies, because a schema-valid query against the
wrong revision or the wrong `Partition` returns a confident, wrong result.

A third, structural check runs at execution: `OksQueryExpression::CheckSyntax()`
(`oks/src/query.cpp:441–444, :543–620`).

**Confidence: Confirmed.**

## 4. Evaluating the prompt's proposed representation

The prompt proposes:

```
Class
├── attributes {name, type, multiplicity}
├── relationships {target, relationship type}
└── inheritance
```

**Assessment against the implementation: necessary but not sufficient.** Missing items that
the evidence shows are needed:

| Missing | Why it is needed | Evidence |
|---|---|---|
| **`range`** | Enum attributes have their legal values only in `range`; a comparison against an invalid enum is schema-valid but meaningless | `Schema.h:56`; `oks/oks/attribute.h:235`, enum helpers `:487–541` |
| **`int_format`** | Integer literals may be hex/oct/dec; the value is parsed with `SetValues(second.c_str(), a)` against the attribute | `Schema.h:57`; `oks/src/query.cpp:407` |
| **`is_not_null`** | Determines whether a null test is meaningful | `Schema.h:58` |
| **`description`** | The bridge from natural language to schema names; without it, mapping "how many trigger applications" onto class names is guesswork | `Schema.h:61, :119, :158` |
| **`is_abstract`** | Abstract classes have no objects; a query on one returns nothing | `Schema.h:159` |
| **Cardinality**, not just "relationship type" | Drives `some` vs `all` and whether a result is a list | `Schema.h:117, :103–108` |
| **Subclasses** (not only superclasses) | Drives the `this` vs `all` prefix decision | `Schema.h:160–161` |
| **The grammar itself** | Not in the schema at all (§2.1) | `oks/src/query.cpp` |

Recommended per-class representation for the LLM (an **engineering proposal**):

```
class <name>  [abstract?]                        # p_name, p_abstract
  description: <text>                            # p_description
  superclasses: [...]   subclasses: [...]        # p_superclasses, p_subclasses
  attributes:
    <name> : <type> [multi] [not-null] [format]  # p_name, p_type, p_is_multi_value,
             range=<range>  default=<v>          #   p_is_not_null, p_int_format, p_range
             -- <description>
  relationships:
    <name> -> <target class>  <cardinality> [composite]
             -- <description>
```

## 5. Versioning: configuration revision → schema revision

**Repository finding. The mapping is guaranteed by construction, because there is only one
revision.** Schema and data are files in one Git repository, checked out together at one
tag/hash/date (document `03` §7, document `07` §9).

**Therefore:**
- **Guaranteed:** the schema in effect for a configuration revision **is** the schema at that
  Git revision. There is no separate schema version to resolve.
- **Confirmed:** the schema **can** differ between revisions — OKS supports schema evolution
  (`oks/README.md:3`) and the kernel tracks modified schema files
  (`oks/oks/kernel.h:1283–1300`).
- **Not established from the new-release repository:** how often it changes in practice.

**Consequence, and it is a hard requirement, not a preference:** schema retrieved for the LLM
**must come from the same checkout as the data being queried**. A cached "current" schema
used against a 2018 revision can produce queries that are schema-valid today and invalid — or
worse, silently different in meaning — then.

**Confidence: Confirmed.**

## 6. Retrieval strategy — engineering choices, not repository facts

**The repository does not recommend any retrieval algorithm — it contains no LLM- or
retrieval-related code at all.**

*What was searched:* all 220 checked-out packages (`*.cpp`, `*.h`, `*.py`, `*.md`) for
`embedding`, `vector search`, `semantic search`, `rag`, `llm`, `language model`; plus
`config`, `oks` and `dal` documentation for guidance on presenting schema to a consumer.

*Result:* `vector search`, `semantic search`, `rag` and `language model` — **zero matches**.
The apparent `llm` and `embedding` matches are false positives and were checked individually:
`llm` occurs only inside unrelated identifiers (`FullModeBuilder`, `IsFullMode`,
`ScrollMgr`, `PollManager`, …), and `embedding` occurs in three files that concern
**embedding the Python interpreter in C++** (`config/src/python/embedding.cpp`,
`omniPy/examples/embed/embed.py`, `ers2idl/ers2idl/ers2idl.h`) — not vector embeddings.

**Not established from the new-release repository.** Any retrieval-strategy statement in this
document is therefore an engineering proposal and must never be cited as a repository fact.

What follows is therefore **engineering discussion**, labelled as such, constrained by the
facts above.

### 6.1 The size question decides the strategy

The decisive input is how many classes a real ATLAS configuration exposes. Known:
`core.schema.xml` has **83 classes** (document `07` §7), and the release ships 103 schema
files. The production total is **Not established from the new-release repository**.

- If the loaded schema is on the order of a few hundred classes with short descriptions, the
  **whole schema plausibly fits in a modern context window**, and retrieval is unnecessary.
- If it is much larger, selection becomes necessary.

**This should be measured before any retrieval machinery is built** — it is one call to
`Configuration.classes()` against a real configuration. Building a vector index before
measuring would be premature.

### 6.2 Options, if selection proves necessary

| Strategy | Fit to this problem | Note |
|---|---|---|
| **Exact / keyword** | Strong. Class and attribute names are identifiers; users often name them nearly exactly ("RunControlApplication") | Cheap, debuggable, no extra infrastructure |
| **Semantic / vector** | Helps when the user's words differ from schema names; `p_description` gives real text to embed | Adds infrastructure and a staleness problem: an index must be **per revision** (§5) |
| **Hybrid** | Keyword first, semantic fallback | Reasonable end state |
| **Graph expansion** | *Not optional* — once a class is selected, its relationship targets must be pulled in too, or nested queries cannot be formed (`oks/src/query.cpp:363`) | Follows from the implementation |

**Recommendation for a six-week prototype:** start with **no retrieval** — send the full
class list plus full detail for the handful of classes selected by exact/keyword match, then
expand one relationship hop. Add semantic retrieval only if measurement shows it is needed.
**Labelled: engineering proposal.**

### 6.3 Why generate-and-validate lowers the stakes

Because `OksQuery(cl, text)` + `good()` is an exact, schema-aware, side-effect-free validator
(document `04` §2.3), an imperfect first attempt is cheap to detect and correct. The error
messages name the offending element and the class scope
(`oks/src/query.cpp:341–349, :379–387`), so they can be fed back to the model. This is a
**repository-supported** advantage and it argues for a simple retrieval strategy plus a
validation loop, rather than elaborate up-front retrieval.

## 7. H1–H5

### H1 — Supplying relevant schema information to an LLM

**Finding.** Retrieve through `Configuration.attributes()/relations()/superclasses()/subclasses()/classes()`
on the same `Configuration` used for the query (document `07` §8 G4), render per §4, and
include the grammar of §2.1 as fixed instructions.
**Confidence:** the *availability* is Confirmed; the *rendering* is an engineering proposal.

### H2 — Exact/keyword vs semantic vs hybrid

**Not established from the new-release repository** — the repository expresses no preference
(§6). As an engineering choice: keyword-first, measure, add semantic only if needed (§6.2).

### H3 — Schema representation needed by the LLM

Per §4: the prompt's three fields plus `range`, `int_format`, `is_not_null`, `is_abstract`,
`description`, cardinality and subclasses. **Confidence: Confirmed** that these fields exist
and are needed for validity; the layout is a proposal.

### H4 — Relationship representation for semantically valid queries

**Finding.** A relationship must carry **name**, **target class** and **cardinality**, and
the target class's own members must be retrievable, because the nested expression is parsed
*in the scope of the target class*:

> `oks/src/query.cpp:363–376`
> ```cpp
> OksClass *relc = c->get_kernel()->find_class(r->get_type());
> if(!relc) { ... }
> OksQueryExpression *qe2 = create_expression(relc, third);
> ```

So relationship representation is not decoration — it determines which names are legal one
level down. **Confidence: Confirmed.**

### H5 — Schema consistency across revisions

**Finding.** Guaranteed to be consistent *within* a revision; **not** guaranteed *across*
revisions; the matching historical revision **must** be used. §5.
**Confidence: Confirmed.**

## 8. Prototype recommendation

1. Resolve run → revision (document `03`), check out, open `Configuration`.
2. From that same object, retrieve the class list; select candidate classes by keyword match
   on names and descriptions; expand one relationship hop.
3. Render as §4, with the §2.1 grammar as fixed instruction text.
4. Generate `(class, query)`.
5. **Validate with the real parser** — construct the query and check `good()`; on failure,
   return the parser's message to the model and retry, bounded.
6. Execute, serialise, answer.

## 9. Explicit assumptions

- That a real configuration's schema is small enough to enumerate classes cheaply.
  **Untested** — measure first (§6.1).
- That `p_description` is populated well enough in production schemas to help NL mapping.
  `core.schema.xml` does carry descriptions, but coverage across all packages was not audited.
- That an LLM can reliably produce the `( this|all ( … ) )` prefix and reversed operand order
  given explicit instruction plus a validation loop. **Untested; this is the single largest
  technical risk in the query-generation step.**

## 10. Unknowns

1. Number of classes in a production configuration (§6.1).
2. Description coverage in production schemas.
3. `p_range` grammar beyond the docstring example (document `07` §11).
4. Whether `class_t::p_attributes` includes inherited attributes (document `07` §11).
5. Regex semantics for `~=` (document `04` §12) — affects any generated regex.
6. `uid`-typed attributes through `config` (document `07` §4).

## 11. Evidence index

| File | Symbols / lines |
|---|---|
| `oks/src/query.cpp` | keywords :15–31; ctor and `this`/`all` prefix :85–176 (check :127–137); `create_expression` :182–425; tokenising/quotes :208–228; brackets :231–257; and/or arity :280–288; not arity :312–316; relationship + target-class scope :339–376 (`find_class` :363); comparator + operand order :377–420; comparator table :392–401; `SetValues` :407; `CheckSyntax` :441–444, :543–620 |
| `oks/oks/query.h` | expression classes :134–300; `QueryPath` :~340–400 |
| `config/config/Schema.h` | `type_t` :20–37; `int_format_t` :42–47; `attribute_t` :52–61; `cardinality_t` :103–108; `relationship_t` :113–119; `class_t` :155–163 |
| `config/config/Configuration.h` | `get(class, objects, query, ...)` :698; path query :716 |
| `config/python/config/Configuration.py` | schema methods :137–211; internal OKS query example :563–564 |
| `oks/oks/kernel.h` | modified schema files :1283–1300 |
| `oks/oks/attribute.h` | `get_range` :235; enum helpers :487–541 |
| `oks/README.md` | schema evolution :3 |
| `dal/data/schema/core.schema.xml` | DTD :6–78; 83 classes |
