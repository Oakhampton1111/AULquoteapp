from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PackingMaterials:
    cartons: int
    bubble_wrap_m: float
    tape_rolls: int
    blankets: int
    special_packaging: Optional[Dict[str, int]] = None

@dataclass
class ContainerRequest:
    container_size: str  # 20ft, 40ft
    is_personal_effects: bool
    item_count: int
    has_dangerous_goods: bool = False
    requires_fumigation: bool = False
    special_handling: List[str] = None  # e.g., ["fragile", "temperature_sensitive"]
    packing_materials: Optional[PackingMaterials] = None


@dataclass
class ContainerQuoteItem:
    description: str
    amount: Decimal
    quantity: int = 1
    unit: str = ""
    notes: Optional[str] = None


class ContainerCalculator:
    """
    Handles container packing service calculations including
    both commercial and personal effects.
    """
    
    def __init__(self):
        self._load_container_rates()
        
    def _load_container_rates(self):
        """Load container packing rates and materials costs."""
        # Base rates
        self.commercial_rates = {
            "20ft": Decimal("350.00"),
            "40ft": Decimal("540.00")
        }
        
        self.pe_rates = {
            "20ft": Decimal("700.00"),
            "40ft": Decimal("1100.00")
        }
        
        # Quantity breakpoints for commercial
        self.quantity_breaks = {
            "20ft": {
                400: Decimal("150.00")
            },
            "40ft": {
                400: Decimal("150.00"),
                800: Decimal("275.00")
            }
        }
        
        # Material rates
        self.material_rates = {
            "carton": Decimal("12.50"),
            "bubble_wrap_m": Decimal("3.50"),
            "tape_roll": Decimal("4.50"),
            "blanket": Decimal("15.00")
        }
        
        # Surcharges
        self.dg_surcharge = Decimal("7.50")  # per piece
        self.fumigation_fee = Decimal("180.00")
        
    def calculate_packing_cost(
        self,
        request: ContainerRequest
    ) -> List[ContainerQuoteItem]:
        """Calculate container packing cost with all applicable charges."""
        items = []
        
        # Calculate base packing cost
        if request.is_personal_effects:
            items.extend(self._calculate_pe_packing(request))
        else:
            items.extend(self._calculate_commercial_packing(request))
            
        # Add packing materials if specified
        if request.packing_materials:
            items.extend(self._calculate_material_costs(request.packing_materials))
            
        # Add surcharges
        items.extend(self._calculate_surcharges(request))
        
        return items
        
    def _calculate_pe_packing(
        self,
        request: ContainerRequest
    ) -> List[ContainerQuoteItem]:
        """Calculate personal effects packing costs."""
        if request.container_size not in self.pe_rates:
            return [ContainerQuoteItem(
                description="Invalid container size",
                amount=Decimal("0.00"),
                notes="Please specify a valid container size (20ft or 40ft)"
            )]
            
        base_rate = self.pe_rates[request.container_size]
        
        return [ContainerQuoteItem(
            description=f"Personal Effects Packing ({request.container_size})",
            amount=base_rate,
            unit="container"
        )]
        
    def _calculate_commercial_packing(
        self,
        request: ContainerRequest
    ) -> List[ContainerQuoteItem]:
        """Calculate commercial packing costs including quantity breaks."""
        if request.container_size not in self.commercial_rates:
            return [ContainerQuoteItem(
                description="Invalid container size",
                amount=Decimal("0.00"),
                notes="Please specify a valid container size (20ft or 40ft)"
            )]
            
        base_rate = self.commercial_rates[request.container_size]
        
        items = [ContainerQuoteItem(
            description=f"Commercial Packing ({request.container_size})",
            amount=base_rate,
            unit="container"
        )]
        
        # Apply quantity breaks if applicable
        if request.container_size in self.quantity_breaks:
            breaks = self.quantity_breaks[request.container_size]
            
            for threshold, discount in sorted(breaks.items(), reverse=True):
                if request.item_count >= threshold:
                    items.append(ContainerQuoteItem(
                        description=f"Volume Discount ({request.item_count} items)",
                        amount=-discount,
                        notes=f"Discount applied for {threshold}+ items"
                    ))
                    break
                    
        return items
        
    def _calculate_material_costs(
        self,
        materials: PackingMaterials
    ) -> List[ContainerQuoteItem]:
        """Calculate packing material costs."""
        items = []
        
        if materials.cartons > 0:
            items.append(ContainerQuoteItem(
                description="Packing Cartons",
                amount=self.material_rates["carton"],
                quantity=materials.cartons,
                unit="carton"
            ))
            
        if materials.bubble_wrap_m > 0:
            items.append(ContainerQuoteItem(
                description="Bubble Wrap",
                amount=self.material_rates["bubble_wrap_m"],
                quantity=materials.cartons,
                unit="meter"
            ))
            
        if materials.tape_rolls > 0:
            items.append(ContainerQuoteItem(
                description="Packing Tape",
                amount=self.material_rates["tape_roll"],
                quantity=materials.tape_rolls,
                unit="roll"
            ))
            
        if materials.blankets > 0:
            items.append(ContainerQuoteItem(
                description="Furniture Blankets",
                amount=self.material_rates["blanket"],
                quantity=materials.blankets,
                unit="blanket"
            ))
            
        if materials.special_packaging:
            for item, quantity in materials.special_packaging.items():
                items.append(ContainerQuoteItem(
                    description=f"Special Packaging: {item}",
                    amount=Decimal("25.00"),  # Default rate for special packaging
                    quantity=quantity,
                    unit="unit"
                ))
                
        return items
        
    def _calculate_surcharges(
        self,
        request: ContainerRequest
    ) -> List[ContainerQuoteItem]:
        """Calculate applicable surcharges."""
        items = []
        
        if request.has_dangerous_goods:
            items.append(ContainerQuoteItem(
                description="Dangerous Goods Handling",
                amount=self.dg_surcharge,
                quantity=request.item_count,
                unit="item",
                notes="Special handling required for dangerous goods"
            ))
            
        if request.requires_fumigation:
            items.append(ContainerQuoteItem(
                description="Fumigation Certificate",
                amount=self.fumigation_fee,
                unit="certificate",
                notes="Required for export to many countries"
            ))
            
        if request.special_handling:
            for handling in request.special_handling:
                if handling == "fragile":
                    items.append(ContainerQuoteItem(
                        description="Fragile Items Handling",
                        amount=Decimal("45.00"),
                        unit="service",
                        notes="Extra care for fragile items"
                    ))
                elif handling == "temperature_sensitive":
                    items.append(ContainerQuoteItem(
                        description="Temperature Control Preparation",
                        amount=Decimal("75.00"),
                        unit="service",
                        notes="Special preparation for temperature-sensitive items"
                    ))
                    
        return items
        
    def validate_request(self, request: ContainerRequest) -> List[str]:
        """Validate container request and return missing information."""
        missing = []
        
        if not request.container_size:
            missing.append("container_size")
        elif request.container_size not in ["20ft", "40ft"]:
            missing.append("valid_container_size")
            
        if request.item_count <= 0:
            missing.append("item_count")
            
        return missing
        
    def get_follow_up_questions(self, request: ContainerRequest) -> List[str]:
        """Generate natural follow-up questions based on missing information."""
        questions = []
        missing = self.validate_request(request)
        
        if "container_size" in missing:
            questions.append("What size container will you need? We offer 20ft and 40ft containers.")
            
        if "valid_container_size" in missing:
            questions.append("We only offer 20ft and 40ft containers. Which one would you prefer?")
            
        if "item_count" in missing:
            questions.append("Approximately how many items will need to be packed?")
            
        if not request.special_handling:
            questions.append("Do you have any items requiring special handling, such as fragile or temperature-sensitive items?")
            
        return questions
        
    def estimate_materials(
        self,
        item_count: int,
        has_furniture: bool = False
    ) -> PackingMaterials:
        """Estimate required packing materials based on item count."""
        # Simple estimation algorithm
        cartons = max(1, item_count // 3)
        bubble_wrap_m = item_count * 0.5
        tape_rolls = max(1, item_count // 20)
        blankets = 0
        
        if has_furniture:
            blankets = max(2, item_count // 5)
            
        return PackingMaterials(
            cartons=cartons,
            bubble_wrap_m=bubble_wrap_m,
            tape_rolls=tape_rolls,
            blankets=blankets
        )
