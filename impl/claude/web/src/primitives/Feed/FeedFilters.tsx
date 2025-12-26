/**
 * FeedFilters Component
 *
 * "A feed without filters is the raw cosmos. A feed with filters is a perspective."
 *
 * Filter UI for feeds:
 * - Layer selection
 * - Loss range slider
 * - Author filter
 * - Time range picker
 * - Tag/principle filters
 * - Ranking mode selector
 */

import { memo, useCallback, useState } from 'react';
import type { FeedFiltersProps, FeedFilter, FeedRanking } from './types';
import { LAYER_NAMES } from './types';

// =============================================================================
// Component
// =============================================================================

export const FeedFilters = memo(function FeedFilters({
  filters,
  onFiltersChange,
  ranking,
  onRankingChange,
  className = '',
}: FeedFiltersProps) {
  const [expanded, setExpanded] = useState(false);

  // Toggle filter active state
  const toggleFilter = useCallback(
    (index: number) => {
      const newFilters = [...filters];
      newFilters[index].active = !newFilters[index].active;
      onFiltersChange(newFilters);
    },
    [filters, onFiltersChange]
  );

  // Add layer filter
  const addLayerFilter = useCallback(
    (layer: number) => {
      const newFilter: FeedFilter = {
        type: 'layer',
        value: layer,
        label: `Layer ${layer}: ${LAYER_NAMES[layer]}`,
        active: true,
      };
      onFiltersChange([...filters, newFilter]);
    },
    [filters, onFiltersChange]
  );

  // Add loss range filter
  const addLossRangeFilter = useCallback(
    (min: number, max: number) => {
      const newFilter: FeedFilter = {
        type: 'loss-range',
        value: [min, max],
        label: `Loss ${(min * 100).toFixed(0)}-${(max * 100).toFixed(0)}%`,
        active: true,
      };
      onFiltersChange([...filters, newFilter]);
    },
    [filters, onFiltersChange]
  );

  // Remove filter
  const removeFilter = useCallback(
    (index: number) => {
      const newFilters = filters.filter((_, i) => i !== index);
      onFiltersChange(newFilters);
    },
    [filters, onFiltersChange]
  );

  // Clear all filters
  const clearFilters = useCallback(() => {
    onFiltersChange([]);
  }, [onFiltersChange]);

  return (
    <div className={`feed-filters ${className}`}>
      {/* Header */}
      <div className="feed-filters__header">
        <button
          className="feed-filters__toggle"
          onClick={() => setExpanded(!expanded)}
        >
          <span className="feed-filters__toggle-icon">
            {expanded ? '▼' : '▶'}
          </span>
          <span className="feed-filters__toggle-text">
            Filters {filters.filter((f) => f.active).length > 0 && `(${filters.filter((f) => f.active).length})`}
          </span>
        </button>

        {/* Ranking selector */}
        <div className="feed-filters__ranking">
          <label className="feed-filters__ranking-label">Sort:</label>
          <select
            className="feed-filters__ranking-select"
            value={ranking}
            onChange={(e) => onRankingChange(e.target.value as FeedRanking)}
          >
            <option value="chronological">Newest First</option>
            <option value="loss-ascending">Lowest Loss</option>
            <option value="loss-descending">Highest Loss</option>
            <option value="engagement">Most Engaged</option>
            <option value="algorithmic">Algorithmic</option>
          </select>
        </div>

        {/* Clear all */}
        {filters.length > 0 && (
          <button
            className="feed-filters__clear"
            onClick={clearFilters}
            title="Clear all filters"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Expanded filter controls */}
      {expanded && (
        <div className="feed-filters__expanded">
          {/* Active filters */}
          {filters.length > 0 && (
            <div className="feed-filters__active">
              <div className="feed-filters__active-label">Active Filters:</div>
              <div className="feed-filters__active-list">
                {filters.map((filter, index) => (
                  <div
                    key={index}
                    className={`feed-filters__filter-chip ${
                      filter.active ? 'feed-filters__filter-chip--active' : ''
                    }`}
                  >
                    <button
                      className="feed-filters__filter-chip-toggle"
                      onClick={() => toggleFilter(index)}
                      title={filter.active ? 'Disable filter' : 'Enable filter'}
                    >
                      <span className="feed-filters__filter-chip-checkbox">
                        {filter.active ? '✓' : '○'}
                      </span>
                      <span className="feed-filters__filter-chip-label">
                        {filter.label}
                      </span>
                    </button>
                    <button
                      className="feed-filters__filter-chip-remove"
                      onClick={() => removeFilter(index)}
                      title="Remove filter"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Add filters */}
          <div className="feed-filters__add">
            {/* Layer filters */}
            <div className="feed-filters__add-section">
              <div className="feed-filters__add-label">Add Layer Filter:</div>
              <div className="feed-filters__layer-buttons">
                {Object.entries(LAYER_NAMES).map(([layer, name]) => (
                  <button
                    key={layer}
                    className="feed-filters__layer-button"
                    onClick={() => addLayerFilter(parseInt(layer))}
                    title={`Filter by ${name}`}
                  >
                    L{layer}
                  </button>
                ))}
              </div>
            </div>

            {/* Loss range filters */}
            <div className="feed-filters__add-section">
              <div className="feed-filters__add-label">Add Loss Range Filter:</div>
              <div className="feed-filters__loss-buttons">
                <button
                  className="feed-filters__loss-button feed-filters__loss-button--healthy"
                  onClick={() => addLossRangeFilter(0, 0.2)}
                  title="Healthy (0-20%)"
                >
                  Healthy
                </button>
                <button
                  className="feed-filters__loss-button feed-filters__loss-button--warning"
                  onClick={() => addLossRangeFilter(0.2, 0.5)}
                  title="Warning (20-50%)"
                >
                  Warning
                </button>
                <button
                  className="feed-filters__loss-button feed-filters__loss-button--critical"
                  onClick={() => addLossRangeFilter(0.5, 0.8)}
                  title="Critical (50-80%)"
                >
                  Critical
                </button>
                <button
                  className="feed-filters__loss-button feed-filters__loss-button--emergency"
                  onClick={() => addLossRangeFilter(0.8, 1.0)}
                  title="Emergency (80-100%)"
                >
                  Emergency
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});
