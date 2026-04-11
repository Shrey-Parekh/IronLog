import { Routes, Route } from 'react-router-dom'
import Dashboard from '@/pages/Dashboard'
import WorkoutLogger from '@/pages/WorkoutLogger'
import Exercises from '@/pages/Exercises'
import ExerciseDetail from '@/pages/ExerciseDetail'
import Analytics from '@/pages/Analytics'
import Programs from '@/pages/Programs'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/workout" element={<WorkoutLogger />} />
      <Route path="/exercises" element={<Exercises />} />
      <Route path="/exercises/:id" element={<ExerciseDetail />} />
      <Route path="/analytics" element={<Analytics />} />
      <Route path="/programs" element={<Programs />} />
    </Routes>
  )
}
