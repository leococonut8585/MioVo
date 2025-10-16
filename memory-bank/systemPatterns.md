# MioVo System Patterns

## Architecture Patterns

### 1. Microservice-like Process Isolation
**Pattern**: 各主要コンポーネントを独立プロセスとして実行
- **Electron GUI** (メインプロセス)
- **FastAPI Gateway** (ジョブ管理・進捗・再試行)
- **AivisSpeech Engine** (TTS専用、ONNX)
- **RVC Service** (VC専用、PyTorch/Docker隔離)

**Benefits**:
- クラッシュの影響を局所化
- 個別のスケーリング・再起動が可能
- 技術スタックの混在（ONNX vs PyTorch）を許容

### 2. LRU Model Cache Pattern
**Pattern**: RVCモデルをLRUキャッシュで管理
- 常駐数: 5-7モデル（VRAM制約内）
- 未使用モデルは自動退避
- `torch.cuda.empty_cache()` でメモリ解放

**Reference**: AllTalk TTSのLRU実装を参考

### 3. Chunk-and-Stream Pattern
**Pattern**: 長文を小チャンクに分割し、逐次処理
- **短文** (≤500字): 単発処理
- **中文** (~2000字): 4-6チャンク並列TTS → RVC逐次
- **長文** (2000字超): キュー逐次 + ストリーミング再生

**Key**: 
- TTS並列化でスループット向上
- RVC逐次化でVRAMフラグメンテーション抑制

### 4. Watchdog Pattern
**Pattern**: 5秒ごとにヘルスチェック、自動再起動
- AivisSpeech: `GET /speakers`
- RVC: `GET /models`
- 応答なし → プロセス再起動

### 5. Atomic File Update Pattern (L節準拠)
**Pattern**: 
1. 一時ファイル (.tmp) へ書き込み
2. 検証（lint/test）
3. アトミックにリネーム or 差分適用

**禁止**: 大きいファイルの全置換、省略コメント

## API Design Patterns

### AivisSpeech API Flow
```
1. GET /speakers
   → スタイルID一覧取得（初期化時）

2. POST /audio_query?speaker={styleId}&text={text}
   → AudioQuery JSON取得
   → accent_phrases, intonationScale, pitchScale等

3. [GUI編集]
   → accent_phrasesの編集（アクセント核移動）
   → intonationScale微調整

4. POST /synthesis?speaker={styleId}
   → 編集済みAudioQuery JSONを送信
   → WAV取得
```

**Key Points**:
- `/audio_query`と`/synthesis`の分離により、編集・再合成が柔軟
- 行単位の部分再生成が可能

### RVC API Flow
```
1. POST /models/{name}
   → モデルロード（LRUキャッシュへ）

2. POST /params
   → f0method, protect, index_rate等を設定

3. POST /convert
   → 入力WAV (base64) + パラメータ
   → 出力WAV (base64)
```

**Key Points**:
- パラメータとモデルの事前設定により、変換リクエストがシンプル
- 複数リクエストで同一設定を使い回し可能

### Vocal Separation Flow (Demucs)
```
1. CLI実行
   demucs --two-stems=vocals input.wav

2. 出力取得
   - separated/htdemucs/input/vocals.wav
   - separated/htdemucs/input/no_vocals.wav

3. RVC変換 (vocals.wavのみ)

4. ミックス
   vocals_converted + no_vocals → final.wav
```

## Data Models

### AudioQuery Structure (AivisSpeech)
```typescript
interface AudioQuery {
  accent_phrases: AccentPhrase[];
  speedScale: number;        // 話速 (0.5-2.0)
  pitchScale: number;        // 音高 (0.0-2.0)
  intonationScale: number;   // 抑揚 (0.0-2.0)
  volumeScale: number;       // 音量 (0.0-2.0)
  prePhonemeLength: number;  // 前空白
  postPhonemeLength: number; // 後空白
  outputSamplingRate: number; // 48000
  outputStereo: boolean;
  kana?: string;
}

interface AccentPhrase {
  moras: Mora[];
  accent: number;  // アクセント核位置（0-indexed）
  pause_mora?: Mora;
  is_interrogative?: boolean;
}

interface Mora {
  text: string;
  consonant?: string;
  consonant_length?: number;
  vowel: string;
  vowel_length: number;
  pitch: number;
}
```

### RVC Parameters
```typescript
interface RVCParams {
  f0method: 'harvest' | 'rmvpe' | 'crepe' | 'pm';
  protect: number;      // 0.0-0.5 (子音保護)
  index_rate: number;   // 0.0-1.0
  filter_radius: number; // 3-7
  resample_sr: number;  // 0=auto
  rms_mix_rate: number; // 0.0-1.0
}
```

### Task State Management
```typescript
interface Task {
  id: string;
  type: 'tts' | 'rvc' | 'separation';
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  chunks?: Chunk[];
  result?: string; // output file path
  error?: string;
}

interface Chunk {
  index: number;
  text: string;
  audioQuery?: AudioQuery;
  wavPath?: string;
  status: 'pending' | 'done' | 'error';
}
```

## Error Handling Patterns

### Retry Strategy
```python
# 指数バックオフ（最大3回）
async def retry_with_backoff(func, max_tries=3):
    for i in range(max_tries):
        try:
            return await func()
        except Exception as e:
            if i == max_tries - 1:
                raise
            await asyncio.sleep(0.8 * (2 ** i))
```

### Graceful Degradation
- **TTS失敗** → その行だけスキップ、ユーザーに通知
- **RVC失敗** → オリジナル音声を保持
- **GPU不可** → AivisSpeechはCPUフォールバック
- **Docker不可** → RVC機能を無効化、TTS機能は継続

## Security & Privacy Patterns

### Local-First Architecture
- **原則**: すべての処理をローカルで完結
- **禁止**: APIキー不要、クラウドアップロード不要
- **例外**: モデルの初回ダウンロードのみインターネット接続必要

### Sensitive Data Handling
- **原稿**: メモリ上でのみ処理、ディスク書き込みは一時ファイル
- **音声**: tmp/配下で処理、完了後はユーザー指定パスへ移動
- **モデル**: ローカルディレクトリに保存（`./rvc_models/`）

## Configuration Management

### config.yml Structure
```yaml
system:
  cuda_device: "cuda:0"
  model_cache_size: 6
  max_vram_gb: 28

aivisspeech:
  port: 10101
  gpu_mode: true
  chunk_chars: 500
  default_style_id: 888753760
  default_intonation: 1.0

rvc:
  port: 10102
  device: "cuda:0"
  model_dir: "./rvc_models"
  f0method_reading: "rmvpe"
  f0method_singing: "harvest"
  protect: 0.5
  preload_models: ["VoiceA", "VoiceB"]

processing:
  parallel_tts_chunks: 4
  use_demucs: true
  demucs_preset: "htdemucs"
  mix_vocals_db: 0
  mix_accomp_db: -3
  samplerate: 48000
  bitdepth: 24

ui:
  theme: "dark"
  keymap:
    play_pause: "Space"
    accent_left: "ArrowLeft"
    accent_right: "ArrowRight"
    intonation_up: "ArrowUp"
    intonation_down: "ArrowDown"
    emotion_toggle: ["1","2","3","4","5"]
```

## Testing Patterns

### Acceptance Criteria (DoD)
- [ ] 10,000字テキストの自動分割・全合成成功
- [ ] 行単位の部分再生成が即時反映
- [ ] 市販曲WAVの分離→変換→再ミックス成功
- [ ] キーボード操作が直感的に機能
- [ ] 連続処理100回でプロセス無停止

### Performance Benchmarks
- **TTS Latency**: <2秒/500字チャンク
- **RVC Latency**: <5秒/30秒音声
- **Separation**: <30秒/5分楽曲
- **Memory Leak**: 100回処理後もVRAM増加<10%

## Deployment Patterns

### Windows Installer
- **Format**: NSIS / Electron Builder
- **Bundled**: 
  - Electron本体
  - Node.js runtime
  - Python環境（embeddable版）
  - AivisSpeech engine
  - FFmpeg
- **Optional**: Docker Desktop (RVC用)

### Update Strategy
- **Auto-update**: Electron auto-updater
- **Model Update**: 手動ダウンロード（プライバシー優先）
- **Engine Update**: バージョン互換性チェック → 段階的更新
