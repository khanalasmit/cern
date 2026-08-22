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

# OKS C++ Query — Complete Setup Guide

Build a C++ program that queries the ATLAS TDAQ OKS configuration database,
using CMake. Covers: create C++ → create CMake → create build script → run.

---

## Prerequisites

SSH into CERN and source the TDAQ release (**once per terminal session**):

```bash
ssh <your_username>@lxplus.cern.ch
cd ~/private/my_tdaq_project          # or your project folder
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh
```

Verify CMake is available:
```bash
cmake --version
```

---

## Step 1 — Create the C++ source (`query_oks.cpp`)

```bash
nano query_oks.cpp
```

Paste this:

```cpp
#include <iostream>
#include <string>
#include "oks/kernel.h"
#include "oks/class.h"
#include "oks/query.h"
#include "oks/object.h"
#include "oks/file.h"

int main() {
    // 1. Initialize the OKS kernel (ATLAS TDAQ uses OksKernel)
    OksKernel kernel;

    try {
        std::string db_file = "siom/hw/computers.data.xml";

        // 2. Load the data file (repository-relative path)
        OksFile* fh = kernel.load_file(db_file.c_str());
        if (!fh) {
            std::cerr << "Failed to load file: " << db_file << "\n";
            return 1;
        }
        std::cout << "Successfully loaded: " << db_file << "\n\n";
    }
    catch (const oks::exception& e) {
        std::cerr << "OKS Exception: " << e.what() << std::endl;
        return 1;
    }
    catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return 1;
    }

    // 3. Find the target class
    OksClass* computer_class = kernel.find_class("Computer");
    if (!computer_class) {
        std::cerr << "Error: Class 'Computer' not found.\n";
        return 1;
    }

    // 4. Define the OKS query (S-expression syntax)
    std::string query_str = "(all (\"Memory\" \"1024\" >=))";
    OksQuery query(computer_class, query_str.c_str());

    if (!query.good()) {
        std::cerr << "Error: Invalid query syntax: " << query_str << std::endl;
        return 1;
    }

    // 5. Execute the query
    OksObject::List* results = computer_class->execute_query(&query);

    // 6. Print the results
    if (results && !results->empty()) {
        std::cout << "Found " << results->size() << " matching computers:\n";
        for (auto it = results->begin(); it != results->end(); ++it) {
            OksObject* obj = *it;
            std::cout << " -> Object ID: " << obj->GetId() << "\n";
        }
    } else {
        std::cout << "Query ran, but found 0 matching objects.\n";
    }

    if (results) delete results;
    return 0;
}
```

Save & exit: `Ctrl+O`, `Enter`, `Ctrl+X`.

---

## Step 2 — Create `CMakeLists.txt`

```bash
nano CMakeLists.txt
```

Paste this (it auto-detects your CPU architecture, OS version, and compiler
so it picks the correct TDAQ library folder):

```cmake
cmake_minimum_required(VERSION 3.14)
project(OksQueryApp CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ===== Change this if you switch TDAQ releases =====
set(TDAQ_VERSION "14-00-00" CACHE STRING "TDAQ release version")

set(TDAQ_ROOT        "/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-${TDAQ_VERSION}/installed")
set(TDAQ_COMMON_ROOT "/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq-common/tdaq-common-${TDAQ_VERSION}/installed")

# ===== Detect the current platform =====
# OS major version from /etc/os-release (e.g. "9" on AlmaLinux 9)
file(STRINGS "/etc/os-release" _os_release)
set(OS_MAJOR "")
foreach(_line ${_os_release})
    if(_line MATCHES "^VERSION_ID=\"?([0-9]+)")
        set(OS_MAJOR "${CMAKE_MATCH_1}")
    endif()
endforeach()
if(NOT OS_MAJOR)
    message(FATAL_ERROR "Could not detect OS version from /etc/os-release")
endif()

# Compiler major version (e.g. 15 from 15.2.0)
string(REGEX MATCH "^[0-9]+" GCC_MAJOR "${CMAKE_CXX_COMPILER_VERSION}")

message(STATUS "Platform: ${CMAKE_SYSTEM_PROCESSOR} | OS: el${OS_MAJOR} | GCC: ${GCC_MAJOR}")

# ===== Locate the correct lib dir (exact match, then any -opt) =====
function(find_tdaq_lib root out_var)
    set(_exact "${root}/${CMAKE_SYSTEM_PROCESSOR}-el${OS_MAJOR}-gcc${GCC_MAJOR}-opt/lib")
    if(EXISTS "${_exact}")
        set(${out_var} "${_exact}" PARENT_SCOPE)
        return()
    endif()
    file(GLOB _matches "${root}/${CMAKE_SYSTEM_PROCESSOR}-el${OS_MAJOR}-*-opt/lib")
    if(_matches)
        list(GET _matches 0 _first)
        set(${out_var} "${_first}" PARENT_SCOPE)
        return()
    endif()
    message(FATAL_ERROR "No lib dir under ${root} for ${CMAKE_SYSTEM_PROCESSOR}-el${OS_MAJOR}")
endfunction()

find_tdaq_lib(${TDAQ_ROOT} TDAQ_LIB)
find_tdaq_lib(${TDAQ_COMMON_ROOT} TDAQ_COMMON_LIB)

message(STATUS "OKS library dir : ${TDAQ_LIB}")
message(STATUS "ERS library dir : ${TDAQ_COMMON_LIB}")

# ===== Executable =====
add_executable(query_oks query_oks.cpp)

target_include_directories(query_oks PRIVATE
    ${TDAQ_ROOT}/include
    ${TDAQ_COMMON_ROOT}/include
)

target_link_directories(query_oks PRIVATE
    ${TDAQ_LIB}
    ${TDAQ_COMMON_LIB}
)

target_link_libraries(query_oks PRIVATE oks ers)

# Bake library paths into the executable so it runs anywhere
set_target_properties(query_oks PROPERTIES
    BUILD_RPATH   "${TDAQ_LIB};${TDAQ_COMMON_LIB}"
    INSTALL_RPATH "${TDAQ_LIB};${TDAQ_COMMON_LIB}"
)
```

---

## Step 3 — Create the build helper (`build.sh`)

```bash
nano build.sh
```

Paste this:

```bash
#!/bin/bash
# build.sh — configure, build, and run the OKS query
set -e
cmake -S . -B build > /dev/null
cmake --build build
echo "----------------------------------------"
./build/query_oks
```

Make it executable:

```bash
chmod +x build.sh
```

---

## Step 4 — Build and run

**First time (or after editing `CMakeLists.txt`):**
```bash
./build.sh
```

**Every time after editing `query_oks.cpp`:**
```bash
./build.sh
```

**Or manually, without the script:**
```bash
cmake -S . -B build
cmake --build build
./build/query_oks
```

### Expected output
```
-- Platform: x86_64 | OS: el9 | GCC: 15
-- OKS library dir : .../installed/x86_64-el9-gcc15-opt/lib
-- ERS library dir : .../installed/x86_64-el9-gcc15-opt/lib
...
Successfully loaded: siom/hw/computers.data.xml

Found 2 matching computers:
 -> Object ID: localhost.localdomain
 -> Object ID: localhost
```

---

## Customizing the query

Edit `query_oks.cpp`:

- **Change the data file** → line with `std::string db_file = ...`
- **Change the class** → `kernel.find_class("Computer")` and the `-c` equivalent
- **Change the query** → the `query_str` line

Then run `./build.sh` again.

### Query syntax reminder
```
( all | this  <expression> )
```
| Type | Example |
|---|---|
| Attribute | `(all ("Memory" "1024" >=))` |
| Equality | `(all ("RLogin" "ssh" =))` |
| Regex | `(all ("Name" ".*lxplus.*" ~=))` |
| Object ID | `(all (object-id "localhost" =))` |
| AND | `(all (and ("A" "1" =) ("B" "2" =)))` |
| Relationship | `(all ("RunsOn" some (object-id "host" =)))` |

Comparators: `=` `!=` `<` `>` `<=` `>=` `~=`

---

## Optional — Read attribute values (not just IDs)

Replace the print loop (Step 6) in `query_oks.cpp` with:

```cpp
    if (results && !results->empty()) {
        std::cout << "Found " << results->size() << " matching computers:\n";
        for (auto it = results->begin(); it != results->end(); ++it) {
            OksObject* obj = *it;
            std::cout << " -> Object ID: " << obj->GetId() << "\n";

            OksData* mem   = obj->GetAttributeValue("Memory");
            OksData* cpu   = obj->GetAttributeValue("CPU");
            OksData* cores = obj->GetAttributeValue("NumberOfCores");

            std::cout << "      Memory: " << *mem   << " MB\n";
            std::cout << "      CPU:    " << *cpu   << " MHz\n";
            std::cout << "      Cores:  " << *cores << "\n";
        }
    }
```

Then `./build.sh`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ers/ers.h: No such file` | Missing `tdaq-common` includes | Handled by `CMakeLists.txt` (both include dirs added) |
| `'std::source_location' ... C++20` | Headers need C++20 | Handled (`CMAKE_CXX_STANDARD 20`) |
| `skipping incompatible ... aarch64` | Glob picked wrong arch | Handled (platform detection) |
| `undefined reference ... GLIBC_2.38` | Picked `el10` lib on `el9` | Handled (OS version detection) |
| `No lib dir under ...` | Wrong release path | Check `TDAQ_VERSION` matches a real CVMFS release |

### Clean rebuild (if anything gets confused)
```bash
rm -rf build
./build.sh
```

---

## Files summary

| File | Purpose |
|---|---|
| `query_oks.cpp` | The C++ query program |
| `CMakeLists.txt` | Build configuration (auto-detects platform) |
| `build.sh` | One-command build + run |
| `build/query_oks` | Compiled executable (output) |
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
# OKS / TDAQ Version Guide — Latest & Previous Versions

There are **two kinds of versions** in the TDAQ world. This guide covers both:

| Type | What it is | Where it lives | How you switch |
|---|---|---|---|
| **Software release** | The code/tools (`oks_dump`, libs, Python) | CVMFS folders | Source a different `setup.sh` |
| **Configuration revision** | The configuration *data* (XML files) | OKS Git repository | Git checkout / `oks_clone_repository` |

---

## Table of Contents

- [Part A — Software Releases (CVMFS)](#part-a--software-releases-cvmfs)
- [Part B — Configuration Revisions (Git)](#part-b--configuration-revisions-git)
- [Part C — Using a Version with C++](#part-c--using-a-version-with-c)
- [Quick Reference](#quick-reference)

---

# Part A — Software Releases (CVMFS)

Releases like `tdaq-13-00-00`, `tdaq-14-00-00` are folders on CVMFS.

## A1. List all available releases

```bash
ls /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq | sort -V
```

The last entry is the **latest** release.

## A2. Switch to a release (latest or previous)

> ⚠️ Always use a **fresh shell** — never source one release on top of another.

```bash
exit                                          # leave the old environment
ssh <your_username>@lxplus.cern.ch            # fresh login

# Source the release you want:
# LATEST
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh
# PREVIOUS (just change the version number)
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-13-00-00/installed/setup.sh
```

## A3. Verify which release is active

```bash
which oks_dump        # path should contain the release you sourced
echo $BINARY_TAG      # platform tag set by the release (if defined)
```

## A4. If you don't know the exact path

```bash
find /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq \
     -maxdepth 5 -name setup.sh 2>/dev/null | sort -V | tail -10
```

---

# Part B — Configuration Revisions (Git)

Every configuration ever used is preserved in the **OKS Git repository**:
- Each run's config is tagged `r<runNumber>@<partition>`
- The Run Number DB stores the exact commit hash per run

You can retrieve any revision by **hash**, **tag**, or **date**.

## B1. Using plain git

```bash
# Clone once
mkdir ~/oks-repo && cd ~/oks-repo
git clone `oks_git_repository` .

# See all versions
git log --oneline --all --decorate     # full history
git tag -l 'r*'                        # run tags
git branch -a                          # branches

# Go to a previous version
git checkout <commit-hash>             # e.g. git checkout 6800fe3b
git checkout r380689@all_hosts         # or by run tag

# Back to latest
git checkout master
```

## B2. Using `oks_clone_repository` (recommended)

Clones and checks out a specific version in one step:

```bash
# Latest (default)
oks_clone_repository

# Previous, by commit hash
oks_clone_repository --version hash:6800fe3b

# Previous, by run tag (runNumber@partition)
oks_clone_repository --version tag:r380689@all_hosts

# Previous, by date (config as of that date)
oks_clone_repository --version date:"2026-06-15"
oks_clone_repository --version date:"2020-07-31T16:33:59"
oks_clone_repository --version date:"2 years ago"      # tdaq-13-01-00+
```

## B3. Using the `TDAQ_DB_VERSION` environment variable

No manual checkout — OKS tools resolve the version automatically:

```bash
export TDAQ_DB_VERSION=hash:6800fe3b               # exact revision
export TDAQ_DB_VERSION=date:"2026-06-15"           # latest before date
unset  TDAQ_DB_VERSION                             # back to latest (HEAD)
```

| Format | Meaning |
|---|---|
| `hash:<value>` | Exact commit |
| `date:<value>` | Latest revision *before* that date |
| `tag:<value>` | Run tag (`r<run>@<partition>`) |

## B4. Find which version a run used, then get it

```bash
# 1. Query the Run Number DB for a time window
rn_ls -c "oracle://atonr_adg/rn_r" -w ATLAS_RUN_NUMBER \
      -s '2020-07-31T12:00:00' -t '2020-08-02T12:00:00' -a '%xml'
#    → note the hash in the "Version" column and the "Config Name"

# 2. Check out exactly that version
oks_clone_repository --version hash:<that-hash>
```

## B5. List versions WITHOUT cloning

```bash
git ls-remote --tags  `oks_git_repository`    # all tags + hashes
git ls-remote --heads `oks_git_repository`    # all branches
```

---

# Part C — Using a Version with C++

Key insight: **reading an older configuration needs NO recompilation.**
Your C++ binary just loads whatever files OKS points it at.

## C1. Older configuration (git revision) — no rebuild

```bash
# 1. Check out the old version
cd `oks_clone_repository --version hash:6800fe3b`

# 2. Tell OKS to use this checkout
export TDAQ_DB_USER_REPOSITORY=`pwd`

# 3. Run your existing binary
~/private/my_tdaq_project/build/query_oks
```

## C2. Different software release — rebuild required

If you switch the *release* your code links against (Part A), rebuild:

```bash
# source the other release first (Part A), then:
cd ~/private/my_tdaq_project
rm -rf build
./build.sh
```

## Summary: do you need to rebuild?

| Change | Rebuild C++? |
|---|---|
| Older/newer configuration revision (git) | ❌ No |
| Different data file or query | ❌ No (edit code only if hardcoded) |
| Different TDAQ software release | ✅ Yes |

---

# Quick Reference

| Goal | Command |
|---|---|
| List software releases | `ls /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq \| sort -V` |
| Use latest release | `source .../tdaq-14-00-00/installed/setup.sh` (fresh shell) |
| Use previous release | `source .../tdaq-13-00-00/installed/setup.sh` (fresh shell) |
| Config history | `git log --oneline --all` |
| Config run tags | `git tag -l 'r*'` |
| Checkout config version | `git checkout <hash-or-tag>` |
| Clone config at version | `oks_clone_repository --version hash:\|tag:\|date:` |
| Pin version via env | `export TDAQ_DB_VERSION=hash:<h>` / `date:<d>` |
| Version used by a run | `rn_ls ... -a '%xml'` |
| Use checkout in tools/C++ | `export TDAQ_DB_USER_REPOSITORY=\`pwd\`` |
| Back to latest config | `git checkout master` / `unset TDAQ_DB_VERSION` |

---

## Notes & Gotchas

- **Fresh shell for releases** — sourcing one release over another mixes paths.
- **"Latest before date"** — a date selector returns the newest commit *before* that date.
- **Relative dates** (`"2 years ago"`) need tdaq-13-01-00 or newer.
- **Repository filenames** — with git access, use repo-relative names like
  `daq/segments/setup.data.xml`, not filesystem paths.
- **CERN GitLab mirror** (`atlas-tdaq-software/oks`) is read-only; real config
  changes go through the TDAQ git server.

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