import logging
import uuid
from typing import Optional, List, Dict, Any # Retaining for potential future use in methods

from .base import BaseCRMService
from warehouse_quote_app.app.schemas.crm import CRMCustomer, CRMCustomerCreate, CRMQuote, CRMQuoteCreate

logger = logging.getLogger(__name__)

# In-memory storage for placeholder service
# In a real scenario with multiple instances, this would need a shared store (e.g., Redis, DB)
# or be designed as stateless if CRM is the sole source of truth.
placeholder_crm_db: Dict[str, Any] = {
    "customers_by_crm_id": {},
    "customers_by_email": {},
    "quotes_by_crm_id": {},
    "quotes_by_crm_customer_id": {}
}


class PlaceholderCRMService(BaseCRMService):
    """
    Placeholder implementation of the CRM service.
    Logs actions and uses in-memory storage for basic simulation.
    """

    async def create_or_update_customer(self, customer_data: CRMCustomerCreate) -> Optional[str]:
        logger.info(f"Attempting to create or update customer in CRM: {customer_data.email}")
        
        # Check if customer exists by email to simulate update
        existing_crm_id_by_email = placeholder_crm_db["customers_by_email"].get(customer_data.email)
        
        if existing_crm_id_by_email:
            crm_id = existing_crm_id_by_email
            logger.info(f"Updating existing customer in CRM. Email: {customer_data.email}, CRM ID: {crm_id}")
            # Update existing customer details
            existing_customer_record = placeholder_crm_db["customers_by_crm_id"].get(crm_id)
            if existing_customer_record:
                updated_data = customer_data.model_dump(exclude_unset=True)
                for key, value in updated_data.items():
                    setattr(existing_customer_record, key, value) # Update fields
            else: # Should not happen if customers_by_email is consistent
                logger.error(f"Data inconsistency: Customer with email {customer_data.email} has crm_id {crm_id} in email index, but not found in main customer store.")
                # Fallback to creating a new one, though this indicates an issue.
                # Or simply return None / raise error
                return None

        else:
            # Create new customer
            crm_id = f"placeholder_cust_{uuid.uuid4()}"
            logger.info(f"Creating new customer in CRM. Email: {customer_data.email}, New CRM ID: {crm_id}")
            
            # Store using CRMCustomer schema to include crm_id
            new_customer_record = CRMCustomer(
                **customer_data.model_dump(),
                crm_id=crm_id
            )
            placeholder_crm_db["customers_by_crm_id"][crm_id] = new_customer_record
            placeholder_crm_db["customers_by_email"][customer_data.email] = crm_id
            
        return crm_id

    async def get_customer_by_email(self, email: str) -> Optional[CRMCustomer]:
        logger.info(f"Attempting to get customer by email from CRM: {email}")
        crm_id = placeholder_crm_db["customers_by_email"].get(email)
        if crm_id:
            customer_record = placeholder_crm_db["customers_by_crm_id"].get(crm_id)
            if customer_record:
                logger.info(f"Customer found in CRM. Email: {email}, CRM ID: {crm_id}")
                return customer_record # customer_record is already a CRMCustomer instance
            else:
                logger.warning(f"Data inconsistency: Customer crm_id {crm_id} found for email {email}, but no record in main store.")
        
        logger.info(f"Customer with email {email} not found in CRM.")
        return None

    async def link_quote_to_customer(self, crm_customer_id: str, quote_data: CRMQuoteCreate) -> Optional[str]:
        logger.info(f"Attempting to link quote (App Quote ID: {quote_data.app_quote_id}) to CRM Customer ID: {crm_customer_id}")
        
        if crm_customer_id not in placeholder_crm_db["customers_by_crm_id"]:
            logger.warning(f"Customer with CRM ID {crm_customer_id} not found. Cannot link quote.")
            return None
            
        crm_quote_id = f"placeholder_quote_{uuid.uuid4()}"
        
        # Store using CRMQuote schema
        new_quote_record = CRMQuote(
            **quote_data.model_dump(),
            crm_quote_id=crm_quote_id
            # crm_customer_id=crm_customer_id # If CRMQuote schema had this field
        )
        
        placeholder_crm_db["quotes_by_crm_id"][crm_quote_id] = new_quote_record
        
        if crm_customer_id not in placeholder_crm_db["quotes_by_crm_customer_id"]:
            placeholder_crm_db["quotes_by_crm_customer_id"][crm_customer_id] = []
        placeholder_crm_db["quotes_by_crm_customer_id"][crm_customer_id].append(new_quote_record)
        
        logger.info(f"Quote linked successfully. CRM Quote ID: {crm_quote_id}, CRM Customer ID: {crm_customer_id}")
        return crm_quote_id

    async def update_quote_status(self, crm_quote_id: str, status: str, status_reason: Optional[str] = None) -> bool:
        logger.info(f"Attempting to update status of CRM Quote ID: {crm_quote_id} to '{status}'. Reason: {status_reason or 'N/A'}")
        
        quote_record = placeholder_crm_db["quotes_by_crm_id"].get(crm_quote_id)
        if quote_record:
            quote_record.status = status
            # In a real CRM, you might log the status_reason as a note or activity.
            logger.info(f"CRM Quote ID: {crm_quote_id} status updated to '{status}'.")
            return True
        
        logger.warning(f"CRM Quote ID: {crm_quote_id} not found. Status update failed.")
        return False
