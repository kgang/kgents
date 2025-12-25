/**
 * TelescopeShell — Unified navigation shell for the entire application
 *
 * "The file is a lie. There is only the graph."
 *
 * Wraps AppShell with telescope context, providing:
 * - Focal distance ruler (vertical navigation)
 * - Loss threshold slider (filtering control)
 * - Telescope state context for all children
 *
 * This is the first step toward the radical redesign where page-based
 * routing is replaced by continuous focal distance navigation.
 */

import { ReactNode, useCallback, useState } from 'react';
import { TelescopeProvider, useTelescope } from '../../hooks/useTelescopeState';
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

// =============================================================================
// Internal Components
// =============================================================================

/**
 * Loss threshold slider (compact, in header area).
 */
function LossThresholdSlider({
  value,
  onChange,
}: {
  value: number;
  onChange: (value: number) => void;
}) {
  const [isDragging, setIsDragging] = useState(false);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange(parseFloat(e.target.value));
    },
    [onChange]
  );

  return (
    <div
      className={`loss-threshold-slider ${isDragging ? 'loss-threshold-slider--dragging' : ''}`}
    >
      <label
        htmlFor="loss-threshold"
        className="loss-threshold-slider__label"
        title="Filter nodes by loss value (0 = axioms only, 1 = show all)"
      >
        Loss ≤
      </label>
      <input
        id="loss-threshold"
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={value}
        onChange={handleChange}
        onMouseDown={() => setIsDragging(true)}
        onMouseUp={() => setIsDragging(false)}
        onTouchStart={() => setIsDragging(true)}
        onTouchEnd={() => setIsDragging(false)}
        className="loss-threshold-slider__input"
        aria-label={`Loss threshold: ${(value * 100).toFixed(0)}%`}
      />
      <span className="loss-threshold-slider__value">
        {(value * 100).toFixed(0)}%
      </span>
    </div>
  );
}

/**
 * Gradient toggle button (compact control).
 */
function GradientToggle({
  enabled,
  onToggle,
}: {
  enabled: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      className={`gradient-toggle ${enabled ? 'gradient-toggle--active' : ''}`}
      onClick={onToggle}
      title={`${enabled ? 'Hide' : 'Show'} gradient field`}
      aria-label={`${enabled ? 'Hide' : 'Show'} gradient field`}
      aria-pressed={enabled}
    >
      <span className="gradient-toggle__icon">∇</span>
    </button>
  );
}

/**
 * Inner shell that uses telescope context.
 */
function TelescopeShellInner({ children }: { children: ReactNode }) {
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
      {/* Focal distance ruler - left side */}
      <FocalDistanceRuler
        visibleLayers={state.visibleLayers}
        onLayerClick={handleLayerClick}
      />

      {/* Controls overlay - top right */}
      <div className="telescope-shell__controls">
        <LossThresholdSlider
          value={state.lossThreshold}
          onChange={handleLossThresholdChange}
        />
        <GradientToggle
          enabled={state.showGradients}
          onToggle={handleGradientToggle}
        />
      </div>

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
