# Warehouse Quote App Services

This directory contains the business logic services for the Warehouse Quote Application.

## Service Structure

The services are organized into the following categories:

### Core Services

- **base.py**: Base service classes and interfaces
- **admin.py**: Administrative services for managing the application
- **audit_logger.py**: Service for logging audit events
- **client.py**: Client management services
- **crm.py**: Customer relationship management services
- **customer.py**: Customer management services
- **quote_generator.py**: Quote generation service
- **quote_service.py**: Core quote service for natural language processing
- **quote_lifecycle.py**: Quote lifecycle management service
- **rate.py**: Rate calculation and management services
- **rate_admin.py**: Rate administration services

### Business Services

Located in the `business/` subdirectory:

- **rate_calculator.py**: Storage pricing calculation service
- **container_calculator.py**: Container packing service calculations
- **distance_calculator.py**: Service for calculating distances between postcodes
- **transport_calculator.py**: Transport rate calculation service
- **rule_engine.py**: Business rule validation and enforcement service

### Other Service Directories

- **communication/**: Services for handling communication with customers
- **conversation/**: Conversation state management services
- **llm/**: Large language model integration services
- **metrics/**: Services for collecting and reporting metrics
- **validation/**: Data validation services

## Quote Services

### Quote Lifecycle Service

The `quote_lifecycle.py` service manages the complete lifecycle of quotes, from creation to acceptance/rejection. It provides the following functionality:

- **Create Quote**: Creates a new quote for a customer
- **Get Quote**: Retrieves a quote by ID
- **List Quotes**: Lists quotes with pagination and filtering
- **Update Quote Status**: Updates the status of a quote (accept/reject)
- **Delete Quote**: Deletes a quote

The service uses the repository pattern to interact with the database and provides comprehensive error handling and logging.

### Quote Service

The `quote_service.py` service handles natural language processing for quote generation. It provides:

- Processing of natural language quote requests
- Integration with business services for calculations
- Generation of quote responses with line items
- Handling of missing information and follow-up questions

## Dependencies and Injection

Services follow a consistent dependency injection pattern:

1. Services accept database sessions and optional repositories in their constructors
2. API endpoints instantiate services directly with the injected database session
3. Services use repositories for data access
4. Repositories handle database operations and model conversions

This pattern ensures:
- Clear separation of concerns
- Testability of services
- Flexibility in service composition
- Consistent error handling

## Error Handling

Services implement a consistent error handling pattern:
- Business logic errors are raised as `ValueError` with descriptive messages
- Database errors are caught and logged
- Unexpected errors are logged and propagated for global handling

## Async Support

All services support async/await patterns for database operations, ensuring efficient handling of concurrent requests.
