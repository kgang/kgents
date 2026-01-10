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

// DD-21: Bee behavior system (PROTO_SPEC S6: Bee Taxonomy)
export {
  BEE_BEHAVIORS,
  updateBeeBehavior,
  getBeeTelegraph,
  getBeeMovement,
  isBeeVulnerable,
  isBeeAttacking,
  type BeeBehaviorConfig,
  type TelegraphData,
} from './enemies';

// DD-030: Metamorphosis system
export {
  METAMORPHOSIS_CONFIG,
  TIDE_CONFIG,
  updateSurvivalTime,
  calculatePulsingState,
  updatePulsingStates,
  findSeekTarget,
  getSeekingVelocity,
  checkCombineCollision,
  resetNearbyTimers,
  createColossalTide,
  updateMetamorphosis,
  type MetamorphosisResult,
} from './metamorphosis';

// DD-030-4: Colossal system (THE TIDE)
export {
  COLOSSAL_CONFIG,
  getColossalMovement,
  checkAbsorption,
  applyAbsorption,
  shouldFission,
  performFission,
  shouldActivateGravityWell,
  activateGravityWell,
  applyGravityWell,
  updateColossalBehavior,
  isColossal,
  getColossals,
  getColossalState,
  clearColossalState,
  type ColossalMoveState,
  type ColossalState,
  type ColossalUpdate,
} from './colossal';

// Player Modeling: Adaptive difficulty and behavior analysis
export {
  // Type guards
  isPlayerId,
  isRunId,
  isMovementStyle,
  isPlayStyle,
  isDamageEvent,
  isKillEvent,
  isAdaptationMark,
  // Factory functions
  generatePlayerId,
  generateRunId,
  createInitialHeatmap,
  createInitialRunMicroState,
  createInitialPlayerMacroState,
  createInitialPreferences,
  createInitialPlayerDataStore,
  // Adaptation rules
  calculateSpawnAdjustment,
  calculateUpgradeWeighting,
  shouldTriggerMercy,
  shouldTriggerChallenge,
  detectPlayStyle,
  // Utilities
  emitAdaptationMark,
  classifyMovementStyle,
  updateHeatmap,
  calculateSkillScore,
  // Types
  type PlayerId,
  type RunId,
  type GameTimestamp,
  type DamageEvent,
  type DamageSource,
  type KillEvent,
  type ClutchMoment,
  type ComboChain,
  type UpgradeSelection,
  type MovementStyle,
  type MovementWindow,
  type HeatmapCell,
  type RunMicroState,
  type SkillDataPoint,
  type UpgradePreference,
  type DeathCauseAnalysis,
  type PlayerMacroState,
  type PlayStyle,
  type PlayStyleAnalysis,
  type SpawnAdjustment,
  type WeightedUpgrade,
  type MercyDecision,
  type ChallengeDecision,
  type AdaptationMark,
  type AmberMemory,
  type Milestone,
  type GamePreferences,
  type PlayerDataStore,
} from './player-modeling';

// Event system (replay, serialization, analytics)
export {
  GameEventBus,
  ReplayController,
  EventValidator,
  AggregateAnalytics,
  EventWitnessBridge,
  createEventFactory,
  createFilter,
  EventFilters,
  getEventBus,
  resetEventBus,
  DEFAULT_ANALYTICS_CONFIG,
  type GameEvent,
  type GameEventCategory,
  type GameEventType,
  type GameplayEvent,
  type PlayerEvent,
  type AdaptationEvent,
  type WitnessEvent,
  type SystemEvent,
  type EnemySpawnedEvent,
  type EnemyKilledEvent,
  type ProjectileFiredEvent,
  type ProjectileHitEvent,
  type WaveStartedEvent,
  type WaveCompletedEvent,
  type MetamorphosisEvent,
  type ColossalFissionEvent,
  type GravityWellActivatedEvent,
  type PlayerMovedEvent,
  type PlayerDamagedEvent,
  type PlayerHealedEvent,
  type PlayerLevelUpEvent,
  type UpgradeSelectedEvent,
  type SynergyDiscoveredEvent,
  type DashUsedEvent,
  type PlayerDeathEvent,
  type DifficultyAdjustedEvent,
  type SpawnRateChangedEvent,
  type EnemyTypeUnlockedEvent,
  type MarkEmittedEvent,
  type ClutchMomentEvent,
  type CrystalCreatedEvent,
  type GameStartedEvent,
  type GamePausedEvent,
  type GameResumedEvent,
  type GameEndedEvent,
  type ErrorOccurredEvent,
  type DamageSource as EventDamageSource,
  type AttackType,
  type EventFilter,
  type ReplayFrame,
  type ReplayState,
  type ValidationResult,
  type AnalyticsConfig,
  type AggregateMetric,
  type LocalAnalyticsEvent,
} from './events';

// Witness-Adaptive Bridge: Transparency layer between witness and adaptation systems
// Provides player-facing explanations for WHY the game adapts
export {
  // State creation
  createAdaptationState,
  createDefaultPreferences as createDefaultAdaptationPreferences,
  createPlayerLearningProfile,
  // Adaptation logic
  calculateAdaptationInputs,
  decideAdaptations,
  applyAdaptations,
  // Crystal enhancement
  createAmberMemory as createWitnessedAmberMemory,
  // Profile management
  updatePlayerProfile,
  // Review interface
  createAdaptationReview,
  // Storage keys
  STORAGE_KEYS as WITNESS_STORAGE_KEYS,
  // Types (namespaced to avoid conflicts with player-modeling)
  type AdaptationType,
  type AdaptationInputs,
  type AdaptationOutput,
  type AdaptationWitnessMark,
  type AdaptationOverride,
  type AdaptationReview,
  type AdaptationExplanation,
  type AdaptationSummary,
  type AdaptationContext,
  type AmberMemory as WitnessedAmberMemory,
  type SkillDataPoint as WitnessedSkillDataPoint,
  type PlayerInsight,
  type AdaptationPreferences,
  type PlayerLearningProfile,
  type AdaptationNotification,
  type AdaptationState,
  type UseActiveAdaptationsResult,
  type UseAdaptationHistoryResult,
  type UseAdaptationPreferencesResult,
  type UseAdaptationNotificationsResult,
} from './witness-adaptive-bridge';

// Run 036: New Abilities System (36 abilities across 6 categories)
export {
  ABILITY_POOL,
  getAllAbilities,
  getAbility,
  getAbilitiesByCategory,
  getRiskRewardAbilities,
  getKeystoneAbilities,
  createInitialAbilities,
  addAbility,
  generateAbilityChoices,
  getAbilityChoices,
  hasAbility,
  getAbilityLevel,
  canTakeAbility,
  computeAbilityEffects,
  resetRuntimeForWave,
  recordKillForTrophyScent,
  incrementSawtoothCounter,
  hasConflict,
  getConflicts,
  wouldConflict,
  type AbilityId,
  type AbilityCategory,
  type Ability,
  type AbilityEffect,
  type AbilityMechanic,
  type AbilityCurse,
  type CurseEffect,
  type ActiveAbilities as NewActiveAbilities,
  type AbilityRuntime,
  type ComputedEffects,
  type RiskLevel,
  type SkillDemand,
  type ComboPotential,
  type AbilityJuiceConfig,
} from './abilities';

// Run 036: Mandible Reaver Melee System
export {
  MANDIBLE_REAVER_CONFIG,
  createInitialMeleeState,
  canAttack,
  startAttack,
  isInAttackArc,
  findTargetsInArc,
  calculateMeleeDamage,
  updateMeleeAttack,
  getModifiedConfig,
  getMultishotDirections,
  getArcRenderPoints,
  getAttackProgress,
  type MandibleReaverConfig,
  type MeleeAttackState,
  type MeleeUpdateResult,
  type MeleeHit,
  type MeleeEvent,
  type MeleeEventType,
  type MeleeTarget,
} from './melee';

// Run 036: Hornet-Native Combo Discovery System (27 combos)
export {
  COMBO_POOL,
  getCombo,
  getCombosByTier,
  createInitialComboState,
  applyComboDiscovery,
  activateCombo,
  trackAbilityOrder,
  checkForCombos,
  checkDeathCombos,
  getPossibleCombos,
  getComboHint,
  type Combo,
  type ComboTier,
  type ComboEffect,
  type ComboState,
  type ComboDiscovery,
  type ComboCheckResult,
  type AlmostCombo,
  type SpecialCondition,
} from './combos';

// Run 036: Apex Strike Dash System (Predator Hunt)
export {
  // Config
  APEX_CONFIG,
  // State factory
  createInitialApexState,
  // Phase checks
  canApex,
  canChain,
  isVulnerable,
  isUnstoppable,
  isStriking,
  isLocking,
  isInGripMoment,
  // Phase transitions
  initiateLock,
  updateLockDirection,
  executeStrike,
  onStrikeHit,
  onStrikeMiss,
  attemptChain,
  // Hit detection
  checkStrikeHit,
  // Update loop
  updateApexStrike,
  getStrikeVelocity,
  // Progress getters
  getBloodlustPercent,
  getBloodlustDamageMultiplier,
  getCooldownProgress,
  getChainWindowProgress,
  getLockProgress,
  getStrikeProgress,
  // Visual helpers
  getBloodlustColor,
  getStrikeTrailPoints,
  getAimIndicatorEnd,
  // Input helpers
  getAimFromInput,
  // Types
  type ApexPhase,
  type ApexStrikeState,
  type ApexStrikeConfig,
  type ApexEvent,
  type StrikeHitResult,
  type ApexUpdateResult,
  type ApexTarget,
} from './apex-strike';
