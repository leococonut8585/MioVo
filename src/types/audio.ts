/**
 * Audio-related type definitions
 */

// AivisSpeech AudioQuery structure
export interface Mora {
  text: string
  consonant?: string
  consonant_length?: number
  vowel: string
  vowel_length: number
  pitch: number
}

export interface AccentPhrase {
  moras: Mora[]
  accent: number  // Accent nucleus position (0-indexed)
  pause_mora?: Mora
  is_interrogative?: boolean
}

export interface AudioQuery {
  accent_phrases: AccentPhrase[]
  speedScale: number        // 0.5-2.0
  pitchScale: number        // 0.0-2.0
  intonationScale: number   // 0.0-2.0
  volumeScale: number       // 0.0-2.0
  prePhonemeLength: number
  postPhonemeLength: number
  outputSamplingRate: number
  outputStereo: boolean
  kana?: string
}

// Text chunk for processing
export interface TextChunk {
  index: number
  text: string
  audioQuery?: AudioQuery
  wavPath?: string
  status: 'pending' | 'processing' | 'done' | 'error'
  error?: string
}

// Reading mode state
export interface ReadingLine {
  id: string
  text: string
  chunk?: TextChunk
  selected: boolean
}

// Emotion/Style
export interface EmotionStyle {
  id: string
  name: string
  speakerId: number
  icon?: string
}

// Voice model
export interface VoiceModel {
  id: string
  name: string
  type: 'tts' | 'rvc'
  speakerId?: number  // For AivisSpeech
  modelPath?: string  // For RVC
}

// Audio settings
export interface AudioSettings {
  speedScale: number
  pitchScale: number
  intonationScale: number
  volumeScale: number
  sampleRate: number
  bitDepth: 16 | 24 | 32
}

// RVC parameters
export interface RVCParams {
  f0method: 'harvest' | 'rmvpe' | 'crepe' | 'pm'
  protect: number      // 0.0-0.5
  index_rate: number   // 0.0-1.0
  filter_radius: number // 3-7
  resample_sr: number  // 0=auto
  rms_mix_rate: number // 0.0-1.0
}

// Task state
export type TaskStatus = 'idle' | 'queued' | 'processing' | 'completed' | 'failed'

export interface Task {
  id: string
  type: 'tts' | 'rvc' | 'separation'
  status: TaskStatus
  progress: number // 0-100
  chunks?: TextChunk[]
  result?: string
  error?: string
  createdAt: Date
  updatedAt: Date
}
