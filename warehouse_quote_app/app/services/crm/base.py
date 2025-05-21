import abc
from typing import Optional, List, Dict, Any # Keep these for potential use in methods
# Import the actual Pydantic models from schemas.crm
from warehouse_quote_app.app.schemas.crm import CRMCustomer, CRMCustomerCreate, CRMQuote, CRMQuoteCreate

class BaseCRMService(abc.ABC):
    """Abstract base class for CRM integration services."""

    @abc.abstractmethod
    async def create_or_update_customer(self, customer_data: CRMCustomerCreate) -> Optional[str]:
        """
        Creates a new customer or updates an existing one in the CRM.
        Returns the CRM's unique identifier for the customer if successful, else None.
        """
        pass

    @abc.abstractmethod
    async def get_customer_by_email(self, email: str) -> Optional[CRMCustomer]:
        """
        Retrieves customer details from the CRM by email.
        Returns customer data if found, else None.
        """
        pass

    @abc.abstractmethod
    async def link_quote_to_customer(self, crm_customer_id: str, quote_data: CRMQuoteCreate) -> Optional[str]:
        """
        Links a quote to an existing customer in the CRM.
        Returns the CRM's unique identifier for the quote if successful, else None.
        """
        pass

    @abc.abstractmethod
    async def update_quote_status(self, crm_quote_id: str, status: str, status_reason: Optional[str] = None) -> bool:
        """
        Updates the status of an existing quote in the CRM.
        Returns True if successful, else False.
        """
        pass

    # Optional: Add other common CRM operations as needed
    # async def get_quote_details(self, crm_quote_id: str) -> Optional[CRMQuote]:
    #     pass
    #
    # async def log_interaction(self, crm_customer_id: str, interaction_type: str, details: Dict[str, Any]) -> bool:
    #     pass
