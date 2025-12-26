/**
 * ContentPane — The heart of the editor
 *
 * Vim-like mode philosophy:
 * - NORMAL: Rendered view with interactive tokens (clickable links, toggleable tasks)
 * - INSERT: Full editing mode via CodeMirror
 *
 * Architecture:
 * - NORMAL mode: Uses InteractiveDocument to render parsed SceneGraph
 *   → AGENTESE paths are clickable
 *   → Checkboxes are toggleable
 *   → Code blocks have syntax highlighting + copy
 *   → "Specs stop being documentation and become live control surfaces"
 *
 * - INSERT mode: Uses MarkdownEditor (CodeMirror) with editable mode
 *   → Full text editing with history
 *   → Preserves scroll position on mode switch
 *
 * Content flow:
 * - workingContent (from K-Block) is the source of truth during edits
 * - Falls back to node.content when no working content exists
 */

import { memo, useCallback, useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';
import { AnimatePresence } from 'framer-motion';
import { MarkdownEditor, MarkdownEditorRef } from '../../components/editor';
import { InteractiveDocument } from '../../components/tokens';
import { Portal } from './Portal';
import { Minimap } from '../Minimap';
import { useDocumentParser, createFallbackSceneGraph } from '../useDocumentParser';
import type { GraphNode, PortalState } from '../state/types';

/**
 * ContentPaneRef — Imperative handle for scroll operations.
 * Works in both NORMAL and INSERT modes.
 */
export interface ContentPaneRef {
  scrollLines: (delta: number) => void;
  scrollParagraph: (delta: number) => void;
  scrollToTop: () => void;
  scrollToBottom: () => void;
}

interface ContentPaneProps {
  node: GraphNode | null;
  mode: string;
  cursor: { line: number; column: number };
  workingContent?: string;
  onContentChange?: (content: string) => void;
  onNavigate?: (path: string) => void;
  onToggle?: (newState: boolean, taskId?: string) => Promise<void>;
  readerRef?: React.RefObject<MarkdownEditorRef | null>;
  portals?: Map<string, PortalState>;
  onCursorChange?: (line: number, column: number) => void;
}

export const ContentPane = memo(forwardRef<ContentPaneRef, ContentPaneProps>(function ContentPane({
  node,
  mode,
  cursor: _cursor,
  workingContent,
  onContentChange,
  onNavigate,
  onToggle,
  onCursorChange: _onCursorChange,
  readerRef,
  portals,
}, ref) {
  // Editor ref for INSERT mode
  const editorRef = useRef<MarkdownEditorRef>(null);
  const prevModeRef = useRef(mode);

  // Scroll container ref for tracking scroll position
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Scroll state for minimap
  const [scrollTop, setScrollTop] = useState(0);
  const [viewportRatio, setViewportRatio] = useState(0.2);

  // Use working content if available (edited content), otherwise use node content
  const displayContent = workingContent ?? node?.content ?? '';

  // Convert portals Map to array for rendering
  const portalArray = portals ? Array.from(portals.values()) : [];

  // Determine if we're in INSERT mode
  const isInsertMode = mode === 'INSERT';

  // Parse content to SceneGraph for NORMAL mode
  // Skip parsing in INSERT mode for performance
  const { sceneGraph, isLoading: _isLoading } = useDocumentParser({
    content: displayContent,
    layoutMode: 'COMFORTABLE',
    skip: isInsertMode, // Don't parse in INSERT mode
    debounceMs: 150, // Fast debounce for responsive feel
  });

  // Handle mode transitions
  useEffect(() => {
    const wasInsert = prevModeRef.current === 'INSERT';
    const isInsert = mode === 'INSERT';

    // Entering INSERT mode
    if (isInsert && !wasInsert) {
      requestAnimationFrame(() => {
        editorRef.current?.setReadonly(false);
        editorRef.current?.focus();
      });
    }

    // Exiting INSERT mode (back to NORMAL)
    if (!isInsert && wasInsert) {
      requestAnimationFrame(() => {
        editorRef.current?.setReadonly(true);
      });
    }

    prevModeRef.current = mode;
  }, [mode]);

  // Forward ref to parent for NORMAL mode scroll navigation (on editor when visible)
  useEffect(() => {
    if (readerRef && 'current' in readerRef) {
      (readerRef as React.MutableRefObject<MarkdownEditorRef | null>).current = editorRef.current;
    }
  }, [readerRef, editorRef.current]);

  // Handle content changes from CodeMirror
  const handleContentChange = useCallback(
    (newContent: string) => {
      onContentChange?.(newContent);
    },
    [onContentChange]
  );

  // Handle navigation from InteractiveDocument (AGENTESE paths, links)
  const handleNavigate = useCallback(
    (path: string) => {
      onNavigate?.(path);
    },
    [onNavigate]
  );

  // Handle toggle from InteractiveDocument (task checkboxes)
  const handleToggle = useCallback(
    async (newState: boolean, taskId?: string) => {
      await onToggle?.(newState, taskId);
    },
    [onToggle]
  );

  // Track scroll position for minimap
  const handleScroll = useCallback(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const { scrollTop, scrollHeight, clientHeight } = container;
    const maxScroll = scrollHeight - clientHeight;

    if (maxScroll > 0) {
      const normalizedScrollTop = scrollTop / maxScroll;
      const normalizedViewportRatio = clientHeight / scrollHeight;

      setScrollTop(normalizedScrollTop);
      setViewportRatio(normalizedViewportRatio);
    } else {
      setScrollTop(0);
      setViewportRatio(1);
    }
  }, []);

  // Handle jump to position from minimap
  const handleJumpToPosition = useCallback((position: number) => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const { scrollHeight, clientHeight } = container;
    const maxScroll = scrollHeight - clientHeight;
    const targetScroll = position * maxScroll;

    container.scrollTo({ top: targetScroll, behavior: 'smooth' });
  }, []);

  // Update scroll position when container is mounted or resized
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    // Initial scroll position - use requestAnimationFrame to ensure DOM is ready
    requestAnimationFrame(() => {
      handleScroll();
    });

    // Add scroll listener with passive flag for better performance
    container.addEventListener('scroll', handleScroll, { passive: true });

    // Add resize observer to update viewport ratio
    const resizeObserver = new ResizeObserver(() => {
      // Debounce resize updates slightly
      requestAnimationFrame(() => {
        handleScroll();
      });
    });

    resizeObserver.observe(container);

    return () => {
      container.removeEventListener('scroll', handleScroll);
      resizeObserver.disconnect();
    };
  }, [handleScroll]);

  // Recalculate scroll position when content changes
  // This ensures the minimap viewport indicator updates correctly
  useEffect(() => {
    requestAnimationFrame(() => {
      handleScroll();
    });
  }, [displayContent, handleScroll]);

  // Expose scroll methods via imperative handle
  useImperativeHandle(ref, () => ({
    scrollLines: (delta: number) => {
      const container = scrollContainerRef.current;
      if (!container) return;

      // Scroll by line height (approximately 1.5em = 24px at 16px base)
      const lineHeight = 24;
      container.scrollBy({ top: delta * lineHeight, behavior: 'smooth' });
    },
    scrollParagraph: (delta: number) => {
      const container = scrollContainerRef.current;
      if (!container) return;

      // Scroll by paragraph (5 lines ≈ 120px)
      const paragraphHeight = 120;
      container.scrollBy({ top: delta * paragraphHeight, behavior: 'smooth' });
    },
    scrollToTop: () => {
      const container = scrollContainerRef.current;
      if (!container) return;

      container.scrollTo({ top: 0, behavior: 'smooth' });
    },
    scrollToBottom: () => {
      const container = scrollContainerRef.current;
      if (!container) return;

      container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    },
  }), []);

  // Empty state
  if (!node) {
    return (
      <div className="content-pane content-pane--empty">
        <div className="content-pane__welcome">
          <h2>Membrane Editor</h2>
          <p>&quot;The file is a lie. There is only the graph.&quot;</p>
          <div className="content-pane__hints">
            <p>
              <em>Click nodes/edges to navigate</em> — Graph-first navigation
            </p>
            <p>
              <kbd>gh/gl</kbd> Navigate parent/child
            </p>
            <p>
              <kbd>gj/gk</kbd> Navigate siblings
            </p>
            <p>
              <kbd>gd</kbd> Go to definition
            </p>
            <p>
              <kbd>gr</kbd> Go to references
            </p>
            <p>
              <kbd>zo/zc</kbd> Open/close portals
            </p>
            <p>
              <kbd>i</kbd> Enter INSERT mode
            </p>
            <p>
              <kbd>Escape</kbd> Return to NORMAL mode
            </p>
          </div>
        </div>
      </div>
    );
  }

  // INSERT mode: Full CodeMirror editor with ghost text
  if (isInsertMode) {
    return (
      <div className="content-pane content-pane--insert">
        <MarkdownEditor
          ref={editorRef}
          value={displayContent}
          onChange={handleContentChange}
          readonly={false}
          placeholder="Enter content..."
          fillHeight
          autoFocus
          enableGhostText
        />
        <AnimatePresence>
          {portalArray.map((portal) => (
            <Portal key={portal.edgeId} portal={portal} />
          ))}
        </AnimatePresence>
      </div>
    );
  }

  // NORMAL mode: Interactive rendered view with tokens
  // Use SceneGraph if available, otherwise create fallback
  const renderGraph = sceneGraph || createFallbackSceneGraph(displayContent);

  return (
    <div className="content-pane content-pane--normal">
      <div
        ref={scrollContainerRef}
        className="content-pane__interactive-container"
      >
        <InteractiveDocument
          sceneGraph={renderGraph}
          onNavigate={handleNavigate}
          onToggle={handleToggle}
          className="content-pane__interactive"
        />
      </div>
      <Minimap
        sceneGraph={renderGraph}
        content={displayContent}
        scrollTop={scrollTop}
        viewportRatio={viewportRatio}
        onJumpToPosition={handleJumpToPosition}
      />
      <AnimatePresence>
        {portalArray.map((portal) => (
          <Portal key={portal.edgeId} portal={portal} />
        ))}
      </AnimatePresence>
    </div>
  );
}));
