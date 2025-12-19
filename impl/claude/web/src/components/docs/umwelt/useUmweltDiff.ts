/**
 * useUmweltDiff - Compute what changes when observer shifts
 *
 * "The noun is a lie. There is only the rate of change."
 *
 * This hook computes the diff between two observer states,
 * determining which aspects become revealed, hidden, or unchanged.
 *
 * @see plans/umwelt-visualization.md
 */

import { useMemo, useCallback } from 'react';
import type { Observer } from '../ObserverPicker';
import type { PathMetadata } from '../useAgenteseDiscovery';
import type { AspectInfo, UmweltDiff } from './umwelt.types';

// =============================================================================
// Capability Checking
// =============================================================================

/**
 * Determines what capability (if any) is required for an aspect.
 */
function getRequiredCapability(aspect: string): string | null {
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
// Aspect Extraction
// =============================================================================

/**
 * Extract all aspects visible to an observer from metadata.
 */
function getVisibleAspects(
  observer: Observer,
  metadata: Record<string, PathMetadata>
): AspectInfo[] {
  const result: AspectInfo[] = [];

  for (const [path, pathMeta] of Object.entries(metadata)) {
    const aspects = pathMeta.aspects || ['manifest'];

    for (const aspect of aspects) {
      const requiredCapability = getRequiredCapability(aspect);

      if (hasCapability(observer, requiredCapability)) {
        result.push({
          aspect,
          path,
          requiredCapability,
          hasContract: false, // TODO: get from schema
          isStreaming: pathMeta.effects?.includes('streaming') ?? false,
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
 */
export function useAspectAvailability(
  observer: Observer
): (aspect: string) => { available: boolean; reason?: string } {
  return useCallback(
    (aspect: string) => {
      const required = getRequiredCapability(aspect);

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
