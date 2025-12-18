/**
 * PathProjection - Generic AGENTESE Path to Projection Wrapper
 *
 * The core primitive for projection-first pages. Handles:
 * - AGENTESE path invocation via gateway
 * - Loading states with PersonalityLoading
 * - Error handling with EmpathyError
 * - Trace collection for devex visibility
 * - Observer-dependent projections
 * - Streaming support (future)
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 * @see spec/protocols/projection.md - The Projection Protocol
 *
 * @example
 * ```tsx
 * // Minimal projection-first page (< 50 LOC target)
 * export default function BrainPage() {
 *   return (
 *     <PathProjection path="self.memory" aspect="manifest">
 *       {(data, { density }) => (
 *         <BrainVisualization data={data} density={density} />
 *       )}
 *     </PathProjection>
 *   );
 * }
 * ```
 */

import {
  useEffect,
  useState,
  useCallback,
  useMemo,
  useRef,
  type ReactNode,
  type CSSProperties,
} from 'react';
import { useShell, useTracedInvoke } from './ShellProvider';
import { PersonalityLoading } from '@/components/joy/PersonalityLoading';
import { EmpathyError } from '@/components/joy/EmpathyError';
import { apiClient, AgenteseError } from '@/api/client';
import type { Density, Observer, CrownJewel } from './types';

// =============================================================================
// Types
// =============================================================================

/**
 * Context provided to projection children.
 * Contains everything needed to render density-aware, observer-dependent content.
 */
export interface ProjectionContext {
  /** Current layout density */
  density: Density;
  /** Current observer (who is looking) */
  observer: Observer;
  /** Loading state */
  loading: boolean;
  /** Error if any */
  error: Error | null;
  /** Refetch data */
  refetch: () => void;
  /** Whether streaming is active (future) */
  streaming: boolean;
  /** The AGENTESE path that was invoked */
  path: string;
  /** The aspect that was invoked */
  aspect: string;
  /** Mobile viewport (<768px) */
  isMobile: boolean;
  /** Tablet viewport (768-1024px) */
  isTablet: boolean;
  /** Desktop viewport (>1024px) */
  isDesktop: boolean;
}

/**
 * Props for PathProjection component.
 * @template T - The type of data returned from the AGENTESE path
 */
export interface PathProjectionProps<T = unknown> {
  /** AGENTESE path (e.g., "self.memory", "world.town.citizens") */
  path: string;
  /** Aspect to invoke. Default: "manifest" */
  aspect?: string;
  /** Request body for POST aspects */
  body?: Record<string, unknown>;
  /** Render function receiving data and context */
  children: (data: T, context: ProjectionContext) => ReactNode;
  /** Which Crown Jewel this projection belongs to (for loading states) */
  jewel?: CrownJewel;
  /** Loading action verb (for personalized loading messages) */
  loadingAction?: string;
  /** Custom loading component */
  loadingComponent?: ReactNode;
  /** Custom error component */
  errorComponent?: ReactNode;
  /** Skip initial fetch (for manual control) */
  skipInitialFetch?: boolean;
  /** Polling interval in ms (0 = disabled) */
  pollInterval?: number;
  /** Container className */
  className?: string;
  /** Container style */
  style?: CSSProperties;
  /** Called when data is fetched successfully */
  onSuccess?: (data: T) => void;
  /** Called when fetch fails */
  onError?: (error: Error) => void;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Infer Crown Jewel from AGENTESE path.
 */
function inferJewel(path: string): CrownJewel | undefined {
  const pathLower = path.toLowerCase();

  // Map path prefixes to jewels
  const mappings: Array<{ pattern: RegExp | string; jewel: CrownJewel }> = [
    { pattern: /^self\.memory/, jewel: 'brain' },
    { pattern: /^world\.codebase/, jewel: 'gestalt' },
    { pattern: /^concept\.gardener|^self\.garden/, jewel: 'gardener' },
    { pattern: /^world\.atelier/, jewel: 'atelier' },
    { pattern: /^world\.town/, jewel: 'coalition' },
    { pattern: /^world\.park/, jewel: 'park' },
    { pattern: /^world\.domain/, jewel: 'domain' },
  ];

  for (const { pattern, jewel } of mappings) {
    if (typeof pattern === 'string' ? pathLower.includes(pattern) : pattern.test(pathLower)) {
      return jewel;
    }
  }

  return undefined;
}

/**
 * Convert AGENTESE path to API route.
 * e.g., "self.memory" + "manifest" => "/agentese/self/memory/manifest"
 */
function pathToRoute(path: string, aspect: string): string {
  const segments = path.split('.');
  return `/agentese/${segments.join('/')}/${aspect}`;
}

/**
 * Determine error type from error instance.
 */
function getErrorType(error: Error): 'network' | 'notfound' | 'permission' | 'timeout' | 'unknown' {
  if (error instanceof AgenteseError) {
    const msg = error.message.toLowerCase();
    if (msg.includes('not found') || msg.includes('404')) return 'notfound';
    if (msg.includes('permission') || msg.includes('403') || msg.includes('unauthorized')) return 'permission';
    if (msg.includes('timeout')) return 'timeout';
  }

  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return 'network';
  }

  return 'unknown';
}

// =============================================================================
// AGENTESE Response Type
// =============================================================================

interface AgenteseResponse<T> {
  path: string;
  aspect: string;
  result: T;
  error?: string;
}

/**
 * Unwrap AGENTESE gateway response.
 */
function unwrapResponse<T>(response: { data: AgenteseResponse<T> }): T {
  if (!response.data) {
    throw new AgenteseError('Missing response data', 'unknown');
  }

  if (response.data.error) {
    throw new AgenteseError(response.data.error, response.data.path, response.data.aspect);
  }

  const result = response.data.result;

  // Handle BasicRendering-style responses (Crown Jewels pattern)
  if (
    result &&
    typeof result === 'object' &&
    'metadata' in result &&
    'summary' in result &&
    'content' in result
  ) {
    const metadata = (result as { metadata: unknown }).metadata;
    if (metadata && typeof metadata === 'object' && !('error' in metadata && Object.keys(metadata as object).length === 1)) {
      return metadata as T;
    }
  }

  return result;
}

// =============================================================================
// Constants
// =============================================================================

/** Minimum time between fetches (debounce) */
const FETCH_DEBOUNCE_MS = 200;

// =============================================================================
// Component
// =============================================================================

/**
 * PathProjection - Generic AGENTESE path to projection wrapper.
 *
 * This is the foundation of projection-first pages. It:
 * 1. Invokes an AGENTESE path via the gateway
 * 2. Handles loading/error states with personality
 * 3. Provides density and observer context to children
 * 4. Collects traces for devex visibility
 *
 * Target: Pages using PathProjection should be < 50 LOC.
 */
export function PathProjection<T = unknown>({
  path,
  aspect = 'manifest',
  body,
  children,
  jewel,
  loadingAction,
  loadingComponent,
  errorComponent,
  skipInitialFetch = false,
  pollInterval = 0,
  className,
  style,
  onSuccess,
  onError,
}: PathProjectionProps<T>) {
  const { density, observer, isMobile, isTablet, isDesktop } = useShell();
  const tracedInvoke = useTracedInvoke();

  // State
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!skipInitialFetch);
  const [error, setError] = useState<Error | null>(null);
  const [streaming] = useState(false); // Future: streaming support

  // ---------------------------------------------------------------------------
  // Fix 2: Stable body reference via JSON serialization
  // Prevents infinite re-fetch when body prop is an inline object literal
  // ---------------------------------------------------------------------------
  const bodyJson = useMemo(() => JSON.stringify(body ?? null), [body]);

  // ---------------------------------------------------------------------------
  // Fix 3: Debounce to prevent rapid-fire fetches
  // ---------------------------------------------------------------------------
  const lastFetchRef = useRef<number>(0);
  const isFetchingRef = useRef<boolean>(false);

  // Infer jewel from path if not provided
  const effectiveJewel = jewel ?? inferJewel(path);

  // Fetch function - now includes bodyJson in deps for proper reactivity
  const fetchData = useCallback(async () => {
    // Debounce: skip if too recent (unless it's the first fetch)
    const now = Date.now();
    if (lastFetchRef.current > 0 && now - lastFetchRef.current < FETCH_DEBOUNCE_MS) {
      return;
    }

    // Prevent concurrent fetches
    if (isFetchingRef.current) {
      return;
    }

    lastFetchRef.current = now;
    isFetchingRef.current = true;
    setLoading(true);
    setError(null);

    try {
      const route = pathToRoute(path, aspect);
      // Parse body from bodyJson to ensure we use the current value
      const currentBody = bodyJson ? JSON.parse(bodyJson) : undefined;
      const isGet = aspect === 'manifest' && !currentBody;

      const result = await tracedInvoke(path, aspect, async () => {
        if (isGet) {
          const response = await apiClient.get<AgenteseResponse<unknown>>(route);
          return unwrapResponse(response);
        } else {
          const response = await apiClient.post<AgenteseResponse<unknown>>(route, currentBody ?? {});
          return unwrapResponse(response);
        }
      });

      setData(result as T);
      onSuccess?.(result as T);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      onError?.(error);
    } finally {
      setLoading(false);
      isFetchingRef.current = false;
    }
  }, [path, aspect, bodyJson, tracedInvoke, onSuccess, onError]);

  // Fetch effect - runs on mount and when path/aspect/body changes
  // The debounce guard inside fetchData prevents rapid-fire requests
  const hasInitialFetched = useRef(false);
  useEffect(() => {
    if (skipInitialFetch) return;

    // Track if this is initial mount vs param change
    const isInitial = !hasInitialFetched.current;
    if (isInitial) {
      hasInitialFetched.current = true;
    }

    fetchData();
  }, [fetchData, skipInitialFetch]);

  // Polling
  useEffect(() => {
    if (pollInterval <= 0) return;

    const interval = setInterval(fetchData, pollInterval);
    return () => clearInterval(interval);
  }, [fetchData, pollInterval]);

  // Projection context
  const context: ProjectionContext = useMemo(
    () => ({
      density,
      observer,
      loading,
      error,
      refetch: fetchData,
      streaming,
      path,
      aspect,
      isMobile,
      isTablet,
      isDesktop,
    }),
    [density, observer, loading, error, fetchData, streaming, path, aspect, isMobile, isTablet, isDesktop]
  );

  // Loading state
  if (loading && !data) {
    if (loadingComponent) {
      return <>{loadingComponent}</>;
    }

    return (
      <div className={`flex items-center justify-center min-h-[200px] ${className ?? ''}`} style={style}>
        <PersonalityLoading
          jewel={effectiveJewel ?? 'brain'}
          action={loadingAction}
          size="md"
        />
      </div>
    );
  }

  // Error state
  if (error && !data) {
    if (errorComponent) {
      return <>{errorComponent}</>;
    }

    const errorType = getErrorType(error);

    return (
      <div className={`flex items-center justify-center min-h-[200px] ${className ?? ''}`} style={style}>
        <EmpathyError
          type={errorType}
          details={error.message}
          action="Try Again"
          onAction={fetchData}
        />
      </div>
    );
  }

  // Render children with data and context
  // At this point, data is guaranteed to be non-null (checked in error/loading states above)
  return (
    <div className={className} style={style}>
      {children(data as T, context)}
    </div>
  );
}

// =============================================================================
// Convenience Variants
// =============================================================================

/**
 * PathProjection with automatic polling.
 */
export function LivePathProjection(
  props: Omit<PathProjectionProps, 'pollInterval'> & { interval?: number }
) {
  const { interval = 5000, ...rest } = props;
  return <PathProjection {...rest} pollInterval={interval} />;
}

/**
 * PathProjection that skips initial fetch (for manual triggering).
 */
export function LazyPathProjection(props: PathProjectionProps) {
  return <PathProjection {...props} skipInitialFetch />;
}

export default PathProjection;
