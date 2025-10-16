/**
 * PlayAllControls Component
 * Controls for playing all timeline items continuously
 */
import { motion, useReducedMotion } from 'motion/react'

interface PlayAllControlsProps {
  isPlaying: boolean
  isPaused: boolean
  currentIndex: number
  totalLines: number
  playbackSpeed: number
  onPlay: () => void
  onPause: () => void
  onStop: () => void
  onSkip: () => void
  onSpeedChange: (speed: number) => void
}

export function PlayAllControls({
  isPlaying,
  isPaused,
  currentIndex,
  totalLines,
  playbackSpeed,
  onPlay,
  onPause,
  onStop,
  onSkip,
  onSpeedChange
}: PlayAllControlsProps) {
  const shouldReduceMotion = useReducedMotion()
  const progress = totalLines > 0 ? ((currentIndex + 1) / totalLines) * 100 : 0
  
  const speedOptions = [1.0, 1.25, 1.5, 2.0]
  
  return (
    <motion.div
      initial={shouldReduceMotion ? false : { opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-lg mb-4"
    >
      {/* Play/Pause/Stop buttons */}
      <div className="flex items-center gap-2">
        {!isPlaying ? (
          <motion.button
            onClick={onPlay}
            disabled={totalLines === 0}
            className="flex items-center justify-center w-10 h-10 bg-primary-600 text-white rounded-full hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
            whileTap={shouldReduceMotion ? {} : { scale: 0.95 }}
            aria-label="すべて再生"
            title="すべて再生 (Space)"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 4.5a1 1 0 00-1 1v9a1 1 0 001.707.707l8-4.5a1 1 0 000-1.414l-8-4.5A1 1 0 005 4.5z" />
            </svg>
          </motion.button>
        ) : (
          <>
            {/* Pause button */}
            <motion.button
              onClick={isPaused ? onPlay : onPause}
              className="flex items-center justify-center w-10 h-10 bg-yellow-600 text-white rounded-full hover:bg-yellow-700 transition-colors"
              whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
              whileTap={shouldReduceMotion ? {} : { scale: 0.95 }}
              aria-label={isPaused ? "再開" : "一時停止"}
              title={isPaused ? "再開 (Space)" : "一時停止 (Space)"}
            >
              {isPaused ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5 4.5a1 1 0 00-1 1v9a1 1 0 001.707.707l8-4.5a1 1 0 000-1.414l-8-4.5A1 1 0 005 4.5z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6 4a1 1 0 011 1v10a1 1 0 11-2 0V5a1 1 0 011-1zm7 0a1 1 0 011 1v10a1 1 0 11-2 0V5a1 1 0 011-1z" />
                </svg>
              )}
            </motion.button>
            
            {/* Stop button */}
            <motion.button
              onClick={onStop}
              className="flex items-center justify-center w-10 h-10 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors"
              whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
              whileTap={shouldReduceMotion ? {} : { scale: 0.95 }}
              aria-label="停止"
              title="停止 (Esc)"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <rect x="6" y="6" width="8" height="8" />
              </svg>
            </motion.button>
          </>
        )}
        
        {/* Skip button */}
        <motion.button
          onClick={onSkip}
          disabled={!isPlaying || currentIndex >= totalLines - 1}
          className="flex items-center justify-center w-10 h-10 bg-slate-700 text-white rounded-full hover:bg-slate-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
          whileTap={shouldReduceMotion ? {} : { scale: 0.95 }}
          aria-label="次へスキップ"
          title="次へスキップ (→)"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M13.586 10l-5.793 5.793a1 1 0 001.414 1.414l6.5-6.5a1 1 0 000-1.414l-6.5-6.5a1 1 0 00-1.414 1.414L13.586 10z" />
          </svg>
        </motion.button>
      </div>
      
      {/* Progress indicator */}
      <div className="flex-1">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span>
            {isPlaying ? `再生中: ${currentIndex + 1} / ${totalLines}` : 'すべて再生'}
          </span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="relative h-2 bg-slate-700 rounded-full overflow-hidden">
          <motion.div
            className="absolute inset-y-0 left-0 bg-primary-500"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          />
        </div>
      </div>
      
      {/* Speed control */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-slate-400">速度:</span>
        <select
          value={playbackSpeed}
          onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
          className="px-2 py-1 bg-slate-700 text-slate-200 text-sm rounded border border-slate-600 focus:outline-none focus:ring-2 focus:ring-primary-500"
          aria-label="再生速度"
        >
          {speedOptions.map(speed => (
            <option key={speed} value={speed}>
              {speed}x
            </option>
          ))}
        </select>
      </div>
    </motion.div>
  )
}