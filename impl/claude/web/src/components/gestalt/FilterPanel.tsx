/**
 * FilterPanel - Complete filter interface for Gestalt visualization.
 *
 * Combines all filter controls:
 * - Module search (fuzzy)
 * - View presets (one-click configurations)
 * - Health grade filter (toggle by grade)
 * - Layer filter (dropdown)
 * - Display toggles (edges, violations, labels)
 * - Node limit slider
 *
 * @see plans/gestalt-visual-showcase.md Chunk 1
 */

import { useCallback, useMemo } from 'react';
import type { CodebaseModule, CodebaseTopologyResponse } from '../../api/types';
import { HEALTH_GRADE_CONFIG } from '../../api/types';
import { ElasticContainer } from '../elastic/ElasticContainer';
import { ViewPresets } from './ViewPresets';
import { HealthFilter } from './HealthFilter';
import { ModuleSearch } from './ModuleSearch';
import { ObserverSwitcher, DEFAULT_OBSERVERS } from '../path';
import {
  calculateGradeDistribution,
  HEALTH_GRADES,
  type Density,
  type FilterState,
  type HealthGrade,
  type ViewPreset,
} from './types';

// =============================================================================
// Props
// =============================================================================

export interface FilterPanelProps {
  /** Topology data (for modules and layers) */
  topology: CodebaseTopologyResponse | null;
  /** Current filter state */
  filters: FilterState;
  /** Callback to update filters */
  onFiltersChange: (updates: Partial<FilterState>) => void;
  /** Callback when a module is selected (from search) */
  onModuleSelect: (module: CodebaseModule) => void;
  /** Callback when hovering over a search result */
  onModuleFocus?: (module: CodebaseModule | null) => void;
  /** Density for responsive sizing */
  density: Density;
  /** Whether this is in a drawer (mobile) */
  isDrawer?: boolean;
  /** Additional class names */
  className?: string;
  /** Current observer (Wave 0 Foundation 2) */
  observer?: string;
  /** Callback when observer changes */
  onObserverChange?: (observer: string) => void;
}

// =============================================================================
// Component
// =============================================================================

export function FilterPanel({
  topology,
  filters,
  onFiltersChange,
  onModuleSelect,
  onModuleFocus,
  density,
  isDrawer,
  className,
  observer,
  onObserverChange,
}: FilterPanelProps) {
  const isCompact = density === 'compact';

  // Calculate grade distribution
  const gradeDistribution = useMemo(() => {
    if (!topology) return { 'A+': 0, A: 0, 'B+': 0, B: 0, 'C+': 0, C: 0, D: 0, F: 0 };
    return calculateGradeDistribution(topology.nodes);
  }, [topology]);

  // Handlers
  const handlePresetSelect = useCallback(
    (preset: ViewPreset) => {
      // Special handling for "core" preset
      if (preset.id === 'core') {
        // Filter to only show core layers (protocols, agents)
        onFiltersChange({
          ...preset.filters,
          enabledGrades: new Set(HEALTH_GRADES), // All grades
        });
      } else {
        onFiltersChange(preset.filters);
      }
    },
    [onFiltersChange]
  );

  const handleGradeToggle = useCallback(
    (grade: HealthGrade) => {
      const newGrades = new Set(filters.enabledGrades);
      if (newGrades.has(grade)) {
        newGrades.delete(grade);
      } else {
        newGrades.add(grade);
      }
      onFiltersChange({ enabledGrades: newGrades, activePreset: null });
    },
    [filters.enabledGrades, onFiltersChange]
  );

  const handleGradeSetAll = useCallback(
    (enabled: boolean) => {
      const newGrades = enabled ? new Set(HEALTH_GRADES) : new Set<string>();
      onFiltersChange({ enabledGrades: newGrades, activePreset: null });
    },
    [onFiltersChange]
  );

  const handleDisplayToggle = useCallback(
    (key: 'showEdges' | 'showViolations' | 'showLabels' | 'showAnimation', value: boolean) => {
      onFiltersChange({ [key]: value, activePreset: null });
    },
    [onFiltersChange]
  );

  return (
    <ElasticContainer
      layout="stack"
      direction="vertical"
      gap={isCompact ? 'var(--elastic-gap-sm)' : 'var(--elastic-gap-md)'}
      padding={isCompact ? 'var(--elastic-gap-sm)' : 'var(--elastic-gap-md)'}
      className={`
        bg-gray-800/80 overflow-y-auto
        ${isDrawer ? 'h-full rounded-t-xl backdrop-blur-md' : 'border-l border-gray-700'}
        ${className}
      `}
      style={{ minWidth: isDrawer ? 'auto' : isCompact ? 200 : 260 }}
    >
      {/* Observer Switcher - Wave 0 Foundation 2 */}
      {observer && onObserverChange && (
        <div className="pb-2 border-b border-gray-700 mb-2">
          <ObserverSwitcher
            current={observer}
            available={DEFAULT_OBSERVERS.gestalt}
            onChange={onObserverChange}
            variant={isCompact ? 'minimal' : 'pills'}
            size={isCompact ? 'sm' : 'md'}
          />
        </div>
      )}

      {/* Module Search */}
      {topology && (
        <ModuleSearch
          modules={topology.nodes}
          onSelect={onModuleSelect}
          onFocus={onModuleFocus}
          density={density}
        />
      )}

      {/* View Presets */}
      <ViewPresets
        activePreset={filters.activePreset}
        onPresetSelect={handlePresetSelect}
        density={density}
      />

      {/* Health Grade Filter */}
      <HealthFilter
        enabledGrades={filters.enabledGrades}
        onToggle={handleGradeToggle}
        onSetAll={handleGradeSetAll}
        distribution={gradeDistribution}
        density={density}
      />

      {/* Layer Filter */}
      {topology && topology.layers.length > 0 && (
        <div>
          <h4
            className={`font-semibold text-gray-400 mb-1 uppercase tracking-wide ${
              isCompact ? 'text-[10px]' : 'text-xs'
            }`}
          >
            Layer
          </h4>
          <select
            value={filters.layerFilter || ''}
            onChange={(e) =>
              onFiltersChange({ layerFilter: e.target.value || null, activePreset: null })
            }
            className={`
              w-full bg-gray-700 border border-gray-600 rounded-lg
              text-white focus:border-green-500 focus:ring-1 focus:ring-green-500
              ${isCompact ? 'px-2 py-1 text-xs' : 'px-2 py-1.5 text-sm'}
            `}
          >
            <option value="">All layers</option>
            {topology.layers.map((layer) => (
              <option key={layer} value={layer}>
                {layer}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Display Toggles */}
      <div>
        <h4
          className={`font-semibold text-gray-400 mb-2 uppercase tracking-wide ${
            isCompact ? 'text-[10px]' : 'text-xs'
          }`}
        >
          Display
        </h4>
        <div className={isCompact ? 'flex flex-wrap gap-3' : 'space-y-2'}>
          {[
            { key: 'showEdges' as const, label: 'Edges', color: 'green' },
            { key: 'showViolations' as const, label: 'Violations', color: 'red' },
            { key: 'showLabels' as const, label: 'Labels', color: 'blue' },
            { key: 'showAnimation' as const, label: 'Flow', color: 'purple' },
          ].map((opt) => (
            <label key={opt.key} className="flex items-center gap-2 cursor-pointer group">
              <input
                type="checkbox"
                checked={filters[opt.key]}
                onChange={(e) => handleDisplayToggle(opt.key, e.target.checked)}
                className={`
                  rounded bg-gray-700 border-gray-600
                  focus:ring-offset-gray-800
                  ${isCompact ? 'w-3 h-3' : 'w-4 h-4'}
                `}
                style={{
                  accentColor:
                    opt.color === 'green'
                      ? '#22c55e'
                      : opt.color === 'red'
                        ? '#ef4444'
                        : opt.color === 'purple'
                          ? '#8b5cf6'
                          : '#3b82f6',
                }}
              />
              <span
                className={`text-gray-300 group-hover:text-white transition-colors ${
                  isCompact ? 'text-xs' : 'text-sm'
                }`}
              >
                {opt.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Max Nodes Slider */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <h4
            className={`font-semibold text-gray-400 uppercase tracking-wide ${
              isCompact ? 'text-[10px]' : 'text-xs'
            }`}
          >
            Nodes
          </h4>
          <span className={`text-green-400 font-mono ${isCompact ? 'text-xs' : 'text-sm'}`}>
            {filters.maxNodes}
          </span>
        </div>
        <input
          type="range"
          min={50}
          max={500}
          step={25}
          value={filters.maxNodes}
          onChange={(e) => onFiltersChange({ maxNodes: parseInt(e.target.value) })}
          className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-green-500"
        />
      </div>

      {/* Health Distribution Bar (non-compact only) */}
      {!isCompact && topology && (
        <div className="pt-3 border-t border-gray-700">
          <h4 className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">
            Distribution
          </h4>
          <div className="space-y-1.5">
            {HEALTH_GRADES.filter((g) => gradeDistribution[g] > 0).map((grade) => {
              const config = HEALTH_GRADE_CONFIG[grade];
              const count = gradeDistribution[grade];
              const percentage = (count / topology.nodes.length) * 100;

              return (
                <div key={grade} className="flex items-center gap-2">
                  <span className="w-6 text-center font-bold text-xs" style={{ color: config.color }}>
                    {grade}
                  </span>
                  <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-300"
                      style={{ width: `${percentage}%`, backgroundColor: config.color }}
                    />
                  </div>
                  <span className="text-gray-400 text-xs w-6 text-right font-mono">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </ElasticContainer>
  );
}

export default FilterPanel;
