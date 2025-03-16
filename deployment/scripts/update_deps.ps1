# Update dependencies script
param(
    [string]$env = "all"
)

# Install pip-tools if not already installed
pip install pip-tools

# Function to compile requirements for a specific environment
function Update-Requirements {
    param(
        [string]$InputFile,
        [string]$OutputFile
    )
    Write-Host "Compiling requirements for $InputFile..."
    pip-compile --upgrade --generate-hashes --allow-unsafe --output-file $OutputFile $InputFile
}

# Set the requirements directory
$reqDir = Join-Path $PSScriptRoot ".." "requirements"

# Update based on environment parameter
switch ($env.ToLower()) {
    "base" {
        Update-Requirements -InputFile "$reqDir\base.in" -OutputFile "$reqDir\base.txt"
    }
    "dev" {
        Update-Requirements -InputFile "$reqDir\dev.in" -OutputFile "$reqDir\dev.txt"
    }
    "ml" {
        Update-Requirements -InputFile "$reqDir\ml.in" -OutputFile "$reqDir\ml.txt"
    }
    "prod" {
        Update-Requirements -InputFile "$reqDir\prod.in" -OutputFile "$reqDir\prod.txt"
    }
    "all" {
        Update-Requirements -InputFile "$reqDir\base.in" -OutputFile "$reqDir\base.txt"
        Update-Requirements -InputFile "$reqDir\dev.in" -OutputFile "$reqDir\dev.txt"
        Update-Requirements -InputFile "$reqDir\ml.in" -OutputFile "$reqDir\ml.txt"
        Update-Requirements -InputFile "$reqDir\prod.in" -OutputFile "$reqDir\prod.txt"
    }
    default {
        Write-Host "Invalid environment. Use: base, dev, ml, prod, or all"
        exit 1
    }
}

Write-Host "Requirements update complete!"
