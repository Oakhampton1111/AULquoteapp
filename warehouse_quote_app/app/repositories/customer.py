"""Customer repository for database operations."""

from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from warehouse_quote_app.app.models.customer import Customer
from warehouse_quote_app.app.core.logging import get_logger

logger = get_logger("customer_repository")

class CustomerRepository:
    """Repository for customer database operations."""

    def __init__(self, db: Session) -> None:
        """Initialize the customer repository.
        
        Args:
            db: Database session
        """
        self.db = db

    def get(self, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID.
        
        Args:
            customer_id: ID of the customer to retrieve
            
        Returns:
            Customer: Customer object if found, None otherwise
        """
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_by_email(self, email: str) -> Optional[Customer]:
        """Get a customer by email.
        
        Args:
            email: Email of the customer to retrieve
            
        Returns:
            Customer: Customer object if found, None otherwise
        """
        return self.db.query(Customer).filter(Customer.email == email).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """List customers with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Customer]: List of customer objects
        """
        return self.db.query(Customer).offset(skip).limit(limit).all()

    def create(self, customer_data: Dict[str, Any]) -> Customer:
        """Create a new customer.
        
        Args:
            customer_data: Dictionary with customer data
            
        Returns:
            Customer: Created customer object
        """
        customer = Customer(**customer_data)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(self, customer_id: int, customer_data: Dict[str, Any]) -> Optional[Customer]:
        """Update an existing customer.
        
        Args:
            customer_id: ID of the customer to update
            customer_data: Dictionary with updated customer data
            
        Returns:
            Customer: Updated customer object if found, None otherwise
        """
        customer = self.get(customer_id)
        if not customer:
            return None
            
        for key, value in customer_data.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
                
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer_id: int) -> bool:
        """Delete a customer.
        
        Args:
            customer_id: ID of the customer to delete
            
        Returns:
            bool: True if customer was deleted, False otherwise
        """
        customer = self.get(customer_id)
        if not customer:
            return False
            
        self.db.delete(customer)
        self.db.commit()
        return True

    def count(self) -> int:
        """Count total number of customers.
        
        Returns:
            int: Total number of customers
        """
        return self.db.query(Customer).count()

    def search(self, query: str, limit: int = 10) -> List[Customer]:
        """Search for customers by name or email.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List[Customer]: List of matching customers
        """
        search_pattern = f"%{query}%"
        return (
            self.db.query(Customer)
            .filter(
                (Customer.name.ilike(search_pattern)) | 
                (Customer.email.ilike(search_pattern))
            )
            .limit(limit)
            .all()
        )

    def get_dashboard_data(self, customer_id: int) -> Dict[str, Any]:
        """Get dashboard data for a customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            Dict[str, Any]: Dashboard data including profile, quotes, and services
        """
        # This would typically join with quotes and other related tables
        # For now, return a basic structure
        customer = self.get(customer_id)
        if not customer:
            return {}
            
        return {
            "profile": customer,
            "recent_quotes": [],
            "active_services": [],
            "notifications": []
        }
