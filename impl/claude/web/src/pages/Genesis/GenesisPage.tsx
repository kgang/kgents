/**
 * GenesisPage — First-Run Experience
 *
 * Grounded in: spec/protocols/genesis-clean-slate.md
 *
 * "Genesis is self-description, not interrogation."
 *
 * The system teaches itself to the user through the Constitutional Graph.
 * No questionnaires. No preferences. Just exploration.
 */

import { useState, useCallback } from 'react';
import type { GenesisPhase, GenesisLayer, GenesisState } from '../../types';
import { INITIAL_GENESIS_STATE } from '../../types';
import { GenesisLanding } from './GenesisLanding';
import { ConstitutionalExplorer } from './ConstitutionalExplorer';
import { FirstDeclaration } from './FirstDeclaration';
import './genesis.css';

/**
 * Genesis Page — The first-run experience
 */
export function GenesisPage() {
  const [state, setState] = useState<GenesisState>(INITIAL_GENESIS_STATE);

  // Phase transitions
  const handleEnterGarden = useCallback(() => {
    setState((prev) => ({ ...prev, phase: 'explore' }));
  }, []);

  const handleReadyToExtend = useCallback(() => {
    setState((prev) => ({ ...prev, phase: 'extend' }));
  }, []);

  const handleComplete = useCallback((declaration: string) => {
    setState((prev) => ({
      ...prev,
      phase: 'complete',
      userDeclaration: declaration,
    }));
    // TODO: Navigate to workspace with the new declaration
    window.location.href = '/workspace';
  }, []);

  const handleBack = useCallback(() => {
    setState((prev) => ({ ...prev, phase: 'explore' }));
  }, []);

  // Layer navigation
  const handleLayerChange = useCallback((layer: GenesisLayer) => {
    setState((prev) => ({ ...prev, currentLayer: layer }));
  }, []);

  // Node selection
  const handleSelectNode = useCallback((nodeId: string | null) => {
    setState((prev) => ({
      ...prev,
      selectedNodeId: nodeId,
      visitedNodes:
        nodeId && !prev.visitedNodes.includes(nodeId)
          ? [...prev.visitedNodes, nodeId]
          : prev.visitedNodes,
    }));
  }, []);

  return (
    <div className="genesis-page">
      {state.phase === 'landing' && <GenesisLanding onEnter={handleEnterGarden} />}

      {state.phase === 'explore' && (
        <ConstitutionalExplorer
          currentLayer={state.currentLayer}
          selectedNodeId={state.selectedNodeId}
          visitedNodes={state.visitedNodes}
          onLayerChange={handleLayerChange}
          onSelectNode={handleSelectNode}
          onReadyToExtend={handleReadyToExtend}
        />
      )}

      {state.phase === 'extend' && (
        <FirstDeclaration onComplete={handleComplete} onBack={handleBack} />
      )}
    </div>
  );
}

export default GenesisPage;
