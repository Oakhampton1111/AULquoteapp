"""Database initialization and cleanup functions."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generator, AsyncGenerator
from sqlalchemy.orm import Session

from warehouse_quote_app.app.database.session import Base, sessionmanager
from warehouse_quote_app.app.core.config import settings

async def init_db() -> None:
    """Initialize database with tables and initial data."""
    # Create tables
    await sessionmanager.create_all()
    
    # Create initial data if needed
    async with sessionmanager.session() as session:
        from warehouse_quote_app.app.core.init_data import create_initial_data
        await create_initial_data(session)
        await session.commit()

async def close_db() -> None:
    """Close database connections."""
    await sessionmanager.close()
    # Also close synchronous connections
    engine.dispose()

# Legacy synchronous database functions for backward compatibility
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create engine for synchronous operations
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# Session factory for synchronous operations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    """Dependency for synchronous database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_sync_db() -> None:
    """Initialize database with tables and initial data (synchronous version)."""
    # Import models here to ensure they are registered with the Base
    from warehouse_quote_app.app.models import (
        user, quote, storage, transport, container
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
