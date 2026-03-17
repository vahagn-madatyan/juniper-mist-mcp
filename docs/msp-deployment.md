# Juniper Mist MCP Server — MSP Deployment Guide

This guide covers deploying the Juniper Mist MCP server in managed service provider (MSP) environments. It provides detailed configuration instructions, safety mechanisms, deployment patterns, and operational guidance for running the server in production.

## Overview

The Juniper Mist MCP server is a Model Context Protocol (MCP) server that enables AI assistants (such as Claude Desktop) to interact with the Juniper Mist API for network management and operations.

### Target Audience

This documentation is written for **MSP engineers** who manage network infrastructure across multiple customer organizations using Juniper Mist.

### Key Capabilities

- **Multi-Org Support**: Configure and manage multiple customer organizations from a single server instance
- **Read Operations**: List organizations, retrieve device statistics, client data, alarms, events, WLANs, RF templates, inventory, and device configuration commands
- **Write Operations** (optional): Modify WLANs, manage NAC rules, WXLAN policies, and security policies
- **Region Mapping**: Support for US, EU, Government (GC1, GC2), and Asia Pacific cloud regions
- **Safety Layers**: Read-only by default with optional write tool enablement

## Installation

### Prerequisites

- Python 3.11 or later
- pip package manager

### Install from Source

Clone the repository and install in editable mode:

```bash
cd /path/to/juniper-mist-mcp
pip install -e .
```

This installs the `mist-mcp` package and its dependencies, including:
- `fastmcp` — MCP server framework
- `mistapi` — Juniper Mist Python SDK
- `python-dotenv` — Environment variable loading

## Configuration

### Environment File Format

The server uses a `.env` file to configure organization credentials. The file should be located in the project root or specified via the `--env-file` flag.

#### Naming Convention

Use the following prefix-based naming:

| Variable | Description |
|----------|-------------|
| `MIST_TOKEN_<ORGNAME>` | API token for the organization (required) |
| `MIST_REGION_<ORGNAME>` | Regional API endpoint (optional, defaults to US) |

The `<ORGNAME>` suffix is case-sensitive and identifies each organization's configuration.

### Supported Regional Endpoints

| Region | Endpoint | Use Case |
|--------|----------|----------|
| US (default) | `api.mist.com` | North America deployments |
| EU | `api.eu.mist.com` | European deployments |
| Government Cloud 1 | `api.gc1.mist.com` | US Government (FedRAMP) |
| Government Cloud 2 | `api.gc2.mist.com` | US Government (additional) |
| Asia Pacific 2 | `api.ac2.mist.com` | APAC deployments |

### Example Configuration

Create a `.env` file based on the following examples:

```bash
# Example Organization 1: US-based company (default region)
MIST_TOKEN_example_org=your_token_here_example_org
# MIST_REGION_example_org=api.mist.com  # Optional, this is the default

# Example Organization 2: EU-based company using EU region
MIST_TOKEN_acme_corp=your_token_here_acme_corp
MIST_REGION_acme_corp=api.eu.mist.com

# Example Organization 3: Government customer using GC1 region
MIST_TOKEN_gov_agency=your_token_here_gov_agency
MIST_REGION_gov_agency=api.gc1.mist.com
```

### Obtaining API Tokens

1. Log in to the Mist portal at [https://admin.mist.com](https://admin.mist.com)
2. Navigate to **Organization** → **Settings** → **API Tokens**
3. Create a new API token with appropriate scope (read-only or admin based on needs)
4. Copy the token to your `.env` file

> **Security Note**: Treat API tokens as secrets. Do not commit them to version control. Add `.env` to your `.gitignore` file.

## Safety Features

The server implements a four-layer safety model to prevent unintended network modifications:

### Layer 1: Read-Only Default

All write tools are **disabled by default**. When the server starts without the `--enable-write-tools` flag, only read operations are available (10 tools).

### Layer 2: CLI Flag for Write Tools

The `--enable-write-tools` flag explicitly enables modification tools. This provides intentional, explicit opt-in for write operations:

```bash
python -m mist_mcp.server --enable-write-tools
```

When enabled, 4 additional write tools become available:
- `mist_update_wlan` — Modify WLAN/SSID configurations
- `mist_manage_nac_rules` — Create, update, or delete NAC rules
- `mist_manage_wxlan` — Manage WXLAN microsegmentation policies
- `mist_manage_security_policies` — Modify security policies

### Layer 3: MCP Annotations

The server uses MCP protocol annotations to communicate tool capabilities to AI assistants:

- **Read tools**: Marked with `readOnlyHint=True` — signals to the AI that these tools don't modify state
- **Write tools**: Marked with `destructiveHint=True` — signals that these tools make changes

These annotations help AI assistants make informed decisions about when to use write tools and prompt users for confirmation.

### Layer 4: Pre-Flight Platform Validation

Before executing write operations, the server validates platform-specific constraints:

- **ID Format Validation**: Verifies that resource IDs (WLAN IDs, rule IDs, policy IDs) are non-empty and follow UUID format
- **Parameter Validation**: Ensures required fields are present for update and delete operations
- **Suspicious Input Detection**: Logs warnings for potentially incorrect IDs that don't match expected formats

This validation runs before any API call, providing an additional safety checkpoint.

### Enabling Write Tools Safely

To enable write tools:

```bash
python -m mist_mcp.server --enable-write-tools
```

**Precautions**:
1. Only enable write tools when explicitly needed
2. Review the AI's planned operations before allowing execution
3. Consider using read-only tokens for day-to-day operations
4. Use admin tokens only when modifications are required

## Deployment Modes

### Stdio Mode (Claude Desktop)

In stdio mode, the server communicates with Claude Desktop via standard input/output. This is the recommended mode for local development and individual AI assistant interactions.

#### Running in Stdio Mode

```bash
# Default stdio transport
python -m mist_mcp.server

# Or explicitly specify stdio
python -m mist_mcp.server --transport=stdio
```

#### Configuring Claude Desktop

Add the server to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "juniper-mist": {
      "command": "python",
      "args": [
        "-m",
        "mist_mcp.server"
      ],
      "env": {
        "MIST_TOKEN_org1": "your_token_here"
      }
    }
  }
}
```

> **Note**: Alternatively, create a `.env` file in the project directory and the server will load it automatically.

### HTTP Mode (Centralized SaaS)

In HTTP mode, the server runs as a streamable HTTP server, allowing centralized deployment where multiple clients can connect.

#### Running in HTTP Mode

```bash
# Basic HTTP server on default port (8000)
python -m mist_mcp.server --transport=http

# Custom host and port
python -m mist_mcp.server --transport=http --host=0.0.0.0 --port=8080

# Enable write tools in HTTP mode
python -m mist_mcp.server --transport=http --enable-write-tools
```

#### Using Behind a Reverse Proxy

For production deployments, consider running behind a reverse proxy (nginx, Traefik, etc.) for:
- TLS termination
- Authentication
- Rate limiting
- Load balancing

Example nginx configuration:

```nginx
location /mcp/ {
    proxy_pass http://localhost:8000/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Running the Server

### Command-Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `--enable-write-tools` | Enable write tools (4 additional tools) | Disabled |
| `--transport` | Transport protocol: `stdio` or `http` | `stdio` |
| `--host` | Host to bind to for HTTP transport | `0.0.0.0` |
| `--port` | Port to bind to for HTTP transport | `8000` |
| `--env-file` | Path to .env file | `.env` |

### Example Commands

**Stdio mode (read-only):**
```bash
python -m mist_mcp.server
```

**Stdio mode with write tools:**
```bash
python -m mist_mcp.server --enable-write-tools
```

**HTTP mode (read-only):**
```bash
python -m mist_mcp.server --transport=http --port=8000
```

**HTTP mode with write tools:**
```bash
python -m mist_mcp.server --transport=http --host=0.0.0.0 --port=8080 --enable-write-tools
```

**Custom environment file:**
```bash
python -m mist_mcp.server --env-file=/path/to/custom.env
```

## Verification

### Verify Server is Working

Use the `mist_list_orgs` tool to verify the server is functioning correctly:

1. Start the server: `python -m mist_mcp.server`
2. In your AI assistant, call the `mist_list_orgs` tool
3. Verify that it returns your configured organizations

Expected output example:
```json
[
  {"name": "example_org", "region": "api.mist.com", "has_token": true},
  {"name": "acme_corp", "region": "api.eu.mist.com", "has_token": true}
]
```

### Run the Test Suite

Run the test suite to verify the server's behavior:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_rate_limit.py -v

# Run tests with verbose output
pytest tests/ -v --tb=short
```

### Run Verification Scripts

The project includes verification scripts that check specific functionality:

```bash
# Verify S05: Safety layers & multi-tenancy
bash scripts/verify_s05.sh

# Verify S06: Testing & validation
bash scripts/verify_s06.sh
```

### Verify Write Tools Disabled

To confirm write tools are properly disabled by default:

```bash
python -c "
import asyncio
from mist_mcp.server import mcp, register_tools, reset_tool_registration

async def check():
    reset_tool_registration()
    register_tools(enable_write=False)
    tools = await mcp.list_tools()
    return [t.name for t in tools]

tools = asyncio.run(check())
print(f'Total tools: {len(tools)}')
print('Tools:', ', '.join(sorted(tools)))
"
```

Expected output shows 10 read-only tools; write tools should NOT appear.

## Troubleshooting

### Common Errors and Solutions

#### "Configuration file not found: .env"

**Cause**: The `.env` file doesn't exist in the specified location.

**Solution**: Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env with your actual tokens
```

#### "Organization 'X' is not configured"

**Cause**: The organization name used in a tool call doesn't match any `MIST_TOKEN_*` variable in your `.env` file.

**Solution**:
1. Check your `.env` file for the correct organization name (case-sensitive)
2. Verify the token is set: `MIST_TOKEN_yourorg=your_token`
3. Restart the server after modifying `.env`

#### "Unknown region 'X'"

**Cause**: The region value doesn't match any known Mist cloud endpoint.

**Solution**: Use one of the supported regions:
- `api.mist.com` (US, default)
- `api.eu.mist.com` (EU)
- `api.gc1.mist.com` (Government Cloud 1)
- `api.gc2.mist.com` (Government Cloud 2)
- `api.ac2.mist.com` (Asia Pacific 2)

#### "Failed to fetch orgs: 401 - Unauthorized"

**Cause**: Invalid or expired API token.

**Solution**:
1. Verify the token in your `.env` file is correct
2. Log in to Mist portal and generate a new API token
3. Update the token in your `.env` file
4. Restart the server

#### "No session manager available"

**Cause**: The server started without a valid configuration (no `.env` file or all tokens invalid).

**Solution**: Ensure your `.env` file exists and contains valid tokens.

#### Write tools not working

**Cause**: Write tools require the `--enable-write-tools` flag.

**Solution**: Start the server with the flag:
```bash
python -m mist_mcp.server --enable-write-tools
```

### Debugging Tips

**Enable verbose logging:**
```bash
# Run with Python logging set to DEBUG
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from mist_mcp.server import main
main()
"
```

**Check loaded configuration:**
```bash
python -c "
from mist_mcp.config import Config
config = Config()
print('Organizations:', config.orgs)
for org in config.get_all_orgs():
    print(f'  {org.name}: region={org.region}, has_token={bool(org.token)}')
"
```

## References

### Official Documentation

- **Mist API Documentation**: [https://api.mist.com/](https://api.mist.com/)
- **Mist Portal**: [https://admin.mist.com](https://admin.mist.com)
- **FastMCP Documentation**: [https://fastmcp.docs.iex.dev/](https://fastmcp.docs.iex.dev/)
- **MCP Specification**: [https://spec.modelcontextprotocol.io/](https://spec.modelcontextprotocol.io/)

### Project Resources

- **Repository**: [https://github.com/your-org/juniper-mist-mcp](https://github.com/your-org/juniper-mist-mcp)
- **Issue Tracker**: [https://github.com/your-org/juniper-mist-mcp/issues](https://github.com/your-org/juniper-mist-mcp/issues)

### Python Packages

- **mistapi** — Juniper Mist Python SDK
- **fastmcp** — FastMCP server framework
- **python-dotenv** — Environment variable loading
