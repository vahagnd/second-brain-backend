from fastapi import FastAPI
from sb_gateway.routers import init_routers
from sb_gateway.settings import app_settings


app = FastAPI(root_path=app_settings.api_prefix)

init_routers(app=app)
