from fastapi import APIRouter
from models.system import VersionResponse
from settings import app_settings

router = APIRouter(tags=["system"])


@router.get("/version")
def get_version() -> VersionResponse:
    """Get WF Backend version."""
    return VersionResponse(version=app_settings.version)
