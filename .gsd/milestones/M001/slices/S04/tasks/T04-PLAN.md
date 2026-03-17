---
estimated_steps: 9
estimated_files: 3
---

# T04: Security policies tool + verification script

**Slice:** S04 — Write tools (tier3)
**Milestone:** M001

## Description

Implement the `mist_manage_security_policies` tool for creating, updating, and deleting security policies. This completes the tier3 toolset. Also create a verification script `scripts/verify_s04.sh` that confirms all four tier3 tools are registered and tests pass, providing a single command to validate the slice.

## Steps

1. Open `mist_mcp/server.py` and locate after `mist_manage_wxlan` tool.
2. Add new `@mcp.tool` function `mist_manage_security_policies` with parameters `org`, `action`, `policy_id=None`, `body=None`. Include docstring describing security policies purpose.
3. Implement validation identical to previous multi-action tools: check `action` is one of `["create", "update", "delete"]`. Enforce required parameters per action.
4. Import `mistapi.api.v1.orgs.secpolicies` module and call appropriate SDK method: `createOrgSecPolicy`, `updateOrgSecPolicy`, or `deleteOrgSecPolicy`.
5. Return `serialize_api_response(response)`.
6. Add tests to `tests/test_server.py`: signature test, org validation test, action validation tests.
7. Create `scripts/verify_s04.sh` script that:
   - Verifies 14 tools total registered (10 existing + 4 new tier3)
   - Lists tier3 tool names
   - Runs pytest tests for tier3 tools (filter by "mist_update_wlan", "mist_manage_nac_rules", "mist_manage_wxlan", "mist_manage_security_policies")
   - Exits with success if all checks pass.
8. Ensure script is executable (`chmod +x scripts/verify_s04.sh`).
9. Run verification script to confirm slice completion.

## Must-Haves

- [ ] `mist_manage_security_policies` tool registered in MCP server
- [ ] Tool accepts `org`, `action`, `policy_id` (optional), `body` (optional) parameters
- [ ] Tool validates action parameter and required parameters
- [ ] Tool calls correct SDK method based on action
- [ ] Verification script `scripts/verify_s04.sh` exists and passes
- [ ] Total tool count is 14

## Verification

- Run `bash scripts/verify_s04.sh` — exits 0, outputs success.
- Run `python3 -c "import asyncio; from mist_mcp.server import mcp; tools = asyncio.run(mcp.list_tools()); print(len(tools))"` — prints 14.
- Run `pytest tests/test_server.py -v` — all tests pass (including new tier3 tests).

## Observability Impact

- Tool logs invocation with action and parameters via `logger.info`.
- Verification script provides clear pass/fail status for slice completion.

## Inputs

- `mist_mcp/server.py` — existing tool pattern, helpers.
- `mistapi.api.v1.orgs.secpolicies` SDK methods (research).
- T02/T03 multi-action pattern and validation logic.
- `scripts/verify_s03.sh` as template for verification script.

## Expected Output

- Modified `mist_mcp/server.py` with new `mist_manage_security_policies` tool.
- Modified `tests/test_server.py` with new tests for the tool.
- New file `scripts/verify_s04.sh` that verifies slice completion.
- Total tool count increased from 13 to 14.