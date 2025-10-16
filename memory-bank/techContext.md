# MioVo Technical Context

## Technology Stack

### Core Components

#### 1. AivisSpeech Engine (TTS)
- **Version**: Latest stable (2025-10)
- **Runtime**: ONNX Runtime 1.22-1.23系
- **Port**: 10101 (default)
- **API**: VOICEVOX互換HTTP API
  - `/speakers` → スタイルID一覧
  - `/audio_query` → AudioQuery JSON取得
  - `/synthesis` → WAV生成
- **Model Format**: AIVMX (ONNX)
- **Key Advantage**: PyTorch非依存、CPUでも動作可能
- **Critical Constraint**: 
  - **推奨500字/回**、1000字超は非推奨
  - 文境界での分割が必須

#### 2. RVC (Voice Conversion)
- **Implementation**: rvc-python API
- **Port**: 10102 (recommended)
- **Runtime**: PyTorch (要注意)
- **API Endpoints**:
  - `POST /convert` - 音声変換
  - `GET /models` - モデル一覧
  - `POST /models/{name}` - モデルロード
  - `GET/POST /params` - パラメータ設定
  - `POST /set_device` - デバイス設定
- **Key Parameters**:
  - `f0method`: harvest (歌唱推奨) / rmvpe (朗読推奨)
  - `protect`: 子音保護 (0.0-0.5)
  - `index_rate`: インデックス比率

#### 3. Demucs v4 (Vocal Separation)
- **Version**: v4 (Hybrid Transformer)
- **Provider**: Meta
- **Usage**: CLI呼び出し
  - `demucs --two-stems=vocals input.wav`
- **Output**: vocals.wav / no_vocals.wav
- **Advantage**: 高精度分離、PyTorchベース統合容易

### GPU/Driver Requirements (RTX 5090)

#### Critical Configuration
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **Driver**: 
  - Windows: R570系 570.65以上
  - Linux: 570.26以上
- **CUDA**: 12.8.1 (Blackwell初期ネイティブ対応)
- **cuDNN**: 9.14系

#### PyTorch Strategy (重要)
**問題**: PyTorch安定版のSM_120（RTX 50系）サポートは不均一

**対策**: 3パターンの優先順位
1. **A. NGC/公式コンテナ** (最推奨)
   - `pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime`
   - Docker/WSL2でRVCプロセスのみ実行
   - SM_120対応確認済み

2. **B. PyTorch 2.9 + cu128/13.0系**
   - 2.8系のホイール不足・SM_120未完全対応を解消
   - 環境差異に注意

3. **C. ソースビルド**
   - `TORCH_CUDA_ARCH_LIST="12.0+PTX"`
   - 最終手段として

**設計方針**: AivisSpeechはONNXでPyTorch非依存のため安定。RVCのみを別プロセス（Docker/WSL2）で隔離することで、PyTorch問題を局所化。

### VRAM Budget (推定)
- AivisSpeech (ONNX, GPU): ~3-4GB
- RVCモデル1本: ~2-3GB
- HuBERT/ContentVec: ~0.5GB
- バッファ: ~1-2GB
- **合計**: ~6.5-9.5GB/リクエスト

**戦略**: LRUキャッシュでモデル5-7本常駐可能（32GB中28GB上限設定）

## System Architecture

```
[Electron GUI]
   └─[FastAPI Gateway: 8000]
        ├─[AivisSpeech Engine: 10101, ONNX]
        └─[RVC Service: 10102, PyTorch/Docker]
             └─[Demucs Worker]
```

### Process Isolation Benefits
1. AivisSpeech: 安定・高速（ONNX）
2. RVC: PyTorch問題を隔離（別プロセス）
3. クラッシュ影響の局所化
4. 個別スケーリング可能

## Performance & Quality

### Text Processing
- **Chunking**: 500字単位で自動分割
- **Split Strategy**: 文境界正規表現 `(?<=[。！？!?])\s+`
- **Parallel TTS**: 4-6チャンク並行処理
- **Sequential RVC**: メモリフラグメンテーション抑制

### Audio Pipeline
- **Sample Rate**: 48kHz
- **Bit Depth**: 24bit
- **Format**: WAV (lossless)
- **Vocal Mix**: 0dB (default)
- **Accomp Mix**: -3dB (clip prevention)

### Model Management
- **Cache Strategy**: LRU (Least Recently Used)
- **Preload**: 初期起動時に指定モデルをプレロード
- **Hot Swap**: `torch.cuda.empty_cache()` でメモリ解放
- **Watchdog**: 5秒ごとにヘルスチェック

## Known Risks & Mitigations

### Risk 1: PyTorch SM_120 Support
- **Impact**: RVCプロセスがGPU未使用/失敗
- **Mitigation**: NGC/WSL2/Dockerでコンテナ化（A策優先）

### Risk 2: Long Text Quality Degradation
- **Impact**: 抑揚劣化・メモリリーク
- **Mitigation**: 500字分割・行単位再生成

### Risk 3: Vocal Consonant Loss
- **Impact**: 歌唱明瞭度低下
- **Mitigation**: RVC `protect`/`filter_radius`調整UI提供

### Risk 4: Model Switch Latency
- **Impact**: 操作感悪化
- **Mitigation**: LRU常駐・事前プレロード

## Development Environment
- **OS**: Windows 10/11 (WSL2 for RVC optional)
- **Node.js**: 18+ (Electron)
- **Python**: 3.9-3.11
- **Frontend**: React + TypeScript
- **Backend**: FastAPI + uvicorn
- **Desktop**: Electron

## External Dependencies
- Docker Desktop (RVC隔離用、optional)
- FFmpeg (audio processing)
- Visual C++ Redistributable (ONNX Runtime)
