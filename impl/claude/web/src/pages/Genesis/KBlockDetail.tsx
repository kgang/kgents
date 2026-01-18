/**
 * KBlockDetail — Full K-Block Content View
 *
 * Shows the complete content of a K-Block with its proof and derivations.
 */

import type { GenesisKBlock } from '../../types';
import { isAxiom, getLayerInfo } from '../../types';
import { getKBlock } from '../../data/genesis-seed';

interface KBlockDetailProps {
  kblock: GenesisKBlock;
  onNavigateToDerivation: (id: string) => void;
}

/**
 * Detailed view of a K-Block
 */
export function KBlockDetail({ kblock, onNavigateToDerivation }: KBlockDetailProps) {
  const layerInfo = getLayerInfo(kblock.layer);
  const isL0 = isAxiom(kblock);

  // Get parent K-Blocks for derivation display
  const parentKBlocks = kblock.derivationsFrom
    .map((id) => getKBlock(id))
    .filter((k): k is GenesisKBlock => k !== undefined);

  // Get child K-Blocks for derivation display
  const childKBlocks = kblock.derivationsTo
    .map((id) => getKBlock(id))
    .filter((k): k is GenesisKBlock => k !== undefined);

  return (
    <article
      className="kblock-detail"
      style={{ '--kblock-color': kblock.color } as React.CSSProperties}
    >
      {/* Header */}
      <header className="kblock-detail__header">
        <div className="kblock-detail__badges">
          <span className="kblock-detail__layer-badge">
            L{kblock.layer}: {layerInfo.name}
          </span>
          {isL0 && <span className="kblock-detail__axiom-badge">AXIOM</span>}
          {kblock.proof && (
            <span className="kblock-detail__galois-badge">
              L = {kblock.proof.galoisLoss.toFixed(2)}
            </span>
          )}
        </div>
        <h2 className="kblock-detail__title">{kblock.title}</h2>
        <p className="kblock-detail__path">
          <code>{kblock.path}</code>
        </p>
      </header>

      {/* Content */}
      <section className="kblock-detail__content">
        {kblock.content.split('\n\n').map((paragraph, i) => (
          <p key={i} className="kblock-detail__paragraph">
            {paragraph.split('\n').map((line, j) => (
              <span key={j}>
                {line}
                {j < paragraph.split('\n').length - 1 && <br />}
              </span>
            ))}
          </p>
        ))}
      </section>

      {/* Proof (for L1+) */}
      {kblock.proof && (
        <section className="kblock-detail__proof">
          <h3 className="kblock-detail__section-title">Toulmin Proof</h3>
          <div className="kblock-detail__proof-grid">
            <div className="kblock-detail__proof-item">
              <span className="kblock-detail__proof-label">Data</span>
              <span className="kblock-detail__proof-value">{kblock.proof.data}</span>
            </div>
            <div className="kblock-detail__proof-item">
              <span className="kblock-detail__proof-label">Warrant</span>
              <span className="kblock-detail__proof-value">{kblock.proof.warrant}</span>
            </div>
            <div className="kblock-detail__proof-item">
              <span className="kblock-detail__proof-label">Claim</span>
              <span className="kblock-detail__proof-value">{kblock.proof.claim}</span>
            </div>
            <div className="kblock-detail__proof-item">
              <span className="kblock-detail__proof-label">Galois Loss</span>
              <span className="kblock-detail__proof-value">
                L = {kblock.proof.galoisLoss.toFixed(3)} (confidence:{' '}
                {(kblock.confidence * 100).toFixed(0)}%)
              </span>
            </div>
          </div>
        </section>
      )}

      {/* Axiom notice (for L0) */}
      {isL0 && (
        <section className="kblock-detail__axiom-notice">
          <p>
            <strong>This is an axiom.</strong> It has no proof because it IS the foundation. The
            Mirror Test (your somatic response) is the only arbiter.
          </p>
          <p className="kblock-detail__axiom-question">
            "Does this feel true for you on your best day?"
          </p>
        </section>
      )}

      {/* Derivations */}
      {(parentKBlocks.length > 0 || childKBlocks.length > 0) && (
        <section className="kblock-detail__derivations">
          {/* Derives from */}
          {parentKBlocks.length > 0 && (
            <div className="kblock-detail__derives-from">
              <h3 className="kblock-detail__section-title">Derives From</h3>
              <ul className="kblock-detail__derivation-list">
                {parentKBlocks.map((parent) => (
                  <li key={parent.id}>
                    <button
                      className="kblock-detail__derivation-link"
                      onClick={() => onNavigateToDerivation(parent.id)}
                      style={{ '--link-color': parent.color } as React.CSSProperties}
                    >
                      <span className="kblock-detail__derivation-layer">L{parent.layer}</span>
                      <span className="kblock-detail__derivation-title">{parent.title}</span>
                      <span className="kblock-detail__derivation-arrow">↗</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Derives to */}
          {childKBlocks.length > 0 && (
            <div className="kblock-detail__derives-to">
              <h3 className="kblock-detail__section-title">Derives To</h3>
              <ul className="kblock-detail__derivation-list">
                {childKBlocks.map((child) => (
                  <li key={child.id}>
                    <button
                      className="kblock-detail__derivation-link"
                      onClick={() => onNavigateToDerivation(child.id)}
                      style={{ '--link-color': child.color } as React.CSSProperties}
                    >
                      <span className="kblock-detail__derivation-layer">L{child.layer}</span>
                      <span className="kblock-detail__derivation-title">{child.title}</span>
                      <span className="kblock-detail__derivation-arrow">↘</span>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* Tags */}
      {kblock.tags.length > 0 && (
        <footer className="kblock-detail__tags">
          {kblock.tags.map((tag) => (
            <span key={tag} className="kblock-detail__tag">
              {tag}
            </span>
          ))}
        </footer>
      )}
    </article>
  );
}
