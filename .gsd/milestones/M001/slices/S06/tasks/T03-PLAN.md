---
estimated_steps: 5
estimated_files: 1
---

# T03: Create slice verification script

**Slice:** S06 — Testing & validation
**Milestone:** M001

## Description

Create a verification script `scripts/verify_s06.sh` that automatically validates the slice deliverables: behavioral tests pass and deployment documentation exists. The script follows the same pattern as `verify_s05.sh` (colored output, clear pass/fail) and ensures the slice meets its verification criteria.

## Steps

1. Examine `scripts/verify_s05.sh` to understand the pattern: colored output, Python subprocess for checking tool counts, pytest integration, and clear summary.
2. Create `scripts/verify_s06.sh` with:
   - Shebang and set -e, color definitions.
   - Section 1: "Test 1 – Rate limit behavioral tests" that runs `pytest tests/test_rate_limit.py -v` and captures exit code.
   - Section 2: "Test 2 – Documentation existence" that checks if `docs/msp-deployment.md` exists and contains required sections (e.g., "Configuration", "Safety Features", "Deployment Modes") using grep.
   - Section 3: "Test 3 – Success tracking tests" (optional) could run a subset of existing serialize_api_response tests to ensure no regression.
   - Summary section that prints overall pass/fail and exits with appropriate code.
3. Make the script executable (`chmod +x scripts/verify_s06.sh`).
4. Run the script to verify it works (should pass if T01 and T02 are complete).
5. Add a note in the script that it expects the test file and documentation to be present (they will be created by previous tasks).

## Must-Haves

- [ ] `scripts/verify_s06.sh` exists and is executable.
- [ ] Script runs `pytest tests/test_rate_limit.py` and reports pass/fail.
- [ ] Script checks for existence of `docs/msp-deployment.md` and validates key sections.
- [ ] Script outputs colored pass/fail messages and exits with 0 only if all checks pass.

## Verification

- Run `bash scripts/verify_s06.sh` and observe all checks pass (assuming T01 and T02 are done).
- Run the script with missing test file or documentation to ensure it fails appropriately (optional).

## Observability Impact

- No runtime observability changes; this is a verification script.

## Inputs

- `scripts/verify_s05.sh` — pattern for colored verification scripts.
- `tests/test_rate_limit.py` — created by T01.
- `docs/msp-deployment.md` — created by T02.

## Expected Output

- `scripts/verify_s06.sh` that can be used to verify the slice deliverables.
- Automated validation of R013 and R014.