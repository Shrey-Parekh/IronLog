import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import SetLoggerRow from '@/components/SetLoggerRow'
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
        <div className="workout-header">
          <div>
            <h1 className="type-h1">{activeSession.session_name || 'Workout Session'}</h1>
            <div className="workout-meta">
              <span className="workout-time">
                <TimerIcon size={16} weight="light" />
                {formatElapsedTime(elapsedTime)}
              </span>
              <span>{activeSession.exercises.reduce((sum, ex) => sum + ex.sets.filter(s => s.logged).length, 0)} sets</span>
            </div>
          </div>
          <button
            className="btn-primary"
            onClick={() => setShowFinishModal(true)}
            disabled={activeSession.exercises.length === 0}
          >
            <Check size={18} weight="bold" />
            Finish
          </button>
        </div>

        <div className="exercise-list">
          {activeSession.exercises.map((exercise) => (
            <ExerciseCard
              key={exercise.exercise_order}
              exercise={exercise}
              onRemove={() => removeExercise(exercise.exercise_order)}
              onAddSet={() => addSet(exercise.exercise_order)}
              onUpdateSet={(setOrder, data) => updateSet(exercise.exercise_order, setOrder, data)}
              onLogSet={(setOrder) => handleLogSet(exercise.exercise_order, setOrder)}
              onUpdateNotes={(notes) => updateExerciseNotes(exercise.exercise_order, notes)}
            />
          ))}

          <button className="btn-add-dashed" onClick={() => setShowExercisePicker(true)}>
            <Plus size={20} weight="bold" />
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

      {/* Finish Modal */}
      <AnimatePresence>
        {showFinishModal && (
          <>
            <div className="modal-backdrop" onClick={() => setShowFinishModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="modal-container"
            >
              <div className="card-raised">
                <h2 className="type-h2">Finish Workout?</h2>
                <p className="type-body-sm" style={{ margin: 'var(--space-3) 0 var(--space-5)', color: 'var(--text-secondary)' }}>
                  {activeSession.exercises.reduce((sum, ex) => sum + ex.sets.filter(s => s.logged).length, 0)} sets · {activeSession.exercises.length} exercises · {formatElapsedTime(elapsedTime)}
                </p>
                <div className="modal-actions">
                  <button className="btn-secondary" onClick={() => setShowFinishModal(false)}>
                    Keep Training
                  </button>
                  <button className="btn-primary" onClick={handleFinishWorkout}>
                    Finish
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <NavigationBar />
    </>
  )
}

interface ExerciseCardProps {
  exercise: any
  onRemove: () => void
  onAddSet: () => void
  onUpdateSet: (setOrder: number, data: any) => void
  onLogSet: (setOrder: number) => void
  onUpdateNotes: (notes: string) => void
}

function ExerciseCard({ exercise, onRemove, onAddSet, onUpdateSet, onLogSet, onUpdateNotes }: ExerciseCardProps) {
  const [showMenu, setShowMenu] = useState(false)
  const [showNotes, setShowNotes] = useState(false)

  return (
    <div className="card">
      <div className="exercise-header">
        <div>
          <h3 className="type-h2">{exercise.exercise_name}</h3>
          <p className="type-caption">{exercise.sets.filter((s: any) => s.logged).length} / {exercise.sets.length} completed</p>
        </div>
        <button className="btn-icon" onClick={() => setShowMenu(!showMenu)}>
          <DotsThreeVertical size={20} weight="bold" />
        </button>
        
        {showMenu && (
          <>
            <div className="menu-backdrop" onClick={() => setShowMenu(false)} />
            <div className="exercise-menu">
              <button className="btn-ghost" onClick={() => { setShowNotes(!showNotes); setShowMenu(false) }}>
                Notes
              </button>
              <button className="btn-ghost danger" onClick={() => { onRemove(); setShowMenu(false) }}>
                Remove
              </button>
            </div>
          </>
        )}
      </div>

      {showNotes && (
        <textarea
          placeholder="Notes..."
          value={exercise.notes || ''}
          onChange={(e) => onUpdateNotes(e.target.value)}
          className="input exercise-notes"
        />
      )}

      <div className="set-headers">
        <span>SET</span>
        <span>WEIGHT</span>
        <span>REPS</span>
        <span>RPE</span>
        <span></span>
      </div>

      <div className="sets-list">
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

      <button className="btn-ghost add-set-btn" onClick={onAddSet}>
        <Plus size={18} weight="bold" />
        Add Set
      </button>
    </div>
  )
}
