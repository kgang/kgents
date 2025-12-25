/**
 * HelpPanel — Keyboard shortcut reference
 *
 * "Tasteful > feature-complete. Take the modal concept, not the cruft."
 *
 * Displays all available keybindings organized by mode.
 * Triggered by '?' in NORMAL mode.
 */

import { memo, useEffect } from 'react';
import { NORMAL_MODE_BINDINGS_DOC } from './useKeyHandler';
import './HelpPanel.css';

interface HelpPanelProps {
  onClose: () => void;
}

/**
 * Group bindings by category (based on prefix/description patterns)
 */
function groupBindings() {
  const scrollNav: typeof NORMAL_MODE_BINDINGS_DOC = [];
  const graphNav: typeof NORMAL_MODE_BINDINGS_DOC = [];
  const portalOps: typeof NORMAL_MODE_BINDINGS_DOC = [];
  const modeSwitches: typeof NORMAL_MODE_BINDINGS_DOC = [];

  for (const binding of NORMAL_MODE_BINDINGS_DOC) {
    const keys = binding.keys;
    const desc = binding.description.toLowerCase();

    if (desc.includes('scroll') || keys === 'j' || keys === 'k' || keys === '{' || keys === '}') {
      scrollNav.push(binding);
    } else if (keys.startsWith('z')) {
      portalOps.push(binding);
    } else if (keys.startsWith('g') && !desc.includes('mode')) {
      graphNav.push(binding);
    } else {
      modeSwitches.push(binding);
    }
  }

  return { scrollNav, graphNav, portalOps, modeSwitches };
}

export const HelpPanel = memo(function HelpPanel({ onClose }: HelpPanelProps) {
  const { scrollNav, graphNav, portalOps, modeSwitches } = groupBindings();

  // Handle keyboard events: Escape and ? to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' || e.key === '?') {
        e.preventDefault();
        e.stopPropagation();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div className="help-panel" role="dialog" aria-label="Keyboard shortcuts">
      <div className="help-panel__backdrop" onClick={onClose} />
      <div className="help-panel__content">
        <header className="help-panel__header">
          <h2>Keyboard Shortcuts</h2>
          <button className="help-panel__close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        <div className="help-panel__body">
          {/* Scroll Navigation */}
          <section className="help-panel__section">
            <h3>Reading (Scroll)</h3>
            <table className="help-panel__table">
              <tbody>
                {scrollNav.map((b) => (
                  <tr key={b.keys}>
                    <td>
                      <kbd>{b.keys}</kbd>
                    </td>
                    <td>{b.description}</td>
                  </tr>
                ))}
                <tr>
                  <td>
                    <kbd>gg</kbd> / <kbd>G</kbd>
                  </td>
                  <td>Go to top / bottom</td>
                </tr>
              </tbody>
            </table>
          </section>

          {/* Graph Navigation */}
          <section className="help-panel__section">
            <h3>Graph Navigation</h3>
            <table className="help-panel__table">
              <tbody>
                {graphNav.map((b) => (
                  <tr key={b.keys}>
                    <td>
                      <kbd>{b.keys}</kbd>
                    </td>
                    <td>{b.description}</td>
                  </tr>
                ))}
                <tr>
                  <td>
                    <kbd>Ctrl+o</kbd>
                  </td>
                  <td>Go back in trail</td>
                </tr>
              </tbody>
            </table>
          </section>

          {/* Portal Operations */}
          <section className="help-panel__section">
            <h3>Portals (Fold)</h3>
            <table className="help-panel__table">
              <tbody>
                {portalOps.map((b) => (
                  <tr key={b.keys}>
                    <td>
                      <kbd>{b.keys}</kbd>
                    </td>
                    <td>{b.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          {/* Mode Switches */}
          <section className="help-panel__section">
            <h3>Modes</h3>
            <table className="help-panel__table">
              <tbody>
                {modeSwitches.map((b) => (
                  <tr key={b.keys}>
                    <td>
                      <kbd>{b.keys}</kbd>
                    </td>
                    <td>{b.description}</td>
                  </tr>
                ))}
                <tr>
                  <td>
                    <kbd>Esc</kbd>
                  </td>
                  <td>Return to NORMAL mode</td>
                </tr>
              </tbody>
            </table>
          </section>

          {/* Navigation */}
          <section className="help-panel__section">
            <h3>Navigation</h3>
            <table className="help-panel__table">
              <tbody>
                <tr>
                  <td>
                    <kbd>:</kbd>
                  </td>
                  <td>Enter command mode (ex commands)</td>
                </tr>
                <tr>
                  <td>
                    <em>Click nodes/edges</em>
                  </td>
                  <td>Navigate graph (no command palette—graph-first!)</td>
                </tr>
              </tbody>
            </table>
          </section>

          {/* Commands */}
          <section className="help-panel__section">
            <h3>Commands (: mode)</h3>
            <table className="help-panel__table">
              <tbody>
                <tr>
                  <td>
                    <kbd>:w</kbd>
                  </td>
                  <td>Save with witness mark</td>
                </tr>
                <tr>
                  <td>
                    <kbd>:ag &lt;path&gt;</kbd>
                  </td>
                  <td>Invoke AGENTESE endpoint</td>
                </tr>
                <tr>
                  <td>
                    <kbd>:crystallize</kbd>
                  </td>
                  <td>Crystallize current session</td>
                </tr>
                <tr>
                  <td>
                    <kbd>:checkpoint</kbd>
                  </td>
                  <td>Create K-Block checkpoint</td>
                </tr>
              </tbody>
            </table>
          </section>

          {/* Edge Mode */}
          <section className="help-panel__section">
            <h3>Edge Mode (ge)</h3>
            <table className="help-panel__table">
              <tbody>
                <tr>
                  <td>
                    <kbd>d/e/i/r/c/t/u/s/n</kbd>
                  </td>
                  <td>Select edge type</td>
                </tr>
                <tr>
                  <td>
                    <kbd>j/k</kbd>
                  </td>
                  <td>Navigate targets</td>
                </tr>
                <tr>
                  <td>
                    <kbd>Enter</kbd> / <kbd>y</kbd>
                  </td>
                  <td>Confirm</td>
                </tr>
                <tr>
                  <td>
                    <kbd>Esc</kbd> / <kbd>n</kbd>
                  </td>
                  <td>Cancel</td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>

        <footer className="help-panel__footer">
          <span className="help-panel__hint">Press <kbd>?</kbd> or <kbd>Esc</kbd> to close</span>
        </footer>
      </div>
    </div>
  );
});

export default HelpPanel;
