/**
 * Qualia Validation Module
 *
 * General-purpose tools for validating experiential qualities in games.
 *
 * Exports:
 * - Framework: State machine, time dynamics, and emergence validators
 * - Debug API: Helpers for interacting with game debug APIs
 *
 * Usage:
 *   import { createStateMachineValidator, waitForDebugApi } from './qualia-validation';
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

// Framework exports
export {
  createStateMachineValidator,
  createTimeDynamicsAnalyzer,
  createEmergenceDetector,
  generateReport,
  type QualiaResult,
  type QualiaValidator,
  type ValidationReport,
  type StateMachineConfig,
  type StateMachineEvidence,
  type TimeDynamicsConfig,
  type TimeDynamicsEvidence,
  type EmergenceConfig,
  type EmergenceEvidence,
} from './framework';

// Debug API exports
export {
  waitForDebugApi,
  getGameState,
  getEnemies,
  getPlayer,
  getTelegraphs,
  spawnEnemy,
  setInvincible,
  skipWave,
  killAllEnemies,
  triggerLevelUp,
  getLastDamage,
  calculateIntensity,
  getEnemyBehaviorState,
  waitForEnemyState,
  waitForTelegraph,
  captureEvidence,
  captureSequence,
  type DebugEnemy,
  type DebugPlayer,
  type DebugDamageEvent,
  type DebugTelegraph,
  type DebugGameState,
} from './debug-api';
