import { useState } from 'react'

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
  const [isFocused, setIsFocused] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value
    
    // Allow empty input
    if (inputValue === '') {
      onChange(0)
      return
    }
    
    // Parse the value
    const numValue = parseFloat(inputValue)
    
    // Validate and update
    if (!isNaN(numValue) && numValue >= min && numValue <= max) {
      onChange(Number(numValue.toFixed(1)))
    }
  }

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <input
        type="number"
        inputMode="decimal"
        value={value > 0 ? value : ''}
        onChange={handleChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder}
        min={min}
        max={max}
        step="0.1"
        className="input"
        style={{
          width: '100%',
          background: 'var(--bg-raised)',
          border: `2px solid ${isFocused ? 'var(--sage-400)' : 'var(--border-default)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '14px 48px 14px 16px',
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '18px',
          fontWeight: 500,
          color: 'var(--text-primary)',
          transition: 'all 0.2s var(--ease-gentle)',
          boxShadow: isFocused ? 'var(--shadow-focus)' : 'none',
        }}
      />
      <span
        className="type-caption"
        style={{
          position: 'absolute',
          right: '16px',
          top: '50%',
          transform: 'translateY(-50%)',
          color: 'var(--text-tertiary)',
          fontSize: '12px',
          fontWeight: 600,
          pointerEvents: 'none',
        }}
      >
        {unit}
      </span>
    </div>
  )
}
