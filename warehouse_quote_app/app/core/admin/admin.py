"""
Admin functionality and permissions.
"""

from typing import List, Optional, Type, TypeVar, Annotated, TYPE_CHECKING, Any, Union
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# Import auth dependencies first
from warehouse_quote_app.app.core.auth import AdminUserDep
# Import get_db from dedicated module to avoid circular import
from warehouse_quote_app.app.database.get_db import get_db

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from warehouse_quote_app.app.models.user import User
    UserType = User
else:
    UserType = Any

T = TypeVar('T')

def check_admin_permission(user: "UserType") -> None:
    """Check if user has admin permissions."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

def admin_required(func):
    """Decorator to require admin permissions."""
    async def wrapper(current_user: "UserType" = Depends(AdminUserDep), *args, **kwargs):
        check_admin_permission(current_user)
        return await func(current_user, *args, **kwargs)
    return wrapper

async def get_admin_users(db: Session) -> List["UserType"]:
    """Get all admin users."""
    # Import at runtime to avoid circular imports
    from warehouse_quote_app.app.models.user import User
    return db.query(User).filter(User.is_admin == True).all()

async def grant_admin(db: Session, user_id: int, granting_admin: "UserType") -> Optional["UserType"]:
    """Grant admin privileges to a user."""
    # Import at runtime to avoid circular imports
    from warehouse_quote_app.app.models.user import User
    
    # Check if granting user is an admin
    check_admin_permission(granting_admin)
    
    # Cannot grant admin to self
    if granting_admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot grant admin privileges to yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = True
    db.commit()
    return user

async def revoke_admin(db: Session, user_id: int, revoking_admin: "UserType") -> Optional["UserType"]:
    """Revoke admin privileges from a user."""
    # Import at runtime to avoid circular imports
    from warehouse_quote_app.app.models.user import User
    
    # Check if revoking user is an admin
    check_admin_permission(revoking_admin)
    
    # Cannot revoke admin from self
    if revoking_admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke your own admin privileges"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Count total admins
    admin_count = db.query(User).filter(User.is_admin == True).count()
    if admin_count <= 1 and user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke the last admin's privileges"
        )
    
    user.is_admin = False
    db.commit()
    return user

__all__ = [
    'check_admin_permission',
    'admin_required',
    'get_admin_users',
    'grant_admin',
    'revoke_admin',
]
