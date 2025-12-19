/**
 * Tests for Gardener query hooks.
 *
 * @see hooks/useGardenerQuery.ts
 * @see services/gardener/contracts.py
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import {
  useGardenerManifest,
  useGardenerSession,
  useGardenerPolynomial,
  useGardenerSessions,
  useGardenerPropose,
  useDefineSession,
  useAdvanceSession,
  useRouteInput,
  gardenerQueryKeys,
} from '../useGardenerQuery';

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
  path: 'concept.gardener',
  aspect: 'manifest',
  result: {
    active_session_id: 'session-001',
    active_session_name: 'Crown Jewels Integration',
    active_phase: 'ACT',
    total_sessions: 5,
    polynomial_ascii: '[SENSE] -> [ACT*] -> [REFLECT]',
  },
};

const mockSessionResponse = {
  path: 'concept.gardener',
  aspect: 'session.manifest',
  result: {
    status: 'active',
    session_id: 'session-001',
    name: 'Crown Jewels Integration',
    phase: 'ACT',
    phase_emoji: '\u26a1',
    phase_label: 'Acting',
    phase_desc: 'Executing the plan',
    sense_count: 2,
    act_count: 3,
    reflect_count: 0,
    intent: 'Complete Brain service integration',
    plan_path: 'plans/crown-jewels-enlightened.md',
    polynomial: '[S:2] -> [A:3*] -> [R:0]',
  },
};

const mockPolynomialResponse = {
  path: 'concept.gardener',
  aspect: 'session.polynomial',
  result: {
    current_phase: 'ACT',
    polynomial_ascii: '[S:2] -> [A:3*] -> [R:0]',
    diagram: '  SENSE ─── ACT* ─── REFLECT\n    2        3         0',
    valid_transitions: ['REFLECT'],
    sense_count: 2,
    act_count: 3,
    reflect_count: 0,
  },
};

const mockSessionsListResponse = {
  path: 'concept.gardener',
  aspect: 'sessions.manifest',
  result: {
    sessions: [
      { id: 'session-001', name: 'Crown Jewels Integration', phase: 'ACT', created_at: '2024-12-18T10:00:00Z', updated_at: '2024-12-18T14:30:00Z', is_active: true },
      { id: 'session-002', name: 'API Refactoring', phase: 'REFLECT', created_at: '2024-12-17T09:00:00Z', updated_at: '2024-12-17T18:00:00Z', is_active: false },
    ],
    count: 2,
    active_id: 'session-001',
  },
};

const mockProposeResponse = {
  path: 'concept.gardener',
  aspect: 'propose',
  result: {
    suggestion_count: 3,
    suggestions: [
      { path: 'self.memory.capture', description: 'Capture today\'s learnings', priority: 'high', reasoning: 'End of ACT phase' },
      { path: 'concept.gardener.session.advance', description: 'Move to REFLECT phase', priority: 'medium', reasoning: 'Significant progress made' },
    ],
  },
};

const mockDefineResponse = {
  path: 'concept.gardener',
  aspect: 'session.define',
  result: {
    status: 'created',
    session_id: 'session-003',
    name: 'New Feature Development',
    phase: 'SENSE',
    polynomial: '[S:0*] -> [A:0] -> [R:0]',
    message: 'Session created successfully',
  },
};

const mockAdvanceResponse = {
  path: 'concept.gardener',
  aspect: 'session.advance',
  result: {
    status: 'advanced',
    phase: 'REFLECT',
    phase_emoji: '\ud83e\udde0',
    phase_label: 'Reflecting',
    phase_desc: 'Reviewing outcomes and learning',
    polynomial: '[S:2] -> [A:3] -> [R:1*]',
    message: 'Advanced from ACT to REFLECT',
  },
};

const mockRouteResponse = {
  path: 'concept.gardener',
  aspect: 'route',
  result: {
    original_input: 'show me the brain topology',
    resolved_path: 'self.memory.topology',
    confidence: 0.92,
    method: 'llm',
    alternatives: ['self.memory.manifest', 'self.memory.surface'],
    explanation: 'User wants to visualize memory structure',
  },
};

// =============================================================================
// Test Utilities
// =============================================================================

beforeEach(() => {
  vi.clearAllMocks();
});

// =============================================================================
// useGardenerManifest Tests
// =============================================================================

describe('useGardenerManifest', () => {
  it('fetches manifest on mount', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: mockManifestResponse });

    const { result } = renderHook(() => useGardenerManifest());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockManifestResponse.result);
    expect(result.current.data?.active_phase).toBe('ACT');
    expect(mockApiClient.get).toHaveBeenCalledWith('/agentese/concept/gardener/manifest');
  });

  it('handles errors gracefully', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: { path: 'concept.gardener', aspect: 'manifest', error: 'No active session' },
    });

    const { result } = renderHook(() => useGardenerManifest());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.error?.message).toBe('No active session');
  });
});

// =============================================================================
// useGardenerSession Tests
// =============================================================================

describe('useGardenerSession', () => {
  it('fetches active session status', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockSessionResponse });

    const { result } = renderHook(() => useGardenerSession());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockSessionResponse.result);
    expect(result.current.data?.status).toBe('active');
    expect(result.current.data?.phase).toBe('ACT');
  });

  it('respects enabled option', async () => {
    renderHook(() => useGardenerSession({ enabled: false }));

    expect(mockApiClient.post).not.toHaveBeenCalled();
  });
});

// =============================================================================
// useGardenerPolynomial Tests
// =============================================================================

describe('useGardenerPolynomial', () => {
  it('fetches polynomial visualization', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockPolynomialResponse });

    const { result } = renderHook(() => useGardenerPolynomial());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockPolynomialResponse.result);
    expect(result.current.data?.current_phase).toBe('ACT');
    expect(result.current.data?.valid_transitions).toContain('REFLECT');
  });
});

// =============================================================================
// useGardenerSessions Tests
// =============================================================================

describe('useGardenerSessions', () => {
  it('fetches session list', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockSessionsListResponse });

    const { result } = renderHook(() => useGardenerSessions());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockSessionsListResponse.result);
    expect(result.current.data?.count).toBe(2);
    expect(result.current.data?.active_id).toBe('session-001');
  });
});

// =============================================================================
// useGardenerPropose Tests
// =============================================================================

describe('useGardenerPropose', () => {
  it('fetches proactive suggestions', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockProposeResponse });

    const { result } = renderHook(() => useGardenerPropose());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockProposeResponse.result);
    expect(result.current.data?.suggestion_count).toBe(3);
    expect(result.current.data?.suggestions?.length).toBe(2);
  });
});

// =============================================================================
// useDefineSession Tests
// =============================================================================

describe('useDefineSession', () => {
  it('creates new session successfully', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockDefineResponse });

    const { result } = renderHook(() => useDefineSession());

    expect(result.current.isPending).toBe(false);

    const defineResult = await result.current.mutateAsync({
      name: 'New Feature Development',
      plan_path: 'plans/new-feature.md',
      intent_description: 'Implement new user authentication',
      intent_priority: 'high',
    });

    expect(defineResult).toEqual(mockDefineResponse.result);
    expect(defineResult.status).toBe('created');
    expect(defineResult.phase).toBe('SENSE');
    expect(mockApiClient.post).toHaveBeenCalledWith(
      '/agentese/concept/gardener/session.define',
      expect.objectContaining({ name: 'New Feature Development' })
    );
  });

  it('handles define errors', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: { path: 'concept.gardener', aspect: 'session.define', error: 'Session limit reached' },
    });

    const { result } = renderHook(() => useDefineSession());

    await expect(result.current.mutateAsync({ name: 'test' }))
      .rejects.toThrow('Session limit reached');
  });
});

// =============================================================================
// useAdvanceSession Tests
// =============================================================================

describe('useAdvanceSession', () => {
  it('advances to next phase', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockAdvanceResponse });

    const { result } = renderHook(() => useAdvanceSession());

    const advanceResult = await result.current.mutateAsync({});

    expect(advanceResult).toEqual(mockAdvanceResponse.result);
    expect(advanceResult.status).toBe('advanced');
    expect(advanceResult.phase).toBe('REFLECT');
  });

  it('handles advance errors', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: { path: 'concept.gardener', aspect: 'session.advance', error: 'No active session' },
    });

    const { result } = renderHook(() => useAdvanceSession());

    await expect(result.current.mutateAsync({}))
      .rejects.toThrow('No active session');
  });
});

// =============================================================================
// useRouteInput Tests
// =============================================================================

describe('useRouteInput', () => {
  it('routes natural language to AGENTESE path', async () => {
    mockApiClient.post.mockResolvedValueOnce({ data: mockRouteResponse });

    const { result } = renderHook(() => useRouteInput());

    const routeResult = await result.current.mutateAsync({
      input: 'show me the brain topology',
      use_llm: true,
    });

    expect(routeResult).toEqual(mockRouteResponse.result);
    expect(routeResult.resolved_path).toBe('self.memory.topology');
    expect(routeResult.confidence).toBe(0.92);
    expect(routeResult.method).toBe('llm');
  });

  it('handles routing errors', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: { path: 'concept.gardener', aspect: 'route', error: 'Unable to parse input' },
    });

    const { result } = renderHook(() => useRouteInput());

    await expect(result.current.mutateAsync({ input: 'gibberish' }))
      .rejects.toThrow('Unable to parse input');
  });
});

// =============================================================================
// Query Keys Tests
// =============================================================================

describe('gardenerQueryKeys', () => {
  it('generates correct key structure', () => {
    expect(gardenerQueryKeys.all).toEqual(['gardener']);
    expect(gardenerQueryKeys.manifest()).toEqual(['gardener', 'manifest']);
    expect(gardenerQueryKeys.session()).toEqual(['gardener', 'session']);
    expect(gardenerQueryKeys.polynomial()).toEqual(['gardener', 'polynomial']);
    expect(gardenerQueryKeys.sessions()).toEqual(['gardener', 'sessions']);
    expect(gardenerQueryKeys.propose()).toEqual(['gardener', 'propose']);
  });
});
