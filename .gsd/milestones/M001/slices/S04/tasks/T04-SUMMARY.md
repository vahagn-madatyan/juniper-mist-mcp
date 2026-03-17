---
id: T04
parent: S04
milestone: M001
provides:
  - mist_manage_security_policies MCP tool for creating/updating/deleting security policies
key_files:
  - mist_mcp/server.py
  - tests/test_server.py
  - scripts/verify_s04.sh
key_decisions:
  - Used mistapi.api.v1.orgs.secpolicies SDK methods (createOrgSecPolicy, updateOrgSecPolicy, deleteOrgSecPolicy)
patterns_established:
  - Tier3 write tool pattern with multi-action validation (create/update/delete)
observability_surfaces:
  - Tool invocation logged via logger.info with org, action, and policy_id (no sensitive body content)
  - Error responses serialized with error: True flag and status_code from Mist API
duration: 45m
verification_result: passed
completed_at: 2026-03-16
blocker_discovered: false
---

# T04: Security policies tool + verification script

**Added mist_manage_security_policies tool and created S04 verification script**

## What Happened

Implemented the final tier3 write tool `mist_manage_security_policies` for managing security policies in Juniper Mist organizations, following the same multi-action pattern as `mist_manage_nac_rules` and `mist_manage_wxlan`. Created the `scripts/verify_s04.sh` verification script to confirm all four tier3 tools are registered and all tests pass.

The tool supports three actions:
- **create**: Create a new security policy (requires body)
- **update**: Update an existing security policy (requires policy_id and body)
- **delete**: Delete a security policy (requires policy_id)

## Verification

All verification checks passed:
- `bash scripts/verify_s04.sh` exits 0 ✓
- Total tool count: 14 (10 existing + 4 new tier3) ✓
- All pytest tests pass (61 tests) ✓
- Tool appears in registered tools list ✓

Tier3 tools verified:
- mist_update_wlan
- mist_manage_nac_rules
- mist_manage_wxlan
- mist_manage_security_policies

## Diagnostics

- Tool invocation logged via `logger.info(f"Tool called: mist_manage_security_policies(org={org}, action={action_lower}, policy_id={policy_id})")`
- Error responses serialized with `error: True` flag and status_code from Mist API
- No sensitive data (API tokens) logged

## Deviations

None. The implementation followed the task plan exactly.

## Known Issues

None.

## Files Created/Modified

- `mist_mcp/server.py` — Added mist_manage_security_policies tool function
- `tests/test_server.py` — Added 7 tests for the new tool (signature, org validation, action validation)
- `scripts/verify_s04.sh` — Created verification script for S04 slice
