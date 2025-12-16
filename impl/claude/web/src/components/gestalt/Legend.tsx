/**
 * Legend - Interactive, collapsible legend for Gestalt visualization.
 *
 * Shows visual encoding explanations:
 * - Node health colors (gradient from A+ to F)
 * - Node size (based on LOC)
 * - Edge types (import vs violation)
 * - Layer rings
 *
 * Features:
 * - Collapsible (state persisted to localStorage)
 * - Position configurable
 * - Density-aware sizing
 * - Extensible for infrastructure node types (future)
 *
 * @see plans/gestalt-visual-showcase.md Chunk 2
 */

import { useState, useEffect, useCallback } from 'react';
import { HEALTH_GRADE_CONFIG } from '../../api/types';
import type { Density } from './types';

// =============================================================================
// Types
// =============================================================================

export interface LegendProps {
  /** Position of the legend overlay */
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  /** Whether to start collapsed */
  defaultCollapsed?: boolean;
  /** Density for responsive sizing */
  density: Density;
  /** Additional class names */
  className?: string;
  /** Custom node types (for infrastructure expansion) */
  nodeTypes?: NodeKindConfig[];
  /** Custom edge types (for infrastructure expansion) */
  edgeTypes?: EdgeKindConfig[];
}

/** Configuration for a node kind (future infrastructure expansion) */
export interface NodeKindConfig {
  id: string;
  label: string;
  shape: 'sphere' | 'cylinder' | 'torus' | 'octahedron' | 'box' | 'cone';
  color: string;
}

/** Configuration for an edge kind (future infrastructure expansion) */
export interface EdgeKindConfig {
  id: string;
  label: string;
  color: string;
  style: 'solid' | 'dashed' | 'dotted';
  animated?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const STORAGE_KEY = 'gestalt-legend-collapsed';

/** Health grade groups for the legend */
const HEALTH_GROUPS = [
  { grades: ['A+', 'A'], label: 'A+/A', tier: 'excellent' },
  { grades: ['B+', 'B'], label: 'B+/B', tier: 'good' },
  { grades: ['C+', 'C'], label: 'C+/C', tier: 'fair' },
  { grades: ['D', 'F'], label: 'D/F', tier: 'poor' },
] as const;

/** Default edge types for current implementation */
const DEFAULT_EDGE_TYPES: EdgeKindConfig[] = [
  { id: 'import', label: 'Import', color: '#6b7280', style: 'solid' },
  { id: 'violation', label: 'Violation', color: '#ef4444', style: 'solid' },
];

// =============================================================================
// Subcomponents
// =============================================================================

interface LegendSectionProps {
  title: string;
  children: React.ReactNode;
  density: Density;
}

function LegendSection({ title, children, density }: LegendSectionProps) {
  const isCompact = density === 'compact';
  return (
    <div className={isCompact ? 'mb-2' : 'mb-3'}>
      <h5 className={`text-gray-400 uppercase tracking-wider mb-1 ${isCompact ? 'text-[9px]' : 'text-[10px]'}`}>
        {title}
      </h5>
      {children}
    </div>
  );
}

interface HealthColorSwatchProps {
  grade: string;
  density: Density;
}

function HealthColorSwatch({ grade, density }: HealthColorSwatchProps) {
  const config = HEALTH_GRADE_CONFIG[grade];
  const isCompact = density === 'compact';
  const size = isCompact ? 10 : 12;
  const color = config?.color || '#6b7280';

  return (
    <span
      className="inline-block rounded-full"
      style={{
        width: size,
        height: size,
        backgroundColor: color,
        boxShadow: `0 0 4px ${color}40`,
      }}
      title={`Grade: ${grade}`}
    />
  );
}

interface EdgeSwatchProps {
  edge: EdgeKindConfig;
  density: Density;
}

function EdgeSwatch({ edge, density }: EdgeSwatchProps) {
  const isCompact = density === 'compact';
  const width = isCompact ? 24 : 32;
  const height = isCompact ? 3 : 4;

  // Create dashed pattern if needed
  const dashStyle = edge.style === 'dashed' ? '4 2' : edge.style === 'dotted' ? '2 2' : undefined;

  return (
    <svg width={width} height={height} className="inline-block align-middle">
      <line
        x1={0}
        y1={height / 2}
        x2={width}
        y2={height / 2}
        stroke={edge.color}
        strokeWidth={edge.id === 'violation' ? 2.5 : 1.5}
        strokeDasharray={dashStyle}
        strokeLinecap="round"
      />
      {edge.animated && (
        <circle r={2} fill={edge.color}>
          <animateMotion dur="1.5s" repeatCount="indefinite">
            <mpath xlinkHref={`#edge-path-${edge.id}`} />
          </animateMotion>
        </circle>
      )}
    </svg>
  );
}

interface NodeSizeSwatchProps {
  size: 'small' | 'medium' | 'large';
  label: string;
  density: Density;
}

function NodeSizeSwatch({ size, label, density }: NodeSizeSwatchProps) {
  const isCompact = density === 'compact';
  const sizeMap = {
    small: isCompact ? 6 : 8,
    medium: isCompact ? 10 : 12,
    large: isCompact ? 14 : 16,
  };
  const diameter = sizeMap[size];

  return (
    <div className="flex items-center gap-1.5">
      <span
        className="inline-block rounded-full bg-gray-400/60"
        style={{ width: diameter, height: diameter }}
      />
      <span className={`text-gray-300 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>{label}</span>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function Legend({
  position,
  defaultCollapsed = false,
  density,
  className = '',
  nodeTypes,
  edgeTypes = DEFAULT_EDGE_TYPES,
}: LegendProps) {
  // Collapsed state with localStorage persistence
  const [isCollapsed, setIsCollapsed] = useState(() => {
    if (typeof window === 'undefined') return defaultCollapsed;
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored !== null ? stored === 'true' : defaultCollapsed;
  });

  // Persist collapse state
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(isCollapsed));
  }, [isCollapsed]);

  const handleToggle = useCallback(() => {
    setIsCollapsed((prev) => !prev);
  }, []);

  const isCompact = density === 'compact';

  // Position styles
  const positionStyles: Record<typeof position, string> = {
    'top-left': 'top-3 left-3',
    'top-right': 'top-3 right-3',
    'bottom-left': 'bottom-3 left-3',
    'bottom-right': 'bottom-3 right-3',
  };

  return (
    <div
      className={`
        absolute z-30 bg-gray-800/95 backdrop-blur-sm rounded-lg shadow-xl
        border border-gray-700/50 transition-all duration-200
        ${positionStyles[position]}
        ${className}
      `}
      style={{ minWidth: isCollapsed ? 'auto' : isCompact ? 140 : 180 }}
    >
      {/* Header */}
      <button
        onClick={handleToggle}
        className={`
          w-full flex items-center justify-between gap-2
          text-white font-semibold transition-colors hover:bg-gray-700/50
          ${isCompact ? 'px-2 py-1.5 text-xs' : 'px-3 py-2 text-sm'}
          ${isCollapsed ? 'rounded-lg' : 'rounded-t-lg border-b border-gray-700/50'}
        `}
        aria-expanded={!isCollapsed}
        aria-controls="legend-content"
      >
        <span className="flex items-center gap-1.5">
          <span className={isCompact ? 'text-sm' : 'text-base'}>🗺️</span>
          <span>Legend</span>
        </span>
        <span className={`transition-transform duration-200 ${isCollapsed ? '' : 'rotate-180'}`}>
          ▼
        </span>
      </button>

      {/* Content */}
      {!isCollapsed && (
        <div
          id="legend-content"
          className={isCompact ? 'px-2 py-2' : 'px-3 py-3'}
        >
          {/* Node Health */}
          <LegendSection title="Node Health" density={density}>
            <div className={`flex flex-wrap gap-x-3 ${isCompact ? 'gap-y-1' : 'gap-y-1.5'}`}>
              {HEALTH_GROUPS.map((group) => (
                <div key={group.label} className="flex items-center gap-1">
                  <HealthColorSwatch grade={group.grades[0]} density={density} />
                  <span className={`text-gray-300 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
                    {group.label}
                  </span>
                </div>
              ))}
            </div>
          </LegendSection>

          {/* Node Size */}
          <LegendSection title="Node Size" density={density}>
            <div className={`flex ${isCompact ? 'gap-2' : 'gap-3'} flex-wrap`}>
              <NodeSizeSwatch size="small" label="<100" density={density} />
              <NodeSizeSwatch size="medium" label="~500" density={density} />
              <NodeSizeSwatch size="large" label=">1K" density={density} />
            </div>
          </LegendSection>

          {/* Edges */}
          <LegendSection title="Edges" density={density}>
            <div className={`flex flex-col ${isCompact ? 'gap-1' : 'gap-1.5'}`}>
              {edgeTypes.map((edge) => (
                <div key={edge.id} className="flex items-center gap-2">
                  <EdgeSwatch edge={edge} density={density} />
                  <span className={`text-gray-300 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
                    {edge.label}
                  </span>
                </div>
              ))}
            </div>
          </LegendSection>

          {/* Custom Node Types (infrastructure expansion) */}
          {nodeTypes && nodeTypes.length > 0 && (
            <LegendSection title="Node Types" density={density}>
              <div className={`flex flex-wrap gap-x-3 ${isCompact ? 'gap-y-1' : 'gap-y-1.5'}`}>
                {nodeTypes.map((nodeType) => (
                  <div key={nodeType.id} className="flex items-center gap-1">
                    <span
                      className="inline-block rounded"
                      style={{
                        width: isCompact ? 10 : 12,
                        height: isCompact ? 10 : 12,
                        backgroundColor: nodeType.color,
                      }}
                    />
                    <span className={`text-gray-300 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
                      {nodeType.label}
                    </span>
                  </div>
                ))}
              </div>
            </LegendSection>
          )}

          {/* Rings Explanation */}
          <div className={`pt-2 border-t border-gray-700/50 mt-1 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
            <span className="text-gray-400">
              <span className="text-indigo-400 mr-1">Rings</span>
              = Architectural Layers
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Legend;
