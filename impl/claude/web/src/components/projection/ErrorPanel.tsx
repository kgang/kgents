/**
 * ErrorPanel: Technical error display with retry affordance.
 *
 * Renders technical errors with category-specific icons,
 * error details, and optional retry button.
 */

import type { ErrorInfo } from '../../reactive/schema';
import { getErrorEmoji, isErrorRetryable } from '../../reactive/schema';
import { STATE_COLORS, SEMANTIC_COLORS } from '../../constants';

interface ErrorPanelProps {
  error: ErrorInfo;
  onRetry?: () => void;
  showRetry?: boolean;
}

/**
 * Color mapping for error categories.
 * Uses semantic colors from design system where appropriate.
 */
const CATEGORY_COLORS: Record<string, { border: string; bg: string; text: string }> = {
  network: { border: STATE_COLORS.warning, bg: '#fffbeb', text: '#92400e' },
  notFound: { border: '#3b82f6', bg: '#eff6ff', text: '#1e40af' },
  permission: { border: STATE_COLORS.error, bg: '#fef2f2', text: '#991b1b' },
  timeout: { border: STATE_COLORS.warning, bg: '#fffbeb', text: '#92400e' },
  validation: { border: SEMANTIC_COLORS.collaboration, bg: '#faf5ff', text: '#6b21a8' },
  unknown: { border: STATE_COLORS.error, bg: '#fef2f2', text: '#991b1b' },
};

export function ErrorPanel({ error, onRetry, showRetry = true }: ErrorPanelProps) {
  const emoji = getErrorEmoji(error.category);
  const colors = CATEGORY_COLORS[error.category] || CATEGORY_COLORS.unknown;
  const canRetry = showRetry && isErrorRetryable(error);

  return (
    <div
      className="kgents-error-panel"
      style={{
        borderLeft: `4px solid ${colors.border}`,
        backgroundColor: colors.bg,
        padding: '16px',
        borderRadius: '4px',
        margin: '8px 0',
      }}
      role="alert"
      aria-live="assertive"
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '8px',
        }}
      >
        <span style={{ fontSize: '24px' }} role="img" aria-label={error.category}>
          {emoji}
        </span>
        <span style={{ fontWeight: 600, color: colors.text }}>
          {error.message}
        </span>
      </div>

      {/* Details */}
      <p style={{ color: colors.text, fontSize: '14px', margin: '4px 0' }}>
        Code: <code>{error.code}</code>
      </p>

      {error.traceId && (
        <p style={{ color: colors.text, fontSize: '12px', opacity: 0.7, margin: '4px 0' }}>
          Trace: {error.traceId}
        </p>
      )}

      {/* Retry button */}
      {canRetry && onRetry && (
        <div style={{ marginTop: '12px' }}>
          {error.retryAfterSeconds ? (
            <p style={{ fontSize: '14px', color: colors.text, marginBottom: '8px' }}>
              Retry in {error.retryAfterSeconds}s...
            </p>
          ) : null}
          <button
            onClick={onRetry}
            style={{
              padding: '8px 16px',
              backgroundColor: colors.border,
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 500,
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Fallback suggestion */}
      {error.fallbackAction && (
        <p
          style={{
            marginTop: '12px',
            fontSize: '14px',
            fontStyle: 'italic',
            color: colors.text,
          }}
        >
          ◎ {error.fallbackAction}
        </p>
      )}
    </div>
  );
}

export default ErrorPanel;
