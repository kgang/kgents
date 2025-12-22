/**
 * SuggestionPanel - AI-suggested connections for trail exploration.
 *
 * Visual Trail Graph Session 3: Intelligence
 * Living Earth Aesthetic (Crown Jewels Genesis)
 *
 * "The aesthetic is the structure perceiving itself. Beauty is not revealed—it breathes."
 *
 * Shows AI suggestions for the selected step:
 * - Related trails (semantic similarity)
 * - Suggested files to explore
 * - Inferred edge types
 * - Reasoning prompts
 *
 * "Daring, bold, creative, opinionated but not gaudy" - Voice anchor
 *
 * @see plans/visual-trail-graph-fullstack.md Session 3
 * @see creative/crown-jewels-genesis-moodboard.md
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  getSuggestions,
  type TrailSuggestion,
  type RelatedTrail,
  type SuggestedFile,
  type InferredEdge,
} from '../../api/trail';
import {
  LIVING_EARTH,
  BACKGROUNDS,
  GROWING,
  UNFURLING,
  BREATHING,
  getEdgeColor,
} from './living-earth';

// =============================================================================
// Types
// =============================================================================

export interface SuggestionPanelProps {
  /** Current trail ID */
  trailId: string | null;
  /** Selected step index */
  stepIndex: number | null;
  /** Callback when a suggested file is selected */
  onSelectFile?: (path: string, edgeType: string) => void;
  /** Callback when a related trail is selected */
  onSelectTrail?: (trailId: string) => void;
  /** Optional className */
  className?: string;
}

// =============================================================================
// Sub-components
// =============================================================================

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

function Section({ title, children }: SectionProps) {
  return (
    <motion.div
      className="mb-4 last:mb-0"
      initial={{ opacity: 0, scaleY: 0 }}
      animate={{ opacity: 1, scaleY: 1 }}
      transition={{ duration: UNFURLING.duration, ease: UNFURLING.ease }}
      style={{ transformOrigin: 'top' }}
    >
      <h4 className="text-xs uppercase tracking-wide mb-2" style={{ color: LIVING_EARTH.clay }}>
        {title}
      </h4>
      <div className="space-y-1.5">{children}</div>
    </motion.div>
  );
}

function RelatedTrailItem({ trail, onClick }: { trail: RelatedTrail; onClick?: () => void }) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.01, x: 2 }}
      whileTap={{ scale: 0.99 }}
      className="w-full text-left p-2 rounded transition-colors group"
      style={{
        backgroundColor: 'transparent',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = BACKGROUNDS.hover;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent';
      }}
    >
      <div className="flex justify-between items-center">
        <span className="text-sm truncate transition-colors" style={{ color: LIVING_EARTH.sand }}>
          {trail.name}
        </span>
        <span className="text-xs transition-colors" style={{ color: LIVING_EARTH.clay }}>
          {Math.round(trail.score * 100)}%
        </span>
      </div>
      <div className="text-xs mt-0.5" style={{ color: LIVING_EARTH.wood }}>
        {trail.step_count} steps
      </div>
    </motion.button>
  );
}

function SuggestedFileItem({
  file,
  edge,
  onClick,
}: {
  file: SuggestedFile;
  edge: InferredEdge | undefined;
  onClick?: () => void;
}) {
  const edgeType = edge?.edge_type || 'explores';
  const edgeColor = getEdgeColor(edgeType);

  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.01, x: 2 }}
      whileTap={{ scale: 0.99 }}
      className="w-full text-left p-2 rounded transition-colors group"
      style={{ backgroundColor: 'transparent' }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = BACKGROUNDS.hover;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent';
      }}
    >
      <div className="flex items-center gap-2">
        <span
          className="text-sm truncate transition-colors flex-1"
          style={{ color: LIVING_EARTH.honey }}
        >
          {file.path}
        </span>
        <span
          className="text-xs px-1.5 py-0.5 rounded"
          style={{
            backgroundColor: `${edgeColor}25`,
            color: edgeColor,
            borderWidth: 1,
            borderColor: `${edgeColor}40`,
          }}
        >
          {edgeType}
        </span>
      </div>
      <div className="text-xs mt-0.5 transition-colors" style={{ color: LIVING_EARTH.clay }}>
        {file.reason}
      </div>
    </motion.button>
  );
}

function ReasoningPromptItem({ prompt }: { prompt: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-sm italic pl-3 py-1.5 transition-colors cursor-default"
      style={{
        color: LIVING_EARTH.sand,
        borderLeftWidth: 2,
        borderLeftColor: LIVING_EARTH.wood,
      }}
      whileHover={{
        borderLeftColor: LIVING_EARTH.copper,
        color: LIVING_EARTH.lantern,
      }}
    >
      "{prompt}"
    </motion.div>
  );
}

function LoadingState() {
  return (
    <div className="flex items-center gap-2 py-4">
      <motion.span
        animate={{
          rotate: 360,
          scale: [1, 1.1, 1],
        }}
        transition={{
          rotate: { duration: 2, repeat: Infinity, ease: 'linear' },
          scale: { duration: BREATHING.duration, repeat: Infinity, ease: 'easeInOut' },
        }}
        className="text-lg"
      >
        🌱
      </motion.span>
      <span className="text-sm" style={{ color: LIVING_EARTH.sand }}>
        Growing suggestions...
      </span>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="text-sm italic py-4 text-center" style={{ color: LIVING_EARTH.clay }}>
      Select a step to see AI suggestions
    </div>
  );
}

function NoSuggestionsState() {
  return (
    <div className="text-sm italic py-4 text-center" style={{ color: LIVING_EARTH.clay }}>
      No suggestions for this step
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * SuggestionPanel component.
 *
 * Fetches and displays AI suggestions for the selected trail step.
 */
export function SuggestionPanel({
  trailId,
  stepIndex,
  onSelectFile,
  onSelectTrail,
  className = '',
}: SuggestionPanelProps) {
  const [suggestions, setSuggestions] = useState<TrailSuggestion | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch suggestions when trail/step changes
  useEffect(() => {
    if (!trailId || stepIndex === null) {
      setSuggestions(null);
      return;
    }

    setLoading(true);
    setError(null);

    getSuggestions(trailId, stepIndex)
      .then((result) => {
        setSuggestions(result);
      })
      .catch((err) => {
        setError(err.message || 'Failed to fetch suggestions');
        setSuggestions(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [trailId, stepIndex]);

  // No trail or step selected
  if (!trailId || stepIndex === null) {
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
        <h3
          className="text-sm font-medium mb-3 flex items-center gap-2"
          style={{ color: LIVING_EARTH.sand }}
        >
          <span>AI Suggestions</span>
          <span
            className="text-xs px-1.5 py-0.5 rounded"
            style={{
              backgroundColor: `${LIVING_EARTH.fern}50`,
              color: LIVING_EARTH.sprout,
            }}
          >
            Intelligence
          </span>
        </h3>
        <EmptyState />
      </motion.div>
    );
  }

  // Check if there are any suggestions
  const hasSuggestions =
    suggestions &&
    (suggestions.related_trails.length > 0 ||
      suggestions.suggested_files.length > 0 ||
      suggestions.reasoning_prompts.length > 0);

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
        <h3
          className="text-sm font-medium flex items-center gap-2"
          style={{ color: LIVING_EARTH.sand }}
        >
          <span>AI Suggestions</span>
          {loading && (
            <motion.span
              animate={{ rotate: 360, scale: [1, 1.1, 1] }}
              transition={{
                rotate: { duration: 2, repeat: Infinity, ease: 'linear' },
                scale: { duration: BREATHING.duration, repeat: Infinity },
              }}
              className="text-sm"
            >
              🌱
            </motion.span>
          )}
        </h3>
        <span className="text-xs" style={{ color: LIVING_EARTH.clay }}>
          Step {stepIndex + 1}
        </span>
      </div>

      {/* Content */}
      <div className="p-4 max-h-[400px] overflow-y-auto">
        <AnimatePresence mode="wait">
          {loading && <LoadingState />}

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-sm py-2"
              style={{ color: LIVING_EARTH.warning }}
            >
              {error}
            </motion.div>
          )}

          {!loading && !error && !hasSuggestions && <NoSuggestionsState />}

          {!loading && suggestions && hasSuggestions && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              transition={{ duration: 0.2 }}
            >
              {/* Related Trails */}
              {suggestions.related_trails.length > 0 && (
                <Section title="Related Trails">
                  {suggestions.related_trails.map((trail) => (
                    <RelatedTrailItem
                      key={trail.trail_id}
                      trail={trail}
                      onClick={() => onSelectTrail?.(trail.trail_id)}
                    />
                  ))}
                </Section>
              )}

              {/* Suggested Files */}
              {suggestions.suggested_files.length > 0 && (
                <Section title="Explore Next">
                  {suggestions.suggested_files.map((file, i) => (
                    <SuggestedFileItem
                      key={file.path}
                      file={file}
                      edge={suggestions.inferred_edges[i]}
                      onClick={() =>
                        onSelectFile?.(
                          file.path,
                          suggestions.inferred_edges[i]?.edge_type || 'explores'
                        )
                      }
                    />
                  ))}
                </Section>
              )}

              {/* Reasoning Prompts */}
              {suggestions.reasoning_prompts.length > 0 && (
                <Section title="Questions to Consider">
                  {suggestions.reasoning_prompts.map((prompt, i) => (
                    <ReasoningPromptItem key={i} prompt={prompt} />
                  ))}
                </Section>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

export default SuggestionPanel;
