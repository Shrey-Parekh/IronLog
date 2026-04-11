import NavigationBar from '@/components/NavigationBar'
import EmptyState from '@/components/EmptyState'
import { Info } from 'lucide-react'

export default function ExerciseDetail() {
  return (
    <div 
      className="min-h-screen pb-20"
      style={{ background: '#0A0A0B' }}
    >
      <div className="max-w-[540px] mx-auto p-5">
        <h1 className="page-title">Exercise Detail</h1>
        
        <EmptyState
          icon={Info}
          title="Select an exercise"
          description="Choose an exercise from the library to view detailed information, instructions, and your personal stats."
        />
      </div>
      <NavigationBar />
    </div>
  )
}
