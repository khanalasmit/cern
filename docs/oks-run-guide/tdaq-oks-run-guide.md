# ATLAS TDAQ OKS Guide — Validated on lxplus 

> **Prerequisite:** Every command in this guide assumes you have loaded the TDAQ environment. If a command prints object IDs and attributes, it is a data-producing query. If it prints only XML filenames, it is in file-list mode.

---

## Table of Contents

1. [SSH & Environment Setup](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#1-ssh--environment-setup)
2. [OKS Core Concepts](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#2-oks-core-concepts)
3. [Command Line: ](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#3-command-line-oks_dump)
4. [Python API: ](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#4-python-api-config-module)
5. [Native C++ API](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#5-native-c-api)
6. [Git Version Control](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#6-git-version-control)
7. [CMake Work Area](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#7-cmake-work-area)
8. [Troubleshooting](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#8-troubleshooting)
9. [Daily Workflow Cheat Sheet](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#9-daily-workflow-cheat-sheet)
10. [Appendix: Query Syntax Quick Reference](https://www.kimi.ai/chat/1a02a43f-43c2-8d8e-8000-09db4ac3b637?chat_enter_method=home#appendix-query-syntax-quick-reference)

---

## 1. SSH & Environment Setup

### 1.1 Connect to lxplus

bash  

```bash
ssh adhikari@lxplus.cern.ch
```

### 1.2 Setup TDAQ Environment

Add the following alias once to your `~/.bashrc` (optional but recommended):

bash  

```bash
alias cm_setup='source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tools/cmake_tdaq/bin/cm_setup.sh'
```

Load the production release:

bash  

```bash
cm_setup prod
```

Or load a specific release:

bash  

```bash
cm_setup tdaq-13-00-00
cm_setup nightly
cm_setup prod dbg
```

### 1.3 Verify Setup

bash  

```bash
echo $TDAQ_INST_PATH
which oks_dump
which cmake
which gcc
gcc --version
```

**Expected:** `TDAQ_INST_PATH` points to `/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-13-00-00/installed`, and all commands resolve.



## 2. OKS Core Concepts

### 2.1 Terminology

Table 

| TermMeaningExample         |                                                |                                       |
| -------------------------- | ---------------------------------------------- | ------------------------------------- |
| **Schema** (`.schema.xml`) | Defines classes, attributes, and relationships | `daq/schema/core.schema.xml`          |
| **Data** (`.data.xml`)     | Contains actual object instances               | `daq/segments/setup.data.xml`         |
| **Class**                  | Object type (like a table)                     | `Application`, `Segment`, `Partition` |
| **Object**                 | Instance of a class (like a row)               | `initial@Segment`                     |
| **Attribute**              | Property of an object                          | `InitTimeout`, `name`                 |
| **Relation**               | Link to another object                         | `RunsOn`, `Segments`                  |

### 2.2 Three Different Things Called "Version"

Table 

| What changesExampleSelected byRequires rebuild? |                                                         |                                                             |                                                                             |
| ----------------------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------- |
| **TDAQ software release**                       | `tdaq-13-00-00`                                         | `cm_setup tdaq-13-00-00`                                    | **Yes** — use a build directory configured for that release                 |
| **OKS configuration revision**                  | `hash:6800fe3b`, `date:2024-06-15`, `tag:r454833@ATLAS` | `OksKernel` constructor, `TDAQ_DB_VERSION`, or Git checkout | **No** — the same executable can read any compatible configuration revision |
| **Git tag name**                                | `r454833@ATLAS`                                         | `tag:<name>`                                                | No — a tag is just a named commit                                           |

A Git tag is not guaranteed to exist. A commit hash is the precise fallback; a date selects the latest commit before that date. A plain release-looking string is **not** a selector unless it is the name of an actual Git tag — always use the required `tag:`, `hash:`, or `date:` prefix.

### 2.3 Key Environment Variables

bash  

```bash
echo $TDAQ_DB_REPOSITORY      # Git URL for OKS configs (set by the release)
echo $TDAQ_DB_VERSION         # Requested revision for an automatic checkout
echo $TDAQ_DB_USER_REPOSITORY # Existing local checkout; takes precedence if set
```

When `TDAQ_DB_USER_REPOSITORY` is set, OKS attaches to that directory and uses its current `HEAD`. It does **not** automatically switch to `TDAQ_DB_VERSION` or to the `OksKernel` constructor argument. A read-only `OksKernel` only reads this variable at construction time.

---

## 3. Command Line: `oks_dump`

`oks_dump` is the primary CLI tool for querying OKS. It is available immediately after `cm_setup prod`.

### 3.1 Basic Listing

bash  

```bash
# List all files loaded by a data file (schema + data)
oks_dump -f daq/segments/setup-initial.data.xml

# List only schema files
oks_dump -s daq/segments/setup.data.xml

# List only data files
oks_dump -d daq/segments/setup.data.xml
```

> **Important:** `-f` is **file-list mode**. It prints loaded XML paths; it does **not** print objects. Use `-f` only for include/load inspection, never for object or query output.

### 3.2 Filter by Class

bash  

```bash
# Do NOT use -f here.
oks_dump -c IPCServiceApplication daq/segments/setup.data.xml
```

Use a **concrete class** for a first output test. `Application` is abstract and has no objects directly of that class; its objects are instances of subclasses such as `IPCServiceApplication`, `RunControlApplication`, and `CustomLifetimeApplication`.

### 3.3 Query by Object ID

> **Rule:** The `-q` option **requires** `-c <Class>`.

bash  

```bash
oks_dump -c Segment -q '(this (object-id "initial" =))' daq/segments/setup.data.xml
```

### 3.4 Regex Match on Attribute

bash  

```bash
oks_dump -c IPCServiceApplication -q '(all ("Parameters" ".*" ~=))' daq/segments/setup.data.xml
```

### 3.5 Relationship Query

The host `pc-tbed-onl-03.cern.ch` is defined in `daq/hw/hosts.data.xml`, which is included by `daq/segments/setup.data.xml`.

bash  

```bash
oks_dump \
  -c IPCServiceApplication \
  -q '(all ("RunsOn" some (object-id "pc-tbed-onl-03.cern.ch" =)))' \
  daq/segments/setup.data.xml
```

Before relying on a query in an automated workflow, check the installed command's exact options:

bash  

```bash
oks_dump --help
```

### 3.6 Numeric Comparison

bash  

```bash
oks_dump -c IPCServiceApplication -q '(all ("InitTimeout" 30 >))' daq/segments/setup.data.xml
```

### 3.7 Path Query

bash  

```bash
oks_dump --path "initial@Segment" '(path-to "common-environment@Segment" (direct "Segments"))' daq/segments/setup.data.xml
```

### 3.8 Query Grammar Rules

Table 

| Query TypeSyntaxNotes |                                         |                                       |
| --------------------- | --------------------------------------- | ------------------------------------- |
| All objects of class  | (omit `-q`) or use empty query          | `-c Application` alone                |
| Single object by ID   | `(this (object-id "id" =))`             | Must wrap in `this`                   |
| All matching ID       | `(all (object-id "prefix.*" ~=))`       | Regex on ID                           |
| Attribute filter      | `(all ("attr" value op))`               | `=`, `!=`, `~=`, `>`, `<`, `>=`, `<=` |
| Relationship          | `(all ("rel" some (object-id "id" =)))` | `some` = at least one                 |
| Logical AND           | `(all (and (cond1) (cond2)))`           | Both must match                       |
| Logical OR            | `(all (or (cond1) (cond2)))`            | Either matches                        |
| Logical NOT           | `(all (not (cond)))`                    | Negation                              |

> **Critical Rule:** Every query string must start with `all` or `this`. `(object-id "x" =)` alone is **invalid** and crashes.

---

## 4. Python API: `config` Module

The `config` module is located at `$TDAQ_INST_PATH/lib/python`.

### 4.1 Basic Setup and Count Objects

bash  

```bash
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config

cfg = config.Configuration("oksconfig:daq/segments/setup.data.xml")
apps = cfg.get_objs("Application")
print("Total applications:", len(apps))
PYEOF
```

### 4.2 List Objects Safely

`name` is not a universal OKS attribute. In particular, a `CustomLifetimeApplication` can be returned by `get_objs("Application")` but does not have an attribute literally named `name`. An OKS object ID and an OKS attribute are different things.

bash  

```bash
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config

cfg = config.Configuration("oksconfig:daq/segments/setup.data.xml")
apps = cfg.get_objs("Application")

for app in apps[:5]:
    # Safe: prints the ConfigObject representation without assuming a `name` field.
    print(app)
PYEOF
```

### 4.3 Get Single Object by UID

The OKS object ID/UID is the database identifier of the object itself, such as `CHIP`, `RDB`, or `MTS` in the DAQ data files. It is not the same thing as an arbitrary Python attribute like `name`.

bash  

```bash
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config

cfg = config.Configuration("oksconfig:daq/segments/setup.data.xml")

# Real object IDs in this data set include names such as CHIP, DDC, MTS, RDB.
try:
    app = cfg.get_obj("IPCServiceApplication", "CHIP")
    print("Found:", app)
    print("UID:", app.UID())
except Exception as e:
    print("Not found:", e)
PYEOF
```

> **Important:** `get_obj()` expects the concrete OKS object ID, not a "display name" or a Python attribute value. If the object is missing, it raises an exception.

### 4.4 Query with OKS Query String

OKS query strings are evaluated by the native backend. Use real schema members from the class hierarchy (`Parameters` is a real inherited attribute; `RunsOn` is a real relationship). Avoid assumptions such as a universal `name` attribute.

bash  

```bash
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config

cfg = config.Configuration("oksconfig:daq/segments/setup.data.xml")

# Real attribute from Application / its subclasses
apps = cfg.get_objs("Application", '(all ("Parameters" ".*" ~=))')
print("Parameterized apps:", len(apps))

# Real relationship query: find apps assigned to a specific host
host = "pc-tbed-onl-03.cern.ch"
apps_on_host = cfg.get_objs(
    "Application",
    '(all ("RunsOn" some (object-id "%s" =)))' % host,
)
print("Apps on %s:" % host, len(apps_on_host))
PYEOF
```

If you do not know the host in advance, the safe Python-side pattern is to test the relationship explicitly:

```python
for app in cfg.get_objs("Application"):
    if app['RunsOn'] is not None:
        print(app.UID(), "->", app['RunsOn'].UID())
```

### 4.5 Filter by Timeout in Python

> **Note:** Numeric `>` in query strings may not be supported in all backends. Python-side filtering is the safest fallback.

bash  

```bash
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config

cfg = config.Configuration("oksconfig:daq/segments/setup.data.xml")
apps = cfg.get_objs("Application")

for app in apps:
    try:
        t = int(app['InitTimeout'])
        if t > 30:
            print(app, ":", t, "s")
    except Exception:
        pass
PYEOF
```

### 4.6 Schema Introspection

bash  

```bash
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config

cfg = config.Configuration("oksconfig:daq/segments/setup.data.xml")

print("Classes:", cfg.classes()[:10])
print("Application attributes:", list(cfg.attributes("Application").keys()))
print("Application relations:", list(cfg.relations("Application").keys()))
PYEOF
```

### 4.7 Relationship Traversal

bash  

```bash
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config

cfg = config.Configuration("oksconfig:daq/segments/setup.data.xml")
apps = cfg.get_objs("Application")

for app in apps[:3]:
    print("App:", app)
    try:
        host = app['RunsOn']
        print("  RunsOn:", host)
    except Exception:
        print("  No RunsOn relation")
PYEOF
```

### 4.8 Historical Version via Connection String

The `version=` connection-string option is passed to `OksKernel` in the same way as the C++ constructor argument. It selects a revision only when OKS is allowed to create its own checkout; unset `TDAQ_DB_USER_REPOSITORY` first.

bash  

```bash
unset TDAQ_DB_USER_REPOSITORY
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config

cfg = config.Configuration(
    "oksconfig:daq/segments/setup.data.xml&version=tag:r454833@ATLAS"
)
print("Historical apps:", len(cfg.get_objs("Application")))
PYEOF
```

### 4.9 Python API Reference

Table 

| TaskCode                        |                                                            |
| ------------------------------- | ---------------------------------------------------------- |
| Open DB                         | `cfg = config.Configuration("oksconfig:file.xml")`         |
| List classes                    | `cfg.classes()`                                            |
| List attributes                 | `cfg.attributes("Application")`                            |
| List relations                  | `cfg.relations("Application")`                             |
| Get all objects                 | `cfg.get_objs("Application")`                              |
| Get with query                  | `cfg.get_objs("Application", '(query-string)')`            |
| Get one object                  | `cfg.get_obj("Application", "uid")`                        |
| Print an object safely          | `print(app)`                                               |
| Read an actual schema attribute | `app['Parameters']` (only after checking the class schema) |
| Read relation                   | `app['RunsOn']`                                            |
| Historical version              | `config.Configuration("oksconfig:file&version=tag:x")`     |

> **Important:** Use `get_objs()`, not `get_objects()`. Do not assume `obj['name']` exists; access only attributes/relations that the object's class (including inherited members) declares.

---

## 5. Native C++ API

### 5.1 Create Work Area (Run Once)

bash  

```bash
mkdir -p ~/tdaq-cpp-work/oks-query-demo/src
cd ~/tdaq-cpp-work/oks-query-demo
```

### 5.2 Package CMakeLists.txt

> **Rule:** TDAQ packages use `tdaq_package()`, **NOT** `project()` or `cmake_minimum_required()`.

bash  

```bash
cat > ~/tdaq-cpp-work/oks-query-demo/CMakeLists.txt << 'EOF'
tdaq_package()
tdaq_add_executable(oks_query_demo src/main.cpp)
target_link_libraries(oks_query_demo PRIVATE oks config)
EOF
```

### 5.3 Top-Level CMakeLists.txt

bash  

```bash
cat > ~/tdaq-cpp-work/CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.25.0)
project(work)
find_package(TDAQ)
include(CTest)
tdaq_work_area()
EOF
```

### 5.4 Example 1: List All Objects

Use `nano` to create the file (do NOT paste C++ into bash directly):

bash  

```bash
nano ~/tdaq-cpp-work/oks-query-demo/src/main.cpp
```

Type this inside nano:

cpp  

```cpp
#include <oks/kernel.h>
#include <oks/query.h>
#include <oks/object.h>
#include <iostream>

int main() {
    OksKernel kernel;
    kernel.load_file("daq/schema/core.schema.xml");
    kernel.load_file("daq/segments/setup.data.xml");

    // Use a concrete class. Application is abstract and has no direct objects.
    OksClass* c = kernel.find_class("IPCServiceApplication");
    if (!c) {
        std::cerr << "No IPCServiceApplication class" << std::endl;
        return 1;
    }

    std::cout << "=== IPCServiceApplication objects ===" << std::endl;
    if (const OksObject::Map* objs = c->objects()) {
        for (const auto& pair : *objs) {
            std::cout << "  " << pair.second->GetId() << std::endl;
        }
    }

    return 0;
}
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

Build and run:

bash  

```bash
cd ~/tdaq-cpp-work
cmake -B build
cmake --build build -j 4
./build/oks-query-demo/oks_query_demo
```

### 5.5 Example 2: Query with Attribute Filter

> **Output rule for C++:** `OksClass::objects()` contains objects directly of that class. It will be empty when called on abstract `Application`. Use a concrete class for direct listing, or use a query execution method with its subclass-search semantics verified for the installed OKS release.

bash  

```bash
nano ~/tdaq-cpp-work/oks-query-demo/src/main.cpp
```

cpp  

```cpp
#include <oks/kernel.h>
#include <oks/query.h>
#include <oks/object.h>
#include <iostream>

int main() {
    OksKernel kernel;
    kernel.load_file("daq/schema/core.schema.xml");
    kernel.load_file("daq/segments/setup.data.xml");

    OksClass* c = kernel.find_class("IPCServiceApplication");
    if (!c) {
        std::cerr << "No IPCServiceApplication class" << std::endl;
        return 1;
    }

    std::cout << "=== Apps with InitTimeout > 30 ===" << std::endl;
    OksQuery q(c, "all (InitTimeout 30 >)");
    if (q.good()) {
        OksObject::List* r = c->execute_query(&q);
        if (r) {
            for (auto it = r->begin(); it != r->end(); ++it) {
                std::cout << "  " << (*it)->GetId() << std::endl;
            }
            delete r;
        }
    } else {
        std::cerr << "Invalid query" << std::endl;
    }

    return 0;
}
```

bash  

```bash
cd ~/tdaq-cpp-work
cmake --build build -j 4
./build/oks-query-demo/oks_query_demo
```

### 5.6 Example 3: Relationship Query

cpp  

```cpp
#include <oks/kernel.h>
#include <oks/query.h>
#include <oks/object.h>
#include <iostream>

int main() {
    OksKernel kernel;
    kernel.load_file("daq/schema/core.schema.xml");
    kernel.load_file("daq/segments/setup.data.xml");

    OksClass* c = kernel.find_class("IPCServiceApplication");
    if (!c) {
        std::cerr << "No IPCServiceApplication class" << std::endl;
        return 1;
    }

    std::cout << "=== Apps running on pc-tbed-onl-03 ===" << std::endl;
    OksQuery q(c, R"(all (RunsOn some (object-id "pc-tbed-onl-03.cern.ch" =)))");
    if (q.good()) {
        OksObject::List* r = c->execute_query(&q);
        if (r) {
            for (auto it = r->begin(); it != r->end(); ++it) {
                std::cout << "  " << (*it)->GetId() << std::endl;
            }
            delete r;
        }
    }

    return 0;
}
```

### 5.7 Example 4: Nested Logical Query (AND)

cpp  

```cpp
#include <oks/kernel.h>
#include <oks/query.h>
#include <oks/object.h>
#include <iostream>

int main() {
    OksKernel kernel;
    kernel.load_file("daq/schema/core.schema.xml");
    kernel.load_file("daq/segments/setup.data.xml");

    OksClass* c = kernel.find_class("IPCServiceApplication");
    if (!c) { std::cerr << "No class" << std::endl; return 1; }

    std::cout << "=== Applications with Parameters and InitTimeout > 30 ===" << std::endl;
    OksQuery q(c, R"(all (and (Parameters ".*" ~=) (InitTimeout 30 >)))");
    if (q.good()) {
        OksObject::List* r = c->execute_query(&q);
        if (r) {
            for (auto it = r->begin(); it != r->end(); ++it) {
                std::cout << "  " << (*it)->GetId() << std::endl;
            }
            delete r;
        }
    }

    return 0;
}
```

### 5.8 Example 5: Git Version in Constructor

This example shows how OKS chooses a Git revision at runtime. It is not about rebuilding the program; changing the revision selector only changes which configuration files the same binary reads.

Two environment variables control the repository mode:

`TDAQ_DB_REPOSITORY`
: Enables the git-backed OKS repository and stores the repository URL(s) configured by the release. If this variable is not set, OKS falls back to filesystem repositories.

`TDAQ_DB_USER_REPOSITORY`
: Points to an existing working copy that OKS should use directly. When it is set, OKS does not create a temporary checkout and ignores the constructor selector and `TDAQ_DB_VERSION` for that process.

The constructor argument after `oks_query_demo` is a **version selector** for automatic checkout mode only. Use one of these forms:

```text
hash:<commit-hash>   # exact commit; use this when no tag exists
date:<date-or-timestamp>   # latest commit at or before the given date
tag:<tag-name>       # exact Git tag name in the repository
```

If no selector is provided, OKS uses the latest revision available in the configured repository. If a tag, hash, or date does not resolve to an existing revision, the checkout fails; there is no automatic fallback to another selector type.

The safest workflow is:

1. Use automatic checkout for one-off reads.
2. Use `hash:` when you want a precise revision and no matching tag exists.
3. Use `date:` when you want the latest revision not newer than a known timestamp.
4. Use `tag:` only after validating that the tag exists in the repository.

To make the constructor argument take effect, keep `TDAQ_DB_REPOSITORY` enabled by the release and unset `TDAQ_DB_USER_REPOSITORY`. The kernel then creates a temporary checkout at the requested revision and removes it when destroyed.

cpp  

```cpp
#include <oks/kernel.h>
#include <oks/object.h>
#include <iostream>

int main(int argc, char* argv[]) {
    const char* version = (argc > 1) ? argv[1] : nullptr;

    // 5th argument is an OKS configuration Git selector.
    // Applied only when OKS creates its own checkout (no TDAQ_DB_USER_REPOSITORY).
    OksKernel kernel(false, false, false, true, version);

    kernel.load_file("daq/schema/core.schema.xml");
    kernel.load_file("daq/segments/setup.data.xml");

    OksClass* c = kernel.find_class("IPCServiceApplication");
    if (c) {
        if (const OksObject::Map* objs = c->objects()) {
            std::cout << "Loaded " << objs->size() << " applications" << std::endl;
        }
    }

    return 0;
}
```

Build and run:

bash  

```bash
cd ~/tdaq-cpp-work
cmake --build build -j 4

# Runtime configuration selection: no rebuild needed when changing only this value.
# `env -u` affects this program only; it does not change your current shell.
env -u TDAQ_DB_USER_REPOSITORY \
  ./build/oks-query-demo/oks_query_demo "tag:r454833@ATLAS"

# Equivalent alternatives:
# ./build/oks-query-demo/oks_query_demo "hash:6800fe3b"
# ./build/oks-query-demo/oks_query_demo "date:2024-06-15"

# No selector: use the latest revision from the configured repository.
env -u TDAQ_DB_USER_REPOSITORY \
    ./build/oks-query-demo/oks_query_demo
```

Do not assume `r454833@ATLAS` exists in every repository. Discover and validate a tag with `git tag -l` and `git rev-parse "refs/tags/<tag-name>"`; otherwise use a known hash.

If you want to compare actual configuration results across revisions, run the same query against each selector. For example, the following command checks the same class/query pair under three different revisions:

bash  

```bash
for version in "tag:r454833@ATLAS" "hash:6800fe3b" "date:2024-06-15"; do
    echo "== $version =="
    env -u TDAQ_DB_USER_REPOSITORY TDAQ_DB_VERSION="$version" \
      oks_dump -c IPCServiceApplication -q '(all ("Parameters" ".*" ~=))' daq/segments/setup.data.xml
done
```

If you are using `oks_dump` or another query tool instead of the demo binary, the same revision selector rules apply: run the query once for each revision you want to compare, and keep `TDAQ_DB_USER_REPOSITORY` unset so the selector is actually used.

### 5.9 C++ API Reference

Table 

| TaskCode                                         |                                                                                             |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| Create kernel                                    | `OksKernel kernel;`                                                                         |
| Load schema                                      | `kernel.load_file("daq/schema/core.schema.xml");`                                           |
| Load data                                        | `kernel.load_file("daq/segments/setup.data.xml");`                                          |
| Find a concrete class                            | `OksClass* c = kernel.find_class("IPCServiceApplication");`                                 |
| List all objects                                 | `if (const OksObject::Map* objs = c->objects()) { for (const auto& pair : *objs) { ... } }` |
| Object ID                                        | `pair.second->GetId()`                                                                      |
| Create query                                     | `OksQuery q(c, "all (InitTimeout 30 >)");`                                                  |
| Validate query                                   | `if (q.good()) { ... }`                                                                     |
| Execute query                                    | `OksObject::List* r = c->execute_query(&q);`                                                |
| Iterate results                                  | `for (auto it = r->begin(); it != r->end(); ++it)`                                          |
| Cleanup                                          | `delete r;`                                                                                 |
| Configuration revision (automatic checkout only) | `OksKernel kernel(false,false,false,true,"hash:6800fe3b");`                                 |

> **Critical:** Always check `q.good()` before `execute_query()`. Invalid query strings are rejected by the parser, and execution should only happen after validation.

---

## 6. Git Version Control

### 6.1 Check Current Settings

bash  

```bash
echo $TDAQ_DB_REPOSITORY
echo $TDAQ_DB_VERSION
oks-git-status
```

### 6.2 Selecting a Version for an Automatic Checkout

`TDAQ_DB_VERSION` is read when OKS creates a temporary user checkout. It does not change an existing `OksKernel`, and it does not switch a checkout named by `TDAQ_DB_USER_REPOSITORY`.

bash  

```bash
# Do not point OKS at an existing clone for this mode.
unset TDAQ_DB_USER_REPOSITORY
export TDAQ_DB_VERSION="hash:6800fe3b"

# Start a new program/process after changing the requested revision.
oks_dump -c IPCServiceApplication daq/segments/setup.data.xml
```

For a C++ program that supplies the version to `OksKernel`, prefer a process-scoped unset:

bash  

```bash
env -u TDAQ_DB_USER_REPOSITORY \
  ./build/oks-query-demo/oks_query_demo "hash:6800fe3b"
```

Use this mode for one-off historical reads. Use exactly one selector at a time:

bash  

```bash
export TDAQ_DB_VERSION="hash:6800fe3b"       # a known commit; recommended when no tag exists
export TDAQ_DB_VERSION="date:2024-06-15"     # latest commit before this date
export TDAQ_DB_VERSION="tag:r454833@ATLAS"   # only if this tag exists
```

### 6.3 Using a Persistent Clone (Optional)

Use this mode when you need a persistent working copy for editing, repeated inspection, or repository operations. Here Git — not `TDAQ_DB_VERSION` and not the C++ constructor argument — chooses the revision.

Never run `git checkout` in a directory while an OKS process is reading from it; finish the process first.

bash  

```bash
cd ~/tdaq-config
git fetch --tags
git switch --detach 6800fe3b        # or: git switch --detach "r454833@ATLAS"
git rev-parse HEAD                  # record the exact revision actually selected
export TDAQ_DB_USER_REPOSITORY="$PWD"
export TDAQ_DB_PATH="$PWD"
```

To create such a clone with the OKS utility instead:

bash  

```bash
cd "$(oks_clone_repository --version hash:6800fe3b)"
git rev-parse HEAD
export TDAQ_DB_USER_REPOSITORY="$PWD"
export TDAQ_DB_PATH="$PWD"
```

`oks_clone_repository --version` accepts `hash:`, `date:`, and `tag:`.

### 6.4 Mode Comparison

Table 

| NeedRecommended modeReason                           |                                                                                  |                                                                              |
| ---------------------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Read one historical revision once                    | Constructor argument or `TDAQ_DB_VERSION`, with `TDAQ_DB_USER_REPOSITORY` absent | OKS creates an isolated temporary checkout; no manual Git switch is required |
| Repeatedly inspect one chosen revision               | Set `TDAQ_DB_USER_REPOSITORY` to a persistent clone at that revision             | Avoids a new clone for every run; you can inspect its `HEAD` with Git        |
| Compare two revisions in one program or concurrently | Two distinct persistent clones/worktrees, or two automatic-checkout kernels      | Each kernel/process has an independent, stable set of XML files              |
| Edit, commit, update, or tag configuration           | A persistent clone named by `TDAQ_DB_USER_REPOSITORY`                            | These repository operations intentionally act on that working copy           |

The C++ API is not required for version selection: the same repository rules apply to `oks_dump` and the Python `oksconfig` backend. Use C++ when your application needs native integration or long-lived in-memory object/query access — not merely because a version must be selected.

### 6.5 Switching Revisions While the Program Is Running

An `OksKernel` contains the schema and objects it loaded; changing an environment variable cannot retarget that existing kernel. For a new revision, destroy the old kernel and construct/load a new one, or run a new process. For a persistent clone, make the Git switch only after the old kernel/process is finished. For two revisions at once, use separate checkouts (or automatic temporary checkouts) and separate kernels.

No rebuild is necessary for any of these configuration revision changes. Rebuild/reconfigure only when changing the TDAQ software release selected by `cm_setup`, because that can change the headers and libraries used by the executable.

### 6.6 Commit Changes

bash  

```bash
cd $TDAQ_DB_USER_REPOSITORY
oks-commit.sh -m "Updated timeout values" -u `pwd`
```

Or raw git:

bash  

```bash
git add daq/segments/setup.data.xml
git commit -m "Updated timeout values"
git push origin master
```

### 6.7 Disable Git Mode

bash  

```bash
oks-git-off
```

### 6.8 Re-enable Git Mode

bash  

```bash
oks-git-on
```

---

## 7. CMake Work Area

### 7.1 Structure for Your AI Project

plain  

```plain
tdaq-ai-work/
├── CMakeLists.txt                 # Top-level work area
├── build/                         # cmake -B build
├── installed/                     # make install
└── tdaq-nlp-ai/
    ├── CMakeLists.txt             # Package
    ├── src/                       # C++ source
    ├── python/                    # Python modules
    │   ├── nlp_query.py
    │   ├── schema_introspector.py
    │   ├── query_generator.py
    │   ├── query_validator.py
    │   └── query_executor.py
    └── tests/
        └── test_queries.py
```

### 7.2 Top-Level CMakeLists.txt

bash  

```bash
cat > ~/tdaq-ai-work/CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.25.0)
project(work)
find_package(TDAQ)
include(CTest)
tdaq_work_area()
EOF
```

### 7.3 Package CMakeLists.txt

bash  

```bash
mkdir -p ~/tdaq-ai-work/tdaq-nlp-ai/python
cat > ~/tdaq-ai-work/tdaq-nlp-ai/CMakeLists.txt << 'EOF'
tdaq_package()
tdaq_add_python_package(tdaq_nlp_ai)
tdaq_add_scripts(python/nlp_query.py)
EOF
```

### 7.4 Build and Install

bash  

```bash
cd ~/tdaq-ai-work
cmake -B build
cmake --build build -j 4
cmake --build build --target install
```

### 7.5 Activate Local Installation

bash  

```bash
cd ~/tdaq-ai-work
. installed/setup.sh
```

---

## 8. Troubleshooting

Table 

| ErrorCauseFix                                                           |                                                       |                                                                                                         |
| ----------------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `Cannot find possible release candidate`                                | Typed wrong version or cached env var                 | Use `cm_setup prod` in a fresh shell                                                                    |
| `oks_dump: command not found`                                           | Environment not loaded                                | Run `cm_setup prod`                                                                                     |
| `Query can only be executed when class name is provided`                | Used `-q` without `-c`                                | Add `-c Application`                                                                                    |
| `the first token must be 'all' or 'this'`                               | Query string missing wrapper                          | Use `(this (object-id "x" =))` not `(object-id "x" =)`                                                  |
| `bad query syntax`                                                      | Invalid query grammar                                 | Check attribute names with schema dump                                                                  |
| `AttributeError: 'Configuration' object has no attribute 'get_objects'` | Wrong method name                                     | Use `get_objs()`                                                                                        |
| `AttributeError: 'ConfigObject' object has no attribute 'get_ID'`       | Do not guess object-ID APIs                           | Use `print(obj)` first; inspect the installed API with `dir(obj)` before relying on an ID accessor      |
| `KeyError: 'name'`                                                      | `name` is not a universal OKS attribute               | Use `print(obj)` or inspect `cfg.attributes(class_name)`; access only declared attributes               |
| `oks_dump -f` prints only XML paths                                     | `-f` is files-only mode                               | Remove `-f` from object/query commands; leave the XML data filename as the final positional argument    |
| C++ `c->objects()` is empty                                             | Selected class is abstract or has no direct instances | Use a concrete class such as `IPCServiceApplication`; inspect/verify subclass-query behavior separately |
| `class OksObject has no member named 'get_id'`                          | Wrong C++ method                                      | Use `GetId()` (capital G, capital I)                                                                    |
| `Segmentation fault` on query                                           | Executed bad query without `good()` check             | Always `if (q.good())` before `execute_query()`                                                         |
| `Query "all"` parse error                                               | `"all"` is not a valid query                          | Use `c->objects()` to list all                                                                          |
| `unable to open X server`                                               | Pasted Python into bash                               | Use `python3 << 'PYEOF'` wrapper                                                                        |
| `syntax error near unexpected token`                                    | Pasted CMake/C++ into bash                            | Use `nano` or `cat > file << 'EOF'`                                                                     |
| `event not found`                                                       | `!` inside bash double quotes                         | Use `nano` for C++ files                                                                                |
| `missing terminating " character`                                       | `\n` became real newline                              | Use `std::endl` instead of `\n` in file writes                                                          |
| `can't open display`                                                    | `oks_data_editor` needs X11                           | Use `ssh -Y` or stick to `oks_dump`                                                                     |

---

## 9. Daily Workflow Cheat Sheet

bash  

```bash
# 1. SSH and setup
ssh adhikari@lxplus.cern.ch
cm_setup prod

# 2. Quick CLI query
oks_dump -c IPCServiceApplication daq/segments/setup.data.xml | head -n 20

# 3. Python introspection
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config
cfg = config.Configuration("oksconfig:daq/segments/setup.data.xml")
print("Apps:", len(cfg.get_objs("Application")))
print("Attrs:", list(cfg.attributes("Application").keys()))
PYEOF

# 4. Python filter by timeout
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, os.environ['TDAQ_INST_PATH'] + '/lib/python')
import config
cfg = config.Configuration("oksconfig:daq/segments/setup.data.xml")
for app in cfg.get_objs("Application"):
    try:
        if int(app['InitTimeout']) > 30:
            print(app, ":", app['InitTimeout'], "s")
    except: pass
PYEOF

# 5. C++ build
cd ~/tdaq-cpp-work
cmake --build build -j 4
./build/oks-query-demo/oks_query_demo

# 6. Configuration Git revision (runtime data selection, not a C++ rebuild)
# This uses an automatic temporary checkout. Use a hash if no tag exists.
env -u TDAQ_DB_USER_REPOSITORY TDAQ_DB_VERSION="hash:6800fe3b" \
  oks_dump -c IPCServiceApplication daq/segments/setup.data.xml
```

---

## Appendix: Query Syntax Quick Reference

### OKS Query Grammar (Same for CLI, Python, and C++)

plain  

```plain
query := all predicate | this predicate
predicate := (attribute value comparator)
          | (attribute value ~=)           # regex
          | (relation some predicate)
          | (relation all predicate)
          | (and predicate predicate)
          | (or predicate predicate)
          | (not predicate)
          | (object-id "id" =)
          | (object-id "pattern" ~=)

comparator := = | != | > | < | >= | <=
```

### Examples by Complexity

Table 

| GoalCLI / Python StringC++ String      |                                              |                                                                             |
| -------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------- |
| All direct objects of a concrete class | (omit query)                                 | use `c->objects()` with `IPCServiceApplication`, not abstract `Application` |
| By exact ID                            | `(this (object-id "x" =))`                   | `"this (object-id \"x\" =)"`                                                |
| Parameters regex                       | `(all ("Parameters" ".*" ~=))`             | `"all (Parameters \".*\" ~=)"`                                              |
| Timeout > 30                           | `(all ("InitTimeout" 30 >))`                 | `"all (InitTimeout 30 >)"`                                                  |
| Runs on host                           | `(all ("RunsOn" some (object-id "host" =)))` | `"all (RunsOn some (object-id \"host\" =))"`                                |
| AND condition                          | `(all (and (A) (B)))`                        | `"all (and (A) (B))"`                                                       |
| OR condition                           | `(all (or (A) (B)))`                         | `"all (or (A) (B))"`                                                        |

> **C++ Note:** In C++ query strings, quotes inside the string must be escaped as `\"`.
