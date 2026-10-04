from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.system import CapabilityStatus, HealthResponse, SystemStatusResponse

router = APIRouter(tags=["system"])


@router.get("/health/live", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    return HealthResponse(status="ok", service="ledgerlens-api")


@router.get("/health/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    return HealthResponse(status="ok", service="ledgerlens-api")


@router.get("/api/v1/system/status", response_model=SystemStatusResponse)
async def system_status(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SystemStatusResponse:
    return SystemStatusResponse(
        application="LedgerLens",
        environment=settings.environment,
        release="0.1.0",
        status="foundation_ready",
        capabilities=[
            CapabilityStatus(name="API foundation", status="ready", vertex_task="T-01"),
            CapabilityStatus(name="Tenant security", status="ready", vertex_task="T-02"),
            CapabilityStatus(name="Document ingestion", status="ready", vertex_task="T-03"),
            CapabilityStatus(name="Hybrid retrieval", status="ready", vertex_task="T-04"),
            CapabilityStatus(name="Grounded answers", status="ready", vertex_task="T-05"),
        ],
    )
