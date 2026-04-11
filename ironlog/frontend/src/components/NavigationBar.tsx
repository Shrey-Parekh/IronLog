import { Link, useLocation } from 'react-router-dom'
import { House, Barbell, BookOpen, ChartLineUp } from '@phosphor-icons/react'

const navItems = [
  { path: '/', icon: House, label: 'Home' },
  { path: '/workout', icon: Barbell, label: 'Workout' },
  { path: '/exercises', icon: BookOpen, label: 'Exercises' },
  { path: '/analytics', icon: ChartLineUp, label: 'Analytics' },
]

export default function NavigationBar() {
  const location = useLocation()

  return (
    <nav className="bottom-nav">
      <div className="bottom-nav-inner">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path
          return (
            <Link
              key={path}
              to={path}
              className={`nav-item ${isActive ? 'nav-item-active' : ''}`}
            >
              <Icon size={22} weight={isActive ? 'fill' : 'light'} />
              <span className="nav-label">{label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
