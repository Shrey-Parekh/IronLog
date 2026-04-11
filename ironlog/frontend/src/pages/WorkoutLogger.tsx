import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import SetLoggerRow from '@/components/SetLoggerRow'
import RestTimer from '@/components/RestTimer'
import ExercisePicker from './ExercisePicker'
import { useWorkoutStore } from '@/stores/workoutStore'
import { useWorkoutSession } from '@/hooks/useWorkoutSession'
import { Barbell, Plus, X, DotsThreeVertical, Check, Timer as TimerIcon } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'motion/react'

export default function WorkoutLogger() {
  const navigate = useNavigate()
  const { activeSession, isLogging, startSession, addExercise, removeExercise, addSet, updateSet, logSet, updateExerciseNotes } = useWorkoutStore()
  const { elapsedTime, saveSession } = useWorkoutSession()
  
  const [showExercisePicker, setShowExercisePicker] = useState(false)
  const [showFinishModal, setShowFinishModal] = useState(false)
  const [restTimerActive, setRestTimerActive] = useState(false)
  const [restTimerSeconds, setRestTimerSeconds] = useState(90)
  const [expandedExercise, setExpandedExercise] = useState<number | null>(null)

  const handleStartWorkout = () => {
    startSession()
  }

  const handleAddExercise = (exercise: any) => {
    addExercise(exercise.id, exercise.display_name)
    setShowExercisePicker(false)
  }

  const handleLogSet = (exerciseOrder: number, setOrder: number) => {
    logSet(exerciseOrder, setOrder)
    
    // Auto-add next set
    const exercise = activeSession?.exercises.find(ex => ex.exercise_order === exerciseOrder)
    if (exercise) {
      const currentSet = exercise.sets.find(s => s.set_order === setOrder)
      const isLastSet = setOrder === exercise.sets.length
      
      if (isLastSet && currentSet?.logged) {
        addSet(exerciseOrder)
      }
    }
    
    // Start rest timer
    setRestTimerActive(true)
    setRestTimerSeconds(90) // Default 90s, can be customized based on exercise type
  }

  const handleFinishWorkout = async () => {
    if (!activeSession) return
    
    const success = await saveSession()
    if (success) {
      setShowFinishModal(false)
      navigate('/')
    }
  }

  const formatElapsedTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      return `${hours}h ${mins}m`
    }
    return `${mins}m ${secs}s`
  }

  if (!isLogging || !activeSession) {
    return (
      <div className="page">
        <h1 className="page-title">Workout Logger</h1>
        
        <EmptyState
          icon={Barbell}
          title="Ready to train"
          description="Start a new workout session to begin logging your sets and tracking progress."
          action={{
            label: 'Start workout',
            onClick: handleStartWorkout
          }}
        />
        
        <NavigationBar />
      </div>
    )
  }

  return (
    <>
      <div className="page">
        {/* Session Header */}
        <div style={{ marginBottom: 'var(--space-6)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
            <div>
              <h1 className="type-h1" style={{ marginBottom: '4px' }}>
                {activeSession.session_name || 'Workout Session'}
              </h1>
              <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                  <TimerIcon size={16} weight="light" color="var(--text-tertiary)" />
                  <span className="type-body-sm tabular-nums">{formatElapsedTime(elapsedTime)}</span>
                </div>
                <span className="type-body-sm" style={{ color: 'var(--text-tertiary)' }}>
                  {activeSession.exercises.reduce((sum, ex) => sum + ex.sets.filter(s => s.logged).length, 0)} sets logged
                </span>
              </div>
            </div>
            <button
              type="button"
              className="btn-primary"
              onClick={() => setShowFinishModal(true)}
              disabled={activeSession.exercises.length === 0}
            >
              <Check size={18} weight="bold" />
              Finish
            </button>
          </div>
        </div>

        {/* Exercises */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {activeSession.exercises.map((exercise) => (
            <ExerciseCard
              key={exercise.exercise_order}
              exercise={exercise}
              isExpanded={expandedExercise === exercise.exercise_order}
              onToggleExpand={() => setExpandedExercise(expandedExercise === exercise.exercise_order ? null : exercise.exercise_order)}
              onRemove={() => removeExercise(exercise.exercise_order)}
              onAddSet={() => addSet(exercise.exercise_order)}
              onUpdateSet={(setOrder, data) => updateSet(exercise.exercise_order, setOrder, data)}
              onLogSet={(setOrder) => handleLogSet(exercise.exercise_order, setOrder)}
              onUpdateNotes={(notes) => updateExerciseNotes(exercise.exercise_order, notes)}
            />
          ))}

          {/* Add Exercise Button */}
          <button
            type="button"
            className="btn-add-dashed"
            onClick={() => setShowExercisePicker(true)}
          >
            <Plus size={18} weight="bold" />
            Add Exercise
          </button>
        </div>
      </div>

      {/* Exercise Picker Modal */}
      <AnimatePresence>
        {showExercisePicker && (
          <ExercisePicker
            onSelect={handleAddExercise}
            onClose={() => setShowExercisePicker(false)}
          />
        )}
      </AnimatePresence>

      {/* Finish Workout Modal */}
      <AnimatePresence>
        {showFinishModal && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50"
              style={{ background: 'rgba(0, 0, 0, 0.4)' }}
              onClick={() => setShowFinishModal(false)}
            />
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-5"
            >
              <div className="card-raised" style={{ maxWidth: '400px', width: '100%' }}>
                <h2 className="type-h2" style={{ marginBottom: 'var(--space-3)' }}>
                  Finish Workout?
                </h2>
                <p className="type-body-sm" style={{ marginBottom: 'var(--space-5)' }}>
                  You've logged {activeSession.exercises.reduce((sum, ex) => sum + ex.sets.filter(s => s.logged).length, 0)} sets across {activeSession.exercises.length} exercises in {formatElapsedTime(elapsedTime)}.
                </p>
                <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setShowFinishModal(false)}
                    style={{ flex: 1 }}
                  >
                    Keep Training
                  </button>
                  <button
                    type="button"
                    className="btn-primary"
                    onClick={handleFinishWorkout}
                    style={{ flex: 1 }}
                  >
                    Finish
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Rest Timer */}
      <RestTimer
        isActive={restTimerActive}
        initialSeconds={restTimerSeconds}
        onComplete={() => setRestTimerActive(false)}
        onDismiss={() => setRestTimerActive(false)}
      />

      <NavigationBar />
    </>
  )
}

interface ExerciseCardProps {
  exercise: any
  isExpanded: boolean
  onToggleExpand: () => void
  onRemove: () => void
  onAddSet: () => void
  onUpdateSet: (setOrder: number, data: any) => void
  onLogSet: (setOrder: number) => void
  onUpdateNotes: (notes: string) => void
}

function ExerciseCard({
  exercise,
  isExpanded,
  onToggleExpand,
  onRemove,
  onAddSet,
  onUpdateSet,
  onLogSet,
  onUpdateNotes,
}: ExerciseCardProps) {
  const [showMenu, setShowMenu] = useState(false)
  const [showNotes, setShowNotes] = useState(false)

  return (
    <div className="card" style={{ position: 'relative' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 'var(--space-4)' }}>
        <div style={{ flex: 1 }}>
          <h3 className="type-h2" style={{ marginBottom: '4px' }}>
            {exercise.exercise_name}
          </h3>
          <p className="type-caption">
            {exercise.sets.filter((s: any) => s.logged).length} / {exercise.sets.length} sets completed
          </p>
        </div>
        <div style={{ position: 'relative' }}>
          <button
            type="button"
            className="btn-icon"
            onClick={() => setShowMenu(!showMenu)}
          >
            <DotsThreeVertical size={20} weight="bold" />
          </button>
          {showMenu && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                marginTop: '4px',
                background: 'var(--bg-raised)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                boxShadow: 'var(--shadow-md)',
                padding: 'var(--space-2)',
                zIndex: 10,
                minWidth: '140px',
              }}
            >
              <button
                type="button"
                className="btn-ghost"
                style={{ width: '100%', justifyContent: 'flex-start' }}
                onClick={() => {
                  setShowNotes(!showNotes)
                  setShowMenu(false)
                }}
              >
                Notes
              </button>
              <button
                type="button"
                className="btn-ghost"
                style={{ width: '100%', justifyContent: 'flex-start', color: 'var(--danger-text)' }}
                onClick={() => {
                  onRemove()
                  setShowMenu(false)
                }}
              >
                Remove
              </button>
            </motion.div>
          )}
        </div>
      </div>

      {/* Notes */}
      {showNotes && (
        <div style={{ marginBottom: 'var(--space-4)' }}>
          <textarea
            placeholder="Add notes for this exercise..."
            value={exercise.notes || ''}
            onChange={(e) => onUpdateNotes(e.target.value)}
            className="input"
            style={{ minHeight: '80px', resize: 'vertical' }}
          />
        </div>
      )}

      {/* Set Headers */}
      <div className="set-row" style={{ opacity: 0.6, marginBottom: 'var(--space-2)' }}>
        <div className="set-column-header">SET</div>
        <div className="set-column-header">WEIGHT</div>
        <div className="set-column-header">REPS</div>
        <div className="set-column-header">RPE</div>
        <div />
      </div>

      {/* Sets */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {exercise.sets.map((set: any) => (
          <SetLoggerRow
            key={set.set_order}
            setNumber={set.set_order}
            weight={set.weight_kg}
            reps={set.reps}
            rpe={set.rpe}
            isLogged={set.logged}
            isPR={set.is_pr}
            onWeightChange={(weight) => onUpdateSet(set.set_order, { weight_kg: weight })}
            onRepsChange={(reps) => onUpdateSet(set.set_order, { reps })}
            onRPEChange={(rpe) => onUpdateSet(set.set_order, { rpe })}
            onLog={() => onLogSet(set.set_order)}
          />
        ))}
      </div>

      {/* Add Set Button */}
      <button
        type="button"
        className="btn-ghost"
        style={{ width: '100%', marginTop: 'var(--space-3)' }}
        onClick={onAddSet}
      >
        <Plus size={18} weight="bold" />
        Add Set
      </button>
    </div>
  )
}
