"""Base service class with CRUD operations."""

from sqlalchemy.orm import Session
from typing import Any, Generic, TypeVar, Optional, Type, List, Dict
from pydantic import BaseModel
from warehouse_quote_app.app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class that includes CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        """Initialize service with model class."""
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        return self.model.get(db, id)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination."""
        return self.model.get_multi(db, skip=skip, limit=limit)

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_in_data = obj_in.model_dump()
        return self.model.create(db, data=obj_in_data)

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing record."""
        update_data = obj_in.model_dump(exclude_unset=True)
        return self.model.update(db, db_obj=db_obj, data=update_data)

    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Delete a record by ID."""
        return self.model.delete(db, id=id)
