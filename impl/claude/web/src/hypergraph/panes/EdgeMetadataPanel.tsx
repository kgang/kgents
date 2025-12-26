/**
 * EdgeMetadataPanel -- Rich edge information sidebar
 *
 * Provides an accessible, detailed view of all edges connected to the current node.
 * Designed for users who want more context than the compact EdgeGutter badges.
 *
 * Features:
 * - Grouped by edge type (derives_from, implements, tests, references, contradicts)
 * - Expandable sections with full edge details
 * - Confidence visualization with color coding
 * - Click to navigate to connected nodes
 * - Witness mark indicators
 *
 * "The file is a lie. There is only the graph."
 */

import { memo, useState } from 'react';
import type { Edge, EdgeType } from '../state/types';
import './EdgeMetadataPanel.css';

// =============================================================================
// Types
// =============================================================================

export interface EdgeMetadataPanelProps {
  /** Incoming edges (to this node) */
  incomingEdges: Edge[];
  /** Outgoing edges (from this node) */
  outgoingEdges: Edge[];
  /** Current node path */
  currentNodePath?: string;
  /** Navigate to a connected node */
  onEdgeClick?: (edge: Edge) => void;
  /** Panel open state */
  isOpen: boolean;
  /** Toggle panel */
  onToggle: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const EDGE_TYPE_INFO: Record<EdgeType, { label: string; icon: string; description: string }> = {
  derives_from: {
    label: 'Derives From',
    icon: '<<',
    description: 'This node derives from or builds upon',
  },
  implements: {
    label: 'Implements',
    icon: '>>',
    description: 'Implementation relationships',
  },
  tests: {
    label: 'Tests',
    icon: 'T',
    description: 'Test coverage relationships',
  },
  references: {
    label: 'References',
    icon: '@',
    description: 'General references',
  },
  contradicts: {
    label: 'Contradicts',
    icon: '!!',
    description: 'Conflicting or contradictory relationships',
  },
  extends: {
    label: 'Extends',
    icon: '^',
    description: 'Inheritance or extension relationships',
  },
  contains: {
    label: 'Contains',
    icon: '{}',
    description: 'Container relationships',
  },
  uses: {
    label: 'Uses',
    icon: '->',
    description: 'Dependency relationships',
  },
  defines: {
    label: 'Defines',
    icon: ':=',
    description: 'Definition relationships',
  },
};

const ORIGIN_LABELS: Record<string, string> = {
  git: 'Git',
  ast: 'AST',
  user: 'User',
  llm: 'LLM',
  import: 'Import',
};

// =============================================================================
// Helpers
// =============================================================================

function getConfidenceLevel(confidence: number | undefined): 'high' | 'medium' | 'low' | 'unknown' {
  if (confidence === undefined) return 'unknown';
  if (confidence >= 0.8) return 'high';
  if (confidence >= 0.5) return 'medium';
  return 'low';
}

function formatConfidence(confidence: number | undefined): string {
  if (confidence === undefined) return 'Unknown';
  return `${Math.round(confidence * 100)}%`;
}

function getNodeName(path: string): string {
  const parts = path.split('/');
  const filename = parts[parts.length - 1] || path;
  return filename.replace(/\.(md|py|ts|tsx|js|jsx)$/, '');
}

function groupEdgesByType(edges: Edge[]): Map<EdgeType, Edge[]> {
  const grouped = new Map<EdgeType, Edge[]>();
  for (const edge of edges) {
    const existing = grouped.get(edge.type) || [];
    existing.push(edge);
    grouped.set(edge.type, existing);
  }
  return grouped;
}

// =============================================================================
// Sub-components
// =============================================================================

interface EdgeItemProps {
  edge: Edge;
  direction: 'incoming' | 'outgoing';
  currentNodePath?: string;
  onEdgeClick?: (edge: Edge) => void;
}

const EdgeItem = memo(function EdgeItem({
  edge,
  direction,
  currentNodePath: _currentNodePath,
  onEdgeClick,
}: EdgeItemProps) {
  const targetPath = direction === 'incoming' ? edge.source : edge.target;
  const confidenceLevel = getConfidenceLevel(edge.confidence);

  return (
    <button
      className={`edge-metadata-panel__edge edge-metadata-panel__edge--${confidenceLevel}`}
      onClick={() => onEdgeClick?.(edge)}
      title={`Navigate to ${targetPath}`}
    >
      <div className="edge-metadata-panel__edge-main">
        <span className="edge-metadata-panel__edge-name">{getNodeName(targetPath)}</span>
        {edge.markId && (
          <span className="edge-metadata-panel__witness-mark" title="Has witness mark">
            +
          </span>
        )}
      </div>

      <div className="edge-metadata-panel__edge-meta">
        <span className={`edge-metadata-panel__confidence edge-metadata-panel__confidence--${confidenceLevel}`}>
          {formatConfidence(edge.confidence)}
        </span>

        {edge.origin && (
          <span className="edge-metadata-panel__origin" title={`Origin: ${edge.origin}`}>
            {ORIGIN_LABELS[edge.origin] || edge.origin}
          </span>
        )}
      </div>

      <div className="edge-metadata-panel__edge-path" title={targetPath}>
        {targetPath}
      </div>

      {edge.context && (
        <div className="edge-metadata-panel__edge-context" title={edge.context}>
          {edge.context}
        </div>
      )}
    </button>
  );
});

interface EdgeGroupProps {
  type: EdgeType;
  edges: Edge[];
  direction: 'incoming' | 'outgoing';
  currentNodePath?: string;
  onEdgeClick?: (edge: Edge) => void;
  defaultExpanded?: boolean;
}

const EdgeGroup = memo(function EdgeGroup({
  type,
  edges,
  direction,
  currentNodePath,
  onEdgeClick,
  defaultExpanded = false,
}: EdgeGroupProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const info = EDGE_TYPE_INFO[type];

  // Calculate average confidence for the group
  const edgesWithConfidence = edges.filter((e): e is Edge & { confidence: number } => e.confidence !== undefined);
  const avgConfidence = edgesWithConfidence.length > 0
    ? edgesWithConfidence.reduce((sum, e) => sum + e.confidence, 0) / edgesWithConfidence.length
    : undefined;
  const confidenceLevel = getConfidenceLevel(avgConfidence);

  // Check if any edge has a witness mark
  const hasWitness = edges.some((e) => e.markId);

  return (
    <div className={`edge-metadata-panel__group edge-metadata-panel__group--${type}`}>
      <button
        className="edge-metadata-panel__group-header"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <span className="edge-metadata-panel__group-icon">{info.icon}</span>
        <span className="edge-metadata-panel__group-label">{info.label}</span>
        <span className="edge-metadata-panel__group-count">{edges.length}</span>
        {hasWitness && <span className="edge-metadata-panel__group-witness">+</span>}
        <span className={`edge-metadata-panel__group-confidence edge-metadata-panel__group-confidence--${confidenceLevel}`}>
          {formatConfidence(avgConfidence)}
        </span>
        <span className="edge-metadata-panel__group-toggle">{expanded ? '-' : '+'}</span>
      </button>

      {expanded && (
        <div className="edge-metadata-panel__group-content">
          {edges.map((edge) => (
            <EdgeItem
              key={edge.id}
              edge={edge}
              direction={direction}
              currentNodePath={currentNodePath}
              onEdgeClick={onEdgeClick}
            />
          ))}
        </div>
      )}
    </div>
  );
});

interface EdgeDirectionSectionProps {
  title: string;
  edges: Edge[];
  direction: 'incoming' | 'outgoing';
  currentNodePath?: string;
  onEdgeClick?: (edge: Edge) => void;
}

const EdgeDirectionSection = memo(function EdgeDirectionSection({
  title,
  edges,
  direction,
  currentNodePath,
  onEdgeClick,
}: EdgeDirectionSectionProps) {
  const grouped = groupEdgesByType(edges);

  // Sort by importance: derives_from first, then contradicts, then others
  const sortOrder: EdgeType[] = [
    'derives_from',
    'contradicts',
    'implements',
    'tests',
    'extends',
    'references',
    'contains',
    'uses',
    'defines',
  ];

  const sortedTypes = Array.from(grouped.keys()).sort((a, b) => {
    const aIndex = sortOrder.indexOf(a);
    const bIndex = sortOrder.indexOf(b);
    return aIndex - bIndex;
  });

  if (sortedTypes.length === 0) {
    return (
      <div className="edge-metadata-panel__section">
        <h4 className="edge-metadata-panel__section-title">{title}</h4>
        <p className="edge-metadata-panel__empty">No edges</p>
      </div>
    );
  }

  return (
    <div className="edge-metadata-panel__section">
      <h4 className="edge-metadata-panel__section-title">
        {title}
        <span className="edge-metadata-panel__section-count">({edges.length})</span>
      </h4>
      {sortedTypes.map((type) => {
        const typeEdges = grouped.get(type);
        if (!typeEdges) return null;
        return (
          <EdgeGroup
            key={type}
            type={type}
            edges={typeEdges}
            direction={direction}
            currentNodePath={currentNodePath}
            onEdgeClick={onEdgeClick}
            defaultExpanded={type === 'derives_from' || type === 'contradicts'}
          />
        );
      })}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const EdgeMetadataPanel = memo(function EdgeMetadataPanel({
  incomingEdges,
  outgoingEdges,
  currentNodePath,
  onEdgeClick,
  isOpen,
  onToggle,
}: EdgeMetadataPanelProps) {
  const totalEdges = incomingEdges.length + outgoingEdges.length;

  return (
    <aside
      className={`edge-metadata-panel ${isOpen ? 'edge-metadata-panel--open' : 'edge-metadata-panel--closed'}`}
      aria-label="Edge metadata panel"
    >
      {/* Toggle button */}
      <button
        className="edge-metadata-panel__toggle"
        onClick={onToggle}
        aria-expanded={isOpen}
        aria-label={isOpen ? 'Close edge panel' : 'Open edge panel'}
        title={isOpen ? 'Close edge panel (gE)' : 'Open edge panel (gE)'}
      >
        <span className="edge-metadata-panel__toggle-icon">{isOpen ? '>' : '<'}</span>
        <span className="edge-metadata-panel__toggle-label">Edges</span>
        {!isOpen && totalEdges > 0 && (
          <span className="edge-metadata-panel__toggle-count">{totalEdges}</span>
        )}
      </button>

      {/* Panel content */}
      {isOpen && (
        <div className="edge-metadata-panel__content">
          {/* Header */}
          <div className="edge-metadata-panel__header">
            <h3 className="edge-metadata-panel__title">Edge Graph</h3>
            <span className="edge-metadata-panel__total">{totalEdges} edges</span>
          </div>

          {/* Legend */}
          <div className="edge-metadata-panel__legend">
            <span className="edge-metadata-panel__legend-item edge-metadata-panel__legend-item--high">
              High (80%+)
            </span>
            <span className="edge-metadata-panel__legend-item edge-metadata-panel__legend-item--medium">
              Med (50-80%)
            </span>
            <span className="edge-metadata-panel__legend-item edge-metadata-panel__legend-item--low">
              Low (&lt;50%)
            </span>
          </div>

          {/* Incoming edges */}
          <EdgeDirectionSection
            title="Incoming"
            edges={incomingEdges}
            direction="incoming"
            currentNodePath={currentNodePath}
            onEdgeClick={onEdgeClick}
          />

          {/* Outgoing edges */}
          <EdgeDirectionSection
            title="Outgoing"
            edges={outgoingEdges}
            direction="outgoing"
            currentNodePath={currentNodePath}
            onEdgeClick={onEdgeClick}
          />

          {/* Hint */}
          <div className="edge-metadata-panel__hint">
            <kbd>gE</kbd> Toggle panel | Click edge to navigate
          </div>
        </div>
      )}
    </aside>
  );
});

export default EdgeMetadataPanel;
