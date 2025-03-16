"""
Third-party logistics (3PL) service for managing warehouse operations.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session

from warehouse_quote_app.app.core.monitoring import log_event
from warehouse_quote_app.app.schemas.quote import ThreePLServices
from warehouse_quote_app.app.services.base import BaseService

class ThreePLService(BaseService):
    """Service for managing 3PL operations."""

    def calculate_3pl_cost(
        self,
        three_pl: ThreePLServices,
        db: Session
    ) -> Decimal:
        """Calculate 3PL services cost."""
        if not three_pl:
            return Decimal('0')

        total_cost = Decimal('0')
        
        # Unpacking costs
        if three_pl.unpacking:
            container_costs = {
                "20ft": Decimal('200.00'),
                "40ft": Decimal('350.00'),
                "40ft HC": Decimal('400.00')
            }
            total_cost += container_costs.get(
                three_pl.container_size,
                Decimal('200.00')  # Default to 20ft container cost
            )
            
        # Barcode scanning
        if three_pl.barcode_scanning:
            total_cost += Decimal('50.00')
            
        # Cargo labelling
        if three_pl.cargo_labelling:
            total_cost += Decimal('30.00')
            
        # Order picking
        if three_pl.order_picking:
            total_cost += Decimal('75.00')
            
        return total_cost

    def log_3pl_calculation(
        self,
        db: Session,
        three_pl: ThreePLServices,
        cost: Decimal,
        user_id: int
    ) -> None:
        """Log 3PL cost calculation."""
        log_event(
            db=db,
            event_type="3pl_cost_calculated",
            user_id=user_id,
            resource_type="3pl",
            resource_id="calculation",
            details={
                "services": three_pl.model_dump(),
                "calculated_cost": str(cost)
            }
        )
