import { useState, useEffect } from 'react'
import { useWorkoutStore } from '@/stores/workoutStore'
import api from '@/services/api'

export function useWorkoutSession() {
  const {
    activeSession,
    isLogging,
    startSession,
    endSession,
    addExercise,
    removeExercise,
    addSet,
    updateSet,
    logSet,
  } = useWorkoutStore()

  const [elapsedTime, setElapsedTime] = useState(0)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    if (!isLogging || !activeSession) return

    const startTime = new Date(activeSession.started_at).getTime()
    const interval = setInterval(() => {
      const now = Date.now()
      const elapsed = Math.floor((now - startTime) / 1000)
      setElapsedTime(elapsed)
    }, 1000)

    return () => clearInterval(interval)
  }, [isLogging, activeSession])

  const formatElapsedTime = () => {
    const hours = Math.floor(elapsedTime / 3600)
    const minutes = Math.floor((elapsedTime % 3600) / 60)
    const seconds = elapsedTime % 60
    return `${hours.toString().padStart(2, '0')}:${minutes
      .toString()
      .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  const saveSession = async () => {
    if (!activeSession) return

    setIsSaving(true)
    try {
      // Create session
      const sessionResponse = await api.post('/workouts/sessions', {
        started_at: activeSession.started_at,
        session_name: activeSession.session_name,
        notes: activeSession.notes,
        bodyweight_kg: activeSession.bodyweight_kg,
      })

      const sessionId = sessionResponse.data.data.id

      // Add exercises and sets
      for (const exercise of activeSession.exercises) {
        const exerciseResponse = await api.post(
          `/workouts/sessions/${sessionId}/exercises`,
          {
            exercise_id: exercise.exercise_id,
            user_exercise_id: exercise.user_exercise_id,
            exercise_order: exercise.exercise_order,
            notes: exercise.notes,
          }
        )

        const workoutExerciseId = exerciseResponse.data.data.id

        // Add logged sets only
        for (const set of exercise.sets.filter((s) => s.logged)) {
          await api.post(`/workouts/exercises/${workoutExerciseId}/sets`, {
            set_order: set.set_order,
            set_type: set.set_type,
            weight_kg: set.weight_kg,
            reps: set.reps,
            rpe: set.rpe,
            rir: set.rir,
          })
        }
      }

      // Finish session
      await api.patch(`/workouts/sessions/${sessionId}`, {
        finished_at: new Date().toISOString(),
      })

      endSession()
      return true
    } catch (error) {
      console.error('Failed to save session:', error)
      return false
    } finally {
      setIsSaving(false)
    }
  }

  return {
    activeSession,
    isLogging,
    elapsedTime: formatElapsedTime(),
    isSaving,
    startSession,
    endSession,
    addExercise,
    removeExercise,
    addSet,
    updateSet,
    logSet,
    saveSession,
  }
}
