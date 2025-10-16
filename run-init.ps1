# Memory Bank初期化実行ラッパー（D-補遺準拠）
$ErrorActionPreference = "Stop"

# ログディレクトリ作成
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$logDir = "tmp/cli/$ts"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# 初期化スクリプト実行（出力をファイルへ）
$logFile = Join-Path $logDir "init-memory-bank.out.txt"
& ".\init-memory-bank.ps1" *> $logFile

# 結果表示
Get-Content -Raw $logFile
