# 01. The OKS C++ library code — DUNE-DAQ fork (`DUNE-DAQ/oks`)

Source repository (public, default branch `develop`):
- https://github.com/DUNE-DAQ/oks
- Clone: `git clone https://github.com/DUNE-DAQ/oks`
- Baseline of the fork: CERN tag `oks-08-03-04` (Apr 2022), i.e. the same OKS engine used by ATLAS TDAQ tdaq-09-04-00.

Local copies of the whole source tree were kept under
`repos/../` (see `FINAL_REPORT.md`); this document records the files that
are most valuable for building an English->OKS-query training corpus,
with exact snippets.

---

## 1.1 Layout of the repository

| Path                        | Content                                              |
|-----------------------------|------------------------------------------------------|
| `include/oks/query.hpp`     | Query classes: `OksQuery`, `OksQueryExpression`, `OksComparator`, `OksAndExpression`, `OksOrExpression`, `OksNotExpression`, `OksRelationshipExpression`, `oks::QueryPath` |
| `include/oks/index.hpp`     | `OksIndex` (fast object lookup) + query operators    |
| `include/oks/kernel.hpp`    | `OksKernel` — load/save/new schema & data, git repository versions |
| `include/oks/class.hpp`     | `OksClass` — `execute_query()`, `find_object()`, `get_object()` |
| `include/oks/object.hpp`    | `OksObject` — attributes, relationships, `find_path()` |
| `include/oks/attribute.hpp` | `OksAttribute` — types, ranges, defaults              |
| `include/oks/relationship.hpp` | `OksRelationship` — cardinalities, composite/exclusive |
| `include/oks/file.hpp`      | `OksFile` — data/schema files, includes, comments     |
| `src/query.cpp`             | Query string parser (the OKS query grammar)           |
| `apps/oks_dump.cxx`         | CLI tool: dump classes, objects, execute queries, path queries |
| `apps/oks_clone_repository.cxx` | Clone git config repository with `-b/-c/-t/-d` options |
| `apps/oks_check_schema.cxx`, `oks_validate_repository.cxx` | Check/validate    |
| `scripts/oks-*.sh`          | `oks-commit.sh`, `oks-tag.sh`, `oks-checkout.sh`, `oks-import.sh`, `oks-copy.sh`, ... |
| `pybindsrc/module.cpp`      | Python bindings (module `oks`), 1-line `python/oks/__init__.py` |

---

## 1.2 The OKS query grammar (authoritative)

`src/query.cpp` lines 23–39 — the reserved tokens:

```cpp
const char * OR          = "or";
const char * AND         = "and";
const char * NOT         = "not";
const char * SOME        = "some";
const char * THIS_CLASS  = "this";
const char * ALL_SUB     = "all";        // in CERN sources: ALL_SUBCLASSES
const char * OID         = "object-id";
const char * EQ          = "=";
const char * NE          = "!=";
const char * RE          = "~=";
const char * LE          = "<=";
const char * GE          = ">=";
const char * LS          = "<";
const char * GT          = ">";
const char * PATH_TO     = "path-to";
const char * DIRECT      = "direct";
const char * NESTED      = "nested";
```

A query string is Lisp-like: `(operator operand1 operand2 ...)`.
Two summary forms:

1. **Scope** — the query applies either to objects of the given class
   only (`this`) or to the class and all its subclasses (`all`):

       (this <expr>)
       (all  <expr>)

2. **Expressions** — compositional tree:

```
expr        ::= comparator
              | ("and"/"or" expr*)
              | ("not" expr)
              | ("rel-name" ("some"|"all") expr)
              | ("object-id" "id" "=")
comparator  ::= ("attr-name" "value" op)   op in {=, !=, ~=, <=, >=, <, >}
```

Full grammar documentation is embedded in `query.hpp` (see the "Query string
syntax" comment block around line 300–420) and in `docs/README.md` of the
same repository.

---

## 903 Examples from the repository tests/examples

### 903.1 Simple attribute comparator (C++), `oks_utils/examples/comparator.cpp`

```cpp
#include <oks/attribute.h>
#include <oks/query.h>

int main()
{
  const OksAttribute a("Name", OksAttribute::string_type, false, "", "unknown", "...", true);
  OksComparator qc(&a, new OksData("Peter"), OksQuery::equal_cmp);
  std::cout << qc << std::endl;   // prints  "Name" "Peter" =
}
```

### 903.2 Query over a class, `oks_utils/examples/query.cpp`

```cpp
OksKernel k;
k.new_schema("/tmp/car.schema");
k.new_data("/tmp/car.data");
OksClass * p = new OksClass("Car", "Describes a car", false, &k);
OksAttribute * a = new OksAttribute("Max Speed", OksAttribute::u16_int_type, false, "", "160", "...", true);
p->add(a);
OksObject * bmw316i = new OksObject(p, "BMW 316i");
OksObject * bmw318i = new OksObject(p, "BMW 318i");
OksObject * bmw320i = new OksObject(p, "BMW 320i");
OksData d((uint16_t) 196);
bmw316i->SetAttributeValue("Max Speed", &d);
d.Set((uint16_t) 201); bmw318i->SetAttributeValue("Max Speed", &d);
d.Set((uint16_t) 214); bmw320i->SetAttributeValue("Max Speed", &d);

// "find all cars with Max Speed > 200"
OksQuery q(false, new OksComparator(a, new OksData((unsigned short) 200),
                                    OksQuery::greater_cmp));
std::list<OksObject *> * result = p->execute_query(&q);
```

### 903.3 Boolean/arithmetic composition, `examples/and_expression.cpp`,
`or_expression.cpp`, `not_expression.cpp`, `r_expression.cpp`

```cpp
OksAttribute a("Height", OksAttribute::float_type, ...);
OksOrExpression or_q;
or_q.add(new OksComparator(&a, new OksData((float)1.65), OksQuery::greater_or_equal_cmp));
or_q.add(new OksComparator(&a, new OksData((float)1.88), OksQuery::less_or_equal_cmp));

OksNotExpression ne(new OksComparator(&a, new OksData((unsigned short)25), OksQuery::less_cmp));

OksRelationship r("has car", "Car", OksRelationship::Zero, OksRelationship::Many, ...);
OksRelationshipExpression rqe(&r, new OksComparator(&a, new OksData("BMW"), OksQuery::equal_cmp), false);
```

Note: `OksQuery::equal_cmp`, `not_equal_cmp`, `less_cmp`, `less_or_equal_cmp`,
`greater_cmp`, `greater_or_equal_cmp`, and the regular-expression comparator
`re_cmp` (introduced in tdaq-01-09-00, source `include/oks/index.hpp`) map to
the text operators `=  !=  <  <=  >  >=  ~=`.

### 903.5 `oks_dump` command line (the natural text interface to OKS queries)

From `apps/oks_dump.cxx` (usage banner, lines ~44–81):

```
oks_dump [options] database-file(s)
    [--files-only | --files-stat-only | --schema-files-only ... | --data-files-only | ...]
    [--class class-name [--query query [--print-references depth class... | --print-referenced_by]]]
    [--path object-from object-to query]
    -f | --files-only            print list of oks file names
    -F | --files-stat-only ...
    -s | --schema-files-only ...
    -S | --schema-files-stat-only
    -d | --data-files-only
    -D | --data-files-stat-only
    -c | --class class-name      dump given class (all objects or matching query)
    -q | --query query           print objects matching query (can be used with --class)
    -r | --print-references N [C1...]  print referenced objects
    -b | --print-referenced_by [name]  print referencing objects
    -p | --path obj query        print path from object 'obj' to object of query expression
    -i | --input-from-files      read file list from file
    -a | --allow-duplicated-objects-via-inheritance
```

Exit codes: 0 = ok, 1 = bad command line, 2 = bad oks file(s), 3 = bad query,
4 = class not found, 5 = dangling references found.

---

## 1.4 Git-repository versioning API relevant to "find which configuration was used"

`include/oks/kernel.hpp`:

- `struct OksRepositoryVersion` (line ~514): members incl. `tag`, `sha1`,
  `date`/`time`, `branch`, `author`, `comment`, `workdir`, 
  `OksRepositoryVersion(const std::string&, const std::string&, ...)`.
- `OksKernel::load_file(...)`, `load_schema(...)`, `load_data(...)`.
- `get_repository_root()` / `get_repository_mapping_dir()` (lines ~938, 960).
- `tag_repository(tag)` (line 1579): tag current version e.g. `r380689@all_hosts`.
- `get_repository_versions(skip_irrelevant, command_line)` (line 1667) — list
  all versions; `get_repository_versions_by_hash(sha1)` (1681);
  `get_repository_versions_by_date(...)` (1695); `read_repository_version(...)`
  (1705); `get_repository_versions_diff(sha1a, sha1b)` (1643).
- Environment variables (`docs/README.md`, CERN RELEASE_NOTES "tdaq-09-01-00"):
  `TDAQ_DB_REPOSITORY` (enable git), `TDAQ_DB_USER_REPOSITORY`, `TDAQ_DB_VERSION`
  (`hash:<sha1>` or `date:<ts>`), `OKS_REPOSITORY_MAPPING_DIR`, `TDAQ_DB_PATH`.

Shifter-relevant command-line mapping:

| Question                          | OKS answer                                              |
|-----------------------------------|---------------------------------------------------------|
| What config version ran for run 380689? | tag `r380689@all_hosts`; `oks_clone_repository --version tag:r380689@all_hosts` |
| Which version by hash?            | `oks_clone_repository --version hash:6800fe3b`           |
| Which version by date?            | `oks_clone_repository --version 'date:2020-08-02 10:00:00'` |
| List all versions?                | `oks_dump -r ...` / kernel `get_repository_versions(...)` |

---

## 1.5 Python bindings

`pybindsrc/module.cpp` exposes the kernel/class/object API; the Python
package name is `oks` (`python/oks/__init__.py` is intentionally *empty*
— C++ bindings only; builds with cmake + pybind11).

---

## 1.6 Copyright / licence

All OKS/DAL code files are © CERN (ATLAS collaboration) — https://github.com/DUNE-DAQ/oks — BSD-3-Clause style licence (`LICENSE` in root). 
Keep attribution when redistributing snippets.