"""Rate administration service for managing rates."""

from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from warehouse_quote_app.app.database.db import get_db
from warehouse_quote_app.app.models.rate import Rate
from warehouse_quote_app.app.schemas.rate.rate import RateCreate, RateUpdate
from warehouse_quote_app.app.repositories.rate import RateRepository


class RateAdminService:
    """Service layer for admin rate management."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = RateRepository(Rate)

    async def list(self, skip: int = 0, limit: int = 100) -> List[Rate]:
        return self.repo.get_multi(self.db, skip=skip, limit=limit)

    async def get(self, rate_id: int) -> Optional[Rate]:
        return self.repo.get(self.db, rate_id)

    async def create(self, rate: RateCreate) -> Rate:
        return self.repo.create(self.db, obj_in=rate)

    async def update(self, rate_id: int, rate_in: RateUpdate) -> Rate:
        db_rate = self.repo.get(self.db, rate_id)
        if not db_rate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")
        return self.repo.update(self.db, db_obj=db_rate, obj_in=rate_in)

    async def delete(self, rate_id: int) -> None:
        db_rate = self.repo.get(self.db, rate_id)
        if not db_rate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")
        self.repo.delete(self.db, id=rate_id)


def get_rate_admin_service(db: Session = Depends(get_db)) -> RateAdminService:
    return RateAdminService(db)
