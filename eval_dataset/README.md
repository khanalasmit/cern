# Evaluation dataset

Two generated files feed the translation pipeline and make its accuracy measurable.

| File | Role |
| --- | --- |
| [`oks_schema_corpus.xml`](oks_schema_corpus.xml) | The retrieval corpus the RAG indexer ingests: configuration schema, object data, and the OKS C++ API. |
| [`oks_eval_queries.jsonl`](oks_eval_queries.jsonl) | 144 shifter questions paired with their ground-truth `OksQuery`, gold IR, gold schema elements and expected result set. |

Supporting sources, all of which can be read on their own:

| File | Role |
| --- | --- |
| [`build_dataset.py`](build_dataset.py) | Regenerates both files. Fails the build if any gold query is invalid. |
| [`oks_model.py`](oks_model.py) | Schema/data loader plus a reference `OksQuery` evaluator, used to validate and execute the gold queries. |
| [`query_specs.py`](query_specs.py) | The curated question specs. This is the file to edit when adding rows. |
| [`oks_cpp_api.schema.xml`](oks_cpp_api.schema.xml) | The OKS C++ API surface written as an OKS schema. |

Rebuild after any change to `test_schema/`, `test_data/` or `query_specs.py`:

```bash
python eval_dataset/build_dataset.py
```

`--check` validates without writing anything, which is what a CI job should run.

---

## File 1 — `oks_schema_corpus.xml`

Same shape as `oks_scraped/oks_schema_examples.xml`, and a strict superset of it, so
it drops into `HybridIndexer.ingest_xml` with no code change:

```python
indexer = HybridIndexer()
indexer.ingest_xml("eval_dataset/oks_schema_corpus.xml")
```

70 `<example>` blocks:

| Kind | Count | Contents |
| --- | --- | --- |
| `configuration-schema` | 46 | Every `test_schema/xml/*.schema.xml`, one example per file, DOCTYPE and comments stripped. 454 classes. |
| `cpp-api-schema` | 1 | `OksKernel`, `OksClass`, `OksObject`, `OksQuery` and the rest of the API, as 22 OKS classes. |
| `configuration-data` | 18 | Every `test_data/**/*.data.xml`. 825 objects, so object ids and attribute values are retrievable, not just class definitions. |
| `curated-example` | 5 | The original hand-written tutorial/DAL examples, carried forward unchanged. |
| `grammar` | 1 | The S-expression grammar and its operand rules. |

Running the pipeline's own chunking over it yields **482 class chunks**.

Each `<example>` carries a `<caption>` written for semantic retrieval, plus `kind`,
`source` and a count attribute. The current indexer ignores those; the architecture in
[`../rag.md`](../rag.md) uses them as metadata filters.

### Why the C++ API is in the same corpus

Questions the agent gets split into two families. *"Which applications run on
lxplus001?"* needs the configuration schema. *"Which call executes a parsed query?"* or
*"how do I build an `(and ...)` expression programmatically?"* needs the API. Both are
answered from one index because the API is expressed in the same vocabulary: C++ data
members become `<attribute>`, associations become `<relationship>`, and every documented
public method becomes a `<method>` carrying its verbatim prototype — which is a legal
OKS schema element, not an invention (see the schema DTD in
`docs/OKS_Grammar_Query_CppAPI_Reference.pdf`, section 5).

---

## File 2 — `oks_eval_queries.jsonl`

One JSON object per line.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Stable row id, `OKSQ-001` … |
| `split` | string | `eval` for every row. See the leakage note below. |
| `difficulty` | string | `easy` \| `medium` \| `hard` |
| `question` | string | The shifter question, in plain English. |
| `target_class` | string | The class the query runs against. `OksQuery` carries no class; `oks_dump --class` supplies it. |
| `scope` | string | `all` (class + subclasses) or `this` (class only). |
| `constructs` | string[] | Grammar features exercised. This is the error-taxonomy axis. |
| `query_ir` | object \| null | The ground-truth intermediate representation. `null` for path queries. |
| `query_oks` | string | The ground-truth query, serialised by the same rules as `agent/serializer.py`. |
| `gold_schema_elements` | object | `{classes, attributes, relationships}` derived by walking the IR. This is M2's gold retrieval set. |
| `expected_object_ids` | string[] \| null | Sorted ids the query returns against `test_data`. `null` for path queries. |
| `expected_count` | int \| null | `len(expected_object_ids)`. |
| `ir_expressible` | bool | `false` for the 5 path-query rows the current IR cannot represent. |
| `scope_class_count` | int | Classes in scope: 1 + subclasses. Shows how much `all` widens the search. |
| `oks_dump_cmd` | string | Ready-to-run validation/execution command. |
| `note` | string | Why the query is shaped this way, and the mistake it guards against. |
| `source_file` | string | Schema file the target class comes from. |

### Composition

```
144 rows       easy 54    medium 51    hard 39
139 rows carry an expected result set (median 4 objects)
  5 rows are path queries, not expressible in the current IR
```

Constructs covered: all seven comparators, `this`/`all` scope, `and`/`or`/`not`
(including three-operand forms), `object-id`, `some`/`all` relationship quantifiers,
regex escaping, enum and multi-value attributes, empty-value comparisons, two- and
three-hop relationship chains, boolean structure nested *inside* a relationship, and
`path-to` with `direct`/`nested`.

### Every row is machine-checked

The build refuses to emit a row unless:

1. the target class exists;
2. every attribute resolves on the class it is used against, **including through
   relationships** — the nested expression of `("rel" some <expr>)` is typed by the
   relationship's `class-type`, not by the outer class;
3. every relationship resolves and its `class-type` is a known class;
4. `and`/`or` have two or more operands and `not` has exactly one;
5. `object-id` uses `=` only;
6. the serialiser reproduces the query string exactly; and
7. the query matches at least one object, unless the row is deliberately marked as an
   empty-result case.

Rule 2 is not academic. `("InitializationDependsFrom" some ("InterfaceName" "is/repository" =))`
reads perfectly well but does not parse: that relationship's `class-type` is
`BaseApplication`, and `InterfaceName` is declared on `IPCServiceApplicationBase`. Three
rows carry the `class-type-typing` construct tag specifically to test this.

### Expected result sets

`expected_object_ids` comes from the reference evaluator in `oks_model.py`, whose
semantics follow `OksObject::SatisfiesQueryExpression`. Four cases the documentation
leaves open are decided here and recorded in `oks_model.SEMANTIC_NOTES`:

* a comparison against a multi-value attribute succeeds if **any** element matches;
* an object with no stored value is evaluated against the schema `init-value`;
* an empty or unparseable value on a numeric attribute reads as `0`, on a bool as false;
* `("rel" all <expr>)` over an **empty** reference list is **false**, never vacuously true.

The last one is the only real judgement call. Re-verify the expected sets with
`oks_dump` once an OKS installation is available; the `oks_dump_cmd` field on each row is
the command to do it with.

### Few-shot leakage

`FewShotManager` reads `question`, `query_oks` and `note`, so this file loads as a
few-shot source without modification — **and that would leak the test set**. Keep the
few-shot pool and the eval set apart: use `oks_scraped/gold_pairs.jsonl` for few-shot
and this file for scoring, or split this file by `id` and pass only the held-out half.

One caveat about the existing few-shot pool. Of its 50 rows, 11 are not OKS queries at
all (they are `oks_dump` command lines or prose answers) and 12 place a scope token
inside an expression, for example
`(or (all ("Name" "Fake" =)) (all ("Timeout" "500" >)))`. The OKS parser requires
`all`/`this` as the **first token of the whole query** and nowhere else, so those 12 do
not parse. 27 of 50 rows are usable. Prompting with the other 23 teaches the model
syntax that fails at the parser.

---

## Computing the numbers

### M3 — translation accuracy

The specification asks for execution-based scoring, not string comparison:

```
execution accuracy = |{rows : result_set(generated) == expected_object_ids}| / N
```

Run the generated query with `oks_dump --class <target_class> --query '<generated>'`
over the `test_data` files and compare the returned ids to `expected_object_ids`.
Without an OKS install, `oks_model.execute()` is the stand-in oracle.

Report alongside it, never instead of it:

* **valid-syntax rate** — the query parses (`OksQuery::good()`, or `oks_dump` not
  exiting 3);
* **exact match** — `generated == query_oks` after canonicalising whitespace. Useful as
  a diagnostic, misleading as a headline: several rows have more than one correct
  serialisation.
* **failure breakdown** by `constructs`, so "regex escaping is wrong 40% of the time"
  is visible instead of one aggregate number.

### M2 — schema retrieval

`gold_schema_elements` is the gold set, derived automatically from the ground-truth IR,
so no separate annotation exists to drift out of date.

```
precision = |retrieved ∩ gold| / |retrieved|
recall    = |retrieved ∩ gold| / |gold|
```

Score classes, attributes and relationships separately — recall on relationships is the
number that predicts whether the hard band can work at all. `scope_class_count` shows
how many classes `all` pulls in, which is the retrieval budget the question really needs.

### Ablation

Report the four rungs the specification asks for, on the same rows:

| Rung | Configuration |
| --- | --- |
| 1 | Plain prompt, no retrieval, no examples |
| 2 | + few-shot examples |
| 3 | + schema retrieval |
| 4 | + validate/repair loop (full system) |

The 5 `ir_expressible: false` rows will fail at every rung until the IR grows a
path-query node. Report them separately rather than letting them depress the headline.
