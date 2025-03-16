# Testing Guide

## Overview

The AUL Quote App uses a comprehensive testing strategy with different types of tests:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete business flows
- **UI Tests**: Test frontend with Playwright
- **Rate Calculator Tests**: Test quote calculations
- **Auth Tests**: Test authentication system
- **AI Component Tests**: Test AI integration

## Project Structure

```
warehouse_quote_app/
├── app/                     # Backend code
│   ├── __init__.py
│   ├── auth/               # Auth module
│   │   └── __init__.py
│   ├── customer/           # Customer module
│   │   └── __init__.py
│   ├── quote/             # Quote module
│   │   └── __init__.py
│   └── rate/              # Rate module
│       └── __init__.py
├── tests/                  # Tests
│   ├── conftest.py              # Shared fixtures and configuration
│   ├── api/                     # API endpoint tests
│   │   ├── auth/               # Auth API tests
│   │   │   └── test_endpoints.py
│   │   ├── customer/           # Customer API tests
│   │   │   └── test_endpoints.py
│   │   ├── quote/             # Quote API tests
│   │   │   └── test_endpoints.py
│   │   └── rate/              # Rate API tests
│   │       └── test_endpoints.py
│   ├── e2e/                    # End-to-end tests
│   │   ├── test_auth_flow.py   # Authentication flow tests
│   │   ├── test_quote_flow.py  # Quote creation flow tests
│   │   └── test_admin_flow.py  # Admin operations tests
│   ├── integration/           # Integration tests
│   │   ├── test_auth.py       # Auth integration tests
│   │   ├── test_ai.py         # AI integration tests
│   │   ├── test_quotes.py     # Quote integration tests
│   │   └── test_rate_llm.py   # Rate LLM integration tests
│   ├── repositories/         # Repository tests
│   │   ├── quote/            # Quote repository tests
│   │   │   └── test_repository.py
│   │   └── rate/             # Rate repository tests
│   │       └── test_repository.py
│   ├── rate_calculator/       # Rate calculator tests
│   │   ├── core/             # Core calculator functionality
│   │   │   ├── test_calculations.py
│   │   │   └── test_setup.py
│   │   └── edge_cases/       # Edge case handling
│   │       └── test_cases.py
│   ├── ui/                    # UI tests with Playwright
│   │   ├── auth/              # Auth UI tests
│   │   │   ├── test_auth.py
│   │   │   └── test_login.py
│   │   ├── admin/             # Admin UI tests
│   │   │   └── test_admin.py
│   │   └── customer/          # Customer UI tests
│   │       └── test_quote.py
│   └── unit/                 # Unit tests
│       ├── auth/              # Auth unit tests
│       │   ├── test_service.py
│       │   └── test_users.py
│       ├── ai/                # AI component unit tests
│       ├── components/        # React component tests
│       ├── customer/          # Customer unit tests
│       │   └── test_service.py
│       ├── quote/            # Quote unit tests
│       │   └── test_service.py
│       ├── rate/             # Rate unit tests
│       │   ├── test_calculator.py
│       │   ├── test_cards.py
│       │   ├── test_components.py
│       │   ├── test_limit.py
│       │   ├── test_optimization.py
│       │   └── test_rates.py
│       └── services/         # Service layer tests
│           └── test_validation.py
├── frontend/                # Frontend code
│   ├── auth/              # Auth module
│   │   └── __init__.py
│   ├── customer/          # Customer module
│   │   └── __init__.py
│   └── quote/            # Quote module
│       └── __init__.py
└── run.ps1                 # Run script
```

## Testing Strategy

### Test Categories

#### 1. Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Focus on business logic
- Aim for high coverage

##### Key Areas
- Rate calculations
- Quote generation
- Data validation
- Authorization rules

#### 2. Integration Tests
- Test component interactions
- Database operations
- API endpoints
- External service integration

##### Key Flows
- Quote creation to approval
- Rate card updates
- Customer management
- Report generation

#### 3. End-to-End Tests
- Complete user workflows
- UI interaction
- Data persistence
- Email notifications

##### Critical Paths
- Quote lifecycle
- User authentication
- Payment processing
- Document generation

## Test Implementation

### 1. Testing Stack
- pytest for Python tests
- Jest for JavaScript tests
- Cypress for E2E tests
- pytest-cov for coverage

### 2. Test Data
- Factories for test data
- Fixtures for common scenarios
- Seed data for integration tests
- Clean up after tests

### 3. Mocking Strategy
- Mock external APIs
- Mock database calls in unit tests
- Mock file system operations
- Mock time-dependent operations

## Quality Gates

### 1. Coverage Requirements
- 90% coverage for business logic
- 80% coverage for API layer
- 70% coverage for UI components
- Critical paths must have 100%

### 2. Performance Tests
- Response time benchmarks
- Load testing scenarios
- Stress testing limits
- Resource usage monitoring

### 3. Security Tests
- Authentication tests
- Authorization tests
- Input validation
- SQL injection prevention

## Continuous Testing

### 1. CI Pipeline
- Run tests on every PR
- Block merges on test failures
- Report coverage changes
- Performance regression checks

### 2. Automated Testing
- Nightly full test suite
- Scheduled performance tests
- Regular security scans
- API contract tests

### 3. Test Monitoring
- Test execution metrics
- Coverage trends
- Failure patterns
- Performance trends

## Best Practices

### 1. Test Organization
- Follow AAA pattern
- One assertion per test
- Descriptive test names
- Proper test isolation

### 2. Test Maintenance
- Regular test review
- Remove flaky tests
- Update outdated tests
- Document test purposes

### 3. Test Environment
- Reproducible setup
- Clean state between tests
- Configurable test data
- Proper cleanup

## Specialized Testing

### 1. Rate Card Testing
- Edge case calculations
- Volume discount logic
- Special rate handling
- Rate card versioning

### 2. Quote Testing
- Quote calculation accuracy
- Approval workflow
- Document generation
- Version control

### 3. Report Testing
- Data aggregation
- Calculation accuracy
- Export functionality
- Large dataset handling

## Running Tests

### Backend Tests

Run all tests:
```bash
# Using pytest directly
pytest warehouse_quote_app/tests

# Using the run script (recommended)
.\run.ps1 -Command test -Target backend
```

Run specific test types:
```bash
# Core functionality tests
pytest warehouse_quote_app/tests/unit/          # Unit tests
pytest warehouse_quote_app/tests/integration/   # Integration tests
pytest warehouse_quote_app/tests/e2e/          # E2E tests

# Feature-specific tests
pytest -m rate_calculator  # Rate calculator tests
pytest -m ai               # AI component tests

# Test with coverage
pytest --cov=warehouse_quote_app/app --cov-report=html
```

### Frontend Tests

```bash
# Run all frontend tests
npm test

# Run specific test suites
npm test auth              # Auth tests
npm test quotes            # Quote tests
npm test ai                # AI tests

# Run E2E tests with Playwright
npm run test:e2e

# Run with coverage
npm test -- --coverage
```

## Test Categories

### 1. Authentication Tests
- Login flow
- Password reset
- Token management
- Role-based access
- Session handling
- Security measures

### 2. AI Component Tests
- Language model accuracy
- RAG system retrieval
- Memory management
- Context handling
- Rate validation
- Quote generation

### 3. Integration Tests
- API endpoints
- Database operations
- External services
- WebSocket connections
- File operations
- Cache management

### 4. UI Tests
- Component rendering
- User interactions
- Form validation
- Error handling
- Loading states
- Navigation flow

### 5. E2E Tests
- Complete user journeys
- Cross-component flows
- Data persistence
- Error scenarios
- Performance metrics

## Test Coverage Requirements

- Backend: Minimum 80% coverage
- Frontend: Minimum 70% coverage
- Critical paths: 100% coverage
- AI components: 90% coverage
- Auth system: 100% coverage

## Test Artifacts and Evidence

### Test Artifacts Directory (`tests/artifacts/`)
Test artifacts are temporary files generated during test execution. These are gitignored and should not be committed.

```
tests/artifacts/
├── api/           # API test artifacts
├── e2e/          # E2E test artifacts
├── integration/  # Integration test artifacts
├── ui/           # UI test artifacts
└── unit/         # Unit test artifacts
```

### Test Evidence Directory (`tests/evidence/`)
Test evidence includes permanent test results and reports that should be preserved.

```
tests/evidence/
├── coverage/     # Coverage reports
├── performance/  # Performance test results
├── security/     # Security test results
└── reports/      # Test execution reports
```

### Evidence Collection Guidelines

1. **Coverage Reports**
   - HTML coverage reports from pytest-cov
   - Frontend coverage reports from Jest
   - Consolidated coverage metrics

2. **Performance Reports**
   - Load test results
   - Response time metrics
   - Resource utilization data

3. **Security Reports**
   - Security scan results
   - Penetration test reports
   - Vulnerability assessments

4. **Test Reports**
   - Test execution summaries
   - Failure analysis reports
   - Regression test results

### Test Artifact Guidelines

1. **Temporary Files**
   - All files in `tests/artifacts/` are temporary
   - Cleaned up after test execution
   - Not committed to version control

2. **File Organization**
   - Group artifacts by test type
   - Use consistent naming conventions
   - Clean up after each test run

## Testing Best Practices

### 1. Test Organization
- Group related tests
- Clear test names
- Shared fixtures
- Clean setup/teardown
- Isolated test data

### 2. Test Quality
- Test one thing at a time
- Use meaningful assertions
- Mock external dependencies
- Handle async operations
- Clean test data

### 3. AI Testing
- Test model accuracy
- Validate outputs
- Check edge cases
- Monitor performance
- Test failure modes

### 4. Auth Testing
- Test security measures
- Validate token handling
- Check role enforcement
- Test error scenarios
- Monitor auth attempts

## Important Notes

1. **Project Structure**:
   - All backend code is in the `warehouse_quote_app/app` directory
   - Tests import from `warehouse_quote_app.app` package
   - Frontend code is in the `frontend` directory

2. **Test Database**:
   - Tests use SQLite for faster execution
   - Database URL: `sqlite+aiosqlite:///./test.db`
   - Automatically created and cleaned up

3. **API Paths**:
   - All API endpoints start with `/api`
   - Example: `/api/auth/login`, `/api/users/`

4. **Environment Variables**:
   - Set `TESTING=1` for test mode
   - Database URL configured in test fixtures
   - AI/LLM keys mocked in tests

5. **Running Tests**:
   - Use `run.ps1` script (recommended)
   - Or use pytest directly
   - Frontend tests use npm commands
