/**
 * Soul Data Fetching Hooks (AGENTESE Contract-Driven)
 *
 * Hooks for K-gent soul state within Forge context.
 * AGENTESE Path: world.forge.soul
 *
 * @see services/forge/soul_node.py
 * @see agents/k/eigenvectors.py
 */

import { useEffect, useCallback, useState } from 'react';
import { KENT_EIGENVECTORS, type KentEigenvectorDimensions } from '@/components/eigenvector';

// === Types ===

export interface SoulManifestResponse {
  type: 'soul_manifest';
  mode: string;
  eigenvectors: KentEigenvectorDimensions;
  session_interactions: number;
  session_tokens: number;
  has_llm: boolean;
}

export interface SoulVibeResponse {
  type: 'soul_vibe';
  dimensions: KentEigenvectorDimensions;
  context: string;
}

interface AsyncState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

// === AGENTESE Fetch Helper ===

async function fetchAgentese<T>(path: string): Promise<T> {
  // Convert AGENTESE path to URL path (world.forge.soul.manifest → world/forge/soul/manifest)
  const urlPath = path.replace(/\./g, '/');
  const response = await fetch(`/api/agentese/${urlPath}`);

  if (!response.ok) {
    throw new Error(`AGENTESE fetch failed: ${response.status} ${response.statusText}`);
  }

  const json = await response.json();

  // AGENTESE responses wrap result in { result: T } or return T directly
  return json.result ?? json;
}

// === Hooks ===

/**
 * Hook for K-gent soul manifest (mode, interactions, eigenvectors).
 *
 * AGENTESE Path: world.forge.soul.manifest
 */
export function useSoulManifest(options?: { refreshInterval?: number }) {
  const [state, setState] = useState<AsyncState<SoulManifestResponse>>({
    data: null,
    isLoading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await fetchAgentese<SoulManifestResponse>('world.forge.soul.manifest');
      setState({ data, isLoading: false, error: null });
    } catch (err) {
      // On error, return dormant state with Kent's default eigenvectors
      setState({
        data: {
          type: 'soul_manifest',
          mode: 'dormant',
          eigenvectors: KENT_EIGENVECTORS,
          session_interactions: 0,
          session_tokens: 0,
          has_llm: false,
        },
        isLoading: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      });
    }
  }, []);

  useEffect(() => {
    refetch();

    // Optional: Refresh on interval
    const interval = options?.refreshInterval;
    if (interval && interval > 0) {
      const timer = setInterval(refetch, interval);
      return () => clearInterval(timer);
    }
  }, [refetch, options?.refreshInterval]);

  return {
    ...state,
    refetch,
  };
}

/**
 * Hook for K-gent soul vibe (eigenvectors with context prompt).
 *
 * AGENTESE Path: world.forge.soul.vibe
 */
export function useSoulVibe() {
  const [state, setState] = useState<AsyncState<SoulVibeResponse>>({
    data: null,
    isLoading: true,
    error: null,
  });

  const refetch = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await fetchAgentese<SoulVibeResponse>('world.forge.soul.vibe');
      setState({ data, isLoading: false, error: null });
    } catch (err) {
      // On error, return Kent's default eigenvectors
      setState({
        data: {
          type: 'soul_vibe',
          dimensions: KENT_EIGENVECTORS,
          context: 'K-gent soul not connected',
        },
        isLoading: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      });
    }
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return {
    ...state,
    refetch,
  };
}

// === Utility Functions ===

/**
 * Check if soul is in an active (non-dormant) mode.
 */
export function isSoulActive(manifest: SoulManifestResponse | null): boolean {
  if (!manifest) return false;
  return manifest.mode !== 'dormant' && manifest.mode !== 'unknown';
}

/**
 * Get soul mode icon.
 */
export function getSoulModeIcon(mode: string): string {
  const icons: Record<string, string> = {
    reflect: '🪞',
    advise: '💡',
    challenge: '⚔️',
    explore: '🧭',
    dormant: '💤',
    unknown: '❓',
  };
  return icons[mode] || '✨';
}

/**
 * Get soul mode display name.
 */
export function getSoulModeLabel(mode: string): string {
  const labels: Record<string, string> = {
    reflect: 'Reflecting',
    advise: 'Advising',
    challenge: 'Challenging',
    explore: 'Exploring',
    dormant: 'Dormant',
    unknown: 'Unknown',
  };
  return labels[mode] || mode;
}
