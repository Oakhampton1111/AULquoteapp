"""
Transport service for managing logistics operations.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session

from warehouse_quote_app.app.core.monitoring import log_event
from warehouse_quote_app.app.schemas.quote import TransportServices
from warehouse_quote_app.app.services.base import BaseService

class TransportService(BaseService):
    """Service for managing transport operations."""

    def calculate_transport_cost(
        self,
        transport: TransportServices,
        db: Session
    ) -> Decimal:
        """Calculate transport cost."""
        if not transport or not transport.destination_postcode:
            return Decimal('0')

        # Base rate per shipment
        base_rate = Decimal('100.00')
        
        # Calculate distance factor based on postcode
        # This is a simplified example - in reality, you'd use a proper distance calculation
        distance_factor = self._calculate_distance_factor(transport.destination_postcode)
        
        # Calculate number of shipments
        num_shipments = transport.num_shipments or 1
        
        # Calculate total cost
        total_cost = base_rate * Decimal(str(distance_factor)) * Decimal(str(num_shipments))
        
        return total_cost

    def _calculate_distance_factor(self, postcode: str) -> float:
        """Calculate distance factor based on postcode."""
        # This is a simplified example
        # In reality, you'd use a proper distance calculation service
        try:
            postcode_num = int(postcode)
            if postcode_num < 2000:  # Sydney metro
                return 1.0
            elif postcode_num < 3000:  # NSW regional
                return 1.5
            elif postcode_num < 4000:  # VIC
                return 2.0
            elif postcode_num < 5000:  # QLD
                return 2.5
            else:  # Other states
                return 3.0
        except ValueError:
            return 1.0  # Default to metro rate if invalid postcode

    def log_transport_calculation(
        self,
        db: Session,
        transport: TransportServices,
        cost: Decimal,
        user_id: int
    ) -> None:
        """Log transport cost calculation."""
        log_event(
            db=db,
            event_type="transport_cost_calculated",
            user_id=user_id,
            resource_type="transport",
            resource_id="calculation",
            details={
                "services": transport.model_dump(),
                "calculated_cost": str(cost)
            }
        )
