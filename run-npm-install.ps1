# npm install execution wrapper (D-section compliant)
$ErrorActionPreference = "Stop"

Write-Host "=== MioVo Dependencies Installation ===" -ForegroundColor Cyan
Write-Host ""

# Create log directory
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$logDir = "tmp/cli/$ts"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Log file path
$logFile = Join-Path $logDir "npm-install.out.txt"

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
Write-Host "This may take several minutes. Please wait..." -ForegroundColor Yellow
Write-Host ""

# Run npm install (output to file)
npm install *> $logFile 2>&1

# Display summary
Write-Host "=== Installation Output (First 50 lines) ===" -ForegroundColor Cyan
Get-Content $logFile | Select-Object -First 50

Write-Host ""
Write-Host "... (full log saved to $logFile) ..." -ForegroundColor Gray
Write-Host ""

Write-Host "=== Installation Output (Last 20 lines) ===" -ForegroundColor Cyan
Get-Content $logFile | Select-Object -Last 20

Write-Host ""
Write-Host "Installation completed. Check log for details: $logFile" -ForegroundColor Green
