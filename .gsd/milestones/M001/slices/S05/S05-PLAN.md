# S05: Safety layers & multi-tenancy

**Goal:** Implement four-layer safety model (R008-R011) for the Juniper Mist MCP server. Write tools disabled by default, require explicit enable flag, include destructive hints, and have platform validation.

**Demo:** Start server without `--enable-write-tools` flag → only 10 read/config tools registered. Start with flag → all 14 tools registered, write tools have `destructiveHint=True`, read tools have `readOnlyHint=True`. Validation errors caught before API calls.

## Must-Haves

- Write tools are NOT registered by default (R008)
- Write tools ARE registered when `--enable-write-tools` flag is set (R009)
- Read tools have `readOnlyHint=True` annotation (R010)
- Write tools have `destructiveHint=True` annotation (R010)
- Write operations perform basic platform validation before submission (R011)
- All existing tests pass with new registration pattern

## Proof Level

- This slice proves: integration
- Real runtime required: yes
- Human/UAT required: no

## Verification

- `bash scripts/verify_s05.sh` (new script) that:
  1. Starts server without flag, checks only 10 tools registered (no write tools)
  2. Starts server with flag, checks all 14 tools registered
  3. Verifies read tools have `readOnlyHint=True`
  4. Verifies write tools have `destructiveHint=True` (when enabled)
  5. Runs pytest test suite for safety layers (new tests)
- `pytest tests/test_server.py -xvs` passes all tests (including new safety tests)
- **Diagnostic check:** Run server and inspect logs for annotation hints (e.g., `Registered write tool: mist_update_wlan [destructiveHint=True]`) - this verifies the observability signal works

## Observability / Diagnostics

- Runtime signals: Server logs which tools are registered at startup (INFO level)
- Inspection surfaces: MCP `tools/list` endpoint reveals tool annotations
- Failure visibility: `ValueError` raised for missing parameters, logged with tool name
- Redaction constraints: none (tool names and annotations are not sensitive)
- **Diagnostic check:** Run server and inspect logs for annotation hints (e.g., `Registered write tool: mist_update_wlan [destructiveHint=True]`)

## Integration Closure

- Upstream surfaces consumed: write tools from S04 (`mist_update_wlan`, `mist_manage_nac_rules`, `mist_manage_wxlan`, `mist_manage_security_policies`)
- New wiring introduced: `register_tools()` called from `main()` with `enable_write` flag
- What remains before the milestone is truly usable end-to-end: S06 testing & validation (rate limit awareness, deployment guide)

## Tasks

- [x] **T01: Refactor tool registration to manual pattern** `est:45m`
  - Why: Remove `@mcp.tool` decorators and implement manual registration via `mcp.add_tool()` to allow conditional registration. This is the foundation for safety layers.
  - Files: `mist_mcp/server.py`, `tests/test_server.py`, `scripts/verify_s04.sh`
  - Do: Remove all 14 `@mcp.tool` decorators. Define a `register_tools(enable_write: bool)` function that registers all tools manually. Keep the `mcp` instance global but don't call `register_tools` yet (all tools still registered). Update tests that rely on tool registration to call `register_tools(enable_write=True)` before checking. Update `scripts/verify_s04.sh` to call `register_tools(enable_write=True)` before checking tool list.
  - Verify: `pytest tests/test_server.py -xvs` passes all existing tests; `bash scripts/verify_s04.sh` passes.
  - Done when: All 61 existing tests pass with the new manual registration pattern, and S04 verification script still works.

- [x] **T02: Add annotation hints (readOnlyHint/destructiveHint)** `est:30m`
  - Why: Fulfill R010: tools that could disrupt network connectivity or security must include `destructiveHint=True`, triggering LLM permission dialog.
  - Files: `mist_mcp/server.py`, `tests/test_server.py`
  - Do: In `register_tools`, add `annotations={"readOnlyHint": True}` for 10 read tools (tier1 and tier2). Add `annotations={"destructiveHint": True}` for 4 write tools (tier3). Ensure annotations are passed to `mcp.add_tool()`.
  - Verify: Write a test that checks tool annotations exist. Run `pytest tests/test_server.py -xvs` to confirm tests still pass.
  - Done when: All tools have appropriate annotations, and a new test verifies annotations are present.

- [x] **T03: Implement conditional write tool registration based on flag** `est:30m`
  - Why: Fulfill R008 and R009: write tools only registered when `--enable-write-tools` flag is set.
  - Files: `mist_mcp/server.py`, `tests/test_server.py`
  - Do: Modify `register_tools` to skip write tools when `enable_write=False`. Update `main()` to call `register_tools(args.enable_write_tools)` before `mcp.run()`. Remove the warning log about write tools not yet implemented.
  - Verify: Write a test that verifies write tools are missing when `enable_write=False`. Update existing tool signature tests to conditionally check write tools.
  - Done when: Starting server without flag shows only 10 tools; with flag shows 14 tools.

- [x] **T04: Update tests for safety layers** `est:45m`
  - Why: Ensure the safety layer behavior is covered by tests and regressions are caught.
  - Files: `tests/test_server.py`, `mist_mcp/server.py`
  - Do: Add tests: `test_write_tools_not_registered_by_default()`, `test_write_tools_registered_with_flag()`, `test_read_tools_have_readonly_hint()`, `test_write_tools_have_destructive_hint()`. Update existing tool signature tests to handle conditional registration. Ensure test isolation (clear mcp tools between tests).
  - Verify: `pytest tests/test_server.py -xvs` passes all new and existing tests.
  - Done when: New safety tests pass and all tests run successfully.

- [x] **T05: Create verification script for S05** `est:30m`
  - Why: Provide a standalone verification script that demonstrates the safety layers work as required.
  - Files: `scripts/verify_s05.sh`
  - Do: Create a new script that starts the server in both modes, queries tool list via JSON-RPC, checks tool counts and annotations. Use similar pattern to `verify_s04.sh`.
  - Verify: Run `bash scripts/verify_s05.sh` and confirm it passes.
  - Done when: Verification script exits with code 0 and outputs success messages.

- [x] **T06: Add basic platform validation enhancement** `est:30m`
  - Why: Fulfill R011: write operations validate against Mist platform constraints before submission.
  - Files: `mist_mcp/server.py`, `tests/test_server.py`
  - Do: Add a `validate_platform_constraints(tool_name: str, params: dict) -> None` function that performs basic validation (e.g., check UUID format for IDs, required fields per action). Call it from each write tool before API call. Log validation warnings.
  - Verify: Write a test that invalid parameters trigger validation error. Ensure existing tests still pass.
  - Done when: Validation function is called in all write tools and logs appropriate warnings.

## Files Likely Touched

- `mist_mcp/server.py`
- `tests/test_server.py`
- `scripts/verify_s05.sh`
- `scripts/verify_s04.sh` (maybe update tool count expectation)