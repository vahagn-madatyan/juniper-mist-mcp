# Decisions Register

<!-- Append-only. Never edit or remove existing rows.
     To reverse a decision, add a new row that supersedes it.
     Read this file at the start of any planning or research phase. -->

| # | When | Scope | Decision | Choice | Rationale | Revisable? |
|---|------|-------|----------|--------|-----------|------------|
| D001 | M001 | stack | MCP server implementation language | Python + FastMCP | FastMCP is the recommended Python framework for MCP; integrates well with mistapi SDK; Zscaler reference patterns are Python-based | No |
| D002 | M001 | auth | Authentication token storage | .env file with per-org tokens | MSP-friendly: easy to manage multiple customer tokens; follows 12-factor app pattern; no database dependency | Yes — if token rotation or secret manager needed |
| D003 | M001 | multi-tenancy | Org switching mechanism | org parameter per tool call | Cleanest UX for MSP engineers: specify customer in natural language; matches how they think about work | No |
| D004 | M001 | safety | Safety approach | Four-layer safety model (read-only default, explicit write enable, destructive hints, platform validation) | Defense in depth for MSP operations; prevents accidental misconfiguration; follows dashboard architecture | No |
| D005 | M001 | transport | Deployment transports | Both stdio (local) and streamable HTTP (centralized) | MSPs need both local dev/testing and centralized SaaS deployment options; FastMCP supports both | No |
| D006 | M001 | region | Regional endpoint handling | Region per org in config | Mist has 5 regional APIs; each customer org may be in different region; must be configurable per org | No |
| D007 | M001 | tool-design | Tool naming convention | {prefix}_{verb}_{resource} following Zscaler patterns | Consistency with reference architecture; clear semantics for both LLM and engineers | No |
| D008 | M001 | scope | Vendor focus | Juniper Mist only (single milestone) | Depth over breadth; establish solid patterns for one vendor before expanding; MSPs can deploy Mist-only now | Yes — superseded when multi-vendor milestone starts |
| D009 | M001 | tool-tiers | Tool implementation order | All three tiers (read, config view, write) in first milestone | MSPs need both monitoring and safe configuration capabilities; cannot ship read-only only | No |
| D010 | M001 | config | .env variable naming convention | MIST_TOKEN_<ORGNAME> and MIST_REGION_<ORGNAME> prefixes, case‑sensitive | Simple, predictable mapping from org name to token and region; matches common 12‑factor practice | Yes — if prefix conflicts arise |
| D011 | M001 | region | Region validation | Warn on unknown region but allow any hostname | Mist may add new regional endpoints; strict validation would break forward compatibility. Log warning to alert operator. | Yes — if Mist publishes official region list API |
| D012 | M001 | rate-limit | Rate-limit retry mechanism | Use mistapi's built-in retry | The mistapi library already handles 429 responses with 3 retries and exponential backoff; no need to add tenacity on top. | Yes — if custom retry logic needed |
| D013 | M001/S02 | API endpoints | API endpoint selection | Used mistapi SDK methods: listOrgDevicesStats, getSiteSleSummary, searchOrgWirelessClients, searchOrgAlarms, searchOrgEvents | Direct SDK methods are more reliable than raw API calls; ensures proper authentication and response handling | Yes — if Mist API changes |
| D014 | M001/S02 | data-format | Response serialization | serialize_api_response helper for JSON-serializable dicts with status_code, error, data, has_more fields | Consistent format across all tools for LLM consumption; handles APIResponse objects from mistapi | Yes — if MCP protocol changes response format |
| D015 | M001/S04 | tool-design | Write tool pattern for multi-action operations | Single tool with action parameter and conditional required parameters, following the same validate_org → get_session → get_org_id → API call → serialize pattern | Simplifies LLM interaction: one tool per resource type instead of separate create/update/delete tools; matches Mist SDK organization; reduces tool proliferation while maintaining clear parameter validation | Yes — if action parameter proves confusing or validation logic becomes too complex |