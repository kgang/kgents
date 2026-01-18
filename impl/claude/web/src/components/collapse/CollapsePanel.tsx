/**
 * CollapsePanel — Shows collapsing function results
 *
 * Grounded in: spec/ui/axioms.md — A2 (Sloppification), A8 (Understandability)
 *
 * Four collapsing functions:
 * - TypeScript → Binary (compiles?)
 * - Tests → Binary (passes?)
 * - Constitution → Score (0-7)
 * - Galois → Loss (0-1)
 *
 * These make AI capabilities graspable.
 */

import type {
  CollapseState,
  CollapseResult,
  ConstitutionalCollapse,
  GaloisCollapse,
  SlopLevel,
} from '../../types';
import {
  COLLAPSE_COLORS,
  COLLAPSE_ICONS,
  GALOIS_TIER_COLORS,
  SLOP_COLORS,
  formatCollapseResult,
  formatGaloisLoss,
  formatConstitutionalScore,
} from '../../types';

interface CollapsePanelProps {
  /** Current collapse state */
  state: CollapseState;

  /** Compact mode (less detail) */
  compact?: boolean;
}

/**
 * Panel showing all four collapsing functions.
 */
export function CollapsePanel({ state, compact = false }: CollapsePanelProps) {
  return (
    <div className="collapse-panel panel-severe">
      <h3 className="text-xs text-secondary">COLLAPSE</h3>

      {/* Binary functions */}
      <CollapseBar label="TypeScript" result={state.typescript} />
      <CollapseBar label="Tests" result={state.tests} />

      {/* Constitutional score */}
      <ConstitutionalBar constitution={state.constitution} compact={compact} />

      {/* Galois loss */}
      <GaloisBar galois={state.galois} />

      {/* Overall assessment */}
      <SlopAssessment level={state.overallSlop} evidence={state.evidence} />
    </div>
  );
}

/**
 * Bar for binary collapse results.
 */
function CollapseBar({ label, result }: { label: string; result: CollapseResult }) {
  const color = COLLAPSE_COLORS[result.status];
  const icon = COLLAPSE_ICONS[result.status];
  const text = formatCollapseResult(result);

  return (
    <div className="collapse-bar">
      <span className="collapse-bar__label text-xs">{label}:</span>
      <span className="collapse-bar__value" style={{ color }}>
        {icon} {text}
      </span>
    </div>
  );
}

/**
 * Bar for constitutional score.
 */
function ConstitutionalBar({
  constitution,
  compact,
}: {
  constitution: ConstitutionalCollapse;
  compact: boolean;
}) {
  const normalizedScore = constitution.score / 7; // 0-1
  const barWidth = `${normalizedScore * 100}%`;
  const color =
    normalizedScore >= 0.8
      ? 'var(--collapse-pass)'
      : normalizedScore >= 0.6
        ? 'var(--collapse-partial)'
        : 'var(--collapse-fail)';

  return (
    <div className="collapse-bar collapse-bar--constitutional">
      <span className="collapse-bar__label text-xs">Constitution:</span>
      <div className="collapse-bar__track">
        <div className="collapse-bar__fill" style={{ width: barWidth, backgroundColor: color }} />
      </div>
      <span className="collapse-bar__value" style={{ color }}>
        {formatConstitutionalScore(constitution)}
      </span>
      {!compact && constitution.weakest && (
        <span className="collapse-bar__hint text-xs text-muted">weak: {constitution.weakest}</span>
      )}
    </div>
  );
}

/**
 * Bar for Galois loss.
 */
function GaloisBar({ galois }: { galois: GaloisCollapse }) {
  const color = GALOIS_TIER_COLORS[galois.tier];
  const barWidth = `${(1 - galois.loss) * 100}%`; // Invert: low loss = more bar

  return (
    <div className="collapse-bar collapse-bar--galois">
      <span className="collapse-bar__label text-xs">Galois:</span>
      <div className="collapse-bar__track">
        <div className="collapse-bar__fill" style={{ width: barWidth, backgroundColor: color }} />
      </div>
      <span className="collapse-bar__value" style={{ color }}>
        {formatGaloisLoss(galois)}
      </span>
    </div>
  );
}

/**
 * Overall sloppification assessment.
 */
function SlopAssessment({ level, evidence }: { level: SlopLevel; evidence: string[] }) {
  const color = SLOP_COLORS[level];
  const label = level.toUpperCase();

  return (
    <div className="collapse-assessment">
      <div className="collapse-assessment__header">
        <span className="text-xs text-secondary">SLOP:</span>
        <span className="collapse-assessment__level" style={{ color }}>
          {label}
        </span>
      </div>
      {evidence.length > 0 && (
        <div className="collapse-assessment__evidence text-xs text-muted">
          {evidence.slice(0, 2).join(' • ')}
        </div>
      )}
    </div>
  );
}

/**
 * Compact collapse indicator for status line.
 */
export function CollapseIndicator({ state }: { state: CollapseState }) {
  const color = SLOP_COLORS[state.overallSlop];

  return (
    <span className="collapse-indicator" style={{ color }}>
      slop:{state.overallSlop}
    </span>
  );
}

export default CollapsePanel;
