/**
 * ChartControls — Search, filters, and controls panel
 *
 * Provides vim-style search (/) and filtering by tier/status.
 * STARK BIOME themed.
 *
 * "The file is a lie. There is only the graph."
 */

import { useRef, useEffect, useCallback } from 'react';
import { TIER_COLORS, getTierLabel, hexToString } from './StarRenderer';

import './ChartControls.css';

// =============================================================================
// Types
// =============================================================================

interface ChartControlsProps {
  /** Current search query */
  searchQuery: string;
  /** Search results count */
  resultCount: number;
  /** Current focused result index */
  focusedIndex: number;
  /** Whether search is focused */
  searchFocused: boolean;
  /** Current zoom level */
  zoomLevel: number;
  /** Status filter */
  statusFilter: string;
  /** Tier filter (bitmask or null for all) */
  tierFilter: number[] | null;
  /** Whether simulation is running */
  isSimulating: boolean;
  /** Callbacks */
  onSearchChange: (query: string) => void;
  onSearchFocus: (focused: boolean) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onZoomReset: () => void;
  onStatusFilterChange: (status: string) => void;
  onTierFilterChange: (tiers: number[] | null) => void;
  onReheat: () => void;
}

// =============================================================================
// Component
// =============================================================================

export function ChartControls({
  searchQuery,
  resultCount,
  focusedIndex,
  searchFocused,
  zoomLevel,
  statusFilter,
  tierFilter,
  isSimulating,
  onSearchChange,
  onSearchFocus,
  onZoomIn,
  onZoomOut,
  onZoomReset,
  onStatusFilterChange,
  onTierFilterChange,
  onReheat,
}: ChartControlsProps) {
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Focus search input when searchFocused becomes true
  useEffect(() => {
    if (searchFocused && searchInputRef.current) {
      searchInputRef.current.focus();
      searchInputRef.current.select();
    }
  }, [searchFocused]);

  // Handle search input change
  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onSearchChange(e.target.value);
    },
    [onSearchChange]
  );

  // Handle search input focus/blur
  const handleSearchFocus = useCallback(() => {
    onSearchFocus(true);
  }, [onSearchFocus]);

  const handleSearchBlur = useCallback(() => {
    onSearchFocus(false);
  }, [onSearchFocus]);

  // Handle search input key events
  const handleSearchKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        onSearchFocus(false);
        onSearchChange('');
        searchInputRef.current?.blur();
      }
    },
    [onSearchChange, onSearchFocus]
  );

  // Toggle tier in filter
  const toggleTier = useCallback(
    (tier: number) => {
      if (tierFilter === null) {
        // Currently showing all, switch to only this tier
        onTierFilterChange([tier]);
      } else if (tierFilter.includes(tier)) {
        // Remove this tier
        const newFilter = tierFilter.filter((t) => t !== tier);
        onTierFilterChange(newFilter.length === 0 ? null : newFilter);
      } else {
        // Add this tier
        onTierFilterChange([...tierFilter, tier]);
      }
    },
    [tierFilter, onTierFilterChange]
  );

  // Check if tier is active
  const isTierActive = (tier: number) => {
    return tierFilter === null || tierFilter.includes(tier);
  };

  return (
    <div className="chart-controls">
      {/* Search */}
      <div className="chart-controls__search">
        <div className="chart-controls__search-input-wrapper">
          <span className="chart-controls__search-icon">/</span>
          <input
            ref={searchInputRef}
            type="text"
            className="chart-controls__search-input"
            placeholder="Search specs..."
            value={searchQuery}
            onChange={handleSearchChange}
            onFocus={handleSearchFocus}
            onBlur={handleSearchBlur}
            onKeyDown={handleSearchKeyDown}
          />
          {searchQuery && (
            <span className="chart-controls__search-count">
              {resultCount > 0 ? `${focusedIndex + 1}/${resultCount}` : '0'}
            </span>
          )}
        </div>
        <div className="chart-controls__search-hint">
          <kbd>j</kbd>/<kbd>k</kbd> navigate &middot; <kbd>Enter</kbd> select &middot;{' '}
          <kbd>Esc</kbd> clear
        </div>
      </div>

      {/* Status Filter */}
      <div className="chart-controls__filter">
        <label className="chart-controls__filter-label">Status</label>
        <select
          className="chart-controls__select"
          value={statusFilter}
          onChange={(e) => onStatusFilterChange(e.target.value)}
        >
          <option value="">All</option>
          <option value="ACTIVE">Active</option>
          <option value="ORPHAN">Orphan</option>
          <option value="DEPRECATED">Deprecated</option>
        </select>
      </div>

      {/* Tier Filter */}
      <div className="chart-controls__tiers">
        <label className="chart-controls__filter-label">Tiers</label>
        <div className="chart-controls__tier-buttons">
          {[0, 1, 2, 3, 4].map((tier) => (
            <button
              key={tier}
              className={`chart-controls__tier-btn ${isTierActive(tier) ? 'chart-controls__tier-btn--active' : ''}`}
              onClick={() => toggleTier(tier)}
              title={getTierLabel(tier)}
              style={
                {
                  '--tier-color': hexToString(TIER_COLORS[tier]),
                } as React.CSSProperties
              }
            >
              {tier}
            </button>
          ))}
          <button
            className="chart-controls__tier-btn chart-controls__tier-btn--all"
            onClick={() => onTierFilterChange(null)}
            title="Show all tiers"
          >
            All
          </button>
        </div>
      </div>

      {/* Zoom Controls */}
      <div className="chart-controls__zoom">
        <button className="chart-controls__zoom-btn" onClick={onZoomIn} title="Zoom In (+)">
          +
        </button>
        <span className="chart-controls__zoom-level">{Math.round(zoomLevel * 100)}%</span>
        <button className="chart-controls__zoom-btn" onClick={onZoomOut} title="Zoom Out (-)">
          -
        </button>
        <button className="chart-controls__zoom-btn" onClick={onZoomReset} title="Reset View (0)">
          0
        </button>
      </div>

      {/* Simulation */}
      <div className="chart-controls__simulation">
        {isSimulating ? (
          <span className="chart-controls__simulating">Simulating...</span>
        ) : (
          <button
            className="chart-controls__reheat-btn"
            onClick={onReheat}
            title="Reheat simulation"
          >
            &#x21bb; Reheat
          </button>
        )}
      </div>
    </div>
  );
}

export default ChartControls;
