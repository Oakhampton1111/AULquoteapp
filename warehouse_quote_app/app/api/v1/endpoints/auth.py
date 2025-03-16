"""Authentication endpoints."""
import logging
from datetime import timedelta, datetime
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from warehouse_quote_app.app.crud import user as user_crud
from warehouse_quote_app.app import models, schemas
from warehouse_quote_app.app.api import deps
from warehouse_quote_app.app.core import security
from warehouse_quote_app.app.core.config import settings
from warehouse_quote_app.app.core.security import get_password_hash
from warehouse_quote_app.app.services.audit_logger import get_audit_logger, AuditLogger
from warehouse_quote_app.app.schemas.user.auth import (
    Token,
    PasswordResetRequest,
    PasswordResetConfirm
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=schemas.Token)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    audit_logger: AuditLogger = Depends(get_audit_logger)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    # Update last login timestamp
    user.last_login = datetime.now()
    db.commit()
    
    # Log successful login
    audit_logger.log_action(
        user_id=user.id,
        action="login",
        resource_type="user",
        resource_id=user.id,
        details={"method": "password"}
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "is_admin": user.is_admin
    }

@router.post("/admin/login", response_model=schemas.Token)
def admin_login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    audit_logger: AuditLogger = Depends(get_audit_logger)
) -> Any:
    """
    Admin-specific login endpoint with additional security checks.
    """
    user = user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive admin account",
        )
    
    access_token_expires = timedelta(minutes=settings.ADMIN_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, 
        expires_delta=access_token_expires,
        admin=True
    )
    
    # Log the admin login attempt
    audit_logger.log_action(
        user_id=user.id,
        action="admin_login",
        resource_type="user",
        resource_id=user.id,
        details={"method": "password"}
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_admin": True,
            "name": user.name
        }
    }

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    audit_logger: AuditLogger = Depends(get_audit_logger)
) -> Any:
    """
    Create new user.
    """
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    
    user = user_crud.create(db, obj_in=user_in)
    
    # Log the registration
    audit_logger.log_action(
        user_id=user.id,
        action="user_register",
        resource_type="user",
        resource_id=user.id,
        details={"email": user.email}
    )
    
    return user

@router.post("/reset-password/request")
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(deps.get_db),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Request password reset."""
    user = user_crud.get_by_email(db, email=request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    reset_token = security.create_password_reset_token(user.id)
    # TODO: Send password reset email
    
    audit_logger.log_action(
        user_id=user.id,
        action="password_reset_request",
        resource_type="user",
        resource_id=user.id,
        details={"email": user.email}
    )
    
    return {"message": "Password reset email sent"}

@router.post("/reset-password/confirm")
def confirm_password_reset(
    confirm: PasswordResetConfirm,
    db: Session = Depends(deps.get_db),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Confirm password reset."""
    user_id = security.verify_password_reset_token(confirm.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    hashed_password = get_password_hash(confirm.new_password)
    user.hashed_password = hashed_password
    db.commit()
    
    audit_logger.log_action(
        user_id=user.id,
        action="password_reset_complete",
        resource_type="user",
        resource_id=user.id,
        details={"user_id": user.id}
    )
    
    return {"message": "Password reset successful"}

@router.get("/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    """Get current user."""
    return current_user
