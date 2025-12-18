/**
 * GhostHeritageGraph - The Crown Jewel Visualization
 *
 * Visualizes the Ghost Heritage DAG: seeing what almost was alongside what is.
 *
 * Design Principles (2D Renaissance):
 * - Living Earth palette (browns, greens, warm tones)
 * - Chosen path = solid line, ghost paths = dashed/translucent
 * - Interactive: click ghost to see "why rejected"
 * - Respects density modes (compact/comfortable/spacious)
 *
 * ASCII Reference:
 * ```
 *  TIME ──────────────────────────────────────────────────────▶
 *
 *  Depth 0:    [chosen] ─────────────────────────────────────
 *              │
 *  Depth 1:    [chosen] ───────────────┬──────────────────
 *              │                       │
 *              │                       [ghost] "par" (Order matters)
 *              │
 *  Depth 2:    [chosen] ───────────────┬──────────────────
 *              │                       │
 *              │                       [ghost] "branch" (Needs context)
 * ```
 *
 * @see spec/protocols/differance.md - The specification
 * @see plans/differance-cultivation.md - Phase 5: FRUITING
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { useCallback, useMemo, useState } from 'react';
import { GitBranch, Eye, EyeOff, ChevronRight, RefreshCw } from 'lucide-react';
import { useShell } from '@/shell';
import { Breathe } from '@/components/joy';
import type {
  HeritageResponse,
  HeritageNodeResponse,
  HeritageEdgeResponse,
  WhyResponse,
} from '@/hooks/useDifferanceQuery';

// =============================================================================
// Types
// =============================================================================

export interface GhostHeritageGraphProps {
  /** Heritage DAG data from AGENTESE */
  heritage: HeritageResponse;
  /** Why explanation (optional) */
  why?: WhyResponse | null;
  /** Callback when node is clicked */
  onNodeClick?: (nodeId: string, node: HeritageNodeResponse) => void;
  /** Callback when ghost is selected for exploration */
  onExploreGhost?: (nodeId: string) => void;
  /** Callback to replay from trace */
  onReplayFrom?: (nodeId: string) => void;
  /** Loading state */
  isLoading?: boolean;
  /** Refetch callback */
  onRefetch?: () => void;
  /** Custom class name */
  className?: string;
}

// Node type visual properties
const NODE_STYLES: Record<
  HeritageNodeResponse['type'],
  {
    bg: string;
    border: string;
    text: string;
    glow?: string;
  }
> = {
  chosen: {
    bg: 'bg-[#4A6B4A]',
    border: 'border-[#8BAB8B]',
    text: 'text-[#F5E6D3]',
    glow: 'shadow-[0_0_8px_rgba(139,171,139,0.4)]',
  },
  ghost: {
    bg: 'bg-[#4A3728]/50',
    border: 'border-[#6B4E3D] border-dashed',
    text: 'text-[#AB9080]',
  },
  deferred: {
    bg: 'bg-[#5A4A3A]/30',
    border: 'border-[#8B7B6B] border-dotted',
    text: 'text-[#8B7B6B]',
  },
  spec: {
    bg: 'bg-[#3A4A5A]/40',
    border: 'border-[#6B8BAB]',
    text: 'text-[#9BBBDB]',
  },
  impl: {
    bg: 'bg-[#4A6B4A]/70',
    border: 'border-[#6B8B6B]',
    text: 'text-[#D4E4D4]',
  },
};

const EDGE_STYLES: Record<HeritageEdgeResponse['type'], string> = {
  produced: 'stroke-[#8BAB8B] stroke-2',
  ghosted: 'stroke-[#6B4E3D] stroke-1 stroke-dasharray-4',
  deferred: 'stroke-[#8B7B6B] stroke-1 stroke-dasharray-2',
  concretized: 'stroke-[#6B8BAB] stroke-2',
};

// =============================================================================
// Main Component
// =============================================================================

export function GhostHeritageGraph({
  heritage,
  why,
  onNodeClick,
  onExploreGhost,
  onReplayFrom,
  isLoading = false,
  onRefetch,
  className = '',
}: GhostHeritageGraphProps) {
  const { density, isMobile } = useShell();
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [showGhosts, setShowGhosts] = useState(true);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Organize nodes by depth for horizontal layout
  const nodesByDepth = useMemo(() => {
    const byDepth: Map<number, HeritageNodeResponse[]> = new Map();
    Object.values(heritage.nodes).forEach((node) => {
      const existing = byDepth.get(node.depth) || [];
      existing.push(node);
      byDepth.set(node.depth, existing);
    });
    return byDepth;
  }, [heritage.nodes]);

  // Filter visible nodes
  const visibleNodes = useMemo(() => {
    if (showGhosts) {
      return Object.values(heritage.nodes);
    }
    return Object.values(heritage.nodes).filter((n) => n.type !== 'ghost');
  }, [heritage.nodes, showGhosts]);

  const visibleEdges = useMemo(() => {
    if (showGhosts) {
      return heritage.edges;
    }
    const visibleIds = new Set(visibleNodes.map((n) => n.id));
    return heritage.edges.filter((e) => visibleIds.has(e.source) && visibleIds.has(e.target));
  }, [heritage.edges, visibleNodes, showGhosts]);

  // Handle node click
  const handleNodeClick = useCallback(
    (nodeId: string) => {
      const node = heritage.nodes[nodeId];
      if (!node) return;
      setSelectedNode(nodeId === selectedNode ? null : nodeId);
      onNodeClick?.(nodeId, node);
    },
    [heritage.nodes, selectedNode, onNodeClick]
  );

  // Count stats
  const ghostCount = Object.values(heritage.nodes).filter((n) => n.type === 'ghost').length;
  const explorableCount = Object.values(heritage.nodes).filter(
    (n) => n.type === 'ghost' && n.explorable
  ).length;

  const isCompact = density === 'compact';
  const nodeSize = isCompact ? 'w-28 h-16' : 'w-36 h-20';
  const fontSize = isCompact ? 'text-[10px]' : 'text-xs';

  // ==========================================================================
  // Mobile Layout (vertical scrolling list)
  // ==========================================================================
  if (isMobile) {
    return (
      <div className={`flex flex-col h-full bg-[#2D1B14] ${className}`}>
        {/* Header */}
        <HeritageHeader
          heritage={heritage}
          why={why}
          ghostCount={ghostCount}
          explorableCount={explorableCount}
          showGhosts={showGhosts}
          onToggleGhosts={() => setShowGhosts(!showGhosts)}
          onRefetch={onRefetch}
          isLoading={isLoading}
          compact
        />

        {/* Node List (vertical) */}
        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          {Array.from(nodesByDepth.entries())
            .sort(([a], [b]) => a - b)
            .map(([depth, nodes]) => (
              <div key={depth} className="space-y-2">
                <div className="text-[10px] text-[#6B4E3D] uppercase tracking-wide">
                  Depth {depth}
                </div>
                {nodes
                  .filter((n) => showGhosts || n.type !== 'ghost')
                  .map((node) => (
                    <HeritageNodeCard
                      key={node.id}
                      node={node}
                      isSelected={selectedNode === node.id}
                      onClick={() => handleNodeClick(node.id)}
                      onExplore={node.explorable ? () => onExploreGhost?.(node.id) : undefined}
                      compact
                    />
                  ))}
              </div>
            ))}
        </div>

        {/* Selected Node Detail */}
        {selectedNode && heritage.nodes[selectedNode] && (
          <NodeDetailPanel
            node={heritage.nodes[selectedNode]}
            onExplore={
              heritage.nodes[selectedNode].explorable
                ? () => onExploreGhost?.(selectedNode)
                : undefined
            }
            onReplay={() => onReplayFrom?.(selectedNode)}
            onClose={() => setSelectedNode(null)}
          />
        )}
      </div>
    );
  }

  // ==========================================================================
  // Desktop Layout (horizontal DAG visualization)
  // ==========================================================================
  return (
    <div className={`flex flex-col h-full bg-[#2D1B14] ${className}`}>
      {/* Header */}
      <HeritageHeader
        heritage={heritage}
        why={why}
        ghostCount={ghostCount}
        explorableCount={explorableCount}
        showGhosts={showGhosts}
        onToggleGhosts={() => setShowGhosts(!showGhosts)}
        onRefetch={onRefetch}
        isLoading={isLoading}
      />

      {/* DAG Visualization */}
      <div className="flex-1 overflow-auto p-4">
        <div className="relative min-h-full">
          {/* SVG for edges */}
          <svg
            className="absolute inset-0 w-full h-full pointer-events-none"
            style={{ minWidth: `${(heritage.max_depth + 1) * 200}px` }}
          >
            {visibleEdges.map((edge, i) => {
              const sourceNode = heritage.nodes[edge.source];
              const targetNode = heritage.nodes[edge.target];
              if (!sourceNode || !targetNode) return null;

              // Calculate positions (simplified horizontal layout)
              const x1 = sourceNode.depth * 180 + 90;
              const y1 = 60 + (visibleNodes.indexOf(sourceNode) % 3) * 80;
              const x2 = targetNode.depth * 180 + 90;
              const y2 = 60 + (visibleNodes.indexOf(targetNode) % 3) * 80;

              return (
                <line
                  key={`${edge.source}-${edge.target}-${i}`}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  className={EDGE_STYLES[edge.type]}
                  strokeDasharray={
                    edge.type === 'ghosted' ? '4,4' : edge.type === 'deferred' ? '2,2' : undefined
                  }
                />
              );
            })}
          </svg>

          {/* Nodes */}
          <div
            className="relative flex gap-8"
            style={{ minWidth: `${(heritage.max_depth + 1) * 200}px` }}
          >
            {Array.from(nodesByDepth.entries())
              .sort(([a], [b]) => a - b)
              .map(([depth, nodes]) => (
                <div key={depth} className="flex flex-col gap-4">
                  <div className={`${fontSize} text-[#6B4E3D] uppercase tracking-wide text-center`}>
                    {depth === 0 ? 'Origin' : `Depth ${depth}`}
                  </div>
                  {nodes
                    .filter((n) => showGhosts || n.type !== 'ghost')
                    .map((node) => (
                      <HeritageNodeBox
                        key={node.id}
                        node={node}
                        isSelected={selectedNode === node.id}
                        isHovered={hoveredNode === node.id}
                        onClick={() => handleNodeClick(node.id)}
                        onHover={() => setHoveredNode(node.id)}
                        onLeave={() => setHoveredNode(null)}
                        size={nodeSize}
                        fontSize={fontSize}
                      />
                    ))}
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Selected Node Detail Panel */}
      {selectedNode && heritage.nodes[selectedNode] && (
        <NodeDetailPanel
          node={heritage.nodes[selectedNode]}
          onExplore={
            heritage.nodes[selectedNode].explorable
              ? () => onExploreGhost?.(selectedNode)
              : undefined
          }
          onReplay={() => onReplayFrom?.(selectedNode)}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface HeritageHeaderProps {
  heritage: HeritageResponse;
  why?: WhyResponse | null;
  ghostCount: number;
  explorableCount: number;
  showGhosts: boolean;
  onToggleGhosts: () => void;
  onRefetch?: () => void;
  isLoading?: boolean;
  compact?: boolean;
}

function HeritageHeader({
  heritage,
  why,
  ghostCount,
  explorableCount,
  showGhosts,
  onToggleGhosts,
  onRefetch,
  isLoading,
  compact,
}: HeritageHeaderProps) {
  return (
    <header className="flex-shrink-0 bg-[#4A3728]/50 border-b border-[#6B4E3D] px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Left: Title and info */}
        <div className="flex items-center gap-3">
          <Breathe intensity={0.3} speed="slow">
            <GitBranch className={`${compact ? 'w-5 h-5' : 'w-6 h-6'} text-[#8BAB8B]`} />
          </Breathe>
          <div>
            <h1 className={`font-semibold text-[#F5E6D3] ${compact ? 'text-sm' : 'text-base'}`}>
              Ghost Heritage Graph
            </h1>
            <p className={`text-[#AB9080] ${compact ? 'text-[10px]' : 'text-xs'}`}>
              {heritage.chosen_path.length} chosen, {ghostCount} ghosts
              {explorableCount > 0 && ` (${explorableCount} explorable)`}
            </p>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          {/* Toggle ghosts */}
          <button
            onClick={onToggleGhosts}
            className={`
              flex items-center gap-1 px-2 py-1 rounded text-xs
              ${showGhosts ? 'bg-[#4A6B4A]/30 text-[#8BAB8B]' : 'bg-[#4A3728]/30 text-[#AB9080]'}
              hover:bg-[#4A3728]/50 transition-colors
            `}
            title={showGhosts ? 'Hide ghosts' : 'Show ghosts'}
          >
            {showGhosts ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            {!compact && <span>{showGhosts ? 'Ghosts' : 'Hidden'}</span>}
          </button>

          {/* Refetch */}
          {onRefetch && (
            <button
              onClick={onRefetch}
              disabled={isLoading}
              className="p-1.5 rounded bg-[#4A3728]/30 text-[#AB9080] hover:bg-[#4A3728]/50 transition-colors disabled:opacity-50"
              title="Refresh"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          )}
        </div>
      </div>

      {/* Why summary (if available) */}
      {why && why.summary && (
        <div className={`mt-2 ${compact ? 'text-[10px]' : 'text-xs'} text-[#8BAB8B] italic`}>
          {why.summary}
        </div>
      )}
    </header>
  );
}

interface HeritageNodeBoxProps {
  node: HeritageNodeResponse;
  isSelected: boolean;
  isHovered: boolean;
  onClick: () => void;
  onHover: () => void;
  onLeave: () => void;
  size: string;
  fontSize: string;
}

function HeritageNodeBox({
  node,
  isSelected,
  isHovered,
  onClick,
  onHover,
  onLeave,
  size,
  fontSize,
}: HeritageNodeBoxProps) {
  const style = NODE_STYLES[node.type];

  return (
    <button
      onClick={onClick}
      onMouseEnter={onHover}
      onMouseLeave={onLeave}
      className={`
        ${size} ${style.bg} ${style.border} ${style.text}
        ${style.glow || ''}
        ${isSelected ? 'ring-2 ring-[#D4A574]' : ''}
        ${isHovered ? 'scale-105' : ''}
        border rounded-lg p-2 flex flex-col justify-center items-center
        transition-all duration-200 cursor-pointer
        hover:brightness-110
      `}
    >
      <div className={`${fontSize} font-medium truncate w-full text-center`}>{node.operation}</div>
      <div className={`${fontSize} opacity-70 truncate w-full text-center`}>
        {node.type}
        {node.explorable && ' *'}
      </div>
    </button>
  );
}

interface HeritageNodeCardProps {
  node: HeritageNodeResponse;
  isSelected: boolean;
  onClick: () => void;
  onExplore?: () => void;
  compact?: boolean;
}

function HeritageNodeCard({
  node,
  isSelected,
  onClick,
  onExplore,
  compact,
}: HeritageNodeCardProps) {
  const style = NODE_STYLES[node.type];

  return (
    <div
      onClick={onClick}
      className={`
        ${style.bg} ${style.border} ${style.text}
        ${style.glow || ''}
        ${isSelected ? 'ring-2 ring-[#D4A574]' : ''}
        border rounded-lg p-3 cursor-pointer
        transition-all duration-200 hover:brightness-110
      `}
    >
      <div className="flex items-center justify-between">
        <div>
          <div className={`${compact ? 'text-xs' : 'text-sm'} font-medium`}>{node.operation}</div>
          <div className={`${compact ? 'text-[10px]' : 'text-xs'} opacity-70`}>
            {node.type} at depth {node.depth}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {node.explorable && onExplore && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onExplore();
              }}
              className="p-1 rounded bg-[#4A6B4A]/30 text-[#8BAB8B] hover:bg-[#4A6B4A]/50"
              title="Explore this ghost"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      {node.reason && (
        <div className={`mt-2 ${compact ? 'text-[10px]' : 'text-xs'} opacity-60 italic`}>
          {node.reason}
        </div>
      )}
    </div>
  );
}

interface NodeDetailPanelProps {
  node: HeritageNodeResponse;
  onExplore?: () => void;
  onReplay?: () => void;
  onClose: () => void;
}

function NodeDetailPanel({ node, onExplore, onReplay, onClose }: NodeDetailPanelProps) {
  const style = NODE_STYLES[node.type];

  return (
    <div className="flex-shrink-0 bg-[#4A3728]/70 border-t border-[#6B4E3D] p-4">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className={`font-semibold ${style.text}`}>{node.operation}</h3>
          <p className="text-xs text-[#AB9080]">
            {node.type} | depth {node.depth} | {node.timestamp}
          </p>
        </div>
        <button onClick={onClose} className="text-[#AB9080] hover:text-[#F5E6D3] text-lg">
          x
        </button>
      </div>

      {/* Inputs */}
      {node.inputs.length > 0 && (
        <div className="mb-3">
          <span className="text-xs text-[#6B4E3D]">Inputs: </span>
          <span className="text-xs text-[#AB9080]">{node.inputs.join(', ')}</span>
        </div>
      )}

      {/* Reason */}
      {node.reason && <div className="mb-3 text-xs text-[#8BAB8B] italic">{node.reason}</div>}

      {/* Output */}
      {node.output !== undefined && (
        <div className="mb-3">
          <span className="text-xs text-[#6B4E3D]">Output: </span>
          <code className="text-xs text-[#D4A574] bg-[#1A2E1A] px-1.5 py-0.5 rounded">
            {typeof node.output === 'string'
              ? node.output
              : JSON.stringify(node.output).slice(0, 50)}
          </code>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 mt-4">
        {node.explorable && onExplore && (
          <button
            onClick={onExplore}
            className="flex-1 px-3 py-2 bg-[#4A6B4A] text-[#F5E6D3] rounded text-sm font-medium hover:bg-[#5A7B5A] transition-colors"
          >
            Explore Ghost
          </button>
        )}
        {onReplay && (
          <button
            onClick={onReplay}
            className="px-3 py-2 bg-[#4A3728] text-[#AB9080] rounded text-sm hover:bg-[#5A4738] transition-colors"
          >
            Replay From Here
          </button>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default GhostHeritageGraph;
