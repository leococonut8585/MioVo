# Memory Bank Initialization Script (Q-section compliant)
$ErrorActionPreference = "Stop"

# Create memory-bank directory
if (!(Test-Path "memory-bank")) {
    New-Item -ItemType Directory -Path "memory-bank" | Out-Null
    Write-Host "[OK] memory-bank directory created"
}

# Required files list
$files = @(
    'projectbrief.md',
    'productContext.md',
    'techContext.md',
    'systemPatterns.md',
    'activeContext.md',
    'progress.md'
)

# Create files (preserve existing)
foreach ($f in $files) {
    $path = Join-Path "memory-bank" $f
    if (!(Test-Path $path)) {
        New-Item -ItemType File -Path $path | Out-Null
        Write-Host "[OK] $f created"
    } else {
        Write-Host "[SKIP] $f already exists"
    }
}

# Initialization marker
$initFile = "memory-bank\.initialized"
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Add-Content -Path $initFile -Value "initialized: $timestamp"
Write-Host "[OK] Initialization completed: $timestamp"
