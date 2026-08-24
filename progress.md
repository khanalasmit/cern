# MCP Deployment Planning Progress

## Current status

**MCP implementation is complete locally on `feature/mcp-server`.** The first
version is stateless; conversation memory remains in the external agent/harness.
The remaining work is device integration on LXPLUS with one pinned TDAQ
release and a Python 3.10+ virtual environment.

## Active session

- Read the existing plan, findings, and progress files before changing source; all three remain untracked and will not be staged.
- Confirmed the task targets the existing `Translator`/`Executor`/`OksPipeline` architecture and requires a service boundary rather than CLI reuse.
- Confirmed local MCP SDK availability (1.27.1) under the active Python 3.11.9 environment; actual TDAQ/LXPLUS runtime remains unverified.
- Added the service facade, MCP entry point, tests, launcher, and deployment docs.
- Renamed the internal `ast/` package to `oks_ast/` and updated all imports so
  tooling run inside the package cannot shadow Python's standard-library `ast`.
- Installed and tested MCP SDK 1.29.1 locally through the declared
  `mcp>=1.12,<2` requirement.
- Final local checks: **183 passed, 9 skipped**; compile, shell syntax, and
  `git diff --check` checks pass.
- A real MCP stdio client initialized the server, listed `oks_query`,
  `oks_translate`, and `oks_environment_probe`, and called the tools.

## Completed analysis

- Identified `oksquery_translator/` as the primary package for this work.
- Confirmed the existing flow: schema retrieval → few-shot prompt → LLM translation → validation/repair → OKS execution → result interpretation.
- Confirmed the CLI supports `translate`, `version`, and `probe`, but not MCP or conversation memory.
- Ran the package tests: **49 passed**.
- Ran the local CLI environment probe: the local machine does not have `oks_dump`, the Python `config` module, or a live schema; those must be verified on the SSH target.
- Checked official MCP transport guidance: use stdio for a local subprocess or Streamable HTTP for a deployed server; do not start a new implementation with legacy SSE.
- Confirmed SSH access to `cshah@lxplus9112.cern.ch` (RHEL 9.8); the alias `lxplus.cern.ch` resolved to `lxplus9112.cern.ch`.
- Confirmed on LXPLUS: Python 3.9.25 and TDAQ release 14.00.00 are available; the TDAQ setup script runs successfully.
- Reviewed the team's LXPLUS demo on the `rhythm` branch: the end-to-end pipeline completes, but the demo exposes interpreter-selection, local `ast` naming, mixed-release, and semantic-completeness issues that must be fixed before MCP integration.

## Main recommendation

Build an `OksQueryService` facade and a thin stateless MCP adapter on the user's latest `rhythm` branch. Start with one safe tool, `oks_query`, using fixed server-side data configuration. Use stdio if the agent can launch on the device; otherwise run Streamable HTTP on loopback and connect through an SSH tunnel. Let the external agent/harness manage memory and follow-ups.

## Blocking information needed from the team

- Exact TDAQ release and OKS data file.
- Exact commit SHA of the user's branch containing the latest `rhythm` code.
- Whether the target may run a long-lived process or expose a local forwarded port.
- Where the agent will run.
- Whether the MCP server should be single-user or shared.
- Whether outbound LLM API access is allowed from the device.

## Next action

Push/clone this branch on LXPLUS and run the real TDAQ integration checks:
verify one consistent release's `oks_dump`, Python `config`, schema, data file,
LLM connectivity, and one known query through the MCP client.
