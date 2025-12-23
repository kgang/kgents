/**
 * PortalToken — Expandable hyperedge for inline navigation.
 *
 * THE KEY UNIFICATION: "The doc comes to you."
 *
 * Renders expandable edges like:
 *   ▶ [tests] ──→ 3 files
 *   ▶ [implements] ──→ services/brain/
 *   ▶ [extends] ──→ d-gent.md
 *
 * Expands inline to show destinations without navigating away.
 *
 * "You don't go to the doc. The doc comes to you."
 *
 * @see spec/protocols/portal-token.md
 */

import { memo, useCallback, useState } from 'react';

import { GrowingContainer } from '../../components/genesis/GrowingContainer';

import './tokens.css';

// =============================================================================
// Types
// =============================================================================

export interface PortalDestination {
  path: string;
  title?: string;
  preview?: string;
  exists?: boolean;
}

interface PortalTokenProps {
  /** Edge type (e.g., "tests", "implements", "extends") */
  edgeType: string;
  /** Source path (where this portal is from) */
  sourcePath?: string;
  /** Destinations this edge connects to */
  destinations: PortalDestination[];
  /** Called when a destination is clicked */
  onNavigate?: (path: string) => void;
  /** Called when expansion state changes */
  onExpand?: (expanded: boolean) => void;
  /** Additional class names */
  className?: string;
  /** Initially expanded? */
  defaultExpanded?: boolean;
  /** Maximum destinations to show before "show more" */
  maxVisible?: number;
}

// =============================================================================
// Component
// =============================================================================

export const PortalToken = memo(function PortalToken({
  edgeType,
  sourcePath: _sourcePath,
  destinations,
  onNavigate,
  onExpand,
  className,
  defaultExpanded = false,
  maxVisible = 5,
}: PortalTokenProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [showAll, setShowAll] = useState(false);

  const handleToggleExpand = useCallback(() => {
    const newState = !expanded;
    setExpanded(newState);
    onExpand?.(newState);
  }, [expanded, onExpand]);

  const handleDestinationClick = useCallback(
    (path: string) => {
      onNavigate?.(path);
    },
    [onNavigate]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleToggleExpand();
      }
    },
    [handleToggleExpand]
  );

  const count = destinations.length;
  const visibleDestinations = showAll ? destinations : destinations.slice(0, maxVisible);
  const hasMore = !showAll && destinations.length > maxVisible;

  return (
    <div
      className={`portal-token ${expanded ? 'portal-token--expanded' : ''} ${className ?? ''}`}
      data-edge-type={edgeType}
      data-count={count}
    >
      {/* Toggle button */}
      <button
        type="button"
        className="portal-token__toggle"
        onClick={handleToggleExpand}
        onKeyDown={handleKeyDown}
        title={expanded ? `Collapse ${edgeType}` : `Expand ${edgeType} (${count})`}
        aria-expanded={expanded}
      >
        <span className="portal-token__icon">{expanded ? '\u25BC' : '\u25B6'}</span>
        <span className="portal-token__edge-type">[{edgeType}]</span>
        <span className="portal-token__arrow">──→</span>
        <span className="portal-token__count">
          {count} {count === 1 ? 'item' : 'items'}
        </span>
      </button>

      {/* Expanded destinations */}
      {expanded && (
        <GrowingContainer>
          <ul className="portal-token__list">
            {visibleDestinations.map((dest, index) => (
              <li
                key={dest.path}
                className={`portal-token__item ${dest.exists === false ? 'portal-token__item--missing' : ''}`}
              >
                <button
                  type="button"
                  className="portal-token__destination"
                  onClick={() => handleDestinationClick(dest.path)}
                  disabled={dest.exists === false}
                  title={dest.preview || dest.path}
                >
                  <span className="portal-token__dest-index">{index + 1}.</span>
                  <span className="portal-token__dest-path">{dest.title || dest.path}</span>
                  {dest.exists === false && (
                    <span className="portal-token__dest-missing">missing</span>
                  )}
                </button>
                {dest.preview && <div className="portal-token__preview">{dest.preview}</div>}
              </li>
            ))}
            {hasMore && (
              <li className="portal-token__show-more">
                <button
                  type="button"
                  className="portal-token__show-more-btn"
                  onClick={() => setShowAll(true)}
                >
                  +{destinations.length - maxVisible} more
                </button>
              </li>
            )}
          </ul>
        </GrowingContainer>
      )}
    </div>
  );
});
