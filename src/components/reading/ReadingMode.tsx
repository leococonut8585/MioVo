/**
 * Reading Mode Component
 * Main UI for text-to-speech mode
 */
import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import type { ReadingLine, EmotionStyle, AudioSettings } from '../../types/audio'
import { TimelineEditor } from '../timeline/TimelineEditor'
import { PlayAllControls } from './PlayAllControls'
import { usePlayAll } from '../../hooks/usePlayAll'

export function ReadingMode() {
  const shouldReduceMotion = useReducedMotion()
  const [lines, setLines] = useState<ReadingLine[]>([])
  const [selectedLineId, setSelectedLineId] = useState<string>()
  const [audioSettings, setAudioSettings] = useState<AudioSettings>({
    speedScale: 1.0,
    pitchScale: 0.0,
    intonationScale: 1.0,
    volumeScale: 1.0,
    sampleRate: 48000,
    bitDepth: 24
  })
  
  // Speaker management (dynamic from API)
  const [availableStyles, setAvailableStyles] = useState<EmotionStyle[]>([])
  const [selectedEmotion, setSelectedEmotion] = useState<EmotionStyle | null>(null)
  const [speakersLoading, setSpeakersLoading] = useState(true)
  
  // Audio management
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [audioCache, setAudioCache] = useState<Map<string, Blob>>(new Map())
  const audioRef = useRef<HTMLAudioElement | null>(null)
  
  // Accent editing
  const [accentPhrases, setAccentPhrases] = useState<Map<string, any>>(new Map())
  const [editingLineId, setEditingLineId] = useState<string | null>(null)
  const [hoveredMoraIndex, setHoveredMoraIndex] = useState<number | null>(null)
  
  // Pause insertion
  const [pauseInsertMode, setPauseInsertMode] = useState(false)
  const [selectedPauseType, setSelectedPauseType] = useState<'short' | 'long' | 'custom'>('short')
  const [customPauseDuration, setCustomPauseDuration] = useState(500)
  
  // Play All state
  const [playingLineId, setPlayingLineId] = useState<string | null>(null)
  
  // Play All callbacks
  const handleLineHighlight = useCallback((lineId: string | null) => {
    setPlayingLineId(lineId)
  }, [])
  
  const handleAutoScroll = useCallback((lineId: string) => {
    const element = document.getElementById(`timeline-line-${lineId}`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [])
  
  // Initialize usePlayAll hook
  const {
    isPlaying,
    isPaused,
    currentIndex,
    playbackSpeed,
    play,
    pause,
    stop,
    skip,
    setPlaybackSpeed
  } = usePlayAll({
    lines,
    audioSettings,
    selectedEmotion,
    onLineHighlight: handleLineHighlight,
    onAutoScroll: handleAutoScroll
  })

  // Fetch available speakers on mount
  useEffect(() => {
    const fetchSpeakers = async () => {
      try {
        setSpeakersLoading(true)
        const response = await fetch('/tts/speakers')
        
        if (!response.ok) {
          throw new Error('Failed to fetch speakers')
        }
        
        const data = await response.json()
        const speakers = data.speakers || []
        
        // Extract all styles from all speakers
        const styles: EmotionStyle[] = []
        
        // Handle different speaker data formats
        if (Array.isArray(speakers) && speakers.length > 0) {
          for (const speaker of speakers) {
            if (speaker.styles && speaker.styles.length > 0) {
              // VOICEVOX/AivisSpeech format with styles
              for (const style of speaker.styles) {
                styles.push({
                  id: `${speaker.speaker_uuid || speaker.speaker_id || 'speaker'}-${style.id}`,
                  name: `${speaker.name} (${style.name})`,
                  speakerId: style.id  // Use the actual style ID from the service
                })
              }
            } else {
              // Simple format without styles
              const speakerId = speaker.speaker_id || 0
              styles.push({
                id: `speaker-${speakerId}`,
                name: speaker.name || `Speaker ${speakerId}`,
                speakerId: speakerId
              })
            }
          }
          console.log('Loaded speakers:', styles)
        }
        
        // Add default speakers if no speakers are available
        if (styles.length === 0) {
          styles.push(
            { id: 'default-0', name: 'Default', speakerId: 0 },
            { id: 'default-1', name: 'Female', speakerId: 1 },
            { id: 'default-2', name: 'Male', speakerId: 2 }
          )
        }
        
        setAvailableStyles(styles)
        
        // Set first style as default
        if (styles.length > 0) {
          setSelectedEmotion(styles[0])
        }
        
      } catch (err) {
        console.error('Failed to fetch speakers:', err)
        setError(err instanceof Error ? err.message : 'Failed to fetch speakers')
        
        // Add fallback speakers even on error
        const fallbackStyles: EmotionStyle[] = [
          { id: 'default-0', name: 'Default', speakerId: 0 },
          { id: 'default-1', name: 'Female', speakerId: 1 },
          { id: 'default-2', name: 'Male', speakerId: 2 }
        ]
        setAvailableStyles(fallbackStyles)
        setSelectedEmotion(fallbackStyles[0])
      } finally {
        setSpeakersLoading(false)
      }
    }
    
    fetchSpeakers()
  }, [])

  const handleTextPaste = (text: string) => {
    // Split text into lines
    const newLines: ReadingLine[] = text.split('\n')
      .filter(line => line.trim().length > 0)
      .map((text, index) => ({
        id: `line-${Date.now()}-${index}`,
        text: text.trim(),
        selected: false
      }))
    
    setLines(newLines)
    if (newLines.length > 0) {
      setSelectedLineId(newLines[0].id)
    }
  }

  // Generate TTS audio for a line
  const handleGenerate = async (lineId: string) => {
    const line = lines.find(l => l.id === lineId)
    if (!line || !selectedEmotion) return

    setLoading(true)
    setError(null)

    try {
      // Use the new backend gateway API
      const ttsRequest = {
        text: line.text,
        speaker_id: selectedEmotion.speakerId,
        speed_scale: audioSettings.speedScale,
        pitch_scale: audioSettings.pitchScale,
        intonation_scale: audioSettings.intonationScale,
        volume_scale: audioSettings.volumeScale
      }
      
      const response = await fetch('/tts/synthesize', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(ttsRequest)
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Synthesis failed: ${response.statusText}`)
      }
      
      const taskResponse = await response.json()
      
      // Check if the task completed successfully
      if (taskResponse.status !== 'completed') {
        throw new Error(taskResponse.error || 'TTS generation failed')
      }
      
      // Decode base64 audio data
      if (!taskResponse.result?.audio_base64) {
        throw new Error('No audio data in response')
      }
      
      // Convert base64 to blob
      const audioData = atob(taskResponse.result.audio_base64)
      const audioArray = new Uint8Array(audioData.length)
      for (let i = 0; i < audioData.length; i++) {
        audioArray[i] = audioData.charCodeAt(i)
      }
      const audioBlob = new Blob([audioArray], { type: 'audio/wav' })
      
      // Cache the audio
      setAudioCache(prev => new Map(prev).set(lineId, audioBlob))
      
      // Update line status
      const lineIndex = lines.findIndex(l => l.id === lineId)
      setLines(prev => prev.map(l =>
        l.id === lineId
          ? { ...l, chunk: { index: lineIndex, text: l.text, id: `chunk-${lineId}`, status: 'done' as const } }
          : l
      ))
      
      console.log(`Generated audio for line: ${lineId}`)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(errorMessage)
      console.error('Generation failed:', err)
      
      // Update line status to error
      const lineIndex = lines.findIndex(l => l.id === lineId)
      setLines(prev => prev.map(l =>
        l.id === lineId
          ? { ...l, chunk: { index: lineIndex, text: l.text, id: `chunk-${lineId}`, status: 'error' as const, error: errorMessage } }
          : l
      ))
    } finally {
      setLoading(false)
    }
  }

  // Play audio for a line
  const handlePlay = async (lineId: string) => {
    const audio = audioCache.get(lineId)
    
    if (!audio) {
      console.log('No audio cached, generating first...')
      await handleGenerate(lineId)
      return
    }

    try {
      // Create audio element if needed
      if (!audioRef.current) {
        audioRef.current = new Audio()
      }

      // Stop current playback
      audioRef.current.pause()
      audioRef.current.currentTime = 0

      // Play new audio
      const audioUrl = URL.createObjectURL(audio)
      audioRef.current.src = audioUrl
      await audioRef.current.play()

      console.log(`Playing audio for line: ${lineId}`)

      // Cleanup URL after playback ends
      audioRef.current.onended = () => {
        URL.revokeObjectURL(audioUrl)
      }

    } catch (err) {
      console.error('Playback failed:', err)
      setError(err instanceof Error ? err.message : 'Playback failed')
    }
  }

  // Adjust accent position (simplified for new API)
  const handleAccentAdjust = async (lineId: string, phraseIndex: number, newAccent: number) => {
    // Note: The new backend API doesn't support accent adjustment directly
    // This would require regenerating the entire audio with different parameters
    console.log(`Accent adjustment requested for line: ${lineId}, phrase: ${phraseIndex}, accent: ${newAccent}`)
    setError('アクセント調整機能は現在のバックエンドでは利用できません')
  }

  // Insert pause between phrases (simplified for new API)
  const handlePauseInsert = async (lineId: string, phraseIndex: number) => {
    // Note: The new backend API doesn't support pause insertion directly
    // This would require regenerating the entire audio with modified text
    console.log(`Pause insertion requested for line: ${lineId}, phrase: ${phraseIndex}`)
    setError('ポーズ挿入機能は現在のバックエンドでは利用できません')
  }

  // Save all generated audio as WAV
  const handleSaveWav = async () => {
    if (audioCache.size === 0) {
      setError('音声が生成されていません。まずテキストを貼り付けて生成してください。')
      return
    }

    try {
      // For now, save the first cached audio
      // TODO: Merge multiple audio files
      const firstAudio = Array.from(audioCache.values())[0]
      
      if (!firstAudio) return

      // Create download link
      const url = URL.createObjectURL(firstAudio)
      const a = document.createElement('a')
      a.href = url
      a.download = `miovo-reading-${Date.now()}.wav`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      console.log('Audio saved successfully')

    } catch (err) {
      console.error('Save failed:', err)
      setError(err instanceof Error ? err.message : 'Save failed')
    }
  }

  return (
    <div className="grid grid-cols-[1fr_320px] gap-6 h-full">
      {/* Left: Timeline Editor */}
      <div className="flex flex-col">
        {/* Text Input Area */}
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <div className="relative">
            <textarea
              id="text-input"
              className="w-full h-32 p-4 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="ここにテキストを貼り付けてください..."
              onPaste={(e) => {
                const text = e.clipboardData.getData('text')
                if (text) {
                  handleTextPaste(text)
                }
              }}
            />
            <motion.button
              onClick={() => {
                const textarea = document.getElementById('text-input') as HTMLTextAreaElement
                if (textarea && textarea.value.trim()) {
                  handleTextPaste(textarea.value)
                  textarea.value = ''
                }
              }}
              className="absolute bottom-4 right-4 px-4 py-2 bg-primary-600 text-white text-sm rounded-lg font-semibold hover:bg-primary-700 transition-colors"
              whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
              whileTap={shouldReduceMotion ? {} : { scale: 0.95 }}
            >
              生成開始
            </motion.button>
          </div>
        </motion.div>
        
        {/* Play All Controls */}
        <PlayAllControls
          isPlaying={isPlaying}
          isPaused={isPaused}
          currentIndex={currentIndex}
          totalLines={lines.length}
          playbackSpeed={playbackSpeed}
          onPlay={play}
          onPause={pause}
          onStop={stop}
          onSkip={skip}
          onSpeedChange={setPlaybackSpeed}
        />

        {/* Timeline */}
        <TimelineEditor
          lines={lines}
          selectedLineId={selectedLineId}
          playingLineId={playingLineId}
          onLineSelect={setSelectedLineId}
          onLineUpdate={(lineId, text) => {
            setLines(prev => prev.map(line =>
              line.id === lineId ? { ...line, text } : line
            ))
          }}
          onLineGenerate={handleGenerate}
          onLinePlay={handlePlay}
          onAccentEdit={(lineId) => {
            setEditingLineId(lineId)
            console.log('Accent edit mode for line:', lineId)
          }}
        />
      </div>

      {/* Right: Settings Panel */}
      <motion.div
        initial={shouldReduceMotion ? false : { opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex flex-col gap-4"
      >
        {/* Emotion Selection */}
        <div className="p-4 bg-slate-800/50 rounded-lg">
          <h4 className="text-sm font-semibold text-slate-300 mb-3">
            感情スタイル
          </h4>
          {speakersLoading ? (
            <div className="text-sm text-slate-400">読み込み中...</div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {availableStyles.map((emotion, index) => (
                <motion.button
                  key={emotion.id}
                  onClick={() => setSelectedEmotion(emotion)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                    selectedEmotion?.id === emotion.id
                      ? 'bg-primary-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                  whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
                  whileTap={shouldReduceMotion ? {} : { scale: 0.95 }}
                  aria-label={`感情: ${emotion.name}`}
                  aria-pressed={selectedEmotion?.id === emotion.id}
                >
                  <kbd className="text-xs opacity-60 mr-1">{index + 1}</kbd>
                  {emotion.name}
                </motion.button>
              ))}
            </div>
          )}
        </div>

        {/* Audio Settings */}
        <div className="p-4 bg-slate-800/50 rounded-lg">
          <h4 className="text-sm font-semibold text-slate-300 mb-3">
            音声設定
          </h4>
          <div className="space-y-3">
            {/* Speed */}
            <div>
              <label className="text-xs text-slate-400 mb-1 block">
                話速: {audioSettings.speedScale.toFixed(2)}x
              </label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.05"
                value={audioSettings.speedScale}
                onChange={(e) => setAudioSettings(prev => ({
                  ...prev,
                  speedScale: parseFloat(e.target.value)
                }))}
                className="w-full"
              />
            </div>

            {/* Pitch */}
            <div>
              <label className="text-xs text-slate-400 mb-1 block">
                音高: {audioSettings.pitchScale.toFixed(2)}
              </label>
              <input
                type="range"
                min="-1.0"
                max="1.0"
                step="0.05"
                value={audioSettings.pitchScale}
                onChange={(e) => setAudioSettings(prev => ({
                  ...prev,
                  pitchScale: parseFloat(e.target.value)
                }))}
                className="w-full"
              />
            </div>

            {/* Intonation */}
            <div>
              <label className="text-xs text-slate-400 mb-1 block">
                抑揚: {audioSettings.intonationScale.toFixed(2)}
              </label>
              <input
                type="range"
                min="0.0"
                max="2.0"
                step="0.05"
                value={audioSettings.intonationScale}
                onChange={(e) => setAudioSettings(prev => ({
                  ...prev,
                  intonationScale: parseFloat(e.target.value)
                }))}
                className="w-full"
              />
            </div>
          </div>
        </div>

        {/* Export Button */}
        <motion.button
          onClick={handleSaveWav}
          disabled={loading || audioCache.size === 0}
          className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          whileHover={shouldReduceMotion ? {} : { scale: 1.02 }}
          whileTap={shouldReduceMotion ? {} : { scale: 0.98 }}
        >
          {loading ? '生成中...' : 'WAVで保存'}
        </motion.button>
        
        {/* Error display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-3 bg-red-900/20 border border-red-700 rounded-lg text-sm text-red-300"
          >
            {error}
          </motion.div>
        )}
      </motion.div>
      
      {/* Accent Editor Modal */}
      {editingLineId && accentPhrases.has(editingLineId) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setEditingLineId(null)}
        >
          <motion.div
            initial={shouldReduceMotion ? false : { scale: 0.95, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={shouldReduceMotion ? undefined : { scale: 0.95, y: 20 }}
            className="bg-slate-800 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-200">
                アクセント調整
              </h3>
              <button
                onClick={() => setEditingLineId(null)}
                className="text-slate-400 hover:text-slate-200 text-xl"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              {accentPhrases.get(editingLineId)?.map((phrase: any, phraseIndex: number) => (
                <div key={phraseIndex} className="p-3 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs text-slate-400">フレーズ {phraseIndex + 1}</span>
                    <span className="text-sm text-slate-200">
                      {phrase.moras?.map((m: any) => m.text).join('') || ''}
                    </span>
                  </div>
                  
                  {/* Visual accent bar (slider) */}
                  <div className="mb-3">
                    <label className="text-xs text-slate-400 mb-2 block">
                      アクセント位置: {phrase.accent || 0} / {phrase.moras?.length || 0}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max={phrase.moras?.length || 0}
                      value={phrase.accent || 0}
                      onChange={(e) => {
                        const newAccent = parseInt(e.target.value, 10)
                        if (!isNaN(newAccent)) {
                          handleAccentAdjust(editingLineId, phraseIndex, newAccent)
                        }
                      }}
                      className="w-full"
                    />
                  </div>
                  
                  {/* Accent adjustment buttons (up/down arrows) */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        const current = phrase.accent || 0
                        if (current > 0) {
                          handleAccentAdjust(editingLineId, phraseIndex, current - 1)
                        }
                      }}
                      disabled={loading || (phrase.accent || 0) === 0}
                      className="px-3 py-1 bg-slate-600 text-white rounded text-sm hover:bg-slate-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      ▼ 下げる
                    </button>
                    <input
                      type="number"
                      min="0"
                      max={phrase.moras?.length || 0}
                      value={phrase.accent || 0}
                      onChange={(e) => {
                        const newAccent = parseInt(e.target.value, 10)
                        if (!isNaN(newAccent)) {
                          handleAccentAdjust(editingLineId, phraseIndex, newAccent)
                        }
                      }}
                      className="px-2 py-1 bg-slate-600 text-slate-200 rounded text-sm w-20 text-center"
                    />
                    <button
                      onClick={() => {
                        const current = phrase.accent || 0
                        const max = phrase.moras?.length || 0
                        if (current < max) {
                          handleAccentAdjust(editingLineId, phraseIndex, current + 1)
                        }
                      }}
                      disabled={loading || (phrase.accent || 0) >= (phrase.moras?.length || 0)}
                      className="px-3 py-1 bg-slate-600 text-white rounded text-sm hover:bg-slate-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      ▲ 上げる
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Pause insertion UI */}
            <div className="mt-4 p-3 bg-slate-700/30 rounded-lg border border-slate-600">
              <h4 className="text-sm font-semibold text-slate-300 mb-3">
                ポーズ挿入
              </h4>
              <div className="space-y-3">
                {/* Pause type selection */}
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedPauseType('short')}
                    className={`px-3 py-1 rounded text-sm transition-colors ${
                      selectedPauseType === 'short'
                        ? 'bg-green-600 text-white'
                        : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
                    }`}
                  >
                    短（100ms）
                  </button>
                  <button
                    onClick={() => setSelectedPauseType('long')}
                    className={`px-3 py-1 rounded text-sm transition-colors ${
                      selectedPauseType === 'long'
                        ? 'bg-green-600 text-white'
                        : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
                    }`}
                  >
                    長（300ms）
                  </button>
                  <button
                    onClick={() => setSelectedPauseType('custom')}
                    className={`px-3 py-1 rounded text-sm transition-colors ${
                      selectedPauseType === 'custom'
                        ? 'bg-green-600 text-white'
                        : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
                    }`}
                  >
                    任意
                  </button>
                </div>
                
                {/* Custom pause duration */}
                {selectedPauseType === 'custom' && (
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-slate-400">長さ（ms）:</label>
                    <input
                      type="number"
                      min="80"
                      max="3000"
                      step="50"
                      value={customPauseDuration}
                      onChange={(e) => setCustomPauseDuration(parseInt(e.target.value, 10))}
                      className="px-2 py-1 bg-slate-600 text-slate-200 rounded text-sm w-24"
                    />
                  </div>
                )}
                
                {/* Insert pause buttons for each phrase */}
                <div className="text-xs text-slate-400 mb-2">
                  フレーズ後にポーズを挿入:
                </div>
                {accentPhrases.get(editingLineId)?.map((phrase: any, phraseIndex: number) => (
                  <button
                    key={`pause-${phraseIndex}`}
                    onClick={() => handlePauseInsert(editingLineId, phraseIndex)}
                    disabled={loading}
                    className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mr-2 mb-2"
                  >
                    フレーズ{phraseIndex + 1}後
                  </button>
                ))}
              </div>
            </div>
            
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => setEditingLineId(null)}
                className="flex-1 px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors"
              >
                閉じる
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}
