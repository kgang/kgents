/**
 * ASHC Self-Awareness API Client
 *
 * Frontend client for the ASHC Self-Awareness service.
 *
 * Philosophy:
 *   "The compiler that knows itself is the compiler that trusts itself."
 *
 * The five APIs correspond to fundamental questions:
 *   - am_i_grounded: "Do I derive from axioms?"
 *   - what_principle_justifies: "Why is this action valid?"
 *   - verify_self_consistency: "Is the system coherent?"
 *   - get_derivation_ancestors: "Where do I come from?"
 *   - get_downstream_impact: "What depends on me?"
 *
 * @see services/zero_seed/ashc_self_awareness.py
 */

import type {
  GroundingResult,
  JustificationResult,
  ConsistencyReport,
  ConstitutionalKBlock,
  EvidenceTier,
} from '../components/constitutional/graphTypes';
import { getEvidenceTier } from '../components/constitutional/graphTypes';

// =============================================================================
// API Base
// =============================================================================

const API_BASE = '/api/ashc';

// =============================================================================
// Request Cache
// =============================================================================

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const cache = new Map<string, CacheEntry<unknown>>();
const CACHE_TTL_MS = 10000; // 10 second TTL

function getCached<T>(key: string): T | null {
  const entry = cache.get(key);
  if (!entry) return null;

  if (Date.now() - entry.timestamp > CACHE_TTL_MS) {
    cache.delete(key);
    return null;
  }

  return entry.data as T;
}

function setCache<T>(key: string, data: T): void {
  cache.set(key, { data, timestamp: Date.now() });

  // Limit cache size
  if (cache.size > 50) {
    const now = Date.now();
    for (const [k, v] of cache.entries()) {
      if (now - v.timestamp > CACHE_TTL_MS) {
        cache.delete(k);
      }
    }
  }
}

// In-flight deduplication
const inFlight = new Map<string, Promise<unknown>>();

// =============================================================================
// Fetch Helper
// =============================================================================

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`ASHC API error: ${response.status} - ${error}`);
  }

  return response.json();
}

// =============================================================================
// Raw API Response Types (snake_case from Python)
// =============================================================================

interface RawGroundingResult {
  is_grounded: boolean;
  derivation_path: string[];
  loss_at_each_step: number[];
  evidence_tier: string;
  total_loss: number;
}

interface RawJustificationResult {
  principle: string;
  loss_score: number;
  reasoning: string;
  derivation_chain: string[];
  evidence_tier: string;
}

interface RawConsistencyViolation {
  kind: string;
  block_id: string;
  description: string;
  related_blocks: string[];
}

interface RawConsistencyReport {
  is_consistent: boolean;
  violations: RawConsistencyViolation[];
  circular_dependencies: [string, string][];
  orphan_blocks: string[];
  total_blocks: number;
  grounded_blocks: number;
}

interface RawGenesisKBlock {
  id: string;
  title: string;
  layer: number;
  galois_loss: number;
  content: string;
  derives_from: string[];
  tags: string[];
}

// =============================================================================
// Response Transformers
// =============================================================================

function transformGroundingResult(raw: RawGroundingResult): GroundingResult {
  return {
    isGrounded: raw.is_grounded,
    derivationPath: raw.derivation_path,
    lossAtEachStep: raw.loss_at_each_step,
    evidenceTier: raw.evidence_tier as EvidenceTier,
    totalLoss: raw.total_loss,
  };
}

function transformJustificationResult(raw: RawJustificationResult): JustificationResult {
  return {
    principle: raw.principle,
    lossScore: raw.loss_score,
    reasoning: raw.reasoning,
    derivationChain: raw.derivation_chain,
    evidenceTier: raw.evidence_tier as EvidenceTier,
  };
}

function transformConsistencyReport(raw: RawConsistencyReport): ConsistencyReport {
  return {
    isConsistent: raw.is_consistent,
    violations: raw.violations.map((v) => ({
      kind: v.kind as 'circular' | 'orphan' | 'layer_violation' | 'missing_parent',
      blockId: v.block_id,
      description: v.description,
      relatedBlocks: v.related_blocks,
    })),
    circularDependencies: raw.circular_dependencies,
    orphanBlocks: raw.orphan_blocks,
    totalBlocks: raw.total_blocks,
    groundedBlocks: raw.grounded_blocks,
    consistencyScore: raw.total_blocks > 0 ? raw.grounded_blocks / raw.total_blocks : 1.0,
  };
}

function transformGenesisKBlock(raw: RawGenesisKBlock): ConstitutionalKBlock {
  return {
    id: raw.id,
    title: raw.title,
    layer: raw.layer as 0 | 1 | 2 | 3,
    galoisLoss: raw.galois_loss,
    evidenceTier: getEvidenceTier(raw.galois_loss),
    derivesFrom: raw.derives_from,
    dependents: [], // Will be computed from edges
    tags: raw.tags,
    content: raw.content,
  };
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Check if a block is grounded in L0 axioms.
 *
 * GO-016: Returns bool + derivation path showing how this block
 * derives from Constitutional axioms.
 *
 * @param blockId - The K-Block ID to check (e.g., "COMPOSABLE", "ASHC")
 * @returns GroundingResult with derivation path and loss information
 */
export async function amIGrounded(blockId: string): Promise<GroundingResult> {
  const cacheKey = `grounded:${blockId}`;

  const cached = getCached<GroundingResult>(cacheKey);
  if (cached) return cached;

  const existing = inFlight.get(cacheKey);
  if (existing) return existing as Promise<GroundingResult>;

  const promise = fetchJson<RawGroundingResult>(
    `${API_BASE}/grounded/${encodeURIComponent(blockId)}`
  )
    .then((raw) => {
      const result = transformGroundingResult(raw);
      setCache(cacheKey, result);
      return result;
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, promise);
  return promise;
}

/**
 * Find which Constitutional principle justifies an action.
 *
 * GO-017: Returns the principle that best grounds the given action,
 * along with Galois loss measuring alignment quality.
 *
 * @param action - Description of the action to justify
 * @returns JustificationResult with principle and reasoning
 */
export async function whatPrincipleJustifies(action: string): Promise<JustificationResult> {
  const cacheKey = `justify:${action}`;

  const cached = getCached<JustificationResult>(cacheKey);
  if (cached) return cached;

  const result = await fetchJson<RawJustificationResult>(`${API_BASE}/justify`, {
    method: 'POST',
    body: JSON.stringify({ action }),
  });

  const transformed = transformJustificationResult(result);
  setCache(cacheKey, transformed);
  return transformed;
}

/**
 * Verify the consistency of the derivation graph.
 *
 * GO-018: Checks that the Constitutional structure is internally coherent.
 *
 * @returns ConsistencyReport with violations and statistics
 */
export async function verifySelfConsistency(): Promise<ConsistencyReport> {
  const cacheKey = 'consistency';

  const cached = getCached<ConsistencyReport>(cacheKey);
  if (cached) return cached;

  const existing = inFlight.get(cacheKey);
  if (existing) return existing as Promise<ConsistencyReport>;

  const promise = fetchJson<RawConsistencyReport>(`${API_BASE}/consistency`)
    .then((raw) => {
      const result = transformConsistencyReport(raw);
      setCache(cacheKey, result);
      return result;
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, promise);
  return promise;
}

/**
 * Get the full lineage of a block back to L0 axioms.
 *
 * GO-019: Returns all ancestors in derivation order.
 *
 * @param blockId - The K-Block ID to trace
 * @returns List of ancestor block IDs (this block first, axioms last)
 */
export async function getDerivationAncestors(blockId: string): Promise<string[]> {
  const cacheKey = `ancestors:${blockId}`;

  const cached = getCached<string[]>(cacheKey);
  if (cached) return cached;

  const result = await fetchJson<{ ancestors: string[] }>(
    `${API_BASE}/ancestors/${encodeURIComponent(blockId)}`
  );

  setCache(cacheKey, result.ancestors);
  return result.ancestors;
}

/**
 * Get all blocks that depend on (derive from) this block.
 *
 * GO-020: Returns all descendants that would be affected if this block were modified.
 *
 * @param blockId - The K-Block ID to trace forward
 * @returns List of dependent block IDs
 */
export async function getDownstreamImpact(blockId: string): Promise<string[]> {
  const cacheKey = `downstream:${blockId}`;

  const cached = getCached<string[]>(cacheKey);
  if (cached) return cached;

  const result = await fetchJson<{ dependents: string[] }>(
    `${API_BASE}/downstream/${encodeURIComponent(blockId)}`
  );

  setCache(cacheKey, result.dependents);
  return result.dependents;
}

/**
 * Get all genesis K-Blocks from the backend.
 *
 * @returns Array of all Constitutional K-Blocks
 */
export async function getAllGenesisBlocks(): Promise<ConstitutionalKBlock[]> {
  const cacheKey = 'genesis-blocks';

  const cached = getCached<ConstitutionalKBlock[]>(cacheKey);
  if (cached) return cached;

  const existing = inFlight.get(cacheKey);
  if (existing) return existing as Promise<ConstitutionalKBlock[]>;

  const promise = fetchJson<{ blocks: RawGenesisKBlock[] }>(`${API_BASE}/blocks`)
    .then((raw) => {
      const blocks = raw.blocks.map(transformGenesisKBlock);
      setCache(cacheKey, blocks);
      return blocks;
    })
    .finally(() => {
      inFlight.delete(cacheKey);
    });

  inFlight.set(cacheKey, promise);
  return promise;
}

/**
 * Get detailed explanation of why a block exists.
 *
 * High-level query combining multiple APIs for a human-readable explanation.
 *
 * @param blockId - The K-Block ID to explain
 * @returns Markdown-formatted explanation
 */
export async function whyDoesThisExist(blockId: string): Promise<string> {
  const result = await fetchJson<{ explanation: string }>(
    `${API_BASE}/why/${encodeURIComponent(blockId)}`
  );
  return result.explanation;
}

// =============================================================================
// Cache Management
// =============================================================================

/**
 * Clear all cached data.
 * Useful after mutations or when forcing a refresh.
 */
export function clearCache(): void {
  cache.clear();
}

/**
 * Clear cache for a specific block.
 */
export function invalidateBlock(blockId: string): void {
  cache.delete(`grounded:${blockId}`);
  cache.delete(`ancestors:${blockId}`);
  cache.delete(`downstream:${blockId}`);
  cache.delete('consistency');
  cache.delete('genesis-blocks');
}
