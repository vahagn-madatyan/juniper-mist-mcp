"""Entry point for running the server as a module or console script.

Usage:
    python -m mist_mcp.server [options]
    juniper-mist-mcp [options]
"""

from mist_mcp.server import main

if __name__ == "__main__":
    main()
