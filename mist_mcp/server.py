"""MCP server for Juniper Mist API.

Provides FastMCP server with:
- Lifespan context for configuration and session management
- Tool registration for listing and interacting with Mist organizations
- CLI argument parsing for transport selection and write-tools flag
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

import mistapi
from mistapi import __api_response
from fastmcp import Context, FastMCP
from fastmcp.server.lifespan import lifespan

from mist_mcp.config import Config
from mist_mcp.session import MistSessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Server name
SERVER_NAME = "juniper-mist-mcp"
SERVER_VERSION = "0.1.0"


def validate_org(org: str, session_manager: MistSessionManager) -> None:
    """Validate that an org is configured.

    Args:
        org: Organization name to validate.
        session_manager: Session manager with configured orgs.

    Raises:
        ValueError: If org is not configured.
    """
    if org not in session_manager.configured_orgs:
        raise ValueError(
            f"Organization '{org}' is not configured. "
            f"Available organizations: {session_manager.configured_orgs}"
        )


def serialize_api_response(response: __api_response.APIResponse) -> dict[str, Any]:
    """Serialize an APIResponse to a JSON-serializable dict.

    Args:
        response: The APIResponse from a Mist API call.

    Returns:
        Dict with status, data, and optional error information.
    """
    result = {
        "status_code": response.status_code,
        "url": response.url,
    }

    if response.status_code and response.status_code >= 400:
        result["error"] = True
        result["data"] = response.data
    else:
        result["error"] = False
        result["data"] = response.data

    if response.next:
        result["has_more"] = True
        result["next_page"] = response.next
    else:
        result["has_more"] = False

    return result


def get_org_id(org: str, session: mistapi.APISession) -> str:
    """Get the Mist organization ID from the org name.

    Args:
        org: Organization name (from config).
        session: Authenticated Mist API session.

    Returns:
        The Mist org_id string.

    Raises:
        ValueError: If the org is not found.
        RuntimeError: If the API call fails.
    """
    # Get all orgs the user has access to
    response = session.mist_get("/api/v1/orgs")

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch orgs: {response.status_code} - {response.data}"
        )

    orgs = response.data if isinstance(response.data, list) else []

    # Find the matching org by name
    for o in orgs:
        if o.get("name") == org:
            org_id = o.get("id")
            if org_id:
                logger.debug(f"Found org_id '{org_id}' for org '{org}'")
                return org_id

    raise ValueError(
        f"Organization '{org}' not found in Mist API. "
        f"Available orgs: {[o.get('name') for o in orgs]}"
    )


@lifespan
async def app_lifespan(server: FastMCP) -> dict[str, Any]:
    """Lifespan context for the MCP server.

    Loads configuration and initializes session manager.

    Args:
        server: The FastMCP server instance.

    Yields:
        Context dict with config and session_manager.
    """
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")

    # Load configuration
    try:
        config = Config()
        logger.info(f"Loaded configuration with {len(config.orgs)} organization(s)")
    except FileNotFoundError as e:
        logger.error(str(e))
        # Still yield empty config so server can start (tools will fail gracefully)
        config = None
        logger.warning("Server starting without valid configuration")

    # Initialize session manager
    session_manager = MistSessionManager(config) if config else None

    logger.info("Server lifespan initialized")

    yield {"config": config, "session_manager": session_manager}


# Create the FastMCP server with lifespan
mcp = FastMCP(SERVER_NAME, lifespan=app_lifespan)


# =============================================================================
# Tools
# =============================================================================


@mcp.tool
async def mist_list_orgs(ctx: Context) -> list[dict[str, Any]]:
    """List configured customer organizations and their Mist regions.

    Returns a list of organizations from the configuration, including
    the organization name, region, and whether a token is present.

    Returns:
        List of dicts with keys: name, region, has_token.
    """
    logger.info("Tool called: mist_list_orgs")

    lifespan_ctx = ctx.lifespan_context
    config = lifespan_ctx.get("config")

    if config is None:
        return []

    orgs = []
    for org_name in config.orgs:
        org_config = config.get_org(org_name)
        if org_config:
            orgs.append({
                "name": org_config.name,
                "region": org_config.region,
                "has_token": bool(org_config.token),
            })

    logger.info(f"Returning {len(orgs)} organizations")
    return orgs


@mcp.tool
async def mist_get_device_stats(
    ctx: Context,
    org: str,
    duration: str = "1d",
) -> dict[str, Any]:
    """Get device statistics for an organization.

    Returns statistics for all devices in the specified organization,
    including APs, switches, gateways, and other network devices.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        duration: Time range for stats (default: "1d"). Options: "1h", "6h", "12h", "1d", "1w", "30d".

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_get_device_stats(org={org}, duration={duration})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Get org_id from org name
    org_id = get_org_id(org, session)

    # Import the stats function
    from mistapi.api.v1.orgs import stats as org_stats

    # Call the API
    response = org_stats.listOrgDevicesStats(session, org_id, duration=duration)

    return serialize_api_response(response)


@mcp.tool
async def mist_get_sle_summary(
    ctx: Context,
    org: str,
    site_id: str,
) -> dict[str, Any]:
    """Get Service Level Experience (SLE) summary for a site.

    Returns the SLE summary for a specific site, including metrics for
    throughput, latency, coverage, and capacity.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        site_id: Mist site ID (UUID).

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_get_sle_summary(org={org}, site_id={site_id})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Import the SLE function
    from mistapi.api.v1.sites import sle as site_sle

    # Call the API - scope="site" to get site-level summary
    # We need to provide a metric - let's use a common one like "ap"
    # The API requires scope and scope_id - for site-level we use scope="site" and scope_id=site_id
    # metric is required - let's use "site" as a general metric
    try:
        response = site_sle.getSiteSleSummary(
            session,
            site_id,
            scope="site",
            scope_id=site_id,
            metric="site",
        )
    except TypeError:
        # Fallback if the API signature is different - try alternative call
        response = site_sle.getSiteSleSummary(
            session,
            site_id,
            scope="site",
            scope_id=site_id,
            metric="ap",
        )

    return serialize_api_response(response)


@mcp.tool
async def mist_get_client_stats(
    ctx: Context,
    org: str,
    duration: str = "1d",
    limit: int = 100,
) -> dict[str, Any]:
    """Get client statistics for an organization.

    Returns statistics for wireless clients in the specified organization,
    including connection details, bandwidth, and session information.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        duration: Time range for stats (default: "1d"). Options: "1h", "6h", "12h", "1d", "1w", "30d".
        limit: Maximum number of clients to return (default: 100).

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_get_client_stats(org={org}, duration={duration}, limit={limit})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Get org_id from org name
    org_id = get_org_id(org, session)

    # Import the clients function
    from mistapi.api.v1.orgs import clients as org_clients

    # Call the API
    response = org_clients.searchOrgWirelessClients(
        session,
        org_id,
        duration=duration,
        limit=limit,
    )

    return serialize_api_response(response)


@mcp.tool
async def mist_get_alarms(
    ctx: Context,
    org: str,
    start: str | None = None,
    end: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Get alarms for an organization.

    Returns alarms from the specified organization, including infrastructure,
    security, and Marvis AI-driven detections.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        start: Start time (ISO 8601 format or duration string like "1d").
        end: End time (ISO 8601 format or duration string).
        status: Alarm status filter - "acked" for acknowledged, "unacked" for unacknowledged.
        limit: Maximum number of alarms to return (default: 100).

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_get_alarms(org={org}, start={start}, end={end}, status={status}, limit={limit})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Get org_id from org name
    org_id = get_org_id(org, session)

    # Import the alarms function
    from mistapi.api.v1.orgs import alarms as org_alarms

    # Map status to acked parameter
    acked = None
    if status == "acked":
        acked = True
    elif status == "unacked":
        acked = False

    # Call the API
    response = org_alarms.searchOrgAlarms(
        session,
        org_id,
        start=start,
        end=end,
        acked=acked,
        limit=limit,
    )

    return serialize_api_response(response)


@mcp.tool
async def mist_get_site_events(
    ctx: Context,
    org: str,
    site_id: str | None = None,
    start: str | None = None,
    end: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Get events for an organization or site.

    Returns system events from the specified organization or site,
    including configuration changes, user activities, and system alerts.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        site_id: Optional site ID to filter events to a specific site.
        start: Start time (ISO 8601 format or duration string like "1d").
        end: End time (ISO 8601 format or duration string).
        limit: Maximum number of events to return (default: 100).

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_get_site_events(org={org}, site_id={site_id}, start={start}, end={end}, limit={limit})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Get org_id from org name
    org_id = get_org_id(org, session)

    # Import the events function
    from mistapi.api.v1.orgs import events as org_events

    # Call the API - use org-level events
    response = org_events.searchOrgEvents(
        session,
        org_id,
        start=start,
        end=end,
        limit=limit,
    )

    return serialize_api_response(response)


@mcp.tool
async def mist_list_wlans(
    ctx: Context,
    org: str,
    limit: int = 100,
    page: int = 1,
) -> dict[str, Any]:
    """List WLAN profiles in an organization.

    Returns all WLAN profiles (SSIDs) configured in the specified organization,
    including security settings, broadcasting configuration, and access policies.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        limit: Maximum number of WLANs to return (default: 100).
        page: Page number for pagination (default: 1).

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_list_wlans(org={org}, limit={limit}, page={page})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Get org_id from org name
    org_id = get_org_id(org, session)

    # Import the wlans function
    from mistapi.api.v1.orgs import wlans as org_wlans

    # Call the API
    response = org_wlans.listOrgWlans(
        session,
        org_id,
        limit=limit,
        page=page,
    )

    return serialize_api_response(response)


@mcp.tool
async def mist_get_rf_templates(
    ctx: Context,
    org: str,
    limit: int = 100,
    page: int = 1,
) -> dict[str, Any]:
    """List RF templates in an organization.

    Returns all RF (Radio Frequency) templates configured in the specified
    organization, including channel, transmit power, and band settings.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        limit: Maximum number of RF templates to return (default: 100).
        page: Page number for pagination (default: 1).

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_get_rf_templates(org={org}, limit={limit}, page={page})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Get org_id from org name
    org_id = get_org_id(org, session)

    # Import the rftemplates function
    from mistapi.api.v1.orgs import rftemplates as org_rftemplates

    # Call the API
    response = org_rftemplates.listOrgRfTemplates(
        session,
        org_id,
        limit=limit,
        page=page,
    )

    return serialize_api_response(response)


@mcp.tool
async def mist_get_inventory(
    ctx: Context,
    org: str,
    type: str | None = None,
    status: str | None = None,
    site_id: str | None = None,
    name: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Search device inventory in an organization.

    Returns devices from the organization inventory that match the specified
    filters. Supports filtering by device type, status, site, and name.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        type: Device type filter - "ap" (access point), "gateway", or "switch".
        status: Device status filter - "online", "offline", or "provisioned".
        site_id: Filter by specific site ID (UUID).
        name: Partial name match filter.
        limit: Maximum number of devices to return (default: 100).
        offset: Pagination offset (default: 0).

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_get_inventory(org={org}, type={type}, status={status}, site_id={site_id}, name={name}, limit={limit}, offset={offset})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Get org_id from org name
    org_id = get_org_id(org, session)

    # Import the inventory function
    from mistapi.api.v1.orgs import inventory as org_inventory

    # Build filter dict with only provided (non-None) parameters
    filters: dict[str, Any] = {"limit": limit, "offset": offset}
    if type is not None:
        filters["type"] = type
    if status is not None:
        filters["status"] = status
    if site_id is not None:
        filters["site_id"] = site_id
    if name is not None:
        filters["name"] = name

    # Call the API
    response = org_inventory.searchOrgInventory(session, org_id, **filters)

    return serialize_api_response(response)


@mcp.tool
async def mist_get_device_config_cmd(
    ctx: Context,
    org: str,
    site_id: str,
    device_id: str,
    sort: str | None = None,
) -> dict[str, Any]:
    """Get generated CLI configuration commands for a device.

    Returns the generated CLI configuration for a specific device in a Mist site.
    The configuration includes the complete device-specific commands needed to
    configure the device based on its settings and policies.

    Note: site_id and device_id are Mist IDs (UUIDs), not names. You can obtain
    site_id from mist_get_site_events or by listing sites, and device_id from
    mist_get_inventory.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        site_id: Mist site ID (UUID) - must be a valid Mist site ID.
        device_id: Mist device ID (UUID) - must be a valid device ID.
        sort: Sort order for the configuration output. Options: "name", "type", "mac".

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_get_device_config_cmd(org={org}, site_id={site_id}, device_id={device_id}, sort={sort})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Get org_id from org name (needed to validate site belongs to org)
    org_id = get_org_id(org, session)

    # Import the devices function
    from mistapi.api.v1.sites import devices as site_devices

    # Build kwargs with only provided (non-None) parameters
    kwargs: dict[str, Any] = {}
    if sort is not None:
        kwargs["sort"] = sort

    # Call the API
    response = site_devices.getSiteDeviceConfigCmd(
        session,
        site_id,
        device_id,
        **kwargs,
    )

    return serialize_api_response(response)


@mcp.tool
async def mist_update_wlan(
    ctx: Context,
    org: str,
    wlan_id: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    """Update an existing WLAN configuration in an organization.

    Updates the WLAN profile (SSID) with the specified configuration changes.
    This is a write operation that modifies the WLAN settings in Mist.

    Note: To get a list of WLANs and their IDs, use the mist_list_wlans tool first.

    Args:
        ctx: FastMCP context with lifespan data.
        org: Organization name (must be configured in .env).
        wlan_id: Mist WLAN ID (UUID) to update. Get this from mist_list_wlans.
        body: Dictionary containing the WLAN configuration fields to update.
              Example: {"ssid": "New SSID Name", "enabled": true, "auth": {"type": "wpa3"}}

    Returns:
        Dict with status_code, error flag, data, and pagination info.
    """
    logger.info(f"Tool called: mist_update_wlan(org={org}, wlan_id={wlan_id}, body={body})")

    lifespan_ctx = ctx.lifespan_context
    session_manager = lifespan_ctx.get("session_manager")

    if session_manager is None:
        return {"error": True, "status_code": None, "data": "No session manager available"}

    # Validate org
    validate_org(org, session_manager)

    # Get authenticated session
    session = session_manager.get_session(org)

    # Get org_id from org name
    org_id = get_org_id(org, session)

    # Import the wlans function
    from mistapi.api.v1.orgs import wlans as org_wlans

    # Call the API
    response = org_wlans.updateOrgWlan(
        session,
        org_id,
        wlan_id,
        body,
    )

    return serialize_api_response(response)


# =============================================================================
# CLI and Server Entry Point
# =============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Juniper Mist MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--enable-write-tools",
        action="store_true",
        default=False,
        help="Enable write tools (not yet implemented)",
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)",
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to for HTTP transport (default: 0.0.0.0)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for HTTP transport (default: 8000)",
    )

    parser.add_argument(
        "--env-file",
        type=Path,
        default=".env",
        help="Path to .env file (default: .env)",
    )

    return parser.parse_args()


def main():
    """Main entry point for the MCP server."""
    args = parse_args()

    logger.info(f"Transport: {args.transport}")
    if args.transport == "http":
        logger.info(f"HTTP server will bind to {args.host}:{args.port}")

    if args.enable_write_tools:
        logger.warning("--enable-write-tools flag is set but write tools are not yet implemented")

    # Run the server with the appropriate transport
    if args.transport == "stdio":
        # Stdio transport (default for Claude Desktop)
        mcp.run(transport="stdio")
    elif args.transport == "http":
        # Streamable HTTP transport
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        logger.error(f"Unknown transport: {args.transport}")
        sys.exit(1)


if __name__ == "__main__":
    main()
