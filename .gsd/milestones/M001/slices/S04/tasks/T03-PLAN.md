---
estimated_steps: 7
estimated_files: 2
---

# T03: WXLAN management tool

**Slice:** S04 — Write tools (tier3)
**Milestone:** M001

## Description

Implement the `mist_manage_wxlan` tool for creating, updating, and deleting WXLAN microsegmentation rules. This follows the exact multi-action pattern established in T02 (NAC rules), but uses the `wxrules` SDK module instead. The tool validates action parameter, enforces required parameters, and calls the appropriate SDK method.

## Steps

1. Open `mist_mcp/server.py` and locate after `mist_manage_nac_rules` tool.
2. Add new `@mcp.tool` function `mist_manage_wxlan` with parameters `org`, `action`, `rule_id=None`, `body=None`. Include docstring describing WXLAN microsegmentation purpose.
3. Implement validation identical to NAC rules: check `action` is one of `["create", "update", "delete"]` (case-insensitive). Raise `ValueError` if invalid.
4. Enforce required parameters per action: `body` required for create/update, `rule_id` required for update/delete.
5. Import `mistapi.api.v1.orgs.wxrules` module and call appropriate SDK method: `createOrgWxRule`, `updateOrgWxRule`, or `deleteOrgWxRule`.
6. Return `serialize_api_response(response)`.
7. Add tests to `tests/test_server.py`: signature test, org validation test, action validation tests. Reuse patterns from T02 tests.

## Must-Haves

- [ ] `mist_manage_wxlan` tool registered in MCP server
- [ ] Tool accepts `org`, `action`, `rule_id` (optional), `body` (optional) parameters
- [ ] Tool validates action parameter (raises ValueError for invalid action)
- [ ] Tool enforces required parameters per action (raises ValueError if missing)
- [ ] Tool calls correct SDK method based on action
- [ ] Tests pass: `pytest tests/test_server.py::test_mist_manage_wxlan_signature -v`

## Verification

- Run `python3 -c "import asyncio; from mist_mcp.server import mcp; print([t.name for t in asyncio.run(mcp.list_tools())])"` and verify `mist_manage_wxlan` appears.
- Run `pytest tests/test_server.py -k mist_manage_wxlan -v` — all tests pass.
- Test action validation: call tool with invalid action and expect ValueError.

## Observability Impact

- Tool logs invocation with action and parameters via `logger.info`.
- Validation errors are raised as ValueError with clear messages.

## Inputs

- `mist_mcp/server.py` — existing tool pattern, helpers.
- `mistapi.api.v1.orgs.wxrules` SDK methods (research).
- T02's multi-action pattern and validation logic.

## Expected Output

- Modified `mist_mcp/server.py` with new `mist_manage_wxlan` tool.
- Modified `tests/test_server.py` with new tests for the tool.
- Total tool count increased from 12 to 13.