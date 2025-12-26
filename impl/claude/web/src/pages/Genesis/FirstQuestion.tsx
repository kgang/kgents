/**
 * FirstQuestion — First Time User Experience Phase 2
 *
 * "What matters most to you right now?"
 *
 * This is the moment where the system becomes personal. The user's first
 * declaration becomes their first K-Block (likely L3 Goal layer).
 *
 * From the spec:
 * > "The act of declaring, capturing, and auditing your decisions
 * >  is itself a radical act of self-transformation."
 *
 * Examples:
 * - "I want to build a personal knowledge base"
 * - "I believe in open source"
 * - "I'm exploring what I believe"
 * - "I value clarity over complexity"
 *
 * @see spec/protocols/zero-seed.md (axiom structure)
 * @see plans/zero-seed-creative-strategy-v2.md §Journey 1 (FTUE)
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GrowingContainer } from '../../components/joy';
import './Genesis.css';

// =============================================================================
// Types
// =============================================================================

interface FirstDeclarationResponse {
  kblock_id: string;
  layer: number;
  loss: number;
  justification: string;
}

// =============================================================================
// Component
// =============================================================================

export function FirstQuestion() {
  const navigate = useNavigate();
  const [declaration, setDeclaration] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const examples = [
    'I want to build a personal knowledge base',
    'I believe in open source',
    "I'm exploring what I believe",
    'I value clarity over complexity',
  ];

  const handleSubmit = async () => {
    if (!declaration.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch('/api/onboarding/first-declaration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          declaration: declaration.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create first K-Block');
      }

      const data: FirstDeclarationResponse = await response.json();

      // Navigate to K-Block creation celebration with data
      navigate('/genesis/first-kblock', {
        state: {
          declaration: declaration.trim(),
          ...data,
        },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="genesis-page">
      <div className="genesis-question-container">
        <GrowingContainer autoTrigger duration="deliberate">
          <h1 className="genesis-question-title">
            What matters most to you right now?
          </h1>
        </GrowingContainer>

        <GrowingContainer autoTrigger delay={300} duration="normal">
          <p className="genesis-question-subtitle">
            Your answer becomes your first personal axiom—a fixed point from which everything else derives.
          </p>
        </GrowingContainer>

        <GrowingContainer autoTrigger delay={600} duration="normal">
          <div className="genesis-input-container">
            <textarea
              className="genesis-textarea"
              placeholder="Type what matters to you..."
              value={declaration}
              onChange={(e) => setDeclaration(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus
              rows={3}
              disabled={isSubmitting}
            />
            <p className="genesis-input-hint">
              Press <kbd>⌘</kbd> + <kbd>Enter</kbd> to continue
            </p>
          </div>
        </GrowingContainer>

        {/* Examples */}
        <GrowingContainer autoTrigger delay={900} duration="normal">
          <div className="genesis-examples">
            <p className="genesis-examples-title">Examples:</p>
            <ul className="genesis-examples-list">
              {examples.map((example, index) => (
                <li key={index} className="genesis-example-item">
                  <button
                    type="button"
                    className="genesis-example-btn"
                    onClick={() => setDeclaration(example)}
                    disabled={isSubmitting}
                  >
                    "{example}"
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </GrowingContainer>

        {/* Error state */}
        {error && (
          <GrowingContainer autoTrigger duration="quick">
            <div className="genesis-error">
              <p>{error}</p>
            </div>
          </GrowingContainer>
        )}

        {/* Submit button */}
        <GrowingContainer autoTrigger delay={1200} duration="normal">
          <button
            type="button"
            className="genesis-submit-btn"
            onClick={handleSubmit}
            disabled={!declaration.trim() || isSubmitting}
          >
            {isSubmitting ? 'Creating...' : 'Continue →'}
          </button>
        </GrowingContainer>
      </div>
    </div>
  );
}

export default FirstQuestion;
