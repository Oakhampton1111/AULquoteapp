# Root-level script to run development commands from anywhere
param (
    [Parameter(Mandatory=$true)]
    [ValidateSet(
        # Development commands
        'setup', 'lint', 'test', 'clean', 'build', 'format', 'all',
        # Database commands
        'db:seed', 'db:migrate', 'db:backup', 'db:restore',
        # Docker commands
        'docker:up', 'docker:down', 'docker:build',
        # Deployment commands
        'deploy:build', 'deploy:push', 'deploy:rollback'
    )]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('frontend', 'backend', 'both')]
    [string]$Target = 'both'
)

$ErrorActionPreference = 'Stop'
$rootDir = $PSScriptRoot

# Development commands
$devCommands = @('setup', 'lint', 'test', 'clean', 'build', 'format', 'all')
if ($Command -in $devCommands) {
    & "$rootDir\scripts\dev\dev-tools.ps1" -Command $Command -Target $Target
    exit $LASTEXITCODE
}

# Database commands
switch ($Command) {
    'db:seed' {
        & python "$rootDir\scripts\db\seed_rate_cards.py"
    }
    'db:migrate' {
        Write-Host "Running database migrations..."
        & alembic upgrade head
    }
    'db:backup' {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = "backup_${timestamp}.sql"
        Write-Host "Creating database backup: $backupFile"
        # Add your database backup command here
    }
    'db:restore' {
        Write-Host "Restoring database from backup..."
        # Add your database restore command here
    }
}

# Docker commands
switch ($Command) {
    'docker:up' {
        Write-Host "Starting Docker containers..."
        docker-compose up -d
    }
    'docker:down' {
        Write-Host "Stopping Docker containers..."
        docker-compose down
    }
    'docker:build' {
        Write-Host "Building Docker images..."
        docker-compose build
    }
}

# Deployment commands
switch ($Command) {
    'deploy:build' {
        Write-Host "Building for deployment..."
        & "$rootDir\scripts\deploy\build.ps1"
    }
    'deploy:push' {
        Write-Host "Pushing to deployment..."
        & "$rootDir\scripts\deploy\push.ps1"
    }
    'deploy:rollback' {
        Write-Host "Rolling back deployment..."
        & "$rootDir\scripts\deploy\rollback.ps1"
    }
}
