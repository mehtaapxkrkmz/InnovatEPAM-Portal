from contextlib import asynccontextmanager
import logging
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.ideas import router as ideas_router
from app.core.config import get_settings
from app.db.client import mongo_manager


logger = logging.getLogger(__name__)


def _mongo_target(uri: str) -> str:
    parsed = urlparse(uri)
    host = parsed.hostname or "unknown-host"
    scheme = parsed.scheme or "mongodb"
    return f"{scheme}://{host}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to MongoDB target: %s", _mongo_target(get_settings().mongo_uri))
    mongo_manager.connect()
    try:
        yield
    finally:
        mongo_manager.close()


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ideas_router, prefix="/ideas", tags=["ideas"])
uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
