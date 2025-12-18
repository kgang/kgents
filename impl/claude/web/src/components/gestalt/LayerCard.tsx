/**
 * LayerCard - Organic layer panel with health-colored modules
 *
 * Displays a codebase layer (protocols, services, agents, models) as an
 * expandable card with module badges showing health grades.
 *
 * Living Earth aesthetic: cards "breathe" when all modules are healthy.
 *
 * @see spec/protocols/2d-renaissance.md - §4.1 Gestalt2D
 */

import { useState, useCallback, useMemo } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { Breathe } from '@/components/joy';
import { HEALTH_GRADE_CONFIG } from '@/api/types';
import type { WorldCodebaseTopologyResponse } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

type CodebaseNode = WorldCodebaseTopologyResponse['nodes'][number];

export interface LayerCardProps {
  /** Layer name (protocols, services, agents, etc.) */
  layer: string;
  /** Modules in this layer */
  nodes: CodebaseNode[];
  /** Accent color for the layer */
  color: string;
  /** Currently selected module ID */
  selectedModule?: string | null;
  /** Module selection callback */
  onModuleSelect?: (moduleId: string) => void;
  /** Compact mode for mobile */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const MAX_COLLAPSED_MODULES = 6;
const MAX_EXPANDED_MODULES = 20;

// =============================================================================
// Component
// =============================================================================

export function LayerCard({
  layer,
  nodes,
  color,
  selectedModule,
  onModuleSelect,
  compact = false,
  className = '',
}: LayerCardProps) {
  const [expanded, setExpanded] = useState(false);

  // Calculate health distribution
  const healthStats = useMemo(() => {
    const healthy = nodes.filter(
      (n) => n.health_grade.startsWith('A') || n.health_grade.startsWith('B')
    ).length;
    const atRisk = nodes.length - healthy;
    const isHealthy = atRisk === 0;
    return { healthy, atRisk, isHealthy };
  }, [nodes]);

  // Sort by health (worst first when expanding to see problems)
  const sortedNodes = useMemo(() => {
    return [...nodes].sort((a, b) => {
      const gradeOrder = ['F', 'D', 'C', 'C+', 'B', 'B+', 'A', 'A+'];
      return gradeOrder.indexOf(a.health_grade) - gradeOrder.indexOf(b.health_grade);
    });
  }, [nodes]);

  // Modules to display
  const displayLimit = expanded ? MAX_EXPANDED_MODULES : MAX_COLLAPSED_MODULES;
  const displayedNodes = sortedNodes.slice(0, displayLimit);
  const hasMore = nodes.length > displayLimit;

  const toggleExpand = useCallback(() => {
    setExpanded((prev) => !prev);
  }, []);

  const handleModuleClick = useCallback(
    (moduleId: string) => {
      onModuleSelect?.(moduleId);
    },
    [onModuleSelect]
  );

  return (
    <div
      className={`
        bg-[#2a2a2a] rounded-lg overflow-hidden
        border border-gray-700 hover:border-gray-600 transition-colors
        ${className}
      `}
    >
      {/* Header */}
      <button
        onClick={toggleExpand}
        className="w-full flex items-center justify-between p-3 hover:bg-[#333] transition-colors"
      >
        <div className="flex items-center gap-3">
          <Breathe intensity={healthStats.isHealthy ? 0.2 : 0} speed="slow">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
          </Breathe>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className={`font-medium text-white ${compact ? 'text-sm' : 'text-base'}`}>
                {formatLayerName(layer)}
              </span>
              <span className={`text-gray-500 ${compact ? 'text-xs' : 'text-sm'}`}>
                {nodes.length}
              </span>
            </div>
            {!compact && (
              <div className="text-xs text-gray-500 flex items-center gap-2">
                {healthStats.healthy > 0 && (
                  <span className="text-green-400">{healthStats.healthy} healthy</span>
                )}
                {healthStats.atRisk > 0 && (
                  <span className="text-amber-400">{healthStats.atRisk} at risk</span>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Health bar mini */}
          <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all duration-300"
              style={{ width: `${(healthStats.healthy / nodes.length) * 100}%` }}
            />
          </div>
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </button>

      {/* Module Grid */}
      <div
        className={`
          px-3 pb-3 transition-all duration-300 overflow-hidden
          ${expanded ? 'max-h-[600px]' : 'max-h-[160px]'}
        `}
      >
        <div className="flex flex-wrap gap-1.5">
          {displayedNodes.map((node) => (
            <ModuleBadge
              key={node.id}
              node={node}
              isSelected={node.id === selectedModule}
              onClick={handleModuleClick}
              compact={compact}
            />
          ))}
          {hasMore && (
            <span className="text-xs text-gray-500 px-2 py-0.5">
              +{nodes.length - displayLimit} more
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface ModuleBadgeProps {
  node: CodebaseNode;
  isSelected: boolean;
  onClick: (moduleId: string) => void;
  compact: boolean;
}

function ModuleBadge({ node, isSelected, onClick, compact }: ModuleBadgeProps) {
  const gradeConfig = HEALTH_GRADE_CONFIG[node.health_grade] || {
    color: '#6B7280',
    bg: '#374151',
    label: node.health_grade,
  };

  return (
    <button
      onClick={() => onClick(node.id)}
      className={`
        group flex items-center gap-1.5 px-2 py-1 rounded
        transition-all duration-200
        ${isSelected ? 'bg-[#4A6B4A] ring-1 ring-[#8BAB8B]' : 'bg-[#3a3a3a] hover:bg-[#444]'}
        ${compact ? 'text-[10px]' : 'text-xs'}
      `}
      title={`${node.label} (${node.health_grade}) - ${node.lines_of_code} LoC`}
    >
      {/* Grade indicator */}
      <span
        className="w-1.5 h-1.5 rounded-full flex-shrink-0"
        style={{ backgroundColor: gradeConfig.color }}
      />

      {/* Module name */}
      <span className={`truncate max-w-[100px] ${isSelected ? 'text-white' : 'text-gray-300'}`}>
        {node.label}
      </span>

      {/* Grade badge (on hover or if at-risk) */}
      {(node.health_grade.startsWith('C') ||
        node.health_grade.startsWith('D') ||
        node.health_grade === 'F') && (
        <span className="text-[9px] font-bold px-1 rounded" style={{ color: gradeConfig.color }}>
          {node.health_grade}
        </span>
      )}
    </button>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatLayerName(layer: string): string {
  // Capitalize first letter of each word
  return layer
    .split(/[._-]/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export default LayerCard;
