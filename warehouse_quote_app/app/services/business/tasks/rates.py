"""
Rate-related background tasks.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tasks.celery import celery_app
from app.models.rate import Rate, RateCard
from app.core.db import get_db
from app.services.business.rates import RateService

@celery_app.task
async def update_rate_cards() -> int:
    """Update all rate cards with latest rates.
    
    Returns:
        int: Number of rate cards updated
    """
    session = next(get_db())
    rate_service = RateService(session)
    
    # Get all active rate cards
    rate_cards = await session.execute(
        select(RateCard).where(RateCard.is_active == True)
    ).scalars().all()
    
    # Update each rate card with latest rates
    updated_count = 0
    for card in rate_cards:
        try:
            await rate_service.update_rate_card(card.id)
            updated_count += 1
        except Exception as e:
            # Log error but continue processing other cards
            print(f"Error updating rate card {card.id}: {str(e)}")
    
    await session.commit()
    return updated_count

@celery_app.task
async def optimize_rate_cards() -> int:
    """Run optimization on all active rate cards.
    
    Returns:
        int: Number of rate cards optimized
    """
    session = next(get_db())
    rate_service = RateService(session)
    
    # Get all active rate cards
    rate_cards = await session.execute(
        select(RateCard).where(RateCard.is_active == True)
    ).scalars().all()
    
    # Optimize each rate card
    optimized_count = 0
    for card in rate_cards:
        try:
            await rate_service.optimize_rate(card.id, {"time_range": 90})
            optimized_count += 1
        except Exception as e:
            # Log error but continue processing other cards
            print(f"Error optimizing rate card {card.id}: {str(e)}")
    
    await session.commit()
    return optimized_count

__all__ = ['update_rate_cards', 'optimize_rate_cards']
