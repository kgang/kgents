/**
 * ReasoningPanel - Step-by-step reasoning trace display.
 *
 * Shows the trail steps with their edge types and reasoning annotations.
 * Syncs selection with TrailGraph.
 *
 * Features:
 * - Scrollable step list
 * - Edge type badges
 * - LLM reasoning in quote style
 * - Selection highlighting
 *
 * @see spec/protocols/trail-protocol.md Section 8
 */

import { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import type { TrailStep } from '../../api/trail';

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
      <div
        className={`bg-gray-800 rounded-lg border border-gray-700 p-4 ${className}`}
      >
        <h3 className="text-sm font-medium text-gray-300 mb-3">{title}</h3>
        <div className="text-sm text-gray-500 italic">No steps in trail</div>
      </div>
    );
  }

  return (
    <div
      className={`bg-gray-800 rounded-lg border border-gray-700 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-300">{title}</h3>
        <span className="text-xs text-gray-500">{steps.length} steps</span>
      </div>

      {/* Steps list */}
      <div
        ref={scrollRef}
        className="max-h-[400px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600"
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
              className={`
                px-4 py-3 cursor-pointer transition-colors
                ${isSelected ? 'bg-blue-900/30 border-l-2 border-blue-500' : 'hover:bg-gray-700/50'}
                ${!isLast ? 'border-b border-gray-700/50' : ''}
              `}
            >
              {/* Step header */}
              <div className="flex items-start gap-2">
                {/* Step number */}
                <span
                  className={`
                    flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs
                    ${isSelected ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-400'}
                  `}
                >
                  {index + 1}
                </span>

                {/* Step content */}
                <div className="flex-1 min-w-0">
                  {/* Source path */}
                  <div className="font-medium text-gray-200 truncate">
                    {getHolonName(step.source_path)}
                  </div>

                  {/* Full path */}
                  <div
                    className="text-xs text-gray-500 truncate mt-0.5"
                    title={step.source_path}
                  >
                    {step.source_path}
                  </div>

                  {/* Edge badge */}
                  {step.edge && (
                    <div className="flex items-center gap-1.5 mt-2">
                      <EdgeBadge edgeType={step.edge} />
                      <span className="text-xs text-gray-400">
                        {step.destination_paths?.[0]
                          ? `to ${getHolonName(step.destination_paths[0])}`
                          : ''}
                      </span>
                    </div>
                  )}

                  {/* Reasoning annotation */}
                  {step.reasoning && (
                    <div className="mt-2 pl-3 border-l-2 border-gray-600">
                      <p className="text-xs text-gray-400 italic leading-relaxed">
                        "{step.reasoning}"
                      </p>
                    </div>
                  )}

                  {/* Loop warning */}
                  {step.loop_status !== 'OK' && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-amber-400">
                      <span>Loop detected:</span>
                      <span className="font-medium">{step.loop_status}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Timestamp */}
              {step.created_at && (
                <div className="text-xs text-gray-600 mt-2 pl-8">
                  {formatTime(step.created_at)}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
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
      style={{ backgroundColor: `${color}20`, color }}
    >
      <span className="opacity-70">[</span>
      {edgeType}
      <span className="opacity-70">]</span>
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

function getEdgeColor(edgeType: string): string {
  const colors: Record<string, string> = {
    imports: '#3b82f6',
    contains: '#f59e0b',
    tests: '#22c55e',
    implements: '#8b5cf6',
    calls: '#ec4899',
    semantic: '#06b6d4',
    similar_to: '#06b6d4',
    type_of: '#8b5cf6',
    pattern: '#f97316',
  };
  return colors[edgeType] || '#6b7280';
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
