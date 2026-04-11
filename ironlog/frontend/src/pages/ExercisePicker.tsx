import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { MagnifyingGlass, X, ArrowLeft, Clock } from '@phosphor-icons/react'
import { motion } from 'motion/react'
import api from '@/services/api'

interface Exercise {
  id: number
  name: string
  display_name: string
  movement_pattern: string
  equipment: string
  is_compound: boolean
  difficulty: string
}

interface MuscleGroup {
  id: number
  name: string
  display_name: string
}

interface ExercisePickerProps {
  onSelect: (exercise: Exercise) => void
  onClose: () => void
}

export default function ExercisePicker({ onSelect, onClose }: ExercisePickerProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [muscleGroups, setMuscleGroups] = useState<MuscleGroup[]>([])
  const [selectedMuscleGroup, setSelectedMuscleGroup] = useState<number | null>(null)
  const [recentExercises, setRecentExercises] = useState<Exercise[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchMuscleGroups()
    fetchRecentExercises()
  }, [])

  useEffect(() => {
    if (searchQuery) {
      searchExercises()
    } else if (selectedMuscleGroup) {
      fetchExercisesByMuscleGroup()
    } else {
      setExercises([])
    }
  }, [searchQuery, selectedMuscleGroup])

  const fetchMuscleGroups = async () => {
    try {
      const response = await api.get('/muscle-groups')
      setMuscleGroups(response.data.data || [])
    } catch (error) {
      console.error('Failed to fetch muscle groups:', error)
    }
  }

  const fetchRecentExercises = async () => {
    // TODO: Implement recent exercises from workout history
    // For now, just show empty
    setRecentExercises([])
  }

  const searchExercises = async () => {
    if (!searchQuery.trim()) return
    setLoading(true)
    try {
      const response = await api.get(`/exercises/search?q=${encodeURIComponent(searchQuery)}`)
      setExercises(response.data.data || [])
    } catch (error) {
      console.error('Failed to search exercises:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchExercisesByMuscleGroup = async () => {
    if (!selectedMuscleGroup) return
    setLoading(true)
    try {
      const response = await api.get(`/muscle-groups/${selectedMuscleGroup}/exercises`)
      setExercises(response.data.data || [])
    } catch (error) {
      console.error('Failed to fetch exercises:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExerciseSelect = (exercise: Exercise) => {
    onSelect(exercise)
    onClose()
  }

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

  return (
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
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        background: 'var(--bg-base)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div
        style={{
          background: 'var(--bg-raised)',
          borderBottom: '1px solid var(--border-subtle)',
          padding: 'var(--space-4) var(--space-5)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-3)',
        }}
      >
        <button type="button" className="btn-icon" onClick={onClose}>
          <ArrowLeft size={22} weight="light" />
        </button>
        <h2 className="type-h1" style={{ flex: 1, margin: 0 }}>
          Add Exercise
        </h2>
      </div>

      {/* Search */}
      <div style={{ padding: 'var(--space-5)' }}>
        <div className="relative">
          <MagnifyingGlass
            size={18}
            weight="light"
            className="absolute left-3 top-1/2 -translate-y-1/2"
            style={{ color: 'var(--text-placeholder)' }}
          />
          <input
            type="text"
            placeholder="Search exercises..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              setSelectedMuscleGroup(null)
            }}
            className="input"
            style={{ paddingLeft: '42px' }}
            autoFocus
          />
          {searchQuery && (
            <button
              type="button"
              className="btn-icon absolute right-2 top-1/2 -translate-y-1/2"
              style={{ width: '32px', height: '32px' }}
              onClick={() => setSearchQuery('')}
            >
              <X size={16} weight="bold" />
            </button>
          )}
        </div>
      </div>

      {/* Muscle Group Filters */}
      {!searchQuery && (
        <div
          style={{
            padding: '0 var(--space-5) var(--space-4)',
            display: 'flex',
            gap: 'var(--space-2)',
            overflowX: 'auto',
            scrollbarWidth: 'none',
          }}
        >
          <button
            type="button"
            className={`chip ${!selectedMuscleGroup ? 'chip-active' : ''}`}
            onClick={() => setSelectedMuscleGroup(null)}
          >
            All
          </button>
          {muscleGroups.map((group) => (
            <button
              key={group.id}
              type="button"
              className={`chip ${selectedMuscleGroup === group.id ? 'chip-active' : ''}`}
              onClick={() => setSelectedMuscleGroup(group.id)}
            >
              {group.display_name}
            </button>
          ))}
        </div>
      )}

      {/* Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '0 var(--space-5) var(--space-5)' }}>
        {/* Recent Exercises */}
        {!searchQuery && !selectedMuscleGroup && recentExercises.length > 0 && (
          <div style={{ marginBottom: 'var(--space-6)' }}>
            <div className="section-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <Clock size={16} weight="light" color="var(--text-tertiary)" />
                <span className="section-label">RECENT</span>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {recentExercises.map((exercise) => (
                <ExerciseCard
                  key={exercise.id}
                  exercise={exercise}
                  onClick={() => handleExerciseSelect(exercise)}
                  getDifficultyColor={getDifficultyColor}
                />
              ))}
            </div>
          </div>
        )}

        {/* Exercise List */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--space-8)' }}>
            <p className="type-body-sm">Loading exercises...</p>
          </div>
        ) : exercises.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            {exercises.map((exercise) => (
              <ExerciseCard
                key={exercise.id}
                exercise={exercise}
                onClick={() => handleExerciseSelect(exercise)}
                getDifficultyColor={getDifficultyColor}
              />
            ))}
          </div>
        ) : searchQuery || selectedMuscleGroup ? (
          <div style={{ textAlign: 'center', padding: 'var(--space-8)' }}>
            <p className="type-body-sm">No exercises found</p>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: 'var(--space-8)' }}>
            <p className="type-body-sm">Search or select a muscle group to browse exercises</p>
          </div>
        )}
      </div>
    </motion.div>
  )
}

function ExerciseCard({
  exercise,
  onClick,
  getDifficultyColor,
}: {
  exercise: Exercise
  onClick: () => void
  getDifficultyColor: (difficulty: string) => string
}) {
  return (
    <button
      type="button"
      className="card card-interactive"
      onClick={onClick}
      style={{
        width: '100%',
        textAlign: 'left',
        padding: 'var(--space-4)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
        <div style={{ flex: 1 }}>
          <h3 className="type-h3" style={{ marginBottom: '4px' }}>
            {exercise.display_name}
          </h3>
          <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap' }}>
            <span
              className="type-caption"
              style={{
                background: 'var(--bg-inset)',
                padding: '2px 6px',
                borderRadius: 'var(--radius-xs)',
              }}
            >
              {exercise.equipment}
            </span>
            {exercise.is_compound && (
              <span
                className="type-caption"
                style={{
                  background: 'var(--sage-50)',
                  color: 'var(--sage-700)',
                  padding: '2px 6px',
                  borderRadius: 'var(--radius-xs)',
                }}
              >
                Compound
              </span>
            )}
          </div>
        </div>
        <div
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: getDifficultyColor(exercise.difficulty),
            flexShrink: 0,
            marginTop: '6px',
          }}
        />
      </div>
    </button>
  )
}
