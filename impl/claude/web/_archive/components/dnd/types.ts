/**
 * DnD System Types: Data types for drag-and-drop interactions.
 *
 * These types define the contract between draggable items and drop zones,
 * enabling type-safe composition of agents into pipelines.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import type { CitizenCardJSON } from '@/reactive/types';

// =============================================================================
// Drag Data
// =============================================================================

/**
 * Types of items that can be dragged in the system.
 */
export type DragItemType = 'agent' | 'pipeline-node' | 'widget' | 'archetype';

/**
 * Data attached to a draggable item.
 */
export interface DragData<T = unknown> {
  /** Type of dragged item */
  type: DragItemType;

  /** Unique identifier */
  id: string;

  /** Zone from which the item was dragged */
  sourceZone: string;

  /** Item-specific payload */
  payload: T;
}

/**
 * Specialized drag data for agent items.
 */
export interface AgentDragData extends DragData<CitizenCardJSON> {
  type: 'agent';
}

/**
 * Specialized drag data for pipeline nodes.
 */
export interface PipelineNodeDragData extends DragData<PipelineNodeData> {
  type: 'pipeline-node';
}

// =============================================================================
// Drop Zones
// =============================================================================

/**
 * Configuration for a drop zone.
 */
export interface DropZoneConfig {
  /** Unique identifier for this drop zone */
  id: string;

  /** Types of items this zone accepts */
  accepts: DragItemType[];

  /** Maximum items allowed (-1 = unlimited) */
  maxItems?: number;

  /** Whether the zone is currently accepting drops */
  isActive?: boolean;
}

/**
 * Result of a drop operation.
 */
export interface DropResult {
  /** Whether the drop was successful */
  success: boolean;

  /** The zone where the item was dropped */
  zoneId: string;

  /** Error message if drop failed */
  error?: string;
}

// =============================================================================
// Pipeline Data Model
// =============================================================================

/**
 * A node in the pipeline canvas.
 */
export interface PipelineNodeData {
  /** Unique node identifier */
  id: string;

  /** Node type determines rendering and behavior */
  type: 'agent' | 'operation' | 'input' | 'output';

  /** Position on canvas (pixels) */
  position: { x: number; y: number };

  /** Node-specific data (e.g., agent config) */
  data: unknown;

  /** Input/output ports for connections */
  ports: {
    inputs: Port[];
    outputs: Port[];
  };
}

/**
 * A port on a pipeline node (connection point).
 */
export interface Port {
  /** Unique port identifier */
  id: string;

  /** Display label */
  label: string;

  /** Type hint for validation (e.g., 'agent', 'data', 'any') */
  type: string;

  /** ID of connected port, if any */
  connected?: string;
}

/**
 * An edge connecting two nodes.
 */
export interface PipelineEdge {
  /** Unique edge identifier */
  id: string;

  /** Source connection */
  source: {
    nodeId: string;
    portId: string;
  };

  /** Target connection */
  target: {
    nodeId: string;
    portId: string;
  };
}

/**
 * Complete pipeline definition.
 */
export interface Pipeline {
  /** Unique pipeline identifier */
  id: string;

  /** Human-readable name */
  name: string;

  /** Nodes in the pipeline */
  nodes: PipelineNodeData[];

  /** Edges connecting nodes */
  edges: PipelineEdge[];

  /** Metadata */
  meta?: {
    createdAt: Date;
    updatedAt: Date;
    description?: string;
  };
}

// =============================================================================
// Type Guards
// =============================================================================

/**
 * Check if drag data is for an agent.
 */
export function isAgentDragData(data: DragData): data is AgentDragData {
  return data.type === 'agent';
}

/**
 * Check if drag data is for a pipeline node.
 */
export function isPipelineNodeDragData(data: DragData): data is PipelineNodeDragData {
  return data.type === 'pipeline-node';
}
