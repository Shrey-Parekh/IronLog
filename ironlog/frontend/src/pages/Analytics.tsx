import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import { ChartLineUp } from '@phosphor-icons/react'

export default function Analytics() {
  return (
    <div className="page">
      <h1 className="page-title">Analytics</h1>
      
      <EmptyState
        icon={ChartLineUp}
        title="Nothing to analyze yet"
        description="Complete a few workouts and your training data will appear here."
        action={{
          label: 'Start a workout',
          onClick: () => window.location.href = '/workout'
        }}
      />
      
      <NavigationBar />
    </div>
  )
}
