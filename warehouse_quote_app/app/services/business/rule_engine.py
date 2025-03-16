from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class BusinessRule:
    code: str
    description: str
    error_message: str
    severity: str  # error, warning, info
    
@dataclass
class ServiceDimensions:
    has_oversized: bool

@dataclass
class ValidationContext:
    service_types: Set[str]
    has_dangerous_goods: bool
    storage_duration: Optional[int] = None
    transport_type: Optional[str] = None
    customer_type: Optional[str] = None
    is_personal_effects: bool = False
    dimensions: Optional[ServiceDimensions] = None

class BusinessRuleEngine:
    """
    Business Rule Engine that validates service combinations and enforces business rules.
    Designed to work with natural language processing systems.
    """
    
    def __init__(self):
        self._initialize_rules()
        
    def _initialize_rules(self):
        """Initialize business rules."""
        self.rules: Dict[str, BusinessRule] = {
            "DG_STORAGE": BusinessRule(
                code="DG_STORAGE",
                description="Dangerous goods require special handling and storage",
                error_message="Please note that dangerous goods storage requires special handling",
                severity="info"
            ),
            "DG_TRANSPORT": BusinessRule(
                code="DG_TRANSPORT",
                description="Dangerous goods transport restrictions",
                error_message="Transport of dangerous goods must comply with regulations",
                severity="warning"
            ),
            "CONTAINER_PACKING": BusinessRule(
                code="CONTAINER_PACKING",
                description="Container packing excludes handling out charges",
                error_message="Note: Handling out charges are not applicable for container packing",
                severity="info"
            ),
            "FREE_STORAGE": BusinessRule(
                code="FREE_STORAGE",
                description="Free storage period for qualifying cargo",
                error_message="Free storage period will be applied to your quote",
                severity="info"
            )
        }
        
        # Service compatibility matrix
        self.service_compatibility = {
            "storage": {"transport", "container_packing"},
            "transport": {"storage", "container_packing"},
            "container_packing": {"storage", "transport"}
        }
        
    def validate_service_combination(self, context: ValidationContext) -> List[str]:
        """
        Validate service combinations and return any issues.
        Returns messages in natural language format.
        """
        messages = []
        
        # Check service compatibility
        for service in context.service_types:
            compatible_services = self.service_compatibility.get(service, set())
            incompatible = context.service_types - compatible_services - {service}
            if incompatible:
                messages.append(
                    f"Please note that {service} cannot be combined with "
                    f"{', '.join(incompatible)}. Let me help you adjust your request."
                )
        
        # Check DG rules
        if context.has_dangerous_goods:
            if "storage" in context.service_types:
                messages.append(
                    "Special handling procedures apply for dangerous goods storage."
                )
            if "transport" in context.service_types:
                messages.append(
                    "Additional surcharges apply for dangerous goods transport."
                )
                
        # Check personal effects specific rules
        if context.is_personal_effects:
            if "container_packing" in context.service_types:
                messages.append(
                    "Personal effects packing requires additional documentation "
                    "and special handling procedures."
                )
            if "transport" in context.service_types:
                messages.append(
                    "Personal effects transport includes additional insurance coverage."
                )
        
        return messages
    
    def get_clarifying_questions(self, context: ValidationContext) -> List[str]:
        """
        Generate clarifying questions based on business rules.
        Returns questions in conversational format.
        """
        questions = []
        
        # Add personal effects specific questions
        if context.is_personal_effects:
            if "container_packing" in context.service_types:
                questions.append(
                    "Do you have any valuable or fragile items that require "
                    "special packing materials?"
                )
                questions.append(
                    "Would you like information about our export documentation "
                    "services for personal effects?"
                )
        
        # Add general service questions
        if "storage" in context.service_types and not context.storage_duration:
            questions.append(
                "How long do you anticipate needing storage for?"
            )
            
        if "transport" in context.service_types and not context.transport_type:
            questions.append(
                "What type of transport service do you require? We offer local, "
                "interstate, and container transport options."
            )
        
        return questions
    
    def apply_special_rules(self, context: ValidationContext) -> List[str]:
        """
        Apply special business rules and return applicable messages.
        Returns messages in natural language format.
        """
        messages = []
        
        # Add personal effects specific rules
        if context.is_personal_effects:
            messages.append(
                "As a personal effects service, we provide comprehensive "
                "insurance coverage and professional packing services."
            )
            
            if "container_packing" in context.service_types:
                messages.append(
                    "Our personal effects packing service includes high-quality "
                    "materials and expert handling of your belongings."
                )
        
        # Add service combination rules
        if len(context.service_types) > 1:
            messages.append(
                "Combined service discounts may apply to your quote. "
                "Our team will review and apply any eligible discounts."
            )
        
        # Apply storage duration rules
        if "storage" in context.service_types and context.storage_duration:
            if context.storage_duration >= 52:  # 1 year or more
                messages.append(
                    "For long-term storage (12+ months), we offer volume discounts "
                    "and flexible payment terms. Our team will contact you to discuss options."
                )
            elif context.storage_duration >= 26:  # 6 months or more
                messages.append(
                    "For medium-term storage (6+ months), we can offer competitive rates "
                    "and flexible storage solutions."
                )
            
            if context.storage_duration > 2:
                messages.append(
                    "I've applied our free storage period to your quote. "
                    "The first two weeks of storage will be complimentary."
                )
        
        # Add oversized item handling messages
        if "storage" in context.service_types:
            if context.dimensions and context.dimensions.has_oversized:
                messages.append(
                    "Special handling procedures apply for oversized items. "
                    "Our team will ensure safe storage and proper equipment is used."
                )
        
        # Apply customer type specific rules
        if context.customer_type == "preferred":
            messages.append(
                "As a preferred customer, I've applied your special rates "
                "to this quote."
            )
        
        return messages
    
    def get_rule_description(self, rule_code: str) -> Optional[str]:
        """Get description of a specific business rule."""
        rule = self.rules.get(rule_code)
        return rule.description if rule else None
