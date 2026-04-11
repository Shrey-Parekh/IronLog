import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import { Dumbbell } from 'lucide-react'

export default function WorkoutLogger() {
  return (
    <div 
      className="min-h-screen pb-20"
      style={{ background: '#0A0A0B' }}
    >
      <div className="max-w-[540px] mx-auto p-5">
        <h1 className="page-title">Workout Logger</h1>
        
        <EmptyState
          icon={Dumbbell}
          title="Ready to train"
          description="Start a new workout session to begin logging your sets and tracking progress."
          action={{
            label: 'Start workout',
            onClick: () => console.log('Start workout')
          }}
        />
      </div>
      <NavigationBar />
    </div>
  )
}
