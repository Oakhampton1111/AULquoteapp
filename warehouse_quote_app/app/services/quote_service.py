from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from decimal import Decimal

from .business.rate_calculator import RateCalculator, ServiceDimensions, StorageRequest
from .business.transport_calculator import TransportCalculator, TransportRequest
from .business.container_calculator import ContainerCalculator, ContainerRequest, PackingMaterials
from .business.rule_engine import BusinessRuleEngine, ValidationContext

@dataclass
class QuoteRequest:
    """Represents a natural language quote request after initial processing."""
    services: List[str]
    dimensions: Optional[ServiceDimensions] = None
    storage_type: Optional[str] = None
    duration_weeks: Optional[int] = None
    quantity: Optional[int] = None
    has_dangerous_goods: bool = False
    customer_type: Optional[str] = None
    company_name: Optional[str] = None
    
    # Transport specific fields
    transport_type: Optional[str] = None
    from_postcode: Optional[str] = None
    to_postcode: Optional[str] = None
    from_suburb: Optional[str] = None
    to_suburb: Optional[str] = None
    container_size: Optional[str] = None
    duration_hours: Optional[float] = None
    vehicle_type: Optional[str] = None
    return_journey: bool = True
    
    # Container specific fields
    container_type: Optional[str] = None
    packing_materials: Optional[PackingMaterials] = None
    loading_assistance: bool = False


@dataclass
class QuoteResponse:
    """Response containing both quote details and conversation guidance."""
    line_items: List[Dict[str, Any]]
    total_amount: Decimal
    messages: List[str]
    follow_up_questions: List[str]
    missing_information: List[str]


class QuoteService:
    """Service that handles quote generation with natural language processing support."""
    
    def __init__(self):
        self.rate_calculator = RateCalculator()
        self.transport_calculator = TransportCalculator()
        self.container_calculator = ContainerCalculator()
        self.rule_engine = BusinessRuleEngine()
    
    def process_quote_request(self, request: QuoteRequest) -> QuoteResponse:
        """
        Process a quote request and return both quote details and conversation guidance.
        """
        # Validate the request using business rules
        validation_context = ValidationContext(
            service_types=request.services,
            has_dangerous_goods=request.has_dangerous_goods,
            customer_type=request.customer_type,
            dimensions=request.dimensions,
            storage_type=request.storage_type,
            transport_type=request.transport_type,
            container_type=request.container_type
        )
        
        validation_result = self.rule_engine.validate_request(validation_context)
        
        # Initialize response
        line_items = []
        total_amount = Decimal('0.00')
        messages = []
        follow_up_questions = []
        missing_information = []
        
        # Add validation messages
        if validation_result.warnings:
            messages.extend(validation_result.warnings)
        
        if validation_result.errors:
            messages.extend(validation_result.errors)
            missing_information.extend(validation_result.missing_fields)
            return QuoteResponse(
                line_items=[],
                total_amount=Decimal('0.00'),
                messages=messages,
                follow_up_questions=self._generate_follow_up_questions(request, missing_information),
                missing_information=missing_information
            )
        
        # Process storage service if requested
        if 'storage' in request.services:
            if not request.dimensions or not request.storage_type or not request.duration_weeks:
                missing = []
                if not request.dimensions:
                    missing.append("dimensions")
                if not request.storage_type:
                    missing.append("storage type")
                if not request.duration_weeks:
                    missing.append("duration")
                
                missing_str = ", ".join(missing)
                messages.append(f"I need more information about {missing_str} to calculate storage costs.")
                missing_information.extend(missing)
            else:
                # Calculate storage costs
                storage_request = StorageRequest(
                    dimensions=request.dimensions,
                    storage_type=request.storage_type,
                    duration_weeks=request.duration_weeks,
                    has_dangerous_goods=request.has_dangerous_goods,
                    quantity=request.quantity or 1
                )
                
                storage_result = self.rate_calculator.calculate_storage_rate(storage_request)
                
                # Add storage line items
                line_items.extend(storage_result.line_items)
                total_amount += storage_result.total_amount
                
                # Add storage-specific messages
                if storage_result.notes:
                    messages.extend(storage_result.notes)
        
        # Process transport service if requested
        if 'transport' in request.services:
            if not request.transport_type or not (request.from_postcode and request.to_postcode):
                missing = []
                if not request.transport_type:
                    missing.append("transport type")
                if not request.from_postcode:
                    missing.append("pickup location")
                if not request.to_postcode:
                    missing.append("delivery location")
                
                missing_str = ", ".join(missing)
                messages.append(f"I need more information about {missing_str} to calculate transport costs.")
                missing_information.extend(missing)
            else:
                # Calculate transport costs
                transport_request = TransportRequest(
                    transport_type=request.transport_type,
                    from_postcode=request.from_postcode,
                    to_postcode=request.to_postcode,
                    from_suburb=request.from_suburb,
                    to_suburb=request.to_suburb,
                    has_dangerous_goods=request.has_dangerous_goods,
                    return_journey=request.return_journey,
                    duration_hours=request.duration_hours,
                    vehicle_type=request.vehicle_type
                )
                
                transport_result = self.transport_calculator.calculate_transport_rate(transport_request)
                
                # Add transport line items
                line_items.extend(transport_result.line_items)
                total_amount += transport_result.total_amount
                
                # Add transport-specific messages
                if transport_result.notes:
                    messages.extend(transport_result.notes)
        
        # Process container service if requested
        if 'container' in request.services:
            if not request.container_size or not request.duration_weeks:
                missing = []
                if not request.container_size:
                    missing.append("container size")
                if not request.duration_weeks:
                    missing.append("rental duration")
                
                missing_str = ", ".join(missing)
                messages.append(f"I need more information about {missing_str} to calculate container costs.")
                missing_information.extend(missing)
            else:
                # Calculate container costs
                container_request = ContainerRequest(
                    container_size=request.container_size,
                    duration_weeks=request.duration_weeks,
                    has_dangerous_goods=request.has_dangerous_goods,
                    packing_materials=request.packing_materials,
                    loading_assistance=request.loading_assistance
                )
                
                container_result = self.container_calculator.calculate_container_rate(container_request)
                
                # Add container line items
                line_items.extend(container_result.line_items)
                total_amount += container_result.total_amount
                
                # Add container-specific messages
                if container_result.notes:
                    messages.extend(container_result.notes)
        
        # Generate follow-up questions based on missing information
        follow_up_questions = self._generate_follow_up_questions(request, missing_information)
        
        # Add conversation context
        conversation_context = self.get_conversation_context(request)
        if conversation_context:
            messages.extend(conversation_context)
        
        return QuoteResponse(
            line_items=line_items,
            total_amount=total_amount,
            messages=messages,
            follow_up_questions=follow_up_questions,
            missing_information=missing_information
        )
    
    def format_response_for_llm(self, response: QuoteResponse) -> str:
        """
        Format the quote response in a natural, conversational way for the LLM.
        """
        result = []
        
        # Add messages first
        if response.messages:
            result.extend(response.messages)
            result.append("")  # Empty line for spacing
        
        # If we have line items, format the quote
        if response.line_items:
            result.append("Here's your quote:")
            result.append("")
            
            # Add line items
            for item in response.line_items:
                result.append(f"- {item['description']}: ${item['total']:.2f}")
            
            result.append("")
            result.append(f"Total: ${response.total_amount:.2f}")
            result.append("")
        
        # Add follow-up questions
        if response.follow_up_questions:
            if not response.line_items:
                result.append("To provide you with an accurate quote, I need some additional information:")
            else:
                result.append("I have a few follow-up questions to improve your quote:")
            
            for question in response.follow_up_questions:
                result.append(f"- {question}")
            
            result.append("")
        
        return "\n".join(result)
    
    def get_conversation_context(self, request: QuoteRequest) -> List[str]:
        """
        Get relevant context to help guide the conversation.
        """
        context = []
        
        # Add service-specific context
        if 'storage' in request.services:
            if request.storage_type == 'climate_controlled':
                context.append("Our climate-controlled storage is perfect for sensitive items like electronics, artwork, or wine collections.")
            elif request.storage_type == 'hazardous':
                context.append("For hazardous materials storage, we follow strict safety protocols and regulatory compliance.")
        
        if 'transport' in request.services:
            if request.transport_type == 'local':
                context.append("Our local transport service includes same-day delivery within the metropolitan area.")
            elif request.transport_type == 'long_haul':
                context.append("For long-haul transport, we offer tracking services and guaranteed delivery timeframes.")
        
        if 'container' in request.services:
            if request.container_size == '20ft':
                context.append("Our 20ft containers are ideal for residential moves or small business inventory.")
            elif request.container_size == '40ft':
                context.append("40ft containers provide ample space for large commercial shipments or complete household relocations.")
        
        # Add customer-specific context
        if request.customer_type == 'business':
            context.append("As a business customer, you may be eligible for volume discounts on recurring services.")
        elif request.customer_type == 'individual':
            context.append("We offer flexible scheduling options for individual customers, including weekend service.")
        
        return context
    
    def _generate_follow_up_questions(self, request: QuoteRequest, missing_information: List[str]) -> List[str]:
        """
        Generate follow-up questions based on missing information.
        """
        questions = []
        
        if 'dimensions' in missing_information and 'storage' in request.services:
            questions.append("What are the dimensions (length, width, height) of the items you need to store?")
        
        if 'storage_type' in missing_information and 'storage' in request.services:
            questions.append("What type of storage do you need? We offer standard, climate-controlled, and specialized storage options.")
        
        if 'duration_weeks' in missing_information:
            if 'storage' in request.services or 'container' in request.services:
                questions.append("How long do you need the storage/container for (in weeks)?")
        
        if 'transport_type' in missing_information and 'transport' in request.services:
            questions.append("What type of transport service do you need? We offer local delivery, long-haul transport, and specialized options.")
        
        if ('from_postcode' in missing_information or 'to_postcode' in missing_information) and 'transport' in request.services:
            questions.append("Could you provide the pickup and delivery postcodes for the transport service?")
        
        if 'container_size' in missing_information and 'container' in request.services:
            questions.append("What size container do you need? We offer 20ft and 40ft containers.")
        
        if 'customer_type' in missing_information:
            questions.append("Are you inquiring as an individual or a business?")
        
        return questions
