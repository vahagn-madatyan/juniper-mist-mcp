---
estimated_steps: 6
estimated_files: 2
---

# T04: Update tests for safety layers

**Slice:** S05 — Safety layers & multi-tenancy
**Milestone:** M001

## Description

Add comprehensive tests for safety layer behavior and ensure test isolation. This includes verifying tool counts, annotations, and conditional registration across different test scenarios.

## Steps

1. In `tests/test_server.py`, add a helper function `reset_tools()` that clears registered tools from the global `mcp` instance (e.g., `mcp._tools.clear()` if attribute exists). If not, use `importlib.reload` to reload the module.
2. Create a pytest fixture `clean_mcp` that calls `reset_tools()` before each test that uses tool registration.
3. Update existing tool signature tests (e.g., `test_mist_update_wlan_signature`) to use the fixture and call `register_tools(enable_write=True)`.
4. Add missing safety layer tests:
   - `test_read_tools_have_readonly_hint` (already in T02)
   - `test_write_tools_have_destructive_hint` (already in T02)
   - `test_write_tools_not_registered_by_default` (already in T03)
   - `test_write_tools_registered_with_flag` (already in T03)
   - `test_annotation_persistence`: verify annotations survive tool listing.
5. Ensure all tests pass with the new fixture and isolation.
6. Run the full test suite and verify no regressions.

## Must-Haves

- [ ] Test isolation: each test starts with a clean tool registry
- [ ] All safety layer tests pass (tool counts, annotations)
- [ ] Existing tests still pass with updated fixture
- [ ] No duplicate tool registration across tests

## Verification

- Run `pytest tests/test_server.py -xvs --tb=short` and see all tests pass.
- Run `pytest tests/test_server.py -xvs -k "hint"` to see annotation tests pass.
- Run `pytest tests/test_server.py -xvs -k "registered"` to see conditional registration tests pass.

## Observability Impact

- Tests provide clear failure messages if safety layers break.

## Inputs

- `tests/test_server.py` with existing tests and new annotation/conditional tests from T02/T03.
- `mist_mcp/server.py` with conditional registration from T03.

## Expected Output

- Updated `tests/test_server.py` with fixture and proper test isolation.
- All tests passing.
- Safety layer behavior validated by automated tests.