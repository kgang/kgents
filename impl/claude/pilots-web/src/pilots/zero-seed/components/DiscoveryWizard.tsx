/**
 * DiscoveryWizard - The axiom discovery experience
 *
 * This component embodies the archaeology metaphor:
 * - We "surface" and "uncover" axioms, not "create" them
 * - Language emphasizes recognition over invention
 * - We found traces of patterns, we don't prescribe beliefs
 *
 * Design Philosophy (from PROTO_SPEC):
 * - QA-1: Value discovery feels like recognition, not invention
 * - QA-5: System never tells you what to value
 *
 * Anti-Patterns Avoided:
 * - NO value imposition
 * - NO coherence worship
 * - NO philosophical gatekeeping
 *
 * Joy Dimension: SURPRISE ("Oh, that's what I actually believe")
 *
 * @see pilots/zero-seed-personal-governance-lab/PROTO_SPEC.md
 */

import { useState, useCallback } from 'react';
import type { DiscoveredAxiom, DiscoveryReport } from '@kgents/shared-primitives';
import { LIVING_EARTH, useWindowLayout } from '@kgents/shared-primitives';
import { getLossClassification } from '@/api/zero-seed';

// =============================================================================
// Types
// =============================================================================

export interface DiscoveryWizardProps {
  /** Discovered axioms from latest discovery run */
  discoveredAxioms: DiscoveredAxiom[];
  /** Latest discovery report with stats */
  discoveryReport?: DiscoveryReport;
  /** Whether discovery is in progress */
  isDiscovering: boolean;
  /** Whether validation is in progress */
  isValidating: boolean;
  /** Handler for discovering axioms from corpus */
  onDiscover: (corpus: string) => Promise<void>;
  /** Handler for validating a custom axiom */
  onValidateCustom: (content: string) => Promise<void>;
  /** Handler for adding an axiom to constitution */
  onAddToConstitution: (axiom: DiscoveredAxiom) => Promise<void>;
  /** Handler for selecting an axiom for detail view */
  onSelectAxiom?: (axiom: DiscoveredAxiom) => void;
}

// =============================================================================
// Density-aware Sizing
// =============================================================================

const SIZES = {
  compact: {
    gap: 'gap-3',
    padding: 'p-3',
    cardPadding: 'p-3',
    textareaRows: 6,
    buttonPadding: 'px-3 py-2',
  },
  comfortable: {
    gap: 'gap-4',
    padding: 'p-4',
    cardPadding: 'p-4',
    textareaRows: 8,
    buttonPadding: 'px-4 py-2.5',
  },
  spacious: {
    gap: 'gap-6',
    padding: 'p-6',
    cardPadding: 'p-5',
    textareaRows: 10,
    buttonPadding: 'px-5 py-3',
  },
} as const;

// =============================================================================
// Component
// =============================================================================

/**
 * DiscoveryWizard
 *
 * The axiom discovery experience. Accepts a corpus of text
 * (journal entries, decisions, reflections) and surfaces
 * patterns that qualify as semantic fixed points.
 *
 * Key language choices:
 * - "Uncovered" not "Created"
 * - "This pattern emerged" not "We recommend"
 * - "We found traces of..." not "You believe..."
 */
export function DiscoveryWizard({
  discoveredAxioms,
  discoveryReport,
  isDiscovering,
  isValidating,
  onDiscover,
  onValidateCustom,
  onAddToConstitution,
  onSelectAxiom,
}: DiscoveryWizardProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  const [corpus, setCorpus] = useState('');
  const [customAxiom, setCustomAxiom] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  // Handle discovery submission
  const handleDiscover = useCallback(async () => {
    if (!corpus.trim() || isDiscovering) return;
    await onDiscover(corpus);
  }, [corpus, isDiscovering, onDiscover]);

  // Handle custom axiom validation
  const handleValidateCustom = useCallback(async () => {
    if (!customAxiom.trim() || isValidating) return;
    await onValidateCustom(customAxiom);
    setCustomAxiom('');
    setShowCustomInput(false);
  }, [customAxiom, isValidating, onValidateCustom]);

  return (
    <div className={`discovery-wizard flex flex-col ${sizes.gap}`}>
      {/* Corpus Input Section */}
      <section
        className={`${sizes.cardPadding} rounded-lg`}
        style={{
          background: `${LIVING_EARTH.sage}11`,
          border: `1px solid ${LIVING_EARTH.sage}22`,
        }}
      >
        <h2
          className="font-medium mb-2"
          style={{ color: LIVING_EARTH.lantern }}
        >
          Share Your Thoughts
        </h2>
        <p
          className="text-sm mb-4 opacity-70"
          style={{ color: LIVING_EARTH.sand }}
        >
          Paste journal entries, past decisions, or reflections.
          We will surface patterns that reveal what you actually value.
        </p>

        <textarea
          value={corpus}
          onChange={(e) => setCorpus(e.target.value)}
          placeholder={`Example entries:

"I chose to stay late because the team was counting on me..."

"I declined the promotion because I value time with my family more than..."

"I felt uncomfortable when they asked me to cut corners..."

The more text you provide, the more patterns we can uncover.`}
          rows={sizes.textareaRows}
          className={`
            w-full rounded-lg ${sizes.padding}
            resize-none outline-none transition-all
            focus:ring-2
          `}
          style={{
            background: LIVING_EARTH.bark,
            color: LIVING_EARTH.lantern,
            border: `1px solid ${LIVING_EARTH.sage}33`,
          }}
          disabled={isDiscovering}
        />

        <div className="flex justify-between items-center mt-4">
          <span
            className="text-xs opacity-50"
            style={{ color: LIVING_EARTH.sand }}
          >
            {corpus.length > 0 && `${corpus.split(/\s+/).filter(Boolean).length} words`}
          </span>

          <button
            onClick={handleDiscover}
            disabled={!corpus.trim() || isDiscovering}
            className={`
              ${sizes.buttonPadding} rounded-lg font-medium
              transition-all duration-150
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
            style={{
              background: LIVING_EARTH.amber,
              color: LIVING_EARTH.bark,
            }}
          >
            {isDiscovering ? 'Discovering...' : 'Discover My Axioms'}
          </button>
        </div>
      </section>

      {/* Discovery Results */}
      {discoveredAxioms.length > 0 && (
        <section className={`flex flex-col ${sizes.gap}`}>
          {/* Results Header */}
          <div className="flex justify-between items-baseline">
            <h2
              className="font-medium"
              style={{ color: LIVING_EARTH.lantern }}
            >
              Patterns Uncovered
            </h2>
            {discoveryReport && (
              <span
                className="text-xs opacity-60"
                style={{ color: LIVING_EARTH.sand }}
              >
                {discoveryReport.patterns_analyzed} patterns analyzed in{' '}
                {(discoveryReport.duration_ms / 1000).toFixed(1)}s
              </span>
            )}
          </div>

          {/* Axiom Cards */}
          <div className={`grid gap-4`}>
            {discoveredAxioms.map((axiom, index) => (
              <AxiomCard
                key={`${axiom.content.slice(0, 20)}-${index}`}
                axiom={axiom}
                onAdd={() => onAddToConstitution(axiom)}
                onSelect={() => onSelectAxiom?.(axiom)}
                isAdding={isValidating}
              />
            ))}
          </div>
        </section>
      )}

      {/* Empty State (after discovery with no results) */}
      {discoveryReport && discoveredAxioms.length === 0 && !isDiscovering && (
        <div
          className={`${sizes.cardPadding} rounded-lg text-center`}
          style={{
            background: `${LIVING_EARTH.sage}11`,
            border: `1px dashed ${LIVING_EARTH.sage}33`,
          }}
        >
          <p style={{ color: LIVING_EARTH.sand }} className="opacity-70">
            No strong patterns emerged yet. Try adding more text,
            especially decisions you have made and why.
          </p>
        </div>
      )}

      {/* Custom Axiom Input */}
      <section>
        {!showCustomInput ? (
          <button
            onClick={() => setShowCustomInput(true)}
            className="text-sm opacity-60 hover:opacity-100 transition-opacity"
            style={{ color: LIVING_EARTH.sage }}
          >
            + I already know something I believe
          </button>
        ) : (
          <div
            className={`${sizes.cardPadding} rounded-lg`}
            style={{
              background: `${LIVING_EARTH.amber}11`,
              border: `1px solid ${LIVING_EARTH.amber}22`,
            }}
          >
            <h3
              className="font-medium mb-2"
              style={{ color: LIVING_EARTH.amber }}
            >
              Test a Belief
            </h3>
            <p
              className="text-sm mb-3 opacity-70"
              style={{ color: LIVING_EARTH.sand }}
            >
              Enter something you believe. We will check if it qualifies as an axiom
              (survives semantic restructuring unchanged).
            </p>

            <textarea
              value={customAxiom}
              onChange={(e) => setCustomAxiom(e.target.value)}
              placeholder="Example: I believe that honesty builds trust over time."
              rows={3}
              className={`
                w-full rounded-lg ${sizes.padding} mb-3
                resize-none outline-none transition-all
                focus:ring-2
              `}
              style={{
                background: LIVING_EARTH.bark,
                color: LIVING_EARTH.lantern,
                border: `1px solid ${LIVING_EARTH.amber}33`,
              }}
              disabled={isValidating}
            />

            <div className="flex gap-2 justify-end">
              <button
                onClick={() => {
                  setShowCustomInput(false);
                  setCustomAxiom('');
                }}
                className={`${sizes.buttonPadding} rounded-lg opacity-60 hover:opacity-100`}
                style={{ color: LIVING_EARTH.sand }}
              >
                Cancel
              </button>
              <button
                onClick={handleValidateCustom}
                disabled={!customAxiom.trim() || isValidating}
                className={`
                  ${sizes.buttonPadding} rounded-lg font-medium
                  transition-all duration-150
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
                style={{
                  background: LIVING_EARTH.amber,
                  color: LIVING_EARTH.bark,
                }}
              >
                {isValidating ? 'Validating...' : 'Test This'}
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Guidance Footer */}
      <footer
        className="text-xs text-center opacity-40 pt-4"
        style={{ color: LIVING_EARTH.sand }}
      >
        These patterns were surfaced from your words.
        We do not suggest what you should believe.
      </footer>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface AxiomCardProps {
  axiom: DiscoveredAxiom;
  onAdd: () => void;
  onSelect?: () => void;
  isAdding: boolean;
}

/**
 * AxiomCard
 *
 * Displays a discovered axiom with:
 * - Content
 * - Loss badge (classification)
 * - Stability indicator
 * - "Add to Constitution" button
 *
 * Language: archaeological, not prescriptive
 */
function AxiomCard({ axiom, onAdd, onSelect, isAdding }: AxiomCardProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];
  const classification = getLossClassification(axiom.loss);

  // Badge colors based on tier
  const badgeStyles = {
    axiom: { bg: `${LIVING_EARTH.amber}33`, color: LIVING_EARTH.amber },
    strong: { bg: `${LIVING_EARTH.sage}33`, color: LIVING_EARTH.sage },
    moderate: { bg: `${LIVING_EARTH.sand}33`, color: LIVING_EARTH.sand },
    weak: { bg: `${LIVING_EARTH.rust}22`, color: LIVING_EARTH.rust },
  };

  const badge = badgeStyles[classification.tier];

  return (
    <div
      className={`${sizes.cardPadding} rounded-lg cursor-pointer transition-all hover:ring-1`}
      style={{
        background: `${LIVING_EARTH.sage}11`,
        border: `1px solid ${LIVING_EARTH.sage}22`,
      }}
      onClick={onSelect}
    >
      {/* Header with badge */}
      <div className="flex justify-between items-start mb-2">
        <span
          className="text-xs px-2 py-1 rounded-full"
          style={{ background: badge.bg, color: badge.color }}
        >
          {classification.label}
        </span>
        <span
          className="text-xs opacity-50"
          style={{ color: LIVING_EARTH.sand }}
        >
          L: {(axiom.loss * 100).toFixed(1)}%
        </span>
      </div>

      {/* Content */}
      <p
        className="mb-3 leading-relaxed"
        style={{ color: LIVING_EARTH.lantern }}
      >
        {axiom.content}
      </p>

      {/* Footer with stability and action */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <StabilityIndicator stability={axiom.stability} />
          <span
            className="text-xs opacity-50"
            style={{ color: LIVING_EARTH.sand }}
          >
            {classification.description}
          </span>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onAdd();
          }}
          disabled={isAdding}
          className={`
            text-sm px-3 py-1.5 rounded-lg font-medium
            transition-all duration-150
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
          style={{
            background: `${LIVING_EARTH.amber}22`,
            color: LIVING_EARTH.amber,
          }}
        >
          {isAdding ? 'Adding...' : 'Add to Constitution'}
        </button>
      </div>
    </div>
  );
}

interface StabilityIndicatorProps {
  stability: number;
}

/**
 * StabilityIndicator
 *
 * Visual indicator of how stable an axiom is across iterations.
 * Lower stability (more variation) = less certain.
 */
function StabilityIndicator({ stability }: StabilityIndicatorProps) {
  // Stability is std dev, so lower is better
  // Convert to a 0-3 scale where 3 is most stable
  const level = stability < 0.05 ? 3 : stability < 0.15 ? 2 : stability < 0.3 ? 1 : 0;

  return (
    <div className="flex gap-0.5" title={`Stability: ${((1 - stability) * 100).toFixed(0)}%`}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="w-1.5 h-3 rounded-sm"
          style={{
            background:
              i < level
                ? LIVING_EARTH.sage
                : `${LIVING_EARTH.sage}33`,
          }}
        />
      ))}
    </div>
  );
}

export default DiscoveryWizard;
