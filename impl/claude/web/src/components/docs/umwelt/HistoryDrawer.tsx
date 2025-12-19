/**
 * HistoryDrawer - Exploration breadcrumbs through Umwelt space
 *
 * "Session Timeline - Track your observer switches as exploration traces"
 *
 * This drawer shows the history of observer switches in the current session,
 * allowing users to:
 * - See where they've been
 * - Revert to a previous observer state
 * - Understand how different observers perceive differently
 *
 * @see plans/umwelt-v2-expansion.md (3A. Observer History + Exploration Breadcrumbs)
 */

import { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { History, RotateCcw, Trash2, X, ArrowRight, Plus, Minus } from 'lucide-react';
import type { UmweltTrace } from './umwelt.types';
import { getObserverColor } from './umwelt.types';

// =============================================================================
// Types
// =============================================================================

interface HistoryDrawerProps {
  /** Whether the drawer is open */
  isOpen: boolean;
  /** Close the drawer */
  onClose: () => void;
  /** History entries (most recent last) */
  history: UmweltTrace[];
  /** Current observer archetype (for highlighting) */
  currentArchetype: string;
  /** Callback when user wants to revert to an entry */
  onRevert: (entryId: string) => void;
  /** Callback to clear all history */
  onClear: () => void;
}

// =============================================================================
// Helpers
// =============================================================================

function formatTimeAgo(timestamp: number): string {
  const seconds = Math.floor((Date.now() - timestamp) / 1000);

  if (seconds < 60) return 'just now';
  if (seconds < 120) return '1 min ago';
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
  if (seconds < 7200) return '1 hour ago';
  return `${Math.floor(seconds / 3600)} hours ago`;
}

function formatTime(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
}

// =============================================================================
// Component
// =============================================================================

export function HistoryDrawer({
  isOpen,
  onClose,
  history,
  currentArchetype,
  onRevert,
  onClear,
}: HistoryDrawerProps) {
  // Reverse history so most recent is at top
  const reversedHistory = useMemo(() => [...history].reverse(), [history]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 300, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 500, damping: 40 }}
            className="fixed right-0 top-0 bottom-0 w-80 bg-gray-800 border-l border-gray-700 z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-cyan-400" />
                <h2 className="font-semibold text-white">Exploration History</h2>
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg hover:bg-gray-700 transition-colors"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4">
              {reversedHistory.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No observer switches yet</p>
                  <p className="text-xs mt-1">Switch observers to build your history</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* Current state indicator */}
                  <div className="flex items-center gap-2 mb-4">
                    <div
                      className="w-3 h-3 rounded-full animate-pulse"
                      style={{ backgroundColor: getObserverColor(currentArchetype) }}
                    />
                    <span className="text-sm text-gray-300">
                      Currently:{' '}
                      <span
                        className="font-medium capitalize"
                        style={{ color: getObserverColor(currentArchetype) }}
                      >
                        {currentArchetype}
                      </span>
                    </span>
                  </div>

                  {/* History entries */}
                  {reversedHistory.map((entry, idx) => (
                    <HistoryEntry
                      key={entry.id}
                      entry={entry}
                      isLatest={idx === 0}
                      onRevert={() => onRevert(entry.id)}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            {reversedHistory.length > 0 && (
              <div className="p-4 border-t border-gray-700">
                <button
                  onClick={onClear}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg
                             bg-gray-700/50 text-gray-400 text-sm
                             hover:bg-red-500/20 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Clear History</span>
                </button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// =============================================================================
// Subcomponents
// =============================================================================

interface HistoryEntryProps {
  entry: UmweltTrace;
  isLatest: boolean;
  onRevert: () => void;
}

function HistoryEntry({ entry, isLatest, onRevert }: HistoryEntryProps) {
  const fromColor = getObserverColor(entry.from.archetype);
  const toColor = getObserverColor(entry.to.archetype);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        p-3 rounded-lg border
        ${isLatest ? 'border-cyan-500/30 bg-cyan-500/5' : 'border-gray-700 bg-gray-700/30'}
      `}
    >
      {/* Observer transition */}
      <div className="flex items-center gap-2 mb-2">
        <span
          className="text-sm font-medium capitalize"
          style={{ color: fromColor }}
        >
          {entry.from.archetype}
        </span>
        <ArrowRight className="w-3 h-3 text-gray-500" />
        <span
          className="text-sm font-medium capitalize"
          style={{ color: toColor }}
        >
          {entry.to.archetype}
        </span>
        {isLatest && (
          <span className="ml-auto text-xs text-cyan-400">(latest)</span>
        )}
      </div>

      {/* Diff summary */}
      <div className="flex items-center gap-3 text-xs text-gray-400 mb-2">
        {entry.diff.revealedCount > 0 && (
          <span className="flex items-center gap-1 text-green-400">
            <Plus className="w-3 h-3" />
            {entry.diff.revealedCount} revealed
          </span>
        )}
        {entry.diff.hiddenCount > 0 && (
          <span className="flex items-center gap-1 text-amber-400">
            <Minus className="w-3 h-3" />
            {entry.diff.hiddenCount} hidden
          </span>
        )}
      </div>

      {/* Timestamp and path */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span title={formatTime(entry.timestamp)}>{formatTimeAgo(entry.timestamp)}</span>
        {entry.activePath && (
          <span className="truncate max-w-[120px]" title={entry.activePath}>
            @ {entry.activePath.split('.').pop()}
          </span>
        )}
      </div>

      {/* Revert button */}
      <button
        onClick={onRevert}
        className="mt-2 w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md
                   bg-gray-600/30 text-gray-400 text-xs
                   hover:bg-gray-600/50 hover:text-gray-200 transition-colors"
      >
        <RotateCcw className="w-3 h-3" />
        <span>Revert to {entry.from.archetype}</span>
      </button>
    </motion.div>
  );
}

export default HistoryDrawer;
