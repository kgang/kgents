/**
 * Tests for MaskCardEnhanced component.
 *
 * T-gent Type I: Contract tests (required props, defaults)
 * T-gent Type II: Saboteur tests (edge cases, boundary values)
 * T-gent Type III: Spy tests (callback verification)
 *
 * @see impl/claude/web/src/components/park/MaskCardEnhanced.tsx
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MaskCardEnhanced, MaskGridEnhanced } from '@/components/park/MaskCardEnhanced';
import type { ParkMaskInfo, ParkMaskArchetype } from '@/api/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const createMockMask = (overrides?: Partial<ParkMaskInfo>): ParkMaskInfo => ({
  name: 'The Trickster',
  archetype: 'TRICKSTER' as ParkMaskArchetype,
  description: 'Playful chaos agent',
  flavor_text: 'The world is a stage for improvisation',
  intensity: 0.8,
  special_abilities: ['bypass rules', 'creative solutions', 'chaos injection', 'pattern breaking'],
  restrictions: ['must maintain playfulness', 'cannot harm innocent'],
  transform: {
    creativity: 0.3,
    trust: -0.1,
    empathy: 0.0,
    authority: -0.2,
    playfulness: 0.5,
  },
  ...overrides,
});

const defaultProps = {
  mask: createMockMask(),
  isActive: false,
  onSelect: vi.fn(),
};

// =============================================================================
// Type I: Contract Tests
// =============================================================================

describe('MaskCardEnhanced - Contracts', () => {
  it('renders with required props', () => {
    render(<MaskCardEnhanced {...defaultProps} />);

    expect(screen.getByText('The Trickster')).toBeInTheDocument();
    expect(screen.getByText('Playful chaos agent')).toBeInTheDocument();
  });

  it('applies default disabled prop (false)', () => {
    render(<MaskCardEnhanced {...defaultProps} />);

    const button = screen.getByText('Don Mask');
    expect(button).not.toBeDisabled();
  });

  it('applies default showAffordances prop (true)', () => {
    render(<MaskCardEnhanced {...defaultProps} />);

    expect(screen.getByText('bypass rules')).toBeInTheDocument();
  });

  it('applies default showRadar prop (false)', () => {
    render(<MaskCardEnhanced {...defaultProps} />);

    // Radar should not be visible by default
    const { container } = render(<MaskCardEnhanced {...defaultProps} />);
    expect(container.querySelector('svg[viewBox="0 0 80 80"]')).not.toBeInTheDocument();
  });

  it('applies default showDebtCost prop (true)', () => {
    render(<MaskCardEnhanced {...defaultProps} />);

    // Debt cost badge should be visible
    expect(screen.getByText(/\+\d+%/)).toBeInTheDocument();
  });

  it('applies default compact prop (false)', () => {
    render(<MaskCardEnhanced {...defaultProps} />);

    // Full mode shows full description
    expect(screen.getByText('Playful chaos agent')).toBeInTheDocument();
  });
});

// =============================================================================
// Type II: Saboteur Tests (Edge Cases)
// =============================================================================

describe('MaskCardEnhanced - Saboteurs', () => {
  it('handles all mask archetypes', () => {
    const archetypes: ParkMaskArchetype[] = [
      'TRICKSTER',
      'DREAMER',
      'SKEPTIC',
      'ARCHITECT',
      'CHILD',
      'SAGE',
      'WARRIOR',
      'HEALER',
    ];

    archetypes.forEach(archetype => {
      const { unmount } = render(
        <MaskCardEnhanced
          {...defaultProps}
          mask={createMockMask({ archetype, name: `The ${archetype}` })}
        />
      );

      expect(screen.getByText(`The ${archetype}`)).toBeInTheDocument();
      unmount();
    });
  });

  it('shows "Doff Mask" when active', () => {
    render(<MaskCardEnhanced {...defaultProps} isActive={true} />);

    expect(screen.getByText('Doff Mask')).toBeInTheDocument();
  });

  it('shows "Don Mask" when inactive', () => {
    render(<MaskCardEnhanced {...defaultProps} isActive={false} />);

    expect(screen.getByText('Don Mask')).toBeInTheDocument();
  });

  it('displays check icon when active', () => {
    const { container } = render(<MaskCardEnhanced {...defaultProps} isActive={true} />);

    // Check icon should be visible
    const checkIcon = container.querySelector('.text-amber-500');
    expect(checkIcon).toBeInTheDocument();
  });

  it('highlights active mask with amber border', () => {
    const { container } = render(<MaskCardEnhanced {...defaultProps} isActive={true} />);

    const card = container.querySelector('.border-amber-500');
    expect(card).toBeInTheDocument();
  });

  it('shows low debt cost badge for low-cost masks', () => {
    render(
      <MaskCardEnhanced
        {...defaultProps}
        mask={createMockMask({ archetype: 'CHILD' })}
      />
    );

    // CHILD has 3% cost, should show +3%
    expect(screen.getByText('+3%')).toBeInTheDocument();
  });

  it('shows high debt cost badge for high-cost masks', () => {
    render(
      <MaskCardEnhanced
        {...defaultProps}
        mask={createMockMask({ archetype: 'WARRIOR' })}
      />
    );

    // WARRIOR has 10% cost, should show +10%
    expect(screen.getByText('+10%')).toBeInTheDocument();
  });

  it('displays primary affordances (first 3)', () => {
    render(<MaskCardEnhanced {...defaultProps} />);

    expect(screen.getByText('bypass rules')).toBeInTheDocument();
    expect(screen.getByText('creative solutions')).toBeInTheDocument();
    expect(screen.getByText('chaos injection')).toBeInTheDocument();
  });

  it('displays secondary affordances when not compact', () => {
    render(<MaskCardEnhanced {...defaultProps} />);

    expect(screen.getByText('pattern breaking')).toBeInTheDocument();
  });

  it('displays restrictions', () => {
    render(<MaskCardEnhanced {...defaultProps} />);

    expect(screen.getByText('must maintain playfulness')).toBeInTheDocument();
    expect(screen.getByText('cannot harm innocent')).toBeInTheDocument();
  });

  it('handles masks with no restrictions', () => {
    render(
      <MaskCardEnhanced
        {...defaultProps}
        mask={createMockMask({ restrictions: [] })}
      />
    );

    // Should not crash, just not show restriction section
    expect(screen.getByText('The Trickster')).toBeInTheDocument();
  });

  it('handles masks with many affordances', () => {
    const manyAbilities = Array.from({ length: 10 }, (_, i) => `ability-${i}`);

    render(
      <MaskCardEnhanced
        {...defaultProps}
        mask={createMockMask({ special_abilities: manyAbilities })}
      />
    );

    // Should show first 3
    expect(screen.getByText('ability-0')).toBeInTheDocument();
    expect(screen.getByText('ability-1')).toBeInTheDocument();
    expect(screen.getByText('ability-2')).toBeInTheDocument();
  });

  it('expands to show radar when clicked', () => {
    const { container } = render(
      <MaskCardEnhanced
        {...defaultProps}
        showRadar={true}
      />
    );

    // Click header to expand
    const header = container.querySelector('[role="button"]');
    if (header) {
      fireEvent.click(header);
    }

    // Radar SVG should now be visible
    const radar = container.querySelector('svg');
    expect(radar).toBeInTheDocument();
  });

  it('shows eigenvector transform deltas when expanded', () => {
    const { container } = render(<MaskCardEnhanced {...defaultProps} />);

    // Click to expand
    const header = container.querySelector('[role="button"]');
    if (header) {
      fireEvent.click(header);
    }

    // Should show transform deltas
    expect(screen.getByText(/Eigenvector Transform/)).toBeInTheDocument();
  });

  it('shows flavor text when expanded', () => {
    const { container } = render(<MaskCardEnhanced {...defaultProps} />);

    // Click to expand
    const header = container.querySelector('[role="button"]');
    if (header) {
      fireEvent.click(header);
    }

    expect(screen.getByText(/The world is a stage for improvisation/)).toBeInTheDocument();
  });

  it('handles masks without flavor text', () => {
    const { container } = render(
      <MaskCardEnhanced
        {...defaultProps}
        mask={createMockMask({ flavor_text: null })}
      />
    );

    // Click to expand
    const header = container.querySelector('[role="button"]');
    if (header) {
      fireEvent.click(header);
    }

    // Should not crash
    expect(screen.getByText('The Trickster')).toBeInTheDocument();
  });
});

// =============================================================================
// Type III: Spy Tests (Callbacks)
// =============================================================================

describe('MaskCardEnhanced - Spies', () => {
  it('calls onSelect when Don Mask button clicked', () => {
    const onSelect = vi.fn();

    render(
      <MaskCardEnhanced
        {...defaultProps}
        onSelect={onSelect}
      />
    );

    const button = screen.getByText('Don Mask');
    fireEvent.click(button);

    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it('calls onSelect when Doff Mask button clicked', () => {
    const onSelect = vi.fn();

    render(
      <MaskCardEnhanced
        {...defaultProps}
        isActive={true}
        onSelect={onSelect}
      />
    );

    const button = screen.getByText('Doff Mask');
    fireEvent.click(button);

    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it('does not call onSelect when disabled', () => {
    const onSelect = vi.fn();

    render(
      <MaskCardEnhanced
        {...defaultProps}
        disabled={true}
        onSelect={onSelect}
      />
    );

    const button = screen.getByText('Don Mask');
    expect(button).toBeDisabled();

    fireEvent.click(button);
    expect(onSelect).not.toHaveBeenCalled();
  });

  it('stops propagation when clicking action button', () => {
    const onSelect = vi.fn();
    const { container } = render(
      <MaskCardEnhanced
        {...defaultProps}
        onSelect={onSelect}
      />
    );

    const button = screen.getByText('Don Mask');
    fireEvent.click(button);

    // onSelect should be called
    expect(onSelect).toHaveBeenCalledTimes(1);
  });

  it('handles keyboard navigation for expand/collapse', () => {
    const { container } = render(<MaskCardEnhanced {...defaultProps} />);

    const header = container.querySelector('[role="button"]');
    if (header) {
      fireEvent.keyDown(header, { key: 'Enter' });
    }

    // Should expand and show eigenvector section
    expect(screen.getByText(/Eigenvector Transform/)).toBeInTheDocument();
  });

  it('handles Space key for expand/collapse', () => {
    const { container } = render(<MaskCardEnhanced {...defaultProps} />);

    const header = container.querySelector('[role="button"]');
    if (header) {
      fireEvent.keyDown(header, { key: ' ' });
    }

    // Should expand
    expect(screen.getByText(/Eigenvector Transform/)).toBeInTheDocument();
  });
});

// =============================================================================
// Rendering Mode Tests
// =============================================================================

describe('MaskCardEnhanced - Rendering Modes', () => {
  it('renders compact mode with minimal info', () => {
    render(<MaskCardEnhanced {...defaultProps} compact={true} />);

    expect(screen.getByText('The Trickster')).toBeInTheDocument();
    // Should truncate description
    const description = screen.getByText('Playful chaos agent');
    expect(description.className).toContain('truncate');
  });

  it('hides affordances when showAffordances is false', () => {
    render(<MaskCardEnhanced {...defaultProps} showAffordances={false} />);

    expect(screen.queryByText('bypass rules')).not.toBeInTheDocument();
  });

  it('hides debt cost badge when showDebtCost is false', () => {
    render(<MaskCardEnhanced {...defaultProps} showDebtCost={false} />);

    expect(screen.queryByText(/\+\d+%/)).not.toBeInTheDocument();
  });

  it('shows radar when showRadar is true and expanded', () => {
    const { container } = render(
      <MaskCardEnhanced
        {...defaultProps}
        showRadar={true}
      />
    );

    // Expand
    const header = container.querySelector('[role="button"]');
    if (header) {
      fireEvent.click(header);
    }

    // Radar should be visible
    const radar = container.querySelector('svg');
    expect(radar).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <MaskCardEnhanced
        {...defaultProps}
        className="custom-mask-card"
      />
    );

    expect(container.querySelector('.custom-mask-card')).toBeInTheDocument();
  });

  it('shows compact debt badge in compact mode', () => {
    render(<MaskCardEnhanced {...defaultProps} compact={true} />);

    // Should still show debt cost
    expect(screen.getByText(/\+\d+%/)).toBeInTheDocument();
  });
});

// =============================================================================
// MaskGridEnhanced Tests
// =============================================================================

describe('MaskGridEnhanced - Contracts', () => {
  it('renders multiple masks in grid', () => {
    const masks = [
      createMockMask({ name: 'The Trickster', archetype: 'TRICKSTER' }),
      createMockMask({ name: 'The Dreamer', archetype: 'DREAMER' }),
      createMockMask({ name: 'The Warrior', archetype: 'WARRIOR' }),
    ];

    render(
      <MaskGridEnhanced
        masks={masks}
        currentMask={null}
        onDon={vi.fn()}
        onDoff={vi.fn()}
      />
    );

    expect(screen.getByText('The Trickster')).toBeInTheDocument();
    expect(screen.getByText('The Dreamer')).toBeInTheDocument();
    expect(screen.getByText('The Warrior')).toBeInTheDocument();
  });

  it('shows empty state when no masks', () => {
    render(
      <MaskGridEnhanced
        masks={[]}
        currentMask={null}
        onDon={vi.fn()}
        onDoff={vi.fn()}
      />
    );

    expect(screen.getByText('No masks available')).toBeInTheDocument();
  });

  it('highlights current mask', () => {
    const masks = [createMockMask()];

    render(
      <MaskGridEnhanced
        masks={masks}
        currentMask={masks[0]}
        onDon={vi.fn()}
        onDoff={vi.fn()}
      />
    );

    expect(screen.getByText('Doff Mask')).toBeInTheDocument();
  });

  it('calls onDoff when doffing current mask', () => {
    const onDoff = vi.fn();
    const masks = [createMockMask()];

    render(
      <MaskGridEnhanced
        masks={masks}
        currentMask={masks[0]}
        onDon={vi.fn()}
        onDoff={onDoff}
      />
    );

    const doffButton = screen.getByText('Doff Mask');
    fireEvent.click(doffButton);

    expect(onDoff).toHaveBeenCalledTimes(1);
  });

  it('calls onDon when donning new mask', () => {
    const onDon = vi.fn();
    const masks = [createMockMask({ name: 'The Trickster' })];

    render(
      <MaskGridEnhanced
        masks={masks}
        currentMask={null}
        onDon={onDon}
        onDoff={vi.fn()}
      />
    );

    const donButton = screen.getByText('Don Mask');
    fireEvent.click(donButton);

    expect(onDon).toHaveBeenCalledWith('trickster');
  });

  it('normalizes mask name when calling onDon', () => {
    const onDon = vi.fn();
    const masks = [createMockMask({ name: 'The Great Warrior' })];

    render(
      <MaskGridEnhanced
        masks={masks}
        currentMask={null}
        onDon={onDon}
        onDoff={vi.fn()}
      />
    );

    const donButton = screen.getByText('Don Mask');
    fireEvent.click(donButton);

    // Should remove "the " prefix and lowercase
    expect(onDon).toHaveBeenCalledWith('great warrior');
  });

  it('calls onDoff then onDon when switching masks', () => {
    const onDon = vi.fn();
    const onDoff = vi.fn();
    const masks = [
      createMockMask({ name: 'The Trickster', archetype: 'TRICKSTER' }),
      createMockMask({ name: 'The Warrior', archetype: 'WARRIOR' }),
    ];

    render(
      <MaskGridEnhanced
        masks={masks}
        currentMask={masks[0]}
        onDon={onDon}
        onDoff={onDoff}
      />
    );

    // Click on different mask
    const warriorButton = screen.getAllByText('Don Mask')[0];
    fireEvent.click(warriorButton);

    expect(onDoff).toHaveBeenCalled();
    expect(onDon).toHaveBeenCalledWith('warrior');
  });

  it('shows teaching callout when enabled', () => {
    const masks = [createMockMask()];

    render(
      <MaskGridEnhanced
        masks={masks}
        currentMask={null}
        onDon={vi.fn()}
        onDoff={vi.fn()}
        showTeaching={true}
      />
    );

    expect(screen.getByText(/observer/i)).toBeInTheDocument();
  });

  it('applies compact mode to all cards', () => {
    const masks = [createMockMask(), createMockMask({ name: 'The Warrior' })];

    render(
      <MaskGridEnhanced
        masks={masks}
        currentMask={null}
        onDon={vi.fn()}
        onDoff={vi.fn()}
        compact={true}
      />
    );

    // All cards should be compact
    const descriptions = screen.getAllByText(/Playful chaos agent|description/);
    descriptions.forEach(desc => {
      expect(desc.className).toContain('truncate');
    });
  });
});
