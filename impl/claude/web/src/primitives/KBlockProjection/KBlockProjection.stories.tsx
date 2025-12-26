/**
 * KBlockProjection Stories
 *
 * "The projection is not a view. The projection IS the reality."
 *
 * STARK BIOME: The frame is humble. The content glows.
 * 9 projections, 1 universal renderer, infinite possibilities.
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { KBlockProjection } from './KBlockProjection';
import type {
  KBlock,
  KBlockEdge,
  ObserverContext,
  ProjectionMode,
  Contradiction,
  ConstitutionalWeights,
  WitnessMark,
} from './types';
import './KBlockProjection.css';

// =============================================================================
// Mock Data Factory
// =============================================================================

const now = new Date();

/**
 * Create a mock K-Block with sensible defaults.
 */
function createMockKBlock(overrides: Partial<KBlock> = {}): KBlock {
  return {
    id: 'kb-' + Math.random().toString(36).substring(2, 9),
    path: 'spec/protocols/witness.md',
    content: 'The witness marks every decision. Every mark is a trace. Every trace is agency.',
    baseContent: 'The witness marks every decision.',
    contentHash: 'abc123',
    isolation: 'PRISTINE',
    zeroSeedLayer: 3,
    zeroSeedKind: 'goal',
    lineage: [],
    hasProof: false,
    toulminProof: null,
    confidence: 0.85,
    incomingEdges: [],
    outgoingEdges: [],
    tags: ['witness', 'mark'],
    createdBy: 'kent',
    createdAt: new Date(now.getTime() - 24 * 60 * 60 * 1000),
    updatedAt: new Date(now.getTime() - 2 * 60 * 60 * 1000),
    notIngested: false,
    analysisRequired: false,
    ...overrides,
  };
}

/**
 * Create a mock edge.
 */
function createMockEdge(overrides: Partial<KBlockEdge> = {}): KBlockEdge {
  return {
    id: 'edge-' + Math.random().toString(36).substring(2, 9),
    sourceId: 'kb-source',
    targetId: 'kb-target',
    kind: 'derives_from',
    label: null,
    metadata: {},
    createdBy: 'system',
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}

/**
 * Default observer context.
 */
const defaultObserver: ObserverContext = {
  id: 'kent',
  type: 'user',
  principles: ['TASTEFUL', 'JOY_INDUCING', 'COMPOSABLE'],
  capabilities: ['edit', 'witness', 'navigate'],
  density: 'comfortable',
};

// Agent observer demonstrates read-only, compact agent projections
const agentObserver: ObserverContext = {
  id: 'k-gent',
  type: 'agent',
  principles: ['ETHICAL', 'GENERATIVE'],
  capabilities: ['read', 'witness'],
  density: 'compact',
};

// =============================================================================
// Rich Domain Mock Data
// =============================================================================

/**
 * Axiom: The foundational truth (Layer 1).
 */
const axiomKBlock = createMockKBlock({
  id: 'kb-axiom-001',
  path: 'spec/axioms/joy-over-efficiency.md',
  content: `# Joy Over Efficiency

A tasteful interaction that brings joy is worth 10x an efficient interaction that feels sterile.

Do not optimize joy away.

**Implications:**
- Performance is a constraint, not a goal
- Delight > speed (within reason)
- The user's smile is the real metric`,
  baseContent: `# Joy Over Efficiency

A tasteful interaction that brings joy is worth 10x an efficient interaction that feels sterile.`,
  zeroSeedLayer: 1,
  zeroSeedKind: 'axiom',
  confidence: 0.98,
  tags: ['axiom', 'philosophy', 'joy'],
  lineage: [],
  hasProof: true,
  toulminProof: {
    claim: 'Joy should take precedence over raw efficiency in agent design.',
    grounds: [
      'Users report higher satisfaction with delightful but slower interactions',
      'Sterile efficiency leads to tool fatigue',
      'Joy creates lasting engagement; speed creates transactional relationships',
    ],
    warrant: 'User experience research shows emotional connection drives retention.',
    backing: 'Multiple studies (Nielsen, Aarron Walter) demonstrate emotional design impact.',
    qualifier: 'certainly',
    rebuttals: ['Does not apply to life-critical latency requirements'],
  },
});

/**
 * Value: Derived from axiom (Layer 2).
 */
const valueKBlock = createMockKBlock({
  id: 'kb-value-001',
  path: 'spec/values/tasteful-composition.md',
  content: `# Tasteful Composition

Agents compose like musical phrases, not LEGO blocks.
Each composition should feel inevitable in retrospect.

**Test:** Does this composition make me smile?`,
  baseContent: `# Tasteful Composition

Agents compose like musical phrases.`,
  zeroSeedLayer: 2,
  zeroSeedKind: 'value',
  confidence: 0.92,
  tags: ['value', 'composition', 'tasteful'],
  lineage: ['kb-axiom-001'],
  incomingEdges: [
    createMockEdge({ sourceId: 'kb-axiom-001', kind: 'derives_from', label: 'grounded in' }),
  ],
});

/**
 * Goal: Target state (Layer 3).
 */
const goalKBlock = createMockKBlock({
  id: 'kb-goal-001',
  path: 'spec/goals/constitutional-l3-trust.md',
  content: `# Goal: Achieve Constitutional L3 Trust

**Target Metrics:**
- Alignment score >= 0.9 for 30 consecutive days
- Violation rate < 1%
- Trust capital >= 1.0
- Zero ETHICAL violations

**Timeline:** Q1 2025`,
  baseContent: `# Goal: Achieve Constitutional L3 Trust`,
  zeroSeedLayer: 3,
  zeroSeedKind: 'goal',
  confidence: 0.78,
  tags: ['goal', 'trust', 'constitutional'],
  lineage: ['kb-value-001', 'kb-axiom-001'],
  incomingEdges: [
    createMockEdge({ sourceId: 'kb-value-001', kind: 'implements', label: 'achieves' }),
  ],
  outgoingEdges: [
    createMockEdge({ targetId: 'kb-service-001', kind: 'refines', label: 'operationalizes' }),
  ],
});

/**
 * Service: Implementation (Layer 5) - High loss for drama.
 */
const serviceKBlock = createMockKBlock({
  id: 'kb-service-001',
  path: 'services/witness/mark.py',
  content: `"""
Witness Mark Service

Records all decisions with cryptographic hashes.
Maintains immutable audit trail.
"""

class MarkStore:
    async def record(self, mark: Mark) -> MarkId:
        # Hash, store, broadcast
        pass`,
  baseContent: `"""
Witness Mark Service
"""

class MarkStore:
    pass`,
  zeroSeedLayer: 5,
  zeroSeedKind: null,
  confidence: 0.65,
  isolation: 'DIRTY',
  tags: ['service', 'witness', 'implementation'],
  lineage: ['kb-goal-001'],
  incomingEdges: [
    createMockEdge({ sourceId: 'kb-goal-001', kind: 'implements' }),
  ],
  outgoingEdges: [
    createMockEdge({ targetId: 'kb-impl-001', kind: 'refines' }),
  ],
});

/**
 * Conflicting K-Block for contradiction demos.
 */
const conflictingKBlock = createMockKBlock({
  id: 'kb-conflict-001',
  path: 'spec/protocols/feed-impl.md',
  content: `# Feed Implementation

**WARNING: SPEC DRIFT DETECTED**

Implementation added client-side ranking.
Spec says backend-only ranking.

Coherence: 35%`,
  baseContent: `# Feed Implementation

Spec says backend-only ranking.`,
  zeroSeedLayer: 4,
  isolation: 'CONFLICTING',
  confidence: 0.35,
  tags: ['drift', 'warning', 'feed'],
});

/**
 * Chat message from user.
 */
const chatUserKBlock = createMockKBlock({
  id: 'kb-chat-001',
  path: 'chats/session-001/msg-001.md',
  content: 'How do I add a new agent to the Town simulation?',
  baseContent: 'How do I add a new agent to the Town simulation?',
  zeroSeedLayer: null,
  createdBy: 'kent',
  tags: ['question', 'town'],
});

/**
 * Chat message from agent.
 */
const chatAgentKBlock = createMockKBlock({
  id: 'kb-chat-002',
  path: 'chats/session-001/msg-002.md',
  content: `To add a new agent, use the polynomial agent pattern:

1. Define your state machine in \`agents/your_agent/polynomial.py\`
2. Register with the Town operad via \`@town_citizen\` decorator
3. Run \`kg probe health --all\` to verify registration

Would you like me to create a template?`,
  baseContent: `To add a new agent, use the polynomial agent pattern.`,
  zeroSeedLayer: null,
  createdBy: 'k-gent',
  tags: ['answer', 'town', 'tutorial'],
});

/**
 * K-Block with Toulmin proof.
 */
const proofKBlock = createMockKBlock({
  id: 'kb-proof-001',
  path: 'spec/decisions/event-driven-architecture.md',
  content: `# Decision: Event-Driven Architecture

We adopt event-driven architecture for all agent state transitions.`,
  baseContent: `# Decision: Event-Driven Architecture`,
  zeroSeedLayer: 3,
  hasProof: true,
  tags: ['decision', 'architecture', 'events'],
  toulminProof: {
    claim: 'Event-driven architecture is the correct choice for kgents state management.',
    grounds: [
      'Agents require traceable state transitions for witness marks',
      'Composition is natural with event streams (morphisms)',
      'Decoupling enables heterarchical agent relationships',
      'Performance: async events scale better than sync calls',
    ],
    warrant: 'Traceable, composable systems require observable state transitions.',
    backing: 'Category theory shows morphisms (events) are fundamental; objects (state) are derived.',
    qualifier: 'probably',
    rebuttals: [
      'Simple scripts may not need event overhead',
      'Debugging event chains is harder than call stacks',
    ],
  },
});

/**
 * Genesis cascade hierarchy (for lineage demos).
 */
const genesisHierarchy = [
  createMockKBlock({
    id: 'kb-genesis-001',
    path: 'spec/axioms/composable.md',
    content: '# Composable: Agents are morphisms in a category.',
    baseContent: '# Composable',
    zeroSeedLayer: 1,
    lineage: [],
    tags: ['axiom'],
  }),
  createMockKBlock({
    id: 'kb-genesis-002',
    path: 'spec/values/composition-laws.md',
    content: '# Composition Laws: Associativity, identity, functoriality.',
    baseContent: '# Composition Laws',
    zeroSeedLayer: 2,
    lineage: ['kb-genesis-001'],
    tags: ['value'],
  }),
  createMockKBlock({
    id: 'kb-genesis-003',
    path: 'spec/goals/operad-validation.md',
    content: '# Goal: Validate operad laws at every composition.',
    baseContent: '# Goal: Validate operad laws',
    zeroSeedLayer: 3,
    lineage: ['kb-genesis-002', 'kb-genesis-001'],
    tags: ['goal'],
  }),
];

// =============================================================================
// Contradictions
// =============================================================================

const minorContradiction: Contradiction = {
  id: 'contra-001',
  kblockIds: ['kb-001', 'kb-002'],
  type: 'temporal',
  severity: 'minor',
  description: 'Updated timestamp predates creation timestamp.',
  resolution: 'Verify clock synchronization.',
};

const majorContradiction: Contradiction = {
  id: 'contra-002',
  kblockIds: ['kb-spec', 'kb-impl'],
  type: 'logical',
  severity: 'major',
  description: 'Implementation contradicts spec requirements.',
  resolution: 'Align implementation with spec or update spec.',
};

const criticalContradiction: Contradiction = {
  id: 'contra-003',
  kblockIds: ['kb-ethical', 'kb-action'],
  type: 'constitutional',
  severity: 'critical',
  description: 'Action violates ETHICAL principle.',
  resolution: 'Immediate review required.',
};

// =============================================================================
// Low Constitutional Weights
// =============================================================================

const lowConstitutionalWeights: ConstitutionalWeights = {
  tasteful: 0.3,
  curated: 0.4,
  ethical: 0.5,
  joyInducing: 0.2,
  composable: 0.6,
  heterarchical: 0.4,
  generative: 0.5,
};

// =============================================================================
// Story Helpers
// =============================================================================

const StoryContainer = ({
  children,
  maxWidth = '800px',
  dark = true,
}: {
  children: React.ReactNode;
  maxWidth?: string;
  dark?: boolean;
}) => (
  <div
    style={{
      padding: '24px',
      background: dark ? 'var(--surface-0, #141418)' : 'var(--surface-1, #1a1a1f)',
      borderRadius: '8px',
      maxWidth,
    }}
  >
    {children}
  </div>
);

// =============================================================================
// Meta
// =============================================================================

const meta: Meta<typeof KBlockProjection> = {
  title: 'Primitives/KBlockProjection',
  component: KBlockProjection,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
## KBlockProjection - Universal K-Block Renderer

"The projection is not a view. The projection IS the reality."

**9 Projection Modes:**
- **graph** - Hypergraph node (force-directed, spatial)
- **feed** - Chronological stream item
- **chat** - Conversation message bubble
- **portal** - Expanded full detail view
- **genesis** - Zero Seed lineage cascade
- **card** - Compact summary card
- **inline** - Minimal inline text
- **diff** - Side-by-side content comparison
- **proof** - Toulmin argument structure

**Shared Indicators (All Projections):**
- **Galois Loss** - Coherence drift indicator (warns at >20%)
- **Contradiction Badge** - Logical/temporal/constitutional conflicts
- **Constitutional Score** - Principle alignment (warns at <60%)
- **Proof Badge** - Indicates Toulmin proof attached

**Design Philosophy:** STARK BIOME
- 90% steel (humble frame)
- 10% earned glow (content shines)
        `,
      },
    },
  },
  argTypes: {
    projection: {
      control: 'select',
      options: ['graph', 'feed', 'chat', 'portal', 'genesis', 'card', 'inline', 'diff', 'proof'],
      description: 'Projection surface mode',
    },
    depth: {
      control: { type: 'range', min: 0, max: 5 },
      description: 'Depth in graph (for recursion limits)',
    },
  },
};

export default meta;
type Story = StoryObj<typeof KBlockProjection>;

// =============================================================================
// Main Dispatcher Stories
// =============================================================================

export const Default: Story = {
  name: 'Default (Card)',
  args: {
    kblock: valueKBlock,
    observer: defaultObserver,
    projection: 'card',
  },
  render: (args) => (
    <StoryContainer>
      <KBlockProjection {...args} />
    </StoryContainer>
  ),
};

export const AllProjections: StoryObj = {
  name: 'All 9 Projections',
  render: () => {
    const projections: ProjectionMode[] = [
      'graph', 'feed', 'chat', 'portal', 'genesis', 'card', 'inline', 'diff', 'proof',
    ];
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {projections.map((projection) => (
          <StoryContainer key={projection} maxWidth="100%">
            <div style={{ marginBottom: '12px', color: '#C4A77D', fontFamily: 'monospace', fontSize: '14px' }}>
              projection="{projection}"
            </div>
            <KBlockProjection
              kblock={projection === 'proof' ? proofKBlock : projection === 'diff' ? serviceKBlock : valueKBlock}
              observer={defaultObserver}
              projection={projection}
              depth={projection === 'genesis' ? 1 : 0}
            />
          </StoryContainer>
        ))}
      </div>
    );
  },
};

// =============================================================================
// Individual Projection Stories
// =============================================================================

export const GraphProjection: Story = {
  name: 'Projection: Graph (Hypergraph Node)',
  args: {
    kblock: createMockKBlock({
      ...goalKBlock,
      incomingEdges: [
        createMockEdge({ sourceId: 'kb-value-001', kind: 'derives_from' }),
        createMockEdge({ sourceId: 'kb-axiom-001', kind: 'grounds' }),
      ],
      outgoingEdges: [
        createMockEdge({ targetId: 'kb-service-001', kind: 'implements' }),
        createMockEdge({ targetId: 'kb-service-002', kind: 'implements' }),
        createMockEdge({ targetId: 'kb-test-001', kind: 'verified_by' }),
      ],
    }),
    observer: defaultObserver,
    projection: 'graph',
  },
  render: (args) => (
    <StoryContainer>
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Graph projection shows K-Block as a hypergraph node with edge counts and isolation state.
      </p>
      <KBlockProjection {...args} />
    </StoryContainer>
  ),
};

export const FeedProjection: Story = {
  name: 'Projection: Feed (Stream Item)',
  args: {
    kblock: serviceKBlock,
    observer: defaultObserver,
    projection: 'feed',
  },
  render: (args) => (
    <StoryContainer maxWidth="600px">
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Feed projection shows K-Block as a chronological stream item with layer badge, preview, and metadata.
      </p>
      <KBlockProjection {...args} />
    </StoryContainer>
  ),
};

export const ChatProjection: Story = {
  name: 'Projection: Chat (Conversation)',
  args: {
    kblock: chatUserKBlock,
    observer: defaultObserver,
    projection: 'chat',
  },
  render: () => (
    <StoryContainer maxWidth="600px">
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Chat projection renders K-Blocks as conversation messages. User messages align right; agent messages align left.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <KBlockProjection kblock={chatUserKBlock} observer={defaultObserver} projection="chat" />
        <KBlockProjection kblock={chatAgentKBlock} observer={defaultObserver} projection="chat" />
      </div>
    </StoryContainer>
  ),
};

export const PortalProjection: Story = {
  name: 'Projection: Portal (Full Detail)',
  args: {
    kblock: createMockKBlock({
      ...goalKBlock,
      incomingEdges: [
        createMockEdge({ sourceId: 'kb-value-001', kind: 'derives_from' }),
      ],
      outgoingEdges: [
        createMockEdge({ targetId: 'kb-service-001', kind: 'implements' }),
      ],
    }),
    observer: defaultObserver,
    projection: 'portal',
  },
  render: (args) => (
    <StoryContainer maxWidth="100%">
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Portal projection shows full K-Block details: metadata, content, edges, tags, and lineage.
      </p>
      <KBlockProjection {...args} />
    </StoryContainer>
  ),
};

export const GenesisProjection: Story = {
  name: 'Projection: Genesis (Zero Seed Cascade)',
  render: () => (
    <StoryContainer maxWidth="600px">
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Genesis projection shows K-Block lineage as a cascade. Depth indentation reveals the Zero Seed hierarchy.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {genesisHierarchy.map((kb, idx) => (
          <KBlockProjection
            key={kb.id}
            kblock={kb}
            observer={defaultObserver}
            projection="genesis"
            depth={idx}
          />
        ))}
      </div>
    </StoryContainer>
  ),
};

export const CardProjection: Story = {
  name: 'Projection: Card (Compact Summary)',
  args: {
    kblock: valueKBlock,
    observer: defaultObserver,
    projection: 'card',
  },
  render: (args) => (
    <StoryContainer>
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Card projection shows a compact summary with title, preview, author, and confidence.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        <KBlockProjection {...args} />
        <KBlockProjection kblock={goalKBlock} observer={defaultObserver} projection="card" />
        <KBlockProjection kblock={serviceKBlock} observer={defaultObserver} projection="card" />
      </div>
    </StoryContainer>
  ),
};

export const InlineProjection: Story = {
  name: 'Projection: Inline (Minimal Text)',
  render: () => (
    <StoryContainer>
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Inline projection shows just the title. Perfect for embedding in text or lists.
      </p>
      <p style={{ color: 'var(--text-primary, #E0E0E6)', fontSize: '14px', lineHeight: 1.6 }}>
        This decision is grounded in{' '}
        <KBlockProjection kblock={axiomKBlock} observer={defaultObserver} projection="inline" />{' '}
        and implements{' '}
        <KBlockProjection kblock={goalKBlock} observer={defaultObserver} projection="inline" />.
      </p>
    </StoryContainer>
  ),
};

export const DiffProjection: Story = {
  name: 'Projection: Diff (Side-by-Side)',
  args: {
    kblock: serviceKBlock,
    observer: defaultObserver,
    projection: 'diff',
  },
  render: (args) => (
    <StoryContainer maxWidth="100%">
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Diff projection shows side-by-side comparison between base content and current content.
      </p>
      <KBlockProjection {...args} />
    </StoryContainer>
  ),
};

export const ProofProjection: Story = {
  name: 'Projection: Proof (Toulmin Structure)',
  args: {
    kblock: proofKBlock,
    observer: defaultObserver,
    projection: 'proof',
  },
  render: (args) => (
    <StoryContainer maxWidth="700px">
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Proof projection shows the Toulmin argument structure: claim, grounds, warrant, backing, qualifiers, rebuttals.
      </p>
      <KBlockProjection {...args} />
    </StoryContainer>
  ),
};

export const ProofProjectionNoProof: Story = {
  name: 'Projection: Proof (No Proof Available)',
  args: {
    kblock: valueKBlock,
    observer: defaultObserver,
    projection: 'proof',
  },
  render: (args) => (
    <StoryContainer maxWidth="700px">
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        When a K-Block has no Toulmin proof, the proof projection shows a helpful message.
      </p>
      <KBlockProjection {...args} />
    </StoryContainer>
  ),
};

// =============================================================================
// Indicator Stories
// =============================================================================

export const GaloisLossIndicator: Story = {
  name: 'Indicator: Galois Loss',
  render: () => {
    const handleNavigateLoss = (direction: 'lower' | 'higher') => {
      // eslint-disable-next-line no-console
      console.log(`Navigate ${direction} in Galois hierarchy`);
    };
    return (
      <StoryContainer>
        <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
          Galois loss indicator appears when drift exceeds 20%. Click to navigate the layer hierarchy.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>Low loss (healthy):</div>
            <KBlockProjection
              kblock={axiomKBlock}
              observer={defaultObserver}
              projection="card"
              onNavigateLoss={handleNavigateLoss}
            />
          </div>
          <div>
            <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>Medium loss (warning):</div>
            <KBlockProjection
              kblock={serviceKBlock}
              observer={defaultObserver}
              projection="card"
              onNavigateLoss={handleNavigateLoss}
            />
          </div>
          <div>
            <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>High loss (critical):</div>
            <KBlockProjection
              kblock={conflictingKBlock}
              observer={defaultObserver}
              projection="card"
              onNavigateLoss={handleNavigateLoss}
            />
          </div>
        </div>
      </StoryContainer>
    );
  },
};

export const ContradictionBadge: Story = {
  name: 'Indicator: Contradiction Badge',
  render: () => (
    <StoryContainer>
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Contradiction badges show severity: minor (temporal), major (logical), critical (constitutional).
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>Minor (temporal):</div>
          <KBlockProjection
            kblock={valueKBlock}
            observer={defaultObserver}
            projection="card"
            contradiction={minorContradiction}
          />
        </div>
        <div>
          <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>Major (logical):</div>
          <KBlockProjection
            kblock={goalKBlock}
            observer={defaultObserver}
            projection="card"
            contradiction={majorContradiction}
          />
        </div>
        <div>
          <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>Critical (constitutional):</div>
          <KBlockProjection
            kblock={serviceKBlock}
            observer={defaultObserver}
            projection="card"
            contradiction={criticalContradiction}
          />
        </div>
      </div>
    </StoryContainer>
  ),
};

export const ConstitutionalScoreWarning: Story = {
  name: 'Indicator: Constitutional Score (Low)',
  render: () => (
    <StoryContainer>
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Constitutional score indicator appears when alignment drops below 60%.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>Normal (no indicator):</div>
          <KBlockProjection kblock={axiomKBlock} observer={defaultObserver} projection="card" />
        </div>
        <div>
          <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>Low constitutional alignment:</div>
          <KBlockProjection
            kblock={conflictingKBlock}
            observer={defaultObserver}
            projection="card"
            constitutionalWeights={lowConstitutionalWeights}
          />
        </div>
      </div>
    </StoryContainer>
  ),
};

export const ProofBadge: Story = {
  name: 'Indicator: Proof Badge',
  render: () => (
    <StoryContainer>
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Proof badge (checkmark) appears when a K-Block has a Toulmin proof attached.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>With proof:</div>
          <KBlockProjection kblock={axiomKBlock} observer={defaultObserver} projection="card" />
        </div>
        <div>
          <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>Without proof:</div>
          <KBlockProjection kblock={valueKBlock} observer={defaultObserver} projection="card" />
        </div>
      </div>
    </StoryContainer>
  ),
};

// =============================================================================
// Isolation State Stories
// =============================================================================

export const IsolationStates: Story = {
  name: 'Isolation States',
  render: () => (
    <StoryContainer>
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        K-Blocks have isolation states: PRISTINE, DIRTY, STALE, CONFLICTING, ENTANGLED.
        The left border color indicates state severity.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        {(['PRISTINE', 'DIRTY', 'STALE', 'CONFLICTING', 'ENTANGLED'] as const).map((isolation) => (
          <div key={isolation}>
            <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>{isolation}:</div>
            <KBlockProjection
              kblock={createMockKBlock({ isolation, path: `example/${isolation.toLowerCase()}.md` })}
              observer={defaultObserver}
              projection="card"
            />
          </div>
        ))}
      </div>
    </StoryContainer>
  ),
};

// =============================================================================
// Layer Stories
// =============================================================================

export const AllLayers: Story = {
  name: 'All 7 Zero Seed Layers',
  render: () => {
    const layers = [
      { layer: 1, kind: 'axiom', title: 'Joy Over Efficiency' },
      { layer: 2, kind: 'value', title: 'Tasteful Composition' },
      { layer: 3, kind: 'capability', title: 'Witness Everything' },
      { layer: 4, kind: 'domain', title: 'Agent Town Simulation' },
      { layer: 5, kind: 'service', title: 'Witness Mark Store' },
      { layer: 6, kind: 'construction', title: 'Feed Component' },
      { layer: 7, kind: 'implementation', title: 'mark.py' },
    ];

    return (
      <StoryContainer maxWidth="100%">
        <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
          Zero Seed hierarchy: L1 Axiom (purple) through L7 Implementation (violet).
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {layers.map(({ layer, kind, title }) => (
            <KBlockProjection
              key={layer}
              kblock={createMockKBlock({
                zeroSeedLayer: layer,
                zeroSeedKind: kind,
                path: `layer-${layer}/${title.toLowerCase().replace(/ /g, '-')}.md`,
                content: `Layer ${layer} (${kind}): ${title}`,
              })}
              observer={defaultObserver}
              projection="feed"
            />
          ))}
        </div>
      </StoryContainer>
    );
  },
};

// =============================================================================
// Interactive Stories
// =============================================================================

export const InteractiveWithWitness: Story = {
  name: 'Interactive: Witness Callback',
  render: () => {
    const Demo = () => {
      const [marks, setMarks] = useState<WitnessMark[]>([]);

      const handleWitness = (mark: WitnessMark) => {
        setMarks((prev) => [...prev, mark]);
      };

      return (
        <StoryContainer>
          <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
            The onWitness callback fires when witness marks are created.
            (Note: witness creation is handled by the projection components.)
          </p>
          <KBlockProjection
            kblock={goalKBlock}
            observer={defaultObserver}
            projection="portal"
            onWitness={handleWitness}
          />
          {marks.length > 0 && (
            <div style={{ marginTop: '16px', padding: '12px', background: '#1a1a1f', borderRadius: '4px' }}>
              <div style={{ color: '#C4A77D', fontSize: '12px', marginBottom: '8px' }}>Witness Marks:</div>
              {marks.map((mark) => (
                <div key={mark.id} style={{ color: '#8A8A94', fontSize: '12px' }}>
                  {mark.action} @ {mark.timestamp.toISOString()}
                </div>
              ))}
            </div>
          )}
        </StoryContainer>
      );
    };
    return <Demo />;
  },
};

export const ProjectionSwitcher: Story = {
  name: 'Interactive: Projection Switcher',
  render: () => {
    const Demo = () => {
      const [projection, setProjection] = useState<ProjectionMode>('card');
      const projections: ProjectionMode[] = [
        'graph', 'feed', 'chat', 'portal', 'genesis', 'card', 'inline', 'diff', 'proof',
      ];

      return (
        <StoryContainer maxWidth="100%">
          <div style={{ marginBottom: '16px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {projections.map((p) => (
              <button
                key={p}
                onClick={() => setProjection(p)}
                style={{
                  padding: '6px 12px',
                  background: projection === p ? '#C4A77D' : '#28282F',
                  color: projection === p ? '#141418' : '#E0E0E6',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontFamily: 'monospace',
                  fontSize: '12px',
                }}
              >
                {p}
              </button>
            ))}
          </div>
          <KBlockProjection
            kblock={projection === 'proof' ? proofKBlock : projection === 'diff' ? serviceKBlock : goalKBlock}
            observer={defaultObserver}
            projection={projection}
            depth={1}
          />
        </StoryContainer>
      );
    };
    return <Demo />;
  },
};

// =============================================================================
// Agent Observer Mode
// =============================================================================

export const AgentObserverView: Story = {
  name: 'Observer: Agent Mode (Compact)',
  render: () => (
    <StoryContainer>
      <div style={{ display: 'flex', gap: '24px', flexDirection: 'column' }}>
        <div>
          <h4 style={{ color: '#8A8A94', marginBottom: '8px', fontSize: '12px' }}>
            Human Observer (comfortable, full capabilities)
          </h4>
          <KBlockProjection
            kblock={goalKBlock}
            observer={defaultObserver}
            projection="card"
            depth={1}
          />
        </div>
        <div>
          <h4 style={{ color: '#8A8A94', marginBottom: '8px', fontSize: '12px' }}>
            Agent Observer (compact, read-only, ETHICAL+GENERATIVE principles)
          </h4>
          <KBlockProjection
            kblock={goalKBlock}
            observer={agentObserver}
            projection="card"
            depth={1}
          />
        </div>
      </div>
    </StoryContainer>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Demonstrates how the same K-Block renders differently for human vs agent observers. Agents see compact read-only views.',
      },
    },
  },
};

// =============================================================================
// Edge Cases
// =============================================================================

export const EmptyContent: Story = {
  name: 'Edge Case: Empty Content',
  render: () => (
    <StoryContainer>
      <KBlockProjection
        kblock={createMockKBlock({
          content: '',
          baseContent: '',
          path: 'empty.md',
        })}
        observer={defaultObserver}
        projection="card"
      />
    </StoryContainer>
  ),
};

export const LongContent: Story = {
  name: 'Edge Case: Long Content',
  render: () => (
    <StoryContainer maxWidth="600px">
      <KBlockProjection
        kblock={createMockKBlock({
          content: `# Very Long Content

This K-Block has an extremely long content body to test how the projections handle overflow.

${'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(20)}

## Section Two

${'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '.repeat(15)}

## Section Three

${'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris. '.repeat(10)}`,
          path: 'long-content.md',
        })}
        observer={defaultObserver}
        projection="feed"
      />
    </StoryContainer>
  ),
};

export const ManyTags: Story = {
  name: 'Edge Case: Many Tags',
  render: () => (
    <StoryContainer>
      <KBlockProjection
        kblock={createMockKBlock({
          tags: ['architecture', 'events', 'witness', 'category-theory', 'composition', 'operad', 'polynomial', 'sheaf', 'galois', 'constitutional'],
          path: 'many-tags.md',
        })}
        observer={defaultObserver}
        projection="feed"
      />
    </StoryContainer>
  ),
};

export const ManyEdges: Story = {
  name: 'Edge Case: Many Edges',
  render: () => (
    <StoryContainer>
      <KBlockProjection
        kblock={createMockKBlock({
          incomingEdges: Array.from({ length: 8 }, (_, i) =>
            createMockEdge({ sourceId: `kb-source-${i}`, kind: i % 2 === 0 ? 'derives_from' : 'implements' })
          ),
          outgoingEdges: Array.from({ length: 12 }, (_, i) =>
            createMockEdge({ targetId: `kb-target-${i}`, kind: i % 3 === 0 ? 'refines' : 'evidence_for' })
          ),
          path: 'many-edges.md',
        })}
        observer={defaultObserver}
        projection="graph"
      />
    </StoryContainer>
  ),
};

export const DeepLineage: Story = {
  name: 'Edge Case: Deep Lineage',
  render: () => (
    <StoryContainer>
      <KBlockProjection
        kblock={createMockKBlock({
          lineage: ['kb-parent-1', 'kb-grandparent-1', 'kb-great-grandparent-1', 'kb-ancestor-1', 'kb-ancestor-2'],
          path: 'deep-lineage.md',
        })}
        observer={defaultObserver}
        projection="portal"
      />
    </StoryContainer>
  ),
};

// =============================================================================
// Composition Stories
// =============================================================================

export const FeedWithMultipleItems: Story = {
  name: 'Composition: Feed Stream',
  render: () => (
    <StoryContainer maxWidth="600px">
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Multiple K-Blocks rendered as a feed stream.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
        <KBlockProjection kblock={axiomKBlock} observer={defaultObserver} projection="feed" />
        <KBlockProjection kblock={valueKBlock} observer={defaultObserver} projection="feed" />
        <KBlockProjection kblock={goalKBlock} observer={defaultObserver} projection="feed" />
        <KBlockProjection kblock={serviceKBlock} observer={defaultObserver} projection="feed" />
      </div>
    </StoryContainer>
  ),
};

export const CardGrid: Story = {
  name: 'Composition: Card Grid',
  render: () => (
    <StoryContainer maxWidth="100%">
      <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
        Multiple K-Blocks rendered as a responsive card grid.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        {[axiomKBlock, valueKBlock, goalKBlock, serviceKBlock, proofKBlock, conflictingKBlock].map((kb) => (
          <KBlockProjection key={kb.id} kblock={kb} observer={defaultObserver} projection="card" />
        ))}
      </div>
    </StoryContainer>
  ),
};

export const ChatConversation: Story = {
  name: 'Composition: Chat Conversation',
  render: () => {
    const messages = [
      createMockKBlock({ id: 'msg-1', content: 'What is the witness protocol?', createdBy: 'kent' }),
      createMockKBlock({ id: 'msg-2', content: 'The witness protocol records all decisions with cryptographic hashes, creating an immutable audit trail.', createdBy: 'k-gent' }),
      createMockKBlock({ id: 'msg-3', content: 'How do I create a witness mark?', createdBy: 'kent' }),
      createMockKBlock({ id: 'msg-4', content: 'Use `km "Your action description"` to create a witness mark. The mark captures the action, timestamp, and context.', createdBy: 'k-gent' }),
      createMockKBlock({ id: 'msg-5', content: 'Perfect, thanks!', createdBy: 'kent' }),
    ];

    return (
      <StoryContainer maxWidth="600px">
        <p style={{ color: '#8A8A94', fontSize: '13px', marginBottom: '16px' }}>
          Chat conversation with alternating user and agent messages.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {messages.map((msg) => (
            <KBlockProjection key={msg.id} kblock={msg} observer={defaultObserver} projection="chat" />
          ))}
        </div>
      </StoryContainer>
    );
  },
};
