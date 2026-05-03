"""
Shared fixtures and helpers for e2e tests.
"""

from collections.abc import Generator

import httpx
import pytest
from settings import Settings
from utils import attach_auto_refresh, login


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Provide test settings."""
    return Settings()


@pytest.fixture(scope="session")
def admin_client(settings: Settings) -> Generator[httpx.Client, None, None]:
    """Authenticated HTTP client for tests with administrator privileges.

    Gets a valid token for the administrator.
    """
    client = httpx.Client(base_url=settings.base_url, timeout=300)
    try:
        token = login(client, settings.admin_username, settings.admin_password)
        client.headers.update({"Authorization": f"Bearer {token}"})
        attach_auto_refresh(client, settings.admin_username, settings.admin_password)
        yield client
    finally:
        client.close()


@pytest.fixture(scope="session")
def user_client(settings: Settings) -> Generator[httpx.Client, None, None]:
    """Authenticated HTTP client for tests with regular user privileges.

    Gets a valid token for the regular user.
    """
    client = httpx.Client(base_url=settings.base_url, timeout=300)
    try:
        token = login(client, settings.user_username, settings.user_password)
        client.headers.update({"Authorization": f"Bearer {token}"})
        attach_auto_refresh(client, settings.user_username, settings.user_password)
        yield client
    finally:
        client.close()


@pytest.fixture(scope="session")
def unauthorized_client(settings: Settings) -> Generator[httpx.Client, None, None]:
    """Unauthorized HTTP client for tests without access rights.

    Does not perform login, so Authorization headers are absent.
    """
    client = httpx.Client(base_url=settings.base_url, timeout=240)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="session")
def non_existent_note_id() -> int:
    """Provide a note ID that does not exist in the system."""
    return 999999999


@pytest.fixture(scope="session")
def non_existent_user_id() -> int:
    """Provide a user ID that does not exist in the system."""
    return 999999999
