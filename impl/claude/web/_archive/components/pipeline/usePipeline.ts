/**
 * usePipeline: State management for pipeline editing.
 *
 * Manages the pipeline state including nodes, edges, selection, and
 * history (undo/redo). Provides actions for all pipeline operations.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { useState, useCallback } from 'react';
import type { Pipeline, PipelineNodeData, PipelineEdge, DragData } from '@/components/dnd';
import { isAgentDragData } from '@/components/dnd';
import type { CitizenCardJSON } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export interface PipelineState {
  /** Current pipeline */
  pipeline: Pipeline;

  /** Currently selected node IDs */
  selectedNodes: Set<string>;

  /** Currently selected edge IDs */
  selectedEdges: Set<string>;

  /** Whether the pipeline has unsaved changes */
  isDirty: boolean;

  /** Undo/redo history */
  history: {
    past: Pipeline[];
    future: Pipeline[];
  };
}

export interface PipelineActions {
  // Node operations
  addNode: (node: Omit<PipelineNodeData, 'id'>) => string;
  updateNode: (id: string, updates: Partial<PipelineNodeData>) => void;
  removeNode: (id: string) => void;
  moveNode: (id: string, position: { x: number; y: number }) => void;

  // Edge operations
  addEdge: (edge: Omit<PipelineEdge, 'id'>) => string;
  removeEdge: (id: string) => void;

  // Selection
  selectNode: (id: string, addToSelection?: boolean) => void;
  selectEdge: (id: string, addToSelection?: boolean) => void;
  clearSelection: () => void;

  // History
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;

  // Pipeline operations
  reset: () => void;
  load: (pipeline: Pipeline) => void;
  validate: () => ValidationResult;

  // Drag-drop integration
  handleDrop: (data: DragData, position: { x: number; y: number }) => void;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

export interface ValidationError {
  type: 'disconnected' | 'cycle' | 'invalid_connection' | 'missing_input' | 'missing_output';
  nodeId?: string;
  edgeId?: string;
  message: string;
}

// =============================================================================
// Hook
// =============================================================================

export function usePipeline(initialPipeline?: Pipeline): PipelineState & PipelineActions {
  // Initialize state
  const [state, setState] = useState<PipelineState>(() => ({
    pipeline: initialPipeline || createEmptyPipeline(),
    selectedNodes: new Set(),
    selectedEdges: new Set(),
    isDirty: false,
    history: {
      past: [],
      future: [],
    },
  }));

  // Save to history before mutation
  const saveHistory = useCallback(() => {
    setState((prev) => ({
      ...prev,
      history: {
        past: [...prev.history.past.slice(-50), prev.pipeline],
        future: [],
      },
      isDirty: true,
    }));
  }, []);

  // Generate unique ID
  const generateId = useCallback(() => {
    return `node_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
  }, []);

  // ==========================================================================
  // Node Operations
  // ==========================================================================

  const addNode = useCallback(
    (node: Omit<PipelineNodeData, 'id'>): string => {
      const id = generateId();
      saveHistory();
      setState((prev) => ({
        ...prev,
        pipeline: {
          ...prev.pipeline,
          nodes: [...prev.pipeline.nodes, { ...node, id }],
        },
      }));
      return id;
    },
    [generateId, saveHistory]
  );

  const updateNode = useCallback(
    (id: string, updates: Partial<PipelineNodeData>) => {
      saveHistory();
      setState((prev) => ({
        ...prev,
        pipeline: {
          ...prev.pipeline,
          nodes: prev.pipeline.nodes.map((n) => (n.id === id ? { ...n, ...updates } : n)),
        },
      }));
    },
    [saveHistory]
  );

  const removeNode = useCallback(
    (id: string) => {
      saveHistory();
      setState((prev) => ({
        ...prev,
        pipeline: {
          ...prev.pipeline,
          // Remove the node
          nodes: prev.pipeline.nodes.filter((n) => n.id !== id),
          // Remove connected edges
          edges: prev.pipeline.edges.filter((e) => e.source.nodeId !== id && e.target.nodeId !== id),
        },
        selectedNodes: new Set([...prev.selectedNodes].filter((nid) => nid !== id)),
      }));
    },
    [saveHistory]
  );

  const moveNode = useCallback(
    (id: string, position: { x: number; y: number }) => {
      // Don't save history for every move (would flood history)
      setState((prev) => ({
        ...prev,
        pipeline: {
          ...prev.pipeline,
          nodes: prev.pipeline.nodes.map((n) => (n.id === id ? { ...n, position } : n)),
        },
        isDirty: true,
      }));
    },
    []
  );

  // ==========================================================================
  // Edge Operations
  // ==========================================================================

  const addEdge = useCallback(
    (edge: Omit<PipelineEdge, 'id'>): string => {
      const id = `edge_${Date.now()}`;
      saveHistory();
      setState((prev) => ({
        ...prev,
        pipeline: {
          ...prev.pipeline,
          edges: [...prev.pipeline.edges, { ...edge, id }],
        },
      }));
      return id;
    },
    [saveHistory]
  );

  const removeEdge = useCallback(
    (id: string) => {
      saveHistory();
      setState((prev) => ({
        ...prev,
        pipeline: {
          ...prev.pipeline,
          edges: prev.pipeline.edges.filter((e) => e.id !== id),
        },
        selectedEdges: new Set([...prev.selectedEdges].filter((eid) => eid !== id)),
      }));
    },
    [saveHistory]
  );

  // ==========================================================================
  // Selection
  // ==========================================================================

  const selectNode = useCallback((id: string, addToSelection = false) => {
    setState((prev) => ({
      ...prev,
      selectedNodes: addToSelection
        ? new Set([...prev.selectedNodes, id])
        : new Set([id]),
      selectedEdges: addToSelection ? prev.selectedEdges : new Set(),
    }));
  }, []);

  const selectEdge = useCallback((id: string, addToSelection = false) => {
    setState((prev) => ({
      ...prev,
      selectedEdges: addToSelection
        ? new Set([...prev.selectedEdges, id])
        : new Set([id]),
      selectedNodes: addToSelection ? prev.selectedNodes : new Set(),
    }));
  }, []);

  const clearSelection = useCallback(() => {
    setState((prev) => ({
      ...prev,
      selectedNodes: new Set(),
      selectedEdges: new Set(),
    }));
  }, []);

  // ==========================================================================
  // History
  // ==========================================================================

  const canUndo = state.history.past.length > 0;
  const canRedo = state.history.future.length > 0;

  const undo = useCallback(() => {
    setState((prev) => {
      if (prev.history.past.length === 0) return prev;

      const newPast = [...prev.history.past];
      const previous = newPast.pop()!;

      return {
        ...prev,
        pipeline: previous,
        history: {
          past: newPast,
          future: [prev.pipeline, ...prev.history.future],
        },
      };
    });
  }, []);

  const redo = useCallback(() => {
    setState((prev) => {
      if (prev.history.future.length === 0) return prev;

      const [next, ...newFuture] = prev.history.future;

      return {
        ...prev,
        pipeline: next,
        history: {
          past: [...prev.history.past, prev.pipeline],
          future: newFuture,
        },
      };
    });
  }, []);

  // ==========================================================================
  // Pipeline Operations
  // ==========================================================================

  const reset = useCallback(() => {
    saveHistory();
    setState((prev) => ({
      ...prev,
      pipeline: createEmptyPipeline(),
      selectedNodes: new Set(),
      selectedEdges: new Set(),
    }));
  }, [saveHistory]);

  const load = useCallback((pipeline: Pipeline) => {
    setState((prev) => ({
      ...prev,
      pipeline,
      selectedNodes: new Set(),
      selectedEdges: new Set(),
      isDirty: false,
      history: { past: [], future: [] },
    }));
  }, []);

  const validate = useCallback((): ValidationResult => {
    const errors: ValidationError[] = [];
    const { nodes, edges } = state.pipeline;

    // Check for disconnected nodes (no inputs or outputs)
    for (const node of nodes) {
      const hasIncoming = edges.some((e) => e.target.nodeId === node.id);
      const hasOutgoing = edges.some((e) => e.source.nodeId === node.id);

      if (node.type !== 'input' && !hasIncoming) {
        errors.push({
          type: 'disconnected',
          nodeId: node.id,
          message: `Node "${node.id}" has no incoming connections`,
        });
      }

      if (node.type !== 'output' && !hasOutgoing) {
        errors.push({
          type: 'disconnected',
          nodeId: node.id,
          message: `Node "${node.id}" has no outgoing connections`,
        });
      }
    }

    // Check for missing input node
    if (!nodes.some((n) => n.type === 'input')) {
      errors.push({
        type: 'missing_input',
        message: 'Pipeline has no input node',
      });
    }

    // Check for missing output node
    if (!nodes.some((n) => n.type === 'output')) {
      errors.push({
        type: 'missing_output',
        message: 'Pipeline has no output node',
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }, [state.pipeline]);

  // ==========================================================================
  // Drag-Drop Integration
  // ==========================================================================

  const handleDrop = useCallback(
    (data: DragData, position: { x: number; y: number }) => {
      if (isAgentDragData(data)) {
        const citizen = data.payload as CitizenCardJSON;
        addNode({
          type: 'agent',
          position,
          data: citizen,
          ports: {
            inputs: [{ id: `${citizen.citizen_id}_in`, label: 'Input', type: 'any' }],
            outputs: [{ id: `${citizen.citizen_id}_out`, label: 'Output', type: 'any' }],
          },
        });
      }
    },
    [addNode]
  );

  // ==========================================================================
  // Return
  // ==========================================================================

  return {
    ...state,
    addNode,
    updateNode,
    removeNode,
    moveNode,
    addEdge,
    removeEdge,
    selectNode,
    selectEdge,
    clearSelection,
    undo,
    redo,
    canUndo,
    canRedo,
    reset,
    load,
    validate,
    handleDrop,
  };
}

// =============================================================================
// Helpers
// =============================================================================

function createEmptyPipeline(): Pipeline {
  return {
    id: `pipeline_${Date.now()}`,
    name: 'New Pipeline',
    nodes: [],
    edges: [],
    meta: {
      createdAt: new Date(),
      updatedAt: new Date(),
    },
  };
}

export default usePipeline;
