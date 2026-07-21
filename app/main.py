"""FastAPI application entry point."""

import logging

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import __version__
from app.api.routes.charts import router as charts_router
from app.api.routes.classical import router as classical_router
from app.api.routes.classical_validation import router as classical_validation_router
from app.api.routes.dasha import router as dasha_router
from app.api.routes.panchanga import router as panchanga_router
from app.api.routes.positions import router as positions_router
from app.api.routes.system import router as system_router
from app.core.config import RuntimeSettings, load_runtime_settings
from app.core.runtime_guard import RuntimeGuardMiddleware, request_id_from_scope
from app.core.security import ApiSecurityError, require_api_key


async def _security_error_response(
    request: Request,
    error: ApiSecurityError,
) -> JSONResponse:
    """Translate service-authentication failures without leaking configured secrets."""

    request_id = request_id_from_scope(request.scope)
    headers = {"WWW-Authenticate": "Bearer"} if error.status_code == 401 else None
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.message, "request_id": request_id},
        headers=headers,
    )


def create_app(settings: RuntimeSettings | None = None) -> FastAPI:
    """Create and configure the Jyothisyam API application."""

    runtime = settings or load_runtime_settings()
    logging.basicConfig(level=getattr(logging, runtime.log_level), format="%(message)s")
    docs_url = "/docs" if runtime.docs_enabled else None
    redoc_url = "/redoc" if runtime.docs_enabled else None
    openapi_url = "/openapi.json" if runtime.docs_enabled else None

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
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )
    application.state.runtime_settings = runtime
    application.add_exception_handler(ApiSecurityError, _security_error_response)

    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=list(runtime.allowed_hosts),
    )
    if runtime.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(runtime.cors_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
            expose_headers=["X-Request-ID"],
            max_age=600,
        )
    application.add_middleware(
        RuntimeGuardMiddleware,
        max_request_body_bytes=runtime.max_request_body_bytes,
        request_timeout_seconds=runtime.request_timeout_seconds,
    )

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
