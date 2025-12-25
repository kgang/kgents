/**
 * useMentions — Hook for mention management in chat
 *
 * Manages:
 * - Active mentions (currently injected into context)
 * - Mention resolution (fetch content from backend)
 * - Mention removal
 * - Recent mentions tracking (for autocomplete)
 *
 * @see spec/protocols/chat-web.md Part VI.3
 */

import { useState, useCallback, useEffect } from 'react';
import { nanoid } from 'nanoid';
import type { MentionType, MentionSuggestion } from './MentionPicker';
import type { Mention } from './MentionCard';

// =============================================================================
// Types
// =============================================================================

export interface ResolvedContent {
  content: string;
  metadata?: Record<string, unknown>;
}

export interface UseMentionsResult {
  /** Currently active mentions */
  activeMentions: Mention[];

  /** Add a mention (from picker selection) */
  addMention: (suggestion: MentionSuggestion) => Promise<void>;

  /** Remove a mention by ID */
  removeMention: (id: string) => void;

  /** Resolve mention content (async fetch) */
  resolveMention: (mention: Mention) => Promise<ResolvedContent>;

  /** Recently used mentions (for autocomplete) */
  recentMentions: MentionSuggestion[];

  /** Clear all mentions */
  clearAll: () => void;
}

// =============================================================================
// Mock Resolution Functions
// These will be replaced with actual API calls
// =============================================================================

async function resolveMentionContent(
  type: MentionType,
  value: string
): Promise<ResolvedContent> {
  // Simulate network delay
  await new Promise<void>((resolve) => {
    setTimeout(() => resolve(), 300);
  });

  switch (type) {
    case 'file':
      // TODO: Replace with actual file fetch
      return {
        content: `// File: ${value}\n// TODO: Fetch actual file contents from backend`,
      };

    case 'symbol':
      // TODO: Replace with actual symbol lookup
      return {
        content: `# Symbol: ${value}\n# TODO: Fetch definition + docstring from backend`,
      };

    case 'spec':
      // TODO: Replace with actual spec fetch
      return {
        content: `# Spec: ${value}\n# TODO: Fetch spec contents from backend`,
      };

    case 'witness':
      // TODO: Replace with actual witness query
      return {
        content: `# Witness: ${value}\n# TODO: Fetch witness marks from backend`,
      };

    case 'web':
      // TODO: Replace with actual web fetch
      return {
        content: `# Web: ${value}\n# TODO: Fetch web page contents from backend`,
      };

    case 'terminal':
      // TODO: Replace with actual terminal output
      return {
        content: `# Terminal: ${value}\n# TODO: Fetch terminal output from backend`,
      };

    case 'project':
      // TODO: Replace with actual project tree
      return {
        content: `# Project: ${value}\n# TODO: Fetch project file tree from backend`,
      };

    default:
      throw new Error(`Unknown mention type: ${type}`);
  }
}

// =============================================================================
// Hook
// =============================================================================

const MAX_RECENT_MENTIONS = 10;
const RECENT_MENTIONS_KEY = 'chat-recent-mentions';

export function useMentions(): UseMentionsResult {
  const [activeMentions, setActiveMentions] = useState<Mention[]>([]);
  const [recentMentions, setRecentMentions] = useState<MentionSuggestion[]>(() => {
    // Load recent mentions from localStorage
    try {
      const stored = localStorage.getItem(RECENT_MENTIONS_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // Persist recent mentions to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(RECENT_MENTIONS_KEY, JSON.stringify(recentMentions));
    } catch (error) {
      console.error('Failed to save recent mentions:', error);
    }
  }, [recentMentions]);

  // Add a mention from picker selection
  const addMention = useCallback(
    async (suggestion: MentionSuggestion) => {
      const id = nanoid();

      // Create mention with pending content
      const newMention: Mention = {
        id,
        type: suggestion.type,
        value: suggestion.value,
        label: suggestion.label,
      };

      // Add to active mentions immediately
      setActiveMentions((prev) => [...prev, newMention]);

      // Update recent mentions
      setRecentMentions((prev) => {
        const filtered = prev.filter(
          (m) => !(m.type === suggestion.type && m.value === suggestion.value)
        );
        const updated = [suggestion, ...filtered].slice(0, MAX_RECENT_MENTIONS);
        return updated;
      });

      // Resolve content in background
      try {
        const resolved = await resolveMentionContent(suggestion.type, suggestion.value);
        setActiveMentions((prev) =>
          prev.map((m) =>
            m.id === id
              ? {
                  ...m,
                  content: resolved.content,
                }
              : m
          )
        );
      } catch (error) {
        // Update mention with error
        setActiveMentions((prev) =>
          prev.map((m) =>
            m.id === id
              ? {
                  ...m,
                  error: error instanceof Error ? error.message : 'Failed to load content',
                }
              : m
          )
        );
      }
    },
    []
  );

  // Remove a mention
  const removeMention = useCallback((id: string) => {
    setActiveMentions((prev) => prev.filter((m) => m.id !== id));
  }, []);

  // Resolve mention content (re-fetch if needed)
  const resolveMention = useCallback(async (mention: Mention): Promise<ResolvedContent> => {
    return await resolveMentionContent(mention.type, mention.value);
  }, []);

  // Clear all mentions
  const clearAll = useCallback(() => {
    setActiveMentions([]);
  }, []);

  return {
    activeMentions,
    addMention,
    removeMention,
    resolveMention,
    recentMentions,
    clearAll,
  };
}

export default useMentions;
