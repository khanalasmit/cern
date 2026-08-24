# Text-to-OksQuery Translation Module — Agent Knowledge Base & Operations Guide

> **Purpose:** This document is the complete reference for building and running the
> Natural-Language → OksQuery translation pipeline on the ATLAS TDAQ SSH computing
> environment. It consolidates environment setup, OKS concepts, query syntax, schema
> retrieval, execution methods, temporal (multi-version) access, and the end-to-end
> LLM pipeline design.
>
> **Pipeline at a glance:**
> ```
> User (natural language)
>   → LLM Translation Module (this project)  → generates OksQuery string
>   → Backend executes via C++ OksQuery engine (oks_dump / Python / C++)
>   → Raw results returned
>   → LLM interprets results → clean, understandable answer to user
> ```

---

## Table of Contents
1. [Project Overview & Pipeline Architecture](#1-project-overview--pipeline-architecture)
2. [Environment Setup (SSH + CVMFS + Releases)](#2-environment-setup)
3. [Core OKS Concepts](#3-core-oks-concepts)
4. [OksQuery Syntax Reference (Translation Target)](#4-oksquery-syntax-reference)
5. [Schema Retrieval (for the Translation Module)](#5-schema-retrieval)
6. [Executing Queries (CLI / Python / C++)](#6-executing-queries)
7. [Temporal Access — Configurations Across Time](#7-temporal-access)
8. [The End-to-End LLM Pipeline](#8-the-end-to-end-llm-pipeline)
9. [Few-Shot Examples Library](#9-few-shot-examples-library)
10. [Validate / Repair Loop](#10-validate--repair-loop)
11. [Error Taxonomy & Evaluation](#11-error-taxonomy--evaluation)
12. [Ablation Study Design](#12-ablation-study-design)
13. [Troubleshooting Reference](#13-troubleshooting-reference)

---

## 1. Project Overview & Pipeline Architecture

### The problem
The ATLAS DAQ configuration lives in the **OKS (Object Kernel Support)** framework.
The whole configuration is too large to fit in an LLM context window, so an **MCP
server** must filter data on the backend using the **native C++ OksQuery engine**.
LLMs don't know the proprietary OksQuery syntax, so a **translation layer** converts
natural language → valid OksQuery.

### Module responsibilities
| Component | Role |
|---|---|
| **Schema retrieval** | Pull only the *relevant* OKS schema slice (not the whole schema) into the prompt |
| **Few-shot examples** | Show the LLM correct NL→OksQuery pairs |
| **Translation** | LLM produces an OksQuery string |
| **Validate/repair loop** | Check syntax; if invalid, feed error back and retry |
| **Execution** | Run query via `oks_dump` / Python / C++ |
| **Interpretation** | LLM turns raw results into a clean answer |

### Deliverables (from project spec)
1. **Translation Module (Python)** — importable, with schema retrieval + few-shot + validate/repair.
2. **Evaluation Dataset** — shifter questions paired with ground-truth OksQuery, stratified by difficulty.
3. **Accuracy Benchmark Report** — accuracy measured by *executing* the query and comparing results (not just text); report valid-syntax rate; break failures into an error taxonomy.
4. **Ablation** — report accuracy in stages: plain prompt → +few-shot → +schema retrieval → +validate/repair.

---

## 2. Environment Setup

### 2.1 SSH into CERN
```bash
ssh <your_username>@lxplus.cern.ch
```

### 2.2 Working directory
```bash
cd ~/private/my_tdaq_project        # or your project folder
```

### 2.3 TDAQ releases live on CVMFS
```bash
ls /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq | sort -V
```
You will see releases `tdaq-07-01-00` … `tdaq-14-00-00`. The **latest** is the last entry.

### 2.4 Source a release (once per terminal session)
> ⚠️ Always use a **fresh shell**. Never source one release over another.
```bash
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh
```
Verify:
```bash
which oks_dump          # should point inside the release you sourced
```

### 2.5 Key directories (for tdaq-14-00-00)
| Path | Content |
|---|---|
| `/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/share/data/` | All OKS data + schema |
| `.../share/data/daq/schema/` | **Schema files** (`*.schema.xml`) — class definitions |
| `.../share/data/daq/segments/setup.data.xml` | Main setup file (includes many others) |
| `.../share/data/siom/hw/computers.data.xml` | Example `Computer` objects |
| `.../share/data/daq/sw/test-repository.data.xml` | Test `Executable`/`BaseApplication` objects |

### 2.6 Environment variables that control OKS
| Variable | Purpose |
|---|---|
| `TDAQ_DB_PATH` | Filesystem data search path (used for CVMFS snapshots) |
| `TDAQ_DB_VERSION` | Pin a git revision: `hash:<h>` or `date:<d>` (online nodes) |
| `TDAQ_DB_USER_REPOSITORY` | Point tools at a local git checkout |
| `TDAQ_DB_REPOSITORY` | Git URL(s) enabling git-based access (online) |

---

## 3. Core OKS Concepts

### 3.1 Configuration vs. measurement
OKS stores **configuration (settings)**, not time-series measurements.
| Type | Example | In OKS? |
|---|---|---|
| Set-point / config | "HV should be 1000 V" | ✅ Yes (versioned) |
| Live measured value | "HV read 1000.2 V at 10:00" | ❌ No (DCS/archive) |

### 3.2 Classes (schema) vs. Objects (data)
| | Defined in | Changes between commits? |
|---|---|---|
| **Classes / attributes / relationships** | `*.schema.xml` | ❌ Rarely (schema edits) |
| **Objects / attribute values** | `*.data.xml` | ✅ Constantly (this is what commits track) |

**Key consequence:** The *same query* works across versions; only the **results** differ.
You only change the query if the **schema** changed (attribute renamed/removed).

### 3.3 Versioning model
- **Git hash** = the real versioning of the config (fine-grained, any commit). *Online nodes only.*
- **TDAQ release** = a frozen snapshot of the git history bundled with software. *Available on CVMFS/LXPLUS.*
- **Run tag** = `r<runNumber>@<partition>`; each run records its config hash.

### 3.4 What "electron detection" maps to
Electrons → **Electromagnetic (EM) Calorimeter** → part of the **LAr calorimeter**.
Look for segments/partitions named `LAr`, `EM`, `EMB`, `EMEC`, `Calo`, `Tile`, `ROS`.

---

## 4. OksQuery Syntax Reference

This is the **translation target** — the exact syntax the LLM must produce.

### 4.1 Top-level form
```
( all | this  <expression> )
```
- `all` → search this class **and all subclasses**
- `this` → search **only** this class

### 4.2 Expressions
| Type | Syntax | Example |
|---|---|---|
| Attribute compare | `( "attr" "value" <cmp> )` | `( "InitTimeout" "2" > )` |
| Object-ID compare | `( object-id "id" <cmp> )` | `( object-id "test_dummy" = )` |
| Logical AND | `( and <e1> <e2> ... )` | `( and ("a" "1" =) ("b" "2" =) )` |
| Logical OR | `( or <e1> <e2> ... )` | `( or ("a" "1" =) ("b" "2" =) )` |
| Logical NOT | `( not <e> )` | `( not ("a" "1" =) )` |
| Relationship | `( "RelName" some|all <sub-expr> )` | `( "RunsOn" some (object-id "h" =) )` |

### 4.3 Comparators
| Symbol | Meaning |
|---|---|
| `=` | equal |
| `!=` | not equal |
| `<` `>` | less / greater |
| `<=` `>=` | less-or-equal / greater-or-equal |
| `~=` | regular-expression match |

### 4.4 Rules the translation module MUST enforce
1. The scope token (`all`/`this`) appears **once, at the top**.
2. `and`/`or` need **≥ 2 operands**; `not` needs exactly 1.
3. Attribute/relationship names are **quoted strings**.
4. Attribute must exist in the target class (else: `can't find attribute ...`).
5. Class must exist (else: `can't find class ...`).
6. Numeric values are still written as quoted strings (e.g. `"2"`).
7. Special tokens like `#this.UID` are compared **literally** (stored verbatim).

---

## 5. Schema Retrieval

The translation module must inject **only the relevant schema** into the prompt.

### 5.1 List all class names
```bash
grep -h '<class name=' /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/share/data/daq/schema/*.schema.xml \
  | sed 's/.*name="\([^"]*\)".*/\1/' | sort | uniq
```

### 5.2 Inspect one class's model (attributes + relationships + objects)
```bash
oks_dump -c <ClassName> <data-file>
# e.g.
oks_dump -c BaseApplication daq/segments/setup.data.xml
```
Output shows **Attributes** (name, type, range), **Relationships**, **Methods**, and **Objects**.

### 5.3 Programmatic schema access (Python)
```python
import config
db = config.Configuration("oksconflibs:daq/segments/setup.data.xml")
print(db.classes())                      # all class names
print(db.attributes("BaseApplication"))  # attributes of one class
print(db.relations("BaseApplication"))   # relationships of one class
```

### 5.4 Schema-retrieval strategy for the module
1. Parse the user question for candidate class/attribute keywords.
2. Match keywords → class names (via the class list above).
3. Load **only** those classes' attribute/relationship definitions.
4. Inject that slice into the LLM prompt (not the whole schema).

---

## 6. Executing Queries

### 6.1 CLI (`oks_dump`) — simplest, good for validation
```bash
oks_dump -c <ClassName> -q '<query>' <data-file>
# e.g.
oks_dump -c Executable -q '(all ("InitTimeout" "2" >))' daq/segments/setup.data.xml
```
Useful flags:
- `-c <class>` — class to search
- `-q '<query>'` — query string (requires `-c`)
- `-f <file>` — list included files / inspect a file
- no `-q` — dump the whole class (schema + objects)

**Exit codes** (useful for the validate/repair loop):
| Code | Meaning |
|---|---|
| 0 | OK |
| 1 | Bad command-line parameter |
| 2 | Bad OKS file(s) |
| 3 | **Bad query (syntax error)** |
| 4 | **Class not found** |
| 5 | Dangling references |

### 6.2 Python (`config`) — good for the translation module
```python
import config
db = config.Configuration("oksconflibs:daq/segments/setup.data.xml")
query = '(all ("InitTimeout" "2" >))'
for obj in db.get_objs("Executable", query):
    print(obj.UID())
```
Other helpers: `db.get_obj(class,id)`, `db.get_dal(class,id)`, `db.get_dals(class)`, `db.classes()`.

### 6.3 C++ (native OksQuery engine) — the backend executor
```cpp
#include "oks/kernel.h"
#include "oks/class.h"
#include "oks/query.h"
#include "oks/object.h"
#include "oks/file.h"

OksKernel kernel;
kernel.load_file("daq/segments/setup.data.xml");

OksClass* cls = kernel.find_class("Executable");
std::string qstr = "(all (\"InitTimeout\" \"2\" >))";
OksQuery query(cls, qstr.c_str());

if (query.good()) {
    OksObject::List* results = cls->execute_query(&query);
    // ... iterate results, read attributes via obj->GetAttributeValue("InitTimeout")
}
```

**Build (CMake)** — the module that compiles this must handle:
- C++20 (`set(CMAKE_CXX_STANDARD 20)`) — headers use `std::source_location`
- Include dirs: `<tdaq>/installed/include` and `<tdaq-common>/installed/include`
- Lib dirs: architecture-specific, e.g. `x86_64-el9-gcc15-opt/lib`
- Link: `-loks -lers`

> The query is **executed** at `cls->execute_query(&query)` → routes into
> `OksClass::execute_query()` in `src/query.cpp`, which evaluates each object via
> `OksObject::SatisfiesQueryExpression()`.

---

## 7. Temporal Access

Answer questions like *"what was the configuration in the past?"*

### 7.1 Decision guide
| Situation | Method |
|---|---|
| On LXPLUS, want config from an older release | `TDAQ_DB_PATH` → CVMFS snapshot |
| On an Online node, want config at a date/commit | `TDAQ_DB_VERSION=hash:/date:` |
| Want config used by run number X | `rn_ls` → hash → then use it |

### 7.2 CVMFS snapshot (works on LXPLUS)
```bash
export TDAQ_DB_PATH=/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-13-00-00/installed/share/data
./build/verify_query          # or oks_dump ...
unset TDAQ_DB_PATH            # back to current
```

### 7.3 Git version (online nodes only)
```bash
export TDAQ_DB_VERSION=hash:6800fe3b            # exact commit
export TDAQ_DB_VERSION=date:"2024-03-15"        # latest before date
unset TDAQ_DB_VERSION                            # back to latest
```
Or clone & checkout:
```bash
cd `oks_clone_repository`
git log --oneline | head
git checkout <old-hash>
export TDAQ_DB_USER_REPOSITORY=`pwd`
```
> ⚠️ On LXPLUS, `oks_clone_repository` returns nothing (online git server unreachable).
> Use CVMFS snapshots there.

### 7.4 Config used by a specific run
```bash
rn_ls -c "oracle://atonr_adg/rn_r" -w ATLAS_RUN_NUMBER \
      -s '<start>' -t '<end>' -a '%xml'
# → note the hash in the "Version" column, use it in 7.3
```

### 7.5 Comparing past vs present
```bash
# present
oks_dump -c <Class> -q '<query>' <file> > present.txt
# past (set TDAQ_DB_PATH or TDAQ_DB_VERSION first)
oks_dump -c <Class> -q '<query>' <file> > past.txt
diff present.txt past.txt
```
**Same query, different version → the diff is the configuration change.**

---

## 8. The End-to-End LLM Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│ 1. USER asks a natural-language question                       │
│    e.g. "Which test executables take >2s to initialise?"       │
├──────────────────────────────────────────────────────────────┤
│ 2. SCHEMA RETRIEVAL: find relevant classes/attributes          │
│    (Section 5) — pull only that slice                          │
├──────────────────────────────────────────────────────────────┤
│ 3. PROMPT = system rules (Sec 4) + schema slice + few-shot     │
│    (Sec 9) + user question                                     │
├──────────────────────────────────────────────────────────────┤
│ 4. LLM generates OksQuery string                               │
├──────────────────────────────────────────────────────────────┤
│ 5. VALIDATE/REPAIR (Sec 10): syntax-check; retry if invalid    │
├──────────────────────────────────────────────────────────────┤
│ 6. EXECUTE via oks_dump / Python / C++ (Sec 6)                 │
│    (optionally across versions — Sec 7)                        │
├──────────────────────────────────────────────────────────────┤
│ 7. LLM INTERPRETS raw results → clean, understandable answer   │
└──────────────────────────────────────────────────────────────┘
```

### Interpretation-stage prompt guidance
- Summarize the count and list matching objects.
- Translate object IDs/attributes into plain language.
- For temporal queries, explicitly state *which version* was queried and *what changed*.

---

## 9. Few-Shot Examples Library

Use these NL→OksQuery pairs in the prompt.

### Example 1 — numeric attribute, `>` (easy)
- **Q:** Which test executables take longer than 2 seconds to initialise?
- **Class:** `Executable`
- **OksQuery:** `(all ("InitTimeout" "2" >))`
- **Note:** `>=` would include the boundary; `>` excludes it. 2 is the init-value.

### Example 2 — string equality with special token (easy)
- **Q:** Which test executables run on the object's own host?
- **Class:** `Executable`
- **OksQuery:** `(all ("Host" "#this.UID" =))`
- **Note:** `#this.UID` is a DAL substitution token stored verbatim; compared literally.

### Example 3 — AND of two attributes (medium)
- **Q:** Which applications initialise in 30 seconds and exit within 5?
- **Class:** `BaseApplication`
- **OksQuery:** `(all (and ("InitTimeout" "30" =) ("ExitTimeout" "5" =)))`
- **Note:** `and` needs ≥2 operands; scope token appears once at top.

### Example 4 — relationship traversal
- **Q:** Which applications run on host `lxplus001.cern.ch`?
- **Class:** `Application`
- **OksQuery:** `(all ("RunsOn" some (object-id "lxplus001.cern.ch" =)))`

### Example 5 — regex match
- **Q:** Which applications have a name containing "lxplus"?
- **Class:** `Application`
- **OksQuery:** `(all ("Name" ".*lxplus.*" ~=))`

### Example 6 — match-all (baseline / counting)
- **Q:** List all Computer objects.
- **Class:** `Computer`
- **OksQuery:** `(all (object-id "" !=))`

---

## 10. Validate / Repair Loop

```
generated_query
   │
   ├─► syntax check (run oks_dump -q, inspect exit code / stderr)
   │        │
   │        ├─ exit 0 → proceed to execution
   │        └─ exit 3/4/5 → capture error message
   │                 │
   │                 └─► feed error back to LLM → regenerate (max N retries)
   │
   └─► after N failures → report as invalid-syntax failure
```
- Use **exit code 3** (bad query) and **4** (class not found) as repair triggers.
- The stderr message (e.g. `can't find attribute "Timeout" in class "RunControlApplication"`)
  is valuable feedback for the LLM to correct class/attribute names.

---

## 11. Error Taxonomy & Evaluation

### Measure accuracy by EXECUTION, not text
Run the generated query and compare its **result set** to ground truth.

### Metrics to report
- **Result accuracy** — result set matches ground truth.
- **Valid-syntax rate** — % of generated queries that parse (exit ≠ 3).
- **Failure taxonomy** (break down, don't just pass/fail):
  | Category | Example |
  |---|---|
  | Wrong syntax | Malformed brackets, missing quotes |
  | Wrong class | Queried `Application` instead of `Executable` |
  | Wrong attribute | Used `Timeout` instead of `InitTimeout` |
  | Wrong comparator | Used `=` instead of `>` |
  | Wrong scope | Used `this` instead of `all` |
  | Missing/extra logic | Dropped an `and` operand |

---

## 12. Ablation Study Design

Report accuracy in stages to show each component's contribution:
1. **Plain prompt only** (rules + question)
2. **+ few-shot examples** (Section 9)
3. **+ schema retrieval** (Section 5)
4. **+ validate/repair loop** (Section 10) ← full system

Plot accuracy (result-match %) and valid-syntax rate at each stage.

---

## 13. Troubleshooting Reference

| Symptom | Cause | Fix |
|---|---|---|
| `ers/ers.h: No such file` | Missing tdaq-common includes | Add both include dirs |
| `'std::source_location' ... C++20` | Headers need C++20 | `-std=c++20` / `CMAKE_CXX_STANDARD 20` |
| `skipping incompatible ... aarch64` | Wrong arch lib picked | Filter lib dir by `${CMAKE_SYSTEM_PROCESSOR}` |
| `undefined reference ... GLIBC_2.38` | Picked el10 lib on el9 | Match lib dir to OS version (`el9`) |
| `redefinition of 'int main()'` | Two `main()` in one file | Keep one `main` per file |
| `cannot load file '<x>.data.xml'` | Placeholder/missing file | Use a real repo-relative filename |
| `can't find attribute ...` | Schema changed / wrong attribute | Check class model via `oks_dump -c` |
| `can't find class ...` | Wrong class name | List classes (Section 5.1) |
| `oks_clone_repository` returns nothing | LXPLUS can't reach online git | Use CVMFS snapshot (`TDAQ_DB_PATH`) |
| `The data contain dangling references` | Includes not fully loaded | Warning only; usually safe to ignore |

---

## Appendix A — Quick command cheat-sheet

```bash
# Setup
ssh <user>@lxplus.cern.ch
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh

# Discover
grep -h '<class name=' .../daq/schema/*.schema.xml | sed 's/.*name="\([^"]*\)".*/\1/' | sort | uniq
oks_dump -c <Class> <file>

# Query
oks_dump -c <Class> -q '(all ("<attr>" "<val>" <cmp>))' <file>

# Temporal
export TDAQ_DB_PATH=/cvmfs/.../tdaq-13-00-00/installed/share/data      # LXPLUS
export TDAQ_DB_VERSION=hash:<h>                                          # online
rn_ls -c "oracle://atonr_adg/rn_r" -w ATLAS_RUN_NUMBER -s '<t1>' -t '<t2>' -a '%xml'

# Compare
oks_dump ... > present.txt ; oks_dump ... > past.txt ; diff present.txt past.txt
```

---
*Generated knowledge base — consolidate of full working session. Adjust release
versions and file paths to the active TDAQ release.*

---

## 14. Obtaining Information from the `.xml` Files

### 14.1 Two levels of information
The `.xml` files can be read at two levels. The translation module must work at the
**model level**, not the text level.

| Level | What it is | Tools | Use for |
|---|---|---|---|
| **Raw text** | The XML as characters | `cat`, `grep`, `head` | Locating files / class names only |
| **OKS model** | Parsed classes, attributes, relationships, objects | `oks_dump`, Python `config`, C++ | **Everything else** (translation + execution) |

### 14.2 The two kinds of `.xml` files
| File type | Defines | Naming |
|---|---|---|
| **Schema** | CLASSES (attributes, relationships, methods) | `*.schema.xml` |
| **Data** | OBJECTS (instances + attribute values) | `*.data.xml` |

- Schema location: `.../share/data/daq/schema/*.schema.xml`
- Data location: `.../share/data/daq/segments/`, `.../daq/sw/`, `.../siom/`, etc.

### 14.3 Raw (text) access — only for locating
```bash
# Find which schema files exist
ls .../share/data/daq/schema/*.schema.xml

# List class names across all schema files
grep -h '<class name=' .../share/data/daq/schema/*.schema.xml \
  | sed 's/.*name="\([^"]*\)".*/\1/' | sort | uniq

# Peek at a data file's raw structure
head -50 .../share/data/daq/segments/setup.data.xml
```
> ⚠️ Raw text tells you *what exists* but not *what it means*. Never build a query
> from raw XML — always go through the OKS model.

### 14.4 Model access — the real way
```bash
# See a class's attributes, relationships, and its objects
oks_dump -c <ClassName> <data-file>
```
```python
# Python: structured access
import config
db = config.Configuration("oksconflibs:daq/segments/setup.data.xml")
db.classes()                        # class names
db.attributes("BaseApplication")    # attributes of a class
db.relations("BaseApplication")     # relationships of a class
db.get_objs("Executable")           # objects of a class
```

---

## 15. Obtaining Classes & Objects per Commit Hash

### 15.1 What changes vs. what stays the same
| | Source | Across commit hashes |
|---|---|---|
| **Classes / attributes / relationships** | `*.schema.xml` | Mostly **stable** (change only on schema edits) |
| **Objects / attribute values** | `*.data.xml` | **Change constantly** (this is what commits track) |

**Consequence:** To describe "the system at commit X", you read the schema+data **as
they exist in that commit's checkout.** Same classes, different objects/values.

### 15.2 Select the commit hash first
```bash
# Online node:
export TDAQ_DB_VERSION=hash:<commit-hash>
# LXPLUS fallback (release snapshot instead of exact hash):
export TDAQ_DB_PATH=/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/<release>/installed/share/data
```

### 15.3 Then get classes and objects at that version
```bash
# Classes available at this version
grep -h '<class name=' .../daq/schema/*.schema.xml | sed 's/.*name="\([^"]*\)".*/\1/' | sort | uniq

# A specific class's model + objects at this version
oks_dump -c <ClassName> <data-file>
```
```python
# Python at the selected version
db = config.Configuration("oksconflibs:daq/segments/setup.data.xml")
db.classes()
for o in db.get_objs("Executable"):
    print(o.UID())
```

### 15.4 Per-hash workflow
```
1. Select version      → TDAQ_DB_VERSION=hash:<h>  (or TDAQ_DB_PATH snapshot)
2. List classes        → grep schema  /  db.classes()
3. Inspect a class     → oks_dump -c <Class> <file>
4. Read objects        → oks_dump / db.get_objs(...)
5. Repeat for another hash to compare
```

---

## 16. How the LLM Should Use This Information

The LLM is called **twice**, and each call gets a *different, filtered* slice.

### 16.1 Call #1 — Translation (NL → OksQuery)
Feed the LLM **only the relevant schema slice**:
- The candidate **class** name(s)
- That class's **attributes** (name + type)
- That class's **relationships**
- Few-shot examples

**Do NOT** feed object instances, other classes, or the whole schema.

Example context for Call #1:
```
Class: Executable
Attributes: InitTimeout (u32), ExitTimeout (u32), Host (string), Name (string)
Relationships: (none relevant)
---
Q: Which test executables take longer than 2 seconds to initialise?
OksQuery: (all ("InitTimeout" "2" >))
```

### 16.2 Call #2 — Interpretation (results → answer)
Feed the LLM **only the filtered result set** (the objects that matched), formatted
cleanly — not raw `oks_dump` text.

Example context for Call #2:
```
Query matched 3 objects:
- test_dummy (InitTimeout=3)
- test_dummy_fail_0.01 (InitTimeout=2.5)
- test_dummy_long (InitTimeout=10)
```

### 16.3 Context budget rule
| LLM call | Input | Size target |
|---|---|---|
| Translation | schema slice + few-shot + question | small (1–3 classes) |
| Interpretation | matched objects only | proportional to result count |

---

## 17. Filter vs. Feed-All — The Critical Decision

### 17.1 Answer: **ALWAYS FILTER. Never feed all.**
This is the core constraint of the project:
> *"Pulling the entire configuration into an LLM's context window is technically
> unfeasible due to size constraints."*

Feeding everything would:
- ❌ Overflow the context window
- ❌ Waste tokens on irrelevant data
- ❌ Increase syntax hallucinations
- ❌ Defeat the purpose of the MCP backend filter

### 17.2 Filtering happens at TWO distinct points
| Stage | What is filtered | Filtered by |
|---|---|---|
| **Schema retrieval** (before translation) | Which **classes/attributes** the LLM sees | Keyword/class matching on the question |
| **Query execution** (before interpretation) | Which **objects** come back | The **C++ OksQuery engine** on the backend |

```
                        ┌──────────── FILTER #1: schema retrieval ────────────┐
User question ────────► │ pick only relevant class + attributes + relations  │
                        └───────────────────────┬────────────────────────────┘
                                                ▼
                                   LLM Call #1 (translation)
                                                ▼
                                          OksQuery string
                                                ▼
                        ┌──────────── FILTER #2: OksQuery engine ─────────────┐
                        │ C++ engine scans objects, returns ONLY matches      │
                        └───────────────────────┬────────────────────────────┘
                                                ▼
                                   LLM Call #2 (interpretation)
                                                ▼
                                      clean answer to user
```

### 17.3 Can we filter per user query? — YES, and we MUST
Each user question drives its own filter:
1. **Parse** the question → identify target class + attribute keywords.
2. **Schema filter** → retrieve only that class's definition.
3. **Translate** → LLM emits the OksQuery.
4. **Object filter** → the C++ engine returns only matching objects.
5. **Interpret** → LLM summarizes just those objects.

So the answer to *"filter per query, or feed all?"* is unambiguous:
**filter per query at both the schema level and the object level.** The LLM should
never see the full configuration — only the narrow slice each question requires.

### 17.4 Practical filtering tips
- Cache the **class list** once (it's small) to speed up class matching.
- Retrieve **one class at a time**; add a second only if the question spans a relationship.
- Cap the number of objects passed to Call #2 (e.g. first N + total count) if a query
  could match thousands.
- For temporal questions, apply the same two filters **within the selected commit hash**.

---
*Appended: XML info extraction, per-commit class/object retrieval, LLM usage, and
the filter-vs-feed-all architecture decision.*


---

## 18. MASTER PROMPT — Give This to an Agent to Build the Whole System

> Copy everything inside the code fence below and give it to a coding agent.
> It is self-contained: role, context, environment, deliverables, architecture,
> step-by-step build plan, and acceptance criteria.

```text
========================================================================
ROLE
========================================================================
You are a senior software engineer building the "Text-to-OksQuery
Translation Module" for the ATLAS DAQ configuration system. You will
produce a standalone, importable Python package plus an evaluation and
benchmarking harness. Write clean, documented, production-quality code.

========================================================================
CONTEXT
========================================================================
The ATLAS DAQ configuration is stored in the OKS (Object Kernel Support)
framework. An MCP server lets LLMs query this data, but:
  1. The full configuration is too large for an LLM context window, so
     filtering MUST happen on the backend via the native C++ OksQuery engine.
  2. LLMs do not know the proprietary OksQuery syntax, so a translation
     layer converts natural language -> valid OksQuery strings.

Your module is the middleware that does this translation accurately.

========================================================================
ENVIRONMENT (where queries will be executed)
========================================================================
- SSH host: lxplus.cern.ch
- TDAQ release on CVMFS, e.g.:
    /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/
- Source the release before running anything:
    source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh
- Schema files: <release>/installed/share/data/daq/schema/*.schema.xml
- Data files:   <release>/installed/share/data/daq/segments/setup.data.xml
                <release>/installed/share/data/daq/sw/test-repository.data.xml
                <release>/installed/share/data/siom/hw/computers.data.xml
- Temporal access:
    * Online node: export TDAQ_DB_VERSION=hash:<h>  or  date:"<d>"
    * LXPLUS fallback: export TDAQ_DB_PATH=<older-release>/installed/share/data
  (LXPLUS cannot reach the live OKS git server; use CVMFS snapshots there.)

========================================================================
OksQuery SYNTAX (the translation target)
========================================================================
Top level:      ( all | this  <expression> )
  all  = class + subclasses ; this = only this class
Attribute:      ( "attr" "value" <cmp> )
Object id:      ( object-id "id" <cmp> )
Logic:          ( and <e1> <e2> ... )  ( or <e1> <e2> ... )  ( not <e> )
Relationship:   ( "RelName" some | all <sub-expr> )
Comparators:    =  !=  <  >  <=  >=  ~= (regex)

Hard rules the generator MUST obey:
  * Scope token (all/this) appears once, at the top.
  * and/or need >=2 operands; not needs exactly 1.
  * Attribute / relationship names are quoted strings.
  * Numeric values are quoted strings, e.g. "2".
  * Attribute must exist on the target class.
  * Tokens like #this.UID are compared literally.

========================================================================
DELIVERABLES (build all four)
========================================================================
1. Translation Module (Python package `oksquery_translator/`)
   - schema_retrieval.py : pull ONLY the relevant schema slice
   - prompt_builder.py   : assemble system rules + schema slice + few-shot
   - translator.py       : LLM call #1 -> OksQuery string
   - validator.py        : syntax check + repair loop (retry on failure)
   - executor.py         : run query via oks_dump / Python config / C++
   - interpreter.py      : LLM call #2 -> clean natural-language answer
   - pipeline.py         : end-to-end glue: question -> answer

2. Evaluation Dataset (`eval_dataset.jsonl`)
   - Common shifter questions paired with ground-truth OksQuery.
   - Stratified by difficulty (easy / medium / hard).
   - Each record: {id, question, target_class, query_oks, difficulty,
                   expected_object_ids, expected_count, source_file}

3. Accuracy Benchmark Report generator (`benchmark.py`)
   - Accuracy measured by EXECUTING the generated query and comparing the
     RESULT SET to ground truth (not just comparing query text).
   - Also report valid-syntax rate.
   - Break failures into an error taxonomy:
       wrong_syntax | wrong_class | wrong_attribute | wrong_comparator
       | wrong_scope | missing_logic

4. Ablation harness (`ablation.py`)
   - Report accuracy in stages:
       plain prompt only
       -> + few-shot examples
       -> + schema retrieval
       -> + validate/repair loop (full system)

========================================================================
ARCHITECTURE TO IMPLEMENT
========================================================================
User NL question
  -> [Schema Retrieval]  filter to relevant class + attributes + relations
  -> [Prompt Builder]    rules + schema slice + few-shot + question
  -> [LLM Call #1]       generate OksQuery string
  -> [Validator]         syntax-check; on failure, feed error back & retry
  -> [Executor]          C++ OksQuery engine returns ONLY matching objects
  -> [LLM Call #2]       interpret filtered results -> clean answer

Filtering is mandatory at TWO points (never feed the whole config):
  FILTER #1 (schema retrieval): which classes/attributes the LLM sees.
  FILTER #2 (execution):        the C++ engine returns only matching objects.

========================================================================
STEP-BY-STEP BUILD PLAN
========================================================================
Step 1 - Environment probe:
  * Confirm the release path exists and `oks_dump` runs.
  * Build a list of all class names by scanning the schema files.

Step 2 - schema_retrieval.py:
  * Given a question, identify candidate class + attribute keywords.
  * Return only that class's attributes + relationships (not the whole schema).
  * Cache the class list for speed.

Step 3 - prompt_builder.py:
  * Embed the OksQuery syntax rules above.
  * DISCOVER and LOAD the scraped few-shot examples from the repo root
    (see FEW-SHOT EXAMPLES section) — do not hardcode them.
  * Insert the retrieved schema slice and the user question.

Step 4 - translator.py + validator.py:
  * Call the LLM to produce an OksQuery.
  * Validate by running `oks_dump -c <class> -q '<query>' <file>` and
    inspecting the exit code (0=OK, 3=bad query, 4=class not found).
  * On exit 3/4, feed the stderr message back to the LLM and retry (max N).

Step 5 - executor.py:
  * Prefer the Python `config` module for structured results:
        import config
        db = config.Configuration("oksconflibs:<data-file>")
        objs = db.get_objs(class, query)
  * Return a clean list of {id, attributes} dicts (NOT raw oks_dump text).
  * Support a `version` argument to select a commit hash / CVMFS snapshot.

Step 6 - interpreter.py:
  * Take the clean result list and produce a natural-language summary.
  * State the object count, list key objects, and (for temporal queries)
    which version was queried and what changed.

Step 7 - pipeline.py:
  * Wire Steps 2-6 into `answer(question, version=None) -> str`.

Step 8 - eval_dataset.jsonl + benchmark.py + ablation.py:
  * Populate >=20 shifter questions across easy/medium/hard.
  * benchmark.py executes each generated query and compares result sets.
  * ablation.py toggles components on/off and records accuracy per stage.

========================================================================
FEW-SHOT EXAMPLES & REFERENCE DATA (discover from the repo)
========================================================================
The few-shot examples and supporting reference data have ALREADY been
scraped and committed to the ROOT of this repository. Do NOT hardcode
examples in the prompt. Instead:

1. Discover the scraped data:
   - Search the repo root for scraped few-shot / example files, e.g.:
       ls -la .
       find . -maxdepth 2 -iname "*few*shot*" -o -iname "*example*" \
              -o -iname "*scraped*" -o -iname "*.jsonl" -o -iname "*.json"
   - Look for files like few_shot.jsonl, examples.json, scraped_queries.*,
     or any dataset directory at the repo root.

2. Load them dynamically in prompt_builder.py:
   - Read the scraped file(s) at runtime.
   - Parse each record into {question, class, query_oks, note}.
   - Inject the parsed examples into the prompt.

3. Fall back gracefully:
   - If no scraped file is found, log a warning and use a minimal
     built-in default set (so the module still runs).

Example loader (adapt to the actual scraped format you find):
   def load_few_shot(path="few_shot.jsonl"):
       examples = []
       with open(path) as f:
           for line in f:
               examples.append(json.loads(line))
       return examples

========================================================================
ACCEPTANCE CRITERIA
========================================================================
- `answer(question)` returns a correct, readable answer for easy/medium queries.
- Valid-syntax rate >= 90% on the evaluation dataset.
- Result-set accuracy reported per difficulty level.
- Benchmark report includes the error-taxonomy breakdown.
- Ablation shows monotonic improvement as components are added.
- No full-configuration dump ever enters an LLM prompt (filtering enforced).
- Code is importable: `from oksquery_translator.pipeline import answer`.

========================================================================
BEGIN
========================================================================
Start by probing the environment (Step 1), then create the package skeleton,
then implement each module in order. After each module, write a quick test
that proves it works before moving on. Report progress after each step.
```

---
*Appended: Master agent prompt to build the complete Text-to-OksQuery system.*