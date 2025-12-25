/**
 * Tests for usePortalResolver hook
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { usePortalResolver, resolvePortalURI } from '../usePortalResolver';

// Mock fetch
global.fetch = vi.fn();

describe('usePortalResolver', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('resolves a portal URI successfully', async () => {
    const mockResource = {
      uri: 'file:test.md',
      resource_type: 'file',
      exists: true,
      title: 'test.md',
      preview: 'Test content',
      content: 'Full test content',
      actions: ['expand'],
      metadata: {},
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResource,
    });

    const { result } = renderHook(() => usePortalResolver());

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);

    const promise = result.current.resolvePortal('file:test.md');

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const resource = await promise;

    expect(resource).toEqual(mockResource);
    expect(global.fetch).toHaveBeenCalledWith('/api/portal/resolve', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ uri: 'file:test.md' }),
    });
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      statusText: 'Not Found',
      json: async () => ({ detail: 'Resource not found' }),
    });

    const { result } = renderHook(() => usePortalResolver());

    const resource = await result.current.resolvePortal('file:nonexistent.md');

    expect(resource).toBe(null);
    expect(result.current.error).toBe('Resource not found');
  });

  it('handles network errors gracefully', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => usePortalResolver());

    const resource = await result.current.resolvePortal('file:test.md');

    expect(resource).toBe(null);
    expect(result.current.error).toBe('Network error');
  });
});

describe('resolvePortalURI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('resolves a portal URI successfully', async () => {
    const mockResource = {
      uri: 'mark:mark-123',
      resource_type: 'mark',
      exists: true,
      title: 'Mark 123',
      preview: 'Mark preview',
      content: { action: 'Test action' },
      actions: ['expand'],
      metadata: {},
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResource,
    });

    const resource = await resolvePortalURI('mark:mark-123');

    expect(resource).toEqual(mockResource);
  });

  it('returns null on error', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    const resource = await resolvePortalURI('file:test.md');

    expect(resource).toBe(null);
  });
});
