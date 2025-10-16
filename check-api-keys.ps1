# API Keys Check Script (N-section compliant)
$ErrorActionPreference = "Continue"

Write-Host "=== API Keys Status Check ===" -ForegroundColor Cyan

$keys = @(
    'YOU_API_KEY',
    'TAVILY_API_KEY', 
    'PERPLEXITY_API_KEY',
    'PPLX_API_KEY'
)

$allSet = $true

foreach ($key in $keys) {
    $val = [Environment]::GetEnvironmentVariable($key, 'User')
    if ($val) {
        $len = $val.Length
        Write-Host "[OK] $key is set (length: $len)" -ForegroundColor Green
    } else {
        Write-Host "[MISSING] $key is not set" -ForegroundColor Yellow
        $allSet = $false
    }
}

Write-Host ""
if ($allSet) {
    Write-Host "All required API keys are set!" -ForegroundColor Green
} else {
    Write-Host "Some API keys are missing. Please set them according to N-section." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Required keys for tri-search.mjs:" -ForegroundColor Cyan
    Write-Host "  - YOU_API_KEY" -ForegroundColor White
    Write-Host "  - TAVILY_API_KEY" -ForegroundColor White
    Write-Host "  - PERPLEXITY_API_KEY (or PPLX_API_KEY)" -ForegroundColor White
}
