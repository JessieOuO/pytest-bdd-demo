# Language: Python 3.11
# Packages: pytest==9.0.2, requests==2.32.5

"""
HTTP API endpoint tests.
These tests require the Flask server to be running on localhost:3000.
Run: python run_server.py
"""

from __future__ import annotations
from typing import Dict, Any

import pytest
import requests


BASE_URL = "http://localhost:3000"


@pytest.fixture(scope="session")
def reset_server_state():
    """Reset server state before running API tests."""
    try:
        response = requests.post(f"{BASE_URL}/reset-test-state", timeout=2)
        if response.status_code == 200:
            print("\n✓ Server state reset successfully")
    except requests.exceptions.RequestException:
        pytest.skip("Server not running on localhost:3000. Run: python run_server.py")


@pytest.fixture
def session_client():
    """Create a requests session for maintaining cookies."""
    return requests.Session()


# ============================================================================
# Login Endpoint Tests
# ============================================================================

@pytest.mark.api
class TestLoginEndpoint:
    """Test POST /login endpoint."""

    def test_login_page_loads(self, reset_server_state):
        """GET /login should return 200 and HTML."""
        response = requests.get(f"{BASE_URL}/login")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "Login" in response.text

    def test_login_with_valid_credentials(self, reset_server_state, session_client):
        """POST /login with valid credentials should redirect to dashboard."""
        response = session_client.post(
            f"{BASE_URL}/login",
            data={"username": "demo", "password": "demo"},
            allow_redirects=False
        )
        # Should redirect (302) to dashboard
        assert response.status_code == 302
        assert "/dashboard" in response.headers.get("Location", "")

        # Follow redirect and verify we can access dashboard
        dashboard_response = session_client.get(f"{BASE_URL}/dashboard")
        assert dashboard_response.status_code == 200
        assert "demo" in dashboard_response.text

    def test_login_with_invalid_password(self, reset_server_state):
        """POST /login with wrong password should return error."""
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": "demo", "password": "wrongpassword"}
        )
        assert response.status_code == 200
        assert "Invalid email or password" in response.text

    def test_login_with_nonexistent_user(self, reset_server_state):
        """POST /login with non-existent user should not leak info."""
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": "nonexistent@test.com", "password": "anypass"}
        )
        assert response.status_code == 200
        # Should show generic error, not "user not found"
        assert "Invalid email or password" in response.text
        # Should NOT reveal that user doesn't exist
        assert "not found" not in response.text.lower()
        assert "doesn't exist" not in response.text.lower()

    def test_login_with_empty_credentials(self, reset_server_state):
        """POST /login with empty fields should handle gracefully."""
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": "", "password": ""}
        )
        assert response.status_code == 200
        assert "Invalid email or password" in response.text


# ============================================================================
# Account Lockout Tests
# ============================================================================

@pytest.mark.api
class TestAccountLockout:
    """Test account lockout behavior via HTTP API."""

    def test_account_locks_after_failed_attempts(self, reset_server_state):
        """Account should lock after 5 failed login attempts."""
        # Try 5 times with wrong password
        for i in range(5):
            response = requests.post(
                f"{BASE_URL}/login",
                data={"username": "demo", "password": "wrongpass"}
            )
            assert response.status_code == 200

        # 6th attempt should show account locked
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": "demo", "password": "wrongpass"}
        )
        assert response.status_code == 200
        assert "locked" in response.text.lower()


# ============================================================================
# Dashboard & Authorization Tests
# ============================================================================

@pytest.mark.api
class TestDashboardAccess:
    """Test /dashboard endpoint authorization."""

    def test_dashboard_requires_login(self, reset_server_state):
        """GET /dashboard without session should redirect to login."""
        response = requests.get(f"{BASE_URL}/dashboard", allow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers.get("Location", "")

    def test_dashboard_accessible_after_login(self, reset_server_state, session_client):
        """GET /dashboard with valid session should return 200."""
        # First login
        session_client.post(
            f"{BASE_URL}/login",
            data={"username": "demo", "password": "demo"}
        )

        # Then access dashboard
        response = session_client.get(f"{BASE_URL}/dashboard")
        assert response.status_code == 200
        assert "Dashboard" in response.text
        assert "demo" in response.text


@pytest.mark.api
class TestAdminAccess:
    """Test /admin endpoint authorization."""

    def test_admin_requires_login(self, reset_server_state):
        """GET /admin without session should redirect to login."""
        response = requests.get(f"{BASE_URL}/admin", allow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers.get("Location", "")

    def test_admin_rejects_non_admin_user(self, reset_server_state, session_client):
        """GET /admin with non-admin user should be rejected."""
        # Login as demo (not admin)
        session_client.post(
            f"{BASE_URL}/login",
            data={"username": "demo", "password": "demo"}
        )

        # Try to access admin page
        response = session_client.get(f"{BASE_URL}/admin", allow_redirects=False)
        # Should redirect back to login (access denied)
        assert response.status_code == 302
        assert "/login" in response.headers.get("Location", "")


# ============================================================================
# Logout Tests
# ============================================================================

@pytest.mark.api
class TestLogout:
    """Test /logout endpoint."""

    def test_logout_clears_session(self, reset_server_state, session_client):
        """GET /logout should clear session and redirect to login."""
        # First login
        session_client.post(
            f"{BASE_URL}/login",
            data={"username": "demo", "password": "demo"}
        )

        # Verify we can access dashboard
        response = session_client.get(f"{BASE_URL}/dashboard")
        assert response.status_code == 200

        # Logout
        logout_response = session_client.get(f"{BASE_URL}/logout", allow_redirects=False)
        assert logout_response.status_code == 302
        assert "/login" in logout_response.headers.get("Location", "")

        # Verify we can no longer access dashboard
        dashboard_response = session_client.get(f"{BASE_URL}/dashboard", allow_redirects=False)
        assert dashboard_response.status_code == 302
        assert "/login" in dashboard_response.headers.get("Location", "")


# ============================================================================
# Root Endpoint Tests
# ============================================================================

@pytest.mark.api
class TestRootEndpoint:
    """Test / (root) endpoint."""

    def test_root_redirects_to_login_when_not_authenticated(self, reset_server_state):
        """GET / without session should redirect to /login."""
        response = requests.get(f"{BASE_URL}/", allow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers.get("Location", "")

    def test_root_redirects_to_dashboard_when_authenticated(self, reset_server_state, session_client):
        """GET / with valid session should redirect to /dashboard."""
        # Login first
        session_client.post(
            f"{BASE_URL}/login",
            data={"username": "demo", "password": "demo"}
        )

        # Access root
        response = session_client.get(f"{BASE_URL}/", allow_redirects=False)
        assert response.status_code == 302
        assert "/dashboard" in response.headers.get("Location", "")
