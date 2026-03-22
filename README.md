# Juniper Mist MCP Server

> **⚠️ Juniper now offers an official MCP server for Mist.**
>
> Juniper has released their own MCP server at **https://mcp.ai.juniper.net/mcp/mist** with native integration for Claude Desktop.
>
> **We recommend using the official upstream server instead of this project.** See the [Juniper Mist MCP documentation](https://www.juniper.net/documentation/us/en/software/mist/mist-aiops/shared-content/topics/concept/juniper-mist-mcp-claude.html) for setup instructions.
>
> This community project remains available for use cases that require multi-org MSP routing, write tools, or HTTP transport — features not yet covered by the upstream server. However, for standard single-org monitoring and troubleshooting, the official server is the better choice going forward.

MCP server for managing Juniper Mist networks with AI assistants. Monitor, troubleshoot, and configure customer networks through natural language — built for MSPs managing multiple organizations across regions.

**Input:** Natural language via Claude Desktop (or any MCP client)
**Output:** Device stats, client data, alarms, WLAN configs, inventory, and more

```text
  AI Assistant  ──▶  MCP Server  ──▶  Juniper Mist API
  (Claude, etc.)     (multi-org       (US, EU, GC1, GC2,
                      routing)         APAC regions)
```

---

## Installation

### Option 1: Install from PyPI (recommended)

```bash
pip install juniper-mist-mcp
```

### Option 2: Install with pipx (isolated environment)

```bash
pipx install juniper-mist-mcp
```

### Verify installation

```bash
juniper-mist-mcp --help
```

---

## Setup

### 1. Get a Mist API Token

1. Log in to the Mist portal at [https://admin.mist.com](https://admin.mist.com)
2. Navigate to **Organization** → **Settings** → **API Tokens**
3. Create a new API token with appropriate scope

### 2. Configure Organizations

Create a `.env` file with your organization credentials:

```bash
# US-based org (default region)
MIST_TOKEN_acme_corp=your_token_here

# EU-based org
MIST_TOKEN_euro_client=your_token_here
MIST_REGION_euro_client=api.eu.mist.com

# Government org
MIST_TOKEN_gov_agency=your_token_here
MIST_REGION_gov_agency=api.gc1.mist.com
```

Each org needs a `MIST_TOKEN_<ORGNAME>` variable. Region is optional — defaults to US (`api.mist.com`).

#### Supported Regions

| Region | Endpoint |
|--------|----------|
| US (default) | `api.mist.com` |
| EU | `api.eu.mist.com` |
| Government Cloud 1 | `api.gc1.mist.com` |
| Government Cloud 2 | `api.gc2.mist.com` |
| Asia Pacific | `api.ac2.mist.com` |

---

## Usage

### Run in stdio mode (Claude Desktop)

```bash
# Read-only mode (default — 10 tools)
juniper-mist-mcp

# With write tools enabled (14 tools)
juniper-mist-mcp --enable-write-tools
```

### Run in HTTP mode (centralized deployment)

```bash
# Default port 8000
juniper-mist-mcp --transport=http

# Custom host and port
juniper-mist-mcp --transport=http --host=0.0.0.0 --port=8080

# HTTP + write tools
juniper-mist-mcp --transport=http --port=8080 --enable-write-tools
```

### Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "juniper-mist": {
      "command": "juniper-mist-mcp",
      "env": {
        "MIST_TOKEN_acme_corp": "your_token_here",
        "MIST_REGION_acme_corp": "api.mist.com"
      }
    }
  }
}
```

Or if using a `.env` file alongside the install:

```json
{
  "mcpServers": {
    "juniper-mist": {
      "command": "juniper-mist-mcp",
      "args": ["--env-file", "/path/to/your/.env"]
    }
  }
}
```

### Verify it works

In your AI assistant, ask it to list organizations. The `mist_list_orgs` tool should return your configured orgs:

```json
[
  {"name": "acme_corp", "region": "api.mist.com", "has_token": true},
  {"name": "euro_client", "region": "api.eu.mist.com", "has_token": true}
]
```

---

## Available Tools

### Read Tools (always available)

| Tool | What it does |
|------|--------------|
| `mist_list_orgs` | List configured customer orgs and regions |
| `mist_get_device_stats` | AP, switch, and gateway statistics |
| `mist_get_sle_summary` | Service Level Experience metrics (throughput, latency, coverage) |
| `mist_get_client_stats` | Wireless client connection and bandwidth data |
| `mist_get_alarms` | Infrastructure, security, and Marvis AI alarms |
| `mist_get_site_events` | Config changes, user activities, system alerts |
| `mist_list_wlans` | WLAN/SSID profiles and security settings |
| `mist_get_rf_templates` | Radio frequency templates (channel, power, band) |
| `mist_get_inventory` | Device inventory with type/status/site filters |
| `mist_get_device_config_cmd` | Generated CLI config commands for a device |

### Write Tools (opt-in with `--enable-write-tools`)

| Tool | What it does |
|------|--------------|
| `mist_update_wlan` | Modify WLAN/SSID configurations |
| `mist_manage_nac_rules` | Create, update, or delete 802.1X NAC rules |
| `mist_manage_wxlan` | Manage WXLAN microsegmentation policies |
| `mist_manage_security_policies` | Create, update, or delete security policies |

Every tool takes an `org` parameter to route to the right customer org and region.

---

## Safety Model

Four layers prevent accidental network changes:

1. **Read-only by default** — write tools aren't registered unless you opt in
2. **CLI flag** — must explicitly pass `--enable-write-tools`
3. **MCP annotations** — read tools tagged `readOnlyHint`, write tools tagged `destructiveHint` so the AI asks for confirmation
4. **Pre-flight validation** — UUID format checks and required field validation before any API call

---

## CLI Reference

| Flag | Description | Default |
|------|-------------|---------|
| `--enable-write-tools` | Enable 4 write tools for network modification | Disabled |
| `--transport` | Transport protocol: `stdio` or `http` | `stdio` |
| `--host` | Host for HTTP transport | `0.0.0.0` |
| `--port` | Port for HTTP transport | `8000` |
| `--env-file` | Path to `.env` file | `.env` |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Configuration file not found: .env` | Create a `.env` file from `.env.example` |
| `Organization 'X' is not configured` | Check `MIST_TOKEN_<ORGNAME>` in your `.env` (case-sensitive) |
| `Unknown region 'X'` | Use a supported region endpoint (see table above) |
| `Failed to fetch orgs: 401` | Token is invalid or expired — regenerate in Mist portal |
| Write tools not appearing | Start server with `--enable-write-tools` flag |

---

## Contributing

### Build from source

```bash
git clone https://github.com/vahagn-madatyan/juniper-mist-mcp.git
cd juniper-mist-mcp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run from source
python -m mist_mcp.server --help
```

### Run tests

```bash
pytest tests/ -v
pytest tests/ -v --tb=short
pytest tests/test_config.py -v
```

### Project structure

```text
mist_mcp/
├── __init__.py        # Package version
├── __main__.py        # Module entry point
├── server.py          # MCP server, tool definitions, CLI
├── config.py          # .env loader, org routing, region validation
└── session.py         # Mist API session management
```

### Architecture

- **FastMCP** — MCP server framework handling tool registration, lifespan, and transport
- **mistapi SDK** — Juniper Mist Python SDK for all API calls
- **Multi-tenant routing** — each tool call includes an `org` parameter; the server maintains separate authenticated sessions per org
- **Conditional tool registration** — write tools are only registered when `--enable-write-tools` is passed, using `mcp.add_tool()` with MCP annotations

### Making a release

Releases are published to PyPI automatically via GitHub Actions when a version tag is pushed:

```bash
# Update version in pyproject.toml and mist_mcp/__init__.py
# Commit the version bump
git tag v0.2.0
git push origin v0.2.0
```

The CI pipeline builds the distribution, runs tests, publishes to TestPyPI on every push, and publishes to PyPI on tags matching `v*`.

---

## License

[Apache License 2.0](LICENSE)
