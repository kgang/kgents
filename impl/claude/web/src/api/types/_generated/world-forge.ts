/**
 * Generated types for AGENTESE path: world.forge
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Forge health status manifest response.
 */
export interface WorldForgeManifestResponse {
  total_workshops: number;
  active_workshops: number;
  total_artisans: number;
  total_contributions: number;
  total_exhibitions: number;
  open_exhibitions: number;
  storage_backend: string;
}

/**
 * Response for workshop list aspect.
 */
export interface WorldForgeWorkshopListResponse {
  count: number;
  workshops: {
    id: string;
    name: string;
    description: string | null;
    theme: string | null;
    is_active: boolean;
    artisan_count: number;
    contribution_count: number;
    started_at: string | null;
    created_at: string;
  }[];
}

/**
 * Response for contribution list.
 */
export interface WorldForgeContributionListResponse {
  count: number;
  contributions: {
    id: string;
    artisan_id: string;
    artisan_name: string;
    contribution_type: string;
    content_type: string;
    content: string;
    prompt: string | null;
    inspiration: string | null;
    created_at: string;
  }[];
}

/**
 * Response for festival list.
 */
export interface WorldForgeFestivalListResponse {
  count: number;
  festivals: {
    id: string;
    title: string;
    theme: string;
    description: string | null;
    status: string;
    season: string;
    entry_count: number;
    started_at: string | null;
    ends_at: string | null;
  }[];
}

/**
 * Request for workshop details.
 */
export interface WorldForgeWorkshopGetRequest {
  workshop_id: string;
}

/**
 * Response for workshop details.
 */
export interface WorldForgeWorkshopGetResponse {
  /** Summary of a workshop. */
  workshop: {
    id: string;
    name: string;
    description: string | null;
    theme: string | null;
    is_active: boolean;
    artisan_count: number;
    contribution_count: number;
    started_at: string | null;
    created_at: string;
  };
}

/**
 * Request to create a workshop.
 */
export interface WorldForgeWorkshopCreateRequest {
  name: string;
  description?: string | null;
  theme?: string | null;
  config?: Record<string, unknown> | null;
}

/**
 * Response after creating a workshop.
 */
export interface WorldForgeWorkshopCreateResponse {
  /** Summary of a workshop. */
  workshop: {
    id: string;
    name: string;
    description: string | null;
    theme: string | null;
    is_active: boolean;
    artisan_count: number;
    contribution_count: number;
    started_at: string | null;
    created_at: string;
  };
}

/**
 * Request to end a workshop.
 */
export interface WorldForgeWorkshopEndRequest {
  workshop_id: string;
}

/**
 * Response after ending a workshop.
 */
export interface WorldForgeWorkshopEndResponse {
  success: boolean;
  workshop_id: string;
}

/**
 * Request for artisan list.
 */
export interface WorldForgeArtisanListRequest {
  workshop_id: string;
  specialty?: string | null;
  active_only?: boolean;
}

/**
 * Response for artisan list.
 */
export interface WorldForgeArtisanListResponse {
  count: number;
  artisans: {
    id: string;
    workshop_id: string;
    name: string;
    specialty: string;
    style: string | null;
    is_active: boolean;
    contribution_count: number;
    created_at: string;
  }[];
}

/**
 * Request to join a workshop.
 */
export interface WorldForgeArtisanJoinRequest {
  workshop_id: string;
  name: string;
  specialty: string;
  style?: string | null;
  agent_id?: string | null;
}

/**
 * Response after joining a workshop.
 */
export interface WorldForgeArtisanJoinResponse {
  /** Summary of an artisan. */
  artisan: {
    id: string;
    workshop_id: string;
    name: string;
    specialty: string;
    style: string | null;
    is_active: boolean;
    contribution_count: number;
    created_at: string;
  };
}

/**
 * Request to submit a contribution.
 */
export interface WorldForgeContributeRequest {
  artisan_id: string;
  content: string;
  content_type?: string;
  contribution_type?: string;
  prompt?: string | null;
  inspiration?: string | null;
  notes?: string | null;
}

/**
 * Response after contributing.
 */
export interface WorldForgeContributeResponse {
  /** Summary of a contribution. */
  contribution: {
    id: string;
    artisan_id: string;
    artisan_name: string;
    contribution_type: string;
    content_type: string;
    content: string;
    prompt: string | null;
    inspiration: string | null;
    created_at: string;
  };
}

/**
 * Request to create an exhibition.
 */
export interface WorldForgeExhibitionCreateRequest {
  workshop_id: string;
  name: string;
  description?: string | null;
  curator_notes?: string | null;
}

/**
 * Response after creating an exhibition.
 */
export interface WorldForgeExhibitionCreateResponse {
  /** Summary of an exhibition. */
  exhibition: {
    id: string;
    workshop_id: string;
    name: string;
    description: string | null;
    curator_notes: string | null;
    is_open: boolean;
    view_count: number;
    item_count: number;
    opened_at: string | null;
    created_at: string;
  };
}

/**
 * Request to open an exhibition.
 */
export interface WorldForgeExhibitionOpenRequest {
  exhibition_id: string;
}

/**
 * Response after opening an exhibition.
 */
export interface WorldForgeExhibitionOpenResponse {
  success: boolean;
  exhibition_id: string;
}

/**
 * Request to view an exhibition.
 */
export interface WorldForgeExhibitionViewRequest {
  exhibition_id: string;
}

/**
 * Response after viewing an exhibition.
 */
export interface WorldForgeExhibitionViewResponse {
  /** Summary of an exhibition. */
  exhibition: {
    id: string;
    workshop_id: string;
    name: string;
    description: string | null;
    curator_notes: string | null;
    is_open: boolean;
    view_count: number;
    item_count: number;
    opened_at: string | null;
    created_at: string;
  };
}

/**
 * Request for gallery list.
 */
export interface WorldForgeGalleryListRequest {
  exhibition_id: string;
}

/**
 * Response for gallery list.
 */
export interface WorldForgeGalleryListResponse {
  count: number;
  items: {
    id: string;
    exhibition_id: string;
    artifact_type: string;
    artifact_content: string;
    title: string | null;
    description: string | null;
    display_order: number;
    artisan_ids: string[];
  }[];
}

/**
 * Request to add item to gallery.
 */
export interface WorldForgeGalleryAddRequest {
  exhibition_id: string;
  artifact_content: string;
  artifact_type?: string;
  title?: string | null;
  description?: string | null;
  artisan_ids?: string[] | null;
}

/**
 * Response after adding to gallery.
 */
export interface WorldForgeGalleryAddResponse {
  /** Summary of a gallery item. */
  item: {
    id: string;
    exhibition_id: string;
    artifact_type: string;
    artifact_content: string;
    title: string | null;
    description: string | null;
    display_order: number;
    artisan_ids: string[];
  };
}

/**
 * Token balance manifest.
 */
export interface WorldForgeTokensManifestResponse {
  user_id: string;
  balance: number;
  earning_rate: number | null;
  spending_history?: Record<string, unknown>[] | null;
}

/**
 * Request to submit a bid.
 */
export interface WorldForgeBidSubmitRequest {
  session_id: string;
  bid_type: string;
  content: string;
}

/**
 * Response after submitting a bid.
 */
export interface WorldForgeBidSubmitResponse {
  success: boolean;
  bid_id: string | null;
  new_balance: string;
  error?: string | null;
  reason?: string | null;
}

/**
 * Request to create a festival.
 */
export interface WorldForgeFestivalCreateRequest {
  title: string;
  theme: string;
  description?: string | null;
  duration_hours?: number;
  voting_hours?: number;
}

/**
 * Response after creating a festival.
 */
export interface WorldForgeFestivalCreateResponse {
  /** Summary of a festival. */
  festival: {
    id: string;
    title: string;
    theme: string;
    description: string | null;
    status: string;
    season: string;
    entry_count: number;
    started_at: string | null;
    ends_at: string | null;
  };
}

/**
 * Request to enter a festival.
 */
export interface WorldForgeFestivalEnterRequest {
  festival_id: string;
  artisan: string;
  prompt: string;
  content: string;
  piece_id?: string | null;
}

/**
 * Response after entering a festival.
 */
export interface WorldForgeFestivalEnterResponse {
  /** Summary of a festival entry. */
  entry: {
    id: string;
    festival_id: string;
    artisan: string;
    prompt: string;
    content: string;
    piece_id: string | null;
    submitted_at: string;
  };
}

// =============================================================================
// Legacy Type Aliases (for backwards compatibility during migration)
// =============================================================================

/** @deprecated Use WorldForgeManifestResponse instead */
export type WorldAtelierManifestResponse = WorldForgeManifestResponse;
/** @deprecated Use WorldForgeWorkshopListResponse instead */
export type WorldAtelierWorkshopListResponse = WorldForgeWorkshopListResponse;
/** @deprecated Use WorldForgeContributionListResponse instead */
export type WorldAtelierContributionListResponse = WorldForgeContributionListResponse;
/** @deprecated Use WorldForgeFestivalListResponse instead */
export type WorldAtelierFestivalListResponse = WorldForgeFestivalListResponse;
/** @deprecated Use WorldForgeWorkshopGetRequest instead */
export type WorldAtelierWorkshopGetRequest = WorldForgeWorkshopGetRequest;
/** @deprecated Use WorldForgeWorkshopGetResponse instead */
export type WorldAtelierWorkshopGetResponse = WorldForgeWorkshopGetResponse;
/** @deprecated Use WorldForgeWorkshopCreateRequest instead */
export type WorldAtelierWorkshopCreateRequest = WorldForgeWorkshopCreateRequest;
/** @deprecated Use WorldForgeWorkshopCreateResponse instead */
export type WorldAtelierWorkshopCreateResponse = WorldForgeWorkshopCreateResponse;
/** @deprecated Use WorldForgeWorkshopEndRequest instead */
export type WorldAtelierWorkshopEndRequest = WorldForgeWorkshopEndRequest;
/** @deprecated Use WorldForgeWorkshopEndResponse instead */
export type WorldAtelierWorkshopEndResponse = WorldForgeWorkshopEndResponse;
/** @deprecated Use WorldForgeArtisanListRequest instead */
export type WorldAtelierArtisanListRequest = WorldForgeArtisanListRequest;
/** @deprecated Use WorldForgeArtisanListResponse instead */
export type WorldAtelierArtisanListResponse = WorldForgeArtisanListResponse;
/** @deprecated Use WorldForgeArtisanJoinRequest instead */
export type WorldAtelierArtisanJoinRequest = WorldForgeArtisanJoinRequest;
/** @deprecated Use WorldForgeArtisanJoinResponse instead */
export type WorldAtelierArtisanJoinResponse = WorldForgeArtisanJoinResponse;
/** @deprecated Use WorldForgeContributeRequest instead */
export type WorldAtelierContributeRequest = WorldForgeContributeRequest;
/** @deprecated Use WorldForgeContributeResponse instead */
export type WorldAtelierContributeResponse = WorldForgeContributeResponse;
/** @deprecated Use WorldForgeExhibitionCreateRequest instead */
export type WorldAtelierExhibitionCreateRequest = WorldForgeExhibitionCreateRequest;
/** @deprecated Use WorldForgeExhibitionCreateResponse instead */
export type WorldAtelierExhibitionCreateResponse = WorldForgeExhibitionCreateResponse;
/** @deprecated Use WorldForgeExhibitionOpenRequest instead */
export type WorldAtelierExhibitionOpenRequest = WorldForgeExhibitionOpenRequest;
/** @deprecated Use WorldForgeExhibitionOpenResponse instead */
export type WorldAtelierExhibitionOpenResponse = WorldForgeExhibitionOpenResponse;
/** @deprecated Use WorldForgeExhibitionViewRequest instead */
export type WorldAtelierExhibitionViewRequest = WorldForgeExhibitionViewRequest;
/** @deprecated Use WorldForgeExhibitionViewResponse instead */
export type WorldAtelierExhibitionViewResponse = WorldForgeExhibitionViewResponse;
/** @deprecated Use WorldForgeGalleryListRequest instead */
export type WorldAtelierGalleryListRequest = WorldForgeGalleryListRequest;
/** @deprecated Use WorldForgeGalleryListResponse instead */
export type WorldAtelierGalleryListResponse = WorldForgeGalleryListResponse;
/** @deprecated Use WorldForgeGalleryAddRequest instead */
export type WorldAtelierGalleryAddRequest = WorldForgeGalleryAddRequest;
/** @deprecated Use WorldForgeGalleryAddResponse instead */
export type WorldAtelierGalleryAddResponse = WorldForgeGalleryAddResponse;
/** @deprecated Use WorldForgeTokensManifestResponse instead */
export type WorldAtelierTokensManifestResponse = WorldForgeTokensManifestResponse;
/** @deprecated Use WorldForgeBidSubmitRequest instead */
export type WorldAtelierBidSubmitRequest = WorldForgeBidSubmitRequest;
/** @deprecated Use WorldForgeBidSubmitResponse instead */
export type WorldAtelierBidSubmitResponse = WorldForgeBidSubmitResponse;
/** @deprecated Use WorldForgeFestivalCreateRequest instead */
export type WorldAtelierFestivalCreateRequest = WorldForgeFestivalCreateRequest;
/** @deprecated Use WorldForgeFestivalCreateResponse instead */
export type WorldAtelierFestivalCreateResponse = WorldForgeFestivalCreateResponse;
/** @deprecated Use WorldForgeFestivalEnterRequest instead */
export type WorldAtelierFestivalEnterRequest = WorldForgeFestivalEnterRequest;
/** @deprecated Use WorldForgeFestivalEnterResponse instead */
export type WorldAtelierFestivalEnterResponse = WorldForgeFestivalEnterResponse;
