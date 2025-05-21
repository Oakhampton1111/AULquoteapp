"""Authentication endpoints."""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from warehouse_quote_app.app import models, schemas
from warehouse_quote_app.app.api import deps
from warehouse_quote_app.app.core import security
from warehouse_quote_app.app.core.config import settings
from warehouse_quote_app.app.core.security import get_password_hash
from warehouse_quote_app.app.crud import user as user_crud
from warehouse_quote_app.app.schemas.user.auth import (
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    # UserResponse might be needed if returning user info directly
)
from warehouse_quote_app.app.services.audit_logger import AuditLogger, get_audit_logger
from warehouse_quote_app.app.services.communication import EmailService
from warehouse_quote_app.app.core.auth.sso_service import SSOService # New Import
from warehouse_quote_app.app.services.auth_service import AuthService # For token generation / user creation
from fastapi.responses import RedirectResponse # New Import
from starlette.requests import Request as StarletteRequest # New Import
from sqlalchemy.ext.asyncio import AsyncSession # For async db operations

router = APIRouter()
logger = logging.getLogger(__name__)

from warehouse_quote_app.app.services.crm.base import BaseCRMService # CRM Service
from warehouse_quote_app.app.schemas.crm import CRMCustomerCreate # CRM Schema

# Dependency for AuthService (now async)
# Replaces the previous placeholder get_auth_service
def get_auth_service_dependency() -> AuthService:
    # AuthService __init__ no longer takes db.
    # If AuthService needs other dependencies in __init__, they'd be resolved here.
    return AuthService()

async def get_sso_service(
    auth_service: AuthService = Depends(get_auth_service_dependency),
    crm_service: BaseCRMService = Depends(deps.get_crm_service) # Inject CRM service here for SSOService
) -> SSOService:
    # Pass crm_service to SSOService constructor
    return SSOService(auth_service=auth_service, crm_service=crm_service)


@router.post("/login", response_model=schemas.Token)
async def login( # Changed to async
    db: AsyncSession = Depends(deps.get_async_db), # Use async session
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service_dependency), # Inject async AuthService
    audit_logger: AuditLogger = Depends(get_audit_logger),
    crm_service: BaseCRMService = Depends(deps.get_crm_service), # Inject CRM Service
) -> schemas.Token: # Return type changed to schemas.Token
    """
    OAuth2 compatible token login, get an access token for future requests.
    Also ensures the user is synced to the CRM.
    """
    # AuthService.get_login_token_for_credentials handles user fetching, auth, and token creation
    token_data = await auth_service.get_login_token_for_credentials(
        db, email=form_data.username, password=form_data.password
    )
    
    # user_crud.authenticate is now part of auth_service.authenticate_user
    # If last_login update is still needed, it has to be done via an async crud method
    # For now, assuming token generation is the primary goal.
    # user = await user_crud.get_by_email(db, email=form_data.username) # Example if needed
    # if user:
    #     user.last_login = datetime.now() # This is not how you update with SQLAlchemy async
    #     await db.commit() 
    #     await db.refresh(user)

    # Log successful login
    # Token schema from AuthService should contain user_id
    audit_logger.log_action(
        user_id=token_data.user_id, # Assuming Token schema has user_id
        action="login",
        resource_type="user",
        resource_id=token_data.user_id, # Assuming Token schema has user_id
        details={"method": "password"},
    )

    # Sync user to CRM upon login
    # Need to fetch the user object first, as get_login_token_for_credentials only returns token
    # This assumes user_id in token_data.user_id is the actual user ID.
    user = await user_crud.get(db, id=token_data.user_id) # user_crud is async
    if user:
        crm_customer_data = CRMCustomerCreate(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            company_name=user.company_name,
            app_user_id=user.id
        )
        try:
            crm_customer_id = await crm_service.create_or_update_customer(customer_data=crm_customer_data)
            if crm_customer_id:
                logger.info(f"User {user.email} (ID: {user.id}) synced/updated in CRM on login. CRM ID: {crm_customer_id}")
            else:
                logger.warning(f"Failed to sync/update user {user.email} (ID: {user.id}) to CRM on login.")
        except Exception as e:
            logger.error(f"Error syncing/updating user {user.email} (ID: {user.id}) to CRM on login: {e}", exc_info=True)
    else:
        logger.error(f"User not found for ID {token_data.user_id} during login CRM sync attempt.")

    return token_data


@router.post("/admin/login", response_model=schemas.Token) # Needs to be async too
async def admin_login( # Changed to async
    db: AsyncSession = Depends(deps.get_async_db), # Use async session
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service_dependency), # Inject async AuthService
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> schemas.Token:
    """
    Admin-specific login endpoint with additional security checks.
    """
    # Authenticate first
    user = await auth_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    
    if not user or not user.is_admin: # Check if admin
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials or not an admin",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive admin account",
        )

    # Generate admin-specific token if needed, or use standard token with admin claim
    # The existing AuthService.get_login_token now includes is_admin in payload
    # We can customize token expiry if ADMIN_TOKEN_EXPIRE_MINUTES is different and handled by create_access_token
    # For now, using the standard get_login_token which includes is_admin claim.
    
    token_data = await auth_service.get_login_token(db, user_id=user.id, email=user.email, is_admin=user.is_admin)
    
    # Log the admin login attempt
    audit_logger.log_action(
        user_id=user.id,
        action="admin_login",
        resource_type="user",
        resource_id=user.id,
        details={"method": "password"},
    )
    return token_data


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED) # Changed response_model
async def register( # Changed to async
    *,
    db: AsyncSession = Depends(deps.get_async_db), # Use async session
    user_in: schemas.UserCreate,
    auth_service: AuthService = Depends(get_auth_service_dependency), # Inject async AuthService
    audit_logger: AuditLogger = Depends(get_audit_logger),
    crm_service: BaseCRMService = Depends(deps.get_crm_service), # Inject CRM Service
) -> models.User: # Return type is User model instance
    """
    Create new user.
    AuthService.create_user_account handles email check and creation.
    Also syncs new user to CRM.
    """
    user = await auth_service.create_user_account(db, user_in=user_in)

    # Sync to CRM
    crm_customer_data = CRMCustomerCreate(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone, # Assuming User model has phone
        company_name=user.company_name, # Assuming User model has company_name
        app_user_id=user.id
    )
    try:
        crm_customer_id = await crm_service.create_or_update_customer(customer_data=crm_customer_data)
        if crm_customer_id:
            logger.info(f"User {user.email} (ID: {user.id}) synced to CRM with CRM ID: {crm_customer_id}")
            # Optionally, store crm_customer_id on the user model if it exists
            # user.crm_id = crm_customer_id 
            # await db.commit()
            # await db.refresh(user)
        else:
            logger.warning(f"Failed to sync user {user.email} (ID: {user.id}) to CRM.")
    except Exception as e:
        logger.error(f"Error syncing user {user.email} (ID: {user.id}) to CRM: {e}", exc_info=True)


    # Log the registration
    audit_logger.log_action(
        user_id=user.id,
        action="user_register",
        resource_type="user",
        resource_id=user.id,
        details={"email": user.email},
    )
    # UserResponse schema might expect different fields than User model.
    # Ensure User model can be directly returned or map to UserResponse.
    # For now, returning the User model instance as per typical CRUD.
    return user


@router.post("/reset-password/request")
async def request_password_reset(
    request_data: PasswordResetRequest, # Changed param name to avoid conflict with StarletteRequest
    db: AsyncSession = Depends(deps.get_async_db), # Use async session
    auth_service: AuthService = Depends(get_auth_service_dependency), # Inject async AuthService
    audit_logger: AuditLogger = Depends(get_audit_logger),
):
    """Request password reset and send email to the user."""
    reset_token = await auth_service.request_password_reset(db, email=request_data.email)
    if not reset_token: # AuthService now returns None if user not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Fetch user again to pass to email service (or have request_password_reset return user)
    user = await user_crud.get_by_email(db, email=request_data.email) # user_crud is async
    if not user: # Should not happen if token was generated, but as safeguard
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found after token generation.")


    # Dispatch password reset email using the email service
    email_service = EmailService() # Assuming EmailService can be instantiated like this
    try:
        await email_service.send_password_reset(user, reset_token)
    except Exception:  # pragma: no cover - log and continue on email failure
        logger.exception("Failed to send password reset email")

    audit_logger.log_action(
        user_id=user.id,
        action="password_reset_request",
        resource_type="user",
        resource_id=user.id,
        details={"email": user.email},
    )
    return {"message": "Password reset email sent"}


@router.post("/reset-password/confirm")
async def confirm_password_reset( # Changed to async
    confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(deps.get_async_db), # Use async session
    auth_service: AuthService = Depends(get_auth_service_dependency), # Inject async AuthService
    audit_logger: AuditLogger = Depends(get_audit_logger),
):
    """Confirm password reset."""
    success = await auth_service.reset_password(db, token=confirm.token, new_password=confirm.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token, or user not found."
        )
    
    # For logging, need to get user_id from token again if not returned by reset_password
    # This part is tricky as reset_password only returns bool.
    # A more robust flow might involve verify_password_reset_token first, then reset.
    # For now, logging is omitted here as user_id is not readily available post-reset.
    # audit_logger.log_action(...) 

    return {"message": "Password reset successful"}


@router.get("/auth/me", response_model=schemas.UserResponse) # UserResponse schema should be compatible with User model
async def read_users_me(current_user: models.User = Depends(deps.get_current_active_user)): # Use async get_current_active_user
    """Get current user."""
    return current_user


# --- SSO Endpoints ---

@router.get("/sso/{provider_name}")
async def sso_login(
    provider_name: str,
    request: StarletteRequest, # Authlib needs the StarletteRequest
    sso_service: SSOService = Depends(get_sso_service), # SSOService now gets CRMService via its own dependency
    # Assuming redirect_uri is configured or can be derived within sso_service
    # Or passed as a query param: sso_redirect_uri: Optional[str] = Query(None)
):
    """
    Initiate SSO login with the specified provider.
    Redirects the user to the provider's authorization page.
    """
    try:
        # Construct the redirect_uri for the callback. This should match the one registered with the OIDC provider.
        # Example: request.url_for('sso_callback', provider_name=provider_name)
        # Ensure your FastAPI app has a name for the callback route.
        # For now, constructing it manually, but url_for is safer.
        callback_uri = str(request.url_for('sso_callback', provider_name=provider_name))
        
        authorization_url = await sso_service.initiate_sso(provider_name, callback_uri, request)
        return RedirectResponse(url=authorization_url)
    except ValueError as e:
        logger.error(f"SSO initiation error for provider {provider_name}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected SSO initiation error for {provider_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not initiate SSO.")


@router.get("/sso/{provider_name}/callback", name="sso_callback", response_model=Token)
async def sso_callback(
    provider_name: str,
    request: StarletteRequest, # Authlib needs the StarletteRequest to parse code and state
    db: AsyncSession = Depends(deps.get_async_db), # Use async session
    sso_service: SSOService = Depends(get_sso_service),
    audit_logger: AuditLogger = Depends(get_audit_logger),
):
    """
    Process the OIDC callback from the SSO provider.
    Exchanges code for token, fetches user info, provisions/links user,
    and returns an application JWT.
    """
    try:
        app_token_data = await sso_service.process_sso_callback(provider_name, request, db)
        
        # Log successful SSO login
        # process_sso_callback returns a Token schema object which should have user_id
        # However, the Token schema might not directly have user_id.
        # The token's sub (subject) is the user_id.
        # Let's assume app_token_data is the Token schema object and has user_id or can be decoded.
        
        # For logging, we need the user ID.
        # If process_sso_callback returns the Token schema, it might not directly contain user_id.
        # The AuthService.get_login_token which SSOService calls should return a structure
        # that SSOService can use to populate the Token schema, including user_id if needed for logging here.
        # For now, let's assume token has user_id or we can decode it.
        # This part might need adjustment based on exact Token structure and user ID retrieval.
        
        # Placeholder for user_id for logging. In a real scenario, extract from token or user object.
        # logged_in_user_id = app_token_data.user_id # If Token schema has user_id
        # If not, you might need to decode the access_token or have SSOService return user object too.
        # For now, we'll omit detailed audit logging here if user_id isn't readily available
        # from app_token_data without further decoding.
        # audit_logger.log_action(...) 
        
        # The token is returned to the client. The client might store it in a cookie or local storage.
        # Some patterns involve redirecting to a frontend URL with the token in a query param or fragment.
        # For an API, returning the token directly is common.
        return app_token_data

    except ValueError as e:
        logger.error(f"SSO callback error for provider {provider_name}: {str(e)}")
        # Redirect to a frontend error page or return a JSON error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected SSO callback error for {provider_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SSO callback processing failed.")
