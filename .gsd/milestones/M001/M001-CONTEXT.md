# M001: Juniper Mist MCP Server — Context

**Gathered:** 2026-03-15
**Status:** Ready for planning

## Project Description

A production-grade Model Context Protocol (MCP) server that gives AI agents safe, multi-tenant access to Juniper Mist cloud APIs for network management and orchestration. Designed for MSPs (Managed Service Providers) who manage multiple customer organizations across different Mist regions.

## Why This Milestone

MSP engineers need AI-assisted network management tools that can safely interact with customer Juniper Mist environments. Current MCP landscape has only 2 early-stage Mist servers with gaps in multi-tenancy and safety features. This milestone delivers a complete, safety-first MCP server following Zscaler reference patterns.

## User-Visible Outcome

### When this milestone is complete, the user can:

- Start the MCP server locally or in centralized SaaS deployment
- Use Claude Desktop to query device stats, SLE metrics, alarms across multiple customer orgs
- Safely modify WLAN configurations, NAC rules, and security policies with explicit permission flags
- Switch between customer organizations via `org` parameter in natural language

### Entry point / environment

- Entry point: CLI command `mist-mcp` with flags for transport and safety
- Environment: Local Python environment (stdio for Claude Desktop) or Docker container (streamable HTTP for SaaS)
- Live dependencies involved: Juniper Mist Cloud API (5 regional endpoints), .env file with customer tokens

## Completion Class

- Contract complete means: All tools are defined with proper signatures, authentication works, safety layers implemented
- Integration complete means: Server can actually communicate with live Mist API, retrieve real data, make configuration changes
- Operational complete means: Server handles rate limits gracefully, recovers from API errors, works in both stdio and HTTP transports

## Final Integrated Acceptance

To call this milestone complete, we must prove:

- MSP engineer can use Claude Desktop to troubleshoot a customer network issue (device stats + alarms + SLE metrics)
- MSP engineer can safely update a WLAN configuration with explicit write enable flag
- Server correctly routes requests to appropriate regional endpoint based on org config
- Safety layers prevent accidental write operations when disabled

## Risks and Unknowns

- **Mist API rate limits (5,000 req/hour)** — Server must implement backoff/retry logic and tool design must be rate-limit aware
- **Multi-region authentication complexity** — Different regions may have subtle API differences; need validation across regions
- **Write operation safety** — Need robust validation to prevent breaking customer networks

## Existing Codebase / Prior Art

- `mcp-architecture-dashboard.jsx` — Architecture planning document with tool lists, safety layers, vendor comparisons
- **Zscaler reference patterns** — SDK-first design, ~10 tools per service module, {prefix}_{verb}_{resource} naming
- **MSP platform differentiators** — Multi-tenant credential routing, rate-limit-aware tool design, streamable HTTP for centralized deploy

> See `.gsd/DECISIONS.md` for all architectural and pattern decisions — it is an append-only register; read it during planning, append to it during execution.

## Relevant Requirements

- R001-R004 — Foundation & authentication
- R005 — Tier1 read tools (troubleshooting)
- R006 — Tier2 config tools (viewing)
- R007 — Tier3 write tools (configuration changes)
- R008-R011 — Safety layers
- R012-R014 — Deployment and testing

## Scope

### In Scope

- Python MCP server with FastMCP
- Mist API integration via mistapi SDK
- Multi-tenant org routing with .env config
- All three tool tiers (read, config view, write)
- Four safety layers
- Stdio and streamable HTTP transports
- MSP deployment documentation

### Out of Scope / Non-Goals

- Real-time dashboard UI (separate milestone)
- Multi-vendor support (Prisma, Meraki) — deferred
- Mobile app or web interface
- Advanced analytics beyond Mist API capabilities

## Technical Constraints

- Must support Python 3.11+
- Must use FastMCP ≥2.5.1 for MCP compliance
- Must handle Mist API rate limits (5,000 req/hour per token)
- Must support 5 Mist regional endpoints
- Token storage in .env file (not database)

## Integration Points

- **Juniper Mist Cloud API** — REST API for all network operations
- **Mist Python SDK (mistapi)** — Official SDK for API interactions
- **FastMCP framework** — MCP server implementation
- **Claude Desktop / MCP clients** — Stdio transport consumers

## Open Questions

- **Token refresh strategy** — Mist tokens don't expire; but need handling for token rotation scenarios
- **Configuration persistence** — Should server cache org config or reload .env on each call?
- **Error reporting granularity** — How much API error detail to expose to LLM vs log internally?