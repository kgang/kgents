/**
 * ConfirmWidget: Binary confirmation component.
 *
 * Features:
 * - Confirm/Cancel buttons
 * - Destructive action styling
 * - Keyboard support (Enter to confirm, Escape to cancel)
 */

import React, { useEffect, useCallback } from 'react';

export interface ConfirmWidgetProps {
  /** Confirmation message */
  message: string;
  /** Confirm button label */
  confirmLabel?: string;
  /** Cancel button label */
  cancelLabel?: string;
  /** Is this a destructive action */
  destructive?: boolean;
  /** Confirm callback */
  onConfirm?: () => void;
  /** Cancel callback */
  onCancel?: () => void;
  /** Show as inline or modal */
  variant?: 'inline' | 'modal';
}

export function ConfirmWidget({
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  destructive = false,
  onConfirm,
  onCancel,
  variant = 'inline',
}: ConfirmWidgetProps) {
  // Keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        onConfirm?.();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onCancel?.();
      }
    },
    [onConfirm, onCancel]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const confirmButtonStyles: React.CSSProperties = {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '6px',
    fontWeight: 500,
    cursor: 'pointer',
    backgroundColor: destructive ? '#ef4444' : '#3b82f6',
    color: 'white',
  };

  const cancelButtonStyles: React.CSSProperties = {
    padding: '8px 16px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontWeight: 500,
    cursor: 'pointer',
    backgroundColor: 'white',
    color: '#4b5563',
  };

  const content = (
    <div
      className="kgents-confirm-widget"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        padding: variant === 'modal' ? '24px' : '16px',
        backgroundColor: 'white',
        borderRadius: '8px',
        border: variant === 'inline' ? '1px solid #e5e7eb' : 'none',
        boxShadow: variant === 'modal' ? '0 10px 25px rgba(0, 0, 0, 0.1)' : 'none',
      }}
      role="alertdialog"
      aria-describedby="confirm-message"
    >
      {/* Icon for destructive actions */}
      {destructive && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              backgroundColor: '#fef2f2',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
            }}
          >
            ◇
          </div>
        </div>
      )}

      {/* Message */}
      <p
        id="confirm-message"
        style={{
          margin: 0,
          textAlign: 'center',
          fontSize: '15px',
          color: '#1f2937',
        }}
      >
        {message}
      </p>

      {/* Buttons */}
      <div
        style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'center',
        }}
      >
        <button onClick={onCancel} style={cancelButtonStyles} type="button">
          {cancelLabel}
        </button>
        <button onClick={onConfirm} style={confirmButtonStyles} type="button" autoFocus>
          {confirmLabel}
        </button>
      </div>

      {/* Keyboard hints */}
      <p
        style={{
          margin: 0,
          textAlign: 'center',
          fontSize: '11px',
          color: '#9ca3af',
        }}
      >
        Press Enter to confirm, Escape to cancel
      </p>
    </div>
  );

  if (variant === 'modal') {
    return (
      <div
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
        }}
        onClick={(e) => {
          if (e.target === e.currentTarget) onCancel?.();
        }}
      >
        {content}
      </div>
    );
  }

  return content;
}

export default ConfirmWidget;
