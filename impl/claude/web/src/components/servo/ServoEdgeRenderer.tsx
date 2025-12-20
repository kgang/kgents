/**
 * ServoEdgeRenderer - Renders SceneEdge connections as SVG paths
 *
 * Uses the Organic Vine Algorithm from AgentCanvas for natural-feeling
 * connections between nodes.
 *
 * @see components/canvas/AgentCanvas.tsx - Organic Vine Algorithm
 * @see protocols/agentese/projection/scene.py - SceneEdge
 */

// React is auto-imported in JSX

// =============================================================================
// Types (matching SceneEdge from scene.py)
// =============================================================================

export interface SceneEdge {
  source: string;
  target: string;
  label: string;
  style: 'solid' | 'dashed' | 'dotted';
  metadata: Record<string, unknown>;
}

export interface NodePosition {
  id: string;
  x: number;
  y: number;
}

export interface ServoEdgeRendererProps {
  /** The edge to render */
  edge: SceneEdge;
  /** Position of source node */
  sourcePos: NodePosition;
  /** Position of target node */
  targetPos: NodePosition;
  /** Whether edge is highlighted */
  isHighlighted?: boolean;
  /** Additional className for the path */
  className?: string;
}

// =============================================================================
// Organic Vine Path Calculation (from AgentCanvas)
// =============================================================================

/**
 * Calculate organic vine path between two points.
 *
 * The algorithm creates a natural "droop" like a hanging vine:
 * - Leaves source node horizontally
 * - Arcs downward with gravity
 * - Curves up to meet target node from below
 */
function calculateVinePath(
  fromX: number,
  fromY: number,
  toX: number,
  toY: number
): string {
  const dx = toX - fromX;
  const dy = toY - fromY;
  const dist = Math.sqrt(dx * dx + dy * dy);

  // Droop factor: how much the vine hangs down
  const droopFactor = Math.min(0.3, dist / 800);
  const droop = dist * droopFactor;

  // Determine if we're going up or down
  const goingDown = dy > 0;

  if (goingDown) {
    // Standard vine: droop down then curve up to target
    const cp1x = fromX + dx * 0.3;
    const cp1y = fromY + droop * 0.5;
    const cp2x = fromX + dx * 0.7;
    const cp2y = toY - droop * 0.3;

    return `M ${fromX} ${fromY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${toX} ${toY}`;
  } 
    // Reaching upward: arc out then up
    const absDy = Math.abs(dy);
    const cp1x = fromX + dx * 0.4;
    const cp1y = fromY + absDy * 0.2;
    const cp2x = fromX + dx * 0.6;
    const cp2y = toY + absDy * 0.1;

    return `M ${fromX} ${fromY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${toX} ${toY}`;
  
}

// =============================================================================
// Edge Style Configuration
// =============================================================================

const EDGE_STYLES: Record<SceneEdge['style'], string> = {
  solid: '',
  dashed: '8 4',
  dotted: '2 2',
};

const EDGE_COLORS: Record<string, string> = {
  causal: '#6B8B6B',    // Sage for causality
  dependency: '#C08552', // Copper for dependencies
  flow: '#D4A574',       // Amber for data flow
  default: '#8B8B8B',    // Neutral gray
};

// =============================================================================
// Component
// =============================================================================

export function ServoEdgeRenderer({
  edge,
  sourcePos,
  targetPos,
  isHighlighted = false,
  className = '',
}: ServoEdgeRendererProps) {
  const { style, metadata, label } = edge;

  // Get edge type from metadata
  const edgeType = (metadata.relation as string) ?? 'default';
  const color = EDGE_COLORS[edgeType] ?? EDGE_COLORS.default;

  // Calculate path
  const path = calculateVinePath(sourcePos.x, sourcePos.y, targetPos.x, targetPos.y);

  // Stroke dash array
  const strokeDasharray = EDGE_STYLES[style];

  return (
    <g className={className}>
      {/* Main path */}
      <path
        d={path}
        stroke={color}
        strokeWidth={isHighlighted ? 2.5 : 1.5}
        strokeDasharray={strokeDasharray}
        fill="none"
        strokeLinecap="round"
        className={isHighlighted ? '' : 'animate-vine-breathe'}
        style={{ opacity: isHighlighted ? 1 : 0.7 }}
      />

      {/* Label (if present) */}
      {label && (
        <text
          x={(sourcePos.x + targetPos.x) / 2}
          y={(sourcePos.y + targetPos.y) / 2 - 8}
          textAnchor="middle"
          className="text-[10px] fill-gray-400"
        >
          {label}
        </text>
      )}

      {/* Arrow marker at target */}
      <circle
        cx={targetPos.x}
        cy={targetPos.y}
        r={3}
        fill={color}
        className={isHighlighted ? '' : 'animate-vine-breathe'}
      />
    </g>
  );
}

ServoEdgeRenderer.displayName = 'ServoEdgeRenderer';
