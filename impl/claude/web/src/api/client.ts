import axios, { AxiosError, AxiosInstance } from 'axios';
import type {
  Town,
  CreateTownRequest,
  CitizensResponse,
  CitizenDetailResponse,
  CoalitionsResponse,
  CheckoutSession,
  WorkshopStatus,
  WorkshopPlan,
  BuilderSummary,
  TaskHistoryResponse,
  TaskDetailResponse,
  AggregateMetrics,
  BuilderPerformanceMetrics,
  FlowMetrics,
  WorkshopEvent,
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
    if (metadata && typeof metadata === 'object' && !('error' in metadata && Object.keys(metadata as object).length === 1)) {
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
export async function withAgenteseLogging<T>(
  path: string,
  call: () => Promise<T>
): Promise<T> {
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

  /** Get coalitions - not yet implemented in AUP */
  getCoalitions: async (_townId: string): Promise<CoalitionsResponse> => {
    return { coalitions: [], bridge_citizens: [] };
  },

  /** Get metrics - available via status endpoint */
  getMetrics: async (townId: string, _since_hours?: number): Promise<unknown> => {
    const response = await apiClient.get(`/api/v1/town/${townId}/status`);
    return response.data;
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
// Workshop API
// =============================================================================

export const workshopApi = {
  get: () => apiClient.get<WorkshopStatus>('/v1/workshop'),

  assignTask: (description: string, priority: number = 1) =>
    apiClient.post<WorkshopPlan>('/v1/workshop/task', { description, priority }),

  getStatus: () => apiClient.get<WorkshopStatus>('/v1/workshop/status'),

  getBuilders: () =>
    apiClient.get<{ builders: BuilderSummary[]; count: number }>('/v1/workshop/builders'),

  getBuilder: (archetype: string, lod: number = 1) =>
    apiClient.get(`/v1/workshop/builder/${archetype}?lod=${lod}`),

  whisper: (archetype: string, message: string) =>
    apiClient.post(`/v1/workshop/builder/${archetype}/whisper`, { message }),

  perturb: (action: string, builder?: string, artifact?: unknown) =>
    apiClient.post('/v1/workshop/perturb', { action, builder, artifact }),

  reset: () => apiClient.post('/v1/workshop/reset'),

  getArtifacts: () => apiClient.get('/v1/workshop/artifacts'),

  // History endpoints (Chunk 9)
  getHistory: (page: number = 1, pageSize: number = 10, status?: string) =>
    apiClient.get<TaskHistoryResponse>('/v1/workshop/history', {
      params: { page, page_size: pageSize, status },
    }),

  getTaskDetail: (taskId: string) =>
    apiClient.get<TaskDetailResponse>(`/v1/workshop/history/${taskId}`),

  getTaskEvents: (taskId: string) =>
    apiClient.get<{
      task_id: string;
      events: WorkshopEvent[];
      count: number;
      duration_seconds: number;
    }>(`/v1/workshop/history/${taskId}/events`),

  // Metrics endpoints (Chunk 9)
  getAggregateMetrics: (period: string = '24h') =>
    apiClient.get<AggregateMetrics>('/v1/workshop/metrics/aggregate', {
      params: { period },
    }),

  getBuilderMetrics: (archetype: string, period: string = '24h') =>
    apiClient.get<BuilderPerformanceMetrics>(`/v1/workshop/metrics/builder/${archetype}`, {
      params: { period },
    }),

  getFlowMetrics: () => apiClient.get<FlowMetrics>('/v1/workshop/metrics/flow'),
};

// =============================================================================
// Gallery API
// =============================================================================

export const galleryApi = {
  getAll: (overrides?: GalleryOverrides, category?: string) =>
    apiClient.get<GalleryResponse>('/api/gallery', {
      params: { ...overrides, category },
    }),

  getCategories: () =>
    apiClient.get<{ categories: GalleryCategoryInfo[] }>('/api/gallery/categories'),

  getPilot: (name: string, overrides?: GalleryOverrides) =>
    apiClient.get<PilotResponse>(`/api/gallery/${name}`, {
      params: overrides,
    }),
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
    return new EventSource(`${baseUrl}/agentese/world/codebase/topology/stream${queryString ? `?${queryString}` : ''}`);
  },
};

// =============================================================================
// Infrastructure API (Gestalt Live)
// =============================================================================

import type {
  InfraTopologyResponse,
  InfraHealthResponse,
  InfraEntity,
  InfraStatusResponse,
} from './types';

export const infraApi = {
  /** Get collector status */
  getStatus: () => apiClient.get<InfraStatusResponse>('/api/infra/status'),

  /** Connect to infrastructure data source */
  connect: () => apiClient.post<{ status: string }>('/api/infra/connect'),

  /** Disconnect from infrastructure data source */
  disconnect: () => apiClient.post<{ status: string }>('/api/infra/disconnect'),

  /** Get current infrastructure topology */
  getTopology: (params?: {
    namespaces?: string;
    kinds?: string;
    min_health?: number;
  }) =>
    apiClient.get<InfraTopologyResponse>('/api/infra/topology', { params }),

  /** Get aggregate infrastructure health */
  getHealth: () => apiClient.get<InfraHealthResponse>('/api/infra/health'),

  /** Get single entity details */
  getEntity: (entityId: string) =>
    apiClient.get<InfraEntity>(`/api/infra/entity/${encodeURIComponent(entityId)}`),

  /** Create EventSource for topology stream */
  createTopologyStream: () => {
    const baseUrl = apiClient.defaults.baseURL || '';
    return new EventSource(`${baseUrl}/api/infra/topology/stream`);
  },

  /** Create EventSource for events stream */
  createEventsStream: () => {
    const baseUrl = apiClient.defaults.baseURL || '';
    return new EventSource(`${baseUrl}/api/infra/events/stream`);
  },
};

// =============================================================================
// Gardener API (AGENTESE Universal Protocol)
// Routes:
//   concept.gardener.* - Session management
//   self.garden.* - Idea lifecycle
//   void.garden.* - Serendipity
// =============================================================================

import type {
  GardenerSessionState,
  PolynomialVisualization,
} from './types';

interface GardenerCreateRequest {
  name?: string;
  plan_path?: string;
  intent?: {
    description: string;
    priority?: string;
  };
}

interface GardenerSessionListResponse {
  sessions: GardenerSessionState[];
  active_session_id?: string;
}

interface GardenerPolynomialResponse {
  visualization: PolynomialVisualization;
  agentese_path?: string;
}

export const gardenerApi = {
  /** Get active session via AGENTESE: concept.gardener.manifest */
  getSession: async (): Promise<GardenerSessionState> => {
    const response = await apiClient.get<AgenteseResponse<GardenerSessionState>>(
      '/agentese/concept/gardener/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Create new session via AGENTESE: concept.gardener.start */
  createSession: async (data: GardenerCreateRequest = {}): Promise<GardenerSessionState> => {
    const response = await apiClient.post<AgenteseResponse<GardenerSessionState>>(
      '/agentese/concept/gardener/start',
      data
    );
    return unwrapAgentese(response);
  },

  /** Advance to next phase via AGENTESE: concept.gardener.advance */
  advanceSession: async (): Promise<GardenerSessionState> => {
    const response = await apiClient.post<AgenteseResponse<GardenerSessionState>>(
      '/agentese/concept/gardener/advance',
      {}
    );
    return unwrapAgentese(response);
  },

  /** Get polynomial visualization via AGENTESE: concept.gardener.polynomial */
  getPolynomial: async (): Promise<GardenerPolynomialResponse> => {
    const response = await apiClient.post<AgenteseResponse<GardenerPolynomialResponse>>(
      '/agentese/concept/gardener/polynomial',
      {}
    );
    return unwrapAgentese(response);
  },

  /** List recent sessions via AGENTESE: concept.gardener.sessions */
  listSessions: async (limit = 10): Promise<GardenerSessionListResponse> => {
    const response = await apiClient.post<AgenteseResponse<GardenerSessionListResponse>>(
      '/agentese/concept/gardener/sessions',
      { limit }
    );
    return unwrapAgentese(response);
  },

  // =========================================================================
  // Garden State API (self.garden.* AGENTESE paths)
  // =========================================================================

  /** Get garden state via AGENTESE: self.garden.manifest */
  getGarden: async (): Promise<GardenStateResponse> => {
    const response = await apiClient.get<AgenteseResponse<GardenStateResponse>>(
      '/agentese/self/garden/manifest'
    );
    return unwrapAgentese(response);
  },

  /** Apply a tending gesture via AGENTESE: self.garden.nurture */
  tend: async (
    verb: TendingVerb,
    target: string,
    options?: { tone?: number; reasoning?: string }
  ): Promise<TendResponse> => {
    const response = await apiClient.post<AgenteseResponse<TendResponse>>(
      '/agentese/self/garden/nurture',
      {
        verb,
        target,
        tone: options?.tone ?? 0.5,
        reasoning: options?.reasoning ?? '',
      }
    );
    return unwrapAgentese(response);
  },

  /** Transition garden season via AGENTESE: self.garden.season */
  transitionSeason: async (
    newSeason: GardenSeason,
    reason?: string
  ): Promise<GardenStateResponse> => {
    const response = await apiClient.post<AgenteseResponse<GardenStateResponse>>(
      '/agentese/self/garden/season',
      { new_season: newSeason, reason: reason ?? '' }
    );
    return unwrapAgentese(response);
  },

  /** Focus on a specific plot via AGENTESE: self.garden.focus */
  focusPlot: async (plotName: string): Promise<GardenStateResponse> => {
    const response = await apiClient.post<AgenteseResponse<GardenStateResponse>>(
      '/agentese/self/garden/focus',
      { plot_name: plotName }
    );
    return unwrapAgentese(response);
  },

  // =========================================================================
  // Auto-Inducer API (Phase 8: Season Transition Suggestions)
  // =========================================================================

  /** Accept a suggested season transition via AGENTESE: self.garden.transition.accept */
  acceptTransition: async (
    fromSeason: GardenSeason,
    toSeason: GardenSeason
  ): Promise<TransitionActionResponse> => {
    const response = await apiClient.post<AgenteseResponse<TransitionActionResponse>>(
      '/agentese/self/garden/transition/accept',
      { from_season: fromSeason, to_season: toSeason }
    );
    return unwrapAgentese(response);
  },

  /** Dismiss a suggested season transition via AGENTESE: self.garden.transition.dismiss */
  dismissTransition: async (
    fromSeason: GardenSeason,
    toSeason: GardenSeason
  ): Promise<TransitionActionResponse> => {
    const response = await apiClient.post<AgenteseResponse<TransitionActionResponse>>(
      '/agentese/self/garden/transition/dismiss',
      { from_season: fromSeason, to_season: toSeason }
    );
    return unwrapAgentese(response);
  },

  // =========================================================================
  // Void Garden API (void.garden.* AGENTESE paths)
  // =========================================================================

  /** Serendipity from the void via AGENTESE: void.garden.sip */
  surprise: async (): Promise<unknown> => {
    const response = await apiClient.post<AgenteseResponse<unknown>>(
      '/agentese/void/garden/sip',
      {}
    );
    return unwrapAgentese(response);
  },
};

// Garden API types
import type {
  GardenSeason,
  TendingVerb,
} from '@/reactive/types';

export interface GardenStateResponse {
  garden_id: string;
  name: string;
  created_at: string;
  season: GardenSeason;
  season_since: string;
  plots: Record<string, PlotResponse>;
  active_plot: string | null;
  session_id: string | null;
  memory_crystals: string[];
  prompt_count: number;
  prompt_types: Record<string, number>;
  recent_gestures: GestureResponse[];
  last_tended: string;
  metrics: {
    health_score: number;
    total_prompts: number;
    active_plots: number;
    entropy_spent: number;
    entropy_budget: number;
  };
  computed: {
    health_score: number;
    entropy_remaining: number;
    entropy_percentage: number;
    active_plot_count: number;
    total_plot_count: number;
    season_plasticity: number;
    season_entropy_multiplier: number;
  };
}

export interface PlotResponse {
  name: string;
  path: string;
  description: string;
  plan_path: string | null;
  crown_jewel: string | null;
  prompts: string[];
  season_override: GardenSeason | null;
  rigidity: number;
  progress: number;
  created_at: string;
  last_tended: string;
  tags: string[];
  metadata: Record<string, unknown>;
}

export interface GestureResponse {
  verb: TendingVerb;
  target: string;
  tone: number;
  reasoning: string;
  entropy_cost: number;
  timestamp: string;
  observer: string;
  session_id: string | null;
  result_summary: string;
}

// Phase 8: Transition suggestion types
export interface TransitionSignals {
  gesture_frequency: number;
  gesture_diversity: number;
  plot_progress_delta: number;
  artifacts_created: number;
  time_in_season_hours: number;
  entropy_spent_ratio: number;
  reflect_count: number;
  session_active: boolean;
}

export interface TransitionSuggestion {
  from_season: GardenSeason;
  to_season: GardenSeason;
  confidence: number;
  reason: string;
  signals: TransitionSignals;
  triggered_at: string;
}

export interface TendResponse {
  accepted: boolean;
  state_changed: boolean;
  changes: string[];
  synergies_triggered: string[];
  reasoning_trace: string[];
  error: string | null;
  gesture: GestureResponse;
  // Phase 8: Auto-Inducer
  suggested_transition: TransitionSuggestion | null;
}

export interface TransitionActionResponse {
  status: string;
  garden_state: GardenStateResponse | null;
  message: string;
}

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
