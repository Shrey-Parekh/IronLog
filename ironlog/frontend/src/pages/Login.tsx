import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import api from '@/services/api'

export default function Login() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()
  const { setUser, setTokens } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        const response = await api.post('/auth/login', { email, password })
        const { access_token, refresh_token, user } = response.data.data
        setTokens(access_token, refresh_token)
        setUser(user)
        navigate('/')
      } else {
        const response = await api.post('/auth/register', {
          email,
          password,
          display_name: displayName || null,
        })
        const { access_token, refresh_token, user } = response.data.data
        setTokens(access_token, refresh_token)
        setUser(user)
        navigate('/')
      }
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { error?: { message?: string } } } }
        setError(axiosError.response?.data?.error?.message || 'Authentication failed')
      } else {
        setError('Authentication failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'var(--bg-base)' }}
    >
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 
            className="type-display"
            style={{ fontSize: '42px', marginBottom: '8px' }}
          >
            IronLog
          </h1>
          <p className="type-body-sm">
            AI-powered training intelligence
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="type-h3 block mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input"
            />
          </div>

          {!isLogin && (
            <div>
              <label htmlFor="displayName" className="type-h3 block mb-2">
                Display Name (optional)
              </label>
              <input
                id="displayName"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="input"
              />
            </div>
          )}

          <div>
            <label htmlFor="password" className="type-h3 block mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="input"
            />
          </div>

          {error && (
            <div 
              className="type-body-sm"
              style={{ 
                color: 'var(--danger-text)',
                background: 'var(--danger-bg)',
                border: '1px solid var(--danger-border)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-3)',
              }}
            >
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="btn-primary w-full" 
            disabled={loading}
          >
            {loading ? 'Loading...' : isLogin ? 'Login' : 'Register'}
          </button>

          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            className="btn-ghost w-full"
          >
            {isLogin
              ? "Don't have an account? Register"
              : 'Already have an account? Login'}
          </button>
        </form>
      </div>
    </div>
  )
}
