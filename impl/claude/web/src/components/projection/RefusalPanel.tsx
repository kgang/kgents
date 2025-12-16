/**
 * RefusalPanel: Semantic refusal display.
 *
 * Renders agent refusals distinctly from errors.
 * Uses purple/magenta styling to differentiate.
 */

import type { RefusalInfo } from '../../reactive/schema';

interface RefusalPanelProps {
  refusal: RefusalInfo;
  onAppeal?: () => void;
  onOverride?: () => void;
  showAppeal?: boolean;
  showOverride?: boolean;
}

export function RefusalPanel({
  refusal,
  onAppeal,
  onOverride,
  showAppeal = true,
  showOverride = true,
}: RefusalPanelProps) {
  return (
    <div
      className="kgents-refusal-panel"
      style={{
        borderLeft: '4px solid #a855f7',
        backgroundColor: '#faf5ff',
        padding: '16px',
        borderRadius: '4px',
        margin: '8px 0',
      }}
      role="alert"
      aria-live="polite"
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
        <span style={{ fontSize: '24px' }} role="img" aria-label="Refused">
          🛑
        </span>
        <span style={{ fontWeight: 600, color: '#6b21a8' }}>
          Action Refused
        </span>
      </div>

      {/* Reason */}
      <p style={{ color: '#581c87', margin: '8px 0' }}>
        {refusal.reason}
      </p>

      {/* Consent required */}
      {refusal.consentRequired && (
        <p style={{ color: '#6b21a8', fontSize: '14px', margin: '8px 0' }}>
          <strong>Requires:</strong> {refusal.consentRequired}
        </p>
      )}

      {/* Appeal path */}
      {showAppeal && refusal.appealTo && (
        <p style={{ color: '#6b21a8', fontSize: '14px', margin: '8px 0' }}>
          <strong>Appeal path:</strong>{' '}
          <code
            style={{
              backgroundColor: '#f3e8ff',
              padding: '2px 6px',
              borderRadius: '3px',
            }}
          >
            {refusal.appealTo}
          </code>
          {onAppeal && (
            <button
              onClick={onAppeal}
              style={{
                marginLeft: '8px',
                padding: '4px 12px',
                backgroundColor: '#7c3aed',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              Appeal
            </button>
          )}
        </p>
      )}

      {/* Override option */}
      {showOverride && refusal.overrideCost !== null && (
        <p style={{ color: '#6b21a8', fontSize: '14px', margin: '12px 0 0 0' }}>
          <strong>Override cost:</strong> {refusal.overrideCost} tokens
          {onOverride && (
            <button
              onClick={onOverride}
              style={{
                marginLeft: '8px',
                padding: '4px 12px',
                backgroundColor: '#9333ea',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              Override
            </button>
          )}
        </p>
      )}
    </div>
  );
}

export default RefusalPanel;
