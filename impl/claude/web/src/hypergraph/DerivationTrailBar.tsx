/**
 * DerivationTrailBar — Constitutional derivation breadcrumb trail
 *
 * "The proof IS the decision. The mark IS the witness."
 *
 * Shows the user's current position in Constitutional space as a breadcrumb
 * from CONSTITUTION to their current K-Block, with Galois loss at each hop.
 *
 * Visual Design:
 * ```
 * ┌─ DERIVATION TRAIL ──────────────────────────────────────────────────┐
 * │ ⊙ CONSTITUTION → ◈ COMPOSABLE → ◇ witness.md → ○ mark.py → ● [YOU] │
 * │ [D=0]           L=0.00         L=0.08         L=0.15     [D=4]     │
 * │                                                    [Trace to Axiom]│
 * └─────────────────────────────────────────────────────────────────────┘
 * ```
 *
 * Features:
 * - Clickable nodes for navigation (click any node to jump)
 * - Derivation depth indicator (D=0 for axiom, D=N for current)
 * - Constitutional nodes highlighted with distinct green styling
 * - "Trace to Axiom" button (gG keyboard shortcut)
 * - Animated path tracing on hover
 *
 * States:
 * - Grounded: Full trail with green accents (derivation complete)
 * - Provisional: Trail with yellow warning (pending verification)
 * - Orphan: Shows "? → [YOU]" with "Click to ground" CTA
 *
 * Keyboard shortcuts (when HypergraphEditor focused):
 * - gh → Navigate to derivation parent
 * - gl → Navigate to derivation child
 * - gj → Navigate to next sibling
 * - gk → Navigate to prev sibling
 * - gG → Trace to axiom (genesis)
 *
 * @see spec/protocols/zero-seed.md (Constitutional derivation)
 * @see docs/skills/hypergraph-editor.md
 */

import { memo, useMemo, useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWindowLayout } from '../hooks/useLayoutContext';
import './DerivationTrailBar.css';

// =============================================================================
// Types
// =============================================================================

/**
 * A single node in the derivation path.
 */
export interface DerivationNode {
  /** Unique node identifier */
  id: string;
  /** Display label for the node */
  label: string;
  /** Node kind: constitution, principle, spec, impl, or kblock */
  kind: 'constitution' | 'principle' | 'spec' | 'impl' | 'kblock';
  /** Galois loss at this hop (0-1, where 0 = no loss, 1 = total loss) */
  galoisLoss: number;
  /** Optional tooltip/description */
  description?: string;
  /** Derivation depth (0 = axiom/constitution, N = N hops from root) */
  depth?: number;
  /** Whether this node is a constitutional/axiom node (L1) */
  isConstitutional?: boolean;
}

/**
 * Complete derivation path from constitution to current K-Block.
 */
export interface DerivationPath {
  /** Ordered nodes from root (constitution) to current */
  nodes: DerivationNode[];
  /** Derivation state */
  state: 'grounded' | 'provisional' | 'orphan';
  /** Total accumulated Galois loss */
  totalLoss: number;
  /** Optional message for provisional/orphan states */
  stateMessage?: string;
}

/**
 * Props for the DerivationTrailBar component.
 */
export interface DerivationTrailBarProps {
  /** Current K-Block identifier (null if no block focused) */
  currentKBlockId: string | null;
  /** Full derivation path (null if not computed or orphan) */
  derivationPath: DerivationPath | null;
  /** Handler for clicking a node in the trail */
  onNodeClick: (nodeId: string) => void;
  /** Handler for grounding an orphan K-Block */
  onGroundClick?: () => void;
  /** Handler for "Trace to Axiom" button (gG) */
  onTraceToAxiom?: () => void;
  /** Current derivation depth (0 = at axiom) */
  derivationDepth?: number;
  /** Show keyboard shortcut hints */
  showKeyboardHints?: boolean;
  /** Enable path tracing animation on hover */
  enablePathAnimation?: boolean;
  /** Additional CSS class names */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const GALOIS_LOSS_THRESHOLDS = {
  low: 0.1, // Green: minimal information loss
  medium: 0.25, // Yellow: moderate loss
  high: 0.5, // Red: significant loss
};

const NODE_KIND_CONFIG: Record<DerivationNode['kind'], { color: string; icon: string }> = {
  constitution: { color: '#22c55e', icon: '⊙' }, // Green - the ground
  principle: { color: '#3b82f6', icon: '◈' }, // Blue - core principles
  spec: { color: '#8b5cf6', icon: '◇' }, // Purple - specifications
  impl: { color: '#f59e0b', icon: '○' }, // Amber - implementations
  kblock: { color: '#ec4899', icon: '●' }, // Pink - current position
};

// Animation variants
const trailVariants = {
  hidden: { opacity: 0, y: -10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.2, staggerChildren: 0.05 },
  },
};

const nodeVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 },
  hover: { scale: 1.05 },
  tap: { scale: 0.95 },
};

const tooltipVariants = {
  hidden: { opacity: 0, y: 5, scale: 0.95 },
  visible: { opacity: 1, y: 0, scale: 1 },
};

// =============================================================================
// Subcomponents
// =============================================================================

/**
 * GaloisLossBadge — Shows loss value with color coding
 *
 * Color scheme:
 * - Green (0-0.1): Minimal loss, strong derivation
 * - Yellow (0.1-0.25): Moderate loss, derivation weakening
 * - Red (0.25+): Significant loss, weak derivation
 */
export interface GaloisLossBadgeProps {
  /** Loss value (0-1) */
  loss: number;
  /** Compact mode (number only) */
  compact?: boolean;
  /** Show as accumulated total */
  isTotal?: boolean;
  /** Additional class name */
  className?: string;
}

export const GaloisLossBadge = memo(function GaloisLossBadge({
  loss,
  compact = false,
  isTotal = false,
  className = '',
}: GaloisLossBadgeProps) {
  const getColor = (): string => {
    if (loss < GALOIS_LOSS_THRESHOLDS.low) return '#22c55e'; // Green
    if (loss < GALOIS_LOSS_THRESHOLDS.medium) return '#f59e0b'; // Yellow/Amber
    if (loss < GALOIS_LOSS_THRESHOLDS.high) return '#ef4444'; // Red
    return '#dc2626'; // Dark red for severe loss
  };

  const getBackgroundColor = (): string => {
    if (loss < GALOIS_LOSS_THRESHOLDS.low) return 'rgba(34, 197, 94, 0.1)';
    if (loss < GALOIS_LOSS_THRESHOLDS.medium) return 'rgba(245, 158, 11, 0.1)';
    if (loss < GALOIS_LOSS_THRESHOLDS.high) return 'rgba(239, 68, 68, 0.1)';
    return 'rgba(220, 38, 38, 0.15)';
  };

  const formattedLoss = loss.toFixed(2);
  const percentage = Math.round(loss * 100);

  return (
    <span
      className={`galois-loss-badge ${compact ? 'galois-loss-badge--compact' : ''} ${isTotal ? 'galois-loss-badge--total' : ''} ${className}`}
      style={{
        color: getColor(),
        backgroundColor: getBackgroundColor(),
        borderColor: getColor(),
      }}
      title={`Galois Loss: ${percentage}% information lost from parent`}
    >
      {!compact && <span className="galois-loss-badge__prefix">L=</span>}
      <span className="galois-loss-badge__value">{formattedLoss}</span>
    </span>
  );
});

/**
 * DepthBadge — Shows derivation depth indicator
 *
 * D=0 means at axiom (genesis)
 * D=N means N hops from axiom
 */
export interface DepthBadgeProps {
  depth: number;
  compact?: boolean;
}

export const DepthBadge = memo(function DepthBadge({ depth, compact = false }: DepthBadgeProps) {
  const isGenesis = depth === 0;
  const color = isGenesis ? '#22c55e' : '#64748b';
  const bgColor = isGenesis ? 'rgba(34, 197, 94, 0.15)' : 'rgba(100, 116, 139, 0.15)';

  return (
    <span
      className={`depth-badge ${compact ? 'depth-badge--compact' : ''} ${isGenesis ? 'depth-badge--genesis' : ''}`}
      style={{ color, backgroundColor: bgColor, borderColor: color }}
      title={isGenesis ? 'At axiom (genesis)' : `${depth} hops from axiom`}
    >
      D={depth}
    </span>
  );
});

/**
 * DerivationNodeChip — Single node in the trail
 *
 * Features:
 * - Clickable for navigation
 * - Hover shows derivation details tooltip
 * - Visual distinction by node kind
 * - Constitutional nodes have special green glow styling
 * - Shows depth badge on hover or when constitutional
 */
export interface DerivationNodeChipProps {
  /** The derivation node to display */
  node: DerivationNode;
  /** Whether this is the current/active node */
  isCurrent?: boolean;
  /** Whether this is the first (root) node */
  isRoot?: boolean;
  /** Click handler */
  onClick?: () => void;
  /** Compact mode */
  compact?: boolean;
  /** Index in the trail (for depth) */
  trailIndex?: number;
  /** Enable path tracing animation */
  enableAnimation?: boolean;
}

/**
 * NodeChipTooltip - Extracted tooltip for DerivationNodeChip
 */
const NodeChipTooltip = memo(function NodeChipTooltip({
  node,
  depth,
}: {
  node: DerivationNode;
  depth?: number;
}) {
  const nodeDepth = depth ?? node.depth ?? 0;
  const isConstitutional = node.isConstitutional || node.kind === 'constitution';

  return (
    <motion.div
      className="derivation-node-chip__tooltip"
      variants={tooltipVariants}
      initial="hidden"
      animate="visible"
      exit="hidden"
    >
      <div className="derivation-node-chip__tooltip-header">
        <span className="derivation-node-chip__tooltip-kind">{node.kind}</span>
        <span className="derivation-node-chip__tooltip-label">{node.label}</span>
      </div>
      {isConstitutional && (
        <div className="derivation-node-chip__tooltip-constitutional">Constitutional Axiom</div>
      )}
      {node.description && (
        <div className="derivation-node-chip__tooltip-desc">{node.description}</div>
      )}
      <div className="derivation-node-chip__tooltip-meta">
        <div className="derivation-node-chip__tooltip-depth">
          <span>Depth:</span>
          <DepthBadge depth={nodeDepth} compact />
        </div>
        <div className="derivation-node-chip__tooltip-loss">
          <span>Galois Loss:</span>
          <GaloisLossBadge loss={node.galoisLoss} compact />
        </div>
      </div>
      <div className="derivation-node-chip__tooltip-hint">Click to navigate</div>
    </motion.div>
  );
});

/**
 * Compute chip class names based on state
 */
function getChipClassName(
  isCurrent: boolean,
  isRoot: boolean,
  isConstitutional: boolean,
  enableAnimation: boolean
): string {
  const classes = ['derivation-node-chip'];
  if (isCurrent) classes.push('derivation-node-chip--current');
  if (isRoot) classes.push('derivation-node-chip--root');
  if (isConstitutional) classes.push('derivation-node-chip--constitutional');
  if (enableAnimation) classes.push('derivation-node-chip--animated');
  return classes.join(' ');
}

export const DerivationNodeChip = memo(function DerivationNodeChip({
  node,
  isCurrent = false,
  isRoot = false,
  onClick,
  compact = false,
  trailIndex = 0,
  enableAnimation = false,
}: DerivationNodeChipProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const [isTracing, setIsTracing] = useState(false);
  const config = NODE_KIND_CONFIG[node.kind];
  const chipLabel = compact ? truncateLabel(node.label, 12) : truncateLabel(node.label, 24);
  const showLossBadge = !isRoot && !isCurrent && node.galoisLoss > 0;
  const isConstitutional = node.isConstitutional || node.kind === 'constitution';
  const nodeDepth = node.depth ?? trailIndex;

  // Animation: trace effect on hover
  const handleMouseEnter = useCallback(() => {
    setShowTooltip(true);
    if (enableAnimation && !isCurrent) {
      setIsTracing(true);
    }
  }, [enableAnimation, isCurrent]);

  const handleMouseLeave = useCallback(() => {
    setShowTooltip(false);
    setIsTracing(false);
  }, []);

  // Handle keyboard activation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (onClick && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        onClick();
      }
    },
    [onClick]
  );

  return (
    <motion.div
      className={getChipClassName(isCurrent, isRoot, isConstitutional, isTracing)}
      variants={nodeVariants}
      whileHover="hover"
      whileTap={onClick ? 'tap' : undefined}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={`${node.label}, ${node.kind}, depth ${nodeDepth}${isCurrent ? ', current position' : ''}`}
      style={
        {
          '--node-color': config.color,
          '--animation-delay': `${trailIndex * 0.05}s`,
          cursor: onClick ? 'pointer' : 'default',
        } as React.CSSProperties
      }
    >
      <span className="derivation-node-chip__icon" aria-hidden="true">
        {config.icon}
      </span>
      <span className="derivation-node-chip__label">{chipLabel}</span>
      {isConstitutional && !compact && (
        <span
          className="derivation-node-chip__constitutional-badge"
          aria-label="Constitutional axiom"
        >
          L1
        </span>
      )}
      {isCurrent && (
        <span className="derivation-node-chip__current-badge" aria-label="Current position">
          YOU
        </span>
      )}
      {showLossBadge && <GaloisLossBadge loss={node.galoisLoss} compact={compact} />}
      <AnimatePresence>
        {showTooltip && <NodeChipTooltip node={node} depth={nodeDepth} />}
      </AnimatePresence>
    </motion.div>
  );
});

// =============================================================================
// State Colors
// =============================================================================

const STATE_COLORS: Record<string, string> = {
  grounded: '#22c55e',
  provisional: '#f59e0b',
  orphan: '#ef4444',
};

// =============================================================================
// Helper: Visible Node Computation
// =============================================================================

interface VisibleNode {
  node: DerivationNode;
  index: number;
  showEllipsis: boolean;
}

function computeVisibleNodes(nodes: DerivationNode[], maxVisible: number): VisibleNode[] {
  if (nodes.length <= maxVisible) {
    return nodes.map((node, index) => ({ node, index, showEllipsis: false }));
  }

  // Show: first + ellipsis + last (maxVisible-2)
  const result: VisibleNode[] = [
    { node: nodes[0], index: 0, showEllipsis: false },
    { node: nodes[0], index: -1, showEllipsis: true },
  ];

  const lastCount = maxVisible - 2;
  for (let i = nodes.length - lastCount; i < nodes.length; i++) {
    result.push({ node: nodes[i], index: i, showEllipsis: false });
  }

  return result;
}

// =============================================================================
// Orphan View Subcomponent
// =============================================================================

interface OrphanViewProps {
  currentKBlockId: string | null;
  stateMessage?: string;
  onGroundClick?: () => void;
  className: string;
}

const OrphanView = memo(function OrphanView({
  currentKBlockId,
  stateMessage,
  onGroundClick,
  className,
}: OrphanViewProps) {
  return (
    <motion.nav
      className={`derivation-trail-bar derivation-trail-bar--orphan ${className}`}
      aria-label="Derivation trail (orphan)"
      initial="hidden"
      animate="visible"
      variants={trailVariants}
    >
      <div className="derivation-trail-bar__header">
        <span className="derivation-trail-bar__label">DERIVATION</span>
        <span className="derivation-trail-bar__state" style={{ color: STATE_COLORS.orphan }}>
          ORPHAN
        </span>
      </div>

      <div className="derivation-trail-bar__content derivation-trail-bar__content--orphan">
        <motion.span
          className="derivation-trail-bar__orphan-mark"
          variants={nodeVariants}
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          ?
        </motion.span>

        <span className="derivation-trail-bar__separator" aria-hidden="true">
          →
        </span>

        <div className="derivation-trail-bar__current">
          <span className="derivation-trail-bar__current-icon">●</span>
          <span className="derivation-trail-bar__current-label">
            {currentKBlockId ? truncateLabel(currentKBlockId, 20) : 'Unknown'}
          </span>
          <span className="derivation-trail-bar__current-badge">YOU</span>
        </div>

        {onGroundClick && (
          <motion.button
            className="derivation-trail-bar__ground-btn"
            onClick={onGroundClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Click to ground
          </motion.button>
        )}
      </div>

      {stateMessage && <div className="derivation-trail-bar__message">{stateMessage}</div>}
    </motion.nav>
  );
});

// =============================================================================
// Trail Node List Item Subcomponent
// =============================================================================

interface TrailNodeItemProps {
  item: VisibleNode;
  displayIndex: number;
  totalNodes: number;
  onNodeClick: (nodeId: string) => void;
  isCompact: boolean;
  enableAnimation: boolean;
}

const TrailNodeItem = memo(function TrailNodeItem({
  item,
  displayIndex,
  totalNodes,
  onNodeClick,
  isCompact,
  enableAnimation,
}: TrailNodeItemProps) {
  if (item.showEllipsis) {
    return (
      <li key="ellipsis" className="derivation-trail-bar__ellipsis" aria-hidden="true">
        <span className="derivation-trail-bar__ellipsis-dots">...</span>
      </li>
    );
  }

  const isLast = displayIndex === totalNodes - 1;
  const isFirst = item.index === 0;

  return (
    <li key={`${item.node.id}-${item.index}`} className="derivation-trail-bar__node-item">
      <DerivationNodeChip
        node={item.node}
        isCurrent={isLast}
        isRoot={isFirst}
        onClick={!isLast ? () => onNodeClick(item.node.id) : undefined}
        compact={isCompact}
        trailIndex={item.index}
        enableAnimation={enableAnimation}
      />
      {!isLast && (
        <motion.span
          className="derivation-trail-bar__separator"
          aria-hidden="true"
          animate={enableAnimation ? { opacity: [0.3, 1, 0.3] } : undefined}
          transition={
            enableAnimation
              ? { duration: 1.5, repeat: Infinity, delay: item.index * 0.1 }
              : undefined
          }
        >
          →
        </motion.span>
      )}
    </li>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const DerivationTrailBar = memo(function DerivationTrailBar({
  currentKBlockId,
  derivationPath,
  onNodeClick,
  onGroundClick,
  onTraceToAxiom,
  derivationDepth,
  showKeyboardHints = false,
  enablePathAnimation = true,
  className = '',
}: DerivationTrailBarProps) {
  const { isMobile, isTablet } = useWindowLayout();
  const isCompact = isMobile || isTablet;
  const [isHovering, setIsHovering] = useState(false);

  const visibleNodes = useMemo(() => {
    if (!derivationPath?.nodes.length) return [];
    const maxVisible = isCompact ? 3 : 6;
    return computeVisibleNodes(derivationPath.nodes, maxVisible);
  }, [derivationPath?.nodes, isCompact]);

  const handleNodeClick = useCallback((nodeId: string) => onNodeClick(nodeId), [onNodeClick]);

  // Compute actual depth from path or use prop
  const actualDepth =
    derivationDepth ?? (derivationPath?.nodes.length ? derivationPath.nodes.length - 1 : 0);
  const isAtGenesis = actualDepth === 0;

  // Render orphan state
  if (!derivationPath || derivationPath.state === 'orphan') {
    return (
      <OrphanView
        currentKBlockId={currentKBlockId}
        stateMessage={derivationPath?.stateMessage}
        onGroundClick={onGroundClick}
        className={className}
      />
    );
  }

  const stateClass = derivationPath.state;
  const containerClass = `derivation-trail-bar derivation-trail-bar--${stateClass} ${isCompact ? 'derivation-trail-bar--compact' : ''} ${className}`;

  return (
    <motion.nav
      className={containerClass}
      aria-label="Derivation trail"
      initial="hidden"
      animate="visible"
      variants={trailVariants}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <div className="derivation-trail-bar__header">
        <span className="derivation-trail-bar__label">DERIVATION</span>
        <span className="derivation-trail-bar__state" style={{ color: STATE_COLORS[stateClass] }}>
          {stateClass.toUpperCase()}
        </span>
        {/* Depth indicator */}
        <DepthBadge depth={actualDepth} compact={isCompact} />
        {derivationPath.totalLoss > 0 && (
          <GaloisLossBadge loss={derivationPath.totalLoss} isTotal compact={isCompact} />
        )}
        {/* Trace to Axiom button */}
        {onTraceToAxiom && !isAtGenesis && (
          <motion.button
            className="derivation-trail-bar__trace-btn"
            onClick={onTraceToAxiom}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Trace to axiom (gG)"
          >
            <span className="derivation-trail-bar__trace-icon">⊙</span>
            {!isCompact && <span>Trace to Axiom</span>}
            {showKeyboardHints && <kbd className="derivation-trail-bar__kbd">gG</kbd>}
          </motion.button>
        )}
      </div>

      <div className="derivation-trail-bar__content">
        <ol className="derivation-trail-bar__nodes">
          {visibleNodes.map((item, displayIndex) => (
            <TrailNodeItem
              key={item.showEllipsis ? 'ellipsis' : `${item.node.id}-${item.index}`}
              item={item}
              displayIndex={displayIndex}
              totalNodes={visibleNodes.length}
              onNodeClick={handleNodeClick}
              isCompact={isCompact}
              enableAnimation={enablePathAnimation && isHovering}
            />
          ))}
        </ol>
      </div>

      {derivationPath.state === 'provisional' && derivationPath.stateMessage && (
        <motion.div
          className="derivation-trail-bar__warning"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <span className="derivation-trail-bar__warning-icon">⚠</span>
          {derivationPath.stateMessage}
        </motion.div>
      )}

      {/* Keyboard hints footer */}
      {showKeyboardHints && !isCompact && (
        <div className="derivation-trail-bar__hints">
          <span>
            <kbd>gh</kbd> parent
          </span>
          <span>
            <kbd>gl</kbd> child
          </span>
          <span>
            <kbd>gj</kbd>/<kbd>gk</kbd> siblings
          </span>
          <span>
            <kbd>gG</kbd> genesis
          </span>
        </div>
      )}
    </motion.nav>
  );
});

// =============================================================================
// Helpers
// =============================================================================

/**
 * Truncate a label to max length with ellipsis.
 */
function truncateLabel(label: string, maxLength: number): string {
  if (label.length <= maxLength) return label;
  return label.slice(0, maxLength - 3) + '...';
}

// =============================================================================
// Exports
// =============================================================================

export default DerivationTrailBar;
