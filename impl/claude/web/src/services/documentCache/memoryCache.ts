/**
 * In-Memory LRU Cache
 *
 * Fast in-memory cache for parsed documents with LRU eviction.
 * Lost on page refresh but provides instant access for recent documents.
 */

import type { CachedDocument } from './types';

/**
 * LRU cache entry with access tracking.
 */
interface CacheEntry {
  doc: CachedDocument;
  lastAccessed: number;
}

/**
 * In-memory LRU cache for parsed documents.
 *
 * Features:
 * - Constant time get/set operations
 * - LRU eviction when max capacity reached
 * - TTL validation on retrieval
 * - Content hash validation
 */
export class MemoryCache {
  private cache: Map<string, CacheEntry>;
  private maxSize: number;

  /**
   * Create a new memory cache.
   *
   * @param maxSize - Maximum number of documents to cache (default: 50)
   */
  constructor(maxSize: number = 50) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  /**
   * Get a cached document if it exists and is valid.
   *
   * Validates:
   * - Path matches
   * - Content hash matches (cache key)
   * - Not expired (cachedAt + ttlMs > now)
   *
   * Updates LRU access time on hit.
   *
   * @param path - Document path
   * @param contentHash - Expected content hash
   * @returns Cached document or null if miss/invalid
   */
  get(path: string, contentHash: string): CachedDocument | null {
    const key = this.cacheKey(path, contentHash);
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    // Validate TTL
    const now = Date.now();
    if (now > entry.doc.cachedAt + entry.doc.ttlMs) {
      this.cache.delete(key);
      return null;
    }

    // Update LRU access time
    entry.lastAccessed = now;
    this.cache.set(key, entry);

    return entry.doc;
  }

  /**
   * Store a document in the cache.
   *
   * Evicts least recently used document if at capacity.
   *
   * @param path - Document path
   * @param doc - Cached document
   */
  set(path: string, doc: CachedDocument): void {
    const key = this.cacheKey(path, doc.contentHash);

    // Evict LRU if at capacity
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      this.evictLRU();
    }

    this.cache.set(key, {
      doc,
      lastAccessed: Date.now(),
    });
  }

  /**
   * Invalidate all cached versions of a document.
   *
   * Removes all entries with matching path regardless of hash.
   *
   * @param path - Document path to invalidate
   */
  invalidate(path: string): void {
    const keysToDelete: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (entry.doc.path === path) {
        keysToDelete.push(key);
      }
    }

    for (const key of keysToDelete) {
      this.cache.delete(key);
    }
  }

  /**
   * Clear all cached documents.
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get current cache size.
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Create a cache key from path and hash.
   */
  private cacheKey(path: string, contentHash: string): string {
    return `doc:${path}:${contentHash}`;
  }

  /**
   * Evict the least recently used entry.
   */
  private evictLRU(): void {
    let oldestKey: string | null = null;
    let oldestTime = Infinity;

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessed < oldestTime) {
        oldestTime = entry.lastAccessed;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }
}
