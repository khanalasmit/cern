#!/usr/bin/env bash
set -euo pipefail

# Start the MCP HTTP server in a detached tmux session.  This is a convenient
# development/operations wrapper; use CERN's approved supervisor for a real
# production service.

PROJECT_ROOT="${OKS_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
TDAQ_SETUP_SCRIPT="${TDAQ_SETUP_SCRIPT:-/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh}"
MCP_SESSION="${MCP_SESSION:-oks-mcp}"
MCP_PORT="${MCP_PORT:-8001}"
MCP_HOST="${MCP_HOST:-127.0.0.1}"
OKS_DATA_FILE="${OKS_DATA_FILE:-daq/segments/setup.data.xml}"

if ! command -v tmux >/dev/null 2>&1; then
    echo "tmux is required; install/use the host-provided tmux first." >&2
    exit 1
fi
if [[ ! -f "$TDAQ_SETUP_SCRIPT" ]]; then
    echo "TDAQ setup script not found: $TDAQ_SETUP_SCRIPT" >&2
    exit 1
fi

quote_for_shell() {
    printf '%q' "$1"
}

project_q=$(quote_for_shell "$PROJECT_ROOT")
setup_q=$(quote_for_shell "$TDAQ_SETUP_SCRIPT")
data_q=$(quote_for_shell "$OKS_DATA_FILE")
host_q=$(quote_for_shell "$MCP_HOST")
port_q=$(quote_for_shell "$MCP_PORT")

tmux kill-session -t "$MCP_SESSION" 2>/dev/null || true
tmux new-session -d -s "$MCP_SESSION"
tmux send-keys -t "$MCP_SESSION:0" \
    "cd $project_q && source $setup_q && export OKS_REPO_ROOT=$project_q && export OKS_DATA_FILE=$data_q && export MCP_TRANSPORT=streamable-http && export MCP_HOST=$host_q && export MCP_PORT=$port_q && exec bash deploy/run_mcp.sh" C-m

sleep "${MCP_START_WAIT_SECONDS:-3}"
echo "MCP tmux session: $MCP_SESSION"
echo "Configured endpoint: http://$MCP_HOST:$MCP_PORT/mcp"
if ss -ltn 2>/dev/null | grep -q ":$MCP_PORT[[:space:]]"; then
    echo "Listening: yes"
else
    echo "Listening: not detected yet; inspect logs with:"
    echo "  tmux capture-pane -t $MCP_SESSION:0 -p | tail -40"
    exit 1
fi
