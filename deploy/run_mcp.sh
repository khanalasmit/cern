#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${OKS_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
TDAQ_SETUP_SCRIPT="${TDAQ_SETUP_SCRIPT:-/cvmfs/atlas.cern.ch/repo/sw/tdaq/tdaq/tdaq-14-00-00/installed/setup.sh}"
if [[ -n "${OKS_QUERY_PYTHON:-}" ]]; then
    PYTHON_BIN="$OKS_QUERY_PYTHON"
elif [[ -x "$PROJECT_ROOT/oksquery_translator/venv/bin/python" ]]; then
    PYTHON_BIN="$PROJECT_ROOT/oksquery_translator/venv/bin/python"
else
    PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
fi

if [[ ! -f "$TDAQ_SETUP_SCRIPT" ]]; then
    echo "TDAQ setup script not found: $TDAQ_SETUP_SCRIPT" >&2
    exit 1
fi
if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Project Python interpreter not found or not executable: $PYTHON_BIN" >&2
    exit 1
fi

if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
    echo "The MCP server requires Python 3.10 or newer: $PYTHON_BIN" >&2
    echo "Create the virtualenv with a Python 3.10+ interpreter and set OKS_QUERY_PYTHON." >&2
    exit 1
fi

# Source exactly one release, then invoke the project interpreter explicitly.
# This prevents TDAQ's PATH changes from selecting the wrong openai package.
source "$TDAQ_SETUP_SCRIPT"
export OKS_REPO_ROOT="$PROJECT_ROOT"
exec "$PYTHON_BIN" -m oksquery_translator.mcp_server
