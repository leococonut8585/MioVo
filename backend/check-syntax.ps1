# Python syntax check script
$ErrorActionPreference = "Continue"

Write-Host "=== Python Syntax Check ===" -ForegroundColor Cyan

$files = @(
    "gateway/main.py",
    "gateway/models.py",
    "gateway/routers/tts.py",
    "gateway/routers/rvc.py",
    "aivisspeech/client.py",
    "rvc/server.py"
)

$allOk = $true

foreach ($file in $files) {
    Write-Host "Checking $file..." -ForegroundColor Yellow
    python -m py_compile $file 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] $file" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""
if ($allOk) {
    Write-Host "All Python files passed syntax check!" -ForegroundColor Green
} else {
    Write-Host "Some files have syntax errors." -ForegroundColor Red
}
