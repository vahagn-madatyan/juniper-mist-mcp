---
id: T02
parent: S05
milestone: M001
provides:
  - MCP tool annotations (readOnlyHint for read tools, destructiveHint for write tools)
key_files:
  - mist_mcp/server.py
  - tests/test_server.py
key_decisions:
  - Used FastMCP's Tool.from_function() with ToolAnnotations to add annotations to tools
  - Annotations are Pydantic models from mcp.types (not dicts)
patterns_established:
  - Manual tool registration with annotations using Tool.from_function(func, annotations=ToolAnnotations(...))
observability_surfaces:
  - Runtime logs show annotation hints when tools are registered
  - MCP tools/list endpoint exposes annotations to LLM clients
duration: 25m
verification_result: passed
completed_at: 2026-03-16
blocker_discovered: false
---

# T02: Add annotation hints (readOnlyHint/destructiveHint)

**Added MCP tool annotations to all 14 tools - read tools get `readOnlyHint=True`, write tools get `destructiveHint=True`**

## What Happened

Implemented T02 of Slice S05 (Safety layers & multi-tenancy) which adds MCP annotation hints to tools:

1. Updated `mist_mcp/server.py`:
   - Added imports for `Tool` from `fastmcp.tools` and `ToolAnnotations` from `mcp.types`
   - Modified `register_tools()` function to create tools with annotations using `Tool.from_function(func, annotations=...)`
   - Read tools (10): `ToolAnnotations(readOnlyHint=True)`
   - Write tools (4): `ToolAnnotations(destructiveHint=True)`
   - Updated logging to show annotation hints

2. Added 3 new tests to `tests/test_server.py`:
   - `test_read_tools_have_readonly_hint()` - verifies all 10 read tools have readOnlyHint=True
   - `test_write_tools_have_destructive_hint()` - verifies all 4 write tools have destructiveHint=True
   - `test_all_tools_have_annotations()` - verifies no tools are missing annotations

3. Verified all 64 tests pass (including 3 new annotation tests)

## Verification

- Ran `pytest tests/test_server.py -xvs -k "hint"` - 2 new tests pass
- Ran `pytest tests/test_server.py -xvs -k "annotations"` - 1 new test passes
- Ran full test suite: `pytest tests/test_server.py -xvs` - all 64 tests pass
- Verified runtime logs show annotation hints when tools are registered

## Diagnostics

- Runtime logs at INFO level show: `Registered read tool: mist_list_orgs [readOnlyHint=True]` and `Registered write tool: mist_update_wlan [destructiveHint=True]`
- MCP `tools/list` endpoint returns tool annotations in the response
- Tool annotations are `ToolAnnotations` Pydantic models (access attributes via `.readOnlyHint` not `.get()`)

## Deviations

None - followed the task plan exactly. Note: The initial approach using `mcp.add_tool(func, annotations={...})` failed because FastMCP 3.1.1's `add_tool()` doesn't accept an annotations parameter directly. Solution was to use `Tool.from_function()` to create a tool with annotations first.

## Known Issues

None

## Files Created/Modified

- `mist_mcp/server.py` — Added Tool and ToolAnnotations imports, updated register_tools() to use Tool.from_function() with annotations
- `tests/test_server.py` — Added 3 new annotation verification tests
