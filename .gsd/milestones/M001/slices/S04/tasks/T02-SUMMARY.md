---
id: T02
parent: S04
milestone: M001
provides:
  - mist_manage_nac_rules MCP tool for creating, updating, and deleting NAC rules
key_files:
  - mist_mcp/server.py
  - tests/test_server.py
key_decisions:
  - Used mistapi.api.v1.orgs.nacrules SDK methods (createOrgNacRule, updateOrgNacRule, deleteOrgNacRule)
patterns_established:
  - Tier3 write tool pattern with multi-action validation (create/update/delete)
observability_surfaces:
  - Tool logs invocation via logger.info with action and parameters
  - Validation errors raised as ValueError with clear messages
duration: 15 minutes
verification_result: passed
completed_at: 2026-03-16
blocker_discovered: false
---

# T02: NAC rules management tool

**Added mist_manage_nac_rules tool for creating, updating, and deleting NAC (802.1X) rules in Juniper Mist organizations.**

## What Happened

Implemented the `mist_manage_nac_rules` tool following the established tier3 write tool pattern. The tool:

1. Accepts parameters: `org`, `action` (create/update/delete), `rule_id` (optional), `body` (optional)
2. Validates action parameter (case-insensitive) - raises ValueError for invalid actions
3. Enforces required parameters per action:
   - create: requires body
   - update: requires both rule_id and body
   - delete: requires rule_id
4. Calls appropriate SDK method based on action:
   - createOrgNacRule for create
   - updateOrgNacRule for update
   - deleteOrgNacRule for delete

## Verification

- Tool registered in MCP server: confirmed 12 tools present including `mist_manage_nac_rules`
- All 7 new tests pass:
  - test_mist_manage_nac_rules_signature
  - test_mist_manage_nac_rules_invalid_org
  - test_mist_manage_nac_rules_valid_org
  - test_mist_manage_nac_rules_invalid_action
  - test_mist_manage_nac_rules_create_requires_body
  - test_mist_manage_nac_rules_update_requires_rule_id_and_body
  - test_mist_manage_nac_rules_delete_requires_rule_id
- Invalid action validation confirmed: raises ValueError with message "Invalid action 'invalid'. Must be one of: ['create', 'update', 'delete']"
- All 47 tests in test_server.py pass

## Diagnostics

- Tool invocation logged via `logger.info(f"Tool called: mist_manage_nac_rules(org={org}, action={action_lower}, rule_id={rule_id})")`
- Error responses serialized with `error: True` flag and status_code from Mist API
- No sensitive data (API tokens) logged

## Deviations

None

## Known Issues

None

## Files Created/Modified

- `mist_mcp/server.py` — Added `mist_manage_nac_rules` tool after `mist_update_wlan`
- `tests/test_server.py` — Added 7 new tests for the NAC rules management tool
