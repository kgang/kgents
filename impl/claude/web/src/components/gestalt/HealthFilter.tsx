/**
 * HealthFilter - Toggle health grades with distribution badges.
 *
 * Shows all health grades (A+ through F) as toggle buttons with:
 * - Color-coded grade labels
 * - Module count badges
 * - Multi-select support
 * - Quick all/none toggles
 *
 * @see plans/gestalt-visual-showcase.md Chunk 1
 */

import { HEALTH_GRADE_CONFIG } from '../../api/types';
import { HEALTH_GRADES, type Density, type GradeDistribution, type HealthGrade } from './types';

// =============================================================================
// Props
// =============================================================================

export interface HealthFilterProps {
  /** Set of currently enabled grades */
  enabledGrades: Set<string>;
  /** Callback when a grade is toggled */
  onToggle: (grade: HealthGrade) => void;
  /** Callback to set all grades at once */
  onSetAll: (enabled: boolean) => void;
  /** Distribution of modules by grade */
  distribution: GradeDistribution;
  /** Density for responsive sizing */
  density: Density;
  /** Additional class names */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export function HealthFilter({
  enabledGrades,
  onToggle,
  onSetAll,
  distribution,
  density,
  className,
}: HealthFilterProps) {
  const isCompact = density === 'compact';
  const allEnabled = enabledGrades.size === HEALTH_GRADES.length;
  const noneEnabled = enabledGrades.size === 0;

  // Split grades into two rows for better layout
  const topRow: HealthGrade[] = ['A+', 'A', 'B+', 'B'];
  const bottomRow: HealthGrade[] = ['C+', 'C', 'D', 'F'];

  const renderGradeButton = (grade: HealthGrade) => {
    const config = HEALTH_GRADE_CONFIG[grade] || HEALTH_GRADE_CONFIG['?'];
    const count = distribution[grade] || 0;
    const enabled = enabledGrades.has(grade);

    // Skip grades with 0 modules in compact mode
    if (isCompact && count === 0) return null;

    return (
      <button
        key={grade}
        onClick={() => onToggle(grade)}
        className={`
          flex items-center gap-1 rounded-md font-mono transition-all duration-150
          ${isCompact ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-sm'}
          ${!enabled ? 'opacity-40 hover:opacity-70' : ''}
        `}
        style={{
          backgroundColor: enabled ? `${config.color}22` : 'transparent',
          color: config.color,
          // Ring color is handled by the ring-1 class + Tailwind
          boxShadow: enabled ? `inset 0 0 0 1px ${config.color}66` : 'none',
        }}
        aria-pressed={enabled}
        title={`${grade}: ${count} modules`}
      >
        <span className={`${enabled ? '' : 'line-through'} ${isCompact ? 'text-[10px]' : 'text-xs'} font-bold`}>
          {grade}
        </span>
        {count > 0 && (
          <span className={`text-gray-400 ${isCompact ? 'text-[9px]' : 'text-[10px]'}`}>
            ({count})
          </span>
        )}
      </button>
    );
  };

  return (
    <div className={className}>
      <div className="flex justify-between items-center mb-2">
        <h4
          className={`font-semibold text-gray-400 uppercase tracking-wide ${
            isCompact ? 'text-[10px]' : 'text-xs'
          }`}
        >
          Health Grades
        </h4>
        <div className="flex gap-1">
          <button
            onClick={() => onSetAll(true)}
            disabled={allEnabled}
            className={`
              text-gray-500 hover:text-gray-300 disabled:opacity-30 disabled:cursor-not-allowed
              ${isCompact ? 'text-[9px]' : 'text-[10px]'}
            `}
            title="Enable all grades"
          >
            All
          </button>
          <span className="text-gray-600">|</span>
          <button
            onClick={() => onSetAll(false)}
            disabled={noneEnabled}
            className={`
              text-gray-500 hover:text-gray-300 disabled:opacity-30 disabled:cursor-not-allowed
              ${isCompact ? 'text-[9px]' : 'text-[10px]'}
            `}
            title="Disable all grades"
          >
            None
          </button>
        </div>
      </div>

      {isCompact ? (
        // Compact: horizontal grid
        <div className="flex flex-wrap gap-1">
          {HEALTH_GRADES.map(renderGradeButton)}
        </div>
      ) : (
        // Comfortable/Spacious: two rows
        <div className="space-y-1.5">
          <div className="flex flex-wrap gap-1.5">{topRow.map(renderGradeButton)}</div>
          <div className="flex flex-wrap gap-1.5">{bottomRow.map(renderGradeButton)}</div>
        </div>
      )}
    </div>
  );
}

export default HealthFilter;
