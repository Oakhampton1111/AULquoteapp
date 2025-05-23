﻿"""Rate card and rate management endpoints."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.api import deps
from app.core.auth import get_current_admin_user
from app.models.user import User
from app.models.rate_optimization import (
    RateOptimizationHistory,
    RateValidationRule,
    MarketRateAnalysis
)
from app.schemas.rate.rate_card import (
    RateCardCreate,
    RateCardUpdate,
    RateCardResponse,
    RateCardSettingsCreate,
    RateCardSettingsUpdate,
    RateCardSettingsResponse
)
from app.schemas.rate.rate import (
    RateCreate,
    RateUpdate,
    RateResponse,
    RateCategory,
    RateUnit
)
from app.schemas.rate.rate_optimization import (
    OptimizationRequest,
    OptimizationResponse,
    ValidationRule,
    ValidationRuleCreate,
    MarketAnalysis,
    MarketAnalysisCreate
)
from app.services.business.rates import RateService
from app.services.llm.rate_integration import RateIntegrationService
from app.core.logging import get_logger

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
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db)
):
    """Create new rate card settings."""
    return await rate_service.create_rate_card_settings(settings_in, db)

@router.get(
    "/settings",
    response_model=List[RateCardSettingsResponse],
    dependencies=[Depends(get_current_admin_user)]
)
async def list_rate_card_settings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db)
):
    """List rate card settings."""
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
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db)
):
    """Create new rate card."""
    return await rate_service.create_rate_card(rate_card_in, db)

@router.get(
    "",
    response_model=List[RateCardResponse]
)
async def list_rate_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db)
):
    """List rate cards."""
    return await rate_service.list_rate_cards(skip, limit, is_active, db)

@router.get(
    "/{rate_card_id}",
    response_model=RateCardResponse
)
async def get_rate_card(
    rate_card_id: int = Path(..., gt=0),
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db)
):
    """Get rate card by ID."""
    return await rate_service.get_rate_card(rate_card_id, db)

@router.patch(
    "/{rate_card_id}",
    response_model=RateCardResponse,
    dependencies=[Depends(get_current_admin_user)]
)
async def update_rate_card(
    rate_card_id: int = Path(..., gt=0),
    rate_card_in: RateCardUpdate = None,
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db)
):
    """Update rate card."""
    return await rate_service.update_rate_card(rate_card_id, rate_card_in, db)

# Rate Management Endpoints
@router.get("/rates", response_model=List[RateResponse])
async def get_rates(
    category: Optional[RateCategory] = None,
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db)
):
    """Get all rates or filter by category."""
    return await rate_service.get_rates(category, db)

@router.post("/rates", response_model=RateResponse)
async def create_rate(
    rate: RateCreate,
    rate_service: RateService = Depends(),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(deps.get_db)
):
    """Create a new rate. Admin only."""
    return await rate_service.create_rate(rate, current_user, db)

@router.put("/rates/{rate_id}", response_model=RateResponse)
async def update_rate(
    rate_id: int,
    rate: RateUpdate,
    rate_service: RateService = Depends(),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(deps.get_db)
):
    """Update an existing rate. Admin only."""
    return await rate_service.update_rate(rate_id, rate, current_user, db)

@router.delete("/rates/{rate_id}")
async def delete_rate(
    rate_id: int,
    rate_service: RateService = Depends(),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(deps.get_db)
):
    """Delete a rate. Admin only."""
    await rate_service.delete_rate(rate_id, current_user, db)
    return {"message": "Rate deleted"}

# Rate Optimization Endpoints
@router.post("/optimization/{rate_card_id}", response_model=OptimizationResponse)
async def optimize_rate_card(
    rate_card_id: int,
    request: OptimizationRequest,
    rate_service: RateService = Depends(),
    rate_integration_service: RateIntegrationService = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_admin_user)
) -> OptimizationResponse:
    """Optimize a rate card using AI analysis."""
    try:
        result = await rate_integration_service.optimize_rate_card({
            "id": rate_card_id,
            **request.dict()
        }, db)
        
        # Create optimization history
        history = RateOptimizationHistory(
            rate_card_id=rate_card_id,
            optimization_type=request.optimization_type,
            original_rates=result["original"],
            optimized_rates=result["optimized"],
            confidence_score=result["metrics"]["confidence_score"],
            metrics=result["metrics"]
        )
        db.add(history)
        db.commit()
        
        return OptimizationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize rate card: {str(e)}"
        )

@router.get("/optimization/history/{rate_card_id}", response_model=List[OptimizationResponse])
async def get_optimization_history(
    rate_card_id: int,
    limit: int = Query(10, ge=1, le=100),
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_admin_user)
) -> List[OptimizationResponse]:
    """Get optimization history for a rate card."""
    history = db.query(RateOptimizationHistory)\
        .filter(RateOptimizationHistory.rate_card_id == rate_card_id)\
        .order_by(RateOptimizationHistory.created_at.desc())\
        .limit(limit)\
        .all()
        
    return [OptimizationResponse(
        original=h.original_rates,
        optimized=h.optimized_rates,
        metrics=h.metrics,
        applied=h.applied,
        created_at=h.created_at,
        applied_at=h.applied_at
    ) for h in history]

@router.post("/optimization/rules", response_model=ValidationRule)
async def create_validation_rule(
    rule: ValidationRuleCreate,
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_admin_user)
) -> ValidationRule:
    """Create a new validation rule."""
    db_rule = RateValidationRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return ValidationRule.from_orm(db_rule)

@router.get("/optimization/rules", response_model=List[ValidationRule])
async def get_validation_rules(
    active_only: bool = Query(True),
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_admin_user)
) -> List[ValidationRule]:
    """Get all validation rules."""
    query = db.query(RateValidationRule)
    if active_only:
        query = query.filter(RateValidationRule.is_active == True)
    return [ValidationRule.from_orm(rule) for rule in query.all()]

@router.post("/optimization/market-analysis", response_model=MarketAnalysis)
async def create_market_analysis(
    analysis: MarketAnalysisCreate,
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_admin_user)
) -> MarketAnalysis:
    """Create a new market analysis entry."""
    db_analysis = MarketRateAnalysis(**analysis.dict())
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return MarketAnalysis.from_orm(db_analysis)

@router.get("/optimization/market-analysis", response_model=List[MarketAnalysis])
async def get_market_analysis(
    service_type: str,
    location: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    rate_service: RateService = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_admin_user)
) -> List[MarketAnalysis]:
    """Get market analysis for a service type."""
    query = db.query(MarketRateAnalysis)\
        .filter(MarketRateAnalysis.service_type == service_type)
    
    if location:
        query = query.filter(MarketRateAnalysis.location == location)
    
    analyses = query.order_by(MarketRateAnalysis.created_at.desc())\
        .limit(limit)\
        .all()
    
    return [MarketAnalysis.from_orm(analysis) for analysis in analyses]

@router.post("/optimization/apply/{optimization_id}")
async def apply_optimization(
    optimization_id: int,
    rate_service: RateService = Depends(),
    rate_integration_service: RateIntegrationService = Depends(),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Apply an optimization to a rate card."""
    history = db.query(RateOptimizationHistory)\
        .filter(RateOptimizationHistory.id == optimization_id)\
        .first()
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail="Optimization history not found"
        )
    
    if history.applied:
        raise HTTPException(
            status_code=400,
            detail="Optimization already applied"
        )
    
    try:
        await rate_integration_service.apply_optimization(history, db)
        
        history.applied = True
        history.applied_at = datetime.utcnow()
        history.applied_by = current_user.id
        db.commit()
        
        return {"message": "Optimization applied successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply optimization: {str(e)}"
        )
