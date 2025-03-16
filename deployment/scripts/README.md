# Development Scripts

This directory contains scripts for development, deployment, and maintenance tasks.

## Structure

```
scripts/
├── db/           # Database management scripts
├── dev/          # Development utility scripts
├── deploy/       # Deployment scripts
└── docker/       # Docker utility scripts
```

## Database Scripts

Located in `scripts/db/`:

- `seed.py`: Seed database with initial data
- `migrate.py`: Run database migrations
- `backup.py`: Backup database
- `restore.py`: Restore database from backup
- `add_rate_card.py`: Add new rate cards
- `create_initial_rates.py`: Create initial rates
- `populate_rates.py`: Populate rate data
- `seed_rate_cards.py`: Seed rate card data

## Development Scripts

Located in `scripts/dev/`:

- `setup.py`: Set up development environment
- `lint.py`: Run linting
- `test.py`: Run tests
- `clean.py`: Clean build artifacts
- `generate_types.py`: Generate TypeScript types from Python models

## Deployment Scripts

Located in `scripts/deploy/`:

- `build.sh`: Build application
- `deploy.sh`: Deploy application
- `rollback.sh`: Rollback deployment
- `health_check.sh`: Check deployment health

## Docker Scripts

Located in `scripts/docker/`:

- `build.sh`: Build Docker images
- `start.sh`: Start Docker containers
- `stop.sh`: Stop Docker containers
- `wait-for-it.sh`: Wait for service availability

## Usage

Most scripts can be run directly from the command line:

```bash
# Database scripts
python scripts/db/seed.py
python scripts/db/migrate.py

# Development scripts
python scripts/dev/setup.py
python scripts/dev/lint.py

# Deployment scripts
./scripts/deploy/build.sh
./scripts/deploy/deploy.sh

# Docker scripts
./scripts/docker/build.sh
./scripts/docker/start.sh
```

## Guidelines

1. All scripts should:
   - Have clear documentation
   - Include error handling
   - Support --help flag
   - Be idempotent when possible
   - Log actions appropriately

2. Python scripts should:
   - Use argparse for CLI
   - Follow PEP 8
   - Include type hints
   - Have proper error handling

3. Shell scripts should:
   - Be POSIX compliant
   - Include proper error handling
   - Set appropriate permissions
   - Use shellcheck for linting
