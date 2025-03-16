# Warehouse Quote Application

This project provides a comprehensive solution for managing warehouse quotes, integrating AI-powered rate optimization, and offering a user-friendly interface for both administrators and customers.

Key components include:

*   Frontend: A React-based user interface for managing quotes and interacting with the system.
*   Backend: A FastAPI-based API for handling quote requests, user management, and rate optimization.
*   Shared Services: Contains code shared between the frontend and backend.
*   Database: PostgreSQL database for storing quotes, rates, and user information.
*   AI Integration: Includes AI-powered rate optimization features.

## Features

- **AI-Powered Quote Generation**
  - Interactive chat interface for quote creation
  - Smart information collection
  - Rate compliance enforcement
  - Controlled discount management
  - Real-time rate validation
  - Context-aware suggestions
  - Rate optimization with LLM
  - RAG-powered context retrieval

- **Authentication System**
  - Token-based authentication
  - Role-based access control
  - Password reset flow
  - Session management
  - Activity logging
  - Security monitoring

- **Memory Management**
  - Short-term conversation context
  - Long-term client preferences
  - Service history tracking
  - Common requirements storage
  - Cross-session memory
  - Preference learning

- **Rate Calculator Integration**
  - Real-time quote generation
  - Automatic rate validation
  - Service modification support
  - Discount application rules
  - AI-assisted pricing
  - Market trend analysis

- **Core Features**
  - Real-time chat interface
  - Rate card management
  - RAG system for context
  - Admin dashboard
  - Customer portal
  - Analytics engine

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-ml.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
warehouse_quote_app/
├── app/
│   ├── services/
│   │   ├── llm/               # AI/ML services
│   │   │   ├── model.py       # FLAN-T5 model
│   │   │   ├── rag.py         # RAG service
│   │   │   ├── rate_integration.py # Rate optimization
│   │   │   ├── templates/     # Prompt templates
│   │   │   └── knowledge/     # Knowledge base
│   │   ├── auth/             # Auth services
│   │   │   ├── jwt.py        # JWT handling
│   │   │   ├── password.py   # Password management
│   │   │   └── roles.py      # Role management
│   │   ├── rate_calculator/  # Rate services
│   │   │   ├── calculator.py # Core calculator
│   │   │   ├── validator.py  # Rate validation
│   │   │   └── ai.py        # AI integration
│   │   └── memory/          # Memory services
│   │       ├── context.py    # Context management
│   │       └── storage.py    # Storage handling
│   ├── routes/
│   │   ├── admin.py         # Admin endpoints
│   │   ├── customer.py      # Customer endpoints
│   │   ├── auth.py         # Auth endpoints
│   │   └── chat.py         # Chat endpoints
│   └── models/
│       ├── user.py         # User models
│       ├── quote.py        # Quote models
│       └── rate_card.py    # Rate card models
├── frontend-new/          # React frontend
└── tests/                # Test suite
```

## API Endpoints

The API endpoints are documented in the [ARCHITECTURE.md](docs/ARCHITECTURE.md) file.

## Database Schema

The database schema is documented in the [ARCHITECTURE.md](docs/ARCHITECTURE.md) file.

## Monitoring and Logging

Monitoring and logging are configured using Prometheus and Grafana. Logs are aggregated for easy searching and analysis.

## Dependencies

### Backend
- FastAPI
- SQLAlchemy
- Transformers
- Torch
- FAISS
- Sentence Transformers
- Langchain
- Pydantic
- PyJWT
- Passlib
- Redis

### Frontend
- React
- Ant Design
- React Query
- TypeScript

## Documentation

- [API Documentation](API.md) - API endpoints and usage
- [Auth System](docs/auth.md) - Authentication and authorization
- [Chat System](docs/chat.md) - Chat system architecture
- [Rate Calculator](docs/rate_calculator.md) - Rate calculation
- [AI Integration](docs/ai.md) - AI/ML components

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app
```

### Code Quality
```bash
# Run linter
flake8

# Run type checker
mypy app

# Format code
black app
```

## Recent Updates

### Backend Service Consolidation (February 2025)

#### Service Structure Reorganization
- Consolidated services from multiple directories
- Moved business logic services to `warehouse_quote_app/app/services/business/`
- Created consistent service implementations across the application
- Standardized import paths for better maintainability

#### Business Services Implementation
- **Rate Calculator**: Comprehensive rate calculation service for storage pricing
- **Container Calculator**: Specialized service for container packing calculations
- **Distance Calculator**: Service for calculating distances between locations
- **Transport Calculator**: Handles transport rate calculations with various vehicle types
- **Rule Engine**: Business rule validation and enforcement service

#### Administrative Services
- **Admin Service**: Dashboard metrics, customer and quote management
- **Rate Admin Service**: Rate card management and CRUD operations
- **Quote Generator**: Quote generation logic and pricing calculation

#### Service Integration Updates (March 2025)
- Updated `quote_generator.py` to use business services for calculations
- Integrated Rate Calculator for storage pricing
- Integrated Transport Calculator for transport cost calculations
- Integrated Container Calculator for container packing costs
- Added helper methods to convert between request formats
- Improved decimal handling for financial calculations
- Updated import paths to use fully qualified module names
- Removed redundant files from old directories after migration

### Comprehensive Test Suite Implementation (February 2025)

#### End-to-End Experience Testing
- Created comprehensive test suite for customer and admin experiences
- Implemented test cases for complete user journeys from login to quote management
- Validated quote generation, negotiation, and approval workflows
- Added test coverage for dashboard access and functionality
- Ensured proper authentication and authorization throughout the system

#### Conversation Flow Testing
- Developed detailed tests for conversation state machine
- Validated proper state transitions and parameter extraction
- Tested intent recognition and entity extraction
- Verified quote generation from conversation parameters
- Added test cases for discount negotiation and quote acceptance/rejection

#### Quote Service Testing
- Implemented tests for quote calculation and generation
- Validated discount eligibility and application logic
- Added test coverage for quote approval workflows
- Tested quote acceptance and rejection processes
- Verified quote retrieval and filtering functionality

#### Admin Dashboard Testing
- Created tests for admin dashboard components and access
- Implemented test cases for customer management functionality
- Validated quote approval and discount management
- Tested reporting and analytics features
- Added coverage for rate card management

### Conversation Module Updates (February 2025)

#### Language Support Removal
- Removed multilingual support to simplify the conversation handling module
- Deleted `language_handler.py` and removed all references to `LanguageHandler`
- Updated module documentation to reflect English-only support

#### Conversation Flow Testing
- Conducted thorough testing of the conversation flow
- Verified proper state transitions: initial → storage_type → quantity → duration
- Confirmed error handling for invalid inputs
- Enhanced test logging to provide detailed conversation flow visibility
- All tests passing with proper state management and information gathering

### Database and Configuration (February 2025)
- Added async database session management
- Implemented database initialization with default data
- Enhanced configuration management with environment support
- Added comprehensive error handling for database operations
- Fixed database configuration issues:
  - Added SQLALCHEMY_DATABASE_URI property to Settings class
  - Added DB_ECHO configuration parameter
  - Updated datetime handling to use timezone-aware objects

### Chat API Endpoints (February 2025)
- Added conversation-based quote generation endpoints
- Implemented chat message processing
- Added conversation history retrieval
- Created schemas for chat functionality
- Integrated with conversation state management

### Code Health and Organization
- Improved code health analysis with enhanced metrics
- Reduced code duplication in report schemas
- Added robust base classes for metrics and reporting
- Enhanced error handling and request logging
- Implemented comprehensive middleware stack

### Backend Refactoring (February 2025)

#### Quote Lifecycle Service Implementation
- Created new `quote_lifecycle.py` service for managing the complete quote lifecycle
- Implemented proper async handling of quote operations
- Added comprehensive error handling and logging
- Standardized response models with pagination support
- Added `QuoteListResponse` schema for paginated quote lists

#### API Endpoint Refactoring
- Refactored quote endpoints to use direct dependency injection
- Updated customer endpoints with consistent dependency patterns
- Improved error handling in all API routes
- Standardized import paths using fully qualified module names
- Removed circular dependencies between services and endpoints

#### Dependency Management Improvements
- Simplified service instantiation in route handlers
- Implemented direct AsyncSession injection for better testability
- Removed reliance on global service providers
- Enhanced repository pattern implementation
- Improved separation of concerns between layers

### Application Structure
- Reorganized main application structure
- Added proper FastAPI lifespan management
- Enhanced WebSocket support for real-time features
- Improved static file serving for frontend assets

### Middleware Components
- Added RequestLoggingMiddleware for request tracking
- Implemented ErrorHandlingMiddleware for consistent error responses
- Added AuthenticationMiddleware with token validation
- Created comprehensive exception hierarchy

### Report System
- Enhanced report schema organization
- Added generic base classes for metrics
- Improved customer and service reporting
- Added time-series support for metrics

For detailed information about specific components, see:
- [Authentication](./app/core/security.py)
- [Database](./app/database.py)
- [API Routes](./app/api/v1/api.py)
- [Middleware](./app/middleware/)
- [Report Schemas](./app/schemas/reports/)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see LICENSE for details
