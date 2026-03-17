# S06: Testing & validation — Research

**Date:** 2026-03-16

## Summary

Slice S06 is the final integration slice for M001, responsible for two key deliverables: **R013** (behavioral tests for rate limit handling and success tracking) and **R014** (MSP deployment documentation). The codebase is mature with 71 existing pytest tests covering tool registration, safety layers, and parameter validation. What's missing is documentation and behavioral verification of rate limit handling.

The Mist API has a documented rate limit of 5,000 requests/hour per token (per D012), and the mistapi SDK provides built-in retry logic with 3 retries and exponential backoff. This slice should verify this behavior works correctly and document the complete MSP deployment workflow.

## Recommendation

Implement S06 as two parallel tracks:

1. **Testing track**: Create behavioral tests that verify rate limit handling by mocking the mistapi response with 429 status codes and confirming retry behavior. Add tests for success tracking (metrics/logging) and error propagation. Build on the existing test patterns in `test_server.py` and `test_config.py`.

2. **Documentation track**: Create comprehensive MSP deployment documentation covering multi-org .env configuration, region mapping, safety flag usage, and deployment patterns (stdio for Claude Desktop, HTTP for centralized SaaS).

The slice is straightforward - no new technology or risky integration. It applies known pytest patterns to verify existing SDK behavior and writes documentation for existing functionality.

## Implementation Landscape

### Key Files

- `tests/test_server.py` — 71 existing tests covering tool registration, safety layers, parameter validation; uses pytest with asyncio support
- `tests/test_config.py` — Config loading tests with tempfile-based .env mocking
- `mist_mcp/server.py` — Main server with `serialize_api_response()` and all tool implementations
- `mist_mcp/session.py` — `MistSessionManager` with mistapi session caching; uses SDK's built-in retry
- `mist_mcp/config.py` — `Config` and `OrgConfig` classes for .env parsing
- `scripts/verify_s05.sh` — Bash verification script pattern to follow for S06 verification
- `.env.example` — Example configuration to reference in documentation

### Build Order

1. **Create rate limit behavioral tests first** — These validate R013 and establish confidence in the retry mechanism. Mock `mistapi.APIResponse` with status=429 and verify SDK retry is triggered.

2. **Create success tracking tests** — Verify that `serialize_api_response()` correctly captures status codes, error flags, and pagination metadata across all response types.

3. **Create comprehensive deployment documentation** — Document multi-org .env setup, region mapping, safety flags, stdio vs HTTP deployment. This fulfills R014.

4. **Create end-to-end verification script** — Similar to `verify_s05.sh`, create `verify_s06.sh` that runs behavioral tests and validates documentation exists.

### Verification Approach

- **Rate limit tests**: Mock `__api_response.APIResponse` with status_code=429, verify mistapi's built-in retry is invoked (may need to mock at session level)
- **Success tracking tests**: Verify `serialize_api_response()` returns expected structure with `status_code`, `error`, `data`, `has_more`, `next_page` fields
- **Error handling tests**: Verify 4xx/5xx responses are properly serialized with `error=True` and error data preserved
- **Documentation verification**: Check `docs/` directory exists with `msp-deployment.md` covering all R014 requirements
- **Integration**: Run `pytest tests/test_rate_limit.py -v` and `bash scripts/verify_s06.sh`

## Don't Hand-Roll

| Problem | Existing Solution | Why Use It |
|---------|------------------|------------|
| Rate limit retry | mistapi built-in retry (D012) | Already handles 429 with 3 retries + exponential backoff; no need for tenacity |
| API response mocking | `unittest.mock.MagicMock` with `spec=__api_response.APIResponse` | Pattern already used in `test_server.py` for `test_serialize_api_response` |
| Test structure | pytest with `pytest-asyncio` | Already configured in `pyproject.toml` |
| Temp .env files | `tempfile.NamedTemporaryFile` | Pattern established in `test_config.py` |

## Constraints

- Must use existing pytest configuration from `pyproject.toml` (`testpaths = ["tests"]`, `python_files = ["test_*.py"]`)
- Rate limit tests must mock at the SDK level, not make real API calls
- Documentation must be in Markdown format, placed in `docs/` directory
- Must follow existing bash verification script pattern from S05

## Common Pitfalls

- **Testing actual rate limits** — Don't test against live API; mock the 429 response to verify retry behavior
- **Subprocess test isolation** — For tests that verify global state (like tool registration), use subprocess pattern from S05 tests
- **Documentation drift** — Ensure documented CLI flags match actual `parse_args()` implementation in `server.py`

## Open Risks

- The mistapi SDK's retry behavior is internal; tests may need to mock at the HTTP adapter level or trust SDK documentation
- Success tracking metrics may be limited to logs and response serialization (no dedicated metrics endpoint currently)

## Skills Discovered

| Technology | Skill | Status |
|------------|-------|--------|
| pytest | test (built-in) | installed |

## Sources

- Mist API rate limits: D012 decision record — "Use mistapi's built-in retry" for 429 handling with 3 retries and exponential backoff
- Existing test patterns: `tests/test_server.py` shows subprocess-based isolation for MCP state tests, mock-based testing for API responses
- Safety layer verification: `scripts/verify_s05.sh` provides bash script template for slice verification
- Configuration patterns: `.env.example` shows multi-org configuration format to document
