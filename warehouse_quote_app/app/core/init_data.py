"""Initial data creation for the application."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.models.user import User
from app.models.rate_card import RateCard, RateCardSettings
from app.core.config import settings

async def create_initial_data(db: AsyncSession) -> None:
    """Create initial data in database."""
    # Create superuser if it doesn't exist
    superuser = await db.get(User, settings.FIRST_SUPERUSER_ID)
    if not superuser:
        superuser = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
            full_name="Admin User",
        )
        db.add(superuser)
        await db.flush()

    # Create default rate card settings if they don't exist
    default_settings = await db.get(RateCardSettings, 1)
    if not default_settings:
        default_settings = RateCardSettings(
            name="Default Settings",
            max_quote_items=100,
            max_quote_value=1000000,
            requires_approval_above=50000,
            currency="AUD",
            created_by_id=superuser.id
        )
        db.add(default_settings)
        await db.flush()

    # Create default rate cards if they don't exist
    default_cards = [
        RateCard(
            name="Standard Storage",
            description="Standard pallet storage rates",
            rate_type="STORAGE",
            category="PALLET",
            base_rate=10.00,
            min_rate=8.00,
            max_rate=15.00,
            settings_id=default_settings.id,
            created_by_id=superuser.id
        ),
        RateCard(
            name="Standard Transport",
            description="Standard transport rates per kilometer",
            rate_type="TRANSPORT",
            category="DISTANCE",
            base_rate=2.50,
            min_rate=2.00,
            max_rate=4.00,
            settings_id=default_settings.id,
            created_by_id=superuser.id
        ),
        RateCard(
            name="Standard Handling",
            description="Standard handling rates per pallet",
            rate_type="HANDLING",
            category="PALLET",
            base_rate=5.00,
            min_rate=4.00,
            max_rate=7.00,
            settings_id=default_settings.id,
            created_by_id=superuser.id
        )
    ]
    
    for card in default_cards:
        existing = await db.execute(
            select(RateCard).where(
                RateCard.name == card.name,
                RateCard.rate_type == card.rate_type
            )
        )
        if not existing.scalar_one_or_none():
            db.add(card)
    
    await db.commit()
