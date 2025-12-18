/**
 * PathProjection Tests
 *
 * Tests for the AGENTESE path-to-projection wrapper component.
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 */

import { describe, it, expect, vi, beforeEach, afterEach, type Mock } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactNode } from 'react';
import { ShellProvider } from '@/shell/ShellProvider';
import {
  PathProjection,
  LivePathProjection,
  LazyPathProjection,
} from '@/shell/PathProjection';
import { apiClient } from '@/api/client';

// =============================================================================
// Mocks
// =============================================================================

// Mock the API client
vi.mock('@/api/client', async (importOriginal) => {
  const original = await importOriginal<typeof import('@/api/client')>();
  return {
    ...original,
    apiClient: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

// Mock PersonalityLoading to avoid dependency chain
vi.mock('@/components/joy/PersonalityLoading', () => ({
  PersonalityLoading: ({ jewel, action }: { jewel: string; action?: string }) => (
    <div data-testid="personality-loading" data-jewel={jewel} data-action={action}>
      Loading...
    </div>
  ),
}));

// Mock EmpathyError to avoid dependency chain
vi.mock('@/components/joy/EmpathyError', () => ({
  EmpathyError: ({
    type,
    details,
    action,
    onAction,
  }: {
    type: string;
    details?: string;
    action?: string;
    onAction?: () => void;
  }) => (
    <div data-testid="empathy-error" data-type={type}>
      <span data-testid="error-details">{details}</span>
      {onAction && (
        <button data-testid="retry-button" onClick={onAction}>
          {action}
        </button>
      )}
    </div>
  ),
}));

// =============================================================================
// Test Utilities
// =============================================================================

function Wrapper({ children }: { children: ReactNode }) {
  return <ShellProvider>{children}</ShellProvider>;
}

function mockWindowSize(width: number) {
  Object.defineProperty(window, 'innerWidth', { value: width, writable: true });
  Object.defineProperty(window, 'innerHeight', { value: 768, writable: true });
}

/**
 * Create a successful AGENTESE response
 */
function mockSuccessResponse<T>(data: T) {
  return {
    data: {
      path: 'test.path',
      aspect: 'manifest',
      result: data,
    },
  };
}

/**
 * Create an AGENTESE error response
 */
function mockErrorResponse(error: string) {
  return {
    data: {
      path: 'test.path',
      aspect: 'manifest',
      result: null,
      error,
    },
  };
}

// =============================================================================
// Basic Rendering Tests
// =============================================================================

describe('PathProjection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWindowSize(1200);
    localStorage.clear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders loading state initially', async () => {
    // Mock a slow response
    (apiClient.get as Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockSuccessResponse({ test: 'data' })), 100))
    );

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="manifest">
          {(data) => <div data-testid="content">{JSON.stringify(data)}</div>}
        </PathProjection>
      </Wrapper>
    );

    expect(screen.getByTestId('personality-loading')).toBeInTheDocument();
    expect(screen.getByTestId('personality-loading')).toHaveAttribute('data-jewel', 'brain');
  });

  it('renders children with fetched data', async () => {
    const testData = { crystals: 12, capacity: 0.67 };
    (apiClient.get as Mock).mockResolvedValue(mockSuccessResponse(testData));

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="manifest">
          {(data) => <div data-testid="content">{JSON.stringify(data)}</div>}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('content')).toBeInTheDocument();
    });

    expect(screen.getByTestId('content')).toHaveTextContent(JSON.stringify(testData));
  });

  it('provides context to children', async () => {
    const testData = { id: 'test' };
    (apiClient.get as Mock).mockResolvedValue(mockSuccessResponse(testData));

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="manifest">
          {(_data, context) => (
            <div data-testid="context">
              <span data-testid="density">{context.density}</span>
              <span data-testid="path">{context.path}</span>
              <span data-testid="aspect">{context.aspect}</span>
              <span data-testid="loading">{String(context.loading)}</span>
            </div>
          )}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('context')).toBeInTheDocument();
    });

    expect(screen.getByTestId('density')).toHaveTextContent('spacious');
    expect(screen.getByTestId('path')).toHaveTextContent('self.memory');
    expect(screen.getByTestId('aspect')).toHaveTextContent('manifest');
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
  });
});

// =============================================================================
// Jewel Inference Tests
// =============================================================================

describe('PathProjection jewel inference', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWindowSize(1200);
    localStorage.clear();
  });

  const jewelMappings = [
    { path: 'self.memory', expected: 'brain' },
    { path: 'self.memory.capture', expected: 'brain' },
    { path: 'world.codebase', expected: 'gestalt' },
    { path: 'world.codebase.topology', expected: 'gestalt' },
    { path: 'concept.gardener', expected: 'gardener' },
    { path: 'self.garden.nurture', expected: 'gardener' },
    { path: 'world.forge', expected: 'forge' },
    { path: 'world.town', expected: 'coalition' },
    { path: 'world.town.citizens', expected: 'coalition' },
    { path: 'world.park', expected: 'park' },
    { path: 'world.park.scenario', expected: 'park' },
    { path: 'world.domain', expected: 'domain' },
  ];

  jewelMappings.forEach(({ path, expected }) => {
    it(`infers jewel "${expected}" from path "${path}"`, async () => {
      (apiClient.get as Mock).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockSuccessResponse({})), 100))
      );

      render(
        <Wrapper>
          <PathProjection path={path} aspect="manifest">
            {() => <div>Content</div>}
          </PathProjection>
        </Wrapper>
      );

      expect(screen.getByTestId('personality-loading')).toHaveAttribute('data-jewel', expected);
    });
  });

  it('allows explicit jewel override', async () => {
    (apiClient.get as Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockSuccessResponse({})), 100))
    );

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="manifest" jewel="forge">
          {() => <div>Content</div>}
        </PathProjection>
      </Wrapper>
    );

    // Should use explicit jewel instead of inferred
    expect(screen.getByTestId('personality-loading')).toHaveAttribute('data-jewel', 'forge');
  });
});

// =============================================================================
// Error Handling Tests
// =============================================================================

describe('PathProjection error handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWindowSize(1200);
    localStorage.clear();
  });

  it('renders error state on fetch failure', async () => {
    (apiClient.get as Mock).mockRejectedValue(new Error('Network error'));

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="manifest">
          {(data) => <div data-testid="content">{JSON.stringify(data)}</div>}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('empathy-error')).toBeInTheDocument();
    });

    expect(screen.getByTestId('error-details')).toHaveTextContent('Network error');
  });

  it('renders error state on AGENTESE error response', async () => {
    (apiClient.get as Mock).mockResolvedValue(mockErrorResponse('Path not found'));

    render(
      <Wrapper>
        <PathProjection path="self.unknown" aspect="manifest">
          {(data) => <div data-testid="content">{JSON.stringify(data)}</div>}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('empathy-error')).toBeInTheDocument();
    });

    expect(screen.getByTestId('error-details')).toHaveTextContent('Path not found');
  });

  // TODO: Test flaky due to timing - needs investigation
  it.skip('allows retry on error', async () => {
    const user = userEvent.setup();

    // First call fails, second succeeds
    (apiClient.get as Mock)
      .mockRejectedValueOnce(new Error('Temporary failure'))
      .mockResolvedValueOnce(mockSuccessResponse({ success: true }));

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="manifest">
          {(data) => <div data-testid="content">{JSON.stringify(data)}</div>}
        </PathProjection>
      </Wrapper>
    );

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByTestId('empathy-error')).toBeInTheDocument();
    });

    // Click retry
    await user.click(screen.getByTestId('retry-button'));

    // Wait for success
    await waitFor(() => {
      expect(screen.getByTestId('content')).toBeInTheDocument();
    });

    expect(screen.getByTestId('content')).toHaveTextContent(JSON.stringify({ success: true }));
  });

  // TODO: onError callback not implemented in PathProjection yet
  it.skip('calls onError callback', async () => {
    const onError = vi.fn();
    (apiClient.get as Mock).mockRejectedValue(new Error('Test error'));

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="manifest" onError={onError}>
          {() => <div>Content</div>}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(expect.any(Error));
    });
  });
});

// =============================================================================
// API Call Tests
// =============================================================================

describe('PathProjection API calls', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWindowSize(1200);
    localStorage.clear();
  });

  it('uses GET for manifest aspect without body', async () => {
    (apiClient.get as Mock).mockResolvedValue(mockSuccessResponse({ test: true }));

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="manifest">
          {() => <div>Content</div>}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith('/agentese/self/memory/manifest');
    });
  });

  it('uses POST for non-manifest aspects', async () => {
    (apiClient.post as Mock).mockResolvedValue(mockSuccessResponse({ captured: true }));

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="capture" body={{ content: 'test' }}>
          {() => <div>Content</div>}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith(
        '/agentese/self/memory/capture',
        { content: 'test' }
      );
    });
  });

  it('uses POST for manifest aspect with body', async () => {
    (apiClient.post as Mock).mockResolvedValue(mockSuccessResponse({ filtered: true }));

    render(
      <Wrapper>
        <PathProjection path="world.town" aspect="manifest" body={{ filter: 'active' }}>
          {() => <div>Content</div>}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith(
        '/agentese/world/town/manifest',
        { filter: 'active' }
      );
    });
  });

  it('calls onSuccess callback with data', async () => {
    const onSuccess = vi.fn();
    const testData = { id: 'test-123' };
    (apiClient.get as Mock).mockResolvedValue(mockSuccessResponse(testData));

    render(
      <Wrapper>
        <PathProjection path="self.memory" aspect="manifest" onSuccess={onSuccess}>
          {() => <div>Content</div>}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith(testData);
    });
  });
});

// =============================================================================
// Variant Tests
// =============================================================================

describe('PathProjection variants', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWindowSize(1200);
    localStorage.clear();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('LivePathProjection polls at specified interval', async () => {
    vi.useRealTimers(); // Need real timers for this test

    let callCount = 0;
    (apiClient.get as Mock).mockImplementation(() => {
      callCount++;
      return Promise.resolve(mockSuccessResponse({ count: callCount }));
    });

    render(
      <Wrapper>
        <LivePathProjection path="self.memory" aspect="manifest" interval={100}>
          {(data) => <div data-testid="content">{JSON.stringify(data)}</div>}
        </LivePathProjection>
      </Wrapper>
    );

    // Initial fetch
    await waitFor(() => {
      expect(screen.getByTestId('content')).toHaveTextContent('1');
    });

    // Wait for polling
    await waitFor(
      () => {
        expect(callCount).toBeGreaterThanOrEqual(2);
      },
      { timeout: 500 }
    );
  });

  it('LazyPathProjection skips initial fetch', async () => {
    (apiClient.get as Mock).mockResolvedValue(mockSuccessResponse({ test: true }));

    render(
      <Wrapper>
        <LazyPathProjection path="self.memory" aspect="manifest">
          {(data, { refetch }) => (
            <div>
              {data ? (
                <span data-testid="content">{JSON.stringify(data)}</span>
              ) : (
                <button data-testid="fetch-button" onClick={refetch}>
                  Fetch
                </button>
              )}
            </div>
          )}
        </LazyPathProjection>
      </Wrapper>
    );

    // Should NOT show loading (skipInitialFetch)
    expect(screen.queryByTestId('personality-loading')).not.toBeInTheDocument();

    // Should NOT have made API call
    expect(apiClient.get).not.toHaveBeenCalled();

    // Should show fetch button (no data)
    expect(screen.getByTestId('fetch-button')).toBeInTheDocument();
  });
});

// =============================================================================
// Custom Component Tests
// =============================================================================

describe('PathProjection custom components', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWindowSize(1200);
    localStorage.clear();
  });

  it('renders custom loading component', async () => {
    (apiClient.get as Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockSuccessResponse({})), 100))
    );

    render(
      <Wrapper>
        <PathProjection
          path="self.memory"
          aspect="manifest"
          loadingComponent={<div data-testid="custom-loading">Custom Loading...</div>}
        >
          {() => <div>Content</div>}
        </PathProjection>
      </Wrapper>
    );

    expect(screen.getByTestId('custom-loading')).toBeInTheDocument();
    expect(screen.queryByTestId('personality-loading')).not.toBeInTheDocument();
  });

  it('renders custom error component', async () => {
    (apiClient.get as Mock).mockRejectedValue(new Error('Test error'));

    render(
      <Wrapper>
        <PathProjection
          path="self.memory"
          aspect="manifest"
          errorComponent={<div data-testid="custom-error">Custom Error</div>}
        >
          {() => <div>Content</div>}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('custom-error')).toBeInTheDocument();
    });

    expect(screen.queryByTestId('empathy-error')).not.toBeInTheDocument();
  });
});

// =============================================================================
// BasicRendering Unwrap Tests
// =============================================================================

describe('PathProjection BasicRendering unwrap', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWindowSize(1200);
    localStorage.clear();
  });

  it('unwraps BasicRendering responses with metadata', async () => {
    // Crown Jewels wrap their responses in BasicRendering format
    const basicRenderingResponse = {
      data: {
        path: 'world.park',
        aspect: 'manifest',
        result: {
          summary: 'Park status',
          content: ['Line 1', 'Line 2'],
          metadata: {
            scenario_id: 'test-123',
            phase: 'CALM',
            active: true,
          },
        },
      },
    };

    (apiClient.get as Mock).mockResolvedValue(basicRenderingResponse);

    render(
      <Wrapper>
        <PathProjection path="world.park" aspect="manifest">
          {(data) => (
            <div data-testid="content">
              <span data-testid="scenario-id">{(data as any)?.scenario_id}</span>
              <span data-testid="phase">{(data as any)?.phase}</span>
            </div>
          )}
        </PathProjection>
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('content')).toBeInTheDocument();
    });

    // Should have unwrapped the metadata
    expect(screen.getByTestId('scenario-id')).toHaveTextContent('test-123');
    expect(screen.getByTestId('phase')).toHaveTextContent('CALM');
  });
});
