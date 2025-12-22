/**
 * Collaboration API - Human-Agent Turn-Taking
 *
 * Phase 5C: Collaborative Editing
 *
 * Provides:
 * - Proposal creation and acceptance via AGENTESE
 * - Keystroke tracking for turn-taking
 * - SSE streaming for real-time proposal updates
 * - React hooks for collaboration state
 *
 * Routes via AGENTESE:
 * - POST /agentese/self/collaboration/propose
 * - POST /agentese/self/collaboration/respond
 * - POST /agentese/self/collaboration/keystroke
 * - GET  /agentese/self/collaboration/pending
 * - GET  /agentese/self/collaboration/status
 * - GET  /agentese/self/collaboration/stream (SSE)
 *
 * @see spec/protocols/context-perception.md §6
 */

import { apiClient } from './client';

// =============================================================================
// Types
// =============================================================================

/** Proposal status */
export type ProposalStatus = 'pending' | 'accepted' | 'rejected' | 'expired';

/** Turn state */
export type TurnState = 'human' | 'agent' | 'open';

/** A pending edit proposal from an agent */
export interface Proposal {
  id: string;
  agent_id: string;
  agent_name: string;
  location: string;
  original: string;
  proposed: string;
  description: string;
  created_at: string;
  status: ProposalStatus;
  resolved_at: string | null;
  auto_accept_at: string;
  time_remaining_ms: number;
}

/** Collaboration manifest response */
export interface CollaborationManifest {
  status: string;
  pending_count: number;
  auto_accept_delay_ms: number;
  typing_grace_period_ms: number;
  proposal_cooldown_ms: number;
  features: string[];
}

/** Propose request */
export interface ProposeRequest {
  agent_id: string;
  agent_name: string;
  location: string;
  original: string;
  proposed: string;
  description: string;
}

/** Propose response */
export interface ProposeResponse {
  success: boolean;
  proposal_id: string | null;
  error: string | null;
  auto_accept_at: string | null;
  time_remaining_ms: number;
}

/** Respond request */
export interface RespondRequest {
  proposal_id: string;
  action: 'accept' | 'reject';
}

/** Respond response */
export interface RespondResponse {
  success: boolean;
  proposal_id: string;
  action: string;
  status: string;
  error: string | null;
}

/** Keystroke request */
export interface KeystrokeRequest {
  location: string;
}

/** Keystroke response */
export interface KeystrokeResponse {
  recorded: boolean;
  location: string;
  timestamp: string;
}

/** Pending proposals response */
export interface PendingResponse {
  proposals: Proposal[];
  count: number;
}

/** Status response */
export interface StatusResponse {
  turn_state: TurnState;
  is_human_typing: boolean;
  active_typing_locations: string[];
  pending_proposal_count: number;
}

/** SSE event types */
export type CollaborationEventType =
  | 'status'
  | 'pending'
  | 'proposal_update'
  | 'auto_accept'
  | 'heartbeat';

/** SSE event */
export interface CollaborationEvent {
  type: CollaborationEventType;
  data?: Proposal | StatusResponse | PendingResponse;
  timestamp?: string;
}

// =============================================================================
// AGENTESE Response Wrapper
// =============================================================================

interface AgenteseResponse<T> {
  path: string;
  aspect: string;
  result: {
    summary: string;
    content: string;
    metadata: T;
  };
  error?: string;
}

function unwrapAgentese<T>(response: { data: AgenteseResponse<T> }): T {
  if (response.data.error) {
    throw new Error(response.data.error);
  }
  return response.data.result.metadata;
}

// =============================================================================
// API Client
// =============================================================================

export const collaborationApi = {
  /**
   * Get collaboration manifest (status and config).
   */
  getManifest: async (): Promise<CollaborationManifest> => {
    const response = await apiClient.get<AgenteseResponse<CollaborationManifest>>(
      '/agentese/self/collaboration/manifest'
    );
    return unwrapAgentese(response);
  },

  /**
   * Create a new edit proposal.
   */
  propose: async (request: ProposeRequest): Promise<ProposeResponse> => {
    const response = await apiClient.post<AgenteseResponse<ProposeResponse>>(
      '/agentese/self/collaboration/propose',
      request
    );
    return unwrapAgentese(response);
  },

  /**
   * Accept or reject a proposal.
   */
  respond: async (request: RespondRequest): Promise<RespondResponse> => {
    const response = await apiClient.post<AgenteseResponse<RespondResponse>>(
      '/agentese/self/collaboration/respond',
      request
    );
    return unwrapAgentese(response);
  },

  /**
   * Record a human keystroke to block agent edits.
   */
  keystroke: async (request: KeystrokeRequest): Promise<KeystrokeResponse> => {
    const response = await apiClient.post<AgenteseResponse<KeystrokeResponse>>(
      '/agentese/self/collaboration/keystroke',
      request
    );
    return unwrapAgentese(response);
  },

  /**
   * Get all pending proposals.
   */
  getPending: async (location?: string): Promise<PendingResponse> => {
    const response = await apiClient.post<AgenteseResponse<PendingResponse>>(
      '/agentese/self/collaboration/pending',
      location ? { location } : {}
    );
    return unwrapAgentese(response);
  },

  /**
   * Get current collaboration status.
   */
  getStatus: async (): Promise<StatusResponse> => {
    const response = await apiClient.get<AgenteseResponse<StatusResponse>>(
      '/agentese/self/collaboration/status'
    );
    return unwrapAgentese(response);
  },

  /**
   * Create SSE stream for collaboration events.
   * Uses relative URL so Vite proxy forwards to backend.
   *
   * The stream aspect is invoked directly as `/stream` (not `/stream/stream`).
   * The gateway detects async generators and returns StreamingResponse.
   *
   * Events:
   * - status: Initial turn-taking status
   * - pending: Current pending proposals
   * - proposal_update: Proposal created/updated
   * - auto_accept: Proposal was auto-accepted
   * - heartbeat: Keep-alive (every 5s)
   */
  createStream: (): EventSource => {
    // AGENTESE aspect invocation: /{context}/{holon}/{aspect}
    // Gateway detects AsyncGenerator return and streams as SSE
    return new EventSource('/agentese/self/collaboration/stream');
  },
};

// =============================================================================
// React Hook: useCollaboration
// =============================================================================

import { useState, useEffect, useCallback, useRef } from 'react';

export interface UseCollaborationOptions {
  /** Auto-connect to SSE stream on mount */
  autoConnect?: boolean;
  /** Location to filter proposals */
  location?: string;
  /** Callback when proposal is received */
  onProposal?: (proposal: Proposal) => void;
  /** Callback when proposal is auto-accepted */
  onAutoAccept?: (proposal: Proposal) => void;
}

export interface UseCollaborationReturn {
  /** Pending proposals */
  proposals: Proposal[];
  /** Current turn state */
  turnState: TurnState;
  /** Whether human is typing */
  isHumanTyping: boolean;
  /** Whether connected to SSE stream */
  isConnected: boolean;
  /** Last error */
  error: string | null;
  /** Accept a proposal */
  accept: (proposalId: string) => Promise<void>;
  /** Reject a proposal */
  reject: (proposalId: string) => Promise<void>;
  /** Record keystroke */
  recordKeystroke: (location: string) => Promise<void>;
  /** Reconnect to stream */
  reconnect: () => void;
}

export function useCollaboration(options: UseCollaborationOptions = {}): UseCollaborationReturn {
  const { autoConnect = true, location, onProposal, onAutoAccept } = options;

  // State
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [turnState, setTurnState] = useState<TurnState>('open');
  const [isHumanTyping, setIsHumanTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs
  const streamRef = useRef<EventSource | null>(null);
  const callbacksRef = useRef({ onProposal, onAutoAccept });

  // Update callbacks ref
  useEffect(() => {
    callbacksRef.current = { onProposal, onAutoAccept };
  }, [onProposal, onAutoAccept]);

  // Connect to SSE stream
  const connect = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.close();
    }

    try {
      const stream = collaborationApi.createStream();
      streamRef.current = stream;

      stream.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.debug('[Collaboration] SSE stream connected');
      };

      stream.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as CollaborationEvent;

          switch (data.type) {
            case 'status':
              if (data.data && 'turn_state' in data.data) {
                setTurnState(data.data.turn_state);
                setIsHumanTyping(data.data.is_human_typing);
              }
              break;

            case 'pending':
              if (data.data && 'proposals' in data.data) {
                // Filter by location if specified
                let filteredProposals = data.data.proposals;
                if (location) {
                  filteredProposals = filteredProposals.filter(
                    (p) => p.location === location || p.location.startsWith(location)
                  );
                }
                setProposals(filteredProposals);
              }
              break;

            case 'proposal_update':
              if (data.data && 'id' in data.data) {
                const proposal = data.data as Proposal;
                setProposals((prev) => {
                  const idx = prev.findIndex((p) => p.id === proposal.id);
                  if (idx >= 0) {
                    const updated = [...prev];
                    updated[idx] = proposal;
                    return updated;
                  }
                  // New proposal
                  callbacksRef.current.onProposal?.(proposal);
                  return [...prev, proposal];
                });
              }
              break;

            case 'auto_accept':
              if (data.data && 'id' in data.data) {
                const proposal = data.data as Proposal;
                callbacksRef.current.onAutoAccept?.(proposal);
                // Remove from pending
                setProposals((prev) => prev.filter((p) => p.id !== proposal.id));
              }
              break;

            case 'heartbeat':
              // Just keep-alive
              break;
          }
        } catch (e) {
          console.error('[Collaboration] Failed to parse event:', e);
        }
      };

      stream.onerror = () => {
        setIsConnected(false);
        setError('Connection lost');
        console.debug('[Collaboration] SSE connection error, reconnecting in 3s');
        // Auto-reconnect after 3s
        setTimeout(connect, 3000);
      };
    } catch (e) {
      setError('Failed to connect');
      console.error('[Collaboration] Failed to connect:', e);
    }
  }, [location]);

  // Disconnect
  const disconnect = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }
    setIsConnected(false);
  }, []);

  // Reconnect
  const reconnect = useCallback(() => {
    disconnect();
    connect();
  }, [disconnect, connect]);

  // Accept proposal
  const accept = useCallback(async (proposalId: string) => {
    try {
      await collaborationApi.respond({ proposal_id: proposalId, action: 'accept' });
      setProposals((prev) => prev.filter((p) => p.id !== proposalId));
    } catch (e) {
      console.error('[Collaboration] Failed to accept:', e);
      setError('Failed to accept proposal');
    }
  }, []);

  // Reject proposal
  const reject = useCallback(async (proposalId: string) => {
    try {
      await collaborationApi.respond({ proposal_id: proposalId, action: 'reject' });
      setProposals((prev) => prev.filter((p) => p.id !== proposalId));
    } catch (e) {
      console.error('[Collaboration] Failed to reject:', e);
      setError('Failed to reject proposal');
    }
  }, []);

  // Record keystroke
  const recordKeystroke = useCallback(async (loc: string) => {
    try {
      await collaborationApi.keystroke({ location: loc });
    } catch (e) {
      // Silent failure - keystrokes are best-effort
      console.debug('[Collaboration] Keystroke failed:', e);
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    proposals,
    turnState,
    isHumanTyping,
    isConnected,
    error,
    accept,
    reject,
    recordKeystroke,
    reconnect,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default collaborationApi;
