/**
 * FeedProjection — Chronological Stream Item
 *
 * Renders K-Block as a feed item (similar to FeedItem primitive).
 * Shows: layer, title, preview, timestamp, tags, edge count.
 */

import { memo } from 'react';
import type { ProjectionComponentProps } from '../types';
import { LAYER_NAMES, LAYER_COLORS } from '../types';
import './FeedProjection.css';

export const FeedProjection = memo(function FeedProjection({
  kblock,
  className = '',
}: ProjectionComponentProps) {
  const layerName = kblock.zeroSeedLayer
    ? LAYER_NAMES[kblock.zeroSeedLayer]
    : 'File';
  const layerColor = kblock.zeroSeedLayer
    ? LAYER_COLORS[kblock.zeroSeedLayer]
    : '#666';

  // Extract title from path
  const title = kblock.path.split('/').pop() || kblock.id;

  // Preview (first 200 chars)
  const preview = kblock.content.substring(0, 200);
  const hasMore = kblock.content.length > 200;

  // Format timestamp
  const timestamp = formatRelativeTime(kblock.updatedAt);

  return (
    <div className={`feed-projection ${className}`}>
      {/* Header */}
      <div className="feed-projection__header">
        {/* Layer badge */}
        <div
          className="feed-projection__layer-badge"
          style={{ backgroundColor: layerColor }}
          title={layerName}
        >
          L{kblock.zeroSeedLayer ?? 'F'}
        </div>

        {/* Title */}
        <div className="feed-projection__title">{title}</div>

        {/* Timestamp */}
        <div className="feed-projection__timestamp" title={kblock.updatedAt.toISOString()}>
          {timestamp}
        </div>
      </div>

      {/* Preview */}
      <div className="feed-projection__preview">
        {preview}
        {hasMore && '...'}
      </div>

      {/* Metadata */}
      <div className="feed-projection__metadata">
        {/* Author */}
        <span className="feed-projection__author">{kblock.createdBy}</span>

        {/* Edge count */}
        <span className="feed-projection__edges">
          {kblock.incomingEdges.length + kblock.outgoingEdges.length} edges
        </span>

        {/* Tags */}
        {kblock.tags.length > 0 && (
          <div className="feed-projection__tags">
            {kblock.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="feed-projection__tag">
                {tag}
              </span>
            ))}
            {kblock.tags.length > 3 && (
              <span className="feed-projection__tag feed-projection__tag--more">
                +{kblock.tags.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
});

// Helper: Format relative timestamp
function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  if (diff < 60 * 1000) return 'just now';
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    return `${minutes}m ago`;
  }
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}h ago`;
  }
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));
    return `${days}d ago`;
  }

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}
