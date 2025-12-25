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
 * Also supports authoring states:
 *   💭 @[natural language query?]     — UNPARSED (can be cured)
 *   ◐ @[resolving...]                  — CURING (LLM processing)
 *   ⚠️ @[couldn't resolve]            — FAILED
 *
 * Expands inline to show destinations without navigating away.
 *
 * "You don't go to the doc. The doc comes to you."
 * "And now: authoring IS exploring. Write a portal, open a world."
 *
 * @see spec/protocols/portal-token.md §15 (Deep Integration)
 */

import { memo, useCallback, useState } from 'react';

import { GrowingContainer } from '../joy';
import { PortalResourceIcon } from './PortalResourceIcon';
import { PortalContent } from './PortalContent';
import type { PortalResourceType, ResolvedResource } from './types';

import './tokens.css';

// =============================================================================
// Types
// =============================================================================

/**
 * Portal authoring state — beyond expand/collapse.
 * See spec/protocols/portal-token.md §15.2
 */
export type PortalAuthoringState =
  | 'RESOLVED' // Has edge_type -> destination
  | 'UNPARSED' // Natural language, missing ->
  | 'CURING' // LLM resolution in progress
  | 'FAILED'; // LLM couldn't resolve

export interface PortalDestination {
  path: string;
  title?: string;
  preview?: string;
  exists?: boolean;
}

export interface PortalCureResult {
  success: boolean;
  resolvedPortal?: string;
  confidence: number;
  alternatives?: string[];
}

interface PortalTokenProps {
  /** Edge type (e.g., "tests", "implements", "extends") — null if unparsed */
  edgeType: string | null;
  /** Source path (where this portal is from) */
  sourcePath?: string;
  /** Destinations this edge connects to — empty if unparsed */
  destinations: PortalDestination[];
  /** Authoring state — defaults to RESOLVED for backward compatibility */
  authoringState?: PortalAuthoringState;
  /** Natural language query (if UNPARSED) */
  naturalLanguage?: string;
  /** Called when a destination is clicked */
  onNavigate?: (path: string) => void;
  /** Called when expansion state changes (receives evidence_id if witnessed) */
  onExpand?: (expanded: boolean, evidenceId?: string) => void;
  /** Called when user wants to cure an unparsed portal */
  onCure?: () => Promise<PortalCureResult>;
  /** Additional class names */
  className?: string;
  /** Initially expanded? */
  defaultExpanded?: boolean;
  /** Maximum destinations to show before "show more" */
  maxVisible?: number;
  /** Whether this portal is the current cursor target in PORTAL mode */
  isCursor?: boolean;
  /** Whether this portal was auto-discovered (vs authored) */
  isDiscovered?: boolean;
  /** Resource type for typed portals (NEW) */
  resourceType?: PortalResourceType;
  /** Resolved resource content (NEW) */
  resolvedResource?: ResolvedResource;
  /** Current nesting depth (for witnessing significance rules) */
  depth?: number;
  /** Evidence ID if this portal expansion was witnessed */
  evidenceId?: string;
}

// =============================================================================
// Component
// =============================================================================

export const PortalToken = memo(function PortalToken({
  edgeType,
  sourcePath: _sourcePath,
  destinations,
  authoringState = 'RESOLVED',
  naturalLanguage,
  onNavigate,
  onExpand,
  onCure,
  className,
  defaultExpanded = false,
  maxVisible = 5,
  isCursor = false,
  isDiscovered = false,
  resourceType,
  resolvedResource,
  depth: _depth = 0,
  evidenceId: initialEvidenceId,
}: PortalTokenProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [showAll, setShowAll] = useState(false);
  const [curing, setCuring] = useState(false);
  const [cureError, setCureError] = useState<string | null>(null);
  const [evidenceId] = useState<string | undefined>(initialEvidenceId);

  const handleToggleExpand = useCallback(() => {
    if (authoringState !== 'RESOLVED') return; // Can't expand unparsed portals
    const newState = !expanded;
    setExpanded(newState);
    // Pass evidence_id to parent if we have one
    onExpand?.(newState, evidenceId);
  }, [expanded, onExpand, authoringState, evidenceId]);

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
      // 'c' key to cure (when in PORTAL mode, handled by parent)
    },
    [handleToggleExpand]
  );

  const handleCure = useCallback(async () => {
    if (!onCure || curing) return;
    setCuring(true);
    setCureError(null);
    try {
      const result = await onCure();
      if (!result.success) {
        setCureError('Could not resolve portal');
      }
      // Parent will handle updating the portal state on success
    } catch (err) {
      setCureError(err instanceof Error ? err.message : 'Cure failed');
    } finally {
      setCuring(false);
    }
  }, [onCure, curing]);

  const count = destinations.length;
  const visibleDestinations = showAll ? destinations : destinations.slice(0, maxVisible);
  const hasMore = !showAll && destinations.length > maxVisible;

  // Build class names
  const classNames = [
    'portal-token',
    expanded && 'portal-token--expanded',
    isCursor && 'portal-token--cursor',
    isDiscovered && 'portal-token--discovered',
    `portal-token--${authoringState.toLowerCase()}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  // ==========================================================================
  // Render: UNPARSED portal (natural language query)
  // ==========================================================================
  if (authoringState === 'UNPARSED' || authoringState === 'CURING' || authoringState === 'FAILED') {
    return (
      <div
        className={classNames}
        data-authoring-state={authoringState}
      >
        <div className="portal-token__unparsed">
          <span className="portal-token__unparsed-icon">
            {authoringState === 'CURING' ? '◐' : authoringState === 'FAILED' ? '⚠️' : '💭'}
          </span>
          <span className="portal-token__unparsed-text">
            @[{naturalLanguage || '...'}]
          </span>
          {authoringState === 'UNPARSED' && onCure && (
            <button
              type="button"
              className="portal-token__cure-btn"
              onClick={handleCure}
              disabled={curing}
              title="Cure with LLM"
            >
              ⚡ Cure
            </button>
          )}
          {authoringState === 'CURING' && (
            <span className="portal-token__curing-indicator">Resolving...</span>
          )}
          {authoringState === 'FAILED' && cureError && (
            <span className="portal-token__error">{cureError}</span>
          )}
        </div>
      </div>
    );
  }

  // ==========================================================================
  // Render: RESOLVED portal (standard expandable)
  // ==========================================================================
  return (
    <div
      className={classNames}
      data-edge-type={edgeType}
      data-count={count}
      data-authoring-state={authoringState}
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
        {resourceType && <PortalResourceIcon type={resourceType} />}
        <span className="portal-token__edge-type">[{edgeType}]</span>
        <span className="portal-token__arrow">──→</span>
        <span className="portal-token__count">
          {count} {count === 1 ? 'item' : 'items'}
        </span>
        {isDiscovered && (
          <span className="portal-token__discovered-badge" title="Auto-discovered">
            ✨
          </span>
        )}
        {evidenceId && (
          <span className="portal-token__witness-badge" title={`Witnessed: ${evidenceId}`}>
            👁
          </span>
        )}
      </button>

      {/* Expanded content */}
      {expanded && (
        <GrowingContainer>
          {/* If we have a resolved resource, show rich content */}
          {resolvedResource ? (
            <div className="portal-token__resolved-content">
              <PortalContent resource={resolvedResource} compact={false} />
            </div>
          ) : (
            /* Otherwise, show destination list (legacy behavior) */
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
          )}
        </GrowingContainer>
      )}
    </div>
  );
});
