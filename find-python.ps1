# Find Python 3.11 installation
$ErrorActionPreference = "Continue"

Write-Host "=== Searching for Python 3.11 Installation ===" -ForegroundColor Cyan
Write-Host ""

$searchPaths = @(
    "C:\Python311\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python3.11\python.exe"
)

$found = $false

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        Write-Host "[FOUND] $path" -ForegroundColor Green
        & $path --version
        $found = $true
        break
    }
}

if (-not $found) {
    Write-Host "[NOT FOUND] Python 3.11 not found in standard locations" -ForegroundColor Yellow
    Write-Host "Checking PATH..." -ForegroundColor Cyan
    
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        Write-Host "Python in PATH: $($pythonCmd.Source)" -ForegroundColor Cyan
        & python --version
    }
}
