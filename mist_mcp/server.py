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
