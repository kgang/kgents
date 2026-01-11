/**
 * FeedItem Component
 *
 * "Everything is a K-Block"
 *
 * Displays a single K-Block in the feed with:
 * - Layer badge
 * - Loss indicator
 * - Timestamp
 * - Preview text
 * - Expand/collapse
 * - Contradiction badge (if contradictions detected)
 */

import { memo, useCallback, useMemo } from 'react';
import type { FeedItemProps, KBlock } from './types';
import { LAYER_NAMES, LAYER_COLORS, LOSS_COLORS, LOSS_THRESHOLDS } from './types';
import { ContradictionBadge } from '../Contradiction/ContradictionBadge';
import {
  useItemContradictions,
  getSeverityLevel,
  getOtherKBlock,
} from '../../hooks/useItemContradictions';

// =============================================================================
// Component
// =============================================================================

export const FeedItem = memo(function FeedItem({
  kblock,
  isExpanded,
  onClick,
  onView,
  onEngage,
  onDismiss,
  onContradictionClick,
  className = '',
}: FeedItemProps) {
  // Format timestamp
  const formattedTime = formatTimestamp(kblock.updatedAt);

  // Get loss color
  const lossColor = getLossColor(kblock.loss);

  // Get layer color
  const layerColor = LAYER_COLORS[kblock.layer] || '#666';

  // Handle view on mount
  useCallback(() => {
    onView?.();
  }, [onView]);

  // Fetch contradictions for this K-Block
  const {
    contradictions,
    count: contradictionCount,
    loading: contradictionsLoading,
  } = useItemContradictions(kblock.id);

  // Calculate the highest severity among all contradictions
  const maxSeverity = useMemo(() => {
    if (contradictions.length === 0) return 0;
    return Math.max(...contradictions.map((c) => c.severity));
  }, [contradictions]);

  // Handle contradiction badge click
  const handleContradictionClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation(); // Don't trigger feed item click

      if (contradictions.length > 0 && onContradictionClick) {
        // Get the first contradicting K-Block to pass to the handler
        const firstContradiction = contradictions[0];
        const otherKBlock = getOtherKBlock(kblock.id, firstContradiction);

        // Create a minimal KBlock from the summary for the callback
        const contradictingKBlock: KBlock = {
          id: otherKBlock.id,
          title: otherKBlock.title || 'Untitled',
          content: otherKBlock.content,
          layer: otherKBlock.layer || 1,
          loss:
            firstContradiction.k_block_a.id === kblock.id
              ? firstContradiction.loss_b
              : firstContradiction.loss_a,
          author: 'unknown',
          createdAt: new Date(),
          updatedAt: new Date(),
          tags: [],
          principles: [],
          edgeCount: 0,
        };

        onContradictionClick(contradictingKBlock);
      }
    },
    [contradictions, kblock.id, onContradictionClick]
  );

  return (
    <div
      className={`feed-item ${isExpanded ? 'feed-item--expanded' : ''} ${className}`}
      onClick={onClick}
    >
      {/* Header */}
      <div className="feed-item__header">
        {/* Layer badge */}
        <div
          className="feed-item__layer-badge"
          style={{ backgroundColor: layerColor }}
          title={`Layer ${kblock.layer}: ${LAYER_NAMES[kblock.layer]}`}
        >
          L{kblock.layer}
        </div>

        {/* Title */}
        <div className="feed-item__title">{kblock.title}</div>

        {/* Contradiction badge (show if contradictions exist) */}
        {!contradictionsLoading && contradictionCount > 0 && (
          <div className="feed-item__contradiction" onClick={handleContradictionClick}>
            <ContradictionBadge
              hasContradiction={true}
              severity={getSeverityLevel(maxSeverity)}
              size="sm"
              tooltip={`${contradictionCount} contradiction${contradictionCount > 1 ? 's' : ''} detected`}
            />
            {contradictionCount > 1 && (
              <span className="feed-item__contradiction-count">{contradictionCount}</span>
            )}
          </div>
        )}

        {/* Loss indicator */}
        <div
          className="feed-item__loss"
          style={{ color: lossColor }}
          title={`Loss: ${(kblock.loss * 100).toFixed(1)}%`}
        >
          <div
            className="feed-item__loss-bar"
            style={{
              width: `${kblock.loss * 100}%`,
              backgroundColor: lossColor,
            }}
          />
        </div>

        {/* Timestamp */}
        <div className="feed-item__time" title={kblock.updatedAt.toISOString()}>
          {formattedTime}
        </div>
      </div>

      {/* Metadata */}
      <div className="feed-item__meta">
        {/* Author */}
        <div className="feed-item__author">{kblock.author}</div>

        {/* Edge count */}
        <div className="feed-item__edges" title="Edge count">
          {kblock.edgeCount} edges
        </div>

        {/* Tags */}
        {kblock.tags.length > 0 && (
          <div className="feed-item__tags">
            {kblock.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="feed-item__tag">
                {tag}
              </span>
            ))}
            {kblock.tags.length > 3 && (
              <span className="feed-item__tag feed-item__tag--more">+{kblock.tags.length - 3}</span>
            )}
          </div>
        )}
      </div>

      {/* Preview or full content */}
      <div className="feed-item__content">
        {isExpanded ? (
          // Full content (Markdown rendered)
          <div className="feed-item__full-content">{kblock.content}</div>
        ) : (
          // Preview
          <div className="feed-item__preview">
            {kblock.preview || kblock.content.substring(0, 200)}
            {kblock.content.length > 200 && '...'}
          </div>
        )}
      </div>

      {/* Principles (only show when expanded) */}
      {isExpanded && kblock.principles.length > 0 && (
        <div className="feed-item__principles">
          <div className="feed-item__principles-label">Principles:</div>
          <div className="feed-item__principles-list">
            {kblock.principles.map((principle) => (
              <span key={principle} className="feed-item__principle">
                {principle}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Actions (only show when expanded) */}
      {isExpanded && (
        <div className="feed-item__actions">
          <button
            className="feed-item__action"
            onClick={(e) => {
              e.stopPropagation();
              onEngage?.();
            }}
            title="Edit this K-Block"
          >
            Edit
          </button>

          <button
            className="feed-item__action"
            onClick={(e) => {
              e.stopPropagation();
              // TODO: Navigate to K-Block detail
            }}
            title="View full K-Block"
          >
            View
          </button>

          <button
            className="feed-item__action feed-item__action--secondary"
            onClick={(e) => {
              e.stopPropagation();
              onDismiss?.();
            }}
            title="Dismiss from feed"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Expand indicator */}
      <div className="feed-item__expand-indicator">{isExpanded ? '▲' : '▼'}</div>
    </div>
  );
});

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Format timestamp relative to now.
 */
function formatTimestamp(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  // Less than 1 minute
  if (diff < 60 * 1000) {
    return 'just now';
  }

  // Less than 1 hour
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    return `${minutes}m ago`;
  }

  // Less than 1 day
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}h ago`;
  }

  // Less than 1 week
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));
    return `${days}d ago`;
  }

  // More than 1 week - show full date
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

/**
 * Get color for loss value.
 */
function getLossColor(loss: number): string {
  if (loss < LOSS_THRESHOLDS.HEALTHY) {
    return LOSS_COLORS.HEALTHY;
  } else if (loss < LOSS_THRESHOLDS.WARNING) {
    return LOSS_COLORS.WARNING;
  } else if (loss < LOSS_THRESHOLDS.CRITICAL) {
    return LOSS_COLORS.CRITICAL;
  }
  return LOSS_COLORS.EMERGENCY;
}
