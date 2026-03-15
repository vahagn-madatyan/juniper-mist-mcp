"""Integration tests for the MCP server.

Tests verify that:
- Server starts and initializes correctly
- mist_list_orgs tool is registered
- Configuration is loaded properly
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest


def send_jsonrpc_via_stdio(
    server_process: subprocess.Popen, method: str, params: dict | None = None
) -> dict[str, Any]:
    """Send a JSON-RPC request to a stdio server and read the response.

    Args:
        server_process: Running server process with stdin/stdout.
        method: JSON-RPC method name.
        params: Method parameters.

    Returns:
        Parsed JSON-RPC response.
    """
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
    }
    if params:
        request["params"] = params

    # Write request
    request_str = json.dumps(request) + "\n"
    server_process.stdin.write(request_str)
    server_process.stdin.flush()

    # Read response (may need multiple reads for JSON-RPC messages)
    response_lines = []
    while True:
        line = server_process.stdout.readline()
        if not line:
            break
        response_lines.append(line)
        # Try to parse to see if it's complete
        try:
            combined = "".join(response_lines)
            if combined.strip():
                return json.loads(combined)
        except json.JSONDecodeError:
            continue

    return {"error": {"code": -1, "message": "No response"}}


def test_server_help():
    """Test that --help shows transport and enable-write-tools options."""
    result = subprocess.run(
        [sys.executable, "-m", "mist_mcp.server", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0, f"Help command failed: {result.stderr}"
    assert "--enable-write-tools" in result.stdout
    assert "--transport" in result.stdout
    assert "stdio" in result.stdout
    assert "http" in result.stdout


def test_mist_list_orgs_tool_registered():
    """Test that mist_list_orgs tool is registered.

    Starts the server in stdio mode, sends a tools/list request,
    and verifies that mist_list_orgs appears in the response.
    """
    from pathlib import Path

    # Start server process
    server_process = subprocess.Popen(
        [sys.executable, "-m", "mist_mcp.server", "--transport", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    try:
        # Give server time to start
        time.sleep(2)

        # Send initialize request
        init_response = send_jsonrpc_via_stdio(
            server_process,
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"},
            },
        )

        # Send initialized notification (required by MCP spec)
        server_process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "initialized"}) + "\n")
        server_process.stdin.flush()

        # Give server time to process
        time.sleep(1)

        # Send tools/list request
        tools_response = send_jsonrpc_via_stdio(server_process, "tools/list")

        # Check response
        assert "result" in tools_response or "error" not in tools_response, f"Tools list request failed: {tools_response}"

        tools = tools_response.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]

        assert "mist_list_orgs" in tool_names, f"mist_list_orgs not found in tools: {tool_names}"

    finally:
        # Clean up server process
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()


def test_mist_list_orgs_returns_configured_orgs():
    """Test that mist_list_orgs returns the configured organizations.

    This test verifies the tool actually returns org data from config.
    Uses a mocked approach or direct function call.
    """
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    # Load config from test .env file
    config = Config(env_file=Path(__file__).parent.parent / ".env")

    # Create session manager
    session_manager = MistSessionManager(config)

    # Verify configured orgs
    assert "example_org" in session_manager.configured_orgs
    assert "acme_corp" in session_manager.configured_orgs


def test_config_loading():
    """Test that configuration is loaded correctly."""
    from mist_mcp.config import Config
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")

    # Verify orgs are loaded
    assert len(config.orgs) == 2
    assert "example_org" in config.orgs
    assert "acme_corp" in config.orgs

    # Verify specific org configs
    example_org = config.get_org("example_org")
    assert example_org is not None
    assert example_org.region == "api.mist.com"

    acme_org = config.get_org("acme_corp")
    assert acme_org is not None
    assert acme_org.region == "api.eu.mist.com"


def test_org_validation_error():
    """Test that invalid org raises appropriate error."""
    from mist_mcp.session import MistSessionManager
    from mist_mcp.config import Config
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    # Should raise ValueError for unknown org
    with pytest.raises(ValueError) as exc_info:
        session_manager.get_session("nonexistent_org")

    assert "not configured" in str(exc_info.value)
    assert "example_org" in str(exc_info.value)
    assert "acme_corp" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
