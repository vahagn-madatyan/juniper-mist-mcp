---
estimated_steps: 6
estimated_files: 2
---

# T01: WLAN update tool

**Slice:** S04 — Write tools (tier3)
**Milestone:** M001

## Description

Implement the `mist_update_wlan` tool for updating existing WLAN configurations. This is the simplest write operation (single update method) and establishes the pattern for tier3 write tools. The tool follows the same pattern as tier1/tier2 tools: validate org, get authenticated session, get org_id, call Mist API via SDK, serialize response.

## Steps

1. Open `mist_mcp/server.py` and locate the tier2 tools section (after `mist_get_device_config_cmd`).
2. Add new `@mcp.tool` function `mist_update_wlan` with parameters `org`, `wlan_id`, `body`. Include comprehensive docstring describing the tool's purpose and parameters.
3. Implement the tool: validate org via `validate_org`, get session via `session_manager.get_session(org)`, get org_id via `get_org_id(org, session)`.
4. Import `mistapi.api.v1.orgs.wlans` module and call `updateOrgWlan(session, org_id, wlan_id, body)`.
5. Return `serialize_api_response(response)`.
6. Add tests to `tests/test_server.py`: tool signature test, org validation test, and mock API call test (optional). Use existing test patterns (e.g., `test_mist_update_wlan_signature`, `test_mist_update_wlan_invalid_org`).

## Must-Haves

- [ ] `mist_update_wlan` tool registered in MCP server (appears in tool list)
- [ ] Tool accepts `org`, `wlan_id`, `body` parameters and calls `updateOrgWlan`
- [ ] Tool validates org configuration (raises ValueError for unknown org)
- [ ] Tool returns serialized API response with status_code, error flag, data
- [ ] Tests pass: `pytest tests/test_server.py::test_mist_update_wlan_signature -v`

## Verification

- Run `python3 -c "import asyncio; from mist_mcp.server import mcp; print([t.name for t in asyncio.run(mcp.list_tools())])"` and verify `mist_update_wlan` appears.
- Run `pytest tests/test_server.py -k mist_update_wlan -v` — all tests pass.
- Check tool signature: tool should have three required parameters (org, wlan_id, body).

## Observability Impact

- Tool logs invocation with parameters via `logger.info`.
- Errors from Mist API are captured in serialized response with `error: true`.

## Inputs

- `mist_mcp/server.py` — existing tool pattern, `validate_org`, `get_org_id`, `serialize_api_response` helpers.
- `tests/test_server.py` — existing test patterns for tool registration and org validation.
- S03 forward intelligence: tier2 tools provide read-before-write pattern.

## Expected Output

- Modified `mist_mcp/server.py` with new `mist_update_wlan` tool.
- Modified `tests/test_server.py` with new tests for the tool.
- Total tool count increased from 10 to 11.