# Set API Keys to User Environment Variables (N-section compliant)
# WARNING: This script contains sensitive data. DO NOT commit to repository.
$ErrorActionPreference = "Stop"

Write-Host "=== Setting API Keys to User Environment Variables ===" -ForegroundColor Cyan
Write-Host ""

# API Keys from N-section (dontforgetthis.md)
$keys = @{
    'YOU_API_KEY' = '3ecbdb16-a7cd-4330-81f2-20e9249d1c3f<__>1RdYc0ETU8N2v5f42UQRQKSe'
    'TAVILY_API_KEY' = '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'
    'PERPLEXITY_API_KEY' = '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'
}

foreach ($key in $keys.Keys) {
    try {
        [Environment]::SetEnvironmentVariable($key, $keys[$key], 'User')
        Write-Host "[OK] $key has been set" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to set $key : $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "API keys have been set to User-level environment variables." -ForegroundColor Green
Write-Host "These keys are now available for tri-search.mjs" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Please restart your terminal/IDE for changes to take effect." -ForegroundColor Yellow
Write-Host "Or run: `$env:YOU_API_KEY = [Environment]::GetEnvironmentVariable('YOU_API_KEY', 'User')" -ForegroundColor Yellow
