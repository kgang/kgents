/**
 * Elastic Layout System Stories
 *
 * STARK BIOME Design System - THREE-MODE ELASTIC PATTERN
 *
 * Philosophy: "Tight Frame, Breathing Content"
 *
 * The elastic layout system provides density-aware components that adapt
 * gracefully across three canonical viewport modes:
 *
 * | Mode        | Breakpoint | Use Case            |
 * |-------------|------------|---------------------|
 * | Compact     | < 768px    | Mobile devices      |
 * | Comfortable | 768-1024px | Tablets, small desks|
 * | Spacious    | > 1024px   | Desktop, large screens |
 *
 * CONTENT DEGRADATION STRATEGY:
 * As space decreases, content gracefully degrades:
 *   Full -> Summary -> Title -> Icon
 *
 * What to hide at each density:
 * - Compact: Secondary actions, detailed text, optional icons
 * - Comfortable: Decorative elements, wide margins
 * - Spacious: Show everything, maximize whitespace
 *
 * DENSITY COORDINATION:
 * Components share density state via LayoutContext. Parent containers
 * measure themselves and propagate context to children, enabling
 * coordinated responsive behavior without prop drilling.
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { ElasticContainer } from './ElasticContainer';
import { ElasticCard } from './ElasticCard';
import { ElasticSplit } from './ElasticSplit';
import { ElasticPlaceholder } from './ElasticPlaceholder';
import { FloatingActions, type FloatingAction } from './FloatingActions';
import { BottomDrawer } from './BottomDrawer';

// =============================================================================
// Meta
// =============================================================================

const meta: Meta = {
  title: 'Elastic/Layout System',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
# Elastic Layout System

The three-mode elastic pattern provides density-aware responsive layouts.

## Core Concepts

### Breakpoints
- **Compact** (<768px): Mobile-first, touch-optimized
- **Comfortable** (768-1024px): Balanced for tablets
- **Spacious** (>1024px): Full desktop experience

### Spacing Tokens
- \`--space-xs\`: 4px (compact padding)
- \`--space-sm\`: 8px (tight gaps)
- \`--space-md\`: 16px (standard gap)
- \`--space-lg\`: 24px (comfortable padding)
- \`--space-xl\`: 32px (spacious sections)
- \`--space-2xl\`: 48px (hero margins)

### STARK BIOME Design
- **Steel Frame**: \`steel-carbon\` backgrounds, \`steel-gunmetal\` borders
- **Earned Glow**: \`glow-spore\` for selected/active states
- **Bare Edge**: Minimal border-radius (2-4px)
        `,
      },
    },
  },
};

export default meta;

// =============================================================================
// Sample Content
// =============================================================================

const SampleContent = ({ label, height = '100%' }: { label: string; height?: string }) => (
  <div
    style={{
      padding: '16px',
      background: 'rgba(40, 40, 47, 0.5)',
      borderRadius: '4px',
      height,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#8A8A94',
    }}
  >
    {label}
  </div>
);

// =============================================================================
// ElasticContainer Stories
// =============================================================================

export const ContainerDensityAuto: StoryObj = {
  name: 'Container - Auto Density',
  render: () => (
    <ElasticContainer
      layout="stack"
      gap={{ sm: 'var(--space-sm)', md: 'var(--space-md)', lg: 'var(--space-lg)' }}
      padding={{ sm: 'var(--space-sm)', md: 'var(--space-md)', lg: 'var(--space-lg)' }}
      style={{ background: 'rgba(20, 20, 24, 0.8)', borderRadius: '4px', minHeight: '200px' }}
    >
      <SampleContent label="Item 1" height="60px" />
      <SampleContent label="Item 2" height="60px" />
      <SampleContent label="Item 3" height="60px" />
    </ElasticContainer>
  ),
  parameters: {
    docs: {
      description: {
        story: `
ElasticContainer automatically adapts gap and padding based on available width.
Resize the viewport to see spacing change across density modes.

**Responsive values**: Pass an object with \`sm\`, \`md\`, \`lg\` keys for density-aware spacing.
        `,
      },
    },
  },
};

export const ContainerGrid: StoryObj = {
  name: 'Container - Grid Layout',
  render: () => (
    <ElasticContainer
      layout="grid"
      minItemWidth={150}
      gap="var(--space-md)"
      padding="var(--space-md)"
      style={{ background: 'rgba(20, 20, 24, 0.8)', borderRadius: '4px' }}
    >
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <SampleContent key={i} label={`Card ${i}`} height="100px" />
      ))}
    </ElasticContainer>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Grid layout with auto-fit columns based on `minItemWidth`. Items reflow as container width changes.',
      },
    },
  },
};

export const ContainerEmpty: StoryObj = {
  name: 'Container - Empty State',
  render: () => (
    <ElasticContainer
      layout="stack"
      emptyState={<ElasticPlaceholder for="list" state="empty" emptyMessage="Add items to get started" />}
      style={{ background: 'rgba(20, 20, 24, 0.8)', borderRadius: '4px', minHeight: '200px' }}
    >
      {null}
    </ElasticContainer>
  ),
};

// =============================================================================
// ElasticCard Stories
// =============================================================================

export const CardContentDegradation: StoryObj = {
  name: 'Card - Content Degradation',
  render: () => (
    <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
      {/* Simulated widths to show degradation */}
      {[400, 250, 120, 50].map((width) => (
        <div key={width} style={{ width: `${width}px` }}>
          <p style={{ fontSize: '12px', color: '#8A8A94', marginBottom: '8px' }}>{width}px</p>
          <ElasticCard
            icon={<span style={{ fontSize: '20px' }}>&#9671;</span>}
            title="Agent Alpha"
            summary="Monitors system health and reports anomalies in real-time."
            priority={5}
          >
            <p style={{ fontSize: '14px', color: '#9CA3AF' }}>
              Full content with detailed description and additional metadata that only appears at larger widths.
            </p>
          </ElasticCard>
        </div>
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
ElasticCard automatically degrades content based on available width:

| Width      | Level   | Shows                    |
|------------|---------|--------------------------|
| >= 400px   | Full    | Icon, title, summary, children |
| 280-399px  | Summary | Icon, title, summary     |
| 150-279px  | Title   | Icon, title              |
| < 150px    | Icon    | Icon only                |

The \`minContent\` prop sets the floor (e.g., \`minContent="title"\` ensures title always shows).
        `,
      },
    },
  },
};

export const CardSelected: StoryObj = {
  name: 'Card - Selection States',
  render: () => (
    <div style={{ display: 'flex', gap: '16px' }}>
      <div style={{ width: '300px' }}>
        <ElasticCard
          icon={<span style={{ color: '#8A8A94' }}>&#9675;</span>}
          title="Default Card"
          summary="Not selected"
        />
      </div>
      <div style={{ width: '300px' }}>
        <ElasticCard
          icon={<span style={{ color: '#C4A77D' }}>&#9673;</span>}
          title="Selected Card"
          summary="Selected state with earned glow"
          isSelected
        />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'STARK BIOME: Selected cards earn the `glow-spore` border accent. The frame stays humble until selection.',
      },
    },
  },
};

export const CardInteractive: StoryObj = {
  name: 'Card - Interactive',
  render: () => {
    const [selected, setSelected] = useState<number | null>(null);
    return (
      <ElasticContainer layout="grid" minItemWidth={200} gap="var(--space-md)">
        {[1, 2, 3, 4].map((i) => (
          <ElasticCard
            key={i}
            icon={<span>{i === selected ? '\u25C9' : '\u25CB'}</span>}
            title={`Agent ${i}`}
            summary={`Click to ${selected === i ? 'deselect' : 'select'}`}
            isSelected={selected === i}
            onClick={() => setSelected(selected === i ? null : i)}
          />
        ))}
      </ElasticContainer>
    );
  },
};

// =============================================================================
// ElasticSplit Stories
// =============================================================================

export const SplitResponsive: StoryObj = {
  name: 'Split - Responsive Collapse',
  render: () => (
    <div style={{ height: '300px', border: '1px solid #28282F', borderRadius: '4px' }}>
      <ElasticSplit
        direction="horizontal"
        defaultRatio={0.3}
        collapseAtDensity="compact"
        primary={<SampleContent label="Primary Pane (Navigation)" />}
        secondary={<SampleContent label="Secondary Pane (Content)" />}
      />
    </div>
  ),
  parameters: {
    viewport: { defaultViewport: 'spacious' },
    docs: {
      description: {
        story: `
ElasticSplit collapses to stacked layout at compact density.

**collapseAtDensity options:**
- \`'compact'\`: Only collapse on mobile (<768px)
- \`'comfortable'\`: Collapse on mobile and tablet
- \`'spacious'\`: Never collapse

Switch viewport in toolbar to see collapse behavior.
        `,
      },
    },
  },
};

export const SplitResizable: StoryObj = {
  name: 'Split - Resizable Divider',
  render: () => (
    <div style={{ height: '300px', border: '1px solid #28282F', borderRadius: '4px' }}>
      <ElasticSplit
        direction="horizontal"
        defaultRatio={0.4}
        resizable
        minPaneSize={100}
        primary={<SampleContent label="Drag the divider" />}
        secondary={<SampleContent label="Content adjusts" />}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Drag the divider to resize panes. `minPaneSize` enforces minimum width for each pane.',
      },
    },
  },
};

export const SplitVertical: StoryObj = {
  name: 'Split - Vertical',
  render: () => (
    <div style={{ height: '400px', border: '1px solid #28282F', borderRadius: '4px' }}>
      <ElasticSplit
        direction="vertical"
        defaultRatio={0.6}
        primary={<SampleContent label="Top Pane" />}
        secondary={<SampleContent label="Bottom Pane" />}
      />
    </div>
  ),
};

// =============================================================================
// FloatingActions Stories
// =============================================================================

export const FloatingActionsDefault: StoryObj = {
  name: 'FloatingActions - Default',
  render: () => {
    const actions: FloatingAction[] = [
      { id: 'add', icon: '+', label: 'Add Item', onClick: () => {}, variant: 'primary' },
      { id: 'settings', icon: '\u2699', label: 'Settings', onClick: () => {} },
      { id: 'help', icon: '?', label: 'Help', onClick: () => {} },
    ];
    return (
      <div style={{ position: 'relative', height: '200px', background: 'rgba(20, 20, 24, 0.5)', borderRadius: '4px' }}>
        <FloatingActions actions={actions} position="bottom-right" />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: `
FloatingActions provides mobile-friendly action buttons.

**Physical constraints enforced:**
- Minimum touch target: 48x48px
- Minimum tap spacing: 8px

In compact mode, toolbars project to floating action clusters.
        `,
      },
    },
  },
};

export const FloatingActionsStates: StoryObj = {
  name: 'FloatingActions - States',
  render: () => {
    const actions: FloatingAction[] = [
      { id: 'active', icon: '\u2713', label: 'Active', onClick: () => {}, isActive: true },
      { id: 'loading', icon: '\u21BB', label: 'Loading', onClick: () => {}, loading: true },
      { id: 'disabled', icon: '\u2715', label: 'Disabled', onClick: () => {}, disabled: true },
      { id: 'danger', icon: '!', label: 'Danger', onClick: () => {}, variant: 'danger' },
    ];
    return (
      <div style={{ position: 'relative', height: '250px', background: 'rgba(20, 20, 24, 0.5)', borderRadius: '4px' }}>
        <FloatingActions actions={actions} position="bottom-right" />
      </div>
    );
  },
};

export const FloatingActionsHorizontal: StoryObj = {
  name: 'FloatingActions - Horizontal',
  render: () => {
    const actions: FloatingAction[] = [
      { id: 'prev', icon: '\u2190', label: 'Previous', onClick: () => {} },
      { id: 'play', icon: '\u25B6', label: 'Play', onClick: () => {}, variant: 'primary' },
      { id: 'next', icon: '\u2192', label: 'Next', onClick: () => {} },
    ];
    return (
      <div style={{ position: 'relative', height: '150px', background: 'rgba(20, 20, 24, 0.5)', borderRadius: '4px' }}>
        <FloatingActions actions={actions} position="bottom-right" direction="horizontal" />
      </div>
    );
  },
};

// =============================================================================
// BottomDrawer Stories
// =============================================================================

export const BottomDrawerDefault: StoryObj = {
  name: 'BottomDrawer - Interactive',
  render: () => {
    const [isOpen, setIsOpen] = useState(false);
    return (
      <div style={{ position: 'relative', height: '400px', background: 'rgba(20, 20, 24, 0.5)', borderRadius: '4px' }}>
        <button
          onClick={() => setIsOpen(true)}
          style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            padding: '12px 24px',
            background: '#4A6B4A',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Open Drawer
        </button>
        <BottomDrawer isOpen={isOpen} onClose={() => setIsOpen(false)} title="Detail Panel">
          <div style={{ padding: '16px' }}>
            <p style={{ color: '#E5E7EB', marginBottom: '16px' }}>
              BottomDrawer slides up from the bottom on mobile devices.
            </p>
            <p style={{ color: '#8A8A94', fontSize: '14px' }}>
              Tap the handle, backdrop, or press Escape to close.
            </p>
          </div>
        </BottomDrawer>
      </div>
    );
  },
  parameters: {
    viewport: { defaultViewport: 'compact' },
    docs: {
      description: {
        story: `
BottomDrawer is the mobile projection for Panel primitives.

**Physical constraints:**
- Handle touch target: 48x48px (visual handle: 40x4px)
- Closes via: handle tap, backdrop tap, Escape key

**Temporal coherence:**
- Supports animation coordination with sibling drawers
- Uses \`AnimationConstraint\` for sync strategies (lock_step, stagger)
        `,
      },
    },
  },
};

// =============================================================================
// ElasticPlaceholder Stories
// =============================================================================

export const PlaceholderStates: StoryObj = {
  name: 'Placeholder - States',
  render: () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
      <div>
        <p style={{ fontSize: '12px', color: '#8A8A94', marginBottom: '8px' }}>Loading</p>
        <ElasticPlaceholder for="agent" state="loading" />
      </div>
      <div>
        <p style={{ fontSize: '12px', color: '#8A8A94', marginBottom: '8px' }}>Empty</p>
        <ElasticPlaceholder for="agent" state="empty" />
      </div>
      <div>
        <p style={{ fontSize: '12px', color: '#8A8A94', marginBottom: '8px' }}>Error</p>
        <ElasticPlaceholder for="agent" state="error" error="Connection failed" onRetry={() => {}} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'ElasticPlaceholder provides contextual feedback for loading, empty, and error states.',
      },
    },
  },
};

export const PlaceholderTypes: StoryObj = {
  name: 'Placeholder - Content Types',
  render: () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px' }}>
      {(['agent', 'metric', 'chart', 'list'] as const).map((type) => (
        <div key={type}>
          <p style={{ fontSize: '12px', color: '#8A8A94', marginBottom: '8px' }}>{type}</p>
          <ElasticPlaceholder for={type} state="loading" />
        </div>
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Each content type has a unique skeleton shape optimized for its expected layout.',
      },
    },
  },
};

// =============================================================================
// Combined Demo
// =============================================================================

export const FullElasticDemo: StoryObj = {
  name: 'Full Elastic Demo',
  render: () => {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState<number | null>(null);

    const actions: FloatingAction[] = [
      { id: 'add', icon: '+', label: 'Add Agent', onClick: () => {}, variant: 'primary' },
      { id: 'details', icon: '\u2261', label: 'Details', onClick: () => setDrawerOpen(true) },
    ];

    return (
      <div
        style={{
          position: 'relative',
          height: '500px',
          background: '#141418',
          borderRadius: '4px',
          border: '1px solid #28282F',
          overflow: 'hidden',
        }}
      >
        <ElasticSplit
          direction="horizontal"
          defaultRatio={0.3}
          collapseAtDensity="compact"
          primary={
            <div style={{ padding: '16px', height: '100%' }}>
              <h3 style={{ color: '#E5E7EB', marginBottom: '16px', fontSize: '14px' }}>Agents</h3>
              <ElasticContainer layout="stack" gap="var(--space-sm)">
                {[1, 2, 3].map((i) => (
                  <ElasticCard
                    key={i}
                    icon={<span>{selectedAgent === i ? '\u25C9' : '\u25CB'}</span>}
                    title={`Agent ${i}`}
                    summary={`Status: Active`}
                    isSelected={selectedAgent === i}
                    onClick={() => setSelectedAgent(selectedAgent === i ? null : i)}
                  />
                ))}
              </ElasticContainer>
            </div>
          }
          secondary={
            <div style={{ padding: '16px', height: '100%' }}>
              <h3 style={{ color: '#E5E7EB', marginBottom: '16px', fontSize: '14px' }}>Dashboard</h3>
              {selectedAgent ? (
                <ElasticContainer layout="grid" minItemWidth={150} gap="var(--space-md)">
                  <ElasticPlaceholder for="metric" state="loading" />
                  <ElasticPlaceholder for="metric" state="loading" />
                  <ElasticPlaceholder for="chart" state="loading" />
                </ElasticContainer>
              ) : (
                <ElasticPlaceholder for="custom" state="empty" emptyMessage="Select an agent to view details" />
              )}
            </div>
          }
        />

        <FloatingActions actions={actions} position="bottom-right" />

        <BottomDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} title="Agent Details">
          <div style={{ padding: '16px' }}>
            <p style={{ color: '#9CA3AF' }}>
              {selectedAgent ? `Viewing Agent ${selectedAgent}` : 'No agent selected'}
            </p>
          </div>
        </BottomDrawer>
      </div>
    );
  },
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        story: `
# Complete Elastic Layout Demo

This demo combines all elastic components:
1. **ElasticSplit** - Responsive pane layout
2. **ElasticContainer** - Density-aware container with grid
3. **ElasticCard** - Priority-aware, selectable cards
4. **ElasticPlaceholder** - Loading and empty states
5. **FloatingActions** - Mobile-friendly action buttons
6. **BottomDrawer** - Slide-up panel for details

**Try:**
- Toggle viewport size in toolbar (Compact/Comfortable/Spacious)
- Click cards to select
- Click "Details" FAB to open drawer
        `,
      },
    },
  },
};
