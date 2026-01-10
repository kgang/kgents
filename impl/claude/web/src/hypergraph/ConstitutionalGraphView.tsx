/**
 * ConstitutionalGraphView — Files derived from principles, not contained in folders
 *
 * "The file is a lie. There is only the graph."
 * "Files aren't IN folders—they're DERIVED FROM principles."
 *
 * This component replaces the traditional file tree with a view showing
 * K-Blocks organized by their derivation from Constitutional principles.
 *
 * THE PARADIGM:
 * - CONSTITUTION (root): The principles that govern the system
 * - Principles (level 1): COMPOSABLE, ETHICAL, TASTEFUL, etc.
 * - K-Blocks (grounded): Files that derive from principles
 * - Provisional: Files pending grounding
 * - Orphans: Files with no principle derivation
 *
 * @see spec/protocols/witness.md
 * @see docs/skills/metaphysical-fullstack.md
 */

import { memo, useState, useCallback, useMemo, useRef, useEffect } from 'react';
import {
  ChevronRight,
  ChevronDown,
  GitBranch,
  Eye,
  Layers,
  Network,
  List,
  GripVertical,
} from 'lucide-react';
import type { KBlock } from '../primitives/KBlockProjection/types';
import './ConstitutionalGraphView.css';

// =============================================================================
// Types
// =============================================================================

/**
 * Derivation graph: edges from K-Blocks to their constitutional principles.
 */
export interface DerivationEdge {
  /** Source K-Block ID */
  sourceId: string;
  /** Target principle name (COMPOSABLE, ETHICAL, etc.) */
  principle: string;
  /** Derivation strength (0-1, where 1 = strong derivation) */
  strength: number;
  /** Galois loss (coherence drift, 0 = perfect) */
  loss: number;
}

export interface DerivationGraph {
  /** All derivation edges */
  edges: DerivationEdge[];
  /** Principles in the constitution */
  principles: string[];
}

/**
 * View mode for the Constitutional Graph.
 */
export type ConstitutionalViewMode = 'tree' | 'graph' | 'layer';

/**
 * Derivation tier for layer view grouping.
 */
export type DerivationTier = 'AXIOM' | 'VALUE' | 'SPEC' | 'TUNING';

/**
 * Node status in the derivation graph.
 */
export type NodeStatus = 'grounded' | 'provisional' | 'orphan';

/**
 * Context menu action.
 */
export interface ContextMenuAction {
  id: string;
  label: string;
  icon?: React.ReactNode;
  action: () => void;
}

/**
 * Props for ConstitutionalGraphView.
 */
export interface ConstitutionalGraphViewProps {
  /** K-Blocks to display */
  kblocks: KBlock[];
  /** Derivation graph (edges from K-Blocks to principles) */
  derivationGraph: DerivationGraph;
  /** Currently selected K-Block ID */
  selectedId: string | null;
  /** Callback when a K-Block is selected */
  onSelect: (id: string) => void;
  /** Callback when an orphan is grounded to a principle */
  onGround: (kblockId: string, principle: string) => void;
  /** Initial view mode */
  initialViewMode?: ConstitutionalViewMode;
  /** Optional class name */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

/** Constitutional principles (the seven principles of kgents) */
const CONSTITUTIONAL_PRINCIPLES = [
  'TASTEFUL',
  'CURATED',
  'ETHICAL',
  'JOY_INDUCING',
  'COMPOSABLE',
  'HETERARCHICAL',
  'GENERATIVE',
] as const;

/** Principle colors (matching NavigationConstitutionalBadge) */
const PRINCIPLE_COLORS: Record<string, string> = {
  TASTEFUL: '#8ba98b', // glow-lichen
  CURATED: '#c4a77d', // glow-spore
  ETHICAL: '#4a6b4a', // life-sage (paramount)
  JOY_INDUCING: '#d4b88c', // glow-amber
  COMPOSABLE: '#6b8b6b', // life-mint
  HETERARCHICAL: '#8bab8b', // life-sprout
  GENERATIVE: '#e5c99d', // glow-light
};

/** Status colors */
const STATUS_COLORS: Record<NodeStatus, string> = {
  grounded: '#22c55e', // Green (derived)
  provisional: '#f59e0b', // Yellow (pending)
  orphan: '#ef4444', // Red (no derivation)
};

/** Tier colors for layer view */
const TIER_COLORS: Record<DerivationTier, string> = {
  AXIOM: '#440154', // Deep purple
  VALUE: '#31688e', // Blue
  SPEC: '#35b779', // Green
  TUNING: '#fde724', // Yellow
};

/** Map K-Block layer to derivation tier */
function getDerivationTier(kblock: KBlock): DerivationTier {
  if (!kblock.zeroSeedLayer) return 'TUNING';
  if (kblock.zeroSeedLayer <= 1) return 'AXIOM';
  if (kblock.zeroSeedLayer === 2) return 'VALUE';
  if (kblock.zeroSeedLayer <= 4) return 'SPEC';
  return 'TUNING';
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Determine the status of a K-Block in the derivation graph.
 */
function getKBlockStatus(kblock: KBlock, derivationGraph: DerivationGraph): NodeStatus {
  const hasEdge = derivationGraph.edges.some((e) => e.sourceId === kblock.id);

  if (!hasEdge) return 'orphan';

  // Check if any edge has sufficient strength
  const strongEdge = derivationGraph.edges.find(
    (e) => e.sourceId === kblock.id && e.strength >= 0.5
  );

  return strongEdge ? 'grounded' : 'provisional';
}

/**
 * Get the primary principle for a K-Block (strongest derivation).
 */
function getPrimaryPrinciple(kblockId: string, derivationGraph: DerivationGraph): string | null {
  const edges = derivationGraph.edges.filter((e) => e.sourceId === kblockId);
  if (edges.length === 0) return null;

  // Sort by strength descending
  const sorted = [...edges].sort((a, b) => b.strength - a.strength);
  return sorted[0].principle;
}

/**
 * Get downstream count (K-Blocks that derive from this one).
 */
function getDownstreamCount(kblockId: string, kblocks: KBlock[]): number {
  return kblocks.filter((kb) => kb.lineage.includes(kblockId)).length;
}

/**
 * Calculate node size based on downstream count.
 */
function getNodeSize(downstreamCount: number): number {
  // Base size 12, max 28
  return Math.min(28, 12 + Math.sqrt(downstreamCount) * 4);
}

/**
 * Calculate edge thickness based on derivation strength.
 */
function getEdgeThickness(loss: number): number {
  // Thickness is inverse of loss (1 - loss)
  // Range: 1px (max loss) to 4px (no loss)
  return 1 + (1 - loss) * 3;
}

// =============================================================================
// Sub-components
// =============================================================================

interface ConstitutionNodeProps {
  expanded: boolean;
  onToggle: () => void;
  principleCount: number;
  kblockCount: number;
}

const ConstitutionNode = memo(function ConstitutionNode({
  expanded,
  onToggle,
  principleCount,
  kblockCount,
}: ConstitutionNodeProps) {
  return (
    <button className="cgv-node cgv-node--constitution" onClick={onToggle} aria-expanded={expanded}>
      <span className="cgv-node__chevron">
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </span>
      <span className="cgv-node__icon cgv-node__icon--purple">&#9679;</span>
      <span className="cgv-node__label">CONSTITUTION</span>
      <span className="cgv-node__meta">
        {principleCount}P / {kblockCount}K
      </span>
    </button>
  );
});

interface PrincipleNodeProps {
  principle: string;
  expanded: boolean;
  onToggle: () => void;
  kblocks: KBlock[];
  derivationGraph: DerivationGraph;
  onDrop?: (kblockId: string) => void;
}

const PrincipleNode = memo(function PrincipleNode({
  principle,
  expanded,
  onToggle,
  kblocks,
  derivationGraph,
  onDrop,
}: PrincipleNodeProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  // Get K-Blocks grounded to this principle
  const groundedKBlocks = useMemo(() => {
    const edgeIds = derivationGraph.edges
      .filter((e) => e.principle === principle && e.strength >= 0.5)
      .map((e) => e.sourceId);
    return kblocks.filter((kb) => edgeIds.includes(kb.id));
  }, [principle, derivationGraph, kblocks]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const kblockId = e.dataTransfer.getData('text/kblock-id');
      if (kblockId && onDrop) {
        onDrop(kblockId);
      }
    },
    [onDrop]
  );

  const color = PRINCIPLE_COLORS[principle] || '#6b8b6b';

  return (
    <div
      className={`cgv-principle ${isDragOver ? 'cgv-principle--drag-over' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <button className="cgv-node cgv-node--principle" onClick={onToggle} aria-expanded={expanded}>
        <span className="cgv-node__chevron">
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </span>
        <span className="cgv-node__icon" style={{ color }}>
          &#9679;
        </span>
        <span className="cgv-node__label">{principle.replace('_', '-')}</span>
        <span className="cgv-node__count">{groundedKBlocks.length}</span>
      </button>
    </div>
  );
});

interface KBlockNodeProps {
  kblock: KBlock;
  status: NodeStatus;
  loss: number;
  isSelected: boolean;
  onSelect: () => void;
  onContextMenu: (e: React.MouseEvent) => void;
  draggable?: boolean;
}

const KBlockNode = memo(function KBlockNode({
  kblock,
  status,
  loss,
  isSelected,
  onSelect,
  onContextMenu,
  draggable = false,
}: KBlockNodeProps) {
  const handleDragStart = useCallback(
    (e: React.DragEvent) => {
      e.dataTransfer.setData('text/kblock-id', kblock.id);
      e.dataTransfer.effectAllowed = 'move';
    },
    [kblock.id]
  );

  // Extract filename from path
  const filename = kblock.path.split('/').pop() || kblock.id;
  const statusColor = STATUS_COLORS[status];

  return (
    <button
      className={`cgv-node cgv-node--kblock cgv-node--${status} ${
        isSelected ? 'cgv-node--selected' : ''
      }`}
      onClick={onSelect}
      onContextMenu={onContextMenu}
      draggable={draggable}
      onDragStart={draggable ? handleDragStart : undefined}
      title={kblock.path}
    >
      {draggable && (
        <span className="cgv-node__drag-handle">
          <GripVertical size={12} />
        </span>
      )}
      <span className="cgv-node__icon" style={{ color: statusColor }}>
        &#9679;
      </span>
      <span className="cgv-node__label">{filename}</span>
      <span className="cgv-node__loss" title={`Loss: ${loss.toFixed(2)}`}>
        L={loss.toFixed(2)}
      </span>
    </button>
  );
});

interface ContextMenuProps {
  x: number;
  y: number;
  actions: ContextMenuAction[];
  onClose: () => void;
}

const ContextMenu = memo(function ContextMenu({ x, y, actions, onClose }: ContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  return (
    <div ref={menuRef} className="cgv-context-menu" style={{ left: x, top: y }} role="menu">
      {actions.map((action) => (
        <button
          key={action.id}
          className="cgv-context-menu__item"
          onClick={() => {
            action.action();
            onClose();
          }}
          role="menuitem"
        >
          {action.icon && <span className="cgv-context-menu__icon">{action.icon}</span>}
          <span className="cgv-context-menu__label">{action.label}</span>
        </button>
      ))}
    </div>
  );
});

interface ViewModeToggleProps {
  mode: ConstitutionalViewMode;
  onChange: (mode: ConstitutionalViewMode) => void;
}

const ViewModeToggle = memo(function ViewModeToggle({ mode, onChange }: ViewModeToggleProps) {
  return (
    <div className="cgv-view-toggle" role="tablist">
      <button
        className={`cgv-view-toggle__btn ${mode === 'tree' ? 'cgv-view-toggle__btn--active' : ''}`}
        onClick={() => onChange('tree')}
        title="Tree view"
        role="tab"
        aria-selected={mode === 'tree'}
      >
        <List size={14} />
      </button>
      <button
        className={`cgv-view-toggle__btn ${mode === 'graph' ? 'cgv-view-toggle__btn--active' : ''}`}
        onClick={() => onChange('graph')}
        title="Graph view"
        role="tab"
        aria-selected={mode === 'graph'}
      >
        <Network size={14} />
      </button>
      <button
        className={`cgv-view-toggle__btn ${mode === 'layer' ? 'cgv-view-toggle__btn--active' : ''}`}
        onClick={() => onChange('layer')}
        title="Layer view"
        role="tab"
        aria-selected={mode === 'layer'}
      >
        <Layers size={14} />
      </button>
    </div>
  );
});

// =============================================================================
// Tree View
// =============================================================================

interface TreeViewProps {
  kblocks: KBlock[];
  derivationGraph: DerivationGraph;
  selectedId: string | null;
  onSelect: (id: string) => void;
  onGround: (kblockId: string, principle: string) => void;
  onContextMenu: (kblockId: string, e: React.MouseEvent) => void;
}

const TreeView = memo(function TreeView({
  kblocks,
  derivationGraph,
  selectedId,
  onSelect,
  onGround,
  onContextMenu,
}: TreeViewProps) {
  const [expandedPrinciples, setExpandedPrinciples] = useState<Set<string>>(
    new Set(CONSTITUTIONAL_PRINCIPLES)
  );
  const [constitutionExpanded, setConstitutionExpanded] = useState(true);
  const [provisionalExpanded, setProvisionalExpanded] = useState(true);
  const [orphansExpanded, setOrphansExpanded] = useState(true);

  // Categorize K-Blocks
  const categorized = useMemo(() => {
    const grounded: Map<string, KBlock[]> = new Map();
    const provisional: KBlock[] = [];
    const orphans: KBlock[] = [];

    // Initialize principle buckets
    CONSTITUTIONAL_PRINCIPLES.forEach((p) => grounded.set(p, []));

    // Helper to add K-Block to principle bucket
    const addToGrounded = (kb: KBlock, principle: string) => {
      const bucket = grounded.get(principle);
      if (bucket) {
        bucket.push(kb);
      }
    };

    kblocks.forEach((kb) => {
      const status = getKBlockStatus(kb, derivationGraph);
      if (status === 'orphan') {
        orphans.push(kb);
      } else if (status === 'provisional') {
        provisional.push(kb);
      } else {
        const principle = getPrimaryPrinciple(kb.id, derivationGraph);
        if (principle && grounded.has(principle)) {
          addToGrounded(kb, principle);
        } else {
          // Fallback to first principle with any edge
          const edge = derivationGraph.edges.find((e) => e.sourceId === kb.id);
          if (edge) {
            addToGrounded(kb, edge.principle);
          }
        }
      }
    });

    return { grounded, provisional, orphans };
  }, [kblocks, derivationGraph]);

  const togglePrinciple = useCallback((principle: string) => {
    setExpandedPrinciples((prev) => {
      const next = new Set(prev);
      if (next.has(principle)) {
        next.delete(principle);
      } else {
        next.add(principle);
      }
      return next;
    });
  }, []);

  const handleGroundToPrinciple = useCallback(
    (principle: string) => (kblockId: string) => {
      onGround(kblockId, principle);
    },
    [onGround]
  );

  return (
    <div className="cgv-tree">
      {/* Constitution Root */}
      <ConstitutionNode
        expanded={constitutionExpanded}
        onToggle={() => setConstitutionExpanded(!constitutionExpanded)}
        principleCount={CONSTITUTIONAL_PRINCIPLES.length}
        kblockCount={
          kblocks.filter((kb) => getKBlockStatus(kb, derivationGraph) === 'grounded').length
        }
      />

      {constitutionExpanded && (
        <div className="cgv-tree__children">
          {CONSTITUTIONAL_PRINCIPLES.map((principle) => {
            const principleKBlocks = categorized.grounded.get(principle) || [];
            const isExpanded = expandedPrinciples.has(principle);

            return (
              <div key={principle} className="cgv-tree__branch">
                <PrincipleNode
                  principle={principle}
                  expanded={isExpanded}
                  onToggle={() => togglePrinciple(principle)}
                  kblocks={kblocks}
                  derivationGraph={derivationGraph}
                  onDrop={handleGroundToPrinciple(principle)}
                />

                {isExpanded && principleKBlocks.length > 0 && (
                  <div className="cgv-tree__leaves">
                    {principleKBlocks.map((kb) => {
                      const edge = derivationGraph.edges.find(
                        (e) => e.sourceId === kb.id && e.principle === principle
                      );
                      return (
                        <KBlockNode
                          key={kb.id}
                          kblock={kb}
                          status="grounded"
                          loss={edge?.loss ?? 0}
                          isSelected={selectedId === kb.id}
                          onSelect={() => onSelect(kb.id)}
                          onContextMenu={(e) => onContextMenu(kb.id, e)}
                        />
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Provisional Section */}
      {categorized.provisional.length > 0 && (
        <div className="cgv-tree__section">
          <button
            className="cgv-node cgv-node--section cgv-node--provisional"
            onClick={() => setProvisionalExpanded(!provisionalExpanded)}
            aria-expanded={provisionalExpanded}
          >
            <span className="cgv-node__chevron">
              {provisionalExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </span>
            <span className="cgv-node__icon cgv-node__icon--yellow">&#9679;</span>
            <span className="cgv-node__label">PROVISIONAL</span>
            <span className="cgv-node__count">{categorized.provisional.length}</span>
          </button>

          {provisionalExpanded && (
            <div className="cgv-tree__leaves">
              {categorized.provisional.map((kb) => {
                const edge = derivationGraph.edges.find((e) => e.sourceId === kb.id);
                return (
                  <KBlockNode
                    key={kb.id}
                    kblock={kb}
                    status="provisional"
                    loss={edge?.loss ?? 0.5}
                    isSelected={selectedId === kb.id}
                    onSelect={() => onSelect(kb.id)}
                    onContextMenu={(e) => onContextMenu(kb.id, e)}
                    draggable
                  />
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Orphans Section */}
      {categorized.orphans.length > 0 && (
        <div className="cgv-tree__section">
          <button
            className="cgv-node cgv-node--section cgv-node--orphan"
            onClick={() => setOrphansExpanded(!orphansExpanded)}
            aria-expanded={orphansExpanded}
          >
            <span className="cgv-node__chevron">
              {orphansExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </span>
            <span className="cgv-node__icon cgv-node__icon--red">&#9679;</span>
            <span className="cgv-node__label">ORPHANS</span>
            <span className="cgv-node__count">{categorized.orphans.length}</span>
          </button>

          {orphansExpanded && (
            <div className="cgv-tree__leaves">
              {categorized.orphans.map((kb) => (
                <KBlockNode
                  key={kb.id}
                  kblock={kb}
                  status="orphan"
                  loss={1}
                  isSelected={selectedId === kb.id}
                  onSelect={() => onSelect(kb.id)}
                  onContextMenu={(e) => onContextMenu(kb.id, e)}
                  draggable
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Graph View (Force-Directed)
// =============================================================================

interface GraphViewProps {
  kblocks: KBlock[];
  derivationGraph: DerivationGraph;
  selectedId: string | null;
  onSelect: (id: string) => void;
  onContextMenu: (kblockId: string, e: React.MouseEvent) => void;
}

interface GraphNodePosition {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

const GraphView = memo(function GraphView({
  kblocks,
  derivationGraph,
  selectedId,
  onSelect,
  onContextMenu,
}: GraphViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [positions, setPositions] = useState<Map<string, GraphNodePosition>>(new Map());
  const animationRef = useRef<number | null>(null);

  // Initialize positions
  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;
    const centerX = width / 2;
    const centerY = height / 2;

    const newPositions = new Map<string, GraphNodePosition>();

    // Position constitution at center
    newPositions.set('CONSTITUTION', { x: centerX, y: 60, vx: 0, vy: 0 });

    // Position principles in a circle around constitution
    const principleRadius = 120;
    CONSTITUTIONAL_PRINCIPLES.forEach((principle, i) => {
      const angle = (i / CONSTITUTIONAL_PRINCIPLES.length) * 2 * Math.PI - Math.PI / 2;
      newPositions.set(principle, {
        x: centerX + Math.cos(angle) * principleRadius,
        y: 120 + Math.sin(angle) * principleRadius * 0.5,
        vx: 0,
        vy: 0,
      });
    });

    // Position K-Blocks with some randomness
    kblocks.forEach((kb) => {
      const angle = Math.random() * 2 * Math.PI;
      const radius = 200 + Math.random() * 100;
      newPositions.set(kb.id, {
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius * 0.7,
        vx: 0,
        vy: 0,
      });
    });

    setPositions(newPositions);

    // Simple force simulation
    const simulate = () => {
      setPositions((prev) => {
        const next = new Map(prev);
        const damping = 0.9;
        const repulsion = 500;
        const attraction = 0.01;

        // Apply forces between K-Blocks
        kblocks.forEach((kb) => {
          const pos = next.get(kb.id);
          if (!pos) return;

          let fx = 0;
          let fy = 0;

          // Repulsion from other K-Blocks
          kblocks.forEach((other) => {
            if (kb.id === other.id) return;
            const otherPos = next.get(other.id);
            if (!otherPos) return;

            const dx = pos.x - otherPos.x;
            const dy = pos.y - otherPos.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const force = repulsion / (dist * dist);

            fx += (dx / dist) * force;
            fy += (dy / dist) * force;
          });

          // Attraction to primary principle
          const principle = getPrimaryPrinciple(kb.id, derivationGraph);
          if (principle) {
            const principlePos = next.get(principle);
            if (principlePos) {
              const dx = principlePos.x - pos.x;
              const dy = principlePos.y - pos.y;
              fx += dx * attraction;
              fy += dy * attraction;
            }
          }

          // Update velocity and position
          pos.vx = (pos.vx + fx) * damping;
          pos.vy = (pos.vy + fy) * damping;
          pos.x += pos.vx;
          pos.y += pos.vy;

          // Boundary constraints
          pos.x = Math.max(30, Math.min(pos.x, (containerRef.current?.clientWidth || 400) - 30));
          pos.y = Math.max(30, Math.min(pos.y, (containerRef.current?.clientHeight || 400) - 30));
        });

        return next;
      });

      animationRef.current = requestAnimationFrame(simulate);
    };

    // Run simulation for a limited time
    let iterations = 0;
    const maxIterations = 100;
    const tick = () => {
      iterations++;
      if (iterations < maxIterations) {
        simulate();
        animationRef.current = requestAnimationFrame(tick);
      }
    };
    tick();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [kblocks, derivationGraph]);

  return (
    <div ref={containerRef} className="cgv-graph">
      <svg className="cgv-graph__svg">
        {/* Edges */}
        {derivationGraph.edges.map((edge) => {
          const sourcePos = positions.get(edge.sourceId);
          const targetPos = positions.get(edge.principle);
          if (!sourcePos || !targetPos) return null;

          const thickness = getEdgeThickness(edge.loss);

          return (
            <line
              key={`${edge.sourceId}-${edge.principle}`}
              className="cgv-graph__edge"
              x1={sourcePos.x}
              y1={sourcePos.y}
              x2={targetPos.x}
              y2={targetPos.y}
              strokeWidth={thickness}
              style={{
                stroke: PRINCIPLE_COLORS[edge.principle] || '#666',
                opacity: 0.3 + edge.strength * 0.7,
              }}
            />
          );
        })}
      </svg>

      {/* Constitution Node */}
      {positions.get('CONSTITUTION') && (
        <div
          className="cgv-graph__node cgv-graph__node--constitution"
          style={{
            left: positions.get('CONSTITUTION')!.x,
            top: positions.get('CONSTITUTION')!.y,
          }}
        >
          CONSTITUTION
        </div>
      )}

      {/* Principle Nodes */}
      {CONSTITUTIONAL_PRINCIPLES.map((principle) => {
        const pos = positions.get(principle);
        if (!pos) return null;

        return (
          <div
            key={principle}
            className="cgv-graph__node cgv-graph__node--principle"
            style={{
              left: pos.x,
              top: pos.y,
              borderColor: PRINCIPLE_COLORS[principle],
            }}
          >
            {principle.replace('_', '-')}
          </div>
        );
      })}

      {/* K-Block Nodes */}
      {kblocks.map((kb) => {
        const pos = positions.get(kb.id);
        if (!pos) return null;

        const status = getKBlockStatus(kb, derivationGraph);
        const downstreamCount = getDownstreamCount(kb.id, kblocks);
        const size = getNodeSize(downstreamCount);
        const filename = kb.path.split('/').pop() || kb.id;

        return (
          <button
            key={kb.id}
            className={`cgv-graph__node cgv-graph__node--kblock cgv-graph__node--${status} ${
              selectedId === kb.id ? 'cgv-graph__node--selected' : ''
            }`}
            style={{
              left: pos.x,
              top: pos.y,
              width: size * 2,
              height: size * 2,
            }}
            onClick={() => onSelect(kb.id)}
            onContextMenu={(e) => onContextMenu(kb.id, e)}
            title={filename}
          >
            <span className="cgv-graph__node-label">{filename.slice(0, 8)}</span>
          </button>
        );
      })}
    </div>
  );
});

// =============================================================================
// Layer View
// =============================================================================

interface LayerViewProps {
  kblocks: KBlock[];
  derivationGraph: DerivationGraph;
  selectedId: string | null;
  onSelect: (id: string) => void;
  onContextMenu: (kblockId: string, e: React.MouseEvent) => void;
}

const LayerView = memo(function LayerView({
  kblocks,
  derivationGraph,
  selectedId,
  onSelect,
  onContextMenu,
}: LayerViewProps) {
  // Group K-Blocks by tier
  const grouped = useMemo(() => {
    const tiers: Record<DerivationTier, KBlock[]> = {
      AXIOM: [],
      VALUE: [],
      SPEC: [],
      TUNING: [],
    };

    kblocks.forEach((kb) => {
      const tier = getDerivationTier(kb);
      tiers[tier].push(kb);
    });

    return tiers;
  }, [kblocks]);

  const tiers: DerivationTier[] = ['AXIOM', 'VALUE', 'SPEC', 'TUNING'];

  return (
    <div className="cgv-layer">
      {tiers.map((tier) => {
        const tierKBlocks = grouped[tier];
        if (tierKBlocks.length === 0) return null;

        return (
          <div key={tier} className="cgv-layer__tier">
            <div className="cgv-layer__tier-header" style={{ borderLeftColor: TIER_COLORS[tier] }}>
              <span className="cgv-layer__tier-name">{tier}</span>
              <span className="cgv-layer__tier-count">{tierKBlocks.length}</span>
            </div>
            <div className="cgv-layer__tier-content">
              {tierKBlocks.map((kb) => {
                const status = getKBlockStatus(kb, derivationGraph);
                const edge = derivationGraph.edges.find((e) => e.sourceId === kb.id);

                return (
                  <KBlockNode
                    key={kb.id}
                    kblock={kb}
                    status={status}
                    loss={edge?.loss ?? (status === 'orphan' ? 1 : 0.5)}
                    isSelected={selectedId === kb.id}
                    onSelect={() => onSelect(kb.id)}
                    onContextMenu={(e) => onContextMenu(kb.id, e)}
                  />
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const ConstitutionalGraphView = memo(function ConstitutionalGraphView({
  kblocks,
  derivationGraph,
  selectedId,
  onSelect,
  onGround,
  initialViewMode = 'tree',
  className = '',
}: ConstitutionalGraphViewProps) {
  const [viewMode, setViewMode] = useState<ConstitutionalViewMode>(initialViewMode);
  const [contextMenu, setContextMenu] = useState<{
    kblockId: string;
    x: number;
    y: number;
  } | null>(null);

  // Handle context menu
  const handleContextMenu = useCallback((kblockId: string, e: React.MouseEvent) => {
    e.preventDefault();
    setContextMenu({
      kblockId,
      x: e.clientX,
      y: e.clientY,
    });
  }, []);

  const closeContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  // Build context menu actions
  const contextMenuActions = useMemo<ContextMenuAction[]>(() => {
    if (!contextMenu) return [];

    const kblock = kblocks.find((kb) => kb.id === contextMenu.kblockId);
    if (!kblock) return [];

    return [
      {
        id: 'view-derivation',
        label: 'View Derivation',
        icon: <GitBranch size={14} />,
        action: () => {
          console.log('[ConstitutionalGraphView] View derivation:', kblock.id);
          // TODO: Implement derivation view navigation
        },
      },
      {
        id: 'show-downstream',
        label: 'Show Downstream',
        icon: <Eye size={14} />,
        action: () => {
          console.log('[ConstitutionalGraphView] Show downstream:', kblock.id);
          // TODO: Implement downstream view
        },
      },
    ];
  }, [contextMenu, kblocks]);

  return (
    <div className={`cgv ${className}`}>
      {/* Header */}
      <header className="cgv__header">
        <h3 className="cgv__title">Constitutional Graph</h3>
        <ViewModeToggle mode={viewMode} onChange={setViewMode} />
      </header>

      {/* Content */}
      <div className="cgv__content">
        {viewMode === 'tree' && (
          <TreeView
            kblocks={kblocks}
            derivationGraph={derivationGraph}
            selectedId={selectedId}
            onSelect={onSelect}
            onGround={onGround}
            onContextMenu={handleContextMenu}
          />
        )}

        {viewMode === 'graph' && (
          <GraphView
            kblocks={kblocks}
            derivationGraph={derivationGraph}
            selectedId={selectedId}
            onSelect={onSelect}
            onContextMenu={handleContextMenu}
          />
        )}

        {viewMode === 'layer' && (
          <LayerView
            kblocks={kblocks}
            derivationGraph={derivationGraph}
            selectedId={selectedId}
            onSelect={onSelect}
            onContextMenu={handleContextMenu}
          />
        )}
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          actions={contextMenuActions}
          onClose={closeContextMenu}
        />
      )}
    </div>
  );
});

// =============================================================================
// Exports
// =============================================================================

export default ConstitutionalGraphView;
