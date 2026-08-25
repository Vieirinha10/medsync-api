import hashlib
import json
import logging
import re
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("medsync.requests")


@dataclass(frozen=True)
class RateLimitRule:
    name: str
    method: str
    path: re.Pattern[str]
    limit: int
    window_seconds: int


RATE_LIMIT_RULES = (
    RateLimitRule("register", "POST", re.compile(r"^/usuarios/registrar$"), 5, 300),
    RateLimitRule("login", "POST", re.compile(r"^/usuarios/login$"), 10, 60),
    RateLimitRule(
        "resend-verification",
        "POST",
        re.compile(r"^/usuarios/reenviar-verificacao$"),
        5,
        300,
    ),
    RateLimitRule(
        "simulation",
        "POST",
        re.compile(r"^/simulacoes/\d+/finalizar$"),
        6,
        600,
    ),
    RateLimitRule(
        "simulation-question",
        "POST",
        re.compile(r"^/simulacoes/resultados/\d+/perguntar$"),
        20,
        600,
    ),
    RateLimitRule(
        "transparent-payment",
        "POST",
        re.compile(r"^/pagamentos/transparente$"),
        5,
        300,
    ),
    RateLimitRule(
        "hosted-checkout",
        "POST",
        re.compile(r"^/pagamentos/checkout$"),
        5,
        300,
    ),
    RateLimitRule(
        "question-explanation",
        "POST",
        re.compile(r"^/questoes/\d+/explicacao$"),
        10,
        600,
    ),
)

MAX_REQUEST_BODY_BYTES = 1_000_000


class SecurityAndObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit():
            if int(content_length) > MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": "Corpo da solicitação excede o limite permitido."
                    },
                )

        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        started_at = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )
        forwarded_proto = request.headers.get("x-forwarded-proto", "")
        if request.url.scheme == "https" or forwarded_proto == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
        if request.url.path.startswith(
            ("/usuarios", "/admin", "/pagamentos", "/simulacoes")
        ):
            response.headers["Cache-Control"] = "no-store"

        logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
                ensure_ascii=False,
            )
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, enabled: bool) -> None:
        super().__init__(app)
        self.enabled = enabled
        self._buckets: dict[tuple[str, str], deque[float]] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _client_key(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        client_ip = forwarded or (request.client.host if request.client else "unknown")
        authorization = request.headers.get("authorization", "")
        if authorization.lower().startswith("bearer "):
            token_fingerprint = hashlib.sha256(
                authorization.encode("utf-8")
            ).hexdigest()[:16]
            return f"{client_ip}:{token_fingerprint}"
        return client_ip

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if not self.enabled:
            return await call_next(request)

        rule = next(
            (
                candidate
                for candidate in RATE_LIMIT_RULES
                if candidate.method == request.method
                and candidate.path.fullmatch(request.url.path)
            ),
            None,
        )
        if rule is None:
            return await call_next(request)

        now = time.monotonic()
        bucket_key = (rule.name, self._client_key(request))
        with self._lock:
            bucket = self._buckets.setdefault(bucket_key, deque())
            cutoff = now - rule.window_seconds
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= rule.limit:
                retry_after = max(1, int(rule.window_seconds - (now - bucket[0])))
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Muitas solicitações. Aguarde antes de tentar novamente."
                    },
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rule.limit)
        return response
