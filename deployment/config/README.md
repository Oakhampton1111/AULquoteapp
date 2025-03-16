# Configuration Management

This directory contains all environment and configuration files for the AUL Quote App.

## Structure

```
config/
├── .env            # Main environment file (gitignored)
├── .env.example    # Example configuration template
├── .env.template   # Base template for new environments
├── development/    # Development environment configs
│   ├── backend.env # Backend development settings
│   └── frontend.env# Frontend development settings
├── production/     # Production environment configs
│   ├── backend.env # Backend production settings
│   └── frontend.env# Frontend production settings
├── staging/        # Staging environment configs
│   ├── backend.env # Backend staging settings
│   └── frontend.env# Frontend staging settings
└── shared/        # Shared configuration
    ├── ai.env     # AI/LLM configuration
    ├── db.env     # Database configuration
    └── rag.env    # RAG system configuration
```

## Configuration Hierarchy

1. Base Configuration:
   - `.env`: Main configuration file
   - Contains essential settings
   - Environment-specific values are overridden

2. Environment-Specific:
   - Located in `development/`, `staging/`, or `production/`
   - Override base configuration
   - Environment-specific optimizations

3. Shared Configuration:
   - Located in `shared/`
   - Component-specific settings
   - Consistent across environments

## Setup Instructions

1. Initial Setup:
   ```bash
   # Copy example configuration
   cp .env.example .env
   
   # Update with your settings
   nano .env
   ```

2. Environment Configuration:
   ```bash
   # Development
   cp development/backend.env.example development/backend.env
   
   # Production
   cp production/backend.env.example production/backend.env
   ```

3. Shared Configuration:
   - Review and update shared/*.env files
   - Maintain consistent settings across environments

## Configuration Guidelines

1. Security:
   - Never commit sensitive values
   - Use environment variables for secrets
   - Rotate sensitive values regularly
   - Use strong passwords and keys

2. Environment Variables:
   - Use clear, descriptive names
   - Document all variables
   - Group related settings
   - Include validation rules

3. Maintenance:
   - Regular audits of configurations
   - Remove unused variables
   - Keep documentation current
   - Test configuration changes

4. Best Practices:
   - Use appropriate data types
   - Include default values
   - Document dependencies
   - Follow naming conventions

## Validation Rules

1. Database Settings:
   - Valid connection strings
   - Appropriate pool sizes
   - Reasonable timeouts
   - Proper permissions

2. Security Settings:
   - Strong secret keys
   - Appropriate token expiry
   - Valid CORS origins
   - Rate limiting rules

3. Feature Flags:
   - Clear naming
   - Default values
   - Documentation
   - Testing impact

## Environment Variables

1. Core Settings:
   ```ini
   APP_ENV=development
   APP_NAME=AUL Quote App
   DEBUG=true
   ```

2. Database Settings:
   ```ini
   POSTGRES_HOST=localhost
   POSTGRES_DB=warehouse_quotes
   DB_POOL_SIZE=5
   ```

3. Security Settings:
   ```ini
   SECRET_KEY=your-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## Troubleshooting

1. Common Issues:
   - Missing environment files
   - Invalid configuration values
   - Permission problems
   - Path issues

2. Validation:
   - Check file permissions
   - Verify environment values
   - Test configuration loading
   - Check log files

3. Updates:
   - Document changes
   - Test in development
   - Backup configurations
   - Monitor impacts
