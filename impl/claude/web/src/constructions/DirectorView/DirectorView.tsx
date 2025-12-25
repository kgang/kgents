/**
 * DirectorView — Telescope + Trail composition for document management
 *
 * "Navigate the document graph. The loss IS the readiness."
 *
 * Replaces DirectorDashboard.tsx (961 LOC) with focused composition.
 *
 * Layout:
 * ┌─────────────────────────────────────────────────────────┐
 * │ Trail (document ancestry)                                │
 * ├─────────────────────────────────────────────────────────┤
 * │                                                          │
 * │  Telescope (documents as nodes)                          │
 * │  - Documents colored by processing status                │
 * │  - Relationships shown as gradients                      │
 * │                                                          │
 * ├─────────────────────────────────────────────────────────┤
 * │ [Upload Zone] (drag & drop)                              │
 * └─────────────────────────────────────────────────────────┘
 */

import { memo, useCallback, useMemo, useState } from 'react';
import { Telescope } from '../../primitives/Telescope/Telescope';
import { Trail } from '../../primitives/Trail/Trail';
import type { NodeProjection, GradientVector } from '../../primitives/Telescope/types';
import type { DocumentStatus } from '../../api/director';
import './DirectorView.css';

// =============================================================================
// Types
// =============================================================================

export interface DirectorViewProps {
  /** Documents as node projections */
  documents: NodeProjection[];

  /** Document relationships as gradients */
  relationships: Map<string, GradientVector>;

  /** Current navigation trail (document ancestry) */
  trail: string[];

  /** Selected document ID */
  selectedDocument?: string;

  /** Document click handler */
  onDocumentClick?: (docId: string) => void;

  /** Trail navigation */
  onTrailClick?: (stepIndex: number, stepId: string) => void;

  /** Upload handler */
  onUpload?: (files: File[]) => void;

  /** Canvas dimensions */
  width?: number;
  height?: number;
}

// =============================================================================
// Constants
// =============================================================================

const STATUS_COLORS: Record<DocumentStatus, string> = {
  uploaded: '#64748b', // Steel gray (waiting)
  processing: '#f59e0b', // Amber (in progress)
  ready: '#10b981', // Green (success)
  executed: '#8b5cf6', // Purple (completed)
  stale: '#94a3b8', // Light steel (old)
  failed: '#ef4444', // Red (error)
  ghost: '#475569', // Dark steel (placeholder)
};

const STATUS_LOSS_MAP: Record<DocumentStatus, number> = {
  uploaded: 0.8, // High loss (not analyzed)
  processing: 0.5, // Mid loss (working on it)
  ready: 0.2, // Low loss (ready to use)
  executed: 0.1, // Very low loss (completed)
  stale: 0.6, // Mid-high loss (needs refresh)
  failed: 1.0, // Max loss (broken)
  ghost: 0.9, // Very high loss (doesn't exist)
};

// =============================================================================
// Component
// =============================================================================

export const DirectorView = memo(function DirectorView({
  documents,
  relationships,
  trail,
  selectedDocument,
  onDocumentClick,
  onTrailClick,
  onUpload,
  width = 1200,
  height = 700,
}: DirectorViewProps) {
  // Upload state
  const [isDragging, setIsDragging] = useState(false);

  // Convert documents to telescope nodes
  const nodes = useMemo(() => {
    return documents.map((doc) => {
      // Get status from metadata (if available)
      const status = (doc as any).status as DocumentStatus | undefined;

      return {
        ...doc,
        color: status ? STATUS_COLORS[status] : doc.color,
        loss: status ? STATUS_LOSS_MAP[status] : doc.loss,
        is_focal: doc.node_id === selectedDocument,
      };
    });
  }, [documents, selectedDocument]);

  // Navigation handlers
  const handleNodeClick = useCallback(
    (nodeId: string) => {
      onDocumentClick?.(nodeId);
    },
    [onDocumentClick]
  );

  const handleNodeNavigate = useCallback(
    (nodeId: string) => {
      onDocumentClick?.(nodeId);
    },
    [onDocumentClick]
  );

  // Upload zone handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;

    // Only set dragging false if actually leaving the element
    if (x <= rect.left || x >= rect.right || y <= rect.top || y >= rect.bottom) {
      setIsDragging(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0 && onUpload) {
        onUpload(files);
      }
    },
    [onUpload]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || []);
      if (files.length > 0 && onUpload) {
        onUpload(files);
      }
    },
    [onUpload]
  );

  // Empty state
  if (documents.length === 0) {
    return (
      <div className="director-view director-view--empty">
        <div className="director-view__empty-state">
          <p className="director-view__empty-title">No documents yet</p>
          <p className="director-view__empty-subtitle">
            Upload spec files to begin. Documents auto-analyze on upload.
          </p>
          {onUpload && (
            <label className="director-view__upload-button">
              Upload Documents
              <input
                type="file"
                multiple
                accept=".md,.txt,.pdf"
                className="director-view__file-input"
                onChange={handleFileSelect}
              />
            </label>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="director-view">
      {/* Trail: Document ancestry */}
      {trail.length > 0 && (
        <div className="director-view__trail">
          <Trail
            path={trail}
            onStepClick={onTrailClick}
            currentIndex={trail.length - 1}
            compact
          />
        </div>
      )}

      {/* Telescope: Documents as nodes */}
      <div className="director-view__telescope">
        <Telescope
          nodes={nodes}
          gradients={relationships}
          onNodeClick={handleNodeClick}
          onNavigate={handleNodeNavigate}
          width={width}
          height={height - 120} // Reserve space for trail and upload
          keyboardEnabled
        />
      </div>

      {/* Upload Zone */}
      {onUpload && (
        <div
          className={`director-view__upload ${isDragging ? 'director-view__upload--dragging' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="director-view__upload-content">
            <span className="director-view__upload-icon">↑</span>
            <span className="director-view__upload-text">
              {isDragging ? 'Drop files to upload' : 'Drag files here or '}
              <label className="director-view__upload-link">
                browse
                <input
                  type="file"
                  multiple
                  accept=".md,.txt,.pdf"
                  className="director-view__file-input"
                  onChange={handleFileSelect}
                />
              </label>
            </span>
          </div>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Helpers
// =============================================================================

/**
 * Create node projection from document entry.
 * Used for transforming API responses into telescope nodes.
 */
export function documentToNode(doc: {
  path: string;
  status: DocumentStatus;
  claim_count?: number | null;
  layer?: number;
}): NodeProjection {
  // Derive layer from document metadata or default to L4 (Specs)
  const layer = doc.layer ?? 4;

  // Calculate scale from claim count (more claims = larger node)
  const claimCount = doc.claim_count ?? 0;
  const scale = 1 + Math.min(claimCount / 50, 1); // Max 2x

  return {
    node_id: doc.path,
    layer,
    position: { x: 0, y: 0 }, // Will be calculated by Telescope
    scale,
    opacity: 1.0,
    is_focal: false,
    color: STATUS_COLORS[doc.status],
    loss: STATUS_LOSS_MAP[doc.status],
  };
}

export default DirectorView;
