"""
Rate administration service for managing rate cards and pricing.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# Fix the import path to use the full module path
from warehouse_quote_app.app.database.db import get_db
from app.schemas.admin import (
    RateCardResponse,
    RateCardCreate,
    RateCardUpdate
)