"""Dependencies for API endpoints."""
from typing import Generator, AsyncGenerator # Added AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession # Added AsyncSession
from warehouse_quote_app.app.database import get_db # Sync session getter
from warehouse_quote_app.app.database.session import AsyncSessionLocal # Assuming this is where AsyncSession factory is

# Re-export get_db for backward compatibility with existing sync endpoints
__all__ = ["get_db", "get_async_db"]


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Committing here might be too broad if an endpoint has multiple db interactions
            # and needs to control transaction boundaries more finely.
            # Consider removing auto-commit/rollback from here and letting endpoint logic handle it.
            # For now, keeping it as per typical simple examples.
            await session.commit() 
        except Exception:
            await session.rollback() 
            raise
        finally:
            await session.close()

# CRM Service Dependency
# Import BaseCRMService and PlaceholderCRMService
from warehouse_quote_app.app.services.crm.base import BaseCRMService
from warehouse_quote_app.app.services.crm.placeholder_service import PlaceholderCRMService

# This can be expanded later to choose CRM service based on config
_crm_service_instance: Optional[BaseCRMService] = None

async def get_crm_service() -> BaseCRMService:
    """
    Dependency that provides a CRM service instance.
    Currently returns a PlaceholderCRMService.
    """
    global _crm_service_instance
    if _crm_service_instance is None:
        # In a real app, you might select the service implementation based on settings:
        # if settings.CRM_PROVIDER == "salesforce":
        #     _crm_service_instance = SalesforceCRMService()
        # elif settings.CRM_PROVIDER == "hubspot":
        #     _crm_service_instance = HubSpotCRMService()
        # else:
        #     _crm_service_instance = PlaceholderCRMService()
        _crm_service_instance = PlaceholderCRMService()
        
    return _crm_service_instance
