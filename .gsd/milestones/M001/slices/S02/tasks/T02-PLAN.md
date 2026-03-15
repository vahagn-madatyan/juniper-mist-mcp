---
estimated_steps: 8
estimated_files: 2
---

# T02: Add client stats, alarms, and events tools

**Slice:** S02 — Read tools (tier1)
**Milestone:** M001

## Description

Implement the remaining three tier1 read-only tools: `mist_get_client_stats`, `mist_get_alarms`, and `mist_get_site_events`. These complete the tier1 toolset for troubleshooting client connectivity, alarms, and audit logs.

## Steps

1. Import required mistapi functions at the top of server.py
2. Implement `mist_get_client_stats` tool:
   - Accept `org` (required), `duration` (optional), `limit` (optional) parameters
   - Validate org using existing validate_org function
   - Get session from session_manager
   - Call mistapi `searchOrgWirelessClients` endpoint
   - Format and return response
3. Implement `mist_get_alarms` tool:
   - Accept `org` (required), `start`, `end`, `status` optional parameters
   - Validate org exists in config
   - Get session from session_manager
   - Call mistapi `searchOrgAlarms` endpoint
   - Format and return response
4. Implement `mist_get_site_events` tool:
   - Accept `org` (required), `site_id` (optional), `start`, `end` optional parameters
   - Validate org exists in config
   - Get session from session_manager
   - Call mistapi `searchOrgEvents` endpoint
   - Format and return response
5. Verify all 5 tools are registered in MCP server

## Must-Haves

- [ ] mist_get_client_stats tool registered and functional
- [ ] mist_get_alarms tool registered and functional
- [ ] mist_get_site_events tool registered and functional
- [ ] All tools accept org parameter and validate org exists
- [ ] All tools return JSON-serializable responses

## Verification

- `python3 -c "from mist_mcp.server import mcp; print(len(mcp._tool_manager._tools))"` — verify 6 tools total (1 from S01 + 5 new)
- `pytest tests/test_server.py -v` — all tests pass

## Observability Impact

- Signals added/changed: INFO logs when each tool is called with org parameter
- How a future agent inspects this: Server logs show tool invocations
- Failure state exposed: ValueError for invalid org, RuntimeError for API failures

## Inputs

- `mist_mcp/server.py` — existing tool registration pattern, first 2 tier1 tools from T01

## Expected Output

- `mist_mcp/server.py` — three new @mcp.tool decorated functions added
