# S05: Safety layers & multi-tenancy — Research

**Date:** 2026-03-16

## Summary

Slice S05 implements the four-layer safety model (R008-R011) for the Juniper Mist MCP server. The write tools from S04 are currently **always registered** but the `--enable-write-tools` flag only logs a warning. This slice must make write tools conditionally registered based on the flag and add MCP annotations for destructive/read-only hints.

The key implementation involves restructuring tool registration from decorator-based (static) to manual registration (dynamic) so that write tools are only added when `--enable-write-tools` is passed. FastMCP supports this via `mcp.add_tool()` for manual registration and the `annotations` parameter for hint metadata.

## Recommendation

**Approach:** Convert from decorator-based tool registration to manual registration pattern.

1. Remove `@mcp.tool` decorators from all tool functions
2. Define tool functions as regular async functions with proper type hints and docstrings
3. Create a `register_tools(enable_write: bool)` function that:
   - Always registers read tools (tier1 + tier2) with `annotations={"readOnlyHint": True}`
   - Conditionally registers write tools (tier3) with `annotations={"destructiveHint": True}` only if `enable_write=True`
4. Call `register_tools()` in `main()` after parsing args

**Why:** FastMCP's `@mcp.tool` decorator registers tools at import time, but we need runtime conditional registration based on CLI flags. Manual registration via `mcp.add_tool()` gives us full control over which tools are exposed.

## Implementation Landscape

### Key Files

- `mist_mcp/server.py` — Contains all tool definitions (10 read + 4 write). Must be refactored to:
  - Remove `@mcp.tool` decorators from the 14 tool functions
  - Add `annotations={"readOnlyHint": True}` to 10 read tools on registration
  - Add `annotations={"destructiveHint": True}` to 4 write tools on registration
  - Add `register_tools(enable_write: bool)` function called from `main()`
  - Update `--enable-write-tools` flag handling to actually control registration

- `tests/test_server.py` — Contains 24 tests for write tools. Must be updated to:
  - Test that write tools are NOT registered when flag is False
  - Test that write tools ARE registered when flag is True
  - Maintain existing tests for write tool functionality when enabled
  - Add tests for `readOnlyHint` and `destructiveHint` annotations

- `scripts/verify_s05.sh` — New verification script needed to:
  - Start server without `--enable-write-tools` and verify only 10 tools registered
  - Start server with `--enable-write-tools` and verify all 14 tools registered
  - Check tool annotations are properly set

### Build Order

1. **Refactor tool registration first** — Unblock all downstream work
   - Convert `@mcp.tool` decorators to `mcp.add_tool()` calls
   - Add `register_tools(enable_write: bool)` function
   - Verify existing tests still pass

2. **Add annotation hints** — Quick win, high value
   - `readOnlyHint=True` for read tools
   - `destructiveHint=True` for write tools

3. **Implement conditional write tool registration** — Core requirement
   - Wire `--enable-write-tools` flag to actually control registration
   - Update tests to verify conditional behavior

4. **Platform validation enhancement** (R011) — Future-proofing
   - Add basic validation that checks required fields before API calls
   - Leverage mistapi SDK validation where available

5. **Verification script** — Prove it works
   - Create `verify_s05.sh` demonstrating safety layers

### Verification Approach

1. **Unit tests**: Update existing tests to verify:
   - `test_write_tools_not_registered_by_default()` — confirm only 10 tools without flag
   - `test_write_tools_registered_with_flag()` — confirm 14 tools with flag
   - `test_read_tools_have_readonly_hint()` — verify annotation presence
   - `test_write_tools_have_destructive_hint()` — verify annotation presence

2. **Integration verification**: Run `scripts/verify_s05.sh` (to be created):
   ```bash
   # Test read-only mode (default)
   python -m mist_mcp --transport stdio &
   # Verify tools/list returns only 10 tools, none are write tools

   # Test write-enabled mode
   python -m mist_mcp --enable-write-tools --transport stdio &
   # Verify tools/list returns all 14 tools including write tools
   ```

3. **Behavioral verification**: Manual testing with MCP client:
   - Without flag: LLM cannot see or call write tools
   - With flag: LLM sees write tools with confirmation prompts due to destructiveHint

## Constraints

- FastMCP tool registration must happen before `mcp.run()` is called
- Tool annotations are immutable after registration (set at `add_tool()` time)
- The `mistapi` SDK handles most API-level validation; R011 is about pre-flight checks
- Backward compatibility: existing tool function signatures must not change

## Common Pitfalls

- **Import-time registration**: The `@mcp.tool` decorator runs at import time, so simply removing the decorator and not calling `add_tool()` will leave tools unregistered. Make sure to call `register_tools()` before `mcp.run()`.

- **Test isolation**: Tests that import `mcp` from server.py will get a fresh FastMCP instance, but if tests run in the same process, tool registration state may persist. Use `mcp._tools.clear()` or fresh imports in tests.

- **Annotation placement**: Annotations go to `mcp.add_tool(func, annotations={...})` not to the function decorator when using manual registration.

## Open Risks

- **Granular tool selection**: R009 mentions pattern matching like `--write-tools "mist_update_*"`. This slice implements the basic on/off switch; pattern matching can be added later if needed.

- **Runtime tool toggling**: Current design registers tools at startup. Dynamic enabling/disabling without restart would require more complex machinery; out of scope for this slice.

## Sources

- FastMCP manual tool registration and annotations (source: [FastMCP Documentation](https://github.com/prefecthq/fastmcp/blob/main/docs/servers/tools.mdx))
- MCP protocol annotations for destructive/read-only hints (source: [FastMCP Integration Guide](https://github.com/prefecthq/fastmcp/blob/main/docs/integrations/chatgpt.mdx))
