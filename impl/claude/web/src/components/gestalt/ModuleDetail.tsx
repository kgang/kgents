/**
 * ModuleDetail - Module detail side panel
 *
 * Shows comprehensive information about a selected module:
 * - Health metrics (coupling, cohesion, instability)
 * - Dependencies and dependents
 * - File path and lines of code
 *
 * @see spec/protocols/2d-renaissance.md - §4.1 Gestalt2D
 */

import { useMemo } from 'react';
import { X, FileCode, ArrowUpRight, ArrowDownRight, BarChart3 } from 'lucide-react';
import { HEALTH_GRADE_CONFIG } from '@/api/types';
import type { WorldCodebaseTopologyResponse } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

type CodebaseNode = WorldCodebaseTopologyResponse['nodes'][number];
type CodebaseLink = WorldCodebaseTopologyResponse['links'][number];

export interface ModuleDetailProps {
  /** The selected module */
  module: CodebaseNode;
  /** All links for finding dependencies/dependents */
  links: CodebaseLink[];
  /** Close callback */
  onClose?: () => void;
  /** Compact mode for mobile */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export function ModuleDetail({
  module,
  links,
  onClose,
  compact = false,
  className = '',
}: ModuleDetailProps) {
  const gradeConfig = HEALTH_GRADE_CONFIG[module.health_grade] || {
    color: '#6B7280',
    bg: '#374151',
    label: module.health_grade,
  };

  // Find dependencies (this module → others)
  const dependencies = useMemo(() => {
    return links
      .filter((l) => l.source === module.id)
      .map((l) => ({
        target: l.target,
        type: l.import_type,
        isViolation: l.is_violation,
      }));
  }, [links, module.id]);

  // Find dependents (others → this module)
  const dependents = useMemo(() => {
    return links
      .filter((l) => l.target === module.id)
      .map((l) => ({
        source: l.source,
        type: l.import_type,
        isViolation: l.is_violation,
      }));
  }, [links, module.id]);

  return (
    <div className={`bg-[#2a2a2a] rounded-lg ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between p-4 border-b border-gray-700">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <FileCode className="w-5 h-5 text-[#4A6B4A] flex-shrink-0" />
            <h3
              className={`font-semibold text-white truncate ${compact ? 'text-sm' : 'text-base'}`}
            >
              {module.label}
            </h3>
          </div>
          {module.layer && (
            <p className="text-xs text-gray-500 mt-1 ml-7">
              Layer: <span className="text-gray-400">{module.layer}</span>
            </p>
          )}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-white transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Health Grade */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">Health Grade</span>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold" style={{ color: gradeConfig.color }}>
              {module.health_grade}
            </span>
            <span className="text-xs text-gray-500">{(module.health_score * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="p-4 border-b border-gray-700">
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3 flex items-center gap-2">
          <BarChart3 className="w-3 h-3" />
          Metrics
        </h4>
        <div className={`grid gap-3 ${compact ? 'grid-cols-2' : 'grid-cols-2'}`}>
          <MetricItem
            label="Coupling"
            value={module.coupling}
            maxValue={1}
            description="Dependencies on other modules"
            goodIsLow
          />
          <MetricItem
            label="Cohesion"
            value={module.cohesion}
            maxValue={1}
            description="Internal consistency"
            goodIsLow={false}
          />
          <MetricItem
            label="Lines"
            value={module.lines_of_code}
            maxValue={2000}
            description="Lines of code"
            goodIsLow
            isCount
          />
          {module.instability !== null && (
            <MetricItem
              label="Instability"
              value={module.instability}
              maxValue={1}
              description="Likelihood of change"
              goodIsLow
            />
          )}
        </div>
      </div>

      {/* Dependencies */}
      {dependencies.length > 0 && (
        <div className="p-4 border-b border-gray-700">
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-2">
            <ArrowUpRight className="w-3 h-3" />
            Dependencies ({dependencies.length})
          </h4>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {dependencies.slice(0, 10).map((dep) => (
              <div
                key={dep.target}
                className={`
                  text-xs px-2 py-1 rounded flex items-center justify-between
                  ${dep.isViolation ? 'bg-red-900/20 text-red-400' : 'bg-gray-700/50 text-gray-300'}
                `}
              >
                <span className="truncate">{extractModuleName(dep.target)}</span>
                {dep.isViolation && (
                  <span className="text-[10px] text-red-400 ml-2">violation</span>
                )}
              </div>
            ))}
            {dependencies.length > 10 && (
              <span className="text-xs text-gray-500">+{dependencies.length - 10} more</span>
            )}
          </div>
        </div>
      )}

      {/* Dependents */}
      {dependents.length > 0 && (
        <div className="p-4">
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-2">
            <ArrowDownRight className="w-3 h-3" />
            Dependents ({dependents.length})
          </h4>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {dependents.slice(0, 10).map((dep) => (
              <div
                key={dep.source}
                className={`
                  text-xs px-2 py-1 rounded flex items-center justify-between
                  ${dep.isViolation ? 'bg-red-900/20 text-red-400' : 'bg-gray-700/50 text-gray-300'}
                `}
              >
                <span className="truncate">{extractModuleName(dep.source)}</span>
                {dep.isViolation && (
                  <span className="text-[10px] text-red-400 ml-2">violation</span>
                )}
              </div>
            ))}
            {dependents.length > 10 && (
              <span className="text-xs text-gray-500">+{dependents.length - 10} more</span>
            )}
          </div>
        </div>
      )}

      {/* No connections */}
      {dependencies.length === 0 && dependents.length === 0 && (
        <div className="p-4 text-center text-gray-500 text-sm">
          No dependencies or dependents found
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface MetricItemProps {
  label: string;
  value: number;
  maxValue: number;
  description: string;
  goodIsLow: boolean;
  isCount?: boolean;
}

function MetricItem({
  label,
  value,
  maxValue,
  description,
  goodIsLow,
  isCount = false,
}: MetricItemProps) {
  // Calculate health color based on value
  const percentage = Math.min(value / maxValue, 1);
  const isGood = goodIsLow ? percentage < 0.5 : percentage > 0.5;
  const color = isGood ? '#4A6B4A' : percentage < 0.75 ? '#D4A574' : '#EF4444';

  return (
    <div className="bg-[#333] rounded p-2">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-400">{label}</span>
        <span className="text-sm font-medium" style={{ color }}>
          {isCount ? value.toLocaleString() : `${(value * 100).toFixed(0)}%`}
        </span>
      </div>
      <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full transition-all duration-300"
          style={{
            width: `${percentage * 100}%`,
            backgroundColor: color,
          }}
        />
      </div>
      <p className="text-[10px] text-gray-500 mt-1">{description}</p>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function extractModuleName(fullPath: string): string {
  const parts = fullPath.split('.');
  if (parts.length <= 2) return fullPath;
  return parts.slice(-2).join('.');
}

export default ModuleDetail;
