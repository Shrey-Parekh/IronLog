import { create } from 'zustand'

interface SetData {
  id?: number
  set_order: number
  set_type: string
  weight_kg: number
  reps: number
  rpe: number | null
  rir: number | null
  is_pr?: boolean
  logged: boolean
}

interface WorkoutExerciseData {
  id?: number
  exercise_id: number | null
  user_exercise_id: number | null
  exercise_name: string
  exercise_order: number
  notes: string | null
  sets: SetData[]
}

interface WorkoutSessionData {
  id?: string
  started_at: string
  session_name: string | null
  notes: string | null
  bodyweight_kg: number | null
  exercises: WorkoutExerciseData[]
}

interface WorkoutState {
  activeSession: WorkoutSessionData | null
  isLogging: boolean
  startSession: (sessionName?: string) => void
  endSession: () => void
  addExercise: (exerciseId: number, exerciseName: string) => void
  removeExercise: (exerciseOrder: number) => void
  addSet: (exerciseOrder: number) => void
  updateSet: (exerciseOrder: number, setOrder: number, data: Partial<SetData>) => void
  logSet: (exerciseOrder: number, setOrder: number) => void
  updateSessionNotes: (notes: string) => void
  updateExerciseNotes: (exerciseOrder: number, notes: string) => void
}

export const useWorkoutStore = create<WorkoutState>((set) => ({
  activeSession: null,
  isLogging: false,

  startSession: (sessionName) =>
    set({
      activeSession: {
        started_at: new Date().toISOString(),
        session_name: sessionName || null,
        notes: null,
        bodyweight_kg: null,
        exercises: [],
      },
      isLogging: true,
    }),

  endSession: () =>
    set({
      activeSession: null,
      isLogging: false,
    }),

  addExercise: (exerciseId, exerciseName) =>
    set((state) => {
      if (!state.activeSession) return state

      const newExercise: WorkoutExerciseData = {
        exercise_id: exerciseId,
        user_exercise_id: null,
        exercise_name: exerciseName,
        exercise_order: state.activeSession.exercises.length + 1,
        notes: null,
        sets: [
          {
            set_order: 1,
            set_type: 'working',
            weight_kg: 0,
            reps: 0,
            rpe: null,
            rir: null,
            logged: false,
          },
        ],
      }

      return {
        activeSession: {
          ...state.activeSession,
          exercises: [...state.activeSession.exercises, newExercise],
        },
      }
    }),

  removeExercise: (exerciseOrder) =>
    set((state) => {
      if (!state.activeSession) return state

      return {
        activeSession: {
          ...state.activeSession,
          exercises: state.activeSession.exercises
            .filter((ex) => ex.exercise_order !== exerciseOrder)
            .map((ex, idx) => ({ ...ex, exercise_order: idx + 1 })),
        },
      }
    }),

  addSet: (exerciseOrder) =>
    set((state) => {
      if (!state.activeSession) return state

      const exercises = state.activeSession.exercises.map((ex) => {
        if (ex.exercise_order === exerciseOrder) {
          const lastSet = ex.sets[ex.sets.length - 1]
          return {
            ...ex,
            sets: [
              ...ex.sets,
              {
                set_order: ex.sets.length + 1,
                set_type: 'working',
                weight_kg: lastSet?.weight_kg || 0,
                reps: lastSet?.reps || 0,
                rpe: null,
                rir: null,
                logged: false,
              },
            ],
          }
        }
        return ex
      })

      return {
        activeSession: {
          ...state.activeSession,
          exercises,
        },
      }
    }),

  updateSet: (exerciseOrder, setOrder, data) =>
    set((state) => {
      if (!state.activeSession) return state

      const exercises = state.activeSession.exercises.map((ex) => {
        if (ex.exercise_order === exerciseOrder) {
          return {
            ...ex,
            sets: ex.sets.map((s) =>
              s.set_order === setOrder ? { ...s, ...data } : s
            ),
          }
        }
        return ex
      })

      return {
        activeSession: {
          ...state.activeSession,
          exercises,
        },
      }
    }),

  logSet: (exerciseOrder, setOrder) =>
    set((state) => {
      if (!state.activeSession) return state

      const exercises = state.activeSession.exercises.map((ex) => {
        if (ex.exercise_order === exerciseOrder) {
          return {
            ...ex,
            sets: ex.sets.map((s) =>
              s.set_order === setOrder ? { ...s, logged: true } : s
            ),
          }
        }
        return ex
      })

      return {
        activeSession: {
          ...state.activeSession,
          exercises,
        },
      }
    }),

  updateSessionNotes: (notes) =>
    set((state) => {
      if (!state.activeSession) return state
      return {
        activeSession: {
          ...state.activeSession,
          notes,
        },
      }
    }),

  updateExerciseNotes: (exerciseOrder, notes) =>
    set((state) => {
      if (!state.activeSession) return state

      const exercises = state.activeSession.exercises.map((ex) =>
        ex.exercise_order === exerciseOrder ? { ...ex, notes } : ex
      )

      return {
        activeSession: {
          ...state.activeSession,
          exercises,
        },
      }
    }),
}))
