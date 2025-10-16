/**
 * Timeline Editor Component
 * Main component for reading mode text editing
 * M-section compliant: Motion + Reduced Motion support
 */
import { useState, useCallback } from 'react'
import { motion, AnimatePresence, useReducedMotion } from 'motion/react'
import type { ReadingLine } from '../../types/audio'
import { useKeyboardShortcuts } from '@hooks/useKeyboardShortcuts'
import { TimelineLine } from './TimelineLine'

interface TimelineEditorProps {
  lines: ReadingLine[]
  onLineUpdate: (lineId: string, text: string) => void
  onLineSelect: (lineId: string) => void
  onLineGenerate: (lineId: string) => void
  onLinePlay: (lineId: string) => void
  onAccentEdit?: (lineId: string) => void
  selectedLineId?: string
  playingLineId?: string | null
}

export function TimelineEditor({
  lines,
  onLineUpdate,
  onLineSelect,
  onLineGenerate,
  onLinePlay,
  onAccentEdit,
  selectedLineId,
  playingLineId
}: TimelineEditorProps) {
  const shouldReduceMotion = useReducedMotion()
  const [hoveredLineId, setHoveredLineId] = useState<string | null>(null)

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onArrowLeft: () => {
      // Move accent nucleus left
      if (selectedLineId) {
        console.log('Accent left:', selectedLineId)
      }
    },
    onArrowRight: () => {
      // Move accent nucleus right
      if (selectedLineId) {
        console.log('Accent right:', selectedLineId)
      }
    },
    onArrowUp: () => {
      // Select previous line
      if (selectedLineId) {
        const currentIndex = lines.findIndex(l => l.id === selectedLineId)
        if (currentIndex > 0) {
          onLineSelect(lines[currentIndex - 1].id)
        }
      } else if (lines.length > 0) {
        onLineSelect(lines[0].id)
      }
    },
    onArrowDown: () => {
      // Select next line
      if (selectedLineId) {
        const currentIndex = lines.findIndex(l => l.id === selectedLineId)
        if (currentIndex < lines.length - 1) {
          onLineSelect(lines[currentIndex + 1].id)
        }
      } else if (lines.length > 0) {
        onLineSelect(lines[0].id)
      }
    },
    onSpace: () => {
      // Play/pause selected line
      if (selectedLineId) {
        onLinePlay(selectedLineId)
      }
    },
    onNumber: (num) => {
      // Switch emotion/style (1-9)
      console.log('Emotion switch:', num)
    },
    onEnter: () => {
      // Regenerate selected line
      if (selectedLineId) {
        onLineGenerate(selectedLineId)
      }
    }
  })

  const handleLineClick = useCallback((lineId: string) => {
    onLineSelect(lineId)
  }, [onLineSelect])

  return (
    <div className="flex flex-col gap-2 p-4 bg-slate-800/50 rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-200">
          タイムライン
        </h3>
        <div className="text-sm text-slate-400">
          {lines.length} 行
        </div>
      </div>

      {/* Timeline tracks */}
      <div className="space-y-2">
        <AnimatePresence mode="popLayout">
          {lines.map((line, index) => (
            <motion.div
              key={line.id}
              layout={!shouldReduceMotion}
              initial={shouldReduceMotion ? false : { opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={shouldReduceMotion ? undefined : { opacity: 0, scale: 0.95 }}
              transition={{
                layout: { duration: 0.3, ease: [0.25, 0.1, 0.25, 1] },
                opacity: { duration: 0.2 },
                y: { duration: 0.3 }
              }}
              onHoverStart={() => setHoveredLineId(line.id)}
              onHoverEnd={() => setHoveredLineId(null)}
            >
              <TimelineLine
                line={line}
                index={index}
                isSelected={selectedLineId === line.id}
                isHovered={hoveredLineId === line.id}
                isPlaying={playingLineId === line.id}
                onClick={() => handleLineClick(line.id)}
                onUpdate={(text) => onLineUpdate(line.id, text)}
                onGenerate={() => onLineGenerate(line.id)}
                onPlay={() => onLinePlay(line.id)}
                onAccentEdit={onAccentEdit ? () => onAccentEdit(line.id) : undefined}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Empty state */}
      {lines.length === 0 && (
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center py-16 text-center"
        >
          <p className="text-slate-400 mb-2">
            テキストを貼り付けて開始してください
          </p>
          <p className="text-sm text-slate-500">
            自動的に行ごとに分割されます
          </p>
        </motion.div>
      )}

      {/* Keyboard hints */}
      <div className="mt-4 pt-4 border-t border-slate-700">
        <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
          <div>
            <kbd className="px-2 py-1 bg-slate-700 rounded">Space</kbd> 再生/停止
          </div>
          <div>
            <kbd className="px-2 py-1 bg-slate-700 rounded">↑↓</kbd> 行選択
          </div>
          <div>
            <kbd className="px-2 py-1 bg-slate-700 rounded">←→</kbd> アクセント調整
          </div>
          <div>
            <kbd className="px-2 py-1 bg-slate-700 rounded">1-9</kbd> 感情切替
          </div>
        </div>
      </div>
    </div>
  )
}
