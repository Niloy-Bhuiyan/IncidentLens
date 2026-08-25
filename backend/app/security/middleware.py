from __future__ import annotations

import re
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.config import Settings
from backend.app.observability import log_event

REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{8,80}$")


class RequestSecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, settings: Settings) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.settings = settings
        self.requests: defaultdict[str, deque[float]] = defaultdict(deque)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        started = time.perf_counter()
        supplied = request.headers.get("x-request-id", "")
        request_id = supplied if REQUEST_ID_RE.fullmatch(supplied) else uuid.uuid4().hex
        request.state.request_id = request_id
        if request.method in {"POST", "PUT", "PATCH"}:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.settings.max_body_bytes:
                return self._error(
                    413, "request_too_large", "Request body exceeds the configured limit", request_id
                )
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                return self._error(
                    415, "unsupported_media_type", "Only application/json is accepted", request_id
                )
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        bucket = self.requests[client]
        while bucket and bucket[0] < now - 60:
            bucket.popleft()
        if len(bucket) >= self.settings.rate_limit_per_minute:
            return self._error(429, "rate_limited", "Too many requests; retry later", request_id)
        bucket.append(now)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        )
        log_event(
            "http_request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round((time.perf_counter() - started) * 1000, 3),
        )
        return response

    @staticmethod
    def _error(status: int, code: str, message: str, request_id: str) -> JSONResponse:
        return JSONResponse(
            status_code=status,
            content={"error": {"code": code, "message": message, "request_id": request_id}},
            headers={"X-Request-ID": request_id, "X-Content-Type-Options": "nosniff"},
        )
