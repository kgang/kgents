/**
 * EvidenceLadder: 7-rung evidence visualization.
 *
 * From spec: "Evidence rungs from L-∞ (orphan) to L3 (bet)."
 *
 * Each rung shows:
 * - Level label (L-∞, L-2, L-1, L0, L1, L2, L3)
 * - Count badge
 * - Fill bar proportional to count
 *
 * @see spec/protocols/witness-assurance-surface.md
 */

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import type { EvidenceLadder as EvidenceLadderType } from '@/api/witness';

// =============================================================================
// Constants
// =============================================================================

const RUNG_COLORS = {
  orphan: { fill: '#EF4444', bg: '#7F1D1D', label: 'Orphan' }, // Red (negative)
  prompt: { fill: '#8B5CF6', bg: '#4C1D95', label: 'Prompt' }, // Purple
  trace: { fill: '#3B82F6', bg: '#1E3A8A', label: 'Trace' }, // Blue
  mark: { fill: '#10B981', bg: '#064E3B', label: 'Mark' }, // Green
  test: { fill: '#14B8A6', bg: '#134E4A', label: 'Test' }, // Teal
  proof: { fill: '#F59E0B', bg: '#78350F', label: 'Proof' }, // Amber
  bet: { fill: '#EC4899', bg: '#831843', label: 'Bet' }, // Pink
} as const;

const LEVEL_LABELS: Record<string, string> = {
  orphan: 'L-∞',
  prompt: 'L-2',
  trace: 'L-1',
  mark: 'L0',
  test: 'L1',
  proof: 'L2',
  bet: 'L3',
};

const RUNG_ORDER = ['bet', 'proof', 'test', 'mark', 'trace', 'prompt', 'orphan'] as const;

// =============================================================================
// Types
// =============================================================================

export interface EvidenceLadderProps {
  /** The evidence ladder data */
  ladder: EvidenceLadderType;
  /** Display mode */
  mode?: 'full' | 'compact' | 'mini';
  /** Callback when a rung is clicked */
  onRungClick?: (level: keyof EvidenceLadderType) => void;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Sub-components
// =============================================================================

interface RungProps {
  level: keyof typeof RUNG_COLORS;
  count: number;
  maxCount: number;
  mode: 'full' | 'compact' | 'mini';
  onClick?: () => void;
  delay?: number;
}

function Rung({ level, count, maxCount, mode, onClick, delay = 0 }: RungProps) {
  const colors = RUNG_COLORS[level];
  const levelLabel = LEVEL_LABELS[level];
  const fillPercent = maxCount > 0 ? (count / maxCount) * 100 : 0;
  const isOrphan = level === 'orphan';

  if (mode === 'mini') {
    return (
      <div
        className="h-2 rounded-sm cursor-pointer hover:brightness-110 transition-all"
        style={{
          backgroundColor: count > 0 ? colors.fill : colors.bg,
          width: `${Math.max(fillPercent, 8)}%`,
          opacity: count > 0 ? 1 : 0.3,
        }}
        title={`${colors.label}: ${count}`}
        onClick={onClick}
      />
    );
  }

  return (
    <motion.div
      className="flex items-center gap-2 cursor-pointer group"
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.2 }}
      onClick={onClick}
    >
      {/* Level label */}
      <span className={`font-mono text-xs w-8 ${isOrphan ? 'text-red-400' : 'text-gray-400'}`}>
        {levelLabel}
      </span>

      {/* Bar */}
      <div
        className="flex-1 h-4 rounded overflow-hidden relative"
        style={{ backgroundColor: colors.bg }}
      >
        <motion.div
          className="h-full rounded"
          style={{ backgroundColor: colors.fill }}
          initial={{ width: 0 }}
          animate={{ width: `${fillPercent}%` }}
          transition={{ delay: delay + 0.1, duration: 0.4, ease: 'easeOut' }}
        />

        {/* Count badge */}
        {mode === 'full' && count > 0 && (
          <span
            className="absolute inset-y-0 right-2 flex items-center text-xs font-medium"
            style={{ color: count > 0 ? '#fff' : colors.fill }}
          >
            {count}
          </span>
        )}
      </div>

      {/* Label (full mode only) */}
      {mode === 'full' && (
        <span
          className="text-xs w-14 text-right group-hover:text-white transition-colors"
          style={{ color: colors.fill }}
        >
          {colors.label}
        </span>
      )}
    </motion.div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function EvidenceLadder({
  ladder,
  mode = 'full',
  onRungClick,
  className = '',
}: EvidenceLadderProps) {
  // Find max count for proportional scaling
  const maxCount = useMemo(() => {
    const counts = [
      ladder.orphan,
      ladder.prompt,
      ladder.trace,
      ladder.mark,
      ladder.test,
      ladder.proof,
      ladder.bet,
    ];
    return Math.max(...counts, 1);
  }, [ladder]);

  // Total evidence (excluding orphans)
  const totalEvidence = useMemo(
    () => ladder.prompt + ladder.trace + ladder.mark + ladder.test + ladder.proof + ladder.bet,
    [ladder]
  );

  if (mode === 'mini') {
    return (
      <div className={`flex flex-col gap-0.5 ${className}`}>
        {RUNG_ORDER.map((level) => (
          <Rung
            key={level}
            level={level}
            count={ladder[level]}
            maxCount={maxCount}
            mode={mode}
            onClick={() => onRungClick?.(level)}
          />
        ))}
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Header */}
      {mode === 'full' && (
        <div className="flex items-center justify-between text-xs text-gray-400 mb-3">
          <span>Evidence Ladder</span>
          <span>
            Total: <span className="text-white">{totalEvidence}</span>
            {ladder.orphan > 0 && (
              <span className="text-red-400 ml-2">
                ({ladder.orphan} orphan{ladder.orphan !== 1 ? 's' : ''})
              </span>
            )}
          </span>
        </div>
      )}

      {/* Rungs (top to bottom: L3 → L-∞) */}
      <div className="space-y-1.5">
        {RUNG_ORDER.map((level, index) => (
          <Rung
            key={level}
            level={level}
            count={ladder[level]}
            maxCount={maxCount}
            mode={mode}
            onClick={() => onRungClick?.(level)}
            delay={index * 0.05}
          />
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default EvidenceLadder;
