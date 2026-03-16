# S03: Config viewing tools (tier2) — UAT

**Milestone:** M001
**Written:** 2026-03-15

## UAT Type

- UAT mode: artifact-driven + live-runtime (mixed)
- Why this mode is sufficient: Contract verification via tests proves tool registration and org validation. Full integration verification requires live Mist API (pending S06).

## Preconditions

- Server can start: `python3 -m mist_mcp.server --help`
- .env file configured with valid org/token/region
- Test suite passes: `pytest tests/test_server.py -v`

## Smoke Test

```bash
# Verify all 10 tools registered (1 base + 5 tier1 + 4 tier2)
python3 -c "from mist_mcp.server import mcp; print(len(mcp._tools))"
# Expected: 10

# Run verification script
bash scripts/verify_s03.sh
# Expected: exits 0, all checks pass
```

## Test Cases

### 1. Tool Registration

1. Import server module and list registered tools
2. **Expected:** All 4 tier2 tools present: mist_list_wlans, mist_get_rf_templates, mist_get_inventory, mist_get_device_config_cmd

### 2. Org Parameter Validation

1. Call any tier2 tool with invalid org name
2. **Expected:** ValueError with "Organization not found" message

### 3. Tool Parameters

1. Inspect tool signatures (via FastMCP introspection)
2. **Expected:** 
   - mist_list_wlans: org (required), limit (optional), page (optional)
   - mist_get_rf_templates: org (required), limit (optional), page (optional)
   - mist_get_inventory: org (required), type/status/site_id/name/limit/offset (optional)
   - mist_get_device_config_cmd: org (required), site_id (required), device_id (required), sort (optional)

### 4. Pagination Support

1. Check serialize_api_response output for paginated tools
2. **Expected:** Response includes has_more (bool) and next_page (int or null) fields

## Edge Cases

### Invalid Org Name

1. Call tool with org="nonexistent_customer"
2. **Expected:** ValueError raised before API call, not 401/403 from API

### Empty Results

1. Call tool for org with no data (e.g., no WLANs configured)
2. **Expected:** Returns empty list [], not error — has_more: false

### Device Config with Invalid IDs

1. Call mist_get_device_config_cmd with invalid site_id or device_id
2. **Expected:** Error response from Mist API (not Python error) — serialized as error: true

## Failure Signals

- pytest tests fail — indicates code regression
- verify_s03.sh exits non-zero — indicates tool registration issue
- ImportError on server module — missing dependencies
- ValueError on valid org — config loading broken

## Requirements Proved By This UAT

- R006 — Tier2 config tools are implemented and verified through contract tests

## Not Proven By This UAT

- Live Mist API integration (requires S06 with sandbox/test org)
- Rate limit handling under load (S06 behavioral tests)
- HTTP transport mode verification (S01 pattern confirmed stdio)
- Write tool safety layers (S05)

## Notes for Tester

- All tests currently use mocked responses or config validation — full integration verification with live Mist API pending S06
- Device config tool requires UUIDs for site_id/device_id, not names — ensure test data includes valid Mist identifiers
- Filter parameters for inventory (type, status, site_id, name) are optional — tool should work with none provided