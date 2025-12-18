/**
 * Tests for Gestalt/Codebase query hooks.
 *
 * @see hooks/useGestaltQuery.ts
 * @see services/gestalt/contracts.py
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import {
  useGestaltManifest,
  useCodebaseHealth,
  useCodebaseDrift,
  useCodebaseTopology,
  useCodebaseModule,
  useScanCodebase,
  gestaltQueryKeys,
} from '../useGestaltQuery';

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
  path: 'world.codebase',
  aspect: 'manifest',
  result: {
    module_count: 45,
    edge_count: 120,
    language: 'python',
    average_health: 0.82,
    overall_grade: 'B+',
    drift_count: 3,
  },
};

const mockHealthResponse = {
  path: 'world.codebase',
  aspect: 'health',
  result: {
    average_health: 0.82,
    overall_grade: 'B+',
    grade_distribution: { 'A': 10, 'B': 25, 'C': 8, 'D': 2 },
    worst_modules: [
      { name: 'legacy.utils', grade: 'D', coupling: 0.9, cohesion: 0.3 },
    ],
    best_modules: [
      { name: 'core.domain', grade: 'A' },
    ],
  },
};

const mockDriftResponse = {
  path: 'world.codebase',
  aspect: 'drift',
  result: {
    total_violations: 5,
    unsuppressed: 3,
    suppressed: 2,
    violations: [
      { rule: 'no-cross-layer', source: 'api', target: 'domain', severity: 'error' },
    ],
  },
};

const mockTopologyResponse = {
  path: 'world.codebase',
  aspect: 'topology',
  result: {
    nodes: [
      { id: 'core.domain', label: 'core.domain', layer: 'domain', health_score: 0.95, x: 0, y: 0, z: 0 },
      { id: 'api.routes', label: 'api.routes', layer: 'api', health_score: 0.78, x: 1, y: 1, z: 0 },
    ],
    links: [
      { source: 'api.routes', target: 'core.domain', import_type: 'direct', is_violation: false },
    ],
    layers: ['domain', 'service', 'api'],
    stats: { node_count: 2, link_count: 1, violation_count: 0, avg_health: 0.86 },
  },
};

const mockModuleResponse = {
  path: 'world.codebase',
  aspect: 'module',
  result: {
    name: 'core.domain',
    path: 'impl/claude/agents/core/domain.py',
    lines_of_code: 250,
    layer: 'domain',
    exports: ['Entity', 'ValueObject', 'Repository'],
    health: { grade: 'A', score: 0.95, coupling: 0.2, cohesion: 0.9 },
    dependencies: ['typing', 'dataclasses'],
    dependents: ['api.routes', 'service.handler'],
  },
};

// =============================================================================
// Test Utilities
// =============================================================================

beforeEach(() => {
  vi.clearAllMocks();
});

// =============================================================================
// useGestaltManifest Tests
// =============================================================================

describe('useGestaltManifest', () => {
  it('fetches manifest on mount', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockManifestResponse });

    const { result } = renderHook(() => useGestaltManifest());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockManifestResponse.result);
    expect(result.current.error).toBeNull();
    expect(mockApiClient.get).toHaveBeenCalledWith('/agentese/world/codebase/manifest');
  });

  it('handles errors gracefully', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: { path: 'world.codebase', aspect: 'manifest', error: 'Codebase not scanned' },
    });

    const { result } = renderHook(() => useGestaltManifest());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.error?.message).toBe('Codebase not scanned');
  });
});

// =============================================================================
// useCodebaseHealth Tests
// =============================================================================

describe('useCodebaseHealth', () => {
  it('fetches health metrics', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockHealthResponse });

    const { result } = renderHook(() => useCodebaseHealth());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockHealthResponse.result);
    expect(result.current.data?.overall_grade).toBe('B+');
  });

  it('respects enabled option', async () => {
    renderHook(() => useCodebaseHealth({ enabled: false }));

    expect(mockApiClient.post).not.toHaveBeenCalled();
  });
});

// =============================================================================
// useCodebaseDrift Tests
// =============================================================================

describe('useCodebaseDrift', () => {
  it('fetches drift violations', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockDriftResponse });

    const { result } = renderHook(() => useCodebaseDrift());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockDriftResponse.result);
    expect(result.current.data?.total_violations).toBe(5);
    expect(result.current.data?.violations.length).toBe(1);
  });
});

// =============================================================================
// useCodebaseTopology Tests
// =============================================================================

describe('useCodebaseTopology', () => {
  it('fetches topology for visualization', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockTopologyResponse });

    const { result } = renderHook(() => useCodebaseTopology());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockTopologyResponse.result);
    expect(result.current.data?.nodes.length).toBe(2);
    expect(result.current.data?.links.length).toBe(1);
    expect(result.current.data?.layers).toContain('domain');
  });

  it('passes filter parameters', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockTopologyResponse });

    renderHook(() => useCodebaseTopology({ maxNodes: 50, minHealth: 0.5, role: 'architect' }));

    await waitFor(() => {
      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/agentese/world/codebase/topology',
        expect.objectContaining({ max_nodes: 50, min_health: 0.5, role: 'architect' })
      );
    });
  });
});

// =============================================================================
// useCodebaseModule Tests
// =============================================================================

describe('useCodebaseModule', () => {
  it('fetches module details', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockModuleResponse });

    const { result } = renderHook(() => useCodebaseModule('core.domain'));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockModuleResponse.result);
    expect(result.current.data?.name).toBe('core.domain');
    expect(result.current.data?.exports).toContain('Entity');
  });

  it('does not fetch when module name is empty', async () => {
    renderHook(() => useCodebaseModule(''));

    expect(mockApiClient.post).not.toHaveBeenCalled();
  });
});

// =============================================================================
// useScanCodebase Tests
// =============================================================================

describe('useScanCodebase', () => {
  it('triggers codebase rescan', async () => {
    const mockScanResponse = {
      path: 'world.codebase',
      aspect: 'scan',
      result: {
        status: 'completed',
        module_count: 48,
        edge_count: 125,
        overall_grade: 'B+',
      },
    };

    mockApiClient.post.mockResolvedValueOnce({ data: mockScanResponse });

    const { result } = renderHook(() => useScanCodebase());

    expect(result.current.isPending).toBe(false);

    const scanResult = await result.current.mutateAsync({});

    expect(scanResult).toEqual(mockScanResponse.result);
    expect(scanResult.status).toBe('completed');
    expect(mockApiClient.post).toHaveBeenCalledWith('/agentese/world/codebase/scan', {});
  });

  it('handles scan errors', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: { path: 'world.codebase', aspect: 'scan', error: 'Scan already in progress' },
    });

    const { result } = renderHook(() => useScanCodebase());

    await expect(result.current.mutateAsync({}))
      .rejects.toThrow('Scan already in progress');
  });
});

// =============================================================================
// Query Keys Tests
// =============================================================================

describe('gestaltQueryKeys', () => {
  it('generates correct key structure', () => {
    expect(gestaltQueryKeys.all).toEqual(['gestalt']);
    expect(gestaltQueryKeys.manifest()).toEqual(['gestalt', 'manifest']);
    expect(gestaltQueryKeys.health()).toEqual(['gestalt', 'health']);
    expect(gestaltQueryKeys.drift()).toEqual(['gestalt', 'drift']);
    expect(gestaltQueryKeys.topology(100)).toEqual(['gestalt', 'topology', 100]);
    expect(gestaltQueryKeys.module('core.domain')).toEqual(['gestalt', 'module', 'core.domain']);
  });
});
