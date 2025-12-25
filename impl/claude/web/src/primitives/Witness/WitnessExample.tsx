/**
 * Witness Primitive - Usage Examples
 *
 * Demonstrates the three main use cases:
 * 1. ASHC compilation evidence
 * 2. Confidence indicators
 * 3. Chat session evidence
 */

import { Witness } from './Witness';
import type { EvidenceCorpus } from '../../types/theory';

// =============================================================================
// Example 1: ASHC Compilation Evidence (Confident)
// =============================================================================

export function ASHCEvidenceExample() {
  const evidence: EvidenceCorpus = {
    tier: 'confident',
    items: [
      {
        id: 'ashc-eq',
        content: 'Equivalence score: 95% (spec↔impl verified)',
        confidence: 0.95,
        source: 'ASHC',
      },
      {
        id: 'ashc-runs',
        content: '14/15 verification runs passed',
        confidence: 0.93,
        source: 'ASHC',
      },
      {
        id: 'ashc-stability',
        content: 'Chaos stability: 92% (robust under perturbation)',
        confidence: 0.92,
        source: 'ASHC',
      },
    ],
    causalGraph: [
      { from: 'ashc-eq', to: 'ashc-stability', influence: 0.85 },
      { from: 'ashc-runs', to: 'ashc-eq', influence: 0.78 },
    ],
  };

  return (
    <div style={{ padding: 20 }}>
      <h3>ASHC Compilation Evidence</h3>
      <Witness evidence={evidence} showCausal={true} />
    </div>
  );
}

// =============================================================================
// Example 2: Per-Turn Confidence (Uncertain)
// =============================================================================

export function ConfidenceIndicatorExample() {
  const evidence: EvidenceCorpus = {
    tier: 'uncertain',
    items: [
      {
        id: 'bayesian',
        content: 'Bayesian posterior: P=0.67 (α=20, β=10)',
        confidence: 0.67,
        source: 'Bayesian',
      },
      {
        id: 'tools',
        content: 'Tools executed: 8 succeeded, 2 failed',
        confidence: 0.8,
        source: 'Tools',
      },
    ],
    causalGraph: [{ from: 'tools', to: 'bayesian', influence: 0.9 }],
  };

  return (
    <div style={{ padding: 20 }}>
      <h3>Per-Turn Confidence</h3>
      <Witness evidence={evidence} showCausal={true} size="sm" />
    </div>
  );
}

// =============================================================================
// Example 3: Low Confidence (Speculative)
// =============================================================================

export function SpeculativeEvidenceExample() {
  const evidence: EvidenceCorpus = {
    tier: 'speculative',
    items: [
      {
        id: 'partial',
        content: 'Only 3/10 test cases passed',
        confidence: 0.3,
        source: 'Tests',
      },
      {
        id: 'uncertain',
        content: 'High variance in results (±35%)',
        confidence: 0.25,
        source: 'Stats',
      },
    ],
    causalGraph: [],
  };

  return (
    <div style={{ padding: 20 }}>
      <h3>Speculative Evidence (Needs Review)</h3>
      <Witness evidence={evidence} />
    </div>
  );
}

// =============================================================================
// Example 4: Compact Mode
// =============================================================================

export function CompactWitnessExample() {
  const evidence: EvidenceCorpus = {
    tier: 'confident',
    items: [
      {
        id: '1',
        content: 'Evidence item 1',
        confidence: 0.9,
        source: 'Source',
      },
      {
        id: '2',
        content: 'Evidence item 2',
        confidence: 0.85,
        source: 'Source',
      },
    ],
    causalGraph: [],
  };

  return (
    <div style={{ padding: 20 }}>
      <h3>Compact Mode (Inline Badge)</h3>
      <p>
        This response has high confidence{' '}
        <Witness evidence={evidence} compact={true} size="sm" /> based on
        multiple sources.
      </p>
    </div>
  );
}

// =============================================================================
// All Examples
// =============================================================================

export function WitnessExamples() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 40 }}>
      <ASHCEvidenceExample />
      <ConfidenceIndicatorExample />
      <SpeculativeEvidenceExample />
      <CompactWitnessExample />
    </div>
  );
}

export default WitnessExamples;
