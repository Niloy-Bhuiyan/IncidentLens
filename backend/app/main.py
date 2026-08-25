from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes import router
from backend.app.config import get_settings
from backend.app.observability import configure_logging
from backend.app.security import RequestSecurityMiddleware
from backend.app.services import InvestigationService

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.investigation_service = InvestigationService(settings)
    yield


app = FastAPI(
    title="IncidentLens API",
    summary="Evidence-first software incident investigation",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(RequestSecurityMiddleware, settings=settings)
app.include_router(router)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", uuid.uuid4().hex)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = (
        exc.detail if isinstance(exc.detail, dict) else {"code": "http_error", "message": str(exc.detail)}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": detail.get("code", "http_error"),
                "message": detail.get("message", "Request failed"),
                "request_id": _request_id(request),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {"location": ".".join(map(str, error["loc"])), "message": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "request_id": _request_id(request),
                "details": details,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    del exc
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred",
                "request_id": _request_id(request),
            }
        },
    )


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"service": "IncidentLens API", "health": "/api/v1/health", "docs": "/docs"}
