/**
 * Keyboard shortcuts hook
 * Handles Arrow keys, Space, Number keys for MioVo
 */
import { useEffect, useCallback } from 'react'

export interface KeyboardShortcutHandlers {
  onArrowLeft?: () => void
  onArrowRight?: () => void
  onArrowUp?: () => void
  onArrowDown?: () => void
  onSpace?: () => void
  onNumber?: (num: number) => void  // 1-9
  onEscape?: () => void
  onEnter?: () => void
}

export function useKeyboardShortcuts(
  handlers: KeyboardShortcutHandlers,
  enabled: boolean = true
) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return

      // Ignore if typing in input/textarea
      const target = event.target as HTMLElement
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return
      }

      // Handle shortcuts
      switch (event.key) {
        case 'ArrowLeft':
          event.preventDefault()
          handlers.onArrowLeft?.()
          break
          
        case 'ArrowRight':
          event.preventDefault()
          handlers.onArrowRight?.()
          break
          
        case 'ArrowUp':
          event.preventDefault()
          handlers.onArrowUp?.()
          break
          
        case 'ArrowDown':
          event.preventDefault()
          handlers.onArrowDown?.()
          break
          
        case ' ':
        case 'Space':
          event.preventDefault()
          handlers.onSpace?.()
          break
          
        case 'Escape':
          event.preventDefault()
          handlers.onEscape?.()
          break
          
        case 'Enter':
          if (!event.shiftKey) {
            // Shift+Enter allows line breaks in textarea
            event.preventDefault()
            handlers.onEnter?.()
          }
          break
          
        default:
          // Number keys 1-9
          if (event.key >= '1' && event.key <= '9') {
            event.preventDefault()
            const num = parseInt(event.key, 10)
            handlers.onNumber?.(num)
          }
          break
      }
    },
    [handlers, enabled]
  )

  useEffect(() => {
    if (!enabled) return

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown, enabled])
}
