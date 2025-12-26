/**
 * JudgmentExperience — First Time User Experience Phase 4 (F3)
 *
 * "The user's first Zero Seed judgment establishes 'I can shape this system.'"
 *
 * This is F3 from ftue-axioms.md:
 * 1. System generates a proposal based on user's seeds
 * 2. User exercises judgment (accept/revise/reject)
 * 3. System shows what emerged from the judgment
 * 4. Witness mark captures the decision trail
 *
 * Philosophy:
 * > "The system proposes; the user disposes."
 *
 * @see spec/protocols/ftue-axioms.md (F3: Judgment Experience)
 * @see spec/protocols/zero-seed.md (judgment mechanics)
 */

import { useEffect, useState, useCallback } from 'react';
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

type JudgmentVerdict = 'accept' | 'revise' | 'reject';

interface ProposalData {
  proposal_id: string;
  proposal_type: 'insight' | 'edge' | 'refinement';
  title: string;
  description: string;
  rationale: string;
  confidence: number;
}

interface JudgmentResult {
  success: boolean;
  verdict: JudgmentVerdict;
  emerged: {
    kblock_id?: string;
    edge_id?: string;
    insight?: string;
  };
  witness_mark_id: string;
  message: string;
}

// =============================================================================
// Proposal Generation (Client-side for FTUE)
// =============================================================================

/**
 * Generate a proposal based on user's first declaration.
 *
 * For FTUE, we generate a meaningful insight that connects their
 * declaration to system capabilities. This is a real proposal that
 * affects system state when accepted.
 */
function generateProposal(declaration: string, _layer: number): ProposalData {
  // Analyze declaration for proposal type
  const lowerDecl = declaration.toLowerCase();

  // Knowledge-focused declarations
  if (lowerDecl.includes('knowledge') || lowerDecl.includes('learn') || lowerDecl.includes('understand')) {
    return {
      proposal_id: `proposal-${Date.now()}`,
      proposal_type: 'insight',
      title: 'Structure Your Learning Path',
      description: `Based on your focus on knowledge, the system suggests creating a "Learning Goals" edge that connects your declaration to specific topics you want to explore. This would help track your progress over time.`,
      rationale: 'Your declaration suggests a desire for structured learning. Creating explicit connections between goals and topics enables the system to surface relevant patterns.',
      confidence: 0.78,
    };
  }

  // Values-focused declarations
  if (lowerDecl.includes('believe') || lowerDecl.includes('value') || lowerDecl.includes('principle')) {
    return {
      proposal_id: `proposal-${Date.now()}`,
      proposal_type: 'refinement',
      title: 'Articulate Your Core Principles',
      description: `Your declaration expresses a belief. The system suggests refining this into 2-3 specific principles that can be tested and evolved. For example: "${declaration}" could become actionable guidelines.`,
      rationale: 'Values become powerful when operationalized. Explicit principles create a foundation for consistent decision-making.',
      confidence: 0.82,
    };
  }

  // Goal-focused declarations
  if (lowerDecl.includes('want') || lowerDecl.includes('build') || lowerDecl.includes('create') || lowerDecl.includes('make')) {
    return {
      proposal_id: `proposal-${Date.now()}`,
      proposal_type: 'edge',
      title: 'Define Your First Milestone',
      description: `Your goal "${declaration}" can be broken into milestones. The system proposes creating a first milestone that represents the smallest meaningful step toward your goal.`,
      rationale: 'Large goals become achievable through decomposition. A first milestone makes progress tangible and trackable.',
      confidence: 0.85,
    };
  }

  // Exploration-focused declarations
  if (lowerDecl.includes('explor') || lowerDecl.includes('discover') || lowerDecl.includes('curious')) {
    return {
      proposal_id: `proposal-${Date.now()}`,
      proposal_type: 'insight',
      title: 'Map Your Exploration Territory',
      description: `Exploration benefits from loose structure. The system suggests creating "seed questions" that represent territories you want to explore, without forcing premature conclusions.`,
      rationale: 'Curiosity flourishes within a structured space. Explicit questions enable serendipitous connections.',
      confidence: 0.72,
    };
  }

  // Default: Generic insight based on any declaration
  return {
    proposal_id: `proposal-${Date.now()}`,
    proposal_type: 'insight',
    title: 'Connect to the Foundation',
    description: `Your declaration "${declaration.substring(0, 50)}${declaration.length > 50 ? '...' : ''}" establishes a new node in your personal knowledge graph. The system suggests explicitly connecting it to the system axioms to ground it in the foundation.`,
    rationale: 'Every personal declaration gains meaning through its connections. Explicit links to the foundation enable coherent growth.',
    confidence: 0.75,
  };
}

// =============================================================================
// Component
// =============================================================================

export function JudgmentExperience() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  // UI state
  const [isLoading, setIsLoading] = useState(true);
  const [proposal, setProposal] = useState<ProposalData | null>(null);
  const [verdict, setVerdict] = useState<JudgmentVerdict | null>(null);
  const [revision, setRevision] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<JudgmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Generate proposal on mount
  useEffect(() => {
    if (!state) {
      navigate('/genesis/first-question');
      return;
    }

    // Simulate brief "thinking" for UX
    const timer = setTimeout(() => {
      const generatedProposal = generateProposal(state.declaration, state.layer);
      setProposal(generatedProposal);
      setIsLoading(false);
    }, 1200);

    return () => clearTimeout(timer);
  }, [state, navigate]);

  // Submit judgment to backend
  const submitJudgment = useCallback(async (selectedVerdict: JudgmentVerdict) => {
    if (!proposal || !state) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch('/api/onboarding/judgment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          proposal_id: proposal.proposal_id,
          proposal_type: proposal.proposal_type,
          proposal_title: proposal.title,
          proposal_description: proposal.description,
          kblock_id: state.kblock_id,
          verdict: selectedVerdict,
          revision: selectedVerdict === 'revise' ? revision : undefined,
          declaration: state.declaration,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to record judgment');
      }

      const data: JudgmentResult = await response.json();
      setResult(data);
      setVerdict(selectedVerdict);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setIsSubmitting(false);
    }
  }, [proposal, state, revision]);

  // Handle verdict selection
  const handleVerdict = (selectedVerdict: JudgmentVerdict) => {
    if (selectedVerdict === 'revise') {
      setVerdict('revise');
    } else {
      submitJudgment(selectedVerdict);
    }
  };

  // Handle revision submit
  const handleRevisionSubmit = () => {
    if (!revision.trim()) return;
    submitJudgment('revise');
  };

  // Handle continue to GrowthWitness (FG: the FTUE culmination)
  const handleContinue = () => {
    // Navigate to GrowthWitness to show emergence
    // FG: Growth Witness is the culmination of FTUE
    navigate('/genesis/growth-witness', {
      state: {
        declaration: state?.declaration,
        kblock_id: state?.kblock_id,
        layer: state?.layer,
        loss: state?.loss,
        justification: state?.justification,
        judgment: result,
        // Note: edges will be fetched by GrowthWitness if needed
        // or passed through location.state if available
      },
    });
  };

  // Guard: redirect if no state
  if (!state) return null;

  // Loading state
  if (isLoading) {
    return (
      <div className="genesis-page">
        <div className="genesis-judgment-container">
          <GrowingContainer autoTrigger duration="deliberate">
            <h1 className="genesis-judgment-title">
              Analyzing your declaration...
            </h1>
          </GrowingContainer>
          <GrowingContainer autoTrigger delay={300} duration="normal">
            <p className="genesis-judgment-subtitle">
              The system is generating a proposal based on what matters to you.
            </p>
          </GrowingContainer>
          <div className="genesis-judgment-loading">
            <div className="genesis-judgment-loading-dot" />
            <div className="genesis-judgment-loading-dot" />
            <div className="genesis-judgment-loading-dot" />
          </div>
        </div>
      </div>
    );
  }

  // Result state (after judgment)
  if (result) {
    return (
      <div className="genesis-page">
        <div className="genesis-judgment-container">
          <GrowingContainer autoTrigger duration="deliberate">
            <h1 className="genesis-judgment-title">
              Your judgment shaped the system.
            </h1>
          </GrowingContainer>

          <GrowingContainer autoTrigger delay={300} duration="normal">
            <div className="genesis-judgment-result">
              <div className="genesis-judgment-result-verdict">
                <span className="genesis-judgment-result-label">Your verdict:</span>
                <span className={`genesis-judgment-result-value genesis-judgment-result-value--${result.verdict}`}>
                  {result.verdict === 'accept' && 'Accepted'}
                  {result.verdict === 'revise' && 'Revised'}
                  {result.verdict === 'reject' && 'Rejected'}
                </span>
              </div>

              <div className="genesis-judgment-result-emerged">
                <h3 className="genesis-judgment-result-emerged-title">What emerged:</h3>
                <p className="genesis-judgment-result-emerged-text">
                  {result.message}
                </p>
                {result.emerged.insight && (
                  <blockquote className="genesis-judgment-result-insight">
                    "{result.emerged.insight}"
                  </blockquote>
                )}
              </div>

              <div className="genesis-judgment-result-witness">
                <span className="genesis-judgment-result-witness-icon">👁</span>
                <span className="genesis-judgment-result-witness-text">
                  Decision witnessed: {result.witness_mark_id.slice(0, 8)}...
                </span>
              </div>
            </div>
          </GrowingContainer>

          <GrowingContainer autoTrigger delay={600} duration="normal">
            <div className="genesis-judgment-axiom-planted">
              <p className="genesis-judgment-axiom-planted-text">
                <strong>Axiom F3 planted:</strong> You have proven you can shape this system.
              </p>
            </div>
          </GrowingContainer>

          <GrowingContainer autoTrigger delay={900} duration="normal">
            <button
              type="button"
              className="genesis-enter-btn"
              onClick={handleContinue}
            >
              Witness Emergence
            </button>
          </GrowingContainer>
        </div>
      </div>
    );
  }

  // Revision input state
  if (verdict === 'revise') {
    return (
      <div className="genesis-page">
        <div className="genesis-judgment-container">
          <GrowingContainer autoTrigger duration="deliberate">
            <h1 className="genesis-judgment-title">
              How would you revise this?
            </h1>
          </GrowingContainer>

          <GrowingContainer autoTrigger delay={200} duration="normal">
            <div className="genesis-judgment-proposal genesis-judgment-proposal--faded">
              <h3 className="genesis-judgment-proposal-title">{proposal?.title}</h3>
              <p className="genesis-judgment-proposal-description">{proposal?.description}</p>
            </div>
          </GrowingContainer>

          <GrowingContainer autoTrigger delay={400} duration="normal">
            <div className="genesis-input-container">
              <textarea
                className="genesis-textarea"
                placeholder="Describe your revision..."
                value={revision}
                onChange={(e) => setRevision(e.target.value)}
                autoFocus
                rows={4}
                disabled={isSubmitting}
              />
              <p className="genesis-input-hint">
                Your revision will modify how the system interprets this proposal.
              </p>
            </div>
          </GrowingContainer>

          {error && (
            <GrowingContainer autoTrigger duration="quick">
              <div className="genesis-error">
                <p>{error}</p>
              </div>
            </GrowingContainer>
          )}

          <GrowingContainer autoTrigger delay={600} duration="normal">
            <div className="genesis-judgment-actions">
              <button
                type="button"
                className="genesis-judgment-btn genesis-judgment-btn--secondary"
                onClick={() => setVerdict(null)}
                disabled={isSubmitting}
              >
                Back
              </button>
              <button
                type="button"
                className="genesis-judgment-btn genesis-judgment-btn--primary"
                onClick={handleRevisionSubmit}
                disabled={!revision.trim() || isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Revision'}
              </button>
            </div>
          </GrowingContainer>
        </div>
      </div>
    );
  }

  // Main judgment UI (proposal display + verdict buttons)
  return (
    <div className="genesis-page">
      <div className="genesis-judgment-container">
        <GrowingContainer autoTrigger duration="deliberate">
          <h1 className="genesis-judgment-title">
            The system has a proposal.
          </h1>
        </GrowingContainer>

        <GrowingContainer autoTrigger delay={200} duration="normal">
          <p className="genesis-judgment-subtitle">
            Based on your declaration, the system generated this insight.
            <br />
            <strong>Your judgment shapes what happens next.</strong>
          </p>
        </GrowingContainer>

        {/* User's declaration for context */}
        <GrowingContainer autoTrigger delay={400} duration="normal">
          <div className="genesis-judgment-context">
            <span className="genesis-judgment-context-label">Your declaration:</span>
            <blockquote className="genesis-judgment-context-quote">
              "{state.declaration}"
            </blockquote>
          </div>
        </GrowingContainer>

        {/* The proposal */}
        <GrowingContainer autoTrigger delay={600} duration="normal">
          <div className="genesis-judgment-proposal">
            <div className="genesis-judgment-proposal-header">
              <span className="genesis-judgment-proposal-type">
                {proposal?.proposal_type === 'insight' && 'System Insight'}
                {proposal?.proposal_type === 'edge' && 'Connection Proposal'}
                {proposal?.proposal_type === 'refinement' && 'Refinement Suggestion'}
              </span>
              <span className="genesis-judgment-proposal-confidence">
                {Math.round((proposal?.confidence || 0) * 100)}% confidence
              </span>
            </div>
            <h3 className="genesis-judgment-proposal-title">{proposal?.title}</h3>
            <p className="genesis-judgment-proposal-description">{proposal?.description}</p>
            <p className="genesis-judgment-proposal-rationale">
              <em>Rationale:</em> {proposal?.rationale}
            </p>
          </div>
        </GrowingContainer>

        {error && (
          <GrowingContainer autoTrigger duration="quick">
            <div className="genesis-error">
              <p>{error}</p>
            </div>
          </GrowingContainer>
        )}

        {/* Verdict buttons */}
        <GrowingContainer autoTrigger delay={800} duration="normal">
          <div className="genesis-judgment-verdicts">
            <button
              type="button"
              className="genesis-judgment-verdict genesis-judgment-verdict--accept"
              onClick={() => handleVerdict('accept')}
              disabled={isSubmitting}
            >
              <span className="genesis-judgment-verdict-icon">&#10003;</span>
              <span className="genesis-judgment-verdict-label">Accept</span>
              <span className="genesis-judgment-verdict-description">
                Apply this proposal
              </span>
            </button>

            <button
              type="button"
              className="genesis-judgment-verdict genesis-judgment-verdict--revise"
              onClick={() => handleVerdict('revise')}
              disabled={isSubmitting}
            >
              <span className="genesis-judgment-verdict-icon">&#9998;</span>
              <span className="genesis-judgment-verdict-label">Revise</span>
              <span className="genesis-judgment-verdict-description">
                Modify this proposal
              </span>
            </button>

            <button
              type="button"
              className="genesis-judgment-verdict genesis-judgment-verdict--reject"
              onClick={() => handleVerdict('reject')}
              disabled={isSubmitting}
            >
              <span className="genesis-judgment-verdict-icon">&#10007;</span>
              <span className="genesis-judgment-verdict-label">Reject</span>
              <span className="genesis-judgment-verdict-description">
                Decline this proposal
              </span>
            </button>
          </div>
        </GrowingContainer>

        <GrowingContainer autoTrigger delay={1000} duration="normal">
          <p className="genesis-judgment-note">
            This is F3: Your first judgment establishes that <em>you shape this system</em>.
          </p>
        </GrowingContainer>
      </div>
    </div>
  );
}

export default JudgmentExperience;
