/**
 * Witness API Client
 *
 * API client for the Witness Crown Jewel - marks, filtering, and real-time streaming.
 *
 * "Every action leaves a mark. The mark IS the witness."
 *
 * @see plans/witness-fusion-ux-implementation.md
 */

import { apiClient } from './client';

// =============================================================================
// Types
// =============================================================================

/**
 * A Mark in the Witness ledger.
 *
 * Marks are the atomic unit of witnessed behavior:
 * - Every action leaves a mark
 * - Marks are immutable once created
 * - Marks can have reasoning and principles
 */
export interface Mark {
  /** Unique mark identifier (e.g., "mark-abc123def456") */
  id: string;

  /** What was done - the core action text */
  action: string;

  /** Why it was done (optional but encouraged) */
  reasoning?: string;

  /** Which principles were honored */
  principles: string[];

  /** Who created the mark */
  author: 'kent' | 'claude' | 'system';

  /** Session context for grouping */
  session_id?: string;

  /** Parent mark for causal lineage */
  parent_mark_id?: string;

  /** When the mark was created (ISO 8601) */
  timestamp: string;

  /** When the mark was retracted (if applicable) */
  retracted_at?: string;

  /** Who retracted the mark (if applicable) */
  retracted_by?: string;
}

/**
 * Request to create a new mark.
 */
export interface CreateMarkRequest {
  /** What was done - the core action text */
  action: string;

  /** Why it was done (optional) */
  reasoning?: string;

  /** Which principles are honored (optional) */
  principles?: string[];

  /** Parent mark ID for causal lineage (optional) */
  parent_mark_id?: string;
}

/**
 * Response from creating a mark.
 */
export interface CreateMarkResponse {
  mark_id: string;
  action: string;
  reasoning?: string;
  principles: string[];
  timestamp: string;
  author: string;
  parent_mark_id?: string;
}

/**
 * Filter options for querying marks.
 */
export interface MarkFilters {
  /** Filter by author */
  author?: 'kent' | 'claude' | 'system';

  /** Filter by principles (any match) */
  principles?: string[];

  /** Filter by date range */
  dateRange?: {
    start: Date;
    end: Date;
  };

  /** Maximum number of marks to return */
  limit?: number;

  /** Only marks from today */
  today?: boolean;

  /** Text search in action/reasoning */
  grep?: string;
}

/**
 * Mark tree for causal lineage visualization.
 */
export interface MarkTree {
  root_mark_id: string;
  total_marks: number;
  tree: MarkTreeNode;
  flat: Mark[];
}

export interface MarkTreeNode extends Mark {
  children: MarkTreeNode[];
}

/**
 * SSE event for real-time mark streaming.
 */
export interface MarkStreamEvent {
  type: 'mark';
  mark: Mark;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Create a new mark.
 *
 * @example
 * const mark = await createMark({
 *   action: "Refactored DI container",
 *   reasoning: "Enable Crown Jewel pattern",
 *   principles: ["composable", "generative"],
 * });
 */
export async function createMark(request: CreateMarkRequest): Promise<Mark> {
  const { data } = await apiClient.post<CreateMarkResponse>(
    '/api/witness/marks',
    request
  );

  // Transform response to Mark format
  return {
    id: data.mark_id,
    action: data.action,
    reasoning: data.reasoning,
    principles: data.principles,
    author: data.author as 'kent' | 'claude' | 'system',
    timestamp: data.timestamp,
    parent_mark_id: data.parent_mark_id,
  };
}

/**
 * Get recent marks with optional filtering.
 *
 * @example
 * const marks = await getRecentMarks({ limit: 20, author: 'kent' });
 */
export async function getRecentMarks(filters?: MarkFilters): Promise<Mark[]> {
  const params = new URLSearchParams();

  if (filters?.limit) {
    params.set('limit', String(filters.limit));
  }
  if (filters?.author) {
    params.set('author', filters.author);
  }
  if (filters?.principles?.length) {
    params.set('principles', filters.principles.join(','));
  }
  if (filters?.today) {
    params.set('today', 'true');
  }
  if (filters?.grep) {
    params.set('grep', filters.grep);
  }

  const query = params.toString();
  const url = `/api/witness/marks${query ? `?${query}` : ''}`;

  const { data } = await apiClient.get<Mark[]>(url);
  return data;
}

/**
 * Get marks from the current session.
 */
export async function getSessionMarks(sessionId?: string): Promise<Mark[]> {
  const url = sessionId
    ? `/api/witness/marks?session_id=${sessionId}`
    : '/api/witness/session';

  const { data } = await apiClient.get<Mark[]>(url);
  return data;
}

/**
 * Retract a mark (marks it as superseded, doesn't delete).
 *
 * @example
 * await retractMark('mark-abc123', 'Typo, meant async not sync');
 */
export async function retractMark(markId: string, reason: string): Promise<Mark> {
  const { data } = await apiClient.post<Mark>(`/api/witness/marks/${markId}/retract`, {
    reason,
  });
  return data;
}

/**
 * Get a specific mark by ID.
 */
export async function getMark(markId: string): Promise<Mark | null> {
  try {
    const { data } = await apiClient.get<Mark>(`/api/witness/marks/${markId}`);
    return data;
  } catch (error) {
    // Return null if not found
    if ((error as { response?: { status?: number } }).response?.status === 404) {
      return null;
    }
    throw error;
  }
}

/**
 * Get the causal tree of marks starting from a root.
 */
export async function getMarkTree(
  rootMarkId: string,
  maxDepth: number = 10
): Promise<MarkTree> {
  const { data } = await apiClient.get<MarkTree>(
    `/api/witness/marks/${rootMarkId}/tree?max_depth=${maxDepth}`
  );
  return data;
}

/**
 * Get the ancestry (parent chain) of a mark.
 */
export async function getMarkAncestry(markId: string): Promise<Mark[]> {
  const { data } = await apiClient.get<{ ancestry: Mark[] }>(
    `/api/witness/marks/${markId}/ancestry`
  );
  return data.ancestry;
}

// =============================================================================
// SSE Streaming
// =============================================================================

/**
 * Subscribe to real-time mark events via SSE.
 *
 * @example
 * const cleanup = subscribeToMarks((mark) => {
 *   console.log('New mark:', mark);
 * });
 *
 * // Later:
 * cleanup();
 */
export function subscribeToMarks(
  onMark: (mark: Mark) => void,
  options?: {
    onError?: (error: Error) => void;
    onConnect?: () => void;
    onDisconnect?: () => void;
    reconnectDelay?: number;
  }
): () => void {
  const API_BASE = import.meta.env.VITE_API_URL || '';
  const url = `${API_BASE}/api/witness/stream`;

  let eventSource: EventSource | null = null;
  let reconnectTimeout: number | null = null;
  let isCleanedUp = false;

  const connect = () => {
    if (isCleanedUp) return;

    eventSource = new EventSource(url);

    eventSource.onopen = () => {
      options?.onConnect?.();
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as MarkStreamEvent;
        if (data.type === 'mark') {
          onMark(data.mark);
        }
      } catch (error) {
        console.error('[subscribeToMarks] Failed to parse event:', error);
      }
    };

    eventSource.onerror = () => {
      options?.onDisconnect?.();
      eventSource?.close();
      eventSource = null;

      // Reconnect after delay
      if (!isCleanedUp) {
        reconnectTimeout = window.setTimeout(
          connect,
          options?.reconnectDelay ?? 3000
        );
      }
    };
  };

  // Start connection
  connect();

  // Return cleanup function
  return () => {
    isCleanedUp = true;
    if (reconnectTimeout !== null) {
      window.clearTimeout(reconnectTimeout);
    }
    eventSource?.close();
  };
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Group marks by day for timeline display.
 */
export function groupMarksByDay(marks: Mark[]): Map<string, Mark[]> {
  const groups = new Map<string, Mark[]>();

  for (const mark of marks) {
    const date = new Date(mark.timestamp).toLocaleDateString();
    const existing = groups.get(date) || [];
    existing.push(mark);
    groups.set(date, existing);
  }

  return groups;
}

/**
 * Group marks by session for timeline display.
 */
export function groupMarksBySession(marks: Mark[]): Map<string, Mark[]> {
  const groups = new Map<string, Mark[]>();

  for (const mark of marks) {
    const sessionId = mark.session_id || 'unknown';
    const existing = groups.get(sessionId) || [];
    existing.push(mark);
    groups.set(sessionId, existing);
  }

  return groups;
}

/**
 * Format timestamp for display.
 */
export function formatMarkTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Check if mark is from today.
 */
export function isMarkFromToday(mark: Mark): boolean {
  const markDate = new Date(mark.timestamp);
  const today = new Date();
  return (
    markDate.getFullYear() === today.getFullYear() &&
    markDate.getMonth() === today.getMonth() &&
    markDate.getDate() === today.getDate()
  );
}

// =============================================================================
// Exports
// =============================================================================

export default {
  createMark,
  getRecentMarks,
  getSessionMarks,
  retractMark,
  getMark,
  getMarkTree,
  getMarkAncestry,
  subscribeToMarks,
  groupMarksByDay,
  groupMarksBySession,
  formatMarkTimestamp,
  isMarkFromToday,
};
