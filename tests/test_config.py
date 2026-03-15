"""Unit tests for mist_mcp.config module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mist_mcp.config import (
    DEFAULT_REGION,
    KNOWN_MIST_REGIONS,
    TOKEN_PREFIX,
    REGION_PREFIX,
    Config,
    OrgConfig,
)


class TestConfig:
    """Tests for the Config class."""

    def test_parsing_multiple_orgs(self):
        """Test parsing configuration with multiple organizations."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("MIST_TOKEN_org1=token1\n")
            f.write("MIST_REGION_org1=api.mist.com\n")
            f.write("MIST_TOKEN_org2=token2\n")
            f.write("MIST_REGION_org2=api.eu.mist.com\n")
            env_path = f.name

        try:
            config = Config(env_path)
            assert len(config.orgs) == 2
            assert "org1" in config.orgs
            assert "org2" in config.orgs

            org1 = config.get_org("org1")
            assert org1 is not None
            assert org1.token == "token1"
            assert org1.region == "api.mist.com"

            org2 = config.get_org("org2")
            assert org2 is not None
            assert org2.token == "token2"
            assert org2.region == "api.eu.mist.com"
        finally:
            os.unlink(env_path)

    def test_missing_region_fallback(self):
        """Test that missing region defaults to api.mist.com."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("MIST_TOKEN_myorg=my_token\n")
            # No MIST_REGION_myorg defined
            env_path = f.name

        try:
            config = Config(env_path)
            assert "myorg" in config.orgs
            org = config.get_org("myorg")
            assert org is not None
            assert org.region == DEFAULT_REGION
        finally:
            os.unlink(env_path)

    def test_invalid_region_warning(self, caplog):
        """Test that invalid region logs a warning but doesn't fail."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("MIST_TOKEN_badorg=bad_token\n")
            f.write("MIST_REGION_badorg=api.invalid-region.com\n")
            env_path = f.name

        try:
            config = Config(env_path)
            assert "badorg" in config.orgs
            org = config.get_org("badorg")
            assert org is not None
            assert org.region == "api.invalid-region.com"

            # Check that warning was logged
            assert any(
                "Unknown region" in record.message
                for record in caplog.records
                if record.levelname == "WARNING"
            )
        finally:
            os.unlink(env_path)

    def test_empty_env_file(self):
        """Test handling of empty .env file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("# Just a comment\n")
            env_path = f.name

        try:
            config = Config(env_path)
            assert len(config.orgs) == 0
        finally:
            os.unlink(env_path)

    def test_missing_token(self):
        """Test that orgs without tokens are not included."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            # Only have region, no token - should be ignored
            f.write("MIST_REGION_nametoken=api.mist.com\n")
            f.write("MIST_TOKEN_validorg=valid_token\n")
            env_path = f.name

        try:
            config = Config(env_path)
            # Only validorg should be present
            assert config.orgs == ["validorg"]
        finally:
            os.unlink(env_path)

    def test_file_not_found(self):
        """Test that missing .env file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError) as exc_info:
            Config("/nonexistent/path/.env")

        assert "Configuration file not found" in str(exc_info.value)

    def test_all_known_regions(self):
        """Test that all known regions are accepted without warning."""
        for region in KNOWN_MIST_REGIONS:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".env", delete=False
            ) as f:
                f.write(f"MIST_TOKEN_testorg=test_token\n")
                f.write(f"MIST_REGION_testorg={region}\n")
                env_path = f.name

            try:
                config = Config(env_path)
                org = config.get_org("testorg")
                assert org is not None
                assert org.region == region
            finally:
                os.unlink(env_path)

    def test_orgs_sorted(self):
        """Test that orgs are returned sorted alphabetically."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("MIST_TOKEN_zebra=token_z\n")
            f.write("MIST_TOKEN_apple=token_a\n")
            f.write("MIST_TOKEN_mango=token_m\n")
            env_path = f.name

        try:
            config = Config(env_path)
            assert config.orgs == ["apple", "mango", "zebra"]
        finally:
            os.unlink(env_path)

    def test_get_all_orgs(self):
        """Test get_all_orgs returns OrgConfig objects."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("MIST_TOKEN_testorg1=tok1\n")
            f.write("MIST_TOKEN_testorg2=tok2\n")
            env_path = f.name

        try:
            config = Config(env_path)
            all_orgs = config.get_all_orgs()

            assert len(all_orgs) == 2
            assert all(isinstance(org, OrgConfig) for org in all_orgs)
            assert all(org.token.startswith("tok") for org in all_orgs)
        finally:
            os.unlink(env_path)

    def test_empty_token_value(self):
        """Test that empty token values are ignored."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("MIST_TOKEN_emptyorg=\n")
            f.write("MIST_TOKEN_realorg=real_token\n")
            env_path = f.name

        try:
            config = Config(env_path)
            # Only realorg should be present (empty token ignored)
            assert config.orgs == ["realorg"]
        finally:
            os.unlink(env_path)
