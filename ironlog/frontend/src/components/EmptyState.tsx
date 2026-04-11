import { Icon as PhosphorIcon } from '@phosphor-icons/react'

interface EmptyStateProps {
  icon: PhosphorIcon
  title: string
  description: string
  action?: { label: string; onClick: () => void }
}

export default function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div 
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '64px 24px 48px',
      }}
    >
      <div 
        style={{
          width: 52,
          height: 52,
          borderRadius: 14,
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 20,
        }}
      >
        <Icon size={24} weight="thin" color="var(--text-tertiary)" />
      </div>
      
      <h3 
        style={{
          fontFamily: "'Plus Jakarta Sans', sans-serif",
          fontSize: 17,
          fontWeight: 600,
          color: 'var(--text-primary)',
          marginBottom: 6,
          textAlign: 'center',
        }}
      >
        {title}
      </h3>
      
      <p 
        style={{
          fontSize: 14,
          color: 'var(--text-secondary)',
          textAlign: 'center',
          maxWidth: 260,
          lineHeight: 1.5,
          marginBottom: action ? 20 : 0,
        }}
      >
        {description}
      </p>
      
      {action && (
        <button className="btn-secondary" onClick={action.onClick}>
          {action.label}
        </button>
      )}
    </div>
  )
}
