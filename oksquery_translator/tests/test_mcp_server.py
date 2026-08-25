import asyncio
import importlib.util

import pytest


mcp_available = importlib.util.find_spec("mcp") is not None
pytestmark = pytest.mark.skipif(not mcp_available, reason="MCP SDK not installed")


def test_mcp_server_registers_expected_tools():
    from oksquery_translator import mcp_server

    assert callable(mcp_server.oks_query)
    assert callable(mcp_server.oks_translate)
    assert callable(mcp_server.oks_environment_probe)
    assert mcp_server.mcp.name == "oksquery-translator"

    tools = asyncio.run(mcp_server.mcp.list_tools())
    assert sorted(tool.name for tool in tools) == [
        "oks_environment_probe",
        "oks_query",
        "oks_translate",
    ]
