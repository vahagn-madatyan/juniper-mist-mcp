---
estimated_steps: 5
estimated_files: 2
---

# T02: Add annotation hints (readOnlyHint/destructiveHint)

**Slice:** S05 — Safety layers & multi-tenancy
**Milestone:** M001

## Description

Add MCP annotations `readOnlyHint=True` for read tools (tier1 + tier2) and `destructiveHint=True` for write tools (tier3). These hints signal to LLM clients that write operations are destructive and require confirmation, fulfilling R010.

## Steps

1. In `mist_mcp/server.py`, update `register_tools` to include annotations for each tool:
   - For read tools (10 tools): `annotations={"readOnlyHint": True}`
   - For write tools (4 tools): `annotations={"destructiveHint": True}`
   Use `mcp.add_tool(func, annotations=annotations)`.
2. Ensure annotations are valid JSON-serializable values (booleans).
3. Add a test in `tests/test_server.py` that verifies annotations are present:
   - `test_read_tools_have_readonly_hint()`: After registering tools, iterate through tool list, check that read tools have `readOnlyHint=True`.
   - `test_write_tools_have_destructive_hint()`: Check write tools have `destructiveHint=True`.
   Use `await mcp.list_tools()` and inspect each tool's `annotations` attribute (should be a dict).
4. Update existing tool signature tests to also verify annotations (optional, but good).
5. Run the test suite to ensure new tests pass and existing tests still pass.

## Must-Haves

- [ ] All read tools have `readOnlyHint=True` annotation
- [ ] All write tools have `destructiveHint=True` annotation
- [ ] New tests verify annotations exist
- [ ] All existing tests still pass

## Verification

- Run `pytest tests/test_server.py -xvs -k "hint"` to see new tests pass.
- Run full test suite to ensure no regressions.

## Observability Impact

- Tool annotations are exposed via MCP `tools/list` endpoint, enabling LLM clients to show confirmation dialogs for destructive operations.

## Inputs

- `mist_mcp/server.py` with manual registration from T01.
- `tests/test_server.py` with updated registration calls.

## Expected Output

- Updated `register_tools` with annotations.
- New tests in `tests/test_server.py` verifying annotations.
- All tests pass.