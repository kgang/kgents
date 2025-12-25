/**
 * TelescopeShell — Unified navigation shell for the entire application
 *
 * "The file is a lie. There is only the graph."
 *
 * Wraps AppShell with telescope context, providing:
 * - Focal distance ruler (vertical navigation with integrated controls)
 * - Telescope state context for all children
 *
 * This is the first step toward the radical redesign where page-based
 * routing is replaced by continuous focal distance navigation.
 */

import { ReactNode, useCallback } from 'react';
import { TelescopeProvider, useTelescope } from '../../hooks/useTelescopeState';
import { useTelescopeUrlSync } from '../../hooks/useTelescopeUrlSync';
import { AppShell } from './AppShell';
import { FocalDistanceRuler } from './FocalDistanceRuler';
import { DerivationTrail } from './DerivationTrail';
import './TelescopeShell.css';

// =============================================================================
// Types
// =============================================================================

interface TelescopeShellProps {
  children: ReactNode;
}

/**
 * Inner shell that uses telescope context.
 */
function TelescopeShellInner({ children }: { children: ReactNode }) {
  // Sync telescope state with URL query params (bidirectional)
  useTelescopeUrlSync();

  const { state, dispatch } = useTelescope();

  const handleLayerClick = useCallback(
    (layer: number) => {
      dispatch({ type: 'JUMP_TO_LAYER', layer });
    },
    [dispatch]
  );

  const handleLossThresholdChange = useCallback(
    (threshold: number) => {
      dispatch({ type: 'SET_LOSS_THRESHOLD', threshold });
    },
    [dispatch]
  );

  const handleGradientToggle = useCallback(() => {
    dispatch({ type: 'TOGGLE_GRADIENTS' });
  }, [dispatch]);

  return (
    <div className="telescope-shell">
      {/* Focal distance ruler - left side with integrated controls */}
      <FocalDistanceRuler
        visibleLayers={state.visibleLayers}
        onLayerClick={handleLayerClick}
        lossThreshold={state.lossThreshold}
        onLossThresholdChange={handleLossThresholdChange}
        showGradients={state.showGradients}
        onGradientsToggle={handleGradientToggle}
      />

      {/* Derivation trail - bottom breadcrumb */}
      <DerivationTrail />

      {/* Main content (wrapped in AppShell) */}
      <div className="telescope-shell__content">
        <AppShell>{children}</AppShell>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * TelescopeShell — Wrap your application to enable telescope navigation.
 *
 * @example
 * ```tsx
 * <TelescopeShell>
 *   <Routes>
 *     <Route path="/editor" element={<HypergraphEditorPage />} />
 *     <Route path="/director" element={<DirectorPage />} />
 *   </Routes>
 * </TelescopeShell>
 * ```
 */
export function TelescopeShell({ children }: TelescopeShellProps) {
  return (
    <TelescopeProvider>
      <TelescopeShellInner>{children}</TelescopeShellInner>
    </TelescopeProvider>
  );
}
