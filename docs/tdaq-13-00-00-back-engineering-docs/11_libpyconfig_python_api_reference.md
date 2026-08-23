# libpyconfig / Python OKS API reference for TDAQ release 13-00-00

This document collects the Python API exposed by the `config` package in release `tdaq-13-00-00`, together with the historical-version mechanism that is supported by the `oksconfig` backend. It is grounded in the source under:

- `Materials/tdaq-cmake-tdaq-13-00-00/config/python/config/Configuration.py`
- `Materials/tdaq-cmake-tdaq-13-00-00/config/python/config/ConfigObject.py`
- `Materials/tdaq-cmake-tdaq-13-00-00/config/src/python/config.cpp`
- `Materials/tdaq-cmake-tdaq-13-00-00/config/config/Configuration.h`
- `Materials/tdaq-cmake-tdaq-13-00-00/oksconfig/doc/RELEASE_NOTES.md`
- `Materials/tdaq-cmake-tdaq-13-00-00/oks/src/kernel.cpp`

## 1. What this is

The Python layer is not a separate database layer. It is a thin wrapper around the native `libpyconfig` Boost.Python binding, which itself wraps the C++ `Configuration` object and the OKS backend.

The main Python entry points are:

- `config.Configuration` — database/session object
- `config.ConfigObject` — object wrapper returned by queries and `get_obj()`

Typical import:

```python
import config

cfg = config.Configuration("oksconfig:combined/partitions/ATLAS.data.xml")
```

In release 13-00-00, the supported historical revision form is:

```python
cfg = config.Configuration(
    "oksconfig:combined/partitions/ATLAS.data.xml&version=tag:r454833@ATLAS"
)
```

This is also documented in `oksconfig/doc/RELEASE_NOTES.md`.

---

## 2. Connection string forms

### 2.1 Basic local configuration

```python
cfg = config.Configuration("oksconfig:test.data.xml")
```

The constructor accepts a connection string in the form:

```text
<backend>:<database>
```

For OKS this is typically:

```text
oksconfig:<database-file>
```

### 2.2 Historical revision selection

The release adds a version parameter to the backend spec:

```text
oksconfig:<database-file>&version=<revision>
```

Valid examples:

```text
oksconfig:combined/partitions/ATLAS.data.xml&version=tag:r454833@ATLAS
oksconfig:combined/partitions/ATLAS.data.xml&version=hash:<sha>
oksconfig:combined/partitions/ATLAS.data.xml&version=branch:<branch>
```

The underlying parser expects the generic form:

```text
param:value
```

and is used by `OksKernel::parse_config_version()`.

### 2.3 Environment variable fallback

If no explicit version is in the connection string, the system also checks:

```bash
export TDAQ_DB_VERSION="tag:r454833@ATLAS"
```

or

```bash
export TDAQ_DB_VERSION="hash:<sha>"
```

This is a process-global fallback and not the preferred concurrency-safe choice when multiple historical views are needed.

---

## 3. Python-class surface

### 3.1 `config.Configuration`

This is the main object that loads an OKS configuration and exposes schema/query access.

Constructor:

```python
Configuration(connection='oksconfig:')
```

Implementation details from `Configuration.py`:

- It calls the native `libpyconfig.Configuration(connection)`
- It initializes a schema cache and configuration database list
- It keeps an internal object cache keyed by class name and UID

### 3.2 `config.ConfigObject`

A `ConfigObject` is the result of `get_obj()`, `get_objs()`, or a relationship traversal.

It exposes object attributes and relationships through a pythonic wrapper:

```python
obj = cfg.get_obj("Partition", "ATLAS")
name = obj["name"]
```

or, in relation access patterns, through object traversal based on schema metadata.

---

## 4. Public methods of `Configuration`

The following list is the user-facing Python API as implemented in `config/python/config/Configuration.py`.

### 4.1 Construction and database selection

```python
cfg = config.Configuration("oksconfig:test.data.xml")
```

Methods:

```python
cfg.databases()
cfg.set_active(name)
```

Purpose:

- `databases()` returns the list of loaded database files
- `set_active(name)` selects the active DB for subsequent write operations

### 4.2 Schema inspection

```python
cfg.classes()
cfg.attributes(class_name, all=False)
cfg.relations(class_name, all=False)
cfg.superclasses(class_name, all=False)
cfg.subclasses(class_name, all=False)
```

Behavior:

- `classes()` returns all loaded classes
- `attributes()` returns direct attributes or all inherited attributes
- `relations()` returns direct or inherited relations
- `superclasses()` / `subclasses()` return the inheritance graph

Example:

```python
classes = cfg.classes()
print(classes[:10])

attrs = cfg.attributes("Partition")
print(attrs.keys())

rels = cfg.relations("Partition")
print(rels.keys())
```

### 4.3 Object lookup and query execution

```python
cfg.get_objs(class_name, query='')
cfg.get_obj(class_name, uid)
```

Behavior:

- `get_objs(class_name, query='')` returns a Python list of `ConfigObject`
- `query` is an OKS query string; empty string means “all objects of this class or subclass”
- `get_obj(class_name, uid)` returns one `ConfigObject`

Example:

```python
objs = cfg.get_objs("Dummy")
print(len(objs))

obj = cfg.get_obj("Dummy", "TestDummy-4")
```

### 4.4 Include management

```python
cfg.get_includes(at=None)
cfg.add_include(include, at=None)
cfg.remove_include(include, at=None)
```

These manage the include files attached to a database.

### 4.5 Object creation and mutation

```python
cfg.create_obj(class_name, uid, at=None)
cfg.destroy_obj(obj)
```

and the corresponding DAL helpers:

```python
cfg.add_dal(dal_obj, at=None, cache=None, recurse=True)
cfg.update_dal(dal_obj, ignore_error=True, at=None, cache=None, recurse=False)
cfg.destroy_dal(dal_obj)
```

These methods are the write-oriented side of the API and should not be used in a read-only prototype.

### 4.6 DAL conversion

```python
cfg.get_dal(class_name, uid)
cfg.get_dals(class_name)
cfg.get_all_dals()
```

These convert `ConfigObject` data to generated DAL wrappers for schema-specific access.

### 4.7 Commit / create / database utilities

The underlying native C++ API includes:

```python
cfg.create_db(db_name, includes)
cfg.commit(log_message='')
cfg.abort()
```

The Python wrapper exposes this write-oriented surface as well, but it is outside the read-only historical-configuration use case.

---

## 5. Native C++ interface behind Python

The Python wrapper is built on top of the C++ `Configuration` API. The relevant C++ surface is declared in `config/config/Configuration.h`.

### 5.1 Core database operations

From the header:

- `bool loaded() const noexcept`
- `void load(const std::string& db_name)`
- `void unload()`
- `void create(const std::string& db_name, const std::list<std::string>& includes)`
- `void import(const std::string& to, const std::string& from, std::filesystem::copy_options options = ...)`
- `bool is_writable(const std::string& db_name) const`
- `void add_include(const std::string& db_name, const std::string& include)`
- `void remove_include(const std::string& db_name, const std::string& include)`
- `void get_includes(const std::string& db_name, std::list<std::string>& includes) const`
- `void set_commit_credentials(const std::string& user, const std::string& password)`
- `void commit(const std::string& log_message = "", const std::string& credentials = "")`
- `void abort()`

### 5.2 Query and object access

- `bool test_object(const std::string& class_name, const std::string& id, ...)`
- `void get(const std::string& class_name, const std::string& id, ConfigObject& object, ...)`
- `void get(const std::string& class_name, std::vector<ConfigObject>& objects, const std::string& query = "", ...)`
- `const daq::config::class_t& get_class_info(const std::string& class_name, bool direct_only = false)`
- `std::vector<daq::config::Version> get_versions(...)`
- `std::vector<daq::config::Version> get_changes()`

### 5.3 Schema introspection

The native binding exposes schema metadata through `class_t`:

- attributes
- relationships
- superclasses
- subclasses
- description fields

This is exported to Python as dictionaries in:

```python
cfg.attributes(class_name, all=False)
cfg.relations(class_name, all=False)
```

The Boost.Python binding in `config/src/python/config.cpp` constructs these as Python `dict` objects.

---

## 6. `ConfigObject` operations

`ConfigObject` is the Python wrapper around the native `ConfigObject` returned by OKS.

### 6.1 Attribute and relation access

The wrapper implements:

```python
obj['attribute_or_relation_name']
obj['name'] = value
```

This is the main access pattern from the Python layer:

```python
obj = cfg.get_obj("Partition", "ATLAS")
print(obj["name"])
print(obj["segments"])
```

The wrapper treats:

- attributes as scalar values or multi-value attributes
- relations as nested `ConfigObject` references or lists of `ConfigObject`

### 6.2 Comparison and hash

```python
obj1 == obj2
obj1 != obj2
hash(obj)
```

This implements object identity semantics based on class name and UID.

### 6.3 Serialization / DAL conversion

```python
obj.as_dal(cache)
```

This converts the object and descendants into DAL objects, which is useful for generated code and reflection-based object handling.

### 6.4 Set operation wrappers

```python
obj.set_obj(name, value)
obj.set_objs(name, value)
```

These adapt relation assignment to the native required `libpyconfig.ConfigObject` instance type.

---

## 7. Query language used by `get_objs()`

The OKS query grammar is enforced at the native layer. The key pattern is that the query string is parsed by `OksQuery` and validated against the schema.

The relevant implementation is in:

- `oks/src/query.cpp`
- `oksconfig/src/OksConfiguration.cpp`

The query grammar is conceptually of the form:

```text
(this | all) ( attribute op value )
```

Common patterns in the repository include:

```python
cfg.get_objs("Dummy", '(this (object-id "" !=))')
```

and similar attribute-based selectors.

The key point for Python use is:

- the query is passed as a string
- the backend validates it against schema metadata
- invalid strings raise a Python `RuntimeError` from the underlying C++ layer

---

## 8. Example usage patterns

### 8.1 Open a configuration

```python
import config

cfg = config.Configuration("oksconfig:combined/partitions/ATLAS.data.xml")
```

### 8.2 List classes

```python
for cls in cfg.classes():
    print(cls)
```

### 8.3 Get all objects of a class

```python
objs = cfg.get_objs("Partition")
for obj in objs:
    print(obj.full_name())
```

### 8.4 Get one object by UID

```python
part = cfg.get_obj("Partition", "ATLAS")
print(part)
```

### 8.5 Inspect attributes and relations

```python
print(cfg.attributes("Partition"))
print(cfg.relations("Partition"))
```

### 8.6 Read attribute values

```python
obj = cfg.get_obj("Partition", "ATLAS")
print(obj["name"])
```

### 8.7 Historical revision use

```python
cfg = config.Configuration(
    "oksconfig:combined/partitions/ATLAS.data.xml&version=tag:r454833@ATLAS"
)
```

This is the historical read pattern used by release 13-00-00.

---

## 9. Release 13-00-00 specific notes

### 9.1 `oksconfig` version parameter

The release note explicitly states:

```text
oksconfig:combined/partitions/ATLAS.data.xml&version=tag:r454833@ATLAS
```

This is the canonical historical configuration syntax.

### 9.2 Revision selection is part of the connection string

The database connection string may carry the selected revision, rather than requiring a shared process-global environment variable. This is the recommended design for concurrent historical reads.

### 9.3 The Python API is still the same API, just addressed with a versioned connection string

The Python layer does not invent its own historical API. Instead, the revision is expressed in the underlying database connection string and consumed by the backend.

### 9.4 Read-only boundary

The same `Configuration` object that supports mutation also includes many write APIs. In a production MCP or service, the safe boundary is:

- allow only: `classes()`, `attributes()`, `relations()`, `get_objs()`, `get_obj()`
- disallow: `create_db`, `commit`, `add_include`, `remove_include`, `destroy_obj`, `update_dal`, `set_commit_credentials`

This is a service-level policy, not a library restriction.

---

## 10. Important interface caveat

The Python API is thin and practical, but not all features are “documented” as a unified high-level Python manual. In practice, the reliable source of truth is:

1. the Python wrapper in `config/python/config/Configuration.py`
2. the native binding in `config/src/python/config.cpp`
3. the C++ class declaration in `config/config/Configuration.h`
4. the OKS query validation logic in `oks/src/query.cpp`

This means the complete interface surface is:

- the Python wrapper methods above
- the native C++ methods exposed by `Configuration`
- the underlying `ConfigObject` attribute/relationship semantics
- the historical revision mechanism through `&version=`

---

## 11. Minimal example: historical read of a real config

```python
import config

cfg = config.Configuration(
    "oksconfig:combined/partitions/ATLAS.data.xml&version=tag:r454833@ATLAS"
)

print(cfg.classes()[:10])

objs = cfg.get_objs("Partition")
for obj in objs:
    print(obj.full_name())

part = cfg.get_obj("Partition", "ATLAS")
print(part["name"])
```

---

## 12. Reference summary

### `config.Configuration`

```python
Configuration(connection='oksconfig:')

classes()
attributes(class_name, all=False)
relations(class_name, all=False)
superclasses(class_name, all=False)
subclasses(class_name, all=False)
get_objs(class_name, query='')
get_obj(class_name, uid)
create_obj(class_name, uid, at=None)
destroy_obj(obj)
get_includes(at=None)
add_include(include, at=None)
remove_include(include, at=None)
create_db(db_name, includes)
commit(log_message='')
abort()
get_dal(class_name, uid)
get_dals(class_name)
get_all_dals()
add_dal(dal_obj, at=None, cache=None, recurse=True)
update_dal(dal_obj, ignore_error=True, at=None, cache=None, recurse=False)
destroy_dal(dal_obj)
```

### `config.ConfigObject`

```python
obj['name']
obj['relation_name']
obj.set_obj(name, value)
obj.set_objs(name, value)
obj.as_dal(cache)
obj == other
obj != other
str(obj)
repr(obj)
```

### Connection strings

```text
oksconfig:<file>
oksconfig:<file>&version=tag:<value>
oksconfig:<file>&version=hash:<sha>
oksconfig:<file>&version=branch:<branch>
```

---

## 13. Bottom line

The Python API is straightforward and robust for read-only access:

- open a configuration with an OKS backend
- inspect schema via `classes()`, `attributes()`, `relations()`
- query objects via `get_objs()` / `get_obj()`
- access object fields through `obj[...]`
- select historical revisions via `&version=...`

This is the exact API pattern to build on for a release-13 historical read-only service or Python MCP layer.
