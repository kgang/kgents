/**
 * CachedBadge: Prominent cache indicator.
 *
 * Displays [CACHED] badge with age tooltip.
 * Positioned top-right, amber/yellow styling.
 */

import React from 'react';
import type { CacheMeta } from '../../reactive/schema';

interface CachedBadgeProps {
  cache: CacheMeta;
  /** Position style */
  position?: 'inline' | 'absolute';
}

/**
 * Format cache age as human-readable string.
 */
function formatCacheAge(cachedAt: string | null): string {
  if (!cachedAt) return 'cached';

  const cached = new Date(cachedAt);
  const now = new Date();
  const diffMs = now.getTime() - cached.getTime();

  if (diffMs < 60000) {
    const secs = Math.floor(diffMs / 1000);
    return `${secs}s ago`;
  }
  if (diffMs < 3600000) {
    const mins = Math.floor(diffMs / 60000);
    return `${mins}m ago`;
  }
  if (diffMs < 86400000) {
    const hours = Math.floor(diffMs / 3600000);
    return `${hours}h ago`;
  }
  const days = Math.floor(diffMs / 86400000);
  return `${days}d ago`;
}

export function CachedBadge({ cache, position = 'inline' }: CachedBadgeProps) {
  const age = formatCacheAge(cache.cachedAt);
  const ttlInfo = cache.ttlSeconds ? ` (TTL: ${cache.ttlSeconds}s)` : '';
  const tooltip = `Cached ${age}${ttlInfo}${cache.deterministic ? ' • Deterministic' : ''}`;

  const baseStyles: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '4px',
    padding: '2px 8px',
    backgroundColor: '#fef3c7',
    color: '#92400e',
    border: '1px solid #f59e0b',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 600,
    fontFamily: 'monospace',
  };

  const absoluteStyles: React.CSSProperties =
    position === 'absolute'
      ? {
          position: 'absolute',
          top: '8px',
          right: '8px',
          zIndex: 10,
        }
      : {};

  return (
    <span
      className="kgents-cached-badge"
      style={{ ...baseStyles, ...absoluteStyles }}
      title={tooltip}
      aria-label={`Cached response: ${age}`}
    >
      <span style={{ fontSize: '10px' }}>◐</span>
      [CACHED {age}]
    </span>
  );
}

export default CachedBadge;
