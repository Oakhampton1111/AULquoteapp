"""Create initial rate cards."""
from datetime import datetime, timezone
from decimal import Decimal
import sys
import os
from pathlib import Path

# Add the parent directory to Python path to import app modules
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from app.database import SessionLocal, Base, engine
from app.models.rate_card import RateCard, RateCardSettings
from app.models.customer import Customer
from app.models.quote import Quote
from app.models.user import User

# Create tables
Base.metadata.create_all(bind=engine)

def create_initial_rates():
    """Create initial rate cards."""
    db = SessionLocal()
    try:
        # First create rate card settings
        settings = RateCardSettings(
            name="Default Settings",
            description="Default rate card settings",
            is_active=True,
            minimum_charge=Decimal("0.00"),
            handling_fee_percentage=Decimal("0.00"),
            tax_rate=Decimal("0.10")
        )
        db.add(settings)
        db.flush()

        rates = [
            # Storage Rates
            RateCard(
                name="Standard Pallet Storage - Internal",
                description="Internal Racked Storage for Standard Pallet (1.2 x 1.2 x 1.65m)",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "storage": {
                        "pallet": {
                            "rate": "5.00",
                            "unit": "per_week",
                            "min_quantity": 1
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Non-Rackable Cargo - Internal Storage",
                description="Internal Storage for Non-Rackable Cargo with 2 weeks free storage",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "storage": {
                        "sqm": {
                            "rate": "4.00",
                            "unit": "per_week",
                            "min_quantity": 1,
                            "free_period_weeks": 2
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Oversize Cargo - Internal Storage",
                description="Internal Storage for Oversize Cargo with 2 weeks free storage",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "storage": {
                        "cbm": {
                            "rate": "4.00",
                            "unit": "per_week",
                            "min_quantity": 1,
                            "free_period_weeks": 2
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Pallet Storage - External",
                description="External Pallet Storage with 2 weeks free storage",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "storage": {
                        "pallet": {
                            "rate": "3.50",
                            "unit": "per_week",
                            "min_quantity": 1,
                            "free_period_weeks": 2
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Non-Rackable Cargo - External Storage",
                description="External Storage for Non-Rackable Cargo with 2 weeks free storage",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "storage": {
                        "sqm": {
                            "rate": "3.00",
                            "unit": "per_week",
                            "min_quantity": 1,
                            "free_period_weeks": 2
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Oversize Cargo - External Storage",
                description="External Storage for Oversize Cargo with 2 weeks free storage",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "storage": {
                        "cbm": {
                            "rate": "3.00",
                            "unit": "per_week",
                            "min_quantity": 1,
                            "free_period_weeks": 2
                        }
                    }
                },
                settings_id=settings.id
            ),
            
            # Pallet Supply Rates
            RateCard(
                name="New Pallet Supply - Export ISPM15",
                description="New Export ISPM15 Compliant Pallet Supply including Wrapping",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "supply": {
                        "pallet": {
                            "rate": "50.00",
                            "unit": "per_unit",
                            "min_quantity": 1,
                            "includes": ["wrapping"]
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Used Pallet Supply - Export ISPM15",
                description="Used Export ISPM15 Compliant Pallet Supply including Wrapping",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "supply": {
                        "pallet": {
                            "rate": "20.00",
                            "unit": "per_unit",
                            "min_quantity": 1,
                            "includes": ["wrapping"]
                        }
                    }
                },
                settings_id=settings.id
            ),
            
            # Handling Rates
            RateCard(
                name="Standard Handling",
                description="Handling In/Out for Standard Pallets or Smaller Packages",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "handling": {
                        "pallet_package": {
                            "rate": "5.00",
                            "unit": "per_unit",
                            "min_quantity": 1
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Oversize Handling",
                description="Handling In/Out for Oversize Cargo",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "handling": {
                        "sqm_cbm": {
                            "rate": "3.00",
                            "unit": "per_unit",
                            "min_quantity": 1
                        }
                    }
                },
                settings_id=settings.id
            ),
            
            # Additional Services
            RateCard(
                name="Dangerous Goods Surcharge",
                description="Additional charge for handling dangerous goods",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "surcharge": {
                        "pallet_package": {
                            "rate": "6.25",
                            "unit": "per_unit",
                            "min_quantity": 1
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Cargo Labelling",
                description="Cargo labelling service when requested",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "service": {
                        "pallet_package": {
                            "rate": "1.50",
                            "unit": "per_unit",
                            "min_quantity": 1
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Re-Weigh and Measure",
                description="Re-weighing and measuring cargo when requested",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "service": {
                        "pallet_package": {
                            "rate": "0.75",
                            "unit": "per_unit",
                            "min_quantity": 1
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Additional Labour",
                description="Additional labour for repacking and strapping",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "labour": {
                        "person_hour": {
                            "rate": "60.00",
                            "unit": "per_hour",
                            "min_quantity": 1
                        }
                    }
                },
                settings_id=settings.id
            )
        ]

        # Add container handling rates
        container_handling_rates = [
            RateCard(
                name="20FT Container Packing",
                description="Standard packing service for 20FT container",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "container_packing": {
                        "20ft": {
                            "base_rate": "350.00",
                            "unit": "per_container",
                            "additional_charges": {
                                "over_400_items": "150.00"
                            }
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="40FT Container Packing",
                description="Standard packing service for 40FT container",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "container_packing": {
                        "40ft": {
                            "base_rate": "540.00",
                            "unit": "per_container",
                            "additional_charges": {
                                "over_400_items": "150.00",
                                "over_800_items": "275.00"
                            }
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Container DG Surcharge",
                description="Dangerous goods surcharge for container packing",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "surcharge": {
                        "dg_piece": {
                            "rate": "7.50",
                            "unit": "per_piece"
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Personal Effects Container",
                description="Container packing for personal effects",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "personal_effects": {
                        "20ft": {
                            "rate": "700.00",
                            "unit": "per_container"
                        },
                        "40ft": {
                            "rate": "1100.00",
                            "unit": "per_container"
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Container Storage - Free Cargo",
                description="Storage for containers with free cargo",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "storage": {
                        "20ft": {
                            "rate": "120.00",
                            "unit": "per_week_or_part"
                        },
                        "40ft": {
                            "rate": "200.00",
                            "unit": "per_week_or_part"
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Urgent Container Pack",
                description="Urgent packing service for containers",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "urgent_packing": {
                        "20ft": {
                            "rate": "150.00",
                            "unit": "per_container"
                        },
                        "40ft": {
                            "rate": "225.00",
                            "unit": "per_container"
                        }
                    }
                },
                settings_id=settings.id
            )
        ]

        # Add container transport rates
        container_transport_rates = [
            RateCard(
                name="Container Side Loader Cartage",
                description="Side loader cartage including empty de-hire",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "cartage": {
                        "20ft": {
                            "base_rate": "435.00",
                            "unit": "per_container",
                            "fuel_surcharge": "current",
                            "terminal_fees": "at_cost"
                        },
                        "40ft": {
                            "base_rate": "510.00",
                            "unit": "per_container",
                            "fuel_surcharge": "current",
                            "terminal_fees": "at_cost"
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Container Transport Surcharges",
                description="Additional charges for container transport",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "surcharges": {
                        "overweight_22_5t": {
                            "rate": "250.00",
                            "unit": "per_container"
                        },
                        "waiting_time": {
                            "rate": "150.00",
                            "unit": "per_hour"
                        },
                        "dg_cartage": {
                            "rate": "130.00",
                            "unit": "per_container"
                        },
                        "road_tolls": {
                            "rate": "50.00",
                            "unit": "per_trip"
                        },
                        "vgm_cwd": {
                            "rate": "50.00",
                            "unit": "per_container"
                        }
                    }
                },
                settings_id=settings.id
            )
        ]

        # Add cartage rates
        cartage_rates = [
            RateCard(
                name="Air Export Cargo Cartage",
                description="Cartage for lodging air export cargo",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "cartage": {
                        "air_export": {
                            "rate": "0.125",
                            "unit": "per_kg_chargeable",
                            "minimum_charge": "160.00"
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Local Transport",
                description="Local transport services",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "local": {
                        "semi_trailer": {
                            "rate": "135.00",
                            "unit": "per_hour",
                            "fuel_surcharge_percent": "24",
                            "minimum_hours": 4
                        },
                        "b_double": {
                            "rate": "175.00",
                            "unit": "per_hour",
                            "fuel_surcharge_percent": "24",
                            "minimum_hours": 4
                        }
                    }
                },
                settings_id=settings.id
            ),
            RateCard(
                name="Long Haul Transport",
                description="Long haul transport services",
                is_active=True,
                effective_from=datetime.now(timezone.utc),
                rates={
                    "long_haul": {
                        "semi_trailer": {
                            "rate": "2.75",
                            "unit": "per_km_both_ways",
                            "fuel_surcharge_percent": "15"
                        },
                        "b_double": {
                            "rate": "3.05",
                            "unit": "per_km_both_ways",
                            "fuel_surcharge_percent": "15"
                        }
                    }
                },
                settings_id=settings.id
            )
        ]

        # Add all rates
        for rate in rates + container_handling_rates + container_transport_rates + cartage_rates:
            db.add(rate)

        db.commit()
        print("Successfully created initial rate cards!")
        
    except Exception as e:
        print(f"Error creating initial rate cards: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_rates()
