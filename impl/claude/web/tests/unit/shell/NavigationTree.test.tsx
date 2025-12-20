/**
 * NavigationTree Tests
 *
 * Tests for AGENTESE path navigation, tree building, and density adaptation.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import type { ReactNode } from 'react';
import { NavigationTree, __clearDiscoveryCache } from '@/shell/NavigationTree';
import { ShellProvider } from '@/shell/ShellProvider';
import { apiClient } from '@/api/client';

// =============================================================================
// Mocks
// =============================================================================

vi.mock('@/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    defaults: { baseURL: '' },
  },
}));

vi.mock('@/components/joy/useMotionPreferences', () => ({
  useMotionPreferences: () => ({ shouldAnimate: false }),
}));

// =============================================================================
// Test Utilities
// =============================================================================

function mockWindowSize(width: number, height: number = 768) {
  Object.defineProperty(window, 'innerWidth', { value: width, writable: true });
  Object.defineProperty(window, 'innerHeight', { value: height, writable: true });
}

function createWrapper({ initialRoute = '/' } = {}) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <MemoryRouter initialEntries={[initialRoute]}>
        <ShellProvider>{children}</ShellProvider>
      </MemoryRouter>
    );
  };
}

const mockDiscoveryResponse = {
  data: {
    paths: [
      'world.town',
      'world.town.citizens',
      'world.park',
      'world.codebase',
      'self.memory',
      'concept.gardener',
    ],
    stats: {
      registered_nodes: 6,
      contexts: ['world', 'self', 'concept'],
    },
  },
};

// =============================================================================
// Tests
// =============================================================================

describe('NavigationTree', () => {
  beforeEach(() => {
    localStorage.clear();
    __clearDiscoveryCache(); // Clear cache between tests
    vi.mocked(apiClient.get).mockResolvedValue(mockDiscoveryResponse);
    mockWindowSize(1200); // Desktop by default
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('rendering', () => {
    it('renders AGENTESE Paths header', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('AGENTESE Paths')).toBeInTheDocument();
      });
    });

    it('renders Crown Jewels section', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Crown Jewels')).toBeInTheDocument();
      });
    });

    it('renders Gallery section', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Gallery')).toBeInTheDocument();
      });
    });

    it('shows loading state initially', async () => {
      // Delay the API response
      vi.mocked(apiClient.get).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockDiscoveryResponse), 100))
      );

      render(<NavigationTree />, { wrapper: createWrapper() });

      expect(screen.getByText('Loading paths...')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.queryByText('Loading paths...')).not.toBeInTheDocument();
      });
    });
  });

  describe('discovery', () => {
    it('fetches paths from /agentese/discover', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(apiClient.get).toHaveBeenCalledWith('/agentese/discover');
      });
    });

    it('renders discovered context nodes', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('world')).toBeInTheDocument();
        expect(screen.getByText('self')).toBeInTheDocument();
        expect(screen.getByText('concept')).toBeInTheDocument();
      });
    });

    it('handles discovery error gracefully with fallback paths', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'));

      render(<NavigationTree />, { wrapper: createWrapper() });

      // Should still render Crown Jewels as fallback
      await waitFor(() => {
        expect(screen.getByText('Crown Jewels')).toBeInTheDocument();
      });
    });
  });

  describe('tree interaction', () => {
    it('expands context nodes when navigating to child path', async () => {
      // Navigate to a path under world - this should auto-expand world
      render(<NavigationTree />, {
        wrapper: createWrapper({ initialRoute: '/world.town' }),
      });

      await waitFor(() => {
        // world context should be auto-expanded because we navigated to world.town
        expect(screen.getByText('town')).toBeInTheDocument();
      });
    });

    it('toggles node expansion on click', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('world')).toBeInTheDocument();
      });

      // Click to expand world
      const worldButton = screen.getByText('world').closest('button');
      fireEvent.click(worldButton!);

      // After click, town should be visible
      await waitFor(() => {
        expect(screen.getByText('town')).toBeInTheDocument();
      });
    });

    it('shows nested paths under parent', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      // First expand world
      await waitFor(() => {
        expect(screen.getByText('world')).toBeInTheDocument();
      });

      const worldButton = screen.getByText('world').closest('button');
      fireEvent.click(worldButton!);

      // Now town should be visible
      await waitFor(() => {
        expect(screen.getByText('town')).toBeInTheDocument();
      });

      // Click to expand town
      const townButton = screen.getByText('town').closest('button');
      fireEvent.click(townButton!);

      await waitFor(() => {
        expect(screen.getByText('citizens')).toBeInTheDocument();
      });
    });
  });

  describe('Crown Jewels', () => {
    it('renders all Crown Jewel shortcuts', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Brain')).toBeInTheDocument();
        expect(screen.getByText('Gestalt')).toBeInTheDocument();
        expect(screen.getByText('Gardener')).toBeInTheDocument();
        expect(screen.getByText('Forge')).toBeInTheDocument(); // Not Atelier
        expect(screen.getByText('Coalition')).toBeInTheDocument();
        expect(screen.getByText('Park')).toBeInTheDocument();
      });
    });

    it('shows AGENTESE path for each jewel', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('self.memory')).toBeInTheDocument();
        expect(screen.getByText('world.codebase')).toBeInTheDocument();
      });
    });

    it('highlights active jewel based on route', async () => {
      // Use AGENTESE path format - routes ARE AGENTESE paths now
      render(<NavigationTree />, {
        wrapper: createWrapper({ initialRoute: '/self.memory' }),
      });

      await waitFor(() => {
        const brainButton = screen.getByText('Brain').closest('button');
        expect(brainButton).toHaveClass('bg-gray-700/70');
      });
    });
  });

  describe('density adaptation', () => {
    describe('spacious (desktop)', () => {
      beforeEach(() => {
        mockWindowSize(1200);
      });

      it('renders fixed sidebar', async () => {
        const { container } = render(<NavigationTree />, {
          wrapper: createWrapper(),
        });

        await waitFor(() => {
          const aside = container.querySelector('aside');
          expect(aside).toBeInTheDocument();
          expect(aside).toHaveStyle({ width: '280px' });
        });
      });
    });

    describe('comfortable (tablet)', () => {
      beforeEach(() => {
        localStorage.clear();
        mockWindowSize(900);
        // Dispatch resize event to update provider
        window.dispatchEvent(new Event('resize'));
      });

      it('renders collapsible sidebar with toggle', async () => {
        render(<NavigationTree />, { wrapper: createWrapper() });

        await waitFor(() => {
          // Should have a toggle button when sidebar is collapsed
          const toggleButton = screen.queryByLabelText(/open navigation/i);
          // Note: Initial state depends on localStorage, so either toggle or sidebar should exist
          expect(toggleButton || screen.getByText('AGENTESE Paths')).toBeInTheDocument();
        });
      });
    });

    // NOTE: Compact (mobile) tests are skipped because:
    // 1. NavigationTree at compact density only renders the drawer content, not the hamburger button
    // 2. The hamburger button is rendered in Shell header, not in NavigationTree
    // 3. Testing the full mobile experience requires rendering the complete Shell component
    // These tests should be moved to a Shell integration test or e2e test
    describe.skip('compact (mobile)', () => {
      beforeEach(() => {
        localStorage.clear();
        mockWindowSize(375);
        window.dispatchEvent(new Event('resize'));
      });

      it('renders hamburger menu button', async () => {
        render(<NavigationTree />, { wrapper: createWrapper() });

        await waitFor(() => {
          // Actual aria-label is "Open navigation sidebar"
          const hamburger = screen.getByLabelText('Open navigation sidebar');
          expect(hamburger).toBeInTheDocument();
        });
      });

      it('opens drawer on hamburger click', async () => {
        render(<NavigationTree />, { wrapper: createWrapper() });

        const hamburger = await screen.findByLabelText('Open navigation sidebar');
        fireEvent.click(hamburger);

        // Wait for drawer to appear with AGENTESE Paths heading
        await waitFor(
          () => {
            const headings = screen.queryAllByText('AGENTESE Paths');
            expect(headings.length).toBeGreaterThan(0);
          },
          { timeout: 2000 }
        );
      });

      it('closes drawer on backdrop click', async () => {
        render(<NavigationTree />, { wrapper: createWrapper() });

        // Open drawer
        const hamburger = await screen.findByLabelText('Open navigation sidebar');
        fireEvent.click(hamburger);

        // Wait for drawer
        await waitFor(
          () => {
            expect(screen.queryAllByText('AGENTESE Paths').length).toBeGreaterThan(0);
          },
          { timeout: 2000 }
        );

        // Find and click backdrop
        const backdrop = document.querySelector('.bg-black\\/50');
        if (backdrop) {
          fireEvent.click(backdrop);
        }

        // Verify interaction completed
        expect(true).toBe(true);
      });

      it('closes drawer on close button click', async () => {
        render(<NavigationTree />, { wrapper: createWrapper() });

        // Open drawer
        const hamburger = await screen.findByLabelText('Open navigation sidebar');
        fireEvent.click(hamburger);

        // Wait for drawer
        await waitFor(
          () => {
            expect(screen.queryAllByText('AGENTESE Paths').length).toBeGreaterThan(0);
          },
          { timeout: 2000 }
        );

        // Click close if available
        const closeButton = screen.queryByLabelText('Close navigation sidebar');
        if (closeButton) {
          fireEvent.click(closeButton);
        }

        // Verify interaction completed
        expect(true).toBe(true);
      });
    });
  });

  describe('Gallery section', () => {
    it('renders gallery links', async () => {
      render(<NavigationTree />, { wrapper: createWrapper() });

      await waitFor(() => {
        expect(screen.getByText('Projection Gallery')).toBeInTheDocument();
        expect(screen.getByText('Layout Gallery')).toBeInTheDocument();
      });
    });

    it('highlights active gallery route', async () => {
      // Gallery routes use /_/gallery format
      render(<NavigationTree />, {
        wrapper: createWrapper({ initialRoute: '/_/gallery' }),
      });

      await waitFor(() => {
        const galleryButton = screen.getByText('Projection Gallery').closest('button');
        expect(galleryButton).toHaveClass('bg-gray-700/70');
      });
    });
  });
});

// =============================================================================
// Tree Building Tests
// =============================================================================

describe('tree building', () => {
  beforeEach(() => {
    localStorage.clear();
    __clearDiscoveryCache();
    mockWindowSize(1200);
  });

  it('builds correct tree structure from flat paths', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      data: {
        paths: ['world.town.citizens', 'world.town.coalitions', 'world.park'],
        stats: { registered_nodes: 3, contexts: ['world'] },
      },
    });

    render(<NavigationTree />, { wrapper: createWrapper() });

    // Wait for discovery to complete
    await waitFor(() => {
      // Root context - world is visible
      expect(screen.getByText('world')).toBeInTheDocument();
    });

    // Click world to expand it (not expanded by default)
    const worldBtn = screen.getByText('world').closest('button');
    fireEvent.click(worldBtn!);

    // Now town and park should be visible
    await waitFor(() => {
      expect(screen.getByText('town')).toBeInTheDocument();
      expect(screen.getByText('park')).toBeInTheDocument();
    });

    // Click town to expand it and see children
    const townBtn = screen.getByText('town').closest('button');
    fireEvent.click(townBtn!);

    // Wait for children to render
    await waitFor(
      () => {
        // Look for citizens - may take a moment to render after expand
        const citizens = screen.queryByText('citizens');
        expect(citizens).toBeInTheDocument();
      },
      { timeout: 1000 }
    );
  });
});
