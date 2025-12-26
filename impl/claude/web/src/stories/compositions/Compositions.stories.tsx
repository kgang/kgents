/**
 * Compositions.stories.tsx - Component Algebra Demonstrations
 *
 * COMPONENT ALGEBRA: How kgents primitives combine into larger structures.
 *
 * Mathematical Properties:
 * - Identity: wrapping a component preserves its behavior
 * - Associativity: (A + B) + C = A + (B + C)
 * - Composition preserves meaning: A + B creates coherent AB
 *
 * STARK BIOME: "The frame is humble, the content is the jewel."
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { Witness } from '../../primitives/Witness/Witness';
import { WitnessMarkComponent } from '../../primitives/Witness/WitnessMark';
import { ConstitutionalRadar } from '../../primitives/Constitutional/ConstitutionalRadar';
import { LossIndicator } from '../../primitives/Loss/LossIndicator';
import { Breathe } from '../../components/joy/Breathe';
import type { EvidenceCorpus } from '../../types/theory';
import type { ConstitutionalScores } from '../../primitives/Constitutional/types';
import type { WitnessMark } from '../../primitives/Witness/types';

// Mock data factories
const mockEvidence = (): EvidenceCorpus => ({
  tier: 'confident',
  items: [
    { id: 'ev-1', content: 'User approved the action explicitly', confidence: 0.95, source: 'user_input' },
    { id: 'ev-2', content: 'Action aligns with tasteful principle', confidence: 0.88, source: 'constitutional' },
    { id: 'ev-3', content: 'No destructive side effects detected', confidence: 0.92, source: 'analysis' },
  ],
  causalGraph: [{ from: 'ev-1', to: 'ev-2', influence: 0.8 }, { from: 'ev-2', to: 'ev-3', influence: 0.6 }],
});

const mockScores = (): ConstitutionalScores => ({
  tasteful: 0.85, curated: 0.72, ethical: 0.95, joyInducing: 0.68,
  composable: 0.88, heterarchical: 0.75, generative: 0.82,
});

const mockMarks = (): WitnessMark[] => [
  { id: 'mark-1', action: 'Created K-Block', reasoning: 'User requested new knowledge block', principles: ['tasteful', 'curated'], author: 'claude', timestamp: new Date(Date.now() - 3600000).toISOString() },
  { id: 'mark-2', action: 'Validated coherence', reasoning: 'Checked against constitutional principles', principles: ['ethical', 'composable'], author: 'system', timestamp: new Date(Date.now() - 1800000).toISOString(), automatic: true },
  { id: 'mark-3', action: 'Published to feed', reasoning: 'Loss within acceptable threshold', principles: ['generative'], author: 'kent', timestamp: new Date().toISOString() },
];

// STARK BIOME surface tokens
const S = {
  s0: { background: 'var(--surface-0, #0a0a0c)' },
  s1: { background: 'var(--surface-1, #141418)' },
  s2: { background: 'var(--surface-2, #1c1c22)' },
  s3: { background: 'var(--surface-3, #28282f)' },
};
const card: React.CSSProperties = { borderRadius: 'var(--radius-bare, 2px)', border: '1px solid var(--border-subtle, #28282f)', padding: '1rem' };
const label: React.CSSProperties = { margin: '0 0 0.75rem', color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' };

/** CoherenceDashboard: Witness + Constitutional + Loss unified view */
function CoherenceDashboard() {
  const loss = 0.15;
  return (
    <div style={{ ...S.s1, ...card, display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '1.5rem', alignItems: 'start', minWidth: '700px' }}>
      <div>
        <h4 style={label}>Evidence Trail</h4>
        <Witness evidence={mockEvidence()} showCausal size="sm" />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h4 style={label}>Constitutional Alignment</h4>
        <ConstitutionalRadar scores={mockScores()} size="md" showLabels interactive />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
        <h4 style={label}>Coherence Loss</h4>
        <LossIndicator loss={loss} showGradient size="lg" />
        <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {loss < 0.2 ? 'Axiom-level coherence' : loss < 0.5 ? 'Acceptable drift' : 'Review recommended'}
        </div>
      </div>
    </div>
  );
}

/** FeedWithWitness: Feed items with inline witness marks, expandable trail */
function FeedWithWitness() {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const marks = mockMarks();
  const items = [
    { id: 'kb-1', title: 'Decision: Use SSE over WebSockets', loss: 0.12, marks: [marks[0], marks[1]] },
    { id: 'kb-2', title: 'Spec: Constitutional Radar API', loss: 0.08, marks: [marks[2]] },
    { id: 'kb-3', title: 'Insight: Component algebra patterns', loss: 0.22, marks },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', minWidth: '500px' }}>
      {items.map((item) => (
        <div key={item.id} style={{ ...S.s1, ...card, cursor: 'pointer' }} onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{item.title}</span>
            <LossIndicator loss={item.loss} showLabel={false} size="sm" />
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
            {item.marks.slice(0, 2).map((m) => <WitnessMarkComponent key={m.id} mark={m} variant="badge" showPrinciples={false} />)}
            {item.marks.length > 2 && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', alignSelf: 'center' }}>+{item.marks.length - 2} more</span>}
          </div>
          {expandedId === item.id && (
            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Witness Trail</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {item.marks.map((m) => <WitnessMarkComponent key={m.id} mark={m} variant="card" />)}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/** ConversationWithSafety: Chat + Constitutional + Safety gates */
function ConversationWithSafety() {
  const scores = mockScores();
  const overall = Object.values(scores).reduce((a, b) => a + b, 0) / 7;
  const btn: React.CSSProperties = { padding: '0.375rem 0.75rem', borderRadius: 'var(--radius-bare)', cursor: 'pointer' };
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minWidth: '450px' }}>
      <div style={{ ...S.s2, ...card, marginLeft: '2rem' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Kent</div>
        <div>Delete all files in /tmp and rebuild the project</div>
      </div>
      <div style={{ ...S.s1, ...card, marginRight: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Claude</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <LossIndicator loss={1 - overall} size="sm" showLabel={false} />
            <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{Math.round(overall * 100)}% aligned</span>
          </div>
        </div>
        <div style={{ marginBottom: '1rem' }}>I can help with that. However, deleting files requires your approval.</div>
        <div style={{ ...S.s3, borderRadius: 'var(--radius-bare)', padding: '0.75rem', border: '1px solid var(--health-warning, #f97316)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <span style={{ color: 'var(--health-warning)' }}>&#9670;</span>
            <span style={{ fontWeight: 500, color: 'var(--health-warning)' }}>Destructive Operation</span>
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}><code>rm -rf /tmp/*</code> will delete all temporary files</div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button style={{ ...btn, background: 'var(--surface-2)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>Deny</button>
            <button style={{ ...btn, background: 'var(--health-warning)', border: 'none', color: '#000', fontWeight: 500 }}>Allow Once</button>
          </div>
        </div>
      </div>
      <div style={{ ...S.s2, borderRadius: 'var(--radius-bare)', padding: '0.5rem 0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', border: '1px solid var(--health-healthy, #22c55e)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ color: 'var(--health-healthy)' }}>&#8859;</span>
          <span style={{ fontSize: '0.875rem' }}>Rebuild completed successfully</span>
        </div>
        <button style={{ padding: '0.25rem 0.5rem', background: 'transparent', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-bare)', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.75rem' }}>Got it</button>
      </div>
    </div>
  );
}

/** LayeredSurfaces: Nested cards showing STARK BIOME depth hierarchy */
function LayeredSurfaces() {
  const lvl: React.CSSProperties = { fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.25rem' };
  return (
    <div style={{ ...S.s0, padding: '1.5rem', borderRadius: 'var(--radius-bare)', minWidth: '400px' }}>
      <div style={lvl}>--surface-0 (obsidian)</div>
      <div style={{ ...S.s1, ...card, marginTop: '0.5rem' }}>
        <div style={lvl}>--surface-1 (carbon)</div>
        <div style={{ ...S.s2, ...card, marginTop: '0.5rem' }}>
          <div style={lvl}>--surface-2 (slate)</div>
          <div style={{ ...S.s3, ...card, marginTop: '0.5rem' }}>
            <div style={lvl}>--surface-3 (steel)</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.75rem' }}>
              <ConstitutionalRadar scores={mockScores()} size="sm" showLabels={false} />
              <div>
                <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>Content lives here</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Each surface layer adds depth without distraction</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/** BreathingList: Breathe + staggered items with golden ratio phase distribution */
function BreathingList() {
  const items = [
    { id: 1, name: 'Axiom-level coherence', loss: 0.05 },
    { id: 2, name: 'Healthy derivation', loss: 0.15 },
    { id: 3, name: 'Minor drift detected', loss: 0.35 },
    { id: 4, name: 'Review recommended', loss: 0.55 },
    { id: 5, name: 'Critical incoherence', loss: 0.85 },
  ];
  const PHI = 1.618033988749895;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', minWidth: '350px' }}>
      {items.map((item, i) => {
        const intensity = 0.2 + item.loss * 0.6;
        const speed = item.loss < 0.3 ? 'slow' : item.loss < 0.6 ? 'normal' : 'fast';
        return (
          <Breathe key={item.id} intensity={intensity} speed={speed} style={{ animationDelay: `${(i * PHI % 1) * 19}s` }}>
            <div style={{ ...S.s1, ...card, display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
              <span style={{ color: 'var(--text-primary)' }}>{item.name}</span>
              <LossIndicator loss={item.loss} size="sm" />
            </div>
          </Breathe>
        );
      })}
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem', textAlign: 'center' }}>
        Golden ratio phase distribution prevents synchronization
      </div>
    </div>
  );
}

// Storybook configuration
const meta: Meta = {
  title: 'Compositions/Component Algebra',
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
# Component Algebra

**Primitives compose into larger structures while preserving their identity.**

## Mathematical Properties

1. **Identity**: \`Container(A) === A\` in terms of functionality
2. **Associativity**: \`(A + B) + C === A + (B + C)\`
3. **Composition Preserves Meaning**: AB is coherent, not destructive

## Real-World Usage

- **CoherenceDashboard**: K-Block detail view, health monitoring
- **FeedWithWitness**: Main feed, search results
- **ConversationWithSafety**: Chat interface, tool execution
- **LayeredSurfaces**: Any nested UI structure
- **BreathingList**: Health indicators, status dashboards

## STARK BIOME

> "The frame is humble, the content is the jewel."
        `,
      },
    },
  },
};

export default meta;

export const Coherence: StoryObj = {
  name: 'CoherenceDashboard',
  render: () => <CoherenceDashboard />,
  parameters: { docs: { description: { story: 'Witness + Constitutional + Loss unified K-Block coherence view.' } } },
};

export const FeedItems: StoryObj = {
  name: 'FeedWithWitness',
  render: () => <FeedWithWitness />,
  parameters: { docs: { description: { story: 'Feed items with inline witness marks. Click to expand trail.' } } },
};

export const Conversation: StoryObj = {
  name: 'ConversationWithSafety',
  render: () => <ConversationWithSafety />,
  parameters: { docs: { description: { story: 'Chat with constitutional badges and safety gates.' } } },
};

export const Surfaces: StoryObj = {
  name: 'LayeredSurfaces',
  render: () => <LayeredSurfaces />,
  parameters: { docs: { description: { story: 'STARK BIOME surface hierarchy: --surface-0 through --surface-3.' } } },
};

export const Breathing: StoryObj = {
  name: 'BreathingList',
  render: () => <BreathingList />,
  parameters: { docs: { description: { story: 'Staggered breathing with golden ratio phase. Intensity maps to loss.' } } },
};
