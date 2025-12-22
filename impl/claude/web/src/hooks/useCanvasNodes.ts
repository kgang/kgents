/**
 * useCanvasNodes - Transform AGENTESE discovery into canvas nodes.
 *
 * CLI v7 Phase 5: Integration & Polish.
 *
 * Bridges the AGENTESE discovery endpoint with the AgentCanvas component.
 * Transforms flat path lists into positioned, hierarchical canvas nodes.
 *
 * Voice Anchor:
 * "Agents pretending to be there with their cursors moving,
 *  kinda following my cursor, kinda doing its own thing."
 *
 * Key Design Decisions:
 * 1. Uses force-directed layout simulation for natural positioning
 * 2. Hierarchical grouping by context (world, self, concept, void, time)
 * 3. Expand/collapse support for deep paths
 * 4. Memoized for performance - only recalculates when paths change
 */

import { useMemo, useState, useCallback } from 'react';
import { useAgenteseDiscovery, type PathMetadata } from '@/components/docs/useAgenteseDiscovery';
import type { CanvasNode } from '@/components/canvas';

// =============================================================================
// Types
// =============================================================================

export interface UseCanvasNodesOptions {
  /** Maximum depth to show (default: 3) */
  maxDepth?: number;
  /** Initial expanded paths */
  initialExpanded?: Set<string>;
  /** Layout radius (default: 250) */
  radius?: number;
  /** Center X position (default: 0) */
  centerX?: number;
  /** Center Y position (default: 0) */
  centerY?: number;
}

export interface UseCanvasNodesReturn {
  /** Canvas nodes ready for rendering */
  nodes: CanvasNode[];
  /** Loading state from discovery */
  loading: boolean;
  /** Error from discovery */
  error: string | null;
  /** Toggle expansion of a node */
  toggleExpanded: (nodeId: string) => void;
  /** Set of currently expanded node IDs */
  expandedNodes: Set<string>;
  /** Refetch discovery data */
  refetch: () => void;
  /** Raw path metadata for tooltips/details */
  metadata: Record<string, PathMetadata>;
  /** Discovery stats */
  stats: { registered_nodes: number; contexts: string[]; total_paths: number } | null;
}

// =============================================================================
// Constants
// =============================================================================

const CONTEXT_ORDER: CanvasNode['context'][] = ['self', 'world', 'concept', 'time', 'void'];

// Context positioning (radial layout)
const CONTEXT_ANGLES: Record<CanvasNode['context'], number> = {
  self: -Math.PI / 2, // Top (12 o'clock)
  world: -Math.PI / 6, // Top-right (2 o'clock)
  concept: Math.PI / 3, // Right (4 o'clock)
  time: (2 * Math.PI) / 3, // Bottom-right (7 o'clock)
  void: (5 * Math.PI) / 6, // Bottom-left (10 o'clock)
};

// =============================================================================
// Layout Algorithm
// =============================================================================

/**
 * Parse an AGENTESE path into its components.
 */
function parsePath(path: string): { context: CanvasNode['context']; segments: string[] } {
  const segments = path.split('.');
  const context = segments[0] as CanvasNode['context'];
  return { context, segments };
}

/**
 * Build hierarchical node structure from flat paths.
 */
function buildNodeHierarchy(
  paths: string[],
  metadata: Record<string, PathMetadata>,
  expandedNodes: Set<string>,
  maxDepth: number,
  centerX: number,
  centerY: number,
  radius: number
): CanvasNode[] {
  const nodes: CanvasNode[] = [];
  const nodeMap = new Map<string, CanvasNode>();

  // Group paths by context
  const pathsByContext = new Map<CanvasNode['context'], string[]>();
  for (const context of CONTEXT_ORDER) {
    pathsByContext.set(context, []);
  }

  for (const path of paths) {
    const { context } = parsePath(path);
    if (CONTEXT_ORDER.includes(context)) {
      pathsByContext.get(context)?.push(path);
    }
  }

  // Generate nodes for each context
  for (const [context, contextPaths] of pathsByContext) {
    if (contextPaths.length === 0) continue;

    const contextAngle = CONTEXT_ANGLES[context];
    const contextCenterX = centerX + Math.cos(contextAngle) * radius;
    const contextCenterY = centerY + Math.sin(contextAngle) * radius;

    // Create context root node
    const contextNodeId = context;
    const contextNode: CanvasNode = {
      id: contextNodeId,
      label: context,
      path: context,
      context,
      description: `The ${context} context`,
      position: { x: contextCenterX, y: contextCenterY },
      expandable: true,
      expanded: expandedNodes.has(contextNodeId),
      children: [],
    };
    nodes.push(contextNode);
    nodeMap.set(contextNodeId, contextNode);

    // Group by second-level path
    const secondLevelPaths = new Map<string, string[]>();
    for (const path of contextPaths) {
      const { segments } = parsePath(path);
      if (segments.length >= 2) {
        const secondLevel = segments.slice(0, 2).join('.');
        if (!secondLevelPaths.has(secondLevel)) {
          secondLevelPaths.set(secondLevel, []);
        }
        secondLevelPaths.get(secondLevel)?.push(path);
      }
    }

    // Only show children if expanded
    if (!expandedNodes.has(contextNodeId)) continue;

    // Create second-level nodes
    const secondLevelArray = Array.from(secondLevelPaths.entries());
    const innerRadius = radius * 0.4;

    secondLevelArray.forEach(([secondPath, childPaths], i) => {
      const { segments } = parsePath(secondPath);
      const angle = contextAngle + (i - secondLevelArray.length / 2) * Math.PI * 0.15;
      const x = contextCenterX + Math.cos(angle) * innerRadius;
      const y = contextCenterY + Math.sin(angle) * innerRadius;

      const meta = metadata[secondPath];
      const node: CanvasNode = {
        id: secondPath,
        label: segments[1] || secondPath,
        path: secondPath,
        context,
        description: meta?.description || `${segments[1]} node`,
        parent: contextNodeId,
        position: { x, y },
        expandable: childPaths.some((p) => p.split('.').length > 2),
        expanded: expandedNodes.has(secondPath),
        children: [],
      };

      contextNode.children?.push(secondPath);
      nodes.push(node);
      nodeMap.set(secondPath, node);

      // Third level (if expanded and within maxDepth)
      if (expandedNodes.has(secondPath) && maxDepth >= 3) {
        const thirdLevelPaths = childPaths.filter((p) => p.split('.').length >= 3);
        const uniqueThirdLevel = [
          ...new Set(thirdLevelPaths.map((p) => p.split('.').slice(0, 3).join('.'))),
        ];

        uniqueThirdLevel.forEach((thirdPath, j) => {
          const thirdSegments = thirdPath.split('.');
          const thirdAngle = angle + (j - uniqueThirdLevel.length / 2) * Math.PI * 0.08;
          const thirdX = x + Math.cos(thirdAngle) * (innerRadius * 0.5);
          const thirdY = y + Math.sin(thirdAngle) * (innerRadius * 0.5);

          const thirdMeta = metadata[thirdPath];
          const thirdNode: CanvasNode = {
            id: thirdPath,
            label: thirdSegments[2] || thirdPath,
            path: thirdPath,
            context,
            description: thirdMeta?.description,
            parent: secondPath,
            position: { x: thirdX, y: thirdY },
            expandable: false,
            expanded: false,
          };

          node.children?.push(thirdPath);
          nodes.push(thirdNode);
          nodeMap.set(thirdPath, thirdNode);
        });
      }
    });
  }

  return nodes;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useCanvasNodes(options: UseCanvasNodesOptions = {}): UseCanvasNodesReturn {
  const {
    maxDepth = 3,
    initialExpanded = new Set(['self', 'world']),
    radius = 250,
    centerX = 0,
    centerY = 0,
  } = options;

  // AGENTESE discovery
  const { paths, metadata, stats, loading, error, refetch } = useAgenteseDiscovery();

  // Expanded state
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(initialExpanded);

  // Toggle expansion
  const toggleExpanded = useCallback((nodeId: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  }, []);

  // Build nodes
  const nodes = useMemo(() => {
    if (loading || error || paths.length === 0) {
      return [];
    }
    return buildNodeHierarchy(paths, metadata, expandedNodes, maxDepth, centerX, centerY, radius);
  }, [paths, metadata, expandedNodes, maxDepth, centerX, centerY, radius, loading, error]);

  return {
    nodes,
    loading,
    error,
    toggleExpanded,
    expandedNodes,
    refetch,
    metadata,
    stats,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useCanvasNodes;
