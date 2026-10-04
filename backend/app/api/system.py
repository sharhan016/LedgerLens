from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.schemas.system import CapabilityStatus, HealthResponse, SystemStatusResponse

router = APIRouter(tags=["system"])


@router.get("/health/live", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    return HealthResponse(status="ok", service="ledgerlens-api")


@router.get("/health/ready", response_model=HealthResponse)
async def readiness(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> HealthResponse:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database is not ready",
        ) from error
    return HealthResponse(status="ok", service="ledgerlens-api")


@router.get("/api/v1/system/status", response_model=SystemStatusResponse)
async def system_status(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SystemStatusResponse:
    return SystemStatusResponse(
        application="LedgerLens",
        environment=settings.environment,
        release="0.1.0",
        status="ready",
        capabilities=[
            CapabilityStatus(name="API foundation", status="ready", vertex_task="T-01"),
            CapabilityStatus(name="Tenant security", status="ready", vertex_task="T-02"),
            CapabilityStatus(name="Document ingestion", status="ready", vertex_task="T-03"),
            CapabilityStatus(name="Hybrid retrieval", status="ready", vertex_task="T-04"),
            CapabilityStatus(name="Grounded answers", status="ready", vertex_task="T-05"),
            CapabilityStatus(name="Routed data sources", status="ready", vertex_task="T-06"),
            CapabilityStatus(name="Operations and evaluation", status="ready", vertex_task="T-07"),
            CapabilityStatus(name="Browser workspace", status="ready", vertex_task="T-08"),
        ],
    )
