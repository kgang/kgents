/**
 * BranchTree Component
 *
 * Visual session tree showing conversation branches using D3.js hierarchy layout.
 * SVG-based tree visualization inspired by git DAG with smooth Bezier curves.
 *
 * "The file is a lie. There is only the graph."
 *
 * Features:
 * - D3.js tree layout with proper hierarchical spacing
 * - Curved Bezier paths for branch connections
 * - Click branch to switch
 * - Hover for branch summary
 * - Right-click menu: Merge, Archive, Delete
 * - Visual indicator for current branch with animated glow
 * - Show turn count per branch
 * - Gradient-colored edges for active branches
 *
 * Implementation:
 * - Uses d3-hierarchy's tree() layout for optimal node positioning
 * - Separation function ensures proper spacing between siblings and cousins
 * - Smooth cubic Bezier curves for connection paths
 * - Animated pulse glow on active node
 * - Responsive scrollbars for large trees
 *
 * @see spec/protocols/chat-web.md §10.2
 */

import { useState, useRef, useEffect, type MouseEvent } from 'react';
import * as React from 'react';
import { hierarchy, tree as d3Tree } from 'd3-hierarchy';
import type { Branch, BranchTreeNode, MergeStrategy } from './useBranching';
import './BranchTree.css';

const MAX_BRANCHES = 3;

export interface BranchTreeProps {
  /** Branch tree structure */
  tree: BranchTreeNode | null;
  /** All branches (flat list) */
  branches: Branch[];
  /** Current active branch ID */
  currentBranch: string;
  /** Can create new fork */
  canFork: boolean;
  /** Switch to branch callback */
  onSwitchBranch: (branchId: string) => void;
  /** Merge branch callback */
  onMergeBranch: (branchId: string, strategy: MergeStrategy) => void;
  /** Archive branch callback */
  onArchiveBranch?: (branchId: string) => void;
  /** Delete branch callback */
  onDeleteBranch?: (branchId: string) => void;
  /** Compact mode (mobile) */
  compact?: boolean;
}

interface ContextMenuState {
  x: number;
  y: number;
  branchId: string;
}

interface TooltipState {
  x: number;
  y: number;
  branch: Branch;
}

/**
 * Visual session tree for branch navigation.
 *
 * @example
 * ```tsx
 * <BranchTree
 *   tree={tree}
 *   branches={branches}
 *   currentBranch={currentBranch}
 *   canFork={canFork}
 *   onSwitchBranch={switchBranch}
 *   onMergeBranch={merge}
 * />
 * ```
 */
export function BranchTree({
  tree,
  branches,
  currentBranch,
  canFork,
  onSwitchBranch,
  onMergeBranch,
  onArchiveBranch,
  onDeleteBranch,
  compact = false,
}: BranchTreeProps) {
  const [collapsed, setCollapsed] = useState(compact);
  const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Close context menu on outside click
  useEffect(() => {
    const handleClick = () => setContextMenu(null);
    if (contextMenu) {
      document.addEventListener('click', handleClick);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [contextMenu]);

  const handleNodeClick = (branch: Branch) => {
    if (!branch.is_merged) {
      onSwitchBranch(branch.id);
    }
  };

  const handleNodeRightClick = (e: MouseEvent, branch: Branch) => {
    e.preventDefault();
    if (!branch.is_merged) {
      setContextMenu({
        x: e.clientX,
        y: e.clientY,
        branchId: branch.id,
      });
    }
  };

  const handleNodeHover = (e: MouseEvent, branch: Branch) => {
    setTooltip({
      x: e.clientX + 10,
      y: e.clientY + 10,
      branch,
    });
  };

  const handleNodeLeave = () => {
    setTooltip(null);
  };

  const handleMerge = (branchId: string, strategy: MergeStrategy) => {
    onMergeBranch(branchId, strategy);
    setContextMenu(null);
  };

  const handleArchive = (branchId: string) => {
    onArchiveBranch?.(branchId);
    setContextMenu(null);
  };

  const handleDelete = (branchId: string) => {
    onDeleteBranch?.(branchId);
    setContextMenu(null);
  };

  if (!tree) {
    return (
      <div className="branch-tree">
        <div className="branch-tree__header">
          <div className="branch-tree__title">Branch Tree</div>
        </div>
        <div className="branch-tree__empty">
          <div className="branch-tree__empty-icon">⥮</div>
          <div>No branches yet</div>
        </div>
      </div>
    );
  }

  const activeBranches = branches.filter((b) => !b.is_merged);
  const showWarning = !canFork && activeBranches.length >= MAX_BRANCHES;

  return (
    <div className={`branch-tree ${collapsed ? 'branch-tree--collapsed' : ''}`}>
      <div className="branch-tree__header">
        <div className="branch-tree__title">
          Branch Tree
          <span className="branch-tree__count">
            {activeBranches.length}/{MAX_BRANCHES}
          </span>
        </div>
        <button
          className="branch-tree__toggle"
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? 'Expand tree' : 'Collapse tree'}
        >
          {collapsed ? '▼' : '▲'}
        </button>
      </div>

      {showWarning && !collapsed && (
        <div className="branch-tree__warning">
          <span className="branch-tree__warning-icon">◆</span>
          Maximum {MAX_BRANCHES} branches. Merge or archive to fork again.
        </div>
      )}

      {!collapsed && (
        <div className="branch-tree__svg">
          <BranchTreeSVG
            ref={svgRef}
            tree={tree}
            currentBranch={currentBranch}
            compact={compact}
            onNodeClick={handleNodeClick}
            onNodeRightClick={handleNodeRightClick}
            onNodeHover={handleNodeHover}
            onNodeLeave={handleNodeLeave}
          />
        </div>
      )}

      {/* Context Menu */}
      {contextMenu && (
        <BranchContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          branchId={contextMenu.branchId}
          currentBranch={currentBranch}
          onMerge={handleMerge}
          onArchive={handleArchive}
          onDelete={handleDelete}
        />
      )}

      {/* Tooltip */}
      {tooltip && (
        <BranchTooltip x={tooltip.x} y={tooltip.y} branch={tooltip.branch} />
      )}
    </div>
  );
}

/**
 * SVG tree renderer with D3-powered layout.
 */
const BranchTreeSVG = React.forwardRef<
  SVGSVGElement,
  {
    tree: BranchTreeNode;
    currentBranch: string;
    compact: boolean;
    onNodeClick: (branch: Branch) => void;
    onNodeRightClick: (e: MouseEvent, branch: Branch) => void;
    onNodeHover: (e: MouseEvent, branch: Branch) => void;
    onNodeLeave: () => void;
  }
>(({ tree, currentBranch, compact, onNodeClick, onNodeRightClick, onNodeHover, onNodeLeave }, ref) => {
  const layout = computeTreeLayout(tree, compact);
  const { width, height, nodes, edges } = layout;

  // Node size: square, not circle
  const nodeSize = compact ? 10 : 12;

  return (
    <svg
      ref={ref}
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="xMidYMid meet"
      style={{ overflow: 'visible' }}
    >
      {/* No gradients — 90% steel */}
      <defs>
        {/* Active edge: solid white */}
        <marker
          id="arrow-active"
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--brutalist-accent, #fff)" />
        </marker>
      </defs>

      {/* Edges - render first so they appear behind nodes */}
      <g className="branch-edges">
        {edges.map((edge) => {
          const isToActive = edge.target.branch.id === currentBranch;
          const isMerged = edge.target.branch.is_merged;
          return (
            <path
              key={`edge-${edge.source.branch.id}-${edge.target.branch.id}`}
              className={`branch-edge ${isToActive ? 'branch-edge--to-active' : ''} ${
                isMerged ? 'branch-edge--merged' : ''
              }`}
              d={edge.path}
              markerEnd={isToActive ? 'url(#arrow-active)' : undefined}
            />
          );
        })}
      </g>

      {/* Nodes — SQUARE, not circle */}
      <g className="branch-nodes">
        {nodes.map((node) => {
          const isActive = node.branch.id === currentBranch;
          const isMerged = node.branch.is_merged;
          return (
            <g
              key={node.branch.id}
              className={`branch-node ${isActive ? 'branch-node--active' : ''} ${
                isMerged ? 'branch-node--merged' : ''
              }`}
              transform={`translate(${node.x}, ${node.y})`}
              onClick={() => onNodeClick(node.branch)}
              onContextMenu={(e) => onNodeRightClick(e, node.branch)}
              onMouseEnter={(e) => onNodeHover(e, node.branch)}
              onMouseLeave={onNodeLeave}
              tabIndex={0}
              role="button"
              aria-label={`Branch: ${node.branch.branch_name} (${node.branch.turn_count} turns)`}
            >
              {/* Outer glow for active node ONLY (earned, not decorative) */}
              {isActive && (
                <rect
                  className="branch-node__glow"
                  x={-nodeSize - 4}
                  y={-nodeSize - 4}
                  width={(nodeSize + 4) * 2}
                  height={(nodeSize + 4) * 2}
                  fill="none"
                  stroke="var(--brutalist-accent, #fff)"
                  strokeWidth="1"
                  opacity="0.3"
                />
              )}
              {/* SQUARE node */}
              <rect
                className="branch-node__square"
                x={-nodeSize}
                y={-nodeSize}
                width={nodeSize * 2}
                height={nodeSize * 2}
              />
              {/* Branch name (hide in compact mode if too small) */}
              {!compact && (
                <text className="branch-node__label" y={-nodeSize - 8}>
                  {node.branch.branch_name}
                </text>
              )}
              {/* Turn count */}
              <text className="branch-node__turn-count" y={nodeSize + 16}>
                {compact ? node.branch.turn_count : `${node.branch.turn_count} turn${node.branch.turn_count === 1 ? '' : 's'}`}
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
});

BranchTreeSVG.displayName = 'BranchTreeSVG';

/**
 * Context menu for branch operations.
 */
function BranchContextMenu({
  x,
  y,
  branchId,
  currentBranch,
  onMerge,
  onArchive,
  onDelete,
}: {
  x: number;
  y: number;
  branchId: string;
  currentBranch: string;
  onMerge: (branchId: string, strategy: MergeStrategy) => void;
  onArchive?: (branchId: string) => void;
  onDelete?: (branchId: string) => void;
}) {
  const isCurrentBranch = branchId === currentBranch;

  return (
    <div className="branch-tree__context-menu" style={{ left: x, top: y }}>
      {!isCurrentBranch && (
        <>
          <button
            className="branch-tree__context-item"
            onClick={() => onMerge(branchId, 'sequential')}
          >
            <span className="branch-tree__context-icon">⇥</span>
            Merge (Sequential)
          </button>
          <button
            className="branch-tree__context-item"
            onClick={() => onMerge(branchId, 'interleave')}
          >
            <span className="branch-tree__context-icon">⇄</span>
            Merge (Interleave)
          </button>
          <button
            className="branch-tree__context-item"
            onClick={() => onMerge(branchId, 'manual')}
          >
            <span className="branch-tree__context-icon">⊕</span>
            Merge (Manual)
          </button>
          <div className="branch-tree__context-divider" />
        </>
      )}

      {onArchive && (
        <button className="branch-tree__context-item" onClick={() => onArchive(branchId)}>
          <span className="branch-tree__context-icon">◇</span>
          Archive
        </button>
      )}

      {onDelete && !isCurrentBranch && (
        <button
          className="branch-tree__context-item branch-tree__context-item--danger"
          onClick={() => onDelete(branchId)}
        >
          <span className="branch-tree__context-icon">◆</span>
          Delete
        </button>
      )}
    </div>
  );
}

/**
 * Tooltip showing branch summary.
 */
function BranchTooltip({ x, y, branch }: { x: number; y: number; branch: Branch }) {
  const createdDate = new Date(branch.created_at).toLocaleDateString();
  const activeDate = new Date(branch.last_active).toLocaleDateString();

  return (
    <div className="branch-tree__tooltip" style={{ left: x, top: y }}>
      <div className="branch-tree__tooltip-title">{branch.branch_name}</div>
      <div className="branch-tree__tooltip-meta">
        {branch.turn_count} turns • Created {createdDate}
      </div>
      <div className="branch-tree__tooltip-summary">
        {branch.is_merged ? (
          <>Merged into {branch.merged_into || 'main'}</>
        ) : (
          <>Last active {activeDate}</>
        )}
      </div>
    </div>
  );
}

/**
 * Compute tree layout for SVG rendering using D3.js hierarchy.
 *
 * Uses d3.tree() for proper hierarchical layout with ANGULAR paths (not curves).
 * "90% steel, 10% glow" — brutalist aesthetic, earned glow only.
 */

interface LayoutNode {
  branch: Branch;
  x: number;
  y: number;
}

interface LayoutEdge {
  source: LayoutNode;
  target: LayoutNode;
  path: string;
}

interface TreeLayout {
  width: number;
  height: number;
  nodes: LayoutNode[];
  edges: LayoutEdge[];
}

function computeTreeLayout(branchTree: BranchTreeNode, compact = false): TreeLayout {
  const NODE_SPACING = compact ? 80 : 120;
  const LEVEL_HEIGHT = compact ? 60 : 100;
  const PADDING = compact ? 30 : 50;

  // Convert BranchTreeNode to D3 hierarchy
  const root = hierarchy(branchTree, (d) => d.children);

  // Count leaves to determine width
  const leafCount = root.leaves().length;
  const width = Math.max(leafCount * NODE_SPACING, 300) + PADDING * 2;
  const height = (root.height + 1) * LEVEL_HEIGHT + PADDING * 2;

  // Create tree layout
  const treeLayout = d3Tree<BranchTreeNode>()
    .size([width - PADDING * 2, height - PADDING * 2])
    .separation((a, b) => (a.parent === b.parent ? 1 : 1.2));

  // Apply layout
  const treeData = treeLayout(root);

  // Extract nodes with positions
  const nodes: LayoutNode[] = [];
  treeData.each((node) => {
    nodes.push({
      branch: node.data.branch,
      x: node.x + PADDING,
      y: node.y + PADDING,
    });
  });

  // Extract edges with ANGULAR paths (not curved)
  // Brutalist aesthetic: right angles, no smoothness
  const edges: LayoutEdge[] = [];
  treeData.links().forEach((link) => {
    const source: LayoutNode = {
      branch: link.source.data.branch,
      x: link.source.x + PADDING,
      y: link.source.y + PADDING,
    };
    const target: LayoutNode = {
      branch: link.target.data.branch,
      x: link.target.x + PADDING,
      y: link.target.y + PADDING,
    };

    // ANGULAR path: vertical then horizontal (L-shape)
    // "The file is a lie. There is only the graph." — pure geometry
    const midY = (source.y + target.y) / 2;
    const path = `M ${source.x} ${source.y} L ${source.x} ${midY} L ${target.x} ${midY} L ${target.x} ${target.y}`;

    edges.push({ source, target, path });
  });

  return {
    width,
    height,
    nodes,
    edges,
  };
}

export default BranchTree;
