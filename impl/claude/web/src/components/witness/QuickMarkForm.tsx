/**
 * QuickMarkForm: Minimal friction mark creation.
 *
 * "Two keystrokes. One mark. No friction."
 *
 * Keyboard shortcuts:
 * - Enter: Submit (action only)
 * - Shift+Enter: Expand reasoning field
 * - Cmd/Ctrl+Enter: Submit with reasoning
 * - Escape: Clear and reset
 *
 * @see plans/witness-fusion-ux-design.md
 */

import {
  useState,
  useCallback,
  useRef,
  useEffect,
  type KeyboardEvent,
  type FormEvent,
} from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { CreateMarkRequest } from '@/api/witness';

// =============================================================================
// Living Earth Palette
// =============================================================================

const LIVING_EARTH = {
  soil: '#2D1B14',
  soilLight: '#3D2B24',
  wood: '#6B4E3D',
  woodLight: '#8B6E5D',
  copper: '#C08552',
  copperLight: '#D09562',
  sage: '#4A6B4A',
  honey: '#E8C4A0',
  lantern: '#F5E6D3',
} as const;

// =============================================================================
// Available Principles
// =============================================================================

const PRINCIPLES = [
  'tasteful',
  'curated',
  'ethical',
  'joy-inducing',
  'composable',
  'heterarchical',
  'generative',
] as const;

// =============================================================================
// Types
// =============================================================================

export interface QuickMarkFormProps {
  /** Called when a mark is submitted */
  onSubmit: (request: CreateMarkRequest) => Promise<void>;

  /** Default principles to select */
  defaultPrinciples?: string[];

  /** Placeholder text for action input */
  placeholder?: string;

  /** Whether the form is disabled */
  disabled?: boolean;

  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Main Component
// =============================================================================

export function QuickMarkForm({
  onSubmit,
  defaultPrinciples = [],
  placeholder = 'What happened? (e.g., "Chose PostgreSQL over SQLite")',
  disabled = false,
  className = '',
}: QuickMarkFormProps) {
  // State
  const [action, setAction] = useState('');
  const [reasoning, setReasoning] = useState('');
  const [selectedPrinciples, setSelectedPrinciples] = useState<Set<string>>(
    new Set(defaultPrinciples)
  );
  const [isExpanded, setIsExpanded] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);

  // Refs
  const actionInputRef = useRef<HTMLInputElement>(null);
  const reasoningInputRef = useRef<HTMLTextAreaElement>(null);

  // Focus action input on mount
  useEffect(() => {
    actionInputRef.current?.focus();
  }, []);

  // Focus reasoning when expanded
  useEffect(() => {
    if (isExpanded) {
      reasoningInputRef.current?.focus();
    }
  }, [isExpanded]);

  // Reset form
  const resetForm = useCallback(() => {
    setAction('');
    setReasoning('');
    setSelectedPrinciples(new Set(defaultPrinciples));
    setIsExpanded(false);
    setError(null);
    actionInputRef.current?.focus();
  }, [defaultPrinciples]);

  // Handle submit
  const handleSubmit = useCallback(
    async (e?: FormEvent) => {
      e?.preventDefault();

      if (!action.trim() || isSubmitting || disabled) {
        return;
      }

      setIsSubmitting(true);
      setError(null);

      try {
        await onSubmit({
          action: action.trim(),
          reasoning: reasoning.trim() || undefined,
          principles:
            selectedPrinciples.size > 0
              ? Array.from(selectedPrinciples)
              : undefined,
        });

        // Show success briefly
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 1500);

        // Reset form
        resetForm();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to create mark');
      } finally {
        setIsSubmitting(false);
      }
    },
    [action, reasoning, selectedPrinciples, onSubmit, isSubmitting, disabled, resetForm]
  );

  // Handle keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Escape: clear and reset
      if (e.key === 'Escape') {
        e.preventDefault();
        resetForm();
        return;
      }

      // Shift+Enter: expand reasoning
      if (e.key === 'Enter' && e.shiftKey && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        setIsExpanded(true);
        return;
      }

      // Cmd/Ctrl+Enter: submit with reasoning
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        handleSubmit();
        return;
      }

      // Enter (no modifiers): submit action only (if not in textarea)
      if (e.key === 'Enter' && !e.shiftKey && !e.metaKey && !e.ctrlKey) {
        // If we're in the reasoning textarea, don't submit on plain Enter
        if (e.target === reasoningInputRef.current) {
          return;
        }
        e.preventDefault();
        handleSubmit();
        return;
      }
    },
    [handleSubmit, resetForm]
  );

  // Toggle principle selection
  const togglePrinciple = useCallback((principle: string) => {
    setSelectedPrinciples((prev) => {
      const next = new Set(prev);
      if (next.has(principle)) {
        next.delete(principle);
      } else {
        next.add(principle);
      }
      return next;
    });
  }, []);

  return (
    <form
      onSubmit={handleSubmit}
      className={`rounded-lg ${className}`}
      style={{ backgroundColor: LIVING_EARTH.soilLight }}
      data-testid="quick-mark-form"
    >
      {/* Action Input */}
      <div className="relative">
        <input
          ref={actionInputRef}
          type="text"
          value={action}
          onChange={(e) => setAction(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isSubmitting}
          className="w-full px-4 py-3 text-base rounded-t-lg border-0 outline-none"
          style={{
            backgroundColor: 'transparent',
            color: LIVING_EARTH.lantern,
          }}
          aria-label="Action"
          data-testid="action-input"
        />

        {/* Submit button (inline) */}
        <motion.button
          type="submit"
          disabled={!action.trim() || isSubmitting || disabled}
          className="absolute right-3 top-1/2 -translate-y-1/2 px-3 py-1 rounded text-sm font-medium transition-opacity"
          style={{
            backgroundColor: LIVING_EARTH.copper,
            color: LIVING_EARTH.soil,
            opacity: action.trim() ? 1 : 0.3,
          }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isSubmitting ? '\u2022\u2022\u2022' : 'Mark'}
        </motion.button>
      </div>

      {/* Expanded Section (Reasoning + Principles) */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {/* Reasoning Input */}
            <div className="px-4 py-2">
              <label
                className="text-xs block mb-1"
                style={{ color: LIVING_EARTH.woodLight }}
              >
                Why? (optional)
              </label>
              <textarea
                ref={reasoningInputRef}
                value={reasoning}
                onChange={(e) => setReasoning(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="The reasoning behind this action..."
                disabled={disabled || isSubmitting}
                rows={2}
                className="w-full px-3 py-2 text-sm rounded border-0 outline-none resize-none"
                style={{
                  backgroundColor: LIVING_EARTH.soil,
                  color: LIVING_EARTH.lantern,
                }}
                data-testid="reasoning-input"
              />
            </div>

            {/* Principle Chips */}
            <div className="px-4 py-2 flex flex-wrap gap-1.5">
              {PRINCIPLES.map((principle) => (
                <button
                  key={principle}
                  type="button"
                  onClick={() => togglePrinciple(principle)}
                  className="px-2 py-0.5 text-xs rounded-full transition-all"
                  style={{
                    backgroundColor: selectedPrinciples.has(principle)
                      ? LIVING_EARTH.honey
                      : `${LIVING_EARTH.honey}20`,
                    color: selectedPrinciples.has(principle)
                      ? LIVING_EARTH.soil
                      : LIVING_EARTH.honey,
                    border: `1px solid ${LIVING_EARTH.honey}40`,
                  }}
                  data-testid={`principle-${principle}`}
                >
                  {principle}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom Bar: Hints + Expand Toggle */}
      <div
        className="flex items-center justify-between px-4 py-2 text-xs border-t"
        style={{
          borderColor: `${LIVING_EARTH.wood}30`,
          color: LIVING_EARTH.wood,
        }}
      >
        <div className="flex gap-3">
          <span>
            <kbd className="px-1 rounded" style={{ backgroundColor: LIVING_EARTH.soil }}>
              Enter
            </kbd>{' '}
            submit
          </span>
          {!isExpanded && (
            <span>
              <kbd className="px-1 rounded" style={{ backgroundColor: LIVING_EARTH.soil }}>
                Shift+Enter
              </kbd>{' '}
              add reasoning
            </span>
          )}
          {isExpanded && (
            <span>
              <kbd className="px-1 rounded" style={{ backgroundColor: LIVING_EARTH.soil }}>
                Cmd+Enter
              </kbd>{' '}
              submit with reasoning
            </span>
          )}
        </div>

        {!isExpanded && (
          <button
            type="button"
            onClick={() => setIsExpanded(true)}
            className="hover:underline"
            style={{ color: LIVING_EARTH.copper }}
          >
            + Add details
          </button>
        )}
      </div>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="px-4 py-2 text-sm"
            style={{
              backgroundColor: `${LIVING_EARTH.copper}20`,
              color: LIVING_EARTH.copper,
            }}
            data-testid="error-message"
          >
            \u26A0\uFE0F {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Success Flash */}
      <AnimatePresence>
        {showSuccess && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="absolute inset-0 flex items-center justify-center rounded-lg pointer-events-none"
            style={{ backgroundColor: `${LIVING_EARTH.sage}90` }}
          >
            <span className="text-2xl">\u2713</span>
          </motion.div>
        )}
      </AnimatePresence>
    </form>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default QuickMarkForm;
