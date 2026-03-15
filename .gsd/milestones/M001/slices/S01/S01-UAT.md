# S01: Foundation & authentication — UAT

**Milestone:** M001
**Written:** 2026-03-15

## UAT Type

- UAT mode: artifact-driven
- Why this mode is sufficient: This slice establishes the foundation (server startup, config loading, transport setup). Full live API authentication is blocked by lack of real Mist tokens in test environment, but all code paths are verified through unit/integration tests.

## Preconditions

- Python 3.11+ installed
- Dependencies installed: `pip install -e .` or `pip install fastmcp mistapi python-dotenv tenacity`
- No .env file required (tests use .env.example)

## Smoke Test

```bash
python3 -m mist_mcp.server --help
```

Expected: Help output shows `--transport`, `--host`, `--port`, `--enable-write-tools` options.

## Test Cases

### 1. Server starts in stdio mode

1. Run `bash scripts/verify_s01.sh`
2. **Expected:** Script exits 0, prints "SUCCESS: mist_list_orgs tool found"

### 2. Configuration loading from .env file

1. Run `python3 -c "from mist_mcp.config import Config; c=Config('.env.example'); print(c.orgs)"`
2. **Expected:** Prints list of org names from .env.example

### 3. mist_list_orgs tool returns configured orgs

1. Start server in stdio mode
2. Query `mist_list_orgs` tool
3. **Expected:** Returns array of org objects with name, region, hasToken fields

### 4. CLI transport selection works

1. Run `python3 -m mist_mcp.server --transport http --port 9000`
2. **Expected:** Server starts on port 9000 (or shows appropriate message for HTTP mode)

### 5. Write tools flag shows warning

1. Run `python3 -m mist_mcp.server --enable-write-tools`
2. **Expected:** Warning message about unimplemented write tools

### 6. Invalid org returns helpful error

1. Query any tool with org="nonexistent_org"
2. **Expected:** ValueError with list of available orgs

## Edge Cases

### Missing .env file

1. Run `python3 -c "from mist_mcp.config import Config; Config('nonexistent.env')"`
2. **Expected:** FileNotFoundError with clear message

### Unknown region

1. Create .env with MIST_REGION_ORG=invalid.region
2. Load config
3. **Expected:** WARNING log about unknown region, but no crash

### Empty token value

1. Create .env with MIST_TOKEN_ORG= (empty)
2. Load config
3. **Expected:** Token treated as missing, hasToken=false in tool output

## Failure Signals

- `pytest tests/test_config.py` failures — config parsing broken
- `pytest tests/test_server.py` failures — server/tool registration broken
- `bash scripts/verify_s01.sh` non-zero exit — transport not working
- `python3 -m mist_mcp.server` crashes on startup — import/initialization error

## Requirements Proved By This UAT

- R001 — Python MCP server with FastMCP framework (server starts, tools registered)
- R002 — Mist API authentication with .env token management (config loading works)
- R003 — Multi-tenant org routing (orgs listed, validation works)
- R004 — Region-aware API client (region validation, default fallback)
- R012 — Transport: stdio + HTTP (CLI options work, verify script passes)

## Not Proven By This UAT

- Live Mist API authentication (no real tokens; tested via mocking/integration tests only)
- HTTP transport end-to-end (CLI accepts --transport http but not fully verified)
- Rate-limit retry behavior (relies on mistapi, not exercised in tests)

## Notes for Tester

- Tokens are never logged; only presence/absence is indicated
- .env file is not tracked in git (see .gitignore)
- Default region is api.mist.com when not specified
- Unknown regions are allowed but logged as warnings (forward compatibility)
