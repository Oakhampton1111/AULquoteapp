"""Add a new rate card to the database."""
from datetime import datetime, timezone
from decimal import Decimal

from warehouse_quote_app.models import RateCard, RateCardSettings, CustomerRateCard
from .base_script import DatabaseScript

def add_rate_cards():
    """Add rate cards to the database."""
    script = DatabaseScript(models=[RateCard, RateCardSettings, CustomerRateCard])
    
    with script as db:
        # Create settings first
        settings = RateCardSettings(
            name="Default Settings",
            description="Default rate card settings",
            is_active=True,
            minimum_charge=Decimal("0.00"),
            handling_fee_percentage=Decimal("0.00"),
            tax_rate=Decimal("0.10"),
            volume_discount_tiers={
                "tier1": {"min_amount": 1000, "discount": 0.05},
                "tier2": {"min_amount": 5000, "discount": 0.10},
                "tier3": {"min_amount": 10000, "discount": 0.15}
            }
        )
        script.add_and_flush(db, settings)

        # Create rate cards
        cards = [
            RateCard(
                name="Standard Pallet Storage",
                description="Internal Racked Storage for Standard Pallet (1.2 x 1.2 x 1.65m)",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                settings_id=settings.id,
                rates={
                    "storage": {
                        "pallet": {
                            "rate": "4.50",
                            "unit": "per pallet per day",
                            "min_units": 1
                        }
                    },
                    "handling": {
                        "inbound": {
                            "rate": "6.00",
                            "unit": "per pallet",
                            "min_units": 1
                        },
                        "outbound": {
                            "rate": "6.00",
                            "unit": "per pallet",
                            "min_units": 1
                        }
                    }
                }
            ),
            RateCard(
                name="Bulk Storage",
                description="Floor Space Storage for Bulk Items",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                settings_id=settings.id,
                rates={
                    "storage": {
                        "floor_space": {
                            "rate": "2.50",
                            "unit": "per square meter per day",
                            "min_units": 10
                        }
                    },
                    "handling": {
                        "inbound": {
                            "rate": "45.00",
                            "unit": "per hour",
                            "min_units": 1
                        },
                        "outbound": {
                            "rate": "45.00",
                            "unit": "per hour",
                            "min_units": 1
                        }
                    }
                }
            )
        ]
        script.bulk_save(db, cards)

if __name__ == "__main__":
    add_rate_cards()
