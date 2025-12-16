/**
 * Atelier API Client
 *
 * API client for Tiny Atelier endpoints.
 * Handles commission streaming, gallery management, and collaboration.
 *
 * Theme: Orisinal.com aesthetic - whimsical, minimal, melancholic but hopeful.
 */

import { apiClient } from './client';

// =============================================================================
// Types
// =============================================================================

export interface Artisan {
  name: string;
  specialty: string;
  personality: string;
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

export interface AtelierStatus {
  status: string;
  total_commissions: number;
  total_pieces: number;
  pending_queue: number;
  available_artisans: string[];
  event_bus_subscribers: number;
}

// SSE Event types
export type AtelierEventType =
  | 'commission_received'
  | 'contemplating'
  | 'working'
  | 'fragment'
  | 'piece_complete'
  | 'error';

export interface AtelierEvent {
  event_type: AtelierEventType;
  artisan: string;
  commission_id: string | null;
  message: string;
  data: Record<string, unknown>;
  timestamp: string;
}

// =============================================================================
// API Functions
// =============================================================================

export const atelierApi = {
  /**
   * List available artisans
   */
  getArtisans: () => apiClient.get<ArtisansResponse>('/api/atelier/artisans'),

  /**
   * Get workshop status
   */
  getStatus: () => apiClient.get<AtelierStatus>('/api/atelier/status'),

  /**
   * List gallery pieces
   */
  getGallery: (params?: {
    artisan?: string;
    form?: string;
    limit?: number;
    offset?: number;
  }) => apiClient.get<GalleryResponse>('/api/atelier/gallery', { params }),

  /**
   * Get a piece with full provenance
   */
  getPiece: (pieceId: string) => apiClient.get<Piece>(`/api/atelier/gallery/${pieceId}`),

  /**
   * Get piece lineage
   */
  getLineage: (pieceId: string) =>
    apiClient.get<LineageResponse>(`/api/atelier/gallery/${pieceId}/lineage`),

  /**
   * Search gallery
   */
  searchGallery: (query: string, limit?: number) =>
    apiClient.get<GalleryResponse>('/api/atelier/gallery/search', {
      params: { query, limit },
    }),

  /**
   * Delete a piece
   */
  deletePiece: (pieceId: string) =>
    apiClient.delete(`/api/atelier/gallery/${pieceId}`),

  /**
   * Queue a commission for background processing
   */
  queueCommission: (artisan: string, request: string, patron?: string) =>
    apiClient.post<CommissionQueuedResponse>('/api/atelier/queue', {
      artisan,
      request,
      patron,
    }),

  /**
   * Get pending queue
   */
  getPending: () => apiClient.get<PendingResponse>('/api/atelier/queue/pending'),
};

// =============================================================================
// SSE Stream URLs
// =============================================================================

/**
 * Get SSE URL for commissioning an artisan
 */
export function getCommissionStreamUrl(): string {
  // Note: SSE is POST but EventSource only supports GET
  // We'll use fetch with ReadableStream instead
  return '/api/atelier/commission';
}

/**
 * Get SSE URL for collaboration
 */
export function getCollaborateStreamUrl(): string {
  return '/api/atelier/collaborate';
}

/**
 * Get SSE URL for processing queue
 */
export function getProcessQueueStreamUrl(all?: boolean): string {
  return `/api/atelier/queue/process${all ? '?all=true' : ''}`;
}
