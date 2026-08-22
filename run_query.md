# OKS Query Guide — Running Queries in ATLAS TDAQ

> A step-by-step guide for running OKS (Object Kernel Support) queries,
> starting from logging into CERN computing resources.
>
> Source repository: https://gitlab.cern.ch/atlas-tdaq-software/oks

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Step 1: SSH into CERN](#2-step-1--ssh-into-cern)
3. [Step 2: Set up the TDAQ Environment](#3-step-2--set-up-the-tdaq-environment)
4. [OKS Query Syntax Reference](#4-oks-query-syntax-reference)
5. [Method A: Command Line (`oks_dump`)](#5-method-a--command-line-oks_dump)
6. [Method B: Python (`config` package)](#6-method-b--python-config-package)
7. [Method C: C++ API](#7-method-c--c-api)
8. [Troubleshooting](#8-troubleshooting)
9. [References](#9-references)

---

## 1. Prerequisites

| Requirement | Details |
|---|---|
| CERN account | Needed for SSH and CERN Single Sign-On |
| SSH client | Any standard SSH client |
| ATLAS/TDAQ membership | Access to the TDAQ software release & configuration repositories |
| An OKS data file | A `*.data.xml` file (or access to the OKS Git repository) you want to query |

---

## 2. Step 1 — SSH into CERN

Log in to the CERN interactive farm (LXPLUS) or a TDAQ development node:

```bash
ssh <your_username>@lxplus.cern.ch
```

If you need a TDAQ-specific machine (e.g. TestBed or Point-1 nodes), follow your group's instructions — the commands below are the same.

---

## 3. Step 2 — Set up the TDAQ Environment

OKS tools are **not** installed in system paths. They live in the ATLAS TDAQ release on CVMFS. Before using any method below, you must source the release setup script.

```bash
# Example — replace with YOUR team's release setup script!
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/<your-release>/setup.sh
```

> ❗ **If you don't know the path:** ask your supervisor/team for
> *"the setup script for our current TDAQ release"*, or check whether your
> project working directory already contains a `setup.sh` and run
> `source setup.sh` there.

After sourcing, verify the tools are available:

```bash
which oks_dump        # should print a path
python -c "import config; print(config.__file__)"   # should print a path (no error)
```

### Useful environment variables

| Variable | Purpose |
|---|---|
| `TDAQ_DB_PATH` | Colon-separated filesystem repositories (file-based access) |
| `TDAQ_DB_REPOSITORY` | Git URL(s) of the OKS repository (git-based access) |
| `TDAQ_DB_USER_REPOSITORY` | Your local checkout of the repository |

For a local file-based query, the simplest approach:

```bash
export TDAQ_DB_PATH=/path/to/directory/with/your/xml/files:$TDAQ_DB_PATH
```

---

## 4. OKS Query Syntax Reference

All three methods (CLI, Python, C++) use the **same query string syntax** —
Lisp-style S-expressions parsed by `src/query.cpp` in the `oks` package.

```
( <all | this> <expression> )
```

- `all` → search this class **and all subclasses**
- `this` → search **only** this class

### Expressions

| Type | Syntax | Example |
|---|---|---|
| Attribute comparison | `( "<attribute>" "<value>" <cmp> )` | `( "status" "active" = )` |
| Object-ID comparison | `( object-id "<id>" <cmp> )` | `( object-id "test" = )` |
| Logical AND | `( and <expr1> <expr2> ... )` | `( and ( "status" "active" = ) ( "version" "2" > ) )` |
| Logical OR | `( or <expr1> <expr2> ... )` | `( or ( "a" "1" = ) ( "b" "2" = ) )` |
| Logical NOT | `( not <expr> )` | `( not ( "status" "active" = ) )` |
| Relationship | `( "<rel-name>" <some | all> <expr> )` | `( "RunsOn" some ( object-id "lxplus001.cern.ch" = ) )` |

### Comparators

| Symbol | Meaning |
|---|---|
| `=` | equal |
| `!=` | not equal |
| `<` / `>` | less / greater |
| `<=` / `>=` | less-or-equal / greater-or-equal |
| `~=` | regular expression match |

### Complete examples (from OKS release notes)

```text
# All objects (incl. subclasses) referencing object "test" via "my-relationship"
(all ("my-relationship" some (object-id "test" =)))

# All applications running on host lxplus001.cern.ch
(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))
```

---

## 5. Method A — Command Line (`oks_dump`)

**Fastest way to run a query — no code needed.**
Implementation: `bin/oks_dump.cpp` in the `oks` repository.

### Basic syntax

```bash
oks_dump -c <ClassName> -q '<query>' <data_file.xml>
```

| Option | Meaning |
|---|---|
| `-c` / `--class` | Class to search |
| `-q` / `--query` | Query string (requires `-c`) |
| `-f` | Just print/check the files |
| `-r` | Also print objects referenced by found objects |
| `--path "<obj>" "<path-query>"` | Path query between two objects |

### Examples

```bash
# All objects of a class
oks_dump -c Application daq/my.data.xml

# Query: attribute equality
oks_dump -c MyClass -q '(all ("status" "active" =))' daq/my.data.xml

# Query: find everything running on a host
oks_dump -c Application -q '(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))' daq/my.data.xml

# Path query example
oks_dump --path "my-partition@Partition" \
  '(path-to "my-app@RunControlApplication" (direct "Segments" "Applications"))' \
  daq/partitions/my.data.xml
```

### Return (exit) codes

| Code | Meaning |
|---|---|
| 0 | OK |
| 1 | Bad command line parameter |
| 2 | Bad OKS file(s) |
| 3 | Bad query (syntax error) |
| 4 | Class not found |
| 5 | Dangling references in loaded data |

---

## 6. Method B — Python (`config` package)

**Best for scripting and interactive work — nothing to compile.**
The Python bindings live in the TDAQ `config` package
(named `conffwk` in the DUNE-DAQ fork). The key method is
`Configuration.get_objs(class_name, query)`.

### Step 1 — Make sure the environment is set up (Section 3)

```bash
python -c "import config"   # must not raise an error
```

### Step 2 — Write the script

Create `run_query.py`:

```python
#!/usr/bin/env python
# run_query.py — run an OKS query from Python

import config   # use "import conffwk as config" on DUNE-DAQ

# 1. Open the OKS database
db = config.Configuration("oksconflibs:daq/my.data.xml")
#    Older ATLAS releases may use:  "oksconfig:daq/my.data.xml"

# 2. Run the query: get_objs(class_name, query_string)
query  = '(all ("status" "active" =))'
results = db.get_objs("MyClass", query)

# 3. Process the answers
print(f"Found {len(results)} matching objects")
for obj in results:
    print(" ->", obj.UID())
```

### Step 3 — Run it

```bash
python run_query.py
```

### Other useful Python methods

```python
db.classes()                          # list all classes
db.get_obj("MyClass", "some-id")      # one object by ID
db.get_dal("MyClass", "some-id")      # pythonic object: dal_obj.Name, ...
db.get_dals("MyClass")                # all objects of a class as DAL objects
db.get_objs("MyClass")                # all objects (empty query)
```

> 💡 **Tip:** validate your query string first with
> `oks_dump -c MyClass -q '<query>' file.xml` — both use the same parser.

---

## 7. Method C — C++ API

**For integrating queries into a compiled application.**
Core files: `oks/query.h`, `src/query.cpp`, `src/index.cpp`.

### Step 1 — Create `main.cpp`

```cpp
#include <iostream>
#include <string>
#include "oks/kernel.h"
#include "oks/query.h"

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <database.xml> <ClassName>\n";
        return 1;
    }

    try {
        // 1. Load the database
        oks::Kernel kernel;
        kernel.load_data(argv[1]);

        // 2. Get the target class
        OksClass* my_class = kernel.find_class(argv[2]);
        if (!my_class) {
            std::cerr << "Class not found\n";
            return 1;
        }

        // 3. Build the query
        OksQuery* query = new OksQuery(my_class, "(all (\"status\" \"active\" =))");

        // 4. Validate + execute
        if (query->good()) {
            OksObject::List* results = my_class->execute_query(query);
            if (results && !results->empty()) {
                std::cout << "Found " << results->size() << " objects\n";
                for (auto it = results->begin(); it != results->end(); ++it)
                    std::cout << " -> " << (*it)->GetId() << "\n";
            } else {
                std::cout << "No objects matched.\n";
            }
        } else {
            std::cerr << "Query syntax is invalid!\n";
        }
        delete query;
    }
    catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```

### Step 2 — Create `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.14)
project(MyOksQueryApp CXX)
set(CMAKE_CXX_STANDARD 17)

find_package(Oks REQUIRED)            # found via the TDAQ release setup
add_executable(run_query main.cpp)
target_link_libraries(run_query PRIVATE oks)
```

### Step 3 — Build and run

```bash
mkdir build && cd build
cmake ..
make
./run_query /path/to/my.data.xml MyClass
```

### How it works internally

```
OksQuery(class, string)          → parses S-expression into expression tree
OksClass::execute_query(q)       → tries index lookup first (src/index.cpp),
                                   otherwise scans all objects
OksObject::SatisfiesQueryExpression(q) → recursively evaluates each object
returns OksObject::List*         → the query answer
```

---

## 8. Troubleshooting

| Problem | Cause / Fix |
|---|---|
| `oks_dump: command not found` | TDAQ environment not sourced — see Section 3 |
| `ImportError: No module named config` | Python bindings not on `PYTHONPATH` — re-source the release setup |
| Exit code 3 (CLI) or `Can't create query` | Query string syntax error — check Section 4; tokens are space-separated, strings in `"..."` |
| Exit code 4 / `Class not found` | Wrong class name — list classes with `oks_dump -f <file>` or Python `db.classes()` |
| `cannot open file` | Wrong path to the XML file, or missing `TDAQ_DB_PATH` |
| CMake: `find_package(Oks)` fails | Environment not sourced, or adjust target name (`oks`, `Oks::oks`, `OKS`) to your release |
| Dangling references warning | Included files missing — load the full set of included data files |

---

## 8.5 Accessing Previous Git Versions & Historical Configurations

Every configuration ever used in a run is preserved in the **OKS Git repository**:
the run number database stores the exact commit hash, and the repository is
**tagged with the run number and partition name**. So any historical
configuration can be retrieved by run number, hash, date, or tag.

### Step 1 — Find out which version a run used

Query the Run Number database for the time window of your run:

```bash
rn_ls -c "oracle://atonr_adg/rn_r" -w ATLAS_RUN_NUMBER \
      -s '2020-07-31T12:00:00' -t '2020-08-02T12:00:00' -a '%xml'
```

| Option | Meaning |
|---|---|
| `-c` | Run Number DB connection string |
| `-w` | Working schema |
| `-s` / `-t` | Search window: start / end time (UTC, ISO 8601) |
| `-a '%xml'` | Only entries whose archived config contains XML |

The output shows per run the **Version** (e.g. `hash:6800fe3b...`),
the **Partition**, and the **Config Name** (e.g.
`daq/partitions/all_hosts.data.xml`). Copy the hash — you need it next.

### Step 2 — Clone the repository at that version

Use the `oks_clone_repository` utility with `--version`:

```bash
# By commit hash (first 4+ chars are enough, if unambiguous)
oks_clone_repository --version hash:6800fe3b

# By run tag  (runNumber@partitionName)
oks_clone_repository --version tag:r380689@all_hosts

# By date (tdaq-13-01-00 and later)
oks_clone_repository --version date:"2026-06-15"
oks_clone_repository --version date:"2 years 1 day 3 minutes ago"

# By branch
oks_clone_repository -b <branch-name>
```

The command prints the path of the checkout. Typical usage:

```bash
cd `oks_clone_repository --version hash:6800fe3b`
export TDAQ_DB_USER_REPOSITORY=`pwd`     # make oks tools use THIS checkout
```

> ⚠️ Do **not** use filesystem-relative paths for oks files from a git
> repository. Use the **repository filename** instead, e.g.
> `daq/segments/setup.data.xml`.

### Step 3 — Or pin the version via an environment variable

Instead of cloning explicitly, OKS tools honor `TDAQ_DB_VERSION`:

```bash
export TDAQ_DB_VERSION=hash:6800fe3b                # explicit revision
export TDAQ_DB_VERSION=date:'2020-07-31T16:33:59'   # latest before date
unset  TDAQ_DB_VERSION                               # back to latest (HEAD)
```

| Format | Meaning |
|---|---|
| `hash:<value>` | Select revision by explicit commit hash |
| `date:<value>` | Select the latest revision before the given date/timestamp |
| `tag:<value>` | Select a run tag (`r<run>@<partition>`) |

### Step 4 — Or use plain Git commands

```bash
# Get the repository URL and clone it
git clone `oks_git_repository` .

# Browse history
git log --oneline -20          # recent commits
git log --oneline -- daq/partitions/all_hosts.data.xml   # history of one file

# List run tags
git tag -l 'r*'

# Switch to an old version / go back to latest
git checkout <hash-or-tag>     # e.g. git checkout r380689@all_hosts
git checkout master            # back to the current configuration
```

### Step 5 — Run queries on the historical configuration

Now simply reuse Method A or Method B on the checked-out file:

```bash
# CLI
oks_dump -c Application -q '(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))' \
         daq/partitions/all_hosts.data.xml

# Python
python - <<'EOF'
import config
db = config.Configuration("oksconflibs:daq/partitions/all_hosts.data.xml")
for obj in db.get_objs("Application"):
    print(obj.UID())
EOF
```

### Quick cheat-sheet — historical configurations

```bash
# 1. Which config/hash was used for run X?
rn_ls -c "oracle://atonr_adg/rn_r" -w ATLAS_RUN_NUMBER \
      -s '<start>' -t '<end>' -a '%xml'

# 2. Get that exact configuration
cd `oks_clone_repository --version hash:<hash>`
export TDAQ_DB_USER_REPOSITORY=`pwd`

# 3. Query it
oks_dump -f daq/partitions/<partition>.data.xml
```

## 9. References

| Resource | Location |
|---|---|
| OKS source repository | https://gitlab.cern.ch/atlas-tdaq-software/oks |
| Query parser | `src/query.cpp` + `oks/query.h` |
| CLI query tool | `bin/oks_dump.cpp` |
| Python bindings | TDAQ `config` package (`python/config/Configuration.py`) |
| OKS release notes (query examples) | `doc/RELEASE_NOTES.md` in the repository |
| DUNE-DAQ fork (public mirror) | https://github.com/DUNE-DAQ/oks |

### Quick cheat-sheet

```bash
# CLI
oks_dump -c <Class> -q '(all ("<attr>" "<val>" =))' <file.xml>

# Python
import config
db = config.Configuration("oksconflibs:<file.xml>")
for o in db.get_objs("<Class>", '(all ("<attr>" "<val>" =))'):
    print(o.UID())
```

---
*Generated guide — adjust release paths and file locations to your project.*