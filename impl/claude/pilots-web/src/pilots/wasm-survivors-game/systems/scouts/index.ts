/**
 * Scout Coordination System
 *
 * Enhanced scout bee behavior with two distinct attack patterns:
 * - Solo Flanking: Fast orbiting + hit-and-run stings (mosquito-like harassment)
 * - Coordinated Arc: 3+ scouts encircle and attack in staggered waves
 *
 * @see PROTO_SPEC.md S6: Bee Taxonomy
 * @see config.ts for timing/damage constants
 * @see types.ts for type definitions
 */

// Types
export type {
  ScoutMode,
  ScoutCoordinationState,
  SoloFlankPhase,
  SoloFlankState,
  EncirclePhase,
  CoordinatedGroup,
  ScoutCoordinationManager,
  ScoutEvent,
  SoloFlankTelegraph,
  CoordinatedTelegraph,
} from './types';

// Configuration
export {
  SCOUT_COORDINATION_CONFIG,
  SOLO_STING_CONFIG,
  COORDINATED_ARC_CONFIG,
  SCOUT_WAVE_SCALING,
  getScaledSoloConfig,
  getScaledCoordinatedConfig,
} from './config';

// Core functions
export {
  // Factory functions
  createScoutCoordinationManager,
  createScoutCoordinationState,
  createSoloFlankState,
  createCoordinatedGroup,

  // Mode detection
  evaluateScoutMode,

  // Update functions
  updateSoloFlank,
  updateCoordinatedGroup,
  updateScoutCoordinationSystem,

  // Telegraph generators (for rendering)
  getSoloFlankTelegraph,
  getCoordinatedTelegraph,

  // Result type
  type ScoutSystemUpdateResult,
} from './coordination';

// Integration helpers (for game loop)
export {
  processScoutCoordination,
  applyScoutCoordinationToEnemies,
  isScoutCoordinated,
  cleanupDeadScouts,
  processScoutEvents,
  type ScoutCoordinationResult,
} from './integration';

// Rendering
export {
  renderSoloFlankTelegraph,
  renderCoordinatedTelegraph,
  renderScoutTelegraphs,
} from './render';
