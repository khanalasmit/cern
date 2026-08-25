"""Stateless MCP server for the OKS query service.

Run locally with::

    python -m oksquery_translator.mcp_server

The default transport is stdio. The calling agent owns conversation memory
and must pass a complete question to ``oks_query``.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

def _configured_port() -> int:
    """Read and validate the HTTP port without changing stdio behavior."""
    raw_port = os.environ.get("MCP_PORT", "8000")
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise RuntimeError("MCP_PORT must be an integer between 1 and 65535") from exc
    if not 1 <= port <= 65535:
        raise RuntimeError("MCP_PORT must be an integer between 1 and 65535")
    return port


try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - requirements installs it
    load_dotenv = None

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - exercised by install checks
    raise RuntimeError(
        "The MCP SDK is not installed. Install oksquery_translator/requirements.txt."
    ) from exc

from .service import OksQueryService, ServiceInputError, service_from_environment

logger = logging.getLogger("oksquery_translator.mcp")
mcp = FastMCP(
    "oksquery-translator",
    host=os.environ.get("MCP_HOST", "127.0.0.1"),
    port=_configured_port(),
)
_service: Optional[OksQueryService] = None


def _load_environment() -> None:
    if load_dotenv is None:
        return
    package_dir = Path(__file__).resolve().parent
    repo_root = package_dir.parent
    for path in (
        repo_root / ".env",
        repo_root / "translator_module" / ".env",
        package_dir / ".env",
    ):
        if path.is_file():
            load_dotenv(path, override=False)


def get_service() -> OksQueryService:
    global _service
    if _service is None:
        _load_environment()
        _service = service_from_environment()
    return _service


@mcp.tool()
def oks_query(question: str, version: Optional[str] = None) -> Dict[str, Any]:
    """Translate and execute one complete natural-language OKS question.

    The question must be self-contained. Follow-up context belongs to the
    calling agent, not this stateless server. A successful result with
    result_count=0 means the query ran correctly but matched no objects; it is
    not a reason for the server to retry or broaden the query automatically.
    """
    try:
        return get_service().query(question, version=version)
    except ServiceInputError as exc:
        return {"status": "error", "message": str(exc), "warnings": []}
    except Exception as exc:  # Keep tool failures structured and observable.
        logger.exception("oks_query failed")
        return {
            "status": "error",
            "message": f"OKS query service failed: {exc}",
            "warnings": [],
        }


@mcp.tool()
def oks_translate(question: str, version: Optional[str] = None) -> Dict[str, Any]:
    """Translate a question without executing the resulting OKS query."""
    try:
        return get_service().translate(question, version=version)
    except ServiceInputError as exc:
        return {"status": "error", "message": str(exc), "warnings": []}
    except Exception as exc:
        logger.exception("oks_translate failed")
        return {"status": "error", "message": f"Translation failed: {exc}", "warnings": []}


@mcp.tool()
def oks_environment_probe() -> Dict[str, Any]:
    """Report TDAQ runtime readiness without exposing credentials."""
    try:
        return get_service().environment_probe()
    except Exception as exc:
        logger.exception("oks_environment_probe failed")
        return {"status": "error", "message": f"Environment probe failed: {exc}"}


def main() -> None:
    """Start the MCP server; stdio is the safe default transport."""
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport not in {"stdio", "streamable-http"}:
        raise ValueError(
            "MCP_TRANSPORT must be 'stdio' or 'streamable-http'"
        )
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
