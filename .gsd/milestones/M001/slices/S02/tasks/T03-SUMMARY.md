---
id: T03
parent: S02
milestone: M001
provides:
  - test_tier1_tools_registered verifies all 5 tools registered
  - test_*_invalid_org tests verify org validation for each tool
  - test_*_valid_org tests verify valid orgs work
  - verify_s02.sh end-to-end verification script
key_files:
  - tests/test_server.py
  - scripts/verify_s02.sh
key_decisions:
  - Used asyncio directly in verify script instead of stdio JSON-RPC for reliability
patterns_established:
  - All new tests follow pytest pattern from existing test_server.py
  - Tests verify org parameter validation via validate_org function
observability_surfaces: none (tests are verification only)
duration: 15m
verification_result: passed
completed_at: 2026-03-15
blocker_discovered: false
---

# T03: Add verification tests

**Added comprehensive verification tests for all tier1 read tools.**

## What Happened

Added 14 new test functions to `tests/test_server.py` and created end-to-end verification script `scripts/verify_s02.sh`. Tests cover:
- Tool registration verification (all 5 tier1 tools)
- Org parameter validation for each tool (invalid org raises ValueError)
- Org validation with valid orgs (no exception)
- Additional serialization helpers tested

## Verification

All 24 tests in test_server.py pass:
- `pytest tests/test_server.py -v` — 24 passed
- `bash scripts/verify_s02.sh` — exits 0 with success message
- All tier1 tools verified as registered via asyncio check

## Diagnostics

No runtime diagnostics needed — tests verify tool registration and parameter validation without live API calls.

## Known Issues

None.

## Files Created/Modified

- `tests/test_server.py` — Added 14 new test functions for tier1 tool validation
- `scripts/verify_s02.sh` — Created end-to-end verification script
