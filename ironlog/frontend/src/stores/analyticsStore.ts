import { create } from 'zustand'

interface MuscleGroupVolume {
  muscle_group_id: number
  muscle_group_name: string
  total_sets: number
  total_volume_kg: number
  week_start: string
}

interface StrengthEstimate {
  exercise_id: number
  exercise_name: string
  estimated_1rm: number
  date: string
}

interface PRLog {
  id: number
  exercise_name: string
  weight_kg: number
  reps: number
  estimated_1rm: number
  logged_at: string
}

interface WeeklyVolumeTrend {
  week_start: string
  total_sets: number
  total_volume_kg: number
}

interface AnalyticsState {
  // Volume data
  muscleGroupVolume: MuscleGroupVolume[]
  weeklyVolumeTrend: WeeklyVolumeTrend[]
  
  // Strength data
  strengthEstimates: StrengthEstimate[]
  
  // PR logs
  prLogs: PRLog[]
  
  // Loading states
  volumeLoading: boolean
  strengthLoading: boolean
  prLoading: boolean
  
  // Actions
  setMuscleGroupVolume: (data: MuscleGroupVolume[]) => void
  setWeeklyVolumeTrend: (data: WeeklyVolumeTrend[]) => void
  setStrengthEstimates: (data: StrengthEstimate[]) => void
  setPRLogs: (data: PRLog[]) => void
  setVolumeLoading: (loading: boolean) => void
  setStrengthLoading: (loading: boolean) => void
  setPRLoading: (loading: boolean) => void
  reset: () => void
}

const initialState = {
  muscleGroupVolume: [],
  weeklyVolumeTrend: [],
  strengthEstimates: [],
  prLogs: [],
  volumeLoading: false,
  strengthLoading: false,
  prLoading: false,
}

export const useAnalyticsStore = create<AnalyticsState>((set) => ({
  ...initialState,
  
  setMuscleGroupVolume: (data) => set({ muscleGroupVolume: data }),
  setWeeklyVolumeTrend: (data) => set({ weeklyVolumeTrend: data }),
  setStrengthEstimates: (data) => set({ strengthEstimates: data }),
  setPRLogs: (data) => set({ prLogs: data }),
  setVolumeLoading: (loading) => set({ volumeLoading: loading }),
  setStrengthLoading: (loading) => set({ strengthLoading: loading }),
  setPRLoading: (loading) => set({ prLoading: loading }),
  reset: () => set(initialState),
}))
