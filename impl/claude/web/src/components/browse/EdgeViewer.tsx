/**
 * EdgeViewer — Render K-Block edge as a document
 *
 * Displays:
 * - Source and Target nodes (clickable links)
 * - Edge kind and justification
 * - Confidence score
 * - Creation timestamp
 * - Witness mark ID (if tracked)
 *
 * Philosophy: "The edge IS the proof. The mark IS the witness."
 */

import { useEffect, useState } from 'react';
import {
  Link,
  ArrowRight,
  GitMerge,
  FlaskConical,
  FileSymlink,
  Ban,
  ExternalLink,
  Clock,
  Bookmark,
  Gauge,
} from 'lucide-react';
import { edgesApi, EDGE_KIND_DISPLAY_NAMES, type EdgeDetailResponse } from '../../api/client';
import './EdgeViewer.css';

interface EdgeViewerProps {
  edgeId: string;
  onNavigate?: (path: string) => void;
}

/**
 * Get icon for edge kind.
 */
function getEdgeIcon(edgeType: string) {
  switch (edgeType) {
    case 'derives_from':
      return <ArrowRight size={20} />;
    case 'implements':
      return <GitMerge size={20} />;
    case 'tests':
      return <FlaskConical size={20} />;
    case 'references':
      return <FileSymlink size={20} />;
    case 'contradicts':
      return <Ban size={20} />;
    default:
      return <Link size={20} />;
  }
}

/**
 * Get CSS class for edge kind.
 */
function getEdgeKindClass(edgeType: string): string {
  switch (edgeType) {
    case 'derives_from':
      return 'edge-viewer__kind--derives';
    case 'implements':
      return 'edge-viewer__kind--implements';
    case 'tests':
      return 'edge-viewer__kind--tests';
    case 'references':
      return 'edge-viewer__kind--references';
    case 'contradicts':
      return 'edge-viewer__kind--contradicts';
    default:
      return 'edge-viewer__kind--default';
  }
}

/**
 * Format confidence as percentage with color.
 */
function formatConfidence(confidence: number): { text: string; level: string } {
  const percent = Math.round(confidence * 100);
  let level = 'low';
  if (confidence >= 0.9) level = 'high';
  else if (confidence >= 0.7) level = 'medium';
  return { text: `${percent}%`, level };
}

/**
 * EdgeViewer component.
 */
export function EdgeViewer({ edgeId, onNavigate }: EdgeViewerProps) {
  const [edge, setEdge] = useState<EdgeDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadEdge() {
      setLoading(true);
      setError(null);
      try {
        const data = await edgesApi.getById(edgeId);
        setEdge(data);
      } catch (err) {
        console.error('Failed to load edge:', err);
        setError(err instanceof Error ? err.message : 'Failed to load edge');
      } finally {
        setLoading(false);
      }
    }
    loadEdge();
  }, [edgeId]);

  if (loading) {
    return (
      <div className="edge-viewer edge-viewer--loading">
        <div className="edge-viewer__spinner" />
        <span>Loading edge...</span>
      </div>
    );
  }

  if (error || !edge) {
    return (
      <div className="edge-viewer edge-viewer--error">
        <h2>Error Loading Edge</h2>
        <p>{error || 'Edge not found'}</p>
      </div>
    );
  }

  const confidence = formatConfidence(edge.confidence);
  const displayName = EDGE_KIND_DISPLAY_NAMES[edge.edge_type] || edge.edge_type;

  return (
    <div className="edge-viewer">
      {/* Header with edge type */}
      <header className="edge-viewer__header">
        <div className={`edge-viewer__kind ${getEdgeKindClass(edge.edge_type)}`}>
          {getEdgeIcon(edge.edge_type)}
          <span>{displayName}</span>
        </div>
        <div className="edge-viewer__id">
          <code>{edge.id}</code>
        </div>
      </header>

      {/* Source -> Target visualization */}
      <div className="edge-viewer__connection">
        <button
          className="edge-viewer__node edge-viewer__node--source"
          onClick={() => onNavigate?.(edge.source_path)}
          title={`Navigate to ${edge.source_path}`}
        >
          <div className="edge-viewer__node-header">
            <span className="edge-viewer__node-label">SOURCE</span>
            {edge.source_layer !== null && (
              <span className="edge-viewer__layer">L{edge.source_layer}</span>
            )}
            {edge.source_kind && (
              <span className="edge-viewer__node-kind">{edge.source_kind}</span>
            )}
          </div>
          <div className="edge-viewer__node-title">{edge.source_title}</div>
          <div className="edge-viewer__node-path">{edge.source_path}</div>
          {edge.source_preview && (
            <div className="edge-viewer__node-preview">{edge.source_preview}</div>
          )}
          <ExternalLink size={14} className="edge-viewer__node-link" />
        </button>

        <div className="edge-viewer__arrow">
          <ArrowRight size={24} />
        </div>

        <button
          className="edge-viewer__node edge-viewer__node--target"
          onClick={() => onNavigate?.(edge.target_path)}
          title={`Navigate to ${edge.target_path}`}
        >
          <div className="edge-viewer__node-header">
            <span className="edge-viewer__node-label">TARGET</span>
            {edge.target_layer !== null && (
              <span className="edge-viewer__layer">L{edge.target_layer}</span>
            )}
            {edge.target_kind && (
              <span className="edge-viewer__node-kind">{edge.target_kind}</span>
            )}
          </div>
          <div className="edge-viewer__node-title">{edge.target_title}</div>
          <div className="edge-viewer__node-path">{edge.target_path}</div>
          {edge.target_preview && (
            <div className="edge-viewer__node-preview">{edge.target_preview}</div>
          )}
          <ExternalLink size={14} className="edge-viewer__node-link" />
        </button>
      </div>

      {/* Edge metadata */}
      <div className="edge-viewer__metadata">
        {/* Context/Justification */}
        {edge.context && (
          <div className="edge-viewer__section">
            <h3>Justification</h3>
            <p className="edge-viewer__context">{edge.context}</p>
          </div>
        )}

        {/* Confidence */}
        <div className="edge-viewer__row">
          <div className="edge-viewer__stat">
            <Gauge size={16} />
            <span className="edge-viewer__stat-label">Confidence</span>
            <span className={`edge-viewer__stat-value edge-viewer__confidence--${confidence.level}`}>
              {confidence.text}
            </span>
          </div>

          {/* Timestamp */}
          {edge.created_at && (
            <div className="edge-viewer__stat">
              <Clock size={16} />
              <span className="edge-viewer__stat-label">Created</span>
              <span className="edge-viewer__stat-value">
                {new Date(edge.created_at).toLocaleString()}
              </span>
            </div>
          )}
        </div>

        {/* Witness Mark */}
        {edge.mark_id && (
          <div className="edge-viewer__section">
            <h3>Witness Mark</h3>
            <button
              className="edge-viewer__mark-link"
              onClick={() => onNavigate?.(`witness/mark/${edge.mark_id}`)}
              title="View witness mark"
            >
              <Bookmark size={16} />
              <code>{edge.mark_id}</code>
              <ExternalLink size={14} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default EdgeViewer;
