import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LODGate } from '@/components/paywall/LODGate';
import { useUserStore } from '@/stores/userStore';
import { useUIStore } from '@/stores/uiStore';

// Mock the stores
vi.mock('@/stores/userStore', async () => {
  const actual = await vi.importActual('@/stores/userStore');
  return {
    ...actual,
    useUserStore: vi.fn(),
  };
});

vi.mock('@/stores/uiStore', async () => {
  const actual = await vi.importActual('@/stores/uiStore');
  return {
    ...actual,
    useUIStore: vi.fn(),
  };
});

describe('LODGate', () => {
  const mockSpendCredits = vi.fn();
  const mockRecordAction = vi.fn();
  const mockOpenModal = vi.fn();
  const mockOnUnlock = vi.fn();

  const defaultUserState = {
    credits: 100,
    tier: 'TOURIST',
    spendCredits: mockSpendCredits,
    recordAction: mockRecordAction,
  };

  const defaultUIState = {
    openModal: mockOpenModal,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockSpendCredits.mockReturnValue(true);

    (useUserStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: typeof defaultUserState) => unknown) => {
      if (typeof selector === 'function') {
        return selector(defaultUserState);
      }
      return defaultUserState;
    });

    (useUIStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue(defaultUIState);
  });

  it('should render children when LOD is included in tier', () => {
    // LOD 0 and 1 are always included for TOURIST
    (useUserStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: typeof defaultUserState) => unknown) => {
      if (typeof selector === 'function') {
        // selectIsLODIncluded returns true for LOD 0-1 for TOURIST
        return true;
      }
      return defaultUserState;
    });

    render(
      <LODGate level={1}>
        <div data-testid="content">Protected Content</div>
      </LODGate>
    );

    expect(screen.getByTestId('content')).toBeInTheDocument();
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should show unlock button when LOD is not included', () => {
    (useUserStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: typeof defaultUserState) => unknown) => {
      if (typeof selector === 'function') {
        // LOD 3 is not included for TOURIST
        return false;
      }
      return { ...defaultUserState, credits: 100 };
    });

    render(
      <LODGate level={3}>
        <div data-testid="content">Protected Content</div>
      </LODGate>
    );

    // Should show unlock button with cost
    expect(screen.getByText(/Unlock/)).toBeInTheDocument();
    expect(screen.getByText('LOD 3')).toBeInTheDocument();
  });

  it('should unlock content when user has enough credits', () => {
    (useUserStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: typeof defaultUserState) => unknown) => {
      if (typeof selector === 'function') {
        return false;
      }
      return { ...defaultUserState, credits: 100 };
    });

    render(
      <LODGate level={3} onUnlock={mockOnUnlock}>
        <div data-testid="content">Protected Content</div>
      </LODGate>
    );

    // Click unlock button
    const unlockButton = screen.getByRole('button', { name: /Unlock/ });
    fireEvent.click(unlockButton);

    expect(mockSpendCredits).toHaveBeenCalled();
    expect(mockRecordAction).toHaveBeenCalledWith('lod3');
  });

  it('should open upgrade modal when user cannot afford', () => {
    (useUserStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: typeof defaultUserState) => unknown) => {
      if (typeof selector === 'function') {
        return false;
      }
      return { ...defaultUserState, credits: 5 }; // Not enough credits
    });

    render(
      <LODGate level={3}>
        <div data-testid="content">Protected Content</div>
      </LODGate>
    );

    // Should show "Get Credits" instead of "Unlock"
    const button = screen.getByRole('button', { name: /Get Credits/ });
    fireEvent.click(button);

    expect(mockOpenModal).toHaveBeenCalledWith('upgrade', expect.objectContaining({
      requiredCredits: expect.any(Number),
      currentCredits: 5,
    }));
  });

  it('should show correct LOD descriptions', () => {
    (useUserStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: typeof defaultUserState) => unknown) => {
      if (typeof selector === 'function') {
        return false;
      }
      return { ...defaultUserState, credits: 100 };
    });

    // Test LOD 3
    const { rerender } = render(
      <LODGate level={3}>
        <div>Content</div>
      </LODGate>
    );
    expect(screen.getByText(/Memory/)).toBeInTheDocument();

    // Test LOD 4
    rerender(
      <LODGate level={4}>
        <div>Content</div>
      </LODGate>
    );
    expect(screen.getByText(/Psyche/)).toBeInTheDocument();

    // Test LOD 5
    rerender(
      <LODGate level={5}>
        <div>Content</div>
      </LODGate>
    );
    expect(screen.getByText(/Abyss/)).toBeInTheDocument();
  });

  it('should render content immediately for LOD 0 (always free)', () => {
    (useUserStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector?: (state: typeof defaultUserState) => unknown) => {
      if (typeof selector === 'function') {
        return true;
      }
      return defaultUserState;
    });

    render(
      <LODGate level={0}>
        <div data-testid="content">Free Content</div>
      </LODGate>
    );

    expect(screen.getByTestId('content')).toBeInTheDocument();
  });
});
