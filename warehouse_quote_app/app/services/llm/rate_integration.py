"""
Integration service between LLM and rate service.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from warehouse_quote_app.app.services.business.rates import RateService
from .model import WarehouseLLM
from .rag import RAGService
from warehouse_quote_app.app.schemas.rate.rate import RateCreate, RateUpdate, RateCategory
from warehouse_quote_app.app.core.monitoring import log_event

class RateIntegrationService:
    """Service for rate optimization and integration with LLM."""

    def __init__(
        self,
        db: Session,
        llm: Optional[WarehouseLLM] = None,
        rag: Optional[RAGService] = None
    ):
        """Initialize with optional dependencies."""
        self.db = db
        self.llm = llm or WarehouseLLM()
        self.rag = rag or RAGService()
        self.rate_service = RateService(db, llm, rag)

    def process_quote_request(
        self,
        conversation_history: List[Dict],
        current_context: Dict
    ) -> Dict:
        """Process a quote request using LLM and rate service."""
        # Get relevant rate card context
        service_type = current_context.get("service_type")
        rate_context = self.rag.get_rate_card_context(
            conversation_history,
            service_type
        )
        
        # Extract rate information
        rate_info = self.llm.extract_rate_info(rate_context)
        
        # Calculate rates
        try:
            rates = self.rate_service.get_rates(
                category=rate_info.get("service_type")
            )
            
            # Get quote-specific suggestions
            suggestions = self._get_quote_suggestions(
                current_context,
                rate_info
            )
            
            return {
                "rates": rates,
                "suggestions": suggestions,
                "context": rate_context
            }
            
        except Exception as e:
            log_event(
                db=self.db,
                event_type="quote_request_error",
                details={"error": str(e)}
            )
            raise

    def validate_rate_card(
        self,
        rate_card: Dict
    ) -> Dict[str, Any]:
        """Validate rate card using LLM."""
        return self.rate_service.validate_rate(rate_card)

    def optimize_rate_card(
        self,
        rate_card: Dict
    ) -> Dict[str, Any]:
        """Optimize rate card using LLM."""
        # Get optimization suggestions
        optimization_params = {
            "time_range": 90
        }
        
        result = self.rate_service.optimize_rate(
            rate_card["id"],
            optimization_params
        )
        
        return result
        
    def optimize_rates(self, request: Any) -> List[Dict[str, Any]]:
        """Optimize rates based on the quote request.
        
        Args:
            request: Quote request data
            
        Returns:
            List of optimized rates
        """
        # Extract relevant information from request
        service_types = []
        if hasattr(request, "service_requests"):
            service_types = [sr.service_type for sr in request.service_requests]
        
        # Get optimized rates for each service type
        optimized_rates = []
        for service_type in service_types:
            # Convert service type to rate category
            category = self._map_service_to_category(service_type)
            
            # Get rates for this category
            category_rates = self.rate_service.get_rates(category=category)
            
            # Apply optimizations
            for rate in category_rates:
                optimization_result = self.rate_service.optimize_rate(
                    rate.id,
                    {"context": request.dict()}
                )
                optimized_rates.append(optimization_result)
        
        return optimized_rates
    
    def generate_service_combinations(self, request: Any) -> List[Dict[str, Any]]:
        """Generate different combinations of services for the quote.
        
        Args:
            request: Quote request data
            
        Returns:
            List of service combinations
        """
        # This is a placeholder implementation
        # In a real system, you'd analyze the request and generate optimal combinations
        
        base_combo = {"services": []}
        if hasattr(request, "service_requests"):
            for sr in request.service_requests:
                base_combo["services"].append({
                    "type": sr.service_type,
                    "options": ["standard", "premium", "economy"]
                })
        
        # Generate combinations (simplistic approach)
        combinations = []
        for service in base_combo["services"]:
            for option in service["options"]:
                combo = {
                    "service_type": service["type"],
                    "service_level": option,
                    "estimated_cost": self._get_estimated_cost(service["type"], option)
                }
                combinations.append(combo)
        
        return combinations

    def _get_quote_suggestions(
        self,
        quote_details: Dict,
        rate_info: Dict
    ) -> List[str]:
        """Get quote-specific suggestions."""
        # Get warehouse info from quote details
        warehouse_type = quote_details.get("warehouse_type", "general")
        
        # Get suggestions
        suggestions = []
        
        # Add custom suggestions based on warehouse type
        if warehouse_type == "cold_storage":
            suggestions.append(
                "Consider climate-controlled storage for temperature-sensitive items"
            )
        elif warehouse_type == "hazardous":
            suggestions.append(
                "Additional handling fees may apply for hazardous materials"
            )
            
        return suggestions
        
    def _map_service_to_category(self, service_type: str) -> RateCategory:
        """Map service type to rate category."""
        mapping = {
            "storage": RateCategory.STORAGE,
            "handling": RateCategory.HANDLING,
            "additional": RateCategory.ADDITIONAL,
            "container": RateCategory.CONTAINER,
            "transport": RateCategory.TRANSPORT,
            "export": RateCategory.EXPORT
        }
        
        return mapping.get(service_type.lower(), RateCategory.ADDITIONAL)
        
    def _get_estimated_cost(self, service_type: str, service_level: str) -> float:
        """Get estimated cost for a service type and level."""
        # This would typically come from a database or rate calculation
        # This is just a placeholder implementation
        base_costs = {
            "storage": 100.0,
            "handling": 50.0,
            "transport": 200.0,
            "additional": 30.0
        }
        
        multipliers = {
            "economy": 0.8,
            "standard": 1.0,
            "premium": 1.5
        }
        
        base_cost = base_costs.get(service_type.lower(), 100.0)
        multiplier = multipliers.get(service_level.lower(), 1.0)
        
        return base_cost * multiplier
