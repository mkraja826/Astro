"""FastAPI application entry point."""

from fastapi import FastAPI

from app import __version__
from app.api.routes.system import router as system_router


def create_app() -> FastAPI:
    """Create and configure the Jyothisyam API application."""

    application = FastAPI(
        title="Jyothisyam API",
        summary="Vedic and South Indian astrology calculation platform",
        description=(
            "A versioned API foundation for deterministic Jyothisyam calculations. "
            "The current release contains system endpoints; calculation modules will "
            "be introduced behind explicit versioned routes."
        ),
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    application.include_router(system_router)
    return application


app = create_app()
