"""Common type definitions for the warehouse quote application."""

from enum import Enum, auto
from typing import Dict, Any, Optional, List, Union

class RateCategory(str, Enum):
    """Rate category enumeration."""
    STANDARD = "standard"
    PREMIUM = "premium"
    DISCOUNT = "discount"
    SPECIAL = "special"

class RateType(str, Enum):
    """Rate type enumeration."""
    STORAGE = "storage"
    HANDLING = "handling"
    CONTAINER = "container"
    TRANSPORT = "transport"
    EXPORT = "export"
    ALL = "all"

class ContainerSize(str, Enum):
    """Container size enumeration."""
    TWENTY_FOOT = "20ft"
    FORTY_FOOT = "40ft"
    FORTY_FOOT_HC = "40ft_hc"  # High cube
    FORTY_FIVE_FOOT = "45ft"

class TransportType(str, Enum):
    """Transport type enumeration."""
    LOCAL = "local"
    LONG_HAUL = "long_haul" 
    CONTAINER = "container"

class MeasurementType(str, Enum):
    """Measurement type for rate calculation."""
    AREA = "area"
    VOLUME = "volume"
    WEIGHT = "weight"
    DISTANCE = "distance"
    TIME = "time"
    ITEM = "item"

class StorageType(str, Enum):
    """Storage type enumeration."""
    RACKED = "racked"
    FLOOR = "floor"
    OVERSIZE = "oversize"
    REFRIGERATED = "refrigerated"
    HAZARDOUS = "hazardous"
    BONDED = "bonded"

class ChargeCalculationMethod(str, Enum):
    """Calculation method for charges."""
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    TIERED = "tiered"
    FORMULA = "formula"
