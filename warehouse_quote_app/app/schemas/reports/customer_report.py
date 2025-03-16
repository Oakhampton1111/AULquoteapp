"""Customer activity report schemas."""

from typing import Dict, Optional
from datetime import datetime
from pydantic import Field

from app.schemas.reports.base import (
    BaseReport,
    BaseMetrics,
    ValueMetrics,
    ReportMetadata,
    TimeMetrics
)

class CustomerMetrics(BaseMetrics):
    """Customer activity and value metrics."""
    # Quote metrics
    total_quotes: int = Field(default=0, description="Total number of quotes")
    accepted_quotes: int = Field(default=0, description="Number of accepted quotes")
    rejected_quotes: int = Field(default=0, description="Number of rejected quotes")
    quote_acceptance_rate: float = Field(default=0.0, description="Quote acceptance rate")
    
    # Value metrics
    total_spent: float = Field(default=0.0, description="Total amount spent")
    average_order_value: float = Field(default=0.0, description="Average order value")
    lifetime_value: float = Field(default=0.0, description="Customer lifetime value")
    
    # Time metrics
    average_quote_time: float = Field(default=0.0, description="Average time to quote acceptance")
    last_activity: Optional[datetime] = Field(default=None, description="Last customer activity")

class CustomerReport(BaseReport[CustomerMetrics]):
    """Customer activity report with segmentation."""
    customer_segments: Dict[str, CustomerMetrics] = Field(
        default_factory=dict,
        description="Metrics broken down by customer segment"
    )
    
    def calculate_rates(self) -> None:
        """Calculate success and acceptance rates."""
        super().calculate_rates()  # Calculate base success rates
        
        # Calculate quote acceptance rates
        if self.metrics.total_quotes > 0:
            self.metrics.quote_acceptance_rate = (self.metrics.accepted_quotes / self.metrics.total_quotes) * 100
            
        for metrics in self.customer_segments.values():
            if metrics.total_quotes > 0:
                metrics.quote_acceptance_rate = (metrics.accepted_quotes / metrics.total_quotes) * 100
