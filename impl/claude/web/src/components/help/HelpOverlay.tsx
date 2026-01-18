/**
 * HelpOverlay — Keyboard shortcut reference
 *
 * SEVERE STARK: Dense, no animation, instant dismiss.
 * Shows when user presses '?'
 */

import { useEffect, useCallback } from 'react';
import './HelpOverlay.css';

interface HelpOverlayProps {
  onClose: () => void;
}

interface ShortcutEntry {
  key: string;
  description: string;
}

const SHORTCUTS: ShortcutEntry[] = [
  { key: 'm', description: 'manifest — show K-Block structure' },
  { key: 'w', description: 'witness — show witness trail' },
  { key: 't', description: 'tithe — tend current item' },
  { key: 'f', description: 'refine — enter edit mode' },
  { key: 'd', description: 'define — create new K-Block' },
  { key: 's', description: 'sip — quick peek / preview' },
  { key: '?', description: 'help — show this overlay' },
  { key: 'Esc', description: 'escape — cancel / exit mode' },
];

export function HelpOverlay({ onClose }: HelpOverlayProps) {
  // Close on click outside or Escape
  const handleBackdropClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    },
    [onClose]
  );

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div className="help-overlay" onClick={handleBackdropClick}>
      <div className="help-panel">
        <header className="help-header">
          <h2>Keyboard Shortcuts</h2>
          <button className="help-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        <div className="help-content">
          <table className="help-table">
            <tbody>
              {SHORTCUTS.map(({ key, description }) => (
                <tr key={key}>
                  <td className="help-key">
                    <kbd>{key}</kbd>
                  </td>
                  <td className="help-description">{description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <footer className="help-footer">Press any key to dismiss</footer>
      </div>
    </div>
  );
}

export default HelpOverlay;
