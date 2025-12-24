/**
 * useDocumentProxy — Cache-first document rendering with incremental updates.
 *
 * Implements the Document Proxy system (AD-015) for:
 * - Instant loading via two-tier cache (Memory + IndexedDB)
 * - No screen violence (graceful fallback and pull-to-update)
 * - Section-aware incremental updates
 *
 * State Machine:
 *   idle → loading → cached | parsing → stale → (pull) → cached
 *
 * Principles:
 * - "Watertight Bulkheads": Sections partition the document
 * - "Newspaper on Doorstep": Cached before you ask
 * - "Gentle Pull": Changes suggested, not forced
 *
 * @see spec/protocols/document-proxy.md
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { documentCache } from '../services/documentCache';
import { hashContent } from '../services/documentCache/hashUtils';
import { documentApi, DocumentParseResponse, ParsedSection } from '../api/client';
import type { SceneGraph, SceneNode } from '../components/tokens/types';
import type { CachedDocument, SectionBoundary } from '../services/documentCache/types';

// =============================================================================
// Types
// =============================================================================

/** Current parser version - bump when parse output format changes */
const PARSER_VERSION = '1.0.0';

/** Default TTL for cached documents (24 hours) */
const DEFAULT_TTL_MS = 24 * 60 * 60 * 1000;

/** Document proxy state machine status */
export type DocumentProxyStatus =
  | 'idle' // No document loaded
  | 'loading' // Checking cache
  | 'cached' // Using cached version
  | 'parsing' // Parsing in background
  | 'stale' // Newer version available
  | 'error'; // Parse failed

export interface UseDocumentProxyOptions {
  /** Document path (used as cache key) */
  path: string;
  /** Document content */
  content: string;
  /** Current mode - skip rendering in INSERT mode */
  mode: 'NORMAL' | 'INSERT';
  /** Layout mode for rendering */
  layoutMode?: 'COMPACT' | 'COMFORTABLE' | 'SPACIOUS';
  /** Called when navigating to AGENTESE path */
  onNavigate?: (path: string) => void;
}

export interface UseDocumentProxyReturn {
  // === Rendering ===
  /** SceneGraph to render (cached or fresh) */
  sceneGraph: SceneGraph | null;
  /** Render mode: 'interactive' (parsed) or 'raw' (fallback) */
  renderMode: 'interactive' | 'raw';

  // === Status ===
  /** Current state machine status */
  status: DocumentProxyStatus;
  /** True during initial load or background parse */
  isLoading: boolean;
  /** True if a newer parsed version is available */
  hasPendingUpdate: boolean;
  /** Error message if parsing failed */
  error: string | null;
  /** True if current render is from cache hit */
  cacheHit: boolean;

  // === Actions ===
  /** Apply pending update (pull-to-refresh) */
  pullUpdate: () => void;
  /** Force re-parse (invalidate cache) */
  forceReparse: () => void;

  // === Stats ===
  /** Parse time in ms (0 if cached) */
  parseTimeMs: number;
  /** Token count in current SceneGraph */
  tokenCount: number;
  /** Section count for incremental updates */
  sectionCount: number;
}

// =============================================================================
// Implementation
// =============================================================================

/**
 * Document Proxy hook for cache-first rendering.
 *
 * Usage:
 * ```tsx
 * function ContentPane({ path, content, mode }) {
 *   const {
 *     sceneGraph,
 *     renderMode,
 *     status,
 *     hasPendingUpdate,
 *     pullUpdate,
 *   } = useDocumentProxy({ path, content, mode });
 *
 *   if (mode === 'INSERT') {
 *     return <MarkdownEditor value={content} />;
 *   }
 *
 *   return (
 *     <div>
 *       {hasPendingUpdate && (
 *         <button onClick={pullUpdate}>Update available</button>
 *       )}
 *       {renderMode === 'interactive' ? (
 *         <InteractiveDocument sceneGraph={sceneGraph} />
 *       ) : (
 *         <pre>{content}</pre>
 *       )}
 *     </div>
 *   );
 * }
 * ```
 */
export function useDocumentProxy(options: UseDocumentProxyOptions): UseDocumentProxyReturn {
  const { path, content, mode, layoutMode = 'COMFORTABLE' } = options;

  // === State ===
  const [status, setStatus] = useState<DocumentProxyStatus>('idle');
  const [sceneGraph, setSceneGraph] = useState<SceneGraph | null>(null);
  const [pendingSceneGraph, setPendingSceneGraph] = useState<SceneGraph | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cacheHit, setCacheHit] = useState(false);
  const [parseTimeMs, setParseTimeMs] = useState(0);
  const [sections, setSections] = useState<SectionBoundary[]>([]);
  // Section hashes reserved for Phase 5 incremental parse
  const [_sectionHashes, setSectionHashes] = useState<Record<number, string>>({});

  // === Refs ===
  const contentHashRef = useRef<string>('');
  const abortControllerRef = useRef<AbortController | null>(null);
  const lastParseContentRef = useRef<string>('');

  // === Computed ===
  const isLoading = status === 'loading' || status === 'parsing';
  const hasPendingUpdate = status === 'stale' && pendingSceneGraph !== null;
  const renderMode = sceneGraph !== null ? 'interactive' : 'raw';
  const tokenCount = sceneGraph?.nodes?.length ?? 0;
  const sectionCount = sections.length;

  /**
   * Parse document content and cache result.
   */
  const parseAndCache = useCallback(
    async (contentToHash: string, contentHashValue: string) => {
      const startTime = performance.now();

      try {
        // Parse via API
        const response: DocumentParseResponse = await documentApi.parse(
          contentToHash,
          layoutMode
        );

        const endTime = performance.now();
        setParseTimeMs(Math.round(endTime - startTime));

        // Build cached document
        const cachedDoc: CachedDocument = {
          path,
          contentHash: contentHashValue,
          sceneGraph: response.scene_graph as SceneGraph,
          tokenCount: response.token_count,
          tokenTypes: {}, // TODO: Extract from SceneGraph
          cachedAt: Date.now(),
          ttlMs: DEFAULT_TTL_MS,
          parserVersion: PARSER_VERSION,
          sections: response.sections?.map((s: ParsedSection) => ({
            index: s.index,
            startOffset: s.range_start,
            endOffset: s.range_end,
            hash: s.section_hash,
            type: s.section_type as SectionBoundary['type'],
          })),
          sectionHashes: response.section_hashes,
        };

        // Store in cache
        await documentCache.set(path, cachedDoc);
        documentCache.recordParse();

        // Update section state
        if (cachedDoc.sections) {
          setSections(cachedDoc.sections);
        }
        if (cachedDoc.sectionHashes) {
          setSectionHashes(cachedDoc.sectionHashes);
        }

        return cachedDoc;
      } catch (err) {
        console.error('[useDocumentProxy] Parse failed:', err);
        throw err;
      }
    },
    [path, layoutMode]
  );

  /**
   * Pull pending update (apply stale → cached transition).
   */
  const pullUpdate = useCallback(() => {
    if (pendingSceneGraph) {
      setSceneGraph(pendingSceneGraph);
      setPendingSceneGraph(null);
      setStatus('cached');
    }
  }, [pendingSceneGraph]);

  /**
   * Force re-parse by invalidating cache.
   */
  const forceReparse = useCallback(async () => {
    await documentCache.invalidate(path);
    contentHashRef.current = ''; // Force re-check
    lastParseContentRef.current = '';
    setStatus('loading');
  }, [path]);

  // === Main Effect: Cache-first load ===
  useEffect(() => {
    // Skip in INSERT mode
    if (mode === 'INSERT') {
      return;
    }

    // Skip if content is empty
    if (!content) {
      setStatus('idle');
      setSceneGraph(null);
      return;
    }

    // Skip if content hasn't changed since last parse
    if (content === lastParseContentRef.current && sceneGraph !== null) {
      return;
    }

    // Cancel any in-progress fetch
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    const loadDocument = async () => {
      setStatus('loading');
      setCacheHit(false);
      setError(null);

      try {
        // Compute content hash
        const contentHashValue = await hashContent(content);
        contentHashRef.current = contentHashValue;

        // Check cache
        const cached = await documentCache.get(path, contentHashValue);

        if (cached) {
          // Cache hit! Instant render.
          console.debug(`[useDocumentProxy] Cache hit: ${path}`);
          setSceneGraph(cached.sceneGraph);
          setCacheHit(true);
          setParseTimeMs(0);
          setStatus('cached');
          lastParseContentRef.current = content;

          // Restore section state
          if (cached.sections) {
            setSections(cached.sections);
          }
          if (cached.sectionHashes) {
            setSectionHashes(cached.sectionHashes);
          }

          return;
        }

        // Cache miss - need to parse
        console.debug(`[useDocumentProxy] Cache miss: ${path}`);

        // If we have an existing sceneGraph, show it while parsing
        if (sceneGraph !== null) {
          setStatus('parsing');
        }

        // Parse in background
        const cachedDoc = await parseAndCache(content, contentHashValue);

        // Check if content changed during parse
        if (content !== lastParseContentRef.current && sceneGraph !== null) {
          // Content changed - don't update, let next effect handle it
          return;
        }

        // Apply new sceneGraph
        if (sceneGraph !== null && status !== 'loading') {
          // Already showing a version - go to stale state
          setPendingSceneGraph(cachedDoc.sceneGraph);
          setStatus('stale');
        } else {
          // First load - apply directly
          setSceneGraph(cachedDoc.sceneGraph);
          setStatus('cached');
        }

        lastParseContentRef.current = content;
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          return; // Cancelled, ignore
        }

        console.error('[useDocumentProxy] Load failed:', err);
        setError(err instanceof Error ? err.message : 'Failed to load document');
        setStatus('error');
      }
    };

    void loadDocument();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [content, mode, path, parseAndCache, sceneGraph, status]);

  // === Clear state when mode changes to INSERT ===
  useEffect(() => {
    if (mode === 'INSERT') {
      // Cancel any in-progress operations
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      // Keep sceneGraph for when we return to NORMAL mode
      setPendingSceneGraph(null);
    }
  }, [mode]);

  // === Memoized return value ===
  return useMemo(
    () => ({
      // Rendering
      sceneGraph,
      renderMode,

      // Status
      status,
      isLoading,
      hasPendingUpdate,
      error,
      cacheHit,

      // Actions
      pullUpdate,
      forceReparse,

      // Stats
      parseTimeMs,
      tokenCount,
      sectionCount,
    }),
    [
      sceneGraph,
      renderMode,
      status,
      isLoading,
      hasPendingUpdate,
      error,
      cacheHit,
      pullUpdate,
      forceReparse,
      parseTimeMs,
      tokenCount,
      sectionCount,
    ]
  );
}

// =============================================================================
// Utilities
// =============================================================================

/**
 * Find nodes belonging to a specific section.
 *
 * Used for incremental updates to identify affected nodes.
 */
export function getNodesForSection(
  sceneGraph: SceneGraph,
  sectionIndex: number
): SceneNode[] {
  return sceneGraph.nodes.filter((node) => node.section_index === sectionIndex);
}

/**
 * Check if a section has changed between two documents.
 */
export function sectionChanged(
  oldHashes: Record<number, string>,
  newHashes: Record<number, string>,
  sectionIndex: number
): boolean {
  const oldHash = oldHashes[sectionIndex];
  const newHash = newHashes[sectionIndex];

  // If either is undefined, consider it changed
  if (oldHash === undefined || newHash === undefined) {
    return true;
  }

  return oldHash !== newHash;
}

/**
 * Get list of changed section indices.
 */
export function getChangedSections(
  oldHashes: Record<number, string>,
  newHashes: Record<number, string>
): number[] {
  const allIndices = new Set([
    ...Object.keys(oldHashes).map(Number),
    ...Object.keys(newHashes).map(Number),
  ]);

  return Array.from(allIndices).filter((index) =>
    sectionChanged(oldHashes, newHashes, index)
  );
}

export default useDocumentProxy;
