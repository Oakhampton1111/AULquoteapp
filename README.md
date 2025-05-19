# AU Logistics Warehouse Quote System

⚠️ **IMPORTANT: This is the main documentation entry point. Always start here.** ⚠️

A professional warehouse quote management system built with FastAPI and React.

## Knowledge Graph System

The project includes a sophisticated knowledge graph system for code analysis and maintenance. This system helps track code relationships, detect potential issues, and maintain code quality.

### Components

#### 1. Graph Database (`tools/db/graph_db.py`)
- SQLite-based graph database for storing code structure
- Supports incremental updates and structure queries
- Maintains relationships between code components
- Provides dead code and duplicate detection

#### 2. TypeScript Analyzer (`tools/kg/ts_analyzer.py`)
- Parses TypeScript/TSX files
- Extracts classes, methods, functions, and relationships
- Integrates with the knowledge graph system
- Handles imports and dependencies

#### 3. Graph Updater (`tools/kg/graph_updater.py`)
- Watches for file changes in Python and TypeScript files
- Implements smart validation to prevent unnecessary updates
- Supports four types of updates:
  - `SYNTAX_ONLY`: Only whitespace or comments changed (skipped)
  - `MINOR`: Small changes that don't affect structure
  - `STRUCTURAL`: Changes that affect code structure
  - `BREAKING`: Changes that could break dependencies
- Uses file hashing to detect real changes
- Batches updates for better performance

#### 4. Visualization Dashboard (`tools/visualization/dashboard.py`)
- Interactive Streamlit-based dashboard
- Real-time graph visualization
- Dead code analysis
- Code duplication detection
- Statistics and metrics

### Update Validation System

The knowledge graph implements a robust validation system to ensure updates are appropriate:

1. **Change Detection**
   - File hashing to detect actual content changes
   - Skips updates if only whitespace or comments changed
   - Validates syntax before processing

2. **Structure Analysis**
   - Compares old and new code structure
   - Tracks changes in classes, methods, functions, and imports
   - Identifies breaking changes that could affect dependencies

3. **Update Classification**
   - SYNTAX_ONLY: Skipped (comments, whitespace)
   - MINOR: Method body changes, non-structural updates
   - STRUCTURAL: New classes/functions added
   - BREAKING: Removed or renamed components

4. **Safety Measures**
   - Transaction-based updates
   - Rollback on errors
   - Detailed logging of all changes
   - Batched processing to prevent overwrites

### Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
npm install -g typescript @typescript-eslint/parser @typescript-eslint/typescript-estree
```

2. Start the knowledge graph system:
```bash
python tools/start_knowledge_graph.py
```

This will:
- Launch the visualization dashboard
- Start the file watcher
- Begin tracking code changes

### Usage

The system automatically:
- Tracks changes in Python and TypeScript files
- Updates the knowledge graph when appropriate
- Provides real-time visualization
- Alerts on potential issues (dead code, duplicates)

### Configuration

Key configuration files:
- `requirements.txt`: Python dependencies
- `tools/start_knowledge_graph.py`: System startup
- `tools/visualization/dashboard.py`: Dashboard settings
- `tools/kg/graph_updater.py`: Update validation rules

### Development Status

- [x] Knowledge Graph Generation
- [x] SQLite Database Integration
- [x] Visualization Dashboard
- [x] TypeScript Analysis
- [x] Automated Updates
- [x] Update Validation
- [ ] LangGraph Integration (Next)
- [ ] RAG Pipeline Setup (Planned)

## Contributing

When making changes:
1. Ensure all tests pass
2. Update documentation
3. Follow the update validation guidelines
4. Test with both Python and TypeScript files

## Documentation Map

### Core Documentation
- 📋 [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - **Start here for system design and dependencies**
- 📋 [MIGRATION.md](./docs/MIGRATION.md) - Current progress and next steps

### Component Documentation
- 📁 [warehouse_quote_app/README.md](./warehouse_quote_app/README.md) - Backend service details
- 📁 [frontend/README.md](./frontend/README.md) - Frontend application details
- 📁 [deployment/config/README.md](./deployment/config/README.md) - Configuration guide
- 📁 [deployment/scripts/README.md](./deployment/scripts/README.md) - Utility scripts
- 📁 [shared/README.md](./shared/README.md) - Shared utilities

## Project Status

### Completed
- ✓ Configuration System
  - Base configuration (.env)
  - Environment-specific overrides
  - Shared component settings
- ✓ Documentation Structure
  - Architecture documentation
  - Migration planning
  - Dependency mapping

### In Progress (Critical Path)
1. Core Infrastructure
   - Database setup and configuration
   - Security implementation
   - API foundation

2. Essential Services
   - Authentication service
   - Quote service (basic)
   - Rate service (basic)

3. Testing Infrastructure
   - Test environment setup
   - Core test implementation
   - Integration test setup

See [MIGRATION.md](./docs/MIGRATION.md) for detailed progress and next steps.
See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for system design and dependencies.

## Features

- **Quote Management**
  - Create and manage warehouse quotes
  - Real-time quote status updates
  - Automated quote calculations
  - PDF quote generation
  - AI-powered quote assistance and rate optimization
  - Smart rate validation

- **User Management**
  - Enhanced role-based access control (Admin/Customer)
  - Unified authentication system
  - Secure password reset flow
  - Profile management with preferences
  - Activity tracking and audit logs

- **Rate Card Management**
  - Dynamic rate card configuration
  - Category-based pricing
  - Bulk rate updates
  - Active/Inactive status
  - AI-assisted rate validation

- **Reporting & Analytics**
  - Quote conversion rates
  - Service usage statistics
  - Customer activity tracking
  - Revenue analytics
  - AI insights dashboard

- **Real-time Features**
  - WebSocket notifications
  - Live quote updates
  - Activity feed
  - System alerts
  - Real-time chat support

- **Frontend (React + Vite)**
  - Modern UI with Ant Design
  - Responsive design
  - Unified authentication system
  - Comprehensive error handling
  - Interactive forms with validation
  - Real-time analytics dashboard
  - Efficient data caching with React Query
  - TypeScript for type safety
  - Skeleton loading states
  - Role-based navigation

## Tech Stack

- **Backend**
  - FastAPI
  - SQLAlchemy 2.0+ (async ORM)
  - Pydantic
  - PostgreSQL
  - Redis (Caching)
  - Celery (Task Queue)
  - FLAN-T5 (AI Model)
  - RAG System
  - Langchain

- **Frontend**
  - React 18
  - TypeScript 5
  - Ant Design 5
  - React Query v4
  - React Router v6
  - Styled Components
  - Vite
  - Error Boundaries
  - Context Providers

- **DevOps & Monitoring**
  - Docker
  - Prometheus
  - Sentry
  - OpenTelemetry

- **Testing**
  - Pytest (Backend)
  - React Testing Library (Frontend)
  - Playwright (E2E)

## Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 15+
- Redis (optional, for caching)

### Quick Start
1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Install dependencies:
   ```bash
   # Backend
   cd warehouse_quote_app
   pip install -r requirements/dev.txt

   # Frontend
   cd frontend
   npm install
   ```

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Start development servers:
   ```bash
   # Backend
   uvicorn app.main:app --reload

   # Frontend
   npm run dev
   ```

## Critical Dependencies

1. Configuration → Security → API
   - Configuration must be loaded first
   - Security must be active before API
   - Environment affects both

2. Database → Services → Features
   - Database connection required
   - Services depend on models
   - Features need both

3. AI/LLM → Rate Optimization → Quotes
   - AI models must be configured
   - Rate optimization needs AI
   - Quotes need both

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for complete dependency mapping.

## Testing

### Current Focus
1. Test Environment Setup
   - Test database configuration
   - Mock services
   - Test data preparation

2. Core Tests
   - Authentication
   - Quote generation
   - Rate calculation

3. Integration Tests
   - Service integration
   - API endpoints
   - Performance baselines

See [MIGRATION.md](./docs/MIGRATION.md) for testing roadmap.

## Type Safety

We use strict type checking throughout the codebase to ensure type safety and catch potential errors early. Key components include:

### Backend (Python)
- Strict mypy type checking with `--strict` flag
- Pydantic models for request/response validation
- Type hints required for all functions and methods
- Custom validators for business rules
- No implicit Any types

Key files:
- `app/schemas/base.py`: Base Pydantic models and common configurations
- `app/schemas/customer.py`: Customer-related schemas with validation
- `app/schemas/rate.py`: Rate-related schemas with validation
- `app/services/validation/validation.py`: Validation service with type-safe business rules

### Frontend (TypeScript)
- TypeScript in strict mode
- No implicit any
- Strict null checks
- Exhaustive type checking

For detailed type safety guidelines, see [TYPE_SAFETY.md](./docs/TYPE_SAFETY.md).

## Shared Code Organization

The project uses a shared code structure to maintain consistency between frontend and backend:

### Core Components

1. **Types** (`shared/types/`)
   - Common interfaces
   - API contracts
   - Shared enums
   - Type definitions

2. **Utilities** (`shared/utils/`)
   - Validation functions
   - Formatting helpers
   - Common calculations
   - Shared constants

### Key Features

1. **Type Safety**
   - Consistent types across stack
   - Runtime type checking
   - API contract validation
   - Automatic type generation

2. **Code Reuse**
   - Shared business logic
   - Common utilities
   - Consistent validation
   - Standard formatting

3. **Maintainability**
   - Single source of truth
   - Reduced duplication
   - Centralized updates
   - Version control

For detailed shared code documentation, see [Shared Code Guide](shared/README.md).

## Database Management

The project uses SQLAlchemy with Alembic for database management:

### Structure

```
app/
├── db/           # Database infrastructure
│   ├── migrations/  # Alembic migrations
│   ├── session.py  # Session management
│   └── utils/      # Database utilities
├── models/       # SQLAlchemy models
│   ├── base.py     # Base model class
│   ├── customer.py # Customer models
│   ├── quote.py    # Quote models
│   ├── rate.py     # Rate models
│   └── user.py     # User models
└── config/      # Configuration
    └── settings.py # Database settings
```

### Key Components

1. **Model Organization**
   - Domain-driven design
   - Type-safe interfaces
   - Common base model
   - Field validation
   - Relationship management

2. **Migration Management**
   - Alembic for migrations
   - Version control
   - Automated generation
   - Data migrations
   - Rollback support

3. **Session Management**
   - Connection pooling
   - Transaction handling
   - Resource cleanup
   - Error recovery
   - Health monitoring

4. **Configuration**
   - Environment-based
   - Pool settings
   - Connection timeouts
   - SSL configuration
   - Logging setup

### Development Workflow

1. **Schema Changes**
   ```bash
   # Create migration
   alembic revision --autogenerate -m "add_feature"
   
   # Run migration
   alembic upgrade head
   ```

2. **Model Updates**
   ```python
   # Update model
   class Model(BaseModel):
       field = Column(String)
   
   # Generate migration
   # Test changes
   ```

For detailed documentation, see:
- [Database Guide](app/db/README.md)
- [Model Documentation](app/models/README.md)
- [Migration Guide](app/db/migrations/README.md)

## Configuration Management

The application uses a centralized configuration management system:

```
config/
├── development/     # Development environment
├── production/     # Production environment
├── staging/       # Staging environment
└── shared/        # Shared configuration
```

### Environment Setup

1. Copy appropriate `.env` files from `config/<environment>/` to project root
2. For development:
   ```bash
   cp config/development/backend.env .env
   cp config/development/frontend.env frontend/.env
   ```

### Configuration Categories

1. **Backend Configuration**
   - Application settings
   - Authentication
   - Database
   - AI/LLM
   - Monitoring

2. **Frontend Configuration**
   - API endpoints
   - Feature flags
   - UI settings
   - Development tools

3. **Shared Configuration**
   - Database settings
   - AI model configuration
   - Common variables

For detailed configuration information, see [Configuration Guide](config/README.md).

## Documentation

Comprehensive documentation is available in the `docs` directory:

- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - System architecture and design patterns
- [CONFIGURATION.md](./docs/CONFIGURATION.md) - Configuration structure and management
- [DEVELOPMENT.md](./docs/DEVELOPMENT.md) - Development setup and guidelines
- [TYPE_SAFETY.md](./docs/TYPE_SAFETY.md) - Type safety practices and guidelines
- [AUTH.md](./docs/auth.md) - Authentication system and token blacklist

## Code Cleanup Initiative

The project is undergoing a systematic cleanup and optimization effort. This initiative focuses on:
- Reducing code complexity
- Eliminating redundancy
- Removing dead code
- Improving maintainability

### Cleanup Documentation
- [Cleanup Plan](docs/CLEANUP_PLAN.md): Detailed phased approach to code cleanup
- [High Severity Issues](high_severity_issues.md): Current critical issues being addressed
- [Implementation Details](docs/IMPLEMENTATION_CLEANUP.md): Technical details of the cleanup process

### Progress Tracking
The cleanup is being executed in phases:
1. **Phase 1** (In Progress): High-Severity Structural Issues
2. **Phase 2** (Planned): Critical Dead Code Removal
3. **Phase 3** (Planned): Code Duplication Consolidation
4. **Phase 4** (Planned): Medium and Low Severity Issues

For detailed progress and next steps, see the [Cleanup Plan](docs/CLEANUP_PLAN.md).

## Development Tools

The project includes a centralized development toolset:

### Quick Start

```powershell
# Setup development environment
.\run.ps1 setup

# Run all development tasks
.\run.ps1 all
```

### Available Commands

1. **Environment Setup**
   ```powershell
   .\run.ps1 setup -Target both
   ```

2. **Code Quality**
   ```powershell
   # Lint code
   .\run.ps1 lint

   # Format code
   .\run.ps1 format
   ```

3. **Testing**
   ```powershell
   # Run all tests
   .\run.ps1 test

   # Run frontend tests only
   .\run.ps1 test -Target frontend
   ```

4. **Building**
   ```powershell
   # Build for production
   .\run.ps1 build
   ```

For detailed development documentation, see [Development Tools Guide](scripts/dev/README.md).

## Development Scripts

The project includes various utility scripts in the `scripts/` directory:

### Database Scripts

Located in `scripts/db/`:
- `add_rate_card.py`: Add new rate cards to the database
- `create_initial_rates.py`: Create initial rate structure
- `populate_rates.py`: Populate rates with default values
- `seed_rate_cards.py`: Seed rate cards with test data

### Test Scripts

Located in `scripts/`:
- `cleanup_test_artifacts.ps1`: Clean up test artifacts and reports

### Running Scripts

Use the script runner:

```powershell
# Run a script
.\run.ps1 -ScriptName <script-name>

# Available script names:
- add-rates
- create-rates
- populate-rates
- seed-rates
- cleanup-tests

# Example:
.\run.ps1 -ScriptName create-rates
```

## Build System

The project uses a monorepo structure with centralized build configuration:

### Version Management

All packages in the monorepo share the same version (1.0.0) defined in:
- Root `package.json`
- Frontend `package.json`
- Backend `pyproject.toml`

### Package Management

1. **Frontend (Node.js)**
   ```json
   {
     "name": "aul-quote-app",
     "version": "1.0.0",
     "workspaces": [
       "frontend",
       "shared/*"
     ]
   }
   ```

2. **Backend (Python)**
   ```toml
   [project]
   name = "aul-quote-app"
   version = "1.0.0"
   requires-python = ">=3.9"
   ```

### Dependency Management

1. **Frontend Dependencies**
   - Managed through Yarn Workspaces
   - Shared dependencies in root `package.json`
   - Frontend-specific in `frontend/package.json`

2. **Backend Dependencies**
   - Managed through `pyproject.toml`
   - Development dependencies in `[project.optional-dependencies]`
   - Runtime dependencies in `[project.dependencies]`

### Build Scripts

1. **Frontend**
   ```bash
   # Development
   yarn start          # Start dev server
   yarn build         # Production build
   yarn test          # Run tests
   yarn lint          # Run linting
   yarn format        # Format code

   # Production
   yarn build         # Build for production
   yarn preview       # Preview production build
   ```

2. **Backend**
   ```bash
   # Development
   python -m pip install -e ".[dev]"  # Install with dev dependencies
   pytest                            # Run tests
   black .                          # Format code
   ruff check .                     # Run linting

   # Production
   python -m pip install .          # Install runtime dependencies
   uvicorn app.main:app            # Start server
   ```

### Quality Tools

1. **Frontend**
   - TypeScript for type checking
   - ESLint for linting
   - Prettier for formatting
   - Jest for testing
   - Playwright for E2E tests

2. **Backend**
   - Mypy for type checking
   - Ruff for linting
   - Black for formatting
   - Pytest for testing
   - Coverage.py for test coverage

### CI/CD Integration

The build system is integrated with CI/CD:

1. **Continuous Integration**
   - Type checking
   - Linting
   - Unit tests
   - Integration tests
   - Build verification

2. **Continuous Deployment**
   - Version tagging
   - Artifact creation
   - Environment configuration
   - Deployment verification

### Best Practices

1. **Version Control**
   - Keep versions in sync
   - Use semantic versioning
   - Tag releases
   - Maintain changelog

2. **Dependency Management**
   - Regular updates
   - Security audits
   - Version constraints
   - Peer dependencies

3. **Build Process**
   - Fast feedback
   - Reproducible builds
   - Environment parity
   - Cache optimization

4. **Quality Assurance**
   - Automated testing
   - Code coverage
   - Performance metrics
   - Security scanning

## Recent Updates

### Service Layer Consolidation (February 2025)
- Consolidated rate services into `services/business/rates.py`
  - Combined basic rate operations and AI capabilities
  - Integrated rate card management
  - Added comprehensive rate analytics
- Reorganized tasks into domain-specific directories
  - Moved rate tasks to `services/business/tasks/rates.py`
  - Updated Celery configuration for new task locations
- Improved LLM integration
  - Streamlined rate optimization service
  - Enhanced market analysis capabilities
  - Added validation rules management

### API Structure Improvements
- Consolidated all rate-related endpoints under `/api/v1/rate-cards`
- Updated service dependencies for better maintainability
- Improved error handling and validation
- Added comprehensive request logging

### Schema Organization
- Reorganized schemas by domain:
  - `rate/`: Rate and optimization schemas
  - `quote/`: Quote-related schemas
  - `user/`: User and authentication schemas

### Documentation Updates
- Updated ARCHITECTURE.md with:
  - Detailed service layer organization
  - API endpoint documentation
  - Data flow diagrams
  - Development guidelines
- Added comprehensive API documentation
- Updated development setup instructions

For detailed information about the service layer organization and API structure, please refer to [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start services:
```bash
# Start Redis for Celery
redis-server

# Start Celery worker
celery -A app.core.tasks.celery worker --loglevel=info

# Start FastAPI server
uvicorn app.main:app --reload
```

4. Access the API:
- API Documentation: http://localhost:8000/docs
- Admin Interface: http://localhost:8000/admin

## Development Guidelines

1. Code Organization:
   - Keep business logic in service layer
   - Use repositories for data access
   - Follow clean architecture principles

2. Testing:
   - Write unit tests for all new features
   - Run tests before committing: `pytest`
   - Maintain test coverage above 80%

3. Documentation:
   - Update ARCHITECTURE.md for structural changes
   - Document all new API endpoints
   - Keep README.md current with major updates

## Code Health Analysis

Latest analysis (2025-02-25) shows the following areas need attention:

### 1. Test Code Organization (High Priority)
- **Issue**: Significant code duplication across test files
- **Affected Areas**:
  - Integration tests (`tests/integration/`)
  - API tests (`tests/api/`)
  - Rate calculator tests (`tests/rate_calculator/`)
- **Recommendations**:
  - Create shared test fixtures in `tests/conftest.py`
  - Extract common test utilities to `tests/utils/`
  - Standardize test setup patterns across modules

### 2. Model Layer Optimization (High Priority)
- **Issue**: Duplication in model implementations
- **Affected Files**:
  - `warehouse_quote_app/app/models/base.py`
  - `warehouse_quote_app/app/models/customer.py`
  - `warehouse_quote_app/app/models/quote.py`
  - `warehouse_quote_app/app/models/rate.py`
- **Recommendations**:
  - Extract common fields to base classes
  - Create mixins for shared behaviors (e.g., tracking fields)
  - Standardize relationship definitions

### 3. Code Divergence (Medium Priority)
- **Issue**: High divergence rate (61.27%) indicating inconsistent patterns
- **Key Areas**:
  - Test initialization files
  - API endpoint implementations
- **Recommendations**:
  - Standardize test organization
  - Create consistent patterns for endpoint implementations
  - Document and enforce architectural decisions

### Next Steps

1. **Test Framework Cleanup**
   - Create shared test fixtures
   - Document testing patterns
   - Review and consolidate duplicate test code

2. **Model Layer Refactoring**
   - Review model inheritance hierarchy
   - Extract common functionality
   - Update documentation

3. **Code Standards**
   - Document architectural decisions
   - Create style guides
   - Set up automated checks

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for system design and dependencies.
See [MIGRATION.md](./docs/MIGRATION.md) for detailed progress and next steps.

## Scripts

The project includes various utility scripts in the `scripts/` directory:

### Database Scripts

Located in `scripts/db/`:
- `add_rate_card.py`: Add new rate cards to the database
- `create_initial_rates.py`: Create initial rate structure
- `populate_rates.py`: Populate rates with default values
- `seed_rate_cards.py`: Seed rate cards with test data

### Test Scripts

Located in `scripts/`:
- `cleanup_test_artifacts.ps1`: Clean up test artifacts and reports

### Running Scripts

Use the script runner:

```powershell
# Run a script
.\run.ps1 -ScriptName <script-name>

# Available script names:
- add-rates
- create-rates
- populate-rates
- seed-rates
- cleanup-tests

# Example:
.\run.ps1 -ScriptName create-rates
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Frontend Documentation

For more detailed frontend documentation, see [Frontend Documentation](frontend/README.md)

## Backend Documentation

For more detailed backend documentation, see [Backend Documentation](warehouse_quote_app/README.md)

## API Documentation

For more detailed API documentation, see [API Documentation](docs/API.md)

## Areas for Streamlining and Improvement

Based on a recent architecture review, the following areas have been identified for streamlining and improvement:

- **Rate System - Missing Basic CRUD Operations:** Implement Create, Read, Update, Delete operations for rates to complete the rate management system.
- **OAuth Integration (Planned):** Implement OAuth to enhance security and user experience.
- **Caching:** Actively utilize Redis for caching frequently accessed data.
- **Monitoring and Alerting:** Implement a robust monitoring and alerting system (e.g., Sentry, Prometheus Alertmanager, Prometheus, Grafana).
- **Infrastructure as Code (IaC):** Adopt IaC practices using Terraform or similar tools.
- **CI/CD:** Implement a CI/CD pipeline using GitHub Actions or similar tools.
- **Shared Services:** Ensure that shared components are well-maintained and documented.
- **API Architecture:** Ensure that OpenAPI specification, versioned endpoints, rate limiting, and caching headers are fully implemented and documented.

For detailed information about the service layer organization and API structure, please refer to [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Latest Updates (2025-02-25)

### Code Health Improvements
- **Health Score**: 91.87% (↑10.35%)
- **Analysis Time**: 11.4 seconds (↓32.9s)
- **Key Metrics**:
  - Duplication Rate: 0.23%
  - Orphan Rate: 0.00%
  - Divergence Rate: 26.79%

### Major Changes
1. **Environment Cleanup**:
   - Consolidated virtual environments to single `.venv` in root
   - Removed duplicate `venv` directories

2. **Code Organization**:
   - Created new model mixins:
     - `TrackingMixin`: For metrics tracking
     - `PreferencesMixin`: For user preferences
     - `ContactInfoMixin`: For contact information
   - Created new API endpoint mixins:
     - `PaginationMixin`: For paginated endpoints
     - `QuoteFilterMixin`: For quote filtering
     - `CRUDMixin`: For common CRUD operations

3. **Testing Strategy**:
   - Shifted to knowledge graph-based bug detection
   - Manual UI testing for interface validation
   - Removed traditional test suite

### Next Steps
1. **Model Layer**:
   - Apply new mixins across remaining models
   - Standardize relationship definitions

2. **API Layer**:
   - Apply endpoint mixins to remaining endpoints
   - Standardize error handling

3. **Documentation**:
   - Update API documentation
   - Document new mixin usage

## Code Cleanup Initiative

The project is undergoing a systematic cleanup and optimization effort. This initiative focuses on:
- Reducing code complexity
- Eliminating redundancy
- Removing dead code
- Improving maintainability

### Cleanup Documentation
- [Cleanup Plan](docs/CLEANUP_PLAN.md): Detailed phased approach to code cleanup
- [High Severity Issues](high_severity_issues.md): Current critical issues being addressed
- [Implementation Details](docs/IMPLEMENTATION_CLEANUP.md): Technical details of the cleanup process

### Progress Tracking
The cleanup is being executed in phases:
1. **Phase 1** (In Progress): High-Severity Structural Issues
2. **Phase 2** (Planned): Critical Dead Code Removal
3. **Phase 3** (Planned): Code Duplication Consolidation
4. **Phase 4** (Planned): Medium and Low Severity Issues

For detailed progress and next steps, see the [Cleanup Plan](docs/CLEANUP_PLAN.md).

## Development Tools

The project includes a centralized development toolset:

### Quick Start

```powershell
# Setup development environment
.\run.ps1 setup

# Run all development tasks
.\run.ps1 all
```

### Available Commands

1. **Environment Setup**
   ```powershell
   .\run.ps1 setup -Target both
   ```

2. **Code Quality**
   ```powershell
   # Lint code
   .\run.ps1 lint

   # Format code
   .\run.ps1 format
   ```

3. **Testing**
   ```powershell
   # Run all tests
   .\run.ps1 test

   # Run frontend tests only
   .\run.ps1 test -Target frontend
   ```

4. **Building**
   ```powershell
   # Build for production
   .\run.ps1 build
   ```

For detailed development documentation, see [Development Tools Guide](scripts/dev/README.md).

## Development Scripts

The project includes various utility scripts in the `scripts/` directory:

### Database Scripts

Located in `scripts/db/`:
- `add_rate_card.py`: Add new rate cards to the database
- `create_initial_rates.py`: Create initial rate structure
- `populate_rates.py`: Populate rates with default values
- `seed_rate_cards.py`: Seed rate cards with test data

### Test Scripts

Located in `scripts/`:
- `cleanup_test_artifacts.ps1`: Clean up test artifacts and reports

### Running Scripts

Use the script runner:

```powershell
# Run a script
.\run.ps1 -ScriptName <script-name>

# Available script names:
- add-rates
- create-rates
- populate-rates
- seed-rates
- cleanup-tests

# Example:
.\run.ps1 -ScriptName create-rates
```

## Build System

The project uses a monorepo structure with centralized build configuration:

### Version Management

All packages in the monorepo share the same version (1.0.0) defined in:
- Root `package.json`
- Frontend `package.json`
- Backend `pyproject.toml`

### Package Management

1. **Frontend (Node.js)**
   ```json
   {
     "name": "aul-quote-app",
     "version": "1.0.0",
     "workspaces": [
       "frontend",
       "shared/*"
     ]
   }
   ```

2. **Backend (Python)**
   ```toml
   [project]
   name = "aul-quote-app"
   version = "1.0.0"
   requires-python = ">=3.9"
   ```

### Dependency Management

1. **Frontend Dependencies**
   - Managed through Yarn Workspaces
   - Shared dependencies in root `package.json`
   - Frontend-specific in `frontend/package.json`

2. **Backend Dependencies**
   - Managed through `pyproject.toml`
   - Development dependencies in `[project.optional-dependencies]`
   - Runtime dependencies in `[project.dependencies]`

### Build Scripts

1. **Frontend**
   ```bash
   # Development
   yarn start          # Start dev server
   yarn build         # Production build
   yarn test          # Run tests
   yarn lint          # Run linting
   yarn format        # Format code

   # Production
   yarn build         # Build for production
   yarn preview       # Preview production build
   ```

2. **Backend**
   ```bash
   # Development
   python -m pip install -e ".[dev]"  # Install with dev dependencies
   pytest                            # Run tests
   black .                          # Format code
   ruff check .                     # Run linting

   # Production
   python -m pip install .          # Install runtime dependencies
   uvicorn app.main:app            # Start server
   ```

### Quality Tools

1. **Frontend**
   - TypeScript for type checking
   - ESLint for linting
   - Prettier for formatting
   - Jest for testing
   - Playwright for E2E tests

2. **Backend**
   - Mypy for type checking
   - Ruff for linting
   - Black for formatting
   - Pytest for testing
   - Coverage.py for test coverage

### CI/CD Integration

The build system is integrated with CI/CD:

1. **Continuous Integration**
   - Type checking
   - Linting
   - Unit tests
   - Integration tests
   - Build verification

2. **Continuous Deployment**
   - Version tagging
   - Artifact creation
   - Environment configuration
   - Deployment verification

### Best Practices

1. **Version Control**
   - Keep versions in sync
   - Use semantic versioning
   - Tag releases
   - Maintain changelog

2. **Dependency Management**
   - Regular updates
   - Security audits
   - Version constraints
   - Peer dependencies

3. **Build Process**
   - Fast feedback
   - Reproducible builds
   - Environment parity
   - Cache optimization

4. **Quality Assurance**
   - Automated testing
   - Code coverage
   - Performance metrics
   - Security scanning

## Recent Updates

### Service Layer Consolidation (February 2025)
- Consolidated rate services into `services/business/rates.py`
  - Combined basic rate operations and AI capabilities
  - Integrated rate card management
  - Added comprehensive rate analytics
- Reorganized tasks into domain-specific directories
  - Moved rate tasks to `services/business/tasks/rates.py`
  - Updated Celery configuration for new task locations
- Improved LLM integration
  - Streamlined rate optimization service
  - Enhanced market analysis capabilities
  - Added validation rules management

### API Structure Improvements
- Consolidated all rate-related endpoints under `/api/v1/rate-cards`
- Updated service dependencies for better maintainability
- Improved error handling and validation
- Added comprehensive request logging

### Schema Organization
- Reorganized schemas by domain:
  - `rate/`: Rate and optimization schemas
  - `quote/`: Quote-related schemas
  - `user/`: User and authentication schemas

### Documentation Updates
- Updated ARCHITECTURE.md with:
  - Detailed service layer organization
  - API endpoint documentation
  - Data flow diagrams
  - Development guidelines
- Added comprehensive API documentation
- Updated development setup instructions

For detailed information about the service layer organization and API structure, please refer to [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start services:
```bash
# Start Redis for Celery
redis-server

# Start Celery worker
celery -A app.core.tasks.celery worker --loglevel=info

# Start FastAPI server
uvicorn app.main:app --reload
```

4. Access the API:
- API Documentation: http://localhost:8000/docs
- Admin Interface: http://localhost:8000/admin

## Development Guidelines

1. Code Organization:
   - Keep business logic in service layer
   - Use repositories for data access
   - Follow clean architecture principles

2. Testing:
   - Write unit tests for all new features
   - Run tests before committing: `pytest`
   - Maintain test coverage above 80%

3. Documentation:
   - Update ARCHITECTURE.md for structural changes
   - Document all new API endpoints
   - Keep README.md current with major updates

## Code Health Analysis

Latest analysis (2025-02-25) shows the following areas need attention:

### 1. Test Code Organization (High Priority)
- **Issue**: Significant code duplication across test files
- **Affected Areas**:
  - Integration tests (`tests/integration/`)
  - API tests (`tests/api/`)
  - Rate calculator tests (`tests/rate_calculator/`)
- **Recommendations**:
  - Create shared test fixtures in `tests/conftest.py`
  - Extract common test utilities to `tests/utils/`
  - Standardize test setup patterns across modules

### 2. Model Layer Optimization (High Priority)
- **Issue**: Duplication in model implementations
- **Affected Files**:
  - `warehouse_quote_app/app/models/base.py`
  - `warehouse_quote_app/app/models/customer.py`
  - `warehouse_quote_app/app/models/quote.py`
  - `warehouse_quote_app/app/models/rate.py`
- **Recommendations**:
  - Extract common fields to base classes
  - Create mixins for shared behaviors (e.g., tracking fields)
  - Standardize relationship definitions

### 3. Code Divergence (Medium Priority)
- **Issue**: High divergence rate (61.27%) indicating inconsistent patterns
- **Key Areas**:
  - Test initialization files
  - API endpoint implementations
- **Recommendations**:
  - Standardize test organization
  - Create consistent patterns for endpoint implementations
  - Document and enforce architectural decisions

### Next Steps

1. **Test Framework Cleanup**
   - Create shared test fixtures
   - Document testing patterns
   - Review and consolidate duplicate test code

2. **Model Layer Refactoring**
   - Review model inheritance hierarchy
   - Extract common functionality
   - Update documentation

3. **Code Standards**
   - Document architectural decisions
   - Create style guides
   - Set up automated checks

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for system design and dependencies.
See [MIGRATION.md](./docs/MIGRATION.md) for detailed progress and next steps.

## Scripts

The project includes various utility scripts in the `scripts/` directory:

### Database Scripts

Located in `scripts/db/`:
- `add_rate_card.py`: Add new rate cards to the database
- `create_initial_rates.py`: Create initial rate structure
- `populate_rates.py`: Populate rates with default values
- `seed_rate_cards.py`: Seed rate cards with test data

### Test Scripts

Located in `scripts/`:
- `cleanup_test_artifacts.ps1`: Clean up test artifacts and reports

### Running Scripts

Use the script runner:

```powershell
# Run a script
.\run.ps1 -ScriptName <script-name>

# Available script names:
- add-rates
- create-rates
- populate-rates
- seed-rates
- cleanup-tests

# Example:
.\run.ps1 -ScriptName create-rates
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Frontend Documentation

For more detailed frontend documentation, see [Frontend Documentation](frontend/README.md)

## Backend Documentation

For more detailed backend documentation, see [Backend Documentation](warehouse_quote_app/README.md)

## API Documentation

For more detailed API documentation, see [API Documentation](docs/API.md)

## Areas for Streamlining and Improvement

Based on a recent architecture review, the following areas have been identified for streamlining and improvement:

- **Rate System - Missing Basic CRUD Operations:** Implement Create, Read, Update, Delete operations for rates to complete the rate management system.
- **OAuth Integration (Planned):** Implement OAuth to enhance security and user experience.
- **Caching:** Actively utilize Redis for caching frequently accessed data.
- **Monitoring and Alerting:** Implement a robust monitoring and alerting system (e.g., Sentry, Prometheus Alertmanager, Prometheus, Grafana).
- **Infrastructure as Code (IaC):** Adopt IaC practices using Terraform or similar tools.
- **CI/CD:** Implement a CI/CD pipeline using GitHub Actions or similar tools.
- **Shared Services:** Ensure that shared components are well-maintained and documented.
- **API Architecture:** Ensure that OpenAPI specification, versioned endpoints, rate limiting, and caching headers are fully implemented and documented.

For detailed information about the service layer organization and API structure, please refer to [ARCHITECTURE.md](./docs/ARCHITECTURE.md).
