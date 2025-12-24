/**
 * Document Cache Service
 *
 * Two-tier caching system for parsed documents.
 *
 * Features:
 * - Memory cache (LRU, 50 docs, instant access)
 * - IndexedDB cache (persistent, ~5ms access)
 * - Content hash validation
 * - TTL expiration
 * - Cache promotion (IndexedDB → memory)
 *
 * Usage:
 * ```typescript
 * import { documentCache } from './services/documentCache';
 *
 * // Try cache
 * const cached = await documentCache.get(path, contentHash);
 * if (cached) {
 *   return cached.sceneGraph;
 * }
 *
 * // Parse and cache
 * const parsed = await parseDocument(content);
 * await documentCache.set(path, {
 *   path,
 *   contentHash,
 *   sceneGraph: parsed,
 *   tokenCount: parsed.nodes.length,
 *   tokenTypes: {},
 *   cachedAt: Date.now(),
 *   ttlMs: 24 * 60 * 60 * 1000, // 24 hours
 *   parserVersion: '1.0.0',
 * });
 * ```
 */

export { DocumentCache, documentCache } from './documentCache';
export { MemoryCache } from './memoryCache';
export { IndexedDBCache } from './indexedDBCache';
export { hashContent, hashSection } from './hashUtils';
export type {
  CachedDocument,
  CacheStats,
  SectionBoundary,
  SectionType,
} from './types';
