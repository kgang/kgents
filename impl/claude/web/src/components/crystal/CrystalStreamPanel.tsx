/**
 * CrystalStreamPanel - Real-time crystal event display.
 *
 * Shows incoming crystals as they're created via SSE stream.
 * Animates new crystals appearing and provides event history.
 *
 * Features:
 * - Real-time SSE subscription
 * - Event type filtering
 * - Connection status indicator
 * - Event buffer with scrollable history
 *
 * @see spec/protocols/witness-crystallization.md
 * @see services/witness/stream.py
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import { useCrystalStream, type StreamStatus } from '../../hooks/useCrystalStream';
import { type CrystalEvent, type CrystalLevel, CRYSTAL_LEVELS, getLevelColor } from '../../api/crystal';

// =============================================================================
// Types
// =============================================================================

interface CrystalStreamPanelProps {
  /** Filter to specific level */
  level?: CrystalLevel;
  /** Max events to show (default: 20) */
  maxEvents?: number;
  /** Optional className */
  className?: string;
  /** Height in pixels */
  height?: number;
  /** Callback when crystal is clicked */
  onCrystalClick?: (crystalId: string) => void;
}

// =============================================================================
// Components
// =============================================================================

/**
 * Status indicator badge.
 */
function StatusBadge({ status }: { status: StreamStatus }) {
  const config: Record<StreamStatus, { color: string; label: string; pulse: boolean }> = {
    disconnected: { color: '#6b7280', label: 'Disconnected', pulse: false },
    connecting: { color: '#f59e0b', label: 'Connecting...', pulse: true },
    connected: { color: '#22c55e', label: 'Live', pulse: true },
    reconnecting: { color: '#f59e0b', label: 'Reconnecting...', pulse: true },
    error: { color: '#ef4444', label: 'Error', pulse: false },
  };

  const { color, label, pulse } = config[status];

  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <div
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: color }}
        />
        {pulse && (
          <motion.div
            className="absolute inset-0 w-2 h-2 rounded-full"
            style={{ backgroundColor: color }}
            animate={{ scale: [1, 2], opacity: [0.5, 0] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          />
        )}
      </div>
      <span className="text-xs text-gray-400">{label}</span>
    </div>
  );
}

/**
 * Single crystal event card.
 */
function CrystalEventCard({
  event,
  onClick,
}: {
  event: CrystalEvent;
  onClick?: (crystalId: string) => void;
}) {
  const isCreate = event.type === 'crystal.created';
  const isBatch = event.type === 'crystal.batch';

  if (!isCreate && !isBatch) {
    return null;
  }

  const level = event.data.level as CrystalLevel | undefined;
  const levelColor = level ? getLevelColor(level) : '#6b7280';

  if (isBatch) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 20 }}
        className="p-3 bg-gray-800/50 rounded-lg border border-gray-700"
      >
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-300">
            📦 Batch: {event.data.count} crystals
          </span>
          <span className="text-xs text-gray-500">
            {new Date(event.timestamp).toLocaleTimeString()}
          </span>
        </div>
        {event.data.crystals && event.data.crystals.length > 0 && (
          <div className="mt-2 space-y-1">
            {event.data.crystals.slice(0, 3).map((c) => (
              <div
                key={c.id}
                className="text-xs text-gray-400 truncate cursor-pointer hover:text-gray-200"
                onClick={() => onClick?.(c.id)}
              >
                [{c.level}] {c.insight}
              </div>
            ))}
            {event.data.crystals.length > 3 && (
              <div className="text-xs text-gray-500">
                +{event.data.crystals.length - 3} more
              </div>
            )}
          </div>
        )}
      </motion.div>
    );
  }

  // Single crystal create
  return (
    <motion.div
      initial={{ opacity: 0, x: -20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 20 }}
      className="p-3 rounded-lg border cursor-pointer hover:border-gray-500 transition-colors"
      style={{
        backgroundColor: `${levelColor}10`,
        borderColor: `${levelColor}40`,
      }}
      onClick={() => event.data.id && onClick?.(event.data.id)}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span
            className="px-2 py-0.5 rounded text-xs font-medium"
            style={{ backgroundColor: levelColor, color: 'white' }}
          >
            {level || 'CRYSTAL'}
          </span>
          {event.data.confidence !== undefined && (
            <span className="text-xs text-gray-400">
              {Math.round(event.data.confidence * 100)}%
            </span>
          )}
        </div>
        <span className="text-xs text-gray-500">
          {new Date(event.timestamp).toLocaleTimeString()}
        </span>
      </div>

      <div className="text-sm text-white line-clamp-2">
        {event.data.insight || 'New crystal created'}
      </div>

      {event.data.significance && (
        <div className="mt-1 text-xs text-gray-400 italic line-clamp-1">
          {event.data.significance}
        </div>
      )}

      {event.data.source_count !== undefined && (
        <div className="mt-2 text-xs text-gray-500">
          Compresses {event.data.source_count} sources
        </div>
      )}
    </motion.div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * CrystalStreamPanel component.
 *
 * Displays real-time crystal events with SSE subscription.
 */
export function CrystalStreamPanel({
  level,
  maxEvents = 20,
  className = '',
  height = 400,
  onCrystalClick,
}: CrystalStreamPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  const {
    status,
    events,
    eventCount,
    lastHeartbeat,
    connect,
    disconnect,
    clearEvents,
    isConnected,
  } = useCrystalStream({
    level,
    bufferSize: maxEvents,
  });

  // Filter to crystal events only
  const crystalEvents = events.filter(
    (e) => e.type === 'crystal.created' || e.type === 'crystal.batch'
  );

  // Auto-scroll to bottom on new events
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [crystalEvents.length, autoScroll]);

  // Detect manual scroll
  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop } = scrollRef.current;
    // If user scrolls down, disable auto-scroll
    setAutoScroll(scrollTop < 10);
  };

  return (
    <div
      className={`bg-gray-900 rounded-lg flex flex-col ${className}`}
      style={{ height }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <span className="font-medium text-white">Crystal Stream</span>
          <StatusBadge status={status} />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">
            {eventCount} events
          </span>

          <button
            onClick={clearEvents}
            className="px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs text-gray-300 transition-colors"
            title="Clear events"
          >
            Clear
          </button>

          <button
            onClick={isConnected ? disconnect : connect}
            className={`px-2 py-1 rounded text-xs transition-colors ${
              isConnected
                ? 'bg-red-900/50 hover:bg-red-800/50 text-red-300'
                : 'bg-green-900/50 hover:bg-green-800/50 text-green-300'
            }`}
          >
            {isConnected ? 'Pause' : 'Resume'}
          </button>
        </div>
      </div>

      {/* Level filter indicator */}
      {level && (
        <div className="px-3 py-2 bg-gray-800/50 border-b border-gray-800">
          <span className="text-xs text-gray-400">
            Filtering:{' '}
            <span
              className="font-medium"
              style={{ color: CRYSTAL_LEVELS[level].color }}
            >
              {level}
            </span>
          </span>
        </div>
      )}

      {/* Event list */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-3 space-y-2"
      >
        <AnimatePresence mode="popLayout">
          {crystalEvents.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center text-gray-500 py-8"
            >
              <div className="text-3xl mb-2">💎</div>
              <div className="text-sm">Waiting for crystals...</div>
              {lastHeartbeat && (
                <div className="text-xs mt-2">
                  Last heartbeat: {lastHeartbeat.toLocaleTimeString()}
                </div>
              )}
            </motion.div>
          ) : (
            crystalEvents.map((event, index) => (
              <CrystalEventCard
                key={`${event.timestamp}-${index}`}
                event={event}
                onClick={onCrystalClick}
              />
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Auto-scroll indicator */}
      {!autoScroll && crystalEvents.length > 0 && (
        <button
          onClick={() => {
            setAutoScroll(true);
            if (scrollRef.current) {
              scrollRef.current.scrollTop = 0;
            }
          }}
          className="absolute bottom-16 right-4 px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded-full text-xs text-white shadow-lg transition-colors"
        >
          ↑ New crystals
        </button>
      )}
    </div>
  );
}

export default CrystalStreamPanel;
