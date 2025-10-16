# Leo音声データ一括変換スクリプト v2
# RVC学習用にm4a/mp4をWAV 48kHz 16bit モノラルへ変換
# 呼び出し演算子(&)を使用した確実な実行方式

param(
    [string]$SourceDir = "C:\Users\dokog\OneDrive\仕事\音声データ\Leo",
    [string]$OutputDir = "C:\Users\dokog\OneDrive\仕事\音声データ\Leo_Converted"
)

$ErrorActionPreference = "Continue"

# PATH環境変数を更新
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')

# ログディレクトリ作成
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$logDir = "tmp/cli/$ts"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = "$logDir/audio-conversion.log"

Write-Host "=== Leo音声データ一括変換開始 v2 ===" -ForegroundColor Cyan
"開始時刻: $(Get-Date)" | Out-File -FilePath $logFile -Encoding UTF8

# 出力ディレクトリ作成
if (!(Test-Path -Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    Write-Host "出力ディレクトリ作成: $OutputDir" -ForegroundColor Green
    "出力ディレクトリ作成: $OutputDir" | Out-File -FilePath $logFile -Append -Encoding UTF8
}

# 変換対象ファイル取得（m4a, mp4のみ、txtは除外）
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
        Write-Host "[$current/$($audioFiles.Count)] スキップ: $($file.Name) (既に存在)" -ForegroundColor Gray
        $skipCount++
        continue
    }
    
    Write-Host "[$current/$($audioFiles.Count)] 変換中: $($file.Name)" -ForegroundColor Yellow
    
    try {
        # ffmpegを呼び出し演算子(&)で直接実行
        $errorLog = "$logDir/error_$current.txt"
        
        & ffmpeg -i $file.FullName -ar 48000 -ac 1 -sample_fmt s16 -acodec pcm_s16le -y $outputFile 2> $errorLog
        
        if ($LASTEXITCODE -eq 0) {
            $successCount++
            Write-Host "  ✓ 成功: $($file.BaseName).wav" -ForegroundColor Green
            "成功: $($file.Name) -> $($file.BaseName).wav" | Out-File -FilePath $logFile -Append -Encoding UTF8
        } else {
            $failCount++
            Write-Host "  ✗ 失敗: $($file.Name) (ExitCode: $LASTEXITCODE)" -ForegroundColor Red
            "失敗: $($file.Name) (ExitCode: $LASTEXITCODE)" | Out-File -FilePath $logFile -Append -Encoding UTF8
            
            # エラー内容を記録
            if (Test-Path $errorLog) {
                $errContent = Get-Content $errorLog -Raw
                "エラー詳細: $errContent" | Out-File -FilePath $logFile -Append -Encoding UTF8
            }
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

Write-Host "ログファイル: $logFile" -ForegroundColor Gray
Write-Host "出力ディレクトリ: $OutputDir" -ForegroundColor Gray

# 変換後のファイル情報
if ($successCount -gt 0) {
    Write-Host "`n変換後のWAVファイル情報（先頭5件）:" -ForegroundColor Cyan
    $wavFiles = Get-ChildItem -Path $OutputDir -Filter "*.wav" | Select-Object -First 5 Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}
    $wavFiles | Format-Table -AutoSize
    
    $totalWav = (Get-ChildItem -Path $OutputDir -Filter "*.wav").Count
    if ($totalWav -gt 5) {
        Write-Host "... 他 $($totalWav - 5)ファイル（合計: $totalWav WAVファイル）" -ForegroundColor Gray
    }
}

# 失敗したファイルのリスト
if ($failCount -gt 0 -and $failCount -lt 20) {
    Write-Host "`n失敗したファイル:" -ForegroundColor Yellow
    $failedFiles = Get-Content $logFile | Select-String "失敗:" | ForEach-Object { $_.Line }
    $failedFiles | Select-Object -First 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
}
