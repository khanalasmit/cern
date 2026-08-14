# OKS query examples (for fine-tuning "English question -> OKS query")

Sources used:
- OKS sources: `src/query.cpp`, `include/oks/query.hpp`, `docs/README.md` (https://github.com/DUNE-DAQ/oks)
- CERN original: https://gitlab.cern.ch/atlas-tdaq-software/oks `doc/RELEASE_NOTES.md`
- OKS Data Editor online help: `repos/online-help/data-editor/QueryWindow.html`
- `oks_utils/examples/*.cpp` and `src/bin/oks_tutorial.cpp`

## 1. Query syntax (compact)

```
query          ::= "(" scope expr ")"
scope          ::= "this" | "all"                 ; this = class only, all = class + subclasses
expr           ::= attr_cmp | uid_cmp | rel_expr | and_expr | or_expr | not_expr
and_expr       ::= "and" expr+
or_expr        ::= "or" expr+
not_expr       ::= "not" expr
attr_cmp       ::= "(" "\"attr-name\"" "\"value\"" op ")"
uid_cmp        ::= "(" "object-id" "\"an-object-id\"" "=" ")"
rel_expr       ::= "(" "\"rel-name\"" ("some"|"all") expr ")"
path_query     ::= ( path-to "\"dest-id@class\"" ( direct|nested "\"rel\"" ... ) )
op             ::= "=" | "!=" | "~=" | "<" | "<=" | ">" | ">="
```

Notes:
- `~=` is a *regular expression* compare (added in tdaq-01-09-00).
- `object-id` may only be compared with `=`.
- Query files are plain text, LISP-like, editable by hand (per Data Editor
  online help, section "Saving Query": "The format of the query file is
  simple and can be edited manually by any text editor").

## 2. English -> query examples

### 2.1 Attribute comparisons

| English question | OKS query string |
|---|---|
| find all Computers named pc-tdaq-onl-01 | `(all ("Name" "pc-tdaq-onl-01" =))` |
| find all Computers NOT named pc-tdaq-onl-01 | `(all ("Name" "pc-tdaq-onl-01" !=))` |
| hosts matching pattern pc-tdaq-onl-* | `(all ("Name" "pc-tdaq-onl-.*" ~=))` |
| applications with timeout >= 20 seconds | `(all ("Timeout" "20" >=))` |
| applications with timeout less than 10 | `(all ("Timeout" "10" <))` |
| all partitions run in "physics" mode (multi-value attr) | `(all ("RunTypes" "physics" =))` |
| cars with max speed greater than 200 (tutorial example) | `(all ("Max Speed" "200" >))` |
| anything with height >= 1.88 or <= 1.65 (tall or short) | `(all ("Height" "1.65" >=)) (all ("Height" "1.88" <=))` — combined: `(or (all ("Height" "1.65" >=)) (all ("Height" "1.88" <=)))` |
| adults: age !< 18 i.e. age >= 18 | `(not (all ("Age" "18" <)))` |

Note: in the file form operators are textual; when embedding the query in the
`OksQuery("(all (...)")` constructor, the same syntax is used.

### 2.2 Relationship ("some"/"all") and object-id

| English question | OKS query string |
|---|---|
| all objects of class X that reference object Z via relationship R | `(all ("R" some (object-id "Z" =)))` |
| all applications, incl. subclasses, running on host lxplus001 | `(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))` |
| find the object-id "test" used by relationship "my-relationship" | `(all ("my-relationship" some (object-id "test" =)))` (* RELEASE_NOTES tdaq-01-02-00) |

### 2.3 Path queries

Syntax (from RELEASE_NOTES tdaq-01-02-00, "Path Query"):

```
(path-to "destination-object" (direct "rel-name" ["rel-name"*] [(nested "rel"  ...)]))
```

Genuine example:

```
(path-to "my-id@my-class" (direct "A" "B" (nested "N" (direct "X" "Y" "Z"))))
```

Meaning: start object must have relationships A and B; the object referenced
via them must have relationship N; objects referenced via N must have X, Y, Z;
destination is found if referenced by X/Y/Z.

CLI (found in RELEASE NOTES tdaq-01-02-00, "OKS dump"):

```
oks_dump --path "onlsw_test_3x3_lxlpus@Partition" \
  '(path-to "lxplus-3x3-21-ctrl@RunControlApplication"
     (direct "Segments" "OnlineInfrastructure" (nested "Segments"
        (direct "Applications" "IsControlledBy" "Resources"))))' \
  daq/partitions/lxplus_tests.data.xml
```

### 2.4 Git-version queries (config version)

```
> see config of run 380689, partition all_hosts:
    oks_clone_repository --version tag:r380689@all_hosts
> by commit hash:
    oks_clone_repository --version hash:6800fe3b
> by date:
    oks_clone_repository --version 'date:2020-08-02 10:00:00'
> list stored versions:
    kernel.get_repository_versions(...)       ; or rn_ls (run DB) as in RELEASE NOTES
```

## 3. Comparison enums (C++ names)

From `include/oks/query.hpp` / `examples`:

| C++ | text |
|---|---|
| `OksQuery::equal_cmp` | `=` |
| `OksQuery::not_equal_cmp` | `!=` |
| `OksQuery::less_cmp` | `<` |
| `OksQuery::less_or_equal_cmp` | `<=` |
| `OksQuery::greater_cmp` | `>` |
| `OksQuery::greater_or_equal_cmp` | `>=` |
| regexp comparator | `~=` |

## 4. How the GUI describes it (QueryWindow.html)

"Attribute Expression": select attribute, value, comparator.
"Relationship Expression": choose relationship, toggle "Some Objects Match
Query" vs "All Objects Match Query", nested query form inside.
"Logical + And/Or/Not expressions": tree of any depth, leaves must be
attribute or relationship expressions.
Queries are weak-typed: "An OKS query does not strongly depend on class type:
if two classes have an attribute with the same name, possibly a query can be
applied to both classes."

## 5. Verification & errors

- `oks_dump` exit codes: 0 ok; 1 bad CLI; 2 bad oks file; 3 bad query; 4 class
  not found; 5 dangling references.
- parse failures raise `oks::bad_query_syntax`.

## Provenance

| fact | file |
|---|---|
| grammar tokens & comparators | `src/query.cpp` lines 23-39; `include/oks/query.h` |
| object-id example | CERN RELEASE_NOTES tdaq-01-02-00, section "Query", subsection "Example of query string" |
| path example | CERN RELEASE_NOTES tdaq-01-02-00, "Path Query"; `oks_dump --path` in same |
| regex comparator `~=` | RELEASE_NOTES tdaq-01-09-00 ("add attribute comparator '~='") |
| timing/versioning | RELEASE_NOTES tdaq-09-02-01 + tdaq-09-01-00 (rn_ls example) |
| GUI semantics | `repos/online-help/data-editor/QueryWindow.html` (copied) |