/**
 * LensSelector - Mode switcher for TerrariumView lenses.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Provides toggle between lens modes:
 * - TIMELINE: Chronological list
 * - GRAPH: Causal graph with edges
 * - SUMMARY: Aggregated summary
 * - DETAIL: Full detail for single trace
 */

import React from 'react';
import { List, Network, LayoutGrid, FileText } from 'lucide-react';
import type { LensMode } from '../../api/types/_generated/world-scenery';

// =============================================================================
// Types
// =============================================================================

export interface LensSelectorProps {
  /** Current lens mode */
  current: LensMode;
  /** Callback when mode changes */
  onChange: (mode: LensMode) => void;
  /** Disabled modes */
  disabled?: LensMode[];
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

interface LensOption {
  mode: LensMode;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

const LENS_OPTIONS: LensOption[] = [
  {
    mode: 'TIMELINE',
    label: 'Timeline',
    icon: List,
    description: 'Chronological list of traces',
  },
  {
    mode: 'GRAPH',
    label: 'Graph',
    icon: Network,
    description: 'Causal graph with edges',
  },
  {
    mode: 'SUMMARY',
    label: 'Summary',
    icon: LayoutGrid,
    description: 'Grouped summary view',
  },
  {
    mode: 'DETAIL',
    label: 'Detail',
    icon: FileText,
    description: 'Full detail for single trace',
  },
];

// =============================================================================
// Component
// =============================================================================

export function LensSelector({
  current,
  onChange,
  disabled = [],
  className = '',
}: LensSelectorProps): React.ReactElement {
  return (
    <div
      className={`lens-selector inline-flex items-center gap-1 bg-gray-800/50 rounded-lg p-1 ${className}`}
      role="group"
      aria-label="Lens mode selector"
    >
      {LENS_OPTIONS.map(({ mode, label, icon: Icon, description }) => {
        const isActive = current === mode;
        const isDisabled = disabled.includes(mode);

        return (
          <button
            key={mode}
            onClick={() => !isDisabled && onChange(mode)}
            disabled={isDisabled}
            className={`
              lens-option flex items-center gap-1.5 px-3 py-1.5 rounded-md
              text-sm font-medium transition-all
              ${
                isActive
                  ? 'bg-cyan-900/50 text-cyan-400 border border-cyan-700/50'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/50'
              }
              ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
            title={description}
            aria-pressed={isActive}
          >
            <Icon className="w-4 h-4" />
            <span className="hidden sm:inline">{label}</span>
          </button>
        );
      })}
    </div>
  );
}

export default LensSelector;
