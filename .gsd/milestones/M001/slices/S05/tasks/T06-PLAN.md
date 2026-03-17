---
estimated_steps: 6
estimated_files: 2
---

# T06: Add basic platform validation enhancement

**Slice:** S05 — Safety layers & multi-tenancy
**Milestone:** M001

## Description

Fulfill R011: write operations validate against Mist platform constraints before submission. Add a lightweight validation function that checks required fields, ID formats, and logs warnings. This provides an additional safety layer before hitting the Mist API.

## Steps

1. In `mist_mcp/server.py`, add a `validate_platform_constraints(tool_name: str, params: dict) -> None` function that:
   - For `mist_update_wlan`: ensure `wlan_id` is a UUID format (or at least non-empty string).
   - For `mist_manage_nac_rules`, `mist_manage_wxlan`, `mist_manage_security_policies`: validate that `action` is valid, required parameters present (already done), and IDs are non-empty.
   - Log a warning if validation fails, raise `ValueError` with descriptive message.
2. Call this validation function at the beginning of each write tool (after parameter validation but before API call).
3. Ensure validation does not duplicate existing parameter validation (keep existing checks).
4. Add a test that verifies validation works: `test_platform_validation_rejects_invalid_ids`.
5. Update existing write tool tests to ensure they still pass with validation.
6. Run the test suite to ensure no regressions.

## Must-Haves

- [ ] `validate_platform_constraints` function exists and is called from all 4 write tools
- [ ] Validation logs warnings for suspicious inputs
- [ ] Validation raises `ValueError` for clearly invalid inputs (e.g., empty ID)
- [ ] New test verifies validation behavior
- [ ] All existing tests pass

## Verification

- Run `pytest tests/test_server.py -xvs -k "validation"` to see new test pass.
- Run full test suite to ensure no breakage.
- Manually test with invalid inputs (e.g., empty wlan_id) and see appropriate error.

## Observability Impact

- Validation failures are logged with tool name and parameter details.
- Errors are raised before API calls, preventing unnecessary network requests.

## Inputs

- `mist_mcp/server.py` with write tool implementations.
- `tests/test_server.py` with existing write tool tests.

## Expected Output

- Validation function added.
- Write tools call validation.
- New test added.
- All tests pass.