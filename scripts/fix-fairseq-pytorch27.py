#!/usr/bin/env python3
"""
fairseq checkpoint_utils.py修正スクリプト
PyTorch 2.7のweights_only=Trueデフォルト化に対応
"""

import re

# 修正対象ファイル
CHECKPOINT_UTILS_PATH = "/opt/conda/envs/py310/lib/python3.10/site-packages/fairseq/checkpoint_utils.py"

# ファイル読込
with open(CHECKPOINT_UTILS_PATH, 'r') as f:
    content = f.read()

# Line 315付近を検索・置換
# Before: state = torch.load(f, map_location=torch.device("cpu"))
# After:  state = torch.load(f, map_location=torch.device("cpu"), weights_only=False)

pattern = r'state = torch\.load\(f, map_location=torch\.device\("cpu"\)\)'
replacement = r'state = torch.load(f, map_location=torch.device("cpu"), weights_only=False)'

content_new = re.sub(pattern, replacement, content)

# 変更確認
if content != content_new:
    # ファイル書込
    with open(CHECKPOINT_UTILS_PATH, 'w') as f:
        f.write(content_new)
    print("✓ 修正完了: Line 315に weights_only=False を追加")
    print(f"  対象: {CHECKPOINT_UTILS_PATH}")
else:
    print("⚠ 該当行が見つかりませんでした（既に修正済みの可能性）")
