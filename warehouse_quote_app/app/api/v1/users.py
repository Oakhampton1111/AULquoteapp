"""
User management API routes.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from warehouse_quote_app.app.core.database import get_db
from warehouse_quote_app.app.core.auth import get_current_user, get_current_admin_user
from warehouse_quote_app.app.models.user import User
from warehouse_quote_app.app.services.user_service import UserService
from warehouse_quote_app.app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate
)
from warehouse_quote_app.app.schemas.user.customer import (
    Customer as CustomerSchema,
    CustomerCreate,
    CustomerUpdate
)

router = APIRouter(prefix="/users", tags=["users"])

# User Management Routes
@router.post("", response_model=UserSchema)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new user. Admin only."""
    return await user_service.create_user(user_data)

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user info."""
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_data: UserUpdate,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Update current user."""
    return await user_service.update_user(current_user.id, user_data)

@router.get("", response_model=List[UserSchema])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_admin_user)
):
    """List all users. Admin only."""
    return await user_service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user by ID. Admin only."""
    return await user_service.get_user(user_id)

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user. Admin only."""
    return await user_service.update_user(user_id, user_data)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user. Admin only."""
    await user_service.delete_user(user_id)
    return {"message": "User deleted"}

# Customer Management Routes
@router.post("/customers", response_model=CustomerSchema)
async def create_customer(
    customer_data: CustomerCreate,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new customer. Admin only."""
    return await user_service.create_customer(customer_data)

@router.get("/customers", response_model=List[CustomerSchema])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """List all customers."""
    return await user_service.get_customers(skip=skip, limit=limit)

@router.get("/customers/{customer_id}", response_model=CustomerSchema)
async def get_customer(
    customer_id: int,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get customer by ID."""
    return await user_service.get_customer(customer_id)

@router.put("/customers/{customer_id}", response_model=CustomerSchema)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_admin_user)
):
    """Update customer. Admin only."""
    return await user_service.update_customer(customer_id, customer_data)

@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete customer. Admin only."""
    await user_service.delete_customer(customer_id)
    return {"message": "Customer deleted"}

# User Preferences Routes
@router.get("/me/preferences", response_model=Dict[str, Any])
async def get_user_preferences(
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get current user preferences."""
    return await user_service.get_user_preferences(current_user.id)

@router.put("/me/preferences", response_model=UserSchema)
async def update_user_preferences(
    preferences: Dict[str, Any],
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Update current user preferences."""
    return await user_service.update_user_preferences(current_user.id, preferences)
