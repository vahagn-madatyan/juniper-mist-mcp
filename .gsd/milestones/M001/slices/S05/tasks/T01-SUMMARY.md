---
id: T01
parent: S05
milestone: M001
provides:
  - Manual tool registration function `register_tools(enable_write: bool)`
  - Removed all 14 `@mcp.tool` decorators
  - Tests updated to call registration before checking tool list
key_files:
  - mist_mcp/server.py
  - tests/test_server.py
  - scripts/verify_s04.sh
key_decisions:
  - Used FastMCP's `mcp.add_tool(func)` without annotations for T01 (annotations added in T02)
  - Implemented duplicate registration guard with module-level `_tools_registered` flag
patterns_established:
  - Manual tool registration via `mcp.add_tool()` instead of decorators
observability_surfaces:
  - Server logs tool registration at INFO level
duration: 15m
verification_result: passed
completed_at: 2026-03-16
blocker_discovered: false
---

# T01: Refactor tool registration to manual pattern

**Manual tool registration pattern implemented, all 61 tests pass.**

## What Happened

Removed all 14 `@mcp.tool` decorators from tool functions in `mist_mcp/server.py` and implemented a `register_tools(enable_write: bool)` function that manually registers all tools using `mcp.add_tool()`. The function includes a duplicate registration guard (`_tools_registered` module-level flag) to prevent issues in tests that call registration multiple times.

Updated `main()` to call `register_tools(enable_write=args.enable_write_tools)` before `mcp.run()`. Updated all test functions that check tool registration to call `register_tools(enable_write=True)` before querying the tool list. Updated `scripts/verify_s04.sh` to call `register_tools` before checking tool counts.

## Verification

- `pytest tests/test_server.py -xvs` → **61 passed**
- `bash scripts/verify_s04.sh` → **VERIFICATION PASSED**
- Manual tool check: 14 tools registered (10 read + 4 write)
- Server starts correctly with `--transport stdio` and `--enable-write-tools`

## Diagnostics

- Runtime logs show each tool as it's registered at INFO level
- Tool count verified via `mcp.list_tools()` returns 14 tools

## Deviations

- None: followed the plan exactly

## Known Issues

- None

## Files Created/Modified

- `mist_mcp/server.py` — Removed 14 `@mcp.tool` decorators, added `register_tools()` function, updated `main()`
- `tests/test_server.py` — Added `register_tools` import, updated 14 test functions to call registration before checking tools
- `scripts/verify_s04.sh` — Updated Python verification sections to call `register_tools(enable_write=True)`
