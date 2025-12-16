/**
 * PipelineEdge: Connection line between pipeline nodes.
 *
 * Renders an SVG path connecting output ports to input ports.
 * Uses bezier curves for smooth, visually appealing connections.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { useMemo, type MouseEvent } from 'react';
import { cn } from '@/lib/utils';
import type { PipelineEdge as PipelineEdgeData, PipelineNodeData } from '@/components/dnd';

// =============================================================================
// Types
// =============================================================================

export interface PipelineEdgeProps {
  /** Edge data */
  edge: PipelineEdgeData;

  /** All nodes (for position lookup) */
  nodes: PipelineNodeData[];

  /** Whether the edge is selected */
  isSelected?: boolean;

  /** Called when edge is clicked */
  onClick?: (e: MouseEvent<SVGPathElement>) => void;

  /** Additional class names for the path */
  className?: string;
}

/**
 * Props for rendering an in-progress connection.
 */
export interface DraftEdgeProps {
  /** Start position (from port) */
  start: { x: number; y: number };

  /** End position (cursor or snap point) */
  end: { x: number; y: number };

  /** Whether the end is valid (snapped to port) */
  isValid?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const PORT_OFFSET = {
  x: 75, // Half node width
  y: 40, // Port row height
};

const CURVE_TENSION = 0.5;

// =============================================================================
// Component
// =============================================================================

export function PipelineEdge({ edge, nodes, isSelected = false, onClick, className }: PipelineEdgeProps) {
  // Find source and target nodes
  const sourceNode = nodes.find((n) => n.id === edge.source.nodeId);
  const targetNode = nodes.find((n) => n.id === edge.target.nodeId);

  // Calculate path
  const pathData = useMemo(() => {
    if (!sourceNode || !targetNode) return null;

    // Source: right side of node (output port)
    const start = {
      x: sourceNode.position.x + PORT_OFFSET.x * 2, // Right edge
      y: sourceNode.position.y + PORT_OFFSET.y,
    };

    // Target: left side of node (input port)
    const end = {
      x: targetNode.position.x,
      y: targetNode.position.y + PORT_OFFSET.y,
    };

    return createBezierPath(start, end);
  }, [sourceNode, targetNode]);

  if (!pathData) return null;

  return (
    <path
      d={pathData}
      onClick={onClick}
      className={cn(
        'pipeline-edge fill-none transition-colors cursor-pointer',
        isSelected
          ? 'stroke-town-highlight stroke-[3]'
          : 'stroke-town-accent/60 stroke-2 hover:stroke-town-accent',
        className
      )}
      strokeLinecap="round"
      markerEnd={isSelected ? 'url(#arrowhead-selected)' : 'url(#arrowhead)'}
    />
  );
}

/**
 * Renders an in-progress connection being drawn.
 */
export function DraftEdge({ start, end, isValid = false }: DraftEdgeProps) {
  const pathData = createBezierPath(start, end);

  return (
    <path
      d={pathData}
      className={cn(
        'fill-none stroke-2 stroke-dashed pointer-events-none',
        isValid ? 'stroke-town-highlight' : 'stroke-town-accent/50'
      )}
      strokeLinecap="round"
    />
  );
}

/**
 * SVG definitions for edge markers (arrowheads).
 */
export function EdgeMarkers() {
  return (
    <defs>
      {/* Default arrowhead */}
      <marker
        id="arrowhead"
        markerWidth="10"
        markerHeight="7"
        refX="9"
        refY="3.5"
        orient="auto"
        markerUnits="strokeWidth"
      >
        <polygon
          points="0 0, 10 3.5, 0 7"
          className="fill-town-accent/60"
        />
      </marker>

      {/* Selected arrowhead */}
      <marker
        id="arrowhead-selected"
        markerWidth="10"
        markerHeight="7"
        refX="9"
        refY="3.5"
        orient="auto"
        markerUnits="strokeWidth"
      >
        <polygon
          points="0 0, 10 3.5, 0 7"
          className="fill-town-highlight"
        />
      </marker>
    </defs>
  );
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Create a bezier curve path between two points.
 */
function createBezierPath(
  start: { x: number; y: number },
  end: { x: number; y: number }
): string {
  const dx = end.x - start.x;

  // Horizontal curves look best with horizontal control points
  const cp1 = {
    x: start.x + Math.abs(dx) * CURVE_TENSION,
    y: start.y,
  };

  const cp2 = {
    x: end.x - Math.abs(dx) * CURVE_TENSION,
    y: end.y,
  };

  return `M ${start.x} ${start.y} C ${cp1.x} ${cp1.y}, ${cp2.x} ${cp2.y}, ${end.x} ${end.y}`;
}

/**
 * Create a straight line path (for simple connections).
 */
export function createStraightPath(
  start: { x: number; y: number },
  end: { x: number; y: number }
): string {
  return `M ${start.x} ${start.y} L ${end.x} ${end.y}`;
}

/**
 * Create an orthogonal (right-angle) path.
 */
export function createOrthogonalPath(
  start: { x: number; y: number },
  end: { x: number; y: number }
): string {
  const midX = (start.x + end.x) / 2;

  return [
    `M ${start.x} ${start.y}`,
    `H ${midX}`,
    `V ${end.y}`,
    `H ${end.x}`,
  ].join(' ');
}

export default PipelineEdge;
