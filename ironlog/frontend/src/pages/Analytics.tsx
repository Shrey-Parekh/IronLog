import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import { BarChart3 } from 'lucide-react'

export default function Analytics() {
  return (
    <div 
      className="min-h-screen pb-20"
      style={{ background: '#0A0A0B' }}
    >
      <div className="max-w-[540px] mx-auto p-5">
        <h1 className="page-title">Analytics</h1>
        
        <EmptyState
          icon={BarChart3}
          title="Nothing to analyze yet"
          description="Complete a few workouts and your training data will appear here."
          action={{
            label: 'Start a workout',
            onClick: () => window.location.href = '/workout'
          }}
        />
      </div>
      <NavigationBar />
    </div>
  )
}
