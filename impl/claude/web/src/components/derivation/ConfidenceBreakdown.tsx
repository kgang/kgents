/**
 * ConfidenceBreakdown: Stacked bar visualization of confidence components.
 *
 * Phase 5: Derivation Framework Visualization
 *
 * Shows the three components that contribute to an agent's confidence:
 * - Inherited: From derivation chain (base)
 * - Empirical: From ASHC evidence (capped at 0.2)
 * - Stigmergic: From usage patterns (×0.1)
 *
 * Also shows the tier ceiling and how close the agent is to it.
 *
 * @example
 * ```tsx
 * <ConfidenceBreakdown
 *   data={{
 *     agent_name: "Flux",
 *     inherited_confidence: 0.95,
 *     empirical_confidence: 0.88,
 *     stigmergic_confidence: 0.6,
 *     total_confidence: 0.98,
 *     tier_ceiling: 0.98,
 *     boost: 0.026,
 *     stigmergy_contribution: 0.06,
 *   }}
 * />
 * ```
 */

import { motion } from 'framer-motion';
import type { DerivationConfidenceBreakdown } from '../../api/types';

// =============================================================================
// Types
// =============================================================================

export interface ConfidenceBreakdownProps {
  data: DerivationConfidenceBreakdown;
  className?: string;
  compact?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const COLORS = {
  inherited: '#3b82f6', // blue
  empirical: '#22c55e', // green
  stigmergic: '#f59e0b', // amber
  ceiling: '#ef4444', // red
};

// =============================================================================
// Component
// =============================================================================

export function ConfidenceBreakdown({
  data,
  className = '',
  compact = false,
}: ConfidenceBreakdownProps) {
  const {
    agent_name,
    inherited_confidence,
    empirical_confidence,
    stigmergic_confidence,
    total_confidence,
    tier_ceiling,
    boost,
    stigmergy_contribution,
  } = data;

  // Calculate percentages for the stacked bar
  const inheritedPct = (inherited_confidence / tier_ceiling) * 100;
  const boostPct = (boost / tier_ceiling) * 100;
  const stigmergicPct = (stigmergy_contribution / tier_ceiling) * 100;
  const totalPct = (total_confidence / tier_ceiling) * 100;
  const ceilPct = ((tier_ceiling - total_confidence) / tier_ceiling) * 100;

  if (compact) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className="text-xs text-gray-400">{agent_name}</div>
        <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full"
            style={{
              width: `${totalPct}%`,
              background: `linear-gradient(to right, ${COLORS.inherited} ${inheritedPct}%, ${COLORS.empirical} ${inheritedPct + boostPct}%, ${COLORS.stigmergic} 100%)`,
            }}
            initial={{ width: 0 }}
            animate={{ width: `${totalPct}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        <div className="text-xs font-mono text-gray-300">
          {Math.round(total_confidence * 100)}%
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gray-900 rounded-lg p-4 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-white">{agent_name}</h3>
        <span className="text-2xl font-bold text-white">
          {Math.round(total_confidence * 100)}%
        </span>
      </div>

      {/* Stacked bar */}
      <div className="relative h-8 bg-gray-800 rounded-full overflow-hidden mb-4">
        {/* Inherited base */}
        <motion.div
          className="absolute h-full left-0"
          style={{
            width: `${inheritedPct}%`,
            backgroundColor: COLORS.inherited,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${inheritedPct}%` }}
          transition={{ duration: 0.5 }}
        />

        {/* Empirical boost */}
        <motion.div
          className="absolute h-full"
          style={{
            left: `${inheritedPct}%`,
            width: `${boostPct}%`,
            backgroundColor: COLORS.empirical,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${boostPct}%` }}
          transition={{ duration: 0.5, delay: 0.2 }}
        />

        {/* Stigmergic contribution */}
        <motion.div
          className="absolute h-full"
          style={{
            left: `${inheritedPct + boostPct}%`,
            width: `${stigmergicPct}%`,
            backgroundColor: COLORS.stigmergic,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${stigmergicPct}%` }}
          transition={{ duration: 0.5, delay: 0.4 }}
        />

        {/* Remaining to ceiling */}
        {ceilPct > 0.5 && (
          <motion.div
            className="absolute h-full right-0 opacity-30"
            style={{
              width: `${ceilPct}%`,
              backgroundColor: COLORS.ceiling,
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.3 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          />
        )}

        {/* Ceiling marker */}
        <div
          className="absolute h-full w-0.5 bg-red-500"
          style={{ right: 0 }}
          title={`Tier ceiling: ${Math.round(tier_ceiling * 100)}%`}
        />
      </div>

      {/* Legend / breakdown */}
      <div className="space-y-2 text-xs">
        <div className="flex justify-between">
          <span className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded"
              style={{ backgroundColor: COLORS.inherited }}
            />
            Inherited
          </span>
          <span className="font-mono text-gray-300">
            {inherited_confidence.toFixed(3)}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded"
              style={{ backgroundColor: COLORS.empirical }}
            />
            Empirical (ASHC boost)
          </span>
          <span className="font-mono text-gray-300">
            +{boost.toFixed(3)}
            <span className="text-gray-500 ml-1">
              (from {empirical_confidence.toFixed(2)})
            </span>
          </span>
        </div>

        <div className="flex justify-between">
          <span className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded"
              style={{ backgroundColor: COLORS.stigmergic }}
            />
            Stigmergic (usage)
          </span>
          <span className="font-mono text-gray-300">
            +{stigmergy_contribution.toFixed(3)}
            <span className="text-gray-500 ml-1">
              (from {stigmergic_confidence.toFixed(2)})
            </span>
          </span>
        </div>

        <div className="flex justify-between pt-2 border-t border-gray-700">
          <span className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded border border-red-500"
              style={{ backgroundColor: 'transparent' }}
            />
            Tier ceiling
          </span>
          <span className="font-mono text-gray-300">
            {tier_ceiling.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Formula */}
      <div className="mt-4 p-2 bg-gray-800 rounded text-xs font-mono text-gray-400">
        <code>
          total = base + min(0.2, empirical×0.3) + stigmergic×0.1
        </code>
      </div>
    </div>
  );
}

export default ConfidenceBreakdown;
