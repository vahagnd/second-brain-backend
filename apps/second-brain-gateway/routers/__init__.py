"""Routes module."""

from fastapi import FastAPI
from sb_gateway.routers import health, notes


def init_routers(app: FastAPI):
    # Routers registered first have priority in the event of route conflicts.
    app.include_router(notes.router)

    # Service
    app.include_router(health.router)
