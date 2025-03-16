# Development Tools

This directory contains scripts for development tasks.

## Main Development Script

The `dev-tools.ps1` script centralizes all development tasks for both frontend and backend:

```powershell
# Setup development environment
.\dev-tools.ps1 -Command setup -Target both

# Run linting
.\dev-tools.ps1 -Command lint -Target both

# Run tests
.\dev-tools.ps1 -Command test -Target both

# Clean build artifacts
.\dev-tools.ps1 -Command clean -Target both

# Build for production
.\dev-tools.ps1 -Command build -Target both

# Format code
.\dev-tools.ps1 -Command format -Target both

# Run all tasks
.\dev-tools.ps1 -Command all -Target both
```

### Targeting Specific Parts

You can target specific parts of the application:

```powershell
# Frontend only
.\dev-tools.ps1 -Command lint -Target frontend

# Backend only
.\dev-tools.ps1 -Command test -Target backend
```

### Available Commands

1. `setup`: Install dependencies and set up development environment
2. `lint`: Run code linting
3. `test`: Run tests
4. `clean`: Clean build artifacts
5. `build`: Build for production
6. `format`: Format code
7. `all`: Run all tasks (lint, test, build)

### Available Targets

1. `frontend`: Frontend only
2. `backend`: Backend only
3. `both`: Both frontend and backend (default)

## Individual Tools

The script integrates the following tools:

### Frontend

- ESLint for linting
- Prettier for formatting
- Jest for testing
- Playwright for E2E tests
- TypeScript for type checking

### Backend

- Black for formatting
- isort for import sorting
- mypy for type checking
- ruff for linting
- pytest for testing

## Guidelines

1. Always run linting before committing
2. Ensure all tests pass
3. Format code consistently
4. Keep dependencies up to date
5. Document new development tasks
