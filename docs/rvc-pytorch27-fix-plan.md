# RVC WebUI PyTorch 2.7互換性修正計画

## 日時
2025-10-16 20:25

## 問題
RVC WebUIがPyTorch 2.7の`weights_only=True`デフォルト化により、fairseqモデルロードでUnpicklingError発生

## 計画との整合性確認（F節・G節遵守）
✅ **techContext.md計画**: PyTorch 2.7.0 + CUDA 12.8（RTX 5090 sm_120対応必須）
✅ **現行RVCコンテナ**: PyTorch 2.7.0使用中
✅ **計画からの逸脱なし**: PyTorch 2.7維持が最適

## 修正試行順（期待度順・B節準拠）

### 修正1（最推奨・期待度90%）
**対象**: fairseq checkpoint_utils.py Line 315
**修正**: `torch.load(..., weights_only=False)`追加
**理由**: PyTorch 2.7公式推奨、RTX 5090成功事例多数
**出典**: 
- bleekseeks.com "How to Run RVC WebUI on RTX 50-Series GPUs" (2025最新)
- GitHub RVC-Project issue #2419
- CSDN blog.csdn.net/ccd9287/article/details/146259219

### 修正2（期待度60%）
**対象**: infer/lib/train/utils.py Line 238
**修正**: `tostring_rgb()` → `tobytes()`
**理由**: matplotlib 3.10+互換
**出典**: bleekseeks.com

### 修正3（期待度40%）
**対象**: infer/modules/train/train_index.py
**修正**: 新規ファイル作成
**理由**: 特徴インデックス学習エラー対応
**出典**: bleekseeks.com

## 実行順序（D節デバッグサイクル準拠）
1. 修正1実行 → 学習テスト → 成功なら完了
2. 失敗時 → 修正2実行 → 学習テスト
3. 失敗時 → 修正3実行 → 学習テスト
4. 全失敗時 → 旦那様に報告・指示を仰ぐ

## 参考文献（B節・docs/sources.md記録済み）
- bleekseeks.com/blog/how-to-run-rvc-webui-on-rtx-50-series-gpus-python-3-10-pytorch-2-7
- github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/issues/2486
- github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/issues/2419
- blog.csdn.net/ccd9287/article/details/146259219

## 決定
**採用**: 修正1から順次実行（PyTorch 2.7維持・計画逸脱なし）
