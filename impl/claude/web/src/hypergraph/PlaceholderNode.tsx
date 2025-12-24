/**
 * PlaceholderNode — Visual representation of referenced-but-not-uploaded entities
 *
 * STARK BIOME: "90% calm, 10% delight"
 *
 * Placeholders show:
 * - Dashed border (distinct from real entities)
 * - 70% opacity (not quite there yet)
 * - "Referenced by N files" badge
 * - Upload button in context
 *
 * "The absence is as real as the presence."
 */

import { memo, useCallback } from 'react';
import { Upload, FileQuestion, Link2 } from 'lucide-react';

import './PlaceholderNode.css';

// =============================================================================
// Types
// =============================================================================

export interface PlaceholderData {
  path: string;
  referencedBy: string[];
  edgeTypes?: string[];
}

interface PlaceholderNodeProps {
  /** The placeholder data */
  placeholder: PlaceholderData;
  /** Called when user clicks to navigate to the referencing file */
  onNavigateToRef?: (path: string) => void;
  /** Called when user wants to upload this missing file */
  onUpload?: (path: string) => void;
  /** Whether this node is selected */
  isSelected?: boolean;
}

// =============================================================================
// Main Component
// =============================================================================

export const PlaceholderNode = memo(function PlaceholderNode({
  placeholder,
  onNavigateToRef,
  onUpload,
  isSelected = false,
}: PlaceholderNodeProps) {
  const { path, referencedBy } = placeholder;
  const fileName = path.split('/').pop() || path;
  const directory = path.split('/').slice(0, -1).join('/');

  const handleUploadClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onUpload?.(path);
    },
    [onUpload, path]
  );

  const handleRefClick = useCallback(
    (e: React.MouseEvent, refPath: string) => {
      e.stopPropagation();
      onNavigateToRef?.(refPath);
    },
    [onNavigateToRef]
  );

  return (
    <div
      className={`placeholder-node ${isSelected ? 'placeholder-node--selected' : ''}`}
      role="button"
      tabIndex={0}
    >
      {/* Icon */}
      <div className="placeholder-node__icon">
        <FileQuestion size={24} strokeWidth={1.5} />
      </div>

      {/* Content */}
      <div className="placeholder-node__content">
        <span className="placeholder-node__filename">{fileName}</span>
        {directory && <span className="placeholder-node__directory">{directory}</span>}
      </div>

      {/* References Badge */}
      <div className="placeholder-node__badge">
        <Link2 size={12} />
        <span>
          Referenced by {referencedBy.length} {referencedBy.length === 1 ? 'file' : 'files'}
        </span>
      </div>

      {/* Referencing Files List */}
      {referencedBy.length > 0 && (
        <div className="placeholder-node__refs">
          {referencedBy.slice(0, 3).map((ref) => (
            <button
              key={ref}
              className="placeholder-node__ref-link"
              onClick={(e) => handleRefClick(e, ref)}
              title={`Navigate to ${ref}`}
            >
              {ref.split('/').pop()}
            </button>
          ))}
          {referencedBy.length > 3 && (
            <span className="placeholder-node__ref-more">+{referencedBy.length - 3} more</span>
          )}
        </div>
      )}

      {/* Upload Action */}
      {onUpload && (
        <button className="placeholder-node__upload" onClick={handleUploadClick}>
          <Upload size={14} />
          <span>Upload</span>
        </button>
      )}

      {/* Status Indicator */}
      <div className="placeholder-node__status">
        <span className="placeholder-node__status-dot" />
        <span className="placeholder-node__status-text">Not ingested</span>
      </div>
    </div>
  );
});

// =============================================================================
// Compact Variant (for graph view)
// =============================================================================

interface PlaceholderNodeCompactProps {
  placeholder: PlaceholderData;
  onClick?: (path: string) => void;
}

export const PlaceholderNodeCompact = memo(function PlaceholderNodeCompact({
  placeholder,
  onClick,
}: PlaceholderNodeCompactProps) {
  const { path, referencedBy } = placeholder;
  const fileName = path.split('/').pop() || path;

  const handleClick = useCallback(() => {
    onClick?.(path);
  }, [onClick, path]);

  return (
    <button className="placeholder-node-compact" onClick={handleClick} title={path}>
      <FileQuestion size={14} strokeWidth={1.5} />
      <span className="placeholder-node-compact__name">{fileName}</span>
      <span className="placeholder-node-compact__count">{referencedBy.length}</span>
    </button>
  );
});

export default PlaceholderNode;
