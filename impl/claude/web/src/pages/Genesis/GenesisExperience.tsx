/**
 * GenesisExperience - Unified Constitutional Graph-First Experience
 *
 * "Genesis is self-description, not interrogation."
 *
 * 5 Phases:
 * 1. ARRIVAL    - Welcome with breathing animation, philosophy quote
 * 2. ILLUMINATION - Constitutional Graph reveals with layer tabs (L0-L3)
 * 3. EXPLORATION  - Click K-Blocks to expand details, see derivations
 * 4. CONNECTION   - Animated derivation edges, 4-7-8 breathing on selected
 * 5. DEPARTURE    - Exit CTAs: Write Spec, Explore Editor, See Examples
 *
 * LIVING_EARTH Palette:
 * - L0: #c4a77d (amber/honey) - warmest, axioms
 * - L1: #6b8b6b (sage green) - kernel
 * - L2: #8b7355 (earth brown) - principles
 * - L3: #f5f0e6 (sand/lantern) - coolest, architecture
 *
 * @see spec/protocols/genesis-clean-slate.md
 */

import { useEffect, useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  genesisApi,
  type CleanSlateStatusResponse,
  type DerivationGraphResponse,
} from '../../api/client';
import { GenesisWelcome } from './components/GenesisWelcome';
import { GenesisGraph } from './components/GenesisGraph';
import { GenesisActions } from './components/GenesisActions';
import './GenesisExperience.css';

// =============================================================================
// Types
// =============================================================================

/** Genesis experience phases */
export type GenesisPhase =
  | 'loading'
  | 'not_seeded'
  | 'seeding'
  | 'arrival'
  | 'illumination'
  | 'exploration'
  | 'connection'
  | 'departure'
  | 'error';

/** Layer metadata for display */
export interface LayerInfo {
  id: 0 | 1 | 2 | 3;
  name: string;
  description: string;
  color: string;
  count?: number;
}

// =============================================================================
// Constants - LIVING_EARTH Palette
// =============================================================================

export const LAYER_INFO: Record<number, LayerInfo> = {
  0: {
    id: 0,
    name: 'AXIOMS',
    description: 'Irreducible truths - Entity, Morphism, Mirror Test, Galois',
    color: '#c4a77d', // amber/honey glow (warmest)
  },
  1: {
    id: 1,
    name: 'KERNEL',
    description: 'Bootstrap primitives - Compose, Judge, Ground, Id, Contradict, Sublate, Fix',
    color: '#6b8b6b', // sage green
  },
  2: {
    id: 2,
    name: 'PRINCIPLES',
    description:
      'Design values - Tasteful, Curated, Ethical, Joy-Inducing, Composable, Heterarchical, Generative',
    color: '#8b7355', // earth brown
  },
  3: {
    id: 3,
    name: 'ARCHITECTURE',
    description: 'System patterns - ASHC, Metaphysical Fullstack, Hypergraph Editor, AGENTESE',
    color: '#f5f0e6', // sand/lantern (coolest)
  },
};

// =============================================================================
// Phase Transition Helpers
// =============================================================================

const PHASE_ORDER: GenesisPhase[] = [
  'arrival',
  'illumination',
  'exploration',
  'connection',
  'departure',
];

function getNextPhase(current: GenesisPhase): GenesisPhase | null {
  const idx = PHASE_ORDER.indexOf(current);
  if (idx === -1 || idx >= PHASE_ORDER.length - 1) return null;
  return PHASE_ORDER[idx + 1];
}

// =============================================================================
// Main Component
// =============================================================================

export function GenesisExperience() {
  // State
  const [phase, setPhase] = useState<GenesisPhase>('loading');
  const [status, setStatus] = useState<CleanSlateStatusResponse | null>(null);
  const [graph, setGraph] = useState<DerivationGraphResponse | null>(null);
  const [selectedLayer, setSelectedLayer] = useState<0 | 1 | 2 | 3>(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Derived state
  const selectedKBlock = useMemo(
    () => graph?.nodes.find((n) => n.id === selectedId) || null,
    [graph, selectedId]
  );

  const layerCounts = useMemo(() => {
    if (!graph) return {};
    const counts: Record<number, number> = {};
    Object.entries(graph.layers).forEach(([layer, ids]) => {
      counts[parseInt(layer)] = ids.length;
    });
    return counts;
  }, [graph]);

  // =============================================================================
  // Data Fetching
  // =============================================================================

  const loadStatus = useCallback(async () => {
    try {
      const statusData = await genesisApi.getCleanSlateStatus();
      setStatus(statusData);
      return statusData;
    } catch (err) {
      console.error('[GenesisExperience] Failed to load status:', err);
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
      console.error('[GenesisExperience] Failed to load graph:', err);
      throw err;
    }
  }, []);

  const seedGenesis = useCallback(async () => {
    try {
      setPhase('seeding');
      setError(null);
      await genesisApi.seedCleanSlate(false, false);
      // Reload after seeding
      const newStatus = await loadStatus();
      if (newStatus.is_seeded) {
        await loadGraph();
        setPhase('arrival');
      } else {
        setError('Seeding completed but genesis is not complete');
        setPhase('error');
      }
    } catch (err) {
      console.error('[GenesisExperience] Failed to seed:', err);
      setError(err instanceof Error ? err.message : 'Failed to seed genesis');
      setPhase('error');
    }
  }, [loadStatus, loadGraph]);

  const resetGenesis = useCallback(async () => {
    try {
      setPhase('seeding');
      setError(null);
      setGraph(null);
      setSelectedId(null);
      // Wipe existing and force re-seed
      await genesisApi.seedCleanSlate(true, true);
      // Reload after seeding
      const newStatus = await loadStatus();
      if (newStatus.is_seeded) {
        await loadGraph();
        setPhase('arrival');
      } else {
        setError('Reset completed but genesis is not complete');
        setPhase('error');
      }
    } catch (err) {
      console.error('[GenesisExperience] Failed to reset:', err);
      setError(err instanceof Error ? err.message : 'Failed to reset genesis');
      setPhase('error');
    }
  }, [loadStatus, loadGraph]);

  // Initial load
  useEffect(() => {
    const initialize = async () => {
      try {
        setPhase('loading');
        const statusData = await loadStatus();

        if (statusData.is_seeded) {
          await loadGraph();
          setPhase('arrival');
        } else {
          setPhase('not_seeded');
        }
      } catch (err) {
        console.error('[GenesisExperience] Initialization failed:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize');
        setPhase('error');
      }
    };

    initialize();
  }, [loadStatus, loadGraph]);

  // =============================================================================
  // Phase Transitions
  // =============================================================================

  // advancePhase available for future use: getNextPhase(phase) -> setPhase(next)

  const handleArrivalComplete = useCallback(() => {
    setPhase('illumination');
  }, []);

  const handleLayerChange = useCallback((layer: 0 | 1 | 2 | 3) => {
    setSelectedLayer(layer);
    // Move to exploration when user actively selects a layer
    setPhase((current) => (current === 'illumination' ? 'exploration' : current));
  }, []);

  const handleNodeSelect = useCallback((id: string) => {
    setSelectedId(id);
    // Move to connection when user selects a node
    setPhase((current) =>
      current === 'exploration' || current === 'illumination' ? 'connection' : current
    );
  }, []);

  const handleContinue = useCallback(() => {
    setPhase('departure');
  }, []);

  // =============================================================================
  // Render Helpers
  // =============================================================================

  const renderLoading = () => (
    <div className="genesis-exp genesis-exp--loading">
      <motion.div
        className="genesis-exp__loading"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="genesis-exp__loading-spinner" />
        <p className="genesis-exp__loading-text">Loading Constitutional Graph...</p>
      </motion.div>
    </div>
  );

  const renderNotSeeded = () => (
    <div className="genesis-exp genesis-exp--not-seeded">
      <motion.div
        className="genesis-exp__seed-prompt"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="genesis-exp__seed-title">GENESIS</h1>
        <p className="genesis-exp__seed-subtitle">"The system awaits self-knowledge"</p>
        <div className="genesis-exp__seed-info">
          <p>The Constitutional Graph has not been seeded.</p>
          <p>Seeding will create 22 self-describing K-Blocks:</p>
          <ul>
            <li>4 L0 axioms (irreducible truths)</li>
            <li>7 L1 kernel primitives (bootstrap operations)</li>
            <li>7 L2 principles (design values)</li>
            <li>4 L3 architecture patterns (system descriptions)</li>
          </ul>
        </div>
        <button type="button" className="genesis-exp__seed-button" onClick={seedGenesis}>
          Seed Genesis
        </button>
      </motion.div>
    </div>
  );

  const renderSeeding = () => (
    <div className="genesis-exp genesis-exp--seeding">
      <motion.div
        className="genesis-exp__seeding"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="genesis-exp__loading-spinner genesis-exp__loading-spinner--large" />
        <p className="genesis-exp__seeding-text">Seeding Constitutional Graph...</p>
        <p className="genesis-exp__seeding-subtext">Creating 22 self-describing K-Blocks</p>
      </motion.div>
    </div>
  );

  const renderError = () => (
    <div className="genesis-exp genesis-exp--error">
      <motion.div className="genesis-exp__error" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h2 className="genesis-exp__error-title">Genesis Error</h2>
        <p className="genesis-exp__error-message">{error}</p>
        <div className="genesis-exp__error-actions">
          <button
            type="button"
            className="genesis-exp__error-retry"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
          {status && !status.is_seeded && (
            <button type="button" className="genesis-exp__error-seed" onClick={seedGenesis}>
              Seed Genesis
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );

  // =============================================================================
  // Main Render
  // =============================================================================

  // Handle non-ready states
  if (phase === 'loading') return renderLoading();
  if (phase === 'not_seeded') return renderNotSeeded();
  if (phase === 'seeding') return renderSeeding();
  if (phase === 'error') return renderError();

  // Ready states (arrival through departure)
  const isInGraphPhase = ['illumination', 'exploration', 'connection'].includes(phase);
  const showWelcome = phase === 'arrival';
  const showActions = phase === 'departure';

  return (
    <div className="genesis-exp">
      <AnimatePresence mode="wait">
        {/* Phase 1: Arrival */}
        {showWelcome && (
          <motion.div
            key="welcome"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="genesis-exp__phase"
          >
            <GenesisWelcome onComplete={handleArrivalComplete} />
          </motion.div>
        )}

        {/* Phases 2-4: Illumination, Exploration, Connection */}
        {isInGraphPhase && graph && status && (
          <motion.div
            key="graph"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="genesis-exp__phase genesis-exp__phase--graph"
          >
            <GenesisGraph
              graph={graph}
              status={status}
              selectedLayer={selectedLayer}
              selectedId={selectedId}
              layerInfo={LAYER_INFO}
              layerCounts={layerCounts}
              phase={phase}
              onLayerChange={handleLayerChange}
              onNodeSelect={handleNodeSelect}
              onContinue={handleContinue}
            />
          </motion.div>
        )}

        {/* Phase 5: Departure */}
        {showActions && (
          <motion.div
            key="actions"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="genesis-exp__phase"
          >
            <GenesisActions
              selectedKBlock={selectedKBlock}
              onBack={() => setPhase('connection')}
              onReset={resetGenesis}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default GenesisExperience;
