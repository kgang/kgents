/**
 * SelectionChips - Filter chip display for TerrariumView predicates.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Displays active selection predicates as removable chips.
 */

import React from 'react';
import { X, XCircle } from 'lucide-react';
import type { SelectionPredicate } from '../../api/types/_generated/world-scenery';

// =============================================================================
// Types
// =============================================================================

export interface SelectionChipsProps {
  /** Active predicates */
  predicates: SelectionPredicate[];
  /** Callback when a predicate is removed */
  onRemove: (field: string) => void;
  /** Callback to clear all predicates */
  onClear?: () => void;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Format a predicate for display.
 */
function formatPredicate(predicate: SelectionPredicate): string {
  const opMap: Record<string, string> = {
    EQ: '=',
    NE: '≠',
    IN: '∈',
    NOT_IN: '∉',
    CONTAINS: '⊃',
    STARTS_WITH: '^',
    GT: '>',
    LT: '<',
    GTE: '≥',
    LTE: '≤',
  };

  const op = opMap[predicate.op] || predicate.op;
  const value =
    typeof predicate.value === 'string' ? predicate.value : JSON.stringify(predicate.value);

  return `${predicate.field} ${op} ${value}`;
}

/**
 * Get chip color based on field.
 */
function getChipColor(field: string): string {
  const colorMap: Record<string, string> = {
    origin: 'bg-cyan-900/30 text-cyan-400 border-cyan-700/50',
    phase: 'bg-purple-900/30 text-purple-400 border-purple-700/50',
    tags: 'bg-amber-900/30 text-amber-400 border-amber-700/50',
    timestamp: 'bg-blue-900/30 text-blue-400 border-blue-700/50',
  };

  return colorMap[field] || 'bg-gray-800/50 text-gray-400 border-gray-700/50';
}

// =============================================================================
// Component
// =============================================================================

export function SelectionChips({
  predicates,
  onRemove,
  onClear,
  className = '',
}: SelectionChipsProps): React.ReactElement | null {
  if (predicates.length === 0) {
    return null;
  }

  return (
    <div
      className={`selection-chips flex items-center gap-2 flex-wrap ${className}`}
      role="group"
      aria-label="Active filters"
    >
      {predicates.map((predicate) => (
        <span
          key={predicate.field}
          className={`
            selection-chip inline-flex items-center gap-1.5
            px-2 py-1 rounded-full border text-xs font-medium
            ${getChipColor(predicate.field)}
          `}
        >
          <span>{formatPredicate(predicate)}</span>
          <button
            onClick={() => onRemove(predicate.field)}
            className="hover:text-white transition-colors"
            aria-label={`Remove ${predicate.field} filter`}
          >
            <X className="w-3 h-3" />
          </button>
        </span>
      ))}

      {onClear && predicates.length > 1 && (
        <button
          onClick={onClear}
          className="inline-flex items-center gap-1 px-2 py-1 text-xs text-gray-500 hover:text-gray-300 transition-colors"
          aria-label="Clear all filters"
        >
          <XCircle className="w-3 h-3" />
          <span>Clear all</span>
        </button>
      )}
    </div>
  );
}

export default SelectionChips;
