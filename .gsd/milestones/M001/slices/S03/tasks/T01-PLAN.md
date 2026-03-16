# T01: Implement mist_list_wlans and mist_get_rf_templates tools

**Slice:** S03 — Config viewing tools (tier2)
**Milestone:** M001

## Description

Add two new MCP tools following the established S02 pattern:
- `mist_list_wlans` — List all WLAN profiles in an organization using mistapi's wlans.listOrgWlans
- `mist_get_rf_templates` — List RF templates in an organization using mistapi's rftemplates.listOrgRfTemplates

Both work at org level with pagination support, similar to tier1 tools.

## Steps

1. Read the existing server.py to see S02 tool patterns (mist_get_device_stats, mist_get_client_stats)
2. Import required mistapi functions: `from mistapi.api.v1.orgs import wlans, rftemplates`
3. Add `mist_list_wlans` tool:
   - Accept org (required), limit (optional, default 100), page (optional, default 1)
   - Call validate_org(session_manager, org) to validate org exists
   - Get session: session = session_manager.get_session(org)
   - Get org_id: org_id = get_org_id(org, session)
   - Call wlans.listOrgWlans(session, org_id, limit=limit, page=page)
   - Return serialize_api_response(response)
   - Log INFO with tool name and parameters
4. Add `mist_get_rf_templates` tool:
   - Accept org (required), limit (optional, default 100), page (optional, default 1)
   - Same pattern as mist_list_wlans
   - Call rftemplates.listOrgRfTemplates(session, org_id, limit=limit, page=page)
   - Return serialize_api_response(response)
   - Log INFO with tool name and parameters

## Must-Haves

- [ ] mist_list_wlans tool registered with org, limit, page parameters
- [ ] mist_get_rf_templates tool registered with org, limit, page parameters
- [ ] Both tools follow S02 pattern (validate_org → get_session → get_org_id → API call → serialize)
- [ ] Both tools log INFO with tool name and parameters

## Verification

- `python3 -m mist_mcp.server --help` shows both tools
- `pytest tests/test_server.py -v -k "wlans or rf_templates"` — no import errors
- Tool descriptions mention pagination support

## Inputs

- `mist_mcp/server.py` — Existing S02 tools to follow as pattern
- `tests/test_server.py` — Existing test patterns for tool registration

## Expected Output

- `mist_mcp/server.py` — Two new @mcp.tool functions added
