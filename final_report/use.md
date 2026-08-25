# Comprehensive Technical Reference: Text-to-OksQuery Translation Module
## Agent Knowledge Base for Final Report Generation

> **Purpose:** This document contains all technical concepts, architectural decisions, and implementation details discussed during the development of the Text-to-OksQuery Translation Module project. It is intended as a complete reference for generating the final project report. Every section below contains factual, implementation-verified information that should be reflected in the report.

---

## Table of Contents

1. [The ATLAS DAQ System and Configuration Management](#1-the-atlas-daq-system-and-configuration-management)
2. [Object Kernel Support (OKS) Framework](#2-object-kernel-support-oks-framework)
3. [OksQuery Language](#3-oksquery-language)
4. [Configuration Versioning and Git-Based Service](#4-configuration-versioning-and-git-based-service)
5. [The Translation Module Architecture](#5-the-translation-module-architecture)
6. [Schema-RAG: Retrieval-Augmented Generation for Schema](#6-schema-rag-retrieval-augmented-generation-for-schema)
7. [AST Generation and Validation Pipeline](#7-ast-generation-and-validation-pipeline)
8. [Model Context Protocol (MCP) Server](#8-model-context-protocol-mcp-server)
9. [Deployment: SSH-Based Hosting and Port Tunneling](#9-deployment-ssh-based-hosting-and-port-tunneling)
10. [Evaluation Methodology](#10-evaluation-methodology)
11. [Error Taxonomy](#11-error-taxonomy)
12. [Ablation Study Design](#12-ablation-study-design)
13. [Key Design Decisions and Rationale](#13-key-design-decisions-and-rationale)
14. [References](#14-references)

---

## 1. The ATLAS DAQ System and Configuration Management

### 1.1 The ATLAS Experiment and DAQ

The ATLAS experiment at CERN's Large Hadron Collider (LHC) operates one of the most complex data acquisition (DAQ) systems in scientific computing. This system manages thousands of hardware and software components that must be configured, monitored, and controlled in real time during LHC runs. The configuration spans:

- **Detector electronics** — front-end readout hardware
- **Readout chains** — data flow from detector to storage
- **Trigger algorithms** — real-time event selection logic
- **Computing farms** — processing clusters and their interconnections
- **Run Control** — software that orchestrates the DAQ during a run

All of this configuration is stored and managed through the **Object Kernel Support (OKS)** framework.

### 1.2 The TDAQ System

OKS is built specifically for the ATLAS **Trigger and Data Acquisition (TDAQ)** system. TDAQ is the overarching system responsible for:

- Selecting interesting physics events from the ~40 MHz collision rate
- Reading out detector data for selected events
- Assembling events from multiple detector fragments
- Monitoring the health of the detector and DAQ electronics
- Controlling all hardware and software during a run

The configuration of TDAQ is inherently complex because it must describe:
- Physical hardware topology (racks, crates, boards, computers)
- Software application topology (processes, services, communication channels)
- Relationships between hardware and software (which application runs on which computer)
- Operational parameters (timeouts, thresholds, buffer sizes)
- Inheritance hierarchies (specialized classes extending base classes)

### 1.3 Evolution of Configuration Management

The management of ATLAS DAQ configuration has evolved significantly:

**Early systems (pre-2007):** Monolithic database services that struggled with scale and complexity. Alexandrov et al. (2007) identified the fundamental challenge: the online configurations database service must simultaneously provide fast read access to thousands of DAQ processes at run start, support concurrent editing by configuration experts, maintain version control for reproducibility, and ensure atomic transitions between configurations [Ref: Alexandrov et al., J. Phys. Conf. Ser. 119:022004, 2007].

**LHC Run 3 (2022+):** Adoption of a Git-based configuration service that brought distributed version control, branching, tagging, and full provenance tracking to the ATLAS DAQ configuration [Ref: "The git based ATLAS data acquisition configuration service in LHC Run 3"]. Under this architecture:
- Every configuration state is a Git commit
- Every run is associated with a specific revision
- The entire history of the detector configuration is queryable
- Multiple configurations can coexist via branching
- Reproducibility is guaranteed by commit hashes

---

## 2. Object Kernel Support (OKS) Framework

### 2.1 What is OKS?

OKS (Object Kernel Support) is a **persistent in-memory object database** purpose-built for the ATLAS TDAQ system. It provides a schema-driven, object-oriented configuration model [Ref: "The OKS persistent in-memory object manager"].

Key characteristics:
- **Persistent:** Configuration data survives process restarts via XML file storage
- **In-memory:** Objects are loaded into RAM for fast access during run operations
- **Object-oriented:** Uses classes, attributes, relationships, inheritance
- **Schema-driven:** All data conforms to a predefined schema
- **Version-controlled:** Configurations are tracked via Git

### 2.2 Core Concepts

**Classes:** The fundamental building blocks of the OKS schema. Each class defines:
- A unique name (e.g., `Application`, `Computer`, `Segment`)
- A set of attributes (typed properties)
- Relationships to other classes
- Optional superclass (for inheritance)
- Optional description

**Attributes:** Typed properties of a class. Each attribute has:
- A name (e.g., `InitTimeout`, `Name`, `Host`)
- A type (u8, u16, u32, u64, i8, i16, i32, i64, f32, f64, bool, string, enum, date)
- An optional initial value
- An optional range constraint
- An optional description
- A multi-value flag (can it hold multiple values?)
- An is-not-null flag (is it mandatory?)

**Relationships:** Named connections between classes. Each relationship has:
- A name (e.g., `RunsOn`, `Contains`, `HasBackup`)
- A target class type
- A cardinality (one-to-one, one-to-many, many-to-many)
- A description
- Can be composite (ownership) or non-composite (reference)

**Inheritance:** Classes can extend superclasses:
- Child classes inherit all attributes and relationships of their parent
- Multiple levels of inheritance are supported
- The "effective members" of a class include all inherited members

**Objects:** Instances of classes with specific attribute values. Objects have:
- A unique identifier (UID)
- Values for each defined attribute
- References to related objects via relationships

### 2.3 OKS Data Storage

OKS stores data in XML files:
- **Schema files (`*.schema.xml`):** Define classes, attributes, relationships, and inheritance
- **Data files (`*.data.xml`):** Define object instances with attribute values

The data files reference the schema files and can include other data files, creating a hierarchical include structure. A typical ATLAS configuration consists of hundreds of interconnected XML files.

### 2.4 The Scale of the ATLAS Configuration

The full ATLAS TDAQ configuration comprises:
- **500+ schema classes** (the exact number varies by TDAQ release and partition; a standard environment probe discovers approximately 518 classes)
- **Thousands of configuration objects** (instances of those classes)
- **Multiple inheritance hierarchies** (e.g., `Application → BaseApplication → TestableObject`)
- **Dozens of relationship types** connecting classes

This scale is the fundamental reason why the full configuration cannot be loaded into an LLM's context window.

### 2.5 Accessing OKS Data

OKS data can be accessed through:

1. **C++ API:** The native interface, used by the TDAQ online system
   - `OksKernel` class: loads configuration, provides query execution
   - `OksClass`, `OksObject`, `OksAttribute` classes: schema and data access
   - `OksQuery` class: executes OksQuery strings against loaded data

2. **Python `config` module:** Python bindings wrapping the C++ API
   - `config.Configuration("oksconflibs:<file>")`: loads a configuration
   - `db.classes()`: lists all class names
   - `db.attributes(class_name)`: gets attributes of a class
   - `db.relations(class_name)`: gets relationships of a class
   - `db.get_objs(class_name, query)`: executes a query and returns matching objects

3. **`oks_dump` CLI tool:** Command-line utility for inspecting OKS data
   - `oks_dump -c <ClassName> <data-file>`: dumps a class definition and its objects
   - `oks_dump -f <data-file>`: lists included files
   - Exit codes: 0=OK, 1=bad parameter, 2=bad file, 3=bad query, 4=class not found, 5=dangling references

---

## 3. OksQuery Language

### 3.1 Overview

OksQuery is the proprietary query language used to filter and retrieve objects from the OKS database. It employs a strict, S-expression-like syntax based on filter clauses. The language is:
- **Proprietary:** Not documented in any public LLM training corpus
- **Strict:** Syntax errors cause immediate rejection
- **Typed:** Operators must match attribute types
- **Class-scoped:** Queries target a specific class
- **Relationship-aware:** Can traverse relationships between classes

### 3.2 Syntax Structure

The general form of an OksQuery is:

```
(all | this  <expression>)
```

Where:
- `all` searches the target class AND all its subclasses
- `this` searches ONLY the target class (no subclasses)

### 3.3 Expressions

**Attribute comparison:**
```
("<attribute_name>" "<value>" <operator>)
```
Example: `("InitTimeout" "2" >)`

**Object ID comparison:**
```
(object-id "<id>" <operator>)
```

**Logical operators:**
```
(and <expr1> <expr2> ...)
(or <expr1> <expr2> ...)
(not <expr>)
```

**Relationship traversal:**
```
("<relationship_name>" some | all  <sub-expression>)
```
- `some`: at least one related object must match
- `all`: all related objects must match

### 3.4 Operators

| Operator | Meaning | Applicable Types |
|---|---|---|
| `=` | Equal | All types |
| `!=` | Not equal | All types |
| `<` | Less than | Numeric types only |
| `>` | Greater than | Numeric types only |
| `<=` | Less than or equal | Numeric types only |
| `>=` | Greater than or equal | Numeric types only |
| `~=` | Regular expression match | String type only |

### 3.5 Type Constraints

Operators are type-constrained:
- **Numeric types (u8–u64, i8–i64, f32, f64):** `=`, `!=`, `<`, `>`, `<=`, `>=`
- **String type:** `=`, `!=`, `~=`
- **Boolean type:** `=`, `!=`
- **Enum type:** `=`, `!=`

Using a numeric operator on a string attribute is a type error that will cause query rejection.

### 3.6 Example Queries

```
; Find executables with init timeout greater than 2 seconds
(all ("InitTimeout" "2" >))

; Find applications named "App1"
(all ("Name" "App1" =))

; Find applications running on computer "pc01"
(all ("RunsOn" some (object-id "pc01" =)))

; Find objects with specific timeout AND name
(all (and ("InitTimeout" "30" =) ("ExitTimeout" "5" =)))

; Find applications whose name contains "trigger"
(all ("Name" ".*trigger.*" ~=))

; Find only direct instances (not subclasses)
(this ("Name" "pc01" =))
```

### 3.7 Why LLMs Cannot Generate OksQuery Natively

1. **Absent from training data:** OksQuery is proprietary to ATLAS TDAQ and does not appear in public corpora
2. **Strict syntax:** Even minor formatting errors (missing quotes, wrong parentheses) cause rejection
3. **Schema-dependent:** Valid class names, attribute names, and relationship paths depend on the specific TDAQ release
4. **Type-sensitive:** Operator selection depends on attribute type, which requires schema knowledge
5. **Version-specific:** A class/attribute valid in one release may not exist in another

---

## 4. Configuration Versioning and Git-Based Service

### 4.1 The Git-Based Configuration Service

Since LHC Run 3, the ATLAS DAQ configuration is managed via a Git-based service. This means:

- The entire configuration is stored in a Git repository
- Every modification creates a new commit
- Each commit has a unique hash (e.g., `6800fe3b`)
- Runs are associated with specific commits
- Tags mark release points (e.g., `tdaq-14-00-00`)
- Branches allow parallel development of configurations

### 4.2 Version Selectors

A query can target a specific version using one of these selectors:

| Selector | Example | Meaning |
|---|---|---|
| TDAQ release | `tdaq-14-00-00` | A frozen snapshot bundled with software |
| Git tag | `r12345@ATLAS` | A named configuration state |
| Git commit | `6800fe3b` | An exact point in history |
| Run number | `380689` | Resolved to the config used by that run |
| Configuration revision | `abc123` | A specific configuration version |
| Default (none) | — | Currently loaded configuration |

### 4.3 The Schema Fingerprint

To uniquely identify a configuration state, the system computes a **schema fingerprint**:

```
<release>:<git-revision>:<schema-root-hash>
```

This fingerprint is used for:
- Filtering retrieval results (no cross-version contamination)
- Caching (same fingerprint = same schema)
- Validation diagnostics
- Provenance tracking
- Logging

### 4.4 The Schema-Context Invariant

**This is the most critical architectural principle:**

> Every retrieval, schema expansion, LLM context, validation, repair, compilation, and execution operation for a query must use the same resolved OksContext. No schema information from another release, Git revision, configuration, or run may be used.

This means:
- If a user asks about `tdaq-13`, the system must ONLY use classes/attributes from `tdaq-13`
- A class that exists in `tdaq-14` but not `tdaq-13` must NOT be suggested
- The validator checks against the SAME schema the retriever used
- The repair loop uses the SAME schema evidence

### 4.5 OksContext

The `OksContext` is an immutable object that binds together:

```python
class OksContext:
    release: str | None           # e.g., "tdaq-14-00-00"
    git_revision: str | None      # e.g., "6800fe3b"
    run_number: int | None        # e.g., 380689
    configuration_revision: str | None
    schema_identifier: str        # unique ID for this schema
    schema_fingerprint: str       # "<release>:<git-rev>:<schema-hash>"
    kernel: OksKernel             # the version-bound OKS kernel
```

Every downstream component receives this context and never reconstructs version state independently.

---

## 5. The Translation Module Architecture

### 5.1 High-Level Pipeline

The translation module converts natural language to validated OksQuery through a multi-stage pipeline:

```
User Question (Natural Language)
    │
    ▼
[1] Query Preprocessor
    │  Normalizes text, extracts entities, detects intent
    ▼
[2] Schema Retrieval (Schema-RAG)
    │  Finds relevant classes using version-scoped lexical search
    ▼
[3] Schema Context Builder
    │  Constructs the minimal schema slice for the LLM
    ▼
[4] Prompt Builder
    │  Assembles: instructions + AST schema + context + examples + question
    ▼
[5] LLM Generator
    │  Produces a JSON AST (not raw OksQuery)
    ▼
[6] AST Normalizer
    │  Canonicalizes operators, paths, values, structure
    ▼
[7] AST Validator
    │  Checks AST against the version-bound schema
    │  ┌─── VALID ───────────────────┐
    │  │                              │
    ▼  ▼                              │
INVALID?                              │
    │                                 │
    ▼                                 │
[8] Repair Engine (max 2 retries)     │
    │  Sends focused feedback to LLM  │
    │  Gets corrected AST             │
    └──► Re-validate ────────────────►│
                                      ▼
[9] OKSQuery Compiler
    │  Deterministically converts AST → OksQuery string
    ▼
[10] Execution
    │  Native C++ OksQuery engine executes the query
    ▼
Results returned to user/agent
```

### 5.2 Why AST Instead of Raw OksQuery?

The system generates an intermediate **Abstract Syntax Tree (AST)** rather than having the LLM output raw OksQuery strings directly. Reasons:

1. **Inspectable:** Each component (root class, filter, path, operator, value) can be validated independently
2. **Normalizable:** LLM quirks (e.g., writing `"equals"` instead of `"=="`) can be corrected before validation
3. **Unambiguous:** No need to parse the LLM's syntax output; the JSON structure is explicit
4. **Repairable:** When validation fails, specific fields can be identified and corrected
5. **Separation of concerns:** The LLM decides *what* to query; the compiler decides *how* to express it in OksQuery syntax

### 5.3 AST Structure

```json
{
  "root_class": "Application",
  "scope": "all",
  "filters": [
    {
      "path": ["RunsOn", "Name"],
      "operator": "==",
      "value": "pc01"
    }
  ],
  "projection": ["Name"],
  "ordering": null,
  "limit": null
}
```

### 5.4 The Validate/Repair Loop

When the AST fails validation:

1. The validator produces a structured error (e.g., `INVALID_FIELD: RunOn does not exist on Application`)
2. The Repair Engine formats focused feedback including:
   - The specific error
   - The schema fingerprint (reinforcing version context)
   - Valid alternatives (e.g., "valid relationships include: RunsOn → Computer")
3. The LLM receives this feedback and produces a corrected AST
4. The corrected AST is re-validated
5. Hard limit: maximum 2 repair attempts before failing

---

## 6. Schema-RAG: Retrieval-Augmented Generation for Schema

### 6.1 What is Schema-RAG?

Schema-RAG is a specialized form of Retrieval-Augmented Generation where:
- The **retrieval corpus** is the live TDAQ OKS schema itself (not external documents)
- Retrieval is **version-scoped** (filtered by schema fingerprint)
- The retrieved content is a **schema slice** (1–3 relevant classes with attributes and relationships)
- The purpose is to give the LLM enough context to generate a valid AST without seeing the full 500+ class schema

### 6.2 Why Not Just Use the Full Schema?

- The full schema (500+ classes, thousands of attributes) far exceeds any LLM's context window
- Even if it fit, the noise would confuse the LLM
- Version-scoping requires filtering anyway

### 6.3 The Retrieval Pipeline (Cascading Order)

The retrieval follows a strict cascading order:

1. **Exact Lookup:** Match class names exactly (e.g., user says "Application" → class `Application`)
2. **Alias/Token Lookup:** Match synonyms and tokens (e.g., "apps" → `Application`, "machines" → `Computer`, "host" → `Computer`)
3. **FTS/BM25:** Full-text search over class search documents using BM25Okapi
4. **Optional Embeddings:** (Last resort, never first) Vector similarity for fuzzy matching

**Critical rule:** Embeddings are NEVER the first retrieval step. They are optional and only used when earlier stages don't find enough candidates.

### 6.4 The Retrieval Index

Each class is indexed as a `ClassSearchDocument`:

```json
{
  "schema_identifier": "<schema-id>",
  "schema_fingerprint": "<fingerprint>",
  "git_revision": "<git-revision>",
  "configuration_revision": "<config-revision>",
  "class_name": "Application",
  "tokens": ["application", "app"],
  "description": "...",
  "relationships": ["RunsOn", "BackupHosts"],
  "relationship_targets": ["Computer"],
  "attributes": ["Name", "Parameters", "Logging"]
}
```

The index is partitioned by `schema_fingerprint`. Every search query includes the fingerprint as a mandatory filter, ensuring no cross-version results are returned.

### 6.5 Keyword-to-Class Synonym Map

The implementation maintains a synonym dictionary mapping natural language terms to OKS class names:

| User Term | Maps To |
|---|---|
| "application", "app", "applications" | Application, BaseApplication, RunControlApplication |
| "executable", "binary" | Executable, Binary |
| "computer", "host", "machine" | Computer |
| "segment" | Segment, OnlineSegment |
| "partition" | Partition |
| "timeout", "inittimeout" | BaseApplication, Executable |
| "trigger" | DFTriggerIn |
| "readout", "ros" | ROSDescriptor, ReadoutApplication |
| "repository" | SW_Repository |
| "software", "program" | SW_Object, ComputerProgram |
| "container" | Container |
| "control", "controller", "rc" | RunControlApplication, RunControlApplicationBase |

### 6.6 Context Expansion Rules

After initial retrieval, the context builder applies expansion rules:

1. **Expand only what is needed:** If `Application` requires `BaseApplication` (because a relationship is inherited), include it. Do not include all 500+ classes.
2. **One-hop relationship expansion:** If `Application.RunsOn → Computer`, retrieve `Computer`. Only expand further if the query requires it.
3. **Context pruning:** If `Application` has 30 attributes but the question only concerns `RunsOn` and `Name`, do not send unrelated attributes.
4. **Context consistency:** All classes, attributes, relationships, and types must come from the SAME OksContext. Mixed-context expansion is a correctness failure.

### 6.7 What Makes This "Lexical/Keyword RAG"

The implementation uses:
- **BM25Okapi** (from the `rank_bm25` library) for lexical retrieval
- **Synonym hints** for vocabulary bridging
- **No vector embeddings or vector databases**
- The knowledge base is the **live TDAQ OKS schema itself** plus curated few-shot examples

This is "schema-RAG for text-to-query" — a specialized RAG where the corpus is a structured schema rather than prose documents.

---

## 7. AST Generation and Validation Pipeline

### 7.1 The LLM's Role

The LLM's ONLY job is to translate natural language into a JSON AST. It does NOT:
- Write raw OksQuery syntax
- Decide operator formatting
- Handle schema versioning
- Execute queries

The LLM receives:
- Instructions (what to do, what NOT to do)
- The AST schema definition
- OksContext metadata (release, fingerprint)
- The retrieved schema context (1–3 classes)
- Few-shot examples (tagged with compatible schema fingerprint)
- The user's exact original question

### 7.2 AST Normalization

After the LLM produces an AST, the normalizer enforces canonical form:

| LLM Output | Canonical Form |
|---|---|
| `"equals"`, `"="`, `"is equal to"` | `"=="` |
| `"greater than"`, `">"` | `">"` |
| `RunsOn.Name` | `["RunsOn", "Name"]` |
| `"10"` (when schema says u32) | `10` |
| `{"filters": "hello"}` | REJECTED (filters must be array) |

### 7.3 Validation Checks

The validator checks the AST against the version-bound schema:

1. **Root class exists?** — Is the root class defined in this schema fingerprint?
2. **Projection fields exist?** — Do all projected attributes exist on the class (including inherited)?
3. **Filter fields exist?** — Do all filter paths resolve to valid attributes/relationships?
4. **Relationships exist?** — Are relationship names valid for this class?
5. **Relationship targets exist?** — Do relationship targets point to valid classes?
6. **Inheritance resolved?** — Are inherited members correctly attributed?
7. **Path valid?** — Is the full path (e.g., `RunsOn → Computer → Name`) valid?
8. **Operators valid?** — Is the operator applicable to the attribute type?
9. **Value types correct?** — Does the value match the expected type?
10. **Multiplicity correct?** — Are multi-value attributes handled correctly?

### 7.4 Validation Example

```
LLM generates: Application.RunOn
Validator asks: Does "RunOn" exist on Application in schema fingerprint <X>?
OKS says: NO
Error: INVALID_FIELD
  Schema fingerprint: <resolved-context-fingerprint>
  Requested: RunOn
  Possible: RunsOn
```

### 7.5 The Compiler

After validation passes, the compiler deterministically converts the AST to OksQuery:

```
Input AST:
{
  "root_class": "Application",
  "scope": "all",
  "filters": [{"path": ["RunsOn", "Name"], "operator": "==", "value": "pc01"}]
}

Output OksQuery:
(all ("RunsOn" some ("Name" "pc01" =)))
```

**Critical rule:** The compiler NEVER asks the LLM how to write the syntax. It is purely deterministic code.

---

## 8. Model Context Protocol (MCP) Server

### 8.1 What is MCP?

The Model Context Protocol (MCP) is a standardized protocol for connecting LLM-based agents to external tools and data sources. It enables models to:
- Query databases
- Execute code
- Interact with services
- Access files and APIs

All through a unified interface without requiring the LLM to know implementation details.

### 8.2 MCP in This Project

The translation module is deployed as an MCP server that:
- Accepts natural language questions from LLM agents
- Translates them to OksQuery via the pipeline described above
- Executes queries against the OKS database via the C++ backend
- Returns results to the agent

The MCP server acts as a **tool** that the LLM agent can call, similar to how an agent might call a search API or a code executor.

### 8.3 Why MCP?

- **Standardized interface:** Any MCP-compatible agent can use the server
- **Encapsulation:** The agent doesn't need to know OksQuery syntax
- **Security:** The agent never directly accesses the OKS database
- **Context efficiency:** The agent doesn't need the full schema in its context
- **Version management:** The server handles version resolution internally

### 8.4 MCP Server Architecture

```
External LLM Agent
    │
    │ (MCP Protocol over HTTP/SSE)
    ▼
┌─────────────────────────────────┐
│  MCP Server (Python)            │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Translation Module       │   │
│  │  - Schema Retrieval      │   │
│  │  - Prompt Building       │   │
│  │  - LLM Generation       │   │
│  │  - AST Validation       │   │
│  │  - Repair Loop          │   │
│  │  - Compilation          │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Execution Backend        │   │
│  │  - Python config module  │   │
│  │  - (fallback: oks_dump)  │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
    │
    │ (C++ OksQuery engine)
    ▼
OKS Database (XML files / In-memory kernel)
```

### 8.5 Execution Backend

The executor uses a dual-strategy approach:
1. **Primary:** Python `config` module (which binds to the C++ OKS kernel)
2. **Fallback:** CLI `oks_dump` binary (if the config module isn't available)

This ensures the system works across different environment configurations.

---

## 9. Deployment: SSH-Based Hosting and Port Tunneling

### 9.1 The Deployment Challenge

The MCP server must run within CERN's computing environment (to access the OKS database and TDAQ releases) but needs to be accessible to external LLM agents that may not reside inside the CERN network perimeter.

### 9.2 The Solution: SSH Port Tunneling

The system is deployed using SSH port forwarding:

```bash
ssh -L <local_port>:localhost:<remote_port> <user>@lxplus.cern.ch
```

This creates a secure tunnel:
- The MCP server runs on a CERN compute node (e.g., LXPLUS)
- Its HTTP/SSE endpoint is exposed through the SSH tunnel
- External agents connect to `localhost:<local_port>` on their machine
- Traffic is securely forwarded to the MCP server inside CERN

### 9.3 Deployment Architecture

```
External LLM Agent (outside CERN)
    │
    │ Connects to localhost:8080
    ▼
SSH Tunnel (encrypted)
    │
    │ Forwards to CERN internal network
    ▼
MCP Server on LXPLUS/compute node
    │
    │ Accesses TDAQ releases via CVMFS
    ▼
/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/<release>/installed/
    │
    │ Loads OKS configuration
    ▼
OKS Database (schema + data XML files)
```

### 9.4 Environment Setup

Before running the MCP server, the TDAQ environment must be sourced:

```bash
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh
```

This sets up:
- PATH to include OKS tools (`oks_dump`, etc.)
- PYTHONPATH to include the `config` module
- Library paths for C++ OKS libraries
- Data paths for schema and configuration files

### 9.5 Security Considerations

- Authentication relies on CERN's SSH infrastructure (Kerberos/SSH keys)
- No additional authentication layer is implemented in the MCP server itself
- The SSH tunnel provides encryption in transit
- The server operates in read-only mode (no configuration modifications)
- Access control is delegated to CERN's institutional network perimeter

---

## 10. Evaluation Methodology

### 10.1 Evaluation Dataset

The evaluation dataset consists of:
- **Common shifter questions** paired with ground-truth OksQuery equivalents
- **Stratified by difficulty:** Easy (single attribute filter), Medium (multiple conditions or relationships), Hard (multi-hop relationships, complex logic)
- **Each record contains:** question, target class, ground-truth OksQuery, expected object IDs, expected count, source data file

### 10.2 Accuracy Measurement

**Critical principle:** Accuracy is measured by EXECUTING the generated query and comparing RESULT SETS to ground truth, NOT by comparing query text.

Two queries can be syntactically different but semantically equivalent:
```
(all ("InitTimeout" "2" >))
(all ("InitTimeout" "2" >=))  ; if no objects have exactly InitTimeout=2
```

Therefore, execution-based comparison is the only valid accuracy measure.

### 10.3 Metrics

| Metric | Definition |
|---|---|
| **Result-set accuracy** | % of queries where executed result set matches ground truth |
| **Valid-syntax rate** | % of generated queries that parse without syntax errors |
| **Execution success rate** | % of queries that execute successfully against the backend |
| **Repair success rate** | % of initially-invalid queries that become valid after repair |
| **Retrieval precision** | % of retrieved schema classes that are actually needed |

### 10.4 Error Taxonomy

When a query fails, the failure is classified:

| Error Type | Description | Example |
|---|---|---|
| `wrong_syntax` | Malformed OksQuery structure | Missing parentheses, unquoted strings |
| `wrong_class` | Selected incorrect root class | Used `Segment` instead of `Application` |
| `wrong_attribute` | Referenced non-existent attribute | Used `Timeout` instead of `InitTimeout` |
| `wrong_operator` | Used invalid operator for type | Used `>` on a string attribute |
| `wrong_scope` | Used wrong scope token | Used `this` instead of `all` |
| `missing_logic` | Dropped a required logical operator | Missing `and` between two conditions |
| `wrong_relationship` | Used non-existent relationship path | Used `HostedOn` instead of `RunsOn` |
| `wrong_value_type` | Value doesn't match attribute type | String value for u32 attribute |

### 10.5 Reporting Requirements

The benchmark report must include:
- Overall accuracy (result-set based)
- Valid-syntax rate
- Breakdown by difficulty level (easy/medium/hard)
- Breakdown by error taxonomy (not just pass/fail)
- Comparison across ablation stages

---

## 11. Error Taxonomy

### 11.1 Purpose

The error taxonomy provides a structured breakdown of failures, enabling:
- Identification of which component causes which error type
- Targeted improvements (e.g., if `wrong_class` is dominant, improve retrieval)
- Comparison across ablation stages
- Communication of results to stakeholders

### 11.2 Error Categories (Detailed)

**wrong_syntax:**
- The generated OksQuery string is malformed
- Examples: unbalanced parentheses, missing quotes, invalid nesting
- Usually caught by the normalizer/validator before execution
- Indicates the LLM failed to follow the AST schema correctly

**wrong_class:**
- The root class selected by the LLM is incorrect
- Example: User asks about applications, LLM generates query against `Segment`
- Indicates retrieval failed to surface the correct class, or the LLM ignored the schema context

**wrong_attribute:**
- An attribute referenced in the query does not exist on the target class
- Example: Using `Timeout` instead of `InitTimeout`
- Indicates the LLM hallucinated an attribute name not present in the schema context

**wrong_operator:**
- An operator is used that is invalid for the attribute type
- Example: Using `>` on a string attribute (only `=`, `!=`, `~=` are valid)
- Indicates the LLM didn't respect type constraints from the schema context

**wrong_scope:**
- The scope token (`all` vs `this`) is incorrect
- Example: Using `this` when subclasses should be included
- Indicates misunderstanding of the query semantics

**missing_logic:**
- A required logical operator is missing
- Example: Two conditions that should be combined with `and` are instead written as separate filters
- Indicates the LLM didn't correctly interpret the natural language conjunction

**wrong_relationship:**
- A relationship path references a non-existent relationship
- Example: Using `HostedOn` instead of `RunsOn`
- Indicates the LLM hallucinated a relationship name

**wrong_value_type:**
- The value provided doesn't match the expected attribute type
- Example: Providing `"hello"` for a `u32` attribute
- Indicates the LLM didn't respect type information from the schema context

---

## 12. Ablation Study Design

### 12.1 Purpose

The ablation study demonstrates the contribution of each architectural component by progressively adding them and measuring accuracy at each stage.

### 12.2 Stages

| Stage | Configuration | What it tests |
|---|---|---|
| B1 | Plain prompt only (no extras) | Raw LLM capability without any assistance |
| B2 | + Few-shot examples | Value of curated NL→OksQuery pairs |
| B3 | + Schema retrieval (Schema-RAG) | Value of injecting relevant schema context |
| B4 | + Validate/repair loop (full system) | Value of deterministic validation and repair |

### 12.3 Expected Results Pattern

```
B1 (Plain prompt):        ~10-20% accuracy  (LLM hallucinates everything)
B2 (+ Few-shot):          ~30-40% accuracy  (Format improves, schema still unknown)
B3 (+ Schema retrieval):  ~60-70% accuracy  (Correct classes/attributes, some logic errors)
B4 (+ Validate/repair):   ~75-85% accuracy  (Syntax errors eliminated, logic mostly correct)
```

### 12.4 Interpretation

- **B1→B2 gap:** Shows that few-shot examples teach the LLM the AST structure
- **B2→B3 gap:** Shows that schema retrieval provides the vocabulary (class/attribute names)
- **B3→B4 gap:** Shows that validation catches residual errors the LLM still makes

### 12.5 Hypothesis

The largest accuracy jump should be from B2→B3 (adding schema retrieval), because the fundamental problem is that the LLM doesn't know what classes/attributes exist. Few-shot examples teach format, but schema retrieval teaches content.

---

## 13. Key Design Decisions and Rationale

### 13.1 Why AST Instead of Raw OksQuery?

| Approach | Problem |
|---|---|
| LLM outputs raw OksQuery | Must parse LLM's syntax again; ambiguous; hard to validate piece by piece |
| LLM outputs JSON AST | Each component inspectable; normalizable; unambiguous; repairable |

The AST separates **query semantics** (what the user wants) from **query syntax** (how OksQuery expresses it). The LLM handles semantics; the compiler handles syntax.

### 13.2 Why Lexical RAG (BM25) Instead of Embeddings?

| Approach | Advantage | Disadvantage |
|---|---|---|
| BM25/Lexical | Fast, deterministic, no infrastructure needed, version-scoping trivial | Misses semantic synonyms |
| Embeddings/Vector | Captures semantic similarity | Requires vector DB, harder to version-scope, slower |

The project uses BM25 + synonym dictionary as the primary approach because:
- The schema vocabulary is technical and precise (not ambiguous prose)
- Version-scoping is trivial (just filter by fingerprint)
- No external infrastructure needed
- The synonym map handles the vocabulary gap

### 13.3 Why Deterministic Validation Instead of LLM Self-Check?

An LLM checking its own output is unreliable (it may "approve" hallucinated classes). The validator is deterministic code that queries the actual OKS kernel — it cannot hallucinate. If the kernel says `RunOn` doesn't exist on `Application`, the validator rejects it regardless of what the LLM thinks.

### 13.4 Why Read-Only?

The system operates strictly in read-only mode because:
- Writing to the live configuration could damage detector hardware
- Modifying configuration during a run could corrupt physics data
- Configuration changes require expert review and Git commit workflows
- An LLM should never have write access to safety-critical infrastructure

### 13.5 Why Stateless Server Design?

The MCP server is stateless by design (each request resolves its own OksContext) because:
- It enforces the Schema-Context Invariant (no stale cache contamination)
- It prevents cross-version bugs (one request can't accidentally use another's schema)
- Conversational state is managed by the consuming LLM agent, not the server
- It simplifies deployment (no session management, no database for sessions)

---

## 14. References

### 14.1 Primary References (for Background section)

[1] "The git based ATLAS data acquisition configuration service in LHC Run 3." *Journal of Physics: Conference Series*.
— Describes the Git-based configuration management adopted for LHC Run 3.

[2] Alexandrov, et al. "The ATLAS DAQ system online configurations database service challenge." *Journal of Physics: Conference Series*, 119:022004, 2007.
— Identifies the fundamental challenges of online configuration management.

[3] "The OKS persistent in-memory object manager." ATLAS TDAQ Technical Paper.
— Describes the OKS framework architecture and capabilities.

### 14.2 RAG/GraphRAG References (for Literature Review)

[4] Lewis, P., et al. "Retrieval-augmented generation for knowledge-intensive NLP tasks." *NeurIPS*, 2020.
— Introduces the RAG framework.

[5] Zhu, X., et al. "Knowledge Graph-Guided Retrieval Augmented Generation." *arXiv:2502.06864*, NAACL, 2025.
— Proposes KG²RAG: using knowledge graphs to guide retrieval expansion.

### 14.3 Architecture References

[6] Project Description: "Text-to-OksQuery Translation Module" — Minor Project specification.
[7] Architecture Specification: "NL→OKSQuery System Architecture: A Version-Scoped Deterministic Pipeline for Natural Language to Schema Query Translation" — August 2026.

---

## Appendix A: Glossary

| Term | Definition |
|---|---|
| ATLAS | A Toroidal LHC ApparatuS — one of the four major experiments at the LHC |
| DAQ | Data Acquisition — the system that reads out detector data |
| TDAQ | Trigger and Data Acquisition — the overarching ATLAS system |
| OKS | Object Kernel Support — the configuration database framework |
| OksQuery | The proprietary query language for filtering OKS objects |
| OksContext | Immutable object binding a specific schema/config version to a request |
| Schema Fingerprint | Unique identifier for a specific schema state |
| MCP | Model Context Protocol — standardized protocol for LLM tool access |
| AST | Abstract Syntax Tree — intermediate JSON representation of a query |
| Schema-RAG | RAG where the retrieval corpus is the OKS schema itself |
| BM25 | Best Matching 25 — a lexical ranking function for information retrieval |
| LHC | Large Hadron Collider — the particle accelerator at CERN |
| CVMFS | CERN Virtual Machine File System — distributes software releases |
| LXPLUS | CERN's login cluster for interactive computing |
| Shifter | An operator monitoring the detector during a physics run |
| Run | A period of data-taking by the ATLAS experiment |
| Partition | A subset of the detector configured for a specific purpose |

---

## Appendix B: Key Numbers

| Metric | Value |
|---|---|
| Number of OKS schema classes | ~500+ (varies by release; ~518 in standard probe) |
| Number of configuration objects | Thousands |
| Maximum classes in LLM context | 1–3 (schema slice) |
| Maximum repair attempts | 2 |
| Retrieval cascade stages | 4 (Exact → Alias → BM25 → Embeddings) |
| AST validation checks | 10+ |
| OksQuery operator types | 7 (`=`, `!=`, `<`, `>`, `<=`, `>=`, `~=`) |
| Attribute types | 15+ (u8–u64, i8–i64, f32, f64, bool, string, enum, date) |

---

*End of Technical Reference Document*
*This document should be used as the primary source for generating the final project report. All technical claims herein are implementation-verified.*