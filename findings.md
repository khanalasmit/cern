# Repository Findings

This file records evidence gathered while analyzing the repository for the MCP deployment plan.

## Initial discovery

- The implementation checkout is on branch `feature/mcp-server`, based on the latest locally known `origin/rhythm` tip; verify the remote SHA before pushing or deploying.
- The repository contains a package named `oksquery_translator/`, which is the primary candidate for MCP integration.
- A separate `translator_module/` also exists and has a different/older implementation path; it should not be assumed to be the production target without team confirmation.
- The repository includes OKS schema/data fixtures, evaluation datasets, architecture documents, and CERN/TDAQ research notes.
- The user successfully SSHed to `lxplus9112.cern.ch` as `cshah` on 2026-08-24.

## Current application architecture

The primary `oksquery_translator/` package already implements the intended data path:

1. `SchemaRetriever` discovers the live class list and loads a small schema slice using the Python `config` module, `oks_dump`, or XML fallback.
2. `FewShotManager` loads and BM25-selects examples from `combined_data/all_few_shot.jsonl`, then falls back to curated files or built-ins.
3. `PromptBuilder` combines OKS syntax rules, the schema slice, few-shot examples, and the user question.
4. `Translator` calls an OpenAI-compatible LLM, parses `CLASS:`/`QUERY:`, validates the query, and retries with engine/schema feedback.
5. `Executor` runs the validated query through Python `config` first or `oks_dump` second, returning capped structured objects.
6. `Interpreter` makes a second LLM call using only the filtered result objects and has a local fallback answer.
7. `OksPipeline.answer()` orchestrates translation → execution → interpretation; `translate_only()` exposes only translation.
8. `oksquery_translator/cli.py` provides an interactive shell with `translate`, `version`, `probe`, and full-answer commands.

## Remaining deployment gaps after the local MCP implementation

- The first transport is implemented as stdio; no production HTTP/Streamable HTTP deployment, health endpoint, or agent connection configuration has been added yet.
- No conversation/session memory exists in the primary `oksquery_translator` package by design; the external agent owns it.
- No authentication/authorization or per-client isolation exists at a service boundary.
- No systemd/container/CI deployment or SSH bootstrap exists; `deploy/run_mcp.sh` is the current launcher.
- The real TDAQ runtime is external: `config`, `oks_dump`, CVMFS, data files, and release setup are expected on the target device.

## Important service-boundary risks

- `Executor.execute()` accepts a `data_file` configured by the application; an MCP tool must not let an agent choose arbitrary filesystem paths.
- `version` changes process environment variables (`TDAQ_DB_VERSION` or `TDAQ_DB_PATH`) for a request. A concurrent server needs request isolation or a serialized/version-aware execution strategy.
- The LLM output is validated before execution, but MCP input still needs strict limits for question length, class/version values, result count, and request timeouts.
- Interpreter prompts include returned object attributes. Result caps, redaction policy, and audit logging are needed before exposing this to multiple users.
- The CLI's current interactive state has no conversation memory; follow-up support must be added to the service/session layer rather than relying on CLI globals.

## Intended runtime from repository documentation

- SSH target described in `breif.md`: `lxplus.cern.ch`.
- The user's successful login resolved the alias to `lxplus9112.cern.ch`, running Red Hat Enterprise Linux 9.8 (Plow).
- The user account is `cshah`.
- Expected setup: source a TDAQ release from CVMFS, then use `config` and/or `oks_dump`.
- LXPLUS is documented as using CVMFS snapshots for older versions rather than reaching the live OKS Git server.
- SSH access is confirmed, but the repository/session still does not confirm the TDAQ release, filesystem permissions, outbound LLM access, or long-running service/network policy.
- The user then verified on the host: `python3 --version` is `3.9.25`, CVMFS contains `/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00`, and sourcing its `installed/setup.sh` completes for TDAQ Common SW and DAQ SW 14.00.00.
- The pasted output does not clearly show a path for `oks_dump` or the `config available` marker, so those two runtime checks need explicit exit-status diagnostics.
- The repository README documents Python 3.10 or newer, while the target shell currently reports Python 3.9.25. Check for another Python interpreter on LXPLUS before creating the deployment environment; otherwise test and explicitly approve Python 3.9 compatibility.

## MCP transport research

- The official Python SDK documents `stdio` for a host-launched local subprocess and Streamable HTTP for a deployed server listening on a port; new deployments should not start with legacy SSE. [Official SDK run documentation](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/run/index.md)
- The SDK can expose a server through an ASGI application, which allows deployment behind an appropriate process manager/reverse proxy when HTTP is required. [Official SDK ASGI documentation](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/run/asgi.md)
- For the first milestone, stdio is the lowest-risk option if the agent can SSH-launch the process. For a shared remote service, Streamable HTTP is the better target, but it requires authentication, network policy, concurrency handling, and deployment supervision.

## Local verification

- `pytest -q oksquery_translator/tests` passes: 183 tests pass and 9 optional tests skip when the MCP/TDAQ runtime is unavailable.
- The local CLI starts and loads 194 few-shot examples, but its environment probe reports `oks_dump: NOT FOUND`, `config mod: NOT available`, `schema dir: NOT FOUND`, and zero live classes. This is expected on the development machine and confirms that target-device runtime validation is still required.
- The local verification interpreter is Python 3.11.9 and provides MCP SDK 1.29.1 plus pytest. This is local verification only; it does not verify the real LXPLUS/TDAQ runtime.

## Friend's LXPLUS demo analysis

- The demo successfully SSHes from Windows PowerShell to `lxplus990.cern.ch` as user `khanal`, enters `~/private/my_tdaq_project/cern`, updates the `rhythm` branch, activates a package-local virtual environment, sources a TDAQ release, and runs the end-to-end CLI.
- The demonstrated checkout is newer/different from the original local `chandan` checkout: its `oksquery_translator/` contains additional `ast/`, `intent.py`, `context/`, `preprocessing/`, `retrieval/`, and `schema/` components. The MCP implementation now targets `feature/mcp-server` based on the latest locally known `rhythm` code rather than mixing branches.
- `python -m translator_module` fails because `translator_module/__main__.py` does not exist. This is not the MCP failure; it is an incorrect entry-point assumption.
- Running `python -m oksquery_translator` after sourcing TDAQ while the venv was already active selected the CVMFS Python/openai 0.27.8 and failed with `ImportError: cannot import name 'OpenAI'`. The package venv contains openai 3.3.1 and works when invoked explicitly as `oksquery_translator/venv/bin/python -m oksquery_translator`. The deployment launcher must make interpreter selection explicit or activate the venv after TDAQ setup.
- `pip install -r requirments.txt` failed because the filename was misspelled. The internal package has now been renamed from `ast/` to `oks_ast/`, so running tooling from inside `oksquery_translator/` no longer shadows Python's standard-library `ast` module.
- The demo sources TDAQ `prod` and reports TDAQ Common/DAQ 12.00.00, but the runtime probe uses an `oks_dump` binary from TDAQ 12.00.00 and a schema directory from TDAQ 14.00.00. Schema, `config`, `oks_dump`, data files, and setup release must be pinned to one consistent release before production use.
- The end-to-end query completes: intent resolution, schema indexing, translation, semantic validation, OKS execution, and interpretation all run. It finds 29 objects and returns a natural-language answer.
- The successful query took about 211 seconds: roughly 8 seconds intent, 11 seconds indexing, 146 seconds translation LLM call, 0.05 seconds execution, and 45 seconds interpretation LLM call. An MCP server must expose timeouts/status and should avoid unnecessary duplicate LLM calls where possible.
- The user's question included timeout conditions plus an OR condition for host/name. The generated query omitted the host/name condition, and the final answer explicitly admitted this. The MCP response returns the generated query and structured fields rather than hiding the limitation; semantic completeness remains a follow-up quality task.
- The team's proposed architecture is now clarified: MCP should be stateless, while the consuming agent/harness owns conversation history and follow-up resolution. The MCP tool should receive a complete question and return structured OKS results; server-side memory is deferred.

## Implementation design findings

- `OksPipeline.answer()` now accepts `interpret=False`; the MCP service uses it to return filtered structured objects without a second interpretation LLM call, while the existing CLI/API default remains unchanged.
- `Executor.execute()` already passes version selectors to subprocess environments, but its Python `config` backend temporarily mutates process-global environment variables. `OksQueryService` serializes query, translation, and probe calls around the shared pipeline so concurrent transports cannot cross-contaminate versioned requests.
- The MCP adapter returns a stable JSON-shaped dictionary and lets FastMCP serialize it. It rejects blank/oversized questions, invalid version selectors, and caller-selected backend paths. No conversation/session state or caller-supplied data/schema path is accepted.

## Implemented MCP surface

- `oks_query(question, version=None)`: translate, validate, execute, and return the generated OksQuery plus capped structured result objects.
- `oks_translate(question, version=None)`: translation/validation only; never executes OKS.
- `oks_environment_probe()`: non-secret readiness information for development diagnostics.
- Default transport: stdio. The external agent owns memory and must send a complete, self-contained question for every call.

## Local implementation verification

- `183 passed, 9 skipped` in the package test suite.
- Python compilation, shell syntax, and whitespace checks pass.
- An actual MCP client completed initialize/list-tools/tool-call over stdio.
- The local machine lacks the TDAQ `oks_dump`/`config` runtime; real query execution still requires the sourced LXPLUS release.
