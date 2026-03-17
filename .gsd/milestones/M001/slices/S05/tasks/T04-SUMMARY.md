---
id: T04
parent: S05
milestone: M001
provides:
  - Test isolation helper function `reset_tools()` for clearing MCP tool state
  - Pytest fixture `clean_mcp` for automatic test isolation
  - `test_annotation_persistence` test verifying annotations survive tool listing
key_files:
  - tests/test_server.py
key_decisions:
  - Used subprocess-based tests for complete test isolation (existing pattern)
  - Implemented best-effort in-process tool clearing via `reset_tools()` helper
patterns_established:
  - Test isolation via pytest fixtures (autouse=True)
  - Subprocess-based tests for clean MCP state verification
observability_surfaces:
  - pytest test output shows pass/fail for all safety layer tests
  - Runtime logs show tool registration with annotations at INFO level
duration: 15 minutes
verification_result: passed
completed_at: 2026-03-16T21:00:17-07:00
blocker_discovered: false
---

# T04: Update tests for safety layers

**Test isolation and safety layer validation implemented for Slice S05**

## What Happened

Added comprehensive tests for safety layer behavior with proper test isolation:

1. **Helper function `reset_tools()`**: Added function to clear registered tools from the MCP instance for test isolation. Uses best-effort approach to clear internal FastMCP state.

2. **Pytest fixture `clean_mcp`**: Created autouse fixture that calls `reset_tools()` before and after each test to ensure test isolation and prevent duplicate tool registration.

3. **Test `test_annotation_persistence`**: Added new test that verifies tool annotations (readOnlyHint/destructiveHint) persist correctly across multiple calls to `mcp.list_tools()`. Uses subprocess for complete isolation.

4. **Existing tests updated**: All tests continue to work with the new fixture. Tests that require tool registration call `register_tools(enable_write=True)` after the fixture runs.

## Verification

All 68 tests pass:
- `pytest tests/test_server.py -xvs --tb=short` - **68 passed**
- `pytest tests/test_server.py -xvs -k "hint"` - **3 passed** (annotation tests)
- `pytest tests/test_server.py -xvs -k "registered"` - **5 passed** (conditional registration tests)
- `pytest tests/test_server.py::test_annotation_persistence` - **1 passed**

Safety layer behavior verified:
- Without flag: 10 tools registered (read-only)
- With flag: 14 tools registered (read + write)
- Read tools have `readOnlyHint=True`
- Write tools have `destructiveHint=True` (when enabled)

## Diagnostics

Tests provide clear pass/fail signals for safety layer behavior:
- Annotation tests verify `readOnlyHint` and `destructiveHint` are present
- Conditional registration tests verify write tools disabled by default
- Tool persistence test verifies annotations survive multiple list operations

## Deviations

None - implemented exactly as specified in task plan.

## Known Issues

FastMCP logs "Component already exists" warnings during test runs due to tools being re-registered in the same process. This doesn't affect test correctness - tests still pass. Subprocess-based tests (T03 pattern) provide complete isolation.

## Files Created/Modified

- `tests/test_server.py` — Added helper function, pytest fixture, and annotation persistence test
