/**
 * IntegrationDialog — Confirmation dialog for file integration
 *
 * "The file waits in uploads/. When ready, it finds its layer."
 *
 * Shows:
 * - Source file name
 * - Destination path
 * - Detected layer (L1-L7)
 * - Galois loss score
 * - Discovered relationships (edges to existing K-Blocks)
 * - Any contradictions detected
 *
 * User actions:
 * - [Cancel] - Abort integration, file stays in uploads/
 * - [Integrate] - Confirm integration, create K-Block at destination
 *
 * Philosophy: Integration requires witnessing. Show the user what will happen.
 */

import { memo } from 'react';
import { FileText, ArrowRight, AlertTriangle, Link2, Layers } from 'lucide-react';
import type { IntegrationMetadata } from './types';
import './FileExplorer.css';

// =============================================================================
// Types
// =============================================================================

interface IntegrationDialogProps {
  /** Integration metadata */
  metadata: IntegrationMetadata;
  /** Called when user confirms integration */
  onConfirm: () => void;
  /** Called when user cancels */
  onCancel: () => void;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Get layer color based on Zero Seed layer.
 */
function getLayerColor(layer: string): string {
  const layerNum = parseInt(layer.replace('L', ''), 10);
  if (layerNum <= 2) return 'var(--health-critical)'; // L1-L2: Axioms
  if (layerNum <= 4) return 'var(--health-warning)'; // L3-L4: Specs
  if (layerNum <= 5) return 'var(--health-degraded)'; // L5: Implementation
  return 'var(--health-healthy)'; // L6-L7: Docs
}

/**
 * Get loss color based on Galois loss value.
 */
function getLossColor(loss: number): string {
  if (loss < 0.2) return 'var(--health-healthy)';
  if (loss < 0.4) return 'var(--health-degraded)';
  if (loss < 0.6) return 'var(--health-warning)';
  return 'var(--health-critical)';
}

/**
 * Get layer description.
 */
function getLayerDescription(layer: string): string {
  switch (layer) {
    case 'L1':
      return 'Axioms - Foundational truths';
    case 'L2':
      return 'Principles - Derived from axioms';
    case 'L3':
      return 'Protocol Specs - Interface definitions';
    case 'L4':
      return 'Application Specs - Domain logic';
    case 'L5':
      return 'Implementation - Concrete code';
    case 'L6':
      return 'Skills - How-to guides';
    case 'L7':
      return 'Documentation - Reference material';
    default:
      return 'Unknown layer';
  }
}

// =============================================================================
// Component
// =============================================================================

export const IntegrationDialog = memo(function IntegrationDialog({
  metadata,
  onConfirm,
  onCancel,
}: IntegrationDialogProps) {
  const {
    sourcePath,
    destinationPath,
    detectedLayer,
    galoisLoss,
    discoveredEdges,
    contradictions,
  } = metadata;

  const fileName = sourcePath.split('/').pop() || sourcePath;
  const hasContradictions = contradictions.length > 0;

  return (
    <div className="integration-dialog__overlay" onClick={onCancel}>
      <div className="integration-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="integration-dialog__header">
          <Layers size={20} />
          <h2 className="integration-dialog__title">Integrate File</h2>
        </div>

        {/* Body */}
        <div className="integration-dialog__body">
          {/* File flow */}
          <div className="integration-dialog__flow">
            <div className="integration-dialog__flow-item">
              <FileText size={16} />
              <span className="integration-dialog__flow-label">{fileName}</span>
            </div>
            <ArrowRight size={16} className="integration-dialog__flow-arrow" />
            <div className="integration-dialog__flow-item">
              <FileText size={16} />
              <span className="integration-dialog__flow-label">{destinationPath}</span>
            </div>
          </div>

          {/* Layer assignment */}
          <div className="integration-dialog__section">
            <div className="integration-dialog__section-title">Layer Assignment</div>
            <div
              className="integration-dialog__layer-badge"
              style={{ '--layer-color': getLayerColor(detectedLayer) } as React.CSSProperties}
            >
              <span className="integration-dialog__layer-badge-label">{detectedLayer}</span>
              <span className="integration-dialog__layer-badge-description">
                {getLayerDescription(detectedLayer)}
              </span>
            </div>
          </div>

          {/* Galois loss */}
          <div className="integration-dialog__section">
            <div className="integration-dialog__section-title">Galois Loss</div>
            <div className="integration-dialog__loss">
              <div
                className="integration-dialog__loss-bar"
                style={{
                  '--loss-width': `${galoisLoss * 100}%`,
                  '--loss-color': getLossColor(galoisLoss),
                } as React.CSSProperties}
              >
                <div className="integration-dialog__loss-bar-fill" />
              </div>
              <span className="integration-dialog__loss-value">
                {(galoisLoss * 100).toFixed(1)}%
              </span>
            </div>
            <div className="integration-dialog__loss-hint">
              Information loss during integration (lower is better)
            </div>
          </div>

          {/* Discovered edges */}
          {discoveredEdges.length > 0 && (
            <div className="integration-dialog__section">
              <div className="integration-dialog__section-title">
                <Link2 size={16} />
                Discovered Relationships
              </div>
              <ul className="integration-dialog__edge-list">
                {discoveredEdges.map((edge, index) => (
                  <li key={index} className="integration-dialog__edge-item">
                    <span className="integration-dialog__edge-type">[{edge.type}]</span>
                    <span className="integration-dialog__edge-arrow">→</span>
                    <span className="integration-dialog__edge-target">{edge.target}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Contradictions */}
          {hasContradictions && (
            <div className="integration-dialog__section integration-dialog__section--warning">
              <div className="integration-dialog__section-title">
                <AlertTriangle size={16} />
                Contradictions Detected
              </div>
              <ul className="integration-dialog__contradiction-list">
                {contradictions.map((contradiction, index) => (
                  <li key={index} className="integration-dialog__contradiction-item">
                    {contradiction}
                  </li>
                ))}
              </ul>
              <div className="integration-dialog__contradiction-hint">
                Review these contradictions before integrating.
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="integration-dialog__footer">
          <button
            className="btn-base btn-secondary"
            onClick={onCancel}
          >
            Cancel
          </button>
          <button
            className="btn-base btn-primary"
            onClick={onConfirm}
            disabled={hasContradictions}
          >
            Integrate
          </button>
        </div>
      </div>
    </div>
  );
});
