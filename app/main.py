"""FastAPI application entry point."""

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app import __version__
from app.api.routes.charts import router as charts_router
from app.api.routes.classical import router as classical_router
from app.api.routes.classical_validation import router as classical_validation_router
from app.api.routes.dasha import router as dasha_router
from app.api.routes.panchanga import router as panchanga_router
from app.api.routes.positions import router as positions_router
from app.api.routes.system import router as system_router
from app.core.security import ApiSecurityError, require_api_key


async def _security_error_response(
    request: Request,
    error: ApiSecurityError,
) -> JSONResponse:
    """Translate service-authentication failures without leaking configured secrets."""

    del request
    headers = {"WWW-Authenticate": "Bearer"} if error.status_code == 401 else None
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.message},
        headers=headers,
    )


def create_app() -> FastAPI:
    """Create and configure the Jyothisyam API application."""

    application = FastAPI(
        title="Jyothisyam API",
        summary="Vedic and South Indian astrology calculation platform",
        description=(
            "A versioned API for deterministic Jyothisyam calculations and "
            "source-traceable classical reference data. It provides Lahiri sidereal "
            "planetary positions, D1 and D9 charts, sunrise-based Panchanga, nested "
            "Vimshottari timelines, and a Varahamihira reference profile."
        ),
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    application.add_exception_handler(ApiSecurityError, _security_error_response)

    protected = [Depends(require_api_key)]
    application.include_router(system_router)
    application.include_router(positions_router, dependencies=protected)
    application.include_router(charts_router, dependencies=protected)
    application.include_router(panchanga_router, dependencies=protected)
    application.include_router(dasha_router, dependencies=protected)
    application.include_router(classical_router, dependencies=protected)
    application.include_router(classical_validation_router, dependencies=protected)
    return application


app = create_app()
