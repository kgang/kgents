/**
 * Projection Schema: TypeScript mirrors of Python projection types.
 *
 * These types mirror the Python schema in protocols/projection/schema.py
 * for consistent typing across the API boundary.
 *
 * @see protocols/projection/schema.py
 */

// =============================================================================
// Widget Status
// =============================================================================

/**
 * Universal widget lifecycle states.
 *
 * These states drive rendering decisions across all surfaces:
 * - idle: Initial state, no data loaded
 * - loading: Fetching data (show spinner)
 * - streaming: Receiving incremental data (show progress)
 * - done: Successfully completed (show content)
 * - error: Technical failure (show error panel with retry)
 * - refusal: Semantic refusal by agent (show refusal panel)
 * - stale: Cached data that may be outdated (show [CACHED] badge)
 */
export type WidgetStatus =
  | 'idle'
  | 'loading'
  | 'streaming'
  | 'done'
  | 'error'
  | 'refusal'
  | 'stale';

// =============================================================================
// Cache Metadata
// =============================================================================

/**
 * Cache and determinism metadata from AGENTESE v3 hints.
 */
export interface CacheMeta {
  /** Whether this response was served from cache */
  isCached: boolean;
  /** When the response was cached (ISO timestamp) */
  cachedAt: string | null;
  /** Time-to-live for cache entry in seconds */
  ttlSeconds: number | null;
  /** Unique key for this cached response */
  cacheKey: string | null;
  /** Whether the result is deterministic (same input → same output) */
  deterministic: boolean;
}

/**
 * Check if cache is stale based on TTL.
 */
export function isCacheStale(cache: CacheMeta | null): boolean {
  if (!cache?.isCached || !cache.cachedAt || !cache.ttlSeconds) {
    return false;
  }
  const elapsed = (Date.now() - new Date(cache.cachedAt).getTime()) / 1000;
  return elapsed > cache.ttlSeconds;
}

/**
 * Get cache age in seconds, or null if not cached.
 */
export function getCacheAge(cache: CacheMeta | null): number | null {
  if (!cache?.isCached || !cache.cachedAt) {
    return null;
  }
  return (Date.now() - new Date(cache.cachedAt).getTime()) / 1000;
}

// =============================================================================
// Error Information
// =============================================================================

/**
 * Error category for icon/styling selection.
 */
export type ErrorCategory =
  | 'network'
  | 'notFound'
  | 'permission'
  | 'timeout'
  | 'validation'
  | 'unknown';

/**
 * Structured error information for technical failures.
 *
 * This is distinct from RefusalInfo - errors are technical failures,
 * refusals are semantic decisions by the agent.
 */
export interface ErrorInfo {
  /** Type of error for icon/styling selection */
  category: ErrorCategory;
  /** Machine-readable error code (e.g., "ECONNREFUSED") */
  code: string;
  /** Human-readable error message */
  message: string;
  /** Suggested retry delay in seconds (for rate limiting) */
  retryAfterSeconds: number | null;
  /** Suggested fallback action (e.g., "use offline mode") */
  fallbackAction: string | null;
  /** OTEL trace ID for debugging */
  traceId: string | null;
}

/**
 * Get emoji for error category.
 */
export function getErrorEmoji(category: ErrorCategory): string {
  const emojis: Record<ErrorCategory, string> = {
    network: '📡',
    notFound: '🗺️',
    permission: '🔐',
    timeout: '⏰',
    validation: '⚠️',
    unknown: '🌀',
  };
  return emojis[category];
}

/**
 * Check if error is retryable.
 */
export function isErrorRetryable(error: ErrorInfo): boolean {
  return error.category === 'network' || error.category === 'timeout';
}

// =============================================================================
// Refusal Information
// =============================================================================

/**
 * Information about an agent refusal.
 *
 * Refusals are semantic decisions by the agent to not perform an action.
 * They are distinct from errors - the system worked correctly, but the
 * agent chose not to comply.
 */
export interface RefusalInfo {
  /** Human-readable explanation of why the action was refused */
  reason: string;
  /** What consent is needed to proceed (if any) */
  consentRequired: string | null;
  /** AGENTESE path for appealing the decision (e.g., "self.soul.appeal") */
  appealTo: string | null;
  /** Token/credit cost to override the refusal (if available) */
  overrideCost: number | null;
}

// =============================================================================
// Stream Metadata
// =============================================================================

/**
 * Metadata for streaming responses.
 *
 * Tracks progress of incremental data delivery.
 */
export interface StreamMeta {
  /** Expected total items/bytes (null if unknown) */
  totalExpected: number | null;
  /** Items/bytes received so far */
  received: number;
  /** When streaming started (ISO timestamp) */
  startedAt: string | null;
  /** When last chunk was received (ISO timestamp) */
  lastChunkAt: string | null;
}

/**
 * Get stream progress as 0.0-1.0, or -1 if indeterminate.
 */
export function getStreamProgress(stream: StreamMeta | null): number {
  if (!stream || stream.totalExpected === null || stream.totalExpected === 0) {
    return -1; // Indeterminate
  }
  return Math.min(1.0, stream.received / stream.totalExpected);
}

/**
 * Check if stream progress is indeterminate.
 */
export function isStreamIndeterminate(stream: StreamMeta | null): boolean {
  return !stream || stream.totalExpected === null;
}

// =============================================================================
// UI Hints
// =============================================================================

/**
 * AGENTESE v3 projection hint for widget type selection.
 */
export type UIHint = 'form' | 'stream' | 'table' | 'graph' | 'card' | 'text';

// =============================================================================
// Widget Metadata
// =============================================================================

/**
 * Universal metadata for all projected widgets.
 *
 * Captures status, cache info, errors, refusals, and streaming state.
 * This is the "chrome" around widget content.
 */
export interface WidgetMeta {
  /** Current lifecycle state */
  status: WidgetStatus;
  /** Cache/determinism metadata (if applicable) */
  cache: CacheMeta | null;
  /** Error information (if status === 'error') */
  error: ErrorInfo | null;
  /** Refusal information (if status === 'refusal') */
  refusal: RefusalInfo | null;
  /** Streaming metadata (if status === 'streaming') */
  stream: StreamMeta | null;
  /** AGENTESE v3 projection hint for widget type selection */
  uiHint: UIHint | null;
}

/**
 * Check if widget is in a loading state.
 */
export function isLoading(meta: WidgetMeta): boolean {
  return meta.status === 'loading' || meta.status === 'streaming';
}

/**
 * Check if response is from cache.
 */
export function isCached(meta: WidgetMeta): boolean {
  return meta.cache !== null && meta.cache.isCached;
}

/**
 * Check if [CACHED] badge should be shown.
 *
 * Shows badge when data is cached AND stale (past TTL).
 * Fresh cached data doesn't need a badge.
 */
export function showCachedBadge(meta: WidgetMeta): boolean {
  return isCached(meta) && isCacheStale(meta.cache);
}

/**
 * Check if there's an error to display.
 */
export function hasError(meta: WidgetMeta): boolean {
  return meta.status === 'error' && meta.error !== null;
}

/**
 * Check if there's a refusal to display.
 */
export function hasRefusal(meta: WidgetMeta): boolean {
  return meta.status === 'refusal' && meta.refusal !== null;
}

// Factory functions for common states
export const WidgetMetaFactory = {
  idle: (): WidgetMeta => ({
    status: 'idle',
    cache: null,
    error: null,
    refusal: null,
    stream: null,
    uiHint: null,
  }),

  loading: (): WidgetMeta => ({
    status: 'loading',
    cache: null,
    error: null,
    refusal: null,
    stream: null,
    uiHint: null,
  }),

  streaming: (stream?: StreamMeta | null): WidgetMeta => ({
    status: 'streaming',
    cache: null,
    error: null,
    refusal: null,
    stream: stream ?? null,
    uiHint: null,
  }),

  done: (cache?: CacheMeta | null): WidgetMeta => ({
    status: cache && isCacheStale(cache) ? 'stale' : 'done',
    cache: cache ?? null,
    error: null,
    refusal: null,
    stream: null,
    uiHint: null,
  }),

  withError: (error: ErrorInfo): WidgetMeta => ({
    status: 'error',
    cache: null,
    error,
    refusal: null,
    stream: null,
    uiHint: null,
  }),

  withRefusal: (refusal: RefusalInfo): WidgetMeta => ({
    status: 'refusal',
    cache: null,
    error: null,
    refusal,
    stream: null,
    uiHint: null,
  }),
};

// =============================================================================
// Widget Envelope
// =============================================================================

/**
 * Universal envelope wrapping any widget data with metadata.
 *
 * This is the standard format for all projections. It separates
 * the data (T) from the metadata (WidgetMeta), allowing surfaces
 * to render appropriate chrome (error panels, cache badges, etc.)
 * while the data renderer handles the actual content.
 */
export interface WidgetEnvelope<T = unknown> {
  /** The actual widget data/content */
  data: T;
  /** Metadata about status, cache, errors, etc. */
  meta: WidgetMeta;
  /** AGENTESE path that produced this (for debugging) */
  sourcePath: string | null;
  /** Who observed this (for debugging) */
  observerArchetype: string | null;
}

/**
 * Create a new envelope with updated meta.
 */
export function withMeta<T>(envelope: WidgetEnvelope<T>, meta: WidgetMeta): WidgetEnvelope<T> {
  return {
    ...envelope,
    meta,
  };
}

/**
 * Create a new envelope with updated status.
 */
export function withStatus<T>(
  envelope: WidgetEnvelope<T>,
  status: WidgetStatus
): WidgetEnvelope<T> {
  return {
    ...envelope,
    meta: {
      ...envelope.meta,
      status,
    },
  };
}

// =============================================================================
// Type Guards
// =============================================================================

/**
 * Type guard for checking if envelope has error.
 */
export function envelopeHasError<T>(
  envelope: WidgetEnvelope<T>
): envelope is WidgetEnvelope<T> & { meta: { error: ErrorInfo } } {
  return hasError(envelope.meta);
}

/**
 * Type guard for checking if envelope has refusal.
 */
export function envelopeHasRefusal<T>(
  envelope: WidgetEnvelope<T>
): envelope is WidgetEnvelope<T> & { meta: { refusal: RefusalInfo } } {
  return hasRefusal(envelope.meta);
}
