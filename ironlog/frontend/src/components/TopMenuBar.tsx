import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { User, SignOut, List } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'motion/react'

interface TopMenuBarProps {
  user?: {
    email: string
    display_name?: string
  } | null
  onLogout?: () => void
}

export default function TopMenuBar({ user, onLogout }: TopMenuBarProps) {
  const [showMenu, setShowMenu] = useState(false)
  const navigate = useNavigate()

  const handleLogout = () => {
    if (onLogout) {
      onLogout()
    }
    setShowMenu(false)
    navigate('/login')
  }

  return (
    <div className="top-menu-bar">
      <div className="top-menu-inner">
        <Link to="/" className="top-menu-logo">
          <span className="type-h2" style={{ color: 'var(--sage-600)' }}>IronLog</span>
        </Link>

        <div className="top-menu-actions">
          {user ? (
            <div className="relative">
              <button
                type="button"
                className="btn-icon"
                onClick={() => setShowMenu(!showMenu)}
                style={{
                  width: '40px',
                  height: '40px',
                  background: 'var(--sage-50)',
                  border: '2px solid var(--sage-200)',
                }}
              >
                <User size={20} weight="bold" color="var(--sage-600)" />
              </button>

              <AnimatePresence>
                {showMenu && (
                  <>
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="fixed inset-0 z-40"
                      onClick={() => setShowMenu(false)}
                    />
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      transition={{ duration: 0.2 }}
                      className="absolute top-full right-0 mt-2 bg-bg-raised border-2 border-border-subtle rounded-xl shadow-lg p-2 z-50 min-w-[200px]"
                    >
                      <div className="px-3 py-2 border-b border-border-subtle mb-2">
                        <p className="type-body-sm font-semibold text-text-primary">
                          {user.display_name || 'User'}
                        </p>
                        <p className="type-caption text-text-tertiary" style={{ textTransform: 'none', fontSize: '11px' }}>
                          {user.email}
                        </p>
                      </div>
                      
                      <button
                        type="button"
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-text-secondary hover:bg-bg-hover hover:text-danger-text transition-colors"
                      >
                        <SignOut size={18} weight="bold" />
                        <span className="type-body-sm font-medium">Logout</span>
                      </button>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <Link
              to="/login"
              className="btn-secondary"
              style={{
                padding: '8px 16px',
                fontSize: '14px',
              }}
            >
              Login
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
