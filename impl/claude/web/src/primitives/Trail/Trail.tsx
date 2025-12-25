/**
 * Trail — Derivation breadcrumb with PolicyTrace compression ratios
 *
 * "The proof IS the decision. The mark IS the witness."
 *
 * A horizontal breadcrumb component showing the semantic journey through
 * a derivation path. Unlike file paths, this shows the epistemic trajectory
 * with optional principle scores and compression metrics from PolicyTrace.
 *
 * Replaces:
 * - DerivationTrail.tsx (breadcrumb aspect)
 * - FocalDistanceRuler.tsx (principle indicators)
 * - BranchTree.tsx breadcrumbs (path navigation)
 *
 * @see spec/protocols/zero-seed.md (PolicyTrace compression)
 */

import { memo, useCallback } from 'react';
import type { ConstitutionScores } from '../../types/theory';
import './Trail.css';

// =============================================================================
// Types
// =============================================================================

export interface TrailProps {
  /** Navigation path as array of step IDs or names */
  path: string[];

  /** Compression ratio from PolicyTrace (0-1) */
  compressionRatio?: number;

  /** Show principle scores at each step */
  showPrinciples?: boolean;

  /** Principle scores per step (if showPrinciples=true) */
  principleScores?: ConstitutionScores[];

  /** Click handler for path steps */
  onStepClick?: (stepIndex: number, stepId: string) => void;

  /** Maximum visible steps before collapsing */
  maxVisible?: number;

  /** Compact mode (single line, minimal labels) */
  compact?: boolean;

  /** Current step index (highlights as active) */
  currentIndex?: number;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_MAX_VISIBLE = 7;
const PRINCIPLES: (keyof ConstitutionScores)[] = [
  'tasteful',
  'curated',
  'ethical',
  'joyInducing',
  'composable',
  'heterarchical',
  'generative',
];

// =============================================================================
// Component
// =============================================================================

export const Trail = memo(function Trail({
  path,
  compressionRatio,
  showPrinciples = false,
  principleScores,
  onStepClick,
  maxVisible = DEFAULT_MAX_VISIBLE,
  compact = false,
  currentIndex,
}: TrailProps) {
  const handleStepClick = useCallback(
    (index: number, stepId: string) => {
      onStepClick?.(index, stepId);
    },
    [onStepClick]
  );

  // Compute visible path (collapse middle if too long)
  const visiblePath = computeVisiblePath(path, maxVisible);
  const currentStep = currentIndex ?? path.length - 1;

  if (path.length === 0) {
    return null;
  }

  return (
    <nav
      className={`trail ${compact ? 'trail--compact' : ''}`}
      aria-label="Derivation trail"
    >
      {/* Compression indicator */}
      {compressionRatio !== undefined && !compact && (
        <div className="trail__compression" title="PolicyTrace compression ratio">
          <span className="trail__compression-icon">⊕</span>
          <span className="trail__compression-value">
            {Math.round(compressionRatio * 100)}%
          </span>
        </div>
      )}

      {/* Breadcrumb steps */}
      <ol className="trail__steps">
        {visiblePath.map((item, idx) => {
          if (item.type === 'ellipsis') {
            return (
              <li key={`ellipsis-${idx}`} className="trail__step trail__step--ellipsis">
                <span className="trail__ellipsis" aria-hidden="true">
                  …
                </span>
              </li>
            );
          }

          const stepIndex = item.index!;
          const stepId = item.value!;
          const isCurrent = stepIndex === currentStep;
          const isClickable = onStepClick !== undefined && !isCurrent;

          return (
            <li
              key={`${stepId}-${stepIndex}`}
              className={`trail__step ${isCurrent ? 'trail__step--current' : ''}`}
            >
              {/* Step button/label */}
              {isClickable ? (
                <button
                  className="trail__link"
                  onClick={() => handleStepClick(stepIndex, stepId)}
                  title={formatStepTitle(stepId, stepIndex)}
                  aria-label={`Navigate to step ${stepIndex + 1}: ${stepId}`}
                >
                  <span className="trail__step-label">
                    {formatStepLabel(stepId, compact)}
                  </span>
                </button>
              ) : (
                <span className="trail__current-label" aria-current="location">
                  {formatStepLabel(stepId, compact)}
                </span>
              )}

              {/* Principle indicators (if enabled and scores provided) */}
              {showPrinciples &&
                principleScores &&
                principleScores[stepIndex] &&
                !compact && (
                  <div className="trail__principles">
                    {PRINCIPLES.map((key) => {
                      const score = principleScores[stepIndex][key];
                      return (
                        <span
                          key={key}
                          className="trail__principle-dot"
                          style={{
                            opacity: score,
                            backgroundColor: getPrincipleColor(key),
                          }}
                          title={`${key}: ${(score * 100).toFixed(0)}%`}
                          aria-label={`${key}: ${(score * 100).toFixed(0)}%`}
                        />
                      );
                    })}
                  </div>
                )}

              {/* Separator (unless last step) */}
              {stepIndex < path.length - 1 && (
                <span className="trail__separator" aria-hidden="true">
                  →
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
});

// =============================================================================
// Helpers
// =============================================================================

interface PathItem {
  type: 'step' | 'ellipsis';
  value?: string;
  index?: number;
}

/**
 * Collapse middle steps if path exceeds maxVisible.
 * Shows: first 2 + ... + last 2
 */
function computeVisiblePath(path: string[], maxVisible: number): PathItem[] {
  if (path.length <= maxVisible) {
    return path.map((value, index) => ({ type: 'step', value, index }));
  }

  const firstCount = 2;
  const lastCount = 2;
  const visible: PathItem[] = [];

  // First steps
  for (let i = 0; i < firstCount; i++) {
    visible.push({ type: 'step', value: path[i], index: i });
  }

  // Ellipsis
  visible.push({ type: 'ellipsis' });

  // Last steps
  for (let i = path.length - lastCount; i < path.length; i++) {
    visible.push({ type: 'step', value: path[i], index: i });
  }

  return visible;
}

/**
 * Format step label for display.
 * Extracts filename from paths, truncates long IDs.
 */
function formatStepLabel(stepId: string, compact: boolean): string {
  // Extract filename from path
  if (stepId.includes('/')) {
    const parts = stepId.split('/');
    stepId = parts[parts.length - 1];
  }

  // Truncate long IDs
  const maxLen = compact ? 15 : 30;
  if (stepId.length > maxLen) {
    return stepId.slice(0, maxLen - 3) + '...';
  }

  return stepId;
}

/**
 * Format step title (tooltip).
 */
function formatStepTitle(stepId: string, stepIndex: number): string {
  return `Step ${stepIndex + 1}: ${stepId}`;
}

/**
 * Get color for principle indicator dots.
 */
function getPrincipleColor(principle: keyof ConstitutionScores): string {
  const colors: Record<keyof ConstitutionScores, string> = {
    tasteful: '#8ba98b', // glow-lichen
    curated: '#c4a77d', // glow-spore
    ethical: '#4a6b4a', // life-sage
    joyInducing: '#d4b88c', // glow-amber
    composable: '#6b8b6b', // life-mint
    heterarchical: '#8bab8b', // life-sprout
    generative: '#e5c99d', // glow-light
  };
  return colors[principle] || '#888';
}

export default Trail;
