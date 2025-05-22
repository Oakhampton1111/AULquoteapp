"""Simple reporting service used for admin endpoints."""

from sqlalchemy.orm import Session


class ReportingService:
    """Provides basic reporting functionality."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def generate_quote_status_report(self) -> dict:
        """Return a basic quote status report."""
        return {"pending": 0, "accepted": 0, "rejected": 0, "completed": 0, "total": 0}

    async def generate_revenue_report(self, period: str = "month") -> dict:
        """Return a simple revenue report."""
        return {"total": 0, "breakdown": {}}


def get_reporting_service(db: Session) -> ReportingService:
    """Dependency getter."""
    return ReportingService(db)
