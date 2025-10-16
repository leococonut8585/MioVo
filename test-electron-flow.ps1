# Electron統合テストフロー（D-補遺準拠・出力ファイル保存）
# 実行: .\test-electron-flow.ps1

$ErrorActionPreference = "Continue"

# 出力ディレクトリ作成
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir = "tmp/cli/$ts"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Host "=== Electron Integration Test Flow Started ===" -ForegroundColor Cyan
Write-Host "Output: $outDir" -ForegroundColor Gray
Write-Host ""

# ステップ1: サーバー起動確認
Write-Host "`n=== Step 1: Server Status Check ===" -ForegroundColor Cyan

# Docker containers
Write-Host "[Docker] Checking containers..." -ForegroundColor Yellow
docker ps -a --filter "name=miovo" *> "$outDir/01-docker-status.txt"
Get-Content "$outDir/01-docker-status.txt"

$containersRunning = docker ps --filter "name=miovo" --format "{{.Names}}" | Measure-Object -Line
if ($containersRunning.Lines -ge 2) {
    Write-Host "[Docker] OK: Both containers are running" -ForegroundColor Green
} else {
    Write-Host "[Docker] WARNING: Some containers may not be running" -ForegroundColor Yellow
}

# ステップ2: Vite Dev Server起動確認
Write-Host "`n=== Step 2: Vite Dev Server Check ===" -ForegroundColor Cyan

Write-Host "[Vite] Checking if dev server is running on http://localhost:5173" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -Method GET -UseBasicParsing -TimeoutSec 5
    $result = @{
        Success = $true
        StatusCode = $response.StatusCode
        ContentLength = $response.Content.Length
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    $result | ConvertTo-Json -Depth 10 | Out-File -FilePath "$outDir/02-vite-server.json" -Encoding UTF8
    Write-Host "[Vite] OK: Dev server is running (HTTP $($response.StatusCode))" -ForegroundColor Green
    $viteRunning = $true
} catch {
    $result = @{
        Success = $false
        Error = $_.Exception.Message
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    $result | ConvertTo-Json -Depth 10 | Out-File -FilePath "$outDir/02-vite-server.json" -Encoding UTF8
    Write-Host "[Vite] FAILED: Dev server not accessible - $($_.Exception.Message)" -ForegroundColor Red
    $viteRunning = $false
}

if (-not $viteRunning) {
    Write-Host "`n[ACTION REQUIRED] Starting Vite dev server..." -ForegroundColor Yellow
    Write-Host "Executing: npm run dev" -ForegroundColor Gray
    
    # D-補遺準拠: 出力をファイル保存
    $devLog = "$outDir/03-npm-run-dev.txt"
    Write-Host "Dev server output will be saved to: $devLog" -ForegroundColor Gray
    
    # バックグラウンドでnpm run devを起動し、出力をファイルに保存
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev *> '$devLog'" -WindowStyle Normal
    
    Write-Host "Waiting 15 seconds for dev server to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 15
    
    # 再確認
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5173" -Method GET -UseBasicParsing -TimeoutSec 5
        Write-Host "[Vite] OK: Dev server started successfully" -ForegroundColor Green
        $viteRunning = $true
    } catch {
        Write-Host "[Vite] FAILED: Dev server still not accessible after startup attempt" -ForegroundColor Red
        Write-Host "Check log file: $devLog" -ForegroundColor Yellow
    }
}

# ステップ3: Electronアプリ動作確認チェックリスト
Write-Host "`n=== Step 3: Electron App Manual Test Checklist ===" -ForegroundColor Cyan

$checklist = @"
Please perform the following manual tests:

[ ] 1. UI Display Test
    - Open browser: http://localhost:5173
    - Check if the main UI loads correctly
    - Verify Tailwind CSS styles are applied
    - Check for console errors (F12)

[ ] 2. Mode Switch Test (朗読/歌唱)
    - Test switching between Reading Mode and Singing Mode
    - Verify mode-specific UI components appear correctly
    - Check animation smoothness (Motion library)

[ ] 3. Timeline Editor Test
    - Test timeline component interaction
    - Check keyboard shortcuts (Arrow keys, Space, Number keys)
    - Verify drag & drop functionality (if applicable)

[ ] 4. Reduced Motion Test
    - Check if useReducedMotion() is working
    - Verify accessibility features (ARIA labels, focus-visible)

[ ] 5. Backend Integration Test (Optional)
    - Test AivisSpeech TTS generation (requires manual input)
    - Test RVC voice conversion (requires audio file)
    - Test Demucs vocal separation (requires audio file)

Save results to: $outDir/04-manual-test-results.txt
"@

$checklist | Out-File -FilePath "$outDir/04-manual-test-checklist.txt" -Encoding UTF8
Write-Host $checklist

# サマリ
Write-Host "`n=== Test Flow Summary ===" -ForegroundColor Cyan

$summary = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    DockerContainersRunning = ($containersRunning.Lines -ge 2)
    ViteDevServerRunning = $viteRunning
    ManualTestsRequired = $true
    OutputDirectory = $outDir
    NextSteps = @(
        "1. Open browser: http://localhost:5173"
        "2. Perform manual tests from checklist"
        "3. Save test results to: $outDir/04-manual-test-results.txt"
    )
}

$summary | ConvertTo-Json -Depth 10 | Out-File -FilePath "$outDir/summary.json" -Encoding UTF8

Write-Host "Docker Containers: $(if ($containersRunning.Lines -ge 2) { 'Running' } else { 'Incomplete' })" -ForegroundColor $(if ($containersRunning.Lines -ge 2) { 'Green' } else { 'Yellow' })
Write-Host "Vite Dev Server: $(if ($viteRunning) { 'Running' } else { 'Not Running' })" -ForegroundColor $(if ($viteRunning) { 'Green' } else { 'Red' })
Write-Host "`nOutput files: $outDir" -ForegroundColor Gray
Write-Host "Summary: $outDir\summary.json" -ForegroundColor Gray
Write-Host "`nNext: Open http://localhost:5173 in browser for manual testing" -ForegroundColor Cyan
