/**
 * ConstitutionalGraphPage - K-Block Derivation Visualization
 *
 * "The proof IS the decision. The mark IS the witness."
 *
 * Full-page experience for visualizing the constitutional derivation graph,
 * showing L0->L1->L2->L3 epistemic layers and their derivation relationships.
 *
 * Features:
 * - Full constitutional graph with layer bands
 * - Click-to-select blocks for derivation path analysis
 * - Density-aware responsive layout
 * - Grounding and consistency status
 *
 * AGENTESE Path: concept.constitution
 *
 * @see spec/protocols/zero-seed-ashc.md
 * @see docs/skills/metaphysical-fullstack.md
 */

import { useEffect, useCallback } from 'react';
import { ConstitutionalGraphView2 } from '@/components/constitutional';
import { useConstitutionalGraphStore } from '@/stores/constitutionalGraphStore';
import type { AgentesePath } from '@/router';
import type { GroundingResult } from '@/components/constitutional';
import './ConstitutionalGraphPage.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionalGraphPageProps {
  /** AGENTESE context for the page */
  agenteseContext?: AgentesePath;
}

// =============================================================================
// Component
// =============================================================================

export function ConstitutionalGraphPage({ agenteseContext }: ConstitutionalGraphPageProps) {
  // Store actions
  const initializeGraph = useConstitutionalGraphStore((s) => s.initializeGraph);
  const checkConsistency = useConstitutionalGraphStore((s) => s.checkConsistency);
  const consistencyReport = useConstitutionalGraphStore((s) => s.consistencyReport);
  const blocks = useConstitutionalGraphStore((s) => s.blocks);

  // Initialize graph data on mount
  useEffect(() => {
    initializeGraph();
    checkConsistency();
  }, [initializeGraph, checkConsistency]);

  // Handle block selection (optional callback for future extensions)
  const handleBlockSelect = useCallback(
    (blockId: string | null, groundingResult: GroundingResult | null) => {
      // Could emit telemetry, update URL params, or log to witness
      if (blockId && groundingResult) {
        console.debug(
          `[concept.constitution] Selected: ${blockId}, Grounded: ${groundingResult.isGrounded}`
        );
      }
    },
    []
  );

  return (
    <div className="constitutional-graph-page">
      {/* Header */}
      <header className="constitutional-graph-page__header">
        <div className="constitutional-graph-page__header-content">
          <h1 className="constitutional-graph-page__title">Constitutional Derivation Graph</h1>
          <p className="constitutional-graph-page__subtitle">
            K-Block epistemic layers: Axioms (L0) derive Primitives (L1), which derive Principles
            (L2), which derive Architecture (L3).
          </p>
          {agenteseContext && (
            <code className="constitutional-graph-page__path">{agenteseContext.fullPath}</code>
          )}
        </div>

        {/* Stats */}
        <div className="constitutional-graph-page__stats">
          <div className="constitutional-graph-page__stat">
            <span className="constitutional-graph-page__stat-value">{blocks.size}</span>
            <span className="constitutional-graph-page__stat-label">K-Blocks</span>
          </div>
          <div className="constitutional-graph-page__stat">
            <span className="constitutional-graph-page__stat-value">4</span>
            <span className="constitutional-graph-page__stat-label">Layers</span>
          </div>
          {consistencyReport && (
            <div className="constitutional-graph-page__stat">
              <span
                className={`constitutional-graph-page__stat-value ${
                  consistencyReport.isConsistent
                    ? 'constitutional-graph-page__stat-value--success'
                    : 'constitutional-graph-page__stat-value--warning'
                }`}
              >
                {Math.round(consistencyReport.consistencyScore * 100)}%
              </span>
              <span className="constitutional-graph-page__stat-label">Coherence</span>
            </div>
          )}
        </div>
      </header>

      {/* Graph Visualization */}
      <main className="constitutional-graph-page__main">
        <ConstitutionalGraphView2
          className="constitutional-graph-page__graph"
          onBlockSelect={handleBlockSelect}
          showDetailPanel={true}
        />
      </main>

      {/* Footer */}
      <footer className="constitutional-graph-page__footer">
        <p className="constitutional-graph-page__quote">
          "The proof IS the decision. The mark IS the witness."
        </p>
      </footer>
    </div>
  );
}

export default ConstitutionalGraphPage;
