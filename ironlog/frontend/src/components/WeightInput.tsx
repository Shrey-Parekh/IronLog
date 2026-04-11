import { useState } from 'react'
import { X } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'motion/react'

interface WeightInputProps {
  value: number
  onChange: (value: number) => void
  unit?: 'kg' | 'lb'
  min?: number
  max?: number
  placeholder?: string
}

export default function WeightInput({ 
  value, 
  onChange, 
  unit = 'kg',
  min = 0,
  max = 500,
  placeholder = '0'
}: WeightInputProps) {
  const [showNumpad, setShowNumpad] = useState(false)
  const [tempValue, setTempValue] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  const handleNumpadClick = (digit: string) => {
    if (digit === '.' && tempValue.includes('.')) return
    if (tempValue.length >= 6) return
    setTempValue(tempValue + digit)
  }

  const handleNumpadBackspace = () => {
    setTempValue(tempValue.slice(0, -1))
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
      {/* Clean Input Field */}
      <motion.button
        type="button"
        className="clean-input"
        onClick={() => {
          setTempValue(value > 0 ? value.toString() : '')
          setShowNumpad(true)
        }}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        whileTap={{ scale: 0.98 }}
        style={{
          width: '100%',
          background: 'var(--bg-raised)',
          border: `2px solid ${isFocused ? 'var(--sage-400)' : 'var(--border-default)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '14px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          transition: 'all 0.2s var(--ease-gentle)',
          boxShadow: isFocused ? 'var(--shadow-focus)' : 'none',
        }}
      >
        <span
          className="type-stat-sm"
          style={{
            color: value > 0 ? 'var(--text-primary)' : 'var(--text-placeholder)',
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '18px',
            fontWeight: 500,
          }}
        >
          {value > 0 ? value : placeholder}
        </span>
        <span
          className="type-caption"
          style={{
            color: 'var(--text-tertiary)',
            fontSize: '12px',
            fontWeight: 600,
          }}
        >
          {unit}
        </span>
      </motion.button>

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
              className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
              onClick={handleNumpadCancel}
            />

            {/* Numpad */}
            <motion.div
              initial={{ y: '100%', opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: '100%', opacity: 0 }}
              transition={{
                type: 'spring',
                damping: 30,
                stiffness: 300,
              }}
              className="fixed bottom-0 left-0 right-0 z-50 bg-bg-raised rounded-t-2xl shadow-xl border-t border-border-subtle"
              style={{
                paddingBottom: 'max(env(safe-area-inset-bottom), 20px)',
              }}
            >
              {/* Drag handle */}
              <div className="w-10 h-1 bg-border-default rounded-full mx-auto mt-3 mb-4" />

              <div className="px-6 pb-6">
                {/* Display */}
                <motion.div
                  className="bg-bg-surface border-2 border-border-subtle rounded-xl p-5 mb-5 min-h-[70px] flex items-center justify-between"
                  animate={{
                    borderColor: tempValue ? 'var(--sage-300)' : 'var(--border-subtle)',
                  }}
                  transition={{ duration: 0.2 }}
                >
                  <span
                    className="type-stat"
                    style={{
                      fontSize: '36px',
                      color: tempValue ? 'var(--text-primary)' : 'var(--text-placeholder)',
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {tempValue || '0'}
                  </span>
                  <span className="type-h3 text-text-tertiary">
                    {unit}
                  </span>
                </motion.div>

                {/* Numpad Grid */}
                <div className="grid grid-cols-3 gap-2 mb-4">
                  {['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0'].map((key) => (
                    <motion.button
                      key={key}
                      type="button"
                      onClick={() => handleNumpadClick(key)}
                      whileHover={{ scale: 1.02, backgroundColor: 'var(--bg-hover)' }}
                      whileTap={{ scale: 0.98 }}
                      className="bg-bg-raised border-2 border-border-default rounded-xl p-4 font-mono text-xl font-medium text-text-primary min-h-[60px] transition-colors"
                    >
                      {key}
                    </motion.button>
                  ))}
                  
                  {/* Backspace button */}
                  <motion.button
                    type="button"
                    onClick={handleNumpadBackspace}
                    whileHover={{ scale: 1.02, backgroundColor: 'var(--bg-hover)' }}
                    whileTap={{ scale: 0.98 }}
                    className="bg-bg-surface border-2 border-border-default rounded-xl p-4 min-h-[60px] flex items-center justify-center text-text-secondary transition-colors"
                  >
                    <X size={24} weight="bold" />
                  </motion.button>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <motion.button
                    type="button"
                    onClick={handleNumpadCancel}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    className="flex-1 bg-transparent border-2 border-border-default text-text-primary font-semibold py-4 rounded-xl transition-all hover:bg-bg-hover hover:border-border-strong"
                  >
                    Cancel
                  </motion.button>
                  <motion.button
                    type="button"
                    onClick={handleNumpadConfirm}
                    disabled={!tempValue || isNaN(parseFloat(tempValue))}
                    whileHover={{ scale: tempValue ? 1.01 : 1 }}
                    whileTap={{ scale: tempValue ? 0.99 : 1 }}
                    className="flex-1 bg-sage-500 text-text-inverse font-semibold py-4 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:bg-sage-600 shadow-sm hover:shadow-md"
                  >
                    Confirm
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
