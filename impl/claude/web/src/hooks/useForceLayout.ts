/**
 * useForceLayout - Force-directed layout hook for trail visualization.
 *
 * "Bush's Memex realized: Force-directed graph showing exploration trails."
 *
 * Uses d3-force for organic physics simulation:
 * - Nodes repel each other (charged particles)
 * - Edges act as springs (pull connected nodes together)
 * - Semantic edges have longer natural length (concepts further apart)
 *
 * @see brainstorming/visual-trail-graph-r&d.md
 * @see spec/protocols/trail-protocol.md Section 8
 */

import { useMemo, useCallback, useState, useEffect } from 'react';
import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCenter,
  forceCollide,
  forceY,
  type Simulation,
  type SimulationNodeDatum,
  type SimulationLinkDatum,
} from 'd3-force';
import type { TrailGraphNode, TrailGraphEdge } from '../api/trail';

// =============================================================================
// Types
// =============================================================================

/**
 * Options for force layout configuration.
 */
export interface ForceLayoutOptions {
  /** Repulsion strength between nodes (negative = repel) */
  chargeStrength: number;
  /** Base edge length for structural edges */
  linkDistance: number;
  /** Node collision radius */
  collisionRadius: number;
  /** Center gravity strength */
  centerStrength: number;
  /** Canvas width */
  width: number;
  /** Canvas height */
  height: number;
  /** Number of simulation ticks to run */
  ticks: number;
  /** Enable animation (re-runs simulation on changes) */
  animated: boolean;
}

/**
 * Internal node type with simulation coordinates.
 */
interface ForceNode extends SimulationNodeDatum {
  id: string;
  parentIndex?: number | null; // For branching trails
  // d3-force adds: x, y, vx, vy, fx, fy
}

/**
 * Internal link type for simulation.
 */
interface ForceLink extends SimulationLinkDatum<ForceNode> {
  id: string;
  edgeType: string;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_OPTIONS: ForceLayoutOptions = {
  chargeStrength: -400, // Strong repulsion for spread-out layout
  linkDistance: 150, // Base distance between connected nodes
  collisionRadius: 80, // Prevent node overlap
  centerStrength: 0.1, // Gentle pull to center
  width: 800,
  height: 600,
  ticks: 300, // Enough iterations for stable layout
  animated: false,
};

/**
 * Edge type to spring distance mapping.
 *
 * Semantic edges are longer (concepts are conceptually further apart).
 * Structural edges are shorter (tight coupling).
 */
const EDGE_DISTANCES: Record<string, number> = {
  // Structural edges (tight coupling)
  contains: 100,
  implements: 100,
  extends: 100,
  // Medium coupling
  imports: 140,
  uses: 140,
  calls: 140,
  tests: 140,
  // Semantic edges (loose coupling - conceptual leaps)
  semantic: 220,
  'semantic:similar_to': 200,
  'semantic:grounds': 220,
  'semantic:contradicts': 250,
  'semantic:evolves': 200,
  similar_to: 200,
  grounds: 220,
  pattern: 180,
  specifies: 160,
  projects: 160,
  encodes: 180,
};

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for applying force-directed layout to trail graph nodes.
 *
 * @param nodes - Input nodes from trail API
 * @param edges - Input edges from trail API
 * @param options - Layout configuration
 *
 * @returns Nodes with updated positions from physics simulation
 *
 * @example
 * ```tsx
 * const { layoutNodes, isSimulating, runSimulation } = useForceLayout(nodes, edges);
 *
 * <ReactFlow nodes={layoutNodes} edges={edges} ... />
 * ```
 */
export function useForceLayout(
  nodes: TrailGraphNode[],
  edges: TrailGraphEdge[],
  options: Partial<ForceLayoutOptions> = {}
): {
  layoutNodes: TrailGraphNode[];
  isSimulating: boolean;
  runSimulation: () => void;
} {
  const opts = useMemo(
    () => ({ ...DEFAULT_OPTIONS, ...options }),
    [options]
  );

  const [layoutNodes, setLayoutNodes] = useState<TrailGraphNode[]>(nodes);
  const [isSimulating, setIsSimulating] = useState(false);

  /**
   * Get link distance based on edge type.
   */
  const getLinkDistance = useCallback((edge: TrailGraphEdge): number => {
    // Check for semantic prefix
    if (edge.type === 'semantic') {
      return EDGE_DISTANCES[edge.label] || EDGE_DISTANCES.semantic;
    }
    return EDGE_DISTANCES[edge.label] || opts.linkDistance;
  }, [opts.linkDistance]);

  /**
   * Run force simulation and update node positions.
   */
  const runSimulation = useCallback(() => {
    if (nodes.length === 0) {
      setLayoutNodes([]);
      return;
    }

    setIsSimulating(true);

    // Detect branching trails
    const hasBranching = nodes.some((n) =>
      nodes.filter((other) => other.data.parent_index === n.data.step_index).length > 1
    );

    // Create force nodes with initial positions
    const forceNodes: ForceNode[] = nodes.map((node, i) => ({
      id: node.id,
      parentIndex: node.data.parent_index,
      // Use existing position or distribute in a line (for initial layout)
      x: node.position.x || opts.width / 2,
      y: node.position.y || i * 80 + 50,
    }));

    // Create force links
    const forceLinks: ForceLink[] = edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      edgeType: edge.label || 'default',
    }));

    // Create simulation
    const simulation: Simulation<ForceNode, ForceLink> = forceSimulation(forceNodes)
      // Repulsion between all nodes
      .force(
        'charge',
        forceManyBody<ForceNode>()
          .strength(opts.chargeStrength)
          .distanceMax(500) // Limit range of repulsion
      )
      // Spring forces for edges
      .force(
        'link',
        forceLink<ForceNode, ForceLink>(forceLinks)
          .id((d) => d.id)
          .distance((link) => {
            const edge = edges.find((e) => e.id === link.id);
            return edge ? getLinkDistance(edge) : opts.linkDistance;
          })
          .strength(0.7) // Strong-ish springs
      )
      // Center gravity
      .force(
        'center',
        forceCenter(opts.width / 2, opts.height / 2)
          .strength(opts.centerStrength)
      )
      // Prevent node overlap
      .force(
        'collision',
        forceCollide<ForceNode>()
          .radius(opts.collisionRadius)
          .strength(0.8)
      )
      // Vertical gravity to preserve rough order
      .force(
        'y',
        forceY<ForceNode>()
          .y((d) => {
            const node = nodes.find((n) => n.id === d.id);
            // For branching trails, use the depth (tree level) instead of step_index
            if (hasBranching && node) {
              // Count ancestors to determine depth
              let depth = 0;
              let current = node;
              while (current.data.parent_index !== null && current.data.parent_index !== undefined) {
                depth++;
                const parent = nodes.find((n) => n.data.step_index === current.data.parent_index);
                if (!parent) break;
                current = parent;
              }
              return depth * 120 + 100;
            }
            return node ? node.data.step_index * 100 + 100 : opts.height / 2;
          })
          .strength(hasBranching ? 0.15 : 0.05) // Stronger for branching to maintain tree shape
      );

    // Run simulation synchronously
    simulation.tick(opts.ticks);
    simulation.stop();

    // Update node positions
    const updatedNodes = nodes.map((node) => {
      const forceNode = forceNodes.find((fn) => fn.id === node.id);
      if (forceNode && forceNode.x !== undefined && forceNode.y !== undefined) {
        return {
          ...node,
          position: {
            x: forceNode.x,
            y: forceNode.y,
          },
        };
      }
      return node;
    });

    setLayoutNodes(updatedNodes);
    setIsSimulating(false);
  }, [nodes, edges, opts, getLinkDistance]);

  // Run simulation when inputs change (if animated)
  useEffect(() => {
    if (opts.animated || layoutNodes.length === 0) {
      runSimulation();
    }
  }, [nodes, edges, runSimulation, opts.animated, layoutNodes.length]);

  // Initial run
  useEffect(() => {
    runSimulation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    layoutNodes,
    isSimulating,
    runSimulation,
  };
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Apply hybrid layout: dagre for initial positions, d3-force for refinement.
 *
 * This is useful for larger trails where pure force layout might be chaotic.
 * Dagre provides a nice tree structure, force layout adds organic feel.
 *
 * Note: This is a future enhancement - requires dagre dependency.
 */
export function createHybridLayout(
  _nodes: TrailGraphNode[],
  _edges: TrailGraphEdge[],
  _options?: Partial<ForceLayoutOptions>
): TrailGraphNode[] {
  // TODO: Implement hybrid dagre + d3-force layout
  // Step 1: Apply dagre for initial hierarchical layout
  // Step 2: Refine with d3-force using weaker forces
  throw new Error('Hybrid layout not yet implemented - use useForceLayout');
}

// =============================================================================
// Exports
// =============================================================================

export default useForceLayout;
export { DEFAULT_OPTIONS, EDGE_DISTANCES };
