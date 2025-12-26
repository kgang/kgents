/**
 * MarkdownEditor Component
 *
 * A STARK BIOME-themed markdown editor using CodeMirror 6.
 * Supports mode switching: readonly (NORMAL) to editable (INSERT).
 *
 * Key feature: Dynamic readonly switching via CodeMirror Compartments.
 * When readonly prop changes, the editor reconfigures without remounting.
 */

import React, { useEffect, forwardRef, useImperativeHandle, useState, useRef, useCallback, useMemo } from 'react';
import { useCodeMirror, UseCodeMirrorOptions } from './useCodeMirror';
import { ghostTextExtension } from './ghostText';
import { edgeGutterExtension, updateEdges, type LineEdge } from './edgeGutterExtension';
import { useGhostTextSources } from './useGhostTextSources';
import './MarkdownEditor.css';
import './ghostText.css';
import './edgeGutter.css';

/** Scroll cursor fade duration in ms (fast fade for smooth reading) */
const SCROLL_CURSOR_FADE_MS = 650;

export interface MarkdownEditorProps {
  /** Editor content */
  value?: string;
  /** Called when content changes */
  onChange?: (value: string) => void;
  /** Called on blur */
  onBlur?: () => void;
  /** Read-only mode - can be changed dynamically */
  readonly?: boolean;
  /** Placeholder text when empty */
  placeholder?: string;
  /** Auto-focus on mount (if not readonly) */
  autoFocus?: boolean;
  /** Additional CSS class */
  className?: string;
  /** Minimum height */
  minHeight?: string | number;
  /** Maximum height (for scrolling) */
  maxHeight?: string | number;
  /** Fill parent height */
  fillHeight?: boolean;
  /** Enable ghost text completions (only in INSERT mode) */
  enableGhostText?: boolean;
  /** Edges with line numbers to display in gutter */
  edges?: LineEdge[];
  /** Called when an edge marker is clicked */
  onEdgeClick?: (edge: LineEdge) => void;
}

export interface MarkdownEditorRef {
  /** Get current content */
  getValue: () => string;
  /** Set content programmatically */
  setValue: (value: string) => void;
  /** Focus the editor */
  focus: () => void;
  /** Check if focused */
  isFocused: () => boolean;
  /** Set readonly state dynamically (vim-like mode switch) */
  setReadonly: (readonly: boolean) => void;
  // --- Scroll Navigation (for NORMAL mode reader view) ---
  /** Scroll by N lines (positive = down, negative = up) */
  scrollLines: (delta: number) => void;
  /** Scroll to next/prev paragraph (blank line) */
  scrollParagraph: (direction: 1 | -1) => void;
  /** Scroll to top of document */
  scrollToTop: () => void;
  /** Scroll to bottom of document */
  scrollToBottom: () => void;
}

/**
 * Markdown editor with STARK BIOME styling
 *
 * Supports dynamic readonly switching for vim-like modes:
 * - NORMAL mode: readonly=true, keyboard scrolling (j/k/etc)
 * - INSERT mode: readonly=false, full editing
 */
export const MarkdownEditor = forwardRef<MarkdownEditorRef, MarkdownEditorProps>(
  function MarkdownEditor(props, ref) {
    const {
      value = '',
      onChange,
      onBlur,
      readonly = false,
      placeholder = '',
      autoFocus = false,
      className = '',
      minHeight,
      maxHeight,
      fillHeight = false,
      enableGhostText = false,
      edges = [],
      onEdgeClick,
    } = props;

    // Ghost text sources
    const { getCompletion } = useGhostTextSources();

    // Stable reference for onEdgeClick to avoid extension recreation
    const onEdgeClickRef = useRef(onEdgeClick);
    onEdgeClickRef.current = onEdgeClick;

    // Build extensions including ghost text and edge gutter
    const extensions = useMemo(() => {
      const exts = [];

      // Add ghost text extension only if enabled and not readonly
      if (enableGhostText && !readonly) {
        exts.push(
          ghostTextExtension({
            fetcher: getCompletion,
          })
        );
      }

      // Add edge gutter extension (always active, shows edges with line numbers)
      // Use stable callback wrapper to avoid recreating extension
      exts.push(
        edgeGutterExtension({
          edges,
          onEdgeClick: (edge) => onEdgeClickRef.current?.(edge),
        })
      );

      return exts;
    }, [enableGhostText, readonly, getCompletion, edges]);

    const options: UseCodeMirrorOptions = {
      initialValue: value,
      onChange,
      onBlur,
      language: 'markdown',
      readonly,
      placeholder,
      autoFocus,
      lineWrapping: true,
      extensions,
    };

    const {
      containerRef,
      view,
      getValue,
      setValue,
      focus,
      isFocused,
      setReadonly,
      scrollLines: rawScrollLines,
      scrollParagraph: rawScrollParagraph,
      scrollToTop: rawScrollToTop,
      scrollToBottom: rawScrollToBottom,
    } = useCodeMirror(options);

    // Update edges when they change (after initial mount)
    useEffect(() => {
      if (view && edges.length > 0) {
        updateEdges(view, edges);
      }
    }, [view, edges]);

    // --- Scroll Cursor State ---
    const [scrollCursorVisible, setScrollCursorVisible] = useState(false);
    const scrollCursorTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    /** Show scroll cursor and set fade timer */
    const showScrollCursor = useCallback(() => {
      setScrollCursorVisible(true);

      // Clear existing timer
      if (scrollCursorTimerRef.current) {
        clearTimeout(scrollCursorTimerRef.current);
      }

      // Set new fade timer
      scrollCursorTimerRef.current = setTimeout(() => {
        setScrollCursorVisible(false);
        scrollCursorTimerRef.current = null;
      }, SCROLL_CURSOR_FADE_MS);
    }, []);

    // Clean up timer on unmount
    useEffect(() => {
      return () => {
        if (scrollCursorTimerRef.current) {
          clearTimeout(scrollCursorTimerRef.current);
        }
      };
    }, []);

    // --- Wrapped Scroll Methods (show cursor on scroll) ---
    const scrollLines = useCallback(
      (delta: number) => {
        rawScrollLines(delta);
        showScrollCursor();
      },
      [rawScrollLines, showScrollCursor]
    );

    const scrollParagraph = useCallback(
      (direction: 1 | -1) => {
        rawScrollParagraph(direction);
        showScrollCursor();
      },
      [rawScrollParagraph, showScrollCursor]
    );

    const scrollToTop = useCallback(() => {
      rawScrollToTop();
      showScrollCursor();
    }, [rawScrollToTop, showScrollCursor]);

    const scrollToBottom = useCallback(() => {
      rawScrollToBottom();
      showScrollCursor();
    }, [rawScrollToBottom, showScrollCursor]);

    // Sync external value changes
    useEffect(() => {
      const currentValue = getValue();
      if (value !== currentValue) {
        setValue(value);
      }
    }, [value, getValue, setValue]);

    // Expose methods via ref
    useImperativeHandle(ref, () => ({
      getValue,
      setValue,
      focus,
      isFocused,
      setReadonly,
      scrollLines,
      scrollParagraph,
      scrollToTop,
      scrollToBottom,
    }));

    // Build style object
    const style: React.CSSProperties = {};
    if (minHeight) {
      style.minHeight = typeof minHeight === 'number' ? `${minHeight}px` : minHeight;
    }
    if (maxHeight) {
      style.maxHeight = typeof maxHeight === 'number' ? `${maxHeight}px` : maxHeight;
    }
    if (fillHeight) {
      style.height = '100%';
    }

    const containerClass = [
      'markdown-editor',
      readonly && 'markdown-editor--readonly',
      fillHeight && 'markdown-editor--fill',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={containerClass} style={style}>
        <div ref={containerRef} className="markdown-editor__container" />
        {/* Scroll cursor - horizontal line that appears during keyboard scroll */}
        <div
          className={`markdown-editor__scroll-cursor ${scrollCursorVisible ? 'markdown-editor__scroll-cursor--visible' : ''}`}
          aria-hidden="true"
        />
      </div>
    );
  }
);

export default MarkdownEditor;

// Re-export LineEdge for convenience
export type { LineEdge } from './edgeGutterExtension';
