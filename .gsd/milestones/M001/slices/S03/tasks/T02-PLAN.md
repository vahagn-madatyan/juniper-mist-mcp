# T02: Implement mist_get_inventory tool

**Slice:** S03 — Config viewing tools (tier2)
**Milestone:** M001

## Description

Add inventory search tool with rich filtering capabilities:
- `mist_get_inventory` — Search/filter device inventory in an organization using mistapi's inventory.searchOrgInventory

This tool has more filter parameters than the org-level tools, making it slightly more complex.

## Steps

1. Import required mistapi function: `from mistapi.api.v1.orgs import inventory`
2. Add `mist_get_inventory` tool with parameters:
   - org (required) — organization name
   - type (optional) — device type: "ap", "gateway", "switch"
   - status (optional) — device status: "online", "offline", "provisioned"
   - site_id (optional) — filter by specific site
   - name (optional) — partial name match
   - limit (optional, default 100) — max results
   - offset (optional, default 0) — pagination offset
3. Follow S02 pattern:
   - Call validate_org(session_manager, org) to validate org exists
   - Get session: session = session_manager.get_session(org)
   - Get org_id: org_id = get_org_id(org, session)
   - Build filter dict with provided parameters (only include non-None values)
   - Call inventory.searchOrgInventory(session, org_id, **filters)
   - Return serialize_api_response(response)
   - Log INFO with tool name and parameters (exclude sensitive values)

## Must-Haves

- [ ] mist_get_inventory tool registered with filtering parameters
- [ ] Supports type filter: "ap", "gateway", "switch"
- [ ] Supports status filter: "online", "offline", "provisioned"
- [ ] Supports site_id filter for site-specific queries
- [ ] Supports name filter for partial name matching
- [ ] Follows S02 pattern (validate_org → get_session → get_org_id → API call → serialize)

## Verification

- `python3 -m mist_mcp.server --help` shows mist_get_inventory with all parameters
- Tool description documents supported filter values

## Inputs

- `mist_mcp/server.py` — S02 patterns for tool implementation
- S03 T01 — Created patterns for org-level tier2 tools

## Expected Output

- `mist_mcp/server.py` — New mist_get_inventory @mcp.tool function
