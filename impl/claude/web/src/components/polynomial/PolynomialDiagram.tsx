/**
 * PolynomialDiagram: Visualize polynomial agent state machines.
 *
 * Foundation 3: Visible Polynomial State
 *
 * This component renders a complete state machine diagram showing:
 * - All positions (states) as nodes
 * - Transitions between states as edges
 * - Current state highlighted
 * - Valid next transitions indicated
 * - History of recent transitions
 *
 * Layouts:
 * - linear: Horizontal or vertical line (good for sequential flows)
 * - circular: Nodes arranged in a circle (good for cyclic state machines)
 * - free: Positions specified manually via x/y in metadata
 *
 * @example
 * ```tsx
 * <PolynomialDiagram
 *   visualization={gardenerVisualization}
 *   layout="linear"
 *   onTransition={(positionId) => advanceToPhase(positionId)}
 * />
 * ```
 */

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import type { PolynomialVisualization, PolynomialEdge } from '../../api/types';
import { PolynomialNode } from './PolynomialNode';

// =============================================================================
// Types
// =============================================================================

export type PolynomialLayout = 'linear' | 'linear-vertical' | 'circular' | 'free';

export interface PolynomialDiagramProps {
  /** The visualization data */
  visualization: PolynomialVisualization;
  /** Layout algorithm */
  layout?: PolynomialLayout;
  /** Called when user clicks to transition to a state */
  onTransition?: (positionId: string) => void;
  /** Show transition history */
  showHistory?: boolean;
  /** Compact mode for smaller displays */
  compact?: boolean;
  /** Show edge labels */
  showEdgeLabels?: boolean;
  /** Custom className */
  className?: string;
}

// =============================================================================
// Layout Calculations
// =============================================================================

interface LayoutPosition {
  id: string;
  x: number;
  y: number;
}

/**
 * Calculate positions for linear (horizontal) layout.
 */
function calculateLinearLayout(
  positions: { id: string }[],
  width: number,
  height: number,
): LayoutPosition[] {
  const count = positions.length;
  if (count === 0) return [];

  const padding = 80;
  const availableWidth = width - padding * 2;
  const spacing = count > 1 ? availableWidth / (count - 1) : 0;
  const y = height / 2;

  return positions.map((p, i) => ({
    id: p.id,
    x: padding + i * spacing,
    y,
  }));
}

/**
 * Calculate positions for linear vertical layout.
 */
function calculateLinearVerticalLayout(
  positions: { id: string }[],
  width: number,
  height: number,
): LayoutPosition[] {
  const count = positions.length;
  if (count === 0) return [];

  const padding = 60;
  const availableHeight = height - padding * 2;
  const spacing = count > 1 ? availableHeight / (count - 1) : 0;
  const x = width / 2;

  return positions.map((p, i) => ({
    id: p.id,
    x,
    y: padding + i * spacing,
  }));
}

/**
 * Calculate positions for circular layout.
 */
function calculateCircularLayout(
  positions: { id: string }[],
  width: number,
  height: number,
): LayoutPosition[] {
  const count = positions.length;
  if (count === 0) return [];

  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 2 - 60;

  // Start from top (-90 degrees)
  const startAngle = -Math.PI / 2;

  return positions.map((p, i) => {
    const angle = startAngle + (2 * Math.PI * i) / count;
    return {
      id: p.id,
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  });
}

/**
 * Get layout positions for the diagram.
 */
function getLayoutPositions(
  visualization: PolynomialVisualization,
  layout: PolynomialLayout,
  width: number,
  height: number,
): Map<string, LayoutPosition> {
  const positions = visualization.positions;
  let layoutPositions: LayoutPosition[];

  switch (layout) {
    case 'linear':
      layoutPositions = calculateLinearLayout(positions, width, height);
      break;
    case 'linear-vertical':
      layoutPositions = calculateLinearVerticalLayout(positions, width, height);
      break;
    case 'circular':
      layoutPositions = calculateCircularLayout(positions, width, height);
      break;
    case 'free':
      // Use positions from metadata if available
      layoutPositions = positions.map((p) => {
        const meta = visualization.metadata as Record<string, { x?: number; y?: number }>;
        const posMeta = meta[p.id];
        return {
          id: p.id,
          x: posMeta?.x ?? width / 2,
          y: posMeta?.y ?? height / 2,
        };
      });
      break;
  }

  return new Map(layoutPositions.map((p) => [p.id, p]));
}

// =============================================================================
// Edge Rendering
// =============================================================================

interface EdgePath {
  edge: PolynomialEdge;
  path: string;
  midX: number;
  midY: number;
}

/**
 * Calculate SVG path for an edge.
 */
function calculateEdgePath(
  edge: PolynomialEdge,
  positions: Map<string, LayoutPosition>,
  nodeRadius: number,
): EdgePath | null {
  const source = positions.get(edge.source);
  const target = positions.get(edge.target);

  if (!source || !target) return null;

  // Calculate direction vector
  const dx = target.x - source.x;
  const dy = target.y - source.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  if (distance === 0) return null;

  // Normalize and offset by node radius
  const nx = dx / distance;
  const ny = dy / distance;

  const startX = source.x + nx * nodeRadius;
  const startY = source.y + ny * nodeRadius;
  const endX = target.x - nx * (nodeRadius + 8); // Extra space for arrow
  const endY = target.y - ny * (nodeRadius + 8);

  // Simple straight line path
  const path = `M ${startX} ${startY} L ${endX} ${endY}`;

  return {
    edge,
    path,
    midX: (startX + endX) / 2,
    midY: (startY + endY) / 2,
  };
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * PolynomialDiagram renders a complete state machine visualization.
 */
export function PolynomialDiagram({
  visualization,
  layout = 'linear',
  onTransition,
  showHistory = false,
  compact = false,
  showEdgeLabels = false,
  className = '',
}: PolynomialDiagramProps) {
  // Dimensions based on mode
  const width = compact ? 400 : 600;
  const height = compact ? 150 : 200;
  const nodeRadius = compact ? 24 : 32;

  // Calculate layout positions
  const layoutPositions = useMemo(
    () => getLayoutPositions(visualization, layout, width, height),
    [visualization, layout, width, height],
  );

  // Calculate edge paths
  const edgePaths = useMemo(() => {
    return visualization.edges
      .map((edge) => calculateEdgePath(edge, layoutPositions, nodeRadius))
      .filter((p): p is EdgePath => p !== null);
  }, [visualization.edges, layoutPositions, nodeRadius]);

  // Set of reachable position IDs
  const reachableSet = useMemo(
    () => new Set(visualization.valid_directions),
    [visualization.valid_directions],
  );

  return (
    <div className={`relative ${className}`} style={{ width, height }}>
      {/* SVG layer for edges */}
      <svg
        className="absolute inset-0 pointer-events-none"
        width={width}
        height={height}
        style={{ overflow: 'visible' }}
      >
        {/* Arrow marker definition */}
        <defs>
          <marker
            id="poly-arrow"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="5"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L10,5 L0,10 L3,5 Z" fill="currentColor" className="text-gray-500" />
          </marker>
          <marker
            id="poly-arrow-valid"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="5"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L10,5 L0,10 L3,5 Z" fill="#f59e0b" />
          </marker>
        </defs>

        {/* Render edges */}
        {edgePaths.map(({ edge, path, midX, midY }) => {
          const isValidTransition =
            edge.source === visualization.current && reachableSet.has(edge.target);

          return (
            <g key={`${edge.source}-${edge.target}`}>
              <motion.path
                d={path}
                fill="none"
                stroke={isValidTransition ? '#f59e0b' : '#4b5563'}
                strokeWidth={isValidTransition ? 2 : 1.5}
                strokeDasharray={edge.is_valid ? undefined : '4 4'}
                markerEnd={isValidTransition ? 'url(#poly-arrow-valid)' : 'url(#poly-arrow)'}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              />

              {/* Edge label */}
              {showEdgeLabels && edge.label && (
                <text
                  x={midX}
                  y={midY - 8}
                  textAnchor="middle"
                  className="text-xs fill-gray-500"
                >
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Node layer */}
      <div className="absolute inset-0">
        {visualization.positions.map((position) => {
          const layoutPos = layoutPositions.get(position.id);
          if (!layoutPos) return null;

          return (
            <div
              key={position.id}
              className="absolute"
              style={{
                left: layoutPos.x,
                top: layoutPos.y,
                transform: 'translate(-50%, -50%)',
              }}
            >
              <PolynomialNode
                position={position}
                isReachable={reachableSet.has(position.id)}
                onTransition={onTransition}
                variant={compact ? 'compact' : 'default'}
                size={nodeRadius * 2}
              />
            </div>
          );
        })}
      </div>

      {/* History overlay */}
      {showHistory && visualization.history.length > 0 && (
        <div className="absolute bottom-0 left-0 right-0 p-2 bg-gray-900/80 rounded-b text-xs text-gray-400">
          <div className="flex gap-2 overflow-x-auto">
            {visualization.history.slice(-5).map((entry, i) => (
              <span key={i} className="whitespace-nowrap">
                {entry.from_position} {'->'} {entry.to_position}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default PolynomialDiagram;
