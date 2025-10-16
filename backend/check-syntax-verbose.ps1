# Python syntax check with error output
$ErrorActionPreference = "Continue"

Write-Host "=== Python Syntax Check (Verbose) ===" -ForegroundColor Cyan

$files = @(
    "gateway/main.py",
    "gateway/models.py"
)

foreach ($file in $files) {
    Write-Host "`nChecking $file..." -ForegroundColor Yellow
    python -m py_compile $file
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK]" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Exit code: $LASTEXITCODE" -ForegroundColor Red
    }
}
