---
estimated_steps: 6
estimated_files: 2
---

# T03: Implement conditional write tool registration based on flag

**Slice:** S05 — Safety layers & multi-tenancy
**Milestone:** M001

## Description

Make write tools (tier3) only registered when `--enable-write-tools` flag is set, fulfilling R008 and R009. This is the core safety layer: by default, the server is read-only.

## Steps

1. In `mist_mcp/server.py`, modify `register_tools(enable_write: bool)` to conditionally register write tools:
   - If `enable_write` is True, register all 4 write tools with `destructiveHint=True`.
   - If `enable_write` is False, skip registration of write tools entirely.
2. Update `main()`: remove the warning log line `logger.warning("--enable-write-tools flag is set but write tools are not yet implemented")`.
3. Add logging in `register_tools` to indicate how many tools are registered (e.g., "Registered X read tools and Y write tools").
4. Update tests to verify conditional behavior:
   - `test_write_tools_not_registered_by_default()`: Call `register_tools(enable_write=False)` and verify only 10 tools appear.
   - `test_write_tools_registered_with_flag()`: Call `register_tools(enable_write=True)` and verify 14 tools appear.
5. Update existing tool signature tests to handle both modes (they should call `register_tools(enable_write=True)` to keep them passing).
6. Ensure the flag works in real runtime: test starting server without flag (should have 10 tools) and with flag (should have 14 tools) using a simple script or subprocess.

## Must-Haves

- [ ] Write tools are NOT registered when `enable_write=False`
- [ ] Write tools ARE registered when `enable_write=True`
- [ ] The `--enable-write-tools` flag actually controls registration (no warning)
- [ ] Tests verify conditional registration

## Verification

- Run `pytest tests/test_server.py -xvs -k "registered"` to see new conditional tests pass.
- Run `python -c "import asyncio; from mist_mcp.server import mcp, register_tools; register_tools(enable_write=False); tools = asyncio.run(mcp.list_tools()); print(len(tools), [t.name for t in tools])"` and confirm only 10 tools.
- Run the same with `enable_write=True` and confirm 14 tools.

## Observability Impact

- Server logs show number of registered tools at startup, indicating whether write tools are enabled.

## Inputs

- `mist_mcp/server.py` with annotation support from T02.
- `tests/test_server.py` with annotation tests.

## Expected Output

- Conditional registration working.
- Updated tests covering both modes.
- `--enable-write-tools` flag now functional.