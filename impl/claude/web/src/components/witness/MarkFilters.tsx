/**
 * MarkFilters: Filter controls for the Witness timeline.
 *
 * Provides filtering by:
 * - Author (kent/claude/system/all)
 * - Principles (any match)
 * - Date range (quick presets + custom)
 * - Text search (grep)
 *
 * "Filter the garden, but don't prune too aggressively."
 *
 * @see plans/witness-fusion-ux-implementation.md
 */

import { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

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
// Available Principles
// =============================================================================

const PRINCIPLES = [
  'tasteful',
  'curated',
  'ethical',
  'joy-inducing',
  'composable',
  'heterarchical',
  'generative',
] as const;

// =============================================================================
// Date Presets
// =============================================================================

type DatePreset = 'today' | 'yesterday' | 'week' | 'month' | 'all';

const DATE_PRESETS: Array<{ value: DatePreset; label: string }> = [
  { value: 'all', label: 'All time' },
  { value: 'today', label: 'Today' },
  { value: 'yesterday', label: 'Yesterday' },
  { value: 'week', label: 'This week' },
  { value: 'month', label: 'This month' },
];

// =============================================================================
// Types
// =============================================================================

export type AuthorFilter = 'all' | 'kent' | 'claude' | 'system';

export interface MarkFilterState {
  /** Author filter */
  author: AuthorFilter;

  /** Principle filters (any match) */
  principles: string[];

  /** Date range (null = all time) */
  dateRange: {
    start: Date;
    end: Date;
  } | null;

  /** Text search (grep) */
  grep: string;
}

export interface MarkFiltersProps {
  /** Current filter state */
  filters: MarkFilterState;

  /** Called when filters change */
  onChange: (filters: MarkFilterState) => void;

  /** Whether to show expanded filters by default */
  defaultExpanded?: boolean;

  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Helper Functions
// =============================================================================

function getDateRangeFromPreset(preset: DatePreset): { start: Date; end: Date } | null {
  const now = new Date();
  const endOfDay = new Date(now);
  endOfDay.setHours(23, 59, 59, 999);

  switch (preset) {
    case 'today': {
      const start = new Date(now);
      start.setHours(0, 0, 0, 0);
      return { start, end: endOfDay };
    }
    case 'yesterday': {
      const start = new Date(now);
      start.setDate(start.getDate() - 1);
      start.setHours(0, 0, 0, 0);
      const end = new Date(start);
      end.setHours(23, 59, 59, 999);
      return { start, end };
    }
    case 'week': {
      const start = new Date(now);
      start.setDate(start.getDate() - 7);
      start.setHours(0, 0, 0, 0);
      return { start, end: endOfDay };
    }
    case 'month': {
      const start = new Date(now);
      start.setMonth(start.getMonth() - 1);
      start.setHours(0, 0, 0, 0);
      return { start, end: endOfDay };
    }
    case 'all':
    default:
      return null;
  }
}

function getPresetFromDateRange(dateRange: { start: Date; end: Date } | null): DatePreset {
  if (!dateRange) return 'all';

  const now = new Date();
  const today = new Date(now);
  today.setHours(0, 0, 0, 0);

  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  yesterday.setHours(0, 0, 0, 0);

  const weekAgo = new Date(now);
  weekAgo.setDate(weekAgo.getDate() - 7);
  weekAgo.setHours(0, 0, 0, 0);

  const monthAgo = new Date(now);
  monthAgo.setMonth(monthAgo.getMonth() - 1);
  monthAgo.setHours(0, 0, 0, 0);

  const startDate = new Date(dateRange.start);
  startDate.setHours(0, 0, 0, 0);

  if (startDate.getTime() === today.getTime()) return 'today';
  if (startDate.getTime() === yesterday.getTime()) return 'yesterday';
  if (Math.abs(startDate.getTime() - weekAgo.getTime()) < 86400000) return 'week';
  if (Math.abs(startDate.getTime() - monthAgo.getTime()) < 86400000) return 'month';

  return 'all';
}

// =============================================================================
// Sub-components
// =============================================================================

interface FilterChipProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
  variant?: 'author' | 'principle' | 'date';
}

function FilterChip({ label, isActive, onClick, variant = 'principle' }: FilterChipProps) {
  const getActiveColor = () => {
    switch (variant) {
      case 'author':
        return LIVING_EARTH.copper;
      case 'date':
        return LIVING_EARTH.sage;
      case 'principle':
      default:
        return LIVING_EARTH.honey;
    }
  };

  const activeColor = getActiveColor();

  return (
    <motion.button
      type="button"
      onClick={onClick}
      className="px-2.5 py-1 text-xs rounded-full transition-all whitespace-nowrap"
      style={{
        backgroundColor: isActive ? activeColor : `${activeColor}20`,
        color: isActive ? LIVING_EARTH.soil : activeColor,
        border: `1px solid ${activeColor}40`,
      }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      data-testid={`filter-chip-${label.toLowerCase().replace(/\s+/g, '-')}`}
    >
      {label}
    </motion.button>
  );
}

interface FilterSectionProps {
  title: string;
  children: React.ReactNode;
}

function FilterSection({ title, children }: FilterSectionProps) {
  return (
    <div className="space-y-1.5">
      <span
        className="text-xs font-medium uppercase tracking-wide"
        style={{ color: LIVING_EARTH.wood }}
      >
        {title}
      </span>
      <div className="flex flex-wrap gap-1.5">{children}</div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function MarkFilters({
  filters,
  onChange,
  defaultExpanded = false,
  className = '',
}: MarkFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  // Count active filters
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.author !== 'all') count++;
    if (filters.principles.length > 0) count += filters.principles.length;
    if (filters.dateRange !== null) count++;
    if (filters.grep.trim()) count++;
    return count;
  }, [filters]);

  // Handlers
  const handleAuthorChange = useCallback(
    (author: AuthorFilter) => {
      onChange({ ...filters, author });
    },
    [filters, onChange]
  );

  const handlePrincipleToggle = useCallback(
    (principle: string) => {
      const principles = filters.principles.includes(principle)
        ? filters.principles.filter((p) => p !== principle)
        : [...filters.principles, principle];
      onChange({ ...filters, principles });
    },
    [filters, onChange]
  );

  const handleDatePresetChange = useCallback(
    (preset: DatePreset) => {
      const dateRange = getDateRangeFromPreset(preset);
      onChange({ ...filters, dateRange });
    },
    [filters, onChange]
  );

  const handleGrepChange = useCallback(
    (grep: string) => {
      onChange({ ...filters, grep });
    },
    [filters, onChange]
  );

  const handleClear = useCallback(() => {
    onChange({
      author: 'all',
      principles: [],
      dateRange: null,
      grep: '',
    });
  }, [onChange]);

  const currentDatePreset = getPresetFromDateRange(filters.dateRange);

  return (
    <div
      className={`rounded-lg ${className}`}
      style={{ backgroundColor: LIVING_EARTH.soilLight }}
      data-testid="mark-filters"
    >
      {/* Collapsed: Single row with expand button */}
      <div className="flex items-center gap-3 px-4 py-2">
        {/* Search Input */}
        <div className="flex-1 relative">
          <input
            type="text"
            value={filters.grep}
            onChange={(e) => handleGrepChange(e.target.value)}
            placeholder="Search marks..."
            className="w-full pl-8 pr-3 py-1.5 text-sm rounded border-0 outline-none"
            style={{
              backgroundColor: LIVING_EARTH.soil,
              color: LIVING_EARTH.lantern,
            }}
            data-testid="grep-input"
          />
          <span
            className="absolute left-2.5 top-1/2 -translate-y-1/2 text-sm"
            style={{ color: LIVING_EARTH.wood }}
          >
            🔍
          </span>
        </div>

        {/* Quick author filter */}
        <div className="flex gap-1">
          {(['all', 'kent', 'claude', 'system'] as const).map((author) => (
            <FilterChip
              key={author}
              label={author === 'all' ? 'All' : author.charAt(0).toUpperCase() + author.slice(1)}
              isActive={filters.author === author}
              onClick={() => handleAuthorChange(author)}
              variant="author"
            />
          ))}
        </div>

        {/* Expand toggle */}
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1.5 px-2 py-1 text-xs rounded transition-colors"
          style={{
            color: LIVING_EARTH.copper,
            backgroundColor: isExpanded ? `${LIVING_EARTH.copper}20` : 'transparent',
          }}
          data-testid="expand-filters"
        >
          <span>
            {isExpanded ? '▾' : '▸'} Filters
            {activeFilterCount > 0 && (
              <span
                className="ml-1 px-1.5 rounded-full text-xs"
                style={{
                  backgroundColor: LIVING_EARTH.copper,
                  color: LIVING_EARTH.soil,
                }}
              >
                {activeFilterCount}
              </span>
            )}
          </span>
        </button>

        {/* Clear button */}
        {activeFilterCount > 0 && (
          <button
            type="button"
            onClick={handleClear}
            className="text-xs px-2 py-1 rounded hover:underline"
            style={{ color: LIVING_EARTH.woodLight }}
            data-testid="clear-filters"
          >
            Clear
          </button>
        )}
      </div>

      {/* Expanded: Full filter sections */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div
              className="px-4 py-3 space-y-4 border-t"
              style={{ borderColor: `${LIVING_EARTH.wood}30` }}
            >
              {/* Principles */}
              <FilterSection title="Principles">
                {PRINCIPLES.map((principle) => (
                  <FilterChip
                    key={principle}
                    label={principle}
                    isActive={filters.principles.includes(principle)}
                    onClick={() => handlePrincipleToggle(principle)}
                    variant="principle"
                  />
                ))}
              </FilterSection>

              {/* Date Range */}
              <FilterSection title="Time Range">
                {DATE_PRESETS.map((preset) => (
                  <FilterChip
                    key={preset.value}
                    label={preset.label}
                    isActive={currentDatePreset === preset.value}
                    onClick={() => handleDatePresetChange(preset.value)}
                    variant="date"
                  />
                ))}
              </FilterSection>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// =============================================================================
// Default Filter State
// =============================================================================

export function createDefaultFilters(): MarkFilterState {
  return {
    author: 'all',
    principles: [],
    dateRange: null,
    grep: '',
  };
}

// =============================================================================
// Exports
// =============================================================================

export { FilterChip, FilterSection };
export default MarkFilters;
