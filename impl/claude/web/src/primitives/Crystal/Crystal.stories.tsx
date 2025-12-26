/**
 * Crystal.stories.tsx - Memory Compression Visualization
 *
 * Stories for the Crystal primitive family:
 * - MoodIndicator: 7D affective signature (dots/bars)
 * - CrystalCard: Single crystal display with expandable details
 * - CrystalHierarchy: Multi-level crystal tree (SESSION -> DAY -> WEEK -> EPOCH)
 *
 * STARK BIOME Aesthetic:
 * - 90% Steel: Cool industrial backgrounds, frames, containers
 * - 10% Earned Glow: Organic accents for special moments (crystallization, insight)
 *
 * Philosophy: "Marks are observations. Crystals are insights."
 * The frame is humble. The content glows.
 *
 * @see MetaReflection.mdx - Journey 4 documentation
 * @see impl/claude/services/witness/crystal.py - Backend schema
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { MoodIndicator } from './MoodIndicator';
import { CrystalCard } from './CrystalCard';
import { CrystalHierarchy } from './CrystalHierarchy';
import type { Crystal, MoodVector, CrystalLevel } from '../../types/crystal';

// =============================================================================
// Mock Data Factories - kgents Domain
// =============================================================================

/**
 * Create a MoodVector with meaningful defaults.
 * Each dimension represents an affective signature aspect.
 */
function createMood(overrides: Partial<MoodVector> = {}): MoodVector {
  return {
    warmth: 0.5,      // Cold/clinical <-> Warm/engaging
    weight: 0.5,      // Light/playful <-> Heavy/serious
    tempo: 0.5,       // Slow/deliberate <-> Fast/urgent
    texture: 0.5,     // Smooth/flowing <-> Rough/struggling
    brightness: 0.5,  // Dim/frustrated <-> Bright/joyful
    saturation: 0.5,  // Muted/routine <-> Vivid/intense
    complexity: 0.5,  // Simple/focused <-> Complex/branching
    ...overrides,
  };
}

/**
 * Create a Crystal with meaningful kgents domain context.
 */
function createCrystal(overrides: Partial<Crystal> = {}): Crystal {
  const now = new Date();
  return {
    id: `crystal-${Math.random().toString(36).slice(2, 8)}`,
    level: 'SESSION',
    insight: 'Implemented categorical composition for agent behaviors',
    significance: 'PolyAgent + Operad + Sheaf pattern enables domain-agnostic composition',
    mood: createMood(),
    confidence: 0.85,
    sourceMarkIds: ['m1', 'm2', 'm3', 'm4', 'm5'],
    sourceCrystalIds: [],
    principles: ['composable', 'generative'],
    topics: ['categorical', 'agents', 'architecture'],
    crystallizedAt: now.toISOString(),
    compressionRatio: 5.0,
    ...overrides,
  };
}

// =============================================================================
// Preset Moods - Domain-Grounded Affective Signatures
// =============================================================================

/** Deep focused work - warm, weighty, slow, smooth, bright */
const MOOD_DEEP_FOCUS = createMood({
  warmth: 0.7,
  weight: 0.8,
  tempo: 0.3,
  texture: 0.2,
  brightness: 0.9,
  saturation: 0.8,
  complexity: 0.4,
});

/** Rush implementation - cool, light, fast, rough, dim */
const MOOD_RUSHED = createMood({
  warmth: 0.3,
  weight: 0.2,
  tempo: 0.95,
  texture: 0.8,
  brightness: 0.4,
  saturation: 0.9,
  complexity: 0.7,
});

/** Breakthrough moment - maximum warmth and brightness */
const MOOD_BREAKTHROUGH = createMood({
  warmth: 0.95,
  weight: 0.6,
  tempo: 0.7,
  texture: 0.1,
  brightness: 1.0,
  saturation: 1.0,
  complexity: 0.3,
});

/** Struggling with complexity - rough, complex, dim */
const MOOD_STRUGGLING = createMood({
  warmth: 0.4,
  weight: 0.9,
  tempo: 0.4,
  texture: 0.9,
  brightness: 0.3,
  saturation: 0.6,
  complexity: 0.95,
});

/** Neutral baseline - all dimensions at midpoint */
const MOOD_NEUTRAL = createMood();

// =============================================================================
// Preset Crystals - kgents Domain Context
// =============================================================================

const CRYSTAL_SESSION_CATEGORICAL = createCrystal({
  id: 'c-session-1',
  level: 'SESSION',
  insight: 'Categorical composition enables domain-agnostic agent behaviors',
  significance: 'PolyAgent + Operad + Sheaf pattern is the ground truth',
  mood: MOOD_DEEP_FOCUS,
  confidence: 0.92,
  sourceMarkIds: ['m1', 'm2', 'm3', 'm4', 'm5', 'm6'],
  principles: ['composable', 'generative', 'heterarchical'],
  topics: ['categorical', 'polyagent', 'operad', 'sheaf'],
  compressionRatio: 6.0,
  crystallizedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
});

const CRYSTAL_SESSION_UI = createCrystal({
  id: 'c-session-2',
  level: 'SESSION',
  insight: 'STARK BIOME aesthetic: 90% steel, 10% earned glow',
  significance: 'The frame is humble. The content glows.',
  mood: MOOD_BREAKTHROUGH,
  confidence: 0.88,
  sourceMarkIds: ['m7', 'm8', 'm9', 'm10'],
  principles: ['tasteful', 'joy-inducing'],
  topics: ['design', 'ui', 'stark-biome'],
  compressionRatio: 4.0,
  crystallizedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
});

const CRYSTAL_SESSION_AGENTESE = createCrystal({
  id: 'c-session-3',
  level: 'SESSION',
  insight: 'AGENTESE path structure enables universal protocol semantics',
  significance: '@node decorator + JIT compilation = zero boilerplate',
  mood: MOOD_DEEP_FOCUS,
  confidence: 0.78,
  sourceMarkIds: ['m11', 'm12', 'm13'],
  principles: ['composable', 'curated'],
  topics: ['agentese', 'protocol', 'routing'],
  compressionRatio: 3.0,
  crystallizedAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
});

const CRYSTAL_DAY_INTEGRATION = createCrystal({
  id: 'c-day-1',
  level: 'DAY',
  insight: 'Full vertical slice from persistence to projection',
  significance: 'Metaphysical fullstack: every agent is a fullstack agent',
  mood: createMood({ warmth: 0.8, brightness: 0.85, complexity: 0.6 }),
  confidence: 0.90,
  sourceMarkIds: [],
  sourceCrystalIds: ['c-session-1', 'c-session-2', 'c-session-3'],
  principles: ['composable', 'heterarchical', 'generative'],
  topics: ['architecture', 'integration', 'fullstack'],
  compressionRatio: 3.0,
  crystallizedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
});

const CRYSTAL_DAY_WITNESS = createCrystal({
  id: 'c-day-2',
  level: 'DAY',
  insight: 'Witness marks provide provenance for all decisions',
  significance: 'The proof IS the decision. The mark IS the witness.',
  mood: createMood({ warmth: 0.7, weight: 0.7, brightness: 0.8 }),
  confidence: 0.85,
  sourceMarkIds: [],
  sourceCrystalIds: ['c-session-4', 'c-session-5'],
  principles: ['ethical', 'curated'],
  topics: ['witness', 'provenance', 'trust'],
  compressionRatio: 2.0,
  crystallizedAt: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
});

const CRYSTAL_WEEK_PATTERNS = createCrystal({
  id: 'c-week-1',
  level: 'WEEK',
  insight: 'Theme emerged: making the implicit explicit',
  significance: 'Constitutional primitives are the through-line for all UI',
  mood: createMood({ warmth: 0.85, brightness: 0.9, saturation: 0.7 }),
  confidence: 0.93,
  sourceMarkIds: [],
  sourceCrystalIds: ['c-day-1', 'c-day-2', 'c-day-3'],
  principles: ['tasteful', 'composable', 'generative'],
  topics: ['patterns', 'constitutional', 'ui-primitives'],
  compressionRatio: 3.0,
  periodStart: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
  periodEnd: new Date().toISOString(),
  crystallizedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
});

const CRYSTAL_EPOCH_FOUNDATION = createCrystal({
  id: 'c-epoch-1',
  level: 'EPOCH',
  insight: 'The categorical foundation was worth the investment',
  significance: 'PolyAgent + Operad + Sheaf enables everything else',
  mood: createMood({ warmth: 0.95, brightness: 1.0, saturation: 0.9, complexity: 0.3 }),
  confidence: 0.97,
  sourceMarkIds: [],
  sourceCrystalIds: ['c-week-1', 'c-week-2', 'c-week-3', 'c-week-4'],
  principles: ['composable', 'generative', 'heterarchical', 'tasteful'],
  topics: ['categorical', 'foundation', 'architecture', 'kgents'],
  compressionRatio: 4.0,
  periodStart: '2025-09-01T00:00:00Z',
  periodEnd: '2025-12-25T00:00:00Z',
  crystallizedAt: '2025-12-25T00:00:00Z',
});

// Full crystal collection for hierarchy stories
const ALL_CRYSTALS: Crystal[] = [
  CRYSTAL_SESSION_CATEGORICAL,
  CRYSTAL_SESSION_UI,
  CRYSTAL_SESSION_AGENTESE,
  CRYSTAL_DAY_INTEGRATION,
  CRYSTAL_DAY_WITNESS,
  CRYSTAL_WEEK_PATTERNS,
  CRYSTAL_EPOCH_FOUNDATION,
];

// =============================================================================
// STARK BIOME Surface Tokens
// =============================================================================

const S = {
  s0: { background: 'var(--surface-0, #0a0a0c)' },
  s1: { background: 'var(--surface-1, #141418)' },
  s2: { background: 'var(--surface-2, #1c1c22)' },
  s3: { background: 'var(--surface-3, #28282f)' },
};

const card: React.CSSProperties = {
  borderRadius: 'var(--radius-bare, 2px)',
  border: '1px solid var(--border-subtle, #28282f)',
  padding: '1rem',
};

const label: React.CSSProperties = {
  margin: '0 0 0.75rem',
  color: 'var(--text-secondary)',
  fontSize: '0.75rem',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

const sectionTitle: React.CSSProperties = {
  fontSize: '0.875rem',
  fontWeight: 600,
  color: 'var(--text-primary)',
  marginBottom: '0.75rem',
  paddingBottom: '0.5rem',
  borderBottom: '1px solid var(--surface-3)',
};

// =============================================================================
// Meta Configuration
// =============================================================================

const meta: Meta = {
  title: 'Primitives/Crystal',
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: `
# Crystal Primitives

Memory compression visualization for kgents. Crystals compress witness marks into reusable insights.

## Philosophy

> "Marks are observations. Crystals are insights."

Experience crystallizes at multiple temporal scales:
- **SESSION**: Minutes (5-20 marks -> 1 crystal)
- **DAY**: Hours (2-5 session crystals -> 1 day crystal)
- **WEEK**: Days (5-7 day crystals -> 1 week crystal)
- **EPOCH**: Months (major milestones, retrospectives)

## STARK BIOME Aesthetic

- **90% Steel**: Cool industrial backgrounds, frames
- **10% Earned Glow**: Organic accents for crystallization moments
- **Level Colors**: SESSION=steel, DAY=sage, WEEK=lichen, EPOCH=amber

## Components

1. **MoodIndicator**: 7D affective signature (warmth, weight, tempo, texture, brightness, saturation, complexity)
2. **CrystalCard**: Single crystal with insight, significance, mood, confidence ring
3. **CrystalHierarchy**: Full hierarchy visualization with collapsible levels

## Crystal Laws

1. Mark Immutability: Marks are never deleted
2. Provenance Chain: Every crystal references sources
3. Level Consistency: Level N only sources from level N-1
4. Compression Monotonicity: Higher levels are denser
        `,
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;

// =============================================================================
// MoodIndicator Stories
// =============================================================================

export const MoodDotsSmall: StoryObj = {
  name: 'MoodIndicator / Dots / Small',
  render: () => (
    <div style={{ ...S.s1, ...card, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <h4 style={sectionTitle}>Mood Indicator - Dots Variant (Small)</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MoodIndicator mood={MOOD_DEEP_FOCUS} size="small" variant="dots" />
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>Deep Focus</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MoodIndicator mood={MOOD_RUSHED} size="small" variant="dots" />
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>Rushed</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MoodIndicator mood={MOOD_BREAKTHROUGH} size="small" variant="dots" />
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>Breakthrough</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MoodIndicator mood={MOOD_STRUGGLING} size="small" variant="dots" />
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>Struggling</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MoodIndicator mood={MOOD_NEUTRAL} size="small" variant="dots" />
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>Neutral</span>
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Small dots variant. Each dot represents one of 7 affective dimensions. Intensity 0-3 maps to opacity and glow.',
      },
    },
  },
};

export const MoodDotsMedium: StoryObj = {
  name: 'MoodIndicator / Dots / Medium',
  render: () => (
    <div style={{ ...S.s1, ...card, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <h4 style={sectionTitle}>Mood Indicator - Dots Variant (Medium)</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MoodIndicator mood={MOOD_DEEP_FOCUS} size="medium" variant="dots" />
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Deep Focus</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MoodIndicator mood={MOOD_BREAKTHROUGH} size="medium" variant="dots" />
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Breakthrough</span>
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Medium dots variant (default). Good for inline display with crystal cards.',
      },
    },
  },
};

export const MoodDotsLarge: StoryObj = {
  name: 'MoodIndicator / Dots / Large',
  render: () => (
    <div style={{ ...S.s1, ...card, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <h4 style={sectionTitle}>Mood Indicator - Dots Variant (Large)</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MoodIndicator mood={MOOD_DEEP_FOCUS} size="large" variant="dots" />
          <span style={{ color: 'var(--text-secondary)' }}>Deep Focus - warm, deliberate, bright</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <MoodIndicator mood={MOOD_BREAKTHROUGH} size="large" variant="dots" />
          <span style={{ color: 'var(--text-secondary)' }}>Breakthrough - maximum warmth and glow</span>
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Large dots variant. Use for detail views or standalone mood displays.',
      },
    },
  },
};

export const MoodBars: StoryObj = {
  name: 'MoodIndicator / Bars Variant',
  render: () => (
    <div style={{ ...S.s1, ...card, display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '300px' }}>
      <h4 style={sectionTitle}>Mood Indicator - Bars Variant</h4>
      <div>
        <p style={label}>Deep Focus</p>
        <MoodIndicator mood={MOOD_DEEP_FOCUS} size="medium" variant="bars" />
      </div>
      <div>
        <p style={label}>Rushed</p>
        <MoodIndicator mood={MOOD_RUSHED} size="medium" variant="bars" />
      </div>
      <div>
        <p style={label}>Breakthrough</p>
        <MoodIndicator mood={MOOD_BREAKTHROUGH} size="medium" variant="bars" />
      </div>
      <div>
        <p style={label}>Struggling</p>
        <MoodIndicator mood={MOOD_STRUGGLING} size="medium" variant="bars" />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Bars variant shows 7 horizontal progress bars. Better for detailed mood inspection.',
      },
    },
  },
};

export const MoodBarsSizes: StoryObj = {
  name: 'MoodIndicator / Bars / Sizes',
  render: () => (
    <div style={{ ...S.s1, ...card, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
      <div>
        <p style={label}>Small</p>
        <MoodIndicator mood={MOOD_DEEP_FOCUS} size="small" variant="bars" />
      </div>
      <div>
        <p style={label}>Medium</p>
        <MoodIndicator mood={MOOD_DEEP_FOCUS} size="medium" variant="bars" />
      </div>
      <div>
        <p style={label}>Large</p>
        <MoodIndicator mood={MOOD_DEEP_FOCUS} size="large" variant="bars" />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Bars variant in all three sizes. Bar height increases with size.',
      },
    },
  },
};

// =============================================================================
// CrystalCard Stories
// =============================================================================

export const CardSession: StoryObj = {
  name: 'CrystalCard / SESSION Level',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem', maxWidth: '500px' }}>
      <h4 style={{ ...sectionTitle, color: 'var(--color-steel-300)' }}>SESSION Crystal</h4>
      <CrystalCard crystal={CRYSTAL_SESSION_CATEGORICAL} expandable />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'SESSION level crystal. Created from marks within a single session. Click to expand details.',
      },
    },
  },
};

export const CardDay: StoryObj = {
  name: 'CrystalCard / DAY Level',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem', maxWidth: '500px' }}>
      <h4 style={{ ...sectionTitle, color: 'var(--color-life-sage)' }}>DAY Crystal</h4>
      <CrystalCard crystal={CRYSTAL_DAY_INTEGRATION} expandable />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'DAY level crystal. Aggregates session crystals from a 24-hour period.',
      },
    },
  },
};

export const CardWeek: StoryObj = {
  name: 'CrystalCard / WEEK Level',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem', maxWidth: '500px' }}>
      <h4 style={{ ...sectionTitle, color: 'var(--color-glow-lichen)' }}>WEEK Crystal</h4>
      <CrystalCard crystal={CRYSTAL_WEEK_PATTERNS} expandable />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'WEEK level crystal. Themes emerge from daily patterns.',
      },
    },
  },
};

export const CardEpoch: StoryObj = {
  name: 'CrystalCard / EPOCH Level',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem', maxWidth: '500px' }}>
      <h4 style={{ ...sectionTitle, color: 'var(--color-glow-amber)' }}>EPOCH Crystal</h4>
      <CrystalCard crystal={CRYSTAL_EPOCH_FOUNDATION} expandable />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'EPOCH level crystal. Major insights spanning months. Maximum earned glow.',
      },
    },
  },
};

export const CardAllLevels: StoryObj = {
  name: 'CrystalCard / All Levels Comparison',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem' }}>
      <h4 style={sectionTitle}>Crystal Levels - STARK BIOME Color Progression</h4>
      <p style={{ ...label, marginBottom: '1rem' }}>
        SESSION=steel-300 | DAY=life-sage | WEEK=glow-lichen | EPOCH=glow-amber
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
        <CrystalCard crystal={CRYSTAL_SESSION_CATEGORICAL} expandable />
        <CrystalCard crystal={CRYSTAL_DAY_INTEGRATION} expandable />
        <CrystalCard crystal={CRYSTAL_WEEK_PATTERNS} expandable />
        <CrystalCard crystal={CRYSTAL_EPOCH_FOUNDATION} expandable />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All four crystal levels side by side. Notice the color progression from steel to amber as temporal scope increases.',
      },
    },
  },
};

export const CardNotExpandable: StoryObj = {
  name: 'CrystalCard / Non-Expandable',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem', maxWidth: '500px' }}>
      <h4 style={sectionTitle}>Non-Expandable Card</h4>
      <CrystalCard crystal={CRYSTAL_SESSION_UI} expandable={false} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Card with expandable=false. No cursor pointer, no expansion on click.',
      },
    },
  },
};

export const CardConfidenceLevels: StoryObj = {
  name: 'CrystalCard / Confidence Ring Variants',
  render: () => {
    const makeConfidenceCrystal = (confidence: number, label: string): Crystal => ({
      ...CRYSTAL_SESSION_CATEGORICAL,
      id: `c-conf-${confidence}`,
      confidence,
      insight: `${label} confidence crystal (${(confidence * 100).toFixed(0)}%)`,
    });

    return (
      <div style={{ ...S.s0, padding: '1.5rem' }}>
        <h4 style={sectionTitle}>Confidence Ring Progression</h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '500px' }}>
          <CrystalCard crystal={makeConfidenceCrystal(0.25, 'Low')} expandable={false} />
          <CrystalCard crystal={makeConfidenceCrystal(0.50, 'Medium')} expandable={false} />
          <CrystalCard crystal={makeConfidenceCrystal(0.75, 'High')} expandable={false} />
          <CrystalCard crystal={makeConfidenceCrystal(0.95, 'Very High')} expandable={false} />
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'The confidence ring (SVG circle) fills proportionally to confidence value.',
      },
    },
  },
};

// =============================================================================
// CrystalHierarchy Stories
// =============================================================================

export const HierarchyTimeline: StoryObj = {
  name: 'CrystalHierarchy / Timeline',
  render: () => {
    const [selected, setSelected] = useState<Crystal | null>(null);

    return (
      <div style={{ ...S.s0, padding: '1.5rem', minWidth: '600px' }}>
        <h4 style={sectionTitle}>Crystal Hierarchy - Timeline Variant</h4>
        <CrystalHierarchy
          crystals={ALL_CRYSTALS}
          variant="timeline"
          onCrystalSelect={(c) => setSelected(c)}
        />
        {selected && (
          <div style={{ ...S.s2, ...card, marginTop: '1rem' }}>
            <p style={label}>Selected Crystal</p>
            <p style={{ color: 'var(--text-primary)', margin: 0 }}>
              [{selected.level}] {selected.insight}
            </p>
          </div>
        )}
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Full hierarchy with all crystal levels. Click headers to collapse/expand. Click cards to select.',
      },
    },
  },
};

export const HierarchyTree: StoryObj = {
  name: 'CrystalHierarchy / Tree',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem', minWidth: '600px' }}>
      <h4 style={sectionTitle}>Crystal Hierarchy - Tree Variant</h4>
      <CrystalHierarchy
        crystals={ALL_CRYSTALS}
        variant="tree"
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Tree variant for hierarchical parent-child visualization.',
      },
    },
  },
};

export const HierarchyInitialCollapsed: StoryObj = {
  name: 'CrystalHierarchy / Initially Collapsed',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem', minWidth: '600px' }}>
      <h4 style={sectionTitle}>Hierarchy with SESSION Collapsed</h4>
      <p style={{ ...label, marginBottom: '1rem' }}>
        initialCollapsed={'{'}['SESSION']{'}'}
      </p>
      <CrystalHierarchy
        crystals={ALL_CRYSTALS}
        initialCollapsed={['SESSION']}
        variant="timeline"
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Start with SESSION level collapsed to show higher-level insights first.',
      },
    },
  },
};

export const HierarchyEmpty: StoryObj = {
  name: 'CrystalHierarchy / Empty State',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem', minWidth: '400px' }}>
      <h4 style={sectionTitle}>Empty Hierarchy</h4>
      <CrystalHierarchy crystals={[]} variant="timeline" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Empty state with hint to use :crystallize command.',
      },
    },
  },
};

export const HierarchySessionOnly: StoryObj = {
  name: 'CrystalHierarchy / Session Only',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem', minWidth: '600px' }}>
      <h4 style={sectionTitle}>Only SESSION Crystals</h4>
      <CrystalHierarchy
        crystals={[
          CRYSTAL_SESSION_CATEGORICAL,
          CRYSTAL_SESSION_UI,
          CRYSTAL_SESSION_AGENTESE,
        ]}
        variant="timeline"
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Hierarchy with only SESSION level populated. Other levels show count 0.',
      },
    },
  },
};

// =============================================================================
// Composition Stories
// =============================================================================

export const CompositionMoodInCard: StoryObj = {
  name: 'Composition / Mood in Card Context',
  render: () => (
    <div style={{ ...S.s0, padding: '1.5rem' }}>
      <h4 style={sectionTitle}>Mood Indicators in Card Context</h4>
      <p style={{ ...label, marginBottom: '1rem' }}>
        MoodIndicator appears in CrystalCard footer with size="small" variant="dots"
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', maxWidth: '800px' }}>
        <CrystalCard
          crystal={{
            ...CRYSTAL_SESSION_CATEGORICAL,
            mood: MOOD_DEEP_FOCUS,
            insight: 'Deep focus session on categorical patterns',
          }}
          expandable
        />
        <CrystalCard
          crystal={{
            ...CRYSTAL_SESSION_UI,
            mood: MOOD_BREAKTHROUGH,
            insight: 'Breakthrough moment in STARK BIOME design',
          }}
          expandable
        />
        <CrystalCard
          crystal={{
            ...CRYSTAL_SESSION_AGENTESE,
            mood: MOOD_RUSHED,
            insight: 'Rushed implementation of AGENTESE routing',
          }}
          expandable
        />
        <CrystalCard
          crystal={{
            ...CRYSTAL_DAY_INTEGRATION,
            mood: MOOD_STRUGGLING,
            insight: 'Struggled with integration complexity',
          }}
          expandable
        />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'MoodIndicator composes naturally within CrystalCard footer. Different moods visible at a glance.',
      },
    },
  },
};

export const CompositionCrystalDashboard: StoryObj = {
  name: 'Composition / Crystal Dashboard',
  render: () => {
    const [selectedCrystal, setSelectedCrystal] = useState<Crystal | null>(null);

    return (
      <div style={{ ...S.s0, padding: '1.5rem' }}>
        <h4 style={sectionTitle}>Crystal Dashboard - Meta Reflection View</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '1.5rem' }}>
          {/* Main hierarchy */}
          <div>
            <CrystalHierarchy
              crystals={ALL_CRYSTALS}
              onCrystalSelect={(c) => setSelectedCrystal(c)}
              initialCollapsed={['SESSION']}
              variant="timeline"
            />
          </div>

          {/* Detail panel */}
          <div style={{ ...S.s1, ...card }}>
            <h5 style={label}>Selected Crystal Details</h5>
            {selectedCrystal ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <span style={{ ...label, display: 'block', marginBottom: '0.25rem' }}>Level</span>
                  <span style={{ color: 'var(--text-primary)' }}>{selectedCrystal.level}</span>
                </div>
                <div>
                  <span style={{ ...label, display: 'block', marginBottom: '0.25rem' }}>Confidence</span>
                  <span style={{ color: 'var(--text-primary)' }}>
                    {(selectedCrystal.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div>
                  <span style={{ ...label, display: 'block', marginBottom: '0.25rem' }}>Mood Signature</span>
                  <MoodIndicator mood={selectedCrystal.mood} size="large" variant="bars" />
                </div>
                <div>
                  <span style={{ ...label, display: 'block', marginBottom: '0.25rem' }}>Principles</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                    {selectedCrystal.principles.map((p) => (
                      <span
                        key={p}
                        style={{
                          fontSize: '0.75rem',
                          padding: '2px 6px',
                          background: 'var(--color-life-moss)',
                          color: 'var(--color-life-mint)',
                          borderRadius: 'var(--radius-bare)',
                        }}
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
                Select a crystal to see details
              </p>
            )}
          </div>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Full dashboard composition: hierarchy + detail panel with mood bars.',
      },
    },
  },
};

export const CompositionColorLegend: StoryObj = {
  name: 'Composition / Level Color Legend',
  render: () => {
    const levels: { level: CrystalLevel; color: string; cssVar: string; description: string }[] = [
      { level: 'SESSION', color: 'var(--color-steel-300)', cssVar: '--color-steel-300', description: 'Minutes (5-20 marks)' },
      { level: 'DAY', color: 'var(--color-life-sage)', cssVar: '--color-life-sage', description: 'Hours (2-5 sessions)' },
      { level: 'WEEK', color: 'var(--color-glow-lichen)', cssVar: '--color-glow-lichen', description: 'Days (5-7 days)' },
      { level: 'EPOCH', color: 'var(--color-glow-amber)', cssVar: '--color-glow-amber', description: 'Months (milestones)' },
    ];

    return (
      <div style={{ ...S.s1, ...card, maxWidth: '500px' }}>
        <h4 style={sectionTitle}>Crystal Level Colors - STARK BIOME</h4>
        <p style={{ ...label, marginBottom: '1rem' }}>
          Color warmth increases with temporal scope. Steel is humble; amber is earned.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {levels.map(({ level, color, cssVar, description }) => (
            <div key={level} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div
                style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  background: color,
                  flexShrink: 0,
                }}
              />
              <span style={{ color, fontWeight: 600, fontFamily: 'var(--font-mono)', width: '80px' }}>
                {level}
              </span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                {cssVar}
              </span>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginLeft: 'auto' }}>
                {description}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Color legend showing STARK BIOME progression from steel (SESSION) to amber (EPOCH).',
      },
    },
  },
};

// =============================================================================
// Interactive Stories
// =============================================================================

export const InteractiveMoodBuilder: StoryObj = {
  name: 'Interactive / Mood Builder',
  render: () => {
    const [mood, setMood] = useState<MoodVector>(MOOD_NEUTRAL);

    const dimensions: (keyof MoodVector)[] = [
      'warmth', 'weight', 'tempo', 'texture', 'brightness', 'saturation', 'complexity'
    ];

    const dimensionLabels: Record<keyof MoodVector, [string, string]> = {
      warmth: ['Cold/clinical', 'Warm/engaging'],
      weight: ['Light/playful', 'Heavy/serious'],
      tempo: ['Slow/deliberate', 'Fast/urgent'],
      texture: ['Smooth/flowing', 'Rough/struggling'],
      brightness: ['Dim/frustrated', 'Bright/joyful'],
      saturation: ['Muted/routine', 'Vivid/intense'],
      complexity: ['Simple/focused', 'Complex/branching'],
    };

    return (
      <div style={{ ...S.s0, padding: '1.5rem' }}>
        <h4 style={sectionTitle}>Interactive Mood Builder</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 200px', gap: '2rem' }}>
          {/* Sliders */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {dimensions.map((dim) => (
              <div key={dim}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                    {dimensionLabels[dim][0]}
                  </span>
                  <span style={{ color: 'var(--text-primary)', fontSize: '0.75rem', fontWeight: 600 }}>
                    {dim}
                  </span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                    {dimensionLabels[dim][1]}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={mood[dim]}
                  onChange={(e) => setMood({ ...mood, [dim]: parseFloat(e.target.value) })}
                  style={{ width: '100%' }}
                />
              </div>
            ))}
          </div>

          {/* Preview */}
          <div style={{ ...S.s1, ...card }}>
            <h5 style={label}>Preview</h5>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', alignItems: 'center' }}>
              <div>
                <p style={{ ...label, textAlign: 'center' }}>Dots (Large)</p>
                <MoodIndicator mood={mood} size="large" variant="dots" />
              </div>
              <div style={{ width: '100%' }}>
                <p style={{ ...label, textAlign: 'center' }}>Bars</p>
                <MoodIndicator mood={mood} size="medium" variant="bars" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactively adjust all 7 mood dimensions and see the MoodIndicator update in real-time.',
      },
    },
  },
};

export const InteractiveCrystalCreator: StoryObj = {
  name: 'Interactive / Crystal Creator',
  render: () => {
    const [level, setLevel] = useState<CrystalLevel>('SESSION');
    const [insight, setInsight] = useState('');
    const [confidence, setConfidence] = useState(0.85);

    const crystal = createCrystal({
      level,
      insight: insight || 'Enter your insight above...',
      confidence,
      mood: MOOD_DEEP_FOCUS,
    });

    return (
      <div style={{ ...S.s0, padding: '1.5rem' }}>
        <h4 style={sectionTitle}>Interactive Crystal Creator</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '2rem' }}>
          {/* Controls */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ ...label, display: 'block' }}>Level</label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value as CrystalLevel)}
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  background: 'var(--surface-2)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--surface-3)',
                  borderRadius: 'var(--radius-bare)',
                }}
              >
                <option value="SESSION">SESSION</option>
                <option value="DAY">DAY</option>
                <option value="WEEK">WEEK</option>
                <option value="EPOCH">EPOCH</option>
              </select>
            </div>
            <div>
              <label style={{ ...label, display: 'block' }}>Insight</label>
              <textarea
                value={insight}
                onChange={(e) => setInsight(e.target.value)}
                placeholder="What did you learn?"
                style={{
                  width: '100%',
                  padding: '0.5rem',
                  background: 'var(--surface-2)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--surface-3)',
                  borderRadius: 'var(--radius-bare)',
                  minHeight: '80px',
                  resize: 'vertical',
                }}
              />
            </div>
            <div>
              <label style={{ ...label, display: 'block' }}>
                Confidence: {(confidence * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={confidence}
                onChange={(e) => setConfidence(parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>
          </div>

          {/* Preview */}
          <div>
            <h5 style={label}>Live Preview</h5>
            <CrystalCard crystal={crystal} expandable />
          </div>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Create a crystal interactively and see it render in real-time.',
      },
    },
  },
};
