/**
 * GroundingDialog -- Modal for grounding orphan K-Blocks to Constitutional principles
 *
 * When a K-Block has no derivation path (orphan), this dialog fetches suggestions
 * from the backend API and lets users select a principle to ground to.
 *
 * Features:
 * - K-Block info at top (title, content preview)
 * - Fetches suggestions from /api/derivation/suggest
 * - Shows 7 principles sorted by confidence
 * - Each principle shows icon, name, loss, confidence, reasoning
 * - Radio selection for principle
 * - Loading states for fetch and confirm
 *
 * Philosophy:
 *   "Every claim derives from axioms. Every axiom traces to Zero Seed."
 *   "Orphans are not failures. They're opportunities for grounding."
 */

import { memo, useCallback, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './GroundingDialog.css';

// =============================================================================
// Types
// =============================================================================

/**
 * A suggested grounding based on content analysis.
 * Matches the backend GroundingSuggestion model.
 */
export interface GroundingSuggestion {
  /** Constitutional principle name (e.g., "COMPOSABLE", "TASTEFUL") */
  principle: string;
  /** Predicted Galois loss if grounded to this principle (0-1, lower is better) */
  galois_loss: number;
  /** Confidence in this suggestion (0-1, higher is better) */
  confidence: number;
  /** Why this principle is suggested */
  reasoning: string;
}

/**
 * Props for the GroundingDialog component.
 */
export interface GroundingDialogProps {
  /** K-Block identifier */
  kblockId: string;
  /** K-Block title for display */
  kblockTitle: string;
  /** K-Block content for analysis and preview */
  kblockContent: string;
  /** Whether the dialog is visible */
  isOpen: boolean;
  /** Callback when dialog is closed */
  onClose: () => void;
  /** Callback when grounding to a principle - called with the principle ID */
  onConfirm: (principleId: string) => Promise<void>;
}

/**
 * K-Block type for export compatibility.
 */
export interface KBlock {
  /** Unique identifier */
  id: string;
  /** File path (may be null for dialogue K-Blocks) */
  path: string | null;
  /** Whether the K-Block has unsaved changes */
  isDirty?: boolean;
  /** Optional display name */
  displayName?: string;
}

// =============================================================================
// Constants
// =============================================================================

const PRINCIPLE_ICONS: Record<string, string> = {
  COMPOSABLE: '>>',
  TASTEFUL: '*',
  GENERATIVE: '~',
  CURATED: '#',
  ETHICAL: '!',
  JOY_INDUCING: ':)',
  HETERARCHICAL: '<>',
  DEFAULT: '◈',
};

const PRINCIPLE_COLORS: Record<string, string> = {
  COMPOSABLE: '#4a9eff', // Blue
  TASTEFUL: '#c4a77d', // Amber/Gold
  GENERATIVE: '#9c27b0', // Purple
  CURATED: '#4caf50', // Green
  ETHICAL: '#ff9800', // Orange
  JOY_INDUCING: '#e91e63', // Magenta
  HETERARCHICAL: '#00bcd4', // Cyan
  DEFAULT: '#888888', // Steel gray
};

// Maximum characters to show in content preview
const CONTENT_PREVIEW_LENGTH = 200;

// =============================================================================
// API Functions
// =============================================================================

async function fetchGroundingSuggestions(content: string): Promise<GroundingSuggestion[]> {
  const response = await fetch('/api/derivation/suggest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch suggestions: ${response.status} - ${errorText}`);
  }

  const data = await response.json();
  return data.suggestions ?? [];
}

// =============================================================================
// Subcomponents
// =============================================================================

interface SuggestionItemProps {
  suggestion: GroundingSuggestion;
  isSelected: boolean;
  onSelect: () => void;
  disabled: boolean;
  isRecommended: boolean;
}

const SuggestionItem = memo(function SuggestionItem({
  suggestion,
  isSelected,
  onSelect,
  disabled,
  isRecommended,
}: SuggestionItemProps) {
  const principleKey = suggestion.principle.toUpperCase().replace(/-/g, '_');
  const icon = PRINCIPLE_ICONS[principleKey] ?? PRINCIPLE_ICONS.DEFAULT;
  const color = PRINCIPLE_COLORS[principleKey] ?? PRINCIPLE_COLORS.DEFAULT;

  return (
    <button
      type="button"
      className={`grounding-dialog__suggestion ${isSelected ? 'grounding-dialog__suggestion--selected' : ''} ${isRecommended ? 'grounding-dialog__suggestion--recommended' : ''}`}
      onClick={onSelect}
      disabled={disabled}
      aria-pressed={isSelected}
      style={{ '--principle-color': color } as React.CSSProperties}
    >
      <div className="grounding-dialog__suggestion-radio">
        <span
          className={`grounding-dialog__radio-indicator ${isSelected ? 'grounding-dialog__radio-indicator--active' : ''}`}
        />
      </div>

      <div className="grounding-dialog__suggestion-content">
        <div className="grounding-dialog__suggestion-header">
          <span className="grounding-dialog__suggestion-icon" style={{ color }}>
            {icon}
          </span>
          <span className="grounding-dialog__suggestion-name">{suggestion.principle}</span>
          <span className="grounding-dialog__suggestion-loss" title="Galois Loss (lower is better)">
            L={suggestion.galois_loss.toFixed(2)}
          </span>
          <span
            className="grounding-dialog__suggestion-confidence"
            title="Confidence (higher is better)"
          >
            C={suggestion.confidence.toFixed(2)}
          </span>
          {isRecommended && (
            <span className="grounding-dialog__recommended-badge">Recommended</span>
          )}
        </div>
        <p className="grounding-dialog__suggestion-reasoning">"{suggestion.reasoning}"</p>
      </div>
    </button>
  );
});

// =============================================================================
// Main Component
// =============================================================================

/**
 * GroundingDialog -- Ground orphan K-Blocks to Constitutional principles
 *
 * Fetches suggestions from the API and lets user select a principle.
 */
export const GroundingDialog = memo(function GroundingDialog({
  kblockId,
  kblockTitle,
  kblockContent,
  isOpen,
  onClose,
  onConfirm,
}: GroundingDialogProps) {
  const [suggestions, setSuggestions] = useState<GroundingSuggestion[]>([]);
  const [selectedPrinciple, setSelectedPrinciple] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGrounding, setIsGrounding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch suggestions when dialog opens
  useEffect(() => {
    if (!isOpen || !kblockContent) {
      return;
    }

    let cancelled = false;

    async function loadSuggestions() {
      setIsLoading(true);
      setError(null);
      setSuggestions([]);
      setSelectedPrinciple(null);

      try {
        const result = await fetchGroundingSuggestions(kblockContent);

        if (cancelled) return;

        // Sort by confidence (highest first), take top 7
        const sorted = result.sort((a, b) => b.confidence - a.confidence).slice(0, 7);

        setSuggestions(sorted);

        // Auto-select the recommended (highest confidence)
        if (sorted.length > 0) {
          setSelectedPrinciple(sorted[0].principle);
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Failed to fetch suggestions');
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadSuggestions();

    return () => {
      cancelled = true;
    };
  }, [isOpen, kblockContent]);

  // Handle escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isGrounding) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, isGrounding, onClose]);

  // Handle grounding action
  const handleGround = useCallback(async () => {
    if (!selectedPrinciple || isGrounding) return;

    setIsGrounding(true);
    setError(null);

    try {
      await onConfirm(selectedPrinciple);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to ground K-Block');
    } finally {
      setIsGrounding(false);
    }
  }, [selectedPrinciple, isGrounding, onConfirm, onClose]);

  // Handle keyboard submission
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        handleGround();
      }
    },
    [handleGround]
  );

  // Content preview (truncated)
  const contentPreview =
    kblockContent.length > CONTENT_PREVIEW_LENGTH
      ? kblockContent.slice(0, CONTENT_PREVIEW_LENGTH) + '...'
      : kblockContent;

  const canGround = selectedPrinciple && !isGrounding && !isLoading;

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="grounding-dialog__overlay" onClick={onClose}>
        <motion.div
          ref={containerRef}
          className="grounding-dialog"
          onClick={(e) => e.stopPropagation()}
          onKeyDown={handleKeyDown}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          role="dialog"
          aria-modal="true"
          aria-labelledby="grounding-dialog-title"
        >
          {/* Header */}
          <header className="grounding-dialog__header">
            <h2 id="grounding-dialog-title" className="grounding-dialog__title">
              <span className="grounding-dialog__title-icon">LINK</span>
              GROUND THIS K-BLOCK
            </h2>
            <button
              className="grounding-dialog__close"
              onClick={onClose}
              disabled={isGrounding}
              title="Close (Esc)"
              aria-label="Close"
            >
              x
            </button>
          </header>

          {/* K-Block Info */}
          <div className="grounding-dialog__kblock-info">
            <div className="grounding-dialog__kblock-header">
              <span className="grounding-dialog__kblock-icon">#</span>
              <span className="grounding-dialog__kblock-title">{kblockTitle}</span>
              <span className="grounding-dialog__kblock-status">(orphan)</span>
            </div>
            <div className="grounding-dialog__kblock-preview">
              <span className="grounding-dialog__preview-label">Content:</span>
              <span className="grounding-dialog__preview-text">{contentPreview}</span>
            </div>
          </div>

          {/* Content */}
          <div className="grounding-dialog__content">
            {/* Loading State */}
            {isLoading && (
              <div className="grounding-dialog__loading">
                <span className="grounding-dialog__spinner" />
                <span>Analyzing content for principle matches...</span>
              </div>
            )}

            {/* Suggestions Section */}
            {!isLoading && suggestions.length > 0 && (
              <div className="grounding-dialog__section">
                <h3 className="grounding-dialog__section-title">
                  SUGGESTED GROUNDINGS (by content analysis):
                </h3>

                <div className="grounding-dialog__suggestions" role="radiogroup">
                  {suggestions.map((suggestion, index) => (
                    <SuggestionItem
                      key={suggestion.principle}
                      suggestion={suggestion}
                      isSelected={selectedPrinciple === suggestion.principle}
                      onSelect={() => setSelectedPrinciple(suggestion.principle)}
                      disabled={isGrounding}
                      isRecommended={index === 0}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && suggestions.length === 0 && !error && (
              <p className="grounding-dialog__empty">
                No principle suggestions available. The K-Block content may not match any known
                principles.
              </p>
            )}
          </div>

          {/* Error State */}
          {error && (
            <div className="grounding-dialog__error" role="alert">
              <span className="grounding-dialog__error-icon">!</span>
              {error}
            </div>
          )}

          {/* Footer */}
          <footer className="grounding-dialog__footer">
            <div className="grounding-dialog__actions">
              <button
                className="grounding-dialog__btn grounding-dialog__btn--secondary"
                onClick={onClose}
                disabled={isGrounding}
              >
                Cancel
              </button>
              <button
                className="grounding-dialog__btn grounding-dialog__btn--primary"
                onClick={handleGround}
                disabled={!canGround}
              >
                {isGrounding ? 'Grounding...' : 'Ground'}
              </button>
            </div>

            <div className="grounding-dialog__hints">
              <kbd>Cmd+Enter</kbd> Ground
              <span className="grounding-dialog__separator">|</span>
              <kbd>Esc</kbd> Cancel
            </div>
          </footer>
        </motion.div>
      </div>
    </AnimatePresence>
  );
});

export default GroundingDialog;
