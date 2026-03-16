# T04: Add verification tests

**Slice:** S03 — Config viewing tools (tier2)
**Milestone:** M001

## Description

Add tests to verify tier2 tool registration, org validation for each tool, and create end-to-end verification script.

## Steps

1. Read existing tests in test_server.py to understand test patterns from S02
2. Add test for tier2 tool registration:
   - `test_tier2_tools_registered` — asserts all 4 tier2 tools are registered in server.mcp
3. Add org validation tests for each tier2 tool:
   - `test_mist_list_wlans_invalid_org` — asserts ValueError for invalid org
   - `test_mist_get_rf_templates_invalid_org` — asserts ValueError for invalid org
   - `test_mist_get_inventory_invalid_org` — asserts ValueError for invalid org
   - `test_mist_get_device_config_cmd_invalid_org` — asserts ValueError for invalid org
4. Create verify_s03.sh script:
   - Run pytest tests/test_server.py with tier2-focused tests
   - Check tool count matches expectation (10 total: 1 base + 5 tier1 + 4 tier2)
   - Exit 0 on success, non-zero on failure

## Must-Haves

- [ ] test_tier2_tools_registered verifies all 4 tools registered
- [ ] Each tier2 tool has invalid_org test
- [ ] verify_s03.sh script exists and exits 0 when run
- [ ] All existing S02 tests still pass

## Verification

- `pytest tests/test_server.py -v` — all tests pass including new tier2 tests
- `bash scripts/verify_s03.sh` — exits 0 with all verifications

## Inputs

- `tests/test_server.py` — Existing test patterns from S02
- `scripts/verify_s02.sh` — Reference for verify script format

## Expected Output

- `tests/test_server.py` — New test methods added
- `scripts/verify_s03.sh` — New verification script created
