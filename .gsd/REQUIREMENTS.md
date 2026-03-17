# Requirements

This file is the explicit capability and coverage contract for the project.

## Active

### R001 — MCP server implemented in Python using FastMCP library, exposing tools via stdio transport
- Class: core-capability
- Status: active
- Description: MCP server implemented in Python using FastMCP library, exposing tools via stdio transport
- Why it matters: Foundation for all other capabilities; must follow MCP specification for compatibility with Claude Desktop and other clients
- Source: user
- Primary owning slice: M001/S01
- Supporting slices: none
- Validation: proved by S01 verification (pytest tests/test_server.py passed, verify_s01.sh passed)
- Notes: Must support Python 3.11+, FastMCP ≥2.5.1

### R002 — Server authenticates to Mist Cloud APIs using static API tokens stored in .env file format
- Class: integration
- Status: active
- Description: Server authenticates to Mist Cloud APIs using static API tokens stored in .env file format
- Why it matters: Without working authentication, no tools can function
- Source: user
- Primary owning slice: M001/S01
- Supporting slices: none
- Validation: proved by S01 verification (config loading tested, session manager initialized)
- Notes: .env format: MIST_TOKEN_ORGNAME=token, MIST_REGION_ORGNAME=api.mist.com etc.

### R003 — Each tool accepts `org` parameter to specify which customer organization to operate on; server routes API calls with appropriate token and region
- Class: operability
- Status: active
- Description: Each tool accepts `org` parameter to specify which customer organization to operate on; server routes API calls with appropriate token and region
- Why it matters: MSP engineers manage multiple customers; need clean switching between orgs
- Source: user
- Primary owning slice: M001/S01
- Supporting slices: none
- Validation: proved by S01 verification (org routing in session manager, mist_list_orgs returns configured orgs)
- Notes: Parameter validation, friendly error messages for invalid org names

### R004 — Server correctly routes API calls to appropriate regional endpoint (api.mist.com, api.eu.mist.com, etc.) based on per-org configuration
- Class: integration
- Status: active
- Description: Server correctly routes API calls to appropriate regional endpoint (api.mist.com, api.eu.mist.com, etc.) based on per-org configuration
- Why it matters: Mist has 5 regional APIs; wrong region = authentication failures
- Source: user
- Primary owning slice: M001/S01
- Supporting slices: none
- Validation: proved by S01 verification (region validation in config.py, session manager uses region for API calls)
- Notes: Must handle region configuration per org

### R005 — Read-only tools for troubleshooting: get device stats, AI-driven SLE (Service Level Experience) metrics, client connectivity data, active alarms, event logs
- Class: primary-user-loop
- Status: active
- Description: Read-only tools for troubleshooting: get device stats, AI-driven SLE (Service Level Experience) metrics, client connectivity data, active alarms, event logs
- Why it matters: MSP engineers spend most time monitoring and troubleshooting; these are highest-value read tools
- Source: dashboard
- Primary owning slice: M001/S02
- Supporting slices: M001/S01
- Validation: proved by S02 verification (24 tests pass, verify_s02.sh exits 0, all 5 tools registered and functional)
- Notes: Following dashboard tool list: mist_get_device_stats, mist_get_sle_summary, mist_get_client_stats, mist_get_alarms, mist_get_site_events

### R006 — Read tools for viewing configuration: list WLAN profiles, inventory management, RF template configs, generated CLI config viewing
- Class: admin/support
- Status: active
- Description: Read tools for viewing configuration: list WLAN profiles, inventory management, RF template configs, generated CLI config viewing
- Why it matters: Engineers need to see current configuration before making changes
- Source: dashboard
- Primary owning slice: M001/S03
- Supporting slices: M001/S02
- Validation: proved by S03 verification (37 tests pass, verify_s03.sh exits 0, all 4 tools registered and functional)
- Notes: mist_list_wlans, mist_get_inventory, mist_get_rf_templates, mist_get_device_config_cmd

### R008 — Server starts with only read tools (tier1 and tier2) registered; write tools require explicit enable flag
- Class: safety
- Status: active
- Description: Server starts with only read tools (tier1 and tier2) registered; write tools require explicit enable flag
- Why it matters: Prevents accidental misconfiguration; MSPs can deploy read-only version to junior staff
- Source: user
- Primary owning slice: M001/S05
- Supporting slices: M001/S04
- Validation: unmapped
- Notes: Must be configurable via command-line flag or env var

### R009 — Write tools (tier3) only registered when server started with --enable-write-tools flag (or equivalent env var)
- Class: safety
- Status: active
- Description: Write tools (tier3) only registered when server started with --enable-write-tools flag (or equivalent env var)
- Why it matters: Explicit opt-in for write capabilities reduces risk
- Source: user
- Primary owning slice: M001/S05
- Supporting slices: M001/S04
- Validation: unmapped
- Notes: Should support pattern matching: --write-tools "mist_update_*"

### R010 — Tools that could disrupt network connectivity or security include destructiveHint=True, triggering LLM permission dialog
- Class: safety
- Status: active
- Description: Tools that could disrupt network connectivity or security include destructiveHint=True, triggering LLM permission dialog
- Why it matters: Extra guard rail for high-risk operations like security policy changes
- Source: user
- Primary owning slice: M001/S05
- Supporting slices: M001/S04
- Validation: unmapped
- Notes: Following MCP best practices for destructive operations

### R011 — Write operations validate against Mist platform constraints (e.g., template validation, config compatibility) before submission
- Class: safety
- Status: active
- Description: Write operations validate against Mist platform constraints (e.g., template validation, config compatibility) before submission
- Why it matters: Prevents configuration errors that Mist API would reject anyway
- Source: user
- Primary owning slice: M001/S05
- Supporting slices: M001/S04
- Validation: unmapped
- Notes: Leverages mistapi SDK validation where available

### R012 — Server supports both stdio transport (local Claude Desktop) and streamable HTTP transport (centralized SaaS deployment)
- Class: operability
- Status: active
- Description: Server supports both stdio transport (local Claude Desktop) and streamable HTTP transport (centralized SaaS deployment)
- Why it matters: MSPs need both local dev/testing and centralized deployment options
- Source: inferred
- Primary owning slice: M001/S01
- Supporting slices: none
- Validation: proved by S01 verification (CLI supports --transport stdio/http, verify_s01.sh confirms stdio works)
- Notes: FastMCP supports both; need configuration for streamable HTTP path

### R013 — Tests verify rate limit handling (5,000 req/hour), success tracking, and appropriate error handling
- Class: quality-attribute
- Status: active
- Description: Tests verify rate limit handling (5,000 req/hour), success tracking, and appropriate error handling
- Why it matters: Mist API has strict rate limits; server must handle them gracefully
- Source: dashboard
- Primary owning slice: M001/S06
- Supporting slices: M001/S01
- Validation: unmapped
- Notes: Should include backoff/retry logic for rate limit responses

### R014 — Documentation covering MSP deployment patterns: multi-org .env structure, region mapping, safety flag usage, centralized vs local deployment
- Class: operability
- Status: active
- Description: Documentation covering MSP deployment patterns: multi-org .env structure, region mapping, safety flag usage, centralized vs local deployment
- Why it matters: MSPs need clear guidance on how to deploy and use in production
- Source: user
- Primary owning slice: M001/S06
- Supporting slices: none
- Validation: unmapped
- Notes: Should include example .env files and command-line examples

## Validated

### R007 — Write tools for configuration changes: update WLAN profiles, manage NAC (802.1X) rules, configure WXLAN microsegmentation, manage security policies
- Class: primary-user-loop
- Status: validated
- Description: Write tools for configuration changes: update WLAN profiles, manage NAC (802.1X) rules, configure WXLAN microsegmentation, manage security policies
- Why it matters: Actual operational value comes from making safe configuration changes
- Source: dashboard
- Primary owning slice: M001/S04
- Supporting slices: M001/S03, M001/S05
- Validation: proved by S04 verification (61 tests pass, verify_s04.sh exits 0, all 4 write tools registered and functional)
- Notes: mist_update_wlan, mist_manage_nac_rules, mist_manage_wxlan, mist_manage_security_policies

## Deferred

### R015 — Extend server to support Palo Alto Prisma Access and Cisco Meraki in addition to Juniper Mist
- Class: core-capability
- Status: deferred
- Description: Extend server to support Palo Alto Prisma Access and Cisco Meraki in addition to Juniper Mist
- Why it matters: MSPs often manage mixed vendor environments; unified interface would be powerful
- Source: dashboard
- Primary owning slice: none
- Supporting slices: none
- Validation: unmapped
- Notes: Deferred to future milestone after Mist server proves stable

## Out of Scope

### R016 — Visual dashboard showing cross-vendor status (like mcp-architecture-dashboard.jsx)
- Class: admin/support
- Status: out-of-scope
- Description: Visual dashboard showing cross-vendor status (like mcp-architecture-dashboard.jsx)
- Why it matters: Would be nice but not required for M001; focus is on MCP server not UI
- Source: dashboard
- Primary owning slice: none
- Supporting slices: none
- Validation: n/a
- Notes: Could be future milestone

## Traceability

| ID | Class | Status | Primary owner | Supporting | Proof |
|---|---|---|---|---|---|
| R001 | core-capability | active | M001/S01 | none | proved by S01 verification (pytest tests/test_server.py passed, verify_s01.sh passed) |
| R002 | integration | active | M001/S01 | none | proved by S01 verification (config loading tested, session manager initialized) |
| R003 | operability | active | M001/S01 | none | proved by S01 verification (org routing in session manager, mist_list_orgs returns configured orgs) |
| R004 | integration | active | M001/S01 | none | proved by S01 verification (region validation in config.py, session manager uses region for API calls) |
| R005 | primary-user-loop | active | M001/S02 | M001/S01 | proved by S02 verification (24 tests pass, verify_s02.sh exits 0, all 5 tools registered and functional) |
| R006 | admin/support | active | M001/S03 | M001/S02 | proved by S03 verification (37 tests pass, verify_s03.sh exits 0, all 4 tools registered and functional) |
| R007 | primary-user-loop | validated | M001/S04 | M001/S03, M001/S05 | proved by S04 verification (61 tests pass, verify_s04.sh exits 0, all 4 write tools registered and functional) |
| R008 | safety | active | M001/S05 | M001/S04 | unmapped |
| R009 | safety | active | M001/S05 | M001/S04 | unmapped |
| R010 | safety | active | M001/S05 | M001/S04 | unmapped |
| R011 | safety | active | M001/S05 | M001/S04 | unmapped |
| R012 | operability | active | M001/S01 | none | proved by S01 verification (CLI supports --transport stdio/http, verify_s01.sh confirms stdio works) |
| R013 | quality-attribute | active | M001/S06 | M001/S01 | unmapped |
| R014 | operability | active | M001/S06 | none | unmapped |
| R015 | core-capability | deferred | none | none | unmapped |
| R016 | admin/support | out-of-scope | none | none | n/a |

## Coverage Summary

- Active requirements: 13
- Mapped to slices: 13
- Validated: 1 (R007)
- Unmapped active requirements: 0
