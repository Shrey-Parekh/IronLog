export interface User {
  id: string
  email: string
  display_name: string | null
  created_at: string
}

export interface MuscleGroup {
  id: number
  name: string
  display_name: string
  body_region: string
  push_pull: string | null
  default_recovery_hours: number
  default_mrv_sets_week: number
  default_mev_sets_week: number
}

export interface ExerciseMuscle {
  muscle_group_id: number
  muscle_group_name: string
  role: string
  activation_pct: number
}

export interface ExerciseSubstitution {
  id: number
  name: string
  display_name: string
  similarity: number
  reason: string | null
}

export interface Exercise {
  id: number
  name: string
  display_name: string
  movement_pattern: string
  equipment: string
  is_compound: boolean
  is_unilateral: boolean
  supports_1rm: boolean
  difficulty: string
  instructions: string | null
  tips: string | null
  common_mistakes: string | null
  muscles: ExerciseMuscle[]
}

export interface ExerciseDetail extends Exercise {
  substitutions: ExerciseSubstitution[]
}

export interface Set {
  id: number
  set_order: number
  set_type: string
  weight_kg: number
  reps: number
  rpe: number | null
  rir: number | null
  is_pr: boolean
  volume_kg: number | null
  estimated_1rm: number | null
  logged_at: string
}

export interface WorkoutExercise {
  id: number
  exercise_id: number | null
  user_exercise_id: number | null
  exercise_order: number
  notes: string | null
  estimated_1rm: number | null
  total_volume_kg: number | null
  sets: Set[]
}

export interface WorkoutSession {
  id: string
  user_id: string
  started_at: string
  finished_at: string | null
  session_name: string | null
  notes: string | null
  overall_rpe: number | null
  bodyweight_kg: number | null
  total_volume_kg: number | null
  total_sets: number | null
  duration_minutes: number | null
  created_at: string
  exercises: WorkoutExercise[]
}

export interface ApiResponse<T> {
  data: T | null
  error: {
    code: string
    message: string
  } | null
}
