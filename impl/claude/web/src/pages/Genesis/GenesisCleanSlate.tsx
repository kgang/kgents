/**
 * GenesisCleanSlate — Constitutional Graph Showcase
 *
 * "The system already knows itself."
 *
 * This page displays the 22 K-Blocks of the Constitutional Graph that form
 * the self-describing genesis of kgents:
 * - L0: 4 axioms (Entity, Morphism, Mirror Test, Galois Ground)
 * - L1: 7 kernel primitives (Compose, Judge, Ground, Id, Contradict, Sublate, Fix)
 * - L2: 7 principles (Tasteful, Curated, Ethical, Joy-Inducing, Composable, Heterarchical, Generative)
 * - L3: 4 architecture (ASHC, Metaphysical Fullstack, Hypergraph Editor, AGENTESE)
 *
 * @see spec/protocols/genesis-clean-slate.md
 */

import { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  genesisApi,
  type CleanSlateStatusResponse,
  type DerivationGraphResponse,
  type CleanSlateKBlock,
} from '../../api/client';
import { ConstitutionalGraphView } from '../../hypergraph/ConstitutionalGraphView';
import type { KBlock } from '../../primitives/KBlockProjection/types';
import type { DerivationGraph } from '../../hypergraph/ConstitutionalGraphView';
import './GenesisCleanSlate.css';

// =============================================================================
// Types
// =============================================================================

type PageState = 'loading' | 'not_seeded' | 'seeding' | 'ready' | 'error';

// =============================================================================
// Layer Display Info
// =============================================================================

const LAYER_INFO: Record<number, { name: string; description: string; color: string }> = {
  0: { name: 'L0: Axiom', description: 'Irreducible truths', color: '#c4a77d' },
  1: { name: 'L1: Kernel', description: 'Bootstrap primitives', color: '#6b8b6b' },
  2: { name: 'L2: Principle', description: 'Design values', color: '#8ba98b' },
  3: { name: 'L3: Architecture', description: 'System patterns', color: '#4a6b4a' },
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Convert API K-Block to frontend KBlock type.
 */
function toKBlock(cleanSlateBlock: CleanSlateKBlock): KBlock {
  const now = new Date();
  return {
    id: cleanSlateBlock.id,
    path: cleanSlateBlock.id, // Genesis IDs are also paths
    content: cleanSlateBlock.content || '',
    baseContent: cleanSlateBlock.content || '',
    contentHash: cleanSlateBlock.id, // Use ID as hash for genesis blocks
    isolation: 'PRISTINE',
    confidence: 1.0 - cleanSlateBlock.galois_loss, // Invert loss to confidence
    zeroSeedLayer: cleanSlateBlock.layer,
    zeroSeedKind:
      cleanSlateBlock.tags.find((t) =>
        ['axiom', 'primitive', 'principle', 'architecture'].includes(t)
      ) || null,
    lineage: cleanSlateBlock.derives_from,
    hasProof: false,
    toulminProof: null,
    incomingEdges: [],
    outgoingEdges: [],
    tags: cleanSlateBlock.tags,
    createdBy: 'system',
    createdAt: now,
    updatedAt: now,
    notIngested: false,
    analysisRequired: false,
  };
}

/**
 * Convert API derivation graph to frontend DerivationGraph type.
 */
function toDerivationGraph(apiGraph: DerivationGraphResponse): DerivationGraph {
  // Map edges to the format expected by ConstitutionalGraphView
  // The component expects edges from K-Block to principle
  // But our graph has derivation edges (child -> parent)
  const edges = apiGraph.edges.map((edge) => ({
    sourceId: edge.to, // The K-Block that derives
    principle: getPrincipleFromId(edge.from), // The source it derives from
    strength: 1.0,
    loss: 0.0,
  }));

  // Extract unique principles from edges
  const principles = [...new Set(edges.map((e) => e.principle))].filter(Boolean);

  return {
    edges,
    principles,
  };
}

/**
 * Extract principle name from genesis ID.
 */
function getPrincipleFromId(id: string): string {
  // genesis:L2:tasteful -> TASTEFUL
  const parts = id.split(':');
  if (parts.length >= 3) {
    return parts[2].toUpperCase().replace('-', '_');
  }
  return id;
}

// =============================================================================
// Inline Components
// =============================================================================

interface CoherenceSummaryProps {
  status: CleanSlateStatusResponse;
  graph: DerivationGraphResponse | null;
}

/**
 * CoherenceSummary — Statistics panel for the Constitutional Graph.
 */
function CoherenceSummary({ status, graph }: CoherenceSummaryProps) {
  const isGrounded = status.is_seeded && status.missing_kblocks.length === 0;
  const statusText = isGrounded ? 'GROUNDED' : 'INCOMPLETE';
  const statusColor = isGrounded ? '#6b8b6b' : '#c4a77d';

  return (
    <motion.div
      className="genesis-cs-coherence"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.2 }}
    >
      <h3 className="genesis-cs-coherence-title">COHERENCE</h3>
      <div className="genesis-cs-coherence-stats">
        <div className="genesis-cs-stat">
          <span className="genesis-cs-stat-value">
            {status.kblock_count}/{status.expected_count}
          </span>
          <span className="genesis-cs-stat-label">K-Blocks</span>
        </div>
        <div className="genesis-cs-stat">
          <span className="genesis-cs-stat-value">
            {status.average_loss !== null ? status.average_loss.toFixed(2) : '--'}
          </span>
          <span className="genesis-cs-stat-label">Avg Loss</span>
        </div>
        <div className="genesis-cs-stat">
          <span className="genesis-cs-stat-value" style={{ color: statusColor }}>
            {statusText}
          </span>
          <span className="genesis-cs-stat-label">Status</span>
        </div>
      </div>
      {graph && (
        <div className="genesis-cs-coherence-layers">
          {Object.entries(LAYER_INFO).map(([layer, info]) => {
            const layerNum = parseInt(layer);
            const count = graph.layers[layerNum]?.length || 0;
            return (
              <div key={layer} className="genesis-cs-layer-stat">
                <span className="genesis-cs-layer-badge" style={{ backgroundColor: info.color }}>
                  {info.name}
                </span>
                <span className="genesis-cs-layer-count">{count}</span>
              </div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
}

interface KBlockDetailProps {
  kblock: CleanSlateKBlock | null;
}

/**
 * KBlockDetail — Detail panel for selected K-Block.
 */
function KBlockDetail({ kblock }: KBlockDetailProps) {
  if (!kblock) {
    return (
      <motion.div
        className="genesis-cs-detail genesis-cs-detail--empty"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <p className="genesis-cs-detail-placeholder">Select a K-Block to view details</p>
      </motion.div>
    );
  }

  const layerInfo = LAYER_INFO[kblock.layer] || {
    name: `L${kblock.layer}`,
    description: '',
    color: '#5a5a64',
  };

  return (
    <motion.div
      className="genesis-cs-detail"
      key={kblock.id}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <div className="genesis-cs-detail-header">
        <span className="genesis-cs-detail-layer" style={{ color: layerInfo.color }}>
          {layerInfo.name}
        </span>
        <span className="genesis-cs-detail-loss">Loss: {kblock.galois_loss.toFixed(3)}</span>
      </div>
      <h3 className="genesis-cs-detail-title">{kblock.title}</h3>
      <p className="genesis-cs-detail-id">{kblock.id}</p>
      {kblock.derives_from.length > 0 && (
        <div className="genesis-cs-detail-derivations">
          <span className="genesis-cs-detail-derivations-label">Derives from:</span>
          <div className="genesis-cs-detail-derivations-list">
            {kblock.derives_from.map((parentId) => (
              <span key={parentId} className="genesis-cs-detail-derivation-badge">
                {parentId.split(':').pop()}
              </span>
            ))}
          </div>
        </div>
      )}
      {kblock.tags.length > 0 && (
        <div className="genesis-cs-detail-tags">
          {kblock.tags.map((tag) => (
            <span key={tag} className="genesis-cs-detail-tag">
              {tag}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function GenesisCleanSlate() {
  // State
  const [pageState, setPageState] = useState<PageState>('loading');
  const [status, setStatus] = useState<CleanSlateStatusResponse | null>(null);
  const [graph, setGraph] = useState<DerivationGraphResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Derived state
  const selectedKBlock = graph?.nodes.find((n) => n.id === selectedId) || null;
  const kblocks: KBlock[] = graph?.nodes.map(toKBlock) || [];
  const derivationGraph: DerivationGraph = graph
    ? toDerivationGraph(graph)
    : { edges: [], principles: [] };

  // =============================================================================
  // Data Fetching
  // =============================================================================

  const loadStatus = useCallback(async () => {
    try {
      const statusData = await genesisApi.getCleanSlateStatus();
      setStatus(statusData);
      return statusData;
    } catch (err) {
      console.error('Failed to load clean slate status:', err);
      throw err;
    }
  }, []);

  const loadGraph = useCallback(async () => {
    try {
      const graphData = await genesisApi.getDerivationGraph();
      setGraph(graphData);
      // Select first L0 node by default
      if (graphData.layers[0]?.length > 0) {
        setSelectedId(graphData.layers[0][0]);
      }
      return graphData;
    } catch (err) {
      console.error('Failed to load derivation graph:', err);
      throw err;
    }
  }, []);

  const seedGenesis = useCallback(async () => {
    try {
      setPageState('seeding');
      setError(null);
      await genesisApi.seedCleanSlate(false, false);
      // Reload status and graph after seeding
      const newStatus = await loadStatus();
      if (newStatus.is_seeded) {
        await loadGraph();
        setPageState('ready');
      } else {
        setError('Seeding completed but genesis is not complete');
        setPageState('error');
      }
    } catch (err) {
      console.error('Failed to seed genesis:', err);
      setError(err instanceof Error ? err.message : 'Failed to seed genesis');
      setPageState('error');
    }
  }, [loadStatus, loadGraph]);

  // Initial load
  useEffect(() => {
    const initialize = async () => {
      try {
        setPageState('loading');
        const statusData = await loadStatus();

        if (statusData.is_seeded) {
          await loadGraph();
          setPageState('ready');
        } else {
          setPageState('not_seeded');
        }
      } catch (err) {
        console.error('Initialization failed:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize');
        setPageState('error');
      }
    };

    initialize();
  }, [loadStatus, loadGraph]);

  // =============================================================================
  // Handlers
  // =============================================================================

  const handleSelect = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  const handleGround = useCallback((kblockId: string, principle: string) => {
    // Genesis K-Blocks are immutable, this is a no-op
    console.log(`Ground ${kblockId} to ${principle} (no-op for genesis)`);
  }, []);

  // =============================================================================
  // Render States
  // =============================================================================

  // Loading state
  if (pageState === 'loading') {
    return (
      <div className="genesis-cs-page genesis-cs-page--loading">
        <motion.div
          className="genesis-cs-loading"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="genesis-cs-loading-spinner" />
          <p className="genesis-cs-loading-text">Loading Constitutional Graph...</p>
        </motion.div>
      </div>
    );
  }

  // Not seeded state
  if (pageState === 'not_seeded') {
    return (
      <div className="genesis-cs-page genesis-cs-page--not-seeded">
        <motion.div
          className="genesis-cs-seed-prompt"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="genesis-cs-seed-title">GENESIS: CLEAN SLATE</h1>
          <p className="genesis-cs-seed-subtitle">"The system awaits self-knowledge"</p>
          <div className="genesis-cs-seed-info">
            <p>The Constitutional Graph has not been seeded.</p>
            <p>Seeding will create 22 self-describing K-Blocks:</p>
            <ul>
              <li>4 L0 axioms (irreducible truths)</li>
              <li>7 L1 kernel primitives (bootstrap operations)</li>
              <li>7 L2 principles (design values)</li>
              <li>4 L3 architecture patterns (system descriptions)</li>
            </ul>
          </div>
          <button type="button" className="genesis-cs-seed-button" onClick={seedGenesis}>
            Seed Genesis
          </button>
        </motion.div>
      </div>
    );
  }

  // Seeding state
  if (pageState === 'seeding') {
    return (
      <div className="genesis-cs-page genesis-cs-page--seeding">
        <motion.div
          className="genesis-cs-seeding"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="genesis-cs-loading-spinner genesis-cs-loading-spinner--large" />
          <p className="genesis-cs-seeding-text">Seeding Constitutional Graph...</p>
          <p className="genesis-cs-seeding-subtext">Creating 22 self-describing K-Blocks</p>
        </motion.div>
      </div>
    );
  }

  // Error state
  if (pageState === 'error') {
    return (
      <div className="genesis-cs-page genesis-cs-page--error">
        <motion.div className="genesis-cs-error" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h2 className="genesis-cs-error-title">Genesis Error</h2>
          <p className="genesis-cs-error-message">{error}</p>
          <div className="genesis-cs-error-actions">
            <button
              type="button"
              className="genesis-cs-error-retry"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
            {status && !status.is_seeded && (
              <button type="button" className="genesis-cs-error-seed" onClick={seedGenesis}>
                Seed Genesis
              </button>
            )}
          </div>
        </motion.div>
      </div>
    );
  }

  // Ready state - main view
  return (
    <div className="genesis-cs-page">
      {/* Header */}
      <motion.header
        className="genesis-cs-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="genesis-cs-title">GENESIS: CLEAN SLATE</h1>
        <p className="genesis-cs-subtitle">"The system already knows itself"</p>
      </motion.header>

      {/* Main content area */}
      <div className="genesis-cs-content">
        {/* Constitutional Graph View */}
        <motion.div
          className="genesis-cs-graph-container"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <ConstitutionalGraphView
            kblocks={kblocks}
            derivationGraph={derivationGraph}
            selectedId={selectedId}
            onSelect={handleSelect}
            onGround={handleGround}
            initialViewMode="layer"
            className="genesis-cs-graph"
          />
        </motion.div>

        {/* Bottom panels */}
        <div className="genesis-cs-panels">
          {/* Coherence Summary */}
          {status && <CoherenceSummary status={status} graph={graph} />}

          {/* K-Block Detail */}
          <AnimatePresence mode="wait">
            <KBlockDetail kblock={selectedKBlock} />
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default GenesisCleanSlate;
