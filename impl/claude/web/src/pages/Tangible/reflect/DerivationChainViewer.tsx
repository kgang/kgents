/**
 * DerivationChainViewer - Visual derivation chain viewer
 *
 * Features:
 * - Visual chain from file -> spec -> principle -> axiom
 * - Layer colors (L0 = gold, L1 = silver, etc.)
 * - Click any node to navigate
 * - Shows Galois loss at each step
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo } from 'react';
import { Layers, ArrowRight, X, AlertTriangle } from 'lucide-react';
import type { DerivationStep, DerivationChain } from './types';
import { LAYER_COLORS, LAYER_NAMES } from './types';

// =============================================================================
// Types
// =============================================================================

export interface DerivationChainViewerProps {
  chain: DerivationChain | null;
  onClose: () => void;
  onNavigate: (path: string) => void;
  isModal?: boolean;
}

// =============================================================================
// Subcomponents
// =============================================================================

interface ChainNodeProps {
  step: DerivationStep;
  isFirst: boolean;
  isLast: boolean;
  isCurrent: boolean;
  onNavigate: () => void;
}

const ChainNode = memo(function ChainNode({
  step,
  isFirst,
  isLast,
  isCurrent,
  onNavigate,
}: ChainNodeProps) {
  const lossPercentage = (step.galoisLoss * 100).toFixed(1);
  const hasSignificantLoss = step.galoisLoss > 0.1;

  return (
    <div className="derivation-chain__node-wrapper">
      {/* Connection line */}
      {!isFirst && (
        <div className="derivation-chain__connector">
          <div className="derivation-chain__line" />
          {step.galoisLoss > 0 && (
            <div
              className="derivation-chain__loss-indicator"
              data-severity={hasSignificantLoss ? 'high' : 'low'}
            >
              -{lossPercentage}%
            </div>
          )}
        </div>
      )}

      {/* Node */}
      <button
        className="derivation-chain__node"
        data-layer={step.layer}
        data-current={isCurrent}
        onClick={onNavigate}
        style={{ '--layer-color': LAYER_COLORS[step.layer] } as React.CSSProperties}
      >
        {/* Layer badge */}
        <div className="derivation-chain__layer-badge">
          <span className="derivation-chain__layer-num">L{step.layer}</span>
          <span className="derivation-chain__layer-name">{LAYER_NAMES[step.layer]}</span>
        </div>

        {/* Title */}
        <div className="derivation-chain__node-title">{step.title}</div>

        {/* Description */}
        {step.description && (
          <div className="derivation-chain__node-description">{step.description}</div>
        )}

        {/* Path */}
        {step.path && <div className="derivation-chain__node-path">{step.path}</div>}

        {/* Loss warning */}
        {hasSignificantLoss && (
          <div className="derivation-chain__node-warning">
            <AlertTriangle size={10} />
            <span>High derivation loss</span>
          </div>
        )}
      </button>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const DerivationChainViewer = memo(function DerivationChainViewer({
  chain,
  onClose,
  onNavigate,
  isModal = false,
}: DerivationChainViewerProps) {
  if (!chain) return null;

  // Sort steps by layer (L0 first)
  const sortedSteps = [...chain.steps].sort((a, b) => a.layer - b.layer);

  // Find current step
  const currentIndex = sortedSteps.findIndex(
    (s) => s.path === chain.sourcePath || s.id === chain.sourceId
  );

  return (
    <div className={`derivation-chain ${isModal ? 'derivation-chain--modal' : ''}`}>
      {/* Header */}
      <div className="derivation-chain__header">
        <div className="derivation-chain__header-title">
          <Layers size={14} />
          <span>Derivation Chain</span>
        </div>
        <div className="derivation-chain__header-stats">
          <span className="derivation-chain__stat">
            {sortedSteps.length} step{sortedSteps.length !== 1 ? 's' : ''}
          </span>
          {chain.totalLoss > 0 && (
            <span
              className="derivation-chain__stat derivation-chain__stat--loss"
              data-severity={chain.totalLoss > 0.2 ? 'high' : 'low'}
            >
              Total loss: {(chain.totalLoss * 100).toFixed(1)}%
            </span>
          )}
        </div>
        <button className="derivation-chain__close" onClick={onClose} aria-label="Close">
          <X size={14} />
        </button>
      </div>

      {/* Chain visualization */}
      <div className="derivation-chain__content">
        <div className="derivation-chain__flow">
          {sortedSteps.map((step, index) => (
            <ChainNode
              key={step.id}
              step={step}
              isFirst={index === 0}
              isLast={index === sortedSteps.length - 1}
              isCurrent={index === currentIndex}
              onNavigate={() => step.path && onNavigate(step.path)}
            />
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="derivation-chain__legend">
        <div className="derivation-chain__legend-title">Layer Legend</div>
        <div className="derivation-chain__legend-items">
          {([0, 1, 2, 3] as const).map((layer) => (
            <div
              key={layer}
              className="derivation-chain__legend-item"
              style={{ '--layer-color': LAYER_COLORS[layer] } as React.CSSProperties}
            >
              <div className="derivation-chain__legend-dot" />
              <span>
                L{layer} {LAYER_NAMES[layer]}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Help text */}
      <div className="derivation-chain__help">
        <p>Click any node to navigate to that K-Block.</p>
        <p>
          <strong>Galois loss</strong> shows coherence degradation from parent to child.
        </p>
      </div>
    </div>
  );
});

export default DerivationChainViewer;
