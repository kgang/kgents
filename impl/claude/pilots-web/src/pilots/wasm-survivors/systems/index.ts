/**
 * WASM Survivors - Systems
 */

export {
  updatePhysics,
  checkCollisions,
  createInitialPlayer,
  createInitialGameState,
  ARENA_WIDTH,
  ARENA_HEIGHT,
  type PhysicsResult,
  type CollisionEvent,
  type CollisionResult,
} from './physics';

export {
  updateSpawner,
  startWave,
  resetSpawner,
  type SpawnResult,
} from './spawn';

export {
  createJuiceSystem,
  processJuice,
  checkClutchMoment,
  COLORS,
  type JuiceSystem,
  type Particle,
  type ShakeState,
  type EscalationState,
  type ClutchMomentConfig,
} from './juice';

export {
  emitWitnessMark,
  sealTrace,
  crystallize,
  type WitnessContext,
  type MarkEvent,
} from './witness';

export {
  createSoundEngine,
  getSoundEngine,
  type SoundEngine,
  type SoundId,
  type SoundOptions,
} from './sound';

export {
  UPGRADE_POOL,
  SYNERGY_POOL,
  getUpgrade,
  generateUpgradeChoices,
  detectNewSynergies,
  createInitialActiveUpgrades,
  applyUpgrade,
  getBuildIdentity,
  type UpgradeType,
  type VerbUpgrade,
  type Synergy,
  type ActiveUpgrades,
} from './upgrades';
