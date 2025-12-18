/**
 * Generated types for AGENTESE path: world.codebase
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

/**
 * Gestalt architecture manifest response.
 */
export interface WorldCodebaseManifestResponse {
  module_count: number;
  edge_count: number;
  overall_grade: string;
  average_health: number;
  drift_count: number;
}

/**
 * Response for health manifest aspect.
 */
export interface WorldCodebaseHealthResponse {
  overall_grade: string;
  average_health: number;
  module_count: number;
  modules: {
    name: string;
    health_grade: string;
    health_score: number;
    lines_of_code: number;
    coupling: number;
    cohesion: number;
    instability: number | null;
  }[];
}

/**
 * Response for drift violations.
 */
export interface WorldCodebaseDriftResponse {
  violation_count: number;
  violations: {
    source_module: string;
    target_module: string;
    severity: string;
    violation_type: string;
    message: string;
  }[];
}

/**
 * Request for topology visualization data.
 */
export interface WorldCodebaseTopologyRequest {
  max_nodes?: number;
  min_health?: number;
  role?: string | null;
}

/**
 * Response for topology visualization.
 */
export interface WorldCodebaseTopologyResponse {
  nodes: {
    id: string;
    label: string;
    layer: string | null;
    health_grade: string;
    health_score: number;
    lines_of_code: number;
    coupling: number;
    cohesion: number;
    instability: number | null;
    x: number;
    y: number;
    z: number;
  }[];
  links: {
    source: string;
    target: string;
    import_type: string;
    is_violation: boolean;
    violation_severity: string | null;
  }[];
  layers: string[];
  /** Statistics for the topology. */
  stats: {
    node_count: number;
    link_count: number;
    layer_count: number;
    violation_count: number;
    avg_health: number;
    overall_grade: string;
  };
}

/**
 * Request for module details.
 */
export interface WorldCodebaseModuleRequest {
  module_name: string;
}

/**
 * Response for module details.
 */
export interface WorldCodebaseModuleResponse {
  name: string;
  path: string;
  layer: string | null;
  lines_of_code: number;
  health_grade: string;
  health_score: number;
  coupling: number;
  cohesion: number;
  instability: number | null;
  dependencies: {
    target: string;
    import_type: string;
  }[];
  dependents: {
    source: string;
    import_type: string;
  }[];
}

/**
 * Request to rescan codebase.
 */
export interface WorldCodebaseScanRequest {
  language?: string;
}

/**
 * Response after rescanning.
 */
export interface WorldCodebaseScanResponse {
  module_count: number;
  edge_count: number;
  overall_grade: string;
  scanned_at: string;
}
