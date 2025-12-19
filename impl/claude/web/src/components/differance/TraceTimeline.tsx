/**
 * TraceTimeline — The Horizontal Timeline for Differance DevEx
 *
 * Replaces the temporary RecentTracesPanel (which used ghosts as proxy data).
 * This component fetches real trace data via time.differance.recent.
 *
 * Design Principles (from differance-devex-enlightenment.md):
 * - "Temporal Intuition": Time flows left-to-right
 * - "Progressive Disclosure": Badge → Timeline → Inspector → Full Graph
 * - "Ghosts Are Friends": Roads not taken feel inviting, not haunting
 * - "Zero-Config Recording": Traces appear automatically from jewel operations
 *
 * ASCII Reference:
 * ```
 * TIME ─────────────────────────────────────────────────▶
 *
 *   ● capture("auth patterns")
 *   │
 *   ├──● surface(similarity=0.8)
 *   │  │
 *   │  ├──○ [GHOST] surface(similarity=0.95) — "too strict"
 *   │  │
 *   │  └──● crystallize()
 *   │     │
 *   │     └──○ [GHOST] defer() — "needs more context"
 *   │
 *   └──● commit()
 * ```
 *
 * @see spec/protocols/differance.md
 * @see plans/differance-devex-enlightenment.md - Phase 7A
 */

import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  GitBranch,
  Clock,
  ChevronRight,
  RefreshCw,
  ExternalLink,
  Filter,
  Layers,
} from 'lucide-react';
import { EARTH, GREEN, GLOW, getJewelIdentityColor } from '@/constants/livingEarth';
import { useRecentTraces, type TracePreview } from '@/hooks/useDifferanceQuery';
import { Breathe } from '@/components/joy';
import { WhyPanel } from './WhyPanel';

// =============================================================================
// Types
// =============================================================================

export interface TraceTimelineProps {
  /** Max traces to fetch */
  limit?: number;
  /** Filter by jewel name */
  jewelFilter?: string;
  /** Callback when "View All" is clicked */
  onViewAll?: () => void;
  /** Callback when a trace is selected for heritage exploration */
  onExploreHeritage?: (traceId: string) => void;
  /** Callback when a trace is selected for inspection */
  onInspect?: (trace: TracePreview) => void;
  /** View mode: list (vertical) or timeline (horizontal) */
  viewMode?: 'list' | 'timeline';
  /** Compact mode for smaller spaces */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// Jewel color mapping for visual consistency
const JEWEL_COLORS: Record<string, string> = {
  brain: GREEN.fern,
  gardener: GREEN.sage,
  forge: GLOW.copper,
  town: EARTH.wood,
  park: GREEN.sage,
  coalition: GLOW.amber,
  gestalt: GREEN.mint,
};

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

function getJewelColor(jewel: string | null | undefined): string {
  if (!jewel) return EARTH.clay;
  return JEWEL_COLORS[jewel.toLowerCase()] ?? getJewelIdentityColor(jewel);
}

// =============================================================================
// Sub-Components
// =============================================================================

interface TraceNodeProps {
  trace: TracePreview;
  isSelected: boolean;
  onClick: () => void;
  compact?: boolean;
  showConnector?: boolean;
}

function TraceNode({ trace, isSelected, onClick, compact, showConnector = true }: TraceNodeProps) {
  const jewelColor = getJewelColor(trace.jewel);
  const hasGhosts = trace.ghost_count > 0;

  return (
    <div className="relative">
      {/* Connector line */}
      {showConnector && (
        <div
          className="absolute left-3 top-0 w-0.5 h-full -z-10"
          style={{ backgroundColor: `${GREEN.sage}40` }}
        />
      )}

      {/* Trace node */}
      <motion.button
        onClick={onClick}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={`
          w-full flex items-start gap-3 px-3 py-2.5 rounded-lg
          text-left transition-all duration-200
          ${isSelected ? 'ring-2 ring-amber-400' : ''}
        `}
        style={{
          backgroundColor: isSelected ? `${GREEN.sage}20` : `${EARTH.bark}60`,
          borderColor: isSelected ? GLOW.amber : 'transparent',
          borderWidth: '1px',
          borderStyle: 'solid',
        }}
      >
        {/* Node indicator */}
        <div className="relative flex-shrink-0 mt-0.5">
          <div
            className="w-6 h-6 rounded-full flex items-center justify-center"
            style={{
              backgroundColor: `${jewelColor}30`,
              border: `2px solid ${jewelColor}`,
            }}
          >
            {hasGhosts ? (
              <GitBranch className="w-3 h-3" style={{ color: jewelColor }} />
            ) : (
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: jewelColor }} />
            )}
          </div>
          {/* Ghost indicator */}
          {hasGhosts && (
            <div
              className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full flex items-center justify-center text-[8px] font-bold"
              style={{ backgroundColor: EARTH.bark, color: GLOW.honey }}
            >
              {trace.ghost_count}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className={`font-medium truncate ${compact ? 'text-xs' : 'text-sm'}`}
              style={{ color: GLOW.lantern }}
            >
              {trace.operation}
            </span>
            {trace.jewel && (
              <span
                className="text-[10px] px-1.5 py-0.5 rounded uppercase tracking-wide"
                style={{ backgroundColor: `${jewelColor}20`, color: jewelColor }}
              >
                {trace.jewel}
              </span>
            )}
          </div>
          <div
            className={`truncate ${compact ? 'text-[10px]' : 'text-xs'}`}
            style={{ color: EARTH.sand }}
          >
            {trace.context || trace.output_preview || 'No context recorded'}
          </div>
        </div>

        {/* Timestamp & action */}
        <div className="flex-shrink-0 flex items-center gap-2">
          <span className="text-[10px]" style={{ color: EARTH.clay }}>
            {formatRelativeTime(trace.timestamp)}
          </span>
          <ChevronRight
            className={`w-4 h-4 transition-transform ${isSelected ? 'rotate-90' : ''}`}
            style={{ color: EARTH.sand }}
          />
        </div>
      </motion.button>
    </div>
  );
}

interface TimelineHeaderProps {
  traceCount: number;
  totalTraces: number;
  jewelFilter: string | null;
  onJewelFilterChange: (jewel: string | null) => void;
  viewMode: 'list' | 'timeline';
  onViewModeChange: (mode: 'list' | 'timeline') => void;
  isLoading: boolean;
  onRefresh: () => void;
  onViewAll?: () => void;
  compact?: boolean;
}

function TimelineHeader({
  traceCount,
  totalTraces,
  jewelFilter,
  onJewelFilterChange,
  viewMode,
  onViewModeChange,
  isLoading,
  onRefresh,
  onViewAll,
  compact,
}: TimelineHeaderProps) {
  const [showFilters, setShowFilters] = useState(false);

  const jewels = ['brain', 'gardener', 'forge', 'town', 'park', 'coalition', 'gestalt'];

  return (
    <div
      className={`flex flex-col gap-2 ${compact ? 'px-3 py-2' : 'px-4 py-3'}`}
      style={{ backgroundColor: `${EARTH.bark}80` }}
    >
      {/* Top row */}
      <div className="flex items-center justify-between">
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
            Trace Timeline
          </span>
          <span
            className="text-[10px] px-1.5 py-0.5 rounded-full"
            style={{ backgroundColor: `${GREEN.sage}30`, color: GREEN.sprout }}
          >
            {traceCount}/{totalTraces}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* View mode toggle */}
          <button
            onClick={() => onViewModeChange(viewMode === 'list' ? 'timeline' : 'list')}
            className="p-1.5 rounded hover:brightness-110 transition-colors"
            style={{ backgroundColor: `${EARTH.bark}60` }}
            title={viewMode === 'list' ? 'Switch to timeline view' : 'Switch to list view'}
          >
            <Layers className="w-3.5 h-3.5" style={{ color: EARTH.sand }} />
          </button>

          {/* Filter toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="p-1.5 rounded hover:brightness-110 transition-colors"
            style={{
              backgroundColor: jewelFilter ? `${GREEN.sage}30` : `${EARTH.bark}60`,
            }}
            title="Filter by jewel"
          >
            <Filter
              className="w-3.5 h-3.5"
              style={{ color: jewelFilter ? GREEN.sprout : EARTH.sand }}
            />
          </button>

          {/* Refresh */}
          <button
            onClick={onRefresh}
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

          {/* View All */}
          {onViewAll && (
            <button
              onClick={onViewAll}
              className="flex items-center gap-1 text-xs hover:underline"
              style={{ color: GREEN.sprout }}
            >
              <span>All</span>
              <ExternalLink className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Filter row */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="flex flex-wrap gap-1.5 overflow-hidden"
          >
            <button
              onClick={() => onJewelFilterChange(null)}
              className="text-[10px] px-2 py-1 rounded-full transition-colors"
              style={{
                backgroundColor: !jewelFilter ? `${GREEN.sage}40` : `${EARTH.bark}60`,
                color: !jewelFilter ? GREEN.sprout : EARTH.sand,
              }}
            >
              All
            </button>
            {jewels.map((jewel) => (
              <button
                key={jewel}
                onClick={() => onJewelFilterChange(jewel === jewelFilter ? null : jewel)}
                className="text-[10px] px-2 py-1 rounded-full transition-colors capitalize"
                style={{
                  backgroundColor:
                    jewel === jewelFilter ? `${getJewelColor(jewel)}40` : `${EARTH.bark}60`,
                  color: jewel === jewelFilter ? getJewelColor(jewel) : EARTH.sand,
                }}
              >
                {jewel}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function EmptyState({ compact, jewelFilter }: { compact?: boolean; jewelFilter?: string | null }) {
  return (
    <div
      className={`flex flex-col items-center justify-center ${compact ? 'py-6' : 'py-10'} text-center`}
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
        {jewelFilter ? `No ${jewelFilter} traces yet` : 'No traces recorded yet'}
      </p>
      <p
        className={`${compact ? 'text-[10px]' : 'text-xs'} mt-1 max-w-xs`}
        style={{ color: EARTH.clay }}
      >
        Traces appear automatically from Crown Jewel operations
      </p>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function TraceTimeline({
  limit = 15,
  jewelFilter: initialJewelFilter,
  onViewAll,
  onExploreHeritage,
  onInspect,
  viewMode: initialViewMode = 'list',
  compact = false,
  className = '',
}: TraceTimelineProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showWhyPanel, setShowWhyPanel] = useState(false);
  const [jewelFilter, setJewelFilter] = useState<string | null>(initialJewelFilter ?? null);
  const [viewMode, setViewMode] = useState<'list' | 'timeline'>(initialViewMode);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch real trace data via AGENTESE
  const { data, isLoading, refetch } = useRecentTraces({
    limit,
    jewelFilter: jewelFilter ?? undefined,
  });

  const traces = data?.traces ?? [];
  const totalTraces = data?.total ?? 0;

  const handleSelectTrace = useCallback(
    (trace: TracePreview) => {
      if (selectedId === trace.id) {
        setShowWhyPanel(!showWhyPanel);
      } else {
        setSelectedId(trace.id);
        setShowWhyPanel(true);
        onInspect?.(trace);
      }
    },
    [selectedId, showWhyPanel, onInspect]
  );

  const handleRefresh = useCallback(() => {
    refetch();
  }, [refetch]);

  // selectedTrace could be used for additional context in future
  // const selectedTrace = useMemo(
  //   () => traces.find((t) => t.id === selectedId),
  //   [traces, selectedId]
  // );

  return (
    <div
      className={`rounded-xl overflow-hidden flex flex-col ${className}`}
      style={{
        backgroundColor: EARTH.soil,
        border: `1px solid ${EARTH.wood}`,
      }}
    >
      {/* Header */}
      <TimelineHeader
        traceCount={traces.length}
        totalTraces={totalTraces}
        jewelFilter={jewelFilter}
        onJewelFilterChange={setJewelFilter}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        isLoading={isLoading}
        onRefresh={handleRefresh}
        onViewAll={onViewAll}
        compact={compact}
      />

      {/* Content */}
      <div
        ref={scrollRef}
        className={`flex-1 overflow-auto ${compact ? 'p-2' : 'p-3'}`}
        style={{ maxHeight: compact ? '300px' : '400px' }}
      >
        {/* Loading state */}
        {isLoading && traces.length === 0 && (
          <div className="flex items-center justify-center py-8">
            <Breathe intensity={0.5} speed="fast">
              <RefreshCw className="w-5 h-5 animate-spin" style={{ color: EARTH.sand }} />
            </Breathe>
          </div>
        )}

        {/* Empty state */}
        {!isLoading && traces.length === 0 && (
          <EmptyState compact={compact} jewelFilter={jewelFilter} />
        )}

        {/* Trace list */}
        {traces.length > 0 && (
          <div className="space-y-1">
            {traces.map((trace, index) => (
              <div key={trace.id}>
                <TraceNode
                  trace={trace}
                  isSelected={selectedId === trace.id}
                  onClick={() => handleSelectTrace(trace)}
                  compact={compact}
                  showConnector={index < traces.length - 1}
                />

                {/* Why panel (expanded inline) */}
                <AnimatePresence>
                  {selectedId === trace.id && showWhyPanel && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden ml-9 mt-1"
                    >
                      <WhyPanel
                        outputId={trace.id}
                        defaultExpanded={true}
                        onExploreHeritage={onExploreHeritage}
                        compact={compact}
                      />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Status footer */}
      {data && (
        <div
          className="flex items-center justify-center gap-2 px-3 py-2 text-[10px]"
          style={{ borderTop: `1px solid ${EARTH.wood}40`, color: EARTH.clay }}
        >
          <div
            className="w-2 h-2 rounded-full"
            style={{
              backgroundColor: data.store_connected ? GREEN.mint : GLOW.copper,
            }}
          />
          <span>{data.store_connected ? 'Store connected' : 'Buffer only'}</span>
          <span>|</span>
          <span>{data.buffer_size} in buffer</span>
        </div>
      )}
    </div>
  );
}

export default TraceTimeline;
