# S01: Foundation & authentication

**Goal:** Build a working Python MCP server that authenticates to Mist API, loads multi-tenant configuration, and provides basic tooling.
**Demo:** Server starts, authenticates to Mist API with .env tokens, lists available orgs, supports both stdio and streamable HTTP transports.

## Must-Haves

- FastMCP server (≥2.5.1) with proper tool registration and lifecycle management (R001)
- Mist API authentication using static API tokens stored in .env file format (R002)
- Multi-tenant org routing: each tool accepts `org` parameter and routes to appropriate token/region (R003)
- Region-aware API client supporting all five Mist regional endpoints (R004)
- Support for both stdio (local) and streamable HTTP (centralized) transports (R012)
- At least one read-only tool (`mist_list_orgs`) that returns configured customer organizations
- Graceful error handling for missing/invalid orgs, tokens, or regions
- Rate-limit-aware retry logic (using tenacity) for 429 responses

## Proof Level

- This slice proves: **integration** (real Mist API authentication, config loading, transport setup)
- Real runtime required: **yes** (server must start and respond to tool calls; authentication must succeed with valid tokens)
- Human/UAT required: **no** (automated verification suffices)

## Verification

- `pytest tests/test_config.py` — unit tests for .env parsing, region validation, org mapping
- `pytest tests/test_server.py` — integration test that starts server and verifies `mist_list_orgs` tool is registered
- `bash scripts/verify_s01.sh` — end-to-end verification: starts server in stdio mode, sends list tools request, confirms `mist_list_orgs` appears (using `mcp-cli` or similar)
- Manual check: `python -m mist_mcp.server --help` shows transport options and `--enable-write-tools` flag (stub)

## Observability / Diagnostics

- Runtime signals: structured logging (INFO level) for org validation, authentication success/failure, rate limit retries
- Inspection surfaces: `mist_list_orgs` tool returns current configuration (org names, regions) for debugging
- Failure visibility: clear error messages in tool responses when org not found, token missing, or region invalid; logged exceptions with context
- Redaction constraints: tokens never logged; only token presence/absence indicated

## Integration Closure

- Upstream surfaces consumed: none (green‑field)
- New wiring introduced in this slice: entrypoint `mist_mcp/server.py`, configuration loader `mist_mcp/config.py`, session manager `mist_mcp/session.py`
- What remains before the milestone is truly usable end-to-end: all other slices (S02–S06) must add remaining tools, safety layers, and deployment documentation

## Tasks

- [x] **T01: Project setup and config loading** `est:1h`
  - Why: Establish the Python project structure, install dependencies, implement configuration loading from .env, and write unit tests for parsing logic.
  - Files: `pyproject.toml`, `.env.example`, `mist_mcp/config.py`, `tests/test_config.py`, `requirements.txt` (optional)
  - Do: Create pyproject.toml with fastmcp≥2.5.1, mistapi, python‑dotenv, tenacity; write Config class that reads .env variables with prefixes MIST_TOKEN_* and MIST_REGION_*; validate region strings against known Mist cloud hosts; implement org mapping; write pytest unit tests for all parsing edge cases.
  - Verify: `pytest tests/test_config.py` passes; `.env.example` exists with correct format; `python -c "from mist_mcp.config import Config; c=Config('.env.example'); print(c.orgs)"` runs without error.
  - Done when: Configuration can be loaded from a .env file, orgs are correctly enumerated, and region validation works.
- [x] **T02: MCP server with org routing and transport support** `est:1.5h`
  - Why: Implement the actual MCP server that uses the configuration, authenticates to Mist API, registers the `mist_list_orgs` tool, and supports both stdio and HTTP transports.
  - Files: `mist_mcp/server.py`, `mist_mcp/session.py`, `mist_mcp/__init__.py`, `tests/test_server.py`, `scripts/verify_s01.sh`
  - Do: Create FastMCP server with lifespan context that loads Config and caches mistapi.APISession per org; register `mist_list_orgs` tool that returns configured orgs; add `org` parameter validation; add tenacity retry decorator for rate‑limit (429) responses; implement CLI argument parsing for `--enable-write-tools` (stub) and transport selection (stdio/http); write integration test that starts server and checks tool registration; write verification script that uses mcp‑cli (or raw JSON‑RPC) to verify the server responds.
  - Verify: `pytest tests/test_server.py` passes; `python -m mist_mcp.server --help` shows transport options; `bash scripts/verify_s01.sh` succeeds (server starts, tool list includes `mist_list_orgs`).
  - Done when: Server can be started in stdio mode, lists available orgs via the tool, and supports both transport modes (HTTP transport requires a separate test but is configurable).

## Files Likely Touched

- `pyproject.toml`
- `.env.example`
- `mist_mcp/__init__.py`
- `mist_mcp/config.py`
- `mist_mcp/session.py`
- `mist_mcp/server.py`
- `tests/test_config.py`
- `tests/test_server.py`
- `scripts/verify_s01.sh`