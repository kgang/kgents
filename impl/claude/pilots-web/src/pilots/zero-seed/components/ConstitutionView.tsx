/**
 * ConstitutionView - Display personal constitution
 *
 * This component displays the user's personal constitution:
 * - List of axioms with status badges
 * - Actions to retire or suspend axioms
 * - Evolution timeline
 *
 * Design Philosophy (from PROTO_SPEC):
 * - QA-2: Amendment process feels ceremonial but not burdensome
 * - QA-4: After a month, produces a shareable personal constitution
 *
 * Language Guidance:
 * - Use "Your constitution reveals..." not "You should believe..."
 * - Use warm, non-judgmental tone
 * - Frame conflicts as "tensions to explore" not "errors to fix"
 *
 * Anti-Patterns Avoided:
 * - NO amendment theater (bureaucratic ritual)
 * - NO coherence worship (score optimization)
 *
 * @see pilots/zero-seed-personal-governance-lab/PROTO_SPEC.md
 */

import { useState, useCallback } from 'react';
import type { Constitution, ConstitutionalAxiom } from '@kgents/shared-primitives';
import { LIVING_EARTH, useWindowLayout } from '@kgents/shared-primitives';
import { getLossClassification } from '@/api/zero-seed';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionViewProps {
  /** The personal constitution */
  constitution?: Constitution;
  /** Whether constitution is loading */
  isLoading: boolean;
  /** Handler for retiring an axiom */
  onRetireAxiom: (axiomId: string, reason: string) => Promise<void>;
  /** Handler for detecting contradictions */
  onDetectContradictions: () => Promise<void>;
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
 * ConstitutionView
 *
 * Displays the user's personal constitution.
 * Each axiom shows status, loss, and available actions.
 */
export function ConstitutionView({
  constitution,
  isLoading,
  onRetireAxiom,
  onDetectContradictions,
}: ConstitutionViewProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  const [retiringAxiomId, setRetiringAxiomId] = useState<string | null>(null);
  const [retirementReason, setRetirementReason] = useState('');

  // Get axioms as array, sorted by status then loss
  const axioms = constitution
    ? Object.values(constitution.axioms).sort((a, b) => {
        // Active first, then by loss (lower is better)
        if (a.status !== b.status) {
          const statusOrder = { active: 0, suspended: 1, conflicting: 2, retired: 3 };
          return statusOrder[a.status] - statusOrder[b.status];
        }
        return a.loss - b.loss;
      })
    : [];

  const activeAxioms = axioms.filter((a) => a.status === 'active');
  const otherAxioms = axioms.filter((a) => a.status !== 'active');

  // Handle retirement
  const handleRetire = useCallback(
    async (axiomId: string) => {
      if (!retirementReason.trim()) return;

      await onRetireAxiom(axiomId, retirementReason);
      setRetiringAxiomId(null);
      setRetirementReason('');
    },
    [retirementReason, onRetireAxiom]
  );

  // Loading state
  if (isLoading) {
    return (
      <div
        className="flex items-center justify-center py-12"
        style={{ color: LIVING_EARTH.sand }}
      >
        <span className="opacity-60">Loading your constitution...</span>
      </div>
    );
  }

  // Empty state
  if (!constitution || axioms.length === 0) {
    return (
      <div
        className={`${sizes.cardPadding} rounded-lg text-center`}
        style={{
          background: `${LIVING_EARTH.sage}11`,
          border: `1px dashed ${LIVING_EARTH.sage}33`,
        }}
      >
        <h2
          className="font-medium mb-2"
          style={{ color: LIVING_EARTH.lantern }}
        >
          Your Constitution Awaits
        </h2>
        <p
          style={{ color: LIVING_EARTH.sand }}
          className="opacity-70 mb-4"
        >
          You have not added any axioms yet.
          Start by discovering what you believe in the Discovery tab.
        </p>
      </div>
    );
  }

  return (
    <div className={`constitution-view flex flex-col ${sizes.gap}`}>
      {/* Constitution Header */}
      <section
        className={`${sizes.cardPadding} rounded-lg`}
        style={{
          background: `${LIVING_EARTH.amber}11`,
          border: `1px solid ${LIVING_EARTH.amber}22`,
        }}
      >
        <div className="flex justify-between items-start">
          <div>
            <h2
              className="font-medium"
              style={{ color: LIVING_EARTH.lantern }}
            >
              {constitution.name}
            </h2>
            <p
              className="text-sm opacity-70 mt-1"
              style={{ color: LIVING_EARTH.sand }}
            >
              {activeAxioms.length} active axiom{activeAxioms.length !== 1 ? 's' : ''}
              {constitution.average_loss > 0 && (
                <span className="ml-2">
                  Average loss: {(constitution.average_loss * 100).toFixed(1)}%
                </span>
              )}
            </p>
          </div>

          <button
            onClick={onDetectContradictions}
            className={`
              text-sm ${sizes.buttonPadding} rounded-lg
              transition-all duration-150
            `}
            style={{
              background: `${LIVING_EARTH.sage}22`,
              color: LIVING_EARTH.sage,
            }}
          >
            Check Tensions
          </button>
        </div>

        {constitution.contradictions.length > 0 && (
          <div
            className="mt-3 p-2 rounded-lg text-sm"
            style={{
              background: `${LIVING_EARTH.rust}22`,
              color: LIVING_EARTH.rust,
            }}
          >
            {constitution.contradictions.length} tension
            {constitution.contradictions.length !== 1 ? 's' : ''} worth exploring
          </div>
        )}
      </section>

      {/* Active Axioms */}
      {activeAxioms.length > 0 && (
        <section>
          <h3
            className="text-sm font-medium mb-3 opacity-60"
            style={{ color: LIVING_EARTH.sand }}
          >
            Your Core Values
          </h3>
          <div className={`grid ${sizes.gap}`}>
            {activeAxioms.map((axiom) => (
              <ConstitutionalAxiomCard
                key={axiom.id}
                axiom={axiom}
                isRetiring={retiringAxiomId === axiom.id}
                retirementReason={retirementReason}
                onStartRetire={() => setRetiringAxiomId(axiom.id)}
                onCancelRetire={() => {
                  setRetiringAxiomId(null);
                  setRetirementReason('');
                }}
                onRetirementReasonChange={setRetirementReason}
                onConfirmRetire={() => handleRetire(axiom.id)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Other Axioms (retired, suspended, conflicting) */}
      {otherAxioms.length > 0 && (
        <section>
          <h3
            className="text-sm font-medium mb-3 opacity-60"
            style={{ color: LIVING_EARTH.sand }}
          >
            Archived Values
          </h3>
          <div className={`grid ${sizes.gap}`}>
            {otherAxioms.map((axiom) => (
              <ConstitutionalAxiomCard
                key={axiom.id}
                axiom={axiom}
                isRetiring={false}
                retirementReason=""
                onStartRetire={() => {}}
                onCancelRetire={() => {}}
                onRetirementReasonChange={() => {}}
                onConfirmRetire={() => {}}
                isArchived
              />
            ))}
          </div>
        </section>
      )}

      {/* Evolution Timeline (if snapshots exist) */}
      {constitution.snapshots.length > 1 && (
        <section
          className={`${sizes.cardPadding} rounded-lg`}
          style={{
            background: `${LIVING_EARTH.sage}11`,
            border: `1px solid ${LIVING_EARTH.sage}22`,
          }}
        >
          <h3
            className="font-medium mb-3"
            style={{ color: LIVING_EARTH.lantern }}
          >
            Evolution Timeline
          </h3>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {constitution.snapshots.slice(-5).map((snapshot, idx) => (
              <div
                key={snapshot.timestamp}
                className="flex-shrink-0 text-center"
                style={{ minWidth: '80px' }}
              >
                <div
                  className="text-2xl font-bold"
                  style={{ color: LIVING_EARTH.amber }}
                >
                  {snapshot.active_count}
                </div>
                <div
                  className="text-xs opacity-60"
                  style={{ color: LIVING_EARTH.sand }}
                >
                  {idx === constitution.snapshots.length - 1
                    ? 'Now'
                    : new Date(snapshot.timestamp).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Shareable Summary */}
      <footer className="text-center pt-4">
        <p
          className="text-xs opacity-40"
          style={{ color: LIVING_EARTH.sand }}
        >
          Your constitution is a living document. It evolves as you do.
        </p>
      </footer>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface ConstitutionalAxiomCardProps {
  axiom: ConstitutionalAxiom;
  isRetiring: boolean;
  retirementReason: string;
  onStartRetire: () => void;
  onCancelRetire: () => void;
  onRetirementReasonChange: (reason: string) => void;
  onConfirmRetire: () => void;
  isArchived?: boolean;
}

/**
 * ConstitutionalAxiomCard
 *
 * Displays an axiom in the constitution with status and actions.
 */
function ConstitutionalAxiomCard({
  axiom,
  isRetiring,
  retirementReason,
  onStartRetire,
  onCancelRetire,
  onRetirementReasonChange,
  onConfirmRetire,
  isArchived,
}: ConstitutionalAxiomCardProps) {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];
  const classification = getLossClassification(axiom.loss);

  // Status badge colors
  const statusStyles: Record<string, { bg: string; color: string; label: string }> = {
    active: { bg: `${LIVING_EARTH.sage}33`, color: LIVING_EARTH.sage, label: 'Active' },
    suspended: { bg: `${LIVING_EARTH.amber}33`, color: LIVING_EARTH.amber, label: 'Suspended' },
    conflicting: { bg: `${LIVING_EARTH.rust}33`, color: LIVING_EARTH.rust, label: 'In Tension' },
    retired: { bg: `${LIVING_EARTH.sand}33`, color: LIVING_EARTH.sand, label: 'Retired' },
  };

  const status = statusStyles[axiom.status] || statusStyles.active;

  return (
    <div
      className={`${sizes.cardPadding} rounded-lg transition-all`}
      style={{
        background: isArchived ? `${LIVING_EARTH.sage}08` : `${LIVING_EARTH.sage}11`,
        border: `1px solid ${LIVING_EARTH.sage}22`,
        opacity: isArchived ? 0.6 : 1,
      }}
    >
      {/* Header with badges */}
      <div className="flex justify-between items-start mb-2">
        <div className="flex gap-2">
          <span
            className="text-xs px-2 py-1 rounded-full"
            style={{ background: status.bg, color: status.color }}
          >
            {status.label}
          </span>
          <span
            className="text-xs px-2 py-1 rounded-full"
            style={{
              background: `${LIVING_EARTH.amber}22`,
              color: LIVING_EARTH.amber,
            }}
          >
            {classification.label}
          </span>
        </div>
        <span
          className="text-xs opacity-50"
          style={{ color: LIVING_EARTH.sand }}
        >
          Since {new Date(axiom.added_at).toLocaleDateString()}
        </span>
      </div>

      {/* Content */}
      <p
        className="mb-3 leading-relaxed"
        style={{ color: LIVING_EARTH.lantern }}
      >
        {axiom.content}
      </p>

      {/* Conflicts indicator */}
      {axiom.conflicts.length > 0 && (
        <div
          className="text-xs mb-3 opacity-70"
          style={{ color: LIVING_EARTH.rust }}
        >
          Has tension with {axiom.conflicts.length} other axiom
          {axiom.conflicts.length !== 1 ? 's' : ''}
        </div>
      )}

      {/* Retirement reason (if retired) */}
      {axiom.status === 'retired' && axiom.retirement_reason && (
        <div
          className="text-xs mb-3 italic opacity-60"
          style={{ color: LIVING_EARTH.sand }}
        >
          Retired: "{axiom.retirement_reason}"
        </div>
      )}

      {/* Actions (only for active axioms) */}
      {!isArchived && axiom.status === 'active' && (
        <>
          {isRetiring ? (
            <div className="space-y-2">
              <p
                className="text-sm"
                style={{ color: LIVING_EARTH.sand }}
              >
                Why are you retiring this axiom? (This helps you reflect.)
              </p>
              <textarea
                value={retirementReason}
                onChange={(e) => onRetirementReasonChange(e.target.value)}
                placeholder="I'm letting go of this because..."
                rows={2}
                className={`
                  w-full rounded-lg ${sizes.padding}
                  resize-none outline-none
                `}
                style={{
                  background: LIVING_EARTH.bark,
                  color: LIVING_EARTH.lantern,
                  border: `1px solid ${LIVING_EARTH.rust}33`,
                }}
              />
              <div className="flex gap-2 justify-end">
                <button
                  onClick={onCancelRetire}
                  className="text-sm px-3 py-1.5 rounded-lg opacity-60 hover:opacity-100"
                  style={{ color: LIVING_EARTH.sand }}
                >
                  Keep It
                </button>
                <button
                  onClick={onConfirmRetire}
                  disabled={!retirementReason.trim()}
                  className={`
                    text-sm px-3 py-1.5 rounded-lg
                    transition-all duration-150
                    disabled:opacity-50 disabled:cursor-not-allowed
                  `}
                  style={{
                    background: `${LIVING_EARTH.rust}33`,
                    color: LIVING_EARTH.rust,
                  }}
                >
                  Retire
                </button>
              </div>
            </div>
          ) : (
            <div className="flex justify-end">
              <button
                onClick={onStartRetire}
                className="text-xs opacity-40 hover:opacity-70 transition-opacity"
                style={{ color: LIVING_EARTH.rust }}
              >
                Retire this axiom
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ConstitutionView;
