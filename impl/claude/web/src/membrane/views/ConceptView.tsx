/**
 * ConceptView — Display a concept explanation
 *
 * Shows conceptual information when a concept: reference is focused.
 * Could wire to AGENTESE concept.* paths in the future.
 */

import { BreathingContainer } from '../../components/genesis/BreathingContainer';

import './ConceptView.css';

// =============================================================================
// Types
// =============================================================================

interface ConceptViewProps {
  concept: string;
}

// =============================================================================
// Component
// =============================================================================

export function ConceptView({ concept }: ConceptViewProps) {
  // For now, show a placeholder
  // TODO: Wire to AGENTESE concept.* paths

  return (
    <div className="concept-view">
      <BreathingContainer intensity="subtle" period="calm">
        <div className="concept-view__content">
          <header className="concept-view__header">
            <span className="concept-view__label">Concept</span>
            <h2 className="concept-view__title">{concept}</h2>
          </header>

          <div className="concept-view__body">
            <p className="concept-view__placeholder">Concept exploration coming soon.</p>
            <p className="concept-view__hint">
              This will wire to AGENTESE <code>concept.*</code> paths to provide rich conceptual
              explanations.
            </p>
          </div>
        </div>
      </BreathingContainer>
    </div>
  );
}
