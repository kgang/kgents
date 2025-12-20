/**
 * Gestalt2D Component Tests
 *
 * Tests for the 2D Renaissance Living Architecture Visualizer.
 * Covers: LayerCard, ViolationFeed, ModuleDetail, Gestalt2D
 *
 * @see spec/protocols/2d-renaissance.md - Phase 3
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ShellProvider } from '@/shell';

// Components
import { LayerCard } from '@/components/gestalt/LayerCard';
import { ViolationFeed } from '@/components/gestalt/ViolationFeed';
import { ModuleDetail } from '@/components/gestalt/ModuleDetail';
import { Gestalt2D } from '@/components/gestalt/Gestalt2D';

import type { WorldCodebaseTopologyResponse } from '@/api/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockNodes: WorldCodebaseTopologyResponse['nodes'] = [
  {
    id: 'protocols.agentese',
    label: 'agentese',
    layer: 'protocols',
    health_grade: 'A+',
    health_score: 0.95,
    lines_of_code: 1200,
    coupling: 0.3,
    cohesion: 0.85,
    instability: 0.2,
    x: 0,
    y: 0,
    z: 0,
  },
  {
    id: 'protocols.api',
    label: 'api',
    layer: 'protocols',
    health_grade: 'A',
    health_score: 0.88,
    lines_of_code: 800,
    coupling: 0.25,
    cohesion: 0.8,
    instability: 0.15,
    x: 1,
    y: 0,
    z: 0,
  },
  {
    id: 'services.brain',
    label: 'brain',
    layer: 'services',
    health_grade: 'A',
    health_score: 0.9,
    lines_of_code: 1500,
    coupling: 0.4,
    cohesion: 0.75,
    instability: 0.3,
    x: 0,
    y: 1,
    z: 0,
  },
  {
    id: 'services.town',
    label: 'town',
    layer: 'services',
    health_grade: 'B+',
    health_score: 0.78,
    lines_of_code: 2000,
    coupling: 0.55,
    cohesion: 0.65,
    instability: 0.45,
    x: 1,
    y: 1,
    z: 0,
  },
  {
    id: 'services.park',
    label: 'park',
    layer: 'services',
    health_grade: 'C',
    health_score: 0.55,
    lines_of_code: 600,
    coupling: 0.7,
    cohesion: 0.5,
    instability: 0.6,
    x: 2,
    y: 1,
    z: 0,
  },
];

const mockLinks: WorldCodebaseTopologyResponse['links'] = [
  {
    source: 'services.brain',
    target: 'protocols.agentese',
    import_type: 'direct',
    is_violation: false,
    violation_severity: null,
  },
  {
    source: 'services.town',
    target: 'services.brain',
    import_type: 'direct',
    is_violation: true,
    violation_severity: 'medium',
  },
  {
    source: 'services.park',
    target: 'agents.flux',
    import_type: 'direct',
    is_violation: true,
    violation_severity: 'high',
  },
];

const mockTopology: WorldCodebaseTopologyResponse = {
  nodes: mockNodes,
  links: mockLinks,
  layers: ['protocols', 'services'],
  stats: {
    node_count: 5,
    link_count: 3,
    layer_count: 2,
    violation_count: 2,
    avg_health: 0.81,
    overall_grade: 'A-',
  },
};

// Shell wrapper for context
const withShell = (ui: React.ReactElement) => <ShellProvider>{ui}</ShellProvider>;

// =============================================================================
// LayerCard Tests
// =============================================================================

describe('LayerCard', () => {
  const protocolNodes = mockNodes.filter((n) => n.layer === 'protocols');

  it('renders layer name and module count', () => {
    render(withShell(<LayerCard layer="protocols" nodes={protocolNodes} color="#4A6B4A" />));

    expect(screen.getByText('Protocols')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Module count
  });

  it('shows health stats', () => {
    render(withShell(<LayerCard layer="protocols" nodes={protocolNodes} color="#4A6B4A" />));

    expect(screen.getByText('2 healthy')).toBeInTheDocument();
  });

  it('renders module badges', () => {
    render(withShell(<LayerCard layer="protocols" nodes={protocolNodes} color="#4A6B4A" />));

    expect(screen.getByText('agentese')).toBeInTheDocument();
    expect(screen.getByText('api')).toBeInTheDocument();
  });

  it('calls onModuleSelect when module clicked', () => {
    const onModuleSelect = vi.fn();

    render(
      withShell(
        <LayerCard
          layer="protocols"
          nodes={protocolNodes}
          color="#4A6B4A"
          onModuleSelect={onModuleSelect}
        />
      )
    );

    fireEvent.click(screen.getByText('agentese'));
    expect(onModuleSelect).toHaveBeenCalledWith('protocols.agentese');
  });

  it('expands to show more modules on click', () => {
    const manyNodes = Array.from({ length: 15 }, (_, i) => ({
      ...mockNodes[0],
      id: `module-${i}`,
      label: `module-${i}`,
    }));

    render(withShell(<LayerCard layer="protocols" nodes={manyNodes} color="#4A6B4A" />));

    // Initially shows +N more
    expect(screen.getByText(/\+\d+ more/)).toBeInTheDocument();

    // Click to expand
    fireEvent.click(screen.getByText('Protocols'));

    // Should show more modules now (up to MAX_EXPANDED_MODULES)
    expect(screen.getByText('module-0')).toBeInTheDocument();
  });

  it('highlights at-risk modules with grade badge', () => {
    const atRiskNodes = [{ ...mockNodes[0], id: 'risky', label: 'risky', health_grade: 'D' }];

    render(withShell(<LayerCard layer="test" nodes={atRiskNodes} color="#4A6B4A" />));

    expect(screen.getByText('D')).toBeInTheDocument();
  });
});

// =============================================================================
// ViolationFeed Tests
// =============================================================================

describe('ViolationFeed', () => {
  const violations = mockLinks.filter((l) => l.is_violation);

  it('renders violation count', () => {
    render(<ViolationFeed violations={violations} />);

    expect(screen.getByText('Violations')).toBeInTheDocument();
    // Use getAllByText since '2' appears multiple times in the violation UI
    expect(screen.getAllByText('2').length).toBeGreaterThan(0);
  });

  it('shows source and target for violations', () => {
    render(<ViolationFeed violations={violations} />);

    // Should show extracted module names
    expect(screen.getByText('services.town')).toBeInTheDocument();
    expect(screen.getByText('services.brain')).toBeInTheDocument();
  });

  it('displays severity badges', () => {
    render(<ViolationFeed violations={violations} />);

    expect(screen.getByText('medium')).toBeInTheDocument();
    expect(screen.getByText('high')).toBeInTheDocument();
  });

  it('shows healthy state when no violations', () => {
    render(<ViolationFeed violations={[]} />);

    expect(screen.getByText('No architecture violations detected')).toBeInTheDocument();
  });

  it('respects maxDisplay limit', () => {
    const manyViolations = Array.from({ length: 15 }, (_, i) => ({
      ...mockLinks[1],
      source: `module-${i}`,
      target: `target-${i}`,
    }));

    render(<ViolationFeed violations={manyViolations} maxDisplay={5} />);

    // Should show "Show X more" button
    expect(screen.getByText(/Show \d+ more violations/)).toBeInTheDocument();
  });
});

// =============================================================================
// ModuleDetail Tests
// =============================================================================

describe('ModuleDetail', () => {
  const testModule = mockNodes[0]; // protocols.agentese

  it('renders module name and layer', () => {
    render(<ModuleDetail module={testModule} links={mockLinks} />);

    expect(screen.getByText('agentese')).toBeInTheDocument();
    expect(screen.getByText('protocols')).toBeInTheDocument();
  });

  it('displays health grade prominently', () => {
    render(<ModuleDetail module={testModule} links={mockLinks} />);

    expect(screen.getByText('A+')).toBeInTheDocument();
    expect(screen.getByText('95%')).toBeInTheDocument();
  });

  it('shows metrics (coupling, cohesion)', () => {
    render(<ModuleDetail module={testModule} links={mockLinks} />);

    expect(screen.getByText('Coupling')).toBeInTheDocument();
    expect(screen.getByText('Cohesion')).toBeInTheDocument();
    expect(screen.getByText('Lines')).toBeInTheDocument();
  });

  it('lists dependents when module is a target', () => {
    const targetModule = mockNodes[2]; // services.brain

    render(<ModuleDetail module={targetModule} links={mockLinks} />);

    expect(screen.getByText(/Dependents/)).toBeInTheDocument();
  });

  it('lists dependencies when module is a source', () => {
    const sourceModule = mockNodes[2]; // services.brain

    render(<ModuleDetail module={sourceModule} links={mockLinks} />);

    // Check that Dependencies section exists (may appear multiple times)
    expect(screen.getAllByText(/Dependencies/).length).toBeGreaterThan(0);
    // Brain depends on agentese
    expect(screen.getByText('protocols.agentese')).toBeInTheDocument();
  });

  it('calls onClose when X clicked', () => {
    const onClose = vi.fn();

    render(<ModuleDetail module={testModule} links={mockLinks} onClose={onClose} />);

    const closeButton = screen.getByLabelText('Close');
    fireEvent.click(closeButton);
    expect(onClose).toHaveBeenCalled();
  });
});

// =============================================================================
// Gestalt2D Integration Tests
// =============================================================================

describe('Gestalt2D', () => {
  it('renders header with stats', () => {
    render(withShell(<Gestalt2D topology={mockTopology} />));

    expect(screen.getByText('Gestalt')).toBeInTheDocument();
    expect(screen.getByText('Living Architecture Visualizer')).toBeInTheDocument();
    expect(screen.getByText('A-')).toBeInTheDocument(); // Overall grade
  });

  it('renders architecture tree (default view)', () => {
    render(withShell(<Gestalt2D topology={mockTopology} />));

    // Default view is tree mode which shows "Architecture Tree" header
    expect(screen.getByText('Architecture Tree')).toBeInTheDocument();
    // Stats shown: "X modules · Y layers"
    expect(screen.getByText(/modules/)).toBeInTheDocument();
  });

  it('renders violations feed', () => {
    render(withShell(<Gestalt2D topology={mockTopology} />));

    // Violations section should be present
    expect(screen.getAllByText('Violations').length).toBeGreaterThan(0);
    // The violation count '2' appears in both header stats and feed
    expect(screen.getAllByText('2').length).toBeGreaterThan(0);
  });

  it('shows module count in header', () => {
    render(withShell(<Gestalt2D topology={mockTopology} />));

    expect(screen.getByText('5/5')).toBeInTheDocument(); // filtered/total
  });

  it('shows module detail when module selected', async () => {
    render(withShell(<Gestalt2D topology={mockTopology} />));

    // Click on a module badge
    fireEvent.click(screen.getByTitle(/agentese.*A\+/i));

    // Module detail should appear - grade appears in both badge and detail panel
    expect(screen.getAllByText('A+').length).toBeGreaterThan(0);
    expect(screen.getByText('Health Grade')).toBeInTheDocument();
  });
});

// =============================================================================
// Accessibility Tests
// =============================================================================

describe('Gestalt2D Accessibility', () => {
  it('layer cards are keyboard accessible', () => {
    render(
      withShell(<LayerCard layer="protocols" nodes={mockNodes.slice(0, 2)} color="#4A6B4A" />)
    );

    const button = screen.getByRole('button', { name: /Protocols/i });
    expect(button).toBeInTheDocument();
  });

  it('module badges have descriptive titles', () => {
    render(
      withShell(<LayerCard layer="protocols" nodes={mockNodes.slice(0, 1)} color="#4A6B4A" />)
    );

    const badge = screen.getByTitle(/agentese.*A\+.*LoC/i);
    expect(badge).toBeInTheDocument();
  });

  it('close button has aria-label', () => {
    render(<ModuleDetail module={mockNodes[0]} links={mockLinks} onClose={() => {}} />);

    expect(screen.getByLabelText('Close')).toBeInTheDocument();
  });
});

// =============================================================================
// Density Tests
// =============================================================================

describe('Gestalt2D Density Behavior', () => {
  it('renders compact mode correctly', () => {
    render(
      withShell(
        <LayerCard layer="protocols" nodes={mockNodes.slice(0, 2)} color="#4A6B4A" compact />
      )
    );

    // In compact mode, should not show health stats text
    expect(screen.queryByText('2 healthy')).not.toBeInTheDocument();
  });

  it('renders compact violation feed', () => {
    render(<ViolationFeed violations={mockLinks.filter((l) => l.is_violation)} compact />);

    // Compact mode should not show severity labels
    expect(screen.queryByText('medium')).not.toBeInTheDocument();
  });

  it('renders compact module detail', () => {
    render(<ModuleDetail module={mockNodes[0]} links={mockLinks} compact />);

    // Should still show key info
    expect(screen.getByText('agentese')).toBeInTheDocument();
    expect(screen.getByText('A+')).toBeInTheDocument();
  });
});
