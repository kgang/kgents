/**
 * Registry Component Stories
 *
 * STARK BIOME Design System Demo
 *
 * These stories showcase the Token Registry components:
 * - TokenRegistry: Main virtualized grid container
 * - TokenTile: Individual token cards with tier icons
 * - TokenFilters: Search and filter controls
 * - TokenDetailPanel: Slide-out detail view
 *
 * Philosophy: "The frame is humble. The content glows."
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState, useCallback } from 'react';
import { TokenRegistry } from './TokenRegistry';
import { TokenTile, TokenTilePlaceholder } from './TokenTile';
import { TokenFilters } from './TokenFilters';
import { TokenDetailPanel } from './TokenDetailPanel';
import type { TokenItem, TokenType, TokenStatus, FilterState } from './types';
import { DEFAULT_FILTERS, TIER_LABELS, TIER_ICONS } from './types';

// Import component CSS
import './TokenRegistry.css';
import './TokenTile.css';
import './TokenFilters.css';
import './TokenDetailPanel.css';

// =============================================================================
// Mock Data - Tokens
// =============================================================================

/** Generate mock tokens for testing */
const generateMockTokens = (count: number): TokenItem[] => {
  const types: TokenType[] = ['spec', 'principle', 'impl'];
  const statuses: TokenStatus[] = ['ACTIVE', 'ORPHAN', 'DEPRECATED', 'ARCHIVED', 'CONFLICTING'];
  const tiers: (0 | 1 | 2 | 3 | 4)[] = [0, 1, 2, 3, 4];

  const tokenNames = [
    'AGENTESE Protocol', 'Witness Service', 'PolyAgent Core', 'Operad Grammar',
    'Sheaf Coherence', 'DataBus Events', 'SynergyBus Bridge', 'Town Simulation',
    'K-gent Soul', 'M-gent Memory', 'Constitutional Trust', 'Zero Seed',
    'Galois Metrics', 'Director Dashboard', 'Registry Browser', 'Hypergraph Editor',
    'Elastic UI', 'Modal System', 'Breathing Animation', 'Joy Primitives',
    'Feed Renderer', 'Loss Display', 'Meta Observer', 'Contradiction Resolver',
  ];

  return Array.from({ length: count }, (_, i) => {
    const tier = tiers[i % 5];
    const type = types[i % 3];
    const status = i < count * 0.7 ? 'ACTIVE' : statuses[Math.floor(Math.random() * 5)];
    const name = tokenNames[i % tokenNames.length];

    return {
      id: `spec/${type}s/${name.toLowerCase().replace(/\s+/g, '-')}.md`,
      name: name,
      type,
      tier,
      status,
      icon: TIER_ICONS[tier],
      hasEvidence: Math.random() > 0.3,
      claimCount: Math.floor(Math.random() * 20) + 1,
      implCount: Math.floor(Math.random() * 10),
      testCount: Math.floor(Math.random() * 8),
      wordCount: Math.floor(Math.random() * 2000) + 200,
    };
  });
};

/** Sample tokens for stories */
const mockTokens = generateMockTokens(24);

/** Principle tokens (Tier 0) */
const mockPrincipleTokens: TokenItem[] = [
  {
    id: 'spec/principles/composable.md',
    name: 'Composable',
    type: 'principle',
    tier: 0,
    status: 'ACTIVE',
    icon: TIER_ICONS[0],
    hasEvidence: true,
    claimCount: 12,
    implCount: 45,
    testCount: 38,
    wordCount: 890,
  },
  {
    id: 'spec/principles/tasteful.md',
    name: 'Tasteful',
    type: 'principle',
    tier: 0,
    status: 'ACTIVE',
    icon: TIER_ICONS[0],
    hasEvidence: true,
    claimCount: 8,
    implCount: 32,
    testCount: 24,
    wordCount: 650,
  },
  {
    id: 'spec/principles/ethical.md',
    name: 'Ethical',
    type: 'principle',
    tier: 0,
    status: 'ACTIVE',
    icon: TIER_ICONS[0],
    hasEvidence: true,
    claimCount: 15,
    implCount: 28,
    testCount: 22,
    wordCount: 1200,
  },
  {
    id: 'spec/principles/joy_inducing.md',
    name: 'Joy Inducing',
    type: 'principle',
    tier: 0,
    status: 'ACTIVE',
    icon: TIER_ICONS[0],
    hasEvidence: true,
    claimCount: 6,
    implCount: 18,
    testCount: 12,
    wordCount: 480,
  },
  {
    id: 'spec/principles/curated.md',
    name: 'Curated',
    type: 'principle',
    tier: 0,
    status: 'ACTIVE',
    icon: TIER_ICONS[0],
    hasEvidence: true,
    claimCount: 9,
    implCount: 21,
    testCount: 15,
    wordCount: 720,
  },
  {
    id: 'spec/principles/heterarchical.md',
    name: 'Heterarchical',
    type: 'principle',
    tier: 0,
    status: 'ACTIVE',
    icon: TIER_ICONS[0],
    hasEvidence: true,
    claimCount: 11,
    implCount: 14,
    testCount: 8,
    wordCount: 950,
  },
  {
    id: 'spec/principles/generative.md',
    name: 'Generative',
    type: 'principle',
    tier: 0,
    status: 'ACTIVE',
    icon: TIER_ICONS[0],
    hasEvidence: true,
    claimCount: 7,
    implCount: 16,
    testCount: 10,
    wordCount: 580,
  },
];

/** Mixed status tokens for testing filters */
const mockMixedStatusTokens: TokenItem[] = [
  { ...mockPrincipleTokens[0], status: 'ACTIVE' },
  { ...mockPrincipleTokens[1], status: 'ORPHAN', id: 'spec/orphaned-spec.md', name: 'Orphaned Spec' },
  { ...mockPrincipleTokens[2], status: 'DEPRECATED', id: 'spec/old-api.md', name: 'Old API' },
  { ...mockPrincipleTokens[3], status: 'ARCHIVED', id: 'spec/archived-feature.md', name: 'Archived Feature' },
  { ...mockPrincipleTokens[4], status: 'CONFLICTING', id: 'spec/conflicting-claim.md', name: 'Conflicting Claim' },
];

// =============================================================================
// Storybook Meta
// =============================================================================

const meta: Meta<typeof TokenRegistry> = {
  title: 'Components/Registry',
  component: TokenRegistry,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: `
## Token Registry - Virtualized Token Grid

The Registry system provides a utilitarian flat grid for navigating 100s of specs,
dozens of principles, and 1000s of implementations.

**Components:**
- **TokenRegistry**: Main virtualized grid container
- **TokenTile**: Individual token cards with tier icons
- **TokenFilters**: Search and filter controls
- **TokenDetailPanel**: Slide-out detail view

**Features:**
- Virtualized rendering (handles 1000s of items at 60fps)
- Responsive grid (auto-columns based on width)
- Vim-style keyboard navigation (j/k, Enter, /)
- Slide-out detail panel

**Keyboard Shortcuts:**
- \`j\`/\`k\` - Navigate up/down
- \`Enter\` - Open detail panel
- \`e\` - Open in editor
- \`/\` - Focus search
- \`?\` - Show help

**STARK BIOME Design:**
- Steel frame with tier-colored borders
- Minimal chrome, maximum content density
- Earned glow through tier colors

Philosophy: "The frame is humble. The content glows."
        `,
      },
    },
  },
};

export default meta;

type Story = StoryObj<typeof TokenRegistry>;

// =============================================================================
// TokenRegistry Stories
// =============================================================================

/** Default registry view with mock data. */
export const Default: Story = {
  name: 'Registry - Default',
  args: {
    onOpenEditor: (path) => console.log('Open editor:', path),
  },
  decorators: [
    (Story) => (
      <div style={{ height: '600px', width: '100%', background: '#0A0A0C' }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    docs: {
      description: {
        story: 'The default registry view. Currently shows empty state since the spec ledger backend was removed.',
      },
    },
  },
};

// =============================================================================
// TokenTile Stories
// =============================================================================

export const TileDefault: StoryObj = {
  name: 'Tile - Default',
  render: () => (
    <TokenTile
      token={mockPrincipleTokens[0]}
      onClick={() => console.log('Clicked')}
      onDoubleClick={() => console.log('Double-clicked')}
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'Default token tile with hover tooltip showing path and stats.',
      },
    },
  },
};

export const TileSelected: StoryObj = {
  name: 'Tile - Selected',
  render: () => (
    <TokenTile
      token={mockPrincipleTokens[0]}
      selected={true}
      onClick={() => console.log('Clicked')}
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'Selected tile shows highlighted border based on tier color.',
      },
    },
  },
};

export const TileAllTiers: StoryObj = {
  name: 'Tile - All Tiers',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {[0, 1, 2, 3, 4].map((tier) => (
        <div key={tier} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ color: '#8A8A94', fontSize: '12px', width: '100px' }}>
            T{tier}: {TIER_LABELS[tier]}
          </span>
          <TokenTile
            token={{
              ...mockPrincipleTokens[0],
              tier: tier as 0 | 1 | 2 | 3 | 4,
              icon: TIER_ICONS[tier],
              name: `${TIER_LABELS[tier]} Item`,
              id: `spec/${TIER_LABELS[tier].toLowerCase()}/item.md`,
            }}
          />
        </div>
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All five tier variants with their corresponding icons and colors.',
      },
    },
  },
};

export const TileAllStatuses: StoryObj = {
  name: 'Tile - All Statuses',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {mockMixedStatusTokens.map((token) => (
        <div key={token.id} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ color: '#8A8A94', fontSize: '12px', width: '100px' }}>
            {token.status}
          </span>
          <TokenTile token={token} />
        </div>
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All five status variants: Active, Orphan, Deprecated, Archived, Conflicting.',
      },
    },
  },
};

export const TileWithEvidence: StoryObj = {
  name: 'Tile - With/Without Evidence',
  render: () => (
    <div style={{ display: 'flex', gap: '24px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <span style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>
          Has Evidence
        </span>
        <TokenTile
          token={{ ...mockPrincipleTokens[0], hasEvidence: true }}
        />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <span style={{ color: '#8A8A94', fontSize: '11px', textTransform: 'uppercase' }}>
          No Evidence
        </span>
        <TokenTile
          token={{ ...mockPrincipleTokens[0], hasEvidence: false, implCount: 0, testCount: 0 }}
        />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Tiles with and without evidence (impl/test counts).',
      },
    },
  },
};

export const TilePlaceholder: StoryObj = {
  name: 'Tile - Loading Placeholder',
  render: () => <TokenTilePlaceholder />,
  parameters: {
    docs: {
      description: {
        story: 'Placeholder tile shown during loading states.',
      },
    },
  },
};

export const TileGrid: StoryObj = {
  name: 'Tile - Grid Layout',
  render: () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
        gap: '8px',
        padding: '16px',
        background: '#141418',
        borderRadius: '4px',
      }}
    >
      {mockPrincipleTokens.map((token) => (
        <TokenTile key={token.id} token={token} />
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Grid layout showing all 7 principle tokens.',
      },
    },
  },
};

// =============================================================================
// TokenFilters Stories
// =============================================================================

/** Interactive filters demo */
const FiltersDemo = () => {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [searchFocused, setSearchFocused] = useState(false);

  const toggleType = useCallback((type: TokenType) => {
    setFilters((prev) => ({
      ...prev,
      types: prev.types.includes(type)
        ? prev.types.filter((t) => t !== type)
        : [...prev.types, type],
    }));
  }, []);

  const toggleStatus = useCallback((status: TokenStatus) => {
    setFilters((prev) => ({
      ...prev,
      statuses: prev.statuses.includes(status)
        ? prev.statuses.filter((s) => s !== status)
        : [...prev.statuses, status],
    }));
  }, []);

  const toggleTier = useCallback((tier: number) => {
    setFilters((prev) => ({
      ...prev,
      tiers: prev.tiers.includes(tier)
        ? prev.tiers.filter((t) => t !== tier)
        : [...prev.tiers, tier],
    }));
  }, []);

  const toggleEvidence = useCallback(() => {
    setFilters((prev) => ({
      ...prev,
      hasEvidence: prev.hasEvidence === null ? true : prev.hasEvidence ? false : null,
    }));
  }, []);

  return (
    <div style={{ maxWidth: '800px', padding: '16px', background: '#141418', borderRadius: '4px' }}>
      <TokenFilters
        filters={filters}
        totalCount={150}
        filteredCount={filters.types.length > 0 || filters.statuses.length > 0 ? 42 : 150}
        onSearchChange={(query) => setFilters((prev) => ({ ...prev, search: query }))}
        onToggleType={toggleType}
        onToggleStatus={toggleStatus}
        onToggleTier={toggleTier}
        onToggleEvidence={toggleEvidence}
        onClear={() => setFilters(DEFAULT_FILTERS)}
        searchFocused={searchFocused}
        onSearchFocus={() => setSearchFocused(true)}
        onSearchBlur={() => setSearchFocused(false)}
      />
    </div>
  );
};

export const FiltersDefault: StoryObj = {
  name: 'Filters - Interactive',
  render: () => <FiltersDemo />,
  parameters: {
    docs: {
      description: {
        story: 'Interactive filter bar. Try clicking the chips to toggle filters.',
      },
    },
  },
};

export const FiltersWithSearch: StoryObj = {
  name: 'Filters - With Search',
  render: () => (
    <div style={{ maxWidth: '800px', padding: '16px', background: '#141418', borderRadius: '4px' }}>
      <TokenFilters
        filters={{ ...DEFAULT_FILTERS, search: 'agentese' }}
        totalCount={150}
        filteredCount={12}
        onSearchChange={() => {}}
        onToggleType={() => {}}
        onToggleStatus={() => {}}
        onToggleTier={() => {}}
        onToggleEvidence={() => {}}
        onClear={() => {}}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Filter bar with an active search query showing reduced count.',
      },
    },
  },
};

export const FiltersActive: StoryObj = {
  name: 'Filters - Multiple Active',
  render: () => (
    <div style={{ maxWidth: '800px', padding: '16px', background: '#141418', borderRadius: '4px' }}>
      <TokenFilters
        filters={{
          search: '',
          types: ['spec', 'principle'],
          statuses: ['ACTIVE'],
          tiers: [0, 1],
          hasEvidence: true,
        }}
        totalCount={150}
        filteredCount={28}
        onSearchChange={() => {}}
        onToggleType={() => {}}
        onToggleStatus={() => {}}
        onToggleTier={() => {}}
        onToggleEvidence={() => {}}
        onClear={() => {}}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Multiple active filters showing the Clear button.',
      },
    },
  },
};

// =============================================================================
// TokenDetailPanel Stories
// =============================================================================

export const DetailPanel: StoryObj = {
  name: 'Detail Panel',
  render: () => (
    <div style={{ position: 'relative', height: '400px', width: '100%' }}>
      <TokenDetailPanel
        path="spec/protocols/agentese.md"
        onClose={() => console.log('Close')}
        onOpenEditor={(path) => console.log('Open editor:', path)}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Detail panel showing the current stub state. Backend has been removed.',
      },
    },
  },
};

// =============================================================================
// Combined & State Stories
// =============================================================================

export const FullRegistryDemo: StoryObj = {
  name: 'Full Demo',
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        padding: '24px',
        background: '#0A0A0C',
        minHeight: '600px',
      }}
    >
      <div style={{ background: '#141418', borderRadius: '4px', padding: '16px' }}>
        <TokenFilters
          filters={DEFAULT_FILTERS}
          totalCount={24}
          filteredCount={24}
          onSearchChange={() => {}}
          onToggleType={() => {}}
          onToggleStatus={() => {}}
          onToggleTier={() => {}}
          onToggleEvidence={() => {}}
          onClear={() => {}}
        />
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: '8px',
          padding: '16px',
          background: '#141418',
          borderRadius: '4px',
        }}
      >
        {mockTokens.slice(0, 20).map((token, idx) => (
          <TokenTile key={token.id} token={token} selected={idx === 3} />
        ))}
      </div>

      <div
        style={{
          padding: '12px 16px',
          background: '#141418',
          borderRadius: '4px',
          display: 'flex',
          gap: '24px',
          color: '#8A8A94',
          fontSize: '12px',
        }}
      >
        <span><kbd style={{ background: '#28282F', padding: '2px 6px', borderRadius: '2px' }}>j</kbd>/<kbd style={{ background: '#28282F', padding: '2px 6px', borderRadius: '2px' }}>k</kbd> nav</span>
        <span><kbd style={{ background: '#28282F', padding: '2px 6px', borderRadius: '2px' }}>Enter</kbd> details</span>
        <span><kbd style={{ background: '#28282F', padding: '2px 6px', borderRadius: '2px' }}>e</kbd> edit</span>
        <span><kbd style={{ background: '#28282F', padding: '2px 6px', borderRadius: '2px' }}>/</kbd> search</span>
        <span><kbd style={{ background: '#28282F', padding: '2px 6px', borderRadius: '2px' }}>?</kbd> help</span>
      </div>
    </div>
  ),
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        story: `
# Full Registry Demo

Complete registry UI with filters, grid, and keyboard hints.

This demonstrates the STARK BIOME design:
- Steel frame (#141418 panels on #0A0A0C background)
- Tier-colored borders on selected token
- Minimal keyboard hints bar
- Grid auto-adapts to container width
        `,
      },
    },
  },
};

export const EmptyState: StoryObj = {
  name: 'State - Empty',
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '300px',
        background: '#141418',
        borderRadius: '4px',
        padding: '48px',
      }}
    >
      <span style={{ fontSize: '24px', color: '#8A8A94', marginBottom: '12px' }}>
        &empty;
      </span>
      <p style={{ color: '#8A8A94', margin: 0, marginBottom: '16px' }}>
        No tokens match your filters
      </p>
      <button
        style={{
          background: '#28282F',
          border: '1px solid #3E3E46',
          borderRadius: '4px',
          color: '#E5E7EB',
          padding: '8px 16px',
          cursor: 'pointer',
        }}
      >
        Clear Filters
      </button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Empty state shown when no tokens match the current filters.',
      },
    },
  },
};

export const LoadingState: StoryObj = {
  name: 'State - Loading',
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '300px',
        background: '#141418',
        borderRadius: '4px',
        padding: '48px',
      }}
    >
      <span
        style={{
          fontSize: '24px',
          color: '#8A8A94',
          marginBottom: '12px',
          animation: 'pulse 2s ease-in-out infinite',
        }}
      >
        &loz;
      </span>
      <p style={{ color: '#8A8A94', margin: 0 }}>
        Loading registry...
      </p>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Loading state with pulsing diamond icon.',
      },
    },
  },
};

export const ErrorState: StoryObj = {
  name: 'State - Error',
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '300px',
        background: '#141418',
        borderRadius: '4px',
        padding: '48px',
        border: '1px solid rgba(239, 68, 68, 0.3)',
      }}
    >
      <span style={{ fontSize: '24px', color: '#EF4444', marginBottom: '12px' }}>
        !
      </span>
      <p style={{ color: '#EF4444', margin: 0, marginBottom: '16px' }}>
        Failed to load registry
      </p>
      <button
        style={{
          background: '#28282F',
          border: '1px solid #3E3E46',
          borderRadius: '4px',
          color: '#E5E7EB',
          padding: '8px 16px',
          cursor: 'pointer',
        }}
      >
        Retry
      </button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Error state with red accent and retry button.',
      },
    },
  },
};
