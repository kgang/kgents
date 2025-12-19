/**
 * useUmweltDiff - Compute what changes when observer shifts
 *
 * "The noun is a lie. There is only the rate of change."
 *
 * This hook computes the diff between two observer states,
 * determining which aspects become revealed, hidden, or unchanged.
 *
 * Umwelt v2 (2025-12-19): Registry-backed capability resolution with heuristic fallback.
 * The registry is truth; heuristics are graceful degradation.
 *
 * @see plans/umwelt-visualization.md
 * @see plans/umwelt-v2-expansion.md
 */

import { useMemo, useCallback } from 'react';
import type { Observer } from '../ObserverPicker';
import type { PathMetadata, AspectMetadataEntry } from '../useAgenteseDiscovery';
import type { AspectInfo, UmweltDiff } from './umwelt.types';

// =============================================================================
// Capability Checking (Umwelt v2: Registry-backed with heuristic fallback)
// =============================================================================

/**
 * Determines what capability (if any) is required for an aspect.
 *
 * Umwelt v2: Uses registry metadata when available, falls back to heuristics.
 * The registry is the SINGLE SOURCE OF TRUTH - heuristics are graceful degradation.
 *
 * @param aspect - The aspect name (e.g., "create", "manifest")
 * @param aspectMetadata - Optional metadata from registry with requiredCapability
 * @returns Required capability string or null (null = read capability)
 */
function getRequiredCapability(
  aspect: string,
  aspectMetadata?: AspectMetadataEntry
): string | null {
  // Priority 1: Registry truth (Umwelt v2)
  if (aspectMetadata?.requiredCapability !== undefined) {
    return aspectMetadata.requiredCapability;
  }

  // Priority 2: Heuristic fallback (graceful degradation)
  // These are the legacy rules - kept for paths without @aspect decorators

  // Mutations require write
  if (['create', 'update', 'delete'].some((m) => aspect.includes(m))) {
    return 'write';
  }

  // Admin aspects
  if (aspect.includes('admin') || aspect.includes('govern')) {
    return 'admin';
  }

  // Void aspects require void capability
  if (aspect.includes('sip') || aspect.includes('tithe') || aspect.includes('void')) {
    return 'void';
  }

  // Default: read
  return null; // null means 'read' (base capability everyone has)
}

/**
 * Checks if an observer has a required capability.
 */
function hasCapability(observer: Observer, capability: string | null): boolean {
  if (capability === null) {
    // Base read capability
    return observer.capabilities.includes('read');
  }

  // Write capability implies read
  if (capability === 'read') {
    return observer.capabilities.includes('read');
  }

  return observer.capabilities.includes(capability);
}

// =============================================================================
// Aspect Extraction (Umwelt v2: Registry-aware)
// =============================================================================

/**
 * Extract all aspects visible to an observer from metadata.
 *
 * Umwelt v2: Now uses per-aspect metadata from registry when available.
 * This provides:
 * - Accurate requiredCapability from @aspect decorator
 * - Contract awareness (hasContract = has schema)
 * - Streaming detection from metadata
 */
function getVisibleAspects(
  observer: Observer,
  metadata: Record<string, PathMetadata>
): AspectInfo[] {
  const result: AspectInfo[] = [];

  for (const [path, pathMeta] of Object.entries(metadata)) {
    const aspects = pathMeta.aspects || ['manifest'];
    const aspectMetadataMap = pathMeta.aspectMetadata || {};

    for (const aspect of aspects) {
      // Get per-aspect metadata if available (Umwelt v2)
      const aspectMeta = aspectMetadataMap[aspect];

      // Use registry-backed capability resolution with heuristic fallback
      const requiredCapability = getRequiredCapability(aspect, aspectMeta);

      if (hasCapability(observer, requiredCapability)) {
        result.push({
          aspect,
          path,
          requiredCapability,
          // Umwelt v2: Contract awareness from metadata
          hasContract: aspectMeta !== undefined,
          // Umwelt v2: Streaming from metadata or effects
          isStreaming: aspectMeta?.streaming ?? pathMeta.effects?.includes('streaming') ?? false,
        });
      }
    }
  }

  return result;
}

/**
 * Create a unique key for an aspect (path + aspect name).
 */
function aspectKey(info: AspectInfo): string {
  return `${info.path}:${info.aspect}`;
}

// =============================================================================
// Core Diff Algorithm
// =============================================================================

/**
 * Compute the diff between two observer states.
 *
 * @example
 * ```ts
 * const diff = computeUmweltDiff(guestObserver, developerObserver, metadata);
 * // diff.revealed contains aspects now visible to developer but not guest
 * // diff.hidden contains aspects visible to guest but not developer
 * // diff.unchanged contains aspects visible to both
 * ```
 */
export function computeUmweltDiff(
  prevObserver: Observer,
  nextObserver: Observer,
  metadata: Record<string, PathMetadata>
): UmweltDiff {
  const prevVisible = getVisibleAspects(prevObserver, metadata);
  const nextVisible = getVisibleAspects(nextObserver, metadata);

  const prevKeys = new Set(prevVisible.map(aspectKey));
  const nextKeys = new Set(nextVisible.map(aspectKey));

  // Aspects that are now visible (weren't before)
  const revealed = nextVisible.filter((a) => !prevKeys.has(aspectKey(a)));

  // Aspects that are now hidden (were visible before)
  const hidden = prevVisible.filter((a) => !nextKeys.has(aspectKey(a)));

  // Aspects that remain visible
  const unchanged = nextVisible.filter((a) => prevKeys.has(aspectKey(a)));

  return {
    revealed,
    hidden,
    unchanged,
    observer: { from: prevObserver, to: nextObserver },
  };
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook to compute umwelt diff with memoization.
 */
export function useUmweltDiff(
  prevObserver: Observer | null,
  nextObserver: Observer,
  metadata: Record<string, PathMetadata>
): UmweltDiff | null {
  return useMemo(() => {
    if (!prevObserver || prevObserver.archetype === nextObserver.archetype) {
      return null;
    }

    return computeUmweltDiff(prevObserver, nextObserver, metadata);
  }, [prevObserver, nextObserver, metadata]);
}

/**
 * Hook to check if a specific aspect is available to the current observer.
 *
 * Umwelt v2: Accepts optional aspectMetadata for registry-backed capability check.
 */
export function useAspectAvailability(
  observer: Observer
): (aspect: string, aspectMeta?: AspectMetadataEntry) => { available: boolean; reason?: string } {
  return useCallback(
    (aspect: string, aspectMeta?: AspectMetadataEntry) => {
      const required = getRequiredCapability(aspect, aspectMeta);

      if (!hasCapability(observer, 'read')) {
        return { available: false, reason: 'Requires read capability' };
      }

      if (required && !hasCapability(observer, required)) {
        return { available: false, reason: `Requires ${required} capability` };
      }

      return { available: true };
    },
    [observer]
  );
}

export default useUmweltDiff;
