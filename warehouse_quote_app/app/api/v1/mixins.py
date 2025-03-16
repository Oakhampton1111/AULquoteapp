"""API endpoint mixins for common functionality."""
from typing import Optional, TypeVar, Generic, List, Type, Dict, Any
from fastapi import Query, Path, Depends, APIRouter
from pydantic import BaseModel
from datetime import datetime

from warehouse_quote_app.app.core.auth import get_current_user, get_current_admin_user
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.schemas.quote import QuoteStatus

T = TypeVar('T', bound=BaseModel)
ServiceType = TypeVar('ServiceType')

class PaginationMixin(Generic[T]):
    """Mixin for paginated endpoints."""
    
    @staticmethod
    def paginate(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100)
    ):
        return {"skip": skip, "limit": limit}

class QuoteFilterMixin:
    """Mixin for quote filtering endpoints."""
    
    @staticmethod
    def filter_quotes(
        status: Optional[QuoteStatus] = Query(None),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        customer_id: Optional[int] = Query(None)
    ):
        return {
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "customer_id": customer_id
        }

class CRUDMixin(Generic[T, ServiceType]):
    """Mixin for CRUD operations."""
    
    def __init__(
        self,
        router: APIRouter,
        path: str,
        response_model: Type[T],
        service_dependency,
        admin_only: bool = False
    ):
        self.router = router
        self.path = path
        self.response_model = response_model
        self.service_dependency = service_dependency
        self.get_current_user_fn = get_current_admin_user if admin_only else get_current_user
        
        self.setup_routes()
    
    def setup_routes(self):
        """Set up CRUD routes."""
        
        @self.router.get(f"/{self.path}/{{item_id}}", response_model=self.response_model)
        async def get_item(
            item_id: int = Path(..., gt=0),
            current_user: User = Depends(self.get_current_user_fn),
            service: Any = Depends(self.service_dependency)
        ):
            return await service.get(item_id)
        
        @self.router.get(f"/{self.path}", response_model=List[self.response_model])
        async def list_items(
            pagination: dict = Depends(PaginationMixin.paginate),
            current_user: User = Depends(self.get_current_user_fn),
            service: Any = Depends(self.service_dependency)
        ):
            return await service.list(**pagination)
        
        @self.router.post(f"/{self.path}", response_model=self.response_model)
        async def create_item(
            item: T,
            current_user: User = Depends(self.get_current_user_fn),
            service: Any = Depends(self.service_dependency)
        ):
            return await service.create(item)
        
        @self.router.put(f"/{self.path}/{{item_id}}", response_model=self.response_model)
        async def update_item(
            item_id: int,
            item: T,
            current_user: User = Depends(self.get_current_user_fn),
            service: Any = Depends(self.service_dependency)
        ):
            return await service.update(item_id, item)
        
        @self.router.delete(f"/{self.path}/{{item_id}}")
        async def delete_item(
            item_id: int,
            current_user: User = Depends(self.get_current_user_fn),
            service: Any = Depends(self.service_dependency)
        ):
            return await service.delete(item_id)

class ReportingMixin:
    """Mixin for reporting functionality."""

    @staticmethod
    def get_date_range(
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        default_days: int = 30
    ) -> Dict[str, datetime]:
        """Get date range for reports."""
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - datetime.timedelta(days=default_days)
            
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date"
            )
            
        return {
            "start_date": start_date,
            "end_date": end_date
        }

    @staticmethod
    def get_report_format(
        format: str = Query("json", enum=["json", "csv", "pdf"])
    ) -> str:
        """Get report format."""
        return format

    @staticmethod
    def get_report_filters(
        customer_id: Optional[int] = Query(None),
        service_type: Optional[str] = Query(None),
        status: Optional[str] = Query(None)
    ) -> Dict[str, Any]:
        """Get common report filters."""
        filters = {}
        if customer_id:
            filters["customer_id"] = customer_id
        if service_type:
            filters["service_type"] = service_type
        if status:
            filters["status"] = status
        return filters
