---
id: S05
parent: M001
milestone: M001
provides:
  - Four-layer safety model for Juniper Mist MCP server
  - Read-only default mode (10 tools)
  - Explicit opt-in for write tools via --enable-write-tools flag (14 tools)
  - MCP tool annotations (readOnlyHint=True for read tools, destructiveHint=True for write tools)
  - Pre-flight platform validation for write operations (UUID format checks)
requires:
  - slice: S04
    provides: Tier3 write tools (mist_update_wlan, mist_manage_nac_rules, etc.)
affects:
  - S06
key_files:
  - mist_mcp/server.py
  - tests/test_server.py
  - scripts/verify_s05.sh
key_decisions:
  - Refactored from @mcp.tool decorators to manual registration using mcp.add_tool() and Tool.from_function() to enable conditional logic and annotations.
  - Implemented subprocess-based tests to ensure complete MCP state isolation when verifying conditional tool registration.
  - Used regex for UUID validation in pre-flight checks, logging warnings for non-UUID strings to allow for flexibility while providing a safety signal.
patterns_established:
  - Manual tool registration with conditional branches for capability-based access control.
  - Use of MCP annotations (readOnlyHint/destructiveHint) to communicate risk to the LLM and trigger client-side guardrails.
  - Pre-flight "validate_platform_constraints" pattern to catch common errors before API submission.
observability_surfaces:
  - Server logs detailed registration status at startup (tool counts and hints).
  - MCP tools/list endpoint reveals annotations to connected clients.
  - Validation warnings logged at WARNING level for suspicious but permitted parameters.
drill_down_paths:
  - .gsd/milestones/M001/slices/S05/tasks/T01-SUMMARY.md
  - .gsd/milestones/M001/slices/S05/tasks/T02-SUMMARY.md
  - .gsd/milestones/M001/slices/S05/tasks/T03-SUMMARY.md
  - .gsd/milestones/M001/slices/S05/tasks/T06-SUMMARY.md
duration: 140m
verification_result: passed
completed_at: 2026-03-16
---

# S05: Safety layers & multi-tenancy

**Implemented a robust four-layer safety model including read-only default operation, explicit write tool opt-in, destructive/read-only annotations, and pre-flight platform validation.**

## What Happened

This slice transformed the server from a "wide open" implementation into a production-ready MSP tool with built-in safety guardrails. 

The team refactored the tool registration system, moving away from simple decorators to a manual registration pattern. This allowed for the implementation of a conditional registration logic where the 4 high-risk "write" tools are hidden by default and only exposed if the `--enable-write-tools` flag is passed at startup. 

All tools were enriched with MCP annotations: "readOnlyHint=True" for data retrieval and "destructiveHint=True" for configuration changes. This ensures that a compatible MCP client (like Claude Desktop) can present a confirmation dialog to the user before an agent executes a destructive change.

Finally, we introduced a platform validation layer that inspects parameters (like WLAN and Rule IDs) before they reach the Mist API. This pre-flight check validates UUID formats and required fields, reducing unnecessary API traffic and catching errors before they impact the network.

## Verification

Verified through both unit tests and a specialized slice-level verification script:
- `pytest tests/test_server.py` → 71 tests passed (including safety layer and validation tests).
- `bash scripts/verify_s05.sh` → Passed all 3 verification suites (Read-only mode, Full mode, and Annotation persistence).
- Manual verification of tool counts and annotation presence in JSON-RPC responses.

## Requirements Advanced

- R008 — Validated: Write tools are not registered by default.
- R009 — Validated: Write tools require the `--enable-write-tools` flag.
- R010 — Validated: readOnlyHint and destructiveHint annotations applied to all tools.
- R011 — Validated: Platform validation active for all write operations.

## Requirements Validated

- R008, R009, R010, R011

## New Requirements Surfaced

- none

## Requirements Invalidated or Re-scoped

- none

## Deviations

- none (followed the task plan exactly)

## Known Limitations

- Platform validation currently focuses on UUID format and presence; it doesn't yet check for complex semantic conflicts (e.g., overlapping IP ranges) which are left for the Mist API to enforce.

## Follow-ups

- none

## Files Created/Modified

- `mist_mcp/server.py` — Refactored registration, added annotations and platform validation.
- `tests/test_server.py` — Added safety and validation test suite with clean state fixtures.
- `scripts/verify_s05.sh` — New automated verification script for safety layers.
- `scripts/verify_s04.sh` — Updated tool count expectations to handle conditional registration.

## Forward Intelligence

### What the next slice should know
- The server is now read-only by default. When testing in S06, you must pass `--enable-write-tools` to verify the full toolset.
- `register_tools()` must be called before `mcp.run()` in `main()`.

### What's fragile
- Test isolation: FastMCP caches tools in the global instance. We added a `reset_tools()` helper, but for 100% clean state testing, continue using the subprocess pattern established in `test_server.py`.

### Authoritative diagnostics
- `bash scripts/verify_s05.sh` is the most reliable way to confirm the safety layers are active and correctly configured.
