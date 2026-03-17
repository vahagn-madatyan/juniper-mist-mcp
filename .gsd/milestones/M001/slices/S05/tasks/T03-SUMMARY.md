---
id: T03
parent: S05
milestone: M001
provides:
  - Conditional write tool registration based on --enable-write-tools flag
  - Read-only mode by default (10 tools)
  - Write-enabled mode when flag set (14 tools)
  - Observability: logs show tool count at startup
key_files:
  - mist_mcp/server.py
  - tests/test_server.py
key_decisions:
  - Used FastMCP's Tool.from_function() with annotations parameter
  - Implemented reset_tool_registration() for test isolation (using subprocess)
patterns_established:
  - Manual tool registration with conditional write tool handling
  - Subprocess-based tests for clean MCP state verification
observability_surfaces:
  - Server logs show: "Tool registration complete: X read tools, Y write tools"
  - Server logs show: "Write tools disabled: 4 write tools not registered (use --enable-write-tools to enable)"
duration: 30m
verification_result: passed
completed_at: 2026-03-16
blocker_discovered: false
---

# T03: Implement conditional write tool registration based on flag

**Conditional write tool registration implemented — server is read-only by default**

## What Happened

Modified `register_tools(enable_write: bool)` to conditionally register the 4 write tools:
- When `enable_write=False` (default): only 10 read tools registered
- When `enable_write=True`: all 14 tools (10 read + 4 write) registered

Updated `main()` to pass the flag from command-line args and removed the outdated warning.

Added `reset_tool_registration()` function to enable test isolation.

Added 3 new tests using subprocess execution to verify conditional behavior:
- `test_write_tools_not_registered_by_default()` - verifies only 10 tools when flag not set
- `test_write_tools_registered_with_flag()` - verifies 14 tools when flag is set
- `test_read_tools_have_readonly_hint_with_write_disabled()` - verifies annotations still work

## Verification

Ran verification commands from task plan:
```bash
# Without flag - shows 10 tools
python3 -c "import asyncio; from mist_mcp.server import mcp, register_tools, reset_tool_registration; reset_tool_registration(); register_tools(enable_write=False); tools = asyncio.run(mcp.list_tools()); print(len(tools))"
# Output: 10

# With flag - shows 14 tools
python3 -c "import asyncio; from mist_mcp.server import mcp, register_tools, reset_tool_registration; reset_tool_registration(); register_tools(enable_write=True); tools = asyncio.run(mcp.list_tools()); print(len(tools))"
# Output: 14
```

Ran full test suite: `pytest tests/test_server.py -xvs` → **67 passed**

## Diagnostics

Runtime logs show:
- `Registered read tool: mist_list_orgs [readOnlyHint=True]`
- `Registered write tool: mist_update_wlan [destructiveHint=True]`
- `Write tools disabled: 4 write tools not registered (use --enable-write-tools to enable)`
- `Tool registration complete: 10 read tools, 0 write tools`

## Deviations

None - followed the task plan exactly.

## Known Issues

Test isolation issue resolved by running conditional tests in subprocesses (necessary because FastMCP persists tools across tests in the same session).

## Files Created/Modified

- `mist_mcp/server.py` — Modified `register_tools()` to conditionally register write tools; added `reset_tool_registration()`; updated `main()` and help text
- `tests/test_server.py` — Added 3 new tests for conditional registration using subprocess execution
