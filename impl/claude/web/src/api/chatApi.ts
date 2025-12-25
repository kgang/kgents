/**
 * Chat API Client
 *
 * API client for chat-web protocol endpoints.
 * Uses AGENTESE Universal Protocol paths for chat operations.
 *
 * Endpoints (Part XIII.3: API Integration):
 * - POST /api/chat/session - Create session
 * - POST /api/chat/{id}/send - Send message (SSE streaming)
 * - POST /api/chat/{id}/fork - Fork branch
 * - POST /api/chat/{id}/merge - Merge branches
 * - POST /api/chat/{id}/rewind - Rewind turns
 * - GET /api/chat/{id}/evidence - Get evidence
 *
 * @see spec/protocols/chat-web.md Part XIII (Implementation Reference)
 */

import { apiClient, type AgenteseResponse, unwrapAgentese } from './client';
import type {
  ChatSession,
  CreateSessionRequest,
  SendMessageRequest,
  ForkSessionRequest,
  MergeSessionRequest,
  RewindSessionRequest,
  TurnResult,
  ChatEvidence,
  SessionCrystal,
} from '@/types/chat';

// =============================================================================
// Chat API
// =============================================================================

export const chatApi = {
  /**
   * Create a new chat session.
   *
   * @param request - Session creation options
   * @returns Created session
   */
  createSession: async (request: CreateSessionRequest = {}): Promise<ChatSession> => {
    const response = await apiClient.post<AgenteseResponse<ChatSession>>(
      '/api/chat/session',
      request
    );
    return unwrapAgentese(response);
  },

  /**
   * Send a message to a chat session.
   *
   * Returns a streaming response via SSE. Use with useProjectedStream hook.
   *
   * @param sessionId - Session ID
   * @param request - Message content and mentions
   * @returns Stream of turn results
   */
  sendMessage: async (
    sessionId: string,
    request: SendMessageRequest
  ): Promise<EventSource> => {
    // For SSE streaming, we need to construct the EventSource manually
    const baseUrl = apiClient.defaults.baseURL || '';
    const token = localStorage.getItem('api_key');

    // Send initial POST to start the stream
    await apiClient.post(`/api/chat/${sessionId}/send`, request);

    // Create EventSource for the streaming response
    const params = new URLSearchParams();
    if (token) params.set('token', token);

    const url = `${baseUrl}/api/chat/${sessionId}/stream?${params.toString()}`;
    return new EventSource(url);
  },

  /**
   * Get current session state.
   *
   * @param sessionId - Session ID
   * @returns Session state
   */
  getSession: async (sessionId: string): Promise<ChatSession> => {
    const response = await apiClient.get<AgenteseResponse<ChatSession>>(
      `/api/chat/${sessionId}`
    );
    return unwrapAgentese(response);
  },

  /**
   * Fork a chat session at a specific turn.
   *
   * Creates a new branch with independent conversation history.
   *
   * @param sessionId - Session ID to fork
   * @param request - Branch name and fork point
   * @returns New session ID
   */
  fork: async (
    sessionId: string,
    request: ForkSessionRequest
  ): Promise<{ session_id: string }> => {
    const response = await apiClient.post<AgenteseResponse<{ session_id: string }>>(
      `/api/chat/${sessionId}/fork`,
      request
    );
    return unwrapAgentese(response);
  },

  /**
   * Merge two chat sessions.
   *
   * Combines conversation history from two branches using the specified strategy.
   *
   * @param sessionId - Main session ID
   * @param request - Other session ID and merge strategy
   * @returns Merge result
   */
  merge: async (
    sessionId: string,
    request: MergeSessionRequest
  ): Promise<{ success: boolean; merged_turn_count: number }> => {
    const response = await apiClient.post<
      AgenteseResponse<{ success: boolean; merged_turn_count: number }>
    >(`/api/chat/${sessionId}/merge`, request);
    return unwrapAgentese(response);
  },

  /**
   * Rewind a session by N turns.
   *
   * Removes the last N turns from the conversation.
   *
   * @param sessionId - Session ID
   * @param request - Number of turns to rewind
   * @returns Updated session state
   */
  rewind: async (
    sessionId: string,
    request: RewindSessionRequest
  ): Promise<ChatSession> => {
    const response = await apiClient.post<AgenteseResponse<ChatSession>>(
      `/api/chat/${sessionId}/rewind`,
      request
    );
    return unwrapAgentese(response);
  },

  /**
   * Get evidence accumulation state for a session.
   *
   * @param sessionId - Session ID
   * @returns Evidence state
   */
  getEvidence: async (sessionId: string): Promise<ChatEvidence> => {
    const response = await apiClient.get<AgenteseResponse<ChatEvidence>>(
      `/api/chat/${sessionId}/evidence`
    );
    return unwrapAgentese(response);
  },

  /**
   * Checkpoint a session (save restore point).
   *
   * @param sessionId - Session ID
   * @param name - Checkpoint name
   * @returns Checkpoint ID
   */
  checkpoint: async (
    sessionId: string,
    name: string
  ): Promise<{ checkpoint_id: string }> => {
    const response = await apiClient.post<AgenteseResponse<{ checkpoint_id: string }>>(
      `/api/chat/${sessionId}/checkpoint`,
      { name }
    );
    return unwrapAgentese(response);
  },

  /**
   * Restore session to a checkpoint.
   *
   * @param sessionId - Session ID
   * @param checkpointId - Checkpoint ID
   * @returns Updated session state
   */
  restoreCheckpoint: async (
    sessionId: string,
    checkpointId: string
  ): Promise<ChatSession> => {
    const response = await apiClient.post<AgenteseResponse<ChatSession>>(
      `/api/chat/${sessionId}/restore`,
      { checkpoint_id: checkpointId }
    );
    return unwrapAgentese(response);
  },

  /**
   * Get session history (all turns).
   *
   * @param sessionId - Session ID
   * @returns Turn list
   */
  getHistory: async (sessionId: string): Promise<{ turns: TurnResult[] }> => {
    const response = await apiClient.get<AgenteseResponse<{ turns: TurnResult[] }>>(
      `/api/chat/${sessionId}/history`
    );
    return unwrapAgentese(response);
  },

  /**
   * Trigger manual compression.
   *
   * @param sessionId - Session ID
   * @returns Compression result
   */
  compress: async (
    sessionId: string
  ): Promise<{ compressed_turns: number; new_context_size: number }> => {
    const response = await apiClient.post<
      AgenteseResponse<{ compressed_turns: number; new_context_size: number }>
    >(`/api/chat/${sessionId}/compress`, {});
    return unwrapAgentese(response);
  },

  /**
   * Crystallize a session (create summary crystal).
   *
   * @param sessionId - Session ID
   * @returns Session crystal
   */
  crystallize: async (sessionId: string): Promise<SessionCrystal> => {
    const response = await apiClient.post<AgenteseResponse<SessionCrystal>>(
      `/api/chat/${sessionId}/crystallize`,
      {}
    );
    return unwrapAgentese(response);
  },

  /**
   * Delete a session.
   *
   * @param sessionId - Session ID
   * @returns Success status
   */
  deleteSession: async (sessionId: string): Promise<{ success: boolean }> => {
    const response = await apiClient.delete<AgenteseResponse<{ success: boolean }>>(
      `/api/chat/${sessionId}`
    );
    return unwrapAgentese(response);
  },

  /**
   * List all sessions (optionally filtered by project).
   *
   * @param projectId - Optional project ID filter
   * @returns Session list
   */
  listSessions: async (projectId?: string): Promise<{ sessions: ChatSession[] }> => {
    const params = projectId ? `?project_id=${projectId}` : '';
    const response = await apiClient.get<AgenteseResponse<{ sessions: ChatSession[] }>>(
      `/api/chat/sessions${params}`
    );
    return unwrapAgentese(response);
  },

  /**
   * Get all crystals for a session or project.
   *
   * @param sessionId - Optional session ID filter
   * @param projectId - Optional project ID filter
   * @returns Crystal list
   */
  getCrystals: async (
    sessionId?: string,
    projectId?: string
  ): Promise<{ crystals: SessionCrystal[] }> => {
    const params = new URLSearchParams();
    if (sessionId) params.set('session_id', sessionId);
    if (projectId) params.set('project_id', projectId);

    const response = await apiClient.get<AgenteseResponse<{ crystals: SessionCrystal[] }>>(
      `/api/chat/crystals?${params.toString()}`
    );
    return unwrapAgentese(response);
  },
};

// =============================================================================
// Context Injection API (Part VI: Context Injection)
// =============================================================================

export const chatContextApi = {
  /**
   * Resolve @mention to inject content.
   *
   * @param type - Mention type (file, symbol, spec, etc.)
   * @param target - Mention target (path, URL, etc.)
   * @returns Injected content card
   */
  resolveMention: async (
    type: string,
    target: string
  ): Promise<{ content: string; metadata: Record<string, unknown> }> => {
    const response = await apiClient.post<
      AgenteseResponse<{ content: string; metadata: Record<string, unknown> }>
    >('/api/chat/mention/resolve', { type, target });
    return unwrapAgentese(response);
  },

  /**
   * Search symbols for @symbol mention autocomplete.
   *
   * Uses hybrid BM25 + vector search.
   *
   * @param query - Search query
   * @returns Symbol matches
   */
  searchSymbols: async (
    query: string
  ): Promise<{ symbols: Array<{ name: string; path: string; docstring: string }> }> => {
    const response = await apiClient.post<
      AgenteseResponse<{ symbols: Array<{ name: string; path: string; docstring: string }> }>
    >('/api/chat/mention/search/symbols', { query });
    return unwrapAgentese(response);
  },

  /**
   * Search files for @file mention autocomplete.
   *
   * @param query - Search query
   * @returns File matches
   */
  searchFiles: async (query: string): Promise<{ files: string[] }> => {
    const response = await apiClient.post<AgenteseResponse<{ files: string[] }>>(
      '/api/chat/mention/search/files',
      { query }
    );
    return unwrapAgentese(response);
  },

  /**
   * Get recent witness marks for @witness mention.
   *
   * @param query - Optional query filter
   * @param limit - Max marks to return
   * @returns Witness marks
   */
  getWitnessMarks: async (
    query?: string,
    limit = 10
  ): Promise<{ marks: Array<{ id: string; content: string; timestamp: string }> }> => {
    const response = await apiClient.post<
      AgenteseResponse<{ marks: Array<{ id: string; content: string; timestamp: string }> }>
    >('/api/chat/mention/witness', { query, limit });
    return unwrapAgentese(response);
  },
};

// =============================================================================
// Tool Transparency API (Part VII: Tool Transparency)
// =============================================================================

export const chatToolApi = {
  /**
   * Get available tools manifest.
   *
   * @returns Tool list with status indicators
   */
  getToolManifest: async (): Promise<{
    tools: Array<{
      name: string;
      description: string;
      status: 'available' | 'limited' | 'gated';
      is_pure_read: boolean;
      is_destructive: boolean;
    }>;
  }> => {
    const response = await apiClient.get<
      AgenteseResponse<{
        tools: Array<{
          name: string;
          description: string;
          status: 'available' | 'limited' | 'gated';
          is_pure_read: boolean;
          is_destructive: boolean;
        }>;
      }>
    >('/api/chat/tools/manifest');
    return unwrapAgentese(response);
  },

  /**
   * Set tool transparency level for session.
   *
   * @param sessionId - Session ID
   * @param level - Transparency level
   */
  setTransparency: async (
    sessionId: string,
    level: 'minimal' | 'approval' | 'detailed'
  ): Promise<{ success: boolean }> => {
    const response = await apiClient.post<AgenteseResponse<{ success: boolean }>>(
      `/api/chat/${sessionId}/transparency`,
      { level }
    );
    return unwrapAgentese(response);
  },

  /**
   * Approve a pending tool execution.
   *
   * @param sessionId - Session ID
   * @param toolExecutionId - Tool execution ID
   */
  approveTool: async (
    sessionId: string,
    toolExecutionId: string
  ): Promise<{ success: boolean }> => {
    const response = await apiClient.post<AgenteseResponse<{ success: boolean }>>(
      `/api/chat/${sessionId}/tools/${toolExecutionId}/approve`,
      {}
    );
    return unwrapAgentese(response);
  },

  /**
   * Deny a pending tool execution.
   *
   * @param sessionId - Session ID
   * @param toolExecutionId - Tool execution ID
   */
  denyTool: async (
    sessionId: string,
    toolExecutionId: string
  ): Promise<{ success: boolean }> => {
    const response = await apiClient.post<AgenteseResponse<{ success: boolean }>>(
      `/api/chat/${sessionId}/tools/${toolExecutionId}/deny`,
      {}
    );
    return unwrapAgentese(response);
  },
};
