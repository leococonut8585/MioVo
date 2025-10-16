/**
 * usePlayAll Hook
 * Manages continuous playback of all timeline items
 */
import { useState, useRef, useCallback, useEffect } from 'react'
import type { ReadingLine, AudioSettings, EmotionStyle } from '../types/audio'

interface UsePlayAllOptions {
  lines: ReadingLine[]
  audioSettings: AudioSettings
  selectedEmotion: EmotionStyle | null
  onLineHighlight?: (lineId: string | null) => void
  onAutoScroll?: (lineId: string) => void
}

interface UsePlayAllReturn {
  isPlaying: boolean
  isPaused: boolean
  currentIndex: number
  playbackSpeed: number
  play: () => Promise<void>
  pause: () => void
  stop: () => void
  skip: () => void
  setPlaybackSpeed: (speed: number) => void
}

export function usePlayAll({
  lines,
  audioSettings,
  selectedEmotion,
  onLineHighlight,
  onAutoScroll
}: UsePlayAllOptions): UsePlayAllReturn {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0)
  
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const audioQueueRef = useRef<Blob[]>([])
  const abortControllerRef = useRef<AbortController | null>(null)
  const isGeneratingRef = useRef(false)
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])
  
  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.code === 'Space' && !e.target || !(e.target as HTMLElement).matches('input, textarea')) {
        e.preventDefault()
        if (isPlaying) {
          if (isPaused) {
            play()
          } else {
            pause()
          }
        } else if (lines.length > 0) {
          play()
        }
      } else if (e.code === 'Escape' && isPlaying) {
        stop()
      } else if (e.code === 'ArrowRight' && isPlaying) {
        skip()
      }
    }
    
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [isPlaying, isPaused, lines.length])
  
  // Generate audio for a single line
  const generateAudioForLine = async (line: ReadingLine, signal: AbortSignal): Promise<Blob | null> => {
    if (!selectedEmotion) return null
    
    try {
      // Create audio query
      const queryParams = new URLSearchParams({
        text: line.text,
        speaker: selectedEmotion.speakerId.toString()
      })
      
      const queryResponse = await fetch(
        `http://localhost:10101/audio_query?${queryParams}`,
        { 
          method: 'POST',
          signal 
        }
      )
      
      if (!queryResponse.ok) {
        throw new Error(`Audio query failed: ${queryResponse.statusText}`)
      }
      
      const audioQuery = await queryResponse.json()
      
      // Apply audio settings with speed adjustment
      audioQuery.speedScale = audioSettings.speedScale * playbackSpeed
      audioQuery.pitchScale = audioSettings.pitchScale
      audioQuery.intonationScale = audioSettings.intonationScale
      audioQuery.volumeScale = audioSettings.volumeScale
      
      // Synthesize speech
      const synthesisParams = new URLSearchParams({
        speaker: selectedEmotion.speakerId.toString()
      })
      
      const synthesisResponse = await fetch(
        `http://localhost:10101/synthesis?${synthesisParams}`,
        {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json; charset=utf-8',
            'accept': 'audio/wav'
          },
          body: JSON.stringify(audioQuery),
          signal
        }
      )
      
      if (!synthesisResponse.ok) {
        throw new Error(`Synthesis failed: ${synthesisResponse.statusText}`)
      }
      
      return await synthesisResponse.blob()
      
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        console.log('Audio generation aborted')
        return null
      }
      console.error('Failed to generate audio for line:', err)
      return null
    }
  }
  
  // Generate all audio in batch
  const generateAllAudio = async (signal: AbortSignal): Promise<Blob[]> => {
    const audioBlobs: Blob[] = []
    isGeneratingRef.current = true
    
    try {
      // Generate audio for each line
      for (let i = 0; i < lines.length; i++) {
        if (signal.aborted) break
        
        const blob = await generateAudioForLine(lines[i], signal)
        if (blob) {
          audioBlobs.push(blob)
        }
      }
    } finally {
      isGeneratingRef.current = false
    }
    
    return audioBlobs
  }
  
  // Play next audio in queue
  const playNextAudio = useCallback(async () => {
    if (currentIndex >= audioQueueRef.current.length) {
      stop()
      return
    }
    
    const audioBlob = audioQueueRef.current[currentIndex]
    if (!audioBlob) {
      setCurrentIndex(prev => prev + 1)
      setTimeout(playNextAudio, 100)
      return
    }
    
    // Highlight current line
    const currentLine = lines[currentIndex]
    if (currentLine) {
      onLineHighlight?.(currentLine.id)
      onAutoScroll?.(currentLine.id)
    }
    
    // Create or reuse audio element
    if (!audioRef.current) {
      audioRef.current = new Audio()
    }
    
    // Set up audio element
    const audioUrl = URL.createObjectURL(audioBlob)
    audioRef.current.src = audioUrl
    audioRef.current.playbackRate = 1.0 // Speed is already applied during synthesis
    
    // Handle audio end
    audioRef.current.onended = () => {
      URL.revokeObjectURL(audioUrl)
      if (isPlaying && !isPaused) {
        setCurrentIndex(prev => prev + 1)
        playNextAudio()
      }
    }
    
    // Play audio
    try {
      await audioRef.current.play()
    } catch (err) {
      console.error('Failed to play audio:', err)
      stop()
    }
  }, [currentIndex, isPlaying, isPaused, lines, onLineHighlight, onAutoScroll])
  
  // Play all lines
  const play = useCallback(async () => {
    if (lines.length === 0) return
    
    // Resume if paused
    if (isPaused && audioRef.current) {
      audioRef.current.play()
      setIsPaused(false)
      return
    }
    
    // Start new playback
    if (!isPlaying) {
      setIsPlaying(true)
      setIsPaused(false)
      setCurrentIndex(0)
      
      // Create abort controller
      abortControllerRef.current = new AbortController()
      
      // Generate all audio
      try {
        const audioBlobs = await generateAllAudio(abortControllerRef.current.signal)
        audioQueueRef.current = audioBlobs
        
        if (audioBlobs.length > 0) {
          playNextAudio()
        } else {
          stop()
        }
      } catch (err) {
        console.error('Failed to generate audio:', err)
        stop()
      }
    }
  }, [lines, isPaused, isPlaying, playNextAudio])
  
  // Pause playback
  const pause = useCallback(() => {
    if (audioRef.current && isPlaying) {
      audioRef.current.pause()
      setIsPaused(true)
    }
  }, [isPlaying])
  
  // Stop playback
  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current = null
    }
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    
    setIsPlaying(false)
    setIsPaused(false)
    setCurrentIndex(0)
    audioQueueRef.current = []
    onLineHighlight?.(null)
  }, [onLineHighlight])
  
  // Skip to next line
  const skip = useCallback(() => {
    if (!isPlaying || currentIndex >= lines.length - 1) return
    
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    
    setCurrentIndex(prev => Math.min(prev + 1, lines.length - 1))
    setTimeout(playNextAudio, 100)
  }, [isPlaying, currentIndex, lines.length, playNextAudio])
  
  return {
    isPlaying,
    isPaused,
    currentIndex,
    playbackSpeed,
    play,
    pause,
    stop,
    skip,
    setPlaybackSpeed
  }
}