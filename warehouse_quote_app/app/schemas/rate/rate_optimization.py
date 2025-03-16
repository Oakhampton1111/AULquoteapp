"""
Schemas for rate optimization. Removed market analysis functionality.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

class OptimizationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    optimization_type: str = Field(
        ...,
        description="Type of optimization to perform",
        examples=["seasonal", "volume_based"]
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for optimization"
    )

class OptimizationResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    original: Dict[str, Any]
    optimized: Dict[str, Any]
    metrics: Dict[str, Any]
    applied: bool = False
    created_at: datetime
    applied_at: Optional[datetime] = None

class ValidationRuleBase(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    name: str
    description: str
    rule_type: str = Field(
        ...,
        description="Type of validation rule",
        examples=["rate_range", "seasonal_adjustment"]
    )
    parameters: Dict[str, Any]
    is_active: bool = True
    severity: str = Field(
        "warning",
        description="Severity level of rule violation",
        examples=["info", "warning", "error"]
    )

class ValidationRuleCreate(ValidationRuleBase):
    pass

class ValidationRule(ValidationRuleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class OptimizationMetrics(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    confidence_score: Decimal = Field(ge=0, le=1)
    potential_revenue_impact: Decimal
    seasonal_factors: Dict[str, Any]
    volume_analysis: Dict[str, Any]
