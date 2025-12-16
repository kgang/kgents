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
};
