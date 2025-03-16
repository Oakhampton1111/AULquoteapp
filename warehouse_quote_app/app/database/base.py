"""Base declarative model for SQLAlchemy ORM."""

from sqlalchemy.orm import registry

# Create registry for declarative models
mapper_registry = registry()
Base = mapper_registry.generate_base()
