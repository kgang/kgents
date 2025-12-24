/**
 * useDocumentParser — Parse markdown content to SceneGraph for interactive rendering.
 *
 * In NORMAL mode, we render the document as interactive tokens:
 * - AGENTESE paths are clickable
 * - Checkboxes are toggleable
 * - Code blocks have syntax highlighting + copy
 * - Links have preview tooltips
 *
 * Uses the AGENTESE self.document.parse endpoint to transform markdown
 * into a SceneGraph that InteractiveDocument can render.
 *
 * "Specs stop being documentation and become live control surfaces."
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { documentApi, DocumentParseResponse } from '../api/client';
import type { SceneGraph } from '../components/tokens/types';

export interface UseDocumentParserOptions {
  /** Content to parse */
  content: string;
  /** Layout mode for rendering */
  layoutMode?: 'COMPACT' | 'COMFORTABLE' | 'SPACIOUS';
  /** Skip parsing (e.g., when in INSERT mode) */
  skip?: boolean;
  /** Debounce delay in ms (default 300) */
  debounceMs?: number;
}

export interface UseDocumentParserReturn {
  /** Parsed SceneGraph for InteractiveDocument */
  sceneGraph: SceneGraph | null;
  /** Loading state */
  isLoading: boolean;
  /** Error message if parsing failed */
  error: string | null;
  /** Token statistics */
  tokenCount: number;
  /** Re-parse manually */
  reparse: () => void;
}

/**
 * Hook to parse markdown content into a SceneGraph.
 *
 * Automatically re-parses when content changes (debounced).
 * Set skip=true to disable parsing (e.g., in INSERT mode).
 */
export function useDocumentParser(options: UseDocumentParserOptions): UseDocumentParserReturn {
  const { content, layoutMode = 'COMFORTABLE', skip = false, debounceMs = 300 } = options;

  const [sceneGraph, setSceneGraph] = useState<SceneGraph | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tokenCount, setTokenCount] = useState(0);

  // Track content hash to avoid re-parsing identical content
  const lastContentHashRef = useRef<string>('');
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Simple hash for content comparison
  const hashContent = (text: string): string => {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return String(hash);
  };

  const parseContent = useCallback(async () => {
    if (skip || !content) {
      setSceneGraph(null);
      setTokenCount(0);
      return;
    }

    // Check if content changed
    const contentHash = hashContent(content);
    if (contentHash === lastContentHashRef.current) {
      return; // Content unchanged, skip parsing
    }

    setIsLoading(true);
    setError(null);

    try {
      const response: DocumentParseResponse = await documentApi.parse(content, layoutMode);

      // Update state with parsed result
      setSceneGraph(response.scene_graph as SceneGraph);
      setTokenCount(response.token_count);
      // eslint-disable-next-line require-atomic-updates -- Intentional: last successful parse wins
      lastContentHashRef.current = contentHash;
    } catch (err) {
      console.error('[useDocumentParser] Parse failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to parse document');
      // Keep existing sceneGraph on error (graceful degradation)
    } finally {
      setIsLoading(false);
    }
  }, [content, layoutMode, skip]);

  // Debounced parsing on content change
  useEffect(() => {
    if (skip) {
      // Clear any pending parse when skipping
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      return;
    }

    // Debounce parsing
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      void parseContent();
    }, debounceMs);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [content, skip, debounceMs, parseContent]);

  // Manual reparse
  const reparse = useCallback(() => {
    lastContentHashRef.current = ''; // Force re-parse
    void parseContent();
  }, [parseContent]);

  return {
    sceneGraph,
    isLoading,
    error,
    tokenCount,
    reparse,
  };
}

/**
 * Create a fallback SceneGraph from raw text.
 * Used when parsing fails or as initial state.
 */
export function createFallbackSceneGraph(content: string): SceneGraph {
  return {
    id: `fallback-${Date.now()}`,
    nodes: [
      {
        id: 'text-0',
        kind: 'TEXT',
        content: content,
        label: '',
        style: {},
        flex: 1,
        min_width: null,
        min_height: null,
        interactions: [],
        section_index: null,
        metadata: {},
      },
    ],
    edges: [],
    layout: {
      direction: 'vertical',
      gap: 0,
      padding: 0,
      mode: 'COMFORTABLE',
    },
    title: '',
    metadata: {},
    created_at: new Date().toISOString(),
  };
}

export default useDocumentParser;
