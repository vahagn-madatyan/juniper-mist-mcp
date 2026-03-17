# S06: Testing & validation — UAT

**Milestone:** M001
**Written:** 2026-03-16

## UAT Type

- UAT mode: artifact-driven (testing & documentation)
- Why this mode is sufficient: This slice focuses on behavioral tests for edge cases (rate limit, errors) and external documentation. No new operational features were added that require live runtime testing beyond this slice's 22 new unit tests.

## Preconditions

- juniper-mist-mcp repo checked out.
- `pip install .` or `pip install -e .` (editable mode).
- No API tokens required for unit testing.

## Smoke Test

Confirm that the new rate limit behavioral tests pass:
`pytest tests/test_rate_limit.py -v`

## Test Cases

### 1. Behavioral Error Handling (Rate Limit)

1. Open `tests/test_rate_limit.py`.
2. Locate `test_rate_limit_429_response`.
3. Observe how a mock 429 response is created and passed to `serialize_api_response`.
4. Run the test: `pytest tests/test_rate_limit.py -k test_rate_limit_429_response`
5. **Expected:** `serialize_api_response` returns a dict with `status_code=429` and `error=True`.

### 2. Success Tracking (Pagination)

1. Open `tests/test_rate_limit.py`.
2. Locate `test_success_tracking_with_pagination`.
3. Observe how a mock response with a `next` property is created.
4. Run the test: `pytest tests/test_rate_limit.py -k test_success_tracking_with_pagination`
5. **Expected:** `serialize_api_response` returns a dict with `has_more=True` and `next_page` URL.

### 3. Documentation Audit

1. Open `docs/msp-deployment.md`.
2. Check for the following sections:
    - Configuration (must show MIST_TOKEN_* pattern)
    - Safety Features (must mention --enable-write-tools)
    - Running the Server (must mention stdio and HTTP transports)
3. **Expected:** All production deployment requirements are clearly outlined.

### 4. Regression Check

1. Run the full test suite: `pytest tests/`
2. **Expected:** 103 passed tests.

## Edge Cases

### Unknown/Missing Status Code

1. Locate `test_edge_case_status_code_none` in `tests/test_rate_limit.py`.
2. Run the test: `pytest tests/test_rate_limit.py -k test_edge_case_status_code_none`
3. **Expected:** `serialize_api_response` defaults to `status_code=0` and `error=True`.

## Failure Signals

- `pytest` failures in `tests/test_rate_limit.py` (indicates regression in response handling logic).
- Missing sections or incorrect CLI flags in `docs/msp-deployment.md` (indicates poor documentation quality).
- `scripts/verify_s06.sh` returning exit code 1.

## Requirements Proved By This UAT

- R013 (Rate Limit Testing) — Proved by tests in cases 1 and 4.
- R014 (MSP Documentation) — Proved by case 3.

## Not Proven By This UAT

- Full live runtime behavior with real Mist rate limits (requires physical/sandbox environment).
- Actual LLM interaction via Claude Desktop (requires manual user test).

## Notes for Tester

None. This is a verification-heavy slice ensuring production readiness. Ensure `pytest` is installed in your environment before running tests.
