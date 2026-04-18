from fastapi import FastAPI
from routers import init_routers
from settings import app_settings

app = FastAPI(root_path=app_settings.api_prefix)

init_routers(app=app)
