/**
 * Example usage of DP visualization components
 *
 * This file demonstrates how to use the three DP components with mock data.
 * Copy and adapt for your use case.
 *
 * To use in a page:
 * ```tsx
 * import { DPExample } from '@/components/dp/example';
 * <DPExample />
 * ```
 */

import { useState } from 'react';
import { ValueFunctionChart } from './ValueFunctionChart';
import { PolicyTraceView } from './PolicyTraceView';
import { ConstitutionScorecard } from './ConstitutionScorecard';
import { DPDashboard } from './DPDashboard';
import type { ValueScore, PolicyTrace, Principle } from './types';

// =============================================================================
// Mock Data
// =============================================================================

const MOCK_VALUE_SCORE: ValueScore = {
  agent_name: 'Compose(Brain, Town)',
  total_score: 0.78,
  min_score: 0.65,
  timestamp: new Date().toISOString(),
  principle_scores: [
    {
      principle: 'TASTEFUL' as Principle,
      score: 0.85,
      evidence: 'Agent serves clear purpose: semantic knowledge management with social simulation',
      weight: 1.0,
      weighted_score: 0.85,
    },
    {
      principle: 'CURATED' as Principle,
      score: 0.9,
      evidence: 'Intentionally composed from two complementary jewels',
      weight: 1.0,
      weighted_score: 0.9,
    },
    {
      principle: 'ETHICAL' as Principle,
      score: 0.95,
      evidence: 'Augments human memory without replacing judgment',
      weight: 2.0,
      weighted_score: 1.9,
    },
    {
      principle: 'JOY_INDUCING' as Principle,
      score: 0.75,
      evidence: 'Delightful emergent behaviors in agent town, but UI needs polish',
      weight: 1.2,
      weighted_score: 0.9,
    },
    {
      principle: 'COMPOSABLE' as Principle,
      score: 0.8,
      evidence: 'Clean operad composition with well-defined interfaces',
      weight: 1.5,
      weighted_score: 1.2,
    },
    {
      principle: 'HETERARCHICAL' as Principle,
      score: 0.65,
      evidence: 'Some residual hierarchy in knowledge graph structure',
      weight: 1.0,
      weighted_score: 0.65,
    },
    {
      principle: 'GENERATIVE' as Principle,
      score: 0.7,
      evidence: 'Spec captures essential structure but could be more compressed',
      weight: 1.0,
      weighted_score: 0.7,
    },
  ],
};

const MOCK_POLICY_TRACE: PolicyTrace = {
  value: 'final_state',
  total_value: 2.45,
  log: [
    {
      state_before: 'initial',
      action: 'Initialize Brain',
      state_after: 'brain_ready',
      value: 0.8,
      rationale: 'Brain provides semantic foundation for knowledge management',
      timestamp: new Date(Date.now() - 3000).toISOString(),
    },
    {
      state_before: 'brain_ready',
      action: 'Initialize Town',
      state_after: 'town_ready',
      value: 0.75,
      rationale: 'Town enables social simulation on top of knowledge graph',
      timestamp: new Date(Date.now() - 2000).toISOString(),
    },
    {
      state_before: 'town_ready',
      action: 'Compose(Brain, Town)',
      state_after: 'composed',
      value: 0.9,
      rationale: 'Composition creates emergent capabilities beyond individual jewels',
      timestamp: new Date(Date.now() - 1000).toISOString(),
    },
  ],
};

// =============================================================================
// Example Component
// =============================================================================

export function DPExample() {
  const [view, setView] = useState<'individual' | 'dashboard'>('individual');

  return (
    <div style={{ padding: '2rem', background: 'var(--steel-950)', minHeight: '100vh' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ color: 'var(--steel-100)', fontFamily: 'var(--font-mono)', fontSize: '1.5rem', marginBottom: '1rem' }}>
          DP Visualization Components
        </h1>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
          <button
            onClick={() => setView('individual')}
            style={{
              padding: '0.5rem 1rem',
              background: view === 'individual' ? 'var(--steel-700)' : 'var(--steel-800)',
              color: 'var(--steel-200)',
              border: '1px solid var(--steel-600)',
              borderRadius: '4px',
              cursor: 'pointer',
              fontFamily: 'var(--font-mono)',
            }}
          >
            Individual Components
          </button>
          <button
            onClick={() => setView('dashboard')}
            style={{
              padding: '0.5rem 1rem',
              background: view === 'dashboard' ? 'var(--steel-700)' : 'var(--steel-800)',
              color: 'var(--steel-200)',
              border: '1px solid var(--steel-600)',
              borderRadius: '4px',
              cursor: 'pointer',
              fontFamily: 'var(--font-mono)',
            }}
          >
            Dashboard
          </button>
        </div>
      </div>

      {view === 'individual' ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* ValueFunctionChart */}
          <section>
            <h2 style={{ color: 'var(--steel-200)', fontFamily: 'var(--font-mono)', fontSize: '1.2rem', marginBottom: '1rem' }}>
              ValueFunctionChart
            </h2>
            <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
              <div>
                <h3 style={{ color: 'var(--steel-400)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Normal</h3>
                <ValueFunctionChart valueScore={MOCK_VALUE_SCORE} />
              </div>
              <div>
                <h3 style={{ color: 'var(--steel-400)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Compact</h3>
                <ValueFunctionChart valueScore={MOCK_VALUE_SCORE} width={300} height={300} compact />
              </div>
            </div>
          </section>

          {/* ConstitutionScorecard */}
          <section>
            <h2 style={{ color: 'var(--steel-200)', fontFamily: 'var(--font-mono)', fontSize: '1.2rem', marginBottom: '1rem' }}>
              ConstitutionScorecard
            </h2>
            <ConstitutionScorecard valueScore={MOCK_VALUE_SCORE} />
          </section>

          {/* PolicyTraceView */}
          <section>
            <h2 style={{ color: 'var(--steel-200)', fontFamily: 'var(--font-mono)', fontSize: '1.2rem', marginBottom: '1rem' }}>
              PolicyTraceView
            </h2>
            <PolicyTraceView trace={MOCK_POLICY_TRACE} />
          </section>
        </div>
      ) : (
        <DPDashboard valueScore={MOCK_VALUE_SCORE} policyTrace={MOCK_POLICY_TRACE} />
      )}
    </div>
  );
}
