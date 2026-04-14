import { BrowserRouter } from 'react-router-dom'
import { AppRoutes } from './routes'
import TopMenuBar from './components/TopMenuBar'
import { useAuthStore } from './stores/authStore'

function App() {
  const { user, logout } = useAuthStore()

  return (
    <BrowserRouter>
      <TopMenuBar user={user} onLogout={logout} />
      <AppRoutes />
    </BrowserRouter>
  )
}

export default App
