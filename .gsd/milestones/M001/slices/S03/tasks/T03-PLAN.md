# T03: Implement mist_get_device_config_cmd tool

**Slice:** S03 — Config viewing tools (tier2)
**Milestone:** M001

## Description

Add device config command tool:
- `mist_get_device_config_cmd` — Get generated CLI configuration for a device using mistapi's devices.getSiteDeviceConfigCmd

This tool is different from org-level tools — it requires both site_id and device_id. The user must know the site and device to query.

## Steps

1. Import required mistapi function: `from mistapi.api.v1.sites import devices`
2. Add `mist_get_device_config_cmd` tool with parameters:
   - org (required) — organization name
   - site_id (required) — Mist site ID (not site name)
   - device_id (required) — Mist device ID
   - sort (optional) — sort order: "name", "type", "mac"
3. Follow S02 pattern:
   - Call validate_org(session_manager, org) to validate org exists
   - Get session: session = session_manager.get_session(org)
   - Get org_id: org_id = get_org_id(org, session) — needed to validate site belongs to org
   - Call devices.getSiteDeviceConfigCmd(session, site_id, device_id, sort=sort)
   - Return serialize_api_response(response)
   - Log INFO with tool name and parameters
4. Document in tool description that site_id and device_id are required and must be valid Mist IDs (not names)

## Must-Haves

- [ ] mist_get_device_config_cmd tool registered with required site_id and device_id
- [ ] Tool description clearly states site_id/device_id are IDs, not names
- [ ] Follows S02 pattern (validate_org → get_session → get_org_id → API call → serialize)
- [ ] Supports optional sort parameter

## Verification

- `python3 -m mist_mcp.server --help` shows mist_get_device_config_cmd with required parameters
- Tool description explains site_id/device_id requirement

## Inputs

- `mist_mcp/server.py` — S02 patterns for tool implementation
- S03 T01/T02 — Created patterns for other tier2 tools

## Expected Output

- `mist_mcp/server.py` — New mist_get_device_config_cmd @mcp.tool function

## Note

Unlike other tier2 tools that work at org level, this tool requires site context. Users typically get site_id from mist_get_site_events or by listing sites, and device_id from inventory search.
