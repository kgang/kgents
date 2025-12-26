/**
 * ContradictionWorkspacePage - Focused Dialectical Resolution
 *
 * A dedicated workspace for resolving contradictions between K-Blocks.
 * Uses CONTRADICTION mode and displays ContradictionPolaroid with ResolutionPanel.
 *
 * Philosophy:
 *   "Contradictions are opportunities. Make resolution a first-class experience."
 *
 * Route: /world.contradiction/:id
 */

import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ContradictionPolaroid } from '../primitives/Contradiction/ContradictionPolaroid';
import { ResolutionPanel } from '../primitives/Contradiction/ResolutionPanel';
import type { ResolutionStrategy } from '../primitives/Contradiction/types';
import { useModeContextSafe } from '../context/ModeContext';
import './ContradictionWorkspacePage.css';

// =============================================================================
// Types
// =============================================================================

interface ContradictionPromptResponse {
  contradiction_id: string;
  k_block_a: {
    id: string;
    content: string;
    title?: string;
    layer?: number;
  };
  k_block_b: {
    id: string;
    content: string;
    title?: string;
    layer?: number;
  };
  strength: number;
  classification: {
    type: string;
    reasoning?: string;
  };
  suggested_strategy: string;
  reasoning: string;
  available_strategies: Array<{
    value: string;
    description: string;
    action_verb: string;
    icon: string;
  }>;
}

// =============================================================================
// Component
// =============================================================================

export function ContradictionWorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const modeContext = useModeContextSafe();

  // State
  const [contradiction, setContradiction] = useState<ContradictionPromptResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showResolutionPanel, setShowResolutionPanel] = useState(false);
  const [resolving, setResolving] = useState(false);

  // Set CONTRADICTION mode when entering this page
  useEffect(() => {
    if (modeContext) {
      modeContext.setMode('CONTRADICTION', 'contradiction-workspace');
    }

    // Return to NORMAL mode when leaving
    return () => {
      if (modeContext) {
        modeContext.setMode('NORMAL', 'leaving-contradiction-workspace');
      }
    };
  }, [modeContext]);

  // Fetch contradiction details
  useEffect(() => {
    if (!id) {
      setError('No contradiction ID provided');
      setLoading(false);
      return;
    }

    const fetchContradiction = async () => {
      try {
        const response = await fetch(`/api/contradictions/${encodeURIComponent(id)}`);

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('Contradiction not found');
          }
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data: ContradictionPromptResponse = await response.json();
        setContradiction(data);
        setLoading(false);
      } catch (err) {
        console.error('[ContradictionWorkspace] Error fetching:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      }
    };

    fetchContradiction();
  }, [id]);

  // Handle resolution strategy selection
  const handleResolve = useCallback(
    async (strategy: ResolutionStrategy) => {
      if (!contradiction || !id) return;

      setResolving(true);

      try {
        // Map frontend strategy to backend strategy
        const strategyMap: Record<ResolutionStrategy, string> = {
          synthesis: 'SYNTHESIZE',
          scope: 'SCOPE',
          temporal: 'SCOPE', // Backend doesn't have temporal, map to SCOPE
          context: 'SCOPE', // Backend doesn't have context, map to SCOPE
          supersede: 'CHOOSE',
        };

        const response = await fetch(`/api/contradictions/${encodeURIComponent(id)}/resolve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            strategy: strategyMap[strategy],
            context: { frontend_strategy: strategy },
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Success - navigate back to feed
        navigate('/self.feed');
      } catch (err) {
        console.error('[ContradictionWorkspace] Error resolving:', err);
        setError(err instanceof Error ? err.message : 'Resolution failed');
      } finally {
        setResolving(false);
        setShowResolutionPanel(false);
      }
    },
    [contradiction, id, navigate]
  );

  // Handle quick resolve from polaroid
  const handleQuickResolve = useCallback((_strategy: ResolutionStrategy) => {
    setShowResolutionPanel(true);
  }, []);

  // Loading state
  if (loading) {
    return (
      <div className="contradiction-workspace contradiction-workspace--loading">
        <div className="contradiction-workspace__loading">
          <div className="contradiction-workspace__loading-spinner" />
          <div className="contradiction-workspace__loading-text">Loading contradiction...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !contradiction) {
    return (
      <div className="contradiction-workspace contradiction-workspace--error">
        <div className="contradiction-workspace__error">
          <div className="contradiction-workspace__error-icon">!</div>
          <div className="contradiction-workspace__error-title">Error</div>
          <div className="contradiction-workspace__error-message">
            {error || 'Contradiction not found'}
          </div>
          <button
            className="contradiction-workspace__error-button"
            onClick={() => navigate('/self.feed')}
          >
            Return to Feed
          </button>
        </div>
      </div>
    );
  }

  // Map backend type to frontend type
  const contradictionType = (contradiction.classification.type?.toLowerCase() || 'productive') as
    | 'genuine'
    | 'productive'
    | 'apparent';

  return (
    <div className="contradiction-workspace">
      {/* Header */}
      <header className="contradiction-workspace__header">
        <button
          className="contradiction-workspace__back"
          onClick={() => navigate('/self.feed')}
          aria-label="Back to feed"
        >
          Back
        </button>
        <div className="contradiction-workspace__title">
          <span className="contradiction-workspace__mode-badge">CONTRADICTION</span>
          <h1>Resolve Contradiction</h1>
        </div>
        <div className="contradiction-workspace__actions">
          <button
            className="contradiction-workspace__resolve-btn"
            onClick={() => setShowResolutionPanel(true)}
          >
            Resolve
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="contradiction-workspace__main">
        <div className="contradiction-workspace__polaroid-container">
          <ContradictionPolaroid
            thesis={{
              content: contradiction.k_block_a.content,
              source: contradiction.k_block_a.title || `K-Block ${contradiction.k_block_a.id}`,
            }}
            antithesis={{
              content: contradiction.k_block_b.content,
              source: contradiction.k_block_b.title || `K-Block ${contradiction.k_block_b.id}`,
            }}
            contradictionType={contradictionType}
            onResolve={handleQuickResolve}
            showActions={true}
          />
        </div>

        {/* Strength indicator */}
        <div className="contradiction-workspace__meta">
          <div className="contradiction-workspace__strength">
            <span className="contradiction-workspace__strength-label">Tension Strength:</span>
            <div className="contradiction-workspace__strength-bar">
              <div
                className="contradiction-workspace__strength-fill"
                style={{ width: `${contradiction.strength * 100}%` }}
              />
            </div>
            <span className="contradiction-workspace__strength-value">
              {Math.round(contradiction.strength * 100)}%
            </span>
          </div>

          <div className="contradiction-workspace__suggestion">
            <span className="contradiction-workspace__suggestion-label">Suggested Strategy:</span>
            <span className="contradiction-workspace__suggestion-value">
              {contradiction.suggested_strategy}
            </span>
          </div>

          {contradiction.reasoning && (
            <div className="contradiction-workspace__reasoning">
              <span className="contradiction-workspace__reasoning-label">Reasoning:</span>
              <p className="contradiction-workspace__reasoning-text">{contradiction.reasoning}</p>
            </div>
          )}
        </div>
      </main>

      {/* Resolution Panel Modal */}
      {showResolutionPanel && (
        <ResolutionPanel
          thesis={contradiction.k_block_a.content}
          antithesis={contradiction.k_block_b.content}
          onSelectStrategy={handleResolve}
          suggestedStrategy={contradiction.suggested_strategy.toLowerCase() as ResolutionStrategy}
          onClose={() => setShowResolutionPanel(false)}
          loading={resolving}
        />
      )}
    </div>
  );
}

export default ContradictionWorkspacePage;
