"""
Admin-related schema definitions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from .quote import QuoteStatus
from .reports.quote_report import QuoteReport
from .reports.service_report import ServiceReport
from .reports.customer_report import CustomerReport

class AdminErrorResponse(BaseModel):
    """Standard error response model for admin routes."""
    model_config = ConfigDict(extra='forbid')
    
    detail: str

class AdminMetricsResponse(BaseModel):
    """Response model for admin metrics."""
    model_config = ConfigDict(extra='forbid')
    
    total_customers: int = Field(..., description="Total number of customers")
    active_customers: int = Field(..., description="Number of active customers")
    new_customers_30d: int = Field(..., description="Number of new customers in last 30 days")
    total_quotes: int = Field(..., description="Total number of quotes")
    pending_quotes: int = Field(..., description="Number of pending quotes")
    completed_quotes: int = Field(..., description="Number of completed quotes")
    total_revenue: float = Field(..., description="Total revenue from completed quotes")
    revenue_30d: float = Field(..., description="Revenue from completed quotes in last 30 days")

class CustomerResponse(BaseModel):
    """Response model for customer data."""
    model_config = ConfigDict(extra='forbid')
    
    id: int
    name: str
    email: str
    company: Optional[str] = None
    is_active: bool
    created_at: datetime
    total_quotes: int = Field(..., description="Total number of quotes by this customer")

class QuoteReport(BaseModel):
    """Response model for quote statistics."""
    model_config = ConfigDict(extra='forbid')
    
    total_quotes: int = Field(..., description="Total number of quotes in period")
    total_value: float = Field(..., description="Total value of quotes in period")
    average_value: float = Field(..., description="Average value of quotes in period")
    status_breakdown: Dict[str, int] = Field(..., description="Number of quotes by status")
    start_date: Optional[datetime] = Field(None, description="Start of reporting period")
    end_date: Optional[datetime] = Field(None, description="End of reporting period")

class ServiceReport(BaseModel):
    """Response model for service usage statistics."""
    model_config = ConfigDict(extra='forbid')
    
    service_usage: Dict[str, int] = Field(..., description="Count of quotes by service type")
    total_quotes: int = Field(..., description="Total number of quotes in period")
    start_date: Optional[datetime] = Field(None, description="Start of reporting period")
    end_date: Optional[datetime] = Field(None, description="End of reporting period")

class CustomerReport(BaseModel):
    """Response model for customer activity statistics."""
    model_config = ConfigDict(extra='forbid')
    
    customer_id: int = Field(..., description="ID of the customer")
    customer_name: str = Field(..., description="Name of the customer")
    total_quotes: int = Field(..., description="Total number of quotes")
    total_value: float = Field(..., description="Total value of quotes")
    quote_status: Dict[str, int] = Field(..., description="Number of quotes by status")
    start_date: Optional[datetime] = Field(None, description="Start of reporting period")
    end_date: Optional[datetime] = Field(None, description="End of reporting period")

class SystemStatus(BaseModel):
    """System status information."""
    model_config = ConfigDict(extra='forbid')
    
    status: str = Field(..., description="Overall system status")
    version: str = Field(..., description="System version")
    uptime: float = Field(..., description="System uptime in hours")
    last_update: datetime = Field(..., description="Last system update timestamp")
    components: Dict[str, str] = Field(..., description="Status of individual components")
    
class UserManagement(BaseModel):
    """User management information."""
    model_config = ConfigDict(extra='forbid')
    
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    admin_users: int = Field(..., description="Number of admin users")
    locked_accounts: int = Field(..., description="Number of locked accounts")
    recent_logins: int = Field(..., description="Number of logins in last 24 hours")

class AuditLog(BaseModel):
    """Audit log entry."""
    model_config = ConfigDict(extra='forbid')
    
    timestamp: datetime = Field(..., description="Event timestamp")
    user_id: int = Field(..., description="User ID who performed the action")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: str = Field(..., description="ID of resource affected")
    details: Dict[str, Any] = Field(..., description="Additional details about the action")
    ip_address: str = Field(..., description="IP address of the user")

class AdminDashboard(BaseModel):
    """Admin dashboard data."""
    model_config = ConfigDict(extra='forbid')
    
    metrics: AdminMetricsResponse = Field(..., description="Key business metrics")
    system_status: SystemStatus = Field(..., description="System status information")
    pending_approvals: List[Dict[str, Any]] = Field(..., description="Pending approvals requiring action")
    recent_activity: List[AuditLog] = Field(..., description="Recent system activity")
    alerts: List[Dict[str, Any]] = Field(..., description="System alerts and notifications")

class RateCardResponse(BaseModel):
    """Response model for rate card data."""
    model_config = ConfigDict(extra='forbid')
    
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    valid_from: datetime
    valid_until: datetime
    rates: Dict[str, Any]

class RateCardCreate(BaseModel):
    """Request model for creating a rate card."""
    model_config = ConfigDict(extra='forbid')
    
    name: str
    description: Optional[str] = None
    is_active: bool = True
    valid_from: datetime
    valid_until: datetime
    rates: Dict[str, Any]

class RateCardUpdate(BaseModel):
    """Request model for updating a rate card."""
    model_config = ConfigDict(extra='forbid')
    
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    rates: Optional[Dict[str, Any]] = None

class QuoteResponse(BaseModel):
    """Response model for quote data."""
    model_config = ConfigDict(extra='forbid')
    
    id: int
    customer_id: int
    customer_name: str
    status: str
    total_amount: float
    created_at: datetime
    service_type: str
    discount: Optional[float] = None

class QuoteGenerateRequest(BaseModel):
    """Request model for generating a quote."""
    model_config = ConfigDict(extra='forbid')
    
    customer_id: int
    service_type: str
    requirements: Dict[str, Any]
    special_instructions: Optional[str] = None
    discount: Optional[float] = None
