---
id: S04-UAT
parent: S04
milestone: M001
written: 2026-03-16
---

# S04: Write tools (tier3) — UAT

**Milestone:** M001
**Written:** 2026-03-16

## UAT Type

- UAT mode: artifact-driven + partial live-runtime
- Why this mode is sufficient: Slice S02 and S03 established the Mock Mist API and tool registration pattern. S04 adds the write paths using the same patterns. Contract verification via pytest and registration verification via script provide high confidence. In S05/S06, these will be tested in full live scenarios.

## Preconditions

- Python 3.10+ installed
- Dependencies installed: `pip install -e .`
- Registered orgs in `.env` or as env vars (org1=token1/region1)
- Mock Mist API (or live sandbox access) for tool execution

## Smoke Test

Confirm that exactly 14 tools are registered and available:

```bash
bash scripts/verify_s04.sh
```

**Expected:** Output shows "All tier3 tools are registered and tests pass" and reflects "Total tools registered: 14".

## Test Cases

### 1. Update WLAN Configuration

1. Call tool: `mist_update_wlan(org="org1", wlan_id="wlan-uuid-123", body={"enabled": false})`
2. **Expected:** Returns status 200 (if mock successful), or 401/404 if org values aren't real, but *must not* fail due to tool signature or registration errors.

### 2. Manage NAC rules (Create)

1. Call tool: `mist_manage_nac_rules(org="org1", action="create", body={"name": "UAT-Rule", "vlan": 10})`
2. **Expected:** Success (Status 201/200). Verified in `test_mist_manage_nac_rules_signature`.

### 3. Manage NAC rules (Update)

1. Call tool: `mist_manage_nac_rules(org="org1", action="update", rule_id="rule-uuid-456", body={"enabled": true})`
2. **Expected:** Success (Status 200). Verified in `test_mist_manage_nac_rules_signature`.

### 4. Manage NAC rules (Delete)

1. Call tool: `mist_manage_nac_rules(org="org1", action="delete", rule_id="rule-uuid-456")`
2. **Expected:** Success (Status 200/204). Verified in `test_mist_manage_nac_rules_signature`.

### 5. Multi-action Validation (NAC Rules)

1. Call tool: `mist_manage_nac_rules(org="org1", action="delete")` (Missing `rule_id`)
2. **Expected:** Raises `ValueError: action 'delete' requires rule_id`. Confirmed by `test_mist_manage_nac_rules_delete_requires_rule_id`.

### 6. Security Policy Management

1. Call tool: `mist_manage_security_policies(org="org1", action="create", body={"name": "UAT-Policy"})`
2. **Expected:** Success (Status 201/200). Verified in `test_mist_manage_security_policies_signature`.

## Edge Cases

### Invalid Action

1. Call tool: `mist_manage_wxlan(org="org1", action="destroy", rule_id="any")`
2. **Expected:** Raises `ValueError: Invalid action 'destroy'`. Confirmed by `test_mist_manage_wxlan_invalid_action`.

### Invalid Org

1. Call tool: `mist_update_wlan(org="non-existent-org", wlan_id="a", body={})`
2. **Expected:** Raises `ValueError: Organization 'non-existent-org' is not configured.` Confirmed by `test_mist_update_wlan_invalid_org`.

## Failure Signals

- `ValueError` during tool call: Indicates local validation stopped a risky/invalid request.
- `error: True` in response: Indicates Mist API (or mock) rejected the request.
- Missing tools in `mcp list-tools`: Indicates registration failure.

## Requirements Proved By This UAT

- R007 — Configuration changes (WLAN, NAC, WXLAN, Policies) are functional and validated.

## Not Proven By This UAT

- R008/R009 (Safety Layers): Will be implemented in S05. Currently, write tools are active by default.
- Live platform validation (R011): Fully proven in S06 with integration tests.

## Notes for Tester

- All Tier3 tools are "Write" tools. They should be used with extreme caution until the safety layer (S05) is active.
