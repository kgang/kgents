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
      // Unauthorized - clear auth and redirect
      localStorage.removeItem('api_key');
      window.location.href = '/';
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
// Town API
// =============================================================================

export const townApi = {
  create: (data: CreateTownRequest = {}) => apiClient.post<Town>('/v1/town', data),

  get: (townId: string) => apiClient.get<Town>(`/v1/town/${townId}`),

  delete: (townId: string) => apiClient.delete(`/v1/town/${townId}`),

  getCitizens: (townId: string) => apiClient.get<CitizensResponse>(`/v1/town/${townId}/citizens`),

  getCitizen: (townId: string, name: string, lod: number = 0, userId: string = 'anonymous') =>
    apiClient.get<CitizenDetailResponse>(
      `/v1/town/${townId}/citizen/${name}?lod=${lod}&user_id=${userId}`
    ),

  getCoalitions: (townId: string) =>
    apiClient.get<CoalitionsResponse>(`/v1/town/${townId}/coalitions`),

  step: (townId: string, cycles: number = 1) =>
    apiClient.post(`/v1/town/${townId}/step`, { cycles }),

  getMetrics: (townId: string, since_hours?: number) =>
    apiClient.get(`/v1/town/${townId}/metrics`, {
      params: since_hours ? { since_hours } : undefined,
    }),
};

// =============================================================================
// INHABIT API
// =============================================================================

export const inhabitApi = {
  start: (townId: string, citizenId: string, forceEnabled: boolean = false) =>
    apiClient.post(`/v1/town/${townId}/inhabit/${citizenId}`, { force_enabled: forceEnabled }),

  getStatus: (townId: string, citizenId: string) =>
    apiClient.get(`/v1/town/${townId}/inhabit/${citizenId}/status`),

  suggest: (townId: string, citizenId: string, action: string) =>
    apiClient.post(`/v1/town/${townId}/inhabit/${citizenId}/suggest`, { action }),

  force: (townId: string, citizenId: string, action: string, severity: number = 0.2) =>
    apiClient.post(`/v1/town/${townId}/inhabit/${citizenId}/force`, { action, severity }),

  apologize: (townId: string, citizenId: string, sincerity: number = 0.3) =>
    apiClient.post(`/v1/town/${townId}/inhabit/${citizenId}/apologize`, { sincerity }),

  end: (townId: string, citizenId: string) =>
    apiClient.delete(`/v1/town/${townId}/inhabit/${citizenId}`),
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
// Brain API (Holographic Brain)
// =============================================================================

export const brainApi = {
  /** Capture content to holographic memory */
  capture: (data: BrainCaptureRequest) =>
    apiClient.post<BrainCaptureResponse>('/v1/brain/capture', data),

  /** Surface ghost memories based on context */
  ghost: (data: BrainGhostRequest) => apiClient.post<BrainGhostResponse>('/v1/brain/ghost', data),

  /** Get brain topology/cartography */
  getMap: () => apiClient.get<BrainMapResponse>('/v1/brain/map'),

  /** Get brain status */
  getStatus: () => apiClient.get<BrainStatusResponse>('/v1/brain/status'),

  /** Get 3D topology data for visualization */
  getTopology: (similarityThreshold = 0.3) =>
    apiClient.get<BrainTopologyResponse>('/v1/brain/topology', {
      params: { similarity_threshold: similarityThreshold },
    }),
};

// =============================================================================
// Gestalt API (Living Architecture Visualizer)
// =============================================================================

export const gestaltApi = {
  /** Get full architecture manifest */
  getManifest: () => apiClient.get<CodebaseManifestResponse>('/v1/world/codebase/manifest'),

  /** Get health metrics summary */
  getHealth: () => apiClient.get<CodebaseHealthResponse>('/v1/world/codebase/health'),

  /** Get drift violations */
  getDrift: () => apiClient.get<CodebaseDriftResponse>('/v1/world/codebase/drift'),

  /** Get module details */
  getModule: (moduleName: string) =>
    apiClient.get<CodebaseModuleResponse>(`/v1/world/codebase/module/${encodeURIComponent(moduleName)}`),

  /** Get topology for visualization (Sprint 2: observer-dependent views) */
  getTopology: (maxNodes = 200, minHealth = 0.0, role?: string) =>
    apiClient.get<CodebaseTopologyResponse>('/v1/world/codebase/topology', {
      params: {
        max_nodes: maxNodes,
        min_health: minHealth,
        ...(role && { role }), // Sprint 2: Observer role
      },
    }),

  /** Force rescan of codebase */
  scan: (language = 'python', path?: string) =>
    apiClient.post<CodebaseScanResponse>('/v1/world/codebase/scan', { language, path }),

  /** Create EventSource for topology stream (Sprint 1: Live Architecture) */
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
    return new EventSource(`${baseUrl}/v1/world/codebase/stream${queryString ? `?${queryString}` : ''}`);
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
// Gardener API (Wave 1: Hero Path)
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
  /** Get active session */
  getSession: () =>
    apiClient.get<GardenerSessionState>('/v1/gardener/session'),

  /** Create new session */
  createSession: (data: GardenerCreateRequest = {}) =>
    apiClient.post<GardenerSessionState>('/v1/gardener/session', data),

  /** Advance to next phase */
  advanceSession: () =>
    apiClient.post<GardenerSessionState>('/v1/gardener/session/advance'),

  /** Get polynomial visualization for active session */
  getPolynomial: () =>
    apiClient.get<GardenerPolynomialResponse>('/v1/gardener/session/polynomial'),

  /** List recent sessions */
  listSessions: (limit = 10) =>
    apiClient.get<GardenerSessionListResponse>('/v1/gardener/sessions', {
      params: { limit },
    }),

  // =========================================================================
  // Garden State API (Phase 7: Web Visualization)
  // =========================================================================

  /** Get garden state */
  getGarden: () =>
    apiClient.get<GardenStateResponse>('/v1/gardener/garden'),

  /** Apply a tending gesture */
  tend: (verb: TendingVerb, target: string, options?: { tone?: number; reasoning?: string }) =>
    apiClient.post<TendResponse>('/v1/gardener/garden/tend', {
      verb,
      target,
      tone: options?.tone ?? 0.5,
      reasoning: options?.reasoning ?? '',
    }),

  /** Transition garden season */
  transitionSeason: (newSeason: GardenSeason, reason?: string) =>
    apiClient.post<GardenStateResponse>('/v1/gardener/garden/season', {
      new_season: newSeason,
      reason: reason ?? '',
    }),

  /** Focus on a specific plot */
  focusPlot: (plotName: string) =>
    apiClient.post<GardenStateResponse>(`/v1/gardener/garden/plot/${plotName}/focus`),

  // =========================================================================
  // Auto-Inducer API (Phase 8: Season Transition Suggestions)
  // =========================================================================

  /** Accept a suggested season transition */
  acceptTransition: (fromSeason: GardenSeason, toSeason: GardenSeason) =>
    apiClient.post<TransitionActionResponse>('/v1/gardener/garden/transition/accept', {
      from_season: fromSeason,
      to_season: toSeason,
    }),

  /** Dismiss a suggested season transition */
  dismissTransition: (fromSeason: GardenSeason, toSeason: GardenSeason) =>
    apiClient.post<TransitionActionResponse>('/v1/gardener/garden/transition/dismiss', {
      from_season: fromSeason,
      to_season: toSeason,
    }),
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

export const parkApi = {
  /** Get current scenario state */
  getScenario: () =>
    apiClient.get<ParkScenarioState>('/api/park/scenario'),

  /** Start a new crisis practice scenario */
  startScenario: (data: ParkStartScenarioRequest = {}) =>
    apiClient.post<ParkScenarioState>('/api/park/scenario/start', data),

  /** Tick scenario timers */
  tick: (data: ParkTickRequest = { count: 1 }) =>
    apiClient.post<ParkScenarioState>('/api/park/scenario/tick', data),

  /** Transition crisis phase */
  transitionPhase: (data: ParkTransitionPhaseRequest) =>
    apiClient.post<ParkScenarioState>('/api/park/scenario/phase', data),

  /** Don or doff a dialogue mask */
  maskAction: (data: ParkMaskActionRequest) =>
    apiClient.post<ParkScenarioState>('/api/park/scenario/mask', data),

  /** Use force mechanic */
  useForce: () =>
    apiClient.post<ParkScenarioState>('/api/park/scenario/force'),

  /** Complete scenario */
  completeScenario: (data: ParkCompleteRequest = { outcome: 'success' }) =>
    apiClient.post<ParkScenarioSummary>('/api/park/scenario/complete', data),

  /** List all available masks */
  getMasks: () =>
    apiClient.get<ParkMaskInfo[]>('/api/park/masks'),

  /** Get mask details */
  getMask: (name: string) =>
    apiClient.get<ParkMaskInfo>(`/api/park/masks/${name}`),

  /** Get Park system status */
  getStatus: () =>
    apiClient.get<ParkStatusResponse>('/api/park/status'),
};
