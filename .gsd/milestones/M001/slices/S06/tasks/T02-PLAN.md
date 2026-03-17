---
estimated_steps: 6
estimated_files: 2
---

# T02: Create comprehensive MSP deployment documentation

**Slice:** S06 — Testing & validation
**Milestone:** M001

## Description

Create MSP deployment documentation that fulfills R014, covering multi-org .env structure, region mapping, safety flag usage, and centralized vs local deployment patterns. The documentation will serve as the primary guide for MSP operators deploying the Juniper Mist MCP server in production.

## Steps

1. Create `docs/` directory if it doesn't exist.
2. Write `docs/msp-deployment.md` with the following sections:
   - **Overview**: Purpose of the server, target audience (MSP engineers), key capabilities.
   - **Installation**: Instructions for installing from source (`pip install -e .`).
   - **Configuration**: Detailed explanation of `.env` file format, naming convention (`MIST_TOKEN_<ORGNAME>`, `MIST_REGION_<ORGNAME>`), supported regional endpoints (api.mist.com, api.eu.mist.com, etc.), example configurations for multiple organizations.
   - **Safety Features**: Explanation of four-layer safety model: read‑only default, `--enable‑write‑tools` flag, MCP annotations (readOnlyHint/destructiveHint), pre‑flight platform validation. Show how to enable write tools and what precautions are in place.
   - **Deployment Modes**:
     - **Stdio mode** (Claude Desktop): Running the server as a local MCP server, configuring Claude Desktop to connect.
     - **HTTP mode** (centralized SaaS): Running as a streamable HTTP server with `--transport=http`, binding to host/port, potential use behind reverse proxy.
   - **Running the Server**: Example commands for both modes, including all CLI flags (`--enable-write-tools`, `--transport`, `--host`, `--port`, `--env-file`).
   - **Verification**: How to verify the server is working (`mist_list_orgs` tool), running the test suite (`pytest`), using verification scripts (`verify_s05.sh`, `verify_s06.sh`).
   - **Troubleshooting**: Common errors (missing .env, invalid token, unknown region) and solutions.
   - **References**: Links to Mist API documentation, FastMCP, and project repository.
3. Ensure the documentation is clear, concise, and uses code blocks for examples.
4. Verify that all required sections are present and accurate by reviewing against `.env.example` and `server.py` argument parser.
5. Optionally create a simple README.md in project root that links to the detailed documentation.
6. Run a quick spell check and formatting check.

## Must-Haves

- [ ] `docs/msp-deployment.md` exists with all required sections.
- [ ] Documentation accurately reflects the current .env format and CLI flags.
- [ ] Documentation includes examples for both stdio and HTTP deployment.
- [ ] Documentation explains safety features and how to enable write tools.

## Verification

- Check that `docs/msp-deployment.md` exists and contains each required section (Overview, Installation, Configuration, Safety Features, Deployment Modes, Running the Server, Verification, Troubleshooting).
- Validate that the content matches the actual implementation (e.g., region list matches .env.example, CLI flags match parse_args).
- No placeholder text remains.

## Observability Impact

- No runtime observability changes; this is documentation.

## Inputs

- `.env.example` — example configuration format.
- `mist_mcp/server.py` — CLI argument definitions and safety layer implementation.
- `mist_mcp/config.py` — region handling and validation.
- `scripts/verify_s05.sh` — example verification pattern.

## Expected Output

- `docs/msp-deployment.md` ready for MSP operators.
- Improved discoverability and deployability of the server.