import { useOfflineSync } from '@/hooks/useOfflineSync'
import { WifiSlash, ArrowsClockwise } from '@phosphor-icons/react'
import { motion, AnimatePresence } from 'motion/react'

export default function OfflineIndicator() {
  const { isOnline, isSyncing, queueCount } = useOfflineSync()

  if (isOnline && queueCount === 0) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: -100, opacity: 0 }}
        className="fixed top-0 left-0 right-0 z-50 bg-warning-bg border-b-2 border-warning-border"
      >
        <div className="container-sm py-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {!isOnline ? (
              <>
                <WifiSlash size={20} weight="bold" className="text-warning-icon" />
                <span className="type-body-sm text-warning-text font-semibold">
                  You're offline
                </span>
              </>
            ) : isSyncing ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <ArrowsClockwise size={20} weight="bold" className="text-info-icon" />
                </motion.div>
                <span className="type-body-sm text-info-text font-semibold">
                  Syncing...
                </span>
              </>
            ) : (
              <>
                <ArrowsClockwise size={20} weight="bold" className="text-warning-icon" />
                <span className="type-body-sm text-warning-text font-semibold">
                  {queueCount} item{queueCount !== 1 ? 's' : ''} pending sync
                </span>
              </>
            )}
          </div>

          {!isOnline && (
            <span className="type-caption text-warning-text">
              Changes will sync when online
            </span>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
