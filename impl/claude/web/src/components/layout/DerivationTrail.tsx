/**
 * DerivationTrail — Breadcrumb showing axiom → current path
 *
 * "The proof IS the decision. The mark IS the witness."
 *
 * Shows the derivation chain from axioms to the current focal point,
 * allowing users to navigate back through the epistemic hierarchy.
 */

import { memo, useCallback } from 'react';
import { useTelescope, getLayerName, getLayerIcon } from '../../hooks/useTelescopeState';

import './DerivationTrail.css';

// =============================================================================
// Types
// =============================================================================

interface DerivationTrailProps {
  /** Optional: Show in compact mode (icons only) */
  compact?: boolean;

  /** Optional: Max number of breadcrumbs to show */
  maxItems?: number;
}

// =============================================================================
// Component
// =============================================================================

export const DerivationTrail = memo(function DerivationTrail({
  compact = false,
  maxItems = 5,
}: DerivationTrailProps) {
  const { state, dispatch } = useTelescope();

  const handleItemClick = useCallback(
    (index: number) => {
      // Navigate back to this point in history
      const targetItem = state.focalHistory[index];
      if (targetItem) {
        dispatch({ type: 'SET_FOCAL_POINT', nodeId: targetItem.nodeId, layer: targetItem.layer });
      }
    },
    [state.focalHistory, dispatch]
  );

  const handleBackClick = useCallback(() => {
    dispatch({ type: 'NAVIGATE_DERIVATION' });
  }, [dispatch]);

  // Show only recent history
  const visibleHistory = state.focalHistory.slice(-maxItems);
  const hasMore = state.focalHistory.length > maxItems;

  // If no focal point and no history, don't render
  if (!state.focalPoint && state.focalHistory.length === 0) {
    return null;
  }

  return (
    <nav
      className={`derivation-trail ${compact ? 'derivation-trail--compact' : ''}`}
      aria-label="Derivation breadcrumb trail"
    >
      {/* Back button */}
      {state.focalHistory.length > 0 && (
        <button
          className="derivation-trail__back"
          onClick={handleBackClick}
          title="Navigate to parent (derivation)"
          aria-label="Navigate back in derivation chain"
        >
          <span className="derivation-trail__back-icon">↖</span>
        </button>
      )}

      {/* Breadcrumb items */}
      <ol className="derivation-trail__list">
        {/* Show ellipsis if history is truncated */}
        {hasMore && (
          <li className="derivation-trail__item derivation-trail__item--ellipsis" aria-hidden="true">
            <span className="derivation-trail__ellipsis">…</span>
          </li>
        )}

        {/* History items */}
        {visibleHistory.map((item: { nodeId: string; layer: number }, index: number) => {
          const globalIndex = state.focalHistory.length - visibleHistory.length + index;
          const layerIcon = getLayerIcon(item.layer);
          const layerName = getLayerName(item.layer);

          return (
            <li key={`${item.nodeId}-${globalIndex}`} className="derivation-trail__item">
              <button
                className="derivation-trail__link"
                onClick={() => handleItemClick(globalIndex)}
                title={`${layerName}: ${item.nodeId}`}
                aria-label={`Navigate to ${layerName}: ${item.nodeId}`}
              >
                <span className="derivation-trail__icon" aria-hidden="true">
                  {layerIcon}
                </span>
                {!compact && (
                  <span className="derivation-trail__label">
                    {formatNodeId(item.nodeId)}
                  </span>
                )}
              </button>
              <span className="derivation-trail__separator" aria-hidden="true">
                →
              </span>
            </li>
          );
        })}

        {/* Current focal point */}
        {state.focalPoint && (
          <li className="derivation-trail__item derivation-trail__item--current">
            <span className="derivation-trail__current">
              <span className="derivation-trail__icon" aria-hidden="true">
                ◉
              </span>
              {!compact && (
                <span className="derivation-trail__label">
                  {formatNodeId(state.focalPoint)}
                </span>
              )}
            </span>
          </li>
        )}
      </ol>
    </nav>
  );
});

// =============================================================================
// Helpers
// =============================================================================

/**
 * Format node ID for display (truncate long paths).
 */
function formatNodeId(nodeId: string): string {
  // If it's a file path, show just the filename
  if (nodeId.includes('/')) {
    const parts = nodeId.split('/');
    return parts[parts.length - 1];
  }

  // Truncate long IDs
  if (nodeId.length > 30) {
    return nodeId.slice(0, 27) + '...';
  }

  return nodeId;
}

export default DerivationTrail;
