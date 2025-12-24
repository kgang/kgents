/**
 * RichHighlighter — Heuristic-based inline text highlighting.
 *
 * Inspired by Rich's ReprHighlighter, this module detects and colorizes
 * common patterns in plain text: strings, numbers, booleans, URLs, UUIDs,
 * file paths, and IP addresses.
 *
 * Philosophy: "The frame is humble. The content glows."
 * We use the STARK BIOME palette with subtle, non-intrusive accents.
 *
 * See: https://github.com/Textualize/rich/blob/master/rich/highlighter.py
 */

import { memo, useMemo, Fragment, type ReactNode } from 'react';

// =============================================================================
// Pattern Definitions (inspired by Rich's ReprHighlighter)
// =============================================================================

/**
 * Pattern types that can be highlighted.
 * These map to CSS classes: .rich-hl--{type}
 */
export type HighlightType =
  | 'string'
  | 'number'
  | 'boolean-true'
  | 'boolean-false'
  | 'none'
  | 'url'
  | 'uuid'
  | 'ipv4'
  | 'ipv6'
  | 'path'
  | 'eui48' // MAC address
  | 'call' // function call like foo()
  | 'brace'; // brackets, braces, parens

interface HighlightPattern {
  type: HighlightType;
  pattern: RegExp;
  priority: number; // Higher priority patterns match first
}

/**
 * Highlight patterns in priority order.
 * Higher priority patterns are matched first to avoid false positives.
 *
 * Regex patterns adapted from Rich's ReprHighlighter:
 * https://github.com/Textualize/rich/blob/master/rich/highlighter.py
 */
const PATTERNS: HighlightPattern[] = [
  // URLs (highest priority - contains other patterns)
  {
    type: 'url',
    pattern: /\b(https?|wss?|file):\/\/[^\s<>"'`\])}]+/g,
    priority: 100,
  },

  // UUIDs (high priority - specific format)
  {
    type: 'uuid',
    pattern: /\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b/g,
    priority: 95,
  },

  // IPv6 addresses (before IPv4 to catch full format)
  {
    type: 'ipv6',
    pattern:
      /\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b|\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\b|\b::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}\b/g,
    priority: 92,
  },

  // IPv4 addresses
  {
    type: 'ipv4',
    pattern: /\b(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})(?:\.(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})){3}\b/g,
    priority: 90,
  },

  // MAC addresses (EUI-48)
  {
    type: 'eui48',
    pattern: /\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b/g,
    priority: 88,
  },

  // File paths (Unix-style) — require at least 2 segments to avoid matching dates
  // Excludes patterns like /01/2024 (date) but matches /home/user, /etc/nginx
  {
    type: 'path',
    pattern: /\B(?:\/(?:[a-zA-Z_][\w.-]*|\.\w+)){2,}\/?/g,
    priority: 85,
  },

  // Strings (single, double, triple quotes - with optional b prefix for bytes)
  // Triple quotes first
  {
    type: 'string',
    pattern: /b?"""[\s\S]*?"""|b?'''[\s\S]*?'''/g,
    priority: 82,
  },
  // Single/double quotes (not greedy, respects escapes)
  {
    type: 'string',
    pattern: /b?"(?:[^"\\]|\\.)*"|b?'(?:[^'\\]|\\.)*'/g,
    priority: 80,
  },

  // Booleans (Python/JS style)
  {
    type: 'boolean-true',
    pattern: /\b(?:True|true)\b/g,
    priority: 75,
  },
  {
    type: 'boolean-false',
    pattern: /\b(?:False|false)\b/g,
    priority: 75,
  },

  // None/null/undefined
  {
    type: 'none',
    pattern: /\b(?:None|null|undefined)\b/g,
    priority: 70,
  },

  // Function calls
  {
    type: 'call',
    pattern: /\b[a-zA-Z_]\w*(?=\()/g,
    priority: 65,
  },

  // Numbers (integers, floats, hex, scientific notation)
  // Hex numbers
  {
    type: 'number',
    pattern: /\b0x[0-9a-fA-F]+\b/g,
    priority: 62,
  },
  // Scientific notation and floats
  {
    type: 'number',
    pattern: /\b-?\d+\.?\d*(?:e[+-]?\d+)?\b/gi,
    priority: 60,
  },

  // Braces, brackets, parentheses
  {
    type: 'brace',
    pattern: /[[\]{}()]/g,
    priority: 50,
  },
];

// =============================================================================
// Match Interface
// =============================================================================

interface Match {
  start: number;
  end: number;
  text: string;
  type: HighlightType;
}

// =============================================================================
// Highlighting Logic
// =============================================================================

/**
 * Find all matches in text, handling overlapping patterns by priority.
 */
function findMatches(text: string): Match[] {
  const matches: Match[] = [];
  const covered = new Set<number>(); // Track covered positions

  // Sort patterns by priority (highest first)
  const sortedPatterns = [...PATTERNS].sort((a, b) => b.priority - a.priority);

  for (const { type, pattern } of sortedPatterns) {
    // Reset regex lastIndex
    pattern.lastIndex = 0;

    let match: RegExpExecArray | null;
    while ((match = pattern.exec(text)) !== null) {
      const start = match.index;
      const end = start + match[0].length;

      // Skip if any position is already covered
      let isOverlapping = false;
      for (let i = start; i < end; i++) {
        if (covered.has(i)) {
          isOverlapping = true;
          break;
        }
      }

      if (!isOverlapping) {
        matches.push({ start, end, text: match[0], type });
        // Mark positions as covered
        for (let i = start; i < end; i++) {
          covered.add(i);
        }
      }
    }
  }

  // Sort by start position for rendering
  return matches.sort((a, b) => a.start - b.start);
}

/**
 * Accessibility titles for highlight types.
 * Provides semantic hints for screen readers and tooltips.
 */
const TYPE_TITLES: Partial<Record<HighlightType, string>> = {
  uuid: 'UUID',
  ipv4: 'IPv4 address',
  ipv6: 'IPv6 address',
  eui48: 'MAC address',
  url: 'URL',
  path: 'File path',
  call: 'Function call',
};

/**
 * Convert matches to React nodes with highlighted spans.
 */
function renderHighlightedText(text: string, matches: Match[]): ReactNode[] {
  if (matches.length === 0) {
    return [text];
  }

  const nodes: ReactNode[] = [];
  let lastEnd = 0;

  for (const match of matches) {
    // Add plain text before this match
    if (match.start > lastEnd) {
      nodes.push(text.slice(lastEnd, match.start));
    }

    // Add highlighted span with optional accessibility title
    const title = TYPE_TITLES[match.type];
    nodes.push(
      <span
        key={`${match.start}-${match.type}`}
        className={`rich-hl rich-hl--${match.type}`}
        title={title}
      >
        {match.text}
      </span>
    );

    lastEnd = match.end;
  }

  // Add remaining text
  if (lastEnd < text.length) {
    nodes.push(text.slice(lastEnd));
  }

  return nodes;
}

// =============================================================================
// Public API
// =============================================================================

interface RichHighlighterProps {
  /** The text content to highlight */
  content: string;
  /** Additional CSS class */
  className?: string;
  /** Disable highlighting (pass through as plain text) */
  disabled?: boolean;
}

/**
 * Maximum text length for highlighting.
 * Beyond this, skip highlighting to prevent UI freezes.
 * 50KB is generous — most UI text is < 5KB.
 */
const MAX_HIGHLIGHT_LENGTH = 50_000;

/**
 * RichHighlighter component — Wraps text with inline highlighting.
 *
 * Usage:
 * ```tsx
 * <RichHighlighter content={someText} />
 * ```
 */
export const RichHighlighter = memo(function RichHighlighter({
  content,
  className,
  disabled = false,
}: RichHighlighterProps) {
  const highlighted = useMemo(() => {
    // Skip highlighting for empty, disabled, or very large content
    if (disabled || !content || content.length > MAX_HIGHLIGHT_LENGTH) {
      return content;
    }

    const matches = findMatches(content);
    if (matches.length === 0) {
      return content;
    }

    return renderHighlightedText(content, matches);
  }, [content, disabled]);

  return (
    <span className={`rich-highlighter ${className ?? ''}`}>
      {Array.isArray(highlighted)
        ? highlighted.map((node, i) => <Fragment key={i}>{node}</Fragment>)
        : highlighted}
    </span>
  );
});

/**
 * Hook for highlighting text without rendering.
 * Returns React nodes that can be composed.
 */
export function useRichHighlight(text: string): ReactNode[] {
  return useMemo(() => {
    if (!text) return [];
    const matches = findMatches(text);
    return renderHighlightedText(text, matches);
  }, [text]);
}

/**
 * Utility to check if text contains any highlightable patterns.
 * Useful for optimization (skip highlighting if no matches).
 */
export function hasHighlightableContent(text: string): boolean {
  for (const { pattern } of PATTERNS) {
    pattern.lastIndex = 0;
    if (pattern.test(text)) {
      return true;
    }
  }
  return false;
}
