/**
 * Forge API Client
 *
 * API client for Forge endpoints.
 * Handles commission streaming, gallery management, and collaboration.
 *
 * The Forge is where Kent builds - not a fishbowl for spectators.
 */

import { apiClient } from './client';

// =============================================================================
// Types
// =============================================================================

export interface EigenvectorDimensions {
  warmth: number;
  curiosity: number;
  trust: number;
  creativity: number;
  patience: number;
  resilience: number;
  ambition: number;
}

export interface Artisan {
  name: string;
  specialty: string;
  personality: string;
  eigenvector?: EigenvectorDimensions;
}

export interface ArtisansResponse {
  artisans: Artisan[];
  total: number;
}

export interface PieceSummary {
  id: string;
  artisan: string;
  form: string;
  preview: string;
  interpretation: string;
  created_at: string;
}

export interface GalleryResponse {
  pieces: PieceSummary[];
  total: number;
}

export interface Provenance {
  interpretation: string;
  considerations: string[];
  choices: Array<{
    decision: string;
    reason: string;
    alternatives: string[];
  }>;
  inspirations: string[];
}

export interface Piece {
  id: string;
  content: unknown;
  artisan: string;
  commission_id: string;
  form: string;
  provenance: Provenance;
  created_at: string;
}

export interface LineageNode {
  piece_id: string;
  artisan: string;
  preview: string;
  depth: number;
}

export interface LineageResponse {
  piece_id: string;
  ancestors: LineageNode[];
  descendants: LineageNode[];
}

export interface QueueItem {
  commission_id: string;
  artisan: string;
  request: string;
  patron: string;
  queued_at: string;
}

export interface PendingResponse {
  items: QueueItem[];
  total: number;
}

export interface CommissionQueuedResponse {
  commission_id: string;
  artisan: string;
  status: string;
}

export interface ForgeStatus {
  status: string;
  total_commissions: number;
  total_pieces: number;
  pending_queue: number;
  available_artisans: string[];
  event_bus_subscribers: number;
}

// SSE Event types
export type ForgeEventType =
  | 'commission_received'
  | 'contemplating'
  | 'working'
  | 'fragment'
  | 'piece_complete'
  | 'error';

export interface ForgeEvent {
  event_type: ForgeEventType;
  artisan: string;
  commission_id: string | null;
  message: string;
  data: Record<string, unknown>;
  timestamp: string;
}

// Legacy aliases for backward compatibility
export type AtelierStatus = ForgeStatus;
export type AtelierEventType = ForgeEventType;
export type AtelierEvent = ForgeEvent;

// =============================================================================
// API Functions
// =============================================================================

export const forgeApi = {
  /**
   * List available artisans
   */
  getArtisans: () => apiClient.get<ArtisansResponse>('/api/forge/artisans'),

  /**
   * Get workshop status
   */
  getStatus: () => apiClient.get<ForgeStatus>('/api/forge/status'),

  /**
   * List gallery pieces
   */
  getGallery: (params?: {
    artisan?: string;
    form?: string;
    limit?: number;
    offset?: number;
  }) => apiClient.get<GalleryResponse>('/api/forge/gallery', { params }),

  /**
   * Get a piece with full provenance
   */
  getPiece: (pieceId: string) => apiClient.get<Piece>(`/api/forge/gallery/${pieceId}`),

  /**
   * Get piece lineage
   */
  getLineage: (pieceId: string) =>
    apiClient.get<LineageResponse>(`/api/forge/gallery/${pieceId}/lineage`),

  /**
   * Search gallery
   */
  searchGallery: (query: string, limit?: number) =>
    apiClient.get<GalleryResponse>('/api/forge/gallery/search', {
      params: { query, limit },
    }),

  /**
   * Delete a piece
   */
  deletePiece: (pieceId: string) =>
    apiClient.delete(`/api/forge/gallery/${pieceId}`),

  /**
   * Queue a commission for background processing
   */
  queueCommission: (artisan: string, request: string, patron?: string) =>
    apiClient.post<CommissionQueuedResponse>('/api/forge/queue', {
      artisan,
      request,
      patron,
    }),

  /**
   * Get pending queue
   */
  getPending: () => apiClient.get<PendingResponse>('/api/forge/queue/pending'),
};

// Legacy alias for backward compatibility
export const atelierApi = forgeApi;

// =============================================================================
// SSE Stream URLs
// =============================================================================

/**
 * Get SSE URL for commissioning an artisan
 */
export function getCommissionStreamUrl(): string {
  // Note: SSE is POST but EventSource only supports GET
  // We'll use fetch with ReadableStream instead
  return '/api/forge/commission';
}

/**
 * Get SSE URL for collaboration
 */
export function getCollaborateStreamUrl(): string {
  return '/api/forge/collaborate';
}

/**
 * Get SSE URL for processing queue
 */
export function getProcessQueueStreamUrl(all?: boolean): string {
  return `/api/forge/queue/process${all ? '?all=true' : ''}`;
}
