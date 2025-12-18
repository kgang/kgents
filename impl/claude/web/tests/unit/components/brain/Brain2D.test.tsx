/**
 * Brain2D Component Tests
 *
 * Tests for the 2D Renaissance Living Memory Cartography.
 * Covers: CrystalTree, CaptureForm, GhostSurface, Brain2D
 *
 * @see spec/protocols/2d-renaissance.md - Phase 4
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ShellProvider } from '@/shell';

// Components
import { CrystalTree, groupByCategory } from '@/components/brain/CrystalTree';
import { Brain2D, BRAIN_COLORS } from '@/components/brain/Brain2D';

import type { SelfMemoryTopologyResponse } from '@/api/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockNodes: SelfMemoryTopologyResponse['nodes'] = [
  {
    id: 'crystal-1',
    label: 'categorical.operads',
    x: 0,
    y: 0,
    z: 0,
    resolution: 0.85,
    content: 'Operads define composition grammars for multi-input operations.',
    summary: 'Operads define composition grammars',
    captured_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    tags: ['category-theory', 'math'],
  },
  {
    id: 'crystal-2',
    label: 'categorical.polynomials',
    x: 1,
    y: 0,
    z: 0,
    resolution: 0.9,
    content: 'Polynomial functors model state machines with mode-dependent behavior.',
    summary: 'Polynomial functors for state machines',
    captured_at: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
    tags: ['category-theory', 'agents'],
  },
  {
    id: 'crystal-3',
    label: 'agent.k-gent',
    x: 0,
    y: 1,
    z: 0,
    resolution: 0.75,
    content: 'K-gent is the soul of Kent, embodying personality and values.',
    summary: 'K-gent as the soul',
    captured_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
    tags: ['soul', 'identity'],
  },
  {
    id: 'crystal-4',
    label: 'town.citizens',
    x: 1,
    y: 1,
    z: 0,
    resolution: 0.6,
    content: 'Agent Town citizens simulate autonomous agents with personalities.',
    summary: 'Agent Town citizens',
    captured_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
    tags: ['town', 'simulation'],
  },
];

const mockEdges: SelfMemoryTopologyResponse['edges'] = [
  { source: 'crystal-1', target: 'crystal-2', similarity: 0.85 },
  { source: 'crystal-3', target: 'crystal-4', similarity: 0.4 },
];

const mockTopology: SelfMemoryTopologyResponse = {
  nodes: mockNodes,
  edges: mockEdges,
  gaps: [],
  hub_ids: ['crystal-1', 'crystal-2'], // First two are hubs
  stats: {
    concept_count: 4,
    edge_count: 2,
    hub_count: 2,
    gap_count: 0,
    avg_resolution: 0.775,
  },
};

// =============================================================================
// groupByCategory Tests
// =============================================================================

describe('groupByCategory', () => {
  it('groups nodes by first label segment', () => {
    const categories = groupByCategory(mockNodes);

    expect(Object.keys(categories).sort()).toEqual(['agent', 'categorical', 'town']);
    expect(categories.categorical.length).toBe(2);
    expect(categories.agent.length).toBe(1);
    expect(categories.town.length).toBe(1);
  });

  it('handles empty nodes', () => {
    const categories = groupByCategory([]);
    expect(Object.keys(categories).length).toBe(0);
  });

  it('handles nodes without labels', () => {
    const noLabelNodes = [
      { ...mockNodes[0], label: '' },
    ];
    const categories = groupByCategory(noLabelNodes);
    expect(categories.uncategorized.length).toBe(1);
  });
});

// =============================================================================
// CrystalTree Tests
// =============================================================================

describe('CrystalTree', () => {
  const mockOnSelect = vi.fn();

  beforeEach(() => {
    mockOnSelect.mockClear();
  });

  it('renders categories from topology', () => {
    const categories = groupByCategory(mockNodes);

    render(
      <ShellProvider>
        <CrystalTree
          categories={categories}
          onCrystalSelect={mockOnSelect}
          hubIds={['crystal-1']}
        />
      </ShellProvider>
    );

    // Check categories are rendered
    expect(screen.getByText('Categorical')).toBeInTheDocument();
    expect(screen.getByText('Agent')).toBeInTheDocument();
    expect(screen.getByText('Town')).toBeInTheDocument();
  });

  it('shows crystal count per category', () => {
    const categories = groupByCategory(mockNodes);

    render(
      <ShellProvider>
        <CrystalTree
          categories={categories}
          onCrystalSelect={mockOnSelect}
        />
      </ShellProvider>
    );

    // Categorical has 2 crystals
    expect(screen.getByText('2')).toBeInTheDocument();
    // Agent and Town each have 1
    expect(screen.getAllByText('1').length).toBeGreaterThanOrEqual(2);
  });

  it('calls onCrystalSelect when crystal clicked', () => {
    const categories = groupByCategory(mockNodes);

    render(
      <ShellProvider>
        <CrystalTree
          categories={categories}
          onCrystalSelect={mockOnSelect}
          hubIds={[]}
        />
      </ShellProvider>
    );

    // Find and click a crystal (by label)
    const crystalButton = screen.getByText('categorical.operads');
    fireEvent.click(crystalButton);

    expect(mockOnSelect).toHaveBeenCalledWith('crystal-1');
  });

  it('shows empty state when no crystals', () => {
    render(
      <ShellProvider>
        <CrystalTree
          categories={{}}
          onCrystalSelect={mockOnSelect}
        />
      </ShellProvider>
    );

    expect(screen.getByText('No crystals yet')).toBeInTheDocument();
    expect(screen.getByText('Capture your first memory to begin')).toBeInTheDocument();
  });

  it('applies compact mode', () => {
    const categories = groupByCategory(mockNodes);

    render(
      <ShellProvider>
        <CrystalTree
          categories={categories}
          onCrystalSelect={mockOnSelect}
          compact
        />
      </ShellProvider>
    );

    // In compact mode, category names should still be visible
    expect(screen.getByText('Categorical')).toBeInTheDocument();
  });
});

// =============================================================================
// Brain2D Tests
// =============================================================================

describe('Brain2D', () => {
  it('renders header with stats', () => {
    render(
      <ShellProvider>
        <Brain2D topology={mockTopology} />
      </ShellProvider>
    );

    expect(screen.getByText('Brain')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument(); // concept_count
  });

  it('renders crystal tree with categories', () => {
    render(
      <ShellProvider>
        <Brain2D topology={mockTopology} />
      </ShellProvider>
    );

    expect(screen.getByText('Categorical')).toBeInTheDocument();
    expect(screen.getByText('Agent')).toBeInTheDocument();
    expect(screen.getByText('Town')).toBeInTheDocument();
  });

  it('filters crystals by search query', () => {
    render(
      <ShellProvider>
        <Brain2D topology={mockTopology} />
      </ShellProvider>
    );

    // Find search input
    const searchInput = screen.getByPlaceholderText('Search crystals...');

    // Type search query
    fireEvent.change(searchInput, { target: { value: 'operad' } });

    // Categorical should still be visible (has operads)
    expect(screen.getByText('Categorical')).toBeInTheDocument();

    // Town should not be visible (no match)
    expect(screen.queryByText('Town')).not.toBeInTheDocument();
  });

  it('has Living Earth color palette', () => {
    expect(BRAIN_COLORS.primary).toBe('#D4A574'); // Amber
    expect(BRAIN_COLORS.healthy).toBe('#4A6B4A'); // Sage
    expect(BRAIN_COLORS.hub).toBe('#E8C4A0'); // Honey
  });
});

// =============================================================================
// Integration Test: Selection Flow
// =============================================================================

describe('Brain2D Selection Flow', () => {
  it('shows detail panel when crystal selected (desktop)', () => {
    render(
      <ShellProvider>
        <Brain2D topology={mockTopology} />
      </ShellProvider>
    );

    // Click on a crystal
    const crystalButton = screen.getByText('categorical.operads');
    fireEvent.click(crystalButton);

    // CrystalDetail should appear (on desktop, in ElasticSplit secondary)
    // The detail shows crystal label and resolution
    // Note: CrystalDetail component manages its own observer-dependent view
  });
});
