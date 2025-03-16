"""Rate card and rate management endpoints."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.api import deps
from warehouse_quote_app.app.core.auth import get_current_admin_user
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.models.rate import Rate
from warehouse_quote_app.app.schemas.rate.rate_optimization import (
    OptimizationRequest,
    OptimizationResponse,
    ValidationRule,
    ValidationRuleCreate
)
from warehouse_quote_app.app.schemas.rate.rate_card import (
    RateCardCreate,
    RateCardUpdate,
    RateCardResponse,
    RateCardSettingsCreate,
    RateCardSettingsUpdate,
    RateCardSettingsResponse
)
from warehouse_quote_app.app.schemas.rate.rate import (
    RateCreate,
    RateUpdate,
    RateResponse,
    RateCategory,
    RateUnit
)
from warehouse_quote_app.app.services.business.rates import RateService
from warehouse_quote_app.app.services.llm.rate_integration import RateIntegrationService
from warehouse_quote_app.app.core.logging import get_logger

router = APIRouter(prefix="/rate-cards")
logger = get_logger("rate_cards")

# Rate Card Settings Endpoints
@router.post(
    "/settings",
    response_model=RateCardSettingsResponse,
    status_code=201,
    dependencies=[Depends(get_current_admin_user)]
)
async def create_rate_card_settings(
    settings_in: RateCardSettingsCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    """Create new rate card settings."""
    rate_service = RateService(db)
    return await rate_service.create_rate_card_settings(settings_in, db)

@router.get(
    "/settings",
    response_model=List[RateCardSettingsResponse],
    dependencies=[Depends(get_current_admin_user)]
)
async def list_rate_card_settings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(deps.get_db)
):
    """List rate card settings."""
    rate_service = RateService(db)
    return await rate_service.list_rate_card_settings(skip, limit, db)

# Rate Card Management Endpoints
@router.post(
    "",
    response_model=RateCardResponse,
    status_code=201,
    dependencies=[Depends(get_current_admin_user)]
)
async def create_rate_card(
    rate_card_in: RateCardCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    """Create new rate card."""
    rate_service = RateService(db)
    return await rate_service.create_rate_card(rate_card_in, db)

@router.get("", response_model=List[RateCardResponse])
async def list_rate_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(deps.get_db)
):
    """List rate cards."""
    rate_service = RateService(db)
    return await rate_service.list_rate_cards(skip, limit, is_active, db)

@router.get("/{rate_card_id}", response_model=RateCardResponse)
async def get_rate_card(
    rate_card_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(deps.get_db)
):
    """Get rate card by ID."""
    rate_service = RateService(db)
    return await rate_service.get_rate_card(rate_card_id, db)

@router.put("/{rate_card_id}", response_model=RateCardResponse)
async def update_rate_card(
    rate_card_id: int = Path(..., gt=0),
    rate_card_in: RateCardUpdate = None,
    db: AsyncSession = Depends(deps.get_db)
):
    """Update rate card."""
    rate_service = RateService(db)
    return await rate_service.update_rate_card(rate_card_id, rate_card_in, db)

# Rate Management Endpoints
@router.get("/rates", response_model=List[RateResponse])
async def get_rates(
    category: Optional[RateCategory] = None,
    db: AsyncSession = Depends(deps.get_db)
):
    """Get all rates or filter by category."""
    rate_service = RateService(db)
    return await rate_service.get_rates(category, db)

@router.post("/rates", response_model=RateResponse)
async def create_rate(
    rate: RateCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Create a new rate. Admin only."""
    rate_service = RateService(db)
    return await rate_service.create_rate(rate, current_user, db)

@router.put("/rates/{rate_id}", response_model=RateResponse)
async def update_rate(
    rate_id: int,
    rate: RateUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Update an existing rate. Admin only."""
    rate_service = RateService(db)
    return await rate_service.update_rate(rate_id, rate, current_user, db)

@router.delete("/rates/{rate_id}")
async def delete_rate(
    rate_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Delete a rate. Admin only."""
    rate_service = RateService(db)
    await rate_service.delete_rate(rate_id, current_user, db)
    return {"message": "Rate deleted"}
