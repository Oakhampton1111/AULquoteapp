"""Base classes for report schemas."""

from typing import Dict, Generic, TypeVar, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ReportMetadata(BaseModel):
    """Common metadata for all reports."""
    generated_at: datetime
    report_id: str
    report_type: str
    time_period: str
    filters: Dict[str, str] = {}

class BaseMetrics(BaseModel):
    """Base class for all metrics."""
    model_config = ConfigDict(extra='forbid')
    
    total_count: int = Field(default=0, description="Total number of items/events")
    success_count: int = Field(default=0, description="Number of successful items/events")
    failure_count: int = Field(default=0, description="Number of failed items/events")
    success_rate: float = Field(default=0.0, description="Success rate as percentage")

class TimeMetrics(BaseMetrics):
    """Time-based metrics."""
    average_duration: float = Field(default=0.0, description="Average duration in seconds")
    total_duration: float = Field(default=0.0, description="Total duration in seconds")
    peak_duration: float = Field(default=0.0, description="Peak duration in seconds")

class ValueMetrics(BaseMetrics):
    """Value-based metrics."""
    total_value: float = Field(default=0.0, description="Total monetary value")
    average_value: float = Field(default=0.0, description="Average monetary value")
    peak_value: float = Field(default=0.0, description="Peak monetary value")

M = TypeVar('M', bound=BaseMetrics)
class BaseReport(BaseModel, Generic[M]):
    """Generic base report with configurable metrics type."""
    model_config = ConfigDict(extra='forbid')
    
    metadata: ReportMetadata
    metrics: M
    segment_metrics: Dict[str, M] = Field(default_factory=dict)
    time_series: Optional[Dict[str, M]] = None
    
    def calculate_rates(self) -> None:
        """Calculate success rates for all metrics."""
        if hasattr(self.metrics, 'total_count') and self.metrics.total_count > 0:
            self.metrics.success_rate = (self.metrics.success_count / self.metrics.total_count) * 100
            
        for metrics in self.segment_metrics.values():
            if metrics.total_count > 0:
                metrics.success_rate = (metrics.success_count / metrics.total_count) * 100
