/**
 * PortalProjection — Expanded Full Detail View
 *
 * Renders K-Block with full content, metadata, edges, and lineage.
 * This is the "expanded" view for deep inspection.
 */

import { memo } from 'react';
import type { ProjectionComponentProps } from '../types';
import { LAYER_NAMES, LAYER_COLORS } from '../types';
import './PortalProjection.css';

export const PortalProjection = memo(function PortalProjection({
  kblock,
  className = '',
}: ProjectionComponentProps) {
  const layerName = kblock.zeroSeedLayer
    ? LAYER_NAMES[kblock.zeroSeedLayer]
    : 'File';
  const layerColor = kblock.zeroSeedLayer
    ? LAYER_COLORS[kblock.zeroSeedLayer]
    : '#666';

  return (
    <div className={`portal-projection ${className}`}>
      {/* Header */}
      <div className="portal-projection__header">
        <div
          className="portal-projection__layer-badge"
          style={{ backgroundColor: layerColor }}
        >
          {layerName}
        </div>
        <h2 className="portal-projection__title">{kblock.path}</h2>
      </div>

      {/* Metadata */}
      <div className="portal-projection__metadata">
        <div className="portal-projection__meta-item">
          <span className="portal-projection__meta-label">ID:</span>
          <span className="portal-projection__meta-value">{kblock.id}</span>
        </div>
        <div className="portal-projection__meta-item">
          <span className="portal-projection__meta-label">Isolation:</span>
          <span className="portal-projection__meta-value">{kblock.isolation}</span>
        </div>
        <div className="portal-projection__meta-item">
          <span className="portal-projection__meta-label">Confidence:</span>
          <span className="portal-projection__meta-value">
            {(kblock.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="portal-projection__meta-item">
          <span className="portal-projection__meta-label">Created:</span>
          <span className="portal-projection__meta-value">
            {kblock.createdAt.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="portal-projection__content">
        <div className="portal-projection__content-label">Content:</div>
        <div className="portal-projection__content-body">{kblock.content}</div>
      </div>

      {/* Edges */}
      {(kblock.incomingEdges.length > 0 || kblock.outgoingEdges.length > 0) && (
        <div className="portal-projection__edges">
          {kblock.incomingEdges.length > 0 && (
            <div className="portal-projection__edge-section">
              <div className="portal-projection__edge-label">
                Incoming ({kblock.incomingEdges.length}):
              </div>
              {kblock.incomingEdges.map((edge) => (
                <div key={edge.id} className="portal-projection__edge">
                  {edge.sourceId} → {edge.kind}
                </div>
              ))}
            </div>
          )}
          {kblock.outgoingEdges.length > 0 && (
            <div className="portal-projection__edge-section">
              <div className="portal-projection__edge-label">
                Outgoing ({kblock.outgoingEdges.length}):
              </div>
              {kblock.outgoingEdges.map((edge) => (
                <div key={edge.id} className="portal-projection__edge">
                  {edge.kind} → {edge.targetId}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tags */}
      {kblock.tags.length > 0 && (
        <div className="portal-projection__tags">
          <div className="portal-projection__tags-label">Tags:</div>
          <div className="portal-projection__tags-list">
            {kblock.tags.map((tag) => (
              <span key={tag} className="portal-projection__tag">
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Lineage */}
      {kblock.lineage.length > 0 && (
        <div className="portal-projection__lineage">
          <div className="portal-projection__lineage-label">Lineage:</div>
          <div className="portal-projection__lineage-list">
            {kblock.lineage.map((parentId) => (
              <span key={parentId} className="portal-projection__lineage-item">
                {parentId}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});
