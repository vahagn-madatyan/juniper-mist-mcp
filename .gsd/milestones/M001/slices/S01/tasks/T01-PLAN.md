---
estimated_steps: 8
estimated_files: 5
---

# T01: Project setup and config loading

**Slice:** S01 — Foundation & authentication
**Milestone:** M001

## Description

Set up Python project structure with FastMCP and mistapi dependencies. Implement configuration loading from `.env` file using prefix‑based naming (`MIST_TOKEN_<ORGNAME>`, `MIST_REGION_<ORGNAME>`). Validate region strings against known Mist cloud hosts. Write unit tests for parsing logic and edge cases.

## Steps

1. Create `pyproject.toml` with `[project]` and `[build-system]` sections; specify dependencies: `fastmcp>=2.5.1`, `mistapi`, `python-dotenv`, `tenacity`. Optionally create `requirements.txt` for compatibility.
2. Create `.env.example` with example variables for two fictional orgs, demonstrating the naming convention and all five Mist regional endpoints.
3. Create package directory `mist_mcp/` with `__init__.py`.
4. Implement `mist_mcp/config.py`: class `Config` that loads `.env` via `dotenv`, extracts orgs from `MIST_TOKEN_*` prefixes, maps each org to its token and region (default region `api.mist.com` if missing). Validate region against known hosts (`api.mist.com`, `api.eu.mist.com`, `api.gc1.mist.com`, `api.gc2.mist.com`, `api.ac2.mist.com`). Provide property `orgs` returning list of configured orgs.
5. Write unit tests in `tests/test_config.py`: test parsing with multiple orgs, missing region fallback, invalid region warning, empty .env, missing token.
6. Add logging setup in `config.py` to log loaded orgs (without tokens) and any region warnings.
7. Ensure the module can be imported and used in a REPL (test via a quick Python command).
8. Update `.gitignore` to exclude `.env` (if not already present).

## Must-Haves

- [ ] `pyproject.toml` exists with correct dependencies
- [ ] `.env.example` exists with correct format and comments
- [ ] `mist_mcp/config.py` loads orgs from `.env` and validates regions
- [ ] `tests/test_config.py` passes all test cases
- [ ] Region validation logs warning for unknown region but does not fail

## Verification

- Run `pytest tests/test_config.py` — all tests pass
- Execute `python -c "from mist_mcp.config import Config; c=Config('.env.example'); print(c.orgs); assert 'example_org' in c.orgs"` — runs without error
- Check that `.env.example` is not tracked as a secret (git status shows it as untracked)

## Observability Impact

- Signals added/changed: INFO‑level log when configuration is loaded, listing orgs (without tokens); WARNING for unknown region strings
- How a future agent inspects this: run server with `--verbose` flag (if added later) or read logs; also `mist_list_orgs` tool will expose configured orgs
- Failure state exposed: missing .env file raises `FileNotFoundError` with clear message; missing token for an org logs error and skips that org

## Inputs

- `S01-RESEARCH.md` — design decisions about .env format and region handling
- `REQUIREMENTS.md` — R002, R004 for token and region requirements

## Expected Output

- `pyproject.toml` — project definition and dependencies
- `.env.example` — example configuration file
- `mist_mcp/__init__.py` — package marker
- `mist_mcp/config.py` — configuration loader
- `tests/test_config.py` — unit tests for config parsing