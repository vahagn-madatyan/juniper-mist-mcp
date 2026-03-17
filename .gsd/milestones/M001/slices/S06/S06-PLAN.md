# S06: Testing & validation

**Goal:** All tools work with rate limit awareness; MSP deployment guide complete; behavioral tests verify success tracking.
**Demo:** Behavioral tests pass, deployment documentation exists, verification script runs successfully.

## Must-Haves

- R013: Tests verify rate limit handling (5,000 req/hour), success tracking, and appropriate error handling.
- R014: Documentation covering MSP deployment patterns: multi-org .env structure, region mapping, safety flag usage, centralized vs local deployment.

## Proof Level

- This slice proves: integration
- Real runtime required: no
- Human/UAT required: no

## Verification

- `pytest tests/test_rate_limit.py -v` passes
- `bash scripts/verify_s06.sh` passes
- `docs/msp-deployment.md` exists and contains required sections

## Tasks

- [x] **T01: Create behavioral tests for rate limit handling and success tracking** `est:60m`
  - Why: Fulfills R013 — need to verify that the server handles rate limits gracefully via mistapi's built-in retry logic and that success tracking (status codes, error flags, pagination) works correctly across all response types.
  - Files: `tests/test_rate_limit.py`, `tests/test_server.py` (optional updates)
  - Do: Create new test file with mocks for mistapi.APISession and APIResponse to simulate 429 rate limit responses, verify error serialization. Test success tracking: verify serialize_api_response handles success, error, pagination correctly. Use existing test patterns from test_server.py (subprocess isolation, MagicMock). Ensure tests cover all response fields (status_code, error, data, has_more, next_page). Mock the SDK's built-in retry behavior (or trust it) and ensure our tools don't crash.
  - Verify: Run `pytest tests/test_rate_limit.py -v` and see all tests pass.
  - Done when: All new tests pass and cover rate limit, success tracking, error handling.

- [x] **T02: Create comprehensive MSP deployment documentation** `est:45m`
  - Why: Fulfills R014 — MSPs need clear guidance on how to deploy and use the server in production, covering multi-org configuration, region mapping, safety flags, and transport modes.
  - Files: `docs/msp-deployment.md`, `.env.example` (reference)
  - Do: Create docs/ directory if missing. Write markdown documentation covering: 1) Multi-org .env structure (MIST_TOKEN_*, MIST_REGION_*), 2) Region mapping (5 Mist regions, custom hosts), 3) Safety flag usage (--enable-write-tools, read-only default), 4) Deployment patterns (stdio for Claude Desktop, HTTP for centralized SaaS), 5) Example commands and verification steps. Reference existing .env.example and command-line flags from server.py.
  - Verify: Check that `docs/msp-deployment.md` exists and contains all required sections.
  - Done when: Documentation is complete and ready for MSP operators.

- [x] **T03: Create slice verification script** `est:30m`
  - Why: Ensure the slice's deliverables (tests, documentation) are automatically verifiable, following the pattern established in S05.
  - Files: `scripts/verify_s06.sh`
  - Do: Create bash script that runs the new rate limit tests, checks for deployment documentation existence, and validates that the documentation includes key sections. Use colors and clear pass/fail output like verify_s05.sh. Optionally run a subset of existing tests to ensure no regression.
  - Verify: Run `bash scripts/verify_s06.sh` and see all checks pass.
  - Done when: Verification script passes on current codebase.

## Files Likely Touched

- `tests/test_rate_limit.py`
- `docs/msp-deployment.md`
- `scripts/verify_s06.sh`
- `tests/test_server.py` (optional updates)
- `mist_mcp/server.py` (optional updates to improve error handling)

## Observability / Diagnostics

For this slice, observability is focused on **test verification signals** rather than runtime diagnostics:

- **Test Coverage Signals**: The rate limit tests verify that serialize_api_response correctly handles:
  - 429 responses with `error=True` and preserved error data
  - 5xx errors with proper error flagging
  - Pagination metadata (`has_more`, `next_page`)
  
- **Diagnostic Failures**: When tests fail, pytest provides:
  - Explicit assertion failures with expected vs actual values
  - Clear test names describing what failed (e.g., `test_rate_limit_429_response`)
  - Verbose output via `-v` flag showing test class and method names

- **No Runtime Changes**: This slice adds unit tests only; no runtime observability changes required (tests verify existing serialize_api_response behavior).

## Verification Summary

| Check | Status |
|-------|--------|
| pytest tests/test_rate_limit.py -v | ✓ PASS (22 tests) |
| pytest tests/ (no regression) | ✓ PASS (103 tests) |
| docs/msp-deployment.md exists | ✓ PASS |
| scripts/verify_s06.sh passes | ✓ PASS |