# S03: Config viewing tools (tier2)

**Goal:** Implement tier2 read-only configuration viewing tools for WLANs, inventory, RF templates, and device CLI config
**Demo:** Agent can query WLAN configurations, device inventory with filtering, RF templates, and generated device CLI configurations for any customer organization

## Must-Haves

- mist_list_wlans tool: List all WLAN profiles in an organization with pagination support
- mist_get_inventory tool: Search/filter device inventory by type, status, site
- mist_get_rf_templates tool: List RF templates in an organization with pagination
- mist_get_device_config_cmd tool: Get generated CLI configuration for a device (requires site_id + device_id)
- All tools integrate with existing S02 patterns (serialize_api_response, validate_org, get_org_id)
- Tests verify tool registration, org validation, and response serialization

## Proof Level

- This slice proves: contract + integration
- Real runtime required: yes (need live Mist API for full verification)
- Human/UAT required: no (tests cover contract verification)

## Verification

- `pytest tests/test_server.py -v` — all tier1 + tier2 tools registered
- `bash scripts/verify_s03.sh` — end-to-end verification
- `python3 -m mist_mcp.server --help` — shows all 10 tools (1 base + 5 tier1 + 4 tier2)

## Observability / Diagnostics

- Runtime signals: INFO logs when each tool is called with org parameter
- Inspection surfaces: python3 -m mist_mcp.server --help
- Failure visibility: ValueError for invalid orgs, RuntimeError for API failures, serialize_api_response errors
- Redaction constraints: None (all data from Mist API is non-sensitive org data)

## Integration Closure

- Upstream surfaces consumed: serialize_api_response helper, get_org_id helper, validate_org function, MistSessionManager
- New wiring introduced in this slice: 4 new MCP tools registered in server.py
- What remains before the milestone is truly usable end-to-end: S04 write tools, S05 safety layers, S06 testing/documentation

## Tasks

- [x] **T01: Implement mist_list_wlans and mist_get_rf_templates tools** `est:30m`
  - Why: These are the simplest tier2 tools — both work at org level with pagination, following the same pattern as tier1 tools
  - Files: `mist_mcp/server.py`
  - Do: Add two @mcp.tool functions using mistapi SDK: wlans.listOrgWlans and rftemplates.listOrgRfTemplates. Follow S02 pattern: validate_org → get_session → get_org_id → API call → serialize response
  - Verify: python3 -m mist_mcp.server --help shows new tools
  - Done when: Both tools registered, import S02 helpers, follow existing patterns
- [x] **T02: Implement mist_get_inventory tool** `est:30m`
  - Why: Inventory search has rich filtering (type, status, site_id) — slightly more complex than org-level tools
  - Files: `mist_mcp/server.py`
  - Do: Add mist_get_inventory using mistapi's inventory.searchOrgInventory. Expose useful filters: type (ap/gateway/switch), status, site_id, name (partial match). Follow S02 pattern
  - Verify: python3 -m mist_mcp.server --help shows mist_get_inventory
  - Done when: Tool registered with type/status/site_id/name filters
- [x] **T03: Implement mist_get_device_config_cmd tool** `est:30m`
  - Why: Device config requires both site_id and device_id — different from org-level tools, must document this requirement clearly
  - Files: `mist_mcp/server.py`
  - Do: Add mist_get_device_config_cmd using mistapi's devices.getSiteDeviceConfigCmd. Requires site_id and device_id parameters. Must get org_id first to look up site. Follow S02 pattern
  - Verify: python3 -m mist_mcp.server --help shows tool with required parameters
  - Done when: Tool registered with site_id + device_id parameters, tool description explains requirement
- [x] **T04: Add verification tests** `est:30m`
  - Why: Need tests to verify tier2 tool registration, org validation for each tool, response serialization
  - Files: `tests/test_server.py`, `scripts/verify_s03.sh`
  - Do: Add tests: test_tier2_tools_registered, test_mist_list_wlans_invalid_org, test_mist_get_inventory_invalid_org, test_mist_get_rf_templates_invalid_org, test_mist_get_device_config_cmd_invalid_org. Create verify_s03.sh
  - Verify: pytest tests/test_server.py -v shows all tests pass
  - Done when: All tier2 tools have validation tests, verify_s03.sh exits 0

## Files Likely Touched

- `mist_mcp/server.py` — Add 4 new @mcp.tool functions
- `tests/test_server.py` — Add tests for tier2 tools
- `scripts/verify_s03.sh` — Create end-to-end verification script
