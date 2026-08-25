# Draft update for the final report

> This is a review draft only. It has not been integrated into
> `final_report/final_report.tex`. It is based on the implementation in the
> `rhythm` and `origin/feature/mcp-server` branches, while the report itself
> remains on the `report` branch.

## 3.1 Project Approach

The project followed an incremental and iterative development approach built
around the existing ATLAS TDAQ Object Kernel Support (OKS) database and native
query tools. The work began with a basic translation prototype and was extended
through successive increments, including prototype refinement, version-aware
configuration support, structured validation, query execution, and MCP
integration. The work focused on a reliable translation layer rather than a new
database or query engine, while maintaining a read-only boundary for
configuration inspection.

### I. Domain and Runtime Analysis

The OKS object model, OksQuery grammar, schema and data files, Python `config`
binding, and `oks_dump` command were examined first. Current and historical
configuration access was also considered because classes and attributes may
vary between TDAQ releases or revisions. This established the query vocabulary,
supported relationships, version selectors, and runtime requirements.

### II. Version-Scoped Context and Retrieval

For each request, the system resolves the selected configuration and creates an
`OksContext` containing version metadata and a content-derived schema
fingerprint. The question is analysed for intent, run information, and relevant
terms. Exact and lexical matching, synonym hints, attribute inspection, and
relationship expansion then produce a compact, version-matched schema slice.
This schema-RAG step grounds generation without sending the complete OKS schema
to the language model.

### III. Structured Translation and Validation

The language model generates a JSON intermediate representation describing the
target class, scope, comparisons, logical operators, and relationships. The
representation is deterministically normalised and checked against the active
schema for valid classes, attributes, case-sensitive names, inherited members,
relationship targets, and nested expressions. Failed validation produces a
focused diagnostic for a bounded repair loop. A deterministic compiler then
converts the validated representation into the executable OksQuery expression.

### IV. Execution and MCP Integration

The query is executed through the Python `config` interface or the `oks_dump`
fallback, and structured results are returned with query, version, target class,
and status metadata. The pipeline is exposed through a stateless MCP service
with tools for querying, translation without execution, and environment
inspection. Conversation history remains with the calling agent, while the
service enforces input, version, result, and read-only limits.

### V. Verification and Evaluation

Unit, integration, and MCP contract tests verify the pipeline components. The
project 
