/**
 * WelcomeToStudio — First Time User Experience Phase 3
 *
 * Celebrates the first K-Block creation (F1: Identity Seed) and shows:
 * - Layer assignment (likely L1 Axiom for FTUE)
 * - Loss score with friendly explanation (coherence = 1 - loss)
 * - "You've made your first declaration"
 *
 * Then transitions to the Judgment Experience (F3).
 *
 * FTUE Flow: GenesisPage -> FirstQuestion -> WelcomeToStudio -> JudgmentExperience -> Studio
 *
 * From the spec:
 * > "A statement is axiomatic iff L(statement) < epsilon1 (default: 0.05)"
 * > "coherence(proof) = 1 - L(proof)"
 *
 * @see spec/protocols/ftue-axioms.md (FTUE axioms F1, F2, F3, FG)
 * @see spec/protocols/zero-seed.md (Galois loss)
 */

import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { GrowingContainer } from '../../components/joy';
import './Genesis.css';

// =============================================================================
// Types
// =============================================================================

interface LocationState {
  declaration: string;
  kblock_id: string;
  layer: number;
  loss: number;
  justification: string;
}

// =============================================================================
// Component
// =============================================================================

export function WelcomeToStudio() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [showCelebration, setShowCelebration] = useState(false);

  useEffect(() => {
    // Show celebration animation after component mounts
    const timeout = setTimeout(() => setShowCelebration(true), 800);
    return () => clearTimeout(timeout);
  }, []);

  // Redirect if no state (direct navigation)
  useEffect(() => {
    if (!state) {
      navigate('/genesis/first-question');
    }
  }, [state, navigate]);

  if (!state) return null;

  const handleContinue = () => {
    // Navigate to F3: Judgment Experience
    // Pass the K-Block state so the judgment can reference the user's declaration
    navigate('/genesis/judgment', {
      state: {
        declaration: state.declaration,
        kblock_id: state.kblock_id,
        layer: state.layer,
        loss: state.loss,
        justification: state.justification,
      },
    });
  };

  const getLayerName = (layer: number): string => {
    const layerNames: Record<number, string> = {
      0: 'System',
      1: 'Axiom',
      2: 'Value',
      3: 'Goal',
      4: 'Spec',
      5: 'Implementation',
      6: 'Reflection',
      7: 'Meta',
    };
    return layerNames[layer] || 'Unknown';
  };

  const getLossFriendlyExplanation = (loss: number): string => {
    // Map loss to coherence (1 - loss) for user-friendly display
    const coherence = 1 - loss;
    if (coherence >= 0.95) return 'Near-axiomatic — this is a fixed point!';
    if (coherence >= 0.8) return 'Very coherent — you know what you want!';
    if (coherence >= 0.6) return 'Pretty clear, with room to grow.';
    if (coherence >= 0.4) return "Exploratory — and that's okay!";
    return 'Very open-ended — the system will help you refine this.';
  };

  return (
    <div className="genesis-page">
      <div className="genesis-kblock-container">
        <GrowingContainer autoTrigger duration="deliberate">
          <h1 className="genesis-kblock-title">
            Your first K-Block is being created...
          </h1>
        </GrowingContainer>

        {/* K-Block preview */}
        <GrowingContainer autoTrigger delay={400} duration="normal">
          <div className="genesis-kblock-preview">
            <div className="genesis-kblock-header">
              <span className="genesis-kblock-kind">
                {getLayerName(state.layer).toUpperCase()}
              </span>
              <h2 className="genesis-kblock-declaration">{state.declaration}</h2>
            </div>

            <div className="genesis-kblock-meta">
              <div className="genesis-kblock-meta-item">
                <span className="genesis-kblock-meta-label">Layer:</span>
                <span className="genesis-kblock-meta-value">
                  L{state.layer} ({getLayerName(state.layer)})
                </span>
              </div>

              <div className="genesis-kblock-meta-item">
                <span className="genesis-kblock-meta-label">Coherence:</span>
                <span className="genesis-kblock-meta-value">
                  {((1 - state.loss) * 100).toFixed(0)}% — {getLossFriendlyExplanation(state.loss)}
                </span>
              </div>

              <div className="genesis-kblock-meta-item">
                <span className="genesis-kblock-meta-label">Justification:</span>
                <span className="genesis-kblock-meta-value">"{state.justification}"</span>
              </div>
            </div>
          </div>
        </GrowingContainer>

        {/* Celebration */}
        {showCelebration && (
          <GrowingContainer autoTrigger duration="deliberate">
            <div className="genesis-celebration">
              <p className="genesis-celebration-emoji">✨</p>
              <p className="genesis-celebration-text">
                You've made your first declaration.
              </p>
              <p className="genesis-celebration-subtext">
                The system will help you make it more coherent over time.
              </p>
            </div>
          </GrowingContainer>
        )}

        {/* Continue to F3: Judgment Experience */}
        {showCelebration && (
          <GrowingContainer autoTrigger delay={600} duration="normal">
            <button
              type="button"
              className="genesis-enter-btn"
              onClick={handleContinue}
            >
              Continue
            </button>
          </GrowingContainer>
        )}
      </div>
    </div>
  );
}

export default WelcomeToStudio;
