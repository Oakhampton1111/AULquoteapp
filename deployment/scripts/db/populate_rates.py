from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud.rate_card import RateCardService
from app.schemas.rate_card import RateCardCreate, RateType, RateCategory, ClientType

def populate_rates(db: Session):
    rate_service = RateCardService()
    
    # Storage and Handling Rates
    rates = [
        # Internal Storage Rates
        RateCardCreate(
            name="Internal Pallet Storage",
            description="Pallet Storage - Internal Racked 1.2 x 1.2 x 1.65m",
            rate_type=RateType.STORAGE,
            category=RateCategory.PALLET,
            base_rate=Decimal("5.00"),
            min_charge=Decimal("40.00"),
            per_unit="per_pallet_per_week",
            client_type=ClientType.ALL,
            conditions=None,
            is_active=True
        ),
        RateCardCreate(
            name="External Pallet Storage",
            description="Pallet Storage - External Covered Area",
            rate_type=RateType.STORAGE,
            category=RateCategory.PALLET,
            base_rate=Decimal("3.50"),
            min_charge=Decimal("30.00"),
            per_unit="per_pallet_per_week",
            client_type=ClientType.ALL,
            conditions=None,
            is_active=True
        ),
        RateCardCreate(
            name="Bulk Storage",
            description="Bulk Storage Area - Floor Space",
            rate_type=RateType.STORAGE,
            category=RateCategory.BULK,
            base_rate=Decimal("2.00"),
            min_charge=Decimal("100.00"),
            per_unit="per_sqm_per_week",
            client_type=ClientType.ALL,
            conditions=None,
            is_active=True
        ),
        
        # Handling Rates
        RateCardCreate(
            name="Pallet In",
            description="Unloading and Put-away of Pallets",
            rate_type=RateType.HANDLING,
            category=RateCategory.INBOUND,
            base_rate=Decimal("6.50"),
            min_charge=Decimal("50.00"),
            per_unit="per_pallet",
            client_type=ClientType.ALL,
            conditions=None,
            is_active=True
        ),
        RateCardCreate(
            name="Pallet Out",
            description="Picking and Loading of Pallets",
            rate_type=RateType.HANDLING,
            category=RateCategory.OUTBOUND,
            base_rate=Decimal("6.50"),
            min_charge=Decimal("50.00"),
            per_unit="per_pallet",
            client_type=ClientType.ALL,
            conditions=None,
            is_active=True
        ),
        
        # Value-Added Services
        RateCardCreate(
            name="Labeling",
            description="Product Labeling Service",
            rate_type=RateType.VALUE_ADDED,
            category=RateCategory.LABELING,
            base_rate=Decimal("0.50"),
            min_charge=Decimal("25.00"),
            per_unit="per_item",
            client_type=ClientType.ALL,
            conditions=None,
            is_active=True
        ),
        RateCardCreate(
            name="Repacking",
            description="Product Repacking Service",
            rate_type=RateType.VALUE_ADDED,
            category=RateCategory.REPACKING,
            base_rate=Decimal("1.00"),
            min_charge=Decimal("30.00"),
            per_unit="per_item",
            client_type=ClientType.ALL,
            conditions=None,
            is_active=True
        ),
        
        # Transport Rates
        RateCardCreate(
            name="Local Delivery - Small Van",
            description="Local Delivery Service using Small Van",
            rate_type=RateType.TRANSPORT,
            category=RateCategory.LOCAL_DELIVERY,
            base_rate=Decimal("80.00"),
            min_charge=Decimal("80.00"),
            per_unit="per_trip",
            client_type=ClientType.ALL,
            conditions={"max_weight": 1000, "max_pallets": 2},
            is_active=True
        ),
        RateCardCreate(
            name="Local Delivery - Medium Truck",
            description="Local Delivery Service using Medium Truck",
            rate_type=RateType.TRANSPORT,
            category=RateCategory.LOCAL_DELIVERY,
            base_rate=Decimal("120.00"),
            min_charge=Decimal("120.00"),
            per_unit="per_trip",
            client_type=ClientType.ALL,
            conditions={"max_weight": 4000, "max_pallets": 6},
            is_active=True
        ),
        
        # Special Rates for Corporate Clients
        RateCardCreate(
            name="Corporate Bulk Storage",
            description="Bulk Storage Area - Floor Space (Corporate Rate)",
            rate_type=RateType.STORAGE,
            category=RateCategory.BULK,
            base_rate=Decimal("1.80"),
            min_charge=Decimal("90.00"),
            per_unit="per_sqm_per_week",
            client_type=ClientType.CORPORATE,
            conditions={"min_volume": 100},
            is_active=True
        ),
        RateCardCreate(
            name="Corporate Pallet Storage",
            description="Pallet Storage - Internal (Corporate Rate)",
            rate_type=RateType.STORAGE,
            category=RateCategory.PALLET,
            base_rate=Decimal("4.50"),
            min_charge=Decimal("35.00"),
            per_unit="per_pallet_per_week",
            client_type=ClientType.CORPORATE,
            conditions={"min_pallets": 50},
            is_active=True
        ),
    ]
    
    # Create rates in database
    for rate in rates:
        try:
            rate_service.create_rate(db, rate)
            print(f"Created rate: {rate.name}")
        except Exception as e:
            print(f"Error creating rate {rate.name}: {str(e)}")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        populate_rates(db)
    finally:
        db.close()
