/**
 * useCodeMirror Hook
 *
 * React hook for CodeMirror 6 integration.
 * Handles setup, teardown, and state synchronization.
 */

import { useRef, useEffect, useCallback, useState } from 'react';
import { EditorState, Extension } from '@codemirror/state';
import { EditorView, keymap, placeholder as placeholderExt } from '@codemirror/view';
import { markdown } from '@codemirror/lang-markdown';
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
import { vim, Vim } from '@replit/codemirror-vim';
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
  /** Enable vim keybindings */
  vimMode?: boolean;
  /** Read-only mode */
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
}

/**
 * Hook for creating and managing a CodeMirror 6 editor
 */
export function useCodeMirror(options: UseCodeMirrorOptions = {}): UseCodeMirrorReturn {
  const {
    initialValue = '',
    onChange,
    onBlur,
    language = 'markdown',
    vimMode = false,
    readonly = false,
    placeholder = '',
    extensions: additionalExtensions = [],
    lineWrapping = true,
    autoFocus = false,
  } = options;

  const containerRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);
  const [, setMounted] = useState(false);

  // Track if we're updating from external setValue to avoid loops
  const isSettingValue = useRef(false);

  // Build extensions based on options
  const buildExtensions = useCallback((): Extension[] => {
    const exts: Extension[] = [];

    // Vim mode (must be first if enabled)
    if (vimMode) {
      exts.push(vim());
    }

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

    // Readonly
    if (readonly) {
      exts.push(EditorState.readOnly.of(true));
      exts.push(EditorView.editable.of(false));
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
  }, [
    vimMode,
    language,
    lineWrapping,
    readonly,
    placeholder,
    onChange,
    onBlur,
    additionalExtensions,
  ]);

  // Initialize editor
  useEffect(() => {
    if (!containerRef.current) return;

    // Create state
    const state = EditorState.create({
      doc: initialValue,
      extensions: buildExtensions(),
    });

    // Create view
    const view = new EditorView({
      state,
      parent: containerRef.current,
    });

    viewRef.current = view;
    setMounted(true);

    // Auto-focus
    if (autoFocus) {
      view.focus();
    }

    // Cleanup
    return () => {
      view.destroy();
      viewRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  // Note: Dynamic reconfiguration would require Compartments.
  // For now, options are set at mount time. If options need to change,
  // the parent should remount the component with a new key.

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
    viewRef.current?.focus();
  }, []);

  // Check if focused
  const isFocused = useCallback((): boolean => {
    return viewRef.current?.hasFocus ?? false;
  }, []);

  return {
    containerRef,
    view: viewRef.current,
    getValue,
    setValue,
    focus,
    isFocused,
  };
}

/**
 * Configure Vim mode defaults
 * Call this once at app startup if using vim mode
 */
export function configureVimDefaults(): void {
  // Set default options
  Vim.defineOption('number', true, 'boolean');

  // Example: Custom mappings can be added here
  // Vim.map('jj', '<Esc>', 'insert');
}

export default useCodeMirror;
