/**
 * DP (Dynamic Programming) visualization components
 *
 * Three components for visualizing the DP-Agent bridge:
 * 1. ValueFunctionChart - Radar chart of principle scores
 * 2. PolicyTraceView - Timeline of solution steps
 * 3. ConstitutionScorecard - Detailed per-principle dashboard
 *
 * Backend: impl/claude/services/categorical/dp_bridge.py
 */

export { ValueFunctionChart } from './ValueFunctionChart';
export type { ValueFunctionChartProps } from './ValueFunctionChart';

export { PolicyTraceView } from './PolicyTraceView';
export type { PolicyTraceViewProps } from './PolicyTraceView';

export { ConstitutionScorecard } from './ConstitutionScorecard';
export type { ConstitutionScorecardProps } from './ConstitutionScorecard';

export type {
  Principle,
  PrincipleScore,
  ValueScore,
  TraceEntry,
  PolicyTrace,
  ConstitutionHealth,
} from './types';

export { PRINCIPLE_LABELS, PRINCIPLE_DESCRIPTIONS } from './types';
