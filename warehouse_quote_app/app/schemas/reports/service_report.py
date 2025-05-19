"""Service usage report schemas."""

from typing import Dict, Optional
from datetime import datetime
from pydantic import Field

from warehouse_quote_app.app.schemas.reports.base import (
    BaseReport,
    BaseMetrics,
    TimeMetrics,
    ReportMetadata
)

class ServiceMetrics(TimeMetrics):
    """Service performance and usage metrics."""
    # Request metrics
    total_requests: int = Field(default=0, description="Total number of API requests")
    successful_requests: int = Field(default=0, description="Number of successful requests")
    failed_requests: int = Field(default=0, description="Number of failed requests")
    error_rate: float = Field(default=0.0, description="API error rate")
    
    # Performance metrics
    average_response_time: float = Field(default=0.0, description="Average API response time")
    p95_response_time: float = Field(default=0.0, description="95th percentile response time")
    p99_response_time: float = Field(default=0.0, description="99th percentile response time")
    
    # Resource metrics
    total_compute_time: float = Field(default=0.0, description="Total compute time used")
    average_compute_cost: float = Field(default=0.0, description="Average compute cost per request")
    peak_memory_usage: float = Field(default=0.0, description="Peak memory usage in MB")

class ServiceReport(BaseReport[ServiceMetrics]):
    """Service usage report with endpoint metrics."""
    endpoint_metrics: Dict[str, ServiceMetrics] = Field(
        default_factory=dict,
        description="Metrics broken down by endpoint"
    )
    
    def calculate_rates(self) -> None:
        """Calculate success and error rates."""
        super().calculate_rates()  # Calculate base success rates
        
        # Calculate error rates
        if self.metrics.total_requests > 0:
            self.metrics.error_rate = (self.metrics.failed_requests / self.metrics.total_requests) * 100
            
        for metrics in self.endpoint_metrics.values():
            if metrics.total_requests > 0:
                metrics.error_rate = (metrics.failed_requests / metrics.total_requests) * 100
