---
estimated_steps: 7
estimated_files: 3
---

# T01: Refactor tool registration to manual pattern

**Slice:** S05 — Safety layers & multi-tenancy
**Milestone:** M001

## Description

Remove `@mcp.tool` decorators and implement manual registration via `mcp.add_tool()`. This decouples tool registration from import time, enabling conditional registration based on the `--enable-write-tools` flag.

## Steps

1. Remove all 14 `@mcp.tool` decorators from tool functions in `mist_mcp/server.py` (lines starting with `@mcp.tool`).
2. Add a `register_tools(enable_write: bool)` function after the tool definitions (before the CLI section). The function should:
   - Register all 10 read tools (tier1 + tier2) using `mcp.add_tool(func, annotations={...})` (annotations will be added in T02, leave empty for now).
   - Register all 4 write tools (tier3) regardless of `enable_write` (for now).
   - Use the same tool functions (they remain unchanged).
3. Update `main()` to call `register_tools(args.enable_write_tools)` before `mcp.run()`.
4. Update test file `tests/test_server.py`:
   - Import `register_tools` from `mist_mcp.server`.
   - In each test that checks tool registration (e.g., `test_mist_update_wlan_signature`), call `register_tools(enable_write=True)` before querying `mcp.list_tools()`.
   - Ensure tests don't double-register tools (calling `register_tools` multiple times may cause duplicates; we can guard with a flag or rely on FastMCP's internal deduplication). Use a simple module-level flag `_tools_registered` to prevent duplicate registration within the same process.
5. Update `scripts/verify_s04.sh` to call `register_tools(enable_write=True)` before checking tool list (since the script imports the mcp instance directly). Modify the Python verification script section accordingly.
6. Run the full test suite to verify all existing tests still pass.
7. Ensure the server still starts correctly in both stdio and HTTP modes (quick smoke test).

## Must-Haves

- [ ] No `@mcp.tool` decorators remain in `mist_mcp/server.py`
- [ ] `register_tools` function exists and registers all 14 tools
- [ ] `main()` calls `register_tools` before `mcp.run()`
- [ ] `scripts/verify_s04.sh` still passes (run `bash scripts/verify_s04.sh`)
- [ ] All 61 existing tests pass (`pytest tests/test_server.py -xvs`)

## Verification

- Run `pytest tests/test_server.py -xvs` and confirm all tests pass (no failures).
- Run `bash scripts/verify_s04.sh` and confirm it passes.
- Start the server with `python -m mist_mcp.server --transport stdio --enable-write-tools` and verify it starts without import errors.

## Observability Impact

- No runtime impact; tool registration happens at startup as before.

## Inputs

- `mist_mcp/server.py` — current version with decorator-based tool registration.
- `tests/test_server.py` — existing test suite with 61 tests.
- `scripts/verify_s04.sh` — existing verification script for S04.

## Expected Output

- `mist_mcp/server.py` updated with manual tool registration.
- `tests/test_server.py` updated to call `register_tools` in tool registration tests.
- `scripts/verify_s04.sh` updated to call `register_tools`.
- All existing functionality preserved.