# S04: Write tools (tier3)

**Goal:** Implement tier3 write tools that enable configuration changes to Juniper Mist organizations.
**Demo:** All four write tools are registered and callable via MCP server, following the same patterns as tier1/tier2 tools.

## Must-Haves

- Implement `mist_update_wlan` tool for updating existing WLAN configurations
- Implement `mist_manage_nac_rules` tool for creating/updating/deleting NAC (802.1X) rules
- Implement `mist_manage_wxlan` tool for creating/updating/deleting WXLAN microsegmentation rules
- Implement `mist_manage_security_policies` tool for creating/updating/deleting security policies
- All tools follow S02/S03 pattern: `validate_org → get_session → get_org_id → API call → serialize_api_response`
- Tools validate required parameters based on action (create/update/delete)
- Tools include proper documentation and logging

## Verification

- `bash scripts/verify_s04.sh` — exits 0, verifies 14 tools registered (10 existing + 4 new)
- `pytest tests/test_server.py -v` — all tests pass (including new tier3 tool tests)
- `python3 -c "import asyncio; from mist_mcp.server import mcp; print([t.name for t in asyncio.run(mcp.list_tools())])"` — includes the four new tool names

### Diagnostic Verification

- `pytest tests/test_server.py -k "invalid_org" -v` — all org validation tests pass, verifying that invalid orgs properly raise errors with "not configured" in error message

## Observability / Diagnostics

- All write tools log invocation via `logger.info()` with org and relevant parameters (excluding sensitive body content)
- API errors from Mist are captured in serialized response with `error: true` flag and status_code
- No sensitive data (API tokens, credentials) is logged — only org name and operation type
- Tool signature and parameter names are visible in MCP introspection for debugging

## Integration Closure

- Upstream surfaces consumed: `mist_mcp/server.py` (tool decorator pattern), `mist_mcp/session.py` (session manager), `mist_mcp/config.py` (org validation)
- New wiring introduced in this slice: Four new @mcp.tool functions added to server.py
- What remains before the milestone is truly usable end-to-end: Safety layers (S05) to disable write tools by default and add destructive hints; Integration testing with live API (S06)

## Tasks

- [x] **T01: WLAN update tool** `est:45m`
  - Why: Establish pattern for simplest write operation (single update method)
  - Files: `mist_mcp/server.py`, `tests/test_server.py`
  - Do: Implement `mist_update_wlan` tool using `mistapi.api.v1.orgs.wlans.updateOrgWlan`. Accept org, wlan_id, body parameters. Validate org, get session, get org_id, call API, serialize response. Add comprehensive tests including mock API calls.
  - Verify: `pytest tests/test_server.py::test_mist_update_wlan_signature -v` passes; tool appears in registered tools list.
  - Done when: Tool is registered and tests pass.
- [x] **T02: NAC rules management tool** `est:45m`
  - Why: Implement multi-action write tool pattern (create/update/delete)
  - Files: `mist_mcp/server.py`, `tests/test_server.py`
  - Do: Implement `mist_manage_nac_rules` tool using `mistapi.api.v1.orgs.nacrules` methods. Accept org, action, rule_id (optional), body (optional). Validate action is one of ["create","update","delete"], enforce required parameters (rule_id for update/delete, body for create/update). Add helper function for action validation if needed. Add tests for all three actions.
  - Verify: `pytest tests/test_server.py::test_mist_manage_nac_rules_signature -v` passes; tool appears in registered tools list.
  - Done when: Tool supports create, update, delete actions with validation.
- [x] **T03: WXLAN management tool** `est:45m`
  - Why: Apply multi-action pattern to WXLAN microsegmentation rules
  - Files: `mist_mcp/server.py`, `tests/test_server.py`
  - Do: Implement `mist_manage_wxlan` tool using `mistapi.api.v1.orgs.wxrules` methods. Same pattern as NAC rules. Add tests.
  - Verify: `pytest tests/test_server.py::test_mist_manage_wxlan_signature -v` passes; tool appears in registered tools list.
  - Done when: Tool supports create, update, delete actions with validation.
- [x] **T04: Security policies tool + verification script** `est:45m`
  - Why: Complete tier3 toolset and provide slice-level verification
  - Files: `mist_mcp/server.py`, `tests/test_server.py`, `scripts/verify_s04.sh`
  - Do: Implement `mist_manage_security_policies` tool using `mistapi.api.v1.orgs.secpolicies` methods. Same pattern as NAC/WXLAN. Add tests. Create verification script `scripts/verify_s04.sh` that checks 14 tools registered and runs tier3 tool tests.
  - Verify: `bash scripts/verify_s04.sh` exits 0; total tool count is 14.
  - Done when: All four tier3 tools registered, tests pass, verification script passes.

## Files Likely Touched

- `mist_mcp/server.py`
- `tests/test_server.py`
- `scripts/verify_s04.sh`
- `.gsd/milestones/M001/slices/S04/tasks/T01-PLAN.md`
- `.gsd/milestones/M001/slices/S04/tasks/T02-PLAN.md`
- `.gsd/milestones/M001/slices/S04/tasks/T03-PLAN.md`
- `.gsd/milestones/M001/slices/S04/tasks/T04-PLAN.md`