# MCP Deployment and Agent Integration Plan

## Goal

Analyze the current OKS query codebase and design a safe, staged plan to deploy it on the SSH-accessible device, expose it as an MCP server, and connect that server to an agent for natural-language OKS queries and follow-up questions.

## Phases

- [completed] Map the repository and identify the production translation/execution path.
- [completed] Verify the target device and SSH/runtime assumptions that can be verified locally; collect the remaining questions for the team.
- [completed] Define the MCP server boundary, tools, resources, memory, and security model.
- [completed] Define deployment, testing, observability, and rollback steps.
- [completed] Review the plan with the team before implementation.
- [completed] Implement the stateless service facade, MCP tools, runtime launcher, and tests on the latest `rhythm` base.
- [completed] Verify the implementation locally, including a real MCP stdio client handshake.
- [pending] Push/clone the branch on LXPLUS and run the real TDAQ integration checks.

## Recommended implementation sequence

### Phase 0 — Confirm the target device

Before writing the server, confirm:

- SSH host and username (the repository documents `lxplus.cern.ch`, but this is not proof of the actual target).
- OS/architecture, Python version, and whether a long-running process is permitted.
- TDAQ release and CVMFS availability; confirm `oks_dump` and Python `config` after sourcing setup.
- Fixed OKS data file(s), schema location, read permissions, and whether temporal version selection is required.
- Outbound access from the device to the chosen OpenAI-compatible LLM endpoint.
- Whether the agent runs on the device, on a laptop, or in another service; and whether the device may expose a port.

Device acceptance commands:

```bash
ssh <user>@<host>
uname -a
python3 --version
source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/<release>/installed/setup.sh
which oks_dump
python3 -c 'import config; print("config available")'
oks_dump -f daq/segments/setup.data.xml
```

### Phase 1 — Extract a service layer

Add a small service facade above the existing components instead of putting MCP decorators throughout the pipeline:

```text
MCP adapter → OksQueryService → Translator → Validator → Executor
                                      └────── optional Interpreter
```

The service owns fixed configuration (allowed data roots, release/data file, result cap, retry cap, timeouts) and returns structured results. The existing CLI and `OksPipeline` remain usable.

Important refactor before concurrent HTTP serving: `Executor` currently changes process-global `TDAQ_DB_VERSION`/`TDAQ_DB_PATH`. Either serialize versioned requests with a lock or refactor subprocess execution to receive a per-request environment. Do not allow version state to leak between users.

### Phase 2 — Implement the first MCP surface

Recommended tools:

1. `oks_query(question, version=None, conversation_id=None)` — main safe path; translate, validate, execute, and return answer metadata plus capped structured results.
2. `oks_translate(question, conversation_id=None)` — optional diagnostic tool; never executes a query.
3. `oks_environment_probe()` — admin/development only; reports runtime readiness without exposing secrets or arbitrary paths.

Do not expose arbitrary shell execution, arbitrary `data_file`, unrestricted class/file paths, or a raw unvalidated OksQuery execution tool in the first version.

The main MCP tool should return `answer`, `oks_query`, `target_class`, `result_count`, `results` (capped), `version_used`, and `attempts`. The agent can use this structured response to explain the result; avoid an unnecessary second LLM call by default in the MCP path, while retaining `Interpreter` for the CLI or an explicit `interpret=True` option.

### Phase 3 — Keep conversation memory outside MCP

- Do not implement a server-side memory database in the first MCP version.
- Let the host agent/harness (Codex, Claude Code, or another agent runtime) own conversation history, sessions, and follow-up context.
- The MCP tool should receive a complete, self-contained question. For a follow-up such as “make those less than 100,” the agent should resolve it using its own context before calling MCP.
- Return structured results and the generated query so the agent can explain, verify, or ask a follow-up.
- Add an optional `conversation_id` only as a request correlation field if the harness wants it; the MCP server should not depend on it for correctness.
- Consider server-side memory later only if a non-agent client needs persistence or the team explicitly wants shared conversation state.

### Phase 4 — Choose transport and deploy

- If the agent can launch a process on the same machine: start with MCP `stdio`.
- If the MCP process runs on the SSH device and the agent is elsewhere: run Streamable HTTP bound to `127.0.0.1` and connect through an SSH local port-forward. This avoids opening the device publicly.
- Only expose a network port directly after adding authentication, authorization, TLS/reverse proxy policy, rate limits, and an operational owner.

The official MCP Python SDK documents stdio for host-launched local processes and Streamable HTTP for deployed servers; legacy SSE is not the starting point for new work. See the official SDK run and ASGI documentation linked in `findings.md`.

### Phase 5 — Test and operate

- Unit tests for service validation, limits, memory isolation, version isolation, and error mapping.
- MCP contract tests using an MCP client/Inspector: initialize, list tools, call a valid query, invalid query, timeout, and no-runtime cases.
- Device integration test with sourced TDAQ release: `oks_dump`, `config`, one known query, one relationship query, and one version/snapshot query if required.
- End-to-end agent test: first question, follow-up question, new conversation, clear conversation.
- Structured logs: request ID, duration, target class, version label, validation attempts, result count, error category; never API keys or full sensitive prompts by default.
- Supervise the process with systemd or the team's approved process manager; keep the working tree/data read-only for the service account.
- Roll back by stopping the service and restoring the previous versioned checkout/configuration; keep deployments versioned rather than editing live files.

## Decision recommendation

Start with a single-user, stdio or SSH-tunnelled Streamable HTTP prototype on the target device. Keep `oksquery_translator` as the domain library, add a service facade and MCP adapter, use fixed read-only OKS configuration, and delay shared HTTP exposure until identity and concurrency are solved.

## Demo-driven prerequisites before MCP code

1. Confirm that the user's branch contains the latest `rhythm` code, and record its exact commit SHA before implementation.
2. Pin one TDAQ release for `setup.sh`, `config`, `oks_dump`, schema, and data.
3. Make the Python interpreter explicit; do not let TDAQ setup override the package venv unexpectedly.
4. Resolve the local `ast/` standard-library shadowing issue and correct the requirements filename/entry-point documentation.
5. Add semantic completeness checks so a generated query cannot silently drop user conditions; return warnings when a question cannot be expressed.
6. Measure and cap LLM latency; decide whether MCP returns structured results directly instead of making the second interpreter LLM call.

## Constraints and decisions to confirm

- SSH target and basic OS are now confirmed: `cshah@lxplus9112.cern.ch`, RHEL 9.8. Python version, TDAQ release, network access, and service policy remain to be verified.
- Python 3.9.25 is present; the repository documents Python 3.10+, so interpreter compatibility is now an explicit Phase 0 gate.
- The server must not expose unrestricted shell or arbitrary OKS file access.
- LLM translation, OKS execution, and answer interpretation should remain separate layers.
- Conversation memory is out of scope for the first MCP server; the external agent/harness owns it.

## Implementation decision

- Working branch: `feature/mcp-server`, based on `origin/rhythm` at the current latest local remote tip.
- MCP is stateless. It receives a complete question and returns structured OKS results; it does not persist conversation history.
- The first transport is stdio. Remote LXPLUS deployment will use the explicit project virtualenv interpreter after sourcing one consistent TDAQ release.

## Current implementation checkpoints

- Confirmed checkout branch is `feature/mcp-server`; verify the exact `HEAD`/`origin/rhythm` SHA with separate `git rev-parse` calls before reporting.
- The local active Python is 3.11.9 and already has MCP SDK 1.27.1, so focused MCP import tests can run locally.
- The service facade owns request validation, fixed data/schema paths, result/retry caps, structured errors, and serialized pipeline access; it calls `Translator` and `Executor` through a supplied pipeline seam in tests.
- Renamed `oksquery_translator/ast/` to `oksquery_translator/oks_ast/` so running tooling from inside the package cannot shadow the Python stdlib `ast` module. Public symbols remain exported through the package root.
- MCP mode calls `OksPipeline.answer(..., interpret=False)`, so the external agent receives filtered structured results without an unnecessary second interpretation LLM call.
- The launcher sources exactly one TDAQ release and invokes the project interpreter explicitly; it rejects Python versions below 3.10 with a clear message.

## Verification completed

- `venv/bin/python -m pytest -q oksquery_translator/tests`: **183 passed, 9 skipped**.
- `venv/bin/python -m compileall -q oksquery_translator`: passed.
- `bash -n deploy/run_mcp.sh`: passed.
- `git diff --check`: passed.
- Real MCP stdio client: initialize, list three tools, call invalid `oks_query`, and call `oks_environment_probe`: passed.

## Errors encountered

| Error | Attempt | Resolution |
|---|---:|---|
| Existing test fixture used an f-string escape unsupported by Python 3.9/3.11 | 1 | Rewrote the fixture expression without changing its JSON payload. |
| MCP SDK 2.0 removed `mcp.server.fastmcp` | 1 | Constrained the dependency to the compatible 1.x SDK (`mcp>=1.12,<2`) and verified 1.29.1. |
| Structured pipeline return referenced `version_label` before initialization | 1 | Initialized the label before the no-interpretation branch and added a regression test. |
| LXPLUS test `test_executor_rejects_invalid_historical_release` failed | 1 | Diagnosis: an invalid `release` falls through to the active current `oks_dump`/`config` backend and returns success; executor must reject it before execution to prevent silently querying current configuration. |
