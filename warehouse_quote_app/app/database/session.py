"""Database session management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncContextManager, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base, registry
from sqlalchemy.pool import AsyncAdaptedQueuePool

# Import the settings at function level to avoid circular imports
from warehouse_quote_app.app.core.config import settings

# Create registry for declarative models
mapper_registry = registry()
Base = mapper_registry.generate_base()

class DatabaseSessionManager:
    """Database session manager."""

    def __init__(self):
        """Initialize session manager."""
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker] = None

    def init(self, db_url: str = None):
        """Initialize database engine and session maker."""
        if self._engine is not None:
            return

        db_url = db_url or settings.ASYNC_SQLALCHEMY_DATABASE_URI
        
        self._engine = create_async_engine(
            db_url,
            echo=settings.DB_ECHO,
            future=True,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            poolclass=AsyncAdaptedQueuePool,
        )
        
        self._sessionmaker = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            expire_on_commit=False,
        )

    async def close(self):
        """Close database connections."""
        if self._engine is None:
            return
        
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def session(self) -> AsyncContextManager[AsyncSession]:
        """Get database session."""
        if self._sessionmaker is None:
            self.init()
            
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def get_sessionmaker(self) -> async_sessionmaker:
        """Get session maker."""
        if self._sessionmaker is None:
            self.init()
        return self._sessionmaker

    async def create_all(self, db_url: str = None):
        """Create all tables."""
        if self._engine is None:
            self.init(db_url)
            
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self, db_url: str = None):
        """Drop all tables."""
        if self._engine is None:
            self.init()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

# Global session manager instance
sessionmanager = DatabaseSessionManager()

# Export only what's needed to avoid circular imports
__all__ = ["Base", "AsyncSession", "async_sessionmaker", "DatabaseSessionManager", "sessionmanager"]
