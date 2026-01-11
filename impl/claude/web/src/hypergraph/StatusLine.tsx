/**
 * StatusLine — Mode indicator and status display
 *
 * Shows: [Mode] | Cursor position | Trail breadcrumb | K-Block status
 *
 * "The file is a lie. There is only the graph."
 */

import React, { memo } from 'react';

import type { EditorMode, Position } from './state/types';
import type { DocumentStatus } from '../api/director';
import type { CoherenceSummary } from '../stores/derivationStore';
import { formatGaloisLoss, getGroundingIcon } from '../stores/derivationStore';
import { DocumentStatusBadge } from '../components/director';
import { NavigationConstitutionalBadge } from './NavigationConstitutionalBadge';

import './StatusLine.css';

// =============================================================================
// Types
// =============================================================================

interface StatusLineProps {
  /** Current editor mode */
  mode: EditorMode;

  /** Cursor position */
  cursor: Position;

  /** Trail breadcrumb text */
  breadcrumb: string;

  /** Pending key sequence (for multi-key bindings) */
  pendingSequence?: string;

  /** K-Block status */
  kblockStatus?: 'PRISTINE' | 'DIRTY' | 'STALE' | 'CONFLICTING' | null;

  /** Current node path */
  nodePath?: string;

  /**
   * Derivation confidence (0-1 scale)
   *
   * When present, displays a confidence indicator using the health color system:
   * - >= 0.8: green (healthy)
   * - >= 0.6: yellow (degraded)
   * - >= 0.4: orange (warning)
   * - < 0.4: red (critical)
   *
   * Use gD to navigate to derivation parent, gc to show breakdown.
   */
  confidence?: number;

  /** Derivation tier (for hover tooltip) */
  derivationTier?: string;

  /** Director document status (for spec files) */
  directorStatus?: DocumentStatus;

  /** Show navigation constitutional badge */
  showConstitutionalBadge?: boolean;

  /** Project-wide coherence summary from derivationStore */
  coherenceSummary?: CoherenceSummary | null;
}

// =============================================================================
// Mode Badge Colors (STARK BIOME — muted, industrial palette)
// =============================================================================

const MODE_COLORS: Record<EditorMode, string> = {
  NORMAL: 'var(--status-normal, #6b8ba3)', // Muted steel-blue
  INSERT: 'var(--status-insert, #4a6b4a)', // Life-sage
  EDGE: 'var(--status-edge, #c4a77d)', // Glow-spore
  VISUAL: 'var(--status-visual, #8b6b8b)', // Muted purple
  COMMAND: 'var(--status-command, #5a4a42)', // Soil-tone
  WITNESS: 'var(--status-witness, #a65d6a)', // Muted coral
};

const MODE_LABELS: Record<EditorMode, string> = {
  NORMAL: 'NORMAL',
  INSERT: '-- INSERT --',
  EDGE: '-- EDGE --',
  VISUAL: '-- VISUAL --',
  COMMAND: ':',
  WITNESS: '-- WITNESS --',
};

// =============================================================================
// Confidence Indicator Helpers
// =============================================================================

type ConfidenceLevel = 'healthy' | 'degraded' | 'warning' | 'critical';

/**
 * Get confidence level from 0-1 score.
 * Matches HEALTH_COLORS thresholds from constants/colors.ts
 */
function getConfidenceLevel(confidence: number): ConfidenceLevel {
  if (confidence >= 0.8) return 'healthy';
  if (confidence >= 0.6) return 'degraded';
  if (confidence >= 0.4) return 'warning';
  return 'critical';
}

/**
 * Format confidence as visual indicator with colored dot
 */
function formatConfidenceIndicator(confidence: number): { bar: string; dot: string } {
  const filled = Math.round(confidence * 8);
  const empty = 8 - filled;
  return {
    bar: '█'.repeat(filled) + '░'.repeat(empty),
    dot: '●', // Colored dot indicator
  };
}

// =============================================================================
// Component
// =============================================================================

export const StatusLine = memo(function StatusLine({
  mode,
  cursor,
  breadcrumb,
  pendingSequence,
  kblockStatus,
  nodePath,
  confidence,
  derivationTier,
  directorStatus,
  showConstitutionalBadge = true,
  coherenceSummary,
}: StatusLineProps) {
  const modeColor = MODE_COLORS[mode];
  const modeLabel = MODE_LABELS[mode];

  // Confidence indicator props
  const confidenceLevel = confidence !== undefined ? getConfidenceLevel(confidence) : null;
  const confidenceIndicator =
    confidence !== undefined ? formatConfidenceIndicator(confidence) : null;
  const confidencePercent = confidence !== undefined ? Math.round(confidence * 100) : null;

  return (
    <div className="status-line" style={{ '--mode-color': modeColor } as React.CSSProperties}>
      {/* Mode indicator */}
      <div className="status-line__mode" data-mode={mode}>
        {modeLabel}
      </div>

      {/* Pending sequence (for multi-key bindings like 'g') */}
      {pendingSequence && <div className="status-line__pending">{pendingSequence}</div>}

      {/* K-Block status */}
      {kblockStatus && (
        <div className="status-line__kblock" data-status={kblockStatus}>
          [{kblockStatus}]
        </div>
      )}

      {/* Derivation confidence indicator */}
      {confidence !== undefined && confidenceLevel && confidenceIndicator && (
        <div
          className="status-line__confidence"
          data-level={confidenceLevel}
          title={`Derivation: ${confidencePercent}%${derivationTier ? ` (${derivationTier})` : ''} — gD: parent, gc: breakdown`}
        >
          <span className="status-line__confidence-dot">{confidenceIndicator.dot}</span>
          <span className="status-line__confidence-bar">{confidenceIndicator.bar}</span>
          <span className="status-line__confidence-value">{confidencePercent}%</span>
        </div>
      )}

      {/* Breadcrumb trail */}
      <div className="status-line__breadcrumb" title={breadcrumb}>
        {breadcrumb}
      </div>

      {/* Spacer */}
      <div className="status-line__spacer" />

      {/* Mode-specific hints */}
      {mode === 'NORMAL' && (
        <div className="status-line__hints" title="Press ? for all shortcuts">
          <kbd>j</kbd>/<kbd>k</kbd> scroll · <kbd>gh</kbd>/<kbd>gl</kbd> nav · <kbd>?</kbd> help
        </div>
      )}
      {mode === 'INSERT' && (
        <div className="status-line__hints">
          <kbd>Esc</kbd> exit
        </div>
      )}
      {mode === 'EDGE' && (
        <div className="status-line__hints">
          <kbd>d/e/i/r/c/t</kbd> type · <kbd>Esc</kbd> cancel
        </div>
      )}

      {/* Director status (for spec files) */}
      {directorStatus && (
        <div className="status-line__director">
          <DocumentStatusBadge status={directorStatus} size="sm" />
        </div>
      )}

      {/* Constitutional Badge (navigation alignment) */}
      {showConstitutionalBadge && (
        <div className="status-line__constitutional">
          <NavigationConstitutionalBadge size="sm" expandable={true} />
        </div>
      )}

      {/* Project Coherence Summary (from derivationStore) */}
      {coherenceSummary && (
        <div
          className="status-line__coherence"
          title={`Project Coherence: ${coherenceSummary.coherencePercent.toFixed(0)}% | Galois Loss: ${formatGaloisLoss(coherenceSummary.averageGaloisLoss)} | ${coherenceSummary.grounded}${getGroundingIcon('grounded')} ${coherenceSummary.provisional}${getGroundingIcon('provisional')} ${coherenceSummary.orphan}${getGroundingIcon('orphan')}`}
        >
          <span className="status-line__coherence-icons">
            <span className="status-line__coherence-grounded">
              {coherenceSummary.grounded}
              {getGroundingIcon('grounded')}
            </span>
            <span className="status-line__coherence-provisional">
              {coherenceSummary.provisional}
              {getGroundingIcon('provisional')}
            </span>
            <span className="status-line__coherence-orphan">
              {coherenceSummary.orphan}
              {getGroundingIcon('orphan')}
            </span>
          </span>
        </div>
      )}

      {/* Node path */}
      {nodePath && <div className="status-line__path">{nodePath}</div>}

      {/* Cursor position */}
      <div className="status-line__cursor">
        {cursor.line + 1},{cursor.column + 1}
      </div>
    </div>
  );
});
