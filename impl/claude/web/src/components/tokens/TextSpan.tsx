/**
 * TextSpan — Plain text renderer for non-token content.
 *
 * This is the fallback renderer for text that isn't a meaning token.
 * It preserves whitespace and renders inline.
 *
 * Cosmetic Features (not tokenized):
 * - Markdown headers (lines starting with #) get styled typography
 * - Bold (**text**) and italic (*text*) get inline styling
 */

import { memo, useMemo, Fragment } from 'react';

import './tokens.css';

interface TextSpanProps {
  content: string;
  className?: string;
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
 * Render a single line, detecting headers cosmetically.
 */
function renderLine(line: string, index: number): React.ReactNode {
  const level = getHeaderLevel(line);

  if (level > 0) {
    const content = getHeaderContent(line);
    return (
      <span
        key={index}
        className={`text-span__header text-span__header--h${level}`}
        role="heading"
        aria-level={level}
      >
        {content}
      </span>
    );
  }

  // Regular text line
  return line;
}

export const TextSpan = memo(function TextSpan({ content, className }: TextSpanProps) {
  // Split content into lines and detect headers
  const rendered = useMemo(() => {
    // Collapse pure whitespace to single newline for doc-like density
    const trimmed = content.replace(/^\n+/, '\n').replace(/\n+$/, '\n');

    // If only whitespace, render minimal
    if (!trimmed.trim()) {
      return trimmed.includes('\n') ? '\n' : '';
    }

    // Check if content has any headers worth processing
    if (!trimmed.includes('#')) {
      return trimmed;
    }

    const lines = trimmed.split('\n');
    const result: React.ReactNode[] = [];

    lines.forEach((line, index) => {
      if (index > 0) {
        result.push('\n');
      }
      result.push(renderLine(line, index));
    });

    return result;
  }, [content]);

  return (
    <span className={`text-span ${className ?? ''}`}>
      {Array.isArray(rendered)
        ? rendered.map((node, i) => <Fragment key={i}>{node}</Fragment>)
        : rendered}
    </span>
  );
});
