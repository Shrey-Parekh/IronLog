import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import { Info } from '@phosphor-icons/react'

export default function ExerciseDetail() {
  return (
    <div className="page">
      <h1 className="page-title">Exercise Detail</h1>
      
      <EmptyState
        icon={Info}
        title="Select an exercise"
        description="Choose an exercise from the library to view detailed information, instructions, and your personal stats."
      />
      
      <NavigationBar />
    </div>
  )
}
