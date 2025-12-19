/**
 * GhostExplorationModal — Explore Roads Not Taken
 *
 * The crown jewel of Differance DevEx: making ghost exploration feel like
 * opening a gift, not opening a wound.
 *
 * Design Principles (from differance-devex-enlightenment.md):
 * - "Ghosts Are Friends": Possibilities preserved, not regrets
 * - "Generative, Not Archival": What should I do next?
 * - Modal Hell avoidance: Keep exploration inline when possible
 *
 * Features:
 * - Side-by-side comparison: chosen path vs ghost path
 * - Fork & Explore: Create a branch to execute the ghost
 * - Compare Only: See the diff without executing
 * - Clear escape hatch: Cancel at any time
 *
 * ASCII Reference:
 * ```
 * ┌─────────────────────────────────────────────────┐
 * │  Exploring: defer() — "needs more context"      │
 * ├─────────────────────────────────────────────────┤
 * │  ┌──────────────┐    ┌──────────────┐          │
 * │  │ CHOSEN PATH  │ vs │ GHOST PATH   │          │
 * │  │              │    │              │          │
 * │  │ crystallize()│    │ defer()      │          │
 * │  │ → crystal    │    │ → pending    │          │
 * │  │ → committed  │    │ → (explore?) │          │
 * │  └──────────────┘    └──────────────┘          │
 * ├─────────────────────────────────────────────────┤
 * │  [Fork & Explore]  [Compare Only]  [Cancel]     │
 * └─────────────────────────────────────────────────┘
 * ```
 *
 * @see spec/protocols/differance.md
 * @see plans/differance-devex-enlightenment.md - Phase 7C
 */

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  GitBranch,
  GitFork,
  ArrowRight,
  Eye,
  Sparkles,
  AlertTriangle,
  Check,
  Loader2,
} from 'lucide-react';
import { EARTH, GREEN, GLOW } from '@/constants/livingEarth';
import { useCreateBranch, useExploreBranch } from '@/hooks/useDifferanceQuery';
import { Breathe } from '@/components/joy';

// =============================================================================
// Types
// =============================================================================

export interface GhostInfo {
  operation: string;
  inputs: string[];
  reason: string;
  explorable: boolean;
}

export interface ChosenPathInfo {
  traceId: string;
  operation: string;
  output?: unknown;
}

export interface GhostExplorationModalProps {
  /** Is the modal open? */
  isOpen: boolean;
  /** Callback when closed */
  onClose: () => void;
  /** The ghost being explored */
  ghost: GhostInfo | null;
  /** The chosen path that was taken instead */
  chosenPath: ChosenPathInfo | null;
  /** Callback after successful exploration */
  onExplored?: (branchId: string) => void;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Sub-Components
// =============================================================================

interface PathCardProps {
  title: string;
  operation: string;
  subtitle?: string;
  isChosen: boolean;
  output?: unknown;
  inputs?: string[];
}

function PathCard({ title, operation, subtitle, isChosen, output, inputs }: PathCardProps) {
  const bgColor = isChosen ? `${GREEN.sage}20` : `${EARTH.bark}60`;
  const borderColor = isChosen ? GREEN.sage : EARTH.clay;
  const iconColor = isChosen ? GREEN.sprout : EARTH.sand;

  return (
    <div
      className="flex-1 rounded-xl p-4"
      style={{ backgroundColor: bgColor, border: `1px solid ${borderColor}` }}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center"
          style={{
            backgroundColor: isChosen ? `${GREEN.sage}40` : `${EARTH.wood}40`,
            border: `2px ${isChosen ? 'solid' : 'dashed'} ${borderColor}`,
          }}
        >
          {isChosen ? (
            <Check className="w-4 h-4" style={{ color: iconColor }} />
          ) : (
            <GitBranch className="w-4 h-4" style={{ color: iconColor }} />
          )}
        </div>
        <div>
          <div
            className="text-xs font-medium uppercase tracking-wide"
            style={{ color: EARTH.clay }}
          >
            {title}
          </div>
          <div
            className="text-sm font-bold"
            style={{ color: isChosen ? GREEN.sprout : GLOW.lantern }}
          >
            {operation}
          </div>
        </div>
      </div>

      {/* Subtitle/Reason */}
      {subtitle && (
        <div
          className="text-xs italic mb-3 px-2 py-1.5 rounded"
          style={{ backgroundColor: `${EARTH.bark}40`, color: EARTH.sand }}
        >
          {subtitle}
        </div>
      )}

      {/* Inputs */}
      {inputs && inputs.length > 0 && (
        <div className="mb-3">
          <div className="text-[10px] mb-1" style={{ color: EARTH.clay }}>
            INPUTS
          </div>
          <div className="flex flex-wrap gap-1">
            {inputs.map((input, i) => (
              <code
                key={i}
                className="text-[10px] px-1.5 py-0.5 rounded"
                style={{ backgroundColor: `${GREEN.moss}50`, color: GREEN.sprout }}
              >
                {input}
              </code>
            ))}
          </div>
        </div>
      )}

      {/* Output (for chosen path) */}
      {isChosen && output !== undefined && (
        <div>
          <div className="text-[10px] mb-1" style={{ color: EARTH.clay }}>
            OUTPUT
          </div>
          <div
            className="text-xs font-mono px-2 py-1.5 rounded overflow-x-auto"
            style={{ backgroundColor: `${GREEN.moss}30`, color: GLOW.lantern }}
          >
            {typeof output === 'string'
              ? output.slice(0, 100)
              : JSON.stringify(output, null, 0).slice(0, 100)}
            {(typeof output === 'string' ? output.length : JSON.stringify(output).length) > 100 &&
              '...'}
          </div>
        </div>
      )}

      {/* Pending indicator (for ghost path) */}
      {!isChosen && (
        <div className="text-center py-4">
          <div
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs"
            style={{ backgroundColor: `${GLOW.amber}20`, color: GLOW.amber }}
          >
            <Sparkles className="w-3 h-3" />
            <span>Awaiting exploration</span>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function GhostExplorationModal({
  isOpen,
  onClose,
  ghost,
  chosenPath,
  onExplored,
  className = '',
}: GhostExplorationModalProps) {
  const [hypothesis, setHypothesis] = useState('');
  const [mode, setMode] = useState<'compare' | 'fork'>('compare');

  // Branch mutations
  const { mutateAsync: createBranch, isPending: isCreating } = useCreateBranch();
  const { mutateAsync: exploreBranch, isPending: isExploring } = useExploreBranch();

  const isPending = isCreating || isExploring;

  const handleForkAndExplore = useCallback(async () => {
    if (!ghost || !chosenPath) return;

    try {
      // 1. Create branch from the trace point
      const branch = await createBranch({
        from_trace_id: chosenPath.traceId,
        name: `explore-${ghost.operation}`,
        hypothesis:
          hypothesis || `Exploring: ${ghost.operation} instead of ${chosenPath.operation}`,
      });

      // 2. Explore the ghost on that branch
      await exploreBranch({
        ghost_id: `${ghost.operation}:${ghost.inputs.join(',')}`,
        branch_id: branch.branch_id,
      });

      // 3. Notify parent and close
      onExplored?.(branch.branch_id);
      onClose();
    } catch (error) {
      console.error('[GhostExplorationModal] Exploration failed:', error);
    }
  }, [ghost, chosenPath, hypothesis, createBranch, exploreBranch, onExplored, onClose]);

  const handleClose = useCallback(() => {
    if (!isPending) {
      setHypothesis('');
      setMode('compare');
      onClose();
    }
  }, [isPending, onClose]);

  if (!ghost || !chosenPath) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40"
            style={{ backgroundColor: `${EARTH.soil}CC` }}
            onClick={handleClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={`
              fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2
              w-full max-w-2xl max-h-[90vh] overflow-auto
              z-50 rounded-2xl
              ${className}
            `}
            style={{
              backgroundColor: EARTH.soil,
              border: `1px solid ${EARTH.wood}`,
              boxShadow: `0 25px 50px -12px ${EARTH.soil}80`,
            }}
          >
            {/* Header */}
            <div
              className="sticky top-0 z-10 flex items-center justify-between px-5 py-4"
              style={{
                backgroundColor: `${EARTH.bark}F0`,
                borderBottom: `1px solid ${EARTH.wood}`,
              }}
            >
              <div className="flex items-center gap-3">
                <Breathe intensity={0.3} speed="slow">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: `${GLOW.amber}20` }}
                  >
                    <GitFork className="w-5 h-5" style={{ color: GLOW.amber }} />
                  </div>
                </Breathe>
                <div>
                  <h2 className="text-lg font-bold" style={{ color: GLOW.lantern }}>
                    Explore Ghost
                  </h2>
                  <p className="text-xs" style={{ color: EARTH.sand }}>
                    {ghost.operation} — {ghost.reason || 'Road not taken'}
                  </p>
                </div>
              </div>

              <button
                onClick={handleClose}
                disabled={isPending}
                className="p-2 rounded-lg transition-colors disabled:opacity-50"
                style={{ backgroundColor: `${EARTH.bark}60` }}
              >
                <X className="w-5 h-5" style={{ color: EARTH.sand }} />
              </button>
            </div>

            {/* Content */}
            <div className="p-5 space-y-5">
              {/* Comparison view */}
              <div className="flex gap-4 items-stretch">
                <PathCard
                  title="Chosen Path"
                  operation={chosenPath.operation}
                  isChosen={true}
                  output={chosenPath.output}
                />

                {/* Divider */}
                <div className="flex flex-col items-center justify-center gap-1 px-2">
                  <div className="text-[10px] font-medium" style={{ color: EARTH.clay }}>
                    VS
                  </div>
                  <ArrowRight className="w-4 h-4" style={{ color: EARTH.clay }} />
                </div>

                <PathCard
                  title="Ghost Path"
                  operation={ghost.operation}
                  subtitle={ghost.reason}
                  isChosen={false}
                  inputs={ghost.inputs}
                />
              </div>

              {/* Exploration not available warning */}
              {!ghost.explorable && (
                <div
                  className="flex items-start gap-3 px-4 py-3 rounded-lg"
                  style={{
                    backgroundColor: `${GLOW.copper}15`,
                    border: `1px solid ${GLOW.copper}30`,
                  }}
                >
                  <AlertTriangle
                    className="w-5 h-5 flex-shrink-0 mt-0.5"
                    style={{ color: GLOW.copper }}
                  />
                  <div>
                    <div className="text-sm font-medium" style={{ color: GLOW.copper }}>
                      Ghost not explorable
                    </div>
                    <div className="text-xs mt-0.5" style={{ color: EARTH.sand }}>
                      This ghost was marked as non-revisitable. You can compare but not execute.
                    </div>
                  </div>
                </div>
              )}

              {/* Hypothesis input (for fork mode) */}
              {ghost.explorable && mode === 'fork' && (
                <div>
                  <label className="text-xs font-medium mb-1.5 block" style={{ color: EARTH.clay }}>
                    Hypothesis (optional)
                  </label>
                  <input
                    type="text"
                    value={hypothesis}
                    onChange={(e) => setHypothesis(e.target.value)}
                    placeholder="What are you testing by exploring this ghost?"
                    className="w-full px-4 py-2.5 rounded-lg text-sm outline-none transition-colors"
                    style={{
                      backgroundColor: `${EARTH.bark}60`,
                      border: `1px solid ${EARTH.wood}`,
                      color: GLOW.lantern,
                    }}
                    disabled={isPending}
                  />
                </div>
              )}
            </div>

            {/* Footer actions */}
            <div
              className="sticky bottom-0 flex gap-3 px-5 py-4"
              style={{ backgroundColor: `${EARTH.bark}F0`, borderTop: `1px solid ${EARTH.wood}` }}
            >
              {/* Cancel */}
              <button
                onClick={handleClose}
                disabled={isPending}
                className="px-4 py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
                style={{ backgroundColor: `${EARTH.bark}60`, color: EARTH.sand }}
              >
                Cancel
              </button>

              {/* Compare Only */}
              <button
                onClick={() => setMode('compare')}
                disabled={isPending}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                style={{
                  backgroundColor: mode === 'compare' ? `${GREEN.sage}30` : `${EARTH.bark}60`,
                  color: mode === 'compare' ? GREEN.sprout : EARTH.sand,
                }}
              >
                <Eye className="w-4 h-4" />
                Compare Only
              </button>

              {/* Fork & Explore */}
              {ghost.explorable && (
                <button
                  onClick={() => {
                    if (mode === 'fork') {
                      handleForkAndExplore();
                    } else {
                      setMode('fork');
                    }
                  }}
                  disabled={isPending}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  style={{
                    backgroundColor: mode === 'fork' ? `${GLOW.amber}30` : `${EARTH.bark}60`,
                    color: mode === 'fork' ? GLOW.amber : EARTH.sand,
                  }}
                >
                  {isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Exploring...
                    </>
                  ) : (
                    <>
                      <GitFork className="w-4 h-4" />
                      {mode === 'fork' ? 'Confirm Fork' : 'Fork & Explore'}
                    </>
                  )}
                </button>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default GhostExplorationModal;
