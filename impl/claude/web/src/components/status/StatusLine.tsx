/**
 * StatusLine — Dense footer status bar
 *
 * Grounded in: spec/ui/severe-stark.md
 * "Every pixel used. Information density over whitespace."
 *
 * Shows:
 * - Current path/context
 * - Garden health
 * - Collapse status
 * - Connection status
 * - Keyboard hints
 */

import type { GardenState, CollapseState } from '../../types';
import { SLOP_COLORS } from '../../types';

interface StatusLineProps {
  /** Current AGENTESE path */
  currentPath?: string;

  /** Garden state (optional) */
  gardenState?: GardenState;

  /** Collapse state (optional) */
  collapseState?: CollapseState;

  /** Connection status */
  connectionStatus?: 'connected' | 'connecting' | 'disconnected';

  /** Current mode (Kent's Decision #6) */
  mode?: 'navigate' | 'edit' | 'witness' | 'command';

  /** Show keyboard hints */
  showHints?: boolean;
}

/**
 * Dense status line footer.
 */
export function StatusLine({
  currentPath = 'workspace',
  gardenState,
  collapseState,
  connectionStatus = 'connected',
  mode = 'navigate',
  showHints = true,
}: StatusLineProps) {
  return (
    <footer className="status-line">
      {/* Left: Path and mode */}
      <div className="status-line__left">
        <span className="status-line__path">{currentPath}</span>
        <span className="status-line__divider">|</span>
        <ModeIndicator mode={mode} />
      </div>

      {/* Center: Garden and collapse */}
      <div className="status-line__center">
        {gardenState && <GardenStatus state={gardenState} />}
        {collapseState && (
          <>
            <span className="status-line__divider">|</span>
            <CollapseStatus state={collapseState} />
          </>
        )}
      </div>

      {/* Right: Connection and hints */}
      <div className="status-line__right">
        <ConnectionIndicator status={connectionStatus} />
        {showHints && (
          <>
            <span className="status-line__divider">|</span>
            <KeyboardHints mode={mode} />
          </>
        )}
      </div>
    </footer>
  );
}

/**
 * Mode indicator (navigate/edit/witness/command).
 */
function ModeIndicator({ mode }: { mode: string }) {
  const modeColors: Record<string, string> = {
    navigate: 'var(--fg-secondary)',
    edit: 'var(--glow-earned)',
    witness: 'var(--glow-potential)',
    command: 'var(--collapse-pass)',
  };

  return (
    <span className="status-line__mode" style={{ color: modeColors[mode] }}>
      [{mode.toUpperCase()}]
    </span>
  );
}

/**
 * Garden health status.
 */
function GardenStatus({ state }: { state: GardenState }) {
  const healthPercent = Math.round(state.health * 100);
  const color =
    state.health >= 0.8
      ? 'var(--collapse-pass)'
      : state.health >= 0.5
        ? 'var(--collapse-partial)'
        : 'var(--collapse-fail)';

  return (
    <span className="status-line__garden" style={{ color }}>
      garden:{healthPercent}%
      {state.attention.length > 0 && (
        <span className="status-line__attention">({state.attention.length}!)</span>
      )}
    </span>
  );
}

/**
 * Collapse status.
 */
function CollapseStatus({ state }: { state: CollapseState }) {
  const color = SLOP_COLORS[state.overallSlop];

  return (
    <span className="status-line__collapse" style={{ color }}>
      slop:{state.overallSlop}
    </span>
  );
}

/**
 * Connection indicator.
 */
function ConnectionIndicator({ status }: { status: string }) {
  const statusConfig: Record<string, { icon: string; color: string }> = {
    connected: { icon: '●', color: 'var(--collapse-pass)' },
    connecting: { icon: '◐', color: 'var(--collapse-partial)' },
    disconnected: { icon: '○', color: 'var(--collapse-fail)' },
  };

  const config = statusConfig[status] || statusConfig.disconnected;

  return (
    <span
      className="status-line__connection"
      style={{ color: config.color }}
      title={`Connection: ${status}`}
    >
      {config.icon}
    </span>
  );
}

/**
 * Keyboard hints for current mode (Kent's Decision #6).
 */
function KeyboardHints({ mode }: { mode: string }) {
  const hints: Record<string, string> = {
    navigate: 'm:manifest w:witness f:refine d:define ?:help',
    edit: 't:tithe s:sip esc:exit',
    witness: 't:tithe esc:exit',
    command: 'enter:exec esc:cancel tab:complete',
  };

  return (
    <span className="status-line__hints text-xs text-muted">{hints[mode] || hints.navigate}</span>
  );
}

export default StatusLine;
