# API Keys Check Execution Wrapper (D-section compliant)
$ErrorActionPreference = "Stop"

# Log directory creation
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$logDir = "tmp/cli/$ts"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Execute check script (output to file)
$logFile = Join-Path $logDir "check-api-keys.out.txt"
& ".\check-api-keys.ps1" *> $logFile

# Display result
Get-Content -Raw $logFile
