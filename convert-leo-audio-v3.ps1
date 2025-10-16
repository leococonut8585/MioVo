# Leo音声データ一括変換スクリプト v3（最終版）
# RVC学習用にm4a/mp4をWAV 48kHz 16bit モノラルへ変換
# ffmpegフルパス使用で確実に実行

param(
    [string]$SourceDir = "C:\Users\dokog\OneDrive\仕事\音声データ\Leo",
    [string]$OutputDir = "C:\Users\dokog\OneDrive\仕事\音声データ\Leo_Converted"
)

$ErrorActionPreference = "Continue"

# ffmpegフルパス
$ffmpegPath = "C:\Users\dokog\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"

# ffmpegの存在確認
if (!(Test-Path $ffmpegPath)) {
    Write-Host "エラー: ffmpegが見つかりません: $ffmpegPath" -ForegroundColor Red
    exit 1
}

# ログディレクトリ作成
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$logDir = "tmp/cli/$ts"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = "$logDir/audio-conversion.log"

Write-Host "=== Leo音声データ一括変換開始 v3 ===" -ForegroundColor Cyan
"開始時刻: $(Get-Date)" | Out-File -FilePath $logFile -Encoding UTF8
"ffmpeg: $ffmpegPath" | Out-File -FilePath $logFile -Append -Encoding UTF8

# 出力ディレクトリ作成
if (!(Test-Path -Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    Write-Host "出力ディレクトリ作成: $OutputDir" -ForegroundColor Green
}

# 変換対象ファイル取得
$audioFiles = Get-ChildItem -Path $SourceDir -File | Where-Object { $_.Extension -in @('.m4a', '.mp4') }

Write-Host "変換対象: $($audioFiles.Count)ファイル" -ForegroundColor Yellow
"変換対象: $($audioFiles.Count)ファイル" | Out-File -FilePath $logFile -Append -Encoding UTF8

# カウンター
$successCount = 0
$failCount = 0
$skipCount = 0
$current = 0

foreach ($file in $audioFiles) {
    $current++
    $outputFile = Join-Path $OutputDir "$($file.BaseName).wav"
    
    # 既に変換済みならスキップ
    if (Test-Path $outputFile) {
        Write-Host "[$current/$($audioFiles.Count)] スキップ: $($file.Name)" -ForegroundColor DarkGray
        $skipCount++
        continue
    }
    
    Write-Host "[$current/$($audioFiles.Count)] 変換中: $($file.Name)" -ForegroundColor Gray
    
    try {
        # ffmpegフルパスで実行
        $errorLog = "$logDir/error_$current.txt"
        
        & $ffmpegPath -i $file.FullName -ar 48000 -ac 1 -sample_fmt s16 -acodec pcm_s16le -y $outputFile 2> $errorLog
        
        if ($LASTEXITCODE -eq 0 -and (Test-Path $outputFile)) {
            $successCount++
            Write-Host "  ✓ 成功" -ForegroundColor Green
            "成功: $($file.Name)" | Out-File -FilePath $logFile -Append -Encoding UTF8
        } else {
            $failCount++
            Write-Host "  ✗ 失敗 (ExitCode: $LASTEXITCODE)" -ForegroundColor Red
            "失敗: $($file.Name) (ExitCode: $LASTEXITCODE)" | Out-File -FilePath $logFile -Append -Encoding UTF8
        }
    } catch {
        $failCount++
        Write-Host "  ✗ エラー: $($_.Exception.Message)" -ForegroundColor Red
        "エラー: $($file.Name) - $($_.Exception.Message)" | Out-File -FilePath $logFile -Append -Encoding UTF8
    }
}

# 結果サマリ
Write-Host "`n=== 変換完了 ===" -ForegroundColor Cyan
$statusColor = if ($failCount -eq 0) { "Green" } elseif ($successCount -gt 0) { "Yellow" } else { "Red" }
Write-Host "成功: $successCount / 失敗: $failCount / スキップ: $skipCount / 合計: $($audioFiles.Count)" -ForegroundColor $statusColor

"" | Out-File -FilePath $logFile -Append -Encoding UTF8
"=== 変換完了 ===" | Out-File -FilePath $logFile -Append -Encoding UTF8
"成功: $successCount / 失敗: $failCount / スキップ: $skipCount / 合計: $($audioFiles.Count)" | Out-File -FilePath $logFile -Append -Encoding UTF8
"終了時刻: $(Get-Date)" | Out-File -FilePath $logFile -Append -Encoding UTF8

Write-Host "`nログファイル: $logFile" -ForegroundColor Gray
Write-Host "出力ディレクトリ: $OutputDir" -ForegroundColor Gray

# 変換後のファイル情報
$wavFiles = Get-ChildItem -Path $OutputDir -Filter "*.wav"
if ($wavFiles.Count -gt 0) {
    Write-Host "`n変換済みWAVファイル: $($wavFiles.Count)個" -ForegroundColor Cyan
    $totalSize = ($wavFiles | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "合計サイズ: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
    
    Write-Host "`n先頭5件:" -ForegroundColor Gray
    $wavFiles | Select-Object -First 5 Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}} | Format-Table -AutoSize
}
