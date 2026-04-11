import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import { Calendar } from '@phosphor-icons/react'

export default function Programs() {
  return (
    <div className="page">
      <h1 className="page-title">Programs</h1>
      
      <EmptyState
        icon={Calendar}
        title="No programs yet"
        description="Create a custom training program based on your goals and schedule."
        action={{
          label: 'Generate program',
          onClick: () => console.log('Generate program')
        }}
      />
      
      <NavigationBar />
    </div>
  )
}
