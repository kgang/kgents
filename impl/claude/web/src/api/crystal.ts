/**
 * Crystal API - Witness Crystallization Visualization.
 *
 * "Crystallization is observable. Compression is public."
 *
 * Routes:
 *   time.witness.crystal.graph - Get crystal hierarchy as graph data
 *   time.witness.crystal.stream - SSE stream of crystal events
 *   time.witness.crystal.detail - Get crystal detail for expansion
 *
 * @see spec/protocols/witness-crystallization.md
 * @see services/witness/crystal_trail.py
 */

import { apiClient, AgenteseError } from './client';

// =============================================================================
// Types
// =============================================================================

/**
 * Crystal compression levels.
 * From spec/protocols/witness-crystallization.md
 */
export type CrystalLevel = 'SESSION' | 'DAY' | 'WEEK' | 'EPOCH';

/**
 * Level metadata.
 */
export const CRYSTAL_LEVELS: Record<CrystalLevel, { value: number; y: number; color: string }> = {
  SESSION: { value: 0, y: 450, color: '#3b82f6' },   // blue
  DAY: { value: 1, y: 300, color: '#22c55e' },       // green
  WEEK: { value: 2, y: 150, color: '#f59e0b' },      // amber
  EPOCH: { value: 3, y: 50, color: '#8b5cf6' },      // purple
};

/**
 * Evidence strength for crystals.
 */
export type CrystalStrength = 'weak' | 'moderate' | 'strong' | 'definitive';

/**
 * A node in the crystal hierarchy graph.
 * Compatible with TrailGraphNode for visualization.
 */
export interface CrystalGraphNode {
  /** Unique node ID */
  id: string;
  /** Node type for react-flow */
  type: 'crystal' | 'context';
  /** Position in the graph */
  position: { x: number; y: number };
  /** Node data */
  data: {
    /** Crystal ID */
    crystal_id: string;
    /** Crystal level */
    level: CrystalLevel;
    /** Level as number (0-3) */
    level_value: number;
    /** Compressed insight */
    insight: string;
    /** Why this matters */
    significance: string;
    /** Confidence score (0-1) */
    confidence: number;
    /** Number of source marks/crystals */
    source_count: number;
    /** Principles that emerged */
    principles: string[];
    /** Topics for retrieval */
    topics: string[];
    /** When crystallized */
    crystallized_at: string;

    // Trail-compatible fields
    /** AGENTESE path */
    path: string;
    /** Display name (level) */
    holon: string;
    /** Step index (level value) */
    step_index: number;
    /** Edge type */
    edge_type: string;
    /** Reasoning (significance) */
    reasoning: string | null;
    /** Whether currently selected */
    is_current: boolean;
  };
}

/**
 * An edge in the crystal hierarchy graph.
 */
export interface CrystalGraphEdge {
  /** Unique edge ID */
  id: string;
  /** Source node ID (lower level) */
  source: string;
  /** Target node ID (higher level) */
  target: string;
  /** Edge label */
  label: string;
  /** Edge type */
  type: 'compression' | 'structural' | 'semantic';
  /** Whether to animate */
  animated: boolean;
  /** Style overrides */
  style?: {
    strokeDasharray?: string;
  };
}

/**
 * Full crystal graph for visualization.
 */
export interface CrystalGraph {
  /** Graph nodes */
  nodes: CrystalGraphNode[];
  /** Graph edges */
  edges: CrystalGraphEdge[];
  /** Total crystal count */
  total_crystals: number;
  /** Count by level */
  level_counts: Record<CrystalLevel, number>;
  /** Time range covered */
  time_range: [string, string] | null;
}

/**
 * Crystal detail for expansion panel.
 */
export interface CrystalDetail {
  /** Crystal ID */
  id: string;
  /** Level name */
  level: CrystalLevel;
  /** Compressed insight */
  insight: string;
  /** Why it matters */
  significance: string;
  /** Principles that emerged */
  principles: string[];
  /** Topics for retrieval */
  topics: string[];
  /** Confidence score */
  confidence: number;
  /** Number of sources */
  source_count: number;
  /** Source mark IDs (level 0) */
  source_marks: string[];
  /** Source crystal IDs (level 1+) */
  source_crystals: string[];
  /** Mood vector */
  mood: {
    warmth: number;
    weight: number;
    tempo: number;
    texture: number;
    brightness: number;
    saturation: number;
    complexity: number;
  };
  /** When crystallized */
  crystallized_at: string;
  /** Time range covered */
  time_range: [string, string] | null;
}

/**
 * SSE crystal event types.
 */
export type CrystalEventType = 'crystal.created' | 'crystal.batch' | 'heartbeat' | 'error';

/**
 * SSE crystal event.
 */
export interface CrystalEvent {
  type: CrystalEventType;
  timestamp: string;
  data: {
    id?: string;
    level?: CrystalLevel;
    insight?: string;
    significance?: string;
    confidence?: number;
    source_count?: number;
    count?: number;
    crystals?: Array<{
      id: string;
      level: CrystalLevel;
      insight: string;
    }>;
    message?: string;
    code?: string;
  };
}

// =============================================================================
// Response Types
// =============================================================================

interface AgenteseResponse<T> {
  path: string;
  aspect: string;
  result: T;
  error?: string;
}

interface CrystalGraphResponse {
  summary: string;
  content: string;
  metadata: {
    nodes?: CrystalGraphNode[];
    edges?: CrystalGraphEdge[];
    total_crystals?: number;
    level_counts?: Record<string, number>;
    time_range?: [string, string] | null;
    mode?: 'crystal';
    error?: string;
  };
}

interface CrystalDetailResponse {
  summary: string;
  content: string;
  metadata: {
    crystal?: CrystalDetail;
    error?: string;
  };
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Unwrap AGENTESE gateway response.
 */
function unwrapAgentese<T>(response: { data: AgenteseResponse<T> }): T {
  if (!response.data) {
    throw new AgenteseError('Crystal response missing data envelope', 'time.witness.crystal', undefined);
  }
  if (response.data.error) {
    throw new AgenteseError(response.data.error, response.data.path, response.data.aspect);
  }
  return response.data.result;
}

/**
 * Get crystal hierarchy as graph data.
 *
 * @param level - Filter by level (optional)
 * @param limit - Max crystals per level (default: 50)
 */
export async function getCrystalGraph(
  level?: CrystalLevel,
  limit = 50
): Promise<CrystalGraph | null> {
  const response = await apiClient.post<AgenteseResponse<CrystalGraphResponse>>(
    '/agentese/time/witness/crystal/graph',
    {
      level: level?.toLowerCase(),
      limit,
      response_format: 'json',
    }
  );

  const result = unwrapAgentese(response);

  if (!result.metadata.nodes) {
    return null;
  }

  return {
    nodes: result.metadata.nodes,
    edges: result.metadata.edges || [],
    total_crystals: result.metadata.total_crystals || 0,
    level_counts: (result.metadata.level_counts || {}) as Record<CrystalLevel, number>,
    time_range: result.metadata.time_range || null,
  };
}

/**
 * Get crystal detail for expansion.
 *
 * @param crystalId - Crystal ID to fetch
 */
export async function getCrystalDetail(crystalId: string): Promise<CrystalDetail | null> {
  const response = await apiClient.post<AgenteseResponse<CrystalDetailResponse>>(
    '/agentese/time/witness/crystal/detail',
    {
      crystal_id: crystalId,
      response_format: 'json',
    }
  );

  const result = unwrapAgentese(response);
  return result.metadata.crystal || null;
}

// =============================================================================
// SSE Streaming
// =============================================================================

/**
 * Subscribe to crystal stream.
 *
 * @param onEvent - Callback for each event
 * @param onError - Callback for errors
 * @param level - Filter by level (optional)
 *
 * @returns Cleanup function to close the connection
 */
export function subscribeToCrystalStream(
  onEvent: (event: CrystalEvent) => void,
  onError?: (error: Error) => void,
  level?: CrystalLevel
): () => void {
  const url = new URL('/agentese/time/witness/crystal/stream', window.location.origin);
  if (level) {
    url.searchParams.set('level', level.toLowerCase());
  }

  const eventSource = new EventSource(url.toString());

  eventSource.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      onEvent(payload);
    } catch (e) {
      console.error('Failed to parse crystal event:', e);
    }
  };

  // Handle specific event types
  eventSource.addEventListener('crystal.created', (event) => {
    try {
      const payload = JSON.parse((event as MessageEvent).data);
      onEvent({ type: 'crystal.created', ...payload });
    } catch (e) {
      console.error('Failed to parse crystal.created event:', e);
    }
  });

  eventSource.addEventListener('crystal.batch', (event) => {
    try {
      const payload = JSON.parse((event as MessageEvent).data);
      onEvent({ type: 'crystal.batch', ...payload });
    } catch (e) {
      console.error('Failed to parse crystal.batch event:', e);
    }
  });

  eventSource.addEventListener('heartbeat', () => {
    onEvent({
      type: 'heartbeat',
      timestamp: new Date().toISOString(),
      data: { message: 'keep-alive' },
    });
  });

  eventSource.onerror = (e) => {
    console.error('Crystal stream error:', e);
    onError?.(new Error('Crystal stream connection error'));
  };

  // Return cleanup function
  return () => {
    eventSource.close();
  };
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Get color for crystal level.
 */
export function getLevelColor(level: CrystalLevel): string {
  return CRYSTAL_LEVELS[level]?.color || '#6b7280';
}

/**
 * Get strength from confidence score.
 */
export function getConfidenceStrength(confidence: number): CrystalStrength {
  if (confidence >= 0.9) return 'definitive';
  if (confidence >= 0.75) return 'strong';
  if (confidence >= 0.5) return 'moderate';
  return 'weak';
}

/**
 * Get color for confidence strength.
 */
export function getStrengthColor(strength: CrystalStrength): string {
  switch (strength) {
    case 'definitive':
      return '#22c55e'; // green
    case 'strong':
      return '#3b82f6'; // blue
    case 'moderate':
      return '#f59e0b'; // amber
    case 'weak':
      return '#6b7280'; // gray
    default:
      return '#6b7280';
  }
}

/**
 * Format crystal for display.
 */
export function formatCrystal(node: CrystalGraphNode): string {
  const level = node.data.level;
  const insight = node.data.insight.slice(0, 60);
  return `[${level}] ${insight}${node.data.insight.length > 60 ? '...' : ''}`;
}

// =============================================================================
// Exports
// =============================================================================

export type {
  AgenteseResponse,
  CrystalGraphResponse,
  CrystalDetailResponse,
};
