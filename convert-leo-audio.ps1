# Leo音声データ一括変換スクリプト
# RVC学習用にm4a/mp4をWAV 48kHz 16bit モノラルへ変換

param(
    [string]$SourceDir = "C:\Users\dokog\OneDrive\仕事\音声データ\Leo",
    [string]$OutputDir = "C:\Users\dokog\OneDrive\仕事\音声データ\Leo_Converted"
)

$ErrorActionPreference = "Continue"

# PATH環境変数を更新（ffmpegインストール後）
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')

# ログディレクトリ作成
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$logDir = "tmp/cli/$ts"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = "$logDir/audio-conversion.log"

Write-Host "=== Leo音声データ一括変換開始 ===" -ForegroundColor Cyan
"開始時刻: $(Get-Date)" | Tee-Object -FilePath $logFile

# 出力ディレクトリ作成
if (!(Test-Path -Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    Write-Host "出力ディレクトリ作成: $OutputDir" -ForegroundColor Green
    "出力ディレクトリ作成: $OutputDir" | Tee-Object -FilePath $logFile -Append
}

# 変換対象ファイル取得（m4a, mp4のみ）
$audioFiles = Get-ChildItem -Path $SourceDir -File -Include "*.m4a","*.mp4" -Recurse

Write-Host "変換対象: $($audioFiles.Count)ファイル" -ForegroundColor Yellow
"変換対象: $($audioFiles.Count)ファイル" | Tee-Object -FilePath $logFile -Append

# カウンター
$successCount = 0
$failCount = 0
$current = 0

foreach ($file in $audioFiles) {
    $current++
    $outputFile = Join-Path $OutputDir "$($file.BaseName).wav"
    
    Write-Host "[$current/$($audioFiles.Count)] 変換中: $($file.Name)" -ForegroundColor Gray
    
    try {
        # ffmpeg変換実行（スペース含むパスに対応）
        $inputPath = "`"$($file.FullName)`""
        $outputPath = "`"$outputFile`""
        
        $ffmpegCmd = "ffmpeg -i $inputPath -ar 48000 -ac 1 -sample_fmt s16 -acodec pcm_s16le -y $outputPath 2>`"$logDir/ffmpeg_error_$current.txt`""
        
        $process = Start-Process -FilePath "powershell" -ArgumentList "-NoProfile", "-Command", $ffmpegCmd -NoNewWindow -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            $successCount++
            Write-Host "  ✓ 成功: $($file.BaseName).wav" -ForegroundColor Green
            "成功: $($file.Name) -> $($file.BaseName).wav" | Tee-Object -FilePath $logFile -Append
        } else {
            $failCount++
            Write-Host "  ✗ 失敗: $($file.Name) (ExitCode: $($process.ExitCode))" -ForegroundColor Red
            "失敗: $($file.Name) (ExitCode: $($process.ExitCode))" | Tee-Object -FilePath $logFile -Append
        }
    } catch {
        $failCount++
        Write-Host "  ✗ エラー: $($_.Exception.Message)" -ForegroundColor Red
        "エラー: $($file.Name) - $($_.Exception.Message)" | Tee-Object -FilePath $logFile -Append
    }
}

# 結果サマリ
Write-Host "`n=== 変換完了 ===" -ForegroundColor Cyan
Write-Host "成功: $successCount / 失敗: $failCount / 合計: $($audioFiles.Count)" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Yellow" })

"" | Tee-Object -FilePath $logFile -Append
"=== 変換完了 ===" | Tee-Object -FilePath $logFile -Append
"成功: $successCount / 失敗: $failCount / 合計: $($audioFiles.Count)" | Tee-Object -FilePath $logFile -Append
"終了時刻: $(Get-Date)" | Tee-Object -FilePath $logFile -Append

Write-Host "ログファイル: $logFile" -ForegroundColor Gray
Write-Host "出力ディレクトリ: $OutputDir" -ForegroundColor Gray

# 変換後のファイル情報
if ($successCount -gt 0) {
    Write-Host "`n変換後のWAVファイル情報:" -ForegroundColor Cyan
    Get-ChildItem -Path $OutputDir -Filter "*.wav" | Select-Object -First 5 Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}} | Format-Table -AutoSize
    
    if ($successCount -gt 5) {
        Write-Host "... 他 $($successCount - 5)ファイル" -ForegroundColor Gray
    }
}
