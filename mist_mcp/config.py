"""Configuration loader for Juniper Mist MCP Server.

Loads organization configuration from .env files using prefix-based naming:
- MIST_TOKEN_<ORGNAME>: API token for the organization
- MIST_REGION_<ORGNAME>: Regional API endpoint (optional, defaults to api.mist.com)
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Known Mist cloud regional hosts
KNOWN_MIST_REGIONS = frozenset(
    [
        "api.mist.com",
        "api.eu.mist.com",
        "api.gc1.mist.com",
        "api.gc2.mist.com",
        "api.ac2.mist.com",
    ]
)

DEFAULT_REGION = "api.mist.com"

TOKEN_PREFIX = "MIST_TOKEN_"
REGION_PREFIX = "MIST_REGION_"


@dataclass
class OrgConfig:
    """Configuration for a single organization."""

    name: str
    token: str
    region: str


class Config:
    """Loads and validates Mist organization configuration from .env file."""

    def __init__(self, env_file: str | Path = ".env"):
        """Initialize configuration from .env file.

        Args:
            env_file: Path to the .env file to load.

        Raises:
            FileNotFoundError: If the specified env file does not exist.
        """
        self._env_file = Path(env_file)

        if not self._env_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self._env_file}. "
                "Please create a .env file based on .env.example"
            )

        # Load environment variables from .env file (only from this file, not merging with existing env)
        env_vars = dotenv_values(self._env_file)

        self._orgs: dict[str, OrgConfig] = {}
        self._load_orgs(env_vars)

    def _load_orgs(self, env_vars: dict) -> None:
        """Parse environment variables to extract organization configurations."""
        # Find all MIST_TOKEN_* variables
        for key, value in env_vars.items():
            if value is None:  # Skip keys without values
                continue
            if key.startswith(TOKEN_PREFIX) and value:
                org_name = key[len(TOKEN_PREFIX) :]

                # Look for corresponding region variable
                region_key = f"{REGION_PREFIX}{org_name}"
                region = env_vars.get(region_key) or DEFAULT_REGION

                # Validate region
                if region not in KNOWN_MIST_REGIONS:
                    logger.warning(
                        f"Unknown region '{region}' for org '{org_name}'. "
                        f"Known regions: {', '.join(KNOWN_MIST_REGIONS)}. "
                        f"Using anyway (will likely fail at API call time)."
                    )

                self._orgs[org_name] = OrgConfig(
                    name=org_name,
                    token=value,
                    region=region,
                )

        # Log loaded orgs (without tokens)
        if self._orgs:
            org_names = list(self._orgs.keys())
            logger.info(f"Loaded {len(org_names)} organization(s): {org_names}")
        else:
            logger.warning(
                "No organizations configured. "
                f"Add MIST_TOKEN_<ORGNAME> variables to {self._env_file}"
            )

    @property
    def orgs(self) -> list[str]:
        """Return list of configured organization names.

        Returns:
            List of organization names sorted alphabetically.
        """
        return sorted(self._orgs.keys())

    def get_org(self, name: str) -> Optional[OrgConfig]:
        """Get configuration for a specific organization.

        Args:
            name: Organization name (case-sensitive, matches the suffix of MIST_TOKEN_*).

        Returns:
            OrgConfig if found, None otherwise.
        """
        return self._orgs.get(name)

    def get_all_orgs(self) -> list[OrgConfig]:
        """Get all organization configurations.

        Returns:
            List of OrgConfig objects sorted by organization name.
        """
        return [self._orgs[name] for name in self.orgs]
