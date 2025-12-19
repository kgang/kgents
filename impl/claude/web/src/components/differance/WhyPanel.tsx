/**
 * WhyPanel — "Why Did This Happen?" Explanation Panel
 *
 * Inline accordion panel showing the lineage and decisions that led to an output.
 * Uses useWhyExplain() hook to fetch explanation data from AGENTESE.
 *
 * Progressive disclosure pattern:
 * - Compact summary (lineage length, decisions, alternatives)
 * - Expandable chosen path with ghosts
 * - Link to full GhostHeritageGraph
 *
 * @see spec/protocols/differance.md
 * @see plans/differance-crown-jewel-wiring.md Phase 6D
 */

import { useState, useCallback } from 'react';
import { ChevronDown, ChevronRight, GitBranch, AlertCircle, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GLOW, EARTH, GREEN } from '@/constants/livingEarth';
import { useWhyExplain, type WhyChosenStep } from '@/hooks/useDifferanceQuery';
import { Breathe } from '@/components/joy';

// =============================================================================
// Types
// =============================================================================

export interface WhyPanelProps {
  /** Output ID to explain */
  outputId: string;
  /** Whether the panel is initially expanded */
  defaultExpanded?: boolean;
  /** Callback when "Explore Heritage" is clicked */
  onExploreHeritage?: (outputId: string) => void;
  /** Compact mode for inline usage */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Sub-Components
// =============================================================================

function StepItem({
  step,
  isLast,
  compact,
}: {
  step: WhyChosenStep;
  isLast: boolean;
  compact?: boolean;
}) {
  const [showGhosts, setShowGhosts] = useState(false);
  const hasGhosts = step.ghosts && step.ghosts.length > 0;

  return (
    <div className="relative">
      {/* Connection line */}
      {!isLast && (
        <div
          className="absolute left-2 top-5 w-px h-full"
          style={{ backgroundColor: GREEN.sage }}
        />
      )}

      {/* Step node */}
      <div className="flex items-start gap-2">
        {/* Dot indicator */}
        <div
          className="w-4 h-4 rounded-full flex-shrink-0 mt-0.5 flex items-center justify-center"
          style={{
            backgroundColor: GREEN.sage,
            boxShadow: `0 0 4px ${GREEN.sprout}40`,
          }}
        >
          <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: GLOW.lantern }} />
        </div>

        {/* Step content */}
        <div className="flex-1 min-w-0 pb-3">
          <div className="flex items-center justify-between gap-2">
            <span
              className={`font-medium truncate ${compact ? 'text-xs' : 'text-sm'}`}
              style={{ color: GLOW.lantern }}
            >
              {step.operation}
            </span>

            {hasGhosts && (
              <button
                onClick={() => setShowGhosts(!showGhosts)}
                className="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded"
                style={{
                  backgroundColor: `${EARTH.wood}50`,
                  color: EARTH.sand,
                }}
              >
                <GitBranch className="w-2.5 h-2.5" />
                <span>{step.ghosts.length}</span>
                {showGhosts ? (
                  <ChevronDown className="w-2.5 h-2.5" />
                ) : (
                  <ChevronRight className="w-2.5 h-2.5" />
                )}
              </button>
            )}
          </div>

          {/* Inputs */}
          {step.inputs.length > 0 && (
            <div
              className={`${compact ? 'text-[10px]' : 'text-xs'} mt-0.5`}
              style={{ color: EARTH.sand }}
            >
              inputs: {step.inputs.slice(0, 2).join(', ')}
              {step.inputs.length > 2 && ` +${step.inputs.length - 2} more`}
            </div>
          )}

          {/* Ghosts (collapsed by default) */}
          <AnimatePresence>
            {showGhosts && hasGhosts && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="mt-2 space-y-1 overflow-hidden"
              >
                {step.ghosts.map((ghost, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 text-[10px] px-2 py-1 rounded"
                    style={{
                      backgroundColor: `${EARTH.bark}60`,
                      borderLeft: `2px dashed ${EARTH.clay}`,
                    }}
                  >
                    <span style={{ color: EARTH.clay }}>⑂</span>
                    <div>
                      <span style={{ color: EARTH.sand }}>{ghost.operation}</span>
                      <span style={{ color: EARTH.clay }}> — {ghost.reason}</span>
                      {ghost.explorable && (
                        <span
                          className="ml-1 px-1 rounded"
                          style={{ backgroundColor: `${GREEN.sage}40`, color: GREEN.sprout }}
                        >
                          explorable
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function WhyPanel({
  outputId,
  defaultExpanded = false,
  onExploreHeritage,
  compact = false,
  className = '',
}: WhyPanelProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  const { data, isLoading, error } = useWhyExplain(outputId, {
    enabled: expanded && !!outputId,
    format: 'full',
  });

  const handleExplore = useCallback(() => {
    onExploreHeritage?.(outputId);
  }, [onExploreHeritage, outputId]);

  // Header stats
  const stats = data
    ? {
        lineage: data.lineage_length,
        decisions: data.decisions_made,
        alternatives: data.alternatives_considered,
      }
    : null;

  const headerPadding = compact ? 'px-3 py-2' : 'px-4 py-3';
  const contentPadding = compact ? 'px-3 py-2' : 'px-4 py-3';

  return (
    <div
      className={`rounded-lg overflow-hidden ${className}`}
      style={{
        backgroundColor: EARTH.soil,
        border: `1px solid ${EARTH.wood}`,
      }}
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className={`w-full flex items-center justify-between ${headerPadding} hover:brightness-110 transition-colors`}
        style={{ backgroundColor: `${EARTH.bark}80` }}
      >
        <div className="flex items-center gap-2">
          <Breathe intensity={0.2} speed="slow">
            <AlertCircle
              className={compact ? 'w-4 h-4' : 'w-5 h-5'}
              style={{ color: GREEN.sprout }}
            />
          </Breathe>
          <span
            className={`font-medium ${compact ? 'text-xs' : 'text-sm'}`}
            style={{ color: GLOW.lantern }}
          >
            Why This?
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Stats preview */}
          {stats && (
            <div className="flex items-center gap-2 text-[10px]" style={{ color: EARTH.sand }}>
              <span>{stats.lineage} steps</span>
              <span>•</span>
              <span>
                {stats.alternatives} alt{stats.alternatives !== 1 ? 's' : ''}
              </span>
            </div>
          )}

          {expanded ? (
            <ChevronDown className="w-4 h-4" style={{ color: EARTH.sand }} />
          ) : (
            <ChevronRight className="w-4 h-4" style={{ color: EARTH.sand }} />
          )}
        </div>
      </button>

      {/* Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className={contentPadding}>
              {/* Loading */}
              {isLoading && (
                <div className="flex items-center gap-2 text-sm" style={{ color: EARTH.sand }}>
                  <Breathe intensity={0.5} speed="fast">
                    <GitBranch className="w-4 h-4" />
                  </Breathe>
                  <span>Tracing lineage...</span>
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="text-sm" style={{ color: GLOW.copper }}>
                  Could not trace lineage: {error.message}
                </div>
              )}

              {/* Data */}
              {data && !isLoading && (
                <>
                  {/* Summary */}
                  {data.summary && (
                    <p
                      className={`${compact ? 'text-xs' : 'text-sm'} mb-3 italic`}
                      style={{ color: GREEN.sprout }}
                    >
                      {data.summary}
                    </p>
                  )}

                  {/* Chosen path steps */}
                  {data.chosen_path && data.chosen_path.length > 0 && (
                    <div className="space-y-0">
                      {data.chosen_path.map((step, i) => (
                        <StepItem
                          key={step.id}
                          step={step}
                          isLast={i === data.chosen_path!.length - 1}
                          compact={compact}
                        />
                      ))}
                    </div>
                  )}

                  {/* No path data */}
                  {(!data.chosen_path || data.chosen_path.length === 0) && (
                    <p className="text-sm" style={{ color: EARTH.sand }}>
                      No lineage recorded for this output.
                    </p>
                  )}

                  {/* Explore full heritage link */}
                  {onExploreHeritage && (
                    <button
                      onClick={handleExplore}
                      className="flex items-center gap-1 mt-3 text-xs hover:underline"
                      style={{ color: GREEN.sprout }}
                    >
                      <ExternalLink className="w-3 h-3" />
                      <span>Explore full heritage graph</span>
                    </button>
                  )}
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default WhyPanel;
