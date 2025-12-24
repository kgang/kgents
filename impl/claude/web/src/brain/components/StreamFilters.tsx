/**
 * StreamFilters — Filter bar with type chips for Brain stream
 *
 * Provides type-based filtering with visual chips:
 * 🔖 Mark | 💎 Crystal | 🛤️ Trail | ✓ Evidence | 📜 Teaching | 🧪 Lemma
 */

import { useCallback } from 'react';

import type { EntityType, StreamFilters as StreamFiltersType } from '../types';
import { ENTITY_BADGES } from '../types';

import './StreamFilters.css';

// =============================================================================
// Types
// =============================================================================

export interface StreamFiltersProps {
  /** Current filter state */
  filters: StreamFiltersType;

  /** Callback when filters change */
  onChange: (filters: StreamFiltersType) => void;

  /** Whether filters are disabled (e.g., during loading) */
  disabled?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const ALL_TYPES: EntityType[] = ['mark', 'crystal', 'trail', 'evidence', 'teaching', 'lemma'];

// =============================================================================
// Component
// =============================================================================

export function StreamFilters({ filters, onChange, disabled = false }: StreamFiltersProps) {
  // Toggle a type in the filter
  const toggleType = useCallback(
    (type: EntityType) => {
      if (disabled) return;

      const currentTypes = filters.types;
      let newTypes: EntityType[];

      if (currentTypes.length === 0) {
        // Currently showing all — filter to just this type
        newTypes = [type];
      } else if (currentTypes.includes(type)) {
        // Remove this type
        newTypes = currentTypes.filter((t) => t !== type);
        // If no types left, show all
        if (newTypes.length === 0) {
          newTypes = [];
        }
      } else {
        // Add this type
        newTypes = [...currentTypes, type];
        // If all types selected, clear to show all
        if (newTypes.length === ALL_TYPES.length) {
          newTypes = [];
        }
      }

      onChange({ ...filters, types: newTypes });
    },
    [filters, onChange, disabled]
  );

  // Clear all type filters
  const clearTypes = useCallback(() => {
    if (disabled) return;
    onChange({ ...filters, types: [] });
  }, [filters, onChange, disabled]);

  // Check if a type is active
  const isActive = (type: EntityType): boolean => {
    if (filters.types.length === 0) return true; // All active
    return filters.types.includes(type);
  };

  // All types selected = "All" button is active
  const allActive = filters.types.length === 0;

  return (
    <div className="stream-filters" role="group" aria-label="Filter by entity type">
      {/* All button */}
      <button
        type="button"
        className={`stream-filters__chip stream-filters__chip--all ${allActive ? 'stream-filters__chip--active' : ''}`}
        onClick={clearTypes}
        disabled={disabled}
        aria-pressed={allActive}
      >
        All
      </button>

      {/* Type chips */}
      {ALL_TYPES.map((type) => {
        const badge = ENTITY_BADGES[type];
        const active = isActive(type);
        const onlyThisType = filters.types.length === 1 && filters.types[0] === type;

        return (
          <button
            key={type}
            type="button"
            className={`stream-filters__chip ${active ? 'stream-filters__chip--active' : ''} ${onlyThisType ? 'stream-filters__chip--solo' : ''}`}
            onClick={() => toggleType(type)}
            disabled={disabled}
            aria-pressed={active && !allActive}
            data-type={type}
            title={`${active ? 'Hide' : 'Show'} ${badge.label}s`}
          >
            <span className="stream-filters__chip-emoji">{badge.emoji}</span>
            <span className="stream-filters__chip-label">{badge.label}</span>
          </button>
        );
      })}
    </div>
  );
}

// =============================================================================
// Compact variant for mobile
// =============================================================================

export function StreamFiltersCompact({ filters, onChange, disabled = false }: StreamFiltersProps) {
  const toggleType = useCallback(
    (type: EntityType) => {
      if (disabled) return;

      const currentTypes = filters.types;
      let newTypes: EntityType[];

      if (currentTypes.length === 0) {
        newTypes = [type];
      } else if (currentTypes.includes(type)) {
        newTypes = currentTypes.filter((t) => t !== type);
      } else {
        newTypes = [...currentTypes, type];
        if (newTypes.length === ALL_TYPES.length) {
          newTypes = [];
        }
      }

      onChange({ ...filters, types: newTypes });
    },
    [filters, onChange, disabled]
  );

  const isActive = (type: EntityType): boolean => {
    if (filters.types.length === 0) return true;
    return filters.types.includes(type);
  };

  return (
    <div className="stream-filters stream-filters--compact" role="group" aria-label="Filter by type">
      {ALL_TYPES.map((type) => {
        const badge = ENTITY_BADGES[type];
        const active = isActive(type);

        return (
          <button
            key={type}
            type="button"
            className={`stream-filters__chip stream-filters__chip--icon-only ${active ? 'stream-filters__chip--active' : ''}`}
            onClick={() => toggleType(type)}
            disabled={disabled}
            aria-pressed={active}
            data-type={type}
            title={badge.label}
          >
            {badge.emoji}
          </button>
        );
      })}
    </div>
  );
}

// =============================================================================
// Export
// =============================================================================

export default StreamFilters;
