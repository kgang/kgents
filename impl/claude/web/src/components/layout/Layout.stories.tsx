/**
 * Layout Components Stories
 *
 * STARK BIOME: The Cathedral Navigation Experience
 *
 * These stories showcase the layout components that form the structural
 * foundation of the kgents interface.
 *
 * Philosophy:
 * - "Stop documenting agents. Become the agent."
 * - The shell is humble; the content glows
 * - Witness events are always visible (footer stream)
 * - Derivation trails show epistemic provenance
 * - Focal distance enables telescope-style zoom navigation
 *
 * Components:
 * - AppShell: Root layout with navbar and witness footer
 * - WitnessFooter: Always-on compact witness event stream
 * - DerivationTrail: Breadcrumb showing axiom -> current path
 * - FocalDistanceRuler: Vertical navigation for 7-layer epistemic hierarchy
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { MemoryRouter } from 'react-router-dom';
import { AppShell } from './AppShell';
// Note: WitnessFooter and DerivationTrail are mocked in stories
// to avoid hook dependencies. See MockWitnessFooter and MockDerivationTrail.
import { FocalDistanceRuler } from './FocalDistanceRuler';
import { TelescopeProvider, getLayerName } from '../../hooks/useTelescopeState';
import { ModeProvider } from '../../context/ModeContext';

// Import CSS
import './AppShell.css';
import './WitnessFooter.css';
import './DerivationTrail.css';
import './FocalDistanceRuler.css';

// =============================================================================
// Mock Data
// =============================================================================

const mockWitnessEvents = [
  {
    id: 'evt-1',
    type: 'mark' as const,
    timestamp: new Date(),
    action: 'Decided to use SSE over WebSockets',
    reasoning: 'Simpler, sufficient for our needs',
    principles: ['composable', 'tasteful'],
    author: 'kent',
  },
  {
    id: 'evt-2',
    type: 'kblock' as const,
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    path: '/spec/protocols/witness.md',
    actor: 'claude',
    semanticDeltas: [{ kind: 'add', token_id: '1', token_kind: 'heading', token_value: 'New Section' }],
  },
  {
    id: 'evt-3',
    type: 'crystal' as const,
    timestamp: new Date(Date.now() - 10 * 60 * 1000),
    insight: 'AGENTESE paths are places, not identifiers',
    level: 'L2',
    significance: 0.95,
  },
];

// =============================================================================
// Decorators
// =============================================================================

const withProviders = (Story: React.ComponentType) => (
  <MemoryRouter initialEntries={['/world.document']}>
    <ModeProvider>
      <TelescopeProvider>
        <Story />
      </TelescopeProvider>
    </ModeProvider>
  </MemoryRouter>
);

// Telescope-only decorator available for standalone component stories:
// const withTelescopeOnly = (Story) => <TelescopeProvider><Story /></TelescopeProvider>

// =============================================================================
// Meta
// =============================================================================

const meta: Meta = {
  title: 'Components/Layout',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
## The Cathedral Navigation Experience

Layout components form the structural foundation of kgents. Following STARK BIOME
principles, they are humble frames that let content glow.

### Architecture

\`\`\`
+------------------------------------------------------------------+
|  NAVBAR: Logo | Editor | Studio | Feed | Genesis | Sidebar hints |
+------------------------------------------------------------------+
|                                                                  |
|                       MAIN CONTENT AREA                          |
|                                                                  |
|  (DerivationTrail)     ◉ Current focus                          |
|  Axioms -> Goals -> Specs -> [Current]                          |
|                                                                  |
|                                    (FocalDistanceRuler)          |
|                                    L1: Axioms                    |
|                                    L2: Values                    |
|                                    L3: Goals                     |
|                                    L4: Specs    <-- current      |
|                                    L5: Actions                   |
|                                    L6: Reflections               |
|                                    L7: Documents                 |
|                                                                  |
+------------------------------------------------------------------+
|  WITNESS FOOTER: [Connected] evt1 | evt2 | evt3     [NORMAL]     |
+------------------------------------------------------------------+
\`\`\`

### Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Humble Frame** | Navbar and footer use steel gray (\`#18181B\`) |
| **Content Glows** | Main area is darker (\`#141418\`), content stands out |
| **Always Witness** | Footer shows real-time witness events |
| **Epistemic Depth** | 7-layer hierarchy visible via FocalDistanceRuler |
| **Derivation Trails** | Show how you got here from axioms |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| \`Shift+E\` | Navigate to Editor |
| \`Shift+S\` | Navigate to Studio |
| \`Shift+F\` | Navigate to Feed |
| \`Shift+G\` | Navigate to Genesis |
| \`Ctrl+B\` | Toggle Files sidebar |
| \`Ctrl+J\` | Toggle Chat sidebar |
        `,
      },
    },
  },
};

export default meta;

// =============================================================================
// AppShell Stories
// =============================================================================

export const AppShellDefault: StoryObj = {
  name: 'AppShell - Default',
  decorators: [withProviders],
  render: () => (
    <AppShell>
      <div className="h-[400px] flex items-center justify-center text-gray-400">
        <div className="text-center">
          <p className="text-xl mb-2">Main Content Area</p>
          <p className="text-sm">The humble frame lets content glow</p>
        </div>
      </div>
    </AppShell>
  ),
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story: `
The complete AppShell with navbar, content area, and witness footer.

**Navigation items:**
- Editor (Shift+E) - Hypergraph editor
- Studio (Shift+S) - Workspace view
- Feed (Shift+F) - Truth stream
- Genesis (Shift+G) - FTUE demo

**Sidebar hints in navbar:** Ctrl+B Files, Ctrl+J Chat
        `,
      },
    },
  },
};

export const AppShellWithContent: StoryObj = {
  name: 'AppShell - With Rich Content',
  decorators: [withProviders],
  render: () => (
    <AppShell>
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-semibold text-white mb-4">
            Hypergraph Editor
          </h1>
          <p className="text-gray-400 mb-6">
            The file is a lie. There is only the graph.
          </p>
          <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="p-4 rounded-lg bg-gray-800/50 border border-gray-700"
              >
                <div className="text-cyan-400 text-sm font-mono mb-1">
                  Node {i}
                </div>
                <div className="text-gray-500 text-xs">
                  spec/protocols/example-{i}.md
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  ),
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story: 'AppShell with realistic content showing how the frame recedes.',
      },
    },
  },
};

// =============================================================================
// WitnessFooter Stories (Standalone)
// =============================================================================

/**
 * Standalone WitnessFooter with mock data for stories.
 * The real component uses useWitnessStream hook.
 */
function MockWitnessFooter({ events = mockWitnessEvents, connected = true }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <footer
      className="witness-footer"
      data-expanded={expanded}
      style={{ position: 'relative' }}
    >
      <div className="witness-footer__bar" onClick={() => setExpanded(!expanded)}>
        <div className="witness-footer__status" data-connected={connected}>
          <span className="witness-footer__status-dot" />
          <span className="witness-footer__status-label">
            {connected ? 'WITNESS' : 'RECONNECTING'}
          </span>
        </div>

        <div className="witness-footer__events">
          {events.slice(0, 3).map((event) => (
            <div key={event.id} className="witness-footer__event" data-type={event.type}>
              <span className="witness-footer__event-icon">
                {event.type === 'mark' ? '|-' : event.type === 'kblock' ? '{}' : '<>'}
              </span>
              <span className="witness-footer__event-text">
                {event.action || event.path?.split('/').pop() || event.insight?.slice(0, 30)}
              </span>
              <span className="witness-footer__event-time">
                {event.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })}
              </span>
            </div>
          ))}
        </div>

        <div className="witness-footer__mode" data-mode="NORMAL">
          <span className="witness-footer__mode-label">NORMAL</span>
        </div>

        <button className="witness-footer__toggle">
          <span className="witness-footer__toggle-icon">{expanded ? 'v' : '^'}</span>
        </button>
      </div>

      {expanded && (
        <div className="witness-footer__panel">
          <div className="witness-footer__panel-header">
            <h3 className="witness-footer__panel-title">Witness Stream</h3>
          </div>
          <div className="witness-log">
            {events.map((event) => (
              <div key={event.id} className="witness-log__entry" data-type={event.type}>
                <span className="witness-log__time">
                  {event.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
                </span>
                <span className="witness-log__type">{event.type.toUpperCase().padEnd(7)}</span>
                <span className="witness-log__content">
                  {event.action || event.path || event.insight}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </footer>
  );
}

export const WitnessFooterCollapsed: StoryObj = {
  name: 'WitnessFooter - Collapsed',
  render: () => (
    <div style={{ height: '200px', position: 'relative', background: '#141418' }}>
      <MockWitnessFooter />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Compact footer bar showing last 3 witness events.

**Components:**
- Connection status (green dot = connected)
- Recent events with icons (mark: \`|-\`, kblock: \`{}\`, crystal: \`<>\`)
- Mode indicator (NORMAL, INSERT, etc.)
- Expand toggle
        `,
      },
    },
  },
};

export const WitnessFooterExpanded: StoryObj = {
  name: 'WitnessFooter - Expanded',
  render: () => {
    const [expanded, setExpanded] = useState(true);

    return (
      <div style={{ height: '400px', position: 'relative', background: '#141418' }}>
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
          }}
        >
          <footer className="witness-footer" data-expanded={expanded}>
            <div className="witness-footer__bar" onClick={() => setExpanded(!expanded)}>
              <div className="witness-footer__status" data-connected={true}>
                <span className="witness-footer__status-dot" />
                <span className="witness-footer__status-label">WITNESS</span>
              </div>
              <div className="witness-footer__events">
                <span className="text-gray-500 text-sm">Click to collapse</span>
              </div>
              <button className="witness-footer__toggle">
                <span className="witness-footer__toggle-icon">v</span>
              </button>
            </div>
            <div className="witness-footer__panel">
              <div className="witness-footer__panel-header">
                <h3 className="witness-footer__panel-title">Witness Stream</h3>
              </div>
              <div className="witness-log">
                {mockWitnessEvents.map((event) => (
                  <div key={event.id} className="witness-log__entry" data-type={event.type}>
                    <span className="witness-log__time">
                      {event.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
                    </span>
                    <span className="witness-log__type">{event.type.toUpperCase().padEnd(7)}</span>
                    <span className="witness-log__content">
                      {event.action || event.path || event.insight}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </footer>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: `
Expanded panel shows full witness log in \`tail -f\` style.

Each entry shows:
- Timestamp (HH:MM:SS)
- Event type (MARK, KBLOCK, CRYSTAL, etc.)
- Content summary
        `,
      },
    },
  },
};

export const WitnessFooterDisconnected: StoryObj = {
  name: 'WitnessFooter - Disconnected',
  render: () => (
    <div style={{ height: '200px', position: 'relative', background: '#141418' }}>
      <MockWitnessFooter connected={false} events={[]} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Disconnected state shows "RECONNECTING" with gray status dot.',
      },
    },
  },
};

// =============================================================================
// DerivationTrail Stories
// =============================================================================

/**
 * Mock DerivationTrail that doesn't require full Telescope context.
 */
function MockDerivationTrail({
  history = [
    { nodeId: 'principles.md', layer: 1 },
    { nodeId: 'joy-inducing', layer: 2 },
    { nodeId: 'witness-system', layer: 3 },
  ],
  focalPoint = 'WitnessFooter.tsx',
  compact = false,
}) {
  const getIcon = (layer: number) => {
    const icons: Record<number, string> = { 1: '*', 2: '<>', 3: '@', 4: '#', 5: '->', 6: '~', 7: '[]' };
    return icons[layer] || 'o';
  };

  return (
    <nav
      className={`derivation-trail ${compact ? 'derivation-trail--compact' : ''}`}
      aria-label="Derivation breadcrumb trail"
    >
      {history.length > 0 && (
        <button className="derivation-trail__back" title="Navigate to parent">
          <span className="derivation-trail__back-icon">{'<-'}</span>
        </button>
      )}

      <ol className="derivation-trail__list">
        {history.map((item) => (
          <li key={item.nodeId} className="derivation-trail__item">
            <button className="derivation-trail__link" title={`${getLayerName(item.layer)}: ${item.nodeId}`}>
              <span className="derivation-trail__icon">{getIcon(item.layer)}</span>
              {!compact && <span className="derivation-trail__label">{item.nodeId}</span>}
            </button>
            <span className="derivation-trail__separator">-{'>'}</span>
          </li>
        ))}

        {focalPoint && (
          <li className="derivation-trail__item derivation-trail__item--current">
            <span className="derivation-trail__current">
              <span className="derivation-trail__icon">@</span>
              {!compact && <span className="derivation-trail__label">{focalPoint}</span>}
            </span>
          </li>
        )}
      </ol>
    </nav>
  );
}

export const DerivationTrailDefault: StoryObj = {
  name: 'DerivationTrail - Default',
  render: () => (
    <div className="p-4 bg-gray-900 rounded-lg">
      <MockDerivationTrail />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Breadcrumb showing derivation from axioms to current focal point.

**Philosophy:** "The proof IS the decision. The mark IS the witness."

Each item shows:
- Layer icon (Axioms: *, Values: <>, Goals: @, Specs: #, Actions: ->, Reflections: ~, Documents: [])
- Node identifier
- Separator arrow

Click any item to navigate back to that point in the derivation chain.
        `,
      },
    },
  },
};

export const DerivationTrailCompact: StoryObj = {
  name: 'DerivationTrail - Compact',
  render: () => (
    <div className="p-4 bg-gray-900 rounded-lg">
      <MockDerivationTrail compact={true} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Compact mode shows only layer icons, suitable for narrow spaces.',
      },
    },
  },
};

export const DerivationTrailLongPath: StoryObj = {
  name: 'DerivationTrail - Long Path',
  render: () => (
    <div className="p-4 bg-gray-900 rounded-lg overflow-x-auto">
      <MockDerivationTrail
        history={[
          { nodeId: 'axioms/core.md', layer: 1 },
          { nodeId: 'values/joy-inducing', layer: 2 },
          { nodeId: 'goals/witness-everything', layer: 3 },
          { nodeId: 'specs/witness-protocol.md', layer: 4 },
          { nodeId: 'actions/implement-footer', layer: 5 },
          { nodeId: 'reflections/design-review', layer: 6 },
        ]}
        focalPoint="WitnessFooter.tsx"
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Long derivation paths can be truncated with ellipsis via maxItems prop.',
      },
    },
  },
};

// =============================================================================
// FocalDistanceRuler Stories
// =============================================================================

export const FocalDistanceRulerDefault: StoryObj = {
  name: 'FocalDistanceRuler - Default',
  render: () => {
    const [visibleLayers, setVisibleLayers] = useState([4]);

    return (
      <div className="flex gap-8 p-4 bg-gray-900 rounded-lg" style={{ minHeight: '400px' }}>
        <FocalDistanceRuler
          visibleLayers={visibleLayers}
          onLayerClick={(layer) => setVisibleLayers([layer])}
        />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <p className="text-lg mb-2">Current Layer: L{visibleLayers[0]}</p>
            <p className="text-sm">{getLayerName(visibleLayers[0])}</p>
          </div>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: `
Vertical ruler showing the 7-layer epistemic hierarchy.

**Layers (Viridis gradient):**
| Layer | Name | Color | Distance |
|-------|------|-------|----------|
| L1 | Axioms | Purple | Infinity (cosmic) |
| L2 | Values | Purple-teal | 1000 |
| L3 | Goals | Teal | 100 |
| L4 | Specs | Green | 10 (default) |
| L5 | Actions | Lime | 1 |
| L6 | Reflections | Yellow-green | 1 |
| L7 | Documents | Yellow | 0 (ground) |

Click any layer to jump to that focal distance.
        `,
      },
    },
  },
};

export const FocalDistanceRulerCompact: StoryObj = {
  name: 'FocalDistanceRuler - Compact',
  render: () => {
    const [visibleLayers, setVisibleLayers] = useState([4]);

    return (
      <div className="flex gap-4 p-4 bg-gray-900 rounded-lg" style={{ minHeight: '400px' }}>
        <FocalDistanceRuler
          visibleLayers={visibleLayers}
          onLayerClick={(layer) => setVisibleLayers([layer])}
          compact={true}
        />
        <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
          Compact mode: icons only
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Compact mode shows only layer icons, suitable for narrow sidebars.',
      },
    },
  },
};

export const FocalDistanceRulerWithControls: StoryObj = {
  name: 'FocalDistanceRuler - With Controls',
  render: () => {
    const [visibleLayers, setVisibleLayers] = useState([4]);
    const [lossThreshold, setLossThreshold] = useState(0.5);
    const [showGradients, setShowGradients] = useState(true);

    return (
      <div className="flex gap-8 p-4 bg-gray-900 rounded-lg" style={{ minHeight: '500px' }}>
        <FocalDistanceRuler
          visibleLayers={visibleLayers}
          onLayerClick={(layer) => setVisibleLayers([layer])}
          lossThreshold={lossThreshold}
          onLossThresholdChange={setLossThreshold}
          showGradients={showGradients}
          onGradientsToggle={() => setShowGradients(!showGradients)}
        />
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <div className="text-center text-gray-400">
            <p className="text-lg mb-2">Layer: L{visibleLayers[0]} ({getLayerName(visibleLayers[0])})</p>
            <p className="text-sm">Loss Threshold: {(lossThreshold * 100).toFixed(0)}%</p>
            <p className="text-sm">Gradients: {showGradients ? 'Visible' : 'Hidden'}</p>
          </div>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: `
Ruler with additional controls:
- **Loss Threshold Slider:** Filter nodes by loss value (0 = axioms only, 1 = show all)
- **Gradient Toggle:** Show/hide gradient field visualization
        `,
      },
    },
  },
};

export const FocalDistanceRulerMultiLayer: StoryObj = {
  name: 'FocalDistanceRuler - Multi-Layer View',
  render: () => {
    const [visibleLayers, setVisibleLayers] = useState([3, 4, 5]);

    return (
      <div className="flex gap-8 p-4 bg-gray-900 rounded-lg" style={{ minHeight: '400px' }}>
        <FocalDistanceRuler
          visibleLayers={visibleLayers}
          onLayerClick={(layer) => {
            // Toggle layer in selection
            if (visibleLayers.includes(layer)) {
              setVisibleLayers(visibleLayers.filter((l) => l !== layer));
            } else {
              setVisibleLayers([...visibleLayers, layer].sort());
            }
          }}
        />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-gray-400">
            <p className="text-lg mb-2">Visible Layers:</p>
            <div className="flex gap-2 justify-center">
              {visibleLayers.map((l) => (
                <span key={l} className="px-2 py-1 bg-gray-800 rounded text-sm">
                  L{l}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Multiple layers can be visible simultaneously during zoom transitions.',
      },
    },
  },
};

// =============================================================================
// Responsive Layout Demo
// =============================================================================

export const ResponsiveLayout: StoryObj = {
  decorators: [withProviders],
  render: () => (
    <AppShell>
      <div className="p-4">
        <div className="grid gap-4">
          <div className="text-gray-400 text-sm">
            Resize viewport to observe responsive behavior
          </div>

          {/* Mobile-first layout */}
          <div className="flex flex-col md:flex-row gap-4">
            {/* Sidebar - hidden on mobile */}
            <aside className="hidden md:block w-48 p-4 bg-gray-800/50 rounded-lg">
              <FocalDistanceRuler
                visibleLayers={[4]}
                onLayerClick={() => {}}
                compact={true}
              />
            </aside>

            {/* Main content */}
            <main className="flex-1 p-4 bg-gray-800/50 rounded-lg min-h-[300px]">
              <div className="mb-4">
                <MockDerivationTrail compact={false} />
              </div>
              <div className="text-gray-500 text-center py-8">
                Main content area
              </div>
            </main>
          </div>
        </div>
      </div>
    </AppShell>
  ),
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story: `
Responsive layout demonstration:
- **Mobile:** FocalDistanceRuler hidden, DerivationTrail full width
- **Tablet+:** Sidebar with compact ruler, main content with trail
        `,
      },
    },
  },
};

// =============================================================================
// Full Layout Integration
// =============================================================================

export const FullLayoutIntegration: StoryObj = {
  decorators: [withProviders],
  render: () => (
    <AppShell>
      <div className="flex h-[calc(100vh-120px)]">
        {/* Left sidebar - Focal Distance Ruler */}
        <aside className="w-40 border-r border-gray-800 p-2">
          <FocalDistanceRuler
            visibleLayers={[4]}
            onLayerClick={() => {}}
          />
        </aside>

        {/* Main content area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Derivation trail header */}
          <header className="p-2 border-b border-gray-800">
            <MockDerivationTrail />
          </header>

          {/* Content */}
          <div className="flex-1 p-6 overflow-auto">
            <div className="max-w-4xl mx-auto">
              <h1 className="text-2xl font-semibold text-white mb-4">
                Witness Protocol Specification
              </h1>
              <p className="text-gray-400 mb-6">
                "The proof IS the decision. The mark IS the witness."
              </p>
              <div className="prose prose-invert">
                <p className="text-gray-500">
                  This demonstration shows all layout components working together:
                  AppShell provides the outer frame, FocalDistanceRuler enables
                  epistemic navigation, DerivationTrail shows provenance, and
                  WitnessFooter streams real-time witness events.
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </AppShell>
  ),
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story: `
## Complete Layout Integration

All layout components working together as they would in the production app:

1. **AppShell** - Outer frame with navbar and witness footer
2. **FocalDistanceRuler** - Left sidebar for layer navigation
3. **DerivationTrail** - Header showing epistemic provenance
4. **WitnessFooter** - Bottom bar streaming real-time events

This is the "cathedral navigation experience" - humble frames that let
content glow while maintaining constant awareness of witness events
and epistemic position.
        `,
      },
    },
  },
};
