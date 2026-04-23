"""Routes module."""

from fastapi import FastAPI

from routers import (
    admin,
    auth,
    health,
    notes,
    users,
)


def init_routers(app: FastAPI): # noqa: ANN201
    # Routers registered first have priority in the event of route conflicts.
    app.include_router(notes.router)
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(users.router)

    # Service
    app.include_router(health.router)
