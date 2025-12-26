/**
 * Witness Primitives Stories
 *
 * STARK BIOME Design System Demo
 *
 * These stories showcase the Witness primitives:
 * - Witness: Evidence display with confidence tiers and causal graphs
 * - WitnessMark: Individual action marks with principles and reasoning
 * - WitnessTrail: Causal chains of witness marks
 *
 * Philosophy: "The proof IS the decision. The mark IS the witness."
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { Witness } from './Witness';
import { WitnessMarkComponent } from './WitnessMark';
import { WitnessTrailComponent } from './WitnessTrail';
import type { WitnessMark } from './types';
import type { EvidenceCorpus } from '../../types/theory';

// Import component CSS
import './Witness.css';

// =============================================================================
// Mock Data - Evidence
// =============================================================================

/** High confidence evidence demonstrating ASHC-tier compilation. */
const mockHighConfidenceEvidence: EvidenceCorpus = {
  tier: 'confident',
  items: [
    {
      id: 'ev-1',
      content: 'AGENTESE paths are places, not just identifiers. The path IS the address.',
      confidence: 0.95,
      source: 'spec/protocols/agentese.md',
    },
    {
      id: 'ev-2',
      content: 'Constitutional alignment score: 0.92 across all 7 principles.',
      confidence: 0.88,
      source: 'services/witness/constitutional.py',
    },
    {
      id: 'ev-3',
      content: 'Trust level L3 achieved after 150 marks with < 1% violation rate.',
      confidence: 0.91,
      source: 'services/witness/trust.py',
    },
  ],
  causalGraph: [
    { from: 'ev-1', to: 'ev-2', influence: 0.85 },
    { from: 'ev-2', to: 'ev-3', influence: 0.72 },
  ],
};

/** Medium confidence evidence showing uncertain compilation. */
const mockMediumConfidenceEvidence: EvidenceCorpus = {
  tier: 'uncertain',
  items: [
    {
      id: 'ev-4',
      content: 'SSE chosen over WebSockets for unidirectional streaming.',
      confidence: 0.65,
      source: 'decision/2025-12-20',
    },
    {
      id: 'ev-5',
      content: 'Polynomial agent state machine handles mode transitions.',
      confidence: 0.72,
      source: 'agents/polynomial.py',
    },
  ],
  causalGraph: [
    { from: 'ev-4', to: 'ev-5', influence: 0.55 },
  ],
};

/** Low confidence evidence showing speculative compilation. */
const mockLowConfidenceEvidence: EvidenceCorpus = {
  tier: 'speculative',
  items: [
    {
      id: 'ev-6',
      content: 'Hypha foraging may reduce free energy in multi-agent systems.',
      confidence: 0.35,
      source: 'brainstorming/hypha.md',
    },
  ],
  causalGraph: [],
};

/** Large evidence corpus for stress testing. */
const mockLargeEvidence: EvidenceCorpus = {
  tier: 'confident',
  items: [
    { id: 'ev-a1', content: 'PolyAgent implements state-dependent behavior.', confidence: 0.92, source: 'agents/poly.py' },
    { id: 'ev-a2', content: 'Operad defines composition grammar.', confidence: 0.88, source: 'agents/operad.py' },
    { id: 'ev-a3', content: 'Sheaf ensures global coherence.', confidence: 0.85, source: 'agents/sheaf.py' },
    { id: 'ev-a4', content: 'DataBus handles storage events.', confidence: 0.91, source: 'services/witness/bus.py' },
    { id: 'ev-a5', content: 'SynergyBus bridges Crown Jewels.', confidence: 0.87, source: 'services/synergy.py' },
  ],
  causalGraph: [
    { from: 'ev-a1', to: 'ev-a2', influence: 0.78 },
    { from: 'ev-a2', to: 'ev-a3', influence: 0.82 },
    { from: 'ev-a3', to: 'ev-a4', influence: 0.65 },
    { from: 'ev-a4', to: 'ev-a5', influence: 0.71 },
  ],
};

// =============================================================================
// Mock Data - Witness Marks
// =============================================================================

const now = new Date();
const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000).toISOString();
const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000).toISOString();
const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString();

/** Decision mark with full reasoning. */
const mockDecisionMark: WitnessMark = {
  id: 'mark-1',
  action: 'Decided to use SSE over WebSockets',
  reasoning: 'Unidirectional is sufficient, simpler ops, HTTP-native',
  principles: ['composable', 'tasteful'],
  author: 'kent',
  timestamp: fiveMinutesAgo,
  automatic: false,
};

/** Observation mark from Claude. */
const mockObservationMark: WitnessMark = {
  id: 'mark-2',
  action: 'Observed API latency spike (200ms -> 20ms after caching)',
  reasoning: 'Added Redis caching layer to reduce database round-trips',
  principles: ['composable', 'joy_inducing'],
  author: 'claude',
  timestamp: oneHourAgo,
  automatic: false,
};

/** Eureka mark - a discovery moment. */
const mockEurekaMark: WitnessMark = {
  id: 'mark-3',
  action: 'Eureka: AGENTESE paths are places, not identifiers',
  reasoning: 'The path IS the address. This unlocks spatial navigation.',
  principles: ['generative', 'ethical'],
  author: 'kent',
  timestamp: oneHourAgo,
  parent_mark_id: 'mark-1',
  automatic: false,
};

/** Gotcha mark - a warning about pitfalls. */
const mockGotchaMark: WitnessMark = {
  id: 'mark-4',
  action: 'Gotcha: @node runs at import time, not registration',
  reasoning: 'Modules must be imported before nodes are discoverable',
  principles: ['curated', 'heterarchical'],
  author: 'claude',
  timestamp: threeDaysAgo,
  automatic: false,
};

/** System-generated automatic mark. */
const mockAutoMark: WitnessMark = {
  id: 'mark-5',
  action: 'Trust level upgraded: L2 -> L3',
  reasoning: 'Alignment threshold 0.9 reached after 150 marks',
  principles: ['ethical'],
  author: 'system',
  timestamp: now.toISOString(),
  automatic: true,
};

/** Mark without reasoning (minimal). */
const mockMinimalMark: WitnessMark = {
  id: 'mark-6',
  action: 'Committed refactor: K-gent cleanup (-2,452 LOC)',
  principles: ['tasteful', 'curated'],
  author: 'kent',
  timestamp: fiveMinutesAgo,
  automatic: false,
};

/** Long trail of marks for testing. */
const mockLongTrail: WitnessMark[] = Array.from({ length: 12 }, (_, i) => ({
  id: `trail-${i}`,
  action: `Step ${i + 1}: ${['Initialize', 'Validate', 'Transform', 'Compose', 'Execute', 'Verify', 'Commit', 'Push', 'Deploy', 'Monitor', 'Celebrate', 'Document'][i]}`,
  reasoning: i % 2 === 0 ? `Reasoning for step ${i + 1}` : undefined,
  principles: [['tasteful', 'composable', 'ethical', 'generative', 'curated', 'heterarchical', 'joy_inducing'][i % 7]],
  author: i % 3 === 0 ? 'kent' : i % 3 === 1 ? 'claude' : 'system',
  timestamp: new Date(now.getTime() - (11 - i) * 10 * 60 * 1000).toISOString(),
  automatic: i % 4 === 0,
}));

// =============================================================================
// Witness (Evidence Display) Stories
// =============================================================================

const witnessMeta: Meta<typeof Witness> = {
  title: 'Primitives/Witness/Evidence',
  component: Witness,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
## Witness - Evidence Display

Displays compilation evidence with confidence tiers and causal graphs.

**Confidence Tiers:**
- **Confident** (>0.80): Green border, high trust
- **Uncertain** (0.50-0.80): Orange border, moderate trust
- **Speculative** (<0.50): Red border, low trust

**STARK BIOME Design:**
- Steel background surfaces
- Tier-specific border colors (earned glow)
- Breathing animation for high-influence causal edges
- Brutalist foundation: no decoration, just data
        `,
      },
    },
  },
};

export default witnessMeta;

type WitnessStory = StoryObj<typeof Witness>;

/** Default evidence display with high confidence items. */
export const Default: WitnessStory = {
  name: 'Default (High Confidence)',
  args: {
    evidence: mockHighConfidenceEvidence,
    showCausal: true,
    compact: false,
    size: 'md',
  },
};

/** ASHC-tier evidence with causal graph showing influence paths. */
export const HighConfidence: WitnessStory = {
  name: 'High Confidence (ASHC Tier)',
  args: {
    evidence: mockHighConfidenceEvidence,
    showCausal: true,
    compact: false,
    size: 'md',
  },
  parameters: {
    docs: {
      description: {
        story: 'Evidence with >0.80 confidence shows green borders and high-influence causal edges with breathing animation.',
      },
    },
  },
};

/** Medium confidence evidence showing uncertain compilation. */
export const MediumConfidence: WitnessStory = {
  name: 'Medium Confidence (Uncertain)',
  args: {
    evidence: mockMediumConfidenceEvidence,
    showCausal: true,
    compact: false,
    size: 'md',
  },
  parameters: {
    docs: {
      description: {
        story: 'Evidence in the 0.50-0.80 range shows orange borders, indicating moderate trust.',
      },
    },
  },
};

/** Low confidence evidence showing speculative compilation. */
export const LowConfidence: WitnessStory = {
  name: 'Low Confidence (Speculative)',
  args: {
    evidence: mockLowConfidenceEvidence,
    showCausal: false,
    compact: false,
    size: 'md',
  },
  parameters: {
    docs: {
      description: {
        story: 'Evidence below 0.50 shows red borders. Use with caution.',
      },
    },
  },
};

/** Large evidence corpus with multiple causal edges. */
export const MultipleItems: WitnessStory = {
  name: 'Multiple Evidence Items',
  args: {
    evidence: mockLargeEvidence,
    showCausal: true,
    compact: false,
    size: 'md',
  },
};

/** Compact inline display for embedding in other components. */
export const Compact: WitnessStory = {
  name: 'Compact (Inline)',
  args: {
    evidence: mockHighConfidenceEvidence,
    showCausal: false,
    compact: true,
    size: 'md',
  },
  parameters: {
    docs: {
      description: {
        story: 'Compact mode shows just a badge with count, suitable for inline display.',
      },
    },
  },
};

/** Small size variant for constrained spaces. */
export const SmallSize: WitnessStory = {
  name: 'Small Size',
  args: {
    evidence: mockHighConfidenceEvidence,
    showCausal: true,
    compact: false,
    size: 'sm',
  },
};

/** Large size variant for detailed views. */
export const LargeSize: WitnessStory = {
  name: 'Large Size',
  args: {
    evidence: mockHighConfidenceEvidence,
    showCausal: true,
    compact: false,
    size: 'lg',
  },
};

// =============================================================================
// WitnessMark Stories
// =============================================================================

export const MarkDefault: StoryObj = {
  name: 'Mark - Decision',
  render: () => (
    <div style={{ maxWidth: '400px' }}>
      <WitnessMarkComponent mark={mockDecisionMark} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'A decision mark with full reasoning and principle tags. Kent decided to use SSE over WebSockets.',
      },
    },
  },
};

export const MarkObservation: StoryObj = {
  name: 'Mark - Observation',
  render: () => (
    <div style={{ maxWidth: '400px' }}>
      <WitnessMarkComponent mark={mockObservationMark} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'An observation mark from Claude noting performance improvements.',
      },
    },
  },
};

export const MarkEureka: StoryObj = {
  name: 'Mark - Eureka',
  render: () => (
    <div style={{ maxWidth: '400px' }}>
      <WitnessMarkComponent mark={mockEurekaMark} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'A eureka moment - when an insight crystallizes. "AGENTESE paths are places."',
      },
    },
  },
};

export const MarkGotcha: StoryObj = {
  name: 'Mark - Gotcha',
  render: () => (
    <div style={{ maxWidth: '400px' }}>
      <WitnessMarkComponent mark={mockGotchaMark} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'A gotcha mark warning about a common pitfall. Prevents future mistakes.',
      },
    },
  },
};

export const MarkAutomatic: StoryObj = {
  name: 'Mark - Automatic (System)',
  render: () => (
    <div style={{ maxWidth: '400px' }}>
      <WitnessMarkComponent mark={mockAutoMark} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'System-generated automatic mark. Shows "auto" badge in header.',
      },
    },
  },
};

export const MarkWithoutReasoning: StoryObj = {
  name: 'Mark - Without Reasoning',
  render: () => (
    <div style={{ maxWidth: '400px' }}>
      <WitnessMarkComponent mark={mockMinimalMark} showReasoning={false} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'A mark without reasoning text. Sometimes the action speaks for itself.',
      },
    },
  },
};

export const MarkVariants: StoryObj = {
  name: 'Mark - All Variants',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '500px' }}>
      <div>
        <h4 style={{ marginBottom: '8px', color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Card (Default)</h4>
        <WitnessMarkComponent mark={mockDecisionMark} variant="card" />
      </div>
      <div>
        <h4 style={{ marginBottom: '8px', color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Minimal</h4>
        <WitnessMarkComponent mark={mockDecisionMark} variant="minimal" />
      </div>
      <div>
        <h4 style={{ marginBottom: '8px', color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Badge</h4>
        <WitnessMarkComponent mark={mockDecisionMark} variant="badge" />
      </div>
      <div>
        <h4 style={{ marginBottom: '8px', color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>Inline</h4>
        <WitnessMarkComponent mark={mockDecisionMark} variant="inline" />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All four display variants: Card (full), Minimal (border only), Badge (colored pill), Inline (text only).',
      },
    },
  },
};

// =============================================================================
// WitnessTrail Stories
// =============================================================================

export const TrailDefault: StoryObj = {
  name: 'Trail - Default (3-5 Marks)',
  render: () => (
    <div style={{ maxWidth: '500px' }}>
      <WitnessTrailComponent
        marks={[mockDecisionMark, mockObservationMark, mockEurekaMark, mockGotchaMark]}
        showConnections={true}
        showPrinciples={true}
        showReasoning={true}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'A typical trail with 4 marks showing the causal chain of decisions and observations.',
      },
    },
  },
};

export const TrailEmpty: StoryObj = {
  name: 'Trail - Empty',
  render: () => (
    <div style={{ maxWidth: '500px' }}>
      <WitnessTrailComponent marks={[]} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Empty trail shows a dashed border with "No marks yet" message.',
      },
    },
  },
};

export const TrailLong: StoryObj = {
  name: 'Trail - Long (10+ Marks)',
  render: () => (
    <div style={{ maxWidth: '500px' }}>
      <WitnessTrailComponent
        marks={mockLongTrail}
        maxVisible={5}
        showConnections={true}
        showPrinciples={true}
        showReasoning={false}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Long trail with maxVisible=5 shows "+7 more marks" indicator.',
      },
    },
  },
};

export const TrailMixedTypes: StoryObj = {
  name: 'Trail - Mixed Mark Types',
  render: () => (
    <div style={{ maxWidth: '500px' }}>
      <WitnessTrailComponent
        marks={[mockDecisionMark, mockAutoMark, mockEurekaMark, mockObservationMark, mockGotchaMark]}
        showConnections={true}
        showPrinciples={true}
        showReasoning={true}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Trail with mixed mark types: decision, auto, eureka, observation, gotcha.',
      },
    },
  },
};

export const TrailHorizontal: StoryObj = {
  name: 'Trail - Horizontal',
  render: () => (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <WitnessTrailComponent
        marks={[mockDecisionMark, mockEurekaMark, mockAutoMark]}
        orientation="horizontal"
        showConnections={true}
        showPrinciples={false}
        showReasoning={false}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Horizontal trail orientation for timeline-style display.',
      },
    },
  },
};

// =============================================================================
// Combined Dashboard Story
// =============================================================================

export const FullWitnessDashboard: StoryObj = {
  name: 'Full Witness Dashboard',
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '32px',
        padding: '24px',
        background: '#141418',
        borderRadius: '4px',
        border: '1px solid #28282F',
      }}
    >
      <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
        <div style={{ flex: '1 1 400px' }}>
          <h3 style={{ marginBottom: '12px', color: '#e0e0e0', fontSize: '14px' }}>Evidence Corpus</h3>
          <Witness evidence={mockHighConfidenceEvidence} showCausal={true} size="md" />
        </div>
        <div style={{ flex: '1 1 400px' }}>
          <h3 style={{ marginBottom: '12px', color: '#e0e0e0', fontSize: '14px' }}>Session Trail</h3>
          <WitnessTrailComponent
            marks={[mockDecisionMark, mockEurekaMark, mockObservationMark]}
            showConnections={true}
            showPrinciples={true}
            showReasoning={false}
          />
        </div>
      </div>
    </div>
  ),
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        story: `
# Full Witness Dashboard

Combines Evidence display with a session trail of marks.

This dashboard embodies STARK BIOME:
- Steel frame (\`#141418\` background)
- Tier-specific glow (green for confident)
- Principle-colored marks (composable=cyan, ethical=green)

Philosophy: "The trail IS the proof. The proof IS the trail."
        `,
      },
    },
  },
};
