---
id: T03
parent: S03
milestone: M001
provides:
  - mist_get_device_config_cmd MCP tool
key_files:
  - mist_mcp/server.py
key_decisions:
  - Using devices.getSiteDeviceConfigCmd from mistapi.api.v1.sites.devices
  - Following established S02 pattern: validate_org → get_session → get_org_id → API call → serialize
patterns_established:
  - Site-level device config command tool with required site_id and device_id parameters
observability_surfaces:
  - INFO logs output on each tool call with org, site_id, device_id, and sort parameters
  - Serialized response includes error flag and status_code
  - Error responses include error: true flag and status_code
duration: 15 minutes
verification_result: passed
completed_at: 2026-03-15
blocker_discovered: false
---

# T03: Implement mist_get_device_config_cmd tool

**Added mist_get_device_config_cmd MCP tool for retrieving generated CLI configuration for a specific device.**

## What Happened

Implemented the device config command tool following the established S02 pattern:
- Added new `@mcp.tool` async function with required parameters (org, site_id, device_id) and optional sort parameter
- Imported `devices` from `mistapi.api.v1.sites` 
- Used `devices.getSiteDeviceConfigCmd(session, site_id, device_id, sort=sort)` API
- Added comprehensive docstring explaining that site_id and device_id are Mist IDs (UUIDs), not names
- Followed existing error handling and response serialization pattern

## Verification

All verification checks passed:
- `pytest tests/test_server.py -v` — 31 tests passed
- Tool registered in MCP server — confirmed 10 total tools (1 base + 5 tier1 + 4 tier2)
- `mist_get_device_config_cmd` appears in tool list with correct description

## Diagnostics

- Runtime signals: INFO logs when tool is called with org, site_id, device_id, and sort parameters
- Error responses include `error: true` flag and status_code
- Serialized response follows same pattern as other tier2 tools

## Deviations

None — followed the task plan exactly.

## Known Issues

None.

## Files Modified

- `mist_mcp/server.py` — Added `mist_get_device_config_cmd` tool (55 lines added)
