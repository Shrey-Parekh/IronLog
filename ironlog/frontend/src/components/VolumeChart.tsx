import { motion } from 'motion/react'

interface MuscleGroupVolume {
  muscle_group_id: number
  muscle_group_name: string
  total_sets: number
  total_volume_kg: number
}

interface VolumeChartProps {
  data: MuscleGroupVolume[]
  loading?: boolean
}

export default function VolumeChart({ data, loading }: VolumeChartProps) {
  if (loading) {
    return (
      <div className="card">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              <div style={{ 
                height: '14px', 
                width: '120px', 
                background: 'var(--bg-inset)', 
                borderRadius: 'var(--radius-sm)',
                animation: 'pulse 1.5s ease-in-out infinite'
              }} />
              <div style={{ 
                height: '24px', 
                width: '100%', 
                background: 'var(--bg-inset)', 
                borderRadius: 'var(--radius-md)',
                animation: 'pulse 1.5s ease-in-out infinite'
              }} />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="card">
        <p className="type-body-sm" style={{ color: 'var(--text-tertiary)', textAlign: 'center', padding: 'var(--space-6) 0' }}>
          No volume data available yet. Complete some workouts to see your training volume.
        </p>
      </div>
    )
  }

  // Sort by total sets descending
  const sortedData = [...data].sort((a, b) => b.total_sets - a.total_sets)
  const maxSets = Math.max(...sortedData.map(d => d.total_sets))

  return (
    <div className="card">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        {sortedData.map((item, index) => (
          <VolumeBar
            key={item.muscle_group_id}
            name={item.muscle_group_name}
            sets={item.total_sets}
            volume={item.total_volume_kg}
            maxSets={maxSets}
            delay={index * 0.05}
          />
        ))}
      </div>
    </div>
  )
}

interface VolumeBarProps {
  name: string
  sets: number
  volume: number
  maxSets: number
  delay: number
}

function VolumeBar({ name, sets, volume, maxSets, delay }: VolumeBarProps) {
  const percentage = (sets / maxSets) * 100

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 'var(--space-2)' }}>
        <span className="type-body-sm" style={{ fontWeight: 500, color: 'var(--text-primary)' }}>
          {name}
        </span>
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'baseline' }}>
          <span className="type-body-sm tabular-nums" style={{ color: 'var(--text-secondary)' }}>
            {sets} sets
          </span>
          <span className="type-caption tabular-nums" style={{ color: 'var(--text-tertiary)' }}>
            {volume.toFixed(0)} kg
          </span>
        </div>
      </div>
      <div 
        style={{ 
          height: '10px', 
          background: 'var(--bg-inset)', 
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
          position: 'relative'
        }}
      >
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ 
            duration: 0.8, 
            delay,
            ease: [0.16, 1, 0.3, 1]
          }}
          style={{ 
            height: '100%', 
            background: `linear-gradient(90deg, var(--sage-400), var(--sage-500))`,
            borderRadius: 'var(--radius-full)',
            position: 'relative'
          }}
        >
          {/* Shine effect */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: '200%' }}
            transition={{
              duration: 1.5,
              delay: delay + 0.3,
              ease: 'easeInOut'
            }}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              height: '100%',
              width: '50%',
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
            }}
          />
        </motion.div>
      </div>
    </div>
  )
}
