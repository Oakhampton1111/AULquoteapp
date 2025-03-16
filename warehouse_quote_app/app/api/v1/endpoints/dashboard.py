"""Dashboard endpoints for customer and admin views."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.core.auth import get_current_user
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.schemas.dashboard import DashboardResponse
from warehouse_quote_app.app.database.get_db import get_db
from warehouse_quote_app.app.repositories.quote import QuoteRepository
from warehouse_quote_app.app.repositories.user import UserRepository
from warehouse_quote_app.app.core.logging import get_logger
from warehouse_quote_app.app.core.config import settings

router = APIRouter()
logger = get_logger("dashboard")

@router.get(
    "",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Dashboard data retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard data for the current user.
    
    Returns different dashboard data based on user role (admin vs customer).
    """
    try:
        # Get repositories
        quote_repo = QuoteRepository()
        user_repo = UserRepository()
        
        # Basic user info
        user_info = {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "is_admin": current_user.is_admin
        }
        
        # Get recent quotes
        recent_quotes = await quote_repo.get_recent_by_user(db, current_user.id, limit=5)
        
        # Create response
        response = {
            "user_info": user_info,
            "recent_quotes": recent_quotes,
            "terms_and_conditions_url": f"{settings.API_V1_STR}/documents/terms",
            "rate_card_url": f"{settings.API_V1_STR}/documents/rate-card"
        }
        
        # Add admin-specific data if user is admin
        if current_user.is_admin:
            # Get pending quotes count
            pending_count = await quote_repo.count_by_status(db, "pending")
            
            # Get recent users
            recent_users = await user_repo.get_recent(db, limit=5)
            
            # Add to response
            response.update({
                "pending_quotes_count": pending_count,
                "recent_users": recent_users,
                "admin_stats": {
                    "total_quotes": await quote_repo.count_all(db),
                    "total_users": await user_repo.count_all(db),
                    "quotes_this_month": await quote_repo.count_by_date_range(
                        db, 
                        start_date=get_start_of_month(),
                        end_date=get_end_of_month()
                    )
                }
            })
        
        return response
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving dashboard data"
        )


def get_start_of_month() -> str:
    """Get the start date of the current month."""
    from datetime import datetime
    now = datetime.now()
    return datetime(now.year, now.month, 1).isoformat()


def get_end_of_month() -> str:
    """Get the end date of the current month."""
    from datetime import datetime, timedelta
    now = datetime.now()
    next_month = now.replace(day=28) + timedelta(days=4)
    end_of_month = next_month - timedelta(days=next_month.day)
    return end_of_month.isoformat()
