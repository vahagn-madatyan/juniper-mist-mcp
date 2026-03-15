# Project

## What This Is

A production-grade Model Context Protocol (MCP) server that gives AI agents safe, multi-tenant access to Juniper Mist cloud APIs for network management and orchestration. The server is designed for MSPs (Managed Service Providers) who manage multiple customer organizations across different Mist regions.

## Core Value

MSP engineers can use Claude Desktop (or other MCP clients) to monitor, troubleshoot, and safely configure customer Juniper Mist networks through natural language, with built-in safety layers that prevent accidental misconfiguration.

## Current State

S02 (Read tools/tier1) complete. Server now provides 5 tier1 read tools: mist_get_device_stats, mist_get_sle_summary, mist_get_client_stats, mist_get_alarms, mist_get_site_events. All 24 tests pass. Six requirements validated (R001, R002, R003, R004, R005, R012).

## Architecture / Key Patterns

- **Stack**: Python 3.11+, FastMCP ≥2.5.1, mistapi SDK
- **Authentication**: Static API tokens per customer org stored in .env
- **Multi-tenancy**: Each tool call includes `org` parameter to route to the right customer
- **Regional support**: Configurable per org across 5 Mist regions (api.mist.com, api.eu.mist.com, etc.)
- **Safety**: Four-layer safety model: read-only default, explicit write enable flag, destructive hints, platform validation
- **Transport**: Both stdio (local dev) and streamable HTTP (centralized SaaS deployment)
- **Tool naming**: `mist_{verb}_{resource}` convention following Zscaler reference patterns

## Capability Contract

See `.gsd/REQUIREMENTS.md` for the explicit capability contract, requirement status, and coverage mapping.

## Milestone Sequence

- [ ] M001: Juniper Mist MCP Server — Production-ready MCP server with full read/write capabilities and MSP multi-tenancy safety
</result>