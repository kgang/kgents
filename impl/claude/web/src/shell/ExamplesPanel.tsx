/**
 * ExamplesPanel - Pre-seeded example invocations for AGENTESE nodes
 *
 * Part of Habitat 2.0: Priority 2 - Habitat Examples
 * Shows one-click buttons for exploring node affordances without
 * needing to know exact arguments.
 *
 * Features:
 * - Play button icon with aspect label
 * - Subtle JSON preview of kwargs if present
 * - Emerald/green action theming
 * - Accessible keyboard navigation
 *
 * @see spec/protocols/habitat-2.0.md
 */

import { memo } from 'react';
import { Play } from 'lucide-react';
import { motion } from 'framer-motion';

// =============================================================================
// Types
// =============================================================================

export interface NodeExample {
  aspect: string;
  kwargs: Record<string, unknown>;
  label: string;
}

export interface ExamplesPanelProps {
  examples: NodeExample[];
  onExampleClick: (example: NodeExample) => void;
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * ExamplesPanel - Renders pre-seeded examples as one-click buttons
 *
 * @example
 * <ExamplesPanel
 *   examples={[
 *     { aspect: "search", kwargs: { query: "Python" }, label: "Search Python" }
 *   ]}
 *   onExampleClick={(ex) => navigate(`/self.memory:${ex.aspect}?${encodeParams(ex.kwargs)}`)}
 * />
 */
export const ExamplesPanel = memo(function ExamplesPanel({
  examples,
  onExampleClick,
  className = '',
}: ExamplesPanelProps) {
  if (!examples || examples.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wide mb-3">
        <Play className="w-3 h-3" />
        Examples
      </div>

      <div className="space-y-2">
        {examples.map((example, idx) => {
          const hasKwargs = Object.keys(example.kwargs).length > 0;
          const kwargsPreview = hasKwargs
            ? JSON.stringify(example.kwargs, null, 2)
            : null;

          return (
            <motion.button
              key={`${example.aspect}-${idx}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => onExampleClick(example)}
              className="
                w-full text-left px-4 py-3 rounded-lg
                bg-emerald-900/20 border border-emerald-800/30
                hover:bg-emerald-900/30 hover:border-emerald-700/50
                active:bg-emerald-900/40
                transition-all duration-150
                group
              "
              aria-label={`Run example: ${example.label}`}
            >
              {/* Header with icon and label */}
              <div className="flex items-center gap-3">
                <div
                  className="
                  p-1.5 rounded bg-emerald-500/20
                  group-hover:bg-emerald-500/30
                  transition-colors
                "
                >
                  <Play className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-emerald-300">
                    {example.label}
                  </div>
                  <div className="text-xs text-gray-500 font-mono mt-0.5">
                    {example.aspect}
                  </div>
                </div>
              </div>

              {/* Kwargs preview (if present) */}
              {kwargsPreview && (
                <div className="mt-2 pt-2 border-t border-emerald-800/20">
                  <pre className="text-xs text-gray-400 font-mono overflow-x-auto">
                    {kwargsPreview}
                  </pre>
                </div>
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
});

export default ExamplesPanel;
