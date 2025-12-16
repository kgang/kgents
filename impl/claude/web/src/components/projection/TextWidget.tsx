/**
 * TextWidget: Text display with variants.
 *
 * Renders text content with support for:
 * - Variants: plain, code, heading, quote, markdown
 * - Truncation with ellipsis
 * - Syntax highlighting for code
 */

import React from 'react';

export type TextVariant = 'plain' | 'code' | 'heading' | 'quote' | 'markdown';

export interface TextWidgetProps {
  content: string;
  variant?: TextVariant;
  /** Truncate after N lines (0 = no truncation) */
  truncateLines?: number;
  /** Highlight pattern (regex string) */
  highlight?: string;
}

/**
 * Get variant-specific styles.
 */
function getVariantStyles(variant: TextVariant): React.CSSProperties {
  switch (variant) {
    case 'code':
      return {
        fontFamily: 'monospace',
        backgroundColor: '#f3f4f6',
        padding: '12px',
        borderRadius: '4px',
        whiteSpace: 'pre-wrap',
        overflowX: 'auto',
      };
    case 'heading':
      return {
        fontSize: '1.5rem',
        fontWeight: 700,
        marginBottom: '8px',
      };
    case 'quote':
      return {
        borderLeft: '4px solid #9ca3af',
        paddingLeft: '16px',
        fontStyle: 'italic',
        color: '#4b5563',
      };
    case 'markdown':
      return {
        lineHeight: 1.6,
      };
    case 'plain':
    default:
      return {
        lineHeight: 1.5,
      };
  }
}

/**
 * Apply highlight to content.
 */
function highlightContent(content: string, pattern: string): React.ReactNode {
  try {
    const regex = new RegExp(`(${pattern})`, 'gi');
    const parts = content.split(regex);

    return parts.map((part, i) =>
      regex.test(part) ? (
        <mark
          key={i}
          style={{
            backgroundColor: '#fef08a',
            padding: '0 2px',
            borderRadius: '2px',
          }}
        >
          {part}
        </mark>
      ) : (
        part
      )
    );
  } catch {
    // Invalid regex, return as-is
    return content;
  }
}

export function TextWidget({
  content,
  variant = 'plain',
  truncateLines = 0,
  highlight,
}: TextWidgetProps) {
  const styles = getVariantStyles(variant);

  const truncateStyles: React.CSSProperties =
    truncateLines > 0
      ? {
          display: '-webkit-box',
          WebkitLineClamp: truncateLines,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }
      : {};

  const displayContent = highlight ? highlightContent(content, highlight) : content;

  const Tag = variant === 'heading' ? 'h2' : variant === 'quote' ? 'blockquote' : 'div';

  return (
    <Tag
      className={`kgents-text-widget kgents-text-${variant}`}
      style={{ ...styles, ...truncateStyles }}
    >
      {variant === 'code' ? <code>{displayContent}</code> : displayContent}
    </Tag>
  );
}

export default TextWidget;
