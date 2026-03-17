---
estimated_steps: 8
estimated_files: 2
---

# T02: NAC rules management tool

**Slice:** S04 — Write tools (tier3)
**Milestone:** M001

## Description

Implement the `mist_manage_nac_rules` tool for creating, updating, and deleting NAC (802.1X) rules. This introduces the multi-action write tool pattern (create/update/delete) that will be reused for WXLAN and security policies. The tool validates the action parameter, enforces required parameters per action, and calls the appropriate SDK method.

## Steps

1. Open `mist_mcp/server.py` and locate after `mist_update_wlan` tool.
2. Add new `@mcp.tool` function `mist_manage_nac_rules` with parameters `org`, `action`, `rule_id=None`, `body=None`. Include docstring describing the tool's purpose, actions, and parameter requirements.
3. Implement validation: check `action` is one of `["create", "update", "delete"]` (case-insensitive). Raise `ValueError` if invalid.
4. For `action == "create"`: require `body` not None; `rule_id` ignored.
5. For `action == "update"`: require both `rule_id` and `body` not None.
6. For `action == "delete"`: require `rule_id` not None; `body` ignored.
7. Import `mistapi.api.v1.orgs.nacrules` module and call appropriate SDK method: `createOrgNacRule`, `updateOrgNacRule`, or `deleteOrgNacRule`.
8. Add tests to `tests/test_server.py`: signature test, org validation test, action validation tests, required parameter validation tests. Use existing patterns.

## Must-Haves

- [ ] `mist_manage_nac_rules` tool registered in MCP server
- [ ] Tool accepts `org`, `action`, `rule_id` (optional), `body` (optional) parameters
- [ ] Tool validates action parameter (raises ValueError for invalid action)
- [ ] Tool enforces required parameters per action (raises ValueError if missing)
- [ ] Tool calls correct SDK method based on action
- [ ] Tests pass: `pytest tests/test_server.py::test_mist_manage_nac_rules_signature -v`

## Verification

- Run `python3 -c "import asyncio; from mist_mcp.server import mcp; print([t.name for t in asyncio.run(mcp.list_tools())])"` and verify `mist_manage_nac_rules` appears.
- Run `pytest tests/test_server.py -k mist_manage_nac_rules -v` — all tests pass.
- Test action validation: call tool with invalid action (e.g., "invalid") and expect ValueError.

## Observability Impact

- Tool logs invocation with action and parameters via `logger.info`.
- Validation errors are raised as ValueError with clear messages.

## Inputs

- `mist_mcp/server.py` — existing tool pattern, helpers.
- `mistapi.api.v1.orgs.nacrules` SDK methods (research).
- T01's WLAN update tool pattern.

## Expected Output

- Modified `mist_mcp/server.py` with new `mist_manage_nac_rules` tool.
- Modified `tests/test_server.py` with new tests for the tool.
- Total tool count increased from 11 to 12.