/**
 * KBlockProjection — Universal K-Block Renderer
 *
 * "The projection is not a view. The projection IS the reality."
 *
 * Renders K-Blocks across different surfaces while maintaining:
 * - Identity law: KBlockProjection(K, Id, Id) ≅ K
 * - Constitutional coherence
 * - Galois loss awareness
 * - Contradiction detection
 * - Witness capability
 *
 * Design: STARK BIOME (90% steel, 10% earned glow)
 */

import { memo, useMemo } from 'react';
import type {
  KBlockProjectionProps,
  GaloisLoss,
  ConstitutionalWeights,
} from './types';
import {
  calculateGaloisLoss,
  getDefaultConstitutionalWeights,
  getLossColor,
} from './types';

// Import projections
import { GraphProjection } from './projections/GraphProjection';
import { FeedProjection } from './projections/FeedProjection';
import { ChatProjection } from './projections/ChatProjection';
import { PortalProjection } from './projections/PortalProjection';
import { GenesisProjection } from './projections/GenesisProjection';
import { CardProjection } from './projections/CardProjection';
import { InlineProjection } from './projections/InlineProjection';
import { DiffProjection } from './projections/DiffProjection';
import { ProofProjection } from './projections/ProofProjection';

import './KBlockProjection.css';

// =============================================================================
// Main Component
// =============================================================================

export const KBlockProjection = memo(function KBlockProjection({
  kblock,
  observer,
  projection,
  depth = 0,
  onWitness,
  onNavigateLoss,
  constitutionalWeights,
  contradiction,
  className = '',
}: KBlockProjectionProps) {
  // Calculate Galois loss if not provided
  const galoisLoss: GaloisLoss = useMemo(() => calculateGaloisLoss(kblock), [kblock]);

  // Calculate constitutional weights if not provided
  const weights: ConstitutionalWeights = useMemo(
    () => constitutionalWeights || getDefaultConstitutionalWeights(kblock),
    [kblock, constitutionalWeights]
  );

  // Get constitutional score (average of all principles)
  const constitutionalScore = useMemo(() => {
    const values = Object.values(weights);
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  }, [weights]);

  // Select projection component
  const ProjectionComponent = useMemo(() => {
    switch (projection) {
      case 'graph':
        return GraphProjection;
      case 'feed':
        return FeedProjection;
      case 'chat':
        return ChatProjection;
      case 'portal':
        return PortalProjection;
      case 'genesis':
        return GenesisProjection;
      case 'card':
        return CardProjection;
      case 'inline':
        return InlineProjection;
      case 'diff':
        return DiffProjection;
      case 'proof':
        return ProofProjection;
      default:
        return CardProjection; // fallback
    }
  }, [projection]);

  return (
    <div
      className={`kblock-projection kblock-projection--${projection} ${className}`}
      data-kblock-id={kblock.id}
      data-layer={kblock.zeroSeedLayer ?? 'file'}
      data-isolation={kblock.isolation}
    >
      {/* Projection-specific rendering */}
      <ProjectionComponent
        kblock={kblock}
        observer={observer}
        depth={depth}
        onWitness={onWitness}
        onNavigateLoss={onNavigateLoss}
        constitutionalWeights={weights}
        contradiction={contradiction}
        className="kblock-projection__inner"
      />

      {/* Shared indicators (rendered for ALL projections) */}
      <div className="kblock-projection__indicators">
        {/* Galois loss indicator */}
        {galoisLoss.loss > 0.2 && (
          <button
            className="kblock-projection__loss-indicator"
            style={{ borderColor: getLossColor(galoisLoss.loss) }}
            onClick={() =>
              onNavigateLoss?.(galoisLoss.direction || 'lower')
            }
            title={`Galois loss: ${(galoisLoss.loss * 100).toFixed(1)}% - Click to navigate ${galoisLoss.direction || 'lower'}`}
          >
            <span className="kblock-projection__loss-icon">⚠</span>
            <span className="kblock-projection__loss-value">
              {(galoisLoss.loss * 100).toFixed(0)}%
            </span>
          </button>
        )}

        {/* Contradiction badge */}
        {contradiction && (
          <div
            className={`kblock-projection__contradiction kblock-projection__contradiction--${contradiction.severity}`}
            title={contradiction.description}
          >
            <span className="kblock-projection__contradiction-icon">⚔</span>
            <span className="kblock-projection__contradiction-label">
              {contradiction.type}
            </span>
          </div>
        )}

        {/* Constitutional score (only if low) */}
        {constitutionalScore < 0.6 && (
          <div
            className="kblock-projection__constitutional-low"
            title={`Constitutional alignment: ${(constitutionalScore * 100).toFixed(0)}%`}
          >
            <span className="kblock-projection__constitutional-icon">⚖</span>
            <span className="kblock-projection__constitutional-value">
              {(constitutionalScore * 100).toFixed(0)}%
            </span>
          </div>
        )}

        {/* Proof badge (if present) */}
        {kblock.hasProof && (
          <div
            className="kblock-projection__proof-badge"
            title="Has Toulmin proof"
          >
            <span className="kblock-projection__proof-icon">✓</span>
          </div>
        )}
      </div>
    </div>
  );
});

export default KBlockProjection;
