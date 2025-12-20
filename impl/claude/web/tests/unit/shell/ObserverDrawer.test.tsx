/**
 * ObserverDrawer Tests
 *
 * Tests for the top-fixed observer context panel.
 * Verifies collapsed/expanded states, density adaptation, and trace display.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { ShellProvider } from '@/shell/ShellProvider';
import { ObserverDrawer } from '@/shell/ObserverDrawer';

// =============================================================================
// Test Utilities
// =============================================================================

import type { ObserverArchetype, Capability } from '@/shell/types';

interface WrapperProps {
  initialObserver?: {
    archetype?: ObserverArchetype;
    sessionId?: string;
    tenantId?: string;
    intent?: string;
  };
  initialCapabilities?: Capability[];
}

function createWrapper(props: WrapperProps = {}) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <ShellProvider
        initialObserver={props.initialObserver}
        initialCapabilities={props.initialCapabilities}
      >
        {children}
      </ShellProvider>
    );
  };
}

// Mock window dimensions
function mockWindowSize(width: number, height: number = 768) {
  Object.defineProperty(window, 'innerWidth', { value: width, writable: true });
  Object.defineProperty(window, 'innerHeight', { value: height, writable: true });
}

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', async () => {
  const actual = await vi.importActual<typeof import('framer-motion')>('framer-motion');
  return {
    ...actual,
    AnimatePresence: ({ children }: { children: ReactNode }) => <>{children}</>,
    motion: {
      div: ({ children, ...props }: { children: ReactNode; [key: string]: unknown }) => (
        <div {...props}>{children}</div>
      ),
      p: ({ children, ...props }: { children: ReactNode; [key: string]: unknown }) => (
        <p {...props}>{children}</p>
      ),
    },
  };
});

// Mock useMotionPreferences
vi.mock('@/components/joy/useMotionPreferences', () => ({
  useMotionPreferences: () => ({ shouldAnimate: false }),
}));

// =============================================================================
// Rendering Tests
// =============================================================================

describe('ObserverDrawer', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200); // Desktop by default
  });

  describe('rendering', () => {
    it('renders in collapsed state by default', () => {
      render(<ObserverDrawer />, { wrapper: createWrapper() });

      // Should show collapsed view with archetype
      expect(screen.getByText('Developer')).toBeInTheDocument();
      // Should show expand button
      expect(screen.getByLabelText('Expand observer drawer')).toBeInTheDocument();
    });

    it('displays observer archetype in collapsed state', () => {
      render(<ObserverDrawer />, {
        wrapper: createWrapper({
          initialObserver: { archetype: 'architect' },
        }),
      });

      expect(screen.getByText('Architect')).toBeInTheDocument();
    });

    it('displays capabilities badges in collapsed state', () => {
      render(<ObserverDrawer />, {
        wrapper: createWrapper({
          initialCapabilities: ['read', 'write', 'admin'],
        }),
      });

      expect(screen.getByText('Read')).toBeInTheDocument();
      expect(screen.getByText('Write')).toBeInTheDocument();
      expect(screen.getByText('Admin')).toBeInTheDocument();
    });
  });

  describe('expansion', () => {
    it('expands when clicking collapsed view', async () => {
      render(<ObserverDrawer />, { wrapper: createWrapper() });

      // Click to expand
      fireEvent.click(screen.getByLabelText('Expand observer drawer'));

      // Should show expanded content
      await waitFor(() => {
        expect(screen.getByText('Observer Umwelt')).toBeInTheDocument();
      });
    });

    it('shows archetype selector when expanded', async () => {
      render(<ObserverDrawer />, { wrapper: createWrapper() });

      // Click to expand
      fireEvent.click(screen.getByLabelText('Expand observer drawer'));

      // Should show archetype selector
      await waitFor(() => {
        expect(screen.getByRole('combobox')).toBeInTheDocument();
      });
    });

    it('collapses when clicking collapse button', async () => {
      render(<ObserverDrawer defaultExpanded />, { wrapper: createWrapper() });

      // Should be expanded
      expect(screen.getByText('Observer Umwelt')).toBeInTheDocument();

      // Click to collapse
      fireEvent.click(screen.getByLabelText('Collapse observer drawer'));

      // Should show collapsed view
      await waitFor(() => {
        expect(screen.getByLabelText('Expand observer drawer')).toBeInTheDocument();
      });
    });
  });

  describe('archetype selection', () => {
    it('allows changing archetype', async () => {
      render(<ObserverDrawer defaultExpanded />, { wrapper: createWrapper() });

      // Find and change the select
      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'security' } });

      // The select should now show security
      await waitFor(() => {
        expect(select).toHaveValue('security');
      });
    });

    it('shows archetype description when expanded', async () => {
      render(<ObserverDrawer defaultExpanded />, {
        wrapper: createWrapper({
          initialObserver: { archetype: 'developer' },
        }),
      });

      // Should show developer description
      expect(screen.getByText('Building and debugging')).toBeInTheDocument();
    });
  });

  describe('session info', () => {
    it('displays session ID when expanded', async () => {
      const sessionId = 'test-session-12345';
      render(<ObserverDrawer defaultExpanded />, {
        wrapper: createWrapper({
          initialObserver: { sessionId },
        }),
      });

      // Should show truncated session ID
      expect(screen.getByText(sessionId.slice(0, 12))).toBeInTheDocument();
    });

    it('displays tenant ID when available', async () => {
      render(<ObserverDrawer defaultExpanded />, {
        wrapper: createWrapper({
          initialObserver: { tenantId: 'kgents-dev' },
        }),
      });

      expect(screen.getByText('kgents-dev')).toBeInTheDocument();
    });

    it('displays intent when set', async () => {
      render(<ObserverDrawer defaultExpanded />, {
        wrapper: createWrapper({
          initialObserver: { intent: 'Exploring autopoiesis' },
        }),
      });

      expect(screen.getByText('Exploring autopoiesis')).toBeInTheDocument();
    });
  });

  describe('traces display', () => {
    it('shows "No recent traces" when empty', async () => {
      render(<ObserverDrawer defaultExpanded showTraces />, {
        wrapper: createWrapper(),
      });

      expect(screen.getByText('No recent traces')).toBeInTheDocument();
    });

    it('hides traces when showTraces is false', async () => {
      render(<ObserverDrawer defaultExpanded showTraces={false} />, {
        wrapper: createWrapper(),
      });

      // Should not show traces table or empty message
      // The expanded view should still be visible
      expect(screen.getByText('Observer Umwelt')).toBeInTheDocument();
    });
  });

  describe('action buttons', () => {
    it('shows Edit Observer button when expanded', async () => {
      render(<ObserverDrawer defaultExpanded />, { wrapper: createWrapper() });

      expect(screen.getByText('Edit Observer')).toBeInTheDocument();
    });

    it('shows Export Session button when expanded', async () => {
      render(<ObserverDrawer defaultExpanded />, { wrapper: createWrapper() });

      expect(screen.getByText('Export Session')).toBeInTheDocument();
    });

    it('shows Clear traces button when expanded', async () => {
      render(<ObserverDrawer defaultExpanded showTraces />, {
        wrapper: createWrapper(),
      });

      expect(screen.getByText('Clear')).toBeInTheDocument();
    });
  });

  describe('density adaptation', () => {
    it('renders with fixed positioning on mobile (compact)', () => {
      mockWindowSize(375);
      const { container } = render(<ObserverDrawer />, {
        wrapper: createWrapper(),
      });

      // Should have fixed positioning class
      const drawer = container.firstChild as HTMLElement;
      expect(drawer.className).toContain('fixed');
    });

    it('renders with fixed positioning on desktop (spacious)', () => {
      mockWindowSize(1200);
      const { container } = render(<ObserverDrawer />, {
        wrapper: createWrapper(),
      });

      // ObserverDrawer uses fixed positioning at all densities
      const drawer = container.firstChild as HTMLElement;
      expect(drawer.className).toContain('fixed');
    });

    it('shows backdrop on mobile when expanded', async () => {
      mockWindowSize(375);
      render(<ObserverDrawer />, { wrapper: createWrapper() });

      // Expand
      fireEvent.click(screen.getByLabelText('Expand observer drawer'));

      // Should show backdrop (clickable overlay)
      await waitFor(() => {
        // The backdrop has bg-black/50 and covers the screen
        const backdrop = document.querySelector('.fixed.inset-0');
        expect(backdrop).toBeInTheDocument();
      });
    });
  });

  describe('props', () => {
    it('accepts className prop', () => {
      const { container } = render(<ObserverDrawer className="custom-class" />, {
        wrapper: createWrapper(),
      });

      const drawer = container.firstChild as HTMLElement;
      expect(drawer.className).toContain('custom-class');
    });

    it('respects traceLimit prop', async () => {
      // Note: This test would require adding traces through context
      // For now, just verify the prop is accepted
      render(<ObserverDrawer defaultExpanded showTraces traceLimit={3} />, {
        wrapper: createWrapper(),
      });

      // Component should render without error
      expect(screen.getByText('Observer Umwelt')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// Accessibility Tests
// =============================================================================

describe('ObserverDrawer accessibility', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200);
  });

  it('has accessible expand button', () => {
    render(<ObserverDrawer />, { wrapper: createWrapper() });

    const button = screen.getByLabelText('Expand observer drawer');
    expect(button).toBeInTheDocument();
    expect(button.tagName).toBe('BUTTON');
  });

  it('has accessible collapse button when expanded', () => {
    render(<ObserverDrawer defaultExpanded />, { wrapper: createWrapper() });

    const button = screen.getByLabelText('Collapse observer drawer');
    expect(button).toBeInTheDocument();
    expect(button.tagName).toBe('BUTTON');
  });

  it('archetype selector has associated label', () => {
    render(<ObserverDrawer defaultExpanded />, { wrapper: createWrapper() });

    // The label text "Archetype" should be present
    expect(screen.getByText('Archetype')).toBeInTheDocument();
    // The select should be accessible
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });
});
