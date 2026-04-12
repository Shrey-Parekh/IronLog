import { usePWAInstall } from '@/hooks/usePWAInstall'
import { X, Download } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'motion/react'

export default function PWAInstallBanner() {
  const { isInstallable, promptInstall, dismissPrompt } = usePWAInstall()

  if (!isInstallable) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        className="fixed bottom-20 left-4 right-4 z-50 md:left-auto md:right-4 md:max-w-md"
      >
        <div className="card-raised p-4">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 rounded-xl bg-sage-100 flex items-center justify-center flex-shrink-0">
              <Download size={24} weight="bold" className="text-sage-600" />
            </div>

            <div className="flex-1 min-w-0">
              <h3 className="type-h3 mb-1">Install IronLog</h3>
              <p className="type-body-sm text-text-secondary mb-3">
                Install the app for offline access and a better experience
              </p>

              <div className="flex gap-2">
                <button
                  onClick={promptInstall}
                  className="btn-primary flex-1"
                >
                  Install
                </button>
                <button
                  onClick={dismissPrompt}
                  className="btn-secondary"
                >
                  Not now
                </button>
              </div>
            </div>

            <button
              onClick={dismissPrompt}
              className="btn-icon flex-shrink-0"
            >
              <X size={20} weight="bold" />
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
