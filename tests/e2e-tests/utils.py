import httpx


def login(client: httpx.Client, username: str, password: str) -> str:
    """Authenticate and return the access token."""
    response = client.post("/auth/login", json={"username": username, "password": password})
    response.raise_for_status()
    return response.json()["access_token"]


def attach_auto_refresh(client: httpx.Client, username: str, password: str) -> None:
    """Attach an event hook that re-authenticates on 401 responses."""

    def _on_response(response: httpx.Response) -> None:
        if response.status_code == 401:
            try:
                new_token = login(response._client, username, password)  # noqa: SLF001
                response._client.headers.update({"Authorization": f"Bearer {new_token}"})  # noqa: SLF001
            except Exception:  # noqa: BLE001
                pass

    client.event_hooks["response"].append(_on_response)
