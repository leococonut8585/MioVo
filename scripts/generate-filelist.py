#!/usr/bin/env python3
"""
RVC学習用filelist.txt生成スクリプト
0_gt_wavs内の全WAVファイルをリストアップ
"""

import os
import glob

# パス設定
LEO_DIR = "/workspace/RVC-WebUI/logs/LEO"
GT_WAVS_DIR = os.path.join(LEO_DIR, "0_gt_wavs")
OUTPUT_FILE = os.path.join(LEO_DIR, "filelist.txt")

# WAVファイル取得
wav_files = glob.glob(os.path.join(GT_WAVS_DIR, "*.wav"))
wav_files.sort()

# filelist.txt生成（format: gt_wav|feature|f0|f0nsf|speaker_id - 存在確認付き）
valid_count = 0
skipped_count = 0

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for wav_path in wav_files:
        # ベース名取得（拡張子なし）
        base_name = os.path.basename(wav_path).replace('.wav', '')
        
        # 絶対パス構築
        gt_wav = wav_path
        feature = os.path.join(LEO_DIR, f"3_feature768/{base_name}.npy")
        f0 = os.path.join(LEO_DIR, f"2a_f0/{base_name}.wav.npy")
        f0nsf = os.path.join(LEO_DIR, f"2b-f0nsf/{base_name}.wav.npy")
        speaker_id = "0"
        
        # 全ファイルが存在する場合のみ追加
        if os.path.exists(feature) and os.path.exists(f0) and os.path.exists(f0nsf):
            f.write(f"{gt_wav}|{feature}|{f0}|{f0nsf}|{speaker_id}\n")
            valid_count += 1
        else:
            skipped_count += 1

print(f"✓ filelist.txt生成完了")
print(f"  総ファイル数: {len(wav_files)}")
print(f"  有効: {valid_count}件")
print(f"  スキップ: {skipped_count}件")
print(f"  出力先: {OUTPUT_FILE}")

if valid_count > 0:
    print(f"\n先頭5行:")
    with open(OUTPUT_FILE, 'r') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(f"  {line.rstrip()}")
