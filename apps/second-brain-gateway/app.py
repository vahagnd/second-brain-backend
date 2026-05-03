import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import init_routers
from settings import app_settings

app = FastAPI(root_path=app_settings.api_prefix)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.getLogger("uvicorn").handlers = []
logging.getLogger("uvicorn").propagate = True
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").handlers = []
logging.getLogger("uvicorn.access").propagate = True
logging.getLogger("uvicorn.error").handlers = []
logging.getLogger("uvicorn.error").propagate = True

logger = logging.getLogger("middleware")


@app.middleware("http")
async def log_requests(request: Request, call_next):  # noqa: ANN001, ANN201
    """Middleware to log incoming requests and their processing time."""
    start = time.time()
    response = await call_next(request)
    logger.info("%s %s %s %.3fs", request.method, request.url.path, response.status_code, time.time() - start)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


init_routers(app=app)
