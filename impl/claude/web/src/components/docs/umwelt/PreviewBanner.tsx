/**
 * PreviewBanner - Shows when viewing as a different observer
 *
 * "See what this aspect looks like with elevated access"
 *
 * This banner appears when the user is in preview mode, temporarily
 * viewing the UI as if they had a different observer archetype.
 *
 * Features:
 * - Clear visual indicator that you're in preview mode
 * - One-click exit
 * - Auto-exit countdown (60s)
 * - Non-intrusive but unmissable
 *
 * @see plans/umwelt-v2-expansion.md (2C. Ghost Aspect Interaction)
 */

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, X, Clock } from 'lucide-react';
import { getObserverColor } from './umwelt.types';

// =============================================================================
// Types
// =============================================================================

interface PreviewBannerProps {
  /** The archetype being previewed */
  previewArchetype: string;
  /** Callback to exit preview mode */
  onExit: () => void;
  /** Whether to show countdown (default: true) */
  showCountdown?: boolean;
  /** Total preview duration in ms (default: 60000 = 60s) */
  duration?: number;
}

// =============================================================================
// Component
// =============================================================================

export function PreviewBanner({
  previewArchetype,
  onExit,
  showCountdown = true,
  duration = 60000,
}: PreviewBannerProps) {
  const [timeLeft, setTimeLeft] = useState(Math.floor(duration / 1000));
  const observerColor = getObserverColor(previewArchetype);

  // Countdown timer
  useEffect(() => {
    if (!showCountdown) return;

    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [showCountdown]);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: -50, opacity: 0 }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        className="fixed top-0 left-0 right-0 z-50"
        style={{
          background: `linear-gradient(to right, ${observerColor}20, ${observerColor}10, ${observerColor}20)`,
          borderBottom: `1px solid ${observerColor}40`,
        }}
      >
        <div className="max-w-7xl mx-auto px-4 py-2">
          <div className="flex items-center justify-between">
            {/* Left: Preview indicator */}
            <div className="flex items-center gap-3">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center"
                style={{ backgroundColor: `${observerColor}30` }}
              >
                <Eye className="w-4 h-4" style={{ color: observerColor }} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">
                    Previewing as{' '}
                    <span className="capitalize" style={{ color: observerColor }}>
                      {previewArchetype}
                    </span>
                  </span>
                  <span
                    className="px-2 py-0.5 text-xs rounded-full"
                    style={{
                      backgroundColor: `${observerColor}20`,
                      color: observerColor,
                    }}
                  >
                    Preview Mode
                  </span>
                </div>
                <p className="text-xs text-gray-400">
                  Viewing with elevated capabilities • Actions are read-only
                </p>
              </div>
            </div>

            {/* Right: Countdown and exit */}
            <div className="flex items-center gap-4">
              {showCountdown && timeLeft > 0 && (
                <div className="flex items-center gap-1.5 text-gray-400">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm tabular-nums">{timeLeft}s</span>
                </div>
              )}
              <button
                onClick={onExit}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                           bg-gray-700/50 text-gray-300 text-sm font-medium
                           hover:bg-gray-600/50 transition-colors"
              >
                <X className="w-4 h-4" />
                <span>Exit Preview</span>
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

/**
 * Compact version for mobile/tablet.
 */
export function PreviewBannerCompact({
  previewArchetype,
  onExit,
}: Pick<PreviewBannerProps, 'previewArchetype' | 'onExit'>) {
  const observerColor = getObserverColor(previewArchetype);

  return (
    <motion.div
      initial={{ height: 0, opacity: 0 }}
      animate={{ height: 'auto', opacity: 1 }}
      exit={{ height: 0, opacity: 0 }}
      className="overflow-hidden"
      style={{
        backgroundColor: `${observerColor}10`,
        borderBottom: `1px solid ${observerColor}30`,
      }}
    >
      <div className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4" style={{ color: observerColor }} />
          <span className="text-sm text-gray-300">
            Preview:{' '}
            <span className="capitalize font-medium" style={{ color: observerColor }}>
              {previewArchetype}
            </span>
          </span>
        </div>
        <button
          onClick={onExit}
          className="p-1.5 rounded-lg hover:bg-gray-700/50 transition-colors"
        >
          <X className="w-4 h-4 text-gray-400" />
        </button>
      </div>
    </motion.div>
  );
}

export default PreviewBanner;
