from typing import Any

from pydantic import BaseModel, Field


class QueryIntent(BaseModel):
    operation: str
    metric: str | None = None
    group_by: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    time_period: str | None = None