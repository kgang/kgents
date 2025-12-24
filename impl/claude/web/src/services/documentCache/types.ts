/**
 * DocumentCache Type Definitions
 *
 * Types for the document proxy caching system.
 */

import type { SceneGraph } from '../../components/tokens/types';

/**
 * A cached parsed document with metadata for validation and incremental updates.
 */
export interface CachedDocument {
  /** Document path (used as primary key) */
  path: string;

  /** SHA-256 hash of content (first 16 chars) */
  contentHash: string;

  /** Parsed scene graph */
  sceneGraph: SceneGraph;

  /** Total token count */
  tokenCount: number;

  /** Token type distribution */
  tokenTypes: Record<string, number>;

  /** Timestamp when cached (ms since epoch) */
  cachedAt: number;

  /** Time-to-live in milliseconds */
  ttlMs: number;

  /** Parser version for cache invalidation */
  parserVersion: string;

  /** Section metadata for incremental parsing */
  sections?: SectionBoundary[];

  /** Section hash map for change detection */
  sectionHashes?: Record<number, string>;
}

/**
 * Section boundary information for incremental parsing.
 */
export interface SectionBoundary {
  /** Section index */
  index: number;

  /** Start byte offset */
  startOffset: number;

  /** End byte offset */
  endOffset: number;

  /** Content hash of this section */
  hash: string;

  /** Section type */
  type: SectionType;
}

/**
 * Section type discriminator.
 */
export type SectionType =
  | { kind: 'heading'; level: 1 | 2 | 3 | 4 | 5 | 6 }
  | { kind: 'paragraph' }
  | { kind: 'code_block'; language: string }
  | { kind: 'list' }
  | { kind: 'table' }
  | { kind: 'blockquote' }
  | { kind: 'horizontal_rule' }
  | { kind: 'frontmatter' };

/**
 * Cache performance statistics.
 */
export interface CacheStats {
  /** Memory cache hits */
  memoryHits: number;

  /** Memory cache misses */
  memoryMisses: number;

  /** IndexedDB cache hits */
  indexedDBHits: number;

  /** IndexedDB cache misses */
  indexedDBMisses: number;

  /** Total parse operations performed */
  totalParses: number;

  /** Total documents in memory cache */
  memorySize: number;

  /** Total documents in IndexedDB cache */
  indexedDBSize: number;
}
