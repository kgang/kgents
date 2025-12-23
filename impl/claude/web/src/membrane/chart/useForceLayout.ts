/**
 * useForceLayout — Force-directed graph layout
 *
 * Uses d3-force for physics simulation:
 * - Harmonies as springs (attract related specs)
 * - Charge repulsion (separate overlapping specs)
 * - Orphans get stronger repulsion (pushed to periphery)
 *
 * "The file is a lie. There is only the graph."
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCenter,
  forceCollide,
  type Simulation,
  type SimulationNodeDatum,
  type SimulationLinkDatum,
} from 'd3-force';
import type { StarData, ConnectionData } from './useAstronomicalData';

// =============================================================================
// Types
// =============================================================================

/** Node with force simulation properties */
export interface ForceNode extends SimulationNodeDatum {
  id: string;
  tier: number;
  status: string;
  radius: number;
  // Original data
  data: StarData;
}

/** Link with force simulation properties */
export interface ForceLink extends SimulationLinkDatum<ForceNode> {
  source: string | ForceNode;
  target: string | ForceNode;
  strength: number;
  relationship: string;
}

export interface ForceLayoutOptions {
  /** Width of the layout area */
  width: number;
  /** Height of the layout area */
  height: number;
  /** Initial alpha (simulation temperature) */
  alpha?: number;
  /** Alpha decay rate */
  alphaDecay?: number;
  /** Velocity decay (friction) */
  velocityDecay?: number;
  /** Whether to run simulation on mount */
  autoStart?: boolean;
}

export interface ForceLayoutReturn {
  /** Current positioned nodes */
  nodes: StarData[];
  /** Whether simulation is running */
  isSimulating: boolean;
  /** Manually tick the simulation */
  tick: () => void;
  /** Restart the simulation */
  restart: (alpha?: number) => void;
  /** Stop the simulation */
  stop: () => void;
  /** Fix a node position (user dragged) */
  fixNode: (id: string, x: number, y: number) => void;
  /** Unfix a node position */
  unfixNode: (id: string) => void;
}

// =============================================================================
// Constants
// =============================================================================

/** Base charge strength (repulsion) */
const BASE_CHARGE = -100;

/** Orphan charge multiplier (push to periphery) */
const ORPHAN_CHARGE_MULTIPLIER = 2.5;

/** Link strength base */
const LINK_STRENGTH_BASE = 0.3;

/** Collision radius padding */
const COLLISION_PADDING = 8;

// =============================================================================
// Hook
// =============================================================================

export function useForceLayout(
  stars: StarData[],
  connections: ConnectionData[],
  options: ForceLayoutOptions
): ForceLayoutReturn {
  const {
    // width and height reserved for future viewport-aware layout
    alpha = 1,
    alphaDecay = 0.02,
    velocityDecay = 0.4,
    autoStart = true,
  } = options;

  // Refs
  const simulationRef = useRef<Simulation<ForceNode, ForceLink> | null>(null);
  const nodesRef = useRef<ForceNode[]>([]);

  // State
  const [positionedNodes, setPositionedNodes] = useState<StarData[]>(stars);
  const [isSimulating, setIsSimulating] = useState(false);

  // Initialize force nodes from stars
  const initializeNodes = useCallback((): ForceNode[] => {
    return stars.map((star) => {
      // Calculate initial position in tier rings
      const tierStars = stars.filter((s) => s.tier === star.tier);
      const index = tierStars.findIndex((s) => s.id === star.id);
      const ringRadius = 100 + star.tier * 120;
      const angle = (index / tierStars.length) * 2 * Math.PI - Math.PI / 2;

      return {
        id: star.id,
        tier: star.tier,
        status: star.status,
        radius: star.radius,
        // Initial position on tier ring
        x: Math.cos(angle) * ringRadius,
        y: Math.sin(angle) * ringRadius,
        // Original data reference
        data: star,
      };
    });
  }, [stars]);

  // Initialize force links from connections
  const initializeLinks = useCallback((): ForceLink[] => {
    const nodeIds = new Set(stars.map((s) => s.id));

    return connections
      .filter((c) => nodeIds.has(c.source) && nodeIds.has(c.target))
      .map((conn) => ({
        source: conn.source,
        target: conn.target,
        strength: conn.strength,
        relationship: conn.relationship,
      }));
  }, [stars, connections]);

  // Calculate charge strength based on node properties
  const chargeStrength = useCallback((node: ForceNode) => {
    // Orphans get pushed to periphery
    if (node.status === 'ORPHAN') {
      return BASE_CHARGE * ORPHAN_CHARGE_MULTIPLIER;
    }
    // Larger nodes (more evidence) have stronger presence
    return BASE_CHARGE * (1 + node.radius / 10);
  }, []);

  // Calculate link strength based on relationship
  const linkStrength = useCallback((link: ForceLink) => {
    return LINK_STRENGTH_BASE * link.strength;
  }, []);

  // Update positioned nodes from simulation
  const updatePositions = useCallback(() => {
    const nodes = nodesRef.current;
    if (nodes.length === 0) return;

    setPositionedNodes(
      nodes.map((node) => ({
        ...node.data,
        x: node.x ?? 0,
        y: node.y ?? 0,
      }))
    );
  }, []);

  // Initialize simulation
  useEffect(() => {
    if (stars.length === 0) {
      setPositionedNodes([]);
      return;
    }

    // Initialize nodes and links
    const nodes = initializeNodes();
    const links = initializeLinks();
    nodesRef.current = nodes;

    // Create simulation
    const simulation = forceSimulation<ForceNode>(nodes)
      .force(
        'link',
        forceLink<ForceNode, ForceLink>(links)
          .id((d) => d.id)
          .strength(linkStrength)
          .distance(100)
      )
      .force('charge', forceManyBody<ForceNode>().strength(chargeStrength))
      .force('center', forceCenter(0, 0))
      .force(
        'collide',
        forceCollide<ForceNode>((d) => d.radius + COLLISION_PADDING)
      )
      .alpha(alpha)
      .alphaDecay(alphaDecay)
      .velocityDecay(velocityDecay);

    // Handle tick events
    simulation.on('tick', () => {
      updatePositions();
    });

    // Handle simulation end
    simulation.on('end', () => {
      setIsSimulating(false);
      updatePositions();
    });

    simulationRef.current = simulation;

    if (autoStart) {
      setIsSimulating(true);
    } else {
      simulation.stop();
    }

    // Cleanup
    return () => {
      simulation.stop();
      simulationRef.current = null;
    };
  }, [
    stars,
    connections,
    initializeNodes,
    initializeLinks,
    chargeStrength,
    linkStrength,
    updatePositions,
    alpha,
    alphaDecay,
    velocityDecay,
    autoStart,
  ]);

  // Manual tick
  const tick = useCallback(() => {
    const simulation = simulationRef.current;
    if (simulation) {
      simulation.tick();
      updatePositions();
    }
  }, [updatePositions]);

  // Restart simulation
  const restart = useCallback((newAlpha: number = 0.3) => {
    const simulation = simulationRef.current;
    if (simulation) {
      simulation.alpha(newAlpha).restart();
      setIsSimulating(true);
    }
  }, []);

  // Stop simulation
  const stop = useCallback(() => {
    const simulation = simulationRef.current;
    if (simulation) {
      simulation.stop();
      setIsSimulating(false);
    }
  }, []);

  // Fix node position (user dragged)
  const fixNode = useCallback(
    (id: string, x: number, y: number) => {
      const node = nodesRef.current.find((n) => n.id === id);
      if (node) {
        node.fx = x;
        node.fy = y;
        updatePositions();
      }
    },
    [updatePositions]
  );

  // Unfix node position
  const unfixNode = useCallback((id: string) => {
    const node = nodesRef.current.find((n) => n.id === id);
    if (node) {
      node.fx = null;
      node.fy = null;
    }
  }, []);

  return {
    nodes: positionedNodes,
    isSimulating,
    tick,
    restart,
    stop,
    fixNode,
    unfixNode,
  };
}

export default useForceLayout;
