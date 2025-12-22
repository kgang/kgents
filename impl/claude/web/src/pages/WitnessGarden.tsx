/**
 * WitnessGarden: The Witness Assurance Surface page.
 *
 * A living visualization where specs grow as plants, evidence accumulates
 * as soil depth, and orphans appear as weeds to tend.
 *
 * From spec:
 *   "The UI IS the trust surface. Every pixel grows or wilts."
 *
 * @see spec/protocols/witness-assurance-surface.md
 */

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useWindowLayout } from '@/hooks/useLayoutContext';
import { GardenScene, EvidenceLadder } from '@/components/witness/garden';
import { ElasticSplit } from '@/components/elastic';
import {
  getGardenScene,
  getEvidenceLadder,
  type GardenScene as GardenSceneType,
  type SpecPlant,
  type AccountabilityLens,
  type LadderResponse,
} from '@/api/witness';

// =============================================================================
// Types
// =============================================================================

interface WitnessGardenState {
  scene: GardenSceneType | null;
  selectedPlant: SpecPlant | null;
  selectedLadder: LadderResponse | null;
  lens: AccountabilityLens;
  isLoading: boolean;
  error: string | null;
}

// =============================================================================
// Main Component
// =============================================================================

export default function WitnessGardenPage() {
  const { density, isMobile } = useWindowLayout();

  const [state, setState] = useState<WitnessGardenState>({
    scene: null,
    selectedPlant: null,
    selectedLadder: null,
    lens: 'audit',
    isLoading: true,
    error: null,
  });

  // Fetch garden scene
  const fetchGarden = useCallback(async () => {
    try {
      const scene = await getGardenScene({ lens: state.lens, density });
      setState((prev) => ({ ...prev, scene, isLoading: false, error: null }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to load garden',
      }));
    }
  }, [state.lens, density]);

  // Initial fetch
  useEffect(() => {
    fetchGarden();
  }, [fetchGarden]);

  // Keyboard shortcuts for lens switching
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only handle when not typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key.toUpperCase()) {
        case 'A':
          setState((prev) => ({ ...prev, lens: 'audit' }));
          break;
        case 'U':
          setState((prev) => ({ ...prev, lens: 'author' }));
          break;
        case 'T':
          setState((prev) => ({ ...prev, lens: 'trust' }));
          break;
        case 'R':
          fetchGarden();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [fetchGarden]);

  // Handle plant selection
  const handlePlantSelect = async (plant: SpecPlant) => {
    setState((prev) => ({ ...prev, selectedPlant: plant, selectedLadder: null }));

    // Fetch evidence ladder for selected plant
    try {
      const ladder = await getEvidenceLadder(plant.path);
      setState((prev) => ({ ...prev, selectedLadder: ladder }));
    } catch (err) {
      console.error('Failed to fetch ladder:', err);
    }
  };

  // Handle lens change
  const handleLensChange = (lens: AccountabilityLens) => {
    setState((prev) => ({ ...prev, lens }));
  };

  // Loading state
  if (state.isLoading) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900">
        <div className="text-center">
          <motion.div
            className="text-4xl mb-4"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            🌱
          </motion.div>
          <p className="text-gray-400">Growing garden...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (state.error) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900">
        <div className="text-center">
          <div className="text-4xl mb-4">🍂</div>
          <p className="text-red-400 mb-2">Failed to load garden</p>
          <p className="text-gray-500 text-sm mb-4">{state.error}</p>
          <button
            onClick={fetchGarden}
            className="px-4 py-2 bg-gray-800 text-gray-300 rounded hover:bg-gray-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // No scene
  if (!state.scene) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900">
        <p className="text-gray-500">No garden data available</p>
      </div>
    );
  }

  // Detail panel for selected plant
  const DetailPanel = () => {
    if (!state.selectedPlant) {
      return (
        <div className="flex flex-col items-center justify-center h-full p-4 text-gray-500">
          <span className="text-4xl mb-4">🔍</span>
          <p>Select a spec to view details</p>
          <p className="text-xs mt-2 text-gray-600">
            Keyboard: A=Audit, U=Author, T=Trust, R=Refresh
          </p>
        </div>
      );
    }

    const plant = state.selectedPlant;

    return (
      <div className="h-full overflow-auto p-4 bg-gray-900">
        {/* Header */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-white mb-1">{plant.name}</h2>
          <p className="text-sm text-gray-500">{plant.path}</p>
        </div>

        {/* Status */}
        <div className="mb-6">
          <h3 className="text-xs font-medium text-gray-400 uppercase mb-2">Status</h3>
          <div className="flex items-center gap-3">
            <span
              className="px-3 py-1 rounded-full text-sm"
              style={{
                backgroundColor: plant.confidence > 0.8 ? '#10B98120' : '#F59E0B20',
                color: plant.confidence > 0.8 ? '#10B981' : '#F59E0B',
              }}
            >
              {plant.status.replace('_', ' ')}
            </span>
            <span
              className="text-2xl font-bold"
              style={{
                color: plant.confidence > 0.8 ? '#10B981' : '#F59E0B',
              }}
            >
              {(plant.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Evidence Ladder */}
        <div className="mb-6">
          <h3 className="text-xs font-medium text-gray-400 uppercase mb-3">Evidence Ladder</h3>
          {state.selectedLadder ? (
            <EvidenceLadder ladder={state.selectedLadder.ladder} mode="full" />
          ) : (
            <div className="text-gray-500 text-sm">Loading ladder...</div>
          )}
        </div>

        {/* Metrics */}
        <div className="mb-6">
          <h3 className="text-xs font-medium text-gray-400 uppercase mb-2">Metrics</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded bg-gray-800">
              <p className="text-xs text-gray-500">Marks</p>
              <p className="text-lg font-medium text-white">{plant.mark_count}</p>
            </div>
            <div className="p-3 rounded bg-gray-800">
              <p className="text-xs text-gray-500">Tests</p>
              <p className="text-lg font-medium text-white">{plant.test_count}</p>
            </div>
            <div className="p-3 rounded bg-gray-800">
              <p className="text-xs text-gray-500">Height</p>
              <p className="text-lg font-medium text-white">{plant.height}</p>
            </div>
            <div className="p-3 rounded bg-gray-800">
              <p className="text-xs text-gray-500">Health</p>
              <p className="text-lg font-medium text-white">{plant.health}</p>
            </div>
          </div>
        </div>

        {/* Last Evidence */}
        {plant.last_evidence_at && (
          <div className="text-xs text-gray-600">
            Last evidence: {new Date(plant.last_evidence_at).toLocaleString()}
          </div>
        )}
      </div>
    );
  };

  // Mobile: single pane with bottom sheet for details
  if (isMobile) {
    return (
      <div className="h-full flex flex-col bg-gray-900">
        <GardenScene
          scene={state.scene}
          lens={state.lens}
          onLensChange={handleLensChange}
          onPlantSelect={handlePlantSelect}
          selectedPlantPath={state.selectedPlant?.path}
          density="compact"
          className="flex-1"
        />

        {/* Bottom sheet for selected plant */}
        {state.selectedPlant && (
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="h-64 border-t border-gray-700 overflow-auto"
          >
            <DetailPanel />
          </motion.div>
        )}
      </div>
    );
  }

  // Desktop: split pane
  return (
    <div className="h-full bg-gray-900">
      <ElasticSplit
        defaultRatio={0.65}
        collapseAt={768}
        collapsePriority="secondary"
        resizable
        primary={
          <GardenScene
            scene={state.scene}
            lens={state.lens}
            onLensChange={handleLensChange}
            onPlantSelect={handlePlantSelect}
            selectedPlantPath={state.selectedPlant?.path}
            density={density}
            className="h-full"
          />
        }
        secondary={<DetailPanel />}
      />
    </div>
  );
}
