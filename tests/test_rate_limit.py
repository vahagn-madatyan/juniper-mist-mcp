"""Behavioral tests for rate limit handling and success tracking.

These tests verify:
- Rate limit handling (429 responses) are properly serialized with error=True
- Success tracking includes all metadata (status_code, error, data, has_more, next_page)
- Pagination works correctly in serialize_api_response
- Error handling for 4xx and 5xx responses
- Edge cases for missing fields in APIResponse
"""

import pytest
from unittest.mock import MagicMock, patch
from mistapi import __api_response
from mist_mcp.server import serialize_api_response


# =============================================================================
# Test Helper Functions
# =============================================================================


def create_mock_api_response(
    status_code: int,
    data: any,
    url: str = "https://api.mist.com/api/v1/test",
    next_url: str | None = None,
) -> MagicMock:
    """Create a mock APIResponse with specified properties.

    Args:
        status_code: HTTP status code (e.g., 200, 429, 500).
        data: Response data (dict, list, or error message).
        url: The URL that was called.
        next_url: Next page URL for pagination (None for no pagination).

    Returns:
        MagicMock with spec=APIResponse.
    """
    mock_response = MagicMock(spec=__api_response.APIResponse)
    mock_response.status_code = status_code
    mock_response.url = url
    mock_response.data = data
    mock_response.next = next_url
    return mock_response


def create_mock_session() -> MagicMock:
    """Create a mock Mist API session.

    Returns:
        MagicMock representing a mistapi.APISession.
    """
    mock_session = MagicMock()
    return mock_session


def create_mock_context(org_name: str = "example_org") -> MagicMock:
    """Create a mock FastMCP context with session manager.

    Args:
        org_name: Organization name for the mock config.

    Returns:
        MagicMock with lifespan_context containing config and session_manager.
    """
    from mist_mcp.config import Config
    from mist_mcp.session import MistSessionManager
    from pathlib import Path

    # Create a mock config and session manager
    config = Config(env_file=Path(__file__).parent.parent / ".env")
    session_manager = MistSessionManager(config)

    mock_ctx = MagicMock()
    mock_ctx.lifespan_context = {
        "config": config,
        "session_manager": session_manager,
    }
    return mock_ctx


# =============================================================================
# Rate Limit Tests (429 Response)
# =============================================================================


class TestRateLimitHandling:
    """Tests for HTTP 429 (Rate Limit) response handling."""

    def test_rate_limit_429_response(self):
        """Test that 429 rate limit responses are properly serialized.

        Verifies:
        - status_code is 429
        - error is True
        - error data is preserved
        """
        # Create mock 429 response
        mock_response = create_mock_api_response(
            status_code=429,
            data={"error": "Rate limit exceeded", "message": "Too many requests"},
            url="https://api.mist.com/api/v1/orgs/abc/devices/stats",
        )

        # Serialize the response
        result = serialize_api_response(mock_response)

        # Verify rate limit handling
        assert result["status_code"] == 429, f"Expected status_code=429, got {result['status_code']}"
        assert result["error"] is True, f"Expected error=True for 429, got {result['error']}"
        assert result["data"] == {"error": "Rate limit exceeded", "message": "Too many requests"}
        assert "url" in result

    def test_rate_limit_429_with_retry_after(self):
        """Test 429 response with Retry-After header data."""
        # Create mock 429 with retry info
        mock_response = create_mock_api_response(
            status_code=429,
            data={
                "error": "Rate limit exceeded",
                "retry_after": 60,
                "limit": "5000/hour",
            },
            url="https://api.mist.com/api/v1/orgs/abc/stats",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 429
        assert result["error"] is True
        assert result["data"]["retry_after"] == 60
        assert result["data"]["limit"] == "5000/hour"

    def test_rate_limit_429_empty_data(self):
        """Test 429 response with empty error data."""
        mock_response = create_mock_api_response(
            status_code=429,
            data=None,
            url="https://api.mist.com/api/v1/test",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 429
        assert result["error"] is True
        assert result["data"] is None


# =============================================================================
# Success Tracking Tests
# =============================================================================


class TestSuccessTracking:
    """Tests for success response handling and metadata tracking."""

    def test_success_tracking_with_pagination(self):
        """Test that successful response with pagination is correctly serialized.

        Verifies:
        - has_more is True when next URL is present
        - next_page contains the pagination URL
        - error is False for 2xx responses
        - data is preserved
        """
        # Create mock successful response with pagination
        mock_response = create_mock_api_response(
            status_code=200,
            data=[{"id": 1}, {"id": 2}, {"id": 3}],
            url="https://api.mist.com/api/v1/orgs/abc/devices",
            next_url="https://api.mist.com/api/v1/orgs/abc/devices?page=2",
        )

        result = serialize_api_response(mock_response)

        # Verify success tracking with pagination
        assert result["status_code"] == 200, f"Expected status_code=200, got {result['status_code']}"
        assert result["error"] is False, f"Expected error=False for 200, got {result['error']}"
        assert result["data"] == [{"id": 1}, {"id": 2}, {"id": 3}]
        assert result["has_more"] is True, f"Expected has_more=True, got {result.get('has_more')}"
        assert result["next_page"] == "https://api.mist.com/api/v1/orgs/abc/devices?page=2"

    def test_success_tracking_without_pagination(self):
        """Test that successful response without pagination has has_more=False.

        Verifies:
        - has_more is False when no next URL
        - next_page is not present
        - error is False for 2xx responses
        """
        # Create mock successful response without pagination
        mock_response = create_mock_api_response(
            status_code=200,
            data={"status": "ok", "count": 5},
            url="https://api.mist.com/api/v1/orgs/abc/summary",
            next_url=None,
        )

        result = serialize_api_response(mock_response)

        # Verify success tracking without pagination
        assert result["status_code"] == 200
        assert result["error"] is False
        assert result["data"] == {"status": "ok", "count": 5}
        assert result["has_more"] is False, f"Expected has_more=False, got {result.get('has_more')}"
        assert "next_page" not in result, "next_page should not be present when has_more=False"

    def test_success_201_created(self):
        """Test that 201 Created is treated as success."""
        mock_response = create_mock_api_response(
            status_code=201,
            data={"id": "new-resource-id", "created": True},
            url="https://api.mist.com/api/v1/orgs/abc/wlans",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 201
        assert result["error"] is False
        assert result["data"]["id"] == "new-resource-id"

    def test_success_204_no_content(self):
        """Test that 204 No Content is handled correctly."""
        mock_response = create_mock_api_response(
            status_code=204,
            data=None,
            url="https://api.mist.com/api/v1/orgs/abc/settings",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 204
        assert result["error"] is False
        assert result["data"] is None


# =============================================================================
# Error Handling Tests (4xx and 5xx)
# =============================================================================


class TestErrorHandling:
    """Tests for error response handling (4xx and 5xx)."""

    def test_error_handling_400_bad_request(self):
        """Test 400 Bad Request error handling."""
        mock_response = create_mock_api_response(
            status_code=400,
            data={"error": "Bad Request", "details": "Invalid parameter 'duration'"},
            url="https://api.mist.com/api/v1/orgs/abc/devices/stats",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 400
        assert result["error"] is True
        assert "Bad Request" in str(result["data"])

    def test_error_handling_401_unauthorized(self):
        """Test 401 Unauthorized error handling."""
        mock_response = create_mock_api_response(
            status_code=401,
            data={"error": "Unauthorized", "message": "Invalid or expired token"},
            url="https://api.mist.com/api/v1/orgs",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 401
        assert result["error"] is True
        assert "Unauthorized" in str(result["data"])

    def test_error_handling_403_forbidden(self):
        """Test 403 Forbidden error handling."""
        mock_response = create_mock_api_response(
            status_code=403,
            data={"error": "Forbidden", "message": "Insufficient permissions"},
            url="https://api.mist.com/api/v1/orgs/abc/admin",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 403
        assert result["error"] is True

    def test_error_handling_404_not_found(self):
        """Test 404 Not Found error handling."""
        mock_response = create_mock_api_response(
            status_code=404,
            data={"error": "Not Found", "message": "Resource does not exist"},
            url="https://api.mist.com/api/v1/orgs/abc/sites/nonexistent",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 404
        assert result["error"] is True

    def test_error_handling_500_internal_server_error(self):
        """Test 500 Internal Server Error handling."""
        mock_response = create_mock_api_response(
            status_code=500,
            data={"error": "Internal Server Error", "message": "Database connection failed"},
            url="https://api.mist.com/api/v1/orgs/abc/stats",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 500
        assert result["error"] is True
        assert "Internal Server Error" in str(result["data"])

    def test_error_handling_502_bad_gateway(self):
        """Test 502 Bad Gateway error handling."""
        mock_response = create_mock_api_response(
            status_code=502,
            data={"error": "Bad Gateway", "message": "Upstream server unavailable"},
            url="https://api.mist.com/api/v1/orgs",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 502
        assert result["error"] is True

    def test_error_handling_503_service_unavailable(self):
        """Test 503 Service Unavailable error handling."""
        mock_response = create_mock_api_response(
            status_code=503,
            data={"error": "Service Unavailable", "message": "Maintenance in progress"},
            url="https://api.mist.com/api/v1/orgs/abc/devices",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 503
        assert result["error"] is True

    def test_error_handling_504_gateway_timeout(self):
        """Test 504 Gateway Timeout error handling."""
        mock_response = create_mock_api_response(
            status_code=504,
            data={"error": "Gateway Timeout", "message": "Upstream server timed out"},
            url="https://api.mist.com/api/v1/orgs/abc/alarms",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 504
        assert result["error"] is True


# =============================================================================
# Edge Cases for serialize_api_response
# =============================================================================


# Store module reference at module level to avoid name mangling issues
_API_RESPONSE = __api_response


class TestEdgeCases:
    """Edge case tests for serialize_api_response."""

    def test_edge_case_status_code_none(self):
        """Test handling when status_code is None."""
        mock_response = MagicMock(spec=_API_RESPONSE.APIResponse)
        mock_response.status_code = None
        mock_response.url = "https://api.mist.com/api/v1/test"
        mock_response.data = {"result": "ok"}
        mock_response.next = None

        result = serialize_api_response(mock_response)

        # None status_code should not be treated as error
        assert result["status_code"] is None
        # When status_code is None/0, it shouldn't be >= 400, so error should be False
        # But our implementation checks: if status_code and status_code >= 400
        # So None should result in error=False
        assert result["error"] is False

    def test_edge_case_status_code_0(self):
        """Test handling when status_code is 0."""
        mock_response = MagicMock(spec=_API_RESPONSE.APIResponse)
        mock_response.status_code = 0
        mock_response.url = "https://api.mist.com/api/v1/test"
        mock_response.data = {"result": "ok"}
        mock_response.next = None

        result = serialize_api_response(mock_response)

        # 0 status_code should not be treated as error
        assert result["status_code"] == 0
        # 0 is not >= 400, so error should be False
        assert result["error"] is False

    def test_edge_case_next_none_explicit(self):
        """Test handling when next is explicitly None."""
        mock_response = create_mock_api_response(
            status_code=200,
            data=[1, 2, 3],
            url="https://api.mist.com/api/v1/test",
            next_url=None,
        )

        result = serialize_api_response(mock_response)

        assert result["has_more"] is False
        assert "next_page" not in result

    def test_edge_case_empty_string_next(self):
        """Test handling when next is empty string."""
        mock_response = MagicMock(spec=_API_RESPONSE.APIResponse)
        mock_response.status_code = 200
        mock_response.url = "https://api.mist.com/api/v1/test"
        mock_response.data = [1, 2, 3]
        mock_response.next = ""  # Empty string instead of None

        result = serialize_api_response(mock_response)

        # Empty string is falsy, so has_more should be False
        assert result["has_more"] is False

    def test_serialize_api_response_edge_case_data_none(self):
        """Test handling when data is None."""
        mock_response = create_mock_api_response(
            status_code=200,
            data=None,
            url="https://api.mist.com/api/v1/test",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 200
        assert result["error"] is False
        assert result["data"] is None

    def test_serialize_api_response_edge_case_data_string(self):
        """Test handling when data is a string (some APIs return string)."""
        mock_response = create_mock_api_response(
            status_code=200,
            data="Operation successful",
            url="https://api.mist.com/api/v1/test",
        )

        result = serialize_api_response(mock_response)

        assert result["status_code"] == 200
        assert result["error"] is False
        assert result["data"] == "Operation successful"

    def test_serialize_api_response_url_preserved(self):
        """Test that URL is preserved in the response."""
        mock_response = create_mock_api_response(
            status_code=200,
            data={"result": "ok"},
            url="https://api.eu.mist.com/api/v1/orgs/abc/devices",
        )

        result = serialize_api_response(mock_response)

        assert result["url"] == "https://api.eu.mist.com/api/v1/orgs/abc/devices"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])