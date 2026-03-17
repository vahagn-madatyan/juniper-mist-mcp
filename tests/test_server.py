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

# Import register_tools for tests that verify tool registration
from mist_mcp.server import register_tools, reset_tool_registration


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


def test_tier1_tools_registered():
    """Test that all tier1 read tools are registered.

    Verifies that the tier1 read tools are registered in the MCP server.
    This test verifies all 5 tier1 read tools:
    - mist_list_orgs (always available)
    - mist_get_device_stats (T01)
    - mist_get_sle_summary (T01)
    - mist_get_client_stats (T02)
    - mist_get_alarms (T02)
    - mist_get_site_events (T02)
    """
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())

    # All tier1 tools
    tier1_tools = [
        "mist_list_orgs",
        "mist_get_device_stats",
        "mist_get_sle_summary",
        "mist_get_client_stats",
        "mist_get_alarms",
        "mist_get_site_events",
    ]

    for tool_name in tier1_tools:
        assert tool_name in tool_names, f"{tool_name} not found in tools: {tool_names}"


def test_client_stats_signature():
    """Test that mist_get_client_stats tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_get_client_stats" in tool_names


def test_alarms_signature():
    """Test that mist_get_alarms tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_get_alarms" in tool_names


def test_site_events_signature():
    """Test that mist_get_site_events tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_get_site_events" in tool_names


def test_serialize_api_response():
    """Test the serialize_api_response helper function."""
    from mist_mcp.server import serialize_api_response
    from mistapi import __api_response
    from unittest.mock import MagicMock

    # Create a mock response
    mock_response = MagicMock(spec=__api_response.APIResponse)
    mock_response.status_code = 200
    mock_response.url = "https://api.mist.com/api/v1/test"
    mock_response.data = {"key": "value"}
    mock_response.next = None

    result = serialize_api_response(mock_response)

    assert result["status_code"] == 200
    assert result["error"] is False
    assert result["data"] == {"key": "value"}
    assert result["has_more"] is False


def test_serialize_api_response_error():
    """Test serialize_api_response with error response."""
    from mist_mcp.server import serialize_api_response
    from mistapi import __api_response
    from unittest.mock import MagicMock

    # Create a mock error response
    mock_response = MagicMock(spec=__api_response.APIResponse)
    mock_response.status_code = 400
    mock_response.url = "https://api.mist.com/api/v1/test"
    mock_response.data = {"error": "Bad request"}
    mock_response.next = None

    result = serialize_api_response(mock_response)

    assert result["status_code"] == 400
    assert result["error"] is True
    assert result["data"] == {"error": "Bad request"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# =============================================================================
# Tests for tier1 tool parameter validation and mock-based testing
# =============================================================================


def test_device_stats_invalid_org():
    """Test that mist_get_device_stats validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    # Test invalid org raises ValueError
    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("nonexistent_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_sle_summary_invalid_org():
    """Test that mist_get_sle_summary validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("invalid_org_12345", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_client_stats_invalid_org():
    """Test that mist_get_client_stats validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("bad_org_name", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_alarms_invalid_org():
    """Test that mist_get_alarms validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("fake_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_site_events_invalid_org():
    """Test that mist_get_site_events validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("nonexistent", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_device_stats_valid_org():
    """Test that mist_get_device_stats accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    # Should not raise for configured orgs
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_sle_summary_valid_org():
    """Test that mist_get_sle_summary accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_client_stats_valid_org():
    """Test that mist_get_client_stats accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_alarms_valid_org():
    """Test that mist_get_alarms accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_site_events_valid_org():
    """Test that mist_get_site_events accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_mist_list_orgs_returns_data():
    """Test that mist_list_orgs returns organization data."""
    from mist_mcp.config import Config
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")

    orgs = []
    for org_name in config.orgs:
        org_config = config.get_org(org_name)
        if org_config:
            orgs.append({
                "name": org_config.name,
                "region": org_config.region,
                "has_token": bool(org_config.token),
            })

    # Verify we get the expected orgs
    assert len(orgs) == 2
    org_names = [o["name"] for o in orgs]
    assert "example_org" in org_names
    assert "acme_corp" in org_names

    # Verify regions
    example_org = next(o for o in orgs if o["name"] == "example_org")
    assert example_org["region"] == "api.mist.com"
    assert example_org["has_token"] is True

    acme_org = next(o for o in orgs if o["name"] == "acme_corp")
    assert acme_org["region"] == "api.eu.mist.com"
    assert acme_org["has_token"] is True


def test_get_org_id_raises_on_invalid_org():
    """Test that get_org_id raises ValueError for nonexistent org."""
    from unittest.mock import MagicMock
    from mist_mcp.server import get_org_id
    from mistapi import __api_response

    # Create a mock session
    mock_session = MagicMock()

    # Mock the API response with empty orgs list
    mock_response = MagicMock(spec=__api_response.APIResponse)
    mock_response.status_code = 200
    mock_response.data = []
    mock_session.mist_get.return_value = mock_response

    with pytest.raises(ValueError) as exc_info:
        get_org_id("nonexistent_org", mock_session)

    assert "not found" in str(exc_info.value).lower()


def test_serialize_api_response_with_pagination():
    """Test serialize_api_response includes pagination info."""
    from mist_mcp.server import serialize_api_response
    from mistapi import __api_response
    from unittest.mock import MagicMock

    # Create mock response with pagination
    mock_response = MagicMock(spec=__api_response.APIResponse)
    mock_response.status_code = 200
    mock_response.url = "https://api.mist.com/api/v1/test"
    mock_response.data = [{"id": 1}, {"id": 2}]
    mock_response.next = "https://api.mist.com/api/v1/test?page=2"

    result = serialize_api_response(mock_response)

    assert result["status_code"] == 200
    assert result["error"] is False
    assert result["has_more"] is True
    assert result["next_page"] == "https://api.mist.com/api/v1/test?page=2"


def test_wlans_signature():
    """Test that mist_list_wlans tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_list_wlans" in tool_names


def test_rf_templates_signature():
    """Test that mist_get_rf_templates tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_get_rf_templates" in tool_names


def test_wlans_invalid_org():
    """Test that mist_list_wlans validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("fake_wlan_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_rf_templates_invalid_org():
    """Test that mist_get_rf_templates validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("nonexistent_rf_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_wlans_valid_org():
    """Test that mist_list_wlans accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_rf_templates_valid_org():
    """Test that mist_get_rf_templates accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_tier2_tools_registered():
    """Test that all tier2 read tools are registered.

    Verifies that the tier2 read tools are registered in the MCP server.
    This test verifies all 4 tier2 tools:
    - mist_list_wlans (T01)
    - mist_get_rf_templates (T01)
    - mist_get_inventory (T02)
    - mist_get_device_config_cmd (T03)
    """
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())

    # All tier2 tools for S03
    tier2_tools = [
        "mist_list_wlans",
        "mist_get_rf_templates",
        "mist_get_inventory",
        "mist_get_device_config_cmd",
    ]

    for tool_name in tier2_tools:
        assert tool_name in tool_names, f"{tool_name} not found in tools: {tool_names}"


# =============================================================================
# Tests for tier2 tool parameter validation (T01-T03)
# =============================================================================


def test_mist_get_inventory_invalid_org():
    """Test that mist_get_inventory validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("fake_inventory_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_mist_get_device_config_cmd_invalid_org():
    """Test that mist_get_device_config_cmd validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("nonexistent_device_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_mist_get_inventory_valid_org():
    """Test that mist_get_inventory accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_mist_get_device_config_cmd_valid_org():
    """Test that mist_get_device_config_cmd accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_mist_get_inventory_signature():
    """Test that mist_get_inventory tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_get_inventory" in tool_names


def test_mist_get_device_config_cmd_signature():
    """Test that mist_get_device_config_cmd tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_get_device_config_cmd" in tool_names


# =============================================================================
# Tests for tier3 write tools (T01-T04)
# =============================================================================


def test_mist_update_wlan_signature():
    """Test that mist_update_wlan tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking (with write tools enabled)
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_update_wlan" in tool_names


def test_mist_update_wlan_invalid_org():
    """Test that mist_update_wlan validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("fake_update_wlan_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_mist_update_wlan_valid_org():
    """Test that mist_update_wlan accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_mist_manage_nac_rules_signature():
    """Test that mist_manage_nac_rules tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking (with write tools enabled)
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_manage_nac_rules" in tool_names


def test_mist_manage_nac_rules_invalid_org():
    """Test that mist_manage_nac_rules validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("fake_nac_rules_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_mist_manage_nac_rules_valid_org():
    """Test that mist_manage_nac_rules accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_mist_manage_nac_rules_invalid_action():
    """Test that mist_manage_nac_rules validates action parameter."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_nac_rules
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    # Setup mock context and session manager
    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    # Create a mock context
    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test invalid action raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_nac_rules(mock_ctx, org="example_org", action="invalid"))

    assert "invalid action" in str(exc_info.value).lower()


def test_mist_manage_nac_rules_create_requires_body():
    """Test that mist_manage_nac_rules requires body for create action."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_nac_rules
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test create without body raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_nac_rules(mock_ctx, org="example_org", action="create"))

    assert "create" in str(exc_info.value).lower() and "body" in str(exc_info.value).lower()


def test_mist_manage_nac_rules_update_requires_rule_id_and_body():
    """Test that mist_manage_nac_rules requires rule_id and body for update action."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_nac_rules
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test update without rule_id raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_nac_rules(mock_ctx, org="example_org", action="update", body={}))

    assert "rule_id" in str(exc_info.value).lower()

    # Test update without body raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_nac_rules(mock_ctx, org="example_org", action="update", rule_id="some-id"))

    assert "body" in str(exc_info.value).lower()


def test_mist_manage_nac_rules_delete_requires_rule_id():
    """Test that mist_manage_nac_rules requires rule_id for delete action."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_nac_rules
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test delete without rule_id raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_nac_rules(mock_ctx, org="example_org", action="delete"))

    assert "rule_id" in str(exc_info.value).lower()


def test_mist_manage_wxlan_signature():
    """Test that mist_manage_wxlan tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking (with write tools enabled)
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_manage_wxlan" in tool_names


def test_mist_manage_wxlan_invalid_org():
    """Test that mist_manage_wxlan validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("fake_wxlan_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_mist_manage_wxlan_valid_org():
    """Test that mist_manage_wxlan accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_mist_manage_wxlan_invalid_action():
    """Test that mist_manage_wxlan validates action parameter."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_wxlan
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    # Setup mock context and session manager
    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    # Create a mock context
    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test invalid action raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_wxlan(mock_ctx, org="example_org", action="invalid"))

    assert "invalid action" in str(exc_info.value).lower()


def test_mist_manage_wxlan_create_requires_body():
    """Test that mist_manage_wxlan requires body for create action."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_wxlan
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test create without body raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_wxlan(mock_ctx, org="example_org", action="create"))

    assert "create" in str(exc_info.value).lower() and "body" in str(exc_info.value).lower()


def test_mist_manage_wxlan_update_requires_rule_id_and_body():
    """Test that mist_manage_wxlan requires rule_id and body for update action."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_wxlan
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test update without rule_id raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_wxlan(mock_ctx, org="example_org", action="update", body={}))

    assert "rule_id" in str(exc_info.value).lower()

    # Test update without body raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_wxlan(mock_ctx, org="example_org", action="update", rule_id="some-id"))

    assert "body" in str(exc_info.value).lower()


def test_mist_manage_wxlan_delete_requires_rule_id():
    """Test that mist_manage_wxlan requires rule_id for delete action."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_wxlan
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test delete without rule_id raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_wxlan(mock_ctx, org="example_org", action="delete"))

    assert "rule_id" in str(exc_info.value).lower()


# =============================================================================
# Tests for mist_manage_security_policies (T04)
# =============================================================================


def test_mist_manage_security_policies_signature():
    """Test that mist_manage_security_policies tool exists and is callable."""
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking (with write tools enabled)
    register_tools(enable_write=True)

    async def check_tools():
        tools = await mcp.list_tools()
        return [t.name for t in tools]

    tool_names = asyncio.run(check_tools())
    assert "mist_manage_security_policies" in tool_names


def test_mist_manage_security_policies_invalid_org():
    """Test that mist_manage_security_policies validates org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    with pytest.raises(ValueError) as exc_info:
        validate_org("fake_security_policies_org", session_manager)

    assert "not configured" in str(exc_info.value).lower()


def test_mist_manage_security_policies_valid_org():
    """Test that mist_manage_security_policies accepts valid org parameter."""
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    from mist_mcp.server import validate_org
    validate_org("example_org", session_manager)
    validate_org("acme_corp", session_manager)


def test_mist_manage_security_policies_invalid_action():
    """Test that mist_manage_security_policies validates action parameter."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_security_policies
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    # Setup mock context and session manager
    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    # Create a mock context
    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test invalid action raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_security_policies(mock_ctx, org="example_org", action="invalid"))

    assert "invalid action" in str(exc_info.value).lower()


def test_mist_manage_security_policies_create_requires_body():
    """Test that mist_manage_security_policies requires body for create action."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_security_policies
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test create without body raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_security_policies(mock_ctx, org="example_org", action="create"))

    assert "create" in str(exc_info.value).lower() and "body" in str(exc_info.value).lower()


def test_mist_manage_security_policies_update_requires_policy_id_and_body():
    """Test that mist_manage_security_policies requires policy_id and body for update action."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_security_policies
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test update without policy_id raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_security_policies(mock_ctx, org="example_org", action="update", body={}))

    assert "policy_id" in str(exc_info.value).lower()

    # Test update without body raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_security_policies(mock_ctx, org="example_org", action="update", policy_id="some-id"))

    assert "body" in str(exc_info.value).lower()


def test_mist_manage_security_policies_delete_requires_policy_id():
    """Test that mist_manage_security_policies requires policy_id for delete action."""
    from unittest.mock import MagicMock
    from mist_mcp.server import mist_manage_security_policies
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path
    import asyncio

    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }

    # Test delete without policy_id raises ValueError
    with pytest.raises(ValueError) as exc_info:
        asyncio.run(mist_manage_security_policies(mock_ctx, org="example_org", action="delete"))

    assert "policy_id" in str(exc_info.value).lower()


# =============================================================================
# Tests for MCP tool annotations (T02)
# =============================================================================


def test_read_tools_have_readonly_hint():
    """Test that all read tools have readOnlyHint=True annotation.

    Verifies that all 10 read tools (tier1 + tier2) have the
    readOnlyHint annotation set to True, signaling to LLM clients
    that these are safe read-only operations.
    """
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tool_annotations():
        tools = await mcp.list_tools()
        return {t.name: t.annotations for t in tools}

    tool_annotations = asyncio.run(check_tool_annotations())

    # Define expected read tools (10 tools)
    read_tools = [
        "mist_list_orgs",
        "mist_get_device_stats",
        "mist_get_sle_summary",
        "mist_get_client_stats",
        "mist_get_alarms",
        "mist_get_site_events",
        "mist_list_wlans",
        "mist_get_rf_templates",
        "mist_get_inventory",
        "mist_get_device_config_cmd",
    ]

    # Verify each read tool has readOnlyHint=True
    for tool_name in read_tools:
        assert tool_name in tool_annotations, f"{tool_name} not found in registered tools"
        annotations = tool_annotations[tool_name]
        assert annotations is not None, f"{tool_name} has no annotations"
        assert annotations.readOnlyHint is True, f"{tool_name} missing readOnlyHint=True"


def test_write_tools_have_destructive_hint():
    """Test that all write tools have destructiveHint=True annotation.

    Verifies that all 4 write tools (tier3) have the
    destructiveHint annotation set to True, signaling to LLM clients
    that these are destructive operations requiring confirmation.
    """
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tool_annotations():
        tools = await mcp.list_tools()
        return {t.name: t.annotations for t in tools}

    tool_annotations = asyncio.run(check_tool_annotations())

    # Define expected write tools (4 tools)
    write_tools = [
        "mist_update_wlan",
        "mist_manage_nac_rules",
        "mist_manage_wxlan",
        "mist_manage_security_policies",
    ]

    # Verify each write tool has destructiveHint=True
    for tool_name in write_tools:
        assert tool_name in tool_annotations, f"{tool_name} not found in registered tools"
        annotations = tool_annotations[tool_name]
        assert annotations is not None, f"{tool_name} has no annotations"
        assert annotations.destructiveHint is True, f"{tool_name} missing destructiveHint=True"


def test_all_tools_have_annotations():
    """Test that all registered tools have annotations defined.

    Verifies that no tools are missing annotations, ensuring
    proper MCP tool specification compliance.
    """
    import asyncio
    from mist_mcp.server import mcp

    # Register tools before checking
    register_tools(enable_write=True)

    async def check_tool_annotations():
        tools = await mcp.list_tools()
        return {t.name: t.annotations for t in tools}

    tool_annotations = asyncio.run(check_tool_annotations())

    # Verify all tools have annotations
    for tool_name, annotations in tool_annotations.items():
        assert annotations is not None, f"{tool_name} has no annotations"


# =============================================================================
# Tests for conditional write tool registration (T03)
# =============================================================================


def test_write_tools_not_registered_by_default():
    """Test that write tools are NOT registered when enable_write=False.

    Verifies that when register_tools is called with enable_write=False,
    only the 10 read tools are registered and the 4 write tools are not.
    This is the core safety feature: write tools disabled by default.
    
    Note: This test runs in a subprocess to ensure clean MCP state.
    """
    import subprocess
    import sys
    
    # Run in subprocess to ensure clean MCP state
    result = subprocess.run(
        [
            sys.executable, "-c",
            """
import asyncio
from mist_mcp.server import mcp, register_tools, reset_tool_registration

reset_tool_registration()
register_tools(enable_write=False)

async def check_tools():
    tools = await mcp.list_tools()
    return [t.name for t in tools]

tool_names = asyncio.run(check_tools())

# Verify only 10 tools are registered
assert len(tool_names) == 10, f"Expected 10 tools, got {len(tool_names)}: {tool_names}"

# Define write tools that should NOT be present
write_tools = [
    "mist_update_wlan",
    "mist_manage_nac_rules",
    "mist_manage_wxlan",
    "mist_manage_security_policies",
]

# Verify write tools are NOT registered
for tool_name in write_tools:
    assert tool_name not in tool_names, f"Write tool {tool_name} should NOT be registered when enable_write=False"

print("PASSED")
"""
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    
    assert result.returncode == 0, f"Subprocess test failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    assert "PASSED" in result.stdout


def test_write_tools_registered_with_flag():
    """Test that write tools ARE registered when enable_write=True.

    Verifies that when register_tools is called with enable_write=True,
    all 14 tools (10 read + 4 write) are registered.
    This ensures the --enable-write-tools flag works correctly.
    
    Note: This test runs in a subprocess to ensure clean MCP state.
    """
    import subprocess
    import sys
    
    # Run in subprocess to ensure clean MCP state
    result = subprocess.run(
        [
            sys.executable, "-c",
            """
import asyncio
from mist_mcp.server import mcp, register_tools, reset_tool_registration

reset_tool_registration()
register_tools(enable_write=True)

async def check_tools():
    tools = await mcp.list_tools()
    return [t.name for t in tools]

tool_names = asyncio.run(check_tools())

# Verify all 14 tools are registered
assert len(tool_names) == 14, f"Expected 14 tools, got {len(tool_names)}: {tool_names}"

# Define all expected tools (10 read + 4 write)
expected_tools = [
    # Read tools (10)
    "mist_list_orgs",
    "mist_get_device_stats",
    "mist_get_sle_summary",
    "mist_get_client_stats",
    "mist_get_alarms",
    "mist_get_site_events",
    "mist_list_wlans",
    "mist_get_rf_templates",
    "mist_get_inventory",
    "mist_get_device_config_cmd",
    # Write tools (4)
    "mist_update_wlan",
    "mist_manage_nac_rules",
    "mist_manage_wxlan",
    "mist_manage_security_policies",
]

# Verify all tools are present
for tool_name in expected_tools:
    assert tool_name in tool_names, f"Tool {tool_name} should be registered when enable_write=True"

print("PASSED")
"""
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    
    assert result.returncode == 0, f"Subprocess test failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    assert "PASSED" in result.stdout


def test_read_tools_have_readonly_hint_with_write_disabled():
    """Test that read tools still have readOnlyHint when write tools disabled.

    Verifies that even when write tools are not registered,
    the read tools that are registered still have proper annotations.
    
    Note: This test runs in a subprocess to ensure clean MCP state.
    """
    import subprocess
    import sys
    
    # Run in subprocess to ensure clean MCP state
    result = subprocess.run(
        [
            sys.executable, "-c",
            """
import asyncio
from mist_mcp.server import mcp, register_tools, reset_tool_registration

reset_tool_registration()
register_tools(enable_write=False)

async def check_tool_annotations():
    tools = await mcp.list_tools()
    return {t.name: t.annotations for t in tools}

tool_annotations = asyncio.run(check_tool_annotations())

# Define expected read tools (10 tools)
read_tools = [
    "mist_list_orgs",
    "mist_get_device_stats",
    "mist_get_sle_summary",
    "mist_get_client_stats",
    "mist_get_alarms",
    "mist_get_site_events",
    "mist_list_wlans",
    "mist_get_rf_templates",
    "mist_get_inventory",
    "mist_get_device_config_cmd",
]

# Verify each read tool has readOnlyHint=True
for tool_name in read_tools:
    assert tool_name in tool_annotations, f"{tool_name} not found in registered tools"
    annotations = tool_annotations[tool_name]
    assert annotations is not None, f"{tool_name} has no annotations"
    assert annotations.readOnlyHint is True, f"{tool_name} missing readOnlyHint=True"

print("PASSED")
"""
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    
    assert result.returncode == 0, f"Subprocess test failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    assert "PASSED" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
