/**
 * Shell Integration Tests
 *
 * Tests for the unified Shell layout component including:
 * - Error boundary integration
 * - Overall layout composition
 * - Density-responsive behavior
 * - Component integration
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { Shell } from '@/shell/Shell';

// =============================================================================
// Test Utilities
// =============================================================================

// Mock window dimensions
function mockWindowSize(width: number, height: number = 768) {
  Object.defineProperty(window, 'innerWidth', { value: width, writable: true });
  Object.defineProperty(window, 'innerHeight', { value: height, writable: true });
}

// Test content component
function TestContent({ text = 'Test Content' }: { text?: string }) {
  return <div data-testid="test-content">{text}</div>;
}

// Error-throwing component for testing error boundaries
function ThrowingComponent({ shouldThrow = true }: { shouldThrow?: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error from ThrowingComponent');
  }
  return <div>No error</div>;
}

// Render shell with router
function renderShell(initialRoute = '/') {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Routes>
        <Route path="/" element={<Shell />}>
          <Route index element={<TestContent />} />
          <Route path="brain" element={<TestContent text="Brain Page" />} />
          <Route path="error" element={<ThrowingComponent />} />
          <Route path="ok" element={<ThrowingComponent shouldThrow={false} />} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
}

// Mock the API client
vi.mock('@/api/client', () => ({
  apiClient: {
    post: vi.fn().mockResolvedValue({
      data: { path: 'test.path', result: { test: 'data' } },
    }),
    get: vi.fn().mockResolvedValue({
      data: {
        paths: [
          { path: 'self.memory', context: 'self', aspects: ['manifest'] },
          { path: 'world.town', context: 'world', aspects: ['manifest', 'step'] },
        ],
      },
    }),
  },
  AgenteseError: class AgenteseError extends Error {
    constructor(message: string) {
      super(message);
      this.name = 'AgenteseError';
    }
  },
}));

// Mock nanoid for predictable IDs
vi.mock('nanoid', () => ({
  nanoid: vi.fn((length = 21) => 'test-id-' + Math.random().toString(36).slice(2, 2 + length)),
}));

// Mock framer-motion
vi.mock('framer-motion', async () => {
  const actual = await vi.importActual<typeof import('framer-motion')>('framer-motion');
  return {
    ...actual,
    AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    motion: {
      div: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => (
        <div {...props}>{children}</div>
      ),
      p: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => (
        <p {...props}>{children}</p>
      ),
      nav: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => (
        <nav {...props}>{children}</nav>
      ),
      aside: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => (
        <aside {...props}>{children}</aside>
      ),
    },
  };
});

// Mock useMotionPreferences
vi.mock('@/components/joy/useMotionPreferences', () => ({
  useMotionPreferences: () => ({ shouldAnimate: false }),
}));

// =============================================================================
// Layout Tests
// =============================================================================

describe('Shell layout', () => {
  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    mockWindowSize(1200); // Desktop by default
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders main layout structure', async () => {
    renderShell();

    // Should render the shell structure
    await waitFor(() => {
      expect(screen.getByRole('main')).toBeInTheDocument();
    });
  });

  it('renders child content via Outlet', async () => {
    renderShell();

    await waitFor(() => {
      expect(screen.getByTestId('test-content')).toBeInTheDocument();
      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });
  });

  it('renders navigation components', async () => {
    renderShell();

    // Should have navigation (Crown Jewels in nav tree)
    await waitFor(() => {
      // Look for Crown Jewels header in navigation sidebar
      expect(screen.getByText('Crown Jewels')).toBeInTheDocument();
    });

    // Check for jewel links (Brain, etc)
    expect(screen.getByText('Brain')).toBeInTheDocument();
  });

  it('renders terminal component', async () => {
    renderShell();

    await waitFor(() => {
      // Terminal should be present (look for AGENTESE Terminal text or terminal icon)
      expect(screen.getByText('AGENTESE Terminal')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// Density Adaptation Tests
// =============================================================================

describe('Shell density adaptation', () => {
  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders spacious layout on desktop (>1024px)', async () => {
    mockWindowSize(1200);
    renderShell();

    // Should render full layout without header (spacious has no header)
    await waitFor(() => {
      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    // Check for spacious-specific elements (sidebar should be visible)
    expect(screen.getByText('Crown Jewels')).toBeInTheDocument();
  });

  it('renders comfortable layout on tablet (768-1024px)', async () => {
    mockWindowSize(900);
    renderShell();

    await waitFor(() => {
      // Should show header with kgents branding (comfortable/compact shows header)
      expect(screen.getByText('kgents')).toBeInTheDocument();
    });
  });

  it('renders compact layout on mobile (<768px)', async () => {
    mockWindowSize(375);
    renderShell();

    await waitFor(() => {
      // Should show header with kgents branding
      expect(screen.getByText('kgents')).toBeInTheDocument();
    });

    // Mobile should have hamburger menu (NavigationTree uses "Open navigation")
    expect(screen.getByLabelText('Open navigation')).toBeInTheDocument();
  });
});

// =============================================================================
// Error Boundary Tests
// =============================================================================

describe('Shell error boundaries', () => {
  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    mockWindowSize(1200);
    // Suppress console.error for error boundary tests
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.restoreAllMocks();
  });

  it('catches errors in content area and shows error UI', async () => {
    renderShell('/error');

    await waitFor(() => {
      // Should show error boundary UI for projection layer
      expect(screen.getByText(/Content Projection Error/i)).toBeInTheDocument();
    });
  });

  it('shows retry button when error occurs', async () => {
    renderShell('/error');

    await waitFor(() => {
      expect(screen.getByText(/Retry/)).toBeInTheDocument();
    });
  });

  it('navigation tree remains functional when content errors', async () => {
    renderShell('/error');

    // Error in content should not break navigation
    await waitFor(() => {
      expect(screen.getByText('Crown Jewels')).toBeInTheDocument();
    });
  });

  it('terminal remains functional when content errors', async () => {
    renderShell('/error');

    // Error in content should not break terminal
    await waitFor(() => {
      expect(screen.getByText('AGENTESE Terminal')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// Component Integration Tests
// =============================================================================

describe('Shell component integration', () => {
  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    mockWindowSize(1200);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('observer drawer and navigation share shell context', async () => {
    renderShell();

    await waitFor(() => {
      // Both should render with shared context
      expect(screen.getByText('Developer')).toBeInTheDocument(); // Observer drawer
      expect(screen.getByText('Crown Jewels')).toBeInTheDocument(); // Navigation
    });
  });

  it('terminal receives observer context', async () => {
    renderShell();

    await waitFor(() => {
      // Terminal should be present and functional
      const input = screen.getByPlaceholderText('Enter command...');
      expect(input).toBeInTheDocument();
    });
  });

  it('renders correct route content', async () => {
    renderShell('/brain');

    await waitFor(() => {
      expect(screen.getByText('Brain Page')).toBeInTheDocument();
    });
  });
});

// =============================================================================
// Accessibility Tests
// =============================================================================

describe('Shell accessibility', () => {
  beforeEach(() => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    vi.mocked(localStorage.setItem).mockClear();
    mockWindowSize(1200);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('has a main landmark', async () => {
    renderShell();

    await waitFor(() => {
      expect(screen.getByRole('main')).toBeInTheDocument();
    });
  });

  it('has navigation content', async () => {
    renderShell();

    // The navigation tree renders Crown Jewels navigation
    await waitFor(() => {
      expect(screen.getByText('Crown Jewels')).toBeInTheDocument();
    });

    // Check navigation items are present
    expect(screen.getByText('Brain')).toBeInTheDocument();
    expect(screen.getByText('Gardener')).toBeInTheDocument();
  });
});
