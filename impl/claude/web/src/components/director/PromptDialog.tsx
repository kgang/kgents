/**
 * PromptDialog - Modal for displaying and copying execution prompts
 *
 * Shows:
 * - Generated prompt with syntax highlighting
 * - List of target files
 * - Evidence mark ID (L-2 PROMPT mark)
 * - Copy to clipboard functionality
 *
 * Usage:
 * ```tsx
 * import { PromptDialog } from './components/director';
 *
 * function MyComponent() {
 *   const [showPrompt, setShowPrompt] = useState(false);
 *   const [specPath, setSpecPath] = useState('');
 *
 *   return (
 *     <>
 *       <button onClick={() => { setSpecPath('spec/foo.md'); setShowPrompt(true); }}>
 *         Generate Prompt
 *       </button>
 *       {showPrompt && (
 *         <PromptDialog path={specPath} onClose={() => setShowPrompt(false)} />
 *       )}
 *     </>
 *   );
 * }
 * ```
 */

import { useCallback, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import { generatePrompt, type ExecutionPrompt } from '../../api/director';

import './PromptDialog.css';

// =============================================================================
// Types
// =============================================================================

interface PromptDialogProps {
  path: string;
  onClose: () => void;
}

// =============================================================================
// Component
// =============================================================================

export function PromptDialog({ path, onClose }: PromptDialogProps) {
  const [prompt, setPrompt] = useState<ExecutionPrompt | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Load prompt on mount
  useEffect(() => {
    const loadPrompt = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await generatePrompt(path);
        setPrompt(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to generate prompt');
      } finally {
        setLoading(false);
      }
    };

    loadPrompt();
  }, [path]);

  // Copy to clipboard
  const handleCopy = useCallback(() => {
    if (!prompt) return;

    const text = `# Specification: ${prompt.spec_path}

${prompt.spec_content}

## Implementation Targets

${prompt.targets.map((t) => `- ${t}`).join('\n')}

## Context

Claims: ${prompt.context.claims.length}
Existing refs: ${prompt.context.existing_refs.length}

${
  prompt.context.claims.length > 0
    ? `## Claims Detail\n\n${prompt.context.claims
        .map((c) => `- **${c.type}**: ${c.subject} ${c.predicate} (L${c.line})`)
        .join('\n')}`
    : ''
}`;

    navigator.clipboard.writeText(text);
    setCopied(true);

    // Reset copied state after 2 seconds
    setTimeout(() => setCopied(false), 2000);
  }, [prompt]);

  // Handle escape key
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
    <AnimatePresence>
      <div className="prompt-dialog__overlay" onClick={onClose}>
        <motion.div
          className="prompt-dialog"
          onClick={(e) => e.stopPropagation()}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
        >
          {/* Header */}
          <header className="prompt-dialog__header">
            <h2 className="prompt-dialog__title">Execution Prompt</h2>
            <button
              className="prompt-dialog__close"
              onClick={onClose}
              title="Close (Esc)"
              aria-label="Close"
            >
              ✕
            </button>
          </header>

          {/* Content */}
          <div className="prompt-dialog__content">
            {loading && (
              <div className="prompt-dialog__loading">
                <div className="prompt-dialog__spinner" />
                <p>Generating prompt...</p>
              </div>
            )}

            {error && (
              <div className="prompt-dialog__error">
                <p>{error}</p>
              </div>
            )}

            {prompt && !loading && !error && (
              <>
                {/* Evidence Mark */}
                {prompt.mark_id && (
                  <div className="prompt-dialog__evidence">
                    <span className="prompt-dialog__evidence-label">Evidence Mark:</span>
                    <code className="prompt-dialog__evidence-id">{prompt.mark_id}</code>
                  </div>
                )}

                {/* Target Files */}
                {prompt.targets.length > 0 && (
                  <section className="prompt-dialog__section">
                    <h3 className="prompt-dialog__section-title">
                      TARGET FILES ({prompt.targets.length})
                    </h3>
                    <div className="prompt-dialog__targets">
                      {prompt.targets.map((target, i) => (
                        <span key={i} className="prompt-dialog__target-pill">
                          {target}
                        </span>
                      ))}
                    </div>
                  </section>
                )}

                {/* Context Summary */}
                <section className="prompt-dialog__section">
                  <h3 className="prompt-dialog__section-title">CONTEXT</h3>
                  <div className="prompt-dialog__context">
                    <div className="prompt-dialog__context-item">
                      <span className="prompt-dialog__context-label">Claims:</span>
                      <span className="prompt-dialog__context-value">
                        {prompt.context.claims.length}
                      </span>
                    </div>
                    <div className="prompt-dialog__context-item">
                      <span className="prompt-dialog__context-label">Existing refs:</span>
                      <span className="prompt-dialog__context-value">
                        {prompt.context.existing_refs.length}
                      </span>
                    </div>
                  </div>
                </section>

                {/* Spec Content */}
                <section className="prompt-dialog__section">
                  <h3 className="prompt-dialog__section-title">SPECIFICATION</h3>
                  <div className="prompt-dialog__spec-container">
                    <pre className="prompt-dialog__spec-content">
                      <code>{prompt.spec_content}</code>
                    </pre>
                  </div>
                </section>
              </>
            )}
          </div>

          {/* Footer */}
          {prompt && !loading && !error && (
            <footer className="prompt-dialog__footer">
              <button className="prompt-dialog__btn prompt-dialog__btn--secondary" onClick={onClose}>
                Close
              </button>
              <button
                className="prompt-dialog__btn prompt-dialog__btn--primary"
                onClick={handleCopy}
              >
                {copied ? '✓ Copied!' : 'Copy to Clipboard'}
              </button>
            </footer>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
