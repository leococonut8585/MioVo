# Get npm install error log
$ErrorActionPreference = "Continue"

Write-Host "=== Checking npm install error log ===" -ForegroundColor Cyan

# Find latest log directory
$latestDir = Get-ChildItem "tmp/cli" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($latestDir) {
    $logFile = Join-Path $latestDir.FullName "npm-install.out.txt"
    
    if (Test-Path $logFile) {
        Write-Host "Log file found: $logFile" -ForegroundColor Green
        Write-Host ""
        Write-Host "=== Full Error Log ===" -ForegroundColor Yellow
        Get-Content $logFile
    } else {
        Write-Host "Log file not found at: $logFile" -ForegroundColor Red
    }
} else {
    Write-Host "No log directories found in tmp/cli" -ForegroundColor Red
}
