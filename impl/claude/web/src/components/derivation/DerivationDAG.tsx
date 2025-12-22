/**
 * DerivationDAG: Visualization of agent derivation chains.
 *
 * Phase 5: Derivation Framework Visualization
 *
 * This component renders the derivation DAG showing:
 * - Bootstrap axioms at the top (tier 0)
 * - Derived agents layered by tier
 * - derives_from edges as connections
 * - Confidence visualized as node opacity/glow
 * - Interactive navigation through portal tokens
 *
 * Integrates with:
 * - typed-hypergraph: DAG is a hypergraph
 * - portal-token: Nodes are expandable portals
 * - exploration-harness: Navigation leaves trails
 *
 * @example
 * ```tsx
 * <DerivationDAG
 *   data={dagResponse}
 *   onNodeClick={(agentName) => navigate(`/derivation/${agentName}`)}
 * />
 * ```
 */

import { useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import type {
  DerivationDAGNode,
  DerivationDAGEdge,
  DerivationTier,
} from '../../api/types';
import { DERIVATION_TIER_CONFIG } from '../../api/types';

// =============================================================================
// Types
// =============================================================================

export interface DerivationDAGData {
  nodes: DerivationDAGNode[];
  edges: DerivationDAGEdge[];
  tier_layers: Partial<Record<DerivationTier, string[]>>;
  focus: string | null;
}

export interface DerivationDAGProps {
  data: DerivationDAGData;
  onNodeClick?: (agentName: string) => void;
  onEdgeClick?: (source: string, target: string) => void;
  compact?: boolean;
  showLabels?: boolean;
  className?: string;
}

// =============================================================================
// Layout Constants
// =============================================================================

const TIER_ORDER: DerivationTier[] = [
  'bootstrap',
  'functor',
  'polynomial',
  'operad',
  'jewel',
  'app',
];

const NODE_RADIUS = 24;
const TIER_HEIGHT = 80;
const MIN_NODE_SPACING = 60;
const PADDING = 40;

// =============================================================================
// Layout Calculations
// =============================================================================

interface LayoutNode extends DerivationDAGNode {
  x: number;
  y: number;
}

function calculateLayout(data: DerivationDAGData, width: number): Map<string, LayoutNode> {
  const positions = new Map<string, LayoutNode>();

  // Calculate Y position based on tier
  const getTierY = (tier: DerivationTier): number => {
    const tierIndex = TIER_ORDER.indexOf(tier);
    return PADDING + tierIndex * TIER_HEIGHT;
  };

  // Group nodes by tier
  const nodesByTier: Map<DerivationTier, DerivationDAGNode[]> = new Map();
  for (const node of data.nodes) {
    const tier = node.tier;
    if (!nodesByTier.has(tier)) {
      nodesByTier.set(tier, []);
    }
    nodesByTier.get(tier)!.push(node);
  }

  // Position nodes within each tier
  for (const tier of TIER_ORDER) {
    const tierNodes = nodesByTier.get(tier) || [];
    if (tierNodes.length === 0) continue;

    const y = getTierY(tier);
    const availableWidth = width - PADDING * 2;
    const spacing = Math.max(
      MIN_NODE_SPACING,
      availableWidth / (tierNodes.length + 1)
    );

    tierNodes.forEach((node, i) => {
      positions.set(node.id, {
        ...node,
        x: PADDING + (i + 1) * spacing,
        y,
      });
    });
  }

  return positions;
}

// =============================================================================
// Edge Path Calculation
// =============================================================================

interface EdgePath {
  edge: DerivationDAGEdge;
  path: string;
  midX: number;
  midY: number;
}

function calculateEdgePath(
  edge: DerivationDAGEdge,
  positions: Map<string, LayoutNode>,
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

  const startX = source.x + nx * NODE_RADIUS;
  const startY = source.y + ny * NODE_RADIUS;
  const endX = target.x - nx * (NODE_RADIUS + 6);
  const endY = target.y - ny * (NODE_RADIUS + 6);

  // Curved path for better visibility
  const controlX = (startX + endX) / 2;
  const controlY = (startY + endY) / 2 - 20;

  const path = `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`;

  return {
    edge,
    path,
    midX: controlX,
    midY: controlY,
  };
}

// =============================================================================
// DAG Node Component
// =============================================================================

interface DAGNodeProps {
  node: LayoutNode;
  isFocused: boolean;
  onClick?: () => void;
  showLabel: boolean;
}

function DAGNode({ node, isFocused, onClick, showLabel }: DAGNodeProps) {
  const config = DERIVATION_TIER_CONFIG[node.tier];
  const opacity = 0.4 + node.confidence * 0.6; // 40% to 100% based on confidence

  return (
    <g
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {/* Glow for focused/high-confidence nodes */}
      {(isFocused || node.confidence >= 0.9) && (
        <motion.circle
          cx={node.x}
          cy={node.y}
          r={NODE_RADIUS + 8}
          fill={config.color}
          opacity={0.2}
          initial={{ scale: 0.8 }}
          animate={{ scale: [0.8, 1.1, 0.8] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}

      {/* Main node circle */}
      <motion.circle
        cx={node.x}
        cy={node.y}
        r={NODE_RADIUS}
        fill={config.color}
        opacity={opacity}
        stroke={isFocused ? '#fff' : config.color}
        strokeWidth={isFocused ? 3 : 1}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.3, type: 'spring' }}
        whileHover={{ scale: 1.1 }}
      />

      {/* Bootstrap icon for axioms */}
      {node.is_bootstrap && (
        <text
          x={node.x}
          y={node.y + 4}
          textAnchor="middle"
          className="fill-white text-sm font-bold"
          style={{ pointerEvents: 'none' }}
        >
          ✦
        </text>
      )}

      {/* Confidence indicator */}
      {!node.is_bootstrap && (
        <text
          x={node.x}
          y={node.y + 4}
          textAnchor="middle"
          className="fill-white text-xs font-mono"
          style={{ pointerEvents: 'none' }}
        >
          {Math.round(node.confidence * 100)}
        </text>
      )}

      {/* Label */}
      {showLabel && (
        <text
          x={node.x}
          y={node.y + NODE_RADIUS + 16}
          textAnchor="middle"
          className="fill-gray-300 text-xs"
          style={{ pointerEvents: 'none' }}
        >
          {node.label}
        </text>
      )}
    </g>
  );
}

// =============================================================================
// Tier Label Component
// =============================================================================

interface TierLabelProps {
  tier: DerivationTier;
  y: number;
}

function TierLabel({ tier, y }: TierLabelProps) {
  const config = DERIVATION_TIER_CONFIG[tier];

  return (
    <g>
      <text
        x={12}
        y={y + 4}
        className="text-xs font-semibold"
        fill={config.color}
      >
        {tier.charAt(0).toUpperCase() + tier.slice(1)}
      </text>
      <text
        x={12}
        y={y + 16}
        className="text-[10px]"
        fill="#6b7280"
      >
        ≤{(config.ceiling * 100).toFixed(0)}%
      </text>
    </g>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function DerivationDAG({
  data,
  onNodeClick,
  onEdgeClick,
  compact = false,
  showLabels = true,
  className = '',
}: DerivationDAGProps) {
  // Calculate dimensions
  const width = compact ? 500 : 800;
  const height = compact ? 400 : 520;

  // Calculate layout positions
  const positions = useMemo(
    () => calculateLayout(data, width),
    [data, width]
  );

  // Calculate edge paths
  const edgePaths = useMemo(
    () =>
      data.edges
        .map((edge) => calculateEdgePath(edge, positions))
        .filter((p): p is EdgePath => p !== null),
    [data.edges, positions]
  );

  // Click handlers
  const handleNodeClick = useCallback(
    (id: string) => {
      onNodeClick?.(id);
    },
    [onNodeClick]
  );

  const handleEdgeClick = useCallback(
    (source: string, target: string) => {
      onEdgeClick?.(source, target);
    },
    [onEdgeClick]
  );

  // Check which tiers have nodes
  const activeTiers = useMemo(() => {
    const tiers = new Set<DerivationTier>();
    for (const node of data.nodes) {
      tiers.add(node.tier);
    }
    return tiers;
  }, [data.nodes]);

  return (
    <div className={`relative ${className}`}>
      <svg
        width={width}
        height={height}
        className="bg-gray-950 rounded-lg"
      >
        {/* Arrow marker definition */}
        <defs>
          <marker
            id="deriv-arrow"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="4"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path
              d="M0,0 L8,4 L0,8 L2,4 Z"
              fill="#6b7280"
            />
          </marker>
          <marker
            id="deriv-arrow-current"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="4"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path
              d="M0,0 L8,4 L0,8 L2,4 Z"
              fill="#f59e0b"
            />
          </marker>
        </defs>

        {/* Tier labels */}
        {TIER_ORDER.map((tier) => {
          if (!activeTiers.has(tier)) return null;
          const tierIndex = TIER_ORDER.indexOf(tier);
          const y = PADDING + tierIndex * TIER_HEIGHT;
          return <TierLabel key={tier} tier={tier} y={y} />;
        })}

        {/* Edges */}
        <g className="edges">
          {edgePaths.map(({ edge, path }) => (
            <motion.path
              key={`${edge.source}-${edge.target}`}
              d={path}
              fill="none"
              stroke={edge.is_current ? '#f59e0b' : '#4b5563'}
              strokeWidth={edge.is_current ? 2 : 1}
              strokeDasharray={edge.is_current ? undefined : '4 2'}
              markerEnd={
                edge.is_current
                  ? 'url(#deriv-arrow-current)'
                  : 'url(#deriv-arrow)'
              }
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.7 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              style={{ cursor: onEdgeClick ? 'pointer' : 'default' }}
              onClick={() => handleEdgeClick(edge.source, edge.target)}
            />
          ))}
        </g>

        {/* Nodes */}
        <g className="nodes">
          {Array.from(positions.values()).map((node) => (
            <DAGNode
              key={node.id}
              node={node}
              isFocused={data.focus === node.id}
              onClick={() => handleNodeClick(node.id)}
              showLabel={showLabels}
            />
          ))}
        </g>
      </svg>

      {/* Legend */}
      {!compact && (
        <div className="flex gap-4 mt-4 justify-center text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500" />
            Bootstrap (axiom)
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-blue-500" />
            Functor
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-purple-500" />
            Polynomial
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-amber-500" />
            Operad
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-pink-500" />
            Jewel
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-cyan-500" />
            App
          </span>
        </div>
      )}
    </div>
  );
}

export default DerivationDAG;
