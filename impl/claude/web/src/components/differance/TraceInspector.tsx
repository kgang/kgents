/**
 * TraceInspector — Detailed Trace View for Differance DevEx
 *
 * Shows full details of a single trace, including:
 * - Operation and context
 * - Inputs and outputs
 * - "Why this path?" explanation
 * - Ghost alternatives with exploration options
 * - Polynomial state before/after
 *
 * Design Principles (from differance-devex-enlightenment.md):
 * - "Progressive Disclosure": Badge → Timeline → Inspector → Full Graph
 * - "Ghosts Are Friends": Roads not taken feel inviting, not haunting
 * - "Generative, Not Archival": Answer "What should I do next?"
 *
 * ASCII Reference:
 * ```
 * ┌─────────────────────────────────────────────────┐
 * │  crystallize()                         2m ago   │
 * ├─────────────────────────────────────────────────┤
 * │  INPUTS:  concept_id="auth_patterns"            │
 * │  OUTPUT:  crystal_id="crys_7f3a..."             │
 * │  CONTEXT: "User requested memory formation"     │
 * ├─────────────────────────────────────────────────┤
 * │  WHY THIS PATH?                                 │
 * │  → Selected over defer() because context was    │
 * │    sufficient (confidence: 0.87)                │
 * ├─────────────────────────────────────────────────┤
 * │  GHOSTS (1):                                    │
 * │  ○ defer() — "needs more context"               │
 * │    [Explore] [Dismiss]                          │
 * └─────────────────────────────────────────────────┘
 * ```
 *
 * @see spec/protocols/differance.md
 * @see plans/differance-devex-enlightenment.md - Phase 7B
 */

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  GitBranch,
  ChevronDown,
  ChevronRight,
  ArrowRight,
  Sparkles,
  Layers,
  Play,
  Copy,
  Check,
  AlertCircle,
} from 'lucide-react';
import { EARTH, GREEN, GLOW } from '@/constants/livingEarth';
import { useTraceAt, useWhyExplain, type AtAlternative } from '@/hooks/useDifferanceQuery';
import { Breathe } from '@/components/joy';

// =============================================================================
// Types
// =============================================================================

export interface TraceInspectorProps {
  /** Trace ID to inspect */
  traceId: string;
  /** Callback when closed */
  onClose: () => void;
  /** Callback when a ghost is selected for exploration */
  onExploreGhost?: (ghostOperation: string, ghostInputs: string[]) => void;
  /** Callback to replay from this trace */
  onReplayFrom?: (traceId: string) => void;
  /** Callback to navigate to parent trace */
  onNavigateToParent?: (traceId: string) => void;
  /** Callback to view full heritage graph */
  onViewHeritage?: (traceId: string) => void;
  /** Compact mode */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Helper Functions
// =============================================================================

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatRelativeTime(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatTimestamp(timestamp);
}

function truncateOutput(output: unknown, maxLength: number = 100): string {
  if (output === null || output === undefined) return '—';
  if (typeof output === 'string') {
    return output.length > maxLength ? output.slice(0, maxLength) + '...' : output;
  }
  const str = JSON.stringify(output, null, 0);
  return str.length > maxLength ? str.slice(0, maxLength) + '...' : str;
}

// =============================================================================
// Sub-Components
// =============================================================================

interface GhostCardProps {
  ghost: AtAlternative;
  onExplore?: () => void;
  compact?: boolean;
}

function GhostCard({ ghost, onExplore, compact }: GhostCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="rounded-lg overflow-hidden"
      style={{
        backgroundColor: `${EARTH.bark}50`,
        border: `1px dashed ${EARTH.clay}`,
      }}
    >
      <div className={`flex items-start gap-3 ${compact ? 'p-2' : 'p-3'}`}>
        {/* Ghost indicator */}
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: `${EARTH.wood}40` }}
        >
          <GitBranch className="w-4 h-4" style={{ color: EARTH.sand }} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className={`font-medium ${compact ? 'text-xs' : 'text-sm'}`}
              style={{ color: EARTH.sand }}
            >
              {ghost.operation}
            </span>
            {ghost.could_revisit && (
              <span
                className="text-[10px] px-1.5 py-0.5 rounded"
                style={{ backgroundColor: `${GREEN.sage}30`, color: GREEN.sprout }}
              >
                explorable
              </span>
            )}
          </div>
          <div
            className={`${compact ? 'text-[10px]' : 'text-xs'} mt-0.5`}
            style={{ color: EARTH.clay }}
          >
            {ghost.reason || 'No reason recorded'}
          </div>
          {ghost.inputs.length > 0 && (
            <div
              className={`${compact ? 'text-[10px]' : 'text-xs'} mt-1`}
              style={{ color: EARTH.clay }}
            >
              inputs: {ghost.inputs.join(', ')}
            </div>
          )}
        </div>

        {/* Actions */}
        {ghost.could_revisit && onExplore && (
          <button
            onClick={onExplore}
            className="flex-shrink-0 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors"
            style={{
              backgroundColor: `${GREEN.sage}30`,
              color: GREEN.sprout,
            }}
          >
            Explore
          </button>
        )}
      </div>
    </motion.div>
  );
}

interface StateViewerProps {
  title: string;
  positions: Record<string, string[]>;
  compact?: boolean;
}

function StateViewer({ title, positions, compact }: StateViewerProps) {
  const [expanded, setExpanded] = useState(false);
  const isEmpty = Object.keys(positions).length === 0;

  return (
    <div
      className="rounded-lg overflow-hidden"
      style={{ backgroundColor: `${GREEN.moss}30`, border: `1px solid ${GREEN.fern}40` }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className={`w-full flex items-center justify-between ${compact ? 'px-2 py-1.5' : 'px-3 py-2'} text-left`}
      >
        <span
          className={`font-medium ${compact ? 'text-[10px]' : 'text-xs'}`}
          style={{ color: GREEN.sprout }}
        >
          {title}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-[10px]" style={{ color: GREEN.mint }}>
            {Object.keys(positions).length} positions
          </span>
          {expanded ? (
            <ChevronDown className="w-3.5 h-3.5" style={{ color: GREEN.mint }} />
          ) : (
            <ChevronRight className="w-3.5 h-3.5" style={{ color: GREEN.mint }} />
          )}
        </div>
      </button>

      <AnimatePresence>
        {expanded && !isEmpty && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className={`${compact ? 'px-2 pb-2' : 'px-3 pb-3'} overflow-hidden`}
          >
            <div className="space-y-1">
              {Object.entries(positions).map(([key, values]) => (
                <div key={key} className="flex items-start gap-2">
                  <code
                    className="text-[10px] px-1 py-0.5 rounded"
                    style={{ backgroundColor: `${GREEN.fern}30`, color: GREEN.sprout }}
                  >
                    {key}
                  </code>
                  <span className="text-[10px]" style={{ color: EARTH.sand }}>
                    {values.join(', ')}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function TraceInspector({
  traceId,
  onClose,
  onExploreGhost,
  onReplayFrom,
  onNavigateToParent,
  onViewHeritage,
  compact = false,
  className = '',
}: TraceInspectorProps) {
  const [copied, setCopied] = useState(false);
  const [showState, setShowState] = useState(false);

  // Fetch trace details
  const { data: trace, isLoading, error } = useTraceAt(traceId, { enabled: !!traceId });

  // Fetch why explanation
  const { data: why } = useWhyExplain(traceId, {
    enabled: !!traceId,
    format: 'summary',
  });

  const handleCopyId = useCallback(async () => {
    await navigator.clipboard.writeText(traceId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [traceId]);

  const handleExploreGhost = useCallback(
    (ghost: AtAlternative) => {
      onExploreGhost?.(ghost.operation, ghost.inputs);
    },
    [onExploreGhost]
  );

  const padding = compact ? 'p-3' : 'p-4';
  const headerPadding = compact ? 'px-3 py-2' : 'px-4 py-3';

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className={`rounded-xl overflow-hidden flex flex-col ${className}`}
      style={{
        backgroundColor: EARTH.soil,
        border: `1px solid ${EARTH.wood}`,
      }}
    >
      {/* Header */}
      <div
        className={`flex items-center justify-between ${headerPadding}`}
        style={{ backgroundColor: `${EARTH.bark}80` }}
      >
        <div className="flex items-center gap-2 min-w-0">
          <Breathe intensity={0.2} speed="slow">
            <Sparkles className={compact ? 'w-4 h-4' : 'w-5 h-5'} style={{ color: GLOW.amber }} />
          </Breathe>
          <span
            className={`font-medium truncate ${compact ? 'text-xs' : 'text-sm'}`}
            style={{ color: GLOW.lantern }}
          >
            Trace Inspector
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Copy ID */}
          <button
            onClick={handleCopyId}
            className="p-1.5 rounded transition-colors"
            style={{ backgroundColor: `${EARTH.bark}60` }}
            title="Copy trace ID"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5" style={{ color: GREEN.sprout }} />
            ) : (
              <Copy className="w-3.5 h-3.5" style={{ color: EARTH.sand }} />
            )}
          </button>

          {/* Close */}
          <button
            onClick={onClose}
            className="p-1.5 rounded transition-colors"
            style={{ backgroundColor: `${EARTH.bark}60` }}
            title="Close inspector"
          >
            <X className="w-3.5 h-3.5" style={{ color: EARTH.sand }} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className={`flex-1 overflow-auto ${padding}`}>
        {/* Loading */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-8">
            <Breathe intensity={0.5} speed="fast">
              <Sparkles className="w-6 h-6" style={{ color: GLOW.amber }} />
            </Breathe>
            <span className="text-xs mt-2" style={{ color: EARTH.sand }}>
              Loading trace...
            </span>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex flex-col items-center justify-center py-8">
            <AlertCircle className="w-6 h-6" style={{ color: GLOW.copper }} />
            <span className="text-xs mt-2" style={{ color: EARTH.sand }}>
              {error.message}
            </span>
          </div>
        )}

        {/* Trace details */}
        {trace && !isLoading && (
          <div className="space-y-4">
            {/* Operation header */}
            <div>
              <div className="flex items-center justify-between">
                <h2
                  className={`font-bold ${compact ? 'text-base' : 'text-lg'}`}
                  style={{ color: GLOW.lantern }}
                >
                  {trace.operation}
                </h2>
                <span className="text-xs" style={{ color: EARTH.clay }}>
                  {formatRelativeTime(trace.timestamp)}
                </span>
              </div>
              <div className="text-xs mt-1" style={{ color: EARTH.sand }}>
                {trace.context || 'No context recorded'}
              </div>
            </div>

            {/* Inputs */}
            {trace.inputs.length > 0 && (
              <div>
                <div
                  className={`font-medium mb-1.5 ${compact ? 'text-[10px]' : 'text-xs'}`}
                  style={{ color: EARTH.clay }}
                >
                  INPUTS
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {trace.inputs.map((input, i) => (
                    <code
                      key={i}
                      className="text-xs px-2 py-1 rounded"
                      style={{ backgroundColor: `${GREEN.moss}50`, color: GREEN.sprout }}
                    >
                      {input}
                    </code>
                  ))}
                </div>
              </div>
            )}

            {/* Output */}
            <div>
              <div
                className={`font-medium mb-1.5 ${compact ? 'text-[10px]' : 'text-xs'}`}
                style={{ color: EARTH.clay }}
              >
                OUTPUT
              </div>
              <div
                className="text-xs px-3 py-2 rounded font-mono overflow-x-auto"
                style={{ backgroundColor: `${GREEN.moss}30`, color: GLOW.lantern }}
              >
                {truncateOutput(trace.output, 200)}
              </div>
            </div>

            {/* Why explanation */}
            {why && why.summary && (
              <div
                className="rounded-lg p-3"
                style={{ backgroundColor: `${GLOW.amber}10`, border: `1px solid ${GLOW.amber}30` }}
              >
                <div
                  className={`font-medium mb-1.5 ${compact ? 'text-[10px]' : 'text-xs'}`}
                  style={{ color: GLOW.amber }}
                >
                  WHY THIS PATH?
                </div>
                <div className="text-xs italic" style={{ color: GLOW.honey }}>
                  {why.summary}
                </div>
              </div>
            )}

            {/* Ghosts */}
            {trace.alternatives.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <div
                    className={`font-medium ${compact ? 'text-[10px]' : 'text-xs'}`}
                    style={{ color: EARTH.clay }}
                  >
                    GHOSTS
                  </div>
                  <span
                    className="text-[10px] px-1.5 py-0.5 rounded-full"
                    style={{ backgroundColor: `${EARTH.wood}40`, color: EARTH.sand }}
                  >
                    {trace.alternatives.length}
                  </span>
                </div>
                <div className="space-y-2">
                  {trace.alternatives.map((ghost, i) => (
                    <GhostCard
                      key={i}
                      ghost={ghost}
                      onExplore={() => handleExploreGhost(ghost)}
                      compact={compact}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Polynomial state toggle */}
            <div>
              <button
                onClick={() => setShowState(!showState)}
                className={`flex items-center gap-2 w-full ${compact ? 'px-2 py-1.5' : 'px-3 py-2'} rounded-lg text-left transition-colors`}
                style={{ backgroundColor: `${EARTH.bark}40` }}
              >
                <Layers className="w-4 h-4" style={{ color: EARTH.sand }} />
                <span
                  className={`${compact ? 'text-[10px]' : 'text-xs'}`}
                  style={{ color: EARTH.sand }}
                >
                  Polynomial State
                </span>
                {showState ? (
                  <ChevronDown className="w-3.5 h-3.5 ml-auto" style={{ color: EARTH.clay }} />
                ) : (
                  <ChevronRight className="w-3.5 h-3.5 ml-auto" style={{ color: EARTH.clay }} />
                )}
              </button>

              <AnimatePresence>
                {showState && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="mt-2 space-y-2 overflow-hidden"
                  >
                    <StateViewer
                      title="Before"
                      positions={trace.positions_before}
                      compact={compact}
                    />
                    <div className="flex justify-center">
                      <ArrowRight className="w-4 h-4" style={{ color: EARTH.clay }} />
                    </div>
                    <StateViewer
                      title="After"
                      positions={trace.positions_after}
                      compact={compact}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Parent trace link */}
            {trace.parent_trace_id && onNavigateToParent && (
              <button
                onClick={() => onNavigateToParent(trace.parent_trace_id!)}
                className="flex items-center gap-2 text-xs w-full"
                style={{ color: GREEN.sprout }}
              >
                <ArrowRight className="w-3 h-3 rotate-180" />
                <span>Parent: {trace.parent_trace_id.slice(0, 12)}...</span>
              </button>
            )}
          </div>
        )}
      </div>

      {/* Footer actions */}
      {trace && (
        <div
          className={`flex gap-2 ${headerPadding}`}
          style={{ borderTop: `1px solid ${EARTH.wood}40` }}
        >
          {onReplayFrom && (
            <button
              onClick={() => onReplayFrom(traceId)}
              className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-colors"
              style={{ backgroundColor: `${GREEN.sage}30`, color: GREEN.sprout }}
            >
              <Play className="w-3.5 h-3.5" />
              Replay from here
            </button>
          )}
          {onViewHeritage && (
            <button
              onClick={() => onViewHeritage(traceId)}
              className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-colors"
              style={{ backgroundColor: `${GLOW.amber}20`, color: GLOW.amber }}
            >
              <GitBranch className="w-3.5 h-3.5" />
              Full heritage
            </button>
          )}
        </div>
      )}
    </motion.div>
  );
}

export default TraceInspector;
