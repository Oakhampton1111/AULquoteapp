"""Models package."""

# Import base and mixins first to avoid circular imports
from .base import BaseModel
from .mixins import (
    TimestampMixin,
    StatusTrackingMixin,
    SerializationMixin,
    TrackingMixin,
    PreferencesMixin,
    ContactInfoMixin,
    MetricsMixin
)

# Import enums and utility classes
from .crm import InteractionType, DealStage, CRMMixin

# Import main models
from .user import User
from .customer import Customer
from .quote import Quote, QuoteStatus
from .rate import Rate

__all__ = [
    # Base models
    "BaseModel",
    
    # Mixins
    "TimestampMixin",
    "StatusTrackingMixin",
    "SerializationMixin",
    "TrackingMixin",
    "PreferencesMixin",
    "ContactInfoMixin",
    "MetricsMixin",
    "CRMMixin",
    
    # Enums
    "InteractionType",
    "DealStage",
    "QuoteStatus",
    
    # Models
    "User",
    "Customer",
    "Quote",
    "Rate"
]
