/**
 * MarkdownEditor Component
 *
 * A STARK BIOME-themed markdown editor using CodeMirror 6.
 * Supports vim bindings, syntax highlighting, and line wrapping.
 */

import React, { useEffect, forwardRef, useImperativeHandle } from 'react';
import { useCodeMirror, UseCodeMirrorOptions } from './useCodeMirror';
import './MarkdownEditor.css';

export interface MarkdownEditorProps {
  /** Editor content */
  value?: string;
  /** Called when content changes */
  onChange?: (value: string) => void;
  /** Called on blur */
  onBlur?: () => void;
  /** Enable vim mode */
  vimMode?: boolean;
  /** Read-only mode */
  readonly?: boolean;
  /** Placeholder text when empty */
  placeholder?: string;
  /** Auto-focus on mount */
  autoFocus?: boolean;
  /** Additional CSS class */
  className?: string;
  /** Minimum height */
  minHeight?: string | number;
  /** Maximum height (for scrolling) */
  maxHeight?: string | number;
  /** Fill parent height */
  fillHeight?: boolean;
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
}

/**
 * Markdown editor with STARK BIOME styling
 */
export const MarkdownEditor = forwardRef<MarkdownEditorRef, MarkdownEditorProps>(
  function MarkdownEditor(props, ref) {
    const {
      value = '',
      onChange,
      onBlur,
      vimMode = false,
      readonly = false,
      placeholder = '',
      autoFocus = false,
      className = '',
      minHeight,
      maxHeight,
      fillHeight = false,
    } = props;

    const options: UseCodeMirrorOptions = {
      initialValue: value,
      onChange,
      onBlur,
      language: 'markdown',
      vimMode,
      readonly,
      placeholder,
      autoFocus,
      lineWrapping: true,
    };

    const { containerRef, getValue, setValue, focus, isFocused } = useCodeMirror(options);

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
      vimMode && 'markdown-editor--vim',
      readonly && 'markdown-editor--readonly',
      fillHeight && 'markdown-editor--fill',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={containerClass} style={style}>
        <div ref={containerRef} className="markdown-editor__container" />
      </div>
    );
  }
);

export default MarkdownEditor;
