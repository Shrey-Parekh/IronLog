import { Component, ReactNode } from 'react'
import { Warning } from '@phosphor-icons/react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="page">
          <div className="card-raised text-center p-8">
            <div className="w-16 h-16 rounded-full bg-danger-bg border-2 border-danger-border flex items-center justify-center mx-auto mb-4">
              <Warning size={32} weight="bold" className="text-danger-icon" />
            </div>
            
            <h2 className="type-h2 mb-2">Something went wrong</h2>
            <p className="type-body-sm text-text-secondary mb-6">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>

            <div className="flex gap-3 justify-center">
              <button
                onClick={() => window.location.reload()}
                className="btn-primary"
              >
                Reload page
              </button>
              <button
                onClick={() => this.setState({ hasError: false, error: undefined })}
                className="btn-secondary"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
