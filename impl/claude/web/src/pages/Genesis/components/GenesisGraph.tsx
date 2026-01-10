/**
 * GenesisGraph - Phases 2-4: Illumination, Exploration, Connection
 *
 * "The Constitutional Graph IS the system."
 *
 * Features:
 * - Layer tabs (L0/L1/L2/L3) with framer-motion transitions
 * - K-Block nodes with hover states and selection
 * - Animated derivation edges (draw-on-scroll style)
 * - 4-7-8 breathing animation for selected nodes
 * - Detail panel with derivation info
 * - Phase-aware content (illumination shows overview, exploration enables interaction)
 *
 * LIVING_EARTH Palette:
 * - L0: #c4a77d (amber/honey) - warmest
 * - L1: #6b8b6b (sage green)
 * - L2: #8b7355 (earth brown)
 * - L3: #f5f0e6 (sand) - coolest
 *
 * @see spec/protocols/genesis-clean-slate.md
 */

import { memo, useMemo, useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type {
  CleanSlateStatusResponse,
  DerivationGraphResponse,
  CleanSlateKBlock,
} from '../../../api/client';
import type { LayerInfo, GenesisPhase } from '../GenesisExperience';

// =============================================================================
// Types
// =============================================================================

interface GenesisGraphProps {
  /** Full derivation graph data */
  graph: DerivationGraphResponse;
  /** Status data */
  status: CleanSlateStatusResponse;
  /** Currently selected layer tab */
  selectedLayer: 0 | 1 | 2 | 3;
  /** Currently selected K-Block ID */
  selectedId: string | null;
  /** Layer metadata */
  layerInfo: Record<number, LayerInfo>;
  /** K-Block counts per layer */
  layerCounts: Record<number, number>;
  /** Current phase */
  phase: GenesisPhase;
  /** Layer tab change handler */
  onLayerChange: (layer: 0 | 1 | 2 | 3) => void;
  /** Node selection handler */
  onNodeSelect: (id: string) => void;
  /** Continue to next phase */
  onContinue: () => void;
}

// =============================================================================
// Animation Variants
// =============================================================================

const tabVariants = {
  inactive: {
    backgroundColor: 'rgba(42, 37, 34, 0.8)',
    color: '#a39890',
    borderBottomColor: 'transparent',
  },
  active: {
    backgroundColor: 'rgba(42, 37, 34, 1)',
    color: '#e5e0db',
    borderBottomColor: 'var(--layer-color)',
  },
};

const nodeContainerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.2,
    },
  },
};

const nodeVariants = {
  hidden: {
    opacity: 0,
    scale: 0.8,
    y: 10,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: [0.25, 0.46, 0.45, 0.94] as const,
    },
  },
};

const detailVariants = {
  hidden: {
    opacity: 0,
    x: 20,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut' as const,
    },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: {
      duration: 0.2,
    },
  },
};

// 4-7-8 breathing for selected node - combined animation + transition
const getBreathingProps = (layerColor: string) => ({
  animate: {
    scale: [1, 1.03, 1.03, 1],
    boxShadow: [
      `0 0 0 0 ${layerColor}66`,
      `0 0 20px 8px ${layerColor}99`,
      `0 0 20px 8px ${layerColor}99`,
      `0 0 0 0 ${layerColor}66`,
    ],
  },
  transition: {
    duration: 19,
    times: [0, 0.21, 0.58, 1],
    repeat: Infinity,
    ease: 'easeInOut',
  },
});

// =============================================================================
// Sub-components
// =============================================================================

interface LayerTabProps {
  layer: 0 | 1 | 2 | 3;
  info: LayerInfo;
  count: number;
  isActive: boolean;
  onClick: () => void;
}

const LayerTab = memo(function LayerTab({ layer, info, count, isActive, onClick }: LayerTabProps) {
  return (
    <motion.button
      className={`genesis-graph__tab ${isActive ? 'genesis-graph__tab--active' : ''}`}
      style={{ '--layer-color': info.color } as React.CSSProperties}
      variants={tabVariants}
      animate={isActive ? 'active' : 'inactive'}
      onClick={onClick}
      whileHover={{ backgroundColor: 'rgba(50, 45, 42, 1)' }}
    >
      <span className="genesis-graph__tab-layer">L{layer}</span>
      <span className="genesis-graph__tab-name">{info.name}</span>
      <span className="genesis-graph__tab-count">{count}</span>
    </motion.button>
  );
});

interface KBlockNodeProps {
  kblock: CleanSlateKBlock;
  isSelected: boolean;
  layerColor: string;
  onClick: () => void;
  index: number;
}

const KBlockNode = memo(function KBlockNode({
  kblock,
  isSelected,
  layerColor,
  onClick,
  index,
}: KBlockNodeProps) {
  // Extract short name from ID (e.g., "genesis:L0:entity" -> "Entity")
  const shortName = useMemo(() => {
    const parts = kblock.id.split(':');
    const name = parts[parts.length - 1];
    return name.charAt(0).toUpperCase() + name.slice(1).replace(/-/g, ' ');
  }, [kblock.id]);

  const lossColor = useMemo(() => {
    if (kblock.galois_loss < 0.1) return '#22c55e'; // Green
    if (kblock.galois_loss < 0.3) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  }, [kblock.galois_loss]);

  // Get breathing props for selected state
  const breathingProps = isSelected ? getBreathingProps(layerColor) : {};

  return (
    <motion.button
      className={`genesis-graph__node ${isSelected ? 'genesis-graph__node--selected' : ''}`}
      style={{ '--node-color': layerColor } as React.CSSProperties}
      variants={nodeVariants}
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.98 }}
      {...breathingProps}
      title={kblock.title}
    >
      <span className="genesis-graph__node-badge" style={{ borderColor: layerColor }}>
        L{kblock.layer}
      </span>
      <span className="genesis-graph__node-title">{shortName}</span>
      <span
        className="genesis-graph__node-loss"
        style={{ backgroundColor: lossColor }}
        title={`Galois Loss: ${(kblock.galois_loss * 100).toFixed(1)}%`}
      />
    </motion.button>
  );
});

interface KBlockDetailProps {
  kblock: CleanSlateKBlock | null;
  layerInfo: Record<number, LayerInfo>;
  allNodes: CleanSlateKBlock[];
}

const KBlockDetail = memo(function KBlockDetail({
  kblock,
  layerInfo,
  allNodes,
}: KBlockDetailProps) {
  // Find parent K-Blocks by ID - must be called unconditionally (React hooks rules)
  const parents = useMemo(() => {
    if (!kblock) return [];
    return kblock.derives_from
      .map((parentId) => allNodes.find((n) => n.id === parentId))
      .filter((p): p is CleanSlateKBlock => p !== undefined);
  }, [kblock, allNodes]);

  if (!kblock) {
    return (
      <motion.div
        className="genesis-graph__detail genesis-graph__detail--empty"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <p className="genesis-graph__detail-placeholder">Select a K-Block to view details</p>
      </motion.div>
    );
  }

  const info = layerInfo[kblock.layer];

  return (
    <motion.div
      className="genesis-graph__detail"
      key={kblock.id}
      variants={detailVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
    >
      {/* Header */}
      <div className="genesis-graph__detail-header">
        <span className="genesis-graph__detail-layer" style={{ color: info.color }}>
          {info.name}
        </span>
        <span className="genesis-graph__detail-loss">
          Loss: {(kblock.galois_loss * 100).toFixed(1)}%
        </span>
      </div>

      {/* Title */}
      <h3 className="genesis-graph__detail-title">{kblock.title}</h3>

      {/* ID */}
      <p className="genesis-graph__detail-id">{kblock.id}</p>

      {/* Content */}
      {kblock.content && <p className="genesis-graph__detail-content">{kblock.content}</p>}

      {/* Derivations */}
      {parents.length > 0 && (
        <div className="genesis-graph__detail-derivations">
          <span className="genesis-graph__detail-label">Derives from:</span>
          <div className="genesis-graph__detail-parents">
            {parents.map((parent) => (
              <span
                key={parent.id}
                className="genesis-graph__detail-parent"
                style={{ borderColor: layerInfo[parent.layer].color }}
              >
                {parent.title}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tags */}
      {kblock.tags.length > 0 && (
        <div className="genesis-graph__detail-tags">
          {kblock.tags.map((tag) => (
            <span key={tag} className="genesis-graph__detail-tag">
              {tag}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
});

interface DerivationEdgesProps {
  edges: Array<{ from: string; to: string }>;
  nodes: CleanSlateKBlock[];
  selectedId: string | null;
  containerRef: React.RefObject<HTMLDivElement>;
}

const DerivationEdges = memo(function DerivationEdges({
  edges,
  nodes,
  selectedId,
  containerRef,
}: DerivationEdgesProps) {
  const [positions, setPositions] = useState<Map<string, { x: number; y: number }>>(new Map());

  // Calculate node positions after render
  useEffect(() => {
    const updatePositions = () => {
      if (!containerRef.current) return;

      const container = containerRef.current;
      const nodeElements = container.querySelectorAll('[data-kblock-id]');
      const newPositions = new Map<string, { x: number; y: number }>();

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

      setPositions(newPositions);
    };

    // Update after animation
    const timer = setTimeout(updatePositions, 500);
    window.addEventListener('resize', updatePositions);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', updatePositions);
    };
  }, [nodes, containerRef]);

  if (positions.size === 0) return null;

  // Filter edges to only show those involving selected node
  const relevantEdges = selectedId
    ? edges.filter((e) => e.from === selectedId || e.to === selectedId)
    : [];

  return (
    <svg className="genesis-graph__edges">
      {relevantEdges.map((edge, index) => {
        const fromPos = positions.get(edge.from);
        const toPos = positions.get(edge.to);
        if (!fromPos || !toPos) return null;

        const midY = (fromPos.y + toPos.y) / 2;
        const path = `M ${fromPos.x} ${fromPos.y} C ${fromPos.x} ${midY}, ${toPos.x} ${midY}, ${toPos.x} ${toPos.y}`;

        return (
          <motion.path
            key={`${edge.from}-${edge.to}`}
            className="genesis-graph__edge"
            d={path}
            fill="none"
            stroke="var(--accent-amber)"
            strokeWidth={2}
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.6 }}
            transition={{
              pathLength: { delay: index * 0.1, duration: 0.5, ease: 'easeInOut' },
              opacity: { delay: index * 0.1, duration: 0.3 },
            }}
          />
        );
      })}
    </svg>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const GenesisGraph = memo(function GenesisGraph({
  graph,
  status,
  selectedLayer,
  selectedId,
  layerInfo,
  layerCounts,
  phase,
  onLayerChange,
  onNodeSelect,
  onContinue,
}: GenesisGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Get nodes for current layer
  const layerNodes = useMemo(() => {
    const nodeIds = graph.layers[selectedLayer] || [];
    return graph.nodes.filter((n) => nodeIds.includes(n.id));
  }, [graph, selectedLayer]);

  // Get selected K-Block
  const selectedKBlock = useMemo(
    () => graph.nodes.find((n) => n.id === selectedId) || null,
    [graph.nodes, selectedId]
  );

  // Show overview content during illumination phase
  const showOverview = phase === 'illumination';

  return (
    <div className="genesis-graph" ref={containerRef}>
      {/* Header */}
      <header className="genesis-graph__header">
        <div className="genesis-graph__header-content">
          <h1 className="genesis-graph__title">CONSTITUTIONAL GRAPH</h1>
          <p className="genesis-graph__subtitle">
            {showOverview
              ? '22 K-Blocks form the self-describing genesis of kgents'
              : 'Select a K-Block to explore its derivation'}
          </p>
        </div>
        <div className="genesis-graph__stats">
          <div className="genesis-graph__stat">
            <span className="genesis-graph__stat-value">{status.kblock_count}</span>
            <span className="genesis-graph__stat-label">K-Blocks</span>
          </div>
          <div className="genesis-graph__stat">
            <span className="genesis-graph__stat-value">
              {status.average_loss !== null ? (status.average_loss * 100).toFixed(1) : '--'}%
            </span>
            <span className="genesis-graph__stat-label">Avg Loss</span>
          </div>
        </div>
      </header>

      {/* Layer Tabs */}
      <nav className="genesis-graph__tabs">
        {([0, 1, 2, 3] as const).map((layer) => (
          <LayerTab
            key={layer}
            layer={layer}
            info={layerInfo[layer]}
            count={layerCounts[layer] || 0}
            isActive={selectedLayer === layer}
            onClick={() => onLayerChange(layer)}
          />
        ))}
      </nav>

      {/* Main Content */}
      <div className="genesis-graph__content">
        {/* Layer Description */}
        <motion.div
          className="genesis-graph__layer-info"
          key={selectedLayer}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
        >
          <h2
            className="genesis-graph__layer-name"
            style={{ color: layerInfo[selectedLayer].color }}
          >
            L{selectedLayer}: {layerInfo[selectedLayer].name}
          </h2>
          <p className="genesis-graph__layer-description">{layerInfo[selectedLayer].description}</p>
        </motion.div>

        {/* Node Grid + Detail Panel */}
        <div className="genesis-graph__main">
          {/* Nodes Grid */}
          <motion.div
            className="genesis-graph__nodes"
            variants={nodeContainerVariants}
            initial="hidden"
            animate="visible"
            key={selectedLayer}
          >
            {/* SVG Edges Layer */}
            <DerivationEdges
              edges={graph.edges}
              nodes={graph.nodes}
              selectedId={selectedId}
              containerRef={containerRef}
            />

            {/* Node Buttons */}
            {layerNodes.map((node, index) => (
              <div key={node.id} data-kblock-id={node.id}>
                <KBlockNode
                  kblock={node}
                  isSelected={selectedId === node.id}
                  layerColor={layerInfo[node.layer].color}
                  onClick={() => onNodeSelect(node.id)}
                  index={index}
                />
              </div>
            ))}
          </motion.div>

          {/* Detail Panel */}
          <div className="genesis-graph__panel">
            <AnimatePresence mode="wait">
              <KBlockDetail kblock={selectedKBlock} layerInfo={layerInfo} allNodes={graph.nodes} />
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Continue Button */}
      <div className="genesis-graph__footer">
        <motion.button
          type="button"
          className="genesis-graph__continue"
          onClick={onContinue}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Continue
        </motion.button>
      </div>
    </div>
  );
});

export default GenesisGraph;
