# S03: Config viewing tools (tier2) — Research

**Date:** 2026-03-15

## Summary

This slice implements tier2 config viewing tools for the Juniper Mist MCP server. These tools allow MSP engineers to inspect WLAN configurations, device inventory, RF templates, and device CLI configurations. The tools are read-only (no write operations) and follow the same patterns established in S02: org validation, API response serialization, and structured logging.

The implementation requires four new MCP tools:
- `mist_list_wlans` — List all WLAN profiles in an organization
- `mist_get_inventory` — Search/filter device inventory (by type, status, site, etc.)
- `mist_get_rf_templates` — List RF templates in an organization
- `mist_get_device_config_cmd` — Get generated CLI configuration for a device

All tools will use the mistapi SDK functions identified in research and will reuse the `serialize_api_response`, `get_org_id`, and `validate_org` helpers already implemented in S02.

## Recommendation

Follow the exact pattern from S02 for each tool:

1. **Pattern to replicate**: `mist_get_device_stats` and `mist_get_client_stats` are the closest analogs — they use org-level APIs with similar parameter structures.

2. **API endpoints**:
   - `wlans.listOrgWlans(session, org_id, limit, page)` — returns list of WLANs
   - `inventory.searchOrgInventory(session, org_id, type, status, site_id, ...)` — supports rich filtering
   - `rftemplates.listOrgRfTemplates(session, org_id, limit, page)` — returns RF templates
   - `devices.getSiteDeviceConfigCmd(session, site_id, device_id, sort)` — requires both site_id and device_id

3. **Test strategy**: Mirror S02's approach — tests for tool registration, org validation, and response serialization.

## Don't Hand-Roll

| Problem | Existing Solution | Why Use It |
|---------|------------------|------------|
| JSON serialization of API responses | `serialize_api_response()` helper | Already proven in S02; handles errors and pagination |
| Org name to ID resolution | `get_org_id()` helper | Already implemented; avoids duplication |
| Org validation | `validate_org()` function | Already implemented; consistent error handling |
| Rate limit handling | mistapi built-in retry (D012) | SDK handles 429 with exponential backoff |

## Existing Code and Patterns

- `mist_mcp/server.py` — Contains S02 tools (`mist_get_device_stats`, `mist_get_client_stats`, etc.) that follow the exact pattern to replicate:
  - `validate_org` call at start
  - `session_manager.get_session(org)` to get authenticated session
  - `get_org_id(org, session)` to resolve org name to ID
  - Import and call mistapi SDK function
  - Return `serialize_api_response(response)`
  - INFO logging with tool name and parameters

- `tests/test_server.py` — Contains S02 test patterns:
  - `test_tier1_tools_registered()` — verifies all tools are registered
  - `test_*_invalid_org()` — validates org error handling
  - `test_serialize_api_response()` — tests serialization helper

## Constraints

- **Device config command requires site_id**: Unlike other tier2 tools that work at org level, `getSiteDeviceConfigCmd` requires both `site_id` and `device_id`. The user must know the site and device to query.
- **Inventory filtering**: The `searchOrgInventory` function supports many filter parameters — need to expose useful ones (type, status, site_id) without making the tool signature too complex.
- **Rate limits**: Already handled by mistapi SDK per D012 — no additional retry logic needed.

## Common Pitfalls

- **Forgetting to import SDK functions**: Each tool needs `from mistapi.api.v1.orgs import wlans` style imports. Do this inside the tool function (like S02 does) to avoid import-time failures.
- **Missing org_id resolution**: Several tools need org_id — use the existing `get_org_id()` helper, not direct API calls.
- **Device config requires site context**: The `mist_get_device_config_cmd` tool requires site_id and device_id. Must make this clear in the tool description.
- **Inventory type filter values**: The API accepts `type` values like "ap", "gateway", "switch" — need validation or documentation.

## Open Risks

- **Real API testing**: Without live Mist API tokens, verification relies on unit tests. Integration verification would require sandbox/test org credentials.
- **Parameter complexity**: Inventory search has many optional parameters — need to choose which to expose without making the tool signature unwieldy.

## Skills Discovered

No additional skills required. The work uses:
- Python (core)
- mistapi SDK (already available)
- FastMCP (already available)

## Sources

- mistapi SDK exploration via `python3 -c "from mistapi.api.v1.orgs import ..."` commands
- S02 implementation patterns in `mist_mcp/server.py`
- S02 test patterns in `tests/test_server.py`
