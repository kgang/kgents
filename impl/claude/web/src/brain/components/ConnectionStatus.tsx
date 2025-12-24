/**
 * ConnectionStatus — Real-time connection indicator for Brain stream
 *
 * Shows live/disconnected status with reconnection controls.
 */

import './ConnectionStatus.css';

// =============================================================================
// Types
// =============================================================================

export interface ConnectionStatusProps {
  /** Whether connected to SSE stream */
  connected: boolean;

  /** Whether currently attempting to reconnect */
  reconnecting?: boolean;

  /** Number of reconnection attempts */
  reconnectAttempts?: number;

  /** Last error message */
  error?: string | null;

  /** Callback to manually reconnect */
  onReconnect?: () => void;

  /** Variant: 'inline' for header, 'footer' for bottom bar */
  variant?: 'inline' | 'footer';
}

// =============================================================================
// Component
// =============================================================================

export function ConnectionStatus({
  connected,
  reconnecting = false,
  reconnectAttempts = 0,
  error,
  onReconnect,
  variant = 'inline',
}: ConnectionStatusProps) {
  // Determine status
  let status: 'connected' | 'reconnecting' | 'disconnected' | 'error';
  let label: string;
  let ariaLabel: string;

  if (connected) {
    status = 'connected';
    label = 'Live';
    ariaLabel = 'Connected to live stream';
  } else if (reconnecting) {
    status = 'reconnecting';
    label = `Reconnecting${reconnectAttempts > 0 ? ` (${reconnectAttempts})` : '...'}`;
    ariaLabel = `Reconnecting, attempt ${reconnectAttempts}`;
  } else if (error) {
    status = 'error';
    label = 'Error';
    ariaLabel = `Connection error: ${error}`;
  } else {
    status = 'disconnected';
    label = 'Disconnected';
    ariaLabel = 'Disconnected from live stream';
  }

  const showReconnect = !connected && !reconnecting && onReconnect;

  if (variant === 'footer') {
    return (
      <footer className="connection-status connection-status--footer" role="status" aria-label={ariaLabel}>
        <div className="connection-status__content">
          <span className="connection-status__indicator" data-status={status} />
          <span className="connection-status__label">{label}</span>
          {error && <span className="connection-status__error" title={error}>{error}</span>}
          {showReconnect && (
            <button
              type="button"
              className="connection-status__reconnect"
              onClick={onReconnect}
              aria-label="Reconnect to stream"
            >
              Reconnect
            </button>
          )}
        </div>
      </footer>
    );
  }

  // Inline variant
  return (
    <div className="connection-status connection-status--inline" role="status" aria-label={ariaLabel}>
      <span className="connection-status__indicator" data-status={status} />
      <span className="connection-status__label">{label}</span>
      {showReconnect && (
        <button
          type="button"
          className="connection-status__reconnect connection-status__reconnect--small"
          onClick={onReconnect}
          aria-label="Reconnect"
        >
          ↻
        </button>
      )}
    </div>
  );
}

// =============================================================================
// Minimal dot-only variant
// =============================================================================

export interface ConnectionDotProps {
  connected: boolean;
  title?: string;
}

export function ConnectionDot({ connected, title }: ConnectionDotProps) {
  return (
    <span
      className="connection-status__indicator connection-status__indicator--standalone"
      data-status={connected ? 'connected' : 'disconnected'}
      title={title ?? (connected ? 'Connected' : 'Disconnected')}
      role="status"
      aria-label={connected ? 'Connected' : 'Disconnected'}
    />
  );
}

// =============================================================================
// Export
// =============================================================================

export default ConnectionStatus;
