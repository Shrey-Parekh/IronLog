import { useState } from 'react'
import { Check } from '@phosphor-icons/react'
import { motion } from 'motion/react'
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

  const handleRepsAdjust = (delta: number) => {
    const newReps = Math.max(1, Math.min(50, reps + delta))
    onRepsChange(newReps)
  }

  return (
    <motion.div
      className={`set-row ${isLogged ? 'set-row-logged' : 'set-row-active'} ${isPR ? 'set-row-pr' : ''}`}
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
    >
      {/* Set Number */}
      <div className="set-number">{setNumber}</div>

      {/* Weight */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {isLogged ? (
          <span className="type-stat-sm tabular-nums">{weight} kg</span>
        ) : (
          <WeightInput value={weight} onChange={onWeightChange} />
        )}
      </div>

      {/* Reps */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {isLogged ? (
          <span className="type-stat-sm tabular-nums">{reps}</span>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <button
              type="button"
              className="btn-icon"
              style={{ width: '28px', height: '28px' }}
              onClick={() => handleRepsAdjust(-1)}
            >
              −
            </button>
            <input
              type="number"
              value={reps}
              onChange={(e) => onRepsChange(Math.max(1, parseInt(e.target.value) || 1))}
              className="input-numeric"
              style={{ width: '50px', fontSize: '15px' }}
            />
            <button
              type="button"
              className="btn-icon"
              style={{ width: '28px', height: '28px' }}
              onClick={() => handleRepsAdjust(1)}
            >
              +
            </button>
          </div>
        )}
      </div>

      {/* RPE */}
      <div style={{ position: 'relative' }}>
        {isLogged ? (
          <span className="type-stat-sm tabular-nums">{rpe || '—'}</span>
        ) : (
          <>
            <button
              type="button"
              className={`rpe-pill ${rpe ? 'rpe-pill-selected' : ''}`}
              onClick={() => setShowRPEPicker(!showRPEPicker)}
            >
              {rpe || 'RPE'}
            </button>

            {/* RPE Picker Dropdown */}
            {showRPEPicker && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.15 }}
                style={{
                  position: 'absolute',
                  bottom: '100%',
                  right: 0,
                  marginBottom: '8px',
                  background: 'var(--bg-raised)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  boxShadow: 'var(--shadow-md)',
                  padding: 'var(--space-2)',
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: 'var(--space-1)',
                  zIndex: 10,
                  minWidth: '140px',
                }}
              >
                {RPE_VALUES.map((value) => (
                  <button
                    key={value}
                    type="button"
                    className={`rpe-pill ${rpe === value ? 'rpe-pill-selected' : ''}`}
                    onClick={() => {
                      onRPEChange(value)
                      setShowRPEPicker(false)
                    }}
                    style={{ fontSize: '12px' }}
                  >
                    {value}
                  </button>
                ))}
                <button
                  type="button"
                  className="rpe-pill"
                  onClick={() => {
                    onRPEChange(undefined)
                    setShowRPEPicker(false)
                  }}
                  style={{ fontSize: '11px', gridColumn: 'span 3' }}
                >
                  Clear
                </button>
              </motion.div>
            )}
          </>
        )}
      </div>

      {/* Log Checkmark */}
      <div>
        {!isLogged ? (
          <button
            type="button"
            className="btn-icon"
            style={{
              width: '38px',
              height: '38px',
              background: 'var(--sage-500)',
              color: 'var(--text-inverse)',
            }}
            onClick={onLog}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--sage-600)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--sage-500)'
            }}
          >
            <Check size={20} weight="bold" />
          </button>
        ) : (
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--sage-50)',
              border: '1px solid var(--sage-300)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Check size={20} weight="bold" color="var(--sage-600)" />
          </div>
        )}
      </div>

      {/* PR Badge */}
      {isPR && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', damping: 15, stiffness: 300 }}
          className="badge badge-pr"
          style={{
            position: 'absolute',
            top: '-8px',
            right: '-8px',
            fontSize: '9px',
            padding: '2px 6px',
          }}
        >
          PR!
        </motion.div>
      )}
    </motion.div>
  )
}
