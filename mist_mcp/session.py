"""Mist API session management with caching.

Provides MistSessionManager that:
- Creates and caches mistapi.APISession instances per organization
- Uses mistapi's built-in retry logic for rate-limit (429) responses
- Validates org existence before returning sessions
"""

import logging
from typing import Any

import mistapi

from mist_mcp.config import Config, OrgConfig

logger = logging.getLogger(__name__)


class MistSessionManager:
    """Manages Mist API sessions with caching.

    Caches authenticated sessions per organization to avoid repeated
    authentication. Rate-limit retry is handled natively by mistapi
    (3 retries with exponential backoff).
    """

    def __init__(self, config: Config):
        """Initialize the session manager.

        Args:
            config: Configuration object with org details.
        """
        self._config = config
        self._sessions: dict[str, mistapi.APISession] = {}
        logger.info("MistSessionManager initialized")

    def _create_session(self, org_config: OrgConfig) -> mistapi.APISession:
        """Create a new Mist API session for an organization.

        Args:
            org_config: Organization configuration with token and region.

        Returns:
            Authenticated APISession instance.

        Raises:
            RuntimeError: If authentication fails.
        """
        # Create session with host and token directly
        session = mistapi.APISession()
        session.host = org_config.region
        session.apitoken = org_config.token

        # Attempt login to validate the token (this may raise if invalid)
        try:
            session.login()
            logger.info(f"Successfully authenticated to Mist API for org: {org_config.name}")
        except Exception as e:
            logger.error(
                f"Authentication failed for org '{org_config.name}': {e}"
            )
            raise RuntimeError(
                f"Authentication failed for org '{org_config.name}': {e}"
            ) from e

        return session

    def get_session(self, org: str) -> mistapi.APISession:
        """Get or create a cached session for the specified organization.

        Args:
            org: Organization name (matches MIST_TOKEN_* suffix).

        Returns:
            Authenticated APISession for the organization.

        Raises:
            ValueError: If the organization is not configured.
        """
        # Validate org exists in config
        org_config = self._config.get_org(org)
        if org_config is None:
            available_orgs = self._config.orgs
            raise ValueError(
                f"Organization '{org}' is not configured. "
                f"Available organizations: {available_orgs}"
            )

        # Return cached session if available
        if org in self._sessions:
            logger.debug(f"Returning cached session for org: {org}")
            return self._sessions[org]

        # Create and cache new session
        logger.info(f"Creating new session for org: {org}")
        session = self._create_session(org_config)
        self._sessions[org] = session

        return session

    def get_all_sessions(self) -> dict[str, mistapi.APISession]:
        """Get all cached sessions.

        Returns:
            Dictionary mapping org names to their sessions.
        """
        return self._sessions.copy()

    @property
    def configured_orgs(self) -> list[str]:
        """Get list of configured organization names.

        Returns:
            Sorted list of org names.
        """
        return self._config.orgs
