# Check Database Script (No Poetry Required)
Write-Host "`n🔍 Checking Sales CRM Database...`n" -ForegroundColor Cyan

# Check if dependencies are installed
try {
    py -c "import rich" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
        py -m pip install rich sqlalchemy psycopg2-binary python-dotenv
        Write-Host ""
    }
} catch {
    Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
    py -m pip install rich sqlalchemy psycopg2-binary python-dotenv
    Write-Host ""
}

# Run the script
py tests\check_database.py

