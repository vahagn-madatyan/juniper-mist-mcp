# S02: Read tools (tier1) — UAT

**Milestone:** M001
**Written:** 2026-03-15

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: Tier1 tools are read-only and can be verified via unit tests that confirm proper tool registration, parameter validation, and response serialization. Live API verification would require real Mist credentials and orgs with active devices.

## Preconditions

- Python 3.11+ with mist_mcp package installed
- Test environment: pytest configured and running
- Optional: Mist API token in .env for live verification

## Smoke Test

```bash
pytest tests/test_server.py::test_tier1_tools_registered -v
```

Expected: PASSED — confirms all 5 tier1 tools are registered in MCP server.

## Test Cases

### 1. Tool Registration

1. Run: `pytest tests/test_server.py::test_tier1_tools_registered -v`
2. **Expected:** PASSED — lists all 5 tools: mist_get_device_stats, mist_get_sle_summary, mist_get_client_stats, mist_get_alarms, mist_get_site_events

### 2. Org Validation - Invalid Org

1. Run: `pytest tests/test_server.py::test_device_stats_invalid_org -v`
2. **Expected:** PASSED — ValueError raised for invalid org

### 3. Org Validation - Valid Org

1. Run: `pytest tests/test_server.py::test_device_stats_valid_org -v`
2. **Expected:** PASSED — No exception raised for valid org

### 4. Response Serialization

1. Run: `pytest tests/test_server.py::test_serialize_api_response -v`
2. **Expected:** PASSED — APIResponse correctly serialized to dict with status_code, error, data, has_more

### 5. Full Test Suite

1. Run: `pytest tests/test_server.py -v`
2. **Expected:** All 24 tests pass

### 6. End-to-End Verification

1. Run: `bash scripts/verify_s02.sh`
2. **Expected:** Exit code 0 with "VERIFICATION PASSED" message

## Edge Cases

### Invalid Organization Name

1. Run any tier1 tool with org="nonexistent_org"
2. **Expected:** ValueError with message about available organizations

### API Response with Error

1. Run: `pytest tests/test_server.py::test_serialize_api_response_error -v`
2. **Expected:** PASSED — Error responses correctly serialized

### Pagination

1. Run: `pytest tests/test_server.py::test_serialize_api_response_with_pagination -v`
2. **Expected:** PASSED — has_more field correctly set

## Failure Signals

- Test failures indicate broken tool registration or parameter validation
- verify_s02.sh exiting non-zero indicates incomplete slice
- Import errors for mistapi indicate missing dependency

## Requirements Proved By This UAT

- R005 — Tier1 read tools verified through test suite

## Not Proven By This UAT

- Live API calls with real Mist credentials (requires configured .env with valid tokens)
- Rate limit handling under load (S06 will add behavioral tests)
- Write tools (not in scope for S02)

## Notes for Tester

- Tests use mock responses for API calls — actual data retrieval requires live Mist API tokens
- All tools require `org` parameter — this is validated before any API call
- The verify_s02.sh script runs comprehensive checks including tool registration and full test suite
