# MioVo - ローカル音声スタジオ

**文章を自然なナレーションに。曲の"歌い手の声"だけを、まるっと別の声に。**  
**しかも全部、あなたのPCの中だけで完結。**

クラウドに送らず、オフラインで動く"ローカル音声スタジオ"

## ✨ 主な機能

### 🎙️ 1. 自然な読み上げ（朗読モード）
- 文章を貼るだけで、人間らしい抑揚のあるナレーション生成
- 話し方の雰囲気（感情）をボタン一つで切り替え
- 長文も自動分割して途切れない朗読を実現

### ⌨️ 2. キーボードで"しゃべり方"を微調整
- **矢印キー**: 文章のアクセント（抑揚の山）を左右へ調整
- **スペースキー**: その行だけ即プレビュー再生
- **数字キー**: 喜怒哀楽の感情スタイルをワンタッチ切替

### 🔄 3. 気になる一文だけ"作り直し"
- 長い原稿を全部作り直す必要なし
- その行だけサッと再生成
- 部分的なやり直しで無駄な待ち時間を削減

### 🎵 4. 曲の"歌の声だけ"取り替える（歌唱モード）
- 曲ファイルから歌声だけを抽出
- 歌声を別の声色に入れ替え（伴奏はそのまま）
- 「同じメロディで別の人が歌う」音源を作成

### 🔒 5. 完全ローカル・プライバシー安心
- ネットにアップロードしない
- 原稿・音源は外部に出ない
- 企業資料、未公開台本も安心

### 💎 6. WAVで高音質書き出し
- 48kHz/24bit WAV形式で保存
- 動画編集・音楽制作ソフトへそのまま持ち込み可能

## 🚀 Quick Start

### 前提条件
- **OS**: Windows 10/11（推奨）、macOS、Linux
- **GPU**: NVIDIA RTX series（RTX 5090推奨）
- **RAM**: 16GB以上（32GB推奨）
- **Storage**: 50GB以上の空き容量

### インストール

```powershell
# 1. リポジトリをクローン
cd "C:\Program Files (x86)\APP"
git clone <repository-url> MioVo
cd MioVo

# 2. 依存関係をインストール
npm install

# 3. Python環境をセットアップ
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..

# 4. Docker環境をセットアップ（RVC用）
cd docker
docker-compose build
docker-compose up -d
cd ..
```

### 起動方法

```powershell
# 開発モード
npm run electron:dev

# 本番ビルド（Windows）
npm run electron:build:win
```

詳細な手順は [docs/setup-guide.md](docs/setup-guide.md) をご覧ください。

## 🏗️ アーキテクチャ

```
[Electron GUI (React + TypeScript)]
   └─[FastAPI Gateway: 8000]
        ├─[AivisSpeech Engine: 10101, ONNX]
        └─[RVC Service: 10102, PyTorch/Docker]
             └─[Demucs Worker]
```

### 技術スタック

**Frontend**:
- Electron 33.3.1
- React 18.3.1
- TypeScript 5.7.2
- Vite 6.0.5
- Tailwind CSS 4.1.0
- Motion 12.23.0

**Backend**:
- FastAPI 0.115.6
- Python 3.9-3.11
- ONNX Runtime 1.23.x
- PyTorch 2.x (Docker/NGC)

**Audio Processing**:
- AivisSpeech Engine (TTS)
- RVC (Voice Conversion)
- Demucs v4 (Vocal Separation)

## 📖 ドキュメント

- [プロジェクト構造](docs/project-structure.md)
- [セットアップガイド](docs/setup-guide.md)
- [参照文献](C:\Users\dokog\Desktop\docs\sources.md)

## 🎯 開発状況

- [x] プロジェクト構成設計
- [x] コアファイル実装（TypeScript, Electron, React）
- [x] Backend骨格実装（FastAPI, AivisSpeech wrapper, RVC server）
- [ ] UI詳細実装（Timeline editor, キーボードショートカット）
- [ ] 統合テスト
- [ ] パッケージング

## 🔧 開発

### 開発サーバー起動

```powershell
# Terminal 1: Frontend (Vite + Electron)
npm run electron:dev

# Terminal 2: FastAPI Gateway（オプション）
cd backend/gateway
python main.py

# Terminal 3: RVC Service（Docker）
cd docker
docker-compose up rvc
```

### コード品質

```powershell
# 型チェック
npm run type-check

# Lint
npm run lint

# フォーマット
npm run format
```

## 🐛 トラブルシューティング

### Docker GPU が検出されない
```powershell
# NVIDIA Container Toolkit更新
wsl --update
docker run --rm --gpus all nvcr.io/nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi
```

### ポート競合エラー
```powershell
# 使用中のポートを確認
netstat -ano | findstr :10101
netstat -ano | findstr :10102
netstat -ano | findstr :8000

# プロセス終了
taskkill /F /PID <PID>
```

詳細は [docs/setup-guide.md](docs/setup-guide.md) のトラブルシューティングセクションをご覧ください。

## 📝 ライセンス

UNLICENSED - Private Project

## 🙏 謝辞

- [AivisSpeech](https://aivis-project.com/)
- [RVC Python](https://github.com/litagin02/rvc-python)
- [Demucs](https://github.com/facebookresearch/demucs)
- その他、使用している全てのオープンソースプロジェクト

---

**MioVo** - Made with ❤️ for creators
