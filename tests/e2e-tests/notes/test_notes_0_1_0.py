"""
E2E tests for Notes endpoints.
Cases: TC-NOTES-001 to TC-NOTES-021
"""

import httpx
import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.notes]


def test_tc_notes_001_list_notes_user_sees_own(user_client: httpx.Client) -> None:
    """TC-NOTES-001: List notes - success (user sees own only)."""
    response = user_client.get("/notes")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert "items" in body
    assert isinstance(body["items"], list)


def test_tc_notes_002_list_notes_admin_sees_all(admin_client: httpx.Client) -> None:
    """TC-NOTES-002: List notes - admin sees all notes."""
    response = admin_client.get("/notes")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert "items" in body
    assert isinstance(body["items"], list)


def test_tc_notes_003_list_notes_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-NOTES-003: List notes - no auth."""
    response = unauthorized_client.get("/notes")
    assert response.status_code == 401


def test_tc_notes_004_list_notes_semantic_search(user_client: httpx.Client) -> None:
    """TC-NOTES-004: List notes - semantic search (items include score field)."""
    # Create a note first so there's something to search
    create_resp = user_client.post("/notes", json={"content": "Semantic search test note for TC-NOTES-004"})
    assert create_resp.status_code == 201
    note_id = create_resp.json().get("id") if create_resp.status_code == 201 else None

    try:
        response = user_client.get(
            "/notes",
            params={"search": "semantic search", "search_type": "semantic", "top_k": 5},
        )
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert body.get("search_type") == "semantic"
        # If items returned, they should have a score field
        for item in body["items"]:
            assert "score" in item
    finally:
        if note_id is not None:
            user_client.delete(f"/notes/{note_id}")


def test_tc_notes_005_list_notes_like_search(user_client: httpx.Client) -> None:
    """TC-NOTES-005: List notes - LIKE search (items without score field)."""
    create_resp = user_client.post("/notes", json={"content": "LIKE search test note for TC-NOTES-005 unique"})
    assert create_resp.status_code == 201
    note_id = create_resp.json().get("id") if create_resp.status_code == 201 else None

    try:
        response = user_client.get("/notes", params={"search": "TC-NOTES-005 unique", "search_type": "like"})
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert body.get("search_type") == "like"
        for item in body["items"]:
            assert "score" not in item
    finally:
        if note_id is not None:
            user_client.delete(f"/notes/{note_id}")


def test_tc_notes_006_list_notes_pagination(user_client: httpx.Client) -> None:
    """TC-NOTES-006: List notes - pagination."""
    response = user_client.get("/notes", params={"page": 2, "limit": 5})
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert body["limit"] == 5
    assert "items" in body


def test_tc_notes_007_list_notes_sort_created_at_desc(user_client: httpx.Client) -> None:
    """TC-NOTES-007: List notes - sort by created_at desc."""
    response = user_client.get("/notes", params={"sort_by": "created_at", "order_by": "desc"})
    assert response.status_code == 200
    body = response.json()
    items = body["items"]
    if len(items) >= 2:
        # Verify descending order
        for i in range(len(items) - 1):
            assert items[i]["created_at"] >= items[i + 1]["created_at"]


def test_tc_notes_008_list_notes_sort_content_asc(user_client: httpx.Client) -> None:
    """TC-NOTES-008: List notes - sort by content asc."""
    response = user_client.get("/notes", params={"sort_by": "content", "order_by": "asc"})
    assert response.status_code == 200
    body = response.json()
    items = body["items"]
    if len(items) >= 2:
        for i in range(len(items) - 1):
            assert items[i]["content"].lower() <= items[i + 1]["content"].lower()


def test_tc_notes_009_create_note_success(user_client: httpx.Client) -> None:
    """TC-NOTES-009: Create note - success."""
    content = "My new note for TC-NOTES-009 unique content xyz987"
    response = user_client.post("/notes", json={"content": content})
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["content"] == content
    assert "user_id" in body

    # Cleanup
    user_client.delete(f"/notes/{body['id']}")


def test_tc_notes_010_create_note_semantic_duplicate(user_client: httpx.Client) -> None:
    """TC-NOTES-010: Create note - semantic duplicate detected."""
    content = "Unique note content for duplicate detection TC-NOTES-010 alpha bravo charlie"
    # Create the original note
    create_resp = user_client.post("/notes", json={"content": content})
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    try:
        # Try to create a very similar note
        dup_resp = user_client.post("/notes", json={"content": content})
        assert dup_resp.status_code == 409
        body = dup_resp.json()
        assert "similar_notes" in body["detail"]
    finally:
        user_client.delete(f"/notes/{note_id}")


def test_tc_notes_011_create_note_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-NOTES-011: Create note - no auth."""
    response = unauthorized_client.post("/notes", json={"content": "note"})
    assert response.status_code == 401


def test_tc_notes_012_get_note_owner_access(user_client: httpx.Client) -> None:
    """TC-NOTES-012: Get note by ID - owner access."""
    # Create a note to retrieve
    create_resp = user_client.post("/notes", json={"content": "Note for TC-NOTES-012 owner access test"})
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    try:
        response = user_client.get(f"/notes/{note_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == note_id
    finally:
        user_client.delete(f"/notes/{note_id}")


def test_tc_notes_013_get_note_admin_access(user_client: httpx.Client, admin_client: httpx.Client) -> None:
    """TC-NOTES-013: Get note by ID - admin access any note."""
    # Create a note as user
    create_resp = user_client.post("/notes", json={"content": "Note for TC-NOTES-013 admin access test"})
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    try:
        # Admin should be able to access it
        response = admin_client.get(f"/notes/{note_id}")
        assert response.status_code == 200
        assert response.json()["id"] == note_id
    finally:
        user_client.delete(f"/notes/{note_id}")


def test_tc_notes_014_get_note_other_user_not_found(
    admin_client: httpx.Client,
    user_client: httpx.Client,
) -> None:
    """TC-NOTES-014: Get note by ID - user accesses other's note (404)."""
    # Create a note as admin
    create_resp = admin_client.post("/notes", json={"content": "Admin note for TC-NOTES-014 forbidden test"})
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    try:
        # Regular user should get 404
        response = user_client.get(f"/notes/{note_id}")
        assert response.status_code == 404
    finally:
        admin_client.delete(f"/notes/{note_id}")


def test_tc_notes_015_get_note_not_found(user_client: httpx.Client, non_existent_note_id: int) -> None:
    """TC-NOTES-015: Get note by ID - not found."""
    response = user_client.get(f"/notes/{non_existent_note_id}")
    assert response.status_code == 404


def test_tc_notes_016_get_note_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-NOTES-016: Get note by ID - no auth."""
    response = unauthorized_client.get("/notes/1")
    assert response.status_code == 401


def test_tc_notes_017_delete_note_owner_success(user_client: httpx.Client) -> None:
    """TC-NOTES-017: Delete note - owner success."""
    create_resp = user_client.post("/notes", json={"content": "Note for TC-NOTES-017 delete owner test"})
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    response = user_client.delete(f"/notes/{note_id}")
    assert response.status_code == 204


def test_tc_notes_018_delete_note_admin_any(user_client: httpx.Client, admin_client: httpx.Client) -> None:
    """TC-NOTES-018: Delete note - admin deletes any note."""
    # Create a note as user
    create_resp = user_client.post("/notes", json={"content": "Note for TC-NOTES-018 admin delete test"})
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    # Admin deletes it
    response = admin_client.delete(f"/notes/{note_id}")
    assert response.status_code == 204


def test_tc_notes_019_delete_note_other_user_not_found(
    admin_client: httpx.Client,
    user_client: httpx.Client,
) -> None:
    """TC-NOTES-019: Delete note - user deletes other's note (404)."""
    # Create a note as admin
    create_resp = admin_client.post("/notes", json={"content": "Admin note for TC-NOTES-019 forbidden delete"})
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    try:
        # Regular user should get 404
        response = user_client.delete(f"/notes/{note_id}")
        assert response.status_code == 404
    finally:
        admin_client.delete(f"/notes/{note_id}")


def test_tc_notes_020_delete_note_not_found(user_client: httpx.Client, non_existent_note_id: int) -> None:
    """TC-NOTES-020: Delete note - not found."""
    response = user_client.delete(f"/notes/{non_existent_note_id}")
    assert response.status_code == 404


def test_tc_notes_021_delete_note_no_auth(unauthorized_client: httpx.Client) -> None:
    """TC-NOTES-021: Delete note - no auth."""
    response = unauthorized_client.delete("/notes/1")
    assert response.status_code == 401
