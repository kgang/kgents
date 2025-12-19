/**
 * KeyboardHints - Overlay showing available keyboard shortcuts
 *
 * Press '?' to show this overlay. Groups shortcuts by category
 * with a tasteful, minimal design.
 *
 * @see spec/protocols/os-shell.md
 */

import { useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Keyboard } from 'lucide-react';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import type { KeyboardShortcut } from './useKeyboardShortcuts';

// =============================================================================
// Types
// =============================================================================

export interface KeyboardHintsProps {
  /** Whether the overlay is visible */
  isOpen: boolean;
  /** Callback to close the overlay */
  onClose: () => void;
  /** List of shortcuts to display */
  shortcuts: KeyboardShortcut[];
}

// =============================================================================
// Constants
// =============================================================================

const CATEGORY_LABELS: Record<string, string> = {
  navigation: 'Navigation',
  panels: 'Panels',
  actions: 'Actions',
  terminal: 'Terminal',
};

const CATEGORY_ORDER = ['actions', 'panels', 'terminal', 'navigation'];

// =============================================================================
// Component
// =============================================================================

/**
 * KeyboardHints - Modal overlay showing keyboard shortcuts.
 *
 * @example
 * ```tsx
 * <KeyboardHints
 *   isOpen={showHints}
 *   onClose={() => setShowHints(false)}
 *   shortcuts={shortcuts}
 * />
 * ```
 */
export function KeyboardHints({ isOpen, onClose, shortcuts }: KeyboardHintsProps) {
  const { shouldAnimate } = useMotionPreferences();

  // Close on Escape
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, handleKeyDown]);

  // Group shortcuts by category
  const groupedShortcuts = shortcuts.reduce(
    (acc, shortcut) => {
      const category = shortcut.category;
      if (!acc[category]) acc[category] = [];
      acc[category].push(shortcut);
      return acc;
    },
    {} as Record<string, KeyboardShortcut[]>
  );

  // Sort categories
  const sortedCategories = CATEGORY_ORDER.filter((cat) => groupedShortcuts[cat]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: shouldAnimate ? 0.15 : 0 }}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{
              duration: shouldAnimate ? 0.2 : 0,
              ease: [0.4, 0, 0.2, 1],
            }}
            className="fixed z-50 top-[20%] left-1/2 -translate-x-1/2 w-full max-w-md"
          >
            <div className="bg-gray-800/95 backdrop-blur-md rounded-xl border border-gray-700/50 shadow-2xl overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
                <div className="flex items-center gap-3">
                  <Keyboard className="w-5 h-5 text-cyan-400" />
                  <h2 className="text-lg font-semibold text-white">Keyboard Shortcuts</h2>
                </div>
                <button
                  onClick={onClose}
                  className="p-1.5 hover:bg-gray-700/50 rounded-lg transition-colors"
                  aria-label="Close"
                >
                  <X className="w-4 h-4 text-gray-400" />
                </button>
              </div>

              {/* Content */}
              <div className="px-5 py-4 space-y-5 max-h-[60vh] overflow-auto">
                {sortedCategories.map((category) => (
                  <div key={category}>
                    <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                      {CATEGORY_LABELS[category] || category}
                    </h3>
                    <div className="space-y-1">
                      {groupedShortcuts[category].map((shortcut) => (
                        <div
                          key={shortcut.id}
                          className="flex items-center justify-between py-1.5"
                        >
                          <span className="text-sm text-gray-300">{shortcut.label}</span>
                          <kbd className="px-2 py-1 text-xs font-mono bg-gray-700/50 border border-gray-600/50 rounded text-gray-300">
                            {shortcut.keys}
                          </kbd>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Footer */}
              <div className="px-5 py-3 border-t border-gray-700/50 bg-gray-800/50">
                <p className="text-xs text-gray-500 text-center">
                  Press <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-gray-700/50 border border-gray-600/50 rounded">Esc</kbd> to close
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default KeyboardHints;
