/**
 * TextSpan — Plain text renderer for non-token content.
 *
 * This is the fallback renderer for text that isn't a meaning token.
 * It preserves whitespace and renders inline.
 *
 * Cosmetic Features (not tokenized):
 * - Markdown headers (lines starting with #) get styled typography
 * - Rich highlighting: strings, numbers, booleans, URLs, UUIDs, IPs, paths
 *   (inspired by Rich's ReprHighlighter)
 */

import { memo, useMemo, Fragment, type ReactNode } from 'react';

import { RichHighlighter, hasHighlightableContent } from './RichHighlighter';

import './tokens.css';

interface TextSpanProps {
  content: string;
  className?: string;
  /** Disable rich highlighting (for performance in large docs) */
  disableHighlight?: boolean;
}

/**
 * Detect markdown header level from line prefix.
 * Returns 0 if not a header.
 */
function getHeaderLevel(line: string): number {
  const match = line.match(/^(#{1,6})\s+/);
  if (match) {
    return match[1].length;
  }
  return 0;
}

/**
 * Strip header prefix and return content.
 */
function getHeaderContent(line: string): string {
  return line.replace(/^#{1,6}\s+/, '');
}

/**
 * Render text with rich highlighting.
 * Uses RichHighlighter for inline pattern detection.
 */
function renderWithHighlighting(text: string, key: string | number): ReactNode {
  // Optimization: skip highlighting if no patterns detected
  if (!hasHighlightableContent(text)) {
    return text;
  }
  return <RichHighlighter key={key} content={text} />;
}

/**
 * Render a single line, detecting headers cosmetically.
 * Now also applies rich highlighting to line content.
 */
function renderLine(line: string, index: number, enableHighlight: boolean): ReactNode {
  const level = getHeaderLevel(line);

  if (level > 0) {
    const headerText = getHeaderContent(line);
    return (
      <span
        key={index}
        className={`text-span__header text-span__header--h${level}`}
        role="heading"
        aria-level={level}
      >
        {enableHighlight ? renderWithHighlighting(headerText, `h-${index}`) : headerText}
      </span>
    );
  }

  // Regular text line — apply rich highlighting
  if (enableHighlight) {
    return renderWithHighlighting(line, index);
  }
  return line;
}

export const TextSpan = memo(function TextSpan({
  content,
  className,
  disableHighlight = false,
}: TextSpanProps) {
  // Split content into lines and detect headers + apply highlighting
  const rendered = useMemo(() => {
    // Collapse pure whitespace to single newline for doc-like density
    const trimmed = content.replace(/^\n+/, '\n').replace(/\n+$/, '\n');

    // If only whitespace, render minimal
    if (!trimmed.trim()) {
      return trimmed.includes('\n') ? '\n' : '';
    }

    const enableHighlight = !disableHighlight;

    // Check if content has any headers worth processing
    const hasHeaders = trimmed.includes('#');

    // Fast path: no headers and highlighting disabled
    if (!hasHeaders && !enableHighlight) {
      return trimmed;
    }

    // Fast path: no headers but highlighting enabled (single line or simple)
    if (!hasHeaders && enableHighlight && !trimmed.includes('\n')) {
      return renderWithHighlighting(trimmed, 'single');
    }

    // Full processing: split into lines
    const lines = trimmed.split('\n');
    const result: ReactNode[] = [];

    lines.forEach((line, index) => {
      if (index > 0) {
        result.push('\n');
      }
      result.push(renderLine(line, index, enableHighlight));
    });

    return result;
  }, [content, disableHighlight]);

  return (
    <span className={`text-span ${className ?? ''}`}>
      {Array.isArray(rendered)
        ? rendered.map((node, i) => <Fragment key={i}>{node}</Fragment>)
        : typeof rendered === 'string'
          ? rendered
          : rendered}
    </span>
  );
});
