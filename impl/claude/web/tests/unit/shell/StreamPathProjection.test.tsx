/**
 * StreamPathProjection Tests
 *
 * Tests for the SSE-based projection wrapper including:
 * - Loading states
 * - Error states
 * - Successful rendering
 * - Context propagation
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import type { ReactNode } from 'react';
import { ShellProvider } from '@/shell/ShellProvider';
import { StreamPathProjection, type LoaderResult, type StreamResult, type StreamProjectionContext } from '@/shell/StreamPathProjection';
import type { ColonyDashboardJSON } from '@/reactive/types';
import type { TownEvent } from '@/api/types';

// =============================================================================
// Test Utilities
// =============================================================================

// Mock window dimensions
function mockWindowSize(width: number, height: number = 768) {
  Object.defineProperty(window, 'innerWidth', { value: width, writable: true });
  Object.defineProperty(window, 'innerHeight', { value: height, writable: true });
}

function createWrapper() {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <ShellProvider>{children}</ShellProvider>;
  };
}

// Mock loader result
function createLoaderResult(overrides: Partial<LoaderResult> = {}): LoaderResult {
  return {
    townId: 'test-town-123',
    loading: false,
    error: null,
    ...overrides,
  };
}

// Mock stream result
function createStreamResult(overrides: Partial<StreamResult> = {}): StreamResult {
  return {
    dashboard: null,
    events: [],
    isConnected: false,
    isPlaying: false,
    connect: vi.fn(),
    disconnect: vi.fn(),
    ...overrides,
  };
}

// Mock dashboard
function createMockDashboard(): ColonyDashboardJSON {
  return {
    type: 'colony_dashboard',
    colony_id: 'test-town-123',
    phase: 'MORNING',
    day: 1,
    metrics: {
      total_events: 0,
      total_tokens: 0,
      entropy_budget: 1.0,
    },
    citizens: [],
    grid_cols: 3,
    selected_citizen_id: null,
  };
}

// Mock useWindowLayout
vi.mock('../hooks', () => ({
  useWindowLayout: () => ({
    width: 1200,
    height: 768,
    density: 'spacious',
    isMobile: false,
    isTablet: false,
    isDesktop: true,
  }),
}));

// =============================================================================
// Loading State Tests
// =============================================================================

describe('StreamPathProjection loading states', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200);
  });

  it('shows loading indicator when loader.loading is true', () => {
    const loader = createLoaderResult({ loading: true, townId: null });
    const stream = createStreamResult();

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
      >
        {() => <div data-testid="content">Content</div>}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    // Should not show content
    expect(screen.queryByTestId('content')).not.toBeInTheDocument();
    // Should show loading (PersonalityLoading component)
    // Note: PersonalityLoading renders with specific structure
  });

  it('shows loading indicator when townId is null', () => {
    const loader = createLoaderResult({ townId: null, loading: false });
    const stream = createStreamResult();

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
      >
        {() => <div data-testid="content">Content</div>}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    // Should not show content
    expect(screen.queryByTestId('content')).not.toBeInTheDocument();
  });
});

// =============================================================================
// Error State Tests
// =============================================================================

describe('StreamPathProjection error states', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200);
  });

  it('shows error UI when loader.error is set', () => {
    // Note: The component checks loading first, so we need townId to be set
    // OR loading to be false to hit the error branch
    const loader = createLoaderResult({ error: 'Town not found', townId: 'test', loading: false });
    const stream = createStreamResult();

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
      >
        {() => <div data-testid="content">Content</div>}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    // Should show error message
    expect(screen.getByText('Town not found')).toBeInTheDocument();
    // Should show default action
    expect(screen.getByText('Go Back')).toBeInTheDocument();
  });

  it('uses custom notFoundAction label', () => {
    const loader = createLoaderResult({ error: 'Not found', townId: 'test', loading: false });
    const stream = createStreamResult();

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
        notFoundAction="Create New Town"
      >
        {() => <div>Content</div>}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    expect(screen.getByText('Create New Town')).toBeInTheDocument();
  });

  it('calls onNotFoundAction when action button clicked', async () => {
    const loader = createLoaderResult({ error: 'Not found', townId: 'test', loading: false });
    const stream = createStreamResult();
    const onAction = vi.fn();

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
        notFoundAction="Try Again"
        onNotFoundAction={onAction}
      >
        {() => <div>Content</div>}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    const button = screen.getByText('Try Again');
    button.click();

    expect(onAction).toHaveBeenCalledTimes(1);
  });
});

// =============================================================================
// Successful Rendering Tests
// =============================================================================

describe('StreamPathProjection rendering', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200);
  });

  it('renders children when loader succeeds', () => {
    const loader = createLoaderResult();
    const stream = createStreamResult();

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
      >
        {() => <div data-testid="content">Town Content</div>}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    expect(screen.getByTestId('content')).toBeInTheDocument();
    expect(screen.getByText('Town Content')).toBeInTheDocument();
  });

  it('passes stream result to children', () => {
    const loader = createLoaderResult();
    const dashboard = createMockDashboard();
    const events: TownEvent[] = [{
      tick: 1,
      phase: 'MORNING',
      operation: 'test',
      participants: [],
      success: true,
      message: 'Test event',
      tokens_used: 0,
      timestamp: new Date().toISOString(),
    }];
    const stream = createStreamResult({
      dashboard,
      events,
      isConnected: true,
      isPlaying: true,
    });

    let receivedStream: StreamResult | null = null;

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
      >
        {(s) => {
          receivedStream = s;
          return <div>Content</div>;
        }}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    expect(receivedStream).not.toBeNull();
    expect(receivedStream!.dashboard).toBe(dashboard);
    expect(receivedStream!.events).toBe(events);
    expect(receivedStream!.isConnected).toBe(true);
    expect(receivedStream!.isPlaying).toBe(true);
  });

  it('passes context to children', () => {
    const loader = createLoaderResult({ townId: 'my-town-id' });
    const stream = createStreamResult();

    let receivedContext: StreamProjectionContext | null = null;

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
      >
        {(_, ctx) => {
          receivedContext = ctx;
          return <div>Content</div>;
        }}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    expect(receivedContext).not.toBeNull();
    expect(receivedContext!.entityId).toBe('my-town-id');
    expect(receivedContext!.density).toBe('spacious');
    expect(receivedContext!.isDesktop).toBe(true);
    expect(receivedContext!.isMobile).toBe(false);
    expect(receivedContext!.isTablet).toBe(false);
  });

  it('applies className to container', () => {
    const loader = createLoaderResult();
    const stream = createStreamResult();

    const { container } = render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
        className="custom-class"
      >
        {() => <div>Content</div>}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('custom-class');
  });

  it('applies style to container', () => {
    const loader = createLoaderResult();
    const stream = createStreamResult();

    const { container } = render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
        style={{ backgroundColor: 'red' }}
      >
        {() => <div>Content</div>}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.style.backgroundColor).toBe('red');
  });
});

// =============================================================================
// Density Adaptation Tests
// =============================================================================

describe('StreamPathProjection density', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('provides density from shell context', () => {
    mockWindowSize(375); // Mobile
    const loader = createLoaderResult();
    const stream = createStreamResult();

    let receivedContext: StreamProjectionContext | null = null;

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
      >
        {(_, ctx) => {
          receivedContext = ctx;
          return <div>Content</div>;
        }}
      </StreamPathProjection>,
      { wrapper: createWrapper() }
    );

    expect(receivedContext).not.toBeNull();
    expect(receivedContext!.density).toBe('compact');
    expect(receivedContext!.isMobile).toBe(true);
  });

  it('works without shell provider (fallback to window layout)', () => {
    mockWindowSize(1200); // Desktop
    const loader = createLoaderResult();
    const stream = createStreamResult();

    let receivedContext: StreamProjectionContext | null = null;

    render(
      <StreamPathProjection
        jewel="coalition"
        loader={loader}
        stream={stream}
      >
        {(_, ctx) => {
          receivedContext = ctx;
          return <div>Content</div>;
        }}
      </StreamPathProjection>
    );

    // Should still work using useWindowLayout fallback
    expect(receivedContext).not.toBeNull();
    expect(receivedContext!.density).toBeDefined();
  });
});

// =============================================================================
// Crown Jewel Tests
// =============================================================================

describe('StreamPathProjection crown jewel', () => {
  beforeEach(() => {
    localStorage.clear();
    mockWindowSize(1200);
  });

  it('accepts all valid crown jewel types', () => {
    const loader = createLoaderResult();
    const stream = createStreamResult();

    const jewels: Array<'brain' | 'gestalt' | 'gardener' | 'atelier' | 'coalition' | 'park' | 'domain'> = [
      'brain',
      'gestalt',
      'gardener',
      'atelier',
      'coalition',
      'park',
      'domain',
    ];

    for (const jewel of jewels) {
      const { unmount } = render(
        <StreamPathProjection
          jewel={jewel}
          loader={loader}
          stream={stream}
        >
          {() => <div>{jewel}</div>}
        </StreamPathProjection>,
        { wrapper: createWrapper() }
      );

      expect(screen.getByText(jewel)).toBeInTheDocument();
      unmount();
    }
  });
});
