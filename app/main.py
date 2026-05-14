from contextlib import asynccontextmanager
import logging
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.ideas import router as ideas_router
from app.api.endpoints.review_stages import router as review_stages_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc: RequestValidationError):
    errors = [
        {
            "field": " -> ".join(str(part) for part in err.get("loc", [])),
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "validation_error"),
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Validation failed",
            "errors": errors,
        },
    )


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ideas_router, prefix="/ideas", tags=["ideas"])
app.include_router(review_stages_router)
uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes,
    )

    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict):
                responses = operation.get("responses", {})
                responses.pop("422", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}