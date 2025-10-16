# Leo音声データ変換計画

## 日時
2025-10-16 19:23

## 現状
- **総ファイル数**: 221ファイル
- **形式**: m4a (218), mp4 (21), wav (1), txt (3)
- **ソースディレクトリ**: `C:\Users\dokog\OneDrive\仕事\音声データ\Leo`

## 目標仕様（RVC学習最適化）
- **形式**: WAV（無圧縮）
- **サンプリングレート**: 48000 Hz
- **ビットデプス**: 16bit
- **チャンネル**: モノラル (1ch)
- **品質**: ノイズ除去、空白最小化

## 変換手順
1. 出力ディレクトリ作成: `C:\Users\dokog\OneDrive\仕事\音声データ\Leo_Converted`
2. ffmpegで一括変換
3. 変換結果検証
4. RVC学習用データセット準備

## ffmpeg変換コマンド
```powershell
ffmpeg -i input.m4a -ar 48000 -ac 1 -sample_fmt s16 -acodec pcm_s16le output.wav
```

### パラメータ説明
- `-ar 48000`: サンプリングレート48kHz
- `-ac 1`: モノラル変換
- `-sample_fmt s16`: 16bitサンプル形式
- `-acodec pcm_s16le`: PCM 16bit little-endian

## 参考文献
- Zenn.dev "うさぎでもわかるRVC" (2025-10-16)
- neggly.org "RVC でモデル作成" (2024-11-28)
- child-programmer.com "RVC WebUI v2" (2025-01-07)

## ステータス
- [x] ffmpegインストール完了
- [ ] 出力ディレクトリ作成
- [ ] 一括変換スクリプト作成
- [ ] 変換実行
- [ ] 結果検証
