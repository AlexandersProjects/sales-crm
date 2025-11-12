# Sales CRM - Complete Start Script
# Handles Docker cleanup, build, and startup

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "              Sales CRM - Starting Up                          " -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# Check if .env exists
if (!(Test-Path .env)) {
    Write-Host "[CONFIG] Creating .env file from example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "[OK] Created .env file`n" -ForegroundColor Green
    Write-Host "[INFO] To use AI features, edit .env and add your OpenAI API key`n" -ForegroundColor Yellow
}

# Check Docker
Write-Host "[DOCKER] Checking Docker..." -ForegroundColor Cyan
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again.`n" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Docker is running`n" -ForegroundColor Green

# Ask user what to do
Write-Host "Choose startup mode:" -ForegroundColor Cyan
Write-Host "  1. Quick start (restart existing containers)" -ForegroundColor White
Write-Host "  2. Clean rebuild (recommended for first time or after changes)" -ForegroundColor White
Write-Host "  3. Reset everything (removes database data)`n" -ForegroundColor White

$choice = Read-Host "Enter choice (1-3, default: 1)"
if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }

switch ($choice) {
    "1" {
        Write-Host "`n[START] Quick start mode...`n" -ForegroundColor Green
        docker-compose up -d
    }
    "2" {
        Write-Host "`n[REBUILD] Clean rebuild mode...`n" -ForegroundColor Yellow
        Write-Host "Stopping containers..." -ForegroundColor Cyan
        docker-compose down

        Write-Host "Building fresh images..." -ForegroundColor Cyan
        docker-compose build --no-cache

        Write-Host "Starting services..." -ForegroundColor Cyan
        docker-compose up -d
    }
    "3" {
        Write-Host "`n[WARNING] RESET MODE - This will delete all data!`n" -ForegroundColor Red
        $confirm = Read-Host "Are you sure? (yes/no)"
        if ($confirm -eq "yes") {
            Write-Host "Stopping and removing everything..." -ForegroundColor Yellow
            docker-compose down -v

            Write-Host "Rebuilding..." -ForegroundColor Cyan
            docker-compose build --no-cache

            Write-Host "Starting fresh..." -ForegroundColor Cyan
            docker-compose up -d
        } else {
            Write-Host "Cancelled.`n" -ForegroundColor Yellow
            exit 0
        }
    }
    default {
        Write-Host "Invalid choice. Defaulting to quick start...`n" -ForegroundColor Yellow
        docker-compose up -d
    }
}

# Wait for services to be ready
Write-Host "`n[WAIT] Waiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check if services are running
Write-Host "`n[STATUS] Service Status:" -ForegroundColor Cyan
docker-compose ps

# Display access URLs
Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "                  Sales CRM Ready!                             " -ForegroundColor Green
Write-Host "================================================================`n" -ForegroundColor Green

Write-Host "[WEB] Access your application:" -ForegroundColor Cyan
Write-Host "   - Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "   - API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Backend:   http://localhost:8000`n" -ForegroundColor White

Write-Host "[HELP] Useful commands:" -ForegroundColor Cyan
Write-Host "   - View logs:     docker-compose logs -f" -ForegroundColor White
Write-Host "   - Stop services: docker-compose down" -ForegroundColor White
Write-Host "   - Restart:       docker-compose restart" -ForegroundColor White
Write-Host "   - Check DB:      py tests\check_database.py`n" -ForegroundColor White

Write-Host "[BROWSER] Opening frontend in browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"

Write-Host "`nHappy coding!`n" -ForegroundColor Green
