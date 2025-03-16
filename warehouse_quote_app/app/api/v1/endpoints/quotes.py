"""Quote management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from warehouse_quote_app.app.core.auth import get_current_user
from warehouse_quote_app.app.api import deps
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.schemas.quote import (
    QuoteCreate,
    QuoteResponse,
    QuoteStatusUpdate,
    QuoteListResponse,
    QuoteFilter,
    QuoteNegotiationRequest,
    QuoteNegotiationResponse
)
from warehouse_quote_app.app.services.quote_lifecycle import QuoteLifecycleService
from warehouse_quote_app.app.core.logging import get_logger
from warehouse_quote_app.app.api.v1.middleware import rate_limit, cache_response, RATE_LIMIT_STANDARD

router = APIRouter()
logger = get_logger("quotes")

@router.post(
    "/quotes",
    response_model=QuoteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(RATE_LIMIT_STANDARD))],
    responses={
        201: {"description": "Quote created successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
async def create_quote(
    quote_data: QuoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Create a new quote."""
    try:
        quote_service = QuoteLifecycleService(db)
        return await quote_service.create_quote(quote_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating quote: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating quote")

@router.get(
    "/quotes/{quote_id}",
    response_model=QuoteResponse,
    dependencies=[Depends(rate_limit(RATE_LIMIT_STANDARD))],
    responses={
        200: {"description": "Quote retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Quote not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_quote(
    quote_id: int = Path(..., title="Quote ID", ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Get a quote by ID."""
    try:
        quote_service = QuoteLifecycleService(db)
        return await quote_service.get_quote(quote_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving quote: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving quote")

@router.get(
    "/quotes",
    response_model=QuoteListResponse,
    dependencies=[Depends(rate_limit(RATE_LIMIT_STANDARD))],
    responses={
        200: {"description": "Quotes retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
async def list_quotes(
    skip: int = Query(0, title="Skip", description="Number of quotes to skip", ge=0),
    limit: int = Query(100, title="Limit", description="Maximum number of quotes to return", ge=1, le=100),
    status: Optional[str] = Query(None, title="Status", description="Filter by quote status"),
    start_date: Optional[datetime] = Query(None, title="Start Date", description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, title="End Date", description="Filter by end date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """List all quotes with filtering."""
    try:
        quote_service = QuoteLifecycleService(db)
        
        # Create filter object if any filter parameters are provided
        filter_params = None
        if status or start_date or end_date:
            filter_params = QuoteFilter(
                status=status,
                start_date=start_date,
                end_date=end_date
            )
            
        return await quote_service.list_quotes(skip, limit, filter_params)
    except Exception as e:
        logger.error(f"Error listing quotes: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error listing quotes")

@router.patch(
    "/quotes/{quote_id}/status",
    response_model=QuoteResponse,
    dependencies=[Depends(rate_limit(RATE_LIMIT_STANDARD))],
    responses={
        200: {"description": "Quote status updated successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Quote not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_quote_status(
    status_update: QuoteStatusUpdate,
    quote_id: int = Path(..., title="Quote ID", ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Update quote status."""
    try:
        quote_service = QuoteLifecycleService(db)
        return await quote_service.update_quote_status(quote_id, status_update)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating quote status: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating quote status")

@router.post(
    "/quotes/{quote_id}/negotiate",
    response_model=QuoteNegotiationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(RATE_LIMIT_STANDARD))],
    responses={
        201: {"description": "Negotiation request submitted successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Quote not found"},
        500: {"description": "Internal server error"}
    }
)
async def negotiate_quote(
    negotiation_request: QuoteNegotiationRequest,
    quote_id: int = Path(..., title="Quote ID", ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Submit a negotiation request for a quote."""
    try:
        quote_service = QuoteLifecycleService(db)
        return await quote_service.negotiate_quote(
            quote_id, 
            current_user.id,
            negotiation_request
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error negotiating quote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error submitting quote negotiation request"
        )

@router.delete(
    "/quotes/{quote_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(rate_limit(RATE_LIMIT_STANDARD))],
    responses={
        204: {"description": "Quote deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Quote not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_quote(
    quote_id: int = Path(..., title="Quote ID", ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Delete a quote."""
    try:
        quote_service = QuoteLifecycleService(db)
        result = await quote_service.delete_quote(quote_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quote with ID {quote_id} not found")
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting quote: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting quote")
