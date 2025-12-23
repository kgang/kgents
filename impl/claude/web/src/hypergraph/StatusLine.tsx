/**
 * StatusLine — Mode indicator and status display
 *
 * Shows: [Mode] | Cursor position | Trail breadcrumb | K-Block status
 *
 * "The file is a lie. There is only the graph."
 */

import React, { memo } from 'react';

import type { EditorMode, Position } from './types';

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
}

// =============================================================================
// Mode Badge Colors
// =============================================================================

const MODE_COLORS: Record<EditorMode, string> = {
  NORMAL: 'var(--status-normal, #4a9eff)',
  INSERT: 'var(--status-insert, #4caf50)',
  EDGE: 'var(--status-edge, #ff9800)',
  VISUAL: 'var(--status-visual, #9c27b0)',
  COMMAND: 'var(--status-command, #795548)',
  WITNESS: 'var(--status-witness, #e91e63)',
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
// Component
// =============================================================================

export const StatusLine = memo(function StatusLine({
  mode,
  cursor,
  breadcrumb,
  pendingSequence,
  kblockStatus,
  nodePath,
}: StatusLineProps) {
  const modeColor = MODE_COLORS[mode];
  const modeLabel = MODE_LABELS[mode];

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

      {/* Breadcrumb trail */}
      <div className="status-line__breadcrumb" title={breadcrumb}>
        {breadcrumb}
      </div>

      {/* Spacer */}
      <div className="status-line__spacer" />

      {/* Node path */}
      {nodePath && <div className="status-line__path">{nodePath}</div>}

      {/* Cursor position */}
      <div className="status-line__cursor">
        {cursor.line + 1},{cursor.column + 1}
      </div>
    </div>
  );
});
