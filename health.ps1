# Sales CRM - Health Check Script
# Quick check of all services

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "              Sales CRM - Health Check                         " -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$allHealthy = $true

# Check if Docker is running
Write-Host "[DOCKER] Checking Docker..." -ForegroundColor Cyan
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker is not running!`n" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Docker is running`n" -ForegroundColor Green

# Check if containers are running
Write-Host "[CONTAINERS] Checking Docker containers..." -ForegroundColor Cyan
$containers = docker-compose ps --services --filter "status=running" 2>$null

if ($containers) {
    foreach ($container in $containers) {
        Write-Host "[OK] Container '$container' is running" -ForegroundColor Green
    }
    Write-Host ""
} else {
    Write-Host "[ERROR] No containers are running!" -ForegroundColor Red
    Write-Host "[INFO] Run '.\start.ps1' to start the services`n" -ForegroundColor Yellow
    exit 1
}

# Check Backend API
Write-Host "[BACKEND] Checking backend API..." -ForegroundColor Cyan
try {
    $backend = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
    if ($backend.status -eq "healthy") {
        Write-Host "[OK] Backend is healthy (v$($backend.version))" -ForegroundColor Green
        Write-Host "     URL: http://localhost:8000" -ForegroundColor Gray
        Write-Host "     Docs: http://localhost:8000/docs" -ForegroundColor Gray
    } else {
        Write-Host "[WARN] Backend responded but status is not healthy" -ForegroundColor Yellow
        $allHealthy = $false
    }
} catch {
    Write-Host "[ERROR] Backend is not responding!" -ForegroundColor Red
    Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Gray
    $allHealthy = $false
}
Write-Host ""

# Check Frontend
Write-Host "[FRONTEND] Checking frontend..." -ForegroundColor Cyan
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:5173" -Method Head -TimeoutSec 5 -ErrorAction Stop
    if ($frontend.StatusCode -eq 200) {
        Write-Host "[OK] Frontend is accessible" -ForegroundColor Green
        Write-Host "     URL: http://localhost:5173" -ForegroundColor Gray
    } else {
        Write-Host "[WARN] Frontend responded with status: $($frontend.StatusCode)" -ForegroundColor Yellow
        $allHealthy = $false
    }
} catch {
    Write-Host "[ERROR] Frontend is not responding!" -ForegroundColor Red
    Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Gray
    $allHealthy = $false
}
Write-Host ""

# Check Database
Write-Host "[DATABASE] Checking PostgreSQL..." -ForegroundColor Cyan
try {
    $dbCheck = docker exec sales-crm-db pg_isready -U postgres 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database is ready" -ForegroundColor Green
        Write-Host "     Host: localhost:5432" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Database is not ready!" -ForegroundColor Red
        $allHealthy = $false
    }
} catch {
    Write-Host "[ERROR] Cannot check database!" -ForegroundColor Red
    Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Gray
    $allHealthy = $false
}
Write-Host ""

# Test API endpoint
Write-Host "[API] Testing API endpoint..." -ForegroundColor Cyan
try {
    $apiTest = Invoke-RestMethod -Uri "http://localhost:8000/api/tenants" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] API endpoint /api/tenants is working" -ForegroundColor Green
    Write-Host "     Found $($apiTest.Count) tenant(s)" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] API endpoint failed!" -ForegroundColor Red
    Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Gray
    $allHealthy = $false
}
Write-Host ""

# Summary
Write-Host "================================================================" -ForegroundColor Cyan
if ($allHealthy) {
    Write-Host "              ALL SERVICES HEALTHY!                            " -ForegroundColor Green
    Write-Host "================================================================`n" -ForegroundColor Green
    Write-Host "[SUCCESS] All systems operational`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "              SOME SERVICES HAVE ISSUES                        " -ForegroundColor Yellow
    Write-Host "================================================================`n" -ForegroundColor Yellow
    Write-Host "[WARN] Check the errors above`n" -ForegroundColor Yellow
    Write-Host "Troubleshooting tips:" -ForegroundColor Cyan
    Write-Host "  1. Restart services: .\start.ps1" -ForegroundColor White
    Write-Host "  2. Check logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "  3. Rebuild: .\start.ps1 (choose option 2)`n" -ForegroundColor White
    exit 1
}

