/**
 * ProjectRealizationWelcome — Illuminating welcome screen for project derivation coherence
 *
 * Displays the derivation coherence summary when a user opens a project.
 * NOT a gate—the project opens regardless. This illuminates, not enforces.
 *
 * Philosophy:
 *   "Every claim derives from axioms. The welcome screen IS the map."
 *   "Grounded, provisional, orphan—every K-Block has a place in the graph."
 *
 * States:
 * - Scanning: Show spinner and K-Block count
 * - Computing: Show progress bar
 * - Complete: Show full summary with animated numbers
 *
 * @see spec/hypergraph/zero-seed.md
 * @see docs/skills/hypergraph-editor.md
 */

import { memo, useEffect, useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LIVING_EARTH, TIMING, EASING } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export type RealizationState = 'scanning' | 'computing' | 'complete';

export interface CoherenceSummary {
  totalKBlocks: number;
  grounded: number;
  provisional: number;
  orphan: number;
  averageGaloisLoss: number;
  coherencePercent: number;
}

export interface ProjectRealizationWelcomeProps {
  /** Project name to display */
  projectName: string;
  /** Current realization state */
  realizationState: RealizationState;
  /** Progress percentage (0-100) */
  progress: number;
  /** Coherence summary (null until complete) */
  summary: CoherenceSummary | null;
  /** Navigate to full constitutional graph view */
  onViewGraph: () => void;
  /** Filter graph to show only orphan K-Blocks */
  onFocusOrphans: () => void;
  /** Dismiss and continue to project (default action) */
  onContinue: () => void;
}

// =============================================================================
// Constants
// =============================================================================

/** Animation variants for staggered reveal */
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    transition: { duration: TIMING.quick / 1000 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: TIMING.standard / 1000,
      ease: EASING.enter,
    },
  },
};

const summaryItemVariants = {
  hidden: { opacity: 0, x: -10 },
  visible: (custom: number) => ({
    opacity: 1,
    x: 0,
    transition: {
      duration: TIMING.standard / 1000,
      delay: custom * 0.1,
      ease: EASING.enter,
    },
  }),
};

// =============================================================================
// Sub-components
// =============================================================================

interface SpinnerProps {
  size?: number;
}

function Spinner({ size = 20 }: SpinnerProps) {
  return (
    <motion.svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke={LIVING_EARTH.sage}
        strokeWidth="2"
        strokeDasharray="31.4 31.4"
        strokeLinecap="round"
      />
    </motion.svg>
  );
}

interface ProgressBarProps {
  value: number;
}

function ProgressBar({ value }: ProgressBarProps) {
  const clampedValue = Math.max(0, Math.min(100, value));

  return (
    <div className="w-full">
      <div
        className="h-2 rounded-full overflow-hidden"
        style={{ backgroundColor: `${LIVING_EARTH.sage}33` }}
      >
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: LIVING_EARTH.sage }}
          initial={{ width: 0 }}
          animate={{ width: `${clampedValue}%` }}
          transition={{
            duration: TIMING.standard / 1000,
            ease: EASING.standard,
          }}
        />
      </div>
      <div className="text-right text-sm mt-1" style={{ color: LIVING_EARTH.sand }}>
        {Math.round(clampedValue)}%
      </div>
    </div>
  );
}

interface AnimatedNumberProps {
  value: number;
  suffix?: string;
}

function AnimatedNumber({ value, suffix = '' }: AnimatedNumberProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const duration = TIMING.elaborate;
    const startTime = Date.now();
    const startValue = displayValue;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(startValue + (value - startValue) * easeOut);

      setDisplayValue(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
    // Only trigger animation when value changes, not on displayValue changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return (
    <span>
      {displayValue}
      {suffix}
    </span>
  );
}

interface CoherenceBarProps {
  percent: number;
}

function CoherenceBar({ percent }: CoherenceBarProps) {
  const clampedPercent = Math.max(0, Math.min(100, percent));

  return (
    <div className="flex items-center gap-3">
      <div
        className="flex-1 h-3 rounded-full overflow-hidden"
        style={{ backgroundColor: `${LIVING_EARTH.sage}22` }}
      >
        <motion.div
          className="h-full rounded-full"
          style={{
            backgroundColor:
              clampedPercent >= 80
                ? LIVING_EARTH.sage
                : clampedPercent >= 50
                  ? LIVING_EARTH.amber
                  : LIVING_EARTH.copper,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${clampedPercent}%` }}
          transition={{
            duration: TIMING.elaborate / 1000,
            delay: 0.3,
            ease: EASING.standard,
          }}
        />
      </div>
      <span className="text-sm font-medium" style={{ color: LIVING_EARTH.lantern }}>
        <AnimatedNumber value={clampedPercent} suffix="% coherent" />
      </span>
    </div>
  );
}

interface SummaryRowProps {
  icon: string;
  color: string;
  label: string;
  count: number;
  total: number;
  index: number;
}

function SummaryRow({ icon, color, label, count, total, index }: SummaryRowProps) {
  const percent = total > 0 ? Math.round((count / total) * 100) : 0;

  return (
    <motion.div
      className="flex items-center gap-3 py-1"
      variants={summaryItemVariants}
      custom={index}
    >
      <span style={{ color }}>{icon}</span>
      <span style={{ color: LIVING_EARTH.clay }}>{label}:</span>
      <span className="font-medium" style={{ color: LIVING_EARTH.lantern }}>
        <AnimatedNumber value={count} /> K-Blocks
      </span>
      <span className="text-sm" style={{ color: LIVING_EARTH.sand }}>
        ({percent}%)
      </span>
    </motion.div>
  );
}

interface ActionButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

function ActionButton({ onClick, children, variant = 'secondary' }: ActionButtonProps) {
  const isPrimary = variant === 'primary';

  return (
    <motion.button
      className="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      style={{
        backgroundColor: isPrimary ? LIVING_EARTH.sage : 'transparent',
        color: isPrimary ? LIVING_EARTH.lantern : LIVING_EARTH.sand,
        border: isPrimary ? 'none' : `1px solid ${LIVING_EARTH.clay}`,
      }}
      onClick={onClick}
      whileHover={{
        scale: 1.02,
        backgroundColor: isPrimary ? LIVING_EARTH.mint : `${LIVING_EARTH.clay}22`,
      }}
      whileTap={{ scale: 0.98 }}
    >
      {children}
    </motion.button>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export const ProjectRealizationWelcome = memo(function ProjectRealizationWelcome({
  projectName,
  realizationState,
  progress,
  summary,
  onViewGraph,
  onFocusOrphans,
  onContinue,
}: ProjectRealizationWelcomeProps) {
  // Handle keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === 'Escape') {
        e.preventDefault();
        onContinue();
      }
    },
    [onContinue]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Compute display values
  const statusText = useMemo(() => {
    switch (realizationState) {
      case 'scanning':
        return summary
          ? `Scanning K-Blocks... ${summary.totalKBlocks} found`
          : 'Scanning K-Blocks...';
      case 'computing':
        return 'Computing derivation paths...';
      case 'complete':
        return 'Analysis complete';
      default:
        return '';
    }
  }, [realizationState, summary]);

  const isComplete = realizationState === 'complete';
  const hasOrphans = summary && summary.orphan > 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)', backdropFilter: 'blur(4px)' }}
      onClick={onContinue}
    >
      <motion.div
        className="w-full max-w-lg mx-4 rounded-xl overflow-hidden"
        style={{
          backgroundColor: LIVING_EARTH.bark,
          border: `1px solid ${LIVING_EARTH.clay}`,
          boxShadow: `0 24px 48px rgba(0, 0, 0, 0.5)`,
        }}
        onClick={(e) => e.stopPropagation()}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        {/* Header */}
        <motion.div
          className="px-6 py-4 border-b"
          style={{ borderColor: `${LIVING_EARTH.clay}44` }}
          variants={itemVariants}
        >
          <div className="flex items-center gap-2">
            <span style={{ color: LIVING_EARTH.sage }}>&#127793;</span>
            <h2
              className="text-lg font-semibold tracking-wide"
              style={{ color: LIVING_EARTH.lantern }}
            >
              PROJECT REALIZATION: {projectName}
            </h2>
          </div>
        </motion.div>

        {/* Content */}
        <div className="px-6 py-6 space-y-6">
          {/* Status */}
          <motion.div className="flex items-center gap-3" variants={itemVariants}>
            {!isComplete && <Spinner />}
            <span style={{ color: LIVING_EARTH.sand }}>{statusText}</span>
          </motion.div>

          {/* Progress bar (during scanning/computing) */}
          <AnimatePresence mode="wait">
            {!isComplete && (
              <motion.div
                key="progress"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: TIMING.quick / 1000 }}
              >
                <ProgressBar value={progress} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Summary (when complete) */}
          <AnimatePresence mode="wait">
            {isComplete && summary && (
              <motion.div
                key="summary"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: TIMING.standard / 1000 }}
                className="space-y-6"
              >
                {/* Derivation Summary */}
                <motion.div variants={itemVariants}>
                  <h3
                    className="text-sm font-semibold uppercase tracking-wider mb-3"
                    style={{ color: LIVING_EARTH.sand }}
                  >
                    Derivation Summary
                  </h3>
                  <div className="pl-2 space-y-1">
                    <SummaryRow
                      icon="&#9679;"
                      color={LIVING_EARTH.sage}
                      label="Grounded"
                      count={summary.grounded}
                      total={summary.totalKBlocks}
                      index={0}
                    />
                    <SummaryRow
                      icon="&#9679;"
                      color={LIVING_EARTH.amber}
                      label="Provisional"
                      count={summary.provisional}
                      total={summary.totalKBlocks}
                      index={1}
                    />
                    <SummaryRow
                      icon="&#9679;"
                      color={LIVING_EARTH.copper}
                      label="Orphan"
                      count={summary.orphan}
                      total={summary.totalKBlocks}
                      index={2}
                    />
                  </div>
                </motion.div>

                {/* Constitutional Alignment */}
                <motion.div variants={itemVariants}>
                  <h3
                    className="text-sm font-semibold uppercase tracking-wider mb-3"
                    style={{ color: LIVING_EARTH.sand }}
                  >
                    Constitutional Alignment
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span style={{ color: LIVING_EARTH.clay }}>Average Galois Loss:</span>
                      <span className="font-medium" style={{ color: LIVING_EARTH.lantern }}>
                        {summary.averageGaloisLoss.toFixed(2)}
                      </span>
                    </div>
                    <CoherenceBar percent={summary.coherencePercent} />
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Actions */}
          <motion.div className="flex items-center justify-end gap-3 pt-2" variants={itemVariants}>
            {isComplete && (
              <>
                <ActionButton onClick={onViewGraph}>View Full Graph</ActionButton>
                {hasOrphans && (
                  <ActionButton onClick={onFocusOrphans}>Focus on Orphans</ActionButton>
                )}
              </>
            )}
            <ActionButton onClick={onContinue} variant="primary">
              Continue &#8594;
            </ActionButton>
          </motion.div>

          {/* Keyboard hint */}
          <motion.div
            className="text-center text-xs pt-2"
            style={{ color: LIVING_EARTH.clay }}
            variants={itemVariants}
          >
            Press{' '}
            <kbd
              className="px-1.5 py-0.5 rounded mx-1"
              style={{
                backgroundColor: `${LIVING_EARTH.wood}`,
                border: `1px solid ${LIVING_EARTH.clay}`,
              }}
            >
              Enter
            </kbd>{' '}
            or{' '}
            <kbd
              className="px-1.5 py-0.5 rounded mx-1"
              style={{
                backgroundColor: `${LIVING_EARTH.wood}`,
                border: `1px solid ${LIVING_EARTH.clay}`,
              }}
            >
              Esc
            </kbd>{' '}
            to continue
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
});

export default ProjectRealizationWelcome;
