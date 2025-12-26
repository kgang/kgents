/**
 * Navigation Components Stories
 *
 * STARK BIOME: "The persona is a garden, not a museum."
 *
 * Navigation in kgents is AGENTESE-aware. Every link is a path through
 * the five contexts: world, self, concept, void, time.
 *
 * ## Design Philosophy
 *
 * - **Surface Awareness**: NavigationSidebar adapts content based on current surface
 * - **AGENTESE Paths**: AgentLink converts semantic paths to URLs
 * - **Earned Glow**: Active states use `glow-spore` accent, frames stay humble
 * - **Keyboard-First**: Shortcuts are first-class citizens (Ctrl+b, shift+surface keys)
 *
 * ## The Five Surfaces
 *
 * | Surface        | Path             | Purpose                    |
 * |----------------|------------------|----------------------------|
 * | Document       | world.document   | Hypergraph editor          |
 * | Director       | self.director    | Document canvas overview   |
 * | Chart          | world.chart      | Constellation visualization|
 * | Memory         | self.memory      | Marks, crystals, evidence  |
 * | Zero Seed      | void.zero-seed   | Axiom grounding            |
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { MemoryRouter } from 'react-router-dom';
import { useState, useCallback } from 'react';
import { NavigationSidebar, type Surface } from './NavigationSidebar';
import { AgentLink, AgentNavLink } from './AgentLink';

// =============================================================================
// Meta
// =============================================================================

const meta: Meta = {
  title: 'Navigation/Sidebar',
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <MemoryRouter initialEntries={['/world.document']}>
        <Story />
      </MemoryRouter>
    ),
  ],
  parameters: {
    docs: {
      description: {
        component: `
# Navigation System

The navigation system provides AGENTESE-aware routing through the five contexts.

## Core Components

### NavigationSidebar
The unified navigation shell that adapts its content based on the current surface.
Supports five surfaces: Document, Director, Chart, Memory, and Zero Seed.

### AgentLink
AGENTESE-aware link component that converts semantic paths to URLs.
Supports aspects, parameters, and active state detection.

## STARK BIOME Principles

- **Steel Frame**: \`steel-carbon\` backgrounds, \`steel-gunmetal\` borders
- **Earned Glow**: \`glow-spore\` for active navigation items
- **Keyboard Native**: Shortcuts visible on hover (\`Ctrl+b\` toggle, \`Shift+E/D/C/M/Z\` surfaces)

## Surface Content

Each surface gets contextual content in the sidebar:
- **Document**: Recent nodes, trail breadcrumbs, quick actions
- **Director**: Navigation hints
- **Chart**: Constellation picker
- **Memory**: Category filters (Marks, Crystals, Evidence, Trails)
- **Zero Seed**: Five-level navigation
        `,
      },
    },
  },
};

export default meta;

// =============================================================================
// Mock Data
// =============================================================================

const mockRecentNodes = [
  { path: 'spec/agents/k-gent.md', title: 'K-gent Specification' },
  { path: 'spec/protocols/witness.md', title: 'Witness Protocol' },
  { path: 'impl/claude/services/brain/core.py', title: 'Brain Core' },
  { path: 'spec/agents/d-gent.md', title: 'D-gent (Persistence)' },
  { path: 'docs/skills/metaphysical-fullstack.md', title: 'Metaphysical Fullstack' },
];

const mockTrail = [
  { path: 'spec/agents/README.md', title: 'Agents Overview' },
  { path: 'spec/agents/k-gent.md', title: 'K-gent' },
  { path: 'spec/protocols/witness.md', title: 'Witness Protocol' },
];

// =============================================================================
// Wrapper for Interactive Stories
// =============================================================================

const SidebarWrapper = ({
  initialSurface = 'world.document',
  initialExpanded = true,
  height = '600px',
}: {
  initialSurface?: Surface;
  initialExpanded?: boolean;
  height?: string;
}) => {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);

  const handleNavigatePath = useCallback((path: string) => {
    setSelectedPath(path);
    console.log('Navigate to:', path);
  }, []);

  return (
    <div
      style={{
        position: 'relative',
        height,
        background: '#141418',
        borderRadius: '4px',
        border: '1px solid #28282F',
        overflow: 'hidden',
      }}
    >
      <NavigationSidebar
        surface={initialSurface}
        isExpanded={isExpanded}
        onToggle={() => setIsExpanded(!isExpanded)}
        recentNodes={mockRecentNodes}
        trail={mockTrail}
        onNavigatePath={handleNavigatePath}
        topOffset={0}
        bottomOffset={0}
      />
      <div
        style={{
          marginLeft: isExpanded ? '280px' : '48px',
          padding: '24px',
          transition: 'margin-left 0.2s ease',
        }}
      >
        <h2 style={{ color: '#E5E7EB', marginBottom: '16px' }}>Content Area</h2>
        {selectedPath && (
          <p style={{ color: '#9CA3AF', fontSize: '14px' }}>
            Selected: <code style={{ color: '#6cf' }}>{selectedPath}</code>
          </p>
        )}
      </div>
    </div>
  );
};

// =============================================================================
// NavigationSidebar Stories
// =============================================================================

export const Default: StoryObj = {
  name: 'Sidebar - Default (Expanded)',
  render: () => <SidebarWrapper />,
  parameters: {
    docs: {
      description: {
        story: `
The default NavigationSidebar in expanded state showing:
- Surface navigation (Document, Director, Chart, Memory, Zero Seed)
- Recent nodes list
- Trail breadcrumbs
- Quick actions

Click items in the sidebar to see navigation events logged to console.
        `,
      },
    },
  },
};

export const Collapsed: StoryObj = {
  name: 'Sidebar - Collapsed',
  render: () => <SidebarWrapper initialExpanded={false} />,
  parameters: {
    docs: {
      description: {
        story: `
Collapsed sidebar shows only icons. Click the expand button or press \`Ctrl+b\` to expand.
The sidebar auto-collapses to icon-only mode in compact viewport density.
        `,
      },
    },
  },
};

export const DocumentSurface: StoryObj = {
  name: 'Surface - Document (world.document)',
  render: () => <SidebarWrapper initialSurface="world.document" />,
  parameters: {
    docs: {
      description: {
        story: `
**Document Surface** - The hypergraph editor surface.

Shows:
- Trail breadcrumbs (last 5 visited nodes, reversed)
- Recent nodes (last 8 accessed)
- Quick actions (\`:e\` open, \`:w\` save)
        `,
      },
    },
  },
};

export const DirectorSurface: StoryObj = {
  name: 'Surface - Director (self.director)',
  render: () => <SidebarWrapper initialSurface="self.director" />,
  parameters: {
    docs: {
      description: {
        story: `
**Director Surface** - Document canvas overview.

Shows navigation hints for the canvas:
- \`j\`/\`k\` to navigate
- \`/\` to search
- \`Enter\` to open
        `,
      },
    },
  },
};

export const ChartSurface: StoryObj = {
  name: 'Surface - Chart (world.chart)',
  render: () => <SidebarWrapper initialSurface="world.chart" />,
  parameters: {
    docs: {
      description: {
        story: `
**Chart Surface** - Constellation visualization.

Shows constellation picker hint. The full implementation would list
available constellations (agent relationships, dependency graphs, etc).
        `,
      },
    },
  },
};

export const MemorySurface: StoryObj = {
  name: 'Surface - Memory (self.memory)',
  render: () => <SidebarWrapper initialSurface="self.memory" />,
  parameters: {
    docs: {
      description: {
        story: `
**Memory Surface** - Witness marks, crystals, and evidence.

Shows category filters:
- **Marks**: Witness marks with timestamps
- **Crystals**: Crystallized insights
- **Evidence**: Empirical observations
- **Trails**: Navigation history
        `,
      },
    },
  },
};

export const ZeroSeedSurface: StoryObj = {
  name: 'Surface - Zero Seed (void.zero-seed)',
  render: () => <SidebarWrapper initialSurface="void.zero-seed" />,
  parameters: {
    docs: {
      description: {
        story: `
**Zero Seed Surface** - Axiom grounding and proof engine.

Shows the seven-layer navigation:
- \`1\` L1-L2: Axioms & Values
- \`2\` L3-L4: Goals & Specs
- \`3\` L5-L6: Actions & Reflections
- \`4\` L7: Representation
- \`5\` Visual Overview
        `,
      },
    },
  },
};

export const EmptyRecents: StoryObj = {
  name: 'Sidebar - Empty State',
  render: () => {
    const [isExpanded, setIsExpanded] = useState(true);

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
        <NavigationSidebar
          surface="world.document"
          isExpanded={isExpanded}
          onToggle={() => setIsExpanded(!isExpanded)}
          recentNodes={[]}
          trail={[]}
          topOffset={0}
          bottomOffset={0}
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: `
Empty state when no recent nodes or trail exists.
Shows contextual empty messages: "No recent nodes", "No trail".
        `,
      },
    },
  },
};

// =============================================================================
// AgentLink Stories
// =============================================================================

export const AgentLinkBasic: StoryObj = {
  name: 'AgentLink - Basic Usage',
  render: () => (
    <div style={{ padding: '24px', background: '#141418' }}>
      <h3 style={{ color: '#E5E7EB', marginBottom: '16px' }}>AGENTESE Links</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <AgentLink path="world.town.citizen.kent_001" className="agent-link-demo">
          <span style={{ color: '#6cf' }}>world.town.citizen.kent_001</span>
        </AgentLink>
        <AgentLink path="self.chat" aspect="stream" className="agent-link-demo">
          <span style={{ color: '#6cf' }}>self.chat (aspect: stream)</span>
        </AgentLink>
        <AgentLink
          path="concept.proof"
          params={{ layer: '3', mode: 'strict' }}
          className="agent-link-demo"
        >
          <span style={{ color: '#6cf' }}>concept.proof (with params)</span>
        </AgentLink>
      </div>
      <style>{`
        .agent-link-demo {
          display: block;
          padding: 12px 16px;
          background: #28282F;
          border-radius: 4px;
          text-decoration: none;
          transition: background 0.15s;
        }
        .agent-link-demo:hover {
          background: #333;
        }
      `}</style>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
**AgentLink** converts AGENTESE paths to URLs.

| Prop    | Purpose                          |
|---------|----------------------------------|
| path    | AGENTESE path (e.g., 'world.town.citizen.kent_001') |
| aspect  | Optional aspect to invoke        |
| params  | Optional query parameters        |
| replace | Replace history instead of push  |
        `,
      },
    },
  },
};

export const AgentNavLinkActive: StoryObj = {
  name: 'AgentNavLink - Active States',
  render: () => (
    <MemoryRouter initialEntries={['/self.chat']}>
      <div style={{ padding: '24px', background: '#141418' }}>
        <h3 style={{ color: '#E5E7EB', marginBottom: '16px' }}>Navigation Links with Active State</h3>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {[
            { path: 'world.document', label: 'Document' },
            { path: 'self.chat', label: 'Chat (Active)' },
            { path: 'concept.proof', label: 'Proof Engine' },
            { path: 'void.zero-seed', label: 'Zero Seed' },
          ].map(({ path, label }) => (
            <AgentNavLink
              key={path}
              path={path}
              className="nav-link-demo"
              activeClassName="nav-link-demo--active"
            >
              {label}
            </AgentNavLink>
          ))}
        </nav>
        <style>{`
          .nav-link-demo {
            display: block;
            padding: 10px 16px;
            background: transparent;
            border-radius: 4px;
            color: #888;
            text-decoration: none;
            transition: background 0.15s, color 0.15s;
          }
          .nav-link-demo:hover {
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
          }
          .nav-link-demo--active {
            background: rgba(102, 204, 255, 0.1);
            color: #6cf;
          }
        `}</style>
      </div>
    </MemoryRouter>
  ),
  parameters: {
    docs: {
      description: {
        story: `
**AgentNavLink** extends AgentLink with active state detection.

The \`activeClassName\` is applied when the current URL matches the AGENTESE path.
Follows STARK BIOME: active state earns the \`glow-spore\` accent.
        `,
      },
    },
  },
};

export const CustomActiveCheck: StoryObj = {
  name: 'AgentNavLink - Custom Active Check',
  render: () => (
    <MemoryRouter initialEntries={['/world.document/spec/agents']}>
      <div style={{ padding: '24px', background: '#141418' }}>
        <h3 style={{ color: '#E5E7EB', marginBottom: '16px' }}>Custom Active Detection</h3>
        <p style={{ color: '#9CA3AF', fontSize: '14px', marginBottom: '16px' }}>
          Current path: <code style={{ color: '#6cf' }}>/world.document/spec/agents</code>
        </p>
        <nav style={{ display: 'flex', gap: '8px' }}>
          <AgentNavLink
            path="world.document"
            className="pill-link"
            activeClassName="pill-link--active"
            isActive={(currentPath) => currentPath.includes('/world.document')}
          >
            Documents
          </AgentNavLink>
          <AgentNavLink
            path="self.memory"
            className="pill-link"
            activeClassName="pill-link--active"
          >
            Memory
          </AgentNavLink>
        </nav>
        <style>{`
          .pill-link {
            padding: 8px 16px;
            background: #28282F;
            border-radius: 20px;
            color: #888;
            text-decoration: none;
            font-size: 14px;
            transition: all 0.15s;
          }
          .pill-link:hover {
            background: #333;
            color: #fff;
          }
          .pill-link--active {
            background: rgba(102, 204, 255, 0.2);
            color: #6cf;
          }
        `}</style>
      </div>
    </MemoryRouter>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Use \`isActive\` prop for custom active state detection.
Useful for parent-path matching or complex routing scenarios.
        `,
      },
    },
  },
};

// =============================================================================
// Responsive Variants
// =============================================================================

export const ResponsiveCompact: StoryObj = {
  name: 'Responsive - Compact Viewport',
  render: () => <SidebarWrapper height="400px" />,
  parameters: {
    viewport: { defaultViewport: 'mobile1' },
    docs: {
      description: {
        story: `
In compact viewport (<768px):
- Sidebar auto-collapses to icon-only mode
- Tap to expand temporarily
- Touch-optimized tap targets (48x48px minimum)
        `,
      },
    },
  },
};

export const ResponsiveTablet: StoryObj = {
  name: 'Responsive - Tablet Viewport',
  render: () => <SidebarWrapper height="500px" />,
  parameters: {
    viewport: { defaultViewport: 'ipad' },
    docs: {
      description: {
        story: `
In comfortable viewport (768-1024px):
- Sidebar can be expanded or collapsed
- Comfortable spacing for touch and mouse
- Full content visible in expanded state
        `,
      },
    },
  },
};

// =============================================================================
// Philosophy Story
// =============================================================================

export const PhilosophyOverview: StoryObj = {
  name: 'Design Philosophy',
  render: () => (
    <div style={{ padding: '32px', background: '#141418', maxWidth: '800px' }}>
      <h2 style={{ color: '#E5E7EB', marginBottom: '24px' }}>
        Navigation Philosophy
      </h2>
      <div style={{ color: '#9CA3AF', lineHeight: 1.7 }}>
        <h3 style={{ color: '#C4A77D', marginBottom: '12px' }}>
          "The persona is a garden, not a museum."
        </h3>
        <p style={{ marginBottom: '16px' }}>
          Navigation in kgents is not a static map but a living garden that adapts
          to context. The sidebar breathes with the current surface, showing only
          what's relevant.
        </p>

        <h3 style={{ color: '#6cf', marginTop: '24px', marginBottom: '12px' }}>
          AGENTESE: The Semantic Protocol
        </h3>
        <p style={{ marginBottom: '16px' }}>
          Every navigation target is an AGENTESE path through five contexts:
        </p>
        <ul style={{ paddingLeft: '20px', marginBottom: '16px' }}>
          <li><strong>world.*</strong> - External entities and environments</li>
          <li><strong>self.*</strong> - Internal memory and capability</li>
          <li><strong>concept.*</strong> - Abstract definitions and logic</li>
          <li><strong>void.*</strong> - Entropy, serendipity, gratitude</li>
          <li><strong>time.*</strong> - Traces, forecasts, schedules</li>
        </ul>

        <h3 style={{ color: '#22c55e', marginTop: '24px', marginBottom: '12px' }}>
          Keyboard-First, Touch-Ready
        </h3>
        <p>
          Navigation is designed for vim-like keyboard users but never excludes
          mouse or touch. Every action has a keyboard shortcut, every target
          has adequate touch area.
        </p>
      </div>
    </div>
  ),
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        story: 'The philosophical foundation of the navigation system.',
      },
    },
  },
};
