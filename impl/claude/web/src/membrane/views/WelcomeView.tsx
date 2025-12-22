/**
 * WelcomeView — Initial state when no focus is set
 *
 * Shows a welcoming message and recent activity.
 * Uses BreathingContainer for vitality.
 */

import { BreathingContainer } from '../../components/genesis/BreathingContainer';

import './WelcomeView.css';

// =============================================================================
// Component
// =============================================================================

export function WelcomeView() {
  return (
    <div className="welcome-view">
      <BreathingContainer intensity="subtle" period="calm">
        <div className="welcome-view__content">
          <h1 className="welcome-view__title">The Membrane</h1>
          <p className="welcome-view__subtitle">Co-thinking surface</p>

          <div className="welcome-view__description">
            <p>
              This is where you and K-gent think together. Not a chatbot — a collaborative space.
            </p>
          </div>

          <div className="welcome-view__hints">
            <div className="welcome-view__hint">
              <span className="welcome-view__hint-key">Type</span>
              <span className="welcome-view__hint-action">
                Start a thought in the dialogue pane
              </span>
            </div>
            <div className="welcome-view__hint">
              <span className="welcome-view__hint-key">Mention</span>
              <span className="welcome-view__hint-action">
                Reference a file path to see it here
              </span>
            </div>
            <div className="welcome-view__hint">
              <span className="welcome-view__hint-key">Crystallize</span>
              <span className="welcome-view__hint-action">
                Capture decisions to the witness stream
              </span>
            </div>
          </div>

          <div className="welcome-view__quote">
            <blockquote>"The proof IS the decision."</blockquote>
          </div>
        </div>
      </BreathingContainer>
    </div>
  );
}
