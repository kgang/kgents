/**
 * Chat Store — Zustand store for chat state management
 *
 * Manages:
 * - Session state (ChatKBlock pattern)
 * - Streaming responses
 * - Evidence accumulation
 * - Branch navigation
 *
 * @see spec/protocols/chat-web.md Part IV
 */

import { create } from 'zustand';

// =============================================================================
// Types (from spec Part X.6)
// =============================================================================

export interface ChatSession {
  id: string;
  project_id: string | null;
  branch_name: string;
  parent_id: string | null;
  fork_point: number | null;
  turns: Turn[];
  context_size: number;
  evidence: ChatEvidence;
  created_at: string;
  last_active: string;
}

export interface Turn {
  turn_number: number;
  user_message: Message;
  assistant_response: Message;
  tools_used: ToolUse[];
  evidence_delta: EvidenceDelta;
  confidence: number;
  started_at: string;
  completed_at: string;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  mentions: Mention[];
  linearity_tag: 'required' | 'preserved' | 'droppable';
}

export interface ChatEvidence {
  prior_alpha: number;
  prior_beta: number;
  confidence: number;
  should_stop: boolean;
  tools_succeeded: number;
  tools_failed: number;
  ashc_equivalence?: number;
}

export interface Mention {
  type: 'file' | 'symbol' | 'spec' | 'witness' | 'web' | 'terminal' | 'project';
  query: string;
  resolved_path?: string;
}

export interface ToolUse {
  name: string;
  input: Record<string, unknown>;
  output: unknown;
  success: boolean;
  duration_ms: number;
}

export interface EvidenceDelta {
  tools_executed: number;
  tools_succeeded: number;
  confidence_change: number;
}

export interface SessionCrystal {
  session_id: string;
  title: string;
  summary: string;
  key_decisions: string[];
  artifacts: string[];
  final_evidence: {
    confidence: number;
    tools_succeeded: number;
    tools_failed: number;
  };
  created_at: string;
  turn_count: number;
}

export interface TrailingSessionData {
  crystal: SessionCrystal;
  trailingTurns: Turn[];
  crystallizedAt: string;
}

// =============================================================================
// Mutation Tracking (Part VII.2)
// =============================================================================

/**
 * Pending mutation requiring acknowledgment.
 * From spec: "Mutations must speak AND be heard."
 */
export interface PendingMutation {
  id: string;
  tool_name: string;
  description: string;
  target?: string;
  is_destructive: boolean;
  timestamp: string;
}

/**
 * Mutation acknowledgment record.
 */
export interface MutationAcknowledgment {
  mutation_id: string;
  acknowledged_at: string;
  mode: 'click' | 'keyboard' | 'timeout_accept';
}

// =============================================================================
// Trust Escalation (Part VII.3)
// =============================================================================

/**
 * Trust escalation suggestion.
 * Shown after user approves a tool N times.
 */
export interface TrustEscalation {
  id: string;
  tool_name: string;
  approval_count: number;
  timestamp: string;
}

/**
 * Tool trust stats.
 */
export interface ToolTrustStats {
  tool_name: string;
  level: 'never' | 'ask' | 'trusted';
  approval_count: number;
  denial_count: number;
  last_used: string | null;
  escalation_threshold: number;
  escalation_offered: boolean;
}

// =============================================================================
// Pre-Execution Gating (Part VII.3)
// =============================================================================

/**
 * Pending approval for destructive operation.
 * Shows BEFORE tool execution (unlike MutationAcknowledger which shows after).
 */
export interface PendingApproval {
  request_id: string;
  tool_name: string;
  input_preview: string;
  is_destructive: boolean;
  timeout_seconds: number;
  timestamp: string;
}

// =============================================================================
// Store State
// =============================================================================

interface ChatStoreState {
  // Current session
  currentSession: ChatSession | null;

  // Available sessions (for branch tree)
  sessions: ChatSession[];

  // Streaming state
  isStreaming: boolean;
  streamingContent: string;

  // Error state
  error: string | null;

  // Trailing session (crystallized context)
  trailingSession: TrailingSessionData | null;

  // Mutation tracking
  pendingMutations: PendingMutation[];
  acknowledgmentLog: MutationAcknowledgment[];

  // Trust escalation
  pendingEscalations: TrustEscalation[];
  toolTrustStats: Map<string, ToolTrustStats>;

  // Pre-execution gating
  pendingApprovals: PendingApproval[];

  // Actions
  initialize: (sessionId?: string, projectId?: string) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  fork: (sessionId: string, branchName: string) => Promise<void>;
  rewind: (sessionId: string, turns: number) => Promise<void>;
  switchSession: (sessionId: string) => Promise<void>;
  clearError: () => void;

  // Trailing session actions
  continueTrailingSession: () => Promise<void>;
  startFreshFromTrailing: () => Promise<void>;
  dismissTrailing: () => void;

  // Mutation tracking actions
  acknowledgeMutation: (id: string, mode: 'click' | 'keyboard' | 'timeout_accept') => void;
  addPendingMutation: (mutation: PendingMutation) => void;

  // Trust escalation actions
  checkTrustEscalation: (toolName: string) => Promise<void>;
  handleTrustChoice: (escalationId: string, choice: 'trust' | 'keep_asking' | 'never') => Promise<void>;
  dismissEscalation: (escalationId: string) => void;
  loadToolTrustStats: (toolName: string) => Promise<void>;

  // Pre-execution gating actions
  addPendingApproval: (approval: PendingApproval) => void;
  approveToolExecution: (requestId: string, alwaysAllow: boolean) => Promise<void>;
  denyToolExecution: (requestId: string, reason?: string) => Promise<void>;
}

// =============================================================================
// Store Implementation
// =============================================================================

export const useChatStore = create<ChatStoreState>((set, get) => ({
  // Initial state
  currentSession: null,
  sessions: [],
  isStreaming: false,
  streamingContent: '',
  error: null,
  trailingSession: null,
  pendingMutations: [],
  acknowledgmentLog: [],
  pendingEscalations: [],
  toolTrustStats: new Map(),
  pendingApprovals: [],

  // Initialize session
  initialize: async (sessionId?: string, projectId?: string) => {
    try {
      let session: ChatSession;

      if (sessionId) {
        // Load existing session
        const response = await fetch(`/api/chat/session/${sessionId}`);
        if (!response.ok) throw new Error('Failed to load session');
        session = await response.json();
      } else {
        // Create new session
        const response = await fetch('/api/chat/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: projectId }),
        });
        if (!response.ok) throw new Error('Failed to create session');
        session = await response.json();
      }

      set({ currentSession: session, error: null });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // Send message with streaming
  sendMessage: async (message: string) => {
    const { currentSession } = get();
    if (!currentSession) return;

    try {
      set({ isStreaming: true, streamingContent: '', error: null });

      const response = await fetch(`/api/chat/${currentSession.id}/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Split on SSE event boundaries (\n\n)
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Keep incomplete event in buffer

        // Process each complete event
        for (const event of events) {
          if (event.startsWith('data: ')) {
            const jsonStr = event.slice(6); // Remove "data: " prefix
            const data = JSON.parse(jsonStr);

            if (data.type === 'content') {
              // Update streaming content with parsed content
              set({ streamingContent: data.content });
            } else if (data.type === 'pending_approval') {
              // Pre-execution gating: tool needs approval before execution
              const approval: PendingApproval = {
                request_id: data.request_id,
                tool_name: data.tool_name,
                input_preview: data.input_preview,
                is_destructive: data.is_destructive,
                timeout_seconds: data.timeout_seconds,
                timestamp: data.timestamp,
              };
              get().addPendingApproval(approval);
            } else if (data.type === 'done') {
              // Update session with completed turn
              set((state) => ({
                currentSession: state.currentSession ? {
                  ...state.currentSession,
                  turns: [...state.currentSession.turns, data.turn],
                } : null,
                isStreaming: false,
                streamingContent: '',
              }));
              return; // Stream complete
            } else if (data.type === 'error') {
              // Set error state
              set({
                error: data.error,
                isStreaming: false,
                streamingContent: '',
              });
              return;
            }
          }
        }
      }

      // If we exit loop without done event, clean up
      set({ isStreaming: false, streamingContent: '' });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Unknown error',
        isStreaming: false,
      });
    }
  },

  // Fork session
  fork: async (sessionId: string, branchName: string) => {
    try {
      const response = await fetch(`/api/chat/${sessionId}/fork`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ branch_name: branchName }),
      });

      if (!response.ok) throw new Error('Failed to fork session');

      const newSession: ChatSession = await response.json();
      set({ currentSession: newSession, error: null });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // Rewind session
  rewind: async (sessionId: string, turns: number) => {
    try {
      const response = await fetch(`/api/chat/${sessionId}/rewind`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ turns }),
      });

      if (!response.ok) throw new Error('Failed to rewind');

      const session: ChatSession = await response.json();
      set({ currentSession: session, error: null });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // Switch to different session
  switchSession: async (sessionId: string) => {
    await get().initialize(sessionId);
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Continue trailing session - re-activate all trailing turns
  continueTrailingSession: async () => {
    const { trailingSession, currentSession } = get();
    if (!trailingSession || !currentSession) return;

    try {
      // API call to re-activate trailing turns
      const response = await fetch(`/api/chat/${currentSession.id}/continue-trailing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error('Failed to continue trailing session');

      const updatedSession: ChatSession = await response.json();
      set({
        currentSession: updatedSession,
        trailingSession: null,
        error: null
      });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // Start fresh from trailing - create new session with crystal reference
  startFreshFromTrailing: async () => {
    const { trailingSession } = get();
    if (!trailingSession) return;

    try {
      // API call to create new session with crystal reference
      const response = await fetch('/api/chat/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          crystal_reference: trailingSession.crystal.session_id
        }),
      });

      if (!response.ok) throw new Error('Failed to start fresh session');

      const newSession: ChatSession = await response.json();
      set({
        currentSession: newSession,
        trailingSession: null,
        error: null
      });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // Dismiss trailing section
  dismissTrailing: () => {
    set({ trailingSession: null });
  },

  // Acknowledge mutation
  acknowledgeMutation: (id: string, mode: 'click' | 'keyboard' | 'timeout_accept') => {
    const acknowledgment: MutationAcknowledgment = {
      mutation_id: id,
      acknowledged_at: new Date().toISOString(),
      mode,
    };

    set((state) => ({
      pendingMutations: state.pendingMutations.filter((m) => m.id !== id),
      acknowledgmentLog: [...state.acknowledgmentLog, acknowledgment],
    }));
  },

  // Add pending mutation
  addPendingMutation: (mutation: PendingMutation) => {
    set((state) => ({
      pendingMutations: [...state.pendingMutations, mutation],
    }));
  },

  // Check trust escalation after acknowledgment
  checkTrustEscalation: async (toolName: string) => {
    try {
      // Call API to check if escalation should be suggested
      const response = await fetch(`/api/chat/trust/suggest-escalation?tool_name=${toolName}`);
      if (!response.ok) return;

      const data = await response.json();
      if (data.should_suggest) {
        // Add to pending escalations
        const escalation: TrustEscalation = {
          id: `${toolName}-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
          tool_name: toolName,
          approval_count: data.approval_count,
          timestamp: new Date().toISOString(),
        };

        set((state) => ({
          pendingEscalations: [...state.pendingEscalations, escalation],
        }));
      }
    } catch (err) {
      console.error('Failed to check trust escalation:', err);
    }
  },

  // Handle trust choice
  handleTrustChoice: async (escalationId: string, choice: 'trust' | 'keep_asking' | 'never') => {
    const { pendingEscalations } = get();
    const escalation = pendingEscalations.find((e) => e.id === escalationId);
    if (!escalation) return;

    try {
      // Call API to update trust level
      const response = await fetch('/api/chat/trust/choice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: escalation.tool_name,
          choice,
        }),
      });

      if (!response.ok) throw new Error('Failed to update trust level');

      // Remove from pending escalations
      set((state) => ({
        pendingEscalations: state.pendingEscalations.filter((e) => e.id !== escalationId),
      }));

      // Reload tool trust stats
      await get().loadToolTrustStats(escalation.tool_name);
    } catch (err) {
      console.error('Failed to handle trust choice:', err);
    }
  },

  // Dismiss escalation (without choosing)
  dismissEscalation: (escalationId: string) => {
    set((state) => ({
      pendingEscalations: state.pendingEscalations.filter((e) => e.id !== escalationId),
    }));
  },

  // Load tool trust stats
  loadToolTrustStats: async (toolName: string) => {
    try {
      const response = await fetch(`/api/chat/trust/stats?tool_name=${toolName}`);
      if (!response.ok) return;

      const stats: ToolTrustStats = await response.json();
      set((state) => {
        const newStats = new Map(state.toolTrustStats);
        newStats.set(toolName, stats);
        return { toolTrustStats: newStats };
      });
    } catch (err) {
      console.error('Failed to load tool trust stats:', err);
    }
  },

  // ========================================================================
  // Pre-Execution Gating Actions
  // ========================================================================

  // Add pending approval (called when SSE event received)
  addPendingApproval: (approval: PendingApproval) => {
    set((state) => ({
      pendingApprovals: [...state.pendingApprovals, approval],
    }));
  },

  // Approve tool execution
  approveToolExecution: async (requestId: string, alwaysAllow: boolean) => {
    const { currentSession, pendingApprovals } = get();
    if (!currentSession) return;

    // Find the approval
    const approval = pendingApprovals.find((a) => a.request_id === requestId);
    if (!approval) return;

    try {
      // Send approval to backend
      const response = await fetch(`/api/chat/${currentSession.id}/approve-tool`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request_id: requestId,
          approved: true,
          always_allow: alwaysAllow,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to approve tool execution');
      }

      // Remove from pending approvals
      set((state) => ({
        pendingApprovals: state.pendingApprovals.filter((a) => a.request_id !== requestId),
      }));

      // If always_allow was chosen, refresh trust stats
      if (alwaysAllow) {
        await get().loadToolTrustStats(approval.tool_name);
      }
    } catch (err) {
      console.error('Failed to approve tool execution:', err);
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // Deny tool execution
  denyToolExecution: async (requestId: string, reason?: string) => {
    const { currentSession, pendingApprovals } = get();
    if (!currentSession) return;

    // Find the approval
    const approval = pendingApprovals.find((a) => a.request_id === requestId);
    if (!approval) return;

    try {
      // Send denial to backend
      const response = await fetch(`/api/chat/${currentSession.id}/approve-tool`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request_id: requestId,
          approved: false,
          reason: reason || 'User denied approval',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to deny tool execution');
      }

      // Remove from pending approvals
      set((state) => ({
        pendingApprovals: state.pendingApprovals.filter((a) => a.request_id !== requestId),
      }));
    } catch (err) {
      console.error('Failed to deny tool execution:', err);
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },
}));
