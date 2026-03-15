# S02: Read tools (tier1)

**Goal:** Agent can query device stats, SLE metrics, client stats, alarms, and events across customer organizations
**Demo:** All 5 read tools registered in MCP server, respond to tool calls with formatted Mist API data

## Must-Haves

- `mist_get_device_stats` tool returns device statistics for an org
- `mist_get_sle_summary` tool returns SLE metrics for a specific site
- `mist_get_client_stats` tool returns wireless client statistics for an org
- `mist_get_alarms` tool returns active and historical alarms for an org
- `mist_get_site_events` tool returns event logs for an org or site
- All tools accept `org` parameter and validate org exists in config
- All tools return JSON-serialized responses suitable for LLM consumption

## Proof Level

- This slice proves: integration (real API calls via mistapi)
- Real runtime required: yes (mocked tests verify tool registration, real API depends on live tokens)
- Human/UAT required: no (verification via pytest)

## Verification

- `pytest tests/test_server.py::test_tier1_tools_registered -v` — all 5 tools registered
- `pytest tests/test_server.py::test_device_stats -v` — device stats returns formatted data
- `pytest tests/test_server.py::test_sle_summary -v` — SLE summary returns formatted data
- `pytest tests/test_server.py::test_client_stats -v` — client stats returns formatted data
- `pytest tests/test_server.py::test_alarms -v` — alarms returns formatted data
- `pytest tests/test_server.py::test_site_events -v` — events returns formatted data
- `bash scripts/verify_s02.sh` — end-to-end verification of all tools

## Observability / Diagnostics

- Runtime signals: Each tool logs its name and org parameter at INFO level
- Inspection surfaces: `python3 -m mist_mcp.server --help` shows all registered tools
- Failure visibility: ERROR logs for API failures, ValueError for invalid orgs
- Redaction constraints: None (org names are non-sensitive)

## Integration Closure

- Upstream surfaces consumed: MistSessionManager, Config, validate_org function from S01
- New wiring introduced in this slice: 5 new @mcp.tool decorated functions in server.py
- What remains before the milestone is truly usable end-to-end: S03 (config viewing tools), S04 (write tools), S05 (safety layers), S06 (testing)

## Tasks

- [x] **T01: Add device stats and SLE summary tools** `est:30m`
  - Why: Core operational tools for monitoring device health and service levels
  - Files: `mist_mcp/server.py`, `tests/test_server.py`
  - Do: Add mist_get_device_stats and mist_get_sle_summary functions using mistapi endpoints, follow existing server.py pattern with validate_org and ctx.lifespan_context access
  - Verify: pytest tests/test_server.py::test_device_stats -v passes
  - Done when: Both tools registered and respond to mock API responses
- [x] **T02: Add client stats, alarms, and events tools** `est:30m`
  - Why: Complete the tier1 toolset for troubleshooting client connectivity, alarms, and audit logs
  - Files: `mist_mcp/server.py`, `tests/test_server.py`
  - Do: Add mist_get_client_stats, mist_get_alarms, mist_get_site_events functions using mistapi endpoints
  - Verify: pytest tests/test_server.py::test_client_stats -v passes
  - Done when: All 5 tools registered in MCP server
- [x] **T03: Add verification tests** `est:20m`
  - Why: Verify all tools work correctly with proper response formatting
  - Files: `tests/test_server.py`, `scripts/verify_s02.sh`
  - Do: Add unit tests for each tier1 tool covering org validation, API call, response formatting
  - Verify: pytest tests/test_server.py -v passes
  - Done when: All tests pass and verify_s02.sh exits 0

## Files Likely Touched

- `mist_mcp/server.py` — Add 5 new tool functions
- `tests/test_server.py` — Add verification tests
- `scripts/verify_s02.sh` — End-to-end verification script (new)
