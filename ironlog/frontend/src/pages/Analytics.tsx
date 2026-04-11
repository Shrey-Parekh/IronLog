import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import VolumeChart from '@/components/VolumeChart'
import StrengthChart from '@/components/StrengthChart'
import { useAnalytics } from '@/hooks/useAnalytics'
import { ChartLineUp, Barbell, TrendUp, Trophy } from '@phosphor-icons/react'

export default function Analytics() {
  const navigate = useNavigate()
  const {
    muscleGroupVolume,
    strengthEstimates,
    prLogs,
    volumeLoading,
    strengthLoading,
    prLoading,
    fetchVolumeData,
    fetchStrengthData,
    fetchPRLogs,
  } = useAnalytics()

  useEffect(() => {
    fetchVolumeData()
    fetchStrengthData()
    fetchPRLogs()
  }, [])

  const hasData = muscleGroupVolume.length > 0 || strengthEstimates.length > 0 || prLogs.length > 0

  if (!hasData && !volumeLoading && !strengthLoading && !prLoading) {
    return (
      <div className="page">
        <h1 className="page-title">Analytics</h1>
        
        <EmptyState
          icon={ChartLineUp}
          title="Nothing to analyze yet"
          description="Complete a few workouts and your training data will appear here."
          action={{
            label: 'Start a workout',
            onClick: () => navigate('/workout')
          }}
        />
        
        <NavigationBar />
      </div>
    )
  }

  return (
    <div className="page">
      <h1 className="page-title">Analytics</h1>

      {/* Volume by Muscle Group */}
      <div className="section">
        <div className="section-header">
          <h2 className="type-h2">Volume This Week</h2>
        </div>
        <VolumeChart data={muscleGroupVolume} loading={volumeLoading} />
      </div>

      {/* Strength Progress */}
      <div className="section">
        <div className="section-header">
          <h2 className="type-h2">Strength Progress</h2>
        </div>
        <StrengthChart data={strengthEstimates} loading={strengthLoading} />
      </div>

      {/* Recent PRs */}
      {prLogs.length > 0 && (
        <div className="section">
          <div className="section-header">
            <h2 className="type-h2">Recent PRs</h2>
          </div>
          <div className="pr-list">
            {prLogs.map((pr) => (
              <div key={pr.id} className="card pr-card">
                <div className="pr-header">
                  <Trophy size={20} weight="fill" color="var(--pr-icon)" />
                  <span className="type-h3">{pr.exercise_name}</span>
                </div>
                <div className="pr-details">
                  <div className="pr-stat">
                    <span className="type-caption">WEIGHT × REPS</span>
                    <span className="type-stat-sm">{pr.weight_kg}kg × {pr.reps}</span>
                  </div>
                  <div className="pr-stat">
                    <span className="type-caption">EST. 1RM</span>
                    <span className="type-stat-sm">{pr.estimated_1rm.toFixed(1)}kg</span>
                  </div>
                  <div className="pr-stat">
                    <span className="type-caption">DATE</span>
                    <span className="type-body-sm">{new Date(pr.logged_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <NavigationBar />
    </div>
  )
}
