/**
 * ForkModal — Dialog for creating conversation forks
 *
 * Features:
 * - Named branch creation (no "Branch-1" defaults)
 * - 3-branch cognitive limit (MAX_BRANCHES = 3)
 * - Fork point selection (defaults to current turn)
 * - Validation: unique names, no spaces
 * - Keyboard support: Enter to submit, Escape to close
 *
 * @see spec/protocols/chat-web.md §2.2 (Branching Algebra)
 * @see spec/protocols/chat-web.md §4.2-4.4 (Fork UI)
 */

import { memo, useCallback, useEffect, useRef, useState, KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './ForkModal.css';

// =============================================================================
// Constants
// =============================================================================

const MAX_BRANCHES = 3; // Cognitive limit from spec §2.2

// =============================================================================
// Types
// =============================================================================

export interface ForkModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Close handler */
  onClose: () => void;
  /** Confirm handler - receives branch name and optional fork point */
  onConfirm: (branchName: string, forkPoint?: number) => void;
  /** Current turn number (default fork point) */
  currentTurn: number;
  /** Existing branch names for validation */
  existingBranches: string[];
  /** Whether forking is allowed (false if at 3-branch limit) */
  canFork: boolean;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * ForkModal — Create named conversation forks
 */
export const ForkModal = memo(function ForkModal({
  isOpen,
  onClose,
  onConfirm,
  currentTurn,
  existingBranches,
  canFork,
}: ForkModalProps) {
  const [branchName, setBranchName] = useState('');
  const [forkPoint, setForkPoint] = useState(currentTurn);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setBranchName('');
      setForkPoint(currentTurn);
      setError(null);

      // Auto-focus input after animation
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, currentTurn]);

  // Validate branch name
  const validateName = useCallback(
    (name: string): string | null => {
      if (!name.trim()) {
        return 'Branch name is required';
      }

      if (/\s/.test(name)) {
        return 'Branch name cannot contain spaces';
      }

      if (existingBranches.includes(name)) {
        return 'Branch name already exists';
      }

      if (name.length > 50) {
        return 'Branch name too long (max 50 characters)';
      }

      return null;
    },
    [existingBranches]
  );

  // Handle name change
  const handleNameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setBranchName(value);

      // Clear error when user types
      if (error) {
        setError(null);
      }
    },
    [error]
  );

  // Handle confirm
  const handleConfirm = useCallback(() => {
    if (!canFork) return;

    const validationError = validateName(branchName);
    if (validationError) {
      setError(validationError);
      return;
    }

    onConfirm(branchName, forkPoint === currentTurn ? undefined : forkPoint);
    onClose();
  }, [canFork, branchName, forkPoint, currentTurn, validateName, onConfirm, onClose]);

  // Keyboard handling
  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleConfirm();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    },
    [handleConfirm, onClose]
  );

  // Handle escape key globally
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: globalThis.KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const branchCount = existingBranches.length;
  const isAtLimit = branchCount >= MAX_BRANCHES;
  const canSubmit = canFork && branchName.trim().length > 0 && !error;

  return (
    <AnimatePresence>
      <div className="fork-modal__overlay" onClick={onClose}>
        <motion.div
          className="fork-modal"
          onClick={(e) => e.stopPropagation()}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
        >
          {/* Header */}
          <header className="fork-modal__header">
            <h2 className="fork-modal__title">Fork Conversation</h2>
            <button
              className="fork-modal__close"
              onClick={onClose}
              title="Close (Esc)"
              aria-label="Close"
            >
              ✕
            </button>
          </header>

          {/* Content */}
          <div className="fork-modal__content">
            {/* Branch limit warning */}
            {isAtLimit && (
              <div className="fork-modal__warning">
                <span className="fork-modal__warning-icon">◆</span>
                <span className="fork-modal__warning-text">
                  Maximum branches reached ({MAX_BRANCHES}/{MAX_BRANCHES}). Cannot create new
                  forks.
                </span>
              </div>
            )}

            {!isAtLimit && branchCount === MAX_BRANCHES - 1 && (
              <div className="fork-modal__warning fork-modal__warning--info">
                <span className="fork-modal__warning-icon">◇</span>
                <span className="fork-modal__warning-text">
                  This will be your last branch ({MAX_BRANCHES}/{MAX_BRANCHES}). Consider merging
                  dormant branches.
                </span>
              </div>
            )}

            {/* Branch name input */}
            <div className="fork-modal__field">
              <label className="fork-modal__label" htmlFor="branch-name">
                Branch Name
              </label>
              <input
                ref={inputRef}
                id="branch-name"
                type="text"
                className={`fork-modal__input ${error ? 'fork-modal__input--error' : ''}`}
                value={branchName}
                onChange={handleNameChange}
                onKeyDown={handleKeyDown}
                placeholder="explore-new-approach"
                disabled={!canFork}
                maxLength={50}
              />
              {error && <span className="fork-modal__error">{error}</span>}
              <span className="fork-modal__hint">
                Use lowercase with hyphens. No spaces allowed.
              </span>
            </div>

            {/* Fork point selector */}
            <div className="fork-modal__field">
              <label className="fork-modal__label" htmlFor="fork-point">
                Fork from turn
              </label>
              <select
                id="fork-point"
                className="fork-modal__select"
                value={forkPoint}
                onChange={(e) => setForkPoint(Number(e.target.value))}
                disabled={!canFork}
              >
                {Array.from({ length: currentTurn }, (_, i) => i + 1).map((turn) => (
                  <option key={turn} value={turn}>
                    {turn === currentTurn ? `${turn} (current)` : turn}
                  </option>
                ))}
              </select>
              <span className="fork-modal__hint">Select the turn to fork from.</span>
            </div>

            {/* Branch counter */}
            <div className="fork-modal__counter">
              <span className="fork-modal__counter-label">Branches:</span>
              <div className="fork-modal__counter-bar">
                <div
                  className="fork-modal__counter-fill"
                  style={{ width: `${(branchCount / MAX_BRANCHES) * 100}%` }}
                />
              </div>
              <span className="fork-modal__counter-text">
                {branchCount}/{MAX_BRANCHES}
              </span>
            </div>
          </div>

          {/* Footer */}
          <footer className="fork-modal__footer">
            <button className="fork-modal__btn fork-modal__btn--secondary" onClick={onClose}>
              Cancel
            </button>
            <button
              className="fork-modal__btn fork-modal__btn--primary"
              onClick={handleConfirm}
              disabled={!canSubmit}
            >
              Create Fork
            </button>
          </footer>
        </motion.div>
      </div>
    </AnimatePresence>
  );
});

export default ForkModal;
