"""Quote report schemas."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime

class StatusCounts(BaseModel):
    model_config = ConfigDict(extra='forbid')
    PENDING: int
    ACCEPTED: int
    REJECTED: int

class QuoteReport(BaseModel):
    model_config = ConfigDict(extra='forbid')
    total_quotes: int
    accepted_quotes: int
    conversion_rate: float
    status_counts: StatusCounts
    start_date: datetime
    end_date: datetime
