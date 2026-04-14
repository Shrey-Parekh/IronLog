import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import api from '@/services/api'
import { ExerciseDetail as ExerciseDetailType } from '@/types'
import { 
  ArrowLeft, 
  Info, 
  Lightning, 
  Target,
  ListChecks,
  WarningCircle,
  Swap
} from '@phosphor-icons/react'
import { motion } from 'motion/react'

export default function ExerciseDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [exercise, setExercise] = useState<ExerciseDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      fetchExercise()
    }
  }, [id])

  const fetchExercise = async () => {
    if (!id) return
    
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/exercises/${id}`)
      setExercise(response.data.data)
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load exercise')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="page">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-6)' }}>
          <button type="button" className="btn-icon" onClick={() => navigate(-1)}>
            <ArrowLeft size={20} weight="bold" />
          </button>
          <div className="type-h1">Loading...</div>
        </div>
        <NavigationBar />
      </div>
    )
  }

  if (error || !exercise) {
    return (
      <div className="page">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-6)' }}>
          <button type="button" className="btn-icon" onClick={() => navigate(-1)}>
            <ArrowLeft size={20} weight="bold" />
          </button>
        </div>
        <EmptyState
          icon={Info}
          title="Exercise not found"
          description={error || "The exercise you're looking for doesn't exist."}
          action={{
            label: 'Go back',
            onClick: () => navigate(-1)
          }}
        />
        <NavigationBar />
      </div>
    )
  }

  const primaryMuscles = exercise.muscles.filter(m => m.role === 'primary')
  const secondaryMuscles = exercise.muscles.filter(m => m.role === 'secondary')

  return (
    <div className="page">
      {/* Header */}
      <div style={{ marginBottom: 'var(--space-6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
          <button type="button" className="btn-icon" onClick={() => navigate(-1)}>
            <ArrowLeft size={20} weight="bold" />
          </button>
          <h1 className="type-h1">{exercise.display_name}</h1>
        </div>

        {/* Exercise Meta */}
        <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
          <span className="chip">{exercise.movement_pattern}</span>
          <span className="chip">{exercise.equipment}</span>
          {exercise.is_compound && <span className="chip">Compound</span>}
          {exercise.is_unilateral && <span className="chip">Unilateral</span>}
          <span className="chip">{exercise.difficulty}</span>
        </div>
      </div>

      {/* Muscles Targeted */}
      <div className="section">
        <h2 className="type-h2" style={{ marginBottom: 'var(--space-4)' }}>Muscles Targeted</h2>
        <div className="card">
          {primaryMuscles.length > 0 && (
            <div style={{ marginBottom: secondaryMuscles.length > 0 ? 'var(--space-5)' : 0 }}>
              <div className="muscle-section-label">
                <Target size={18} weight="fill" color="var(--sage-500)" />
                <span>Primary</span>
              </div>
              <div className="muscle-bars">
                {primaryMuscles.map((muscle) => (
                  <MuscleBar
                    key={muscle.muscle_group_id}
                    name={muscle.muscle_group_name}
                    activation={muscle.activation_pct}
                    isPrimary={true}
                  />
                ))}
              </div>
            </div>
          )}

          {secondaryMuscles.length > 0 && (
            <div>
              <div className="muscle-section-label secondary">
                <Target size={18} weight="light" color="var(--text-tertiary)" />
                <span>Secondary</span>
              </div>
              <div className="muscle-bars">
                {secondaryMuscles.map((muscle) => (
                  <MuscleBar
                    key={muscle.muscle_group_id}
                    name={muscle.muscle_group_name}
                    activation={muscle.activation_pct}
                    isPrimary={false}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      {exercise.instructions && (
        <div className="section">
          <div className="card">
            <div style={{ display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-3)' }}>
              <ListChecks size={20} weight="light" color="var(--sage-500)" />
              <span className="type-h3">Instructions</span>
            </div>
            <div 
              className="type-body" 
              style={{ 
                color: 'var(--text-secondary)', 
                whiteSpace: 'pre-line',
                lineHeight: 1.7
              }}
            >
              {exercise.instructions}
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      {exercise.tips && (
        <div className="section">
          <div className="card" style={{ background: 'var(--sage-50)', borderColor: 'var(--sage-200)' }}>
            <div style={{ display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-3)' }}>
              <Lightning size={20} weight="fill" color="var(--sage-600)" />
              <span className="type-h3" style={{ color: 'var(--sage-700)' }}>Tips</span>
            </div>
            <div 
              className="type-body" 
              style={{ 
                color: 'var(--sage-700)', 
                whiteSpace: 'pre-line',
                lineHeight: 1.7
              }}
            >
              {exercise.tips}
            </div>
          </div>
        </div>
      )}

      {/* Common Mistakes */}
      {exercise.common_mistakes && (
        <div className="section">
          <div className="card" style={{ background: 'var(--warning-bg)', borderColor: 'var(--warning-border)' }}>
            <div style={{ display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-3)' }}>
              <WarningCircle size={20} weight="fill" color="var(--warning-icon)" />
              <span className="type-h3" style={{ color: 'var(--warning-text)' }}>Avoid These</span>
            </div>
            <div 
              className="type-body" 
              style={{ 
                color: 'var(--warning-text)', 
                whiteSpace: 'pre-line',
                lineHeight: 1.7
              }}
            >
              {exercise.common_mistakes}
            </div>
          </div>
        </div>
      )}

      {/* Substitutions */}
      {exercise.substitutions && exercise.substitutions.length > 0 && (
        <div className="section">
          <div className="section-header">
            <h2 className="type-h2">Alternative Exercises</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {exercise.substitutions.map((sub) => (
              <motion.div
                key={sub.id}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigate(`/exercises/${sub.id}`)}
                className="card card-interactive"
                style={{ cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-1)' }}>
                      <Swap size={16} weight="bold" color="var(--text-tertiary)" />
                      <h3 className="type-h3">{sub.display_name}</h3>
                    </div>
                    {sub.reason && (
                      <p className="type-body-sm" style={{ color: 'var(--text-tertiary)' }}>
                        {sub.reason}
                      </p>
                    )}
                  </div>
                  <div 
                    className="type-caption" 
                    style={{ 
                      color: 'var(--sage-600)',
                      background: 'var(--sage-50)',
                      padding: 'var(--space-1) var(--space-2)',
                      borderRadius: 'var(--radius-sm)'
                    }}
                  >
                    {Math.round(sub.similarity * 100)}% match
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      <NavigationBar />
    </div>
  )
}

interface MuscleBarProps {
  name: string
  activation: number
  isPrimary: boolean
}

function MuscleBar({ name, activation, isPrimary }: MuscleBarProps) {
  return (
    <div className="muscle-bar">
      <div className="muscle-bar-header">
        <span className="muscle-name">{name}</span>
        <span className="muscle-pct">{activation}%</span>
      </div>
      <div className="muscle-bar-track">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${activation}%` }}
          transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className={`muscle-bar-fill ${isPrimary ? 'primary' : 'secondary'}`}
        />
      </div>
    </div>
  )
}
