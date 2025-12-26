/**
 * Edge Gutter CodeMirror Extension
 *
 * Shows inline edge annotations in the CodeMirror gutter.
 * Markers appear at specific line numbers where edges are asserted.
 *
 * Features:
 * - Gutter markers showing edge presence at specific lines
 * - Marker icons by direction: triangular arrow left (incoming), triangular arrow right (outgoing)
 * - Hover tooltip with edge type, target/source path, confidence
 * - Click marker to navigate to connected node
 * - Markers styled by confidence level (green/amber/red border)
 *
 * Architecture:
 * - Uses CodeMirror 6 gutter() extension
 * - Custom GutterMarker class for DOM rendering
 * - StateField to track edges with line numbers
 * - StateEffect for updating edge data
 */

import { Extension, StateField, StateEffect, RangeSet } from '@codemirror/state';
import { EditorView, gutter, GutterMarker } from '@codemirror/view';
import type { Edge, EdgeType } from '../../hypergraph/state/types';

// =============================================================================
// Types
// =============================================================================

/**
 * Edge with required lineNumber for gutter display.
 */
export interface LineEdge extends Edge {
  lineNumber: number;
  /** Whether this is an incoming edge (target is current node) */
  incoming: boolean;
}

/**
 * Options for the edge gutter extension.
 */
export interface EdgeGutterExtensionOptions {
  /** Initial edges to display */
  edges?: LineEdge[];
  /** Called when an edge marker is clicked */
  onEdgeClick?: (edge: LineEdge) => void;
}

// =============================================================================
// Edge Type Utilities
// =============================================================================

/**
 * Get short abbreviation for edge type (for tooltips).
 */
function getEdgeTypeLabel(type: EdgeType): string {
  const labels: Record<EdgeType, string> = {
    implements: 'implements',
    tests: 'tests',
    extends: 'extends',
    derives_from: 'derives from',
    references: 'references',
    contradicts: 'contradicts',
    contains: 'contains',
    uses: 'uses',
    defines: 'defines',
  };
  return labels[type] || type;
}

/**
 * Get confidence level class suffix.
 */
function getConfidenceLevel(confidence: number | undefined): 'high' | 'medium' | 'low' | 'unknown' {
  if (confidence === undefined) return 'unknown';
  if (confidence >= 0.8) return 'high';
  if (confidence >= 0.5) return 'medium';
  return 'low';
}

/**
 * Get the connected path (target for outgoing, source for incoming).
 */
function getConnectedPath(edge: LineEdge): string {
  return edge.incoming ? edge.source : edge.target;
}

/**
 * Format path for display (extract filename or last segment).
 */
function formatPath(path: string): string {
  const segments = path.split('/');
  const last = segments[segments.length - 1];
  // Remove extension if present
  return last.replace(/\.[^.]+$/, '');
}

// =============================================================================
// Gutter Marker
// =============================================================================

/**
 * Spacer GutterMarker to reserve gutter width when no edges present.
 */
class SpacerGutterMarker extends GutterMarker {
  toDOM(): HTMLElement {
    const spacer = document.createElement('span');
    spacer.className = 'edge-line-gutter edge-line-gutter--spacer';
    spacer.textContent = '\u00A0\u00A0'; // Two non-breaking spaces
    return spacer;
  }
}

const spacerMarker = new SpacerGutterMarker();

/**
 * Custom GutterMarker that renders an edge indicator.
 */
class EdgeGutterMarker extends GutterMarker {
  constructor(
    private edges: LineEdge[],
    private onClick?: (edge: LineEdge) => void
  ) {
    super();
  }

  toDOM(): HTMLElement {
    const wrapper = document.createElement('span');
    wrapper.className = 'edge-line-gutter';

    // Group edges by direction
    const incoming = this.edges.filter((e) => e.incoming);
    const outgoing = this.edges.filter((e) => !e.incoming);

    // Render incoming markers (left arrow)
    for (const edge of incoming) {
      wrapper.appendChild(this.createMarker(edge, true));
    }

    // Render outgoing markers (right arrow)
    for (const edge of outgoing) {
      wrapper.appendChild(this.createMarker(edge, false));
    }

    return wrapper;
  }

  private createMarker(edge: LineEdge, isIncoming: boolean): HTMLElement {
    const marker = document.createElement('span');
    const confidenceLevel = getConfidenceLevel(edge.confidence);

    marker.className = [
      'edge-line-marker',
      `edge-line-marker--${confidenceLevel}`,
      `edge-line-marker--${edge.type}`,
      isIncoming ? 'edge-line-marker--incoming' : 'edge-line-marker--outgoing',
      edge.stale ? 'edge-line-marker--stale' : '',
    ]
      .filter(Boolean)
      .join(' ');

    // Arrow icon based on direction
    marker.textContent = isIncoming ? '\u25C1' : '\u25B7'; // triangular arrow left / triangular arrow right

    // Build rich tooltip
    const connectedPath = formatPath(getConnectedPath(edge));
    const typeLabel = getEdgeTypeLabel(edge.type);
    const direction = isIncoming ? 'from' : 'to';
    const confidenceText =
      edge.confidence !== undefined ? `\nConfidence: ${Math.round(edge.confidence * 100)}%` : '';
    const contextText = edge.context ? `\n${edge.context}` : '';
    const staleText = edge.stale ? '\n(stale - target may have changed)' : '';

    marker.title = `${typeLabel} ${direction} ${connectedPath}${confidenceText}${contextText}${staleText}`;

    // Click handler
    if (this.onClick) {
      marker.style.cursor = 'pointer';
      marker.addEventListener('click', (e) => {
        e.stopPropagation();
        this.onClick!(edge);
      });
    }

    // Store edge data for external access
    marker.dataset.edgeId = edge.id;
    marker.dataset.edgeType = edge.type;

    return marker;
  }

  eq(other: EdgeGutterMarker): boolean {
    if (this.edges.length !== other.edges.length) return false;
    return this.edges.every((e, i) => e.id === other.edges[i].id);
  }
}

// =============================================================================
// State Management
// =============================================================================

/**
 * State effect to update edges.
 */
export const setEdges = StateEffect.define<LineEdge[]>();

/**
 * State field tracking edges with line numbers.
 */
const edgeGutterField = StateField.define<LineEdge[]>({
  create() {
    return [];
  },

  update(value, tr) {
    for (const effect of tr.effects) {
      if (effect.is(setEdges)) {
        return effect.value;
      }
    }
    return value;
  },
});

// =============================================================================
// Gutter Extension
// =============================================================================

/**
 * Build markers for the gutter from edge data.
 */
function buildMarkers(
  edges: LineEdge[],
  doc: { line: (n: number) => { from: number } },
  onClick?: (edge: LineEdge) => void
): RangeSet<GutterMarker> {
  // Group edges by line number
  const byLine = new Map<number, LineEdge[]>();
  for (const edge of edges) {
    const lineNum = edge.lineNumber;
    if (lineNum >= 1) {
      if (!byLine.has(lineNum)) {
        byLine.set(lineNum, []);
      }
      byLine.get(lineNum)!.push(edge);
    }
  }

  // Create markers sorted by line position
  const markers: { from: number; marker: GutterMarker }[] = [];

  for (const [lineNum, lineEdges] of byLine) {
    try {
      const line = doc.line(lineNum);
      markers.push({
        from: line.from,
        marker: new EdgeGutterMarker(lineEdges, onClick),
      });
    } catch {
      // Line number out of bounds - skip
    }
  }

  // Sort by position (required by RangeSet)
  markers.sort((a, b) => a.from - b.from);

  return RangeSet.of(markers.map((m) => m.marker.range(m.from)));
}

/**
 * Create the edge gutter extension.
 *
 * Usage:
 * ```ts
 * const extension = edgeGutterExtension({
 *   edges: edgesWithLineNumbers,
 *   onEdgeClick: (edge) => navigateToNode(edge.target)
 * });
 * ```
 */
export function edgeGutterExtension(options: EdgeGutterExtensionOptions = {}): Extension {
  const { edges: initialEdges = [], onEdgeClick } = options;

  return [
    edgeGutterField.init(() => initialEdges),

    gutter({
      class: 'cm-edge-gutter',
      markers: (view) => {
        const edges = view.state.field(edgeGutterField);
        return buildMarkers(edges, view.state.doc, onEdgeClick);
      },
      initialSpacer: () => spacerMarker,
    }),
  ];
}

// =============================================================================
// Utilities
// =============================================================================

/**
 * Update edges in an existing editor view.
 */
export function updateEdges(view: EditorView, edges: LineEdge[]): void {
  view.dispatch({
    effects: setEdges.of(edges),
  });
}

/**
 * Get current edges from editor state.
 */
export function getEdges(view: EditorView): LineEdge[] {
  try {
    return view.state.field(edgeGutterField);
  } catch {
    return [];
  }
}

/**
 * Filter edges to only those with valid line numbers.
 */
export function filterEdgesWithLineNumbers(
  edges: Edge[],
  currentPath: string
): LineEdge[] {
  return edges
    .filter((e): e is Edge & { lineNumber: number } => typeof e.lineNumber === 'number' && e.lineNumber >= 1)
    .map((e) => ({
      ...e,
      incoming: e.target === currentPath,
    }));
}
