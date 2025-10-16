# MioVo Active Context

## Current Phase
**Dockerビルドテスト実行中・5090互換性修正完了フェーズ** (2025-10-16 01:52-)

## Current Status
✅ **完了事項**：
- Memory Bank初期化（6ファイル構成）
- 三段階API検索環境構築（tri-search.mjs + APIキー設定）
- 全5技術の最新情報検証完了（合計122件）
  - AivisSpeech: VOICEVOX互換API確認
  - rvc-python: API実装確認
  - Demucs v4: Hybrid Transformer版確認
  - PyTorch RTX 5090: SM_120問題・対策確認
  - ONNX Runtime: 最新版互換性確認
- **NGC PyTorch 24.10互換性問題の発見と修正（2025-10-16）**
  - 3段階API検索×3回実施（計66件）
  - NGC 24.10公式リリースノートを実機Chrome確認
  - Dockerfile修正完了（計画書通りに戻す）

🔄 **実行中**：
- Dockerイメージビルドテスト（pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime）
- ベースイメージダウンロード中（2.54GB/4.24GB）

## Key Findings from Verification

### ✅ 計画書の妥当性確認（再検証済み）
- **アーキテクチャ**: プロセス分離戦略は適切 ✅
- **技術選定**: 全て実装可能・最新情報と整合 ✅
- **PyTorch戦略**: 計画書の`pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime`が正解だった ✅

### 🔴 発見・修正した問題
1. **NGC PyTorch 24.10互換性問題**（2025-10-16発見・修正完了）
   - CUDA 12.6.2（12.8未満）← RTX 5090 Blackwell (sm_120)には不足
   - PyTorch 2.5.0a0（2.7.0未満）← sm_120非対応
   - **修正**: `nvcr.io/nvidia/pytorch:24.10-py3` → `pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime`
   - **根拠**: 3段階API検索（66件）+ 公式ドキュメント一次確認

### ⚠️ 引き続き注意が必要な点
1. **AivisSpeech長文**: 500字推奨の明確な公式記載は未確認（要追加調査）
2. **RVCバージョン**: 複数の実装あり（rvc-python / RVC WebUI / w-okada版）

## Next Actions (優先順位順)

### 1. プロジェクト構成の詳細設計
- [ ] ディレクトリ構造の設計
- [ ] package.json（Electron + React）
- [ ] requirements.txt（FastAPI + Python依存）
- [ ] docker-compose.yml（RVC環境）
- [ ] .gitignore（APIキー・ビルド成果物除外）

### 2. 開発環境セットアップ手順書作成
- [ ] Electron + React + TypeScript環境
- [ ] FastAPI Gateway実装
- [ ] AivisSpeech Engine導入手順
- [ ] RVC Docker環境構築手順
- [ ] Demucs v4統合手順

### 3. 実装フェーズ準備
- [ ] UIコンポーネント設計（M節準拠：React + Tailwind + Motion）
- [ ] API Gateway設計（ジョブ管理・進捗・リトライ）
- [ ] データモデル設計（AudioQuery / RVCParams / Task）

## Critical Constraints (Red Lines - 再確認)
- **L節**: 大きいファイルは差分編集・バックアップ→検証→反映
- **B節・O節**: 技術情報は三段階API検索で検証済み ✅
- **E節**: サンプルではなく完成版を納品
- **D節**: エラー時は最低3サイクルデバッグ
- **M節**: UIはReact+Tailwind+Motion

## Decisions Made (累積)
1. プロジェクトディレクトリ: `C:\Program Files (x86)\APP\MioVo`
2. Memory Bank構造: 6ファイル構成
3. **PyTorch戦略（修正済み）**: `pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime`（計画書通り）
4. アーキテクチャ: マイクロサービス風プロセス分離
5. 三段階API検索環境: 構築完了・動作確認済み
6. **技術選定の妥当性**: 最新情報による検証完了
7. **NGC PyTorch 24.10問題**: 発見・修正完了（2025-10-16 01:13）

## Open Questions
- プロジェクト構成の詳細（ディレクトリ構造・ファイル配置）
- UI実装方法（M節のパターン1/2/3のいずれを採用するか）
- RVC実装の選定（rvc-python / その他）
- Docker構成の詳細（NGC baseイメージ / 独自ビルド）

## Risks & Concerns
- **PyTorch SM_120**: Docker/NGC戦略が必須（検証で再確認）
- **長文処理**: 500字分割戦略の妥当性を実装で検証必要
- **歌唱品質**: protect/filter_radius調整の最適値を実験で確認必要
- **モデルキャッシュ**: LRU実装の詳細設計が必要

## Reference Documents
- 全参照文献: `docs/sources.md`（継続更新中）
- 検索結果詳細: 
  - 初回検証（2025-10-15）: 122件
  - NGC互換性調査（2025-10-16）: 66件（tmp/research/20251015T155706, 155759, 160015）
- 公式ドキュメント一次確認:
  - https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-24-10.html
- 計画書原本: memory-bank/projectbrief.md, techContext.md
