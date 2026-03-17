---
estimated_steps: 5
estimated_files: 1
---

# T05: Create verification script for S05

**Slice:** S05 — Safety layers & multi-tenancy
**Milestone:** M001

## Description

Create a standalone verification script `scripts/verify_s05.sh` that demonstrates the safety layers work as required. The script should start the server in both modes, query tool lists, verify counts and annotations.

## Steps

1. Create `scripts/verify_s05.sh` based on the pattern of `verify_s04.sh`.
2. Script should:
   - Start server without `--enable-write-tools` flag (in background), send JSON-RPC `tools/list` request, verify only 10 tools present, none are write tools.
   - Start server with `--enable-write-tools` flag, verify 14 tools present, all write tools have `destructiveHint=True`, all read tools have `readOnlyHint=True`.
   - Use Python subprocess and asyncio to query tool list (similar to verify_s04.sh).
   - Output colored success/failure messages.
3. Ensure the script exits with code 0 on success, non-zero on failure.
4. Include a check for annotation presence (readOnlyHint/destructiveHint).
5. Test the script locally to ensure it passes with the current implementation (after T03/T04).

## Must-Haves

- [ ] Script exists at `scripts/verify_s05.sh`
- [ ] Script verifies tool counts in both modes
- [ ] Script verifies annotations
- [ ] Script exits with code 0 when safety layers are correct
- [ ] Script uses similar patterns to `verify_s04.sh` for consistency

## Verification

- Run `bash scripts/verify_s05.sh` and observe it passes.
- Manually break something (e.g., temporarily remove a readOnlyHint) and ensure script fails.

## Observability Impact

- Provides a quick, automated way to confirm safety layers are operational.

## Inputs

- `scripts/verify_s04.sh` as template.
- `mist_mcp/server.py` with safety layers implemented.

## Expected Output

- New verification script `scripts/verify_s05.sh` that passes when run.