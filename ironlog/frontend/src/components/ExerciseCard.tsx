import { CaretRight } from '@phosphor-icons/react'

interface ExerciseCardProps {
  exercise: {
    id: number
    name: string
    display_name: string
    movement_pattern: string
    equipment: string
    is_compound: boolean
    difficulty: string
  }
  onClick?: () => void
  showStats?: boolean
  stats?: {
    lastWeight?: number
    lastReps?: number
    estimated1RM?: number
    totalSets?: number
  }
}

export default function ExerciseCard({ exercise, onClick, showStats, stats }: ExerciseCardProps) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'var(--success-icon)'
      case 'intermediate':
        return 'var(--warning-icon)'
      case 'advanced':
        return 'var(--danger-icon)'
      default:
        return 'var(--text-tertiary)'
    }
  }

  const getDifficultyLabel = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'Beginner'
      case 'intermediate':
        return 'Intermediate'
      case 'advanced':
        return 'Advanced'
      default:
        return ''
    }
  }

  const formatMovementPattern = (pattern: string) => {
    return pattern
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <button
      type="button"
      className={`card ${onClick ? 'card-interactive' : ''}`}
      onClick={onClick}
      style={{
        width: '100%',
        textAlign: 'left',
        padding: 'var(--space-5)',
        cursor: onClick ? 'pointer' : 'default',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: 'var(--space-3)' }}>
        <div style={{ flex: 1 }}>
          {/* Exercise Name */}
          <h3 className="type-h2" style={{ marginBottom: '6px' }}>
            {exercise.display_name}
          </h3>

          {/* Tags */}
          <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap', marginBottom: showStats ? 'var(--space-3)' : 0 }}>
            <span
              className="type-caption"
              style={{
                background: 'var(--bg-inset)',
                padding: '3px 8px',
                borderRadius: 'var(--radius-xs)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              {exercise.equipment}
            </span>
            <span
              className="type-caption"
              style={{
                background: 'var(--bg-inset)',
                padding: '3px 8px',
                borderRadius: 'var(--radius-xs)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              {formatMovementPattern(exercise.movement_pattern)}
            </span>
            {exercise.is_compound && (
              <span
                className="type-caption"
                style={{
                  background: 'var(--sage-50)',
                  color: 'var(--sage-700)',
                  padding: '3px 8px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--sage-200)',
                }}
              >
                Compound
              </span>
            )}
          </div>

          {/* Stats */}
          {showStats && stats && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-3)', marginTop: 'var(--space-3)' }}>
              {stats.lastWeight !== undefined && (
                <div>
                  <p className="type-caption" style={{ marginBottom: '2px' }}>LAST WEIGHT</p>
                  <p className="type-stat-sm tabular-nums">{stats.lastWeight} kg</p>
                </div>
              )}
              {stats.estimated1RM !== undefined && (
                <div>
                  <p className="type-caption" style={{ marginBottom: '2px' }}>EST. 1RM</p>
                  <p className="type-stat-sm tabular-nums">{stats.estimated1RM} kg</p>
                </div>
              )}
              {stats.totalSets !== undefined && (
                <div>
                  <p className="type-caption" style={{ marginBottom: '2px' }}>TOTAL SETS</p>
                  <p className="type-stat-sm tabular-nums">{stats.totalSets}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Side - Difficulty Indicator */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 'var(--space-2)' }}>
          {/* Difficulty Badge */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              borderRadius: 'var(--radius-xs)',
              background: 'var(--bg-inset)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: getDifficultyColor(exercise.difficulty),
                flexShrink: 0,
              }}
            />
            <span className="type-caption" style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
              {getDifficultyLabel(exercise.difficulty)}
            </span>
          </div>
          
          {/* Arrow Icon */}
          {onClick && (
            <CaretRight size={20} weight="bold" color="var(--text-tertiary)" />
          )}
        </div>
      </div>
    </button>
  )
}
