/**
 * ConstitutionalGraphView - Genesis Clean Slate Visualization
 *
 * Visualizes the 22 K-Blocks as a layered derivation graph:
 *
 * L3: ARCHITECTURE   [ASHC] [Fullstack] [Editor] [AGENTESE]
 *         ^               ^          ^         ^
 * L2: PRINCIPLES    [TASTEFUL] [CURATED] [ETHICAL] [JOY] [COMPOSABLE] [HETERO] [GENERATIVE]
 *         ^               ^          ^         ^
 * L1: KERNEL        [Compose] [Judge] [Ground] [Id] [Contradict] [Sublate] [Fix]
 *         ^               ^          ^         ^
 * L0: AXIOMS        [Entity] [Morphism] [Mirror] [Galois]
 *
 * "The constitution is the root. Principles derive from axioms.
 *  Architecture derives from principles. The graph IS the system."
 *
 * @see spec/protocols/clean-slate.md
 * @see docs/skills/hypergraph-editor.md
 */

import { memo, useMemo, useCallback, useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, type Variants } from 'framer-motion';
import { useMotionPreferences } from '../joy/useMotionPreferences';
import './ConstitutionalGraphView.css';

// =============================================================================
// Types
// =============================================================================

/**
 * K-Block for the clean slate visualization.
 * Represents a constitutional building block at a specific layer.
 */
export interface CleanSlateKBlock {
  /** Unique identifier */
  id: string;
  /** Human-readable title */
  title: string;
  /** Full content/description */
  content: string;
  /** Layer in the derivation hierarchy (0-3) */
  layer: 0 | 1 | 2 | 3;
  /** Galois loss (0 = perfect preservation, 1 = complete loss) */
  galoisLoss: number;
  /** IDs of parent K-Blocks this derives from */
  parentIds: string[];
  /** Optional metadata */
  meta?: {
    createdAt?: Date;
    author?: string;
    tags?: string[];
  };
}

/**
 * An edge in the derivation graph.
 */
export interface DerivationEdge {
  /** Source K-Block ID (child/more concrete) */
  sourceId: string;
  /** Target K-Block ID (parent/more abstract) */
  targetId: string;
  /** Galois loss for this derivation step */
  galoisLoss: number;
}

/**
 * Props for ConstitutionalGraphView component.
 */
export interface ConstitutionalGraphViewProps {
  /** K-Blocks to display */
  kblocks: CleanSlateKBlock[];
  /** Derivation edges between K-Blocks */
  edges: DerivationEdge[];
  /** Currently selected K-Block ID */
  selectedId?: string;
  /** Callback when a K-Block is clicked */
  onNodeClick?: (id: string) => void;
  /** Whether data is loading */
  isLoading?: boolean;
}

/**
 * Props for individual node component.
 */
interface NodeProps {
  kblock: CleanSlateKBlock;
  isSelected: boolean;
  onClick: () => void;
  index: number;
}

// =============================================================================
// Constants - LIVING_EARTH Palette
// =============================================================================

/** Layer colors following the LIVING_EARTH palette */
const LAYER_COLORS: Record<number, string> = {
  0: '#c4a77d', // L0: AXIOMS - amber/honey glow
  1: '#6b8b6b', // L1: KERNEL - sage green
  2: '#8b7355', // L2: PRINCIPLES - earth brown
  3: '#f5f0e6', // L3: ARCHITECTURE - lantern/sand
};

/** Layer labels */
const LAYER_LABELS: Record<number, string> = {
  0: 'AXIOMS',
  1: 'KERNEL',
  2: 'PRINCIPLES',
  3: 'ARCHITECTURE',
};

/** Get color intensity based on Galois loss */
function getLossColor(loss: number): string {
  // Green (low loss) -> Yellow -> Red (high loss)
  if (loss < 0.2) return '#22c55e';
  if (loss < 0.5) return '#f59e0b';
  return '#ef4444';
}

/** Get opacity based on Galois loss */
function getLossOpacity(loss: number): number {
  // Higher loss = lower opacity (0.3 to 0.9)
  return 0.9 - loss * 0.6;
}

// =============================================================================
// Animation Variants
// =============================================================================

const nodeVariants: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.8,
    y: 10,
  },
  visible: (index: number) => ({
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      delay: index * 0.05,
      duration: 0.3,
      ease: [0.25, 0.46, 0.45, 0.94],
    },
  }),
  selected: {
    scale: 1.05,
    boxShadow: '0 0 20px rgba(107, 139, 107, 0.6)',
    transition: {
      duration: 0.3,
      repeat: Infinity,
      repeatType: 'reverse',
    },
  },
};

const edgeVariants: Variants = {
  hidden: {
    pathLength: 0,
    opacity: 0,
  },
  visible: (index: number) => ({
    pathLength: 1,
    opacity: 1,
    transition: {
      pathLength: {
        delay: 0.3 + index * 0.02,
        duration: 0.5,
        ease: 'easeInOut',
      },
      opacity: {
        delay: 0.3 + index * 0.02,
        duration: 0.2,
      },
    },
  }),
};

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

// =============================================================================
// Sub-components
// =============================================================================

/**
 * Tooltip component for node hover state.
 */
const NodeTooltip = memo(function NodeTooltip({
  kblock,
  visible,
}: {
  kblock: CleanSlateKBlock;
  visible: boolean;
}) {
  if (!visible) return null;

  return (
    <motion.div
      className="genesis-graph__tooltip"
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 5 }}
    >
      <div className="genesis-graph__tooltip-title">{kblock.title}</div>
      <div className="genesis-graph__tooltip-content">{kblock.content}</div>
      <div className="genesis-graph__tooltip-meta">
        <span>Layer: {LAYER_LABELS[kblock.layer]}</span>
        <span>Loss: {(kblock.galoisLoss * 100).toFixed(1)}%</span>
      </div>
    </motion.div>
  );
});

/**
 * Individual K-Block node component.
 */
const KBlockNode = memo(function KBlockNode({ kblock, isSelected, onClick, index }: NodeProps) {
  const { shouldAnimate } = useMotionPreferences();
  const [isHovered, setIsHovered] = useState(false);
  const nodeRef = useRef<HTMLButtonElement>(null);

  const layerColor = LAYER_COLORS[kblock.layer];
  const lossColor = getLossColor(kblock.galoisLoss);

  // Truncate title if too long
  const displayTitle = kblock.title.length > 12 ? kblock.title.slice(0, 10) + '...' : kblock.title;

  const handleMouseEnter = useCallback(() => setIsHovered(true), []);
  const handleMouseLeave = useCallback(() => setIsHovered(false), []);

  if (!shouldAnimate) {
    return (
      <button
        ref={nodeRef}
        className={`genesis-graph__node genesis-graph__node--l${kblock.layer} ${
          isSelected ? 'genesis-graph__node--selected' : ''
        }`}
        onClick={onClick}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        style={{ '--node-color': layerColor } as React.CSSProperties}
        title={kblock.title}
      >
        <span className="genesis-graph__node-badge">[L{kblock.layer}]</span>
        <span className="genesis-graph__node-title">{displayTitle}</span>
        <span className="genesis-graph__node-loss" style={{ backgroundColor: lossColor }} />
        <AnimatePresence>
          {isHovered && <NodeTooltip kblock={kblock} visible={isHovered} />}
        </AnimatePresence>
      </button>
    );
  }

  return (
    <motion.button
      ref={nodeRef}
      className={`genesis-graph__node genesis-graph__node--l${kblock.layer} ${
        isSelected ? 'genesis-graph__node--selected' : ''
      }`}
      variants={nodeVariants}
      initial="hidden"
      animate={isSelected ? 'selected' : 'visible'}
      custom={index}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{ '--node-color': layerColor } as React.CSSProperties}
      title={kblock.title}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.98 }}
    >
      <span className="genesis-graph__node-badge">[L{kblock.layer}]</span>
      <span className="genesis-graph__node-title">{displayTitle}</span>
      <span className="genesis-graph__node-loss" style={{ backgroundColor: lossColor }} />
      <AnimatePresence>
        {isHovered && <NodeTooltip kblock={kblock} visible={isHovered} />}
      </AnimatePresence>
    </motion.button>
  );
});

/**
 * SVG edge connecting two nodes.
 */
interface EdgePathProps {
  edge: DerivationEdge;
  sourcePos: { x: number; y: number };
  targetPos: { x: number; y: number };
  index: number;
}

const EdgePath = memo(function EdgePath({ edge, sourcePos, targetPos, index }: EdgePathProps) {
  const { shouldAnimate } = useMotionPreferences();
  const opacity = getLossOpacity(edge.galoisLoss);

  // Calculate control points for curved path
  const midY = (sourcePos.y + targetPos.y) / 2;
  const path = `M ${sourcePos.x} ${sourcePos.y}
                C ${sourcePos.x} ${midY},
                  ${targetPos.x} ${midY},
                  ${targetPos.x} ${targetPos.y}`;

  if (!shouldAnimate) {
    return (
      <path
        className="genesis-graph__edge"
        d={path}
        fill="none"
        stroke={LAYER_COLORS[0]}
        strokeWidth={2}
        opacity={opacity}
      />
    );
  }

  return (
    <motion.path
      className="genesis-graph__edge"
      d={path}
      fill="none"
      stroke={LAYER_COLORS[0]}
      strokeWidth={2}
      opacity={opacity}
      variants={edgeVariants}
      initial="hidden"
      animate="visible"
      custom={index}
    />
  );
});

/**
 * Loading skeleton for the graph.
 */
const LoadingSkeleton = memo(function LoadingSkeleton() {
  return (
    <div className="genesis-graph__loading">
      {[3, 2, 1, 0].map((layer) => (
        <div key={layer} className="genesis-graph__layer genesis-graph__layer--skeleton">
          <span className="genesis-graph__layer-label">{LAYER_LABELS[layer]}</span>
          <div className="genesis-graph__layer-nodes">
            {Array.from({ length: layer === 2 ? 7 : layer === 1 ? 7 : 4 }).map((_, i) => (
              <div key={i} className="genesis-graph__node genesis-graph__node--skeleton" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const ConstitutionalGraphView = memo(function ConstitutionalGraphView({
  kblocks,
  edges,
  selectedId,
  onNodeClick,
  isLoading = false,
}: ConstitutionalGraphViewProps) {
  const { shouldAnimate } = useMotionPreferences();
  const containerRef = useRef<HTMLDivElement>(null);
  const [nodePositions, setNodePositions] = useState<Map<string, { x: number; y: number }>>(
    new Map()
  );

  // Group K-Blocks by layer
  const layeredKBlocks = useMemo(() => {
    const layers: Map<number, CleanSlateKBlock[]> = new Map([
      [0, []],
      [1, []],
      [2, []],
      [3, []],
    ]);

    kblocks.forEach((kb) => {
      const layer = layers.get(kb.layer);
      if (layer) {
        layer.push(kb);
      }
    });

    return layers;
  }, [kblocks]);

  // Calculate node positions after render
  useEffect(() => {
    if (!containerRef.current) return;

    const updatePositions = () => {
      const container = containerRef.current;
      if (!container) return;

      const newPositions = new Map<string, { x: number; y: number }>();
      const nodeElements = container.querySelectorAll('[data-kblock-id]');

      nodeElements.forEach((el) => {
        const id = el.getAttribute('data-kblock-id');
        if (id) {
          const rect = el.getBoundingClientRect();
          const containerRect = container.getBoundingClientRect();
          newPositions.set(id, {
            x: rect.left - containerRect.left + rect.width / 2,
            y: rect.top - containerRect.top + rect.height / 2,
          });
        }
      });

      setNodePositions(newPositions);
    };

    // Update after animation completes
    const timer = setTimeout(updatePositions, 500);
    window.addEventListener('resize', updatePositions);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', updatePositions);
    };
  }, [kblocks]);

  // Handle node click
  const handleNodeClick = useCallback(
    (id: string) => {
      onNodeClick?.(id);
    },
    [onNodeClick]
  );

  // Render edges between nodes
  const renderedEdges = useMemo(() => {
    if (nodePositions.size === 0) return null;

    return edges.map((edge, index) => {
      const sourcePos = nodePositions.get(edge.sourceId);
      const targetPos = nodePositions.get(edge.targetId);

      if (!sourcePos || !targetPos) return null;

      return (
        <EdgePath
          key={`${edge.sourceId}-${edge.targetId}`}
          edge={edge}
          sourcePos={sourcePos}
          targetPos={targetPos}
          index={index}
        />
      );
    });
  }, [edges, nodePositions]);

  if (isLoading) {
    return (
      <div className="genesis-graph">
        <header className="genesis-graph__header">
          <h3 className="genesis-graph__title">Constitutional Derivation Graph</h3>
        </header>
        <LoadingSkeleton />
      </div>
    );
  }

  const Container = shouldAnimate ? motion.div : 'div';
  const containerProps = shouldAnimate
    ? {
        variants: containerVariants,
        initial: 'hidden',
        animate: 'visible',
      }
    : {};

  return (
    <div className="genesis-graph" ref={containerRef}>
      <header className="genesis-graph__header">
        <h3 className="genesis-graph__title">Constitutional Derivation Graph</h3>
        <div className="genesis-graph__legend">
          {[3, 2, 1, 0].map((layer) => (
            <span
              key={layer}
              className="genesis-graph__legend-item"
              style={{ '--legend-color': LAYER_COLORS[layer] } as React.CSSProperties}
            >
              L{layer}
            </span>
          ))}
        </div>
      </header>

      <div className="genesis-graph__content">
        {/* SVG layer for edges */}
        <svg className="genesis-graph__svg">{renderedEdges}</svg>

        {/* Layers (bottom to top: L0 -> L3) */}
        <Container className="genesis-graph__layers" {...containerProps}>
          {[3, 2, 1, 0].map((layer) => {
            const layerKBlocks = layeredKBlocks.get(layer) || [];
            let nodeIndex = 0;

            // Calculate starting index for stagger animation
            for (let i = 3; i > layer; i--) {
              nodeIndex += (layeredKBlocks.get(i) || []).length;
            }

            return (
              <div key={layer} className={`genesis-graph__layer genesis-graph__layer--l${layer}`}>
                <span className="genesis-graph__layer-label">{LAYER_LABELS[layer]}</span>
                <div className="genesis-graph__layer-nodes">
                  {layerKBlocks.map((kb, i) => (
                    <div key={kb.id} data-kblock-id={kb.id}>
                      <KBlockNode
                        kblock={kb}
                        isSelected={selectedId === kb.id}
                        onClick={() => handleNodeClick(kb.id)}
                        index={nodeIndex + i}
                      />
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </Container>
      </div>
    </div>
  );
});

// =============================================================================
// Exports
// =============================================================================

export default ConstitutionalGraphView;
