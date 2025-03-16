from decimal import Decimal, ROUND_HALF_UP, localcontext
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ServiceDimensions:
    """Dimensions for storage service calculations"""
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    
    @property
    def volume(self) -> Optional[float]:
        """Calculate volume in cubic meters."""
        if self.length is None or self.width is None or self.height is None:
            return None
        return self.length * self.width * self.height
    
    @property
    def floor_area(self) -> Optional[float]:
        """Calculate floor area in square meters."""
        if self.length is None or self.width is None:
            return None
        return self.length * self.width
    
    def __str__(self) -> str:
        return f"{self.length}m x {self.width}m x {self.height}m"


@dataclass
class StorageRequest:
    dimensions: ServiceDimensions
    duration_weeks: int
    quantity: int
    storage_type: str
    has_dangerous_goods: bool = False


@dataclass
class QuoteLineItem:
    description: str
    amount: Decimal
    quantity: int = 1
    unit: str = ""
    notes: Optional[str] = None


@dataclass
class RateResult:
    line_items: List[Dict[str, Any]]
    total_amount: Decimal
    notes: List[str] = None
    
    def __post_init__(self):
        if self.notes is None:
            self.notes = []


class RateCalculator:
    """Central rate calculation service that handles all pricing logic.
    Designed to work with natural language inputs after processing."""
    
    def __init__(self):
        """Initialize rate calculator with storage rates."""
        self.storage_rates = {
            "standard": {
                "rate": Decimal("10.00"),  # per m³ per week
                "unit": "m³",
                "min_charge": Decimal("50.00"),
                "display_name": "Standard Storage"
            },
            "climate_controlled": {
                "rate": Decimal("15.00"),  # per m³ per week
                "unit": "m³",
                "min_charge": Decimal("75.00"),
                "display_name": "Climate-Controlled Storage"
            },
            "hazardous": {
                "rate": Decimal("20.00"),  # per m³ per week
                "unit": "m³",
                "min_charge": Decimal("100.00"),
                "display_name": "Hazardous Materials Storage"
            }
        }
        
        self.surcharges = {
            "dangerous_goods": Decimal("0.25"),  # 25% surcharge
            "after_hours": Decimal("0.15"),  # 15% surcharge
            "rush_service": Decimal("0.20"),  # 20% surcharge
            "weekend": Decimal("0.10"),  # 10% surcharge
        }
        
        self.handling_fees = {
            "standard": Decimal("5.00"),  # per unit
            "hazardous": Decimal("15.00")  # per hazardous unit
        }
        
        self.applied_rules = []
    
    def _load_rate_configuration(self):
        """Load rate configuration from database or settings."""
        # In a real implementation, this would load from a database
        pass
    
    def calculate_storage_rate(self, request: StorageRequest) -> RateResult:
        """Calculate storage costs based on the request parameters."""
        self.applied_rules = []
        
        if request.storage_type not in self.storage_rates:
            return RateResult(
                line_items=[],
                total_amount=Decimal('0.00'),
                notes=[f"Unknown storage type: {request.storage_type}"]
            )
        
        # Get rate information
        rate_info = self.storage_rates[request.storage_type]
        rate = rate_info["rate"]
        unit = rate_info["unit"]
        min_charge = rate_info.get("min_charge", Decimal('0.00'))
        display_name = rate_info["display_name"]
        
        # Calculate volume if needed
        volume = None
        if unit == "m³" and request.dimensions:
            volume = request.dimensions.volume
            if volume is None:
                return RateResult(
                    line_items=[],
                    total_amount=Decimal('0.00'),
                    notes=["Missing dimensions for volume calculation"]
                )
        
        # Calculate base storage cost
        if unit == "m³":
            base_cost = rate * Decimal(str(volume)) * request.quantity * request.duration_weeks
            self.applied_rules.append("Applied volume-based pricing")
        else:
            base_cost = rate * request.quantity * request.duration_weeks
            self.applied_rules.append("Applied unit-based pricing")
        
        # Apply minimum charge if needed
        if base_cost < min_charge:
            base_cost = min_charge
            self.applied_rules.append(f"Applied minimum charge of ${min_charge}")
        
        # Round to 2 decimal places
        with localcontext() as ctx:
            ctx.rounding = ROUND_HALF_UP
            base_cost = base_cost.quantize(Decimal('0.01'))
        
        # Create line items
        line_items = []
        
        # Add base storage cost
        if unit == "m³":
            description = f"{display_name} ({volume:.2f} {unit} x {request.quantity} units x {request.duration_weeks} weeks)"
        else:
            description = f"{display_name} ({request.quantity} units x {request.duration_weeks} weeks)"
        
        line_items.append({
            "description": description,
            "quantity": 1,
            "unit_price": float(base_cost),
            "total": float(base_cost)
        })
        
        total_amount = base_cost
        
        # Apply dangerous goods surcharge if needed
        if request.has_dangerous_goods:
            dg_surcharge = base_cost * self.surcharges["dangerous_goods"]
            with localcontext() as ctx:
                ctx.rounding = ROUND_HALF_UP
                dg_surcharge = dg_surcharge.quantize(Decimal('0.01'))
            
            line_items.append({
                "description": "Dangerous Goods Surcharge (25%)",
                "quantity": 1,
                "unit_price": float(dg_surcharge),
                "total": float(dg_surcharge)
            })
            
            total_amount += dg_surcharge
            self.applied_rules.append("Applied dangerous goods surcharge")
        
        # Add handling fees
        handling_fee_type = "hazardous" if request.has_dangerous_goods else "standard"
        handling_fee = self.handling_fees[handling_fee_type] * request.quantity
        
        line_items.append({
            "description": f"Handling Fee ({request.quantity} units)",
            "quantity": request.quantity,
            "unit_price": float(self.handling_fees[handling_fee_type]),
            "total": float(handling_fee)
        })
        
        total_amount += handling_fee
        self.applied_rules.append("Applied handling fees")
        
        # Prepare notes
        notes = []
        
        if request.has_dangerous_goods:
            notes.append("Dangerous goods require special handling and storage procedures.")
        
        if request.storage_type == "climate_controlled":
            notes.append("Climate-controlled storage maintains temperature between 18-22°C and humidity between 45-55%.")
        
        if request.duration_weeks > 52:
            notes.append("Long-term storage discounts may be available for commitments over 1 year.")
        
        return RateResult(
            line_items=line_items,
            total_amount=total_amount,
            notes=notes
        )
    
    def get_applied_rules(self) -> List[str]:
        """Get list of business rules applied in calculation."""
        return self.applied_rules
