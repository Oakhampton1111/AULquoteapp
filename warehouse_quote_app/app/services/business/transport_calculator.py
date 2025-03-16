from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from .distance_calculator import DistanceCalculator

@dataclass
class TransportRequest:
    transport_type: str  # local, long_haul, container
    from_postcode: str
    to_postcode: str
    container_size: Optional[str] = None  # 20ft, 40ft
    duration_hours: Optional[float] = None
    is_dangerous_goods: bool = False
    vehicle_type: Optional[str] = None  # semi_trailer, b_double
    return_journey: bool = True
    additional_charges: Dict[str, Decimal] = None

@dataclass
class TransportQuoteItem:
    description: str
    amount: Decimal
    unit: str
    notes: Optional[str] = None

class TransportCalculator:
    """
    Handles all transport-related rate calculations including
    mandatory charges and special conditions.
    """
    
    def __init__(self):
        self._load_transport_rates()
        self.distance_calculator = DistanceCalculator()
        
    def _load_transport_rates(self):
        """Load transport rates and surcharges."""
        # Base rates
        self.local_rates = {
            "semi_trailer": Decimal("180.00"),  # per hour
            "b_double": Decimal("220.00")       # per hour
        }
        
        self.long_haul_rates = {
            "semi_trailer": Decimal("3.50"),    # per km
            "b_double": Decimal("4.20")         # per km
        }
        
        self.container_rates = {
            "20ft": {
                "local": Decimal("350.00"),
                "metro": Decimal("450.00")
            },
            "40ft": {
                "local": Decimal("420.00"),
                "metro": Decimal("520.00")
            }
        }
        
        # Surcharge rates
        self.fuel_surcharges = {
            "local": Decimal("0.24"),       # 24%
            "long_haul": Decimal("0.15"),   # 15%
            "container": Decimal("0.1967")  # 19.67%
        }
        
        # Fixed charges
        self.road_toll = Decimal("50.00")
        self.dg_surcharge = Decimal("130.00")  # per container
        
        # Terminal fees (example rates)
        self.terminal_fees = {
            "20ft": Decimal("95.00"),
            "40ft": Decimal("125.00")
        }
        
    def calculate_transport_cost(
        self,
        request: TransportRequest
    ) -> List[TransportQuoteItem]:
        """Calculate transport cost with all applicable charges."""
        items = []
        
        # Calculate distance and determine transport type
        try:
            distance_km, suggested_type = self.distance_calculator.calculate_distance(
                request.from_postcode,
                request.to_postcode
            )
            
            # Override transport type if zones suggest different type
            if request.transport_type != "container":  # Don't override container transport
                request.transport_type = suggested_type
                
            # Add distance information to items for long haul
            if request.transport_type == "long_haul":
                request.distance_km = distance_km
                
        except ValueError as e:
            # Handle invalid postcodes
            raise ValueError(f"Invalid postcode in transport request: {str(e)}")
        
        if request.transport_type == "local":
            items.extend(self._calculate_local_transport(request))
        elif request.transport_type == "long_haul":
            items.extend(self._calculate_long_haul_transport(request))
        else:  # container
            items.extend(self._calculate_container_transport(request))
            
        # Add road tolls (mandatory for all transport)
        items.append(TransportQuoteItem(
            description="Road Tolls",
            amount=self.road_toll,
            unit="fixed",
            notes="Mandatory charge for all transport services"
        ))
        
        # Add DG surcharge if applicable
        if request.is_dangerous_goods:
            items.append(TransportQuoteItem(
                description="Dangerous Goods Surcharge",
                amount=self.dg_surcharge,
                unit="container",
                notes="DG handling and documentation"
            ))
            
        return items
        
    def _calculate_local_transport(
        self,
        request: TransportRequest
    ) -> List[TransportQuoteItem]:
        """Calculate local transport costs including minimum hours."""
        items = []
        
        # Get hourly rate
        hourly_rate = self.local_rates[request.vehicle_type]
        
        # Apply minimum 4 hours
        hours = max(4.0, request.duration_hours or 4.0)
        base_amount = hourly_rate * Decimal(str(hours))
        
        items.append(TransportQuoteItem(
            description=f"Local Transport - {request.vehicle_type.replace('_', ' ').title()}",
            amount=base_amount,
            unit="hours",
            notes=f"${hourly_rate}/hour, minimum 4 hours"
        ))
        
        # Add fuel surcharge
        fuel_surcharge = base_amount * self.fuel_surcharges["local"]
        items.append(TransportQuoteItem(
            description="Fuel Surcharge",
            amount=fuel_surcharge,
            unit="percentage",
            notes="24% on local transport"
        ))
        
        return items
        
    def _calculate_long_haul_transport(
        self,
        request: TransportRequest
    ) -> List[TransportQuoteItem]:
        """Calculate long haul transport costs including return journey."""
        items = []
        
        # Get per-km rate
        km_rate = self.long_haul_rates[request.vehicle_type]
        
        # Calculate total distance including return if applicable
        total_km = request.distance_km * (2 if request.return_journey else 1)
        base_amount = km_rate * Decimal(str(total_km))
        
        items.append(TransportQuoteItem(
            description=f"Long Haul Transport - {request.vehicle_type.replace('_', ' ').title()}",
            amount=base_amount,
            unit="km",
            notes=f"${km_rate}/km{' (including return journey)' if request.return_journey else ''}"
        ))
        
        # Add fuel surcharge
        fuel_surcharge = base_amount * self.fuel_surcharges["long_haul"]
        items.append(TransportQuoteItem(
            description="Fuel Surcharge",
            amount=fuel_surcharge,
            unit="percentage",
            notes="15% on long haul transport"
        ))
        
        return items
        
    def _calculate_container_transport(
        self,
        request: TransportRequest
    ) -> List[TransportQuoteItem]:
        """Calculate container transport costs including terminal fees."""
        items = []
        
        # Get base rate
        base_rate = self.container_rates[request.container_size]["local"]
        items.append(TransportQuoteItem(
            description=f"Container Transport - {request.container_size}",
            amount=base_rate,
            unit="container",
            notes="Base rate for container transport"
        ))
        
        # Add fuel surcharge
        fuel_surcharge = base_rate * self.fuel_surcharges["container"]
        items.append(TransportQuoteItem(
            description="Fuel Surcharge",
            amount=fuel_surcharge,
            unit="percentage",
            notes="19.67% on container transport"
        ))
        
        # Add terminal fee
        terminal_fee = self.terminal_fees[request.container_size]
        items.append(TransportQuoteItem(
            description="Terminal Fee",
            amount=terminal_fee,
            unit="container",
            notes=f"Standard terminal fee for {request.container_size}"
        ))
        
        return items
        
    def validate_request(self, request: TransportRequest) -> List[str]:
        """Validate transport request and return missing information."""
        missing = []
        
        # Always validate postcodes
        if not request.from_postcode:
            missing.append("pickup postcode")
        elif not self.distance_calculator.validate_postcode(request.from_postcode):
            missing.append(f"valid pickup postcode ('{request.from_postcode}' not found)")
            
        if not request.to_postcode:
            missing.append("delivery postcode")
        elif not self.distance_calculator.validate_postcode(request.to_postcode):
            missing.append(f"valid delivery postcode ('{request.to_postcode}' not found)")
        
        if request.transport_type in ["local", "long_haul"]:
            if not request.vehicle_type:
                missing.append("vehicle type (semi-trailer or B-double)")
                
            if request.transport_type == "local" and not request.duration_hours:
                missing.append("estimated duration in hours")
                
        elif request.transport_type == "container":
            if not request.container_size:
                missing.append("container size (20ft or 40ft)")
                
        return missing
        
    def get_follow_up_questions(self, request: TransportRequest) -> List[str]:
        """Generate natural follow-up questions based on missing information."""
        questions = []
        missing = self.validate_request(request)
        
        for item in missing:
            if "pickup postcode" in item:
                questions.append(
                    "What's the pickup location? You can provide a postcode or suburb name."
                )
            elif "delivery postcode" in item:
                questions.append(
                    "Where would you like the delivery to go? You can provide a postcode or suburb name."
                )
            elif "valid pickup postcode" in item:
                questions.append(
                    f"I couldn't find the pickup postcode. Could you please verify it "
                    f"or provide a suburb name instead?"
                )
            elif "valid delivery postcode" in item:
                questions.append(
                    f"I couldn't find the delivery postcode. Could you please verify it "
                    f"or provide a suburb name instead?"
                )
            elif item == "vehicle type (semi-trailer or B-double)":
                questions.append(
                    "What type of vehicle do you need? We offer semi-trailers and B-doubles."
                )
            elif item == "estimated duration in hours":
                questions.append(
                    "How many hours do you expect to need the transport? "
                    "Note that there is a minimum charge of 4 hours."
                )
            elif item == "container size (20ft or 40ft)":
                questions.append(
                    "Which container size do you need, 20ft or 40ft?"
                )
                
        return questions
        
    def get_zone_info(self, postcode: str) -> Optional[Dict]:
        """Get zone information for a postcode."""
        return self.distance_calculator.get_zone_info(postcode)
