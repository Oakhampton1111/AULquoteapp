"""
Storage service for managing warehouse storage operations.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session

from warehouse_quote_app.app.core.monitoring import log_event
from warehouse_quote_app.app.schemas.quote import StorageRequirements
from warehouse_quote_app.app.services.base import BaseService

class StorageService(BaseService):
    """Service for managing storage operations."""

    def calculate_storage_cost(
        self,
        storage_req: StorageRequirements,
        db: Session
    ) -> Decimal:
        """Calculate storage cost based on requirements."""
        if not storage_req:
            return Decimal('0')

        # Base rate per m²
        base_rate = Decimal('50.00')
        
        # Calculate floor area if not provided directly
        floor_area = storage_req.floor_area
        if not floor_area and storage_req.length and storage_req.width:
            floor_area = storage_req.length * storage_req.width
        
        if not floor_area:
            return Decimal('0')
            
        # Calculate base cost
        base_cost = base_rate * Decimal(str(floor_area))
        
        # Apply height surcharge if exceptionally tall
        if storage_req.is_exceptionally_tall:
            base_cost *= Decimal('1.5')
            
        # Add cost for bulky items
        if storage_req.num_bulky_items:
            bulky_item_rate = Decimal('100.00')
            base_cost += bulky_item_rate * Decimal(str(storage_req.num_bulky_items))
            
        return base_cost

    def log_storage_calculation(
        self,
        db: Session,
        storage_req: StorageRequirements,
        cost: Decimal,
        user_id: int
    ) -> None:
        """Log storage cost calculation."""
        log_event(
            db=db,
            event_type="storage_cost_calculated",
            user_id=user_id,
            resource_type="storage",
            resource_id="calculation",
            details={
                "requirements": storage_req.model_dump(),
                "calculated_cost": str(cost)
            }
        )
