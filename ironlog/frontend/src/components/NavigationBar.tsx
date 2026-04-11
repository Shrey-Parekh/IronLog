import { Link, useLocation } from 'react-router-dom'
import { Home, Dumbbell, BarChart3, BookOpen } from 'lucide-react'

const navItems = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/workout', icon: Dumbbell, label: 'Workout' },
  { path: '/exercises', icon: BookOpen, label: 'Exercises' },
  { path: '/analytics', icon: BarChart3, label: 'Analytics' },
]

export default function NavigationBar() {
  const location = useLocation()

  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 z-[100]"
      style={{
        background: 'rgba(10, 10, 11, 0.85)',
        backdropFilter: 'blur(20px) saturate(180%)',
        WebkitBackdropFilter: 'blur(20px) saturate(180%)',
        borderTop: '1px solid var(--border-subtle)',
        paddingBottom: 'env(safe-area-inset-bottom, 0px)',
      }}
    >
      <div className="flex justify-around items-center h-14 max-w-[480px] mx-auto">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path
          return (
            <Link
              key={path}
              to={path}
              className="flex flex-col items-center gap-0.5 px-4 py-1.5 rounded-md relative transition-colors"
              style={{
                color: isActive ? '#F0B860' : '#55555E',
              }}
            >
              <Icon className="w-[22px] h-[22px]" strokeWidth={1.5} />
              <span 
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: '10px',
                  fontWeight: 500,
                  letterSpacing: '0.02em',
                }}
              >
                {label}
              </span>
              {isActive && (
                <span 
                  className="absolute bottom-0 w-1 h-1 rounded-full"
                  style={{ background: 'var(--accent-primary)' }}
                />
              )}
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
