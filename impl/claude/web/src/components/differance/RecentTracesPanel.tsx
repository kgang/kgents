/**
 * RecentTracesPanel — Recent Heritage Traces Panel for Cockpit
 *
 * Shows the last N traces from the Différance Engine buffer/store.
 * Each trace can be expanded to show its WhyPanel explanation.
 *
 * Design Principles:
 * - Living Earth palette
 * - Progressive disclosure: trace list → WhyPanel → full heritage graph
 * - Fire-and-forget: fetching doesn't block
 *
 * @see spec/protocols/differance.md
 * @see plans/differance-crown-jewel-wiring.md Phase 6D
 */

import { useState, useCallback } from 'react';
import { Clock, GitBranch, ChevronRight, RefreshCw, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GLOW, EARTH, GREEN } from '@/constants/livingEarth';
import {
  useDifferanceManifest,
  useRecentTraces,
  type TracePreview as BackendTracePreview,
} from '@/hooks/useDifferanceQuery';
import { Breathe } from '@/components/joy';
import { WhyPanel } from './WhyPanel';
import { GhostBadge } from './GhostBadge';

// =============================================================================
// Types
// =============================================================================

export interface RecentTracesPanelProps {
  /** Maximum traces to display */
  limit?: number;
  /** Callback when "View All" is clicked */
  onViewAll?: () => void;
  /** Callback when a trace is selected for heritage exploration */
  onExploreHeritage?: (traceId: string) => void;
  /** Compact mode for smaller spaces */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// UI trace preview type (camelCase for React conventions)
interface TracePreview {
  id: string;
  operation: string;
  context: string;
  timestamp: string;
  ghostCount: number;
  outputPreview?: string;
  jewel?: string;
}

// =============================================================================
// Helper Functions
// =============================================================================

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
  return date.toLocaleDateString();
}

/**
 * Transform backend trace (snake_case) to UI trace (camelCase).
 */
function toUITrace(trace: BackendTracePreview): TracePreview {
  return {
    id: trace.id,
    operation: trace.operation,
    context: trace.context,
    timestamp: trace.timestamp,
    ghostCount: trace.ghost_count,
    outputPreview: trace.output_preview,
    jewel: trace.jewel,
  };
}

// =============================================================================
// Sub-Components
// =============================================================================

function TraceItem({
  trace,
  isExpanded,
  onClick,
  onExploreHeritage,
  compact,
}: {
  trace: TracePreview;
  isExpanded: boolean;
  onClick: () => void;
  onExploreHeritage?: (traceId: string) => void;
  compact?: boolean;
}) {
  return (
    <div
      className="rounded-lg overflow-hidden"
      style={{
        backgroundColor: `${EARTH.bark}60`,
        border: `1px solid ${isExpanded ? GREEN.sage : EARTH.wood}40`,
      }}
    >
      {/* Trace Header */}
      <button
        onClick={onClick}
        className={`w-full flex items-center justify-between ${
          compact ? 'px-3 py-2' : 'px-4 py-3'
        } hover:brightness-110 transition-colors text-left`}
      >
        <div className="flex items-center gap-3 min-w-0 flex-1">
          {/* Operation icon */}
          <div
            className="w-8 h-8 rounded flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: `${GREEN.sage}30` }}
          >
            <GitBranch className="w-4 h-4" style={{ color: GREEN.sprout }} />
          </div>

          {/* Operation & context */}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span
                className={`font-medium truncate ${compact ? 'text-xs' : 'text-sm'}`}
                style={{ color: GLOW.lantern }}
              >
                {trace.operation}
              </span>
              {trace.ghostCount > 0 && <GhostBadge count={trace.ghostCount} size="sm" />}
            </div>
            <div
              className={`truncate ${compact ? 'text-[10px]' : 'text-xs'}`}
              style={{ color: EARTH.sand }}
            >
              {trace.context || trace.outputPreview || 'No context'}
            </div>
          </div>
        </div>

        {/* Timestamp & expand indicator */}
        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          <span className="text-[10px]" style={{ color: EARTH.clay }}>
            {formatRelativeTime(trace.timestamp)}
          </span>
          <ChevronRight
            className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
            style={{ color: EARTH.sand }}
          />
        </div>
      </button>

      {/* Expanded WhyPanel */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3">
              <WhyPanel
                outputId={trace.id}
                defaultExpanded={true}
                onExploreHeritage={onExploreHeritage}
                compact={compact}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function EmptyState({ compact }: { compact?: boolean }) {
  return (
    <div
      className={`flex flex-col items-center justify-center ${
        compact ? 'py-6' : 'py-8'
      } text-center`}
    >
      <Breathe intensity={0.3} speed="slow">
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center mb-3"
          style={{ backgroundColor: `${EARTH.bark}60` }}
        >
          <Clock className="w-6 h-6" style={{ color: EARTH.clay }} />
        </div>
      </Breathe>
      <p className={`${compact ? 'text-xs' : 'text-sm'}`} style={{ color: EARTH.sand }}>
        No traces recorded yet
      </p>
      <p className={`${compact ? 'text-[10px]' : 'text-xs'} mt-1`} style={{ color: EARTH.clay }}>
        Traces will appear after Brain or Gardener operations
      </p>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function RecentTracesPanel({
  limit = 10,
  onViewAll,
  onExploreHeritage,
  compact = false,
  className = '',
}: RecentTracesPanelProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Fetch manifest for overall status
  const {
    data: manifest,
    isLoading: manifestLoading,
    refetch: refetchManifest,
  } = useDifferanceManifest();

  // Fetch recent traces from buffer/store via AGENTESE time.differance.recent
  const {
    data: recentData,
    isLoading: recentLoading,
    refetch: refetchRecent,
  } = useRecentTraces({
    enabled: true,
    limit: limit,
  });

  const isLoading = manifestLoading || recentLoading;

  // Transform backend traces to UI format
  const traces: TracePreview[] = recentData?.traces ? recentData.traces.map(toUITrace) : [];

  const handleRefresh = useCallback(() => {
    refetchManifest();
    refetchRecent();
  }, [refetchManifest, refetchRecent]);

  const handleToggleExpand = useCallback((id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  }, []);

  const headerPadding = compact ? 'px-3 py-2' : 'px-4 py-3';

  return (
    <div
      className={`rounded-xl overflow-hidden ${className}`}
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
        <div className="flex items-center gap-2">
          <Breathe intensity={0.2} speed="slow">
            <GitBranch
              className={compact ? 'w-4 h-4' : 'w-5 h-5'}
              style={{ color: GREEN.sprout }}
            />
          </Breathe>
          <span
            className={`font-medium ${compact ? 'text-xs' : 'text-sm'}`}
            style={{ color: GLOW.lantern }}
          >
            Recent Traces
          </span>
          {manifest && (
            <span
              className="text-[10px] px-1.5 py-0.5 rounded-full"
              style={{ backgroundColor: `${GREEN.sage}30`, color: GREEN.sprout }}
            >
              {manifest.trace_count} total
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Refresh button */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="p-1.5 rounded hover:brightness-110 transition-colors disabled:opacity-50"
            style={{ backgroundColor: `${EARTH.bark}60` }}
            title="Refresh traces"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`}
              style={{ color: EARTH.sand }}
            />
          </button>

          {/* View All link */}
          {onViewAll && (
            <button
              onClick={onViewAll}
              className="flex items-center gap-1 text-xs hover:underline"
              style={{ color: GREEN.sprout }}
            >
              <span>View All</span>
              <ExternalLink className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className={compact ? 'p-2' : 'p-3'}>
        {/* Loading state */}
        {isLoading && traces.length === 0 && (
          <div className="flex items-center justify-center py-6">
            <Breathe intensity={0.5} speed="fast">
              <RefreshCw className="w-5 h-5 animate-spin" style={{ color: EARTH.sand }} />
            </Breathe>
          </div>
        )}

        {/* Empty state */}
        {!isLoading && traces.length === 0 && <EmptyState compact={compact} />}

        {/* Trace list */}
        {traces.length > 0 && (
          <div className="space-y-2">
            {traces.map((trace) => (
              <TraceItem
                key={trace.id}
                trace={trace}
                isExpanded={expandedId === trace.id}
                onClick={() => handleToggleExpand(trace.id)}
                onExploreHeritage={onExploreHeritage}
                compact={compact}
              />
            ))}
          </div>
        )}

        {/* Backend status indicator */}
        {manifest && (
          <div
            className="flex items-center justify-center gap-2 mt-3 pt-2 text-[10px]"
            style={{ borderTop: `1px solid ${EARTH.wood}40`, color: EARTH.clay }}
          >
            <div
              className="w-2 h-2 rounded-full"
              style={{
                backgroundColor: manifest.store_connected ? GREEN.mint : GLOW.copper,
              }}
            />
            <span>{manifest.store_connected ? 'Store connected' : 'Buffer only'}</span>
            {manifest.monoid_available && (
              <>
                <span>•</span>
                <span>Monoid available</span>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default RecentTracesPanel;
