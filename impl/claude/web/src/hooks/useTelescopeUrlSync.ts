/**
 * useTelescopeUrlSync — Bidirectional sync between telescope state and URL
 *
 * "The URL is a projection. The state is the truth."
 *
 * Makes telescope positions bookmarkable by encoding:
 * - layer (focal distance as layer number)
 * - focal (current focal point node ID)
 * - loss (loss threshold filter)
 * - gradients (gradient field visibility)
 *
 * URL Format Examples:
 * - /editor?layer=4&focal=node-123&loss=0.5&gradients=true
 * - /zero-seed?layer=1&focal=axiom-1
 * - /chat?session=abc123&layer=4
 *
 * This hook preserves existing query params (like session IDs) while
 * managing telescope-specific params.
 */

import { useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTelescope } from './useTelescopeState';

/**
 * Debounce delay for URL updates (ms).
 * Prevents excessive history entries during continuous telescope navigation.
 */
const URL_UPDATE_DEBOUNCE = 300;

/**
 * Parse layer number from URL, with validation.
 */
function parseLayer(value: string | null): number | null {
  if (!value) return null;
  const layer = parseInt(value, 10);
  if (isNaN(layer) || layer < 1 || layer > 7) return null;
  return layer;
}

/**
 * Parse loss threshold from URL, with validation.
 */
function parseLoss(value: string | null): number | null {
  if (!value) return null;
  const loss = parseFloat(value);
  if (isNaN(loss) || loss < 0 || loss > 1) return null;
  return loss;
}

/**
 * Parse gradients toggle from URL.
 */
function parseGradients(value: string | null): boolean | null {
  if (!value) return null;
  return value === 'true';
}

/**
 * Hook for bidirectional URL ↔ telescope state synchronization.
 *
 * Usage:
 * ```tsx
 * function TelescopeShellInner() {
 *   useTelescopeUrlSync(); // Just call it—handles everything
 *   const { state } = useTelescope();
 *   // ...
 * }
 * ```
 */
export function useTelescopeUrlSync() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { state, dispatch } = useTelescope();
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isInitialMount = useRef(true);

  // ============================================================================
  // URL → State (on mount only)
  // ============================================================================

  useEffect(() => {
    if (!isInitialMount.current) return;
    isInitialMount.current = false;

    const layer = parseLayer(searchParams.get('layer'));
    const focal = searchParams.get('focal');
    const loss = parseLoss(searchParams.get('loss'));
    const gradients = parseGradients(searchParams.get('gradients'));

    // Apply URL params to state (if valid)
    if (layer !== null) {
      dispatch({ type: 'JUMP_TO_LAYER', layer });
    }

    if (focal) {
      dispatch({ type: 'SET_FOCAL_POINT', nodeId: focal, layer: layer ?? 4 });
    }

    if (loss !== null) {
      dispatch({ type: 'SET_LOSS_THRESHOLD', threshold: loss });
    }

    if (gradients !== null && gradients !== state.showGradients) {
      dispatch({ type: 'TOGGLE_GRADIENTS' });
    }
  }, []); // Only on mount
  // eslint-disable-next-line react-hooks/exhaustive-deps

  // ============================================================================
  // State → URL (debounced)
  // ============================================================================

  useEffect(() => {
    // Skip initial mount (already handled above)
    if (isInitialMount.current) return;

    // Clear existing timeout
    if (updateTimeoutRef.current) {
      clearTimeout(updateTimeoutRef.current);
    }

    // Debounce URL updates
    updateTimeoutRef.current = setTimeout(() => {
      const params = new URLSearchParams(searchParams);

      // Determine current layer from visible layers
      // Use the first visible layer as the canonical layer
      const currentLayer = state.visibleLayers[0] ?? 4;
      params.set('layer', currentLayer.toString());

      // Focal point (optional)
      if (state.focalPoint) {
        params.set('focal', state.focalPoint);
      } else {
        params.delete('focal');
      }

      // Loss threshold (only if not default 1.0)
      if (state.lossThreshold < 1.0) {
        params.set('loss', state.lossThreshold.toFixed(2));
      } else {
        params.delete('loss');
      }

      // Gradients (only if disabled, since enabled is default)
      if (!state.showGradients) {
        params.set('gradients', 'false');
      } else {
        params.delete('gradients');
      }

      // Update URL with replace (don't create history entries)
      setSearchParams(params, { replace: true });
    }, URL_UPDATE_DEBOUNCE);

    // Cleanup
    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, [
    state.visibleLayers,
    state.focalPoint,
    state.lossThreshold,
    state.showGradients,
    searchParams,
    setSearchParams,
  ]);
}
