/**
 * GroundingDialog -- Modal for grounding orphan K-Blocks to Constitutional principles
 *
 * When a K-Block has no derivation path (orphan), this dialog suggests
 * Constitutional principles based on content analysis, sorted by Galois loss.
 *
 * Features:
 * - K-Block info at top (path, status)
 * - Suggested principles sorted by Galois loss (lowest first)
 * - Radio selection for principle
 * - Optional: drag-drop target for grounding to another K-Block
 * - Loading state while grounding
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
 * A K-Block to be grounded.
 * Minimal interface needed for the dialog.
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

/**
 * A suggested grounding based on content analysis.
 */
export interface GroundingSuggestion {
  /** Constitutional principle name (e.g., "COMPOSABLE", "TASTEFUL") */
  principle: string;
  /** Galois loss value (0-1, lower is better) */
  galoisLoss: number;
  /** Explanation of why this principle matches */
  reasoning: string;
  /** Whether this is the recommended option (lowest loss) */
  recommended?: boolean;
}

/**
 * Props for the GroundingDialog component.
 */
export interface GroundingDialogProps {
  /** Whether the dialog is visible */
  isOpen: boolean;
  /** Callback when dialog is closed */
  onClose: () => void;
  /** The K-Block to ground */
  kblock: KBlock;
  /** Suggested principles sorted by Galois loss */
  suggestions: GroundingSuggestion[];
  /** Callback when grounding to a principle */
  onGround: (principle: string) => Promise<void>;
  /** Optional: Callback when grounding to another K-Block (drag-drop) */
  onGroundToKBlock?: (parentKBlockId: string) => Promise<void>;
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
  DEFAULT: '@',
};

// =============================================================================
// Subcomponents
// =============================================================================

interface SuggestionItemProps {
  suggestion: GroundingSuggestion;
  isSelected: boolean;
  onSelect: () => void;
  disabled: boolean;
}

const SuggestionItem = memo(function SuggestionItem({
  suggestion,
  isSelected,
  onSelect,
  disabled,
}: SuggestionItemProps) {
  const icon = PRINCIPLE_ICONS[suggestion.principle] ?? PRINCIPLE_ICONS.DEFAULT;

  return (
    <button
      type="button"
      className={`grounding-dialog__suggestion ${isSelected ? 'grounding-dialog__suggestion--selected' : ''} ${suggestion.recommended ? 'grounding-dialog__suggestion--recommended' : ''}`}
      onClick={onSelect}
      disabled={disabled}
      aria-pressed={isSelected}
    >
      <div className="grounding-dialog__suggestion-radio">
        <span
          className={`grounding-dialog__radio-indicator ${isSelected ? 'grounding-dialog__radio-indicator--active' : ''}`}
        />
      </div>

      <div className="grounding-dialog__suggestion-content">
        <div className="grounding-dialog__suggestion-header">
          <span className="grounding-dialog__suggestion-icon">{icon}</span>
          <span className="grounding-dialog__suggestion-name">{suggestion.principle}</span>
          <span className="grounding-dialog__suggestion-loss" title="Galois Loss (lower is better)">
            L={suggestion.galoisLoss.toFixed(2)}
          </span>
          {suggestion.recommended && (
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
 */
export const GroundingDialog = memo(function GroundingDialog({
  isOpen,
  onClose,
  kblock,
  suggestions,
  onGround,
  onGroundToKBlock,
}: GroundingDialogProps) {
  const [selectedPrinciple, setSelectedPrinciple] = useState<string | null>(null);
  const [isGrounding, setIsGrounding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-select recommended (lowest loss) on open
  useEffect(() => {
    if (isOpen && suggestions.length > 0) {
      const recommended = suggestions.find((s) => s.recommended);
      setSelectedPrinciple(recommended?.principle ?? suggestions[0].principle);
      setError(null);
    }
  }, [isOpen, suggestions]);

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
      await onGround(selectedPrinciple);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to ground K-Block');
    } finally {
      setIsGrounding(false);
    }
  }, [selectedPrinciple, isGrounding, onGround, onClose]);

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

  // Drag handlers for K-Block drop zone
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(false);

      if (!onGroundToKBlock) return;

      // Try to get K-Block ID from drag data
      const kblockId = e.dataTransfer.getData('application/kblock-id');
      if (kblockId && kblockId !== kblock.id) {
        setIsGrounding(true);
        setError(null);
        try {
          await onGroundToKBlock(kblockId);
          onClose();
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to ground to K-Block');
        } finally {
          setIsGrounding(false);
        }
      }
    },
    [onGroundToKBlock, kblock.id, onClose]
  );

  // Display name for the K-Block
  const displayName = kblock.displayName ?? kblock.path ?? 'Untitled K-Block';
  const canGround = selectedPrinciple && !isGrounding;

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
            <span className="grounding-dialog__kblock-icon">#</span>
            <span className="grounding-dialog__kblock-path">{displayName}</span>
            <span className="grounding-dialog__kblock-status">(currently orphan)</span>
          </div>

          {/* Content */}
          <div className="grounding-dialog__content">
            {/* Suggestions Section */}
            <div className="grounding-dialog__section">
              <h3 className="grounding-dialog__section-title">
                SUGGESTED GROUNDINGS (by content analysis):
              </h3>

              {suggestions.length === 0 ? (
                <p className="grounding-dialog__empty">No suggestions available.</p>
              ) : (
                <div className="grounding-dialog__suggestions" role="radiogroup">
                  {suggestions.map((suggestion) => (
                    <SuggestionItem
                      key={suggestion.principle}
                      suggestion={suggestion}
                      isSelected={selectedPrinciple === suggestion.principle}
                      onSelect={() => setSelectedPrinciple(suggestion.principle)}
                      disabled={isGrounding}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Drop Zone (optional feature) */}
            {onGroundToKBlock && (
              <div
                className={`grounding-dialog__dropzone ${isDragOver ? 'grounding-dialog__dropzone--active' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <span className="grounding-dialog__dropzone-text">
                  Or drag to any K-Block in the graph to derive from it.
                </span>
              </div>
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
                {isGrounding ? 'Grounding...' : 'Ground to Selected'}
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
