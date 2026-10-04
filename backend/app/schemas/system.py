from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class CapabilityStatus(BaseModel):
    name: str
    status: Literal["ready", "planned"]
    vertex_task: str


class SystemStatusResponse(BaseModel):
    application: str
    environment: str
    release: str
    status: Literal["foundation_ready", "ready"]
    capabilities: list[CapabilityStatus]
