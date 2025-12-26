/**
 * ContradictionExplorer - Surface and explore value tensions
 *
 * This component surfaces contradictions between axioms:
 * - Shows pairs of axioms that have super-additive loss
 * - Provides synthesis hints from ghost alternatives
 * - Allows user to explore, accept, or synthesize tensions
 *
 * Design Philosophy (from PROTO_SPEC):
 * - QA-3: Contradiction surfacing feels clarifying, not judgmental
 *
 * Language Guidance:
 * - "These patterns seem to pull in different directions"
 * - "Would you like to explore this tension?"
 * - NEVER: "You have conflicting values" (sounds judgmental)
 *
 * Anti-Patterns Avoided:
 * - NO contradiction shame (feeling bad about conflicts)
 * - NO coherence worship (optimizing Galois score)
 *
 * @see pilots/zero-seed-personal-governance-lab/PROTO_SPEC.md
 */

import { useState, useCallback } from 'react';
import type {
  Constitution,
  ConstitutionContradiction,
} from '@kgents/shared-primitives';
import { LIVING_EARTH, useWindowLayout } from '@kgents/shared-primitives';
import { getContradictionDescription } from '@/api/zero-seed';

// =============================================================================
// Types
// =============================================================================

export interface ContradictionExplorerProps {
  /** Detected contradictions */
  contradictions: ConstitutionContradiction[];
  /** The personal constitution (for axiom lookup) */
  constitution?: Constitution;
  /** Handler for detecting contradictions */
  onDetect: () => Promise<void>;
}

// =============================================================================
// Density-aware Sizing
// =============================================================================

const SIZES = {
  compact: {
    gap: 'gap-3',
    padding: 'p-3',
    cardPadding: 'p-3',
    buttonPadding: 'px-3 py-2',
  },
  comfortable: {
    gap: 'gap-4',
    padding: 'p-4',
    cardPadding: 'p-4',
    buttonPadding: 'px-4 py-2.5',
  },
  spacious: {
    gap: 'gap-6',
    padding: 'p-6',
    cardPadding: 'p-5',
    buttonPadding: 'px-5 py-3',
  },
} as const;

// =============================================================================
// Component
// =============================================================================

/**
 * ContradictionExplorer
 *
 * Surfaces and explores value tensions in the constitution.
 * Uses clarifying, non-judgmental language throughout.
 */
export function ContradictionExplorer({
  contradictions,
  constitution,
  onDetect,
}: ContradictionExplorerProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  const [isDetecting, setIsDetecting] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Handle detecting contradictions
  const handleDetect = useCallback(async () => {
    setIsDetecting(true);
    try {
      await onDetect();
    } finally {
      setIsDetecting(false);
    }
  }, [onDetect]);

  // Toggle expanded contradiction
  const toggleExpanded = useCallback((id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  }, []);

  // No constitution yet
  if (!constitution) {
    return (
      <div
        className={`${sizes.cardPadding} rounded-lg text-center`}
        style={{
          background: `${LIVING_EARTH.sage}11`,
          border: `1px dashed ${LIVING_EARTH.sage}33`,
        }}
      >
        <p style={{ color: LIVING_EARTH.sand }} className="opacity-70">
          Add some axioms to your constitution first,
          then we can explore any tensions between them.
        </p>
      </div>
    );
  }

  // Active axiom count
  const activeCount = constitution.active_count;

  // Empty state (no contradictions)
  if (contradictions.length === 0) {
    return (
      <div className={`flex flex-col ${sizes.gap}`}>
        <div
          className={`${sizes.cardPadding} rounded-lg text-center`}
          style={{
            background: `${LIVING_EARTH.sage}11`,
            border: `1px solid ${LIVING_EARTH.sage}22`,
          }}
        >
          <h2
            className="font-medium mb-2"
            style={{ color: LIVING_EARTH.lantern }}
          >
            No Tensions Found
          </h2>
          <p
            style={{ color: LIVING_EARTH.sand }}
            className="opacity-70 mb-4"
          >
            {activeCount < 2
              ? 'Add more axioms to check for tensions between them.'
              : 'Your current axioms appear to coexist harmoniously.'}
          </p>

          {activeCount >= 2 && (
            <button
              onClick={handleDetect}
              disabled={isDetecting}
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
              {isDetecting ? 'Checking...' : 'Check Again'}
            </button>
          )}
        </div>

        <footer className="text-center">
          <p
            className="text-xs opacity-40"
            style={{ color: LIVING_EARTH.sand }}
          >
            Tensions are natural. They often reveal productive complexity in your values.
          </p>
        </footer>
      </div>
    );
  }

  return (
    <div className={`contradiction-explorer flex flex-col ${sizes.gap}`}>
      {/* Header */}
      <div className="flex justify-between items-baseline">
        <div>
          <h2
            className="font-medium"
            style={{ color: LIVING_EARTH.lantern }}
          >
            Value Tensions
          </h2>
          <p
            className="text-sm opacity-70 mt-1"
            style={{ color: LIVING_EARTH.sand }}
          >
            These patterns seem to pull in different directions.
            This is normal and often productive.
          </p>
        </div>

        <button
          onClick={handleDetect}
          disabled={isDetecting}
          className={`
            text-sm ${sizes.buttonPadding} rounded-lg
            transition-all duration-150
            disabled:opacity-50
          `}
          style={{
            background: `${LIVING_EARTH.sage}22`,
            color: LIVING_EARTH.sage,
          }}
        >
          {isDetecting ? 'Checking...' : 'Refresh'}
        </button>
      </div>

      {/* Contradiction Cards */}
      <div className={`grid ${sizes.gap}`}>
        {contradictions.map((contradiction, index) => (
          <ContradictionCard
            key={`${contradiction.axiom_a_id}-${contradiction.axiom_b_id}`}
            contradiction={contradiction}
            index={index + 1}
            isExpanded={expandedId === `${contradiction.axiom_a_id}-${contradiction.axiom_b_id}`}
            onToggle={() =>
              toggleExpanded(`${contradiction.axiom_a_id}-${contradiction.axiom_b_id}`)
            }
          />
        ))}
      </div>

      {/* Footer */}
      <footer className="text-center pt-4">
        <p
          className="text-xs opacity-40"
          style={{ color: LIVING_EARTH.sand }}
        >
          Having tensions between values is human.
          You can explore them, accept them, or find a synthesis.
        </p>
      </footer>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface ContradictionCardProps {
  contradiction: ConstitutionContradiction;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}

/**
 * ContradictionCard
 *
 * Displays a single contradiction with:
 * - Both axiom contents
 * - Tension strength indicator
 * - Synthesis hint (if available)
 * - Actions to explore or accept
 *
 * Language: clarifying, not judgmental
 */
function ContradictionCard({
  contradiction,
  index,
  isExpanded,
  onToggle,
}: ContradictionCardProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];
  const description = getContradictionDescription(contradiction.type);

  // Strength indicator colors
  const strengthStyles = {
    strong: { bg: LIVING_EARTH.rust, width: '100%' },
    moderate: { bg: LIVING_EARTH.amber, width: '66%' },
    weak: { bg: LIVING_EARTH.sage, width: '33%' },
    none: { bg: LIVING_EARTH.sand, width: '10%' },
  };

  const strength = strengthStyles[contradiction.type] || strengthStyles.none;

  return (
    <div
      className={`${sizes.cardPadding} rounded-lg cursor-pointer transition-all`}
      style={{
        background: `${LIVING_EARTH.rust}08`,
        border: `1px solid ${LIVING_EARTH.rust}22`,
      }}
      onClick={onToggle}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <span
          className="text-sm font-medium opacity-60"
          style={{ color: LIVING_EARTH.sand }}
        >
          Tension {index}
        </span>

        {/* Strength indicator */}
        <div className="flex items-center gap-2">
          <span
            className="text-xs opacity-60"
            style={{ color: LIVING_EARTH.sand }}
          >
            {contradiction.type.charAt(0).toUpperCase() + contradiction.type.slice(1)}
          </span>
          <div
            className="w-16 h-1.5 rounded-full overflow-hidden"
            style={{ background: `${LIVING_EARTH.rust}22` }}
          >
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: strength.width,
                background: strength.bg,
              }}
            />
          </div>
        </div>
      </div>

      {/* Axiom pair */}
      <div className="space-y-3">
        <div
          className={`${sizes.padding} rounded-lg`}
          style={{
            background: `${LIVING_EARTH.sage}11`,
            border: `1px solid ${LIVING_EARTH.sage}22`,
          }}
        >
          <p style={{ color: LIVING_EARTH.lantern }}>
            {contradiction.axiom_a_content}
          </p>
        </div>

        {/* Tension indicator */}
        <div className="flex items-center justify-center gap-2">
          <div
            className="w-8 h-px"
            style={{ background: `${LIVING_EARTH.rust}44` }}
          />
          <span
            className="text-xs px-2 py-1 rounded-full"
            style={{
              background: `${LIVING_EARTH.rust}22`,
              color: LIVING_EARTH.rust,
            }}
          >
            tension
          </span>
          <div
            className="w-8 h-px"
            style={{ background: `${LIVING_EARTH.rust}44` }}
          />
        </div>

        <div
          className={`${sizes.padding} rounded-lg`}
          style={{
            background: `${LIVING_EARTH.sage}11`,
            border: `1px solid ${LIVING_EARTH.sage}22`,
          }}
        >
          <p style={{ color: LIVING_EARTH.lantern }}>
            {contradiction.axiom_b_content}
          </p>
        </div>
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t" style={{ borderColor: `${LIVING_EARTH.rust}22` }}>
          {/* Description */}
          <p
            className="text-sm mb-3"
            style={{ color: LIVING_EARTH.sand }}
          >
            {description}
          </p>

          {/* Synthesis hint (if available) */}
          {contradiction.synthesis_hint && (
            <div
              className={`${sizes.padding} rounded-lg mb-4`}
              style={{
                background: `${LIVING_EARTH.amber}11`,
                border: `1px solid ${LIVING_EARTH.amber}22`,
              }}
            >
              <p
                className="text-xs font-medium mb-1"
                style={{ color: LIVING_EARTH.amber }}
              >
                Possible Synthesis
              </p>
              <p
                className="text-sm"
                style={{ color: LIVING_EARTH.lantern }}
              >
                {contradiction.synthesis_hint}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 justify-end">
            <ActionButton
              label="Accept Tension"
              description="These values can coexist in tension"
              variant="subtle"
            />
            <ActionButton
              label="Explore"
              description="Reflect on this tension more deeply"
              variant="primary"
            />
          </div>
        </div>
      )}

      {/* Expand indicator */}
      {!isExpanded && (
        <p
          className="text-xs text-center mt-3 opacity-50"
          style={{ color: LIVING_EARTH.sand }}
        >
          Click to explore this tension
        </p>
      )}
    </div>
  );
}

interface ActionButtonProps {
  label: string;
  description: string;
  variant: 'primary' | 'subtle';
  onClick?: () => void;
}

/**
 * ActionButton
 *
 * Button with tooltip-style description.
 */
function ActionButton({ label, description, variant, onClick }: ActionButtonProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  const styles =
    variant === 'primary'
      ? {
          background: `${LIVING_EARTH.amber}22`,
          color: LIVING_EARTH.amber,
        }
      : {
          background: `${LIVING_EARTH.sage}22`,
          color: LIVING_EARTH.sage,
        };

  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        onClick?.();
      }}
      className={`
        text-sm ${sizes.buttonPadding} rounded-lg
        transition-all duration-150
        hover:opacity-80
      `}
      style={styles}
      title={description}
    >
      {label}
    </button>
  );
}

export default ContradictionExplorer;
