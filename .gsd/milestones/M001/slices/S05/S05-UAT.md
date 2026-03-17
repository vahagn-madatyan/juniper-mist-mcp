# S05: Safety layers & multi-tenancy — UAT

**Milestone:** M001
**Written:** 2026-03-16

## UAT Type

- UAT mode: live-runtime/live-mcp-inspection
- Why this mode is sufficient: This slice implements safety layers that directly affect the tool discovery and interaction contracts in the MCP server. Verifying these requires actual runtime inspection of the available tools and their metadata.

## Preconditions

- Server installed and runnable via `python3 -m mist_mcp.server` or similar.
- Environment variables configured (MIST_TOKEN, etc.), although safety layers should work even without valid credentials during registration.

## Smoke Test

Start the server without the flag and verify exactly 10 tools are registered:
```bash
python3 -c "import asyncio; from mist_mcp.server import mcp, register_tools; register_tools(enable_write=False); tools = asyncio.run(mcp.list_tools()); print(len(tools))"
# Expected: 10
```

## Test Cases

### 1. Default Read-Only Mode (R008)

1. Run the server without the `--enable-write-tools` flag.
2. List available tools via the MCP `list_tools` command.
3. **Expected:** 10 read tools are listed. No write tools (`mist_update_wlan`, etc.) are present.

### 2. Explicit Write-Enabled Mode (R009)

1. Run the server with the `--enable-write-tools` flag.
2. List available tools via the MCP `list_tools` command.
3. **Expected:** 14 total tools are listed, including the 4 write tools.

### 3. Tool Annotations & Safety Hints (R010)

1. Start the server with the `--enable-write-tools` flag.
2. Inspect the metadata for `mist_list_orgs` and `mist_update_wlan`.
3. **Expected:** `mist_list_orgs` includes `annotations={"readOnlyHint": True}`. `mist_update_wlan` includes `annotations={"destructiveHint": True}`.

### 4. Pre-flight Platform Validation (R011)

1. Use the `mist_update_wlan` tool with an empty `wlan_id`.
2. **Expected:** Tool execution fails immediately with a `ValueError` indicating that `wlan_id` cannot be empty, before an API call is made.

### 5. UUID Format Warning (Observability)

1. Use the `mist_update_wlan` tool with a non-UUID `wlan_id` (e.g., "my-legacy-wlan").
2. **Expected:** Server logs a WARNING level message about the non-UUID format but permits the operation to proceed (as some legacy IDs or names may still work in certain Mist contexts).

## Edge Cases

### Missing Required IDs

1. Call `mist_manage_nac_rules` with `action="update"` but no `rule_id`.
2. **Expected:** `ValueError` raised during validation.

### Valid UUID Format

1. Call `mist_update_wlan` with a valid UUID (e.g., "550e8400-e29b-41d4-a716-446655440000").
2. **Expected:** Validation passes without warnings or errors.

## Failure Signals

- Any write tool appearing in the tool list when the `--enable-write-tools` flag is NOT set.
- A write tool lacking the `destructiveHint` annotation.
- A read tool lacking the `readOnlyHint` annotation.
- Empty IDs not being caught before attempting an API call.

## Requirements Proved By This UAT

- R008, R009, R010, R011 — All safety layer requirements are verified by runtime inspection and failure injection.

## Not Proven By This UAT

- Semantic data validation (e.g., if a WLAN configuration is logically consistent) is not proven here; this UAT only covers architectural and platform-level safety constraints.

## Notes for Tester

- The server will log registration and validation information at the INFO/WARNING level. These logs are authoritative for confirming the safety layers are active.
- Use `bash scripts/verify_s05.sh` for an automated execution of the core test cases above.
