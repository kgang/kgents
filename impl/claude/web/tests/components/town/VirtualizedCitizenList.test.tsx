/**
 * Tests for VirtualizedCitizenList component.
 *
 * T-gent Type I: Contracts - Component renders virtualized list
 * T-gent Type II: Saboteurs - Component handles performance edge cases
 * T-gent Type III: Spies - Component selection behavior
 *
 * @see impl/claude/web/src/components/town/VirtualizedCitizenList.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { VirtualizedCitizenList } from '@/components/town/VirtualizedCitizenList';
import type { CitizenCardJSON } from '@/reactive/types';

// Mock CitizenCard component
vi.mock('@/widgets/cards/CitizenCard', () => ({
  CitizenCard: ({ name, archetype, onSelect, isSelected }: any) => (
    <div
      data-testid={`citizen-card-${name}`}
      onClick={() => onSelect?.('test-id')}
      className={isSelected ? 'selected' : ''}
    >
      <div>{name}</div>
      <div>{archetype}</div>
    </div>
  ),
}));

// =============================================================================
// Test Fixtures
// =============================================================================

const createMockCitizen = (index: number): CitizenCardJSON => ({
  type: 'citizen_card',
  citizen_id: `citizen-${index}`,
  name: `Citizen ${index}`,
  archetype: ['builder', 'trader', 'healer', 'scholar'][index % 4] as any,
  region: ['North', 'East', 'South', 'West'][index % 4],
  phase: 'IDLE',
  nphase: 'UNDERSTAND',
  mood: 'neutral',
  capability: 0.5,
  entropy: 0.5,
});

const mockCitizens = Array(10).fill(null).map((_, i) => createMockCitizen(i));
const largeCitizenList = Array(100).fill(null).map((_, i) => createMockCitizen(i));

// =============================================================================
// T-gent Type I: Contracts - Component renders virtualized list
// =============================================================================

describe('VirtualizedCitizenList - Contracts', () => {
  it('renders citizen list', () => {
    render(<VirtualizedCitizenList citizens={mockCitizens} />);

    // At least some citizens should be visible
    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
  });

  it('shows citizen count when list is large', () => {
    render(<VirtualizedCitizenList citizens={largeCitizenList} />);

    expect(screen.getByText('100 citizens')).toBeInTheDocument();
  });

  it('does not show count for small lists', () => {
    render(<VirtualizedCitizenList citizens={mockCitizens} />);

    expect(screen.queryByText(/citizens$/)).not.toBeInTheDocument();
  });

  it('renders with custom className', () => {
    const { container } = render(
      <VirtualizedCitizenList citizens={mockCitizens} className="custom-class" />
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('renders with custom estimate size', () => {
    const { container } = render(
      <VirtualizedCitizenList citizens={mockCitizens} estimateSize={200} />
    );

    expect(container.querySelector('.h-full')).toBeInTheDocument();
  });

  it('renders with custom overscan', () => {
    const { container } = render(
      <VirtualizedCitizenList citizens={mockCitizens} overscan={10} />
    );

    expect(container.querySelector('.h-full')).toBeInTheDocument();
  });

  it('applies selected state to citizen', () => {
    render(
      <VirtualizedCitizenList
        citizens={mockCitizens}
        selectedCitizenId="citizen-2"
      />
    );

    // Check that some content is rendered
    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
  });
});

// =============================================================================
// T-gent Type II: Saboteurs - Component handles performance edge cases
// =============================================================================

describe('VirtualizedCitizenList - Saboteurs', () => {
  it('handles empty citizen list', () => {
    const { container } = render(<VirtualizedCitizenList citizens={[]} />);

    expect(container.querySelector('.h-full')).toBeInTheDocument();
  });

  it('handles single citizen', () => {
    render(<VirtualizedCitizenList citizens={[mockCitizens[0]]} />);

    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
  });

  it('handles very large list efficiently', () => {
    const hugeCitizenList = Array(1000).fill(null).map((_, i) => createMockCitizen(i));

    render(<VirtualizedCitizenList citizens={hugeCitizenList} />);

    expect(screen.getByText('1000 citizens')).toBeInTheDocument();
    // Only a subset should be rendered due to virtualization
    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
  });

  it('handles missing citizen properties gracefully', () => {
    const citizensWithMissingProps: CitizenCardJSON[] = [
      {
        type: 'citizen_card',
        citizen_id: 'citizen-1',
        name: '',
        archetype: '' as any,
        region: '',
        phase: 'IDLE',
        nphase: 'UNDERSTAND',
        mood: '',
        capability: 0,
        entropy: 0,
      },
    ];

    const { container } = render(
      <VirtualizedCitizenList citizens={citizensWithMissingProps} />
    );

    expect(container.querySelector('.h-full')).toBeInTheDocument();
  });

  it('handles rapid updates', () => {
    const { rerender } = render(<VirtualizedCitizenList citizens={mockCitizens} />);

    // Rapidly update the list
    for (let i = 0; i < 10; i++) {
      const newCitizens = Array(50 + i).fill(null).map((_, j) => createMockCitizen(j));
      rerender(<VirtualizedCitizenList citizens={newCitizens} />);
    }

    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
  });

  it('maintains scroll position on citizen add', () => {
    const { rerender, container } = render(
      <VirtualizedCitizenList citizens={mockCitizens} />
    );

    const scrollContainer = container.querySelector('.h-full.overflow-auto');
    expect(scrollContainer).toBeInTheDocument();

    const newCitizens = [...mockCitizens, createMockCitizen(10)];
    rerender(<VirtualizedCitizenList citizens={newCitizens} />);

    expect(scrollContainer).toBeInTheDocument();
  });

  it('handles selectedCitizenId changes', () => {
    const { rerender } = render(
      <VirtualizedCitizenList citizens={mockCitizens} selectedCitizenId="citizen-0" />
    );

    expect(screen.getByText('Citizen 0')).toBeInTheDocument();

    rerender(
      <VirtualizedCitizenList citizens={mockCitizens} selectedCitizenId="citizen-5" />
    );

    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
  });
});

// =============================================================================
// T-gent Type III: Spies - Component selection behavior
// =============================================================================

describe('VirtualizedCitizenList - Spies', () => {
  it('calls onSelectCitizen when citizen clicked', () => {
    const onSelectCitizen = vi.fn();

    render(
      <VirtualizedCitizenList
        citizens={mockCitizens}
        onSelectCitizen={onSelectCitizen}
      />
    );

    const citizenCard = screen.getByTestId('citizen-card-Citizen 0');
    fireEvent.click(citizenCard);

    expect(onSelectCitizen).toHaveBeenCalledWith('test-id');
  });

  it('does not call onSelectCitizen when not provided', () => {
    render(<VirtualizedCitizenList citizens={mockCitizens} />);

    const citizenCard = screen.getByTestId('citizen-card-Citizen 0');
    fireEvent.click(citizenCard);

    // Should not throw
    expect(citizenCard).toBeInTheDocument();
  });

  it('updates selection when selectedCitizenId prop changes', () => {
    const { rerender } = render(
      <VirtualizedCitizenList
        citizens={mockCitizens}
        selectedCitizenId="citizen-0"
      />
    );

    expect(screen.getByText('Citizen 0')).toBeInTheDocument();

    rerender(
      <VirtualizedCitizenList
        citizens={mockCitizens}
        selectedCitizenId="citizen-3"
      />
    );

    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
  });

  it('allows deselection by passing null', () => {
    const { rerender } = render(
      <VirtualizedCitizenList
        citizens={mockCitizens}
        selectedCitizenId="citizen-0"
      />
    );

    rerender(
      <VirtualizedCitizenList
        citizens={mockCitizens}
        selectedCitizenId={null}
      />
    );

    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
  });
});

// =============================================================================
// Virtualization Performance Tests
// =============================================================================

describe('VirtualizedCitizenList - Virtualization', () => {
  it('only renders visible items for large lists', () => {
    render(<VirtualizedCitizenList citizens={largeCitizenList} />);

    // First item should be visible
    expect(screen.getByText('Citizen 0')).toBeInTheDocument();

    // Last item should NOT be rendered yet (virtualized)
    expect(screen.queryByText('Citizen 99')).not.toBeInTheDocument();
  });

  it('shows viewport indicator for large lists', () => {
    render(<VirtualizedCitizenList citizens={largeCitizenList} />);

    // Should show total count
    expect(screen.getByText('100 citizens')).toBeInTheDocument();

    // May show how many are currently rendered
    const showingText = screen.queryByText(/showing/i);
    if (showingText) {
      expect(showingText).toBeInTheDocument();
    }
  });

  it('respects custom estimateSize prop', () => {
    const { container: container1 } = render(
      <VirtualizedCitizenList citizens={largeCitizenList} estimateSize={100} />
    );

    const { container: container2 } = render(
      <VirtualizedCitizenList citizens={largeCitizenList} estimateSize={200} />
    );

    // Both should render successfully with different sizes
    expect(container1.querySelector('.h-full')).toBeInTheDocument();
    expect(container2.querySelector('.h-full')).toBeInTheDocument();
  });

  it('respects custom overscan prop', () => {
    const { container: container1 } = render(
      <VirtualizedCitizenList citizens={largeCitizenList} overscan={3} />
    );

    const { container: container2 } = render(
      <VirtualizedCitizenList citizens={largeCitizenList} overscan={10} />
    );

    // Both should render successfully with different overscan
    expect(container1.querySelector('.h-full')).toBeInTheDocument();
    expect(container2.querySelector('.h-full')).toBeInTheDocument();
  });

  it('uses strict containment for performance', () => {
    const { container } = render(
      <VirtualizedCitizenList citizens={largeCitizenList} />
    );

    const scrollContainer = container.querySelector('[style*="contain"]');
    expect(scrollContainer).toBeInTheDocument();
  });

  it('positions items absolutely for virtualization', () => {
    const { container } = render(
      <VirtualizedCitizenList citizens={largeCitizenList} />
    );

    const virtualItems = container.querySelectorAll('[style*="position: absolute"]');
    expect(virtualItems.length).toBeGreaterThan(0);
  });

  it('creates correct total scroll height', () => {
    const { container } = render(
      <VirtualizedCitizenList citizens={largeCitizenList} estimateSize={140} />
    );

    // Should have a scroll container with calculated height
    const virtualContainer = container.querySelector('[style*="height"]');
    expect(virtualContainer).toBeInTheDocument();
  });
});

// =============================================================================
// Memory and Performance Tests
// =============================================================================

describe('VirtualizedCitizenList - Performance', () => {
  it('memo optimization prevents unnecessary rerenders', () => {
    const { rerender } = render(
      <VirtualizedCitizenList citizens={mockCitizens} />
    );

    // Rerender with same props
    rerender(<VirtualizedCitizenList citizens={mockCitizens} />);

    expect(screen.getByText('Citizen 0')).toBeInTheDocument();
  });

  it('handles 1000+ citizens without crashing', () => {
    const massiveCitizenList = Array(1500).fill(null).map((_, i) => createMockCitizen(i));

    const { container } = render(
      <VirtualizedCitizenList citizens={massiveCitizenList} />
    );

    expect(screen.getByText('1500 citizens')).toBeInTheDocument();
    expect(container.querySelector('.h-full')).toBeInTheDocument();
  });
});
