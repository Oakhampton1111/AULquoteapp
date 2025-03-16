"""Dashboard schema definitions."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from warehouse_quote_app.app.schemas.quote import QuoteListItem
from warehouse_quote_app.app.schemas.user import UserListItem


class UserInfo(BaseModel):
    """User information for dashboard."""
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_admin: bool


class AdminStats(BaseModel):
    """Admin statistics for dashboard."""
    total_quotes: int = Field(..., description="Total number of quotes in the system")
    total_users: int = Field(..., description="Total number of users in the system")
    quotes_this_month: int = Field(..., description="Number of quotes created this month")


class DashboardResponse(BaseModel):
    """Dashboard response schema."""
    user_info: UserInfo
    recent_quotes: List[QuoteListItem]
    terms_and_conditions_url: str
    rate_card_url: str
    
    # Admin-specific fields
    pending_quotes_count: Optional[int] = None
    recent_users: Optional[List[UserListItem]] = None
    admin_stats: Optional[AdminStats] = None
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "user_info": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "user123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_admin": False
                },
                "recent_quotes": [
                    {
                        "id": 1,
                        "created_at": "2025-01-01T12:00:00",
                        "status": "pending",
                        "total_amount": 1500.0,
                        "service_type": "storage"
                    }
                ],
                "terms_and_conditions_url": "/api/v1/documents/terms",
                "rate_card_url": "/api/v1/documents/rate-card"
            }
        }
