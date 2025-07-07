from __future__ import annotations

from enum import StrEnum, auto

from pydantic import BaseModel, Field


class HealthProbe(BaseModel):
    """Health Probe object. Holds the overall status and each entity checked."""

    status: HealthStatus
    entities: list[Entity]


class Entity(BaseModel):
    """Entity object. Holds the status for a single entity checked."""

    name: str
    status: HealthStatus
    internal_status: bool = Field(exclude=True)


class HealthStatus(StrEnum):
    """Simple enum for status."""

    HEALTHY = auto()
    UNHEALTHY = auto()
