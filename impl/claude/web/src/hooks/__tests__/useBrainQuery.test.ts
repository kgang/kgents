/**
 * Tests for Brain query hooks.
 *
 * @see hooks/useBrainQuery.ts
 * @see services/brain/contracts.py
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import {
  useBrainManifest,
  useMemorySearch,
  useMemorySurface,
  useMemoryCrystal,
  useMemoryRecent,
  useMemoryByTag,
  useMemoryTopology,
  useCaptureMemory,
  brainQueryKeys,
} from '../useBrainQuery';

// =============================================================================
// Mocks
// =============================================================================

const mockApiClient = {
  get: vi.fn(),
  post: vi.fn(),
};

vi.mock('../../api/client', () => ({
  apiClient: mockApiClient,
}));

// =============================================================================
// Test Fixtures
// =============================================================================

const mockManifestResponse = {
  path: 'self.memory',
  aspect: 'manifest',
  result: {
    status: 'healthy',
    total_crystals: 42,
    active_crystals: 35,
    storage_backend: 'sqlite',
    embedder_type: 'local',
    embedder_dimension: 384,
  },
};

const mockSearchResponse = {
  path: 'self.memory',
  aspect: 'search',
  result: {
    count: 2,
    crystals: [
      { id: 'crystal-1', content: 'Test content', similarity: 0.95 },
      { id: 'crystal-2', content: 'Another test', similarity: 0.87 },
    ],
    query_embedding_time_ms: 12,
    search_time_ms: 5,
  },
};

const mockTopologyResponse = {
  path: 'self.memory',
  aspect: 'topology',
  result: {
    nodes: [
      { id: 'node-1', x: 0, y: 0, z: 0, label: 'Node 1' },
      { id: 'node-2', x: 1, y: 1, z: 1, label: 'Node 2' },
    ],
    edges: [{ source: 'node-1', target: 'node-2', similarity: 0.8 }],
    stats: { node_count: 2, edge_count: 1 },
  },
};

// =============================================================================
// Test Utilities
// =============================================================================

beforeEach(() => {
  vi.clearAllMocks();
});

// =============================================================================
// useBrainManifest Tests
// =============================================================================

describe('useBrainManifest', () => {
  it('fetches manifest on mount', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockManifestResponse });

    const { result } = renderHook(() => useBrainManifest());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockManifestResponse.result);
    expect(result.current.error).toBeNull();
    expect(mockApiClient.get).toHaveBeenCalledWith('/agentese/self/memory/manifest');
  });

  it('handles errors gracefully', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: { path: 'self.memory', aspect: 'manifest', error: 'Storage unavailable' },
    });

    const { result } = renderHook(() => useBrainManifest());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.error?.message).toBe('Storage unavailable');
  });

  it('provides refetch function', async () => {
    mockApiClient.get.mockResolvedValue({ data: mockManifestResponse });

    const { result } = renderHook(() => useBrainManifest());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Call refetch
    result.current.refetch();

    await waitFor(() => {
      expect(mockApiClient.get).toHaveBeenCalledTimes(2);
    });
  });
});

// =============================================================================
// useMemorySearch Tests
// =============================================================================

describe('useMemorySearch', () => {
  it('searches memory when query provided', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockSearchResponse });

    const { result } = renderHook(() => useMemorySearch('test query'));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockSearchResponse.result);
    expect(mockApiClient.post).toHaveBeenCalledWith(
      '/agentese/self/memory/search',
      { query: 'test query', limit: 10 }
    );
  });

  it('does not search when query is empty', async () => {
    const { result } = renderHook(() => useMemorySearch(''));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockApiClient.post).not.toHaveBeenCalled();
    expect(result.current.data).toBeNull();
  });

  it('respects custom limit', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockSearchResponse });

    renderHook(() => useMemorySearch('test', { limit: 5 }));

    await waitFor(() => {
      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/agentese/self/memory/search',
        { query: 'test', limit: 5 }
      );
    });
  });
});

// =============================================================================
// useMemorySurface Tests
// =============================================================================

describe('useMemorySurface', () => {
  it('surfaces memories for context', async () => {
    const mockSurfaceResponse = {
      path: 'self.memory',
      aspect: 'surface',
      result: {
        count: 3,
        crystals: [
          { id: 'c1', content: 'Memory 1', relevance: 0.9 },
        ],
      },
    };

    mockApiClient.post.mockResolvedValueOnce({ data: mockSurfaceResponse });

    const { result } = renderHook(() => useMemorySurface('current context'));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockSurfaceResponse.result);
  });

  it('respects enabled option', async () => {
    renderHook(() => useMemorySurface('context', { enabled: false }));

    expect(mockApiClient.post).not.toHaveBeenCalled();
  });
});

// =============================================================================
// useMemoryTopology Tests
// =============================================================================

describe('useMemoryTopology', () => {
  it('fetches topology for visualization', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockTopologyResponse });

    const { result } = renderHook(() => useMemoryTopology());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockTopologyResponse.result);
    expect(result.current.data?.nodes.length).toBe(2);
    expect(result.current.data?.edges.length).toBe(1);
  });

  it('passes threshold parameter', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockTopologyResponse });

    renderHook(() => useMemoryTopology({ threshold: 0.8 }));

    await waitFor(() => {
      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/agentese/self/memory/topology',
        expect.objectContaining({ threshold: 0.8 })
      );
    });
  });
});

// =============================================================================
// useCaptureMemory Tests
// =============================================================================

describe('useCaptureMemory', () => {
  it('captures content successfully', async () => {
    const mockCaptureResponse = {
      path: 'self.memory',
      aspect: 'capture',
      result: {
        status: 'captured',
        crystal_id: 'new-crystal-123',
        storage: 'sqlite',
      },
    };

    mockApiClient.post.mockResolvedValueOnce({ data: mockCaptureResponse });

    const { result } = renderHook(() => useCaptureMemory());

    expect(result.current.isPending).toBe(false);

    const captureResult = await result.current.mutateAsync({
      content: 'Important insight',
      tags: ['insight', 'test'],
    });

    expect(captureResult).toEqual(mockCaptureResponse.result);
    expect(mockApiClient.post).toHaveBeenCalledWith(
      '/agentese/self/memory/capture',
      { content: 'Important insight', tags: ['insight', 'test'] }
    );
  });

  it('handles capture errors', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: { path: 'self.memory', aspect: 'capture', error: 'Storage full' },
    });

    const { result } = renderHook(() => useCaptureMemory());

    await expect(result.current.mutateAsync({ content: 'test' }))
      .rejects.toThrow('Storage full');
  });
});

// =============================================================================
// Query Keys Tests
// =============================================================================

describe('brainQueryKeys', () => {
  it('generates correct key structure', () => {
    expect(brainQueryKeys.all).toEqual(['brain']);
    expect(brainQueryKeys.manifest()).toEqual(['brain', 'manifest']);
    expect(brainQueryKeys.search('test')).toEqual(['brain', 'search', 'test']);
    expect(brainQueryKeys.topology(0.7)).toEqual(['brain', 'topology', 0.7]);
  });
});
