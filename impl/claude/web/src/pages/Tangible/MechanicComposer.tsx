/**
 * MechanicComposer - Visual operad editor for mechanic composition
 *
 * "Composition is not combination. It's the emergence of new possibility."
 *
 * Center panel in Create Mode. Features:
 * - Drag-and-drop mechanic blocks
 * - Visual composition graph
 * - Operations: Sequential (>>), Parallel (||), Conditional (?:), Feedback (loop)
 * - Live Galois loss preview
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useReducer, useCallback, useRef } from 'react';
import {
  GitBranch,
  Plus,
  Trash2,
  ArrowRight,
  Split,
  HelpCircle,
  RotateCcw,
  MousePointer,
  Link,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import type {
  MechanicComposition,
  CompositionNode,
  CompositionEdge,
  Mechanic,
  ComposerState,
  ComposerAction,
  GameOperad,
} from './types';

// =============================================================================
// Types
// =============================================================================

export interface MechanicComposerProps {
  /** Available mechanics to compose */
  mechanics: Mechanic[];
  /** Current composition being edited */
  composition?: MechanicComposition | null;
  /** The operad defining valid operations */
  operad: GameOperad;
  /** Called when composition is updated */
  onCompose: (result: MechanicComposition) => void;
  /** Called when composition is cleared */
  onClear?: () => void;
}

// =============================================================================
// Reducer
// =============================================================================

function createInitialState(
  mechanics: Mechanic[],
  composition: MechanicComposition | null | undefined
): ComposerState {
  return {
    selectedNodeId: null,
    draggingNodeIds: [],
    composition: composition || null,
    mechanicsLibrary: mechanics,
    zoom: 1,
    pan: { x: 0, y: 0 },
    mode: 'select',
  };
}

function composerReducer(state: ComposerState, action: ComposerAction): ComposerState {
  switch (action.type) {
    case 'SELECT_NODE':
      return { ...state, selectedNodeId: action.nodeId };

    case 'START_DRAG':
      return { ...state, draggingNodeIds: action.nodeIds };

    case 'END_DRAG':
      return { ...state, draggingNodeIds: [] };

    case 'MOVE_NODE': {
      if (!state.composition) return state;
      const nodes = state.composition.nodes.map((node) =>
        node.id === action.nodeId ? { ...node, position: action.position } : node
      );
      return {
        ...state,
        composition: { ...state.composition, nodes },
      };
    }

    case 'ADD_NODE': {
      if (!state.composition) {
        // Create new composition
        return {
          ...state,
          composition: {
            id: `comp-${Date.now()}`,
            name: 'New Composition',
            verbs: [],
            tells: [],
            inputType: 'void',
            outputType: 'void',
            contrastPoles: ['', ''],
            galoisLoss: 0,
            nodes: [action.node],
            edges: [],
            sourceMechanics: action.node.mechanicId ? [action.node.mechanicId] : [],
            expression: '',
          },
        };
      }
      return {
        ...state,
        composition: {
          ...state.composition,
          nodes: [...state.composition.nodes, action.node],
          sourceMechanics: action.node.mechanicId
            ? [...state.composition.sourceMechanics, action.node.mechanicId]
            : state.composition.sourceMechanics,
        },
      };
    }

    case 'REMOVE_NODE': {
      if (!state.composition) return state;
      const nodes = state.composition.nodes.filter((n) => n.id !== action.nodeId);
      const edges = state.composition.edges.filter(
        (e) => e.source !== action.nodeId && e.target !== action.nodeId
      );
      return {
        ...state,
        composition: { ...state.composition, nodes, edges },
        selectedNodeId: state.selectedNodeId === action.nodeId ? null : state.selectedNodeId,
      };
    }

    case 'ADD_EDGE': {
      if (!state.composition) return state;
      return {
        ...state,
        composition: {
          ...state.composition,
          edges: [...state.composition.edges, action.edge],
        },
      };
    }

    case 'REMOVE_EDGE': {
      if (!state.composition) return state;
      return {
        ...state,
        composition: {
          ...state.composition,
          edges: state.composition.edges.filter((e) => e.id !== action.edgeId),
        },
      };
    }

    case 'SET_ZOOM':
      return { ...state, zoom: Math.max(0.25, Math.min(2, action.zoom)) };

    case 'SET_PAN':
      return { ...state, pan: action.pan };

    case 'SET_MODE':
      return { ...state, mode: action.mode };

    case 'LOAD_COMPOSITION':
      return { ...state, composition: action.composition, selectedNodeId: null };

    case 'CLEAR_COMPOSITION':
      return { ...state, composition: null, selectedNodeId: null };

    default:
      return state;
  }
}

// =============================================================================
// Subcomponents
// =============================================================================

interface MechanicBlockProps {
  mechanic: Mechanic;
  onDragStart: (mechanicId: string) => void;
}

const MechanicBlock = memo(function MechanicBlock({ mechanic, onDragStart }: MechanicBlockProps) {
  return (
    <div
      className="composer-mechanic-block"
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData('mechanicId', mechanic.id);
        onDragStart(mechanic.id);
      }}
    >
      <span className="composer-mechanic-block__id">{mechanic.id}</span>
      <span className="composer-mechanic-block__name">{mechanic.name}</span>
      <span className="composer-mechanic-block__type">
        {mechanic.inputType} → {mechanic.outputType}
      </span>
    </div>
  );
});

interface CompositionNodeViewProps {
  node: CompositionNode;
  mechanic?: Mechanic;
  isSelected: boolean;
  zoom: number;
  onSelect: () => void;
  onDelete: () => void;
}

const CompositionNodeView = memo(function CompositionNodeView({
  node,
  mechanic,
  isSelected,
  zoom,
  onSelect,
  onDelete,
}: CompositionNodeViewProps) {
  const getOperationIcon = () => {
    if (node.type !== 'operation' || !node.operation) return null;
    switch (node.operation.type) {
      case 'sequential':
        return <ArrowRight size={16} />;
      case 'parallel':
        return <Split size={16} />;
      case 'conditional':
        return <HelpCircle size={16} />;
      case 'feedback':
        return <RotateCcw size={16} />;
      default:
        return null;
    }
  };

  return (
    <div
      className={`composer-node composer-node--${node.type} ${isSelected ? 'composer-node--selected' : ''}`}
      style={{
        left: node.position.x * zoom,
        top: node.position.y * zoom,
        transform: `scale(${zoom})`,
        transformOrigin: 'top left',
      }}
      onClick={onSelect}
    >
      {node.type === 'mechanic' && mechanic && (
        <>
          <span className="composer-node__id">{mechanic.id}</span>
          <span className="composer-node__name">{mechanic.name}</span>
          <div className="composer-node__verbs">
            {mechanic.verbs.slice(0, 2).map((verb, i) => (
              <span key={i} className="composer-node__verb">
                {verb}
              </span>
            ))}
          </div>
        </>
      )}
      {node.type === 'operation' && (
        <div className="composer-node__operation">
          {getOperationIcon()}
          <span>{node.operation?.symbol}</span>
        </div>
      )}
      {isSelected && (
        <button
          className="composer-node__delete"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          aria-label="Delete node"
        >
          <Trash2 size={12} />
        </button>
      )}
    </div>
  );
});

interface EdgesViewProps {
  edges: CompositionEdge[];
  nodes: CompositionNode[];
  zoom: number;
}

const EdgesView = memo(function EdgesView({ edges, nodes, zoom }: EdgesViewProps) {
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));

  return (
    <svg className="composer-edges" style={{ pointerEvents: 'none' }}>
      {edges.map((edge) => {
        const source = nodeMap.get(edge.source);
        const target = nodeMap.get(edge.target);
        if (!source || !target) return null;

        const x1 = (source.position.x + 60) * zoom;
        const y1 = (source.position.y + 30) * zoom;
        const x2 = target.position.x * zoom;
        const y2 = (target.position.y + 30) * zoom;

        return (
          <g key={edge.id}>
            <line
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              className="composer-edge"
              markerEnd="url(#arrowhead)"
            />
            {edge.label && (
              <text x={(x1 + x2) / 2} y={(y1 + y2) / 2 - 5} className="composer-edge-label">
                {edge.label}
              </text>
            )}
          </g>
        );
      })}
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="var(--steel-500)" />
        </marker>
      </defs>
    </svg>
  );
});

interface ToolbarProps {
  mode: ComposerState['mode'];
  zoom: number;
  hasComposition: boolean;
  onSetMode: (mode: ComposerState['mode']) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onClear: () => void;
}

const Toolbar = memo(function Toolbar({
  mode,
  zoom,
  hasComposition,
  onSetMode,
  onZoomIn,
  onZoomOut,
  onClear,
}: ToolbarProps) {
  return (
    <div className="composer-toolbar">
      <div className="composer-toolbar__modes">
        <button
          className={`composer-toolbar__btn ${mode === 'select' ? 'composer-toolbar__btn--active' : ''}`}
          onClick={() => onSetMode('select')}
          title="Select mode (V)"
        >
          <MousePointer size={14} />
        </button>
        <button
          className={`composer-toolbar__btn ${mode === 'connect' ? 'composer-toolbar__btn--active' : ''}`}
          onClick={() => onSetMode('connect')}
          title="Connect mode (C)"
        >
          <Link size={14} />
        </button>
        <button
          className={`composer-toolbar__btn ${mode === 'add' ? 'composer-toolbar__btn--active' : ''}`}
          onClick={() => onSetMode('add')}
          title="Add mode (A)"
        >
          <Plus size={14} />
        </button>
      </div>

      <div className="composer-toolbar__zoom">
        <button
          className="composer-toolbar__btn"
          onClick={onZoomOut}
          disabled={zoom <= 0.25}
          title="Zoom out"
        >
          <ZoomOut size={14} />
        </button>
        <span className="composer-toolbar__zoom-value">{Math.round(zoom * 100)}%</span>
        <button
          className="composer-toolbar__btn"
          onClick={onZoomIn}
          disabled={zoom >= 2}
          title="Zoom in"
        >
          <ZoomIn size={14} />
        </button>
      </div>

      <div className="composer-toolbar__actions">
        <button
          className="composer-toolbar__btn composer-toolbar__btn--danger"
          onClick={onClear}
          disabled={!hasComposition}
          title="Clear composition"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
});

interface OperationPaletteProps {
  operad: GameOperad;
  onAddOperation: (type: string) => void;
}

const OperationPalette = memo(function OperationPalette({
  operad,
  onAddOperation,
}: OperationPaletteProps) {
  return (
    <div className="composer-operations">
      <span className="composer-operations__label">Operations</span>
      <div className="composer-operations__list">
        {operad.operations.map((op) => (
          <button
            key={op.type}
            className="composer-operations__btn"
            onClick={() => onAddOperation(op.type)}
            title={op.type}
          >
            {op.symbol}
          </button>
        ))}
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const MechanicComposer = memo(function MechanicComposer({
  mechanics,
  composition,
  operad,
  onCompose,
  onClear,
}: MechanicComposerProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [state, dispatch] = useReducer(composerReducer, { mechanics, composition }, (init) =>
    createInitialState(init.mechanics, init.composition)
  );

  // Drag and drop handlers
  const handleDragStart = useCallback((_mechanicId: string) => {
    // Could show a drag preview
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const mechanicId = e.dataTransfer.getData('mechanicId');
      if (!mechanicId || !canvasRef.current) return;

      const rect = canvasRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / state.zoom;
      const y = (e.clientY - rect.top) / state.zoom;

      const newNode: CompositionNode = {
        id: `node-${Date.now()}`,
        type: 'mechanic',
        position: { x, y },
        mechanicId,
      };

      dispatch({ type: 'ADD_NODE', node: newNode });
    },
    [state.zoom]
  );

  // Operation handlers
  const handleAddOperation = useCallback(
    (opType: string) => {
      const operation = operad.operations.find((op) => op.type === opType);
      if (!operation) return;

      const newNode: CompositionNode = {
        id: `node-${Date.now()}`,
        type: 'operation',
        position: { x: 200, y: 200 },
        operation,
      };

      dispatch({ type: 'ADD_NODE', node: newNode });
    },
    [operad.operations]
  );

  // Calculate Galois loss (simplified)
  const calculateGaloisLoss = useCallback(() => {
    if (!state.composition || state.composition.nodes.length < 2) return 0;
    // Simplified: loss increases with number of compositions
    const mechanicCount = state.composition.nodes.filter((n) => n.type === 'mechanic').length;
    const opCount = state.composition.nodes.filter((n) => n.type === 'operation').length;
    return Math.min(1, (opCount * 0.1) / Math.max(1, mechanicCount));
  }, [state.composition]);

  // Save composition
  const handleSave = useCallback(() => {
    if (!state.composition) return;

    const updatedComposition: MechanicComposition = {
      ...state.composition,
      galoisLoss: calculateGaloisLoss(),
      // In a real implementation, would compute these from the graph
      expression: state.composition.nodes
        .filter((n) => n.type === 'mechanic')
        .map((n) => n.mechanicId)
        .join(' >> '),
    };

    onCompose(updatedComposition);
  }, [state.composition, calculateGaloisLoss, onCompose]);

  return (
    <div className="mechanic-composer">
      {/* Header */}
      <div className="mechanic-composer__header">
        <GitBranch size={14} className="mechanic-composer__icon" />
        <span className="mechanic-composer__title">MechanicComposer</span>
        {state.composition && (
          <span className="mechanic-composer__loss">
            Galois Loss: {(calculateGaloisLoss() * 100).toFixed(1)}%
          </span>
        )}
      </div>

      {/* Toolbar */}
      <Toolbar
        mode={state.mode}
        zoom={state.zoom}
        hasComposition={state.composition !== null}
        onSetMode={(mode) => dispatch({ type: 'SET_MODE', mode })}
        onZoomIn={() => dispatch({ type: 'SET_ZOOM', zoom: state.zoom + 0.25 })}
        onZoomOut={() => dispatch({ type: 'SET_ZOOM', zoom: state.zoom - 0.25 })}
        onClear={() => {
          dispatch({ type: 'CLEAR_COMPOSITION' });
          onClear?.();
        }}
      />

      {/* Main Layout */}
      <div className="mechanic-composer__layout">
        {/* Mechanics Library (left) */}
        <div className="mechanic-composer__library">
          <div className="mechanic-composer__library-header">
            <span>Mechanics</span>
            <span className="mechanic-composer__library-count">{mechanics.length}</span>
          </div>
          <div className="mechanic-composer__library-list">
            {mechanics.map((mechanic) => (
              <MechanicBlock key={mechanic.id} mechanic={mechanic} onDragStart={handleDragStart} />
            ))}
          </div>
          <OperationPalette operad={operad} onAddOperation={handleAddOperation} />
        </div>

        {/* Canvas (center) */}
        <div
          ref={canvasRef}
          className="mechanic-composer__canvas"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {state.composition ? (
            <>
              <EdgesView
                edges={state.composition.edges}
                nodes={state.composition.nodes}
                zoom={state.zoom}
              />
              {state.composition.nodes.map((node) => (
                <CompositionNodeView
                  key={node.id}
                  node={node}
                  mechanic={
                    node.mechanicId ? mechanics.find((m) => m.id === node.mechanicId) : undefined
                  }
                  isSelected={state.selectedNodeId === node.id}
                  zoom={state.zoom}
                  onSelect={() => dispatch({ type: 'SELECT_NODE', nodeId: node.id })}
                  onDelete={() => dispatch({ type: 'REMOVE_NODE', nodeId: node.id })}
                />
              ))}
            </>
          ) : (
            <div className="mechanic-composer__empty">
              <p>Drag mechanics here to start composing</p>
              <span className="mechanic-composer__hint">
                Use {'>>'} (sequential), || (parallel), ?: (conditional), or loop (feedback)
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      {state.composition && (
        <div className="mechanic-composer__footer">
          <span className="mechanic-composer__expression">
            {state.composition.expression || 'Building expression...'}
          </span>
          <button className="mechanic-composer__save" onClick={handleSave}>
            Save Composition
          </button>
        </div>
      )}
    </div>
  );
});

export default MechanicComposer;
