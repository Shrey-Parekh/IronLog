import { motion } from 'motion/react'

interface StrengthEstimate {
  exercise_id: number
  exercise_name: string
  estimated_1rm: number
  date: string
}

interface StrengthChartProps {
  data: StrengthEstimate[]
  loading?: boolean
}

export default function StrengthChart({ data, loading }: StrengthChartProps) {
  if (loading) {
    return (
      <div className="card">
        <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ 
            width: '100%', 
            height: '160px', 
            background: 'var(--bg-inset)', 
            borderRadius: 'var(--radius-md)',
            animation: 'pulse 1.5s ease-in-out infinite'
          }} />
        </div>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="card">
        <p className="type-body-sm" style={{ color: 'var(--text-tertiary)', textAlign: 'center', padding: 'var(--space-6) 0' }}>
          No strength data available yet. Log some sets to track your estimated 1RM progress.
        </p>
      </div>
    )
  }

  // Group by exercise
  const exerciseGroups = data.reduce((acc, item) => {
    if (!acc[item.exercise_name]) {
      acc[item.exercise_name] = []
    }
    acc[item.exercise_name].push(item)
    return acc
  }, {} as Record<string, StrengthEstimate[]>)

  // Sort each group by date
  Object.keys(exerciseGroups).forEach(key => {
    exerciseGroups[key].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
  })

  // Get max value for scaling
  const maxValue = Math.max(...data.map(d => d.estimated_1rm))
  const chartHeight = 200

  return (
    <div className="card">
      <div className="strength-chart">
        {Object.entries(exerciseGroups).map(([exerciseName, points], idx) => (
          <ExerciseLine
            key={exerciseName}
            exerciseName={exerciseName}
            points={points}
            maxValue={maxValue}
            chartHeight={chartHeight}
            color={getExerciseColor(idx)}
          />
        ))}
      </div>
      
      <div className="strength-legend">
        {Object.keys(exerciseGroups).map((name, idx) => (
          <div key={name} className="legend-item">
            <div className="legend-dot" style={{ background: getExerciseColor(idx) }} />
            <span className="type-body-sm">{name}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

interface ExerciseLineProps {
  exerciseName: string
  points: StrengthEstimate[]
  maxValue: number
  chartHeight: number
  color: string
}

function ExerciseLine({ points, maxValue, chartHeight, color }: ExerciseLineProps) {
  if (points.length === 0) return null

  const padding = 20
  const width = 100 // percentage
  const height = chartHeight - padding * 2

  // Calculate positions
  const positions = points.map((point, idx) => {
    const x = (idx / (points.length - 1 || 1)) * width
    const y = padding + (1 - point.estimated_1rm / maxValue) * height
    return { x, y, value: point.estimated_1rm }
  })

  // Create SVG path
  const pathData = positions.map((pos, idx) => 
    `${idx === 0 ? 'M' : 'L'} ${pos.x} ${pos.y}`
  ).join(' ')

  return (
    <div className="exercise-line" style={{ height: `${chartHeight}px` }}>
      <svg width="100%" height={chartHeight} style={{ overflow: 'visible' }}>
        {/* Line */}
        <motion.path
          d={pathData}
          fill="none"
          stroke={color}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
        
        {/* Points */}
        {positions.map((pos, idx) => (
          <motion.g key={idx}>
            <motion.circle
              cx={`${pos.x}%`}
              cy={pos.y}
              r="4"
              fill={color}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5 + idx * 0.1, duration: 0.3 }}
            />
            <motion.circle
              cx={`${pos.x}%`}
              cy={pos.y}
              r="8"
              fill={color}
              opacity="0.2"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5 + idx * 0.1, duration: 0.3 }}
            />
          </motion.g>
        ))}
      </svg>
    </div>
  )
}

function getExerciseColor(index: number): string {
  const colors = [
    'var(--sage-500)',
    'var(--powder-400)',
    'var(--clay-400)',
    'var(--sage-300)',
    'var(--powder-600)',
  ]
  return colors[index % colors.length]
}
