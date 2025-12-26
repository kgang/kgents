/**
 * Feed Primitive Stories
 *
 * "The feed is not a view of data. The feed IS the primary interface."
 *
 * STARK BIOME: Surface hierarchy, text hierarchy, Bare Edge styling.
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { FeedItem } from './FeedItem';
import { FeedFilters } from './FeedFilters';
import type { KBlock, FeedFilter, FeedRanking } from './types';
import './Feed.css';

// =============================================================================
// Mock K-Block Data
// =============================================================================

const now = new Date();

const mockKBlocks: KBlock[] = [
  {
    id: 'kb-001', title: 'Architectural Decision: Event-Driven State',
    content: 'We adopt event-driven architecture. Events are first-class citizens, state changes are traceable via witness marks, composition through event streams.',
    layer: 3, loss: 0.08, author: 'k-gent',
    createdAt: new Date(now.getTime() - 2 * 60 * 60 * 1000),
    updatedAt: new Date(now.getTime() - 30 * 60 * 1000),
    tags: ['architecture', 'events'], principles: ['COMPOSABLE', 'GENERATIVE'], edgeCount: 12,
  },
  {
    id: 'kb-002', title: 'Witness Mark: Crystal Integration Complete',
    content: 'Crystal storage layer fully integrated with witness bus. Async batch writes, cryptographic hashing, Galois layer annotations preserved.',
    layer: 5, loss: 0.15, author: 'm-gent',
    createdAt: new Date(now.getTime() - 4 * 60 * 60 * 1000),
    updatedAt: new Date(now.getTime() - 1 * 60 * 60 * 1000),
    tags: ['witness', 'crystal'], principles: ['ETHICAL', 'TASTEFUL'], edgeCount: 8,
  },
  {
    id: 'kb-003', title: 'Goal: Achieve Constitutional L3 Trust',
    content: 'Target: Maintain alignment >= 0.9 for 30 days. Violation rate < 1%, trust capital >= 1.0, no ETHICAL violations.',
    layer: 3, loss: 0.22, author: 'kent',
    createdAt: new Date(now.getTime() - 24 * 60 * 60 * 1000),
    updatedAt: new Date(now.getTime() - 12 * 60 * 60 * 1000),
    tags: ['goal', 'trust'], principles: ['ETHICAL', 'JOY_INDUCING'], edgeCount: 5,
  },
  {
    id: 'kb-004', title: 'Spec Drift Detected: Feed Implementation',
    content: 'WARNING: Implementation drifted from spec. Missing virtualization, added client-side ranking (spec says backend-only).',
    layer: 4, loss: 0.65, author: 'g-gent',
    createdAt: new Date(now.getTime() - 6 * 60 * 60 * 1000),
    updatedAt: new Date(now.getTime() - 2 * 60 * 60 * 1000),
    tags: ['drift', 'warning'], principles: ['CURATED'], edgeCount: 3,
  },
  {
    id: 'kb-005', title: 'Axiom: Joy Over Efficiency',
    content: 'A tasteful interaction that brings joy is worth 10x an efficient interaction that feels sterile. Do not optimize joy away.',
    layer: 1, loss: 0.02, author: 'kent',
    createdAt: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000),
    tags: ['axiom', 'philosophy'], principles: ['JOY_INDUCING', 'TASTEFUL'], edgeCount: 24,
  },
  {
    id: 'kb-006', title: 'Service: Feed Backend API',
    content: 'AGENTESE endpoints: self.feed.cosmos (all), self.feed.coherent (loss < 0.2), self.feed.feedback/record (interactions).',
    layer: 5, loss: 0.12, author: 'd-gent',
    createdAt: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(now.getTime() - 1 * 24 * 60 * 60 * 1000),
    tags: ['service', 'api'], principles: ['COMPOSABLE'], edgeCount: 15,
  },
  {
    id: 'kb-007', title: 'CRITICAL: Coherence Collapse in Town Simulation',
    content: 'Emergency: Coherence dropped below 20%. Coalition trust matrix not updating. Immediate action required.',
    layer: 6, loss: 0.85, author: 't-gent',
    createdAt: new Date(now.getTime() - 30 * 60 * 1000),
    updatedAt: new Date(now.getTime() - 15 * 60 * 1000),
    tags: ['emergency'], principles: [], edgeCount: 2,
  },
];

// =============================================================================
// Meta & Documentation
// =============================================================================

const meta: Meta = {
  title: 'Primitives/Feed',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
## Feed — The Primary Interface

Everything is a K-Block. The feed is how you navigate them.

**K-Block Structure:**
- **Layer (1-7)**: Galois hierarchy (Axiom -> Implementation)
- **Loss (0-1)**: Coherence metric (0 = perfect, 1 = max drift)
- **Principles**: Alignment with constitutional principles

**Algorithmic Ranking:**
- Chronological, loss-ascending/descending, engagement, algorithmic
- Algorithmic combines: coherence (30%) + engagement (40%) + principles (20%) + recency (10%)

**Filter Semantics:**
- Layer: L1 Axiom, L2 Value, L3 Capability, L4 Domain, L5 Service, L6 Construction, L7 Implementation
- Loss range: Healthy (<20%), Warning (20-50%), Critical (50-80%), Emergency (>80%)
        `,
      },
    },
  },
};

export default meta;

// =============================================================================
// FeedItem Stories
// =============================================================================

export const DefaultItem: StoryObj = {
  name: 'FeedItem - Default',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
      <FeedItem kblock={mockKBlocks[0]} isExpanded={false} onClick={() => {}} />
    </div>
  ),
};

export const HighLossWarning: StoryObj = {
  name: 'FeedItem - High Loss (Warning)',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
      <FeedItem kblock={mockKBlocks[3]} isExpanded={false} onClick={() => {}} />
    </div>
  ),
};

export const LowLossHealthy: StoryObj = {
  name: 'FeedItem - Low Loss (Healthy)',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
      <FeedItem kblock={mockKBlocks[4]} isExpanded={false} onClick={() => {}} />
    </div>
  ),
};

export const CriticalLoss: StoryObj = {
  name: 'FeedItem - Critical Loss (Emergency)',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
      <FeedItem kblock={mockKBlocks[6]} isExpanded={false} onClick={() => {}} />
    </div>
  ),
};

export const ExpandedItem: StoryObj = {
  name: 'FeedItem - Expanded State',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
      <FeedItem kblock={mockKBlocks[0]} isExpanded={true} onClick={() => {}} onEngage={() => {}} onDismiss={() => {}} />
    </div>
  ),
};

export const CompactItem: StoryObj = {
  name: 'FeedItem - Compact Variant',
  render: () => (
    <div style={{ maxWidth: '400px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
      <FeedItem kblock={mockKBlocks[1]} isExpanded={false} onClick={() => {}} />
    </div>
  ),
};

export const ItemWithWitnessMarks: StoryObj = {
  name: 'FeedItem - With Witness Marks',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
      <FeedItem kblock={mockKBlocks[1]} isExpanded={true} onClick={() => {}} />
    </div>
  ),
};

export const ItemWithConstitutionalScore: StoryObj = {
  name: 'FeedItem - With Constitutional Score',
  render: () => {
    const kblock: KBlock = { ...mockKBlocks[2], principles: ['ETHICAL', 'JOY_INDUCING', 'TASTEFUL', 'COMPOSABLE'] };
    return (
      <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
        <FeedItem kblock={kblock} isExpanded={true} onClick={() => {}} />
      </div>
    );
  },
};

// =============================================================================
// FeedFilters Stories
// =============================================================================

export const FiltersDefault: StoryObj = {
  name: 'FeedFilters - Default',
  render: () => {
    const Demo = () => {
      const [filters, setFilters] = useState<FeedFilter[]>([]);
      const [ranking, setRanking] = useState<FeedRanking>('chronological');
      return (
        <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
          <FeedFilters filters={filters} onFiltersChange={setFilters} ranking={ranking} onRankingChange={setRanking} />
        </div>
      );
    };
    return <Demo />;
  },
};

export const FiltersWithActive: StoryObj = {
  name: 'FeedFilters - With Active Filter',
  render: () => {
    const Demo = () => {
      const [filters, setFilters] = useState<FeedFilter[]>([
        { type: 'layer', value: 3, label: 'Layer 3: Capability', active: true },
      ]);
      const [ranking, setRanking] = useState<FeedRanking>('chronological');
      return (
        <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
          <FeedFilters filters={filters} onFiltersChange={setFilters} ranking={ranking} onRankingChange={setRanking} />
        </div>
      );
    };
    return <Demo />;
  },
};

export const FiltersMultiple: StoryObj = {
  name: 'FeedFilters - Multiple Filters Selected',
  render: () => {
    const Demo = () => {
      const [filters, setFilters] = useState<FeedFilter[]>([
        { type: 'layer', value: 5, label: 'Layer 5: Service', active: true },
        { type: 'loss-range', value: [0, 0.2] as [number, number], label: 'Loss 0-20%', active: true },
        { type: 'author', value: 'kent', label: 'Author: kent', active: false },
      ]);
      const [ranking, setRanking] = useState<FeedRanking>('loss-ascending');
      return (
        <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
          <FeedFilters filters={filters} onFiltersChange={setFilters} ranking={ranking} onRankingChange={setRanking} />
        </div>
      );
    };
    return <Demo />;
  },
};

export const FilterByLayer: StoryObj = {
  name: 'FeedFilters - Filter by Layer (L1-L7)',
  render: () => {
    const Demo = () => {
      const [filters, setFilters] = useState<FeedFilter[]>([
        { type: 'layer', value: 1, label: 'Layer 1: Axiom', active: true },
      ]);
      const [ranking, setRanking] = useState<FeedRanking>('chronological');
      return (
        <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
          <FeedFilters filters={filters} onFiltersChange={setFilters} ranking={ranking} onRankingChange={setRanking} />
        </div>
      );
    };
    return <Demo />;
  },
};

export const FilterByLossRange: StoryObj = {
  name: 'FeedFilters - Filter by Loss Range',
  render: () => {
    const Demo = () => {
      const [filters, setFilters] = useState<FeedFilter[]>([
        { type: 'loss-range', value: [0.5, 0.8] as [number, number], label: 'Loss 50-80% (Critical)', active: true },
      ]);
      const [ranking, setRanking] = useState<FeedRanking>('loss-descending');
      return (
        <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
          <FeedFilters filters={filters} onFiltersChange={setFilters} ranking={ranking} onRankingChange={setRanking} />
        </div>
      );
    };
    return <Demo />;
  },
};

export const FilterByAuthor: StoryObj = {
  name: 'FeedFilters - Filter by Author',
  render: () => {
    const Demo = () => {
      const [filters, setFilters] = useState<FeedFilter[]>([
        { type: 'author', value: 'kent', label: 'Author: kent', active: true },
      ]);
      const [ranking, setRanking] = useState<FeedRanking>('chronological');
      return (
        <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
          <FeedFilters filters={filters} onFiltersChange={setFilters} ranking={ranking} onRankingChange={setRanking} />
        </div>
      );
    };
    return <Demo />;
  },
};

// =============================================================================
// Feed Composite Stories
// =============================================================================

export const DenseFeed: StoryObj = {
  name: 'Feed - Dense (Many Items)',
  render: () => (
    <div style={{ maxWidth: '600px', maxHeight: '500px', overflowY: 'auto', padding: '16px', background: 'var(--surface-0, #141418)' }}>
      {mockKBlocks.map((kb) => <FeedItem key={kb.id} kblock={kb} isExpanded={false} onClick={() => {}} />)}
      <div style={{ display: 'flex', alignItems: 'center', padding: '16px', color: '#666', fontSize: '12px' }}>
        <span style={{ flex: 1, height: '1px', background: '#28282F' }} />
        <span style={{ padding: '0 12px' }}>End of feed</span>
        <span style={{ flex: 1, height: '1px', background: '#28282F' }} />
      </div>
    </div>
  ),
};

export const EmptyState: StoryObj = {
  name: 'Feed - Empty State',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '48px', background: 'var(--surface-0, #141418)', textAlign: 'center', border: '1px solid #28282F', borderRadius: '4px' }}>
      <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.6 }}>&#128235;</div>
      <div style={{ color: 'var(--text-primary, #E0E0E6)', fontSize: '16px', marginBottom: '8px' }}>No items in feed</div>
      <div style={{ color: 'var(--text-muted, #8A8A94)', fontSize: '13px' }}>Try adjusting your filters or create some K-Blocks.</div>
    </div>
  ),
};

export const LoadingState: StoryObj = {
  name: 'Feed - Loading State',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '48px', background: 'var(--surface-0, #141418)', textAlign: 'center', border: '1px solid #28282F', borderRadius: '4px' }}>
      <div style={{ width: '24px', height: '24px', border: '2px solid #28282F', borderTopColor: '#C4A77D', borderRadius: '50%', margin: '0 auto 16px', animation: 'spin 1s linear infinite' }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{ color: 'var(--text-muted, #8A8A94)', fontSize: '13px' }}>Loading...</div>
    </div>
  ),
};

export const InfiniteScrollHint: StoryObj = {
  name: 'Feed - With Infinite Scroll Hint',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
      {mockKBlocks.slice(0, 3).map((kb) => <FeedItem key={kb.id} kblock={kb} isExpanded={false} onClick={() => {}} />)}
      <div style={{ padding: '24px', textAlign: 'center', color: '#8A8A94', fontSize: '12px', borderTop: '1px dashed #28282F' }}>
        <div>Scroll for more</div>
        <div style={{ fontSize: '18px', marginTop: '4px' }}>&#8595;</div>
      </div>
    </div>
  ),
};

export const FilteredSingleLayer: StoryObj = {
  name: 'Feed - Filtered (Single Layer)',
  render: () => {
    const layer3Items = mockKBlocks.filter((kb) => kb.layer === 3);
    return (
      <div style={{ maxWidth: '600px', padding: '16px', background: 'var(--surface-0, #141418)' }}>
        <div style={{ color: '#8A8A94', fontSize: '12px', marginBottom: '12px', padding: '8px', background: '#1a1a1f', borderRadius: '4px' }}>
          Filtered: Layer 3 (Capability) - {layer3Items.length} items
        </div>
        {layer3Items.map((kb) => <FeedItem key={kb.id} kblock={kb} isExpanded={false} onClick={() => {}} />)}
      </div>
    );
  },
};
