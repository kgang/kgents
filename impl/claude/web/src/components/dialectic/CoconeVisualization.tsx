/**
 * CoconeVisualization - Abstract Categorical Cocone
 *
 * A minimal, meaningful visualization of the categorical cocone structure.
 * "The cocone is not a compromise. It is an Aufhebung - a lifting up."
 *
 * Visual metaphor:
 * - Two nodes at the base (thesis, antithesis)
 * - One apex node (synthesis)
 * - Morphisms (legs) connecting base to apex
 * - Animation shows the "lifting up" moment
 *
 * Design: Brutalist, minimal motion, earned glow only on completion.
 */

import { memo, useMemo } from 'react';
import type { CoconeVisualizationProps, CoconeAnimationState } from './types';

/**
 * Map ceremony phase to animation state.
 */
function getAnimationState(
  phase: CoconeVisualizationProps['phase'],
  hasThesis: boolean,
  hasAntithesis: boolean
): CoconeAnimationState {
  if (phase === 'complete') return 'complete';
  if (phase === 'processing') return 'sublating';
  if (hasThesis && hasAntithesis) return 'converging';
  if (hasAntithesis) return 'antithesis-pulse';
  if (hasThesis) return 'thesis-pulse';
  return 'idle';
}

/**
 * SVG path for the morphism leg (curved arrow).
 */
function MorphismLeg({
  from,
  to,
  active,
  side,
}: {
  from: { x: number; y: number };
  to: { x: number; y: number };
  active: boolean;
  side: 'left' | 'right';
}) {
  // Calculate control point for quadratic curve
  const midX = (from.x + to.x) / 2;
  const midY = (from.y + to.y) / 2;
  const offset = side === 'left' ? -20 : 20;
  const controlX = midX + offset;
  const controlY = midY - 10;

  const pathD = `M ${from.x} ${from.y} Q ${controlX} ${controlY} ${to.x} ${to.y}`;

  return (
    <path
      d={pathD}
      className={`cocone-leg ${active ? 'cocone-leg--active' : ''} cocone-leg--${side}`}
      fill="none"
      strokeWidth={active ? 2 : 1}
      markerEnd={active ? 'url(#arrow-active)' : 'url(#arrow)'}
    />
  );
}

/**
 * Node in the cocone (thesis, antithesis, or synthesis).
 */
function CoconeNode({
  x,
  y,
  label,
  type,
  active,
  hasContent,
}: {
  x: number;
  y: number;
  label: string;
  type: 'thesis' | 'antithesis' | 'synthesis';
  active: boolean;
  hasContent: boolean;
}) {
  return (
    <g className={`cocone-node cocone-node--${type} ${active ? 'cocone-node--active' : ''}`}>
      {/* Outer glow (only when complete/active) */}
      {active && <circle cx={x} cy={y} r={24} className="cocone-node__glow" />}

      {/* Main circle */}
      <circle
        cx={x}
        cy={y}
        r={18}
        className={`cocone-node__circle ${hasContent ? 'cocone-node__circle--filled' : ''}`}
      />

      {/* Label */}
      <text x={x} y={y} dy="0.35em" className="cocone-node__label" textAnchor="middle">
        {label}
      </text>
    </g>
  );
}

/**
 * CoconeVisualization Component
 *
 * An abstract visualization of the categorical cocone:
 *
 *           S (Synthesis)
 *          /|\
 *         / | \
 *        /  |  \
 *       K---+---C
 *     Thesis  Antithesis
 *
 * @example
 * <CoconeVisualization
 *   thesis={thesis}
 *   antithesis={antithesis}
 *   synthesis={synthesis}
 *   phase={phase}
 * />
 */
export const CoconeVisualization = memo(function CoconeVisualization({
  thesis,
  antithesis,
  synthesis,
  phase,
  className = '',
}: CoconeVisualizationProps) {
  // Derive animation state
  const animationState = useMemo(
    () => getAnimationState(phase, !!thesis, !!antithesis),
    [phase, thesis, antithesis]
  );

  // Node positions (in a 100x80 viewBox)
  const thesisPos = { x: 25, y: 65 };
  const antithesisPos = { x: 75, y: 65 };
  const synthesisPos = { x: 50, y: 15 };

  const isThesisActive = animationState === 'thesis-pulse' || animationState === 'converging';
  const isAntithesisActive =
    animationState === 'antithesis-pulse' || animationState === 'converging';
  const isSynthesisActive = animationState === 'sublating' || animationState === 'complete';
  const showLegs =
    animationState === 'converging' ||
    animationState === 'sublating' ||
    animationState === 'complete';

  return (
    <div className={`cocone-visualization ${className}`} data-state={animationState}>
      <svg
        viewBox="0 0 100 80"
        className="cocone-svg"
        aria-label="Categorical cocone visualization"
      >
        {/* Definitions (markers, gradients) */}
        <defs>
          {/* Arrow marker for inactive legs */}
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="4"
            markerHeight="4"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" className="cocone-arrow" />
          </marker>

          {/* Arrow marker for active legs */}
          <marker
            id="arrow-active"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="4"
            markerHeight="4"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" className="cocone-arrow cocone-arrow--active" />
          </marker>

          {/* Glow filter for synthesis node */}
          <filter id="synthesis-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Morphism legs (only shown when converging+) */}
        {showLegs && (
          <g className="cocone-legs">
            <MorphismLeg
              from={thesisPos}
              to={synthesisPos}
              active={isSynthesisActive}
              side="left"
            />
            <MorphismLeg
              from={antithesisPos}
              to={synthesisPos}
              active={isSynthesisActive}
              side="right"
            />
          </g>
        )}

        {/* Base connection (thesis -- antithesis) */}
        <line
          x1={thesisPos.x + 18}
          y1={thesisPos.y}
          x2={antithesisPos.x - 18}
          y2={antithesisPos.y}
          className={`cocone-base ${isThesisActive && isAntithesisActive ? 'cocone-base--active' : ''}`}
        />

        {/* Nodes */}
        <CoconeNode
          x={thesisPos.x}
          y={thesisPos.y}
          label="K"
          type="thesis"
          active={isThesisActive}
          hasContent={!!thesis}
        />

        <CoconeNode
          x={antithesisPos.x}
          y={antithesisPos.y}
          label="C"
          type="antithesis"
          active={isAntithesisActive}
          hasContent={!!antithesis}
        />

        <CoconeNode
          x={synthesisPos.x}
          y={synthesisPos.y}
          label="+"
          type="synthesis"
          active={isSynthesisActive}
          hasContent={!!synthesis}
        />
      </svg>

      {/* Label below visualization */}
      <div className="cocone-label">
        {animationState === 'idle' && 'Enter positions to begin'}
        {animationState === 'thesis-pulse' && 'Thesis entered'}
        {animationState === 'antithesis-pulse' && 'Antithesis entered'}
        {animationState === 'converging' && 'Ready to synthesize'}
        {animationState === 'sublating' && 'Aufhebung in progress...'}
        {animationState === 'complete' && 'Synthesis complete'}
      </div>
    </div>
  );
});

export default CoconeVisualization;
