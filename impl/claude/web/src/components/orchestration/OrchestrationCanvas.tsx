/**
 * OrchestrationCanvas: Full-screen pipeline building mode.
 *
 * Simplified orchestration UI for building and executing agent pipelines.
 * Uses a basic node-based editor with drag-drop functionality.
 */

import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { PipelineTemplates, type PipelineTemplate } from './PipelineTemplates';
import { ExecutionMonitor, type ExecutionStatus, type NodeExecution } from './ExecutionMonitor';

export interface OrchestrationCanvasProps {
  townId: string;
  citizens: AgentInfo[];
  onClose?: () => void;
  onExecute?: (nodes: SimpleNode[], edges: SimpleEdge[]) => Promise<void>;
  className?: string;
}

interface AgentInfo {
  id: string;
  name: string;
  archetype: string;
}

// Simplified node/edge types for the basic editor
interface SimpleNode {
  id: string;
  label: string;
  archetype: string;
  citizenId?: string;
  position: { x: number; y: number };
}

interface SimpleEdge {
  id: string;
  sourceId: string;
  targetId: string;
}

type CanvasMode = 'build' | 'execute' | 'results';

export function OrchestrationCanvas({
  citizens,
  onClose,
  onExecute,
  className,
}: OrchestrationCanvasProps) {
  const [mode, setMode] = useState<CanvasMode>('build');
  const [showTemplates, setShowTemplates] = useState(false);
  const [showPalette, setShowPalette] = useState(true);

  // Simple state management
  const [nodes, setNodes] = useState<SimpleNode[]>([]);
  const [edges, setEdges] = useState<SimpleEdge[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null);
  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus | null>(null);

  // Add node from palette
  const handleAddNode = useCallback((citizen: AgentInfo) => {
    const newNode: SimpleNode = {
      id: `node-${Date.now()}`,
      label: citizen.name,
      archetype: citizen.archetype,
      citizenId: citizen.id,
      position: { x: 200 + nodes.length * 150, y: 200 },
    };
    setNodes((prev) => [...prev, newNode]);
  }, [nodes.length]);

  // Remove node
  const handleRemoveNode = useCallback((nodeId: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== nodeId));
    setEdges((prev) => prev.filter((e) => e.sourceId !== nodeId && e.targetId !== nodeId));
    setSelectedNodeId(null);
  }, []);

  // Start connection
  const handleStartConnection = useCallback((nodeId: string) => {
    setConnectingFrom(nodeId);
  }, []);

  // End connection
  const handleEndConnection = useCallback((targetId: string) => {
    if (connectingFrom && connectingFrom !== targetId) {
      // Check for existing edge
      const exists = edges.some(
        (e) => e.sourceId === connectingFrom && e.targetId === targetId
      );
      if (!exists) {
        setEdges((prev) => [
          ...prev,
          { id: `edge-${Date.now()}`, sourceId: connectingFrom, targetId },
        ]);
      }
    }
    setConnectingFrom(null);
  }, [connectingFrom, edges]);

  // Handle template selection
  const handleSelectTemplate = useCallback((template: PipelineTemplate) => {
    // Map template to our simple nodes
    const newNodes: SimpleNode[] = template.nodes.map((node, i) => {
      const citizen = citizens.find((c) => c.archetype === node.archetype) || citizens[i % citizens.length];
      return {
        id: node.id,
        label: citizen?.name || node.label,
        archetype: node.archetype,
        citizenId: citizen?.id,
        position: node.position,
      };
    });

    // Map template edges (TemplateEdge uses string source/target)
    const newEdges: SimpleEdge[] = template.edges.map((edge) => ({
      id: edge.id,
      sourceId: edge.source,
      targetId: edge.target,
    }));

    setNodes(newNodes);
    setEdges(newEdges);
    setShowTemplates(false);
  }, [citizens]);

  // Clear all
  const handleClear = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setSelectedNodeId(null);
    setConnectingFrom(null);
  }, []);

  // Handle execution
  const handleExecute = useCallback(async () => {
    if (nodes.length === 0) return;

    setMode('execute');

    // Initialize execution status
    const nodeExecutions: NodeExecution[] = nodes.map((node) => ({
      nodeId: node.id,
      status: 'pending',
    }));

    setExecutionStatus({
      pipelineId: `exec-${Date.now()}`,
      status: 'running',
      nodes: nodeExecutions,
      startedAt: new Date(),
    });

    try {
      if (onExecute) {
        await onExecute(nodes, edges);
      } else {
        // Mock execution
        for (const node of nodes) {
          setExecutionStatus((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              nodes: prev.nodes.map((n) =>
                n.nodeId === node.id ? { ...n, status: 'running' } : n
              ),
            };
          });

          await new Promise((r) => setTimeout(r, 800 + Math.random() * 400));

          setExecutionStatus((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              nodes: prev.nodes.map((n) =>
                n.nodeId === node.id ? { ...n, status: 'completed' } : n
              ),
            };
          });
        }
      }

      setExecutionStatus((prev) =>
        prev ? { ...prev, status: 'completed', completedAt: new Date() } : prev
      );
      setMode('results');
    } catch (err) {
      setExecutionStatus((prev) =>
        prev
          ? { ...prev, status: 'failed', error: (err as Error).message, completedAt: new Date() }
          : prev
      );
    }
  }, [nodes, edges, onExecute]);

  // Check if valid (at least 2 nodes connected)
  const isValid = nodes.length >= 2 && edges.length >= 1;

  return (
    <div className={cn('fixed inset-0 z-40 bg-town-bg flex flex-col', className)}>
      {/* Header */}
      <OrchestrationHeader
        mode={mode}
        nodeCount={nodes.length}
        canExecute={isValid}
        onShowTemplates={() => setShowTemplates(true)}
        onTogglePalette={() => setShowPalette(!showPalette)}
        onClear={handleClear}
        onExecute={handleExecute}
        onReset={() => {
          setMode('build');
          setExecutionStatus(null);
        }}
        onClose={onClose}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Agent Palette */}
        {showPalette && mode === 'build' && (
          <AgentPalette citizens={citizens} onAdd={handleAddNode} />
        )}

        {/* Canvas */}
        <div className="flex-1 relative bg-town-surface/10">
          <SimpleCanvas
            nodes={nodes}
            edges={edges}
            selectedNodeId={selectedNodeId}
            connectingFrom={connectingFrom}
            onSelectNode={setSelectedNodeId}
            onRemoveNode={handleRemoveNode}
            onStartConnection={handleStartConnection}
            onEndConnection={handleEndConnection}
            onCancelConnection={() => setConnectingFrom(null)}
          />

          {/* Empty state */}
          {nodes.length === 0 && mode === 'build' && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center text-gray-500">
                <p className="text-lg mb-2">Drag agents from the palette</p>
                <p className="text-sm">or select a template to get started</p>
              </div>
            </div>
          )}
        </div>

        {/* Execution Monitor */}
        {(mode === 'execute' || mode === 'results') && executionStatus && (
          <ExecutionMonitor
            status={executionStatus}
            nodes={nodes.map((n) => ({
              id: n.id,
              label: n.label,
            }))}
            onClose={() => {
              setMode('build');
              setExecutionStatus(null);
            }}
          />
        )}
      </div>

      {/* Templates Modal */}
      {showTemplates && (
        <PipelineTemplates
          onSelect={handleSelectTemplate}
          onClose={() => setShowTemplates(false)}
        />
      )}
    </div>
  );
}

// =============================================================================
// Header
// =============================================================================

interface OrchestrationHeaderProps {
  mode: CanvasMode;
  nodeCount: number;
  canExecute: boolean;
  onShowTemplates: () => void;
  onTogglePalette: () => void;
  onClear: () => void;
  onExecute: () => void;
  onReset: () => void;
  onClose?: () => void;
}

function OrchestrationHeader({
  mode,
  nodeCount,
  canExecute,
  onShowTemplates,
  onTogglePalette,
  onClear,
  onExecute,
  onReset,
  onClose,
}: OrchestrationHeaderProps) {
  return (
    <div className="h-14 border-b border-town-accent/30 flex items-center justify-between px-4 bg-town-surface/30">
      <div className="flex items-center gap-4">
        <h1 className="font-bold text-lg">Pipeline Builder</h1>
        <span
          className={cn(
            'px-2 py-0.5 rounded text-xs font-medium uppercase',
            mode === 'build'
              ? 'bg-blue-500/20 text-blue-400'
              : mode === 'execute'
                ? 'bg-amber-500/20 text-amber-400'
                : 'bg-green-500/20 text-green-400'
          )}
        >
          {mode}
        </span>
        <span className="text-sm text-gray-500">{nodeCount} nodes</span>
      </div>

      <div className="flex items-center gap-2">
        {mode === 'build' && (
          <>
            <button
              onClick={onShowTemplates}
              className="px-3 py-1 text-sm bg-town-surface/50 hover:bg-town-accent/30 rounded transition-colors"
            >
              📋 Templates
            </button>
            <button
              onClick={onTogglePalette}
              className="px-3 py-1 text-sm bg-town-surface/50 hover:bg-town-accent/30 rounded transition-colors"
            >
              🎨 Palette
            </button>
            <button
              onClick={onClear}
              className="px-3 py-1 text-sm bg-town-surface/50 hover:bg-red-500/20 text-gray-400 hover:text-red-400 rounded transition-colors"
            >
              🗑️ Clear
            </button>
          </>
        )}

        {mode === 'results' && (
          <button
            onClick={onReset}
            className="px-3 py-1 text-sm bg-town-surface/50 hover:bg-town-accent/30 rounded transition-colors"
          >
            ← Back to Editor
          </button>
        )}
      </div>

      <div className="flex items-center gap-2">
        {mode === 'build' && (
          <button
            onClick={onExecute}
            disabled={!canExecute}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              canExecute
                ? 'bg-town-highlight hover:bg-town-highlight/80 text-white'
                : 'bg-town-surface text-gray-600 cursor-not-allowed'
            )}
          >
            ▶️ Execute
          </button>
        )}
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 hover:bg-town-accent/20 rounded transition-colors"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Agent Palette
// =============================================================================

interface AgentPaletteProps {
  citizens: AgentInfo[];
  onAdd: (citizen: AgentInfo) => void;
}

function AgentPalette({ citizens, onAdd }: AgentPaletteProps) {
  const [search, setSearch] = useState('');

  const filtered = citizens.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.archetype.toLowerCase().includes(search.toLowerCase())
  );

  const grouped = filtered.reduce(
    (acc, citizen) => {
      const key = citizen.archetype;
      if (!acc[key]) acc[key] = [];
      acc[key].push(citizen);
      return acc;
    },
    {} as Record<string, AgentInfo[]>
  );

  return (
    <div className="w-64 border-r border-town-accent/30 bg-town-surface/20 flex flex-col">
      <div className="p-3 border-b border-town-accent/20">
        <h3 className="font-semibold mb-2">Agents</h3>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search agents..."
          className="w-full bg-town-surface/50 border border-town-accent/30 rounded px-3 py-1 text-sm focus:outline-none focus:border-town-highlight"
        />
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-4">
        {Object.entries(grouped).map(([archetype, agents]) => (
          <div key={archetype}>
            <h4 className="text-xs font-medium text-gray-500 uppercase mb-2 px-2">
              {archetype}
            </h4>
            <div className="space-y-1">
              {agents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => onAdd(agent)}
                  className="w-full text-left px-3 py-2 rounded bg-town-surface/30 hover:bg-town-accent/30 transition-colors text-sm"
                >
                  {getArchetypeEmoji(agent.archetype)} {agent.name}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-town-accent/20 text-xs text-gray-500">
        Click to add agents
      </div>
    </div>
  );
}

// =============================================================================
// Simple Canvas
// =============================================================================

interface SimpleCanvasProps {
  nodes: SimpleNode[];
  edges: SimpleEdge[];
  selectedNodeId: string | null;
  connectingFrom: string | null;
  onSelectNode: (id: string | null) => void;
  onRemoveNode: (id: string) => void;
  onStartConnection: (id: string) => void;
  onEndConnection: (id: string) => void;
  onCancelConnection: () => void;
}

function SimpleCanvas({
  nodes,
  edges,
  selectedNodeId,
  connectingFrom,
  onSelectNode,
  onRemoveNode,
  onStartConnection,
  onEndConnection,
  onCancelConnection,
}: SimpleCanvasProps) {
  return (
    <div
      className="w-full h-full relative"
      onClick={() => {
        onSelectNode(null);
        onCancelConnection();
      }}
    >
      {/* Grid background */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="currentColor"
              strokeOpacity="0.1"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      {/* Edges */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" fill="currentColor" opacity="0.5" />
          </marker>
        </defs>

        {edges.map((edge) => {
          const source = nodes.find((n) => n.id === edge.sourceId);
          const target = nodes.find((n) => n.id === edge.targetId);
          if (!source || !target) return null;

          const x1 = source.position.x + 80;
          const y1 = source.position.y + 30;
          const x2 = target.position.x;
          const y2 = target.position.y + 30;

          return (
            <path
              key={edge.id}
              d={`M ${x1} ${y1} C ${x1 + 50} ${y1}, ${x2 - 50} ${y2}, ${x2} ${y2}`}
              fill="none"
              stroke="currentColor"
              strokeOpacity="0.4"
              strokeWidth="2"
              markerEnd="url(#arrowhead)"
            />
          );
        })}
      </svg>

      {/* Nodes */}
      {nodes.map((node) => (
        <div
          key={node.id}
          className={cn(
            'absolute w-40 p-3 rounded-lg border-2 cursor-pointer transition-all',
            'bg-town-surface/80 backdrop-blur',
            selectedNodeId === node.id
              ? 'border-town-highlight ring-2 ring-town-highlight/30'
              : connectingFrom && connectingFrom !== node.id
                ? 'border-green-500/50 hover:border-green-500'
                : 'border-town-accent/30 hover:border-town-accent'
          )}
          style={{
            left: node.position.x,
            top: node.position.y,
          }}
          onClick={(e) => {
            e.stopPropagation();
            if (connectingFrom && connectingFrom !== node.id) {
              onEndConnection(node.id);
            } else {
              onSelectNode(node.id);
            }
          }}
        >
          <div className="flex items-center gap-2 mb-1">
            <span>{getArchetypeEmoji(node.archetype)}</span>
            <span className="font-medium text-sm truncate">{node.label}</span>
          </div>
          <div className="text-xs text-gray-500">{node.archetype}</div>

          {/* Actions (visible when selected) */}
          {selectedNodeId === node.id && (
            <div className="absolute -top-2 -right-2 flex gap-1">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onStartConnection(node.id);
                }}
                className="w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center hover:bg-blue-600"
                title="Connect"
              >
                →
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onRemoveNode(node.id);
                }}
                className="w-6 h-6 rounded-full bg-red-500 text-white text-xs flex items-center justify-center hover:bg-red-600"
                title="Remove"
              >
                ✕
              </button>
            </div>
          )}
        </div>
      ))}

      {/* Connection hint */}
      {connectingFrom && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-blue-500/20 text-blue-400 px-4 py-2 rounded-full text-sm">
          Click another node to connect, or click canvas to cancel
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getArchetypeEmoji(archetype: string): string {
  const emojis: Record<string, string> = {
    Builder: '🔨',
    Trader: '💼',
    Healer: '💚',
    Scholar: '📚',
    Watcher: '👁️',
    Scout: '🔍',
    Sage: '🧙',
    Spark: '✨',
    Steady: '⚓',
    Sync: '🔗',
  };
  return emojis[archetype] || '👤';
}

export default OrchestrationCanvas;
