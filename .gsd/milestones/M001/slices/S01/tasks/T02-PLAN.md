---
estimated_steps: 10
estimated_files: 6
---

# T02: MCP server with org routing and transport support

**Slice:** S01 — Foundation & authentication
**Milestone:** M001

## Description

Implement the MCP server using FastMCP, with lifespan context that loads configuration and caches authenticated Mist API sessions per org. Register the `mist_list_orgs` tool that returns configured customer organizations. Add `org` parameter validation, rate‑limit retry logic, and support for both stdio and streamable HTTP transports via CLI arguments.

## Steps

1. Create `mist_mcp/session.py`: class `MistSessionManager` that uses `mistapi.APISession` (or `mistapi.api.APISession`). Accept org config (token, region) and create session with `host` and `apitoken`. Cache sessions per org. Add `tenacity` retry decorator for `mistapi.exceptions.APIError` with status 429 (rate limit). Provide method `get_session(org)` returning cached session or raising `ValueError` if org not configured.
2. Create `mist_mcp/server.py`: FastMCP server with `lifespan` context that loads `Config` and creates `MistSessionManager`. Store them in context dict for tool access.
3. Register tool `mist_list_orgs` with description "List configured customer organizations and their Mist regions." Tool returns list of dicts with org name, region, token present (bool). Use `@mcp.tool` decorator.
4. Add `org` parameter validation helper: given org string, ensure it exists in config; if not, raise clear error with available orgs.
5. Implement CLI argument parsing using `argparse`: add `--enable-write-tools` flag (store true, default false), `--transport` choice `stdio`/`http` (default `stdio`), `--host` and `--port` for HTTP transport. Import `fastmcp.transports` and conditionally start appropriate transport.
6. Write integration test `tests/test_server.py`: use `fastmcp.testing` or subprocess to start server in stdio mode, send JSON‑RPC `tools/list` request, verify `mist_list_orgs` appears. Mock Mist API calls (or use dummy token) to avoid real authentication.
7. Create verification script `scripts/verify_s01.sh`: starts server in background, uses `mcp-cli` (if installed) or raw `socat`/`nc` to send `initialize` and `tools/list`, greps for `mist_list_orgs`, then kills server. Provide fallback to Python script if mcp-cli not available.
8. Add logging configuration: INFO level for server start, org validation, tool calls; WARNING for rate limit retries; ERROR for authentication failures.
9. Ensure `__main__.py` entry point: `python -m mist_mcp.server` runs the server.
10. Update `pyproject.toml` with `scripts` entry point `mist-mcp = "mist_mcp.server:main"` (optional).

## Must-Haves

- [ ] `mist_mcp/session.py` caches authenticated sessions per org with rate‑limit retry
- [ ] `mist_mcp/server.py` starts FastMCP server with lifespan and registers `mist_list_orgs`
- [ ] Tool `mist_list_orgs` returns correct org list from configuration
- [ ] CLI supports `--transport stdio` (default) and `--transport http` with `--host`/`--port`
- [ ] `--enable-write-tools` flag exists (stub, does nothing yet)
- [ ] Integration test passes (tool registration verified)
- [ ] Verification script succeeds (server responds with tool list)

## Verification

- Run `pytest tests/test_server.py` — passes
- Execute `python -m mist_mcp.server --help` — shows transport and enable‑write‑tools options
- Run `bash scripts/verify_s01.sh` — exits with code 0 and prints success
- Manual test: start server with `python -m mist_mcp.server --transport stdio` and send JSON‑RPC request (using `mcp-cli` or similar) — `mist_list_orgs` appears in tool list

## Observability Impact

- Signals added/changed: INFO logs for server start, org validation, tool calls; WARNING logs for rate limit retries; ERROR logs for authentication failures (without token)
- How a future agent inspects this: logs printed to stderr (stdio) or captured by transport; `mist_list_orgs` tool reveals current config
- Failure state exposed: missing token causes clear error in tool response; invalid org returns list of available orgs; rate limit retries logged with backoff timing

## Inputs

- `mist_mcp/config.py` from T01 — configuration loader
- `S01-RESEARCH.md` — FastMCP patterns, transport setup
- `REQUIREMENTS.md` — R001, R003, R012

## Expected Output

- `mist_mcp/session.py` — session manager with caching and retry
- `mist_mcp/server.py` — main server module with CLI and transport selection
- `tests/test_server.py` — integration tests
- `scripts/verify_s01.sh` — end‑to‑end verification script
- `mist_mcp/__main__.py` (optional) — entry point for `python -m mist_mcp.server`
- Updated `pyproject.toml` with entry point (optional)