import { useEffect, useState } from 'react'
import { Timer, X, Plus, Minus } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'motion/react'

interface RestTimerProps {
  isActive: boolean
  initialSeconds?: number
  onComplete?: () => void
  onDismiss?: () => void
}

export default function RestTimer({
  isActive,
  initialSeconds = 90,
  onComplete,
  onDismiss,
}: RestTimerProps) {
  const [timeLeft, setTimeLeft] = useState(initialSeconds)
  const [isPaused, setIsPaused] = useState(false)
  const [targetTime, setTargetTime] = useState(initialSeconds)

  useEffect(() => {
    if (isActive) {
      setTimeLeft(initialSeconds)
      setTargetTime(initialSeconds)
      setIsPaused(false)
    }
  }, [isActive, initialSeconds])

  useEffect(() => {
    if (!isActive || isPaused || timeLeft <= 0) return

    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          onComplete?.()
          // Play notification sound (optional)
          if ('vibrate' in navigator) {
            navigator.vibrate([200, 100, 200])
          }
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [isActive, isPaused, timeLeft, onComplete])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const adjustTime = (delta: number) => {
    const newTime = Math.max(0, Math.min(600, timeLeft + delta))
    setTimeLeft(newTime)
    setTargetTime(newTime)
  }

  const progress = targetTime > 0 ? (timeLeft / targetTime) * 100 : 0

  return (
    <AnimatePresence>
      {isActive && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{
            type: 'spring',
            damping: 25,
            stiffness: 300,
          }}
          style={{
            position: 'fixed',
            bottom: 'calc(52px + env(safe-area-inset-bottom, 0px) + 16px)',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 50,
            width: 'calc(100% - 32px)',
            maxWidth: '400px',
          }}
        >
          <div
            style={{
              background: 'var(--bg-raised)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-lg)',
              padding: 'var(--space-4)',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* Progress Bar */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                height: '3px',
                width: `${progress}%`,
                background: timeLeft <= 10 ? 'var(--danger-icon)' : 'var(--sage-400)',
                transition: 'width 1s linear, background 0.3s ease',
              }}
            />

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
              {/* Timer Icon */}
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: 'var(--radius-sm)',
                  background: timeLeft <= 10 ? 'var(--danger-bg)' : 'var(--sage-50)',
                  border: `1px solid ${timeLeft <= 10 ? 'var(--danger-border)' : 'var(--sage-200)'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <Timer
                  size={22}
                  weight="light"
                  color={timeLeft <= 10 ? 'var(--danger-icon)' : 'var(--sage-500)'}
                />
              </div>

              {/* Time Display */}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <span
                    className="type-stat tabular-nums"
                    style={{
                      fontSize: '28px',
                      color: timeLeft <= 10 ? 'var(--danger-text)' : 'var(--text-primary)',
                    }}
                  >
                    {formatTime(timeLeft)}
                  </span>
                  <button
                    type="button"
                    className="btn-ghost"
                    style={{ padding: '4px 8px', fontSize: '12px' }}
                    onClick={() => setIsPaused(!isPaused)}
                  >
                    {isPaused ? 'Resume' : 'Pause'}
                  </button>
                </div>
                <p className="type-caption" style={{ marginTop: '2px' }}>
                  {timeLeft === 0 ? 'Rest complete!' : 'Rest timer'}
                </p>
              </div>

              {/* Adjust Buttons */}
              <div style={{ display: 'flex', gap: 'var(--space-1)' }}>
                <button
                  type="button"
                  className="btn-icon"
                  style={{ width: '32px', height: '32px' }}
                  onClick={() => adjustTime(-15)}
                >
                  <Minus size={16} weight="bold" />
                </button>
                <button
                  type="button"
                  className="btn-icon"
                  style={{ width: '32px', height: '32px' }}
                  onClick={() => adjustTime(15)}
                >
                  <Plus size={16} weight="bold" />
                </button>
              </div>

              {/* Close Button */}
              <button
                type="button"
                className="btn-icon"
                style={{ width: '32px', height: '32px' }}
                onClick={onDismiss}
              >
                <X size={18} weight="bold" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
