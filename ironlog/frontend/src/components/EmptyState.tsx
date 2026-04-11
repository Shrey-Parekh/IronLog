import { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: { label: string; onClick: () => void }
}

export default function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6">
      <div 
        className="w-12 h-12 rounded-xl flex items-center justify-center mb-5"
        style={{
          background: 'var(--bg-tertiary)',
          border: '1px solid var(--border-subtle)',
        }}
      >
        <Icon className="w-5 h-5" strokeWidth={1.5} style={{ color: 'var(--text-tertiary)' }} />
      </div>
      <h3 
        style={{
          fontFamily: "'DM Sans', sans-serif",
          fontSize: '17px',
          fontWeight: 600,
          color: 'var(--text-primary)',
          marginBottom: '8px',
        }}
      >
        {title}
      </h3>
      <p 
        style={{
          fontSize: '14px',
          color: 'var(--text-secondary)',
          textAlign: 'center',
          maxWidth: '280px',
          lineHeight: 1.5,
        }}
      >
        {description}
      </p>
      {action && (
        <button
          onClick={action.onClick}
          className="px-5 py-2.5 rounded-md text-sm font-medium transition-all mt-6"
          style={{
            background: 'transparent',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-default)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--bg-hover)'
            e.currentTarget.style.borderColor = 'var(--border-strong)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent'
            e.currentTarget.style.borderColor = 'var(--border-default)'
          }}
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
