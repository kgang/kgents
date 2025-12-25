/**
 * GenericContent — Fallback for unknown resource types
 *
 * Shows JSON-formatted content for any resource type we don't have
 * a specific renderer for.
 *
 * See spec/protocols/portal-resource-system.md §6.2
 */

import './tokens.css';

// =============================================================================
// Types
// =============================================================================

export interface GenericContentProps {
  /** Content to display */
  content: unknown;
  /** Compact mode */
  compact?: boolean;
}

// =============================================================================
// Component
// =============================================================================

/**
 * GenericContent — JSON fallback renderer
 */
export function GenericContent({ content, compact = false }: GenericContentProps) {
  const maxLines = compact ? 10 : 30;

  // Format content as JSON
  const formatted = JSON.stringify(content, null, 2);
  const lines = formatted.split('\n');
  const displayLines = lines.slice(0, maxLines);
  const hasMore = lines.length > maxLines;

  return (
    <div className="generic-content">
      <div className="generic-content__header">
        <span className="generic-content__label">Content</span>
        <span className="generic-content__type">
          {typeof content === 'object' && content !== null
            ? Array.isArray(content)
              ? 'Array'
              : 'Object'
            : typeof content}
        </span>
      </div>

      <pre className="generic-content__pre">
        <code className="generic-content__code">
          {displayLines.join('\n')}
        </code>
      </pre>

      {hasMore && (
        <div className="generic-content__footer">
          <span className="generic-content__more">
            +{lines.length - maxLines} more lines
          </span>
        </div>
      )}
    </div>
  );
}

export default GenericContent;
