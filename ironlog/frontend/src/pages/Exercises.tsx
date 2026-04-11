import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import NavigationBar from '@/components/NavigationBar'
import ExerciseCard from '@/components/ExerciseCard'
import { MagnifyingGlass, X } from '@phosphor-icons/react'
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

export default function Exercises() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [muscleGroups, setMuscleGroups] = useState<MuscleGroup[]>([])
  const [selectedMuscleGroup, setSelectedMuscleGroup] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchMuscleGroups()
  }, [])

  useEffect(() => {
    if (searchQuery) {
      searchExercises()
    } else if (selectedMuscleGroup) {
      fetchExercisesByMuscleGroup()
    } else {
      fetchAllExercises()
    }
  }, [searchQuery, selectedMuscleGroup])

  const fetchMuscleGroups = async () => {
    try {
      const response = await api.get('/exercises/muscle-groups')
      setMuscleGroups(response.data.data || [])
    } catch (error) {
      console.error('Failed to fetch muscle groups:', error)
    }
  }

  const fetchAllExercises = async () => {
    setLoading(true)
    try {
      const response = await api.get('/exercises')
      setExercises(response.data.data || [])
    } catch (error) {
      console.error('Failed to fetch exercises:', error)
    } finally {
      setLoading(false)
    }
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
      const response = await api.get(`/exercises/muscle-groups/${selectedMuscleGroup}/exercises`)
      setExercises(response.data.data || [])
    } catch (error) {
      console.error('Failed to fetch exercises:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExerciseClick = (exerciseId: number) => {
    navigate(`/exercises/${exerciseId}`)
  }

  return (
    <div className="page">
      <h1 className="page-title">Exercises</h1>
      
      {/* Search */}
      <div className="relative mb-4">
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

      {/* Muscle Group Filters */}
      <div
        className="flex gap-2 overflow-x-auto pb-2 mb-6"
        style={{ scrollbarWidth: 'none' }}
      >
        <button
          type="button"
          className={`chip ${!selectedMuscleGroup && !searchQuery ? 'chip-active' : ''}`}
          onClick={() => {
            setSelectedMuscleGroup(null)
            setSearchQuery('')
          }}
        >
          All
        </button>
        {muscleGroups.map((group) => (
          <button
            key={group.id}
            type="button"
            className={`chip ${selectedMuscleGroup === group.id ? 'chip-active' : ''}`}
            onClick={() => {
              setSelectedMuscleGroup(group.id)
              setSearchQuery('')
            }}
          >
            {group.display_name}
          </button>
        ))}
      </div>

      {/* Exercise List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 'var(--space-8)' }}>
          <p className="type-body-sm">Loading exercises...</p>
        </div>
      ) : exercises.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          {exercises.map((exercise) => (
            <ExerciseCard
              key={exercise.id}
              exercise={exercise}
              onClick={() => handleExerciseClick(exercise.id)}
            />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12">
          <div
            style={{
              width: 52,
              height: 52,
              borderRadius: 14,
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 20,
            }}
          >
            <MagnifyingGlass size={24} weight="thin" color="var(--text-tertiary)" />
          </div>
          <h3 className="type-h2" style={{ marginBottom: '8px', textAlign: 'center' }}>
            {searchQuery || selectedMuscleGroup ? 'No exercises found' : 'Browse 120+ exercises'}
          </h3>
          <p className="type-body-sm" style={{ textAlign: 'center', maxWidth: '280px' }}>
            {searchQuery || selectedMuscleGroup
              ? 'Try adjusting your search or filters'
              : 'Search or pick a muscle group to get started'}
          </p>
        </div>
      )}
      
      <NavigationBar />
    </div>
  )
}
