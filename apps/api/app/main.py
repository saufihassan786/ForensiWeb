"""ForensiWeb Backend Application Bootstrap and ASGI Entrypoint.

This module initializes the FastAPI application, configures middleware
(CORS, security headers), defines the application lifecycle (lifespan),
and exposes root-level discovery and metadata endpoints.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings

# Configure structured application logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("forensiweb.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management for startup and shutdown procedures.

    Yields:
        None: Handover execution during normal application runtime.
    """
    logger.info("Initializing ForensiWeb Backend Application...")
    yield
    logger.info("ForensiWeb Backend Application shutdown complete.")


def create_app(
    title: Optional[str] = None,
    version: Optional[str] = None,
    description: Optional[str] = None,
    cors_origins: Optional[List[str]] = None,
    debug: Optional[bool] = None,
    custom_settings: Optional[Settings] = None,
) -> FastAPI:
    """FastAPI application factory.

    Args:
        title: API application title for OpenAPI metadata.
        version: API application semantic version.
        description: API description for OpenAPI metadata.
        cors_origins: Permitted origins for CORS middleware.
        debug: Enable debug mode.
        custom_settings: Optional explicit Settings instance.

    Returns:
        FastAPI: Fully configured ASGI application instance.
    """
    cfg = custom_settings or get_settings()
    app_title = title or cfg.API_TITLE
    app_version = version or cfg.API_VERSION
    app_description = description or cfg.API_DESCRIPTION
    is_debug = debug if debug is not None else cfg.DEBUG
    environment = cfg.ENVIRONMENT

    application = FastAPI(
        title=app_title,
        version=app_version,
        description=app_description,
        debug=is_debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS middleware
    allowed_origins = cors_origins or cfg.CORS_ORIGINS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get(
        "/",
        summary="API Root Metadata",
        description="Returns core API metadata, operational status, and documentation pointers.",
        tags=["System"],
    )
    async def root_metadata() -> Dict[str, Any]:
        return {
            "name": app_title,
            "version": app_version,
            "status": "online",
            "environment": environment,
            "docs_url": "/docs",
            "openapi_url": "/openapi.json",
            "api_prefix": cfg.API_PREFIX,
        }

    # Mount API v1 router
    from app.api.v1.router import api_v1_router
    application.include_router(api_v1_router)

    # Mount top-level health endpoints (/health, /health/live, /health/ready)
    from app.api.v1.endpoints.health import router as health_router
    application.include_router(health_router)

    # Configure centralized error handling and request ID propagation
    from app.core.errors import setup_error_handling
    setup_error_handling(application)

    return application


# Global ASGI application instance for Uvicorn
app: FastAPI = create_app()

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
