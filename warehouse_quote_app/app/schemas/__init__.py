"""
Schemas package initialization.

This module exports all schema classes and handles circular imports.
"""

from .base import (
    BaseSchema,
    BaseResponseSchema as BaseResponse,
    BaseCreateSchema as BaseRequest,
    BaseUpdateSchema,
    BaseFilterSchema,
    Page,
    PageMetadata,
    ErrorDetail,
    ErrorResponse,
    SuccessResponse,
    WebSocketMessage
)

# User schemas
from .user import User, UserCreate, UserUpdate, UserResponse
from .user.customer import (
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse
)
from .user.auth import (
    Token,
    TokenData,
    UserLogin,
    UserRegister,
    PasswordResetRequest,
    PasswordResetConfirm
)

# Quote schemas
from .quote import (
    Quote,
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteItem,
    QuoteStatus,
    QuoteRequest,
    StorageRequirements,
    StorageType,
    ServiceRequest,
    QuoteDetailResponse,
    QuoteStatusUpdate
)

# Customer schemas
from .customer import (
    CustomerProfileResponse,
    CustomerPreferenceUpdate,
    CustomerDashboardResponse
)

# Client schemas
from .client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientUser
)

# Rate schemas
from .rate import (
    Rate,
    RateCreate,
    RateUpdate,
    RateResponse,
    RateCategory,
    RateFilter
)

__all__ = [
    # Base schemas
    'BaseSchema',
    'BaseResponse',
    'BaseRequest',
    'BaseUpdateSchema',
    'BaseFilterSchema',
    'Page',
    'PageMetadata',
    'ErrorDetail',
    'ErrorResponse',
    'SuccessResponse',
    'WebSocketMessage',
    
    # User schemas
    'User',
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    'CustomerBase',
    'CustomerCreate',
    'CustomerUpdate',
    'CustomerResponse',
    'Token',
    'TokenData',
    'UserLogin',
    'UserRegister',
    'PasswordResetRequest',
    'PasswordResetConfirm',
    
    # Quote schemas
    'Quote',
    'QuoteCreate',
    'QuoteUpdate',
    'QuoteResponse',
    'QuoteItem',
    'QuoteStatus',
    'QuoteRequest',
    'StorageRequirements',
    'StorageType',
    'ServiceRequest',
    'QuoteDetailResponse',
    'QuoteStatusUpdate',
    
    # Customer schemas
    'CustomerProfileResponse',
    'CustomerPreferenceUpdate',
    'CustomerDashboardResponse',
    
    # Client schemas
    'ClientCreate',
    'ClientUpdate',
    'ClientResponse',
    'ClientUser',
    
    # Rate schemas
    'Rate',
    'RateCreate',
    'RateUpdate',
    'RateResponse',
    'RateCategory',
    'RateFilter'
]
