# Backend統合テストスクリプト（D-補遺準拠・出力ファイル保存）
# 実行: .\test-backend-integration.ps1

$ErrorActionPreference = "Continue"

# 出力ディレクトリ作成
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir = "tmp/cli/$ts"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Host "=== Backend Integration Test Started ===" -ForegroundColor Cyan
Write-Host "Output: $outDir" -ForegroundColor Gray
Write-Host ""

# テスト関数
function Test-API {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [string]$LogFile
    )
    
Write-Host "[$Name] Testing..." -ForegroundColor Yellow
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        $result = @{
            Success = $true
            StatusCode = $response.StatusCode
            Content = $response.Content
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
        
        $result | ConvertTo-Json -Depth 10 | Out-File -FilePath $LogFile -Encoding UTF8
        Write-Host "[$Name] OK (HTTP $($response.StatusCode))" -ForegroundColor Green
        return $true
    }
    catch {
        $result = @{
            Success = $false
            Error = $_.Exception.Message
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
        
        $result | ConvertTo-Json -Depth 10 | Out-File -FilePath $LogFile -Encoding UTF8
        Write-Host "[$Name] FAILED: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 1. AivisSpeech API Test
Write-Host "`n=== 1. AivisSpeech API Test ===" -ForegroundColor Cyan

# 1-1. Version check
$test1_1 = Test-API `
    -Name "AivisSpeech Version" `
    -Url "http://localhost:10101/version" `
    -LogFile "$outDir/01-aivisspeech-version.json"

# 1-2. Get speakers
$test1_2 = Test-API `
    -Name "AivisSpeech Speakers" `
    -Url "http://localhost:10101/speakers" `
    -LogFile "$outDir/02-aivisspeech-speakers.json"

# 1-3. Audio query
$test1_3 = Test-API `
    -Name "AivisSpeech Audio Query" `
    -Url "http://localhost:10101/audio_query?text=こんにちは&speaker=0" `
    -Method "POST" `
    -LogFile "$outDir/03-aivisspeech-audio-query.json"

# 2. RVC API Test
Write-Host "`n=== 2. RVC API Test ===" -ForegroundColor Cyan

# 2-1. Health check
$test2_1 = Test-API `
    -Name "RVC Health" `
    -Url "http://localhost:10102/health" `
    -LogFile "$outDir/04-rvc-health.json"

# 2-2. Get models
$test2_2 = Test-API `
    -Name "RVC Models" `
    -Url "http://localhost:10102/models" `
    -LogFile "$outDir/05-rvc-models.json"

# 3. Demucs API Test
Write-Host "`n=== 3. Demucs API Test ===" -ForegroundColor Cyan

# Note: Demucs is integrated as /separate endpoint, not /demucs/info
# 3-1. Check if /separate endpoint exists (without actual audio data)
Write-Host "[Demucs Endpoint Check] /separate endpoint existence check..." -ForegroundColor Yellow
$test3_1 = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:10102/separate" -Method POST -UseBasicParsing -ErrorAction Stop
    Write-Host "[Demucs Endpoint Check] Endpoint exists (expected: requires audio data)" -ForegroundColor Yellow
    $test3_1 = $true
} catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        # 422 Unprocessable Entity = endpoint exists but missing required data (expected)
        Write-Host "[Demucs Endpoint Check] OK (422 = endpoint exists, requires audio_base64)" -ForegroundColor Green
        $test3_1 = $true
        $result = @{
            Success = $true
            StatusCode = 422
            Note = "Endpoint exists, requires audio_base64 parameter"
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
        $result | ConvertTo-Json -Depth 10 | Out-File -FilePath "$outDir/06-demucs-separate-check.json" -Encoding UTF8
    } else {
        Write-Host "[Demucs Endpoint Check] FAILED: $($_.Exception.Message)" -ForegroundColor Red
        $result = @{
            Success = $false
            Error = $_.Exception.Message
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
        $result | ConvertTo-Json -Depth 10 | Out-File -FilePath "$outDir/06-demucs-separate-check.json" -Encoding UTF8
    }
}

# 4. TTS -> RVC Pipeline Test
Write-Host "`n=== 4. TTS -> RVC Pipeline Test ===" -ForegroundColor Cyan
Write-Host "Note: Skipped (requires actual audio files)" -ForegroundColor Yellow
Write-Host "(Model load + voice conversion needs manual test)" -ForegroundColor Gray

# Test Results Summary
Write-Host "`n=== Test Results Summary ===" -ForegroundColor Cyan

$results = @{
    "1-1. AivisSpeech Version" = $test1_1
    "1-2. AivisSpeech Speakers" = $test1_2
    "1-3. AivisSpeech Audio Query" = $test1_3
    "2-1. RVC Health" = $test2_1
    "2-2. RVC Models" = $test2_2
    "3-1. Demucs /separate Endpoint" = $test3_1
}

$successCount = 0
$failCount = 0

foreach ($key in $results.Keys | Sort-Object) {
    $status = if ($results[$key]) { "OK"; $successCount++ } else { "FAILED"; $failCount++ }
    Write-Host "$key : $status"
}

Write-Host "`nSuccess: $successCount / Failed: $failCount / Total: $($successCount + $failCount)" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Yellow" })

# サマリをファイルに保存
$summary = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Success = $successCount
    Failed = $failCount
    Total = $successCount + $failCount
    Results = $results
    OutputDirectory = $outDir
}

$summary | ConvertTo-Json -Depth 10 | Out-File -FilePath "$outDir/summary.json" -Encoding UTF8

Write-Host "`nOutput files: $outDir" -ForegroundColor Gray
Write-Host "Summary: $outDir\summary.json" -ForegroundColor Gray
