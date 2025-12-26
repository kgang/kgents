/**
 * useCodeMirror Hook
 *
 * React hook for CodeMirror 6 integration.
 * Supports dynamic readonly switching via Compartments for vim-like mode changes.
 *
 * Key insight: CodeMirror 6 uses Compartments for dynamic reconfiguration.
 * When readonly changes (NORMAL→INSERT mode), we reconfigure the compartment
 * rather than recreating the entire editor.
 */

import { useRef, useEffect, useCallback, useState } from 'react';
import { Compartment, EditorState, Extension } from '@codemirror/state';
import { EditorView, keymap, placeholder as placeholderExt } from '@codemirror/view';
import { markdown } from '@codemirror/lang-markdown';
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
import { starkBiome } from './starkBiomeTheme';

export interface UseCodeMirrorOptions {
  /** Initial content */
  initialValue?: string;
  /** Called when content changes */
  onChange?: (value: string) => void;
  /** Called on blur */
  onBlur?: () => void;
  /** Language mode */
  language?: 'markdown' | 'plaintext';
  /** Read-only mode - can be changed dynamically */
  readonly?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Additional extensions */
  extensions?: Extension[];
  /** Line wrapping */
  lineWrapping?: boolean;
  /** Auto-focus on mount */
  autoFocus?: boolean;
}

export interface UseCodeMirrorReturn {
  /** Ref to attach to container div */
  containerRef: React.RefObject<HTMLDivElement>;
  /** The EditorView instance (null before mount) */
  view: EditorView | null;
  /** Get current content */
  getValue: () => string;
  /** Set content programmatically */
  setValue: (value: string) => void;
  /** Focus the editor */
  focus: () => void;
  /** Check if editor is focused */
  isFocused: () => boolean;
  /** Set readonly state dynamically */
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
 * Hook for creating and managing a CodeMirror 6 editor
 *
 * Now supports dynamic readonly changes via Compartments.
 * When you call setReadonly(true/false), the editor reconfigures
 * without losing state or requiring remount.
 */
export function useCodeMirror(options: UseCodeMirrorOptions = {}): UseCodeMirrorReturn {
  const {
    initialValue = '',
    onChange,
    onBlur,
    language = 'markdown',
    readonly = false,
    placeholder = '',
    extensions: additionalExtensions = [],
    lineWrapping = true,
    autoFocus = false,
  } = options;

  const containerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const [mounted, setMounted] = useState(false);

  // Compartment for dynamic readonly configuration
  const readonlyCompartment = useRef(new Compartment());

  // Track if we're updating from external setValue to avoid loops
  const isSettingValue = useRef(false);

  // Track current readonly state for the compartment
  const currentReadonly = useRef(readonly);

  /**
   * Build readonly extensions based on state
   */
  const buildReadonlyExtensions = useCallback((isReadonly: boolean): Extension => {
    if (isReadonly) {
      return [EditorState.readOnly.of(true), EditorView.editable.of(false)];
    }
    return [EditorState.readOnly.of(false), EditorView.editable.of(true)];
  }, []);

  /**
   * Build static extensions (those that don't change dynamically)
   */
  const buildStaticExtensions = useCallback((): Extension[] => {
    const exts: Extension[] = [];

    // Base extensions
    exts.push(history());
    exts.push(keymap.of([...defaultKeymap, ...historyKeymap]));

    // Theme
    exts.push(starkBiome);

    // Language
    if (language === 'markdown') {
      exts.push(markdown());
    }

    // Line wrapping
    if (lineWrapping) {
      exts.push(EditorView.lineWrapping);
    }

    // Placeholder
    if (placeholder) {
      exts.push(placeholderExt(placeholder));
    }

    // Update listener for onChange
    if (onChange) {
      exts.push(
        EditorView.updateListener.of((update) => {
          if (update.docChanged && !isSettingValue.current) {
            onChange(update.state.doc.toString());
          }
        })
      );
    }

    // Blur handler
    if (onBlur) {
      exts.push(
        EditorView.domEventHandlers({
          blur: () => {
            onBlur();
            return false;
          },
        })
      );
    }

    // Additional user extensions
    exts.push(...additionalExtensions);

    return exts;
  }, [language, lineWrapping, placeholder, onChange, onBlur, additionalExtensions]);

  // Initialize editor
  useEffect(() => {
    if (!containerRef.current) return;

    // Build initial extensions with compartment for readonly
    const staticExts = buildStaticExtensions();
    const readonlyExt = readonlyCompartment.current.of(buildReadonlyExtensions(readonly));

    // Create state
    const state = EditorState.create({
      doc: initialValue,
      extensions: [...staticExts, readonlyExt],
    });

    // Create view
    const view = new EditorView({
      state,
      parent: containerRef.current,
    });

    viewRef.current = view;
    currentReadonly.current = readonly;
    setMounted(true);

    // Auto-focus if not readonly
    if (autoFocus && !readonly) {
      // Use requestAnimationFrame to ensure DOM is ready
      requestAnimationFrame(() => {
        view.focus();
      });
    }

    // Cleanup
    return () => {
      view.destroy();
      viewRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount - readonly changes handled by setReadonly

  /**
   * Set readonly state dynamically via Compartment reconfiguration
   */
  const setReadonly = useCallback(
    (isReadonly: boolean) => {
      const view = viewRef.current;
      if (!view) return;

      // Skip if already in this state
      if (currentReadonly.current === isReadonly) return;

      // Reconfigure the compartment
      view.dispatch({
        effects: readonlyCompartment.current.reconfigure(buildReadonlyExtensions(isReadonly)),
      });

      currentReadonly.current = isReadonly;

      // If switching to editable, focus the editor
      if (!isReadonly) {
        requestAnimationFrame(() => {
          view.focus();
        });
      }
    },
    [buildReadonlyExtensions]
  );

  // Sync readonly prop changes to the compartment
  useEffect(() => {
    if (mounted) {
      setReadonly(readonly);
    }
  }, [readonly, mounted, setReadonly]);

  // Get current value
  const getValue = useCallback((): string => {
    return viewRef.current?.state.doc.toString() ?? '';
  }, []);

  // Set value programmatically
  const setValue = useCallback((value: string) => {
    const view = viewRef.current;
    if (!view) return;

    isSettingValue.current = true;
    view.dispatch({
      changes: {
        from: 0,
        to: view.state.doc.length,
        insert: value,
      },
    });
    isSettingValue.current = false;
  }, []);

  // Focus the editor
  const focus = useCallback(() => {
    const view = viewRef.current;
    if (!view) return;

    // Focus and place cursor at end if entering edit mode
    view.focus();
  }, []);

  // Check if focused
  const isFocused = useCallback((): boolean => {
    return viewRef.current?.hasFocus ?? false;
  }, []);

  // --- Scroll Navigation Methods ---

  /** Scroll by N lines (positive = down, negative = up) */
  const scrollLines = useCallback((delta: number) => {
    const view = viewRef.current;
    if (!view) return;
    const lineHeight = view.defaultLineHeight;
    view.scrollDOM.scrollTop += delta * lineHeight;
  }, []);

  /** Scroll to next/prev paragraph (blank line boundary) */
  const scrollParagraph = useCallback((direction: 1 | -1) => {
    const view = viewRef.current;
    if (!view) return;

    const doc = view.state.doc;
    const totalLines = doc.lines;

    // Get current visible line from scroll position
    const scrollTop = view.scrollDOM.scrollTop;
    const topBlock = view.lineBlockAtHeight(scrollTop);
    const currentLine = doc.lineAt(topBlock.from).number;

    const isBlank = (lineNum: number) => doc.line(lineNum).text.trim() === '';

    let targetLine: number;

    if (direction > 0) {
      // } — Forward: find next paragraph start
      let i = currentLine;
      while (i < totalLines && !isBlank(i)) i++;
      while (i < totalLines && isBlank(i)) i++;
      targetLine = i <= totalLines ? i : totalLines;
    } else {
      // { — Backward: find previous paragraph start
      let i = currentLine;
      if (i > 1 && !isBlank(i) && (i === 1 || isBlank(i - 1))) {
        i--;
      }
      while (i > 1 && isBlank(i)) i--;
      while (i > 1 && !isBlank(i - 1)) i--;
      targetLine = Math.max(i, 1);
    }

    const targetPos = doc.line(targetLine).from;
    view.dispatch({
      effects: EditorView.scrollIntoView(targetPos, { y: 'start' }),
    });
  }, []);

  /** Scroll to top of document */
  const scrollToTop = useCallback(() => {
    const view = viewRef.current;
    if (!view) return;
    view.dispatch({
      effects: EditorView.scrollIntoView(0, { y: 'start' }),
    });
  }, []);

  /** Scroll to bottom of document */
  const scrollToBottom = useCallback(() => {
    const view = viewRef.current;
    if (!view) return;
    const docLength = view.state.doc.length;
    view.dispatch({
      effects: EditorView.scrollIntoView(docLength, { y: 'end' }),
    });
  }, []);

  return {
    containerRef,
    view: viewRef.current,
    getValue,
    setValue,
    focus,
    isFocused,
    setReadonly,
    scrollLines,
    scrollParagraph,
    scrollToTop,
    scrollToBottom,
  };
}

export default useCodeMirror;
