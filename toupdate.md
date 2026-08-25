# Draft update for the final report

> This draft is retained as an editable record. Sections 3.1, 3.3, and 3.4
> have now been integrated into `final_report/final_report.tex`; Section 3.2
> remains reserved for the system-architecture contribution.

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
translation accuracy is evaluated against the project evaluation dataset.

## 3.3 System Design and Modules

The system was designed as a layered pipeline in which each module has a
separate responsibility. A natural-language question is first processed by the
intent and preprocessing modules. The version resolver identifies current or
historical configuration requirements, while the context builder creates the
version-scoped `OksContext` and schema fingerprint.

The schema layer retrieves the relevant OKS classes, attributes, inherited
members, and relationships. It uses the active schema and lexical matching to
construct a compact context for the language model. The prompt and few-shot
modules then combine this context with OksQuery rules and suitable examples.

The translation layer converts the question into a JSON intermediate
representation. The `oks_ast` modules normalise the representation, validate
its structure and schema semantics, and compile it deterministically into an
OksQuery expression. If validation fails, the translator sends the diagnostic
through a bounded repair loop before compilation.

The execution layer runs the compiled query using the Python `config` binding or
the `oks_dump` fallback. It converts returned objects into structured records
and preserves query, version, target-class, count, and status information. The
`OksPipeline` coordinates intent detection, context construction, translation,
execution, and optional result interpretation.

For external access, the MCP layer adds an `OksQueryService` and a thin MCP
adapter. The `oks_query` tool performs translation and execution, while
`oks_translate` provides translation without execution and
`oks_environment_probe` reports runtime readiness. The service is stateless;
conversation history belongs to the calling agent. It also applies input
validation, result limits, version checks, request serialisation, and the
read-only service boundary. No separate application database or mutation API is
required; configuration data remains in the OKS/TDAQ environment.

The associated report figures are stored in `final_report/`: the use-case,
data-flow, sequence, and class diagrams. They are referenced in Section 3.3 of
the integrated report.

## 3.4 Technology Stack

The system uses the following technologies to support OKS integration,
structured translation, and MCP service delivery:

I. **Python.** Python 3.10 or later is used for the pipeline, service layer,
schema processing, validation, and testing.

II. **OKS/TDAQ integration.** The TDAQ Python `config` binding provides the
primary execution interface, with `oks_dump` as a fallback and diagnostic tool.

III. **LLM and structured validation.** The `openai` package connects to an
OpenAI-compatible endpoint. JSON, Pydantic, and the project `oks_ast` modules
support normalisation, semantic validation, repair, and deterministic
compilation.

IV. **Schema retrieval.** Versioned OKS schemas and Git/runtime metadata provide
context. Lexical retrieval and `rank_bm25` identify relevant classes,
attributes, and relationships.

V. **MCP and deployment.** The Python MCP SDK with FastMCP exposes the query,
translation, and environment-probe tools through `stdio` or Streamable HTTP.
Environment variables, `python-dotenv`, SSH, and `tmux` support configuration
and deployment.

VI. **Testing.** `pytest` is used for unit, integration, service, pipeline, and
MCP contract tests.
