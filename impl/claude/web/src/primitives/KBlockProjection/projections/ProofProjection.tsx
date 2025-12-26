/**
 * ProofProjection — Toulmin Proof Structure
 *
 * Renders K-Block's Toulmin proof (if present).
 * Shows: claim, grounds, warrant, backing, qualifiers, rebuttals.
 */

import { memo } from 'react';
import type { ProjectionComponentProps } from '../types';
import './ProofProjection.css';

export const ProofProjection = memo(function ProofProjection({
  kblock,
  className = '',
}: ProjectionComponentProps) {
  // If no proof, show message
  if (!kblock.hasProof || !kblock.toulminProof) {
    return (
      <div className={`proof-projection ${className}`}>
        <div className="proof-projection__no-proof">
          No Toulmin proof available for this K-Block.
        </div>
      </div>
    );
  }

  const proof = kblock.toulminProof;

  return (
    <div className={`proof-projection ${className}`}>
      {/* Header */}
      <div className="proof-projection__header">
        <div className="proof-projection__title">Toulmin Proof</div>
        <div className="proof-projection__kblock-id">{kblock.id}</div>
      </div>

      {/* Claim */}
      <div className="proof-projection__section">
        <div className="proof-projection__section-label">Claim:</div>
        <div className="proof-projection__claim">{proof.claim}</div>
      </div>

      {/* Grounds */}
      <div className="proof-projection__section">
        <div className="proof-projection__section-label">
          Grounds (Evidence):
        </div>
        <ul className="proof-projection__list">
          {proof.grounds.map((ground, idx) => (
            <li key={idx} className="proof-projection__list-item">
              {ground}
            </li>
          ))}
        </ul>
      </div>

      {/* Warrant */}
      <div className="proof-projection__section">
        <div className="proof-projection__section-label">
          Warrant (Inference Rule):
        </div>
        <div className="proof-projection__warrant">{proof.warrant}</div>
      </div>

      {/* Backing (optional) */}
      {proof.backing && (
        <div className="proof-projection__section">
          <div className="proof-projection__section-label">
            Backing (Justification):
          </div>
          <div className="proof-projection__backing">{proof.backing}</div>
        </div>
      )}

      {/* Qualifier (optional) */}
      {proof.qualifier && (
        <div className="proof-projection__section">
          <div className="proof-projection__section-label">
            Qualifier (Modal Strength):
          </div>
          <div className="proof-projection__qualifier">{proof.qualifier}</div>
        </div>
      )}

      {/* Rebuttals (optional) */}
      {proof.rebuttals && proof.rebuttals.length > 0 && (
        <div className="proof-projection__section">
          <div className="proof-projection__section-label">
            Rebuttals (Exceptions):
          </div>
          <ul className="proof-projection__list">
            {proof.rebuttals.map((rebuttal, idx) => (
              <li key={idx} className="proof-projection__list-item">
                {rebuttal}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
});
