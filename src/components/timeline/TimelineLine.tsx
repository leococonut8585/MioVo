/**
 * Timeline Line Component
 * Individual line in timeline editor
 */
import { motion, useReducedMotion } from 'motion/react'
import type { ReadingLine } from '../../types/audio'
import { clsx } from 'clsx'

interface TimelineLineProps {
  line: ReadingLine
  index: number
  isSelected: boolean
  isHovered: boolean
  onClick: () => void
  onUpdate: (text: string) => void
  onGenerate: () => void
  onPlay: () => void
  onAccentEdit?: () => void
}

export function TimelineLine({
  line,
  index,
  isSelected,
  isHovered: _isHovered,
  onClick,
  onGenerate,
  onPlay,
  onAccentEdit
}: TimelineLineProps) {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      className={clsx(
        'group relative p-4 rounded-lg border transition-colors cursor-pointer',
        isSelected
          ? 'border-primary-500 bg-primary-900/20'
          : 'border-slate-700 bg-slate-800 hover:border-slate-600 hover:bg-slate-750'
      )}
      onClick={onClick}
      whileHover={shouldReduceMotion ? {} : { scale: 1.01 }}
      whileTap={shouldReduceMotion ? {} : { scale: 0.99 }}
      transition={{ duration: 0.15 }}
    >
      {/* Line number */}
      <div className="absolute top-2 left-2 text-xs text-slate-500 font-mono">
        #{index + 1}
      </div>

      {/* Text content */}
      <div className="pl-8 pr-20">
        <p className="text-slate-200 leading-relaxed">
          {line.text}
        </p>
      </div>

      {/* Action buttons */}
      <div className={clsx(
        'absolute top-2 right-2 flex gap-1',
        'opacity-0 group-hover:opacity-100 transition-opacity'
      )}>
        <motion.button
          onClick={(e) => {
            e.stopPropagation()
            onPlay()
          }}
          className="px-2 py-1 text-xs bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
          whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
          whileTap={shouldReduceMotion ? {} : { scale: 0.95 }}
          aria-label="再生"
        >
          ▶
        </motion.button>
        
        <motion.button
          onClick={(e) => {
            e.stopPropagation()
            onGenerate()
          }}
          className="px-2 py-1 text-xs bg-slate-600 text-white rounded hover:bg-slate-700 transition-colors"
          whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
          whileTap={shouldReduceMotion ? {} : { scale: 0.95 }}
          aria-label="再生成"
        >
          🔄
        </motion.button>
        
        {onAccentEdit && (
          <motion.button
            onClick={(e) => {
              e.stopPropagation()
              onAccentEdit()
            }}
            className="px-2 py-1 text-xs bg-amber-600 text-white rounded hover:bg-amber-700 transition-colors"
            whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
            whileTap={shouldReduceMotion ? {} : { scale: 0.95 }}
            aria-label="アクセント調整"
          >
            A
          </motion.button>
        )}
      </div>

      {/* Status indicator */}
      {line.chunk && (
        <div className="absolute bottom-2 right-2">
          <div className={clsx(
            'w-2 h-2 rounded-full',
            line.chunk.status === 'done' && 'bg-green-500',
            line.chunk.status === 'processing' && 'bg-yellow-500 animate-pulse',
            line.chunk.status === 'error' && 'bg-red-500',
            line.chunk.status === 'pending' && 'bg-slate-600'
          )} />
        </div>
      )}
    </motion.div>
  )
}
