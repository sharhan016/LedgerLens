import threading
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.security.dependencies import require_permission
from app.security.principal import Permission, Principal


@dataclass(frozen=True, slots=True)
class MetricSnapshot:
    method: str
    route: str
    status_code: int
    count: int
    average_latency_ms: float
    maximum_latency_ms: float


class RequestMetrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._values: dict[tuple[str, str, int], list[float]] = defaultdict(list)

    def record(self, method: str, route: str, status_code: int, latency_ms: float) -> None:
        with self._lock:
            self._values[(method, route, status_code)].append(latency_ms)

    def snapshot(self) -> list[MetricSnapshot]:
        with self._lock:
            return [
                MetricSnapshot(
                    method=method,
                    route=route,
                    status_code=status_code,
                    count=len(values),
                    average_latency_ms=round(sum(values) / len(values), 3),
                    maximum_latency_ms=round(max(values), 3),
                )
                for (method, route, status_code), values in sorted(self._values.items())
                if values
            ]

    def clear(self) -> None:
        with self._lock:
            self._values.clear()


request_metrics = RequestMetrics()


class RequestTelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        route = getattr(request.scope.get("route"), "path", "unmatched")
        request_metrics.record(request.method, route, response.status_code, elapsed_ms)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.3f}"
        return response


router = APIRouter(tags=["observability"])


@router.get("/api/v1/operations/metrics")
async def metrics(
    principal: Annotated[Principal, Depends(require_permission(Permission.OPERATIONS_READ))],
) -> dict[str, object]:
    return {
        "content_policy": "paths, status codes, counts, and latency only",
        "metrics": [
            {
                "method": item.method,
                "route": item.route,
                "status_code": item.status_code,
                "count": item.count,
                "average_latency_ms": item.average_latency_ms,
                "maximum_latency_ms": item.maximum_latency_ms,
            }
            for item in request_metrics.snapshot()
        ],
    }
