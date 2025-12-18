/**
 * useDesignGateway - Hook bridging local design state with AGENTESE gateway.
 *
 * Combines:
 * - Local useDesignPolynomial for responsive density/content/motion state
 * - AGENTESE gateway for operad verification and law checking
 *
 * The local polynomial runs in the browser for instant responsiveness.
 * The gateway provides authoritative law verification from the backend.
 *
 * @see impl/claude/agents/design/ - Python backend
 * @see impl/claude/protocols/agentese/contexts/design.py - AGENTESE nodes
 */

import { useState, useCallback, useEffect } from 'react';
import {
  designApi,
  type OperadVerifyResponse,
  type OperadManifestResponse,
  type OperadOperation,
} from '../api/client';
import {
  useDesignPolynomial,
  type DesignState,
  type UseDesignPolynomialOptions,
} from './useDesignPolynomial';

// =============================================================================
// Types
// =============================================================================

export interface OperadInfo {
  name: string;
  operations: string[];
  lawCount: number;
}

export interface OperadOperationsInfo {
  layout: Record<string, OperadOperation> | null;
  content: Record<string, OperadOperation> | null;
  motion: Record<string, OperadOperation> | null;
}

export interface UseDesignGatewayOptions extends UseDesignPolynomialOptions {
  /** Whether to auto-fetch operad data on mount (default: true) */
  autoFetch?: boolean;
  /** Whether to auto-verify laws on mount (default: false) */
  autoVerify?: boolean;
}

export interface UseDesignGatewayResult {
  // Local state (from useDesignPolynomial)
  /** Current local design state (responsive to viewport/container) */
  localState: DesignState;
  /** Send input to local state machine */
  send: ReturnType<typeof useDesignPolynomial>['send'];

  // Gateway data
  /** Layout operad info from gateway */
  layoutOperad: OperadInfo | null;
  /** Content operad info from gateway */
  contentOperad: OperadInfo | null;
  /** Motion operad info from gateway */
  motionOperad: OperadInfo | null;
  /** All operad operations (lazy loaded) */
  operations: OperadOperationsInfo;
  /** Law verification results */
  verification: OperadVerifyResponse | null;

  // Loading states
  /** Whether operads are loading */
  isLoadingOperads: boolean;
  /** Whether verification is running */
  isVerifying: boolean;
  /** Error message if any */
  error: string | null;

  // Actions
  /** Refresh operad data from gateway */
  refreshOperads: () => Promise<void>;
  /** Verify all design laws via gateway */
  verifyLaws: () => Promise<OperadVerifyResponse | null>;
  /** Load operations for all operads */
  loadOperations: () => Promise<void>;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useDesignGateway(
  options: UseDesignGatewayOptions = {}
): UseDesignGatewayResult {
  const { autoFetch = true, autoVerify = false, ...polynomialOptions } = options;

  // Local polynomial state machine
  const polynomial = useDesignPolynomial(polynomialOptions);

  // Gateway state
  const [layoutOperad, setLayoutOperad] = useState<OperadInfo | null>(null);
  const [contentOperad, setContentOperad] = useState<OperadInfo | null>(null);
  const [motionOperad, setMotionOperad] = useState<OperadInfo | null>(null);
  const [operations, setOperations] = useState<OperadOperationsInfo>({
    layout: null,
    content: null,
    motion: null,
  });
  const [verification, setVerification] = useState<OperadVerifyResponse | null>(null);

  // Loading states
  const [isLoadingOperads, setIsLoadingOperads] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Transform API response to OperadInfo
  const toOperadInfo = (response: OperadManifestResponse): OperadInfo => ({
    name: response.name,
    operations: response.operations,
    lawCount: response.law_count,
  });

  // Fetch operad manifests
  const refreshOperads = useCallback(async () => {
    setIsLoadingOperads(true);
    setError(null);
    try {
      const [layoutRes, contentRes, motionRes] = await Promise.all([
        designApi.layoutManifest(),
        designApi.contentManifest(),
        designApi.motionManifest(),
      ]);
      setLayoutOperad(toOperadInfo(layoutRes));
      setContentOperad(toOperadInfo(contentRes));
      setMotionOperad(toOperadInfo(motionRes));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch operads';
      setError(message);
      console.error('[useDesignGateway] Failed to fetch operads:', err);
    } finally {
      setIsLoadingOperads(false);
    }
  }, []);

  // Load operations for all operads
  const loadOperations = useCallback(async () => {
    setError(null);
    try {
      const [layoutOps, contentOps, motionOps] = await Promise.all([
        designApi.layoutOperations(),
        designApi.contentOperations(),
        designApi.motionOperations(),
      ]);
      setOperations({
        layout: layoutOps,
        content: contentOps,
        motion: motionOps,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load operations';
      setError(message);
      console.error('[useDesignGateway] Failed to load operations:', err);
    }
  }, []);

  // Verify all design laws
  const verifyLaws = useCallback(async (): Promise<OperadVerifyResponse | null> => {
    setIsVerifying(true);
    setError(null);
    try {
      const result = await designApi.operadVerify();
      setVerification(result);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to verify laws';
      setError(message);
      console.error('[useDesignGateway] Failed to verify laws:', err);
      return null;
    } finally {
      setIsVerifying(false);
    }
  }, []);

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch) {
      refreshOperads();
    }
  }, [autoFetch, refreshOperads]);

  // Auto-verify on mount
  useEffect(() => {
    if (autoVerify) {
      verifyLaws();
    }
  }, [autoVerify, verifyLaws]);

  return {
    // Local state
    localState: polynomial.state,
    send: polynomial.send,

    // Gateway data
    layoutOperad,
    contentOperad,
    motionOperad,
    operations,
    verification,

    // Loading states
    isLoadingOperads,
    isVerifying,
    error,

    // Actions
    refreshOperads,
    verifyLaws,
    loadOperations,
  };
}

export default useDesignGateway;
