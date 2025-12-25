/**
 * WitnessedTrail — Trail component integrated with live witness marks
 *
 * "Every navigation leaves a trail. The trail IS the evidence."
 *
 * Combines the Trail primitive with real-time witness marks from navigation.
 * Shows the derivation path with constitutional scoring indicators.
 *
 * @see spec/synthesis/RADICAL_TRANSFORMATION.md
 */

import { memo, useMemo } from 'react';
import { Trail } from '../primitives/Trail';
import { useWitness, type DomainMark, extractActionType } from '../hooks/useWitness';
import type { ConstitutionScores } from '../types/theory';
import type { GraphNode, Trail as TrailState } from './state/types';
import './WitnessedTrail.css';

// =============================================================================
// Types
// =============================================================================

export interface WitnessedTrailProps {
  /** Current navigation trail from state */
  trail: TrailState;

  /** Current node (for highlighting) */
  currentNode: GraphNode | null;

  /** Navigate to a step in the trail */
  onNavigate?: (stepIndex: number, nodePath: string) => void;

  /** Show principle indicators per step */
  showPrinciples?: boolean;

  /** Show compression ratio */
  showCompression?: boolean;

  /** Compact mode */
  compact?: boolean;

  /** Maximum visible steps */
  maxVisible?: number;
}

// =============================================================================
// Principle Score Extraction
// =============================================================================

/**
 * Extract principle scores from a witness mark.
 * Marks don't carry full scores, so we infer from principles array.
 */
function extractScoresFromMark(mark: DomainMark): ConstitutionScores {
  const scores: ConstitutionScores = {
    tasteful: 0.5,
    curated: 0.5,
    ethical: 0.5,
    joyInducing: 0.5,
    composable: 0.5,
    heterarchical: 0.5,
    generative: 0.5,
  };

  // Boost scores for principles mentioned in the mark
  for (const principle of mark.principles || []) {
    const key = normalizePrincipleKey(principle);
    if (key && key in scores) {
      scores[key as keyof ConstitutionScores] = 1.0;
    }
  }

  return scores;
}

/**
 * Normalize principle name to ConstitutionScores key.
 */
function normalizePrincipleKey(principle: string): keyof ConstitutionScores | null {
  const normalized = principle.toLowerCase().replace(/_/g, '');
  const mapping: Record<string, keyof ConstitutionScores> = {
    tasteful: 'tasteful',
    curated: 'curated',
    ethical: 'ethical',
    joyinducing: 'joyInducing',
    joy_inducing: 'joyInducing',
    composable: 'composable',
    heterarchical: 'heterarchical',
    generative: 'generative',
  };
  return mapping[normalized] ?? null;
}

/**
 * Compute compression ratio from trail and marks.
 * Compression = marks / trail steps (lower = more compressed)
 */
function computeCompression(trailLength: number, markCount: number): number {
  if (trailLength === 0) return 0;
  // Invert so higher = better compression
  return Math.max(0, Math.min(1, 1 - markCount / (trailLength * 2)));
}

// =============================================================================
// Component
// =============================================================================

export const WitnessedTrail = memo(function WitnessedTrail({
  trail,
  currentNode,
  onNavigate,
  showPrinciples = true,
  showCompression = true,
  compact = false,
  maxVisible = 7,
}: WitnessedTrailProps) {
  // Get recent navigation marks
  const { recentMarks, pendingCount } = useWitness({
    filterDomain: 'navigation',
    maxRecent: trail.steps.length * 2,
  });

  // Build path from trail steps
  const path = useMemo(() => {
    return trail.steps.map((step) => {
      // Use title or extract from path
      const segments = step.node.path.split('/');
      return step.node.title || segments[segments.length - 1] || step.node.path;
    });
  }, [trail.steps]);

  // Match marks to trail steps for principle scores
  const principleScores = useMemo(() => {
    if (!showPrinciples) return undefined;

    return trail.steps.map((step) => {
      // Find most recent mark for this node
      const mark = recentMarks.find((m) => {
        const metadata = m.metadata as { toPath?: string } | undefined;
        return metadata?.toPath === step.node.path;
      });

      if (mark) {
        return extractScoresFromMark(mark);
      }

      // Default scores if no mark found
      return {
        tasteful: 0.5,
        curated: 0.5,
        ethical: 0.5,
        joyInducing: 0.5,
        composable: 0.5,
        heterarchical: 0.5,
        generative: 0.5,
      };
    });
  }, [trail.steps, recentMarks, showPrinciples]);

  // Compute compression ratio
  const compressionRatio = useMemo(() => {
    if (!showCompression) return undefined;
    return computeCompression(trail.steps.length, recentMarks.length);
  }, [trail.steps.length, recentMarks.length, showCompression]);

  // Current index in trail
  const currentIndex = useMemo(() => {
    if (!currentNode) return path.length - 1;
    return trail.steps.findIndex((s) => s.node.path === currentNode.path);
  }, [trail.steps, currentNode, path.length]);

  // Handle step click
  const handleStepClick = (stepIndex: number, _stepId: string) => {
    const step = trail.steps[stepIndex];
    if (step && onNavigate) {
      onNavigate(stepIndex, step.node.path);
    }
  };

  if (path.length === 0) {
    return (
      <div className="witnessed-trail witnessed-trail--empty">
        <span className="witnessed-trail__placeholder">No navigation history</span>
      </div>
    );
  }

  return (
    <div className="witnessed-trail">
      <Trail
        path={path}
        compressionRatio={compressionRatio}
        showPrinciples={showPrinciples}
        principleScores={principleScores}
        onStepClick={handleStepClick}
        maxVisible={maxVisible}
        compact={compact}
        currentIndex={currentIndex >= 0 ? currentIndex : undefined}
      />

      {/* Pending mark indicator */}
      {pendingCount > 0 && (
        <div className="witnessed-trail__pending" title={`${pendingCount} marks pending`}>
          <span className="witnessed-trail__pending-dot" />
        </div>
      )}

      {/* Most recent mark preview */}
      {recentMarks.length > 0 && !compact && (
        <div className="witnessed-trail__latest">
          <span className="witnessed-trail__latest-type">
            {extractActionType(recentMarks[0].action) ?? 'nav'}
          </span>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Export
// =============================================================================

export default WitnessedTrail;
