/**
 * WitnessDashboard: The Garden of Marks
 *
 * Full witness experience with:
 * - QuickMarkForm for minimal friction creation
 * - MarkFilters for filtering by author, principle, date, text
 * - MarkTimeline for chronological display with grouping
 * - Real-time updates via SSE (through useWitness hook)
 *
 * "Every action leaves a mark. The mark IS the witness."
 *
 * Layout:
 * ┌─────────────────────────────────────────────────────────────┐
 * │  WITNESS: THE GARDEN OF MARKS                     🌿 Live   │
 * ├─────────────────────────────────────────────────────────────┤
 * │  [QuickMarkForm]                                            │
 * ├─────────────────────────────────────────────────────────────┤
 * │  [MarkFilters]                                              │
 * ├─────────────────────────────────────────────────────────────┤
 * │  [MarkTimeline - grouped by day]                            │
 * └─────────────────────────────────────────────────────────────┘
 *
 * @see plans/witness-fusion-ux-implementation.md
 */

import { useState, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useWitness } from '@/hooks/useWitness';
import { QuickMarkForm } from '@/components/witness/QuickMarkForm';
import { MarkTimeline, type GroupBy } from '@/components/witness/MarkTimeline';
import {
  MarkFilters,
  createDefaultFilters,
  type MarkFilterState,
  type AuthorFilter,
} from '@/components/witness/MarkFilters';
import type { Mark, CreateMarkRequest } from '@/api/witness';

// =============================================================================
// Living Earth Palette
// =============================================================================

const LIVING_EARTH = {
  soil: '#2D1B14',
  soilLight: '#3D2B24',
  wood: '#6B4E3D',
  woodLight: '#8B6E5D',
  copper: '#C08552',
  sage: '#4A6B4A',
  honey: '#E8C4A0',
  lantern: '#F5E6D3',
} as const;

// =============================================================================
// Types
// =============================================================================

export interface WitnessDashboardProps {
  /** Default group-by mode */
  defaultGroupBy?: GroupBy;

  /** Disable real-time updates */
  disableRealtime?: boolean;

  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Apply local filters to marks.
 * (Some filters are applied server-side, others client-side for responsiveness)
 */
function applyLocalFilters(marks: Mark[], filters: MarkFilterState): Mark[] {
  let result = marks;

  // Apply author filter (also done server-side, but keep for responsiveness)
  if (filters.author !== 'all') {
    result = result.filter((m) => m.author === filters.author);
  }

  // Apply principle filter (any match)
  if (filters.principles.length > 0) {
    result = result.filter((m) =>
      filters.principles.some((p) => m.principles.includes(p))
    );
  }

  // Apply date range filter
  if (filters.dateRange) {
    result = result.filter((m) => {
      const markDate = new Date(m.timestamp);
      return markDate >= filters.dateRange!.start && markDate <= filters.dateRange!.end;
    });
  }

  // Apply grep filter (case-insensitive search in action and reasoning)
  if (filters.grep.trim()) {
    const searchTerm = filters.grep.toLowerCase();
    result = result.filter(
      (m) =>
        m.action.toLowerCase().includes(searchTerm) ||
        (m.reasoning && m.reasoning.toLowerCase().includes(searchTerm))
    );
  }

  return result;
}

// =============================================================================
// Sub-components
// =============================================================================

interface ConnectionStatusProps {
  isConnected: boolean;
}

function ConnectionStatus({ isConnected }: ConnectionStatusProps) {
  return (
    <motion.div
      className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs"
      style={{
        backgroundColor: isConnected
          ? `${LIVING_EARTH.sage}30`
          : `${LIVING_EARTH.copper}30`,
        color: isConnected ? LIVING_EARTH.sage : LIVING_EARTH.copper,
      }}
      animate={{
        opacity: isConnected ? 1 : [1, 0.5, 1],
      }}
      transition={{
        duration: isConnected ? 0 : 1.5,
        repeat: isConnected ? 0 : Infinity,
      }}
      data-testid="connection-status"
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{
          backgroundColor: isConnected ? LIVING_EARTH.sage : LIVING_EARTH.copper,
        }}
      />
      {isConnected ? 'Live' : 'Connecting...'}
    </motion.div>
  );
}

interface GroupByToggleProps {
  value: GroupBy;
  onChange: (value: GroupBy) => void;
}

function GroupByToggle({ value, onChange }: GroupByToggleProps) {
  const options: Array<{ value: GroupBy; label: string }> = [
    { value: 'day', label: 'Day' },
    { value: 'session', label: 'Session' },
    { value: 'none', label: 'None' },
  ];

  return (
    <div
      className="flex gap-1 p-0.5 rounded-lg"
      style={{ backgroundColor: LIVING_EARTH.soil }}
      data-testid="group-by-toggle"
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className="px-2 py-1 text-xs rounded transition-all"
          style={{
            backgroundColor:
              value === option.value ? LIVING_EARTH.wood : 'transparent',
            color:
              value === option.value ? LIVING_EARTH.lantern : LIVING_EARTH.woodLight,
          }}
          data-testid={`group-by-${option.value}`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

interface ExportButtonProps {
  marks: Mark[];
  disabled?: boolean;
}

function ExportButton({ marks, disabled = false }: ExportButtonProps) {
  const handleExport = useCallback(() => {
    const json = JSON.stringify(marks, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `witness-marks-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [marks]);

  return (
    <button
      type="button"
      onClick={handleExport}
      disabled={disabled || marks.length === 0}
      className="px-2 py-1 text-xs rounded transition-opacity disabled:opacity-30"
      style={{
        color: LIVING_EARTH.woodLight,
        backgroundColor: `${LIVING_EARTH.wood}20`,
      }}
      data-testid="export-button"
    >
      📤 Export
    </button>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function WitnessDashboard({
  defaultGroupBy = 'day',
  disableRealtime = false,
  className = '',
}: WitnessDashboardProps) {
  // UI State
  const [filters, setFilters] = useState<MarkFilterState>(createDefaultFilters());
  const [groupBy, setGroupBy] = useState<GroupBy>(defaultGroupBy);
  const [selectedMarkId, setSelectedMarkId] = useState<string | null>(null);

  // Convert filter author to hook-compatible type
  const authorFilter = filters.author !== 'all' ? filters.author : undefined;

  // Fetch marks with hook (includes SSE)
  const {
    marks,
    isLoading,
    error,
    createMark,
    retractMark,
    isConnected,
  } = useWitness({
    limit: 100,
    author: authorFilter as 'kent' | 'claude' | 'system' | undefined,
    today: filters.dateRange !== null && isToday(filters.dateRange),
    realtime: !disableRealtime,
  });

  // Apply local filters for instant response
  const filteredMarks = useMemo(
    () => applyLocalFilters(marks, filters),
    [marks, filters]
  );

  // Handlers
  const handleCreateMark = useCallback(
    async (request: CreateMarkRequest) => {
      await createMark(request);
    },
    [createMark]
  );

  const handleRetractMark = useCallback(
    async (markId: string) => {
      // TODO: Open dialog for retraction reason
      await retractMark(markId, 'Retracted by user');
    },
    [retractMark]
  );

  const handleSelectMark = useCallback((mark: Mark) => {
    setSelectedMarkId((prev) => (prev === mark.id ? null : mark.id));
  }, []);

  const handleFilterChange = useCallback((newFilters: MarkFilterState) => {
    setFilters(newFilters);
  }, []);

  return (
    <div
      className={`flex flex-col h-full ${className}`}
      style={{ backgroundColor: LIVING_EARTH.soil }}
      data-testid="witness-dashboard"
    >
      {/* Header */}
      <header
        className="flex items-center justify-between px-4 py-3 border-b"
        style={{ borderColor: `${LIVING_EARTH.wood}30` }}
      >
        <div className="flex items-center gap-3">
          <h1
            className="text-lg font-semibold"
            style={{ color: LIVING_EARTH.lantern }}
          >
            🍂 Witness
          </h1>
          <span
            className="text-xs"
            style={{ color: LIVING_EARTH.woodLight }}
          >
            The Garden of Marks
          </span>
        </div>

        <div className="flex items-center gap-3">
          <ConnectionStatus isConnected={isConnected} />
          <GroupByToggle value={groupBy} onChange={setGroupBy} />
          <ExportButton marks={filteredMarks} />
        </div>
      </header>

      {/* Quick Mark Form */}
      <section className="px-4 py-3">
        <QuickMarkForm
          onSubmit={handleCreateMark}
          placeholder="What happened? Leave a mark..."
        />
      </section>

      {/* Filters */}
      <section className="px-4 pb-3">
        <MarkFilters filters={filters} onChange={handleFilterChange} />
      </section>

      {/* Timeline */}
      <section className="flex-1 overflow-hidden px-4 pb-4">
        <MarkTimeline
          marks={filteredMarks}
          groupBy={groupBy}
          density="comfortable"
          isLoading={isLoading}
          error={error?.message}
          onRetract={handleRetractMark}
          onSelect={handleSelectMark}
          selectedMarkId={selectedMarkId}
          className="h-full rounded-lg"
        />
      </section>

      {/* Stats Footer */}
      <footer
        className="flex items-center justify-between px-4 py-2 text-xs border-t"
        style={{
          borderColor: `${LIVING_EARTH.wood}30`,
          color: LIVING_EARTH.woodLight,
        }}
        data-testid="stats-footer"
      >
        <span>
          {filteredMarks.length} {filteredMarks.length === 1 ? 'mark' : 'marks'}
          {filteredMarks.length !== marks.length && ` (of ${marks.length})`}
        </span>
        <span>
          {isConnected ? '🌿 Real-time enabled' : '⏸ Updates paused'}
        </span>
      </footer>
    </div>
  );
}

// =============================================================================
// Helper Functions
// =============================================================================

function isToday(dateRange: { start: Date; end: Date }): boolean {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const rangeStart = new Date(dateRange.start);
  rangeStart.setHours(0, 0, 0, 0);
  return today.getTime() === rangeStart.getTime();
}

// =============================================================================
// Exports
// =============================================================================

export default WitnessDashboard;
