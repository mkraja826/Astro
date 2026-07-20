"""FastAPI application entry point."""

from fastapi import FastAPI

from app import __version__
from app.api.routes.charts import router as charts_router
from app.api.routes.dasha import router as dasha_router
from app.api.routes.panchanga import router as panchanga_router
from app.api.routes.positions import router as positions_router
from app.api.routes.system import router as system_router


def create_app() -> FastAPI:
    """Create and configure the Jyothisyam API application."""

    application = FastAPI(
        title="Jyothisyam API",
        summary="Vedic and South Indian astrology calculation platform",
        description=(
            "A versioned API for deterministic Jyothisyam calculations. "
            "It provides Lahiri sidereal planetary positions, D1 and D9 charts, "
            "sunrise-based Panchanga, and nested Vimshottari timelines with "
            "optional Sookshma Dasha expansion."
        ),
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    application.include_router(system_router)
    application.include_router(positions_router)
    application.include_router(charts_router)
    application.include_router(panchanga_router)
    application.include_router(dasha_router)
    return application


app = create_app()
