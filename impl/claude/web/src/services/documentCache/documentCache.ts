/**
 * Document Cache Service
 *
 * Two-tier caching system combining memory (fast) and IndexedDB (persistent).
 *
 * Lookup strategy:
 * 1. Check memory cache (instant)
 * 2. Check IndexedDB cache (~5ms)
 * 3. Promote IndexedDB hits to memory
 *
 * This is the main API for the document proxy system.
 */

import type { CachedDocument, CacheStats } from './types';
import { MemoryCache } from './memoryCache';
import { IndexedDBCache } from './indexedDBCache';

/**
 * Two-tier document cache with memory and persistent layers.
 *
 * Usage:
 * ```typescript
 * const cache = new DocumentCache();
 *
 * // Try to get cached document
 * const cached = await cache.get(path, contentHash);
 * if (cached) {
 *   // Use cached SceneGraph
 *   render(cached.sceneGraph);
 * } else {
 *   // Parse and cache
 *   const parsed = await parseDocument(content);
 *   await cache.set(path, parsed);
 * }
 * ```
 */
export class DocumentCache {
  private memoryCache: MemoryCache;
  private indexedDBCache: IndexedDBCache;

  // Stats tracking
  private stats = {
    memoryHits: 0,
    memoryMisses: 0,
    indexedDBHits: 0,
    indexedDBMisses: 0,
    totalParses: 0,
  };

  constructor() {
    this.memoryCache = new MemoryCache(50); // Max 50 docs in memory
    this.indexedDBCache = new IndexedDBCache();

    // Schedule periodic cleanup
    this.scheduleCleanup();
  }

  /**
   * Get a cached document if it exists and is valid.
   *
   * Lookup order:
   * 1. Memory cache (instant)
   * 2. IndexedDB cache (async)
   * 3. Promote IndexedDB hits to memory
   *
   * @param path - Document path
   * @param contentHash - Expected content hash
   * @returns Promise resolving to cached document or null
   */
  async get(path: string, contentHash: string): Promise<CachedDocument | null> {
    // Try memory cache first
    const memoryHit = this.memoryCache.get(path, contentHash);
    if (memoryHit) {
      this.stats.memoryHits++;
      console.debug(`[DocumentCache] Memory hit: ${path}`);
      return memoryHit;
    }

    this.stats.memoryMisses++;

    // Try IndexedDB cache
    const indexedDBHit = await this.indexedDBCache.get(path, contentHash);
    if (indexedDBHit) {
      this.stats.indexedDBHits++;
      console.debug(`[DocumentCache] IndexedDB hit: ${path}`);

      // Promote to memory cache
      this.memoryCache.set(path, indexedDBHit);

      return indexedDBHit;
    }

    this.stats.indexedDBMisses++;
    console.debug(`[DocumentCache] Cache miss: ${path}`);

    return null;
  }

  /**
   * Store a document in both cache layers.
   *
   * @param path - Document path
   * @param doc - Cached document
   */
  async set(path: string, doc: CachedDocument): Promise<void> {
    console.debug(`[DocumentCache] Caching: ${path} (hash: ${doc.contentHash})`);

    // Store in memory cache (sync)
    this.memoryCache.set(path, doc);

    // Store in IndexedDB cache (async)
    try {
      await this.indexedDBCache.set(path, doc);
    } catch (error) {
      console.error('[DocumentCache] IndexedDB set failed:', error);
      // Continue even if IndexedDB fails (memory cache still works)
    }
  }

  /**
   * Invalidate all cached versions of a document.
   *
   * Removes from both memory and IndexedDB.
   *
   * @param path - Document path to invalidate
   */
  async invalidate(path: string): Promise<void> {
    console.debug(`[DocumentCache] Invalidating: ${path}`);

    // Invalidate in memory cache
    this.memoryCache.invalidate(path);

    // Invalidate in IndexedDB cache
    try {
      await this.indexedDBCache.invalidate(path);
    } catch (error) {
      console.error('[DocumentCache] IndexedDB invalidate failed:', error);
    }
  }

  /**
   * Clear all cached documents from both layers.
   */
  async clear(): Promise<void> {
    console.debug('[DocumentCache] Clearing all caches');

    this.memoryCache.clear();

    try {
      await this.indexedDBCache.clear();
    } catch (error) {
      console.error('[DocumentCache] IndexedDB clear failed:', error);
    }

    // Reset stats
    this.stats = {
      memoryHits: 0,
      memoryMisses: 0,
      indexedDBHits: 0,
      indexedDBMisses: 0,
      totalParses: 0,
    };
  }

  /**
   * Get cache performance statistics.
   *
   * @returns Current cache stats
   */
  async getStats(): Promise<CacheStats> {
    const indexedDBSize = await this.indexedDBCache.size();

    return {
      memoryHits: this.stats.memoryHits,
      memoryMisses: this.stats.memoryMisses,
      indexedDBHits: this.stats.indexedDBHits,
      indexedDBMisses: this.stats.indexedDBMisses,
      totalParses: this.stats.totalParses,
      memorySize: this.memoryCache.size(),
      indexedDBSize,
    };
  }

  /**
   * Record a parse operation (for stats tracking).
   */
  recordParse(): void {
    this.stats.totalParses++;
  }

  /**
   * Schedule periodic cleanup of expired entries.
   */
  private scheduleCleanup(): void {
    // Run cleanup every hour
    const cleanupInterval = 60 * 60 * 1000;

    setInterval(() => {
      this.cleanup().catch((error) => {
        console.error('[DocumentCache] Cleanup failed:', error);
      });
    }, cleanupInterval);

    // Run initial cleanup after 5 minutes
    setTimeout(() => {
      this.cleanup().catch((error) => {
        console.error('[DocumentCache] Initial cleanup failed:', error);
      });
    }, 5 * 60 * 1000);
  }

  /**
   * Clean up expired documents from IndexedDB.
   *
   * Removes documents older than 24 hours past their TTL.
   */
  private async cleanup(): Promise<void> {
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours
    const removed = await this.indexedDBCache.cleanup(maxAge);

    if (removed > 0) {
      console.debug(`[DocumentCache] Cleanup removed ${removed} expired documents`);
    }
  }
}

/**
 * Singleton instance for global use.
 */
export const documentCache = new DocumentCache();
