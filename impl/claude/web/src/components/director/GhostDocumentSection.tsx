/**
 * GhostDocumentSection — The Negative Space
 *
 * Displays ghost documents (placeholders created from dangling references).
 *
 * Philosophy:
 *   "The file is a lie. There is only the graph."
 *   Ghosts are entities that SHOULD exist but DON'T yet.
 *   They are visible but de-prioritized — 60% opacity, dashed borders.
 *
 * Affordances:
 *   - Click to view/edit the ghost (fill in content)
 *   - Upload to reconcile (replace ghost with real doc)
 *   - Shows origin (which spec created this ghost)
 */

import { useCallback, useMemo } from 'react';

import {
  type DocumentEntry,
  isGhostDocument,
  ghostHasDraft,
} from '../../api/director';

import './GhostDocumentSection.css';

// =============================================================================
// Types
// =============================================================================

interface GhostDocumentSectionProps {
  documents: DocumentEntry[];
  onSelectDocument?: (path: string) => void;
  onUploadToReconcile?: (path: string) => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

// =============================================================================
// Component
// =============================================================================

export function GhostDocumentSection({
  documents,
  onSelectDocument,
  onUploadToReconcile,
  collapsed = false,
  onToggleCollapse,
}: GhostDocumentSectionProps) {
  // Filter to only ghost documents
  const ghosts = useMemo(
    () => documents.filter(isGhostDocument),
    [documents]
  );

  // Group ghosts by origin spec for better organization
  const ghostsByOrigin = useMemo(() => {
    const groups = new Map<string, DocumentEntry[]>();

    for (const ghost of ghosts) {
      const origin = ghost.ghost_metadata?.created_by_path ?? 'unknown';
      const existing = groups.get(origin) ?? [];
      groups.set(origin, [...existing, ghost]);
    }

    return groups;
  }, [ghosts]);

  const handleSelect = useCallback(
    (path: string) => {
      onSelectDocument?.(path);
    },
    [onSelectDocument]
  );

  const handleUpload = useCallback(
    (e: React.MouseEvent, path: string) => {
      e.stopPropagation();
      onUploadToReconcile?.(path);
    },
    [onUploadToReconcile]
  );

  if (ghosts.length === 0) {
    return null;
  }

  return (
    <section className="ghost-section" data-collapsed={collapsed}>
      {/* Header */}
      <button
        className="ghost-section__header"
        onClick={onToggleCollapse}
        aria-expanded={!collapsed}
      >
        <span className="ghost-section__icon">◭</span>
        <span className="ghost-section__title">
          Ghosts
          <span className="ghost-section__count">{ghosts.length}</span>
        </span>
        <span className="ghost-section__hint">
          Placeholders from dangling references
        </span>
        <span className="ghost-section__toggle">
          {collapsed ? '▶' : '▼'}
        </span>
      </button>

      {/* Content */}
      {!collapsed && (
        <div className="ghost-section__content">
          {/* Explanation for first-time users */}
          <p className="ghost-section__explainer">
            These documents were created as placeholders when other specs referenced them.
            You can <strong>fill in content</strong> or <strong>upload the real document</strong> to reconcile.
          </p>

          {/* Ghost list grouped by origin */}
          {Array.from(ghostsByOrigin.entries()).map(([origin, originGhosts]) => (
            <div key={origin} className="ghost-group">
              <div className="ghost-group__origin">
                <span className="ghost-group__origin-label">Referenced by:</span>
                <span className="ghost-group__origin-path">{origin}</span>
              </div>

              <ul className="ghost-list">
                {originGhosts.map((ghost) => (
                  <GhostDocumentRow
                    key={ghost.path}
                    ghost={ghost}
                    onSelect={handleSelect}
                    onUpload={handleUpload}
                  />
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

// =============================================================================
// Ghost Row Component
// =============================================================================

interface GhostDocumentRowProps {
  ghost: DocumentEntry;
  onSelect: (path: string) => void;
  onUpload: (e: React.MouseEvent, path: string) => void;
}

function GhostDocumentRow({ ghost, onSelect, onUpload }: GhostDocumentRowProps) {
  const hasDraft = ghostHasDraft(ghost);
  const metadata = ghost.ghost_metadata;

  return (
    <li
      className="ghost-row"
      data-has-draft={hasDraft}
      onClick={() => onSelect(ghost.path)}
    >
      <div className="ghost-row__main">
        <span className="ghost-row__path">{ghost.path}</span>
        {metadata?.context && (
          <span className="ghost-row__context">{metadata.context}</span>
        )}
      </div>

      <div className="ghost-row__status">
        {hasDraft ? (
          <span className="ghost-row__badge ghost-row__badge--draft">
            Has draft
          </span>
        ) : (
          <span className="ghost-row__badge ghost-row__badge--empty">
            Empty
          </span>
        )}

        <GhostOriginBadge origin={metadata?.origin ?? 'parsed_reference'} />
      </div>

      <div className="ghost-row__actions">
        <button
          className="ghost-row__action ghost-row__action--edit"
          onClick={(e) => {
            e.stopPropagation();
            onSelect(ghost.path);
          }}
          title="Fill in content"
        >
          ◐
        </button>
        <button
          className="ghost-row__action ghost-row__action--upload"
          onClick={(e) => onUpload(e, ghost.path)}
          title="Upload to reconcile"
        >
          ↑
        </button>
      </div>
    </li>
  );
}

// =============================================================================
// Origin Badge
// =============================================================================

interface GhostOriginBadgeProps {
  origin: string;
}

function GhostOriginBadge({ origin }: GhostOriginBadgeProps) {
  const label = {
    parsed_reference: 'Ref',
    anticipated: 'Anticipated',
    user_created: 'Manual',
  }[origin] ?? origin;

  return (
    <span className="ghost-origin-badge" data-origin={origin}>
      {label}
    </span>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default GhostDocumentSection;
