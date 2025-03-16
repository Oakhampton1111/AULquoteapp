"""
Quote generation service for creating quotes based on customer requirements.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from warehouse_quote_app.app.database import get_db
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.schemas.admin import QuoteGenerateRequest
from warehouse_quote_app.app.schemas.quote import QuoteStatus

# Import business services
from warehouse_quote_app.app.services.business.rate_calculator import RateCalculator, StorageRequest, ServiceDimensions
from warehouse_quote_app.app.services.business.transport_calculator import TransportCalculator, TransportRequest
from warehouse_quote_app.app.services.business.container_calculator import ContainerCalculator, ContainerRequest
from warehouse_quote_app.app.services.business.rule_engine import BusinessRuleEngine, ValidationContext

logger = logging.getLogger(__name__)


class QuoteGenerator:
    """Service for generating quotes."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
        self.rate_calculator = RateCalculator()
        self.transport_calculator = TransportCalculator()
        self.container_calculator = ContainerCalculator()
        self.rule_engine = BusinessRuleEngine()
    
    def generate_quote(self, request: QuoteGenerateRequest, admin_user: User) -> Dict[str, Any]:
        """
        Generate a quote based on customer requirements.
        
        This will:
        1. Validate the request
        2. Calculate pricing based on requirements and rate cards
        3. Apply any discounts
        4. Create a quote record in the database
        5. Notify the customer
        """
        logger.info(f"Generating quote for customer {request.customer_id}")
        
        # Validate customer exists
        # This would normally query the database
        customer = {
            "id": request.customer_id,
            "name": "Example Customer",
            "email": "customer@example.com"
        }
        
        # Calculate pricing based on requirements and rate cards
        line_items = []
        total_amount = Decimal('0.00')
        
        if request.service_type == "storage":
            # Use rate calculator for storage pricing
            storage_request = self._create_storage_request(request.requirements)
            rate_result = self.rate_calculator.calculate_storage_rate(storage_request)
            
            # Add line items from rate calculator
            line_items = rate_result.line_items
            total_amount = rate_result.total_amount
            
        elif request.service_type == "transport":
            # Use transport calculator for transport pricing
            transport_request = self._create_transport_request(request.requirements)
            transport_items = self.transport_calculator.calculate_transport_cost(transport_request)
            
            # Convert transport items to line items format
            for item in transport_items:
                line_items.append({
                    "description": item.description,
                    "quantity": 1,
                    "unit_price": float(item.amount),
                    "total": float(item.amount),
                    "notes": item.notes
                })
                total_amount += item.amount
            
        elif request.service_type == "container":
            # Use container calculator for container pricing
            container_request = self._create_container_request(request.requirements)
            container_items = self.container_calculator.calculate_packing_cost(container_request)
            
            # Convert container items to line items format
            for item in container_items:
                line_items.append({
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": float(item.amount / item.quantity if item.quantity > 0 else item.amount),
                    "total": float(item.amount),
                    "notes": item.notes
                })
                total_amount += item.amount
        
        # Apply discount if specified
        if request.discount:
            discount_amount = total_amount * (Decimal(str(request.discount)) / Decimal('100'))
            total_amount -= discount_amount
            line_items.append({
                "description": f"Discount ({request.discount}%)",
                "quantity": 1,
                "unit_price": float(-discount_amount),
                "total": float(-discount_amount)
            })
        
        # Create quote record
        # This would normally create a record in the database
        quote = {
            "id": 1,
            "customer_id": request.customer_id,
            "customer_name": customer["name"],
            "status": QuoteStatus.PENDING.value,
            "total_amount": float(total_amount),
            "created_at": datetime.now(),
            "service_type": request.service_type,
            "discount": request.discount,
            "line_items": line_items,
            "special_instructions": request.special_instructions
        }
        
        logger.info(f"Quote generated: ID={quote['id']}, Amount={quote['total_amount']}")
        
        return quote
    
    def _create_storage_request(self, requirements: Dict[str, Any]) -> StorageRequest:
        """Create a storage request from requirements."""
        dimensions = ServiceDimensions(
            length=requirements.get("length", 0),
            width=requirements.get("width", 0),
            height=requirements.get("height", 0)
        )
        
        return StorageRequest(
            dimensions=dimensions,
            duration_weeks=requirements.get("duration_weeks", 1),
            quantity=requirements.get("quantity", 1),
            storage_type=requirements.get("storage_type", "standard"),
            has_dangerous_goods=requirements.get("dangerous_goods", False)
        )
    
    def _create_transport_request(self, requirements: Dict[str, Any]) -> TransportRequest:
        """Create a transport request from requirements."""
        return TransportRequest(
            transport_type=requirements.get("transport_type", "local"),
            from_postcode=requirements.get("from_postcode", "4000"),
            to_postcode=requirements.get("to_postcode", "4007"),
            container_size=requirements.get("container_size"),
            duration_hours=requirements.get("duration_hours"),
            is_dangerous_goods=requirements.get("dangerous_goods", False),
            vehicle_type=requirements.get("vehicle_type", "semi_trailer"),
            return_journey=requirements.get("return_journey", True)
        )
    
    def _create_container_request(self, requirements: Dict[str, Any]) -> ContainerRequest:
        """Create a container request from requirements."""
        return ContainerRequest(
            container_size=requirements.get("container_size", "20ft"),
            is_personal_effects=requirements.get("personal_effects", False),
            item_count=requirements.get("item_count", 100),
            has_dangerous_goods=requirements.get("dangerous_goods", False),
            requires_fumigation=requirements.get("fumigation", False),
            special_handling=requirements.get("special_handling")
        )


# Dependency for getting the quote generator service.
def get_quote_generator(db: Session = Depends(get_db)):
    return QuoteGenerator(db)
