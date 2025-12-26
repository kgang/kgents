/**
 * Loss Primitives Stories
 *
 * STARK BIOME Design System — Universal Coherence Thermometer
 *
 * Loss values represent coherence in Zero Seed proofs:
 * - 0.00 = Perfect coherence (axiom-tier grounding)
 * - 1.00 = Maximum drift (nonsense)
 *
 * Tier Mapping (loss thresholds):
 * - CATEGORICAL (0.0-0.2): Green — grounded in axioms
 * - EMPIRICAL (0.2-0.5): Yellow — evidence-supported
 * - AESTHETIC (0.5-0.8): Orange — taste-guided
 * - SOMATIC (0.8-0.9): Red-Orange — intuition zone
 * - CHAOTIC (0.9-1.0): Red — incoherent/nonsense
 *
 * Philosophy: "Loss is the thermometer. Lower is better."
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { LossIndicator } from './LossIndicator';
import { LossGradient } from './LossGradient';
import { LossHeatmap } from './LossHeatmap';
import { WithLoss } from './WithLoss';
import type { LossHeatmapItem } from './LossHeatmap';

// =============================================================================
// Mock Data — Zero Seed Concepts
// =============================================================================

const zeroSeedItems: LossHeatmapItem[] = [
  { id: '1', label: 'Grounding chain', loss: 0.08 },
  { id: '2', label: 'Toulmin proof', loss: 0.15 },
  { id: '3', label: 'Claim coherence', loss: 0.32 },
  { id: '4', label: 'Evidence warrant', loss: 0.28 },
  { id: '5', label: 'Backing validity', loss: 0.45 },
  { id: '6', label: 'Qualifier strength', loss: 0.55 },
  { id: '7', label: 'Rebuttal coverage', loss: 0.68 },
  { id: '8', label: 'Logical bridge', loss: 0.72 },
  { id: '9', label: 'Intuition seed', loss: 0.85 },
];

const smallGrid: LossHeatmapItem[] = [
  { id: 'a', label: 'Axiom A1', loss: 0.05 },
  { id: 'b', label: 'Axiom A2', loss: 0.12 },
  { id: 'c', label: 'Lemma L1', loss: 0.38 },
  { id: 'd', label: 'Conjecture C1', loss: 0.75 },
];

// =============================================================================
// LossIndicator Stories
// =============================================================================

const indicatorMeta: Meta<typeof LossIndicator> = {
  title: 'Primitives/Loss/LossIndicator',
  component: LossIndicator,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
## LossIndicator

A single indicator showing loss value (0.00 = axiom, 1.00 = nonsense).

**Color Mapping:**
- Green (0.0-0.2): CATEGORICAL — axiom-grounded
- Yellow (0.2-0.5): EMPIRICAL — evidence-backed
- Orange (0.5-0.8): AESTHETIC — taste-guided
- Red (0.8-1.0): CHAOTIC — incoherent

**When to use:**
- Show coherence of a single K-Block or proof
- Display loss in headers, cards, or list items
- Quick visual health check for Zero Seed claims
        `,
      },
    },
  },
  argTypes: {
    loss: { control: { type: 'range', min: 0, max: 1, step: 0.01 } },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
  },
};

export default indicatorMeta;

type IndicatorStory = StoryObj<typeof LossIndicator>;

export const LowLoss: IndicatorStory = {
  name: 'CATEGORICAL (0.1)',
  args: { loss: 0.1, showLabel: true, size: 'md' },
  parameters: {
    docs: {
      description: { story: 'Low loss (0.1) — Green indicator. Axiom-tier grounding.' },
    },
  },
};

export const MediumLoss: IndicatorStory = {
  name: 'EMPIRICAL (0.4)',
  args: { loss: 0.4, showLabel: true, size: 'md' },
  parameters: {
    docs: {
      description: { story: 'Medium loss (0.4) — Yellow indicator. Evidence-supported.' },
    },
  },
};

export const HighLoss: IndicatorStory = {
  name: 'AESTHETIC (0.7)',
  args: { loss: 0.7, showLabel: true, size: 'md' },
  parameters: {
    docs: {
      description: { story: 'High loss (0.7) — Orange indicator. Taste-guided territory.' },
    },
  },
};

export const CriticalLoss: IndicatorStory = {
  name: 'CHAOTIC (0.9)',
  args: { loss: 0.9, showLabel: true, size: 'md' },
  parameters: {
    docs: {
      description: { story: 'Critical loss (0.9) — Red indicator. Approaching nonsense.' },
    },
  },
};

export const IndicatorSizes: StoryObj = {
  name: 'Size Variants',
  render: () => (
    <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <LossIndicator loss={0.35} size="sm" showLabel />
        <p style={{ marginTop: '8px', fontSize: '12px', color: '#8A8A94' }}>Small</p>
      </div>
      <div style={{ textAlign: 'center' }}>
        <LossIndicator loss={0.35} size="md" showLabel />
        <p style={{ marginTop: '8px', fontSize: '12px', color: '#8A8A94' }}>Medium</p>
      </div>
      <div style={{ textAlign: 'center' }}>
        <LossIndicator loss={0.35} size="lg" showLabel />
        <p style={{ marginTop: '8px', fontSize: '12px', color: '#8A8A94' }}>Large</p>
      </div>
    </div>
  ),
};

export const WithGradientBar: IndicatorStory = {
  name: 'With Gradient Bar',
  args: { loss: 0.45, showLabel: true, showGradient: true, size: 'md' },
  parameters: {
    docs: {
      description: { story: 'Shows position marker on gradient bar.' },
    },
  },
};

export const DotOnly: IndicatorStory = {
  name: 'Dot Only (No Label)',
  args: { loss: 0.62, showLabel: false, size: 'md' },
};

// =============================================================================
// LossGradient Stories
// =============================================================================

export const GradientDefault: StoryObj = {
  name: 'Gradient/Default',
  render: () => (
    <div style={{ width: '300px' }}>
      <LossGradient currentLoss={0.35} showTicks />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
## LossGradient

A clickable gradient bar for navigating by loss value.

**Features:**
- Click anywhere to jump to that loss level
- Current position marker shows selected value
- Tick marks at 0.00, 0.25, 0.50, 0.75, 1.00

**When to use:**
- Filter K-Blocks by coherence threshold
- Navigate proof chains by loss level
- Set loss threshold for actions
        `,
      },
    },
  },
};

export const GradientInteractive: StoryObj = {
  name: 'Gradient/Interactive',
  render: () => {
    const [loss, setLoss] = useState(0.5);
    return (
      <div style={{ width: '400px' }}>
        <p style={{ marginBottom: '12px', fontSize: '14px', color: '#8A8A94' }}>
          Click on the gradient to select loss: <strong>{loss.toFixed(2)}</strong>
        </p>
        <LossGradient currentLoss={loss} onNavigate={setLoss} showTicks width="100%" />
      </div>
    );
  },
};

export const GradientWidths: StoryObj = {
  name: 'Gradient/Width Variants',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <p style={{ fontSize: '12px', color: '#8A8A94', marginBottom: '8px' }}>200px</p>
        <LossGradient currentLoss={0.3} width={200} />
      </div>
      <div>
        <p style={{ fontSize: '12px', color: '#8A8A94', marginBottom: '8px' }}>300px</p>
        <LossGradient currentLoss={0.5} width={300} />
      </div>
      <div>
        <p style={{ fontSize: '12px', color: '#8A8A94', marginBottom: '8px' }}>100%</p>
        <LossGradient currentLoss={0.7} width="100%" />
      </div>
    </div>
  ),
};

export const GradientNoTicks: StoryObj = {
  name: 'Gradient/Without Ticks',
  render: () => (
    <div style={{ width: '300px' }}>
      <LossGradient currentLoss={0.6} showTicks={false} />
    </div>
  ),
};

// =============================================================================
// LossHeatmap Stories
// =============================================================================

export const HeatmapGrid4x4: StoryObj = {
  name: 'Heatmap/Grid 3x3',
  render: () => (
    <div style={{ width: '400px' }}>
      <LossHeatmap items={zeroSeedItems} layout="grid" columns={3} showValue />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
## LossHeatmap

Displays multiple items with loss-based coloring.

**Color intensity:**
- Background opacity scales with loss
- Border color indicates tier (green/yellow/orange/red)
- Corner dot glows at tier color

**When to use:**
- Compare coherence across multiple proofs
- Visualize K-Block collection health
- Identify outliers in proof chains
        `,
      },
    },
  },
};

export const HeatmapSmall2x2: StoryObj = {
  name: 'Heatmap/Grid 2x2',
  render: () => (
    <div style={{ width: '280px' }}>
      <LossHeatmap items={smallGrid} layout="grid" columns={2} showValue />
    </div>
  ),
};

export const HeatmapList: StoryObj = {
  name: 'Heatmap/List Layout',
  render: () => (
    <div style={{ width: '300px' }}>
      <LossHeatmap items={zeroSeedItems.slice(0, 5)} layout="list" showValue />
    </div>
  ),
};

export const HeatmapClickable: StoryObj = {
  name: 'Heatmap/Clickable Items',
  render: () => {
    const [selected, setSelected] = useState<string | null>(null);
    const items = smallGrid.map((item) => ({
      ...item,
      onClick: () => setSelected(item.id),
    }));
    return (
      <div style={{ width: '280px' }}>
        <p style={{ marginBottom: '12px', fontSize: '14px', color: '#8A8A94' }}>
          Selected: <strong>{selected || 'none'}</strong>
        </p>
        <LossHeatmap items={items} layout="grid" columns={2} showValue />
      </div>
    );
  },
};

// =============================================================================
// WithLoss HOC Stories
// =============================================================================

const SampleCard = () => (
  <div
    style={{
      padding: '16px',
      background: '#1C1C22',
      border: '1px solid #28282F',
      borderRadius: '4px',
      width: '200px',
    }}
  >
    <h3 style={{ margin: 0, fontSize: '14px', color: '#E5E7EB' }}>K-Block #42</h3>
    <p style={{ margin: '8px 0 0', fontSize: '12px', color: '#8A8A94' }}>
      Proof of claim coherence
    </p>
  </div>
);

export const WithLossTopRight: StoryObj = {
  name: 'WithLoss/Top Right',
  render: () => (
    <WithLoss loss={0.25} position="top-right">
      <SampleCard />
    </WithLoss>
  ),
  parameters: {
    docs: {
      description: {
        story: `
## WithLoss HOC

Wraps any component with a loss indicator overlay.

**Position options:**
- top-left, top-right (default)
- bottom-left, bottom-right

**When to use:**
- Add loss indicator to existing cards
- Overlay coherence on previews
- Non-invasive loss display
        `,
      },
    },
  },
};

export const WithLossPositions: StoryObj = {
  name: 'WithLoss/All Positions',
  render: () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px' }}>
      <WithLoss loss={0.15} position="top-left">
        <SampleCard />
      </WithLoss>
      <WithLoss loss={0.35} position="top-right">
        <SampleCard />
      </WithLoss>
      <WithLoss loss={0.65} position="bottom-left">
        <SampleCard />
      </WithLoss>
      <WithLoss loss={0.85} position="bottom-right">
        <SampleCard />
      </WithLoss>
    </div>
  ),
};

export const WithLossLabel: StoryObj = {
  name: 'WithLoss/With Label',
  render: () => (
    <WithLoss loss={0.42} position="top-right" showLabel size="sm">
      <SampleCard />
    </WithLoss>
  ),
};
