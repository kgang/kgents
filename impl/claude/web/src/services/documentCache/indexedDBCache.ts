/**
 * IndexedDB Persistent Cache
 *
 * Persistent cache layer using IndexedDB for document storage.
 * Survives page refresh and provides async access to cached documents.
 */

import type { CachedDocument } from './types';

const DB_NAME = 'kgents-document-cache';
const DB_VERSION = 1;
const STORE_NAME = 'documents';

/**
 * IndexedDB persistent cache for parsed documents.
 *
 * Features:
 * - Persistent storage across page refreshes
 * - Async API with Promise-based interface
 * - Graceful error handling with fallback
 * - TTL-based cleanup
 */
export class IndexedDBCache {
  private dbPromise: Promise<IDBDatabase | null>;

  constructor() {
    this.dbPromise = this.initDB();
  }

  /**
   * Initialize IndexedDB database.
   *
   * Creates object store with indexes for efficient queries.
   */
  private async initDB(): Promise<IDBDatabase | null> {
    if (!('indexedDB' in window)) {
      console.warn('[IndexedDBCache] IndexedDB not available');
      return null;
    }

    return new Promise((resolve) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => {
        console.error('[IndexedDBCache] Failed to open database:', request.error);
        resolve(null); // Graceful fallback
      };

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create object store if it doesn't exist
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const store = db.createObjectStore(STORE_NAME, { keyPath: 'path' });

          // Add indexes for queries
          store.createIndex('contentHash', 'contentHash', { unique: false });
          store.createIndex('cachedAt', 'cachedAt', { unique: false });
        }
      };
    });
  }

  /**
   * Get a cached document if it exists and is valid.
   *
   * Validates:
   * - Path matches
   * - Content hash matches
   * - Not expired (cachedAt + ttlMs > now)
   *
   * @param path - Document path
   * @param contentHash - Expected content hash
   * @returns Promise resolving to cached document or null
   */
  async get(path: string, contentHash: string): Promise<CachedDocument | null> {
    const db = await this.dbPromise;
    if (!db) return null;

    return new Promise((resolve) => {
      const transaction = db.transaction(STORE_NAME, 'readonly');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.get(path);

      request.onsuccess = () => {
        const doc = request.result as CachedDocument | undefined;

        if (!doc) {
          resolve(null);
          return;
        }

        // Validate content hash
        if (doc.contentHash !== contentHash) {
          resolve(null);
          return;
        }

        // Validate TTL
        const now = Date.now();
        if (now > doc.cachedAt + doc.ttlMs) {
          // Expired - clean up asynchronously
          this.invalidate(path).catch(() => {
            // Ignore cleanup errors
          });
          resolve(null);
          return;
        }

        resolve(doc);
      };

      request.onerror = () => {
        console.error('[IndexedDBCache] Get failed:', request.error);
        resolve(null);
      };
    });
  }

  /**
   * Store a document in the cache.
   *
   * @param _path - Document path (used as key, stored in doc)
   * @param doc - Cached document
   */
  async set(_path: string, doc: CachedDocument): Promise<void> {
    const db = await this.dbPromise;
    if (!db) return;

    return new Promise((resolve, reject) => {
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.put(doc);

      request.onsuccess = () => {
        resolve();
      };

      request.onerror = () => {
        console.error('[IndexedDBCache] Set failed:', request.error);
        reject(request.error);
      };
    });
  }

  /**
   * Invalidate all cached versions of a document.
   *
   * @param path - Document path to invalidate
   */
  async invalidate(path: string): Promise<void> {
    const db = await this.dbPromise;
    if (!db) return;

    return new Promise((resolve, reject) => {
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.delete(path);

      request.onsuccess = () => {
        resolve();
      };

      request.onerror = () => {
        console.error('[IndexedDBCache] Invalidate failed:', request.error);
        reject(request.error);
      };
    });
  }

  /**
   * Clean up expired documents.
   *
   * Removes documents where cachedAt + ttlMs < now - maxAge.
   *
   * @param maxAge - Maximum age in milliseconds (default: 24 hours)
   * @returns Promise resolving to number of documents removed
   */
  async cleanup(maxAge: number = 24 * 60 * 60 * 1000): Promise<number> {
    const db = await this.dbPromise;
    if (!db) return 0;

    return new Promise((resolve) => {
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const index = store.index('cachedAt');
      const now = Date.now();
      const cutoff = now - maxAge;

      let removedCount = 0;

      const request = index.openCursor();

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest<IDBCursorWithValue>).result;

        if (cursor) {
          const doc = cursor.value as CachedDocument;
          const expiresAt = doc.cachedAt + doc.ttlMs;

          if (expiresAt < cutoff) {
            cursor.delete();
            removedCount++;
          }

          cursor.continue();
        } else {
          // Done iterating
          resolve(removedCount);
        }
      };

      request.onerror = () => {
        console.error('[IndexedDBCache] Cleanup failed:', request.error);
        resolve(0);
      };
    });
  }

  /**
   * Get total number of cached documents.
   *
   * @returns Promise resolving to document count
   */
  async size(): Promise<number> {
    const db = await this.dbPromise;
    if (!db) return 0;

    return new Promise((resolve) => {
      const transaction = db.transaction(STORE_NAME, 'readonly');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.count();

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        console.error('[IndexedDBCache] Size query failed:', request.error);
        resolve(0);
      };
    });
  }

  /**
   * Clear all cached documents.
   */
  async clear(): Promise<void> {
    const db = await this.dbPromise;
    if (!db) return;

    return new Promise((resolve, reject) => {
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.clear();

      request.onsuccess = () => {
        resolve();
      };

      request.onerror = () => {
        console.error('[IndexedDBCache] Clear failed:', request.error);
        reject(request.error);
      };
    });
  }
}
