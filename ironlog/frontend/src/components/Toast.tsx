import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { CheckCircle, Warning, XCircle, Info, X } from '@phosphor-icons/react'

type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: string
  type: ToastType
  message: string
  duration?: number
}

interface ToastContextType {
  showToast: (type: ToastType, message: string, duration?: number) => void
  hideToast: (id: string) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((type: ToastType, message: string, duration = 5000) => {
    const id = `toast-${Date.now()}-${Math.random()}`
    const toast: Toast = { id, type, message, duration }

    setToasts((prev) => [...prev, toast])

    if (duration > 0) {
      setTimeout(() => {
        hideToast(id)
      }, duration)
    }
  }, [])

  const hideToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}
      <ToastContainer toasts={toasts} onClose={hideToast} />
    </ToastContext.Provider>
  )
}

function ToastContainer({ toasts, onClose }: { toasts: Toast[]; onClose: (id: string) => void }) {
  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-md">
      <AnimatePresence>
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={onClose} />
        ))}
      </AnimatePresence>
    </div>
  )
}

function ToastItem({ toast, onClose }: { toast: Toast; onClose: (id: string) => void }) {
  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: Warning,
    info: Info,
  }

  const colors = {
    success: {
      bg: 'var(--success-bg)',
      border: 'var(--success-border)',
      text: 'var(--success-text)',
      icon: 'var(--success-icon)',
    },
    error: {
      bg: 'var(--danger-bg)',
      border: 'var(--danger-border)',
      text: 'var(--danger-text)',
      icon: 'var(--danger-icon)',
    },
    warning: {
      bg: 'var(--warning-bg)',
      border: 'var(--warning-border)',
      text: 'var(--warning-text)',
      icon: 'var(--warning-icon)',
    },
    info: {
      bg: 'var(--info-bg)',
      border: 'var(--info-border)',
      text: 'var(--info-text)',
      icon: 'var(--info-icon)',
    },
  }

  const Icon = icons[toast.type]
  const color = colors[toast.type]

  return (
    <motion.div
      initial={{ opacity: 0, x: 100, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.95 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
      style={{
        background: color.bg,
        borderColor: color.border,
      }}
      className="flex items-start gap-3 p-4 rounded-xl border-2 shadow-lg min-w-[320px]"
    >
      <Icon size={24} weight="bold" style={{ color: color.icon, flexShrink: 0 }} />
      
      <p className="flex-1 type-body-sm font-medium" style={{ color: color.text }}>
        {toast.message}
      </p>

      <button
        onClick={() => onClose(toast.id)}
        className="btn-icon w-6 h-6"
        style={{ color: color.text }}
      >
        <X size={16} weight="bold" />
      </button>
    </motion.div>
  )
}
