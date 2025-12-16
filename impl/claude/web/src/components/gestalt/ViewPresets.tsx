/**
 * ViewPresets - One-click view preset buttons for Gestalt.
 *
 * Provides quick access to common visualization configurations:
 * - All: Show everything
 * - Healthy: A/B grades only
 * - At Risk: C/D/F grades
 * - Violations: Focus on violation edges
 * - Core: Protocols and agents layers
 *
 * @see plans/gestalt-visual-showcase.md Chunk 1
 */

import { VIEW_PRESETS, type Density, type ViewPreset } from './types';

// =============================================================================
// Props
// =============================================================================

export interface ViewPresetsProps {
  /** Currently active preset ID */
  activePreset: string | null;
  /** Callback when a preset is selected */
  onPresetSelect: (preset: ViewPreset) => void;
  /** Density for responsive sizing */
  density: Density;
  /** Additional class names */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export function ViewPresets({ activePreset, onPresetSelect, density, className }: ViewPresetsProps) {
  const isCompact = density === 'compact';

  return (
    <div className={className}>
      <h4
        className={`font-semibold text-gray-400 mb-2 uppercase tracking-wide ${
          isCompact ? 'text-[10px]' : 'text-xs'
        }`}
      >
        View Presets
      </h4>
      <div className={`flex flex-wrap gap-1.5 ${isCompact ? 'gap-1' : 'gap-1.5'}`}>
        {VIEW_PRESETS.map((preset) => {
          const isActive = activePreset === preset.id;
          return (
            <button
              key={preset.id}
              onClick={() => onPresetSelect(preset)}
              title={preset.description}
              className={`
                flex items-center gap-1 rounded-lg font-medium transition-all duration-150
                ${isCompact ? 'px-2 py-1 text-xs' : 'px-2.5 py-1.5 text-sm'}
                ${
                  isActive
                    ? 'bg-green-600 text-white shadow-md shadow-green-500/20'
                    : 'bg-gray-700/60 text-gray-300 hover:bg-gray-600 hover:text-white'
                }
              `}
              aria-pressed={isActive}
            >
              <span className={isCompact ? 'text-sm' : 'text-base'}>{preset.icon}</span>
              <span>{preset.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default ViewPresets;
