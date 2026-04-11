import { useState } from 'react'
import { Check, Minus, Plus } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'motion/react'
import WeightInput from './WeightInput'

interface SetLoggerRowProps {
  setNumber: number
  weight: number
  reps: number
  rpe?: number
  isLogged: boolean
  isPR?: boolean
  onWeightChange: (weight: number) => void
  onRepsChange: (reps: number) => void
  onRPEChange: (rpe: number | undefined) => void
  onLog: () => void
}

const RPE_VALUES = [6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]

export default function SetLoggerRow({
  setNumber,
  weight,
  reps,
  rpe,
  isLogged,
  isPR,
  onWeightChange,
  onRepsChange,
  onRPEChange,
  onLog,
}: SetLoggerRowProps) {
  const [showRPEPicker, setShowRPEPicker] = useState(false)
  const [isFocused, setIsFocused] = useState<'reps' | null>(null)

  const handleRepsAdjust = (delta: number) => {
    const newReps = Math.max(1, Math.min(50, reps + delta))
    onRepsChange(newReps)
  }

  return (
    <motion.div
      className="relative"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
    >
      <div
        className={`
          grid grid-cols-[40px_1fr_1fr_80px_48px] gap-3 items-center p-4 rounded-xl
          transition-all duration-200
          ${isLogged 
            ? 'bg-bg-surface border-2 border-border-subtle opacity-70' 
            : 'bg-bg-raised border-2 border-border-default hover:border-sage-300'
          }
          ${isPR ? 'ring-2 ring-clay-400 ring-offset-2' : ''}
        `}
      >
        {/* Set Number */}
        <div className="flex items-center justify-center">
          <span className="type-h3 text-text-secondary font-semibold">
            {setNumber}
          </span>
        </div>

        {/* Weight */}
        <div>
          {isLogged ? (
            <div className="flex items-baseline gap-1">
              <span className="type-stat-sm tabular-nums text-text-primary">
                {weight}
              </span>
              <span className="type-caption text-text-tertiary">kg</span>
            </div>
          ) : (
            <WeightInput value={weight} onChange={onWeightChange} placeholder="Weight" />
          )}
        </div>

        {/* Reps */}
        <div>
          {isLogged ? (
            <div className="flex items-baseline gap-1">
              <span className="type-stat-sm tabular-nums text-text-primary">
                {reps}
              </span>
              <span className="type-caption text-text-tertiary">reps</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <motion.button
                type="button"
                onClick={() => handleRepsAdjust(-1)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="w-8 h-8 rounded-lg bg-bg-surface border-2 border-border-default flex items-center justify-center text-text-secondary hover:border-sage-300 hover:text-sage-600 transition-colors"
              >
                <Minus size={16} weight="bold" />
              </motion.button>
              
              <input
                type="number"
                value={reps}
                onChange={(e) => onRepsChange(Math.max(1, parseInt(e.target.value) || 1))}
                onFocus={() => setIsFocused('reps')}
                onBlur={() => setIsFocused(null)}
                className="w-16 h-10 text-center bg-bg-raised border-2 border-border-default rounded-lg font-mono text-lg font-medium text-text-primary focus:border-sage-400 focus:ring-2 focus:ring-sage-200 transition-all outline-none"
                style={{
                  appearance: 'textfield',
                }}
              />
              
              <motion.button
                type="button"
                onClick={() => handleRepsAdjust(1)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="w-8 h-8 rounded-lg bg-bg-surface border-2 border-border-default flex items-center justify-center text-text-secondary hover:border-sage-300 hover:text-sage-600 transition-colors"
              >
                <Plus size={16} weight="bold" />
              </motion.button>
            </div>
          )}
        </div>

        {/* RPE */}
        <div className="relative">
          {isLogged ? (
            <span className="type-body-sm text-text-secondary">
              {rpe ? `RPE ${rpe}` : '—'}
            </span>
          ) : (
            <>
              <motion.button
                type="button"
                onClick={() => setShowRPEPicker(!showRPEPicker)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`
                  w-full h-10 rounded-lg border-2 font-medium text-sm transition-all
                  ${rpe 
                    ? 'bg-powder-50 border-powder-300 text-powder-700' 
                    : 'bg-bg-surface border-border-default text-text-tertiary hover:border-border-strong'
                  }
                `}
              >
                {rpe ? `RPE ${rpe}` : 'RPE'}
              </motion.button>

              {/* RPE Picker Dropdown */}
              <AnimatePresence>
                {showRPEPicker && (
                  <>
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="fixed inset-0 z-40"
                      onClick={() => setShowRPEPicker(false)}
                    />
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                      className="absolute bottom-full right-0 mb-2 bg-bg-raised border-2 border-border-subtle rounded-xl shadow-lg p-2 z-50 min-w-[160px]"
                    >
                      <div className="grid grid-cols-3 gap-1 mb-1">
                        {RPE_VALUES.map((value) => (
                          <motion.button
                            key={value}
                            type="button"
                            onClick={() => {
                              onRPEChange(value)
                              setShowRPEPicker(false)
                            }}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className={`
                              h-9 rounded-lg font-medium text-sm transition-all
                              ${rpe === value 
                                ? 'bg-powder-500 text-white' 
                                : 'bg-bg-surface text-text-primary hover:bg-powder-50 hover:text-powder-700'
                              }
                            `}
                          >
                            {value}
                          </motion.button>
                        ))}
                      </div>
                      <motion.button
                        type="button"
                        onClick={() => {
                          onRPEChange(undefined)
                          setShowRPEPicker(false)
                        }}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="w-full h-9 rounded-lg bg-bg-surface text-text-tertiary text-xs font-medium hover:bg-bg-hover transition-colors"
                      >
                        Clear
                      </motion.button>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </>
          )}
        </div>

        {/* Log Button */}
        <div>
          {!isLogged ? (
            <motion.button
              type="button"
              onClick={onLog}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="w-12 h-12 rounded-xl bg-sage-500 text-white flex items-center justify-center shadow-sm hover:bg-sage-600 hover:shadow-md transition-all"
            >
              <Check size={24} weight="bold" />
            </motion.button>
          ) : (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', damping: 15, stiffness: 300 }}
              className="w-12 h-12 rounded-xl bg-sage-50 border-2 border-sage-300 flex items-center justify-center"
            >
              <Check size={24} weight="bold" className="text-sage-600" />
            </motion.div>
          )}
        </div>
      </div>

      {/* PR Badge */}
      <AnimatePresence>
        {isPR && (
          <motion.div
            initial={{ scale: 0, rotate: -12 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 12 }}
            transition={{ type: 'spring', damping: 12, stiffness: 300 }}
            className="absolute -top-2 -right-2 bg-clay-400 text-white px-3 py-1 rounded-full text-xs font-bold shadow-md z-10"
          >
            🎉 PR!
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

/* Hide number input spinners */
<style jsx>{`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
`}</style>
