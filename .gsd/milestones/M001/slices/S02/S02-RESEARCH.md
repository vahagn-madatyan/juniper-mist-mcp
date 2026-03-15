# S02: Read tools (tier1) — Research

**Date:** 2026-03-15

## Summary

S02 implements the core read-only tools that MSP engineers use most: device stats, SLE (Service Level Experience) metrics, client stats, alarms, and site events. These tools are the highest-value operational tools for day-to-day troubleshooting.

Key findings:
- mistapi library provides all required endpoints under `mistapi.api.v1.orgs.*` and `mistapi.api.v1.sites.*`
- Rate-limit handling is already built into mistapi (3 retries with exponential backoff) — no additional tenacity needed
- SLE metrics require site_id, which means tools need to either accept site_id or list sites for the org first
- API responses use `mistapi.APIResponse` wrapper that needs `.data` access and JSON serialization for MCP

## Recommendation

Build five MCP tools following the existing server pattern:
1. `mist_get_device_stats` — Uses `listOrgDevicesStats` with org-level aggregation
2. `mist_get_sle_summary` — Uses `getSiteSleSummary` (requires site_id parameter)
3. `mist_get_client_stats` — Uses `searchOrgWirelessClients` with aggregation
4. `mist_get_alarms` — Uses `searchOrgAlarms` with filtering options
5. `mist_get_site_events` — Uses `searchOrgEvents` with time-based filtering

All tools follow the pattern: validate org → get session → call API → format response.

**Why this approach**: Direct use of mistapi endpoints is simpler than wrapping — the library is well-designed and handles authentication, pagination, and rate limits natively. Response formatting should be minimal JSON extraction to keep LLM-readable output.

## Don't Hand-Roll

| Problem | Existing Solution | Why Use It |
|---------|------------------|------------|
| Rate-limit retry logic | mistapi built-in (3 retries, exponential backoff) | D012 decision — proven, no additional code needed |
| Authentication | MistSessionManager from S01 | Already implemented and tested |
| Response parsing | mistapi.APIResponse.data access | Native library pattern, minimal transformation |

## Existing Code and Patterns

- `mist_mcp/server.py` — Tool registration pattern with `@mcp.tool` decorator and org validation via `validate_org()` function
- `mist_mcp/session.py` — `MistSessionManager.get_session(org)` returns authenticated `mistapi.APISession`
- `mist_mcp/config.py` — `OrgConfig` dataclass provides `name`, `token`, `region` per org

## API Endpoints Required

| Tool | mistapi Function | Parameters |
|------|-----------------|------------|
| mist_get_device_stats | `mistapi.api.v1.orgs.stats.listOrgDevicesStats` | org_id, type, status, duration |
| mist_get_sle_summary | `mistapi.api.v1.sites.sle.getSiteSleSummary` | site_id (requires site enumeration) |
| mist_get_client_stats | `mistapi.api.v1.orgs.clients.searchOrgWirelessClients` | org_id, duration, limit |
| mist_get_alarms | `mistapi.api.v1.orgs.alarms.searchOrgAlarms` | org_id, start, end, status |
| mist_get_site_events | `mistapi.api.v1.orgs.events.searchOrgEvents` | org_id, start, end, site_id |

## Constraints

- **SLE requires site_id**: Unlike other tools that work at org level, SLE metrics are site-specific. Need to either require site_id parameter or enumerate sites first.
- **APIResponse serialization**: mistapi returns `APIResponse` objects that need `.data` access and may contain non-JSON-serializable types (datetime, etc.)
- **Duration format**: Mist API accepts duration strings like "1h", "24h", "7d" — need to validate or document
- **Config isolation**: Use `dotenv_values()` per S01 decision (D001)

## Common Pitfalls

- **Forgetting `.data` on APIResponse** — MistAPI calls return wrapper, must access `.data` for actual payload
- **Passing wrong ID type** — Some endpoints take org_id, others take site_id; mixing them causes 404s
- **No site_id for SLE** — Without site_id, SLE query fails; must handle gracefully or require parameter
- **Large responses** — Clients and events can return many rows; consider adding limit parameter with sensible default

## Open Risks

1. **Live API validation**: S01 didn't test real authentication; real tokens may reveal issues with token format or region mapping
2. **SLE per-site UX**: Engineers may want org-wide SLE summary, but API is per-site; need to decide if we aggregate or require explicit site selection
3. **Response size**: Large event/client lists could exceed MCP response limits; need pagination or limit defaults

## Skills Discovered

No additional skills required. The work uses:
- Python 3.11+ (already available)
- FastMCP (already in pyproject.toml)
- mistapi (already in pyproject.toml)

## Sources

- MistAPI Python library: `mistapi.api.v1.orgs.*` and `mistapi.api.v1.sites.*` modules
- S01 summary: Established `MistSessionManager.get_session(org)` pattern and `validate_org()` function
- D012 decision: Use mistapi's built-in rate-limit retry mechanism
