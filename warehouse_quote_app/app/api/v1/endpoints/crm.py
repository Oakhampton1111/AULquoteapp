"""CRM endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.database import get_db
from warehouse_quote_app.app.core.auth import get_current_user
from warehouse_quote_app.app.models.crm import InteractionType, DealStage
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.services.crm import CRMService
from warehouse_quote_app.app.schemas.crm import (
    InteractionCreate,
    InteractionRead,
    DealCreate,
    DealRead,
    DealUpdate,
    PipelineStats,
    CustomerCRMStats,
    CustomerWithCRMStats
)

router = APIRouter()

@router.post("/customers/{customer_id}/interactions", response_model=InteractionRead)
async def create_interaction(
    customer_id: int,
    interaction: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer interaction."""
    crm_service = CRMService(db)
    try:
        return await crm_service.create_interaction(
            customer_id=customer_id,
            interaction=interaction,
            agent_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/customers/{customer_id}/interactions", response_model=List[InteractionRead])
async def get_customer_interactions(
    customer_id: int,
    days: Optional[int] = Query(30, ge=1, le=365),
    interaction_type: Optional[InteractionType] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get customer interactions."""
    crm_service = CRMService(db)
    return await crm_service.get_recent_interactions(
        customer_id=customer_id,
        days=days,
        interaction_type=interaction_type
    )

@router.post("/customers/{customer_id}/deals", response_model=DealRead)
async def create_deal(
    customer_id: int,
    deal: DealCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new deal."""
    crm_service = CRMService(db)
    try:
        return await crm_service.create_deal(
            customer_id=customer_id,
            deal=deal,
            agent_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/deals/{deal_id}", response_model=DealRead)
async def update_deal(
    deal_id: int,
    deal_update: DealUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a deal."""
    crm_service = CRMService(db)
    try:
        return await crm_service.update_deal_stage(
            deal_id=deal_id,
            stage=deal_update.stage,
            agent_id=current_user.id,
            metadata=deal_update.metadata
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/pipeline/stats", response_model=PipelineStats)
async def get_pipeline_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get pipeline statistics."""
    crm_service = CRMService(db)
    return await crm_service.get_pipeline_stats()

@router.get("/customers/{customer_id}/crm-stats", response_model=CustomerCRMStats)
async def get_customer_crm_stats(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get CRM statistics for a customer."""
    crm_service = CRMService(db)
    try:
        return await crm_service.get_customer_crm_stats(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/customers", response_model=List[CustomerWithCRMStats])
def get_customers_with_crm_stats(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all customers with their CRM statistics.
    """
    crm_service = CRMService(db)
    return crm_service.get_customers_with_crm_stats(db, skip=skip, limit=limit)
