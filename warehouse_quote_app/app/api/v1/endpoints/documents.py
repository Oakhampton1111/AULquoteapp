"""Document endpoints for retrieving terms, rate cards, and other documentation."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.responses import JSONResponse, FileResponse
import os
from pathlib import Path as FilePath

from warehouse_quote_app.app.core.auth import get_current_user
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.database import get_db
from sqlalchemy.orm import Session
from warehouse_quote_app.app.core.logging import get_logger
from warehouse_quote_app.app.core.config import settings

router = APIRouter()
logger = get_logger("documents")

# Define the documents directory
DOCUMENTS_DIR = FilePath(settings.STATIC_DIR) / "documents"

@router.get(
    "/terms",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Terms and conditions document"},
        404: {"description": "Document not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_terms_and_conditions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the terms and conditions document.
    
    Returns the terms and conditions as a PDF file or JSON content.
    """
    logger.info(f"Retrieving terms and conditions for user {current_user.id}")
    
    try:
        # Check for PDF version
        pdf_path = DOCUMENTS_DIR / "terms_and_conditions.pdf"
        if pdf_path.exists():
            return FileResponse(
                path=str(pdf_path),
                filename="terms_and_conditions.pdf",
                media_type="application/pdf"
            )
        
        # Check for JSON version
        json_path = DOCUMENTS_DIR / "terms_and_conditions.json"
        if json_path.exists():
            import json
            with open(json_path, "r") as f:
                content = json.load(f)
            return JSONResponse(content=content)
        
        # Fallback to mock data if files don't exist
        return JSONResponse(content={
            "title": "Terms and Conditions",
            "version": "1.0.0",
            "last_updated": "2025-01-01",
            "sections": [
                {
                    "title": "General Terms",
                    "content": "These are the general terms for warehouse services..."
                },
                {
                    "title": "Service Guarantees",
                    "content": "We guarantee the following service levels..."
                },
                {
                    "title": "Payment Terms",
                    "content": "Payment is due within 30 days of invoice..."
                }
            ]
        })
    except Exception as e:
        logger.error(f"Error retrieving terms and conditions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving terms and conditions"
        )


@router.get(
    "/rate-card",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Rate card document"},
        404: {"description": "Document not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_rate_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the rate card document.
    
    Returns the rate card as a PDF file or JSON content.
    """
    logger.info(f"Retrieving rate card for user {current_user.id}")
    
    try:
        # Check for PDF version
        pdf_path = DOCUMENTS_DIR / "rate_card.pdf"
        if pdf_path.exists():
            return FileResponse(
                path=str(pdf_path),
                filename="rate_card.pdf",
                media_type="application/pdf"
            )
        
        # Check for JSON version
        json_path = DOCUMENTS_DIR / "rate_card.json"
        if json_path.exists():
            import json
            with open(json_path, "r") as f:
                content = json.load(f)
            return JSONResponse(content=content)
        
        # Fallback to mock data if files don't exist
        return JSONResponse(content={
            "title": "Warehouse Services Rate Card",
            "version": "2025-Q1",
            "effective_date": "2025-01-01",
            "expiration_date": "2025-03-31",
            "rates": [
                {
                    "service": "Standard Storage",
                    "unit": "per cubic meter per month",
                    "base_rate": 25.00,
                    "minimum_charge": 100.00
                },
                {
                    "service": "Climate-Controlled Storage",
                    "unit": "per cubic meter per month",
                    "base_rate": 45.00,
                    "minimum_charge": 150.00
                },
                {
                    "service": "Packing Services",
                    "unit": "per hour",
                    "base_rate": 35.00,
                    "minimum_charge": 70.00
                },
                {
                    "service": "Transport - Local",
                    "unit": "per kilometer",
                    "base_rate": 2.50,
                    "minimum_charge": 50.00
                },
                {
                    "service": "Transport - Interstate",
                    "unit": "per kilometer",
                    "base_rate": 2.00,
                    "minimum_charge": 500.00
                }
            ]
        })
    except Exception as e:
        logger.error(f"Error retrieving rate card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving rate card"
        )
