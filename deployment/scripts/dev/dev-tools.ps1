# Development Tools PowerShell Script

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet('setup', 'lint', 'test', 'clean', 'build', 'format', 'all')]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('frontend', 'backend', 'both')]
    [string]$Target = 'both'
)

$ErrorActionPreference = 'Stop'
$rootDir = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent

function Write-Header {
    param([string]$Message)
    Write-Host "`n=== $Message ===`n" -ForegroundColor Cyan
}

function Run-Frontend {
    param([string]$Script)
    Write-Header "Running Frontend: $Script"
    Push-Location "$rootDir\frontend"
    try {
        npm run $Script
    }
    finally {
        Pop-Location
    }
}

function Run-Backend {
    param([string]$Command)
    Write-Header "Running Backend: $Command"
    Push-Location $rootDir
    try {
        switch ($Command) {
            'lint' {
                python -m black .
                python -m isort .
                python -m mypy .
                python -m ruff check .
            }
            'test' {
                $env:PYTHONPATH = $rootDir
                python -m pytest tests/ --cov=warehouse_quote_app/app --cov-report=term-missing
            }
            'clean' {
                Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
                    *.pyc, __pycache__, .pytest_cache, .coverage, htmlcov, dist, build
            }
            'setup' {
                python -m pip install -e ".[dev]"
            }
            default {
                Write-Error "Unknown backend command: $Command"
            }
        }
    }
    finally {
        Pop-Location
    }
}

# Main execution
try {
    switch ($Command) {
        'setup' {
            if ($Target -in 'frontend','both') {
                Write-Header "Installing Frontend Dependencies"
                Push-Location "$rootDir\frontend"
                try { npm install } finally { Pop-Location }
            }
            if ($Target -in 'backend','both') {
                Run-Backend 'setup'
            }
        }
        'lint' {
            if ($Target -in 'frontend','both') { Run-Frontend 'lint' }
            if ($Target -in 'backend','both') { Run-Backend 'lint' }
        }
        'test' {
            if ($Target -in 'frontend','both') { Run-Frontend 'test' }
            if ($Target -in 'backend','both') { Run-Backend 'test' }
        }
        'clean' {
            if ($Target -in 'frontend','both') { Run-Frontend 'clean' }
            if ($Target -in 'backend','both') { Run-Backend 'clean' }
        }
        'build' {
            if ($Target -in 'frontend','both') { Run-Frontend 'build' }
        }
        'format' {
            if ($Target -in 'frontend','both') { Run-Frontend 'format' }
            if ($Target -in 'backend','both') { Run-Backend 'lint' }
        }
        'all' {
            Write-Header "Running All Development Tasks"
            & $PSCommandPath -Command 'lint' -Target $Target
            & $PSCommandPath -Command 'test' -Target $Target
            & $PSCommandPath -Command 'build' -Target $Target
        }
    }
}
catch {
    Write-Error "Error running command '$Command': $_"
    exit 1
}
