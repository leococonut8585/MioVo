# MioVo - Replit環境セットアップ

## プロジェクト概要

**MioVo（ミオヴォ）** は、完全ローカルで動作する音声スタジオアプリケーションです。
- **朗読モード**: テキストを自然な音声に変換（TTS）
- **歌唱モード**: 曲の歌声を別の声に変換（Voice Conversion）

## アーキテクチャ

### フロントエンド
- **技術**: React 18 + TypeScript + Vite 6
- **ポート**: 5000（Replit要件）
- **UI**: Tailwind CSS 4 + Motion

### バックエンド
- **技術**: FastAPI (Python 3.11) + Uvicorn
- **ポート**: 8000（API Gateway）
- **エンドポイント**: `/docs` でSwagger UIを確認可能

## Replit環境での制限事項

### ⚠️ 重要な制限

このプロジェクトは本来、**Electronデスクトップアプリケーション**として設計されていますが、Replit環境では以下の制限があります：

1. **Electronは実行不可**: Replitはクラウド環境のため、デスクトップGUIアプリケーションを実行できません
   - 解決策: Web版（Vite dev server）のみを実行

2. **外部サービス未接続**: 以下のサービスは別途セットアップが必要です
   - **AivisSpeech Engine** (TTS): ポート10101で動作する音声合成エンジン
   - **RVC Service** (Voice Conversion): ポート10102で動作する音声変換サービス
   - これらはDocker/ローカル環境で実行する必要があります

3. **GPU処理不可**: 音声処理にはNVIDIA GPUが必要ですが、Replit環境では利用できません

### 現在の動作状況

- ✅ **フロントエンドUI**: 正常に表示・動作します
- ✅ **バックエンドAPI**: ゲートウェイとして起動しますが、実際の音声処理は行えません
- ❌ **TTS機能**: AivisSpeechサービスが必要（未接続）
- ❌ **RVC機能**: RVCサービスとDemucsが必要（未接続）

## 開発環境

### インストール済みの環境

- **Node.js**: v20.x
- **Python**: 3.11
- **パッケージマネージャー**: npm, pip

### 設定済みのワークフロー

1. **Frontend**: `npm run dev` → ポート5000
2. **Backend**: `uvicorn main:app` → ポート8000

## ローカル環境での完全セットアップ

完全な機能を利用するには、ローカル環境で以下をセットアップしてください：

### 前提条件
- **OS**: Windows 10/11（推奨）、macOS、Linux
- **GPU**: NVIDIA RTX series（RTX 5090推奨）
- **RAM**: 16GB以上（32GB推奨）
- **Storage**: 50GB以上の空き容量

### セットアップ手順

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd MioVo

# 2. フロントエンド依存関係
npm install

# 3. Python環境（バックエンド）
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..

# 4. Docker環境（RVC + Demucs）
cd docker
docker-compose build
docker-compose up -d
cd ..

# 5. Electronアプリとして起動
npm run electron:dev
```

詳細は [docs/setup-guide.md](docs/setup-guide.md) を参照してください。

## Replit環境での利用方法

### フロントエンドUIのプレビュー

1. 右上の「Webview」タブでUIを確認できます
2. モード切替（朗読/歌唱）やUIコンポーネントの動作確認が可能

### バックエンドAPIの確認

FastAPI のSwagger UI で API仕様を確認：
```
https://<your-repl-url>:8000/docs
```

### テストリクエスト例

```bash
# ヘルスチェック
curl https://<your-repl-url>:8000/health

# TTS テスト（サービス未接続のため失敗します）
curl -X POST https://<your-repl-url>:8000/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは", "speaker_id": 0}'
```

## 最近の変更

### 2025-10-16: Replit環境対応

- ✅ Vite設定を5000ポートに変更
- ✅ Electronプラグインを条件付きで無効化（Replit環境では非実行）
- ✅ バックエンドCORSにReplit domainを追加
- ✅ 相対インポートを絶対インポートに修正
- ✅ フロントエンド・バックエンドのワークフロー作成
- ⚠️ TTS/RVCサービスは未接続（ローカル環境が必要）

## プロジェクト構造

```
MioVo/
├── src/                    # Reactフロントエンド
│   ├── components/         # UIコンポーネント
│   │   ├── reading/        # 朗読モード
│   │   └── singing/        # 歌唱モード
│   ├── hooks/              # カスタムフック
│   └── types/              # TypeScript型定義
├── backend/                # Pythonバックエンド
│   ├── gateway/            # FastAPI ゲートウェイ
│   │   ├── routers/        # APIルーター
│   │   ├── main.py         # エントリーポイント
│   │   └── models.py       # Pydanticモデル
│   ├── aivisspeech/        # TTS クライアント
│   └── rvc/                # RVC サーバー
├── electron/               # Electronメインプロセス
├── docs/                   # ドキュメント
└── docker/                 # Docker設定（RVC）
```

## ユーザー設定

### コーディングスタイル
- TypeScript strict mode 有効
- Python type hints 使用
- Prettier + ESLint でフォーマット

### ワークフロー設定
- フロントエンド: Vite HMR（Hot Module Replacement）有効
- バックエンド: Uvicorn auto-reload 有効

## トラブルシューティング

### フロントエンドが表示されない
1. ワークフローが実行中か確認
2. ポート5000がリッスンされているか確認
3. ブラウザキャッシュをクリア

### バックエンドAPIがエラーを返す
1. ポート8000がリッスンされているか確認
2. `/health` エンドポイントで動作確認
3. TTS/RVC機能はローカル環境が必要

### LSPエラーが表示される
- バックエンドのLSPエラーは、外部サービス（AivisSpeech）のインポートが原因
- 実行には影響しません（該当機能は無効化済み）

## 参考リンク

- [AivisSpeech](https://aivis-project.com/) - TTS エンジン
- [RVC Python](https://github.com/litagin02/rvc-python) - 音声変換
- [Demucs](https://github.com/facebookresearch/demucs) - ボーカル分離

---

**注意**: このプロジェクトの完全な機能を利用するには、ローカル環境での実行が必要です。Replit環境ではUI/APIのプレビューと開発のみが可能です。
