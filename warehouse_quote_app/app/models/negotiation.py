"""Quote negotiation model."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from warehouse_quote_app.app.database.base_class import Base


class NegotiationStatus(str, PyEnum):
    """Negotiation status enum."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTER_OFFERED = "counter_offered"


class QuoteNegotiation(Base):
    """Quote negotiation model."""
    __tablename__ = "quote_negotiations"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    proposed_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    reason = Column(Text, nullable=False)
    additional_notes = Column(Text, nullable=True)
    status = Column(String, default=NegotiationStatus.PENDING, nullable=False)
    admin_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    quote = relationship("Quote", back_populates="negotiations")
    user = relationship("User", back_populates="negotiations")
    
    def __repr__(self):
        """String representation of the negotiation."""
        return f"<QuoteNegotiation(id={self.id}, quote_id={self.quote_id}, status={self.status})>"
