/**
 * CoherenceBadge — Displays project-wide coherence metrics
 *
 * Shows grounded/provisional/orphan counts and average Galois loss.
 * Integrates with the derivationStore for real-time coherence tracking.
 *
 * @see spec/protocols/hypergraph-editor.md
 * @see docs/skills/hypergraph-editor.md
 */

import { memo, useMemo } from 'react';

import type { CoherenceSummary } from '../stores/derivationStore';
import { getCoherenceColor, formatGaloisLoss, getGroundingIcon } from '../stores/derivationStore';
import { lossToColor } from '../hooks/useLoss';

import './CoherenceBadge.css';

// =============================================================================
// Status Helpers
// =============================================================================

/**
 * Get status indicator based on loss value
 * - Stable (loss < 0.3): Green dot
 * - Transitional (0.3-0.7): Yellow dot
 * - Unstable (loss > 0.7): Red dot
 * - Axiomatic (loss < 0.01): Purple star
 */
function getLossStatus(loss: number): { icon: string; color: string; label: string } {
  if (loss < 0.01) return { icon: '\u2605', color: '#9b59b6', label: 'Axiomatic' }; // Purple star
  if (loss < 0.3) return { icon: '\u25CF', color: '#22c55e', label: 'Stable' }; // Green dot
  if (loss <= 0.7) return { icon: '\u25CF', color: '#f1c40f', label: 'Transitional' }; // Yellow dot
  return { icon: '\u25CF', color: '#ef4444', label: 'Unstable' }; // Red dot
}

// =============================================================================
// Types
// =============================================================================

interface CoherenceBadgeProps {
  /** Coherence summary from derivationStore */
  summary: CoherenceSummary | null;

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';

  /** Whether to show expanded view with all metrics */
  expanded?: boolean;

  /** Click handler to toggle expanded view or open coherence panel */
  onClick?: () => void;

  /** Whether badge is in loading state */
  loading?: boolean;

  /** Whether to show the Galois loss metric */
  showGaloisLoss?: boolean;

  /** Whether to show individual counts */
  showCounts?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export const CoherenceBadge = memo(function CoherenceBadge({
  summary,
  size = 'md',
  expanded = false,
  onClick,
  loading = false,
  showGaloisLoss = true,
  showCounts = true,
}: CoherenceBadgeProps) {
  // Extract summary values with safe defaults for hooks (hooks must be called unconditionally)
  const averageGaloisLoss = summary?.averageGaloisLoss ?? 0;
  const coherencePercent = summary?.coherencePercent ?? 0;
  const grounded = summary?.grounded ?? 0;
  const provisional = summary?.provisional ?? 0;
  const orphan = summary?.orphan ?? 0;
  const totalKBlocks = summary?.totalKBlocks ?? 0;

  // Hooks must be called unconditionally before any returns
  const coherenceColorClass = getCoherenceColor(coherencePercent);
  const galoisColor = useMemo(() => lossToColor(averageGaloisLoss), [averageGaloisLoss]);
  const lossStatus = useMemo(() => getLossStatus(averageGaloisLoss), [averageGaloisLoss]);

  // No summary - show placeholder
  if (!summary && !loading) {
    return (
      <div
        className={`coherence-badge coherence-badge--${size} coherence-badge--empty`}
        onClick={onClick}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
        title="No coherence data. Run project realization to compute."
      >
        <span className="coherence-badge__icon">--</span>
        <span className="coherence-badge__label">Coherence</span>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className={`coherence-badge coherence-badge--${size} coherence-badge--loading`}>
        <span className="coherence-badge__spinner" />
        <span className="coherence-badge__label">Computing...</span>
      </div>
    );
  }

  // Compact view: just the percentage and a status indicator
  if (!expanded) {
    return (
      <div
        className={`coherence-badge coherence-badge--${size} ${coherenceColorClass}`}
        onClick={onClick}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
        onKeyDown={(e) => {
          if (onClick && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            onClick();
          }
        }}
        title={`Coherence: ${coherencePercent.toFixed(0)}% (${grounded}/${totalKBlocks} grounded)\nGalois Loss: ${formatGaloisLoss(averageGaloisLoss)}\nStatus: ${lossStatus.label}`}
      >
        <span className="coherence-badge__percent">{coherencePercent.toFixed(0)}%</span>
        {showGaloisLoss && (
          <span
            className="coherence-badge__loss"
            style={{ color: galoisColor, borderColor: galoisColor }}
          >
            <span className="coherence-badge__loss-status" style={{ color: lossStatus.color }}>
              {lossStatus.icon}
            </span>
            {formatGaloisLoss(averageGaloisLoss)}
          </span>
        )}
      </div>
    );
  }

  // Expanded view: show all metrics
  return (
    <div
      className={`coherence-badge coherence-badge--${size} coherence-badge--expanded`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
    >
      {/* Main percentage */}
      <div className={`coherence-badge__main ${coherenceColorClass}`}>
        <span className="coherence-badge__value">{coherencePercent.toFixed(0)}%</span>
        <span className="coherence-badge__label">Coherence</span>
      </div>

      {/* Counts breakdown */}
      {showCounts && (
        <div className="coherence-badge__counts">
          <div className="coherence-badge__count coherence-badge__count--grounded" title="Grounded">
            <span className="coherence-badge__count-icon">{getGroundingIcon('grounded')}</span>
            <span className="coherence-badge__count-value">{grounded}</span>
          </div>
          <div
            className="coherence-badge__count coherence-badge__count--provisional"
            title="Provisional"
          >
            <span className="coherence-badge__count-icon">{getGroundingIcon('provisional')}</span>
            <span className="coherence-badge__count-value">{provisional}</span>
          </div>
          <div className="coherence-badge__count coherence-badge__count--orphan" title="Orphan">
            <span className="coherence-badge__count-icon">{getGroundingIcon('orphan')}</span>
            <span className="coherence-badge__count-value">{orphan}</span>
          </div>
        </div>
      )}

      {/* Galois loss with gradient coloring */}
      {showGaloisLoss && (
        <div
          className="coherence-badge__galois"
          style={
            {
              '--galois-color': galoisColor,
              '--status-color': lossStatus.color,
            } as React.CSSProperties
          }
        >
          <span className="coherence-badge__galois-label">Galois Loss:</span>
          <span className="coherence-badge__galois-status" style={{ color: lossStatus.color }}>
            {lossStatus.icon}
          </span>
          <span className="coherence-badge__galois-value" style={{ color: galoisColor }}>
            {formatGaloisLoss(averageGaloisLoss)}
          </span>
          <span
            className="coherence-badge__galois-status-label"
            style={{ color: lossStatus.color }}
          >
            ({lossStatus.label})
          </span>
        </div>
      )}

      {/* Total count */}
      <div className="coherence-badge__total">
        <span className="coherence-badge__total-value">{totalKBlocks}</span>
        <span className="coherence-badge__total-label">K-Blocks</span>
      </div>
    </div>
  );
});

export default CoherenceBadge;
