import { useState, useEffect, useCallback } from 'react'
import { offlineQueue } from '@/services/offlineQueue'
import api from '@/services/api'

export function useOfflineSync() {
  const [isSyncing, setIsSyncing] = useState(false)
  const [queueCount, setQueueCount] = useState(0)
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  // Update online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Update queue count
  const updateQueueCount = useCallback(async () => {
    const count = await offlineQueue.getQueueCount()
    setQueueCount(count)
  }, [])

  // Sync queued items
  const syncQueue = useCallback(async () => {
    if (!isOnline || isSyncing) return

    setIsSyncing(true)

    try {
      const queued = await offlineQueue.getAllQueued()

      // Sync sessions first
      for (const session of queued.sessions) {
        try {
          await api.post('/workouts/sessions', session.sessionData)
          await offlineQueue.removeSession(session.id)
        } catch (error) {
          console.error('Failed to sync session:', error)
          await offlineQueue.incrementRetry('sessions', session.id)
        }
      }

      // Sync exercises
      for (const exercise of queued.exercises) {
        try {
          await api.post(
            `/workouts/sessions/${exercise.sessionId}/exercises`,
            exercise.exerciseData
          )
          await offlineQueue.removeExercise(exercise.id)
        } catch (error) {
          console.error('Failed to sync exercise:', error)
          await offlineQueue.incrementRetry('exercises', exercise.id)
        }
      }

      // Sync sets
      for (const set of queued.sets) {
        try {
          await api.post(
            `/workouts/exercises/${set.workoutExerciseId}/sets`,
            set.setData
          )
          await offlineQueue.removeSet(set.id)
        } catch (error) {
          console.error('Failed to sync set:', error)
          await offlineQueue.incrementRetry('sets', set.id)
        }
      }

      await updateQueueCount()
    } catch (error) {
      console.error('Sync failed:', error)
    } finally {
      setIsSyncing(false)
    }
  }, [isOnline, isSyncing, updateQueueCount])

  // Auto-sync when coming online
  useEffect(() => {
    if (isOnline) {
      syncQueue()
    }
  }, [isOnline, syncQueue])

  // Update queue count on mount
  useEffect(() => {
    updateQueueCount()
  }, [updateQueueCount])

  return {
    isOnline,
    isSyncing,
    queueCount,
    syncQueue,
    updateQueueCount,
  }
}
