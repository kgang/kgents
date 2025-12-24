/**
 * TokenFilters - Search and filter controls
 *
 * Shows:
 * - Search input with / shortcut
 * - Type chips (Spec, Principle, Impl)
 * - Status chips (Active, Orphan, etc.)
 * - Tier chips (T0-T4)
 * - Evidence toggle
 * - Result count
 *
 * "The frame is humble. The content glows."
 */

import { useCallback, useRef, useEffect, memo } from 'react';
import {
  type TokenType,
  type TokenStatus,
  type FilterState,
  TIER_LABELS,
  TIER_COLORS,
  TYPE_LABELS,
} from './types';

import './TokenFilters.css';

// =============================================================================
// Types
// =============================================================================

interface TokenFiltersProps {
  filters: FilterState;
  totalCount: number;
  filteredCount: number;
  onSearchChange: (query: string) => void;
  onToggleType: (type: TokenType) => void;
  onToggleStatus: (status: TokenStatus) => void;
  onToggleTier: (tier: number) => void;
  onToggleEvidence: () => void;
  onClear: () => void;
  searchFocused?: boolean;
  onSearchFocus?: () => void;
  onSearchBlur?: () => void;
}

// =============================================================================
// Filter Chip
// =============================================================================

interface FilterChipProps {
  label: string;
  active: boolean;
  onClick: () => void;
  color?: string;
  count?: number;
}

const FilterChip = memo(function FilterChip({
  label,
  active,
  onClick,
  color,
  count,
}: FilterChipProps) {
  return (
    <button
      className="token-filter-chip"
      data-active={active}
      onClick={onClick}
      style={color ? ({ '--chip-color': color } as React.CSSProperties) : undefined}
    >
      {label}
      {count !== undefined && count > 0 && (
        <span className="token-filter-chip__count">{count}</span>
      )}
    </button>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const TokenFilters = memo(function TokenFilters({
  filters,
  totalCount,
  filteredCount,
  onSearchChange,
  onToggleType,
  onToggleStatus,
  onToggleTier,
  onToggleEvidence,
  onClear,
  searchFocused,
  onSearchFocus,
  onSearchBlur,
}: TokenFiltersProps) {
  const searchRef = useRef<HTMLInputElement>(null);

  // Focus search on / key
  useEffect(() => {
    if (searchFocused && searchRef.current) {
      searchRef.current.focus();
      searchRef.current.select();
    }
  }, [searchFocused]);

  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onSearchChange(e.target.value);
    },
    [onSearchChange]
  );

  const handleSearchKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        onSearchChange('');
        onSearchBlur?.();
        searchRef.current?.blur();
      }
    },
    [onSearchChange, onSearchBlur]
  );

  const hasActiveFilters =
    filters.search ||
    filters.types.length > 0 ||
    filters.statuses.length > 0 ||
    filters.tiers.length > 0 ||
    filters.hasEvidence !== null;

  const types: TokenType[] = ['spec', 'principle', 'impl'];
  const statuses: TokenStatus[] = ['ACTIVE', 'ORPHAN', 'DEPRECATED'];
  const tiers = [0, 1, 2, 3, 4];

  return (
    <div className="token-filters">
      {/* Search */}
      <div className="token-filters__search">
        <input
          ref={searchRef}
          type="text"
          className="token-filters__search-input"
          placeholder="/ Search..."
          value={filters.search}
          onChange={handleSearchChange}
          onKeyDown={handleSearchKeyDown}
          onFocus={onSearchFocus}
          onBlur={onSearchBlur}
        />
        {filters.search && (
          <button
            className="token-filters__search-clear"
            onClick={() => onSearchChange('')}
            aria-label="Clear search"
          >
            ×
          </button>
        )}
      </div>

      {/* Type Filters */}
      <div className="token-filters__group">
        {types.map((type) => (
          <FilterChip
            key={type}
            label={TYPE_LABELS[type]}
            active={filters.types.includes(type)}
            onClick={() => onToggleType(type)}
          />
        ))}
      </div>

      {/* Status Filters */}
      <div className="token-filters__group">
        {statuses.map((status) => (
          <FilterChip
            key={status}
            label={status.charAt(0) + status.slice(1).toLowerCase()}
            active={filters.statuses.includes(status)}
            onClick={() => onToggleStatus(status)}
          />
        ))}
      </div>

      {/* Tier Filters */}
      <div className="token-filters__group token-filters__group--tiers">
        {tiers.map((tier) => (
          <FilterChip
            key={tier}
            label={`T${tier}`}
            active={filters.tiers.includes(tier)}
            onClick={() => onToggleTier(tier)}
            color={TIER_COLORS[tier]}
          />
        ))}
      </div>

      {/* Evidence Toggle */}
      <div className="token-filters__group">
        <FilterChip
          label={
            filters.hasEvidence === null
              ? 'Evidence'
              : filters.hasEvidence
                ? 'Has Evidence'
                : 'No Evidence'
          }
          active={filters.hasEvidence !== null}
          onClick={onToggleEvidence}
        />
      </div>

      {/* Result Count + Clear */}
      <div className="token-filters__meta">
        <span className="token-filters__count">
          {filteredCount === totalCount ? (
            <>{totalCount} tokens</>
          ) : (
            <>
              {filteredCount} of {totalCount}
            </>
          )}
        </span>
        {hasActiveFilters && (
          <button className="token-filters__clear" onClick={onClear}>
            Clear
          </button>
        )}
      </div>

      {/* Tier Legend (collapsed on mobile) */}
      <div className="token-filters__legend">
        {tiers.map((tier) => (
          <span
            key={tier}
            className="token-filters__legend-item"
            style={{ '--legend-color': TIER_COLORS[tier] } as React.CSSProperties}
          >
            T{tier}: {TIER_LABELS[tier]}
          </span>
        ))}
      </div>
    </div>
  );
});
