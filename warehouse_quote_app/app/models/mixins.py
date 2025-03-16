"""Model mixins for common functionality."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

class TrackingMixin:
    """Mixin for models that need metrics tracking."""
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    total_quotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accepted_quotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_quotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0.0'), nullable=False)
    last_quote_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    async def update_metrics(self) -> None:
        """Update metrics based on quotes."""
        if not hasattr(self, 'quotes'):
            raise AttributeError("TrackingMixin requires a 'quotes' relationship")
        
        self.total_quotes = len(self.quotes)
        self.accepted_quotes = sum(1 for q in self.quotes if q.status == "accepted")
        self.rejected_quotes = sum(1 for q in self.quotes if q.status == "rejected")
        self.total_spent = sum(q.total_amount for q in self.quotes if q.status == "accepted")
        if self.quotes:
            self.last_quote_date = max(q.created_at for q in self.quotes)

class PreferencesMixin:
    """Mixin for models with user preferences."""
    
    preferred_contact_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    notification_preferences: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    special_requirements: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

class ContactInfoMixin:
    """Mixin for models with contact information."""
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

class TimestampMixin:
    """Mixin for timestamp fields."""
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

class StatusTrackingMixin:
    """Mixin for tracking status changes with timestamps and users."""
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    
    # Status timestamps
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # User tracking
    created_by: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    accepted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    rejected_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    completed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    
    async def submit(self, submitted_by: int) -> None:
        """Submit the item."""
        self.status = "submitted"
        self.submitted_at = datetime.utcnow()
        self.submitted_by = submitted_by

    async def accept(self, accepted_by: int) -> None:
        """Accept the item."""
        self.status = "accepted"
        self.accepted_at = datetime.utcnow()
        self.accepted_by = accepted_by

    async def reject(self, rejected_by: int) -> None:
        """Reject the item."""
        self.status = "rejected"
        self.rejected_at = datetime.utcnow()
        self.rejected_by = rejected_by

    async def complete(self, completed_by: int) -> None:
        """Complete the item."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.completed_by = completed_by

class SerializationMixin:
    """Mixin for model serialization."""

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()

    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, data: Dict[str, Any]) -> None:
        """Update model attributes from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class ValidityMixin:
    """Mixin for models with validity periods."""
    
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def is_valid(self, at_time: Optional[datetime] = None) -> bool:
        """Check if the item is valid at the given time."""
        at_time = at_time or datetime.utcnow()
        return (
            self.is_active and
            self.valid_from <= at_time <= self.valid_until
        )

class OptimizationMixin:
    """Mixin for models with AI optimization capabilities."""
    
    optimization_history: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        default=list,
        comment="History of AI-powered optimizations"
    )
    market_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        comment="Latest market analysis data"
    )
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True,
        comment="AI confidence score"
    )
    last_optimized_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
        comment="Timestamp of last optimization"
    )

    def record_optimization(self, analysis: Dict[str, Any], confidence: Decimal) -> None:
        """Record an optimization event."""
        if self.optimization_history is None:
            self.optimization_history = []
            
        self.optimization_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": analysis,
            "confidence": float(confidence)
        })
        self.market_analysis = analysis
        self.confidence_score = confidence
        self.last_optimized_at = datetime.utcnow()

class MetricsMixin:
    """Mixin for tracking business metrics."""
    
    total_quotes: Mapped[int] = mapped_column(Integer, default=0)
    accepted_quotes: Mapped[int] = mapped_column(Integer, default=0)
    rejected_quotes: Mapped[int] = mapped_column(Integer, default=0)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0'))
    last_quote_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    async def update_metrics(self, quotes: List[Any]) -> None:
        """Update metrics based on quotes."""
        self.total_quotes = len(quotes)
        self.accepted_quotes = sum(1 for q in quotes if q.status == "accepted")
        self.rejected_quotes = sum(1 for q in quotes if q.status == "rejected")
        self.total_spent = sum(q.total_amount for q in quotes if q.status == "completed")
        
        if quotes:
            self.last_quote_date = max(q.created_at for q in quotes)
