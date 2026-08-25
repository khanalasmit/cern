# OKS MCP Server — Running and Agent Connection Guide

This is the handoff guide for the stateless OKS MCP server in the
feature/mcp-server branch. It covers the complete path:

~~~text
TDAQ/CVMFS data on LXPLUS
  → oksquery_translator
  → Streamable HTTP MCP server on LXPLUS loopback
  → SSH local tunnel
  → Claude Code or another MCP-compatible agent
~~~

The server translates a complete natural-language question into an OksQuery,
validates it, executes it against the configured OKS data, and returns the
generated query plus filtered structured results. It is read-only and
stateless. The consuming agent owns conversation history and must resolve a
follow-up question into a complete question before calling the server.

## 1. Included components

| Path | Purpose |
| --- | --- |
| oksquery_translator/mcp_server.py | MCP entry point and three tools |
| oksquery_translator/service.py | Safe service boundary and input limits |
| oksquery_translator/pipeline.py | Translation, validation, execution, and result assembly |
| oksquery_translator/executor.py | Python config execution with native oks_dump fallback |
| deploy/run_mcp.sh | Sources one TDAQ release and launches the server |
| deploy/start_mcp_tmux.sh | Starts the HTTP server in detached tmux |
| mcp_running_guide.md | This deployment and connection guide |

The branch contains the verified attribute-extraction fix in commit
be227f3. Always verify the current commit after pulling because the branch may
receive later changes.

## 2. Prerequisites

You need:

1. A CERN account with LXPLUS SSH and 2FA access.
2. CVMFS access to the ATLAS TDAQ release.
3. Python 3.10 or newer. The default LXPLUS python3 may be Python 3.9;
   use an available python3.13, python3.12, python3.11, or python3.10.
4. An OpenAI-compatible LLM endpoint and an API key for translation.
5. tmux for a detached development process, or a CERN-approved supervisor
   for a long-lived service.
6. An MCP-compatible client/agent. Claude Code is covered below.

The MCP server must not be made publicly reachable until authentication,
authorization, rate limits, logging policy, and a persistent service owner
have been approved. The safe default is an SSH tunnel to the loopback-bound
server.

## 3. Clone the correct branch on LXPLUS

Log in from your workstation:

~~~bash
ssh <cern_user>@<lxplus_host>
~~~

Create a workspace and clone the MCP branch:

~~~bash
mkdir -p ~/private/my_tdaq_project
cd ~/private/my_tdaq_project

git clone --branch feature/mcp-server \
  https://github.com/khanalasmit/cern.git cern
cd cern

git branch --show-current
git log -1 --oneline
git status --short
~~~

Expected branch:

~~~text
feature/mcp-server
~~~

For an existing checkout, update without overwriting local work:

~~~bash
cd ~/private/my_tdaq_project/cern
git switch feature/mcp-server
git pull --ff-only origin feature/mcp-server
git log -1 --oneline
~~~

If git pull refuses because the checkout has local changes, stop and inspect
git status. Do not use git reset --hard to solve this without preserving local
changes.

## 4. Source one consistent TDAQ release

Use a fresh shell when changing TDAQ releases. Do not mix a release's Python
bindings, oks_dump, schema, and data with another release.

~~~bash
cd ~/private/my_tdaq_project/cern

export TDAQ_RELEASE=tdaq-14-00-00
export TDAQ_SETUP_SCRIPT=/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/$TDAQ_RELEASE/installed/setup.sh
source "$TDAQ_SETUP_SCRIPT"

command -v oks_dump
oks_dump --help >/dev/null
~~~

The command should resolve inside the same tdaq-14-00-00/installed directory.
If it does not, open a fresh shell and source only the intended setup script.

## 5. Create the project Python environment

Find a Python version at least 3.10:

~~~bash
command -v python3.13 || true
command -v python3.12 || true
command -v python3.11 || true
command -v python3.10 || true
~~~

Choose one that exists. The following example uses Python 3.13:

~~~bash
export OKS_QUERY_PYTHON="$PWD/oksquery_translator/mcp-venv-313/bin/python"

if [[ ! -x "$OKS_QUERY_PYTHON" ]]; then
  python3.13 -m venv "$PWD/oksquery_translator/mcp-venv-313"
fi

"$OKS_QUERY_PYTHON" --version
"$OKS_QUERY_PYTHON" -m pip install -r oksquery_translator/requirements.txt
~~~

The MCP SDK requirement is intentionally constrained to mcp>=1.12,<2.
Always invoke the project interpreter explicitly; after TDAQ setup, python3
may point to a different CVMFS interpreter.

If the machine has Python 3.11 instead:

~~~bash
python3.11 -m venv oksquery_translator/mcp-venv-311
export OKS_QUERY_PYTHON="$PWD/oksquery_translator/mcp-venv-311/bin/python"
"$OKS_QUERY_PYTHON" -m pip install -r oksquery_translator/requirements.txt
~~~

## 6. Configure the LLM key safely

The server loads environment files from the repository root,
translator_module/.env, or oksquery_translator/.env. Use one location and keep
it out of Git.

~~~bash
cp .env.example translator_module/.env
chmod 600 translator_module/.env
~~~

Edit translator_module/.env with the team's approved provider values:

~~~dotenv
LLM_API_KEY=<secret>
LLM_BASE_URL=<OpenAI-compatible-base-URL>
LLM_MODEL=<model-name>
~~~

Never put an API key in a Git commit, shell command pasted into chat, MCP
request body, Cloudflare/ngrok command line, or an agent configuration that
does not need the key. If a secret is exposed in a transcript, revoke it and
issue a replacement.

## 7. Choose the OKS data file deliberately

OKS_DATA_FILE is read when the MCP service starts. Restart the service after
changing it.

### Broad DAQ release setup

Use this for the normal release configuration:

~~~bash
export OKS_DATA_FILE=daq/segments/setup.data.xml
~~~

This is a release snapshot, not live host discovery. It may not contain every
partition or every Computer object.

### Small deterministic Computer demo

Use this only to reproduce the first demo:

~~~bash
export OKS_DATA_FILE=/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq-14-00-00/installed/share/data/siom/hw/computers.data.xml
~~~

That fixture contains two configured records named localhost.localdomain and
localhost. Those names are expected; they are not generated by Claude and do
not describe the current LXPLUS host.

The MCP tool intentionally does not accept an arbitrary data-file path from an
agent. The server operator selects the approved data file at startup.

## 8. Verify the TDAQ runtime

Run these checks after sourcing the release and setting the data file:

~~~bash
export OKS_REPO_ROOT="$PWD"
export OKS_QUERY_PYTHON="$PWD/oksquery_translator/mcp-venv-313/bin/python"
export OKS_DATA_FILE=daq/segments/setup.data.xml

echo "python: $OKS_QUERY_PYTHON"
"$OKS_QUERY_PYTHON" --version
echo "oks_dump: $(command -v oks_dump)"

"$OKS_QUERY_PYTHON" -c 'import mcp; print("mcp available")'
"$OKS_QUERY_PYTHON" -c 'import config; print("config available")'

"$OKS_QUERY_PYTHON" - <<'PY'
from oksquery_translator.service import service_from_environment

probe = service_from_environment().environment_probe()
for key in (
    "status", "data_file", "oks_dump", "config_module",
    "oks_dump_status", "class_count",
):
    print(f"{key}: {probe.get(key)}")
PY
~~~

The probe should report status: success, config_module: available, an oks_dump
path, and a nonzero class_count. If oks_dump is not found, source the release
again. If Python is below 3.10, recreate the project environment with a newer
interpreter.

## 9. Run the MCP server on LXPLUS

For an agent on your workstation, use loopback Streamable HTTP and an SSH
tunnel:

~~~bash
export OKS_REPO_ROOT="$PWD"
export OKS_QUERY_PYTHON="$PWD/oksquery_translator/mcp-venv-313/bin/python"
export TDAQ_SETUP_SCRIPT=/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq-14-00-00/installed/setup.sh
export OKS_DATA_FILE=daq/segments/setup.data.xml
export MCP_TRANSPORT=streamable-http
export MCP_HOST=127.0.0.1
export MCP_PORT=8001
~~~

Start it in detached tmux:

~~~bash
bash deploy/start_mcp_tmux.sh
~~~

Expected output:

~~~text
MCP tmux session: oks-mcp
Configured endpoint: http://127.0.0.1:8001/mcp
Listening: yes
~~~

Inspect the server:

~~~bash
tmux ls
tmux capture-pane -t oks-mcp:0 -p | tail -50
ss -ltn | grep ':8001'
~~~

The listener must be on 127.0.0.1:8001 or another explicitly chosen port.
The server is not reachable from the public internet while bound to loopback.

Stop it during development with:

~~~bash
tmux kill-session -t oks-mcp
~~~

tmux is a convenient development holder, not a production supervisor. It
does not guarantee restart after host reboot, host replacement, or account
cleanup. Use CERN's approved service manager before calling this production.

## 10. Test the query path

This direct test proves that native OKS attributes are returned, not merely
object IDs:

~~~bash
"$OKS_QUERY_PYTHON" - <<'PY'
from oksquery_translator.executor import Executor

data_file = "/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/share/data/siom/hw/computers.data.xml"
result = Executor(data_file=data_file).execute(
    "Computer",
    '(all ("Memory" "500" >))',
)

print("success:", result.success)
print("count:", result.count)
for obj in result.objects:
    print(obj["id"], obj["attributes"])
PY
~~~

With the demo file, expected values are Memory=1024 for both objects. With
daq/segments/setup.data.xml, use classes actually present in that release
setup, such as BaseApplication, and do not assume the demo Computer records
exist.

For the full server path, the agent should call the MCP tool rather than
running the executor snippet. A successful tool call contains status,
oks_query, target_class, result_count, structured results, version_used, and
schema/context metadata.

### Diagnose a zero-result question without the LLM

When an agent reports zero results and starts trying speculative alternatives,
run the direct diagnostic on LXPLUS. It does not call an LLM, MCP, SSH tunnel,
or Claude; it tests the actual selected OKS data file with native oks_dump:

~~~bash
"$OKS_QUERY_PYTHON" deploy/diagnose_oks_query.py \
  --data-file "$OKS_DATA_FILE" \
  --object-id rc_trigger_1 \
  --attribute Name \
  --value rc_trigger_1
~~~

The diagnostic performs two checks for each candidate class:

~~~text
(all (object-id "rc_trigger_1" =))
(all ("Name" "rc_trigger_1" =))
~~~

Interpret the output as follows:

- `status: match` means the native OKS engine found the object.
- `valid_query_no_match` means the query executed correctly but this data
  file/version contains no matching object.
- `query_or_class_error` means the class or attribute is not valid for that
  live schema; inspect the printed stderr.
- If `Name` errors but `object-id` matches, the user named an object ID and
  the correct query is the object-id query, not the tutorial `Name` example.

To search every class discoverable through the Python config binding, add
`--all-classes`. This can take longer because it probes the selected release:

~~~bash
"$OKS_QUERY_PYTHON" deploy/diagnose_oks_query.py \
  --data-file "$OKS_DATA_FILE" \
  --object-id rc_trigger_1 \
  --all-classes
~~~

The MCP response marks a successful zero-result query explicitly as a valid
empty result. The external agent should not retry or broaden it unless the
user asks for a broader search.

## 11. Create the private SSH tunnel

Open a second terminal on your workstation. The LXPLUS server must already
be listening on port 8001:

~~~bash
ssh -N -L 18001:127.0.0.1:8001 <cern_user>@<lxplus_host>
~~~

Leave this terminal running. The agent endpoint on your workstation is:

~~~text
http://127.0.0.1:18001/mcp
~~~

Password and 2FA prompts are normal for CERN SSH. The tunnel does not remove
SSH authentication; it only forwards the already-authenticated connection.

The first host-key prompt is normal on the first connection. Verify the
fingerprint through CERN's trusted instructions before accepting a new key.

### Common tunnel errors

~~~text
channel ... open failed: connect failed: Connection refused
~~~

The tunnel process is alive, but nothing is listening remotely on
127.0.0.1:8001. On LXPLUS run:

~~~bash
ss -ltn | grep ':8001'
tmux capture-pane -t oks-mcp:0 -p | tail -50
~~~

Then start the server again with bash deploy/start_mcp_tmux.sh.

~~~text
HTTP 406 from a plain curl/browser request
~~~

That is not a reliable MCP failure test. Streamable HTTP expects MCP-specific
headers and session initialization. Test through an MCP client or the agent.

## 12. Connect Claude Code

Install the server in Claude Code using the workstation-side forwarded URL:

~~~bash
claude mcp add --transport http --scope user \
  oksquery http://127.0.0.1:18001/mcp
~~~

Verify the configuration:

~~~bash
claude mcp list
claude mcp get oksquery
~~~

Inside Claude Code, run:

~~~text
/mcp
~~~

The server should show as connected and expose:

~~~text
oks_query
oks_translate
oks_environment_probe
~~~

Then test with a complete question:

~~~text
Use the oksquery MCP server. Which BaseApplication objects have ExitTimeout equal to 37? Show the generated OKS query, exact result count, IDs, and matching attributes.
~~~

Do not begin with an incomplete follow-up such as "what about those less
than 30?" The server is stateless. Claude may resolve a follow-up from its
own conversation, but the actual MCP request must contain the complete meaning.

Claude Code supports HTTP/Streamable HTTP MCP servers and manages them with
claude mcp add, claude mcp list, claude mcp get, and /mcp. See the
[Claude Code MCP documentation](https://code.claude.com/docs/en/mcp) for
current client options.

### Team/project configuration

The user-scoped command above is best for a private SSH tunnel because each
user has a different CERN account and local tunnel. If a team deliberately
wants a project-scoped configuration, use:

~~~json
{
  "mcpServers": {
    "oksquery": {
      "type": "http",
      "url": "http://127.0.0.1:18001/mcp"
    }
  }
}
~~~

Only commit a project-scoped file if every team member understands that they
must run their own SSH forward on local port 18001. Never commit credentials
in this file.

## 13. Connect another MCP-compatible agent

Every MCP-compatible client needs these facts:

1. Transport: Streamable HTTP (often named http in client configuration).
2. Endpoint: http://127.0.0.1:18001/mcp when using the SSH tunnel.
3. Tools: oks_query, oks_translate, and oks_environment_probe.

Use the equivalent remote-server configuration in that agent:

~~~json
{
  "mcpServers": {
    "oksquery": {
      "type": "http",
      "url": "http://127.0.0.1:18001/mcp"
    }
  }
}
~~~

Some clients call the type streamable-http instead of http; follow that
client's configuration schema. Do not use legacy SSE for this server.

If the agent runs directly on LXPLUS, use stdio instead of a tunnel:

~~~json
{
  "mcpServers": {
    "oksquery": {
      "type": "stdio",
      "command": "/absolute/path/to/cern/oksquery_translator/mcp-venv-313/bin/python",
      "args": ["-m", "oksquery_translator.mcp_server"],
      "cwd": "/absolute/path/to/cern"
    }
  }
}
~~~

For stdio, the agent should inherit the sourced TDAQ environment or launch a
wrapper that sources TDAQ_SETUP_SCRIPT before invoking the interpreter.
deploy/run_mcp.sh is the preferred launcher when the client can run shell
commands.

## 14. Optional temporary Cloudflare Quick Tunnel

Use this only for short experiments when an SSH tunnel is not possible. It
does not require a purchased domain, but the URL is random and temporary, and
there is no production uptime guarantee:

~~~bash
cloudflared tunnel --url http://127.0.0.1:8001
~~~

Copy the printed https://<random>.trycloudflare.com URL and append /mcp in the
agent configuration. Keep the command running in a controlled session.

Important:

- A tunnel UUID is not a connector token.
- Never paste a Cloudflare token into chat or commit it.
- A named Cloudflare tunnel needs a connector token and normally a managed
  hostname/route for a stable URL.
- The current MCP server has no authentication. Do not expose it through a
  public Quick Tunnel, named tunnel, ngrok, or other public endpoint for
  shared use until an approved authentication layer is implemented.

For a stable external deployment, approve the hostname, identity/authentication
mechanism, access policy, rate limits, audit policy, and service supervisor
first. The agent then uses the stable HTTPS /mcp URL and required
authentication mechanism.

## 15. Production security checklist

The current branch is a working read-only prototype, not an anonymously public
production service. Before shared/public use:

- Add authentication and authorization at the HTTP boundary.
- Bind the service behind an approved reverse proxy or managed tunnel.
- Add a CERN-approved persistent supervisor and restart policy.
- Keep OKS data/schema selection server-side and allowlisted.
- Keep result caps and question/retry limits enabled.
- Add request IDs, duration, result count, target class, and error-category
  logs without logging API keys or unnecessary full prompts.
- Define who may query historical versions and which repositories/releases are
  allowed.
- Confirm whether the LLM endpoint may be called from LXPLUS and what data may
  be sent to it.
- Rotate credentials that appeared in a terminal transcript.

The MCP surface exposes no arbitrary shell tool, arbitrary filesystem path, or
write/mutation operation.

## 16. Update and rollback procedure

Update an existing LXPLUS checkout safely:

~~~bash
cd ~/private/my_tdaq_project/cern
git status --short
git pull --ff-only origin feature/mcp-server

source /cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh
export OKS_REPO_ROOT="$PWD"
export OKS_QUERY_PYTHON="$PWD/oksquery_translator/mcp-venv-313/bin/python"
export OKS_DATA_FILE=daq/segments/setup.data.xml
export MCP_TRANSPORT=streamable-http
export MCP_PORT=8001

"$OKS_QUERY_PYTHON" -m pytest -q oksquery_translator/tests
bash deploy/start_mcp_tmux.sh
~~~

If the new version fails, preserve logs and commit SHA first:

~~~bash
git log -2 --oneline
tmux capture-pane -t oks-mcp:0 -p | tail -100
~~~

Then stop the service and coordinate a rollback to the team's last known-good
commit or checkout. Do not delete the repository or use git reset --hard
without explicit approval and a backup of local work.

## 17. Final acceptance checklist

- [ ] git log -1 shows the intended feature/mcp-server revision.
- [ ] One consistent TDAQ release is sourced.
- [ ] The project interpreter is Python 3.10+ and dependencies are installed.
- [ ] config, mcp, and oks_dump checks pass.
- [ ] The LLM .env exists with mode 600 and is not tracked by Git.
- [ ] OKS_DATA_FILE is the intended approved data file.
- [ ] bash deploy/start_mcp_tmux.sh reports Listening: yes.
- [ ] A direct known query returns expected IDs and attribute values.
- [ ] The SSH tunnel connects without connection refused.
- [ ] The agent shows all three MCP tools in its MCP status screen.
- [ ] A natural-language query returns the generated OksQuery and result set.
- [ ] The agent is told that the MCP server is stateless and must resolve
      follow-ups into complete questions.

If public-access items are not approved, stop at the private SSH-tunnel
deployment. That is the intended safe development configuration.
