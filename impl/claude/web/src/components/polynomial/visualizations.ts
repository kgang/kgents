/**
 * Visualization Factory Functions
 *
 * Foundation 3: Visible Polynomial State
 *
 * These functions create PolynomialVisualization objects for different
 * polynomial agents: Gardener, N-Phase, Citizen, etc.
 */

import type {
  PolynomialVisualization,
  PolynomialPosition,
  PolynomialEdge,
  GardenerSessionState,
} from '../../api/types';

// =============================================================================
// Gardener Session Visualization
// =============================================================================

/**
 * Phase configuration for Gardener.
 */
const GARDENER_PHASES = [
  { id: 'SENSE', label: 'Sense', emoji: '👁️', color: '#3b82f6', description: 'Gather context' },
  { id: 'ACT', label: 'Act', emoji: '⚡', color: '#f59e0b', description: 'Execute intent' },
  { id: 'REFLECT', label: 'Reflect', emoji: '💭', color: '#8b5cf6', description: 'Consolidate learnings' },
] as const;

/**
 * Valid transitions for Gardener polynomial.
 */
const GARDENER_EDGES: PolynomialEdge[] = [
  { source: 'SENSE', target: 'ACT', is_valid: true, label: 'advance' },
  { source: 'ACT', target: 'REFLECT', is_valid: true, label: 'advance' },
  { source: 'ACT', target: 'SENSE', is_valid: true, label: 'rollback' },
  { source: 'REFLECT', target: 'SENSE', is_valid: true, label: 'cycle' },
];

/**
 * Create a PolynomialVisualization for a GardenerSession.
 *
 * @param session - The session state from API or local state
 * @returns PolynomialVisualization ready for rendering
 *
 * @example
 * ```tsx
 * const viz = createGardenerVisualization({
 *   session_id: 'abc123',
 *   name: 'Feature Implementation',
 *   phase: 'ACT',
 *   artifacts_count: 3,
 *   learnings_count: 0,
 *   sense_count: 1,
 *   act_count: 1,
 *   reflect_count: 0,
 * });
 * ```
 */
export function createGardenerVisualization(
  session: GardenerSessionState,
): PolynomialVisualization {
  const currentPhase = session.phase;

  // Build positions with current marked
  const positions: PolynomialPosition[] = GARDENER_PHASES.map((p) => ({
    id: p.id,
    label: p.label,
    emoji: p.emoji,
    color: p.color,
    description: p.description,
    is_current: p.id === currentPhase,
    is_terminal: false,
  }));

  // Calculate valid directions from current position
  const validDirections = GARDENER_EDGES
    .filter((e) => e.source === currentPhase && e.is_valid)
    .map((e) => e.target);

  return {
    id: `gardener-${session.session_id}`,
    name: session.name || 'Gardener Session',
    positions,
    edges: GARDENER_EDGES,
    current: currentPhase,
    valid_directions: validDirections,
    history: [],
    metadata: {
      session_id: session.session_id,
      plan_path: session.plan_path,
      intent: session.intent,
      artifacts_count: session.artifacts_count,
      learnings_count: session.learnings_count,
      cycles: session.reflect_count,
    },
  };
}

// =============================================================================
// N-Phase Visualization
// =============================================================================

/**
 * N-Phase development cycle phases.
 */
const NPHASE_PHASES = [
  { id: 'PLAN', label: 'Plan', emoji: '📋', color: '#94a3b8' },
  { id: 'RESEARCH', label: 'Research', emoji: '🔍', color: '#3b82f6' },
  { id: 'DEVELOP', label: 'Develop', emoji: '🛠️', color: '#22c55e' },
  { id: 'STRATEGIZE', label: 'Strategize', emoji: '🎯', color: '#8b5cf6' },
  { id: 'CROSS-SYNERGIZE', label: 'Cross-Synergize', emoji: '🔗', color: '#ec4899' },
  { id: 'IMPLEMENT', label: 'Implement', emoji: '⚙️', color: '#f59e0b' },
  { id: 'QA', label: 'QA', emoji: '🔬', color: '#06b6d4' },
  { id: 'TEST', label: 'Test', emoji: '🧪', color: '#10b981' },
  { id: 'EDUCATE', label: 'Educate', emoji: '📚', color: '#a855f7' },
  { id: 'MEASURE', label: 'Measure', emoji: '📊', color: '#f97316' },
  { id: 'REFLECT', label: 'Reflect', emoji: '🪞', color: '#6366f1' },
] as const;

/**
 * Create edges for sequential N-Phase flow.
 */
function createNPhaseEdges(): PolynomialEdge[] {
  const edges: PolynomialEdge[] = [];

  // Forward edges
  for (let i = 0; i < NPHASE_PHASES.length - 1; i++) {
    edges.push({
      source: NPHASE_PHASES[i].id,
      target: NPHASE_PHASES[i + 1].id,
      is_valid: true,
      label: 'advance',
    });
  }

  // Backward edges (can go back one phase)
  for (let i = 1; i < NPHASE_PHASES.length; i++) {
    edges.push({
      source: NPHASE_PHASES[i].id,
      target: NPHASE_PHASES[i - 1].id,
      is_valid: true,
      label: 'revisit',
    });
  }

  return edges;
}

/**
 * Create a PolynomialVisualization for N-Phase development cycle.
 *
 * @param currentPhase - Current phase name
 * @param planName - Name of the plan/project
 * @param progress - Overall progress (0-1)
 * @returns PolynomialVisualization ready for rendering
 */
export function createNPhaseVisualization(
  currentPhase: string,
  planName: string,
  progress: number = 0,
): PolynomialVisualization {
  const positions: PolynomialPosition[] = NPHASE_PHASES.map((p) => ({
    id: p.id,
    label: p.label,
    emoji: p.emoji,
    color: p.color,
    is_current: p.id === currentPhase,
    is_terminal: p.id === 'REFLECT',
  }));

  const edges = createNPhaseEdges();

  const validDirections = edges
    .filter((e) => e.source === currentPhase && e.is_valid)
    .map((e) => e.target);

  return {
    id: `nphase-${planName.toLowerCase().replace(/\s+/g, '-')}`,
    name: planName,
    positions,
    edges,
    current: currentPhase,
    valid_directions: validDirections,
    history: [],
    metadata: {
      progress,
      phase_count: NPHASE_PHASES.length,
      current_index: NPHASE_PHASES.findIndex((p) => p.id === currentPhase),
    },
  };
}

// =============================================================================
// Citizen Polynomial Visualization
// =============================================================================

/**
 * Citizen polynomial phases.
 */
const CITIZEN_PHASES = [
  { id: 'IDLE', label: 'Idle', emoji: '⚪', color: '#94a3b8', description: 'Ready for interaction' },
  { id: 'SOCIALIZING', label: 'Socializing', emoji: '💬', color: '#ec4899', description: 'Engaged in social activity' },
  { id: 'WORKING', label: 'Working', emoji: '🔧', color: '#f59e0b', description: 'Performing solo work' },
  { id: 'REFLECTING', label: 'Reflecting', emoji: '💭', color: '#8b5cf6', description: 'Internal contemplation' },
  { id: 'RESTING', label: 'Resting', emoji: '💤', color: '#22c55e', description: 'Right to Rest active' },
] as const;

/**
 * Citizen polynomial transitions.
 */
const CITIZEN_EDGES: PolynomialEdge[] = [
  // From IDLE
  { source: 'IDLE', target: 'SOCIALIZING', is_valid: true, label: 'greet' },
  { source: 'IDLE', target: 'WORKING', is_valid: true, label: 'work' },
  { source: 'IDLE', target: 'REFLECTING', is_valid: true, label: 'reflect' },
  { source: 'IDLE', target: 'RESTING', is_valid: true, label: 'rest' },
  // From SOCIALIZING
  { source: 'SOCIALIZING', target: 'IDLE', is_valid: true, label: 'done' },
  { source: 'SOCIALIZING', target: 'WORKING', is_valid: true, label: 'work' },
  // From WORKING
  { source: 'WORKING', target: 'IDLE', is_valid: true, label: 'done' },
  { source: 'WORKING', target: 'RESTING', is_valid: true, label: 'rest' },
  // From REFLECTING
  { source: 'REFLECTING', target: 'IDLE', is_valid: true, label: 'done' },
  // From RESTING (Right to Rest - only wake is valid)
  { source: 'RESTING', target: 'IDLE', is_valid: true, label: 'wake' },
];

/**
 * Create a PolynomialVisualization for a Citizen agent.
 *
 * @param citizenName - Name of the citizen
 * @param currentPhase - Current phase
 * @param archetype - Citizen archetype
 * @returns PolynomialVisualization ready for rendering
 */
export function createCitizenVisualization(
  citizenName: string,
  currentPhase: string,
  archetype?: string,
): PolynomialVisualization {
  const positions: PolynomialPosition[] = CITIZEN_PHASES.map((p) => ({
    id: p.id,
    label: p.label,
    emoji: p.emoji,
    color: p.color,
    description: p.description,
    is_current: p.id === currentPhase,
    is_terminal: false,
  }));

  const validDirections = CITIZEN_EDGES
    .filter((e) => e.source === currentPhase && e.is_valid)
    .map((e) => e.target);

  return {
    id: `citizen-${citizenName.toLowerCase().replace(/\s+/g, '-')}`,
    name: citizenName,
    positions,
    edges: CITIZEN_EDGES,
    current: currentPhase,
    valid_directions: validDirections,
    history: [],
    metadata: {
      archetype,
      is_resting: currentPhase === 'RESTING',
    },
  };
}

// =============================================================================
// Generic Visualization Creator
// =============================================================================

export interface GenericPolynomialConfig {
  name: string;
  positions: Array<{
    id: string;
    label: string;
    emoji?: string;
    color?: string;
    description?: string;
    is_terminal?: boolean;
  }>;
  edges: Array<{
    source: string;
    target: string;
    label?: string;
  }>;
}

/**
 * Create a PolynomialVisualization from a generic configuration.
 *
 * @param config - Polynomial configuration
 * @param currentId - ID of the current position
 * @returns PolynomialVisualization
 */
export function createGenericVisualization(
  config: GenericPolynomialConfig,
  currentId: string,
): PolynomialVisualization {
  const positions: PolynomialPosition[] = config.positions.map((p) => ({
    id: p.id,
    label: p.label,
    emoji: p.emoji,
    color: p.color,
    description: p.description,
    is_current: p.id === currentId,
    is_terminal: p.is_terminal ?? false,
  }));

  const edges: PolynomialEdge[] = config.edges.map((e) => ({
    source: e.source,
    target: e.target,
    label: e.label,
    is_valid: true,
  }));

  const validDirections = edges
    .filter((e) => e.source === currentId)
    .map((e) => e.target);

  return {
    id: `generic-${config.name.toLowerCase().replace(/\s+/g, '-')}`,
    name: config.name,
    positions,
    edges,
    current: currentId,
    valid_directions: validDirections,
    history: [],
    metadata: {},
  };
}
