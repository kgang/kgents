/**
 * Constitutional Dashboard Stories
 *
 * STARK BIOME Design System Demo
 *
 * These stories showcase the Constitutional Enforcement visualization:
 * - ConstitutionalRadar: 7-principle heptagonal radar chart
 * - ConstitutionalScorecard: Detailed principle breakdown
 * - TrustLevelBadge: L0→L3 trust indicator
 *
 * Philosophy: "The frame is humble. The content glows."
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { ConstitutionalRadar } from './ConstitutionalRadar';
import { ConstitutionalScorecard } from './ConstitutionalScorecard';
import { TrustLevelBadge } from './TrustLevelBadge';
import type { ConstitutionalAlignment, ConstitutionalTrustResult } from './types';

// Import component CSS
import './ConstitutionalRadar.css';
import './ConstitutionalScorecard.css';
import './TrustLevelBadge.css';

// =============================================================================
// Mock Data
// =============================================================================

const mockHighAlignment: ConstitutionalAlignment = {
  principle_scores: {
    TASTEFUL: 0.92,
    CURATED: 0.88,
    ETHICAL: 0.95,
    JOY_INDUCING: 0.85,
    COMPOSABLE: 0.9,
    HETERARCHICAL: 0.82,
    GENERATIVE: 0.87,
  },
  weighted_total: 0.89,
  galois_loss: null,
  tier: 'EMPIRICAL',
  threshold: 0.5,
  is_compliant: true,
  violation_count: 0,
  dominant_principle: 'ETHICAL',
  weakest_principle: 'HETERARCHICAL',
};

const mockMediumAlignment: ConstitutionalAlignment = {
  principle_scores: {
    TASTEFUL: 0.72,
    CURATED: 0.65,
    ETHICAL: 0.78,
    JOY_INDUCING: 0.58,
    COMPOSABLE: 0.7,
    HETERARCHICAL: 0.45,
    GENERATIVE: 0.62,
  },
  weighted_total: 0.66,
  galois_loss: null,
  tier: 'EMPIRICAL',
  threshold: 0.5,
  is_compliant: true,
  violation_count: 1,
  dominant_principle: 'ETHICAL',
  weakest_principle: 'HETERARCHICAL',
};

const mockLowAlignment: ConstitutionalAlignment = {
  principle_scores: {
    TASTEFUL: 0.42,
    CURATED: 0.38,
    ETHICAL: 0.55,
    JOY_INDUCING: 0.35,
    COMPOSABLE: 0.48,
    HETERARCHICAL: 0.3,
    GENERATIVE: 0.4,
  },
  weighted_total: 0.42,
  galois_loss: 0.58,
  tier: 'GALOIS',
  threshold: 0.5,
  is_compliant: false,
  violation_count: 5,
  dominant_principle: 'ETHICAL',
  weakest_principle: 'HETERARCHICAL',
};

const mockTrustL3: ConstitutionalTrustResult = {
  trust_level: 'L3',
  trust_level_value: 3,
  total_marks_analyzed: 150,
  average_alignment: 0.92,
  violation_rate: 0.005,
  trust_capital: 1.5,
  principle_averages: {
    TASTEFUL: 0.91,
    CURATED: 0.88,
    ETHICAL: 0.95,
    JOY_INDUCING: 0.87,
    COMPOSABLE: 0.92,
    HETERARCHICAL: 0.85,
    GENERATIVE: 0.89,
  },
  dominant_principles: ['ETHICAL', 'COMPOSABLE', 'TASTEFUL'],
  reasoning: 'Meets L3 criteria: alignment=0.92≥0.9, violations=0.5%<1%, capital=1.5≥1.0',
};

// =============================================================================
// ConstitutionalRadar Stories
// =============================================================================

const radarMeta: Meta<typeof ConstitutionalRadar> = {
  title: 'Constitutional/Radar',
  component: ConstitutionalRadar,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
## ConstitutionalRadar

A pure SVG heptagonal radar chart visualizing the 7 constitutional principles.

**STARK BIOME Colors:**
- Grid: \`steel-gunmetal\` (#28282F)
- Good scores (>0.8): \`life-sage\` (#4A6B4A)
- Medium scores (0.5-0.8): \`glow-spore\` (#C4A77D)
- Low scores (<0.5): \`accent-error\` (#A65D4A)

**The 7 Principles:**
1. **Tasteful** - Clear, justified purpose
2. **Curated** - Intentional selection
3. **Ethical** - Augments, never replaces (weight: 2.0)
4. **Joy-Inducing** - Delight in interaction (weight: 1.2)
5. **Composable** - Morphisms in a category (weight: 1.5)
6. **Heterarchical** - Flux, not hierarchy
7. **Generative** - Spec as compression
        `,
      },
    },
  },
  argTypes: {
    width: { control: { type: 'range', min: 200, max: 600, step: 50 } },
    height: { control: { type: 'range', min: 200, max: 600, step: 50 } },
  },
};

export default radarMeta;

type RadarStory = StoryObj<typeof ConstitutionalRadar>;

export const HighAlignment: RadarStory = {
  name: '✨ High Alignment (L3)',
  args: {
    alignment: mockHighAlignment,
    width: 400,
    height: 400,
  },
};

export const MediumAlignment: RadarStory = {
  name: '◐ Medium Alignment (L1-L2)',
  args: {
    alignment: mockMediumAlignment,
    width: 400,
    height: 400,
  },
};

export const LowAlignment: RadarStory = {
  name: '○ Low Alignment (L0)',
  args: {
    alignment: mockLowAlignment,
    width: 400,
    height: 400,
  },
};

export const CompactSize: RadarStory = {
  name: 'Compact (200px)',
  args: {
    alignment: mockHighAlignment,
    width: 200,
    height: 200,
  },
};

export const LargeSize: RadarStory = {
  name: 'Spacious (500px)',
  args: {
    alignment: mockHighAlignment,
    width: 500,
    height: 500,
  },
};

// =============================================================================
// TrustLevelBadge Stories
// =============================================================================

export const TrustBadges: StoryObj = {
  name: 'Trust Level Badges',
  render: () => (
    <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <TrustLevelBadge level="L0" size="lg" />
        <p style={{ marginTop: '8px', fontSize: '12px', color: '#8A8A94' }}>
          READ_ONLY
        </p>
      </div>
      <div style={{ textAlign: 'center' }}>
        <TrustLevelBadge level="L1" size="lg" />
        <p style={{ marginTop: '8px', fontSize: '12px', color: '#8A8A94' }}>
          BOUNDED
        </p>
      </div>
      <div style={{ textAlign: 'center' }}>
        <TrustLevelBadge level="L2" size="lg" />
        <p style={{ marginTop: '8px', fontSize: '12px', color: '#8A8A94' }}>
          SUGGESTION
        </p>
      </div>
      <div style={{ textAlign: 'center' }}>
        <TrustLevelBadge level="L3" size="lg" />
        <p style={{ marginTop: '8px', fontSize: '12px', color: '#8A8A94' }}>
          AUTONOMOUS
        </p>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Trust levels represent earned autonomy through constitutional alignment:

- **L0 (READ_ONLY)**: Default, no history — \`steel-zinc\`
- **L1 (BOUNDED)**: avg_alignment ≥ 0.6 — \`life-moss\`
- **L2 (SUGGESTION)**: avg_alignment ≥ 0.8 — \`life-sage\`
- **L3 (AUTONOMOUS)**: avg_alignment ≥ 0.9 — \`glow-spore\` ✨ (Earned glow!)
        `,
      },
    },
  },
};

export const TrustBadgeSizes: StoryObj = {
  name: 'Badge Sizes',
  render: () => (
    <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
      <TrustLevelBadge level="L3" size="sm" />
      <TrustLevelBadge level="L3" size="md" />
      <TrustLevelBadge level="L3" size="lg" />
    </div>
  ),
};

// =============================================================================
// ConstitutionalScorecard Stories
// =============================================================================

export const ScorecardHigh: StoryObj = {
  name: 'Scorecard — High Alignment',
  render: () => (
    <div style={{ maxWidth: '400px' }}>
      <ConstitutionalScorecard
        alignment={mockHighAlignment}
        trust={mockTrustL3}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
The scorecard shows detailed breakdown of all 7 principles with:
- Score bars with health-based coloring
- Overall weighted score
- Trust level with reasoning
- Violation warnings (if any)
        `,
      },
    },
  },
};

export const ScorecardWithViolations: StoryObj = {
  name: 'Scorecard — With Violations',
  render: () => (
    <div style={{ maxWidth: '400px' }}>
      <ConstitutionalScorecard
        alignment={mockLowAlignment}
        trust={{
          trust_level: 'L0',
          trust_level_value: 0,
          total_marks_analyzed: 10,
          average_alignment: 0.42,
          violation_rate: 0.5,
          trust_capital: 0.1,
          principle_averages: mockLowAlignment.principle_scores,
          dominant_principles: ['ETHICAL'],
          reasoning: 'For L1: alignment needs 0.18 more; violations need to drop below 10%',
        }}
      />
    </div>
  ),
};

// =============================================================================
// Combined Dashboard Story
// =============================================================================

export const FullDashboard: StoryObj = {
  name: '🎯 Full Dashboard',
  render: () => (
    <div
      style={{
        display: 'flex',
        gap: '32px',
        padding: '24px',
        background: '#141418', // steel-carbon
        borderRadius: '4px',
        border: '1px solid #28282F', // steel-gunmetal
      }}
    >
      <div>
        <ConstitutionalRadar alignment={mockHighAlignment} width={350} height={350} />
      </div>
      <div style={{ flex: 1, maxWidth: '400px' }}>
        <div style={{ marginBottom: '16px' }}>
          <TrustLevelBadge level="L3" size="lg" showLabel />
        </div>
        <ConstitutionalScorecard alignment={mockHighAlignment} trust={mockTrustL3} />
      </div>
    </div>
  ),
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        story: `
# Constitutional Dashboard

The complete view combining:
1. **Radar** — Visual representation of the 7 principles
2. **Trust Badge** — Current trust level (L0→L3)
3. **Scorecard** — Detailed breakdown with reasoning

This dashboard embodies STARK BIOME:
- Steel frame (\`steel-carbon\` background)
- Earned glow (L3 badge uses \`glow-spore\`)
- Sympathetic errors (\`accent-error\` for violations)
        `,
      },
    },
  },
};
