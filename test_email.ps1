# Test Email Generation Script (No Poetry Required)
Write-Host "`n📧 Testing Email Generation...`n" -ForegroundColor Cyan

# Check if dependencies are installed
try {
    py -c "import openai" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
        py -m pip install rich openai
        Write-Host ""
    }
} catch {
    Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
    py -m pip install rich openai
    Write-Host ""
}

# Run the script
py test_email_generation.py

