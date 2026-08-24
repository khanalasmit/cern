# 12 — Native C++ / OKS usage and `oks_dump` for TDAQ release 13-00-00

This note documents the native OKS / C++ layer behind the Python wrapper, and it gives a practical how-to for the `oks_dump` command in release `tdaq-13-00-00`.

It is grounded in the actual sources under:

- `Materials/tdaq-cmake-tdaq-13-00-00/config/config/Configuration.h`
- `Materials/tdaq-cmake-tdaq-13-00-00/config/src/python/config.cpp`
- `Materials/tdaq-cmake-tdaq-13-00-00/oks/include/oks/kernel.h` (or equivalent kernel declarations)
- `Materials/tdaq-cmake-tdaq-13-00-00/oks/src/query.cpp`
- `Materials/tdaq-cmake-tdaq-13-00-00/oks/bin/oks_dump.cpp`
- `Materials/tdaq-cmake-tdaq-13-00-00/oksconfig/doc/RELEASE_NOTES.md`

## 1. The architecture: Python wrapper vs native OKS

The Python `config` package is a thin wrapper over the native OKS engine. In practice:

- Python `config.Configuration` is a user-facing facade.
- The real semantics live in the native C++ kernel and query engine.
- `OksKernel`, `OksClass`, `OksObject`, `OksQuery`, and `QueryPath` are the lower-level API.

This means:

- Python is excellent for quick inspection and common tasks.
- Native C++ exposes the full and more expressive query system.
- Some more advanced query semantics are visible in the native OKS layer even when the Python wrapper does not expose them as a first-class convenience API.

In other words, the Python layer is not a parallel implementation; it is a limited, ergonomic facade over the C++ backend.

---

## 2. Historical configuration in native code

The release supports loading a historical configuration through the backend version string or via `TDAQ_DB_VERSION`.

Supported form:

```text
oksconfig:<database-file>&version=tag:r454833@ATLAS
```

Equivalent environment fallback:

```bash
export TDAQ_DB_VERSION="tag:r454833@ATLAS"
```

The native `OksKernel` code resolves the repository and revision before the file is loaded. This is the mechanism used by the configuration layer.

Typical C++ sketch:

```cpp
#include <oks/kernel.h>

int main() {
  const char * version = "tag:r454833@ATLAS";
  OksKernel kernel(false, false, false, true, version);

  if (kernel.load_file("combined/partitions/ATLAS.data.xml") == 0) {
    std::cerr << "failed to load data file" << std::endl;
    return 1;
  }

  return 0;
}
```

The constructor is the key place where a historical repository/tag/hash can be selected before schema/data loading.

---

## 3. Native `OksKernel` usage pattern

The canonical pattern is:

1. create kernel
2. load schema/data files
3. find class
4. create query or path
5. execute query
6. inspect objects and relationships

Example:

```cpp
#include <oks/kernel.h>
#include <oks/query.h>
#include <iostream>

int main() {
  OksKernel kernel;

  if (kernel.load_file("schema.xml") == 0) {
    std::cerr << "cannot load schema" << std::endl;
    return 1;
  }

  if (kernel.load_file("data.xml") == 0) {
    std::cerr << "cannot load data" << std::endl;
    return 1;
  }

  OksClass *cls = kernel.find_class("Partition");
  if (!cls) {
    std::cerr << "class not found" << std::endl;
    return 1;
  }

  OksQuery *q = new OksQuery(cls, "all (Name \"ATLAS\" =)");
  if (!q->good()) {
    std::cerr << "bad query" << std::endl;
    return 1;
  }

  OksObject::List *objs = cls->execute_query(q);
  if (objs) {
    for (OksObject::List::iterator it = objs->begin(); it != objs->end(); ++it) {
      std::cout << **it << std::endl;
    }
    delete objs;
  }

  delete q;
  return 0;
}
```

The important point is that `OksClass::execute_query()` is the native query executor and returns a list of object pointers.

---

## 4. OKS query grammar in the native layer

The native grammar is richer than the Python wrapper surface. The source makes this explicit in `oks/src/query.cpp` and `oks/oks/query.h`.

### 4.1 Query keywords

The parser defines these query operators and keywords:

```cpp
OksQuery::OR          = "or"
OksQuery::AND         = "and"
OksQuery::NOT         = "not"
OksQuery::SOME        = "some"
OksQuery::THIS_CLASS  = "this"
OksQuery::ALL_SUBCLASSES = "all"
OksQuery::OID         = "object-id"
OksQuery::EQ          = "="
OksQuery::NE          = "!="
OksQuery::RE          = "~="
OksQuery::LE          = "<="
OksQuery::GE          = ">="
OksQuery::LS          = "<"
OksQuery::GT          = ">"
OksQuery::PATH_TO     = "path-to"
OksQuery::DIRECT      = "direct"
OksQuery::NESTED      = "nested"
```

### 4.2 Overall structure

The outer query must start with either `this` or `all`:

```text
all ( ... )
this ( ... )
```

That is enforced directly by the parser and is one of the strongest pieces of evidence that the query syntax is intentionally structured and schema-aware.

### 4.3 Comparator expressions

A simple predicate is written as:

```text
(<attribute-name> <value> <comparator>)
```

Examples:

```text
all (Name "ATLAS" =)
all (RunNumber 42 >=)
all (Status "READY" =)
```

This is the actual pattern the parser expects and is not the same as a SQL-like `attribute = value` form.

### 4.4 Relationship expressions

Relationship queries are a core feature of OKS and are supported by the native parser:

```text
(<relationship-name> some <nested-expression>)
(<relationship-name> all <nested-expression>)
```

Example pattern:

```text
all (Owner some (Name "ATLAS" =))
```

and the query engine can evaluate nested relation checks recursively.

### 4.5 Logical combinations

Logical expressions combine subexpressions with `and` or `or`, and `not` flips a subexpression:

```text
all (and (Name "ATLAS" =) (Status "OK" =))
all (or (Name "ATLAS" =) (Name "CERN" =))
all (not (Name "ATLAS" =))
```

This is exactly the kind of nested logical expression the Python wrapper does not expose as a rich, first-class query DSL.

### 4.6 Richer semantics than the Python wrapper

From the source, the OKS query engine supports:

- nested relationship expressions
- logical `and` / `or` / `not` composition
- relationship traversal predicates (`some` / `all`)
- path-based queries (`path-to`, `direct`, `nested`)

This is the key distinction:

- Python `Configuration.get_objs(class_name, query='')` is a thin convenience surface.
- The native query engine supports more advanced relational and nested semantics than the Python façade necessarily exposes.

So the correct answer to the question is: the underlying native OKS logic supports the richer relationship and nested query semantics; the Python wrapper is simpler and more constrained.

---

## 5. Path queries and traversal

The native code also supports a path query API via `QueryPath`.

The `oks_dump` CLI exposes this through:

```bash
oks_dump --path <object-from> <query>
```

The underlying API pattern is conceptually:

```cpp
oks::QueryPath q(path_query, kernel);
OksObject::List *objs = obj_from->find_path(q);
```

This is used to find a path between objects rather than just matching a flat attribute predicate.

Example pattern:

```text
--path objid@Class "(path-to ... )"
```

The exact path format is grammar-driven and is checked by `oks::bad_query_syntax` when parsing fails.

This is a stronger form of traversal than a simple Python `get_objs()` call.

---

## 6. `oks_dump` — practical usage guide

The command is built in `oks/bin/oks_dump.cpp` and is the most direct CLI for inspecting OKS configuration files.

### 6.1 Usage synopsis

```bash
oks_dump
    [--files-only | --files-stat-only | --schema-files-only | --schema-files-stat-only | --data-files-only | --data-files-stat-only]
    [--class name-of-class [--query query [--print-references recursion-depth [class-name*] [--]] [--print-referenced_by [name] [--]]]]
    [--path object-from object-to query]
    [--allow-duplicated-objects-via-inheritance]
    [--version]
    [--help]
    [--input-from-files] database-file [database-file(s)]
```

### 6.2 Basic file listing

List all files loaded by the kernel:

```bash
oks_dump my_schema.xml my_data.xml
```

List only schema files:

```bash
oks_dump --schema-files-only my_schema.xml
```

List only data files:

```bash
oks_dump --data-files-only my_data.xml
```

### 6.3 Dump a class

Show all objects in a class:

```bash
oks_dump --class Partition my_data.xml
```

This prints the class structure and objects.

### 6.4 Query a class

Query and filter matching objects:

```bash
oks_dump --class Partition --query 'all (Name "ATLAS" =)' my_data.xml
```

This is the CLI analog of native `OksQuery` evaluation.

### 6.5 Print references and reverse references

Show references from matching objects:

```bash
oks_dump --class Partition --query 'all (Name "ATLAS" =)' --print-references 2
```

Show objects that reference a result through a named relationship:

```bash
oks_dump --class Partition --query 'all (Name "ATLAS" =)' --print-referenced_by owner
```

### 6.6 Path search

Find the path from one object to something matching a path query:

```bash
oks_dump --path object-id@Class 'path-expression'
```

The exact syntax is the native `QueryPath` grammar, not a Pythonic dictionary traversal.

### 6.7 Input from a file list

When the shell command line is too long, pass the file names in a file:

```bash
oks_dump --input-from-files filelist.txt
```

The tool reads each file path from the text file and loads it.

### 6.8 Exit codes

From `oks_dump.cpp`:

- `0` — success
- `1` — bad command line
- `2` — bad OKS file
- `3` — bad query
- `4` — no such class
- `5` — dangling references
- `6` — exception

This makes it useful in shell pipelines and CI checks.

---

## 7. A practical workflow for release 13-00-00

### Option A — quick Python inspection

```python
import config

cfg = config.Configuration("oksconfig:combined/partitions/ATLAS.data.xml&version=tag:r454833@ATLAS")
objs = cfg.get_objs("Partition")
print(len(objs))
```

Useful for read-only inspection and object lookup.

### Option B — native C++ query

```cpp
OksKernel kernel(false, false, false, true, "tag:r454833@ATLAS");
OksClass *c = kernel.find_class("Partition");
OksQuery q(c, "all (Name \"ATLAS\" =)");
OksObject::List *res = c->execute_query(&q);
```

This is the authoritative path when you need the full OKS query engine.

### Option C — command-line inspection

```bash
oks_dump --class Partition --query 'all (Name "ATLAS" =)' ATLAS.data.xml
```

This is the best first step when you do not want to write a small C++ program or Python script.

---

## 8. Final caveat

The release-13 Python API is a useful and practical facade, but it is not the whole story. The real OKS functionality sits below it in the native layer:

- schema-aware query parsing
- nested relationship expressions
- relationship and path traversal
- historical repository selection by version string
- CLI-based inspection through `oks_dump`

If the goal is to understand the full capability of OKS, the native `OksKernel` + `OksQuery` + `oks_dump` path is the correct source of truth.
