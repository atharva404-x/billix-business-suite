#!/usr/bin/env pwsh
# Helper to start the FastAPI backend reliably on Windows.
# It prefers a local .venv, then python, then py -3. If none found,
# it prints installation instructions.

$ErrorActionPreference = 'Stop'

# PSScriptRoot is the scripts directory; repo root is its parent
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "Using virtualenv python at $venvPython"
    & $venvPython -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Using python from PATH"
    & python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
    exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    Write-Host "Using py launcher"
    & py -3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
    exit $LASTEXITCODE
}

Write-Host "No Python executable found. Install Python and try again." -ForegroundColor Yellow
Write-Host "You can install Python using winget (Windows):" -ForegroundColor Yellow
Write-Host "  winget install --id=Python.Python.3 -e" -ForegroundColor Cyan
Write-Host "Or download from https://python.org and ensure 'python' is on PATH." -ForegroundColor Cyan
exit 1
