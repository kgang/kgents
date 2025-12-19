/**
 * Generated types for AGENTESE path: world.forge.commission
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Response for commission list.
 */
export interface WorldForgeCommissionManifestResponse {
  count: number;
  commissions: {
    id: string;
    intent: string;
    name: string | null;
    status: string;
    created_at: string;
    updated_at: string;
    soul_approved: boolean;
    soul_annotation: string | null;
    artisan_outputs: Record<
      string,
      {
        artisan: string;
        status: string;
        output: Record<string, unknown> | null;
        annotation: string | null;
        started_at: string | null;
        completed_at: string | null;
        error?: string | null;
      }
    >;
    artifact_path: string | null;
    artifact_summary: string | null;
    paused: boolean;
  }[];
}

/**
 * Request to create a commission.
 */
export interface WorldForgeCommissionCreateRequest {
  intent: string;
  name?: string | null;
}

/**
 * Response after creating a commission.
 */
export interface WorldForgeCommissionCreateResponse {
  /** Summary of a commission. */
  commission: {
    id: string;
    intent: string;
    name: string | null;
    status: string;
    created_at: string;
    updated_at: string;
    soul_approved: boolean;
    soul_annotation: string | null;
    artisan_outputs: Record<
      string,
      {
        artisan: string;
        status: string;
        output: Record<string, unknown> | null;
        annotation: string | null;
        started_at: string | null;
        completed_at: string | null;
        error?: string | null;
      }
    >;
    artifact_path: string | null;
    artifact_summary: string | null;
    paused: boolean;
  };
}

/**
 * Request for commission details.
 */
export interface WorldForgeCommissionGetRequest {
  commission_id: string;
}

/**
 * Response for commission details.
 */
export interface WorldForgeCommissionGetResponse {
  /** Summary of a commission. */
  commission: {
    id: string;
    intent: string;
    name: string | null;
    status: string;
    created_at: string;
    updated_at: string;
    soul_approved: boolean;
    soul_annotation: string | null;
    artisan_outputs: Record<
      string,
      {
        artisan: string;
        status: string;
        output: Record<string, unknown> | null;
        annotation: string | null;
        started_at: string | null;
        completed_at: string | null;
        error?: string | null;
      }
    >;
    artifact_path: string | null;
    artifact_summary: string | null;
    paused: boolean;
  };
}

/**
 * Request to start commission review.
 */
export interface WorldForgeCommissionStartRequest {
  commission_id: string;
}

/**
 * Response after starting commission.
 */
export interface WorldForgeCommissionStartResponse {
  /** Summary of a commission. */
  commission: {
    id: string;
    intent: string;
    name: string | null;
    status: string;
    created_at: string;
    updated_at: string;
    soul_approved: boolean;
    soul_annotation: string | null;
    artisan_outputs: Record<
      string,
      {
        artisan: string;
        status: string;
        output: Record<string, unknown> | null;
        annotation: string | null;
        started_at: string | null;
        completed_at: string | null;
        error?: string | null;
      }
    >;
    artifact_path: string | null;
    artifact_summary: string | null;
    paused: boolean;
  };
}

/**
 * Request to advance commission to next stage.
 */
export interface WorldForgeCommissionAdvanceRequest {
  commission_id: string;
}

/**
 * Response after advancing commission.
 */
export interface WorldForgeCommissionAdvanceResponse {
  /** Summary of a commission. */
  commission: {
    id: string;
    intent: string;
    name: string | null;
    status: string;
    created_at: string;
    updated_at: string;
    soul_approved: boolean;
    soul_annotation: string | null;
    artisan_outputs: Record<
      string,
      {
        artisan: string;
        status: string;
        output: Record<string, unknown> | null;
        annotation: string | null;
        started_at: string | null;
        completed_at: string | null;
        error?: string | null;
      }
    >;
    artifact_path: string | null;
    artifact_summary: string | null;
    paused: boolean;
  };
}

/**
 * Request to pause a commission.
 */
export interface WorldForgeCommissionPauseRequest {
  commission_id: string;
}

/**
 * Response after pausing commission.
 */
export interface WorldForgeCommissionPauseResponse {
  /** Summary of a commission. */
  commission: {
    id: string;
    intent: string;
    name: string | null;
    status: string;
    created_at: string;
    updated_at: string;
    soul_approved: boolean;
    soul_annotation: string | null;
    artisan_outputs: Record<
      string,
      {
        artisan: string;
        status: string;
        output: Record<string, unknown> | null;
        annotation: string | null;
        started_at: string | null;
        completed_at: string | null;
        error?: string | null;
      }
    >;
    artifact_path: string | null;
    artifact_summary: string | null;
    paused: boolean;
  };
}

/**
 * Request to resume a commission.
 */
export interface WorldForgeCommissionResumeRequest {
  commission_id: string;
}

/**
 * Response after resuming commission.
 */
export interface WorldForgeCommissionResumeResponse {
  /** Summary of a commission. */
  commission: {
    id: string;
    intent: string;
    name: string | null;
    status: string;
    created_at: string;
    updated_at: string;
    soul_approved: boolean;
    soul_annotation: string | null;
    artisan_outputs: Record<
      string,
      {
        artisan: string;
        status: string;
        output: Record<string, unknown> | null;
        annotation: string | null;
        started_at: string | null;
        completed_at: string | null;
        error?: string | null;
      }
    >;
    artifact_path: string | null;
    artifact_summary: string | null;
    paused: boolean;
  };
}

/**
 * Request to cancel a commission.
 */
export interface WorldForgeCommissionCancelRequest {
  commission_id: string;
  reason?: string | null;
}

/**
 * Response after canceling commission.
 */
export interface WorldForgeCommissionCancelResponse {
  success: boolean;
  commission_id: string;
}
