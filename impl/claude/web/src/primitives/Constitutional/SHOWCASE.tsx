/**
 * Constitutional Primitives Showcase
 *
 * Visual demonstration of all Constitutional components.
 * Use this file to test and preview the primitives.
 *
 * To use: Import this component in your dev environment
 */

import { useState } from 'react';
import {
  ConstitutionalRadar,
  PrincipleScore,
  AllPrincipleScores,
  ConstitutionalSummary,
} from './index';
import type { ConstitutionalScores, PrincipleKey } from './types';

// =============================================================================
// Example Scores
// =============================================================================

const EXCELLENT_SCORES: ConstitutionalScores = {
  tasteful: 0.95,
  curated: 0.90,
  ethical: 0.95,
  joyInducing: 0.88,
  composable: 0.92,
  heterarchical: 0.85,
  generative: 0.90,
};

const MODERATE_SCORES: ConstitutionalScores = {
  tasteful: 0.75,
  curated: 0.70,
  ethical: 0.80,
  joyInducing: 0.65,
  composable: 0.72,
  heterarchical: 0.68,
  generative: 0.70,
};

const STRUGGLING_SCORES: ConstitutionalScores = {
  tasteful: 0.45,
  curated: 0.40,
  ethical: 0.55,
  joyInducing: 0.35,
  composable: 0.48,
  heterarchical: 0.42,
  generative: 0.38,
};

// =============================================================================
// Showcase Component
// =============================================================================

export function ConstitutionalShowcase() {
  const [selectedScores, setSelectedScores] =
    useState<ConstitutionalScores>(EXCELLENT_SCORES);
  const [selectedPrinciple, setSelectedPrinciple] = useState<PrincipleKey | null>(
    null
  );

  return (
    <div style={{ padding: '2rem', background: 'var(--surface-0)', minHeight: '100vh' }}>
      <h1 style={{ color: 'var(--text-primary)', marginBottom: '2rem' }}>
        Constitutional Primitives Showcase
      </h1>

      {/* Score Selector */}
      <div style={{ marginBottom: '2rem', display: 'flex', gap: '1rem' }}>
        <button
          onClick={() => setSelectedScores(EXCELLENT_SCORES)}
          style={{
            padding: '0.5rem 1rem',
            background: 'var(--surface-1)',
            border: '1px solid var(--surface-3)',
            color: 'var(--text-primary)',
            cursor: 'pointer',
          }}
        >
          Excellent (90%)
        </button>
        <button
          onClick={() => setSelectedScores(MODERATE_SCORES)}
          style={{
            padding: '0.5rem 1rem',
            background: 'var(--surface-1)',
            border: '1px solid var(--surface-3)',
            color: 'var(--text-primary)',
            cursor: 'pointer',
          }}
        >
          Moderate (71%)
        </button>
        <button
          onClick={() => setSelectedScores(STRUGGLING_SCORES)}
          style={{
            padding: '0.5rem 1rem',
            background: 'var(--surface-1)',
            border: '1px solid var(--surface-3)',
            color: 'var(--text-primary)',
            cursor: 'pointer',
          }}
        >
          Struggling (43%)
        </button>
      </div>

      {/* Selected Principle Display */}
      {selectedPrinciple && (
        <div
          style={{
            padding: '1rem',
            background: 'var(--surface-1)',
            border: '1px solid var(--accent-primary)',
            color: 'var(--text-primary)',
            marginBottom: '2rem',
          }}
        >
          Selected: <strong>{selectedPrinciple}</strong>
        </div>
      )}

      {/* Grid Layout */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '2rem',
        }}
      >
        {/* ConstitutionalRadar - All Sizes */}
        <Section title="ConstitutionalRadar - Small">
          <ConstitutionalRadar
            scores={selectedScores}
            size="sm"
            showLabels={true}
            interactive={true}
            onPrincipleClick={setSelectedPrinciple}
          />
        </Section>

        <Section title="ConstitutionalRadar - Medium">
          <ConstitutionalRadar
            scores={selectedScores}
            size="md"
            showLabels={true}
            interactive={true}
            onPrincipleClick={setSelectedPrinciple}
          />
        </Section>

        <Section title="ConstitutionalRadar - Large">
          <ConstitutionalRadar
            scores={selectedScores}
            size="lg"
            showLabels={true}
            interactive={true}
            onPrincipleClick={setSelectedPrinciple}
          />
        </Section>

        {/* ConstitutionalSummary - Variants */}
        <Section title="ConstitutionalSummary - Compact">
          <ConstitutionalSummary scores={selectedScores} variant="compact" />
        </Section>

        <Section title="ConstitutionalSummary - Expanded">
          <ConstitutionalSummary
            scores={selectedScores}
            variant="expanded"
            showBreakdown={true}
          />
        </Section>

        {/* PrincipleScore - Individual */}
        <Section title="PrincipleScore - Individual">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <PrincipleScore
              principle="composable"
              score={selectedScores.composable}
              size="sm"
            />
            <PrincipleScore
              principle="ethical"
              score={selectedScores.ethical}
              size="md"
            />
            <PrincipleScore
              principle="joyInducing"
              score={selectedScores.joyInducing}
              size="lg"
              onClick={setSelectedPrinciple}
            />
          </div>
        </Section>

        {/* AllPrincipleScores - Grid */}
        <Section title="AllPrincipleScores - Grid">
          <AllPrincipleScores
            scores={selectedScores}
            layout="grid"
            size="md"
            onPrincipleClick={setSelectedPrinciple}
          />
        </Section>

        {/* AllPrincipleScores - Row */}
        <Section title="AllPrincipleScores - Row">
          <AllPrincipleScores
            scores={selectedScores}
            layout="row"
            size="sm"
            showLabels={false}
            onPrincipleClick={setSelectedPrinciple}
          />
        </Section>

        {/* Dashboard Widget Example */}
        <Section title="Dashboard Widget Example">
          <div
            style={{
              padding: '1rem',
              background: 'var(--surface-1)',
              border: '1px solid var(--surface-3)',
            }}
          >
            <h3 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
              K-gent Health
            </h3>
            <ConstitutionalSummary
              scores={selectedScores}
              variant="compact"
              size="sm"
            />
          </div>
        </Section>

        {/* Agent Card Example */}
        <Section title="Agent Card Example">
          <div
            style={{
              padding: '1rem',
              background: 'var(--surface-1)',
              border: '1px solid var(--surface-3)',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '0.5rem',
              }}
            >
              <h3 style={{ color: 'var(--text-primary)' }}>K-gent</h3>
              <PrincipleScore
                principle="composable"
                score={selectedScores.composable}
                size="sm"
              />
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              LLM dialogue, hypnagogia, gatekeeper
            </p>
            <AllPrincipleScores
              scores={selectedScores}
              layout="row"
              size="sm"
              showLabels={false}
            />
          </div>
        </Section>
      </div>
    </div>
  );
}

// =============================================================================
// Helper Components
// =============================================================================

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3
        style={{
          color: 'var(--text-secondary)',
          marginBottom: '1rem',
          fontSize: '0.875rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        }}
      >
        {title}
      </h3>
      {children}
    </div>
  );
}

export default ConstitutionalShowcase;
