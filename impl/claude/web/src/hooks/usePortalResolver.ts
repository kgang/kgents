/**
 * usePortalResolver: Hook for resolving portal URIs
 *
 * Provides a hook to resolve portal URIs through the backend API.
 * Integrates with the PortalToken component for on-demand resource expansion.
 *
 * Usage:
 *   const { resolvePortal, loading, error } = usePortalResolver();
 *   const resource = await resolvePortal("chat:session-123");
 *
 * See: spec/protocols/portal-resource-system.md
 */

import { useState, useCallback } from 'react';
import type { ResolvedResource } from '../components/tokens/types';

interface UsePortalResolverResult {
  resolvePortal: (uri: string) => Promise<ResolvedResource | null>;
  loading: boolean;
  error: string | null;
}

/**
 * Hook for resolving portal URIs.
 *
 * Returns a function to resolve portal URIs and track loading/error state.
 */
export function usePortalResolver(): UsePortalResolverResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resolvePortal = useCallback(async (uri: string): Promise<ResolvedResource | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/portal/resolve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ uri }),
      });

      if (!response.ok) {
        // Extract error message from response
        const errorData = await response.json().catch(() => null);
        const errorMessage = errorData?.detail || `Failed to resolve portal: ${response.statusText}`;

        setError(errorMessage);

        // Return null on error instead of throwing
        // This allows the UI to show fallback content
        return null;
      }

      const resource: ResolvedResource = await response.json();
      return resource;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error resolving portal';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { resolvePortal, loading, error };
}

/**
 * Resolve a portal URI (one-shot, no hook state).
 *
 * Useful for one-off resolutions without component state tracking.
 */
export async function resolvePortalURI(uri: string): Promise<ResolvedResource | null> {
  try {
    const response = await fetch('/api/portal/resolve', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ uri }),
    });

    if (!response.ok) {
      return null;
    }

    const resource: ResolvedResource = await response.json();
    return resource;
  } catch {
    return null;
  }
}
