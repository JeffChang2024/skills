from __future__ import annotations

from pydantic import BaseModel, Field


class ForgeEvent(BaseModel):
    source: str = "openforge"
    schema_version: str = "1.0.0"
    event: str
    run_id: str
    timestamp: str
    data: dict[str, object] = Field(default_factory=dict)
