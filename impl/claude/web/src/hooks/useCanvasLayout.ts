/**
 * useCanvasLayout - Force-directed layout with draggable nodes.
 *
 * CLI v7 Phase 5: Collaborative Canvas.
 *
 * Provides:
 * - Force-directed layout that spreads nodes to avoid overlap
 * - Draggable nodes (local session state only)
 * - Smooth animation between layout changes
 * - Hierarchical grouping by AGENTESE context
 *
 * Voice Anchor:
 * "Opening one concept shouldn't result in severe overlap."
 */

import { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import type { CanvasNode } from '@/components/canvas/AgentCanvas';

// =============================================================================
// Types
// =============================================================================

export interface LayoutOptions {
  /** Center X position */
  centerX?: number;
  /** Center Y position */
  centerY?: number;
  /** Base radius for context groups */
  radius?: number;
  /** Minimum distance between nodes */
  nodeSpacing?: number;
  /** Force simulation iterations */
  iterations?: number;
  /** Whether to animate position changes */
  animated?: boolean;
}

export interface DragState {
  /** Node being dragged */
  nodeId: string | null;
  /** Starting position */
  startPos: { x: number; y: number } | null;
  /** Current offset */
  offset: { x: number; y: number };
}

export interface UseCanvasLayoutReturn {
  /** Computed node positions (with drag offsets applied) */
  positions: Map<string, { x: number; y: number }>;
  /** Start dragging a node */
  startDrag: (nodeId: string, clientX: number, clientY: number) => void;
  /** Update drag position */
  updateDrag: (clientX: number, clientY: number) => void;
  /** End dragging */
  endDrag: () => void;
  /** Is a node being dragged? */
  isDragging: boolean;
  /** Which node is being dragged */
  draggedNodeId: string | null;
  /** Reset all custom positions */
  resetPositions: () => void;
  /** Recalculate layout */
  recalculateLayout: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_OPTIONS: Required<LayoutOptions> = {
  centerX: 0,
  centerY: 0,
  radius: 250,
  nodeSpacing: 120,
  iterations: 50,
  animated: true,
};

// Context angle offsets (evenly distributed around circle)
const CONTEXT_ANGLES: Record<string, number> = {
  self: -Math.PI / 2, // Top
  world: Math.PI / 6, // Top-right
  concept: (5 * Math.PI) / 6, // Top-left
  time: -Math.PI / 6, // Bottom-right
  void: (7 * Math.PI) / 6, // Bottom-left
};

// =============================================================================
// Layout Algorithm
// =============================================================================

interface NodePosition {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

/**
 * Apply force-directed layout simulation.
 * Uses simple spring/repulsion model.
 */
function applyForceLayout(
  nodes: CanvasNode[],
  options: Required<LayoutOptions>
): Map<string, { x: number; y: number }> {
  const { centerX, centerY, radius, nodeSpacing, iterations } = options;

  // Initialize positions
  const positions = new Map<string, NodePosition>();

  // Group nodes by context for initial positioning
  const byContext = new Map<string, CanvasNode[]>();
  nodes.forEach((node) => {
    const existing = byContext.get(node.context) || [];
    byContext.set(node.context, [...existing, node]);
  });

  // Initial radial layout with better spacing
  byContext.forEach((contextNodes, context) => {
    const baseAngle = CONTEXT_ANGLES[context] ?? 0;
    const contextRadius = radius * 0.8;

    // Sort by path depth so parents come first
    const sorted = [...contextNodes].sort(
      (a, b) => a.path.split('.').length - b.path.split('.').length
    );

    sorted.forEach((node, i) => {
      const depth = node.path.split('.').length;
      const angleSpread = Math.min(Math.PI * 0.4, (contextNodes.length * 0.15));
      const nodeAngle = baseAngle + (i / Math.max(1, contextNodes.length - 1) - 0.5) * angleSpread;
      const nodeRadius = contextRadius + (depth - 1) * nodeSpacing * 0.6;

      positions.set(node.id, {
        x: centerX + Math.cos(nodeAngle) * nodeRadius,
        y: centerY + Math.sin(nodeAngle) * nodeRadius,
        vx: 0,
        vy: 0,
      });
    });
  });

  // Force simulation
  const nodeList = Array.from(positions.entries());
  const alpha = 0.3; // Damping
  const repulsionStrength = nodeSpacing * nodeSpacing * 2;
  const attractionStrength = 0.01;

  for (let iter = 0; iter < iterations; iter++) {
    // Apply repulsion between all pairs
    for (let i = 0; i < nodeList.length; i++) {
      for (let j = i + 1; j < nodeList.length; j++) {
        const [, posA] = nodeList[i];
        const [, posB] = nodeList[j];

        const dx = posB.x - posA.x;
        const dy = posB.y - posA.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;

        if (dist < nodeSpacing * 1.5) {
          // Repel if too close
          const force = repulsionStrength / (dist * dist);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;

          posA.vx -= fx;
          posA.vy -= fy;
          posB.vx += fx;
          posB.vy += fy;
        }
      }
    }

    // Apply attraction to parent
    nodes.forEach((node) => {
      if (node.parent) {
        const childPos = positions.get(node.id);
        const parentPos = positions.get(node.parent);

        if (childPos && parentPos) {
          const dx = parentPos.x - childPos.x;
          const dy = parentPos.y - childPos.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;

          // Target distance based on hierarchy
          const targetDist = nodeSpacing * 0.8;
          const force = (dist - targetDist) * attractionStrength;

          childPos.vx += (dx / dist) * force;
          childPos.vy += (dy / dist) * force;
        }
      }
    });

    // Apply center gravity (weak)
    nodeList.forEach(([, pos]) => {
      const dx = centerX - pos.x;
      const dy = centerY - pos.y;
      pos.vx += dx * 0.001;
      pos.vy += dy * 0.001;
    });

    // Apply velocities and damping
    nodeList.forEach(([, pos]) => {
      pos.x += pos.vx * alpha;
      pos.y += pos.vy * alpha;
      pos.vx *= 0.9;
      pos.vy *= 0.9;
    });
  }

  // Return final positions
  const result = new Map<string, { x: number; y: number }>();
  nodeList.forEach(([id, pos]) => {
    result.set(id, { x: pos.x, y: pos.y });
  });

  return result;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useCanvasLayout(
  nodes: CanvasNode[],
  options: LayoutOptions = {}
): UseCanvasLayoutReturn {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  // Computed layout positions
  const [layoutPositions, setLayoutPositions] = useState<Map<string, { x: number; y: number }>>(
    () => new Map()
  );

  // User-dragged offsets (persisted for session)
  const [dragOffsets, setDragOffsets] = useState<Map<string, { x: number; y: number }>>(
    () => new Map()
  );

  // Current drag state
  const [dragState, setDragState] = useState<DragState>({
    nodeId: null,
    startPos: null,
    offset: { x: 0, y: 0 },
  });

  // Ref to track last processed node set
  const lastNodesRef = useRef<string>('');

  // Calculate layout when nodes change
  useEffect(() => {
    const nodeKey = nodes.map((n) => n.id).sort().join(',');

    // Only recalculate if nodes actually changed
    if (nodeKey !== lastNodesRef.current) {
      lastNodesRef.current = nodeKey;

      // Apply force-directed layout
      const newPositions = applyForceLayout(nodes, opts);
      setLayoutPositions(newPositions);
    }
  }, [nodes, opts.centerX, opts.centerY, opts.radius, opts.nodeSpacing, opts.iterations]);

  // Combined positions (layout + drag offsets)
  const positions = useMemo(() => {
    const result = new Map<string, { x: number; y: number }>();

    layoutPositions.forEach((pos, id) => {
      const offset = dragOffsets.get(id) || { x: 0, y: 0 };
      const activeDragOffset =
        dragState.nodeId === id ? dragState.offset : { x: 0, y: 0 };

      result.set(id, {
        x: pos.x + offset.x + activeDragOffset.x,
        y: pos.y + offset.y + activeDragOffset.y,
      });
    });

    return result;
  }, [layoutPositions, dragOffsets, dragState]);

  // Start dragging a node
  const startDrag = useCallback((nodeId: string, clientX: number, clientY: number) => {
    setDragState({
      nodeId,
      startPos: { x: clientX, y: clientY },
      offset: { x: 0, y: 0 },
    });
  }, []);

  // Update drag position
  const updateDrag = useCallback((clientX: number, clientY: number) => {
    setDragState((prev) => {
      if (!prev.nodeId || !prev.startPos) return prev;

      return {
        ...prev,
        offset: {
          x: clientX - prev.startPos.x,
          y: clientY - prev.startPos.y,
        },
      };
    });
  }, []);

  // End dragging - commit offset
  const endDrag = useCallback(() => {
    setDragState((prev) => {
      if (prev.nodeId && (prev.offset.x !== 0 || prev.offset.y !== 0)) {
        // Commit the drag offset
        setDragOffsets((offsets) => {
          const newOffsets = new Map(offsets);
          const existing = newOffsets.get(prev.nodeId!) || { x: 0, y: 0 };
          newOffsets.set(prev.nodeId!, {
            x: existing.x + prev.offset.x,
            y: existing.y + prev.offset.y,
          });
          return newOffsets;
        });
      }

      return {
        nodeId: null,
        startPos: null,
        offset: { x: 0, y: 0 },
      };
    });
  }, []);

  // Reset all custom positions
  const resetPositions = useCallback(() => {
    setDragOffsets(new Map());
  }, []);

  // Force recalculation
  const recalculateLayout = useCallback(() => {
    lastNodesRef.current = '';
    const newPositions = applyForceLayout(nodes, opts);
    setLayoutPositions(newPositions);
    setDragOffsets(new Map());
  }, [nodes, opts]);

  return {
    positions,
    startDrag,
    updateDrag,
    endDrag,
    isDragging: dragState.nodeId !== null,
    draggedNodeId: dragState.nodeId,
    resetPositions,
    recalculateLayout,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useCanvasLayout;
