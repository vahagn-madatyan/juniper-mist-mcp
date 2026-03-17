# Project

## What This Is

A production-grade Model Context Protocol (MCP) server that gives AI agents safe, multi-tenant access to Juniper Mist cloud APIs for network management and orchestration. The server is designed for MSPs (Managed Service Providers) who manage multiple customer organizations across different Mist regions.

## Core Value

MSP engineers can use Claude Desktop (or other MCP clients) to monitor, troubleshoot, and safely configure customer Juniper Mist networks through natural language, with built-in safety layers that prevent accidental misconfiguration.

## Current State

M001 complete. The Juniper Mist MCP server is production-ready with 14 tools (10 read, 4 write), four-layer safety model, multi-tenant org routing across 5 Mist regions, both stdio and HTTP transports, and comprehensive MSP deployment documentation. All 103 tests pass. All 14 requirements (R001–R014) validated.

## Architecture / Key Patterns

- **Stack**: Python 3.11+, FastMCP ≥2.5.1, mistapi SDK
- **Authentication**: Static API tokens per customer org stored in .env
- **Multi-tenancy**: Each tool call includes `org` parameter to route to the right customer
- **Regional support**: Configurable per org across 5 Mist regions (api.mist.com, api.eu.mist.com, etc.)
- **Safety**: Four-layer safety model: read-only default, explicit write enable flag (`--enable-write-tools`), destructive hints via MCP annotations, pre-flight platform validation
- **Transport**: Both stdio (local dev) and streamable HTTP (centralized SaaS deployment)
- **Tool naming**: `mist_{verb}_{resource}` convention following Zscaler reference patterns
- **Tool registration**: Manual `mcp.add_tool()` for conditional registration and annotations
- **Write tools**: Multi-action pattern with `action` parameter (create/update/delete) per resource

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract, requirement status, and coverage mapping.

## Milestone Sequence

- [x] M001: Juniper Mist MCP Server — Production-ready MCP server with 14 tools, four-layer safety, multi-tenant org routing, and MSP deployment docs. All 14 requirements validated. 103 tests pass.
