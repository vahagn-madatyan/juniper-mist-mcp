---
estimated_steps: 8
estimated_files: 2
---

# T01: Add device stats and SLE summary tools

**Slice:** S02 — Read tools (tier1)
**Milestone:** M001

## Description

Implement the first two tier1 read-only tools: `mist_get_device_stats` and `mist_get_sle_summary`. These are the core operational tools for monitoring device health and service levels.

## Steps

1. Import required mistapi functions at the top of server.py
2. Add helper function to serialize APIResponse to JSON-serializable dict
3. Implement `mist_get_device_stats` tool:
   - Accept `org` (required) and optional `duration` parameters
   - Validate org using existing validate_org function
   - Get session from session_manager
   - Call mistapi `listOrgDevicesStats` endpoint
   - Format and return response
4. Implement `mist_get_sle_summary` tool:
   - Accept `org` (required) and `site_id` (required) parameters
   - Validate org exists in config
   - Get session from session_manager
   - Call mistapi `getSiteSleSummary` endpoint
   - Format and return response
5. Run existing tests to ensure nothing breaks
6. Verify new tools are registered in MCP server

## Must-Haves

- [ ] mist_get_device_stats tool registered and functional
- [ ] mist_get_sle_summary tool registered and functional
- [ ] Both tools accept org parameter and validate org exists
- [ ] Both tools return JSON-serializable responses

## Verification

- `pytest tests/test_server.py -v` — all existing tests still pass
- `python3 -c "from mist_mcp.server import mcp; print([t.name for t in mcp._tool_manager._tools])"` — verify tools registered

## Observability Impact

- Signals added/changed: INFO logs when each tool is called with org parameter
- How a future agent inspects this: Server logs show tool invocations
- Failure state exposed: ValueError for invalid org, RuntimeError for API failures

## Inputs

- `mist_mcp/server.py` — existing tool registration pattern
- `mist_mcp/session.py` — MistSessionManager.get_session method

## Expected Output

- `mist_mcp/server.py` — two new @mcp.tool decorated functions added
- `tests/test_server.py` — optional: add basic registration tests
