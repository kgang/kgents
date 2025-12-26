/**
 * Minimap — VSCode-style minimap for NORMAL mode
 *
 * A condensed mini-render of the document text with selective highlighting
 * for major sections (H1 headers only).
 *
 * Philosophy:
 * - 90% steel (mini-rendered text lines as thin bars)
 * - 10% earned glow (H1 headers as labeled landmarks)
 * - Only visible in NORMAL mode (reading/navigation)
 * - Clickable to jump to locations
 *
 * Visual Strategy:
 * - Text lines: Thin gray bars proportional to line length
 * - H1 headers: Labeled landmarks with readable text (first ~8-10 chars)
 * - Empty lines: Gaps in the minimap
 * - Current viewport: Gold outline band
 */

import { memo, useCallback, useEffect, useRef, useState } from 'react';
import type { SceneGraph } from '../components/tokens/types';
import './Minimap.css';

interface MinimapProps {
  /** Parsed SceneGraph (can extract raw content if needed) */
  sceneGraph: SceneGraph | null;
  /** Raw document content for text mini-render */
  content?: string;
  /** Current scroll position (0-1) */
  scrollTop?: number;
  /** Viewport height as fraction of total (0-1) */
  viewportRatio?: number;
  /** Callback when clicking on minimap to jump to position */
  onJumpToPosition?: (position: number) => void;
  /** Optional className */
  className?: string;
}

interface MinimapLine {
  /** Line index (for key) */
  index: number;
  /** Vertical position (0-1) */
  position: number;
  /** Line type */
  type: 'h1' | 'text' | 'empty';
  /** Text content (for H1 headers, truncated) */
  text?: string;
  /** Bar width as percentage (for text lines, based on length) */
  width?: number;
}

/**
 * Extract text lines from raw content for mini-rendering.
 * Returns structured line data for visualization.
 *
 * IMPORTANT: Ignores headers inside code blocks (``` fences).
 * Python comments like `# comment` inside code blocks are NOT headers.
 */
function extractLines(content: string): MinimapLine[] {
  if (!content) return [];

  const lines = content.split('\n');
  const result: MinimapLine[] = [];

  // Calculate max line length for proportional widths
  const maxLength = Math.max(...lines.map(line => line.length), 1);

  // Track whether we're inside a fenced code block
  let inCodeBlock = false;

  lines.forEach((line, index) => {
    const position = index / Math.max(lines.length - 1, 1);
    const trimmed = line.trim();

    // Toggle code block state when encountering ``` fence markers
    // Must check BEFORE any other processing so fence lines themselves
    // are treated as regular text, not headers
    if (trimmed.startsWith('```')) {
      inCodeBlock = !inCodeBlock;
      // Treat fence line as regular text
      const width = Math.max((trimmed.length / maxLength) * 100, 10);
      result.push({
        index,
        position,
        type: 'text',
        width,
      });
      return;
    }

    // Empty line
    if (!trimmed) {
      result.push({
        index,
        position,
        type: 'empty',
      });
      return;
    }

    // H1 header (# Title) - ONLY match single # followed by space
    // Negative lookahead (?!#) ensures we don't match ##, ###, etc.
    // IMPORTANT: Only detect headers OUTSIDE of code blocks
    if (!inCodeBlock) {
      const h1Match = trimmed.match(/^#(?!#)\s+(.+)$/);
      if (h1Match) {
        const headerText = h1Match[1].trim();
        const truncated = headerText.length > 10
          ? headerText.substring(0, 10) + '...'
          : headerText;

        result.push({
          index,
          position,
          type: 'h1',
          text: truncated,
        });
        return;
      }
    }

    // Regular text line - calculate proportional width
    const width = Math.max((trimmed.length / maxLength) * 100, 10); // Min 10% width

    result.push({
      index,
      position,
      type: 'text',
      width,
    });
  });

  return result;
}

/**
 * Minimap component - shows document structure as mini-rendered text
 */
export const Minimap = memo(function Minimap({
  sceneGraph: _sceneGraph,
  content = '',
  scrollTop = 0,
  viewportRatio = 0.2,
  onJumpToPosition,
  className = '',
}: MinimapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [lines, setLines] = useState<MinimapLine[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  // Extract lines when content changes
  useEffect(() => {
    const newLines = extractLines(content);
    setLines(newLines);
  }, [content]);

  // Handle click/drag on minimap to jump to position
  const handleInteraction = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      if (!containerRef.current || !onJumpToPosition) return;

      const rect = containerRef.current.getBoundingClientRect();
      const y = event.clientY - rect.top;
      const position = Math.max(0, Math.min(1, y / rect.height));

      onJumpToPosition(position);
    },
    [onJumpToPosition]
  );

  const handleMouseDown = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      setIsDragging(true);
      handleInteraction(event);
    },
    [handleInteraction]
  );

  const handleMouseMove = useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      if (isDragging) {
        handleInteraction(event);
      }
    },
    [isDragging, handleInteraction]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Calculate viewport indicator position and height
  const viewportTop = scrollTop * 100;
  const viewportHeight = viewportRatio * 100;

  return (
    <div
      ref={containerRef}
      className={`minimap ${className}`}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
      role="slider"
      aria-label="Document minimap"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(scrollTop * 100)}
    >
      {/* Mini-rendered document lines */}
      <div className="minimap__lines" aria-hidden="true">
        {lines.map((line) => {
          if (line.type === 'empty') {
            return (
              <div
                key={line.index}
                className="minimap__line minimap__line--empty"
                style={{ top: `${line.position * 100}%` }}
              />
            );
          }

          if (line.type === 'h1') {
            return (
              <div
                key={line.index}
                className="minimap__line minimap__line--h1"
                style={{ top: `${line.position * 100}%` }}
                title={line.text}
              >
                <span className="minimap__h1-text">{line.text}</span>
              </div>
            );
          }

          // Regular text line
          return (
            <div
              key={line.index}
              className="minimap__line minimap__line--text"
              style={{
                top: `${line.position * 100}%`,
                width: `${line.width}%`,
              }}
            />
          );
        })}
      </div>

      {/* Current viewport indicator (gold band) */}
      <div
        className="minimap__viewport"
        style={{
          top: `${viewportTop}%`,
          height: `${viewportHeight}%`,
        }}
        aria-hidden="true"
      />
    </div>
  );
});
