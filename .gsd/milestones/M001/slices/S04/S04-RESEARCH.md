# S04: Write tools (tier3) — Research

**Date:** 2026-03-16

## Summary

Slice S04 implements the tier3 write tools that enable configuration changes to Juniper Mist organizations. This slice builds directly on the patterns established in S02 (tier1 read) and S03 (tier2 config viewing), using the same `validate_org → get_session → get_org_id → API call → serialize` flow.

The mistapi SDK provides full CRUD operations for WLANs, NAC rules, WXLAN rules, and security policies. S04 will implement tools that use the **update/create/delete** SDK methods, while S05 will wrap these with safety layers (read-only default, explicit enable flag, destructive hints).

This is **light research** — the patterns are established, the SDK is well-understood, and the work involves applying existing patterns to write operations.

## Recommendation

Implement four write tools following the exact pattern used in S02/S03:

1. `mist_update_wlan` — Update existing WLAN (SSID) configuration using `updateOrgWlan`
2. `mist_manage_nac_rules` — Create/update/delete NAC rules using `createOrgNacRule`, `updateOrgNacRule`, `deleteOrgNacRule`
3. `mist_manage_wxlan` — Create/update/delete WXLAN microsegmentation rules using `createOrgWxRule`, `updateOrgWxRule`, `deleteOrgWxRule`
4. `mist_manage_security_policies` — Create/update/delete security policies using `createOrgSecPolicy`, `updateOrgSecPolicy`, `deleteOrgSecPolicy`

Each tool should:
- Accept `org` parameter (validated via `validate_org`)
- Accept `action` parameter ("create", "update", "delete")
- Accept resource-specific identifiers (wlan_id, rule_id, policy_id)
- Accept `body` dict for configuration data (for create/update)
- Follow S02/S03 pattern exactly for session handling and response serialization

## Implementation Landscape

### Key Files

- `mist_mcp/server.py` — Add 4 new @mcp.tool functions for tier3 write operations
- `tests/test_server.py` — Add tests for write tool registration and validation
- `scripts/verify_s04.sh` — Create verification script for tier3 tools

### SDK Methods Available

From `mistapi.api.v1.orgs` modules:

**WLANs (`wlans` module):**
- `updateOrgWlan(session, org_id, wlan_id, body)` — Update WLAN configuration

**NAC Rules (`nacrules` module):**
- `createOrgNacRule(session, org_id, body)` — Create new NAC rule
- `updateOrgNacRule(session, org_id, nacrule_id, body)` — Update existing NAC rule
- `deleteOrgNacRule(session, org_id, nacrule_id)` — Delete NAC rule

**WXLAN Rules (`wxrules` module):**
- `createOrgWxRule(session, org_id, body)` — Create WXLAN microsegmentation rule
- `updateOrgWxRule(session, org_id, wxrule_id, body)` — Update WXLAN rule
- `deleteOrgWxRule(session, org_id, wxrule_id)` — Delete WXLAN rule

**Security Policies (`secpolicies` module):**
- `createOrgSecPolicy(session, org_id, body)` — Create security policy
- `updateOrgSecPolicy(session, org_id, secpolicy_id, body)` — Update security policy
- `deleteOrgSecPolicy(session, org_id, secpolicy_id)` — Delete security policy

### Tool Signatures (Recommended)

```python
@mcp.tool
async def mist_update_wlan(
    ctx: Context,
    org: str,
    wlan_id: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    """Update an existing WLAN (SSID) configuration.
    
    Modifies settings for an existing WLAN including security,
    broadcasting, and access policies.
    """

@mcp.tool
async def mist_manage_nac_rules(
    ctx: Context,
    org: str,
    action: str,  # "create", "update", "delete"
    rule_id: str | None = None,  # Required for update/delete
    body: dict[str, Any] | None = None,  # Required for create/update
) -> dict[str, Any]:
    """Manage NAC (802.1X) rules for network access control.
    
    Create, update, or delete NAC rules that control device
    authentication and network access policies.
    """

@mcp.tool
async def mist_manage_wxlan(
    ctx: Context,
    org: str,
    action: str,  # "create", "update", "delete"
    rule_id: str | None = None,  # Required for update/delete
    body: dict[str, Any] | None = None,  # Required for create/update
) -> dict[str, Any]:
    """Manage WXLAN microsegmentation rules.
    
    Configure microsegmentation policies for zero-trust
    network segmentation and traffic control.
    """

@mcp.tool
async def mist_manage_security_policies(
    ctx: Context,
    org: str,
    action: str,  # "create", "update", "delete"
    policy_id: str | None = None,  # Required for update/delete
    body: dict[str, Any] | None = None,  # Required for create/update
) -> dict[str, Any]:
    """Manage organization security policies.
    
    Create, update, or delete security policies that define
    firewall rules, threat prevention, and compliance settings.
    """
```

### Build Order

1. **T01: WLAN update tool** — Simplest write operation (single update method), establishes pattern
2. **T02: NAC rules management** — Multi-action tool (create/update/delete) with validation
3. **T03: WXLAN management** — Similar pattern to NAC rules
4. **T04: Security policies + tests** — Most complex, comprehensive tests, verification script

Each task unblocks the next by establishing the multi-action tool pattern.

### Verification Approach

1. **Tool registration**: `python3 -c "import asyncio; from mist_mcp.server import mcp; print([t.name for t in asyncio.run(mcp.list_tools())])"` — verify 14 tools (10 existing + 4 new)
2. **CLI flag**: `python3 -m mist_mcp.server --help` — verify `--enable-write-tools` flag exists (already implemented)
3. **Unit tests**: `pytest tests/test_server.py -v` — verify all tests pass
4. **Verification script**: `bash scripts/verify_s04.sh` — comprehensive verification

## Constraints

- **Action parameter validation**: Must validate `action` is one of "create", "update", "delete"
- **Conditional required parameters**: `rule_id`/`policy_id` required for update/delete; `body` required for create/update
- **Response serialization**: Must use existing `serialize_api_response()` helper
- **Org validation**: Must use existing `validate_org()` helper
- **Session management**: Must use existing `session_manager.get_session()`

## Common Pitfalls

- **Missing body for create/update**: Return clear error if `body` is None when required
- **Missing ID for update/delete**: Return clear error if `rule_id`/`policy_id` is None when required
- **Case-sensitive action**: Normalize action to lowercase for comparison
- **Mist API body format**: Ensure body is a dict, not JSON string — SDK handles serialization

## Open Risks

- **SDK validation**: Mist API may reject bodies with missing required fields; error handling should expose SDK error details via `serialize_api_response`
- **Destructive operations**: Delete operations are irreversible; S05 will add safety layer but S04 should document this in tool descriptions

## Sources

- mistapi SDK documentation via `help(mistapi.api.v1.orgs.wlans)` etc.
- S03 forward intelligence: tier2 config viewing tools provide read-before-write pattern
- Decision D014: Response serialization pattern established in S02
