# Python environment setup script (D-section compliant)
$ErrorActionPreference = "Stop"

Write-Host "=== Python Environment Setup ===" -ForegroundColor Cyan
Write-Host ""

# Create log directory
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$logDir = "..\tmp\cli\$ts"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Step 1: Create virtual environment
Write-Host "[1/3] Creating virtual environment..." -ForegroundColor Yellow
$venvLog = Join-Path $logDir "venv-create.log"
python -m venv .venv > $venvLog 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to create venv" -ForegroundColor Red
    Get-Content $venvLog
    exit 1
}

# Step 2: Activate and upgrade pip
Write-Host "[2/3] Upgrading pip..." -ForegroundColor Yellow
$pipLog = Join-Path $logDir "pip-upgrade.log"
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip > $pipLog 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] pip upgraded" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to upgrade pip" -ForegroundColor Red
    Get-Content $pipLog
}

# Step 3: Install requirements
Write-Host "[3/3] Installing requirements..." -ForegroundColor Yellow
Write-Host "  This may take several minutes..." -ForegroundColor Gray
$reqLog = Join-Path $logDir "requirements-install.log"
& ".\.venv\Scripts\pip.exe" install -r requirements.txt > $reqLog 2>&1

Write-Host ""
Write-Host "Installation output (last 30 lines):" -ForegroundColor Cyan
Get-Content $reqLog | Select-Object -Last 30

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Python environment setup completed!" -ForegroundColor Green
    Write-Host "Activate with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "[ERROR] Requirements installation failed" -ForegroundColor Red
    Write-Host "Check log: $reqLog" -ForegroundColor Yellow
}
