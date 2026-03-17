---
id: T06
parent: S05
milestone: M001
provides:
  - Platform validation function `validate_platform_constraints(tool_name, params)` that validates Mist platform constraints before API calls
  - All 4 write tools now call platform validation before making API calls
  - 3 new pytest tests for platform validation behavior
key_files:
  - mist_mcp/server.py — Added validate_platform_constraints function and integrated into all 4 write tools
  - tests/test_server.py — Added 3 new tests: test_platform_validation_rejects_invalid_ids, test_platform_validation_accepts_valid_ids, test_platform_validation_logs_warnings_for_non_uuid
key_decisions:
  - Used regex pattern matching for UUID format validation (with warning for non-UUID but allowing it as names might work)
  - Validation runs after parameter validation but before API calls
patterns_established:
  - Platform validation before API calls as additional safety layer
  - Log warnings for non-UUID IDs (observability), raise ValueError for empty IDs (safety)
observability_surfaces:
  - Validation warnings logged at WARNING level when IDs don't match UUID format
  - Validation failures raised as ValueError before API calls
duration: 25m
verification_result: passed
completed_at: 2026-03-16T20:02:00-07:00
blocker_discovered: false
---

# T06: Add basic platform validation enhancement

**Platform validation function added and integrated into all 4 write tools.**

## What Happened

Implemented R011: added a `validate_platform_constraints(tool_name: str, params: dict) -> None` function that validates Mist platform constraints before write operations are submitted. The function:
- For `mist_update_wlan`: validates `wlan_id` is non-empty, logs warning if not UUID format
- For `mist_manage_nac_rules`: validates `rule_id` is non-empty for update/delete actions, logs warning if not UUID
- For `mist_manage_wxlan`: validates `rule_id` is non-empty for update/delete actions, logs warning if not UUID  
- For `mist_manage_security_policies`: validates `policy_id` is non-empty for update/delete actions, logs warning if not UUID

The function is called from each write tool after parameter validation but before API calls, providing an additional safety layer.

## Verification

- `pytest tests/test_server.py -xvs -k "validation"` - 4 validation tests pass
- `pytest tests/test_server.py -xvs` - All 71 tests pass (no regressions)
- `bash scripts/verify_s05.sh` - All 3 verification tests pass

Tests verify:
1. Empty IDs raise ValueError with descriptive message
2. Valid UUIDs are accepted without errors  
3. Non-UUID format IDs log warnings but don't fail (could be names)

## Diagnostics

To test validation manually:
```python
from mist_mcp.server import validate_platform_constraints

# This raises ValueError
validate_platform_constraints("mist_update_wlan", {"wlan_id": ""})

# This logs warning but succeeds
validate_platform_constraints("mist_update_wlan", {"wlan_id": "my-wlan-name"})

# This passes
import uuid
validate_platform_constraints("mist_update_wlan", {"wlan_id": str(uuid.uuid4())})
```

Runtime: Validation happens at INFO/DEBUG level in server logs before each write tool API call.

## Deviations

None - implemented exactly as planned.

## Known Issues

None.

## Files Created/Modified

- `mist_mcp/server.py` — Added `validate_platform_constraints()` function (lines 68-158), integrated into 4 write tools
- `tests/test_server.py` — Added 3 new platform validation tests
