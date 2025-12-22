/**
 * ReasoningPanel - Step-by-step reasoning trace display.
 *
 * Living Earth Aesthetic (Crown Jewels Genesis):
 * "The aesthetic is the structure perceiving itself. Beauty is not revealed—it breathes."
 *
 * Shows the trail steps with their edge types and reasoning annotations.
 * Syncs selection with TrailGraph.
 *
 * Features:
 * - Scrollable step list with warm earth tones
 * - Living Earth edge type badges
 * - LLM reasoning in organic quote style
 * - Selection highlighting with lantern glow
 *
 * @see spec/protocols/trail-protocol.md Section 8
 * @see creative/crown-jewels-genesis-moodboard.md
 */

import { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import type { TrailStep } from '../../api/trail';
import { LIVING_EARTH, BACKGROUNDS, GROWING, getEdgeColor, glowShadow } from './living-earth';

// =============================================================================
// Types
// =============================================================================

interface ReasoningPanelProps {
  /** Trail steps */
  steps: TrailStep[];
  /** Currently selected step index */
  selectedStep: number | null;
  /** Callback when step is selected */
  onSelectStep: (stepIndex: number | null) => void;
  /** Optional title override */
  title?: string;
  /** Optional className */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * ReasoningPanel component.
 *
 * Displays trail steps with reasoning traces in a scrollable list.
 */
export function ReasoningPanel({
  steps,
  selectedStep,
  onSelectStep,
  title = 'Reasoning Trace',
  className = '',
}: ReasoningPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const selectedRef = useRef<HTMLDivElement>(null);

  // Scroll to selected step when it changes
  useEffect(() => {
    if (selectedStep !== null && selectedRef.current && scrollRef.current) {
      selectedRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [selectedStep]);

  // Empty state
  if (steps.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: GROWING.initialScale }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: GROWING.duration, ease: GROWING.ease }}
        className={`rounded-lg p-4 ${className}`}
        style={{
          backgroundColor: BACKGROUNDS.surface,
          borderWidth: 1,
          borderColor: LIVING_EARTH.wood,
        }}
      >
        <h3 className="text-sm font-medium mb-3" style={{ color: LIVING_EARTH.sand }}>
          {title}
        </h3>
        <div className="text-sm italic" style={{ color: LIVING_EARTH.clay }}>
          No steps in trail
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: GROWING.initialScale }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: GROWING.duration, ease: GROWING.ease }}
      className={`rounded-lg overflow-hidden ${className}`}
      style={{
        backgroundColor: BACKGROUNDS.surface,
        borderWidth: 1,
        borderColor: LIVING_EARTH.wood,
      }}
    >
      {/* Header */}
      <div
        className="px-4 py-3 flex items-center justify-between"
        style={{
          borderBottomWidth: 1,
          borderBottomColor: LIVING_EARTH.wood,
        }}
      >
        <h3 className="text-sm font-medium" style={{ color: LIVING_EARTH.sand }}>
          {title}
        </h3>
        <span className="text-xs" style={{ color: LIVING_EARTH.clay }}>
          {steps.length} steps
        </span>
      </div>

      {/* Steps list */}
      <div
        ref={scrollRef}
        className="max-h-[400px] overflow-y-auto scrollbar-thin"
        style={{ scrollbarColor: `${LIVING_EARTH.wood} ${BACKGROUNDS.surface}` }}
      >
        {steps.map((step, index) => {
          const isSelected = selectedStep === index;
          const isLast = index === steps.length - 1;

          return (
            <motion.div
              key={`step-${index}`}
              ref={isSelected ? selectedRef : undefined}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => onSelectStep(isSelected ? null : index)}
              className="px-4 py-3 cursor-pointer transition-colors"
              style={{
                backgroundColor: isSelected ? `${LIVING_EARTH.copper}20` : 'transparent',
                borderLeftWidth: isSelected ? 2 : 0,
                borderLeftColor: LIVING_EARTH.lantern,
                borderBottomWidth: !isLast ? 1 : 0,
                borderBottomColor: `${LIVING_EARTH.wood}50`,
              }}
              whileHover={{
                backgroundColor: isSelected ? `${LIVING_EARTH.copper}25` : BACKGROUNDS.hover,
              }}
            >
              {/* Step header */}
              <div className="flex items-start gap-2">
                {/* Step number */}
                <span
                  className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs"
                  style={{
                    backgroundColor: isSelected ? LIVING_EARTH.copper : LIVING_EARTH.wood,
                    color: LIVING_EARTH.lantern,
                    boxShadow: isSelected ? glowShadow(LIVING_EARTH.lantern, 'subtle') : undefined,
                  }}
                >
                  {index + 1}
                </span>

                {/* Step content */}
                <div className="flex-1 min-w-0">
                  {/* Source path */}
                  <div
                    className="font-medium truncate"
                    style={{ color: isSelected ? LIVING_EARTH.lantern : LIVING_EARTH.sand }}
                  >
                    {getHolonName(step.source_path)}
                  </div>

                  {/* Full path */}
                  <div
                    className="text-xs truncate mt-0.5"
                    style={{ color: LIVING_EARTH.clay }}
                    title={step.source_path}
                  >
                    {step.source_path}
                  </div>

                  {/* Edge badge */}
                  {step.edge && (
                    <div className="flex items-center gap-1.5 mt-2">
                      <EdgeBadge edgeType={step.edge} />
                      <span className="text-xs" style={{ color: LIVING_EARTH.clay }}>
                        {step.destination_paths?.[0]
                          ? `to ${getHolonName(step.destination_paths[0])}`
                          : ''}
                      </span>
                    </div>
                  )}

                  {/* Reasoning annotation */}
                  {step.reasoning && (
                    <div
                      className="mt-2 pl-3"
                      style={{
                        borderLeftWidth: 2,
                        borderLeftColor: LIVING_EARTH.wood,
                      }}
                    >
                      <p
                        className="text-xs italic leading-relaxed"
                        style={{ color: LIVING_EARTH.sand }}
                      >
                        "{step.reasoning}"
                      </p>
                    </div>
                  )}

                  {/* Loop warning */}
                  {step.loop_status !== 'OK' && (
                    <div
                      className="mt-2 flex items-center gap-1 text-xs"
                      style={{ color: LIVING_EARTH.warning }}
                    >
                      <span>Loop detected:</span>
                      <span className="font-medium">{step.loop_status}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Timestamp */}
              {step.created_at && (
                <div className="text-xs mt-2 pl-8" style={{ color: LIVING_EARTH.wood }}>
                  {formatTime(step.created_at)}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface EdgeBadgeProps {
  edgeType: string;
}

function EdgeBadge({ edgeType }: EdgeBadgeProps) {
  const color = getEdgeColor(edgeType);

  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium"
      style={{
        backgroundColor: `${color}25`,
        color,
        borderWidth: 1,
        borderColor: `${color}40`,
      }}
    >
      <span style={{ opacity: 0.7 }}>[</span>
      {edgeType}
      <span style={{ opacity: 0.7 }}>]</span>
    </span>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getHolonName(path: string): string {
  if (path.includes('.')) {
    return path.split('.').pop() || path;
  }
  if (path.includes('/')) {
    return path.split('/').pop() || path;
  }
  return path;
}

function formatTime(isoString: string): string {
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return isoString;
  }
}

export default ReasoningPanel;
