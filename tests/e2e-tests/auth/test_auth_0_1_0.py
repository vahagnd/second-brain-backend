"""
E2E tests for Authorization endpoints.
Cases: TC-AUTH-001 to TC-AUTH-016
"""

import httpx
import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.auth]


def test_tc_auth_001_login_success(settings, unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-001: Login - success."""
    response = unauthorized_client.post(
        "/auth/login",
        json={"username": settings.user_username, "password": settings.user_password},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_tc_auth_002_login_wrong_password(settings, unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-002: Login - wrong password."""
    response = unauthorized_client.post(
        "/auth/login",
        json={"username": settings.user_username, "password": "definitely_wrong_password"},
    )
    assert response.status_code == 401


def test_tc_auth_003_login_unknown_username(unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-003: Login - unknown username."""
    response = unauthorized_client.post(
        "/auth/login",
        json={"username": "ghost_user_that_does_not_exist", "password": "pass"},
    )
    assert response.status_code == 401


def test_tc_auth_004_refresh_token_success(settings, unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-004: Refresh token - success."""
    # First login to get a refresh token
    login_resp = unauthorized_client.post(
        "/auth/login",
        json={"username": settings.user_username, "password": settings.user_password},
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    response = unauthorized_client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_tc_auth_005_refresh_token_expired(unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-005: Refresh token - expired token (treated as invalid)."""
    # We cannot easily produce a truly expired token in e2e, so we use a garbage value
    response = unauthorized_client.post("/auth/refresh", json={"refresh_token": "expired.token.value"})
    assert response.status_code == 401


def test_tc_auth_006_refresh_token_invalid(unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-006: Refresh token - invalid token."""
    response = unauthorized_client.post("/auth/refresh", json={"refresh_token": "garbage"})
    assert response.status_code == 401


def test_tc_auth_007_refresh_token_revoked_after_logout(
    settings,
    unauthorized_client: httpx.Client,
) -> None:
    """TC-AUTH-007: Refresh token - revoked token (post-logout)."""
    # Login to get tokens
    login_resp = unauthorized_client.post(
        "/auth/login",
        json={"username": settings.user_username, "password": settings.user_password},
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Logout (revokes all refresh tokens)
    logout_resp = unauthorized_client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_resp.status_code == 200

    # Try to use the revoked refresh token
    response = unauthorized_client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401


def test_tc_auth_008_logout_success(settings, unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-008: Logout - success."""
    login_resp = unauthorized_client.post(
        "/auth/login",
        json={"username": settings.user_username, "password": settings.user_password},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]

    response = unauthorized_client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


def test_tc_auth_009_logout_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-009: Logout - no auth."""
    response = unauthorized_client.post("/auth/logout")
    assert response.status_code == 401


def test_tc_auth_010_access_token_blacklisted_after_logout(
    settings,
    unauthorized_client: httpx.Client,
) -> None:
    """TC-AUTH-010: Access token blacklisted after logout."""
    login_resp = unauthorized_client.post(
        "/auth/login",
        json={"username": settings.user_username, "password": settings.user_password},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]

    # Logout
    logout_resp = unauthorized_client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_resp.status_code == 200

    # Try to use the blacklisted access token on a protected endpoint
    response = unauthorized_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 401


def test_tc_auth_011_get_current_user_success(user_client: httpx.Client) -> None:
    """TC-AUTH-011: Get current user - success."""
    response = user_client.get("/users/me")
    assert response.status_code == 200
    body = response.json()
    assert "id" in body
    assert isinstance(body["id"], int)
    assert "username" in body
    assert "role" in body


def test_tc_auth_012_get_current_user_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-012: Get current user - no auth."""
    response = unauthorized_client.get("/users/me")
    assert response.status_code == 401


def test_tc_auth_013_update_own_username_success(settings, unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-013: Update own username - success."""
    # Login fresh to get a dedicated client for this test
    login_resp = unauthorized_client.post(
        "/auth/login",
        json={"username": settings.user_username, "password": settings.user_password},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    new_username = f"{settings.user_username}_renamed_tc013"
    try:
        response = unauthorized_client.patch(
            "/users/me",
            json={"new_username": new_username},
            headers=headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["username"] == new_username
        assert "id" in body
        assert "role" in body
    finally:
        # Restore original username
        unauthorized_client.patch(
            "/users/me",
            json={"new_username": settings.user_username},
            headers=headers,
        )


def test_tc_auth_014_update_own_username_conflict(settings, user_client: httpx.Client) -> None:
    """TC-AUTH-014: Update own username - conflict."""
    # Try to rename to admin's username (which already exists)
    response = user_client.patch(
        "/users/me",
        json={"new_username": settings.admin_username},
    )
    assert response.status_code == 409


def test_tc_auth_015_update_own_username_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-AUTH-015: Update own username - no auth."""
    response = unauthorized_client.patch("/users/me", json={"new_username": "x"})
    assert response.status_code == 401


def test_tc_auth_016_update_own_username_null(user_client: httpx.Client) -> None:
    """TC-AUTH-016: Update own username - null value (username unchanged)."""
    # Get current username first
    me_resp = user_client.get("/users/me")
    assert me_resp.status_code == 200
    original_username = me_resp.json()["username"]

    response = user_client.patch("/users/me", json={"new_username": None})
    assert response.status_code == 200
    assert response.json()["username"] == original_username
