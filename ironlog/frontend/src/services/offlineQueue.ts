import { openDB, DBSchema, IDBPDatabase } from 'idb'

interface OfflineQueueDB extends DBSchema {
  sets: {
    key: string
    value: {
      id: string
      workoutExerciseId: number
      setData: {
        set_order: number
        set_type: string
        weight_kg: number
        reps: number
        rpe?: number
        rir?: number
      }
      timestamp: number
      retries: number
    }
  }
  exercises: {
    key: string
    value: {
      id: string
      sessionId: number
      exerciseData: {
        exercise_id: number
        user_exercise_id?: number
        exercise_order: number
        notes?: string
      }
      timestamp: number
      retries: number
    }
  }
  sessions: {
    key: string
    value: {
      id: string
      sessionData: {
        started_at: string
        session_name?: string
        notes?: string
        bodyweight_kg?: number
      }
      timestamp: number
      retries: number
    }
  }
}

class OfflineQueue {
  private db: IDBPDatabase<OfflineQueueDB> | null = null
  private readonly DB_NAME = 'ironlog-offline'
  private readonly DB_VERSION = 1
  private readonly MAX_RETRIES = 3

  async init() {
    if (this.db) return

    this.db = await openDB<OfflineQueueDB>(this.DB_NAME, this.DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('sets')) {
          db.createObjectStore('sets', { keyPath: 'id' })
        }
        if (!db.objectStoreNames.contains('exercises')) {
          db.createObjectStore('exercises', { keyPath: 'id' })
        }
        if (!db.objectStoreNames.contains('sessions')) {
          db.createObjectStore('sessions', { keyPath: 'id' })
        }
      },
    })
  }

  // Queue a set for offline sync
  async queueSet(workoutExerciseId: number, setData: any) {
    await this.init()
    if (!this.db) return

    const id = `set-${Date.now()}-${Math.random()}`
    await this.db.add('sets', {
      id,
      workoutExerciseId,
      setData,
      timestamp: Date.now(),
      retries: 0,
    })

    return id
  }

  // Queue an exercise for offline sync
  async queueExercise(sessionId: number, exerciseData: any) {
    await this.init()
    if (!this.db) return

    const id = `exercise-${Date.now()}-${Math.random()}`
    await this.db.add('exercises', {
      id,
      sessionId,
      exerciseData,
      timestamp: Date.now(),
      retries: 0,
    })

    return id
  }

  // Queue a session for offline sync
  async queueSession(sessionData: any) {
    await this.init()
    if (!this.db) return

    const id = `session-${Date.now()}-${Math.random()}`
    await this.db.add('sessions', {
      id,
      sessionData,
      timestamp: Date.now(),
      retries: 0,
    })

    return id
  }

  // Get all queued items
  async getAllQueued() {
    await this.init()
    if (!this.db) return { sets: [], exercises: [], sessions: [] }

    const [sets, exercises, sessions] = await Promise.all([
      this.db.getAll('sets'),
      this.db.getAll('exercises'),
      this.db.getAll('sessions'),
    ])

    return { sets, exercises, sessions }
  }

  // Remove a queued item
  async removeSet(id: string) {
    await this.init()
    if (!this.db) return
    await this.db.delete('sets', id)
  }

  async removeExercise(id: string) {
    await this.init()
    if (!this.db) return
    await this.db.delete('exercises', id)
  }

  async removeSession(id: string) {
    await this.init()
    if (!this.db) return
    await this.db.delete('sessions', id)
  }

  // Increment retry count
  async incrementRetry(store: 'sets' | 'exercises' | 'sessions', id: string) {
    await this.init()
    if (!this.db) return

    const item = await this.db.get(store, id)
    if (!item) return

    item.retries += 1

    if (item.retries >= this.MAX_RETRIES) {
      // Remove if max retries reached
      await this.db.delete(store, id)
      return false
    }

    await this.db.put(store, item)
    return true
  }

  // Clear all queued items
  async clearAll() {
    await this.init()
    if (!this.db) return

    await Promise.all([
      this.db.clear('sets'),
      this.db.clear('exercises'),
      this.db.clear('sessions'),
    ])
  }

  // Get queue count
  async getQueueCount() {
    await this.init()
    if (!this.db) return 0

    const [setsCount, exercisesCount, sessionsCount] = await Promise.all([
      this.db.count('sets'),
      this.db.count('exercises'),
      this.db.count('sessions'),
    ])

    return setsCount + exercisesCount + sessionsCount
  }
}

export const offlineQueue = new OfflineQueue()
