/**
 * Tests for Workshop query hooks.
 *
 * @see hooks/useWorkshopQuery.ts
 * @see services/town/contracts.py
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import {
  useWorkshopManifest,
  useWorkshopBuilders,
  useAssignWorkshopTask,
  useAdvanceWorkshop,
  useCompleteWorkshop,
  workshopQueryKeys,
} from '../useWorkshopQuery';

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
  path: 'world.town.workshop',
  aspect: 'manifest',
  result: {
    is_active: true,
    current_phase: 'DESIGNING',
    current_task_id: 'task-123',
    current_task_description: 'Build Crown Jewel integration',
    builders_count: 5,
    artifacts_count: 3,
    total_tokens_used: 1500,
    phase_progress: 0.6,
  },
};

const mockBuildersResponse = {
  path: 'world.town.workshop',
  aspect: 'builders',
  result: {
    builders: [
      { archetype: 'Scout', name: 'Scout-1', phase: 'EXPLORING', is_active: true, is_in_specialty: true },
      { archetype: 'Sage', name: 'Sage-1', phase: 'DESIGNING', is_active: true, is_in_specialty: false },
      { archetype: 'Spark', name: 'Spark-1', phase: 'IDLE', is_active: false, is_in_specialty: false },
      { archetype: 'Steady', name: 'Steady-1', phase: 'PROTOTYPING', is_active: true, is_in_specialty: true },
      { archetype: 'Sync', name: 'Sync-1', phase: 'INTEGRATING', is_active: true, is_in_specialty: true },
    ],
    lead_builder: 'Sage-1',
  },
};

const mockAssignResponse = {
  path: 'world.town.workshop',
  aspect: 'assign',
  result: {
    status: 'assigned',
    task_id: 'task-456',
    description: 'New feature implementation',
    assigned_builders: ['Scout-1', 'Sage-1', 'Steady-1'],
    estimated_tokens: 2000,
  },
};

const mockAdvanceResponse = {
  path: 'world.town.workshop',
  aspect: 'advance',
  result: {
    status: 'advanced',
    previous_phase: 'DESIGNING',
    current_phase: 'PROTOTYPING',
    handoff_from: 'Sage-1',
    handoff_to: 'Steady-1',
  },
};

const mockCompleteResponse = {
  path: 'world.town.workshop',
  aspect: 'complete',
  result: {
    status: 'completed',
    task_id: 'task-123',
    artifacts_produced: 5,
    total_tokens: 3200,
    duration_seconds: 1800,
  },
};

// =============================================================================
// Test Utilities
// =============================================================================

beforeEach(() => {
  vi.clearAllMocks();
});

// =============================================================================
// useWorkshopManifest Tests
// =============================================================================

describe('useWorkshopManifest', () => {
  it('fetches manifest on mount', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockManifestResponse });

    const { result } = renderHook(() => useWorkshopManifest());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockManifestResponse.result);
    expect(result.current.data?.current_phase).toBe('DESIGNING');
    expect(mockApiClient.get).toHaveBeenCalledWith('/agentese/world/town/workshop/manifest');
  });

  it('handles errors gracefully', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: { path: 'world.town.workshop', aspect: 'manifest', error: 'Workshop not initialized' },
    });

    const { result } = renderHook(() => useWorkshopManifest());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.error?.message).toBe('Workshop not initialized');
  });

  it('provides refetch function', async () => {
    mockApiClient.get.mockResolvedValue({ data: mockManifestResponse });

    const { result } = renderHook(() => useWorkshopManifest());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    result.current.refetch();

    await waitFor(() => {
      expect(mockApiClient.get).toHaveBeenCalledTimes(2);
    });
  });
});

// =============================================================================
// useWorkshopBuilders Tests
// =============================================================================

describe('useWorkshopBuilders', () => {
  it('fetches builder list', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockBuildersResponse });

    const { result } = renderHook(() => useWorkshopBuilders());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockBuildersResponse.result);
    expect(result.current.data?.builders.length).toBe(5);
    expect(result.current.data?.lead_builder).toBe('Sage-1');
  });

  it('respects enabled option', async () => {
    renderHook(() => useWorkshopBuilders({ enabled: false }));

    expect(mockApiClient.post).not.toHaveBeenCalled();
  });
});

// =============================================================================
// useAssignWorkshopTask Tests
// =============================================================================

describe('useAssignWorkshopTask', () => {
  it('assigns task successfully', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockAssignResponse });

    const { result } = renderHook(() => useAssignWorkshopTask());

    expect(result.current.isPending).toBe(false);

    const assignResult = await result.current.mutateAsync({
      description: 'New feature implementation',
      priority: 1,
    });

    expect(assignResult).toEqual(mockAssignResponse.result);
    expect(assignResult.task_id).toBe('task-456');
    expect(mockApiClient.post).toHaveBeenCalledWith(
      '/agentese/world/town/workshop/assign',
      { description: 'New feature implementation', priority: 1 }
    );
  });

  it('handles assign errors', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: { path: 'world.town.workshop', aspect: 'assign', error: 'Task already in progress' },
    });

    const { result } = renderHook(() => useAssignWorkshopTask());

    await expect(result.current.mutateAsync({ description: 'test' }))
      .rejects.toThrow('Task already in progress');
  });

  it('sets isPending during mutation', async () => {
    let resolvePromise: (value: unknown) => void;
    const promise = new Promise((resolve) => { resolvePromise = resolve; });
    mockApiClient.post.mockReturnValueOnce(promise);

    const { result } = renderHook(() => useAssignWorkshopTask());

    expect(result.current.isPending).toBe(false);

    // Start the mutation
    const mutationPromise = result.current.mutateAsync({ description: 'test' });

    // Wait for isPending to become true
    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Resolve the promise
    resolvePromise!({ data: mockAssignResponse });
    await mutationPromise;

    // Wait for isPending to become false
    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });
  });
});

// =============================================================================
// useAdvanceWorkshop Tests
// =============================================================================

describe('useAdvanceWorkshop', () => {
  it('advances to next phase', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockAdvanceResponse });

    const { result } = renderHook(() => useAdvanceWorkshop());

    const advanceResult = await result.current.mutateAsync();

    expect(advanceResult).toEqual(mockAdvanceResponse.result);
    expect(advanceResult.previous_phase).toBe('DESIGNING');
    expect(advanceResult.current_phase).toBe('PROTOTYPING');
  });

  it('handles advance errors', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: { path: 'world.town.workshop', aspect: 'advance', error: 'No active task' },
    });

    const { result } = renderHook(() => useAdvanceWorkshop());

    await expect(result.current.mutateAsync())
      .rejects.toThrow('No active task');
  });
});

// =============================================================================
// useCompleteWorkshop Tests
// =============================================================================

describe('useCompleteWorkshop', () => {
  it('completes workshop task', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockCompleteResponse });

    const { result } = renderHook(() => useCompleteWorkshop());

    const completeResult = await result.current.mutateAsync();

    expect(completeResult).toEqual(mockCompleteResponse.result);
    expect(completeResult.status).toBe('completed');
    expect(completeResult.artifacts_produced).toBe(5);
  });

  it('handles completion errors', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: { path: 'world.town.workshop', aspect: 'complete', error: 'Task incomplete' },
    });

    const { result } = renderHook(() => useCompleteWorkshop());

    await expect(result.current.mutateAsync())
      .rejects.toThrow('Task incomplete');
  });
});

// =============================================================================
// Query Keys Tests
// =============================================================================

describe('workshopQueryKeys', () => {
  it('generates correct key structure', () => {
    expect(workshopQueryKeys.all).toEqual(['workshop']);
    expect(workshopQueryKeys.manifest()).toEqual(['workshop', 'manifest']);
    expect(workshopQueryKeys.builders()).toEqual(['workshop', 'builders']);
  });
});
