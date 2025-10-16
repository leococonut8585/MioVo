# ProjectMioVo 手動調査フロー

## 目的
Backend統合テストとElectronアプリの動作確認が完了したため、実際の音声ファイルを使用した統合E2Eテストを実施します。

---

## 前提条件

### 必要なサーバー（全て起動済み）
- ✅ Docker Containers: miovo-aivisspeech, miovo-rvc（両方healthy）
- ✅ Vite Dev Server: http://localhost:5173

### 必要なファイル
- テキストファイル（朗読モードテスト用）
- 音楽ファイル（歌唱モードテスト用: WAV, MP3, FLAC, OGG対応）

---

## フロー1: 朗読モード - TTS生成テスト

### ステップ1: ブラウザでアプリを開く
1. ブラウザで http://localhost:5173 にアクセス
2. 左上「朗読モード」が選択されていることを確認

### ステップ2: テキスト入力と設定
1. メインのテキストエリアに日本語テキストを入力
   - 例: 「こんにちは。今日は良い天気ですね。」
2. 右側の「感情スタイル」を選択（5種類から選択）
   - ニュートラル
   - 嬉しい
   - 悲しい
   - 怒り
   - 落ち着き
3. 音声設定を調整（必要に応じて）
   - 話速: 1.00x（デフォルト）
   - 音高: 0.00
   - 抑揚: 1.00

### ステップ3: 音声生成
1. 「WAVで保存」ボタンをクリック
2. タイムラインに生成された音声が表示されることを確認
3. 生成された音声ファイルをダウンロード

### ステップ4: 結果確認
- [ ] 音声が正常に生成された
- [ ] 音声の内容が入力テキストと一致
- [ ] 選択した感情スタイルが反映されている
- [ ] 音声設定（話速、音高、抑揚）が反映されている

### 期待される動作
- AivisSpeech APIを使用してTTS音声が生成される
- タイムラインに音声波形が表示される
- WAVファイルとしてダウンロード可能

---

## フロー2: 朗読モード - TTS + RVC パイプラインテスト

### 前提条件
- RVCモデルファイル（.pth）が `MioVo/models/rvc/` に配置済み

### ステップ1: TTS音声生成（フロー1と同じ）
1. テキストを入力
2. 感情スタイルと音声設定を調整
3. TTS音声を生成

### ステップ2: RVC声変換（将来実装予定）
**注意**: 現在のUIはTTS生成のみ対応。RVC変換は歌唱モードで実施可能

---

## フロー3: 歌唱モード - ボーカル分離テスト（Demucs）

### ステップ1: 歌唱モードに切替
1. 右上の「歌唱モード」ボタンをクリック
2. UIが歌唱モード専用に切り替わることを確認

### ステップ2: 音楽ファイルをアップロード
1. 中央のドラッグ&ドロップエリアに音楽ファイルをドロップ
   - 対応形式: WAV, MP3, FLAC, OGG
   - または「選択してアップロード」をクリック
2. ファイルが正常にアップロードされることを確認

### ステップ3: ボーカル分離実行（Backend APIを直接テスト）
**注意**: UIからのボーカル分離は将来実装予定。現在はBackend APIを直接テスト可能

#### PowerShellでのテスト例
```powershell
# 音楽ファイルをBase64エンコード
$audioBytes = [System.IO.File]::ReadAllBytes("path/to/your/music.wav")
$audioBase64 = [Convert]::ToBase64String($audioBytes)

# Demucs APIを呼び出し
$body = @{
    audio_base64 = $audioBase64
    model = "htdemucs"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:10102/separate" -Method POST -Body $body -ContentType "application/json" -OutFile "result.json"

# 結果からボーカルと伴奏を取得
$result = Get-Content "result.json" | ConvertFrom-Json
[Convert]::FromBase64String($result.vocals_base64) | Set-Content "vocals.wav" -Encoding Byte
[Convert]::FromBase64String($result.accompaniment_base64) | Set-Content "accompaniment.wav" -Encoding Byte
```

### ステップ4: 結果確認
- [ ] ボーカル分離が正常に実行された
- [ ] vocals.wav（ボーカルのみ）が生成された
- [ ] accompaniment.wav（伴奏のみ）が生成された
- [ ] 分離品質が良好

---

## フロー4: 歌唱モード - RVC声変換テスト

### 前提条件
- RVCモデルファイル（.pth）が `MioVo/models/rvc/` に配置済み
- 変換したい音声ファイル（ボーカル部分）

### ステップ1: RVCモデル選択
1. 右側の「変換先の声」ドロップダウンからモデルを選択
   - モデルが表示されない場合は `MioVo/models/rvc/` にモデルファイルを配置

### ステップ2: 変換設定
1. ピッチ抽出方法: harvest（推奨）
2. 子音保護: 0.50（デフォルト）
3. インデックス比率: 0.75（デフォルト）

### ステップ3: 声変換実行（Backend APIを直接テスト）
**注意**: UIからの声変換は将来実装予定。現在はBackend APIを直接テスト可能

#### PowerShellでのテスト例
```powershell
# 音声ファイルをBase64エンコード
$audioBytes = [System.IO.File]::ReadAllBytes("path/to/vocals.wav")
$audioBase64 = [Convert]::ToBase64String($audioBytes)

# RVC APIを呼び出し
$body = @{
    audio_base64 = $audioBase64
    model_name = "your-model.pth"
    params = @{
        f0method = "harvest"
        protect = 0.5
        index_rate = 0.75
        filter_radius = 3
        resample_sr = 0
        rms_mix_rate = 0.25
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:10102/convert" -Method POST -Body $body -ContentType "application/json" -OutFile "converted_result.json"

# 結果から変換済み音声を取得
$result = Get-Content "converted_result.json" | ConvertFrom-Json
[Convert]::FromBase64String($result.audio_base64) | Set-Content "converted_vocals.wav" -Encoding Byte
```

### ステップ4: 結果確認
- [ ] 声変換が正常に実行された
- [ ] 変換済み音声が生成された
- [ ] 声質が選択したモデルに変換されている
- [ ] 音質が良好（歪みやノイズがない）

---

## フロー5: 統合E2Eテスト（歌唱モード完全版）

### ステップ1: 音楽ファイル準備
1. ボーカル入りの音楽ファイルを用意（WAV, MP3, FLAC, OGG）

### ステップ2: ボーカル分離（Demucs）
1. フロー3に従ってボーカル分離を実行
2. vocals.wavとaccompaniment.wavを取得

### ステップ3: 声変換（RVC）
1. フロー4に従って vocals.wav を声変換
2. converted_vocals.wav を取得

### ステップ4: 音声ミックス（手動）
1. 変換済みボーカル（converted_vocals.wav）と伴奏（accompaniment.wav）を音声編集ソフトで合成
   - 推奨ツール: Audacity（無料）

### ステップ5: 最終結果確認
- [ ] 元の音楽からボーカルが正常に分離された
- [ ] ボーカルの声質が指定モデルに変換された
- [ ] 伴奏と合成した最終音源の音質が良好
- [ ] 全体的な処理時間が許容範囲内

---

## トラブルシューティング

### TTS生成がエラーになる場合
1. コンソールエラーを確認（F12）
2. AivisSpeechコンテナのログを確認:
   ```powershell
   docker logs miovo-aivisspeech
   ```
3. APIエンドポイントが応答しているか確認:
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:10101/version"
   ```

### RVC変換がエラーになる場合
1. RVCモデルファイルが正しく配置されているか確認
2. RVCコンテナのログを確認:
   ```powershell
   docker logs miovo-rvc
   ```
3. モデルが正常にロードされているか確認:
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:10102/models"
   ```

### Demucs分離がエラーになる場合
1. 入力ファイルのフォーマットが対応しているか確認
2. RVCコンテナのログを確認（DemucsはRVCコンテナに統合）
3. メモリ使用量を確認（大きいファイルは多くのメモリを使用）

---

## 結果記録

### 各テスト完了後、以下に結果を記録
記録先: `MioVo/tmp/cli/[timestamp]/manual-test-results.txt`

#### 朗読モード - TTS生成
- 実施日時: 
- 結果: 成功 / 失敗
- コメント: 

#### 歌唱モード - ボーカル分離
- 実施日時: 
- 結果: 成功 / 失敗
- 入力ファイル: 
- 処理時間: 
- コメント: 

#### 歌唱モード - RVC声変換
- 実施日時: 
- 結果: 成功 / 失敗
- 使用モデル: 
- 処理時間: 
- 音質評価: 
- コメント: 

#### 統合E2Eテスト
- 実施日時: 
- 結果: 成功 / 失敗
- 全体処理時間: 
- 総合評価: 
- コメント: 

---

## 次のステップ

### 完了後
1. 結果を記録ファイルに保存
2. 問題があれば `MioVo/memory-bank/progress.md` に記録
3. 必要に応じてコード修正・改善を実施
