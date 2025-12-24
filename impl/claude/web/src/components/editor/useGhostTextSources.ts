/**
 * Ghost Text Completion Sources
 *
 * Aggregates multiple sources of completions with priority weighting:
 * 1. AGENTESE paths (highest priority - cached locally)
 * 2. Spec vocabulary (medium - future: backend integration)
 * 3. Recent marks (lower - future: backend integration)
 *
 * Philosophy: The AI isn't a separate entity you talk to.
 * The AI is in your fingers—completing your thoughts before you finish thinking them.
 */

import { useMemo } from 'react';
import { matchAgentesePath } from './agentesePaths';

export interface CompletionSource {
  /** Source identifier */
  name: string;
  /** Priority (1.0 = highest, 0.0 = lowest) */
  priority: number;
  /** Match function - returns completions for a prefix */
  match: (prefix: string) => Promise<string[]> | string[];
}

export interface GhostTextCompletion {
  /** The completion text to show */
  text: string;
  /** Source that provided this completion */
  source: string;
  /** Priority score */
  priority: number;
}

/**
 * Hook to aggregate ghost text completion sources
 *
 * Returns ordered sources and a combined match function.
 */
export function useGhostTextSources(): {
  sources: CompletionSource[];
  getCompletion: (prefix: string) => Promise<GhostTextCompletion | null>;
} {
  const sources = useMemo<CompletionSource[]>(
    () => [
      {
        name: 'agentese',
        priority: 1.0,
        match: (prefix: string) => {
          const matches = matchAgentesePath(prefix);
          // Return only the completion suffix, not the full path
          return matches.map(match => match.slice(prefix.length));
        },
      },
      {
        name: 'spec-vocabulary',
        priority: 0.7,
        match: async (_prefix: string) => {
          // Future: integrate with backend
          // const response = await fetch(`/api/spec/complete?prefix=${encodeURIComponent(prefix)}`);
          // const data = await response.json();
          // return data.completions || [];
          return [];
        },
      },
      {
        name: 'recent-marks',
        priority: 0.4,
        match: async (_prefix: string) => {
          // Future: integrate with backend
          // const response = await fetch(`/api/marks/recent?prefix=${encodeURIComponent(prefix)}`);
          // const data = await response.json();
          // return data.completions || [];
          return [];
        },
      },
    ],
    []
  );

  /**
   * Get the best completion for a prefix from all sources
   *
   * Algorithm:
   * 1. Query all sources in parallel
   * 2. Filter empty results
   * 3. Return highest priority match
   */
  const getCompletion = useMemo(
    () => async (prefix: string): Promise<GhostTextCompletion | null> => {
      if (!prefix || prefix.length === 0) {
        return null;
      }

      // Query all sources in parallel
      const results = await Promise.all(
        sources.map(async source => {
          try {
            const matches = await source.match(prefix);
            return {
              source: source.name,
              priority: source.priority,
              matches: matches || [],
            };
          } catch (error) {
            console.warn(`Ghost text source "${source.name}" failed:`, error);
            return {
              source: source.name,
              priority: source.priority,
              matches: [],
            };
          }
        })
      );

      // Collect all non-empty completions
      const completions: GhostTextCompletion[] = [];
      for (const result of results) {
        if (result.matches.length > 0) {
          // Take first match from each source
          completions.push({
            text: result.matches[0],
            source: result.source,
            priority: result.priority,
          });
        }
      }

      if (completions.length === 0) {
        return null;
      }

      // Sort by priority (descending) and return best
      completions.sort((a, b) => b.priority - a.priority);
      return completions[0];
    },
    [sources]
  );

  return {
    sources,
    getCompletion,
  };
}
