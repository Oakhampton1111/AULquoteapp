"""
Test utilities for the warehouse quote application.

This module provides helper functions for testing the application.
"""

import asyncio
from typing import Any, Dict, Optional, Callable, TypeVar, Awaitable, List, Union
from unittest.mock import AsyncMock

T = TypeVar('T')


def async_return(value: T) -> Awaitable[T]:
    """
    Create a coroutine that returns the given value.
    
    This is useful for mocking async functions that return values.
    """
    f = asyncio.Future()
    f.set_result(value)
    return f


def configure_mock_db_for_test(mock_db: AsyncMock, test_data: Dict[str, Any]) -> None:
    """
    Configure a mock database session with test data.
    
    Args:
        mock_db: The mock database session to configure
        test_data: Dictionary mapping entity types to test data
    """
    # Configure execute().scalars().all() to return appropriate test data
    def mock_execute_side_effect(query, *args, **kwargs):
        # Extract the entity type from the query (simplified approach)
        query_str = str(query)
        
        result_mock = AsyncMock()
        scalars_mock = AsyncMock()
        all_mock = AsyncMock()
        first_mock = AsyncMock()
        one_mock = AsyncMock()
        
        # Set up the chain of mocks
        result_mock.scalars = lambda: scalars_mock
        scalars_mock.all = lambda: all_mock
        scalars_mock.first = lambda: first_mock
        scalars_mock.one = lambda: one_mock
        result_mock.first = lambda: first_mock
        result_mock.one = lambda: one_mock
        
        # Try to determine what data to return based on the query
        for entity_name, data in test_data.items():
            if entity_name.lower() in query_str.lower():
                all_mock.return_value = data if isinstance(data, list) else [data]
                first_mock.return_value = data[0] if isinstance(data, list) and data else data
                one_mock.return_value = data[0] if isinstance(data, list) and data else data
                return async_return(result_mock)
        
        # Default empty results
        all_mock.return_value = []
        first_mock.return_value = None
        one_mock.return_value = None
        return async_return(result_mock)
    
    # Set the side effect
    mock_db.execute.side_effect = mock_execute_side_effect


def patch_async_method(obj: Any, method_name: str, return_value: Any = None) -> AsyncMock:
    """
    Patch an async method on an object with a mock that returns the given value.
    
    Args:
        obj: The object to patch
        method_name: The name of the method to patch
        return_value: The value to return from the mocked method
        
    Returns:
        The mock object
    """
    mock = AsyncMock()
    if return_value is not None:
        mock.return_value = async_return(return_value)
    
    original_method = getattr(obj, method_name)
    setattr(obj, method_name, mock)
    
    # Store original method for restoration
    mock.original_method = original_method
    
    return mock


def mock_repository_methods(mock_db: AsyncMock, entity_name: str, test_data: Union[List[Any], Any]) -> None:
    """
    Configure a mock database session to handle common repository methods.
    
    Args:
        mock_db: The mock database session to configure
        entity_name: The name of the entity (e.g., 'user', 'quote')
        test_data: Test data to return for the entity
    """
    # Ensure test_data is a list
    data_list = test_data if isinstance(test_data, list) else [test_data]
    
    # Configure common repository methods
    mock_db.add.return_value = None
    mock_db.add_all.return_value = None
    
    # Configure refresh to update the passed object with test data
    async def mock_refresh(obj):
        if hasattr(obj, 'id') and not obj.id:
            # Assign an ID if it doesn't have one
            obj.id = 1
        # Could add more sophisticated logic here to update the object
        return None
    
    mock_db.refresh.side_effect = mock_refresh
