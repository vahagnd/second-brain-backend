"""
E2E tests for Administration endpoints.
Cases: TC-ADM-001 to TC-ADM-024
"""

import httpx
import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.admin]


def test_tc_adm_001_create_user_success(admin_client: httpx.Client) -> None:
    """TC-ADM-001: Create user - success."""
    username = "tc_adm_001_testuser"
    response = admin_client.post(
        "/admin/users",
        json={"username": username, "password": "pass123", "role": "user"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["username"] == username
    assert body["role"] == "user"

    # Cleanup
    admin_client.delete(f"/admin/users/{body['id']}")


def test_tc_adm_002_create_user_duplicate(admin_client: httpx.Client) -> None:
    """TC-ADM-002: Create user - duplicate username."""
    username = "tc_adm_002_duplicate"
    # Create the user first
    create_resp = admin_client.post(
        "/admin/users",
        json={"username": username, "password": "pass123", "role": "user"},
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    try:
        # Try to create again with same username
        dup_resp = admin_client.post(
            "/admin/users",
            json={"username": username, "password": "pass123", "role": "user"},
        )
        assert dup_resp.status_code == 409
    finally:
        admin_client.delete(f"/admin/users/{user_id}")


def test_tc_adm_003_create_user_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-ADM-003: Create user - no auth."""
    response = unauthorized_client.post(
        "/admin/users",
        json={"username": "u", "password": "p", "role": "user"},
    )
    assert response.status_code == 401


def test_tc_adm_004_create_user_non_admin(user_client: httpx.Client) -> None:
    """TC-ADM-004: Create user - non-admin role."""
    response = user_client.post(
        "/admin/users",
        json={"username": "u", "password": "p", "role": "user"},
    )
    assert response.status_code == 403


def test_tc_adm_005_list_users_success(admin_client: httpx.Client) -> None:
    """TC-ADM-005: List all users - success."""
    response = admin_client.get("/admin/users")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert isinstance(body["total"], int)
    assert "items" in body
    assert isinstance(body["items"], list)


def test_tc_adm_006_list_users_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-ADM-006: List all users - no auth."""
    response = unauthorized_client.get("/admin/users")
    assert response.status_code == 401


def test_tc_adm_007_list_users_non_admin(user_client: httpx.Client) -> None:
    """TC-ADM-007: List all users - non-admin."""
    response = user_client.get("/admin/users")
    assert response.status_code == 403


def test_tc_adm_008_get_user_by_id_success(admin_client: httpx.Client) -> None:
    """TC-ADM-008: Get user by ID - success."""
    # Create a user to retrieve
    create_resp = admin_client.post(
        "/admin/users",
        json={"username": "tc_adm_008_getuser", "password": "pass123", "role": "user"},
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    try:
        response = admin_client.get(f"/admin/users/{user_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == user_id
        assert "username" in body
        assert "role" in body
    finally:
        admin_client.delete(f"/admin/users/{user_id}")


def test_tc_adm_009_get_user_not_found(admin_client: httpx.Client, non_existent_user_id: int) -> None:
    """TC-ADM-009: Get user by ID - not found."""
    response = admin_client.get(f"/admin/users/{non_existent_user_id}")
    assert response.status_code == 404


def test_tc_adm_010_get_user_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-ADM-010: Get user by ID - no auth."""
    response = unauthorized_client.get("/admin/users/1")
    assert response.status_code == 401


def test_tc_adm_011_get_user_non_admin(user_client: httpx.Client) -> None:
    """TC-ADM-011: Get user by ID - non-admin."""
    response = user_client.get("/admin/users/1")
    assert response.status_code == 403


def test_tc_adm_012_delete_user_success(admin_client: httpx.Client) -> None:
    """TC-ADM-012: Delete user - success."""
    create_resp = admin_client.post(
        "/admin/users",
        json={"username": "tc_adm_012_deleteuser", "password": "pass123", "role": "user"},
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    response = admin_client.delete(f"/admin/users/{user_id}")
    assert response.status_code == 204


def test_tc_adm_013_delete_user_not_found(admin_client: httpx.Client, non_existent_user_id: int) -> None:
    """TC-ADM-013: Delete user - not found."""
    response = admin_client.delete(f"/admin/users/{non_existent_user_id}")
    assert response.status_code == 404


def test_tc_adm_014_delete_user_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-ADM-014: Delete user - no auth."""
    response = unauthorized_client.delete("/admin/users/1")
    assert response.status_code == 401


def test_tc_adm_015_delete_user_non_admin(user_client: httpx.Client) -> None:
    """TC-ADM-015: Delete user - non-admin."""
    response = user_client.delete("/admin/users/1")
    assert response.status_code == 403


def test_tc_adm_016_update_username_success(admin_client: httpx.Client) -> None:
    """TC-ADM-016: Update username - success."""
    create_resp = admin_client.post(
        "/admin/users",
        json={"username": "tc_adm_016_original", "password": "pass123", "role": "user"},
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    try:
        new_username = "tc_adm_016_renamed"
        response = admin_client.patch(
            f"/admin/users/{user_id}",
            json={"new_username": new_username},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == user_id
        assert body["username"] == new_username
        assert "role" in body
    finally:
        admin_client.delete(f"/admin/users/{user_id}")


def test_tc_adm_017_update_username_conflict(admin_client: httpx.Client, settings) -> None:
    """TC-ADM-017: Update username - conflict."""
    create_resp = admin_client.post(
        "/admin/users",
        json={"username": "tc_adm_017_conflict_user", "password": "pass123", "role": "user"},
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    try:
        # Try to rename to admin's username (already taken)
        response = admin_client.patch(
            f"/admin/users/{user_id}",
            json={"new_username": settings.admin_username},
        )
        assert response.status_code == 409
    finally:
        admin_client.delete(f"/admin/users/{user_id}")


def test_tc_adm_018_update_username_not_found(admin_client: httpx.Client, non_existent_user_id: int) -> None:
    """TC-ADM-018: Update username - not found."""
    response = admin_client.patch(
        f"/admin/users/{non_existent_user_id}",
        json={"new_username": "x"},
    )
    assert response.status_code == 404


def test_tc_adm_019_update_username_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-ADM-019: Update username - no auth."""
    response = unauthorized_client.patch("/admin/users/1", json={"new_username": "x"})
    assert response.status_code == 401


def test_tc_adm_020_update_username_non_admin(user_client: httpx.Client) -> None:
    """TC-ADM-020: Update username - non-admin."""
    response = user_client.patch("/admin/users/1", json={"new_username": "x"})
    assert response.status_code == 403


def test_tc_adm_021_update_password_success(admin_client: httpx.Client) -> None:
    """TC-ADM-021: Update password - success."""
    original_password = "original_pass_tc021"
    create_resp = admin_client.post(
        "/admin/users",
        json={"username": "tc_adm_021_pwduser", "password": original_password, "role": "user"},
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    try:
        response = admin_client.patch(
            f"/admin/users/{user_id}/password",
            json={"new_password": "newpass123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == user_id
        assert "username" in body
        assert "role" in body
    finally:
        admin_client.delete(f"/admin/users/{user_id}")


def test_tc_adm_022_update_password_not_found(admin_client: httpx.Client, non_existent_user_id: int) -> None:
    """TC-ADM-022: Update password - not found."""
    response = admin_client.patch(
        f"/admin/users/{non_existent_user_id}/password",
        json={"new_password": "x"},
    )
    assert response.status_code == 404


def test_tc_adm_023_update_password_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-ADM-023: Update password - no auth."""
    response = unauthorized_client.patch("/admin/users/1/password", json={"new_password": "x"})
    assert response.status_code == 401


def test_tc_adm_024_update_password_non_admin(user_client: httpx.Client) -> None:
    """TC-ADM-024: Update password - non-admin."""
    response = user_client.patch("/admin/users/1/password", json={"new_password": "x"})
    assert response.status_code == 403
