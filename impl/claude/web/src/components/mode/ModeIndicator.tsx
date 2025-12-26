/**
 * ModeIndicator: Visual display of current editing mode
 *
 * Bottom-left pill showing current mode with color coding.
 * Includes subtle animations on mode transitions.
 *
 * @see docs/skills/hypergraph-editor.md - Six-mode modal editing
 */

import { memo } from 'react';
import { useMode } from '@/hooks/useMode';
import './ModeIndicator.css';

// =============================================================================
// Component
// =============================================================================

export interface ModeIndicatorProps {
  /** Variant: 'pill' (default, fixed position) or 'badge' (inline, minimal) */
  variant?: 'pill' | 'badge';

  /** Show keyboard hint (default: true) */
  showHint?: boolean;

  /** Position (default: 'bottom-left') */
  position?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';

  /** Compact mode (smaller, no description) */
  compact?: boolean;
}

/**
 * Mode indicator pill or badge
 *
 * Displays current mode with color, label, and optional description.
 *
 * @example
 * ```tsx
 * // Fixed pill (default)
 * <ModeIndicator />
 *
 * // Inline badge (GitHub label style)
 * <ModeIndicator variant="badge" />
 *
 * // Compact pill version
 * <ModeIndicator compact />
 *
 * // Different position
 * <ModeIndicator position="top-right" />
 * ```
 */
export const ModeIndicator = memo(function ModeIndicator({
  variant = 'pill',
  showHint = true,
  position = 'bottom-left',
  compact = false,
}: ModeIndicatorProps) {
  const { mode, label, description, color } = useMode();

  // Badge variant: inline, minimal, label-only
  if (variant === 'badge') {
    return (
      <div
        className="mode-indicator mode-indicator--badge"
        data-mode={mode}
        style={{
          '--mode-color': color,
        } as React.CSSProperties}
      >
        <div className="mode-indicator__label">{label}</div>
      </div>
    );
  }

  // Pill variant: fixed position, full features
  return (
    <div
      className={`mode-indicator mode-indicator--pill mode-indicator--${position} ${compact ? 'mode-indicator--compact' : ''}`}
      data-mode={mode}
      style={{
        '--mode-color': color,
      } as React.CSSProperties}
    >
      {/* Mode label */}
      <div className="mode-indicator__label">{label}</div>

      {/* Description (unless compact) */}
      {!compact && <div className="mode-indicator__description">{description}</div>}

      {/* Keyboard hint (Escape to return) */}
      {showHint && mode !== 'NORMAL' && (
        <div className="mode-indicator__hint">
          <kbd>Esc</kbd> to exit
        </div>
      )}
    </div>
  );
});

export default ModeIndicator;
