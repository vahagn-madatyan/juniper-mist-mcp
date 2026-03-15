# M001: Juniper Mist MCP Server

**Vision:** MSP engineers can use Claude Desktop to monitor, troubleshoot, and safely configure customer Juniper Mist networks through natural language, with built-in safety layers that prevent accidental misconfiguration.

## Success Criteria

- MSP engineer can query device stats, SLE metrics, and alarms for any customer organization
- Write operations (WLAN updates, NAC rules) require explicit enable flag and show destructive hints
- Server handles 5,000 req/hour rate limits gracefully with backoff/retry logic
- Both local (stdio) and centralized (streamable HTTP) deployments work
- All safety layers are operational and documented for MSP deployment

## Key Risks / Unknowns

- **Mist API regional endpoint differences** — S01 must prove authentication works across all 5 regions
- **Rate limit handling** — S02/S03 tools must be designed with rate limit awareness
- **Write operation safety** — S04/S05 must implement validation that prevents breaking changes

## Proof Strategy

- **Mist API regional endpoint differences** → retire in S01 by proving authentication and basic API calls work for orgs configured with different regions
- **Rate limit handling** → retire in S02 by demonstrating tool design respects rate limits and implements backoff
- **Write operation safety** → retire in S05 by showing write tools are disabled by default and require explicit enable flag with destructive hints

## Verification Classes

- Contract verification: Unit tests for tool signatures, authentication, config parsing
- Integration verification: Live API calls to Mist sandbox/test org, actual data retrieval
- Operational verification: Rate limit simulation, error recovery, both transport modes
- UAT / human verification: MSP engineer uses Claude Desktop to perform real troubleshooting and safe configuration changes

## Milestone Definition of Done

This milestone is complete only when all are true:

- All six slices are complete with working, demoable code
- Server can be started in both stdio and streamable HTTP modes
- Read tools work for real Mist data (not mocked)
- Write tools work when explicitly enabled, with safety layers active
- Rate limit handling is demonstrated through behavioral tests
- MSP deployment documentation exists and is accurate

## Requirement Coverage

- Covers: R001-R014
- Partially covers: none
- Leaves for later: R015 (multi-vendor), R016 (dashboard UI)
- Orphan risks: none (all mapped)

## Slices

- [x] **S01: Foundation & authentication** `risk:low` `depends:[]`
  > After this: Server starts, authenticates to Mist API with .env tokens, lists available orgs, supports both stdio and streamable HTTP transports
- [ ] **S02: Read tools (tier1)** `risk:low` `depends:[S01]`
  > After this: Agent can query device stats, SLE metrics, client stats, alarms, events across customer orgs; tools respect rate limits
- [ ] **S03: Config viewing tools (tier2)** `risk:medium` `depends:[S02]`
  > After this: Agent can inspect WLAN configs, inventory, RF templates, device CLI config; all read tools work together
- [ ] **S04: Write tools (tier3)** `risk:high` `depends:[S03]`
  > After this: Agent can modify WLANs, NAC rules, WXLAN, security policies when write tools enabled; basic validation in place
- [ ] **S05: Safety layers & multi-tenancy** `risk:medium` `depends:[S04]`
  > After this: Write tools disabled by default, require --enable-write-tools flag; destructive hints for risky ops; platform validation active
- [ ] **S06: Testing & validation** `risk:low` `depends:[S05]`
  > After this: All tools work with rate limit awareness; MSP deployment guide complete; behavioral tests verify success tracking

## Boundary Map

### S01 → S02

Produces:
- `MistServer` class with authenticated session per org
- Config loader for .env org/token/region mapping
- Transport setup (stdio + streamable HTTP)
- `list_orgs()` tool showing available customer organizations

Consumes:
- nothing (first slice)

### S02 → S03

Produces:
- Tier1 tools: `mist_get_device_stats`, `mist_get_sle_summary`, `mist_get_client_stats`, `mist_get_alarms`, `mist_get_site_events`
- Rate-limit-aware tool design pattern
- Shared response formatting for consistent LLM consumption

Consumes from S01:
- `MistServer` class for authenticated API calls
- Org routing logic

### S03 → S04

Produces:
- Tier2 tools: `mist_list_wlans`, `mist_get_inventory`, `mist_get_rf_templates`, `mist_get_device_config_cmd`
- Config viewing patterns (safe read-only operations)

Consumes from S02:
- Rate-limit-aware design pattern
- Shared response formatting

### S04 → S05

Produces:
- Tier3 tools: `mist_update_wlan`, `mist_manage_nac_rules`, `mist_manage_wxlan`, `mist_manage_security_policies`
- Write operation templates with parameter validation

Consumes from S03:
- Config viewing tools (to see before changing)

### S05 → S06

Produces:
- Safety layer implementation: read-only default flag, explicit write enable, destructive hints, platform validation
- Command-line flags for safety controls

Consumes from S04:
- Write tool implementations to wrap with safety

### S06 (integration slice)

Produces:
- Behavioral tests for rate limit handling
- MSP deployment documentation
- End-to-end validation scenarios

Consumes from all slices:
- Complete toolset
- Safety layers
- Transport modes