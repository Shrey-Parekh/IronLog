import { useState } from 'react'
import { Minus, Plus, X } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'motion/react'

interface WeightInputProps {
  value: number
  onChange: (value: number) => void
  unit?: 'kg' | 'lb'
  min?: number
  max?: number
}

export default function WeightInput({ 
  value, 
  onChange, 
  unit = 'kg',
  min = 0,
  max = 500 
}: WeightInputProps) {
  const [showNumpad, setShowNumpad] = useState(false)
  const [tempValue, setTempValue] = useState('')

  const adjustWeight = (delta: number) => {
    const newValue = Math.max(min, Math.min(max, value + delta))
    onChange(Number(newValue.toFixed(1)))
  }

  const handleNumpadClick = (digit: string) => {
    if (digit === '.' && tempValue.includes('.')) return
    if (tempValue.length >= 6) return
    setTempValue(tempValue + digit)
  }

  const handleNumpadClear = () => {
    setTempValue('')
  }

  const handleNumpadConfirm = () => {
    const numValue = parseFloat(tempValue)
    if (!isNaN(numValue) && numValue >= min && numValue <= max) {
      onChange(Number(numValue.toFixed(1)))
    }
    setTempValue('')
    setShowNumpad(false)
  }

  const handleNumpadCancel = () => {
    setTempValue('')
    setShowNumpad(false)
  }

  return (
    <>
      <div className="weight-adjuster">
        <button
          type="button"
          className="weight-adjuster-btn"
          onClick={() => adjustWeight(-5)}
        >
          −5
        </button>
        <button
          type="button"
          className="weight-adjuster-btn"
          onClick={() => adjustWeight(-2.5)}
        >
          −2.5
        </button>
        <button
          type="button"
          className="weight-display"
          onClick={() => {
            setTempValue(value.toString())
            setShowNumpad(true)
          }}
        >
          {value}
        </button>
        <button
          type="button"
          className="weight-adjuster-btn"
          onClick={() => adjustWeight(2.5)}
        >
          +2.5
        </button>
        <button
          type="button"
          className="weight-adjuster-btn"
          onClick={() => adjustWeight(5)}
        >
          +5
        </button>
      </div>

      {/* Numpad Modal */}
      <AnimatePresence>
        {showNumpad && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 z-50"
              style={{ background: 'rgba(0, 0, 0, 0.4)' }}
              onClick={handleNumpadCancel}
            />

            {/* Numpad */}
            <motion.div
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{
                type: 'spring',
                damping: 35,
                stiffness: 350,
                mass: 0.8,
              }}
              className="fixed bottom-0 left-0 right-0 z-50"
              style={{
                background: 'var(--bg-raised)',
                borderRadius: '20px 20px 0 0',
                boxShadow: 'var(--shadow-lg)',
                borderTop: '1px solid var(--border-subtle)',
                paddingBottom: 'env(safe-area-inset-bottom, 0px)',
              }}
            >
              {/* Drag handle */}
              <div
                style={{
                  width: 36,
                  height: 4,
                  borderRadius: 2,
                  background: 'var(--border-default)',
                  margin: '10px auto 0',
                }}
              />

              <div style={{ padding: 'var(--space-6)' }}>
                {/* Display */}
                <div
                  style={{
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: 'var(--space-4)',
                    marginBottom: 'var(--space-4)',
                    minHeight: '60px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <span
                    className="type-stat"
                    style={{
                      fontSize: '32px',
                      color: tempValue ? 'var(--text-primary)' : 'var(--text-placeholder)',
                    }}
                  >
                    {tempValue || '0'}
                  </span>
                  <span className="type-body-sm" style={{ color: 'var(--text-tertiary)' }}>
                    {unit}
                  </span>
                </div>

                {/* Numpad Grid */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: 'var(--space-2)',
                    marginBottom: 'var(--space-4)',
                  }}
                >
                  {['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', 'C'].map((key) => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => {
                        if (key === 'C') {
                          handleNumpadClear()
                        } else {
                          handleNumpadClick(key)
                        }
                      }}
                      style={{
                        background: key === 'C' ? 'var(--bg-surface)' : 'var(--bg-raised)',
                        border: '1px solid var(--border-default)',
                        borderRadius: 'var(--radius-md)',
                        padding: 'var(--space-4)',
                        fontFamily: "'DM Mono', monospace",
                        fontSize: '20px',
                        fontWeight: 500,
                        color: key === 'C' ? 'var(--danger-text)' : 'var(--text-primary)',
                        cursor: 'pointer',
                        transition: 'all var(--duration-fast) var(--ease-gentle)',
                        minHeight: '56px',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'var(--bg-hover)'
                        e.currentTarget.style.borderColor = 'var(--border-strong)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background =
                          key === 'C' ? 'var(--bg-surface)' : 'var(--bg-raised)'
                        e.currentTarget.style.borderColor = 'var(--border-default)'
                      }}
                    >
                      {key}
                    </button>
                  ))}
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={handleNumpadCancel}
                    style={{ flex: 1 }}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="btn-primary"
                    onClick={handleNumpadConfirm}
                    style={{ flex: 1 }}
                    disabled={!tempValue || isNaN(parseFloat(tempValue))}
                  >
                    Confirm
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
