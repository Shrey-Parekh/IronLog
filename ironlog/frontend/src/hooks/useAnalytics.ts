import { useEffect } from 'react'
import { useAnalyticsStore } from '@/stores/analyticsStore'
import api from '@/services/api'

export function useAnalytics() {
  const {
    muscleGroupVolume,
    weeklyVolumeTrend,
    strengthEstimates,
    prLogs,
    volumeLoading,
    strengthLoading,
    prLoading,
    setMuscleGroupVolume,
    setWeeklyVolumeTrend,
    setStrengthEstimates,
    setPRLogs,
    setVolumeLoading,
    setStrengthLoading,
    setPRLoading,
  } = useAnalyticsStore()

  const fetchVolumeData = async (weeks: number = 4) => {
    setVolumeLoading(true)
    try {
      // Fetch muscle group volume for current week
      const volumeResponse = await api.get('/analytics/volume/muscle-groups', {
        params: { weeks: 1 }
      })
      setMuscleGroupVolume(volumeResponse.data.data || [])

      // Fetch weekly volume trend
      const trendResponse = await api.get('/analytics/volume/weekly', {
        params: { weeks }
      })
      setWeeklyVolumeTrend(trendResponse.data.data || [])
    } catch (error) {
      console.error('Failed to fetch volume data:', error)
      setMuscleGroupVolume([])
      setWeeklyVolumeTrend([])
    } finally {
      setVolumeLoading(false)
    }
  }

  const fetchStrengthData = async (exerciseId?: number) => {
    setStrengthLoading(true)
    try {
      const params = exerciseId ? { exercise_id: exerciseId } : {}
      const response = await api.get('/analytics/strength/estimates', { params })
      setStrengthEstimates(response.data.data || [])
    } catch (error) {
      console.error('Failed to fetch strength data:', error)
      setStrengthEstimates([])
    } finally {
      setStrengthLoading(false)
    }
  }

  const fetchPRLogs = async (limit: number = 10) => {
    setPRLoading(true)
    try {
      const response = await api.get('/analytics/prs', {
        params: { limit }
      })
      setPRLogs(response.data.data || [])
    } catch (error) {
      console.error('Failed to fetch PR logs:', error)
      setPRLogs([])
    } finally {
      setPRLoading(false)
    }
  }

  const refreshAll = async () => {
    await Promise.all([
      fetchVolumeData(),
      fetchStrengthData(),
      fetchPRLogs(),
    ])
  }

  return {
    // Data
    muscleGroupVolume,
    weeklyVolumeTrend,
    strengthEstimates,
    prLogs,
    
    // Loading states
    volumeLoading,
    strengthLoading,
    prLoading,
    
    // Actions
    fetchVolumeData,
    fetchStrengthData,
    fetchPRLogs,
    refreshAll,
  }
}
