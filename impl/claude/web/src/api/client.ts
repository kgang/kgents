import axios, { AxiosError, AxiosInstance } from 'axios';
import type {
  Town,
  CreateTownRequest,
  CitizensResponse,
  CitizenDetailResponse,
  CoalitionsResponse,
  CheckoutSession,
  // Workshop types removed (AD-009 Phase 3) - use AGENTESE world.workshop.*
  GalleryResponse,
  PilotResponse,
  GalleryCategoryInfo,
  GalleryOverrides,
  BrainCaptureRequest,
  BrainCaptureResponse,
  BrainGhostRequest,
  BrainGhostResponse,
  BrainMapResponse,
  BrainStatusResponse,
  BrainTopologyResponse,
  CodebaseManifestResponse,
  CodebaseHealthResponse,
  CodebaseDriftResponse,
  CodebaseModuleResponse,
  CodebaseTopologyResponse,
  CodebaseScanResponse,
} from './types';

const API_BASE = import.meta.env.VITE_API_URL || '';

// =============================================================================
// AGENTESE Universal Protocol Types
// =============================================================================

/**
 * AGENTESE Gateway response wrapper.
 * All AGENTESE routes wrap the actual result in this envelope.
 */
interface AgenteseResponse<T> {
  path: string;
  aspect: string;
  result: T;
  error?: string;
}

/**
 * Error type for AGENTESE-specific failures.
 */
export class AgenteseError extends Error {
  constructor(
    message: string,
    public readonly path: string,
    public readonly aspect?: string,
    public readonly suggestion?: string
  ) {
    super(message);
    this.name = 'AgenteseError';
  }
}

/**
 * Helper to extract the result from AGENTESE gateway response.
 * Robustified to handle edge cases and provide informative errors.
 *
 * @throws {AgenteseError} If response envelope is malformed or contains an error
 */
function unwrapAgentese<T>(response: { data: AgenteseResponse<T> }): T {
  // Check for missing data envelope
  if (!response.data) {
    throw new AgenteseError(
      'AGENTESE response missing data envelope',
      'unknown',
      undefined,
      'Check backend logs for route handler errors'
    );
  }

  // Check for AGENTESE-level errors
  if (response.data.error) {
    throw new AgenteseError(
      response.data.error,
      response.data.path || 'unknown',
      response.data.aspect,
      'Check /agentese/discover for available paths'
    );
  }

  // Handle case where result is explicitly undefined (valid for some aspects)
  if (response.data.result === undefined) {
    // Log warning in development
    if (import.meta.env.DEV) {
      console.warn(
        `[AGENTESE] ${response.data.path}/${response.data.aspect} returned undefined result`
      );
    }
  }

  const result = response.data.result;

  // Handle BasicRendering-style responses where actual data is in metadata
  // This pattern is used by Crown Jewels (Park, Town, etc.) for CLI-friendly output
  if (
    result &&
    typeof result === 'object' &&
    'metadata' in result &&
    'summary' in result &&
    'content' in result
  ) {
    // Check if metadata has the actual data (not just an error)
    const metadata = (result as { metadata: unknown }).metadata;
    if (
      metadata &&
      typeof metadata === 'object' &&
      !('error' in metadata && Object.keys(metadata as object).length === 1)
    ) {
      return metadata as T;
    }
  }

  return result;
}

/**
 * Wrap an AGENTESE API call with development logging.
 * Use this for debugging route resolution issues.
 *
 * @example
 * ```typescript
 * const result = await withAgenteseLogging('world.town.manifest', () =>
 *   apiClient.get('/agentese/world/town/manifest')
 * );
 * ```
 */
export async function withAgenteseLogging<T>(path: string, call: () => Promise<T>): Promise<T> {
  if (import.meta.env.DEV) {
    console.debug(`[AGENTESE] Calling: ${path}`);
  }
  try {
    const result = await call();
    if (import.meta.env.DEV) {
      console.debug(`[AGENTESE] ${path} succeeded:`, result);
    }
    return result;
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error(`[AGENTESE] ${path} failed:`, error);
    }
    throw error;
  }
}

/**
 * Axios instance with auth interceptor.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Add auth interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('api_key');
  if (token) {
    config.headers['X-API-Key'] = token;
  }
  return config;
});

// Add error interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - dispatch event but DON'T clear key
      // (clearing the key causes cascading failures)
      window.dispatchEvent(
        new CustomEvent('auth-required', {
          detail: { url: error.config?.url },
        })
      );
    }
    if (error.response?.status === 402) {
      // Payment required - dispatch paywall event
      window.dispatchEvent(
        new CustomEvent('paywall-triggered', {
          detail: error.response.data,
        })
      );
    }
    return Promise.reject(error);
  }
);

// =============================================================================
// Town API - AGENTESE Universal Protocol
// =============================================================================

export const townApi = {
  /**
   * Initialize a new town via AUP: /api/v1/town/{town_id}/init
   * Uses AUP routes (multi-tenant) instead of AGENTESE singleton.
   */
  create: async (data: CreateTownRequest = {}): Promise<Town> => {
    // Generate a town ID if not creating demo
    const townId = data.name?.toLowerCase().replace(/\s+/g, '-') || `town-${Date.now()}`;
    return townApi.createWithId(townId, data);
  },

  /**
   * Initialize a town with a specific ID via AUP: /api/v1/town/{town_id}/init
   */
  createWithId: async (townId: string, data: CreateTownRequest = {}): Promise<Town> => {
    const response = await apiClient.post<{
      town_id: string;
      status: string;
      citizens: string[];
      num_citizens: number;
      dialogue: { enabled: boolean };
    }>(`/api/v1/town/${townId}/init`, {
      num_citizens: 5,
      enable_dialogue: data.enable_dialogue ?? false,
    });
    // Transform AUP response to Town type
    return {
      id: response.data.town_id,
      name: data.name || 'Demo Town',
      citizen_count: response.data.num_citizens,
      region_count: 3, // Default regions
      coalition_count: 0,
      total_token_spend: 0,
      status: response.data.status === 'initialized' ? 'active' : 'paused',
    };
  },

  /** Get town status via AUP: /api/v1/town/{town_id}/status */
  get: async (townId: string): Promise<Town> => {
    const response = await apiClient.get<{
      town_id: string;
      day: number;
      phase: string;
      total_events: number;
      tension_index: number;
      cooperation_level: number;
      total_tokens?: number;
    }>(`/api/v1/town/${townId}/status`);
    return {
      id: response.data.town_id,
      name: townId,
      citizen_count: 5, // Default - actual count comes from SSE
      region_count: 3,
      coalition_count: 0,
      total_token_spend: response.data.total_tokens || 0,
      status: 'active',
    };
  },

  /** Delete/stop town - not yet implemented */
  delete: (townId: string) => apiClient.delete(`/api/v1/town/${townId}`),

  /** Step simulation via AUP: /api/v1/town/{town_id}/step */
  step: async (townId: string, _cycles: number = 1): Promise<unknown> => {
    const response = await apiClient.post(`/api/v1/town/${townId}/step`);
    return response.data;
  },

  /** Get citizens - derived from isometric widget via SSE events */
  getCitizens: async (_townId: string): Promise<CitizensResponse> => {
    // Citizens are streamed via SSE, not available via REST
    // Return placeholder - the SSE stream will populate
    return { citizens: [], total: 0, by_archetype: {}, by_region: {} };
  },

  /** Get citizen detail - not available via AUP REST, use SSE */
  getCitizen: async (
    _townId: string,
    name: string,
    _lod: number = 0,
    _userId: string = 'anonymous'
  ): Promise<CitizenDetailResponse> => {
    // Citizen details come from SSE stream - return placeholder
    return {
      lod: 0,
      citizen: {
        name,
        archetype: 'unknown',
        region: 'unknown',
        phase: 'IDLE',
      },
      cost_credits: 0,
    };
  },

  /** @deprecated Coalition feature removed 2025-12-21 */
  getCoalitions: async (_townId: string): Promise<CoalitionsResponse> => {
    return { coalitions: [], bridge_citizens: [] };
  },

  /** Get metrics - available via status endpoint */
  getMetrics: async (townId: string, _since_hours?: number): Promise<unknown> => {
    const response = await apiClient.get(`/api/v1/town/${townId}/status`);
    return response.data;
  },

  // =========================================================================
  // Dialogue API (Phase 5: Town End-to-End)
  // =========================================================================

  /**
   * Start a conversation with a citizen via AGENTESE: world.town.converse
   *
   * @param citizenId - The citizen's ID or name
   * @param topic - Optional conversation topic
   * @returns The created conversation with empty turns
   */
  converse: async (
    citizenId: string,
    topic?: string
  ): Promise<import('./types').ConversationDetail> => {
    const response = await apiClient.post<
      AgenteseResponse<{ conversation: import('./types').ConversationDetail }>
    >('/agentese/world/town/converse', {
      citizen_id: citizenId,
      topic,
    });
    return unwrapAgentese(response).conversation;
  },

  /**
   * Add a turn to a conversation via AGENTESE: world.town.turn
   *
   * The backend will:
   * 1. Store the user's message
   * 2. Generate a citizen response via LLM (DialogueService)
   * 3. Return both turns
   *
   * @param conversationId - The conversation ID
   * @param content - The user's message content
   * @returns The citizen's response turn
   */
  turn: async (conversationId: string, content: string): Promise<import('./types').TurnSummary> => {
    const response = await apiClient.post<
      AgenteseResponse<{ turn: import('./types').TurnSummary }>
    >('/agentese/world/town/turn', {
      conversation_id: conversationId,
      content,
      role: 'user',
    });
    return unwrapAgentese(response).turn;
  },

  /**
   * Get dialogue history for a citizen via AGENTESE: world.town.history
   *
   * @param citizenId - The citizen's ID or name
   * @param limit - Maximum number of conversations to return (default: 10)
   * @returns List of conversation summaries (without turns)
   */
  getHistory: async (
    citizenId: string,
    limit: number = 10
  ): Promise<import('./types').ConversationSummary[]> => {
    const response = await apiClient.post<
      AgenteseResponse<{
        citizen_id: string;
        conversations: import('./types').ConversationSummary[];
      }>
    >('/agentese/world/town/history', {
      citizen_id: citizenId,
      limit,
    });
    return unwrapAgentese(response).conversations;
  },
};

// =============================================================================
// INHABIT API - AGENTESE Universal Protocol
// =============================================================================

export const inhabitApi = {
  /** Start inhabit via AGENTESE: world.town.inhabit.start */
  start: async (
    _townId: string,
    citizenId: string,
    forceEnabled: boolean = false
  ): Promise<unknown> => {
    const response = await apiClient.post<AgenteseResponse<unknown>>(
      '/agentese/world/town/inhabit/start',
      { citizen_id: citizenId, force_enabled: forceEnabled }
    );
    return unwrapAgentese(response);
  },

  /** Get inhabit status via AGENTESE: world.town.inhabit.status */
  getStatus: async (_townId: string, citizenId: string): Promise<unknown> => {
    const response = await apiClient.post<AgenteseResponse<unknown>>(
      '/agentese/world/town/inhabit/status',
      { citizen_id: citizenId }
    );
    return unwrapAgentese(response);
  },

  /** Suggest action via AGENTESE: world.town.inhabit.suggest */
  suggest: async (_townId: string, citizenId: string, action: string): Promise<unknown> => {
    const response = await apiClient.post<AgenteseResponse<unknown>>(
      '/agentese/world/town/inhabit/suggest',
      { citizen_id: citizenId, action }
    );
    return unwrapAgentese(response);
  },

  /** Force action via AGENTESE: world.town.inhabit.force */
  force: async (
    _townId: string,
    citizenId: string,
    action: string,
    severity: number = 0.2
  ): Promise<unknown> => {
    const response = await apiClient.post<AgenteseResponse<unknown>>(
      '/agentese/world/town/inhabit/force',
      { citizen_id: citizenId, action, severity }
    );
    return unwrapAgentese(response);
  },

  /** Apologize via AGENTESE: world.town.inhabit.apologize */
  apologize: async (
    _townId: string,
    citizenId: string,
    sincerity: number = 0.3
  ): Promise<unknown> => {
    const response = await apiClient.post<AgenteseResponse<unknown>>(
      '/agentese/world/town/inhabit/apologize',
      { citizen_id: citizenId, sincerity }
    );
    return unwrapAgentese(response);
  },

  /** End inhabit via AGENTESE: world.town.inhabit.end */
  end: async (_townId: string, citizenId: string): Promise<unknown> => {
    const response = await apiClient.post<AgenteseResponse<unknown>>(
      '/agentese/world/town/inhabit/end',
      { citizen_id: citizenId }
    );
    return unwrapAgentese(response);
  },
};

// =============================================================================
// Payments API
// =============================================================================

export const paymentsApi = {
  createSubscriptionCheckout: (tier: string, successUrl?: string, cancelUrl?: string) =>
    apiClient.post<CheckoutSession>('/api/checkout/subscription', {
      tier,
      success_url: successUrl || `${window.location.origin}/checkout/success`,
      cancel_url: cancelUrl || `${window.location.origin}/`,
    }),

  createCreditsCheckout: (pack: string, successUrl?: string, cancelUrl?: string) =>
    apiClient.post<CheckoutSession>('/api/checkout/credits', {
      pack,
      success_url: successUrl || `${window.location.origin}/checkout/success`,
      cancel_url: cancelUrl || `${window.location.origin}/`,
    }),

  getBalance: () => apiClient.get('/api/user/credits'),

  spendCredits: (amount: number, action: string) =>
    apiClient.post('/api/user/credits/spend', { amount, action }),
};

// =============================================================================
// User API
// =============================================================================

export const userApi = {
  getProfile: () => apiClient.get('/api/user/profile'),

  updateProfile: (data: { name?: string; email?: string }) =>
    apiClient.put('/api/user/profile', data),
};

// =============================================================================
// Workshop API - REMOVED (AD-009 Phase 3)
// =============================================================================
// The /v1/workshop/* endpoints are superseded by:
// - GET /agentese/world/workshop/manifest - Workshop status
// - POST /agentese/world/workshop/task - Assign task
// - GET /agentese/world/workshop/stream (SSE) - Event stream
// - POST /agentese/world/workshop/builders - List builders
// - POST /agentese/world/workshop/perturb - Inject perturbation
// - POST /agentese/world/workshop/history - Task history
// - POST /agentese/world/workshop/metrics - Aggregate metrics
// See: protocols/agentese/contexts/world_workshop.py (WorkshopNode)

// =============================================================================
// Gallery API - AGENTESE Universal Protocol
// Routes:
//   world.gallery.manifest - All pilots
//   world.gallery.categories - Category list
//   world.gallery.pilot - Single pilot detail
// =============================================================================

export const galleryApi = {
  /** Get all pilots via AGENTESE: world.gallery.manifest */
  getAll: async (overrides?: GalleryOverrides, category?: string): Promise<GalleryResponse> => {
    const response = await apiClient.post<AgenteseResponse<GalleryResponse>>(
      '/agentese/world/gallery/manifest',
      { ...overrides, category }
    );
    return unwrapAgentese(response);
  },

  /** Get categories via AGENTESE: world.gallery.categories */
  getCategories: async (): Promise<{ categories: GalleryCategoryInfo[] }> => {
    const response = await apiClient.post<AgenteseResponse<{ categories: GalleryCategoryInfo[] }>>(
      '/agentese/world/gallery/categories',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Get single pilot via AGENTESE: world.gallery.pilot */
  getPilot: async (name: string, overrides?: GalleryOverrides): Promise<PilotResponse> => {
    const response = await apiClient.post<AgenteseResponse<PilotResponse>>(
      '/agentese/world/gallery/pilot',
      { name, ...overrides }
    );
    return unwrapAgentese(response);
  },
};

// =============================================================================
// Brain API (Holographic Brain) - AGENTESE Universal Protocol
// =============================================================================

export const brainApi = {
  /** Capture content to holographic memory via AGENTESE: self.memory.capture */
  capture: async (data: BrainCaptureRequest): Promise<BrainCaptureResponse> => {
    const response = await apiClient.post<AgenteseResponse<BrainCaptureResponse>>(
      '/agentese/self/memory/capture',
      data
    );
    return unwrapAgentese(response);
  },

  /** Surface ghost memories via AGENTESE: self.memory.ghost */
  ghost: async (data: BrainGhostRequest): Promise<BrainGhostResponse> => {
    const response = await apiClient.post<AgenteseResponse<BrainGhostResponse>>(
      '/agentese/self/memory/ghost',
      data
    );
    return unwrapAgentese(response);
  },

  /** Get brain map via AGENTESE: self.memory.map */
  getMap: async (): Promise<BrainMapResponse> => {
    const response = await apiClient.get<AgenteseResponse<BrainMapResponse>>(
      '/agentese/self/memory/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Get brain status via AGENTESE: self.memory.manifest */
  getStatus: async (): Promise<BrainStatusResponse> => {
    const response = await apiClient.get<AgenteseResponse<BrainStatusResponse>>(
      '/agentese/self/memory/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Get 3D topology data via AGENTESE: self.memory.topology */
  getTopology: async (similarityThreshold = 0.3): Promise<BrainTopologyResponse> => {
    const response = await apiClient.post<AgenteseResponse<BrainTopologyResponse>>(
      '/agentese/self/memory/topology',
      { similarity_threshold: similarityThreshold }
    );
    return unwrapAgentese(response);
  },
};

// =============================================================================
// Gestalt API (Living Architecture Visualizer) - AGENTESE Universal Protocol
// Routes:
//   world.codebase.manifest - Architecture overview
//   world.codebase.health - Health metrics
//   world.codebase.topology - 3D visualization data
//   world.codebase.module/* - Module details
//   world.codebase.scan - Trigger rescan
// =============================================================================

export const gestaltApi = {
  /** Get full architecture manifest via AGENTESE: world.codebase.manifest */
  getManifest: async (): Promise<CodebaseManifestResponse> => {
    const response = await apiClient.get<AgenteseResponse<CodebaseManifestResponse>>(
      '/agentese/world/codebase/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Get health metrics summary via AGENTESE: world.codebase.health */
  getHealth: async (): Promise<CodebaseHealthResponse> => {
    const response = await apiClient.get<AgenteseResponse<CodebaseHealthResponse>>(
      '/agentese/world/codebase/health'
    );
    return unwrapAgentese(response);
  },

  /** Get drift violations via AGENTESE: world.codebase.drift */
  getDrift: async (): Promise<CodebaseDriftResponse> => {
    const response = await apiClient.get<AgenteseResponse<CodebaseDriftResponse>>(
      '/agentese/world/codebase/drift'
    );
    return unwrapAgentese(response);
  },

  /** Get module details via AGENTESE: world.codebase (aspect: module) */
  getModule: async (moduleName: string): Promise<CodebaseModuleResponse> => {
    const response = await apiClient.post<AgenteseResponse<CodebaseModuleResponse>>(
      '/agentese/world/codebase/module',
      { module_name: moduleName }
    );
    return unwrapAgentese(response);
  },

  /** Get topology for visualization via AGENTESE: world.codebase.topology */
  getTopology: async (
    maxNodes = 200,
    minHealth = 0.0,
    role?: string
  ): Promise<CodebaseTopologyResponse> => {
    const response = await apiClient.post<AgenteseResponse<CodebaseTopologyResponse>>(
      '/agentese/world/codebase/topology',
      {
        max_nodes: maxNodes,
        min_health: minHealth,
        ...(role && { role }), // Observer role for observer-dependent views
      }
    );
    return unwrapAgentese(response);
  },

  /** Force rescan of codebase via AGENTESE: world.codebase.scan */
  scan: async (language = 'python', path?: string): Promise<CodebaseScanResponse> => {
    const response = await apiClient.post<AgenteseResponse<CodebaseScanResponse>>(
      '/agentese/world/codebase/scan',
      { language, path }
    );
    return unwrapAgentese(response);
  },

  /** Create EventSource for topology stream via AGENTESE: world.codebase.topology/stream */
  createTopologyStream: (options?: {
    maxNodes?: number;
    minHealth?: number;
    pollInterval?: number;
  }) => {
    const baseUrl = apiClient.defaults.baseURL || '';
    const params = new URLSearchParams();
    if (options?.maxNodes) params.set('max_nodes', options.maxNodes.toString());
    if (options?.minHealth) params.set('min_health', options.minHealth.toString());
    if (options?.pollInterval) params.set('poll_interval', options.pollInterval.toString());
    const queryString = params.toString();
    // SSE endpoint uses AGENTESE gateway path
    return new EventSource(
      `${baseUrl}/agentese/world/codebase/topology/stream${queryString ? `?${queryString}` : ''}`
    );
  },
};

// =============================================================================
// Infrastructure API (Gestalt Live) - AGENTESE Universal Protocol
// Routes:
//   world.gestalt.live.status - Collector status
//   world.gestalt.live.connect - Connect to K8s
//   world.gestalt.live.disconnect - Disconnect
//   world.gestalt.live.topology - Current topology
//   world.gestalt.live.topology_stream - SSE topology updates
//   world.gestalt.live.events_stream - SSE event stream
//   world.gestalt.live.health - Aggregate health
//   world.gestalt.live.entity_detail - Entity details
// =============================================================================

import type {
  InfraTopologyResponse,
  InfraHealthResponse,
  InfraEntity,
  InfraStatusResponse,
} from './types';

export const infraApi = {
  /** Get collector status via AGENTESE: world.gestalt.live.status */
  getStatus: async (): Promise<InfraStatusResponse> => {
    const response = await apiClient.get<AgenteseResponse<InfraStatusResponse>>(
      '/agentese/world/gestalt/live/status/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Connect to infrastructure data source via AGENTESE: world.gestalt.live.connect */
  connect: async (): Promise<{ status: string }> => {
    const response = await apiClient.post<AgenteseResponse<{ status: string }>>(
      '/agentese/world/gestalt/live/connect',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Disconnect from infrastructure data source via AGENTESE: world.gestalt.live.disconnect */
  disconnect: async (): Promise<{ status: string }> => {
    const response = await apiClient.post<AgenteseResponse<{ status: string }>>(
      '/agentese/world/gestalt/live/disconnect',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Get current infrastructure topology via AGENTESE: world.gestalt.live.topology */
  getTopology: async (params?: {
    namespaces?: string;
    kinds?: string;
    min_health?: number;
  }): Promise<InfraTopologyResponse> => {
    const response = await apiClient.post<AgenteseResponse<InfraTopologyResponse>>(
      '/agentese/world/gestalt/live/topology',
      params || {}
    );
    return unwrapAgentese(response);
  },

  /** Get aggregate infrastructure health via AGENTESE: world.gestalt.live.health */
  getHealth: async (): Promise<InfraHealthResponse> => {
    const response = await apiClient.post<AgenteseResponse<InfraHealthResponse>>(
      '/agentese/world/gestalt/live/health',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Get single entity details via AGENTESE: world.gestalt.live.entity_detail */
  getEntity: async (entityId: string): Promise<InfraEntity> => {
    const response = await apiClient.post<AgenteseResponse<InfraEntity>>(
      '/agentese/world/gestalt/live/entity_detail',
      { entity_id: entityId }
    );
    return unwrapAgentese(response);
  },

  /** Create EventSource for topology stream via AGENTESE: world.gestalt.live.topology_stream */
  createTopologyStream: () => {
    const baseUrl = apiClient.defaults.baseURL || '';
    return new EventSource(`${baseUrl}/agentese/world/gestalt/live/topology_stream/stream`);
  },

  /** Create EventSource for events stream via AGENTESE: world.gestalt.live.events_stream */
  createEventsStream: () => {
    const baseUrl = apiClient.defaults.baseURL || '';
    return new EventSource(`${baseUrl}/agentese/world/gestalt/live/events_stream/stream`);
  },
};

// =============================================================================
// Design API (Design Language System) - AGENTESE Universal Protocol
// Routes:
//   concept.design.manifest - Design system overview
//   concept.design.layout.* - Layout operad operations
//   concept.design.content.* - Content operad operations
//   concept.design.motion.* - Motion operad operations
//   concept.design.operad.* - Unified design operad
// =============================================================================

/**
 * Response from operad verification.
 */
export interface OperadVerifyResult {
  law: string;
  status: string;
  passed: boolean;
  message: string;
}

export interface OperadVerifyResponse {
  all_passed: boolean;
  results: OperadVerifyResult[];
}

export interface OperadOperation {
  arity: number;
  signature: string;
  description: string;
}

export interface OperadLaw {
  name: string;
  equation: string;
  description: string;
}

export interface DesignManifestResponse {
  dimensions: string[];
  operad: string;
}

export interface OperadManifestResponse {
  name: string;
  operations: string[];
  law_count: number;
}

export const designApi = {
  /** Get design system overview via AGENTESE: concept.design.manifest */
  manifest: async (): Promise<DesignManifestResponse> => {
    const response = await apiClient.get<AgenteseResponse<DesignManifestResponse>>(
      '/agentese/concept/design/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Get layout operad state via AGENTESE: concept.design.layout.manifest */
  layoutManifest: async (): Promise<OperadManifestResponse> => {
    const response = await apiClient.get<AgenteseResponse<OperadManifestResponse>>(
      '/agentese/concept/design/layout/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Get layout operations via AGENTESE: concept.design.layout.operations */
  layoutOperations: async (): Promise<Record<string, OperadOperation>> => {
    const response = await apiClient.post<AgenteseResponse<Record<string, OperadOperation>>>(
      '/agentese/concept/design/layout/operations',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Verify layout laws via AGENTESE: concept.design.layout.verify */
  layoutVerify: async (): Promise<OperadVerifyResult[]> => {
    const response = await apiClient.post<AgenteseResponse<OperadVerifyResult[]>>(
      '/agentese/concept/design/layout/verify',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Get content operad state via AGENTESE: concept.design.content.manifest */
  contentManifest: async (): Promise<OperadManifestResponse> => {
    const response = await apiClient.get<AgenteseResponse<OperadManifestResponse>>(
      '/agentese/concept/design/content/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Get content operations via AGENTESE: concept.design.content.operations */
  contentOperations: async (): Promise<Record<string, OperadOperation>> => {
    const response = await apiClient.post<AgenteseResponse<Record<string, OperadOperation>>>(
      '/agentese/concept/design/content/operations',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Get motion operad state via AGENTESE: concept.design.motion.manifest */
  motionManifest: async (): Promise<OperadManifestResponse> => {
    const response = await apiClient.get<AgenteseResponse<OperadManifestResponse>>(
      '/agentese/concept/design/motion/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Get motion operations via AGENTESE: concept.design.motion.operations */
  motionOperations: async (): Promise<Record<string, OperadOperation>> => {
    const response = await apiClient.post<AgenteseResponse<Record<string, OperadOperation>>>(
      '/agentese/concept/design/motion/operations',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Verify all design laws via AGENTESE: concept.design.operad.verify */
  operadVerify: async (): Promise<OperadVerifyResponse> => {
    const response = await apiClient.post<AgenteseResponse<OperadVerifyResponse>>(
      '/agentese/concept/design/operad/verify',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Check naturality law via AGENTESE: concept.design.operad.naturality */
  operadNaturality: async (): Promise<OperadVerifyResult> => {
    const response = await apiClient.post<AgenteseResponse<OperadVerifyResult>>(
      '/agentese/concept/design/operad/naturality',
      {}
    );
    return unwrapAgentese(response);
  },
};

// =============================================================================
// Park API (Wave 3: Punchdrunk Park)
// =============================================================================

import type {
  ParkScenarioState,
  ParkStartScenarioRequest,
  ParkTickRequest,
  ParkTransitionPhaseRequest,
  ParkMaskActionRequest,
  ParkCompleteRequest,
  ParkScenarioSummary,
  ParkMaskInfo,
  ParkStatusResponse,
} from './types';

// =============================================================================
// Park API (AGENTESE Universal Protocol)
// Routes:
//   world.park.manifest - Park status
//   world.park.scenario.* - Crisis practice scenarios
//   world.park.mask.* - Dialogue masks
//   world.park.force.* - Force mechanic
// =============================================================================

export const parkApi = {
  /** Get current scenario state via AGENTESE: world.park.manifest */
  getScenario: async (): Promise<ParkScenarioState> => {
    const response = await apiClient.get<AgenteseResponse<ParkScenarioState>>(
      '/agentese/world/park/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Start a new crisis practice scenario via AGENTESE: world.park.scenario.start */
  startScenario: async (data: ParkStartScenarioRequest = {}): Promise<ParkScenarioState> => {
    const response = await apiClient.post<AgenteseResponse<ParkScenarioState>>(
      '/agentese/world/park/scenario/start',
      data
    );
    return unwrapAgentese(response);
  },

  /** Tick scenario timers via AGENTESE: world.park.scenario.tick */
  tick: async (data: ParkTickRequest = { count: 1 }): Promise<ParkScenarioState> => {
    const response = await apiClient.post<AgenteseResponse<ParkScenarioState>>(
      '/agentese/world/park/scenario/tick',
      data
    );
    return unwrapAgentese(response);
  },

  /** Transition crisis phase via AGENTESE: world.park.scenario.phase */
  transitionPhase: async (data: ParkTransitionPhaseRequest): Promise<ParkScenarioState> => {
    const response = await apiClient.post<AgenteseResponse<ParkScenarioState>>(
      '/agentese/world/park/scenario/phase',
      data
    );
    return unwrapAgentese(response);
  },

  /** Don or doff a dialogue mask via AGENTESE: world.park.mask.don/doff */
  maskAction: async (data: ParkMaskActionRequest): Promise<ParkScenarioState> => {
    const action = data.action === 'don' ? 'don' : 'doff';
    const response = await apiClient.post<AgenteseResponse<ParkScenarioState>>(
      `/agentese/world/park/mask/${action}`,
      data
    );
    return unwrapAgentese(response);
  },

  /** Use force mechanic via AGENTESE: world.park.force.use */
  useForce: async (): Promise<ParkScenarioState> => {
    const response = await apiClient.post<AgenteseResponse<ParkScenarioState>>(
      '/agentese/world/park/force/use',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Complete scenario via AGENTESE: world.park.scenario.complete */
  completeScenario: async (
    data: ParkCompleteRequest = { outcome: 'success' }
  ): Promise<ParkScenarioSummary> => {
    const response = await apiClient.post<AgenteseResponse<ParkScenarioSummary>>(
      '/agentese/world/park/scenario/complete',
      data
    );
    return unwrapAgentese(response);
  },

  /** List all available masks via AGENTESE: world.park.mask.manifest */
  getMasks: async (): Promise<ParkMaskInfo[]> => {
    const response = await apiClient.get<AgenteseResponse<{ masks: ParkMaskInfo[] }>>(
      '/agentese/world/park/mask/manifest'
    );
    const result = unwrapAgentese(response);
    return result.masks || [];
  },

  /** Get mask details via AGENTESE: world.park.mask.show */
  getMask: async (name: string): Promise<ParkMaskInfo> => {
    const response = await apiClient.post<AgenteseResponse<ParkMaskInfo>>(
      '/agentese/world/park/mask/show',
      { name }
    );
    return unwrapAgentese(response);
  },

  /** Get Park system status via AGENTESE: world.park.manifest */
  getStatus: async (): Promise<ParkStatusResponse> => {
    const response = await apiClient.get<AgenteseResponse<ParkStatusResponse>>(
      '/agentese/world/park/manifest'
    );
    return unwrapAgentese(response);
  },
};

// =============================================================================
// Interactive Text API (Documents as Control Surfaces) - AGENTESE Universal Protocol
// Routes:
//   self.document.manifest - Service status and capabilities
//   self.document.parse - Parse markdown to SceneGraph
//   self.document.task_toggle - Toggle task checkbox with TraceWitness
// =============================================================================

/**
 * Response from document parsing.
 */
export interface DocumentParseResponse {
  scene_graph: unknown;
  token_count: number;
  token_types: Record<string, number>;
}

/**
 * Response from task toggle operation.
 */
export interface TaskToggleResponse {
  success: boolean;
  new_state: boolean;
  task_description: string;
  trace_witness_id: string | null;
  file_updated: boolean;
  error: string | null;
}

/**
 * Response from document manifest (status).
 */
export interface DocumentManifestResponse {
  status: string;
  token_types: string[];
  features: string[];
}

export const documentApi = {
  /** Get service status via AGENTESE: self.document.manifest */
  getStatus: async (): Promise<DocumentManifestResponse> => {
    const response = await apiClient.get<AgenteseResponse<DocumentManifestResponse>>(
      '/agentese/self/document/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Parse markdown text to SceneGraph via AGENTESE: self.document.parse */
  parse: async (text: string, layoutMode = 'COMFORTABLE'): Promise<DocumentParseResponse> => {
    const response = await apiClient.post<AgenteseResponse<DocumentParseResponse>>(
      '/agentese/self/document/parse',
      { text, layout_mode: layoutMode }
    );
    return unwrapAgentese(response);
  },

  /** Toggle task checkbox via AGENTESE: self.document.task_toggle */
  toggleTask: async (
    options:
      | { file_path: string; task_id?: string; line_number?: number }
      | { text: string; line_number: number }
  ): Promise<TaskToggleResponse> => {
    const response = await apiClient.post<AgenteseResponse<TaskToggleResponse>>(
      '/agentese/self/document/task_toggle',
      options
    );
    return unwrapAgentese(response);
  },
};

// =============================================================================
// File API (AGENTESE world.file.*)
// =============================================================================

/**
 * Response from reading a file via AGENTESE world.file.read.
 */
export interface FileReadResponse {
  path: string;
  content: string;
  size: number;
  mtime: number;
  encoding: string;
  cached_at: number;
  lines: number;
  truncated: boolean;
}

export const fileApi = {
  /** Read file content via AGENTESE: world.file.read */
  read: async (path: string): Promise<FileReadResponse> => {
    const response = await apiClient.post<AgenteseResponse<FileReadResponse>>(
      '/agentese/world/file/read',
      { path }
    );
    return unwrapAgentese(response);
  },
};

// =============================================================================
// K-Block API (Transactional Editing) - AGENTESE Universal Protocol
// Routes:
//   self.kblock.manifest - Active K-Blocks
//   self.kblock.create - Create K-Block for file
//   self.kblock.save - Commit K-Block to cosmos
//   self.kblock.discard - Abandon K-Block
//   self.kblock.view_edit - Edit via any view (Phase 3 bidirectional)
//   self.kblock.checkpoint - Create named restore point
//   self.kblock.rewind - Restore to checkpoint
//
// Philosophy:
//   "The K-Block is not where you edit a document.
//    It's where you edit a possible world."
// =============================================================================

/**
 * K-Block isolation states.
 */
export type KBlockIsolation = 'PRISTINE' | 'DIRTY' | 'STALE' | 'CONFLICTING' | 'ENTANGLED';

/**
 * View types available in K-Block.
 */
export type KBlockViewType = 'prose' | 'graph' | 'code' | 'outline' | 'diff' | 'references';

/**
 * K-Block summary for manifest.
 */
export interface KBlockInfo {
  id: string;
  path: string;
  isolation: KBlockIsolation;
  is_dirty: boolean;
  checkpoints: number;
  created_at: string;
  modified_at: string;
}

/**
 * Response from K-Block manifest.
 */
export interface KBlockManifestResponse {
  active_blocks: number;
  blocks: KBlockInfo[];
}

/**
 * Response from K-Block creation.
 */
export interface KBlockCreateResponse {
  block_id: string;
  path: string;
  isolation: KBlockIsolation;
  content_preview?: string;
}

/**
 * Response from K-Block save.
 */
export interface KBlockSaveResponse {
  success: boolean;
  path: string;
  version_id?: string;
  no_changes?: boolean;
  error?: string;
}

/**
 * Response from K-Block discard.
 */
export interface KBlockDiscardResponse {
  success: boolean;
  discarded: string;
}

/**
 * Semantic delta from view edit (Phase 3).
 */
export interface SemanticDelta {
  kind: 'add' | 'remove' | 'modify';
  token_id: string;
  token_kind: string;
  token_value: string;
  old_value?: string;
  new_value?: string;
  parent_id?: string;
  position_hint?: number;
  timestamp: string;
}

/**
 * Response from view edit operation.
 */
export interface KBlockViewEditResponse {
  success: boolean;
  block_id: string;
  source_view: KBlockViewType;
  semantic_deltas: SemanticDelta[];
  content_changed: boolean;
  trace?: {
    source_view: string;
    semantic_deltas: SemanticDelta[];
    old_content_hash: number;
    new_content_hash: number;
    content_changed: boolean;
    actor: string;
    reasoning?: string;
    timestamp: string;
  };
  error?: string;
}

/**
 * Response from checkpoint creation.
 */
export interface KBlockCheckpointResponse {
  checkpoint_id: string;
  name: string;
  block_id: string;
}

/**
 * Reference discovered by ReferencesView.
 */
export interface KBlockReference {
  kind: 'implements' | 'tests' | 'extends' | 'extended_by' | 'references' | 'heritage';
  target: string;
  context?: string;
  line_number?: number;
  confidence: number;
  stale: boolean;
  exists: boolean;
}

/**
 * Response from getting K-Block content (for initial load).
 */
export interface KBlockContentResponse {
  block_id: string;
  path: string;
  content: string;
  base_content: string;
  isolation: KBlockIsolation;
  is_dirty: boolean;
  active_views: KBlockViewType[];
  checkpoints: Array<{
    id: string;
    name: string;
    content_hash: string;
    created_at: string;
  }>;
}

export const kblockApi = {
  /**
   * Get active K-Blocks via AGENTESE: self.kblock.manifest
   */
  manifest: async (): Promise<KBlockManifestResponse> => {
    const response = await apiClient.get<AgenteseResponse<KBlockManifestResponse>>(
      '/agentese/self/kblock/manifest'
    );
    return unwrapAgentese(response);
  },

  /**
   * Create K-Block for file via AGENTESE: self.kblock.create
   *
   * @param path - File path to create K-Block for
   * @returns Created K-Block info including block_id
   */
  create: async (path: string): Promise<KBlockCreateResponse> => {
    const response = await apiClient.post<AgenteseResponse<KBlockCreateResponse>>(
      '/agentese/self/kblock/create',
      { path }
    );
    return unwrapAgentese(response);
  },

  /**
   * Get K-Block content via AGENTESE: self.kblock.get
   *
   * @param blockId - K-Block ID
   * @returns Full K-Block content and state
   */
  get: async (blockId: string): Promise<KBlockContentResponse> => {
    const response = await apiClient.post<AgenteseResponse<KBlockContentResponse>>(
      '/agentese/self/kblock/get',
      { block_id: blockId }
    );
    return unwrapAgentese(response);
  },

  /**
   * Save K-Block to cosmos via AGENTESE: self.kblock.save
   *
   * Commits changes and exits isolation.
   *
   * @param blockId - K-Block ID
   * @param reasoning - Optional reasoning for witness trace
   */
  save: async (blockId: string, reasoning?: string): Promise<KBlockSaveResponse> => {
    const response = await apiClient.post<AgenteseResponse<KBlockSaveResponse>>(
      '/agentese/self/kblock/save',
      { block_id: blockId, reasoning }
    );
    return unwrapAgentese(response);
  },

  /**
   * Discard K-Block via AGENTESE: self.kblock.discard
   *
   * Abandons changes without saving. No cosmic effects.
   *
   * @param blockId - K-Block ID
   */
  discard: async (blockId: string): Promise<KBlockDiscardResponse> => {
    const response = await apiClient.post<AgenteseResponse<KBlockDiscardResponse>>(
      '/agentese/self/kblock/discard',
      { block_id: blockId }
    );
    return unwrapAgentese(response);
  },

  /**
   * Edit via any view (Phase 3 bidirectional) via AGENTESE: self.kblock.view_edit
   *
   * Semantic deltas are extracted and propagated to prose.
   * All views refresh automatically.
   *
   * @param blockId - K-Block ID
   * @param sourceView - Which view was edited
   * @param content - New content
   * @param reasoning - Optional reasoning for witness trace
   */
  viewEdit: async (
    blockId: string,
    sourceView: KBlockViewType,
    content: string,
    reasoning?: string
  ): Promise<KBlockViewEditResponse> => {
    const response = await apiClient.post<AgenteseResponse<KBlockViewEditResponse>>(
      '/agentese/self/kblock/view_edit',
      {
        block_id: blockId,
        source_view: sourceView,
        content,
        reasoning,
      }
    );
    return unwrapAgentese(response);
  },

  /**
   * Create checkpoint via AGENTESE: self.kblock.checkpoint
   *
   * Named restore point within K-Block lifetime.
   *
   * @param blockId - K-Block ID
   * @param name - Checkpoint name
   */
  checkpoint: async (blockId: string, name: string): Promise<KBlockCheckpointResponse> => {
    const response = await apiClient.post<AgenteseResponse<KBlockCheckpointResponse>>(
      '/agentese/self/kblock/checkpoint',
      { block_id: blockId, name }
    );
    return unwrapAgentese(response);
  },

  /**
   * Rewind to checkpoint via AGENTESE: self.kblock.rewind
   *
   * @param blockId - K-Block ID
   * @param checkpointId - Checkpoint ID to restore
   */
  rewind: async (
    blockId: string,
    checkpointId: string
  ): Promise<{ success: boolean; block_id: string; rewound_to: string }> => {
    const response = await apiClient.post<
      AgenteseResponse<{ success: boolean; block_id: string; rewound_to: string }>
    >('/agentese/self/kblock/rewind', { block_id: blockId, checkpoint_id: checkpointId });
    return unwrapAgentese(response);
  },

  /**
   * Get references for K-Block via AGENTESE: self.kblock.references
   *
   * Discovers implements, tests, extends relationships.
   *
   * @param blockId - K-Block ID
   */
  references: async (blockId: string): Promise<{ references: KBlockReference[] }> => {
    const response = await apiClient.post<AgenteseResponse<{ references: KBlockReference[] }>>(
      '/agentese/self/kblock/references',
      { block_id: blockId }
    );
    return unwrapAgentese(response);
  },
};

// =============================================================================
// WitnessedGraph API (9th Crown Jewel) - AGENTESE Universal Protocol
// Routes:
//   concept.graph.manifest - Graph stats
//   concept.graph.neighbors - Edges connected to a path
//   concept.graph.evidence - Evidence supporting a spec
//   concept.graph.trace - Path between nodes
//   concept.graph.search - Search edges by query
//
// Philosophy:
//   "The file is a lie. There is only the graph."
// =============================================================================

import type {
  ConceptGraphManifestResponse,
  ConceptGraphNeighborsResponse,
  ConceptGraphEvidenceResponse,
  ConceptGraphTraceResponse,
  ConceptGraphSearchResponse,
} from './types/_generated/concept-graph';

export const graphApi = {
  /**
   * Get graph stats via AGENTESE: concept.graph.manifest
   */
  manifest: async (): Promise<ConceptGraphManifestResponse> => {
    const response = await apiClient.post<AgenteseResponse<ConceptGraphManifestResponse>>(
      '/agentese/concept/graph/manifest',
      {}
    );
    return unwrapAgentese(response);
  },

  /**
   * Get edges connected to a path via AGENTESE: concept.graph.neighbors
   *
   * @param path - File path to get neighbors for
   */
  neighbors: async (path: string): Promise<ConceptGraphNeighborsResponse> => {
    const response = await apiClient.post<AgenteseResponse<ConceptGraphNeighborsResponse>>(
      '/agentese/concept/graph/neighbors',
      { path }
    );
    return unwrapAgentese(response);
  },

  /**
   * Get evidence supporting a spec via AGENTESE: concept.graph.evidence
   *
   * @param specPath - Spec file path
   */
  evidence: async (specPath: string): Promise<ConceptGraphEvidenceResponse> => {
    const response = await apiClient.post<AgenteseResponse<ConceptGraphEvidenceResponse>>(
      '/agentese/concept/graph/evidence',
      { spec_path: specPath }
    );
    return unwrapAgentese(response);
  },

  /**
   * Find path between nodes via AGENTESE: concept.graph.trace
   *
   * @param start - Start path
   * @param end - End path
   * @param maxDepth - Maximum search depth (default: 5)
   */
  trace: async (start: string, end: string, maxDepth = 5): Promise<ConceptGraphTraceResponse> => {
    const response = await apiClient.post<AgenteseResponse<ConceptGraphTraceResponse>>(
      '/agentese/concept/graph/trace',
      { start, end, max_depth: maxDepth }
    );
    return unwrapAgentese(response);
  },

  /**
   * Search edges by query via AGENTESE: concept.graph.search
   *
   * @param query - Search query
   * @param limit - Maximum results (default: 100)
   */
  search: async (query: string, limit = 100): Promise<ConceptGraphSearchResponse> => {
    const response = await apiClient.post<AgenteseResponse<ConceptGraphSearchResponse>>(
      '/agentese/concept/graph/search',
      { query, limit }
    );
    return unwrapAgentese(response);
  },
};
