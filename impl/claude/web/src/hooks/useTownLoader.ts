/**
 * useTownLoader - Hook for loading or creating Agent Town instances.
 *
 * Handles:
 * - Loading existing towns by ID
 * - Creating demo towns when paramTownId is 'demo'
 * - Error handling for 404s
 *
 * Extracted from Town.tsx for projection-first architecture.
 *
 * @example
 * const { townId, loading, error } = useTownLoader(paramTownId);
 */

import { useState, useEffect, useRef } from 'react';
import { townApi } from '../api/client';

interface UseTownLoaderResult {
  /** The resolved town ID (or null if loading/error) */
  townId: string | null;
  /** Whether the town is loading */
  loading: boolean;
  /** Error message if loading failed */
  error: string | null;
}

const LOAD_TIMEOUT_MS = 15000; // 15 second timeout

export function useTownLoader(paramTownId: string | undefined): UseTownLoaderResult {
  const [townId, setTownId] = useState<string | null>(null);
  const [loading, setLoading] = useState(!!paramTownId); // Only loading if there's a townId to load
  const [error, setError] = useState<string | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (!paramTownId) {
      setLoading(false);
      setError('No town ID provided');
      return;
    }

    // Set a timeout to prevent infinite loading
    timeoutRef.current = setTimeout(() => {
      setLoading(false);
      setError('Request timed out. Is the backend running?');
    }, LOAD_TIMEOUT_MS);

    const clearLoadTimeout = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };

    const loadTown = async (id: string) => {
      setLoading(true);
      setError(null);
      try {
        await townApi.get(id);
        clearLoadTimeout();
        setTownId(id);
      } catch (err: unknown) {
        clearLoadTimeout();
        const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
        if (axiosErr.response?.status === 404) {
          setError(`Town "${id}" not found`);
        } else if (axiosErr.response?.status === 401) {
          setError('Authentication required. Please sign in.');
        } else {
          setError(axiosErr.response?.data?.detail || 'Failed to load town');
        }
      } finally {
        setLoading(false);
      }
    };

    const createDemoTown = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await townApi.createWithId(paramTownId, {
          name: 'Demo Town',
          phase: 3,
          enable_dialogue: false,
        });
        clearLoadTimeout();
        const newTownId = response.id;
        if (newTownId !== paramTownId) {
          window.history.replaceState(null, '', `/town/${newTownId}`);
        }
        setTownId(newTownId);
      } catch (err: unknown) {
        clearLoadTimeout();
        const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
        if (axiosErr.response?.status === 401) {
          setError('Authentication required. Please sign in.');
        } else {
          setError(axiosErr.response?.data?.detail || 'Failed to create demo town');
        }
      } finally {
        setLoading(false);
      }
    };

    if (paramTownId === 'demo') {
      createDemoTown();
    } else {
      loadTown(paramTownId);
    }

    // Cleanup timeout on unmount
    return () => clearLoadTimeout();
  }, [paramTownId]);

  return { townId, loading, error };
}

export default useTownLoader;
