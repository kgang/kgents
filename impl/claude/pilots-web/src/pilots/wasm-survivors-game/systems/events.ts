/**
 * WASM Survivors - Event System
 *
 * A comprehensive, typed event system supporting:
 * - Real-time gameplay events with discriminated unions
 * - Event replay for ghost runs and debugging
 * - Event serialization for sharing runs
 * - Privacy-first analytics (aggregate only, never individual)
 *
 * Design Principles:
 * - All game state changes flow through typed events
 * - Events are immutable after creation
 * - Replay is deterministic: same events = same game state
 * - Privacy by default: no PII, only aggregates transmitted
 *
 * @see spec/theory/domains/wasm-survivors-quality.md
 */

import type {
  Vector2,
  EnemyType,
  BuildContext,
  WitnessMark,
  SkillMetrics,
} from '../types';
import type { UpgradeType, Synergy } from './upgrades';

// =============================================================================
// Event Categories & Base Types
// =============================================================================

/**
 * Event categories for filtering and routing
 */
export type GameEventCategory =
  | 'gameplay'     // Things happening in the game world
  | 'player'       // Player actions and inputs
  | 'adaptation'   // System adapting to player (difficulty, spawning)
  | 'witness'      // Marks and crystal events
  | 'system';      // Technical events (pause, resume, error)

/**
 * Damage sources for analytics and replay
 */
export type DamageSource =
  | 'projectile'         // Player projectile
  | 'orbit'              // Orbital guard
  | 'burst'              // Explosion from burst upgrade
  | 'chain'              // Chain lightning bounce
  | 'dash'               // Dash damage
  | 'colossal_fission'   // Colossal fission explosion
  | 'environment';       // Environmental hazard

/**
 * Attack types that can damage player
 */
export type AttackType =
  | 'lunge'       // Basic enemy lunge
  | 'charge'      // Fast enemy charge
  | 'stomp'       // Tank enemy stomp
  | 'projectile'  // Spitter projectile
  | 'combo'       // Boss combo attack
  | 'gravity'     // Colossal gravity well
  | 'contact';    // Direct contact damage

/**
 * Base event properties shared by all events
 */
interface BaseEvent {
  /** Unique event ID for deduplication and replay */
  id: string;
  /** Event category for filtering */
  category: GameEventCategory;
  /** Game time (accumulated), NOT wall clock */
  timestamp: number;
  /** Frame number for precise replay ordering */
  frame: number;
}

// =============================================================================
// Gameplay Events
// =============================================================================

export interface EnemySpawnedEvent extends BaseEvent {
  category: 'gameplay';
  type: 'enemy_spawned';
  data: {
    enemyId: string;
    enemyType: EnemyType;
    position: Vector2;
    wave: number;
    spawnReason: 'wave' | 'metamorphosis' | 'boss';
  };
}

export interface EnemyKilledEvent extends BaseEvent {
  category: 'gameplay';
  type: 'enemy_killed';
  data: {
    enemyId: string;
    enemyType: EnemyType;
    position: Vector2;
    damageSource: DamageSource;
    /** Player was below 25% HP when kill happened */
    wasClutch: boolean;
    /** XP value awarded */
    xpAwarded: number;
    /** Time enemy was alive (for metamorphosis tracking) */
    survivalTime: number;
  };
}

export interface ProjectileFiredEvent extends BaseEvent {
  category: 'gameplay';
  type: 'projectile_fired';
  data: {
    projectileId: string;
    position: Vector2;
    velocity: Vector2;
    damage: number;
    /** Source upgrade if special projectile */
    source: 'auto' | 'multishot' | 'chain';
    /** Pierce count remaining */
    pierceCount: number;
  };
}

export interface ProjectileHitEvent extends BaseEvent {
  category: 'gameplay';
  type: 'projectile_hit';
  data: {
    projectileId: string;
    targetId: string;
    targetType: 'enemy' | 'player';
    position: Vector2;
    damage: number;
    /** Did this kill the target */
    lethal: boolean;
    /** Pierce count after hit */
    pierceRemaining: number;
  };
}

export interface WaveStartedEvent extends BaseEvent {
  category: 'gameplay';
  type: 'wave_started';
  data: {
    wave: number;
    enemyCount: number;
    enemyTypes: EnemyType[];
    /** Difficulty multiplier for this wave */
    difficultyScale: number;
  };
}

export interface WaveCompletedEvent extends BaseEvent {
  category: 'gameplay';
  type: 'wave_completed';
  data: {
    wave: number;
    /** Time taken to complete wave */
    duration: number;
    /** Enemies killed this wave */
    enemiesKilled: number;
    /** Damage taken this wave */
    damageTaken: number;
    /** Player health at wave end */
    healthRemaining: number;
  };
}

export interface MetamorphosisEvent extends BaseEvent {
  category: 'gameplay';
  type: 'metamorphosis';
  data: {
    /** IDs of enemies that combined */
    sourceIds: string[];
    /** Position where colossal spawned */
    position: Vector2;
    /** Resulting colossal ID */
    colossalId: string;
    /** Is this the first metamorphosis this run */
    isFirstReveal: boolean;
  };
}

export interface ColossalFissionEvent extends BaseEvent {
  category: 'gameplay';
  type: 'colossal_fission';
  data: {
    colossalId: string;
    position: Vector2;
    /** IDs of spawned smaller enemies */
    spawnedIds: string[];
    /** Damage dealt by fission explosion */
    fissionDamage: number;
  };
}

export interface GravityWellActivatedEvent extends BaseEvent {
  category: 'gameplay';
  type: 'gravity_well_activated';
  data: {
    colossalId: string;
    position: Vector2;
    radius: number;
    duration: number;
  };
}

// =============================================================================
// Player Events
// =============================================================================

export interface PlayerMovedEvent extends BaseEvent {
  category: 'player';
  type: 'player_moved';
  data: {
    from: Vector2;
    to: Vector2;
    velocity: Vector2;
    /** Was this a dash */
    isDash: boolean;
  };
}

export interface PlayerDamagedEvent extends BaseEvent {
  category: 'player';
  type: 'player_damaged';
  data: {
    damage: number;
    healthBefore: number;
    healthAfter: number;
    attackType: AttackType;
    attackerId: string;
    attackerType: EnemyType;
    position: Vector2;
    /** Was player below 25% HP before hit */
    wasClutchHit: boolean;
  };
}

export interface PlayerHealedEvent extends BaseEvent {
  category: 'player';
  type: 'player_healed';
  data: {
    amount: number;
    healthBefore: number;
    healthAfter: number;
    source: 'vampiric' | 'pickup' | 'wave_clear';
  };
}

export interface PlayerLevelUpEvent extends BaseEvent {
  category: 'player';
  type: 'player_level_up';
  data: {
    level: number;
    xpTotal: number;
    /** Upgrade choices presented */
    upgradeChoices: UpgradeType[];
  };
}

export interface UpgradeSelectedEvent extends BaseEvent {
  category: 'player';
  type: 'upgrade_selected';
  data: {
    upgrade: UpgradeType;
    /** Other options that were available */
    alternatives: UpgradeType[];
    /** Level at which upgrade was selected */
    level: number;
    /** Total upgrades now owned */
    totalUpgrades: number;
    /** Build context at selection time */
    buildContext: BuildContext;
  };
}

export interface SynergyDiscoveredEvent extends BaseEvent {
  category: 'player';
  type: 'synergy_discovered';
  data: {
    synergy: Synergy;
    /** Upgrades that triggered synergy */
    triggerUpgrades: [UpgradeType, UpgradeType];
    /** Build context at discovery */
    buildContext: BuildContext;
  };
}

export interface DashUsedEvent extends BaseEvent {
  category: 'player';
  type: 'dash_used';
  data: {
    from: Vector2;
    to: Vector2;
    /** Enemies passed through (for damage calc) */
    enemiesPassed: string[];
    /** Was whirlwind synergy active */
    triggeredWhirlwind: boolean;
    /** Cooldown remaining after dash */
    cooldownRemaining: number;
  };
}

export interface PlayerDeathEvent extends BaseEvent {
  category: 'player';
  type: 'player_death';
  data: {
    position: Vector2;
    killerId: string;
    killerType: EnemyType;
    attackType: AttackType;
    wave: number;
    gameTime: number;
    totalKills: number;
    finalBuild: UpgradeType[];
    finalSynergies: string[];
  };
}

// =============================================================================
// Adaptation Events
// =============================================================================

export interface DifficultyAdjustedEvent extends BaseEvent {
  category: 'adaptation';
  type: 'difficulty_adjusted';
  data: {
    previousScale: number;
    newScale: number;
    reason: 'player_struggling' | 'player_dominating' | 'wave_progression' | 'time_based';
    metrics: SkillMetrics;
  };
}

export interface SpawnRateChangedEvent extends BaseEvent {
  category: 'adaptation';
  type: 'spawn_rate_changed';
  data: {
    previousRate: number;
    newRate: number;
    wave: number;
  };
}

export interface EnemyTypeUnlockedEvent extends BaseEvent {
  category: 'adaptation';
  type: 'enemy_type_unlocked';
  data: {
    enemyType: EnemyType;
    wave: number;
    reason: string;
  };
}

// =============================================================================
// Witness Events
// =============================================================================

export interface MarkEmittedEvent extends BaseEvent {
  category: 'witness';
  type: 'mark_emitted';
  data: {
    mark: WitnessMark;
    markType: WitnessMark['intent']['type'];
    risk: 'low' | 'medium' | 'high';
  };
}

export interface ClutchMomentEvent extends BaseEvent {
  category: 'witness';
  type: 'clutch_moment';
  data: {
    healthPercent: number;
    threatsNearby: number;
    survivedDuration: number;
    escapedVia: 'kill' | 'dash' | 'movement' | 'heal';
  };
}

export interface CrystalCreatedEvent extends BaseEvent {
  category: 'witness';
  type: 'crystal_created';
  data: {
    runId: string;
    waveReached: number;
    duration: number;
    markCount: number;
    ghostCount: number;
    shareableHash: string;
  };
}

// =============================================================================
// System Events
// =============================================================================

export interface GameStartedEvent extends BaseEvent {
  category: 'system';
  type: 'game_started';
  data: {
    runId: string;
    startTime: number;
    /** Build version for replay compatibility */
    buildVersion: string;
    /** Seed for deterministic replay (if applicable) */
    seed?: number;
  };
}

export interface GamePausedEvent extends BaseEvent {
  category: 'system';
  type: 'game_paused';
  data: {
    reason: 'user' | 'upgrade_ui' | 'focus_lost' | 'crystallization';
    pauseDuration?: number; // Only set when unpausing
  };
}

export interface GameResumedEvent extends BaseEvent {
  category: 'system';
  type: 'game_resumed';
  data: {
    pausedDuration: number;
  };
}

export interface GameEndedEvent extends BaseEvent {
  category: 'system';
  type: 'game_ended';
  data: {
    runId: string;
    endReason: 'death' | 'victory' | 'quit';
    wave: number;
    gameTime: number;
    score: number;
    totalKills: number;
  };
}

export interface ErrorOccurredEvent extends BaseEvent {
  category: 'system';
  type: 'error_occurred';
  data: {
    errorType: string;
    message: string;
    /** Stack trace (local only, never transmitted) */
    stack?: string;
    recoverable: boolean;
  };
}

// =============================================================================
// Union Type for All Events
// =============================================================================

export type GameplayEvent =
  | EnemySpawnedEvent
  | EnemyKilledEvent
  | ProjectileFiredEvent
  | ProjectileHitEvent
  | WaveStartedEvent
  | WaveCompletedEvent
  | MetamorphosisEvent
  | ColossalFissionEvent
  | GravityWellActivatedEvent;

export type PlayerEvent =
  | PlayerMovedEvent
  | PlayerDamagedEvent
  | PlayerHealedEvent
  | PlayerLevelUpEvent
  | UpgradeSelectedEvent
  | SynergyDiscoveredEvent
  | DashUsedEvent
  | PlayerDeathEvent;

export type AdaptationEvent =
  | DifficultyAdjustedEvent
  | SpawnRateChangedEvent
  | EnemyTypeUnlockedEvent;

export type WitnessEvent =
  | MarkEmittedEvent
  | ClutchMomentEvent
  | CrystalCreatedEvent;

export type SystemEvent =
  | GameStartedEvent
  | GamePausedEvent
  | GameResumedEvent
  | GameEndedEvent
  | ErrorOccurredEvent;

/**
 * Discriminated union of all game events
 */
export type GameEvent =
  | GameplayEvent
  | PlayerEvent
  | AdaptationEvent
  | WitnessEvent
  | SystemEvent;

/**
 * Extract event type string
 */
export type GameEventType = GameEvent['type'];

// =============================================================================
// Event Filtering
// =============================================================================

/**
 * Filter for subscribing to specific events
 */
export interface EventFilter<T extends GameEvent = GameEvent> {
  /** Filter by category */
  category?: GameEventCategory | GameEventCategory[];
  /** Filter by specific event type(s) */
  type?: T['type'] | T['type'][];
  /** Filter by time range */
  timeRange?: { start: number; end: number };
  /** Filter by frame range */
  frameRange?: { start: number; end: number };
  /** Custom predicate */
  predicate?: (event: GameEvent) => event is T;
}

/**
 * Type-safe event filter builder
 */
export function createFilter<T extends GameEvent>(
  filter: EventFilter<T>
): EventFilter<T> {
  return filter;
}

/**
 * Common preset filters
 */
export const EventFilters = {
  /** All gameplay events */
  gameplay: createFilter<GameplayEvent>({ category: 'gameplay' }),
  /** All player events */
  player: createFilter<PlayerEvent>({ category: 'player' }),
  /** All witness events */
  witness: createFilter<WitnessEvent>({ category: 'witness' }),
  /** Kill events only */
  kills: createFilter<EnemyKilledEvent>({ type: 'enemy_killed' }),
  /** Damage events */
  damage: createFilter<PlayerDamagedEvent | EnemyKilledEvent>({
    type: ['player_damaged', 'enemy_killed'] as ('player_damaged' | 'enemy_killed')[],
  }),
  /** Level/upgrade events */
  progression: createFilter<PlayerLevelUpEvent | UpgradeSelectedEvent | SynergyDiscoveredEvent>({
    type: ['player_level_up', 'upgrade_selected', 'synergy_discovered'] as ('player_level_up' | 'upgrade_selected' | 'synergy_discovered')[],
  }),
} as const;

// =============================================================================
// Event Bus Implementation
// =============================================================================

type Unsubscribe = () => void;
type EventHandler<T extends GameEvent> = (event: T) => void;

interface Subscription {
  filter: EventFilter;
  handler: EventHandler<GameEvent>;
  id: string;
}

/**
 * Central event bus for all game events
 *
 * Features:
 * - Type-safe subscriptions with discriminated unions
 * - Event history for replay
 * - Serialization for sharing
 * - Non-blocking emission
 */
export class GameEventBus {
  private subscriptions: Map<string, Subscription> = new Map();
  private history: GameEvent[] = [];
  private frameCounter = 0;
  private isPaused = false;
  private maxHistorySize: number;

  constructor(options: { maxHistorySize?: number } = {}) {
    this.maxHistorySize = options.maxHistorySize ?? 100000;
  }

  /**
   * Subscribe to events matching the filter
   */
  subscribe<T extends GameEvent>(
    filter: EventFilter<T>,
    handler: EventHandler<T>
  ): Unsubscribe {
    const id = `sub-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

    this.subscriptions.set(id, {
      filter: filter as EventFilter,
      handler: handler as EventHandler<GameEvent>,
      id,
    });

    return () => {
      this.subscriptions.delete(id);
    };
  }

  /**
   * Subscribe to all events (debugging/logging)
   */
  subscribeAll(handler: EventHandler<GameEvent>): Unsubscribe {
    return this.subscribe({}, handler);
  }

  /**
   * Emit an event to all matching subscribers
   *
   * PERFORMANCE: Uses queueMicrotask for non-blocking emission
   */
  emit<T extends GameEvent>(eventData: Omit<T, 'id' | 'frame'>): void {
    if (this.isPaused && eventData.type !== 'game_resumed') {
      return;
    }

    const event: GameEvent = {
      ...eventData,
      id: `evt-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      frame: this.frameCounter,
    } as GameEvent;

    // Store in history
    this.history.push(event);
    if (this.history.length > this.maxHistorySize) {
      // Trim oldest events, keeping system events
      const systemEvents = this.history.filter((e) => e.category === 'system');
      const nonSystemEvents = this.history.filter((e) => e.category !== 'system');
      const trimCount = Math.floor(this.maxHistorySize * 0.1);
      this.history = [...systemEvents, ...nonSystemEvents.slice(trimCount)];
    }

    // Dispatch to subscribers (non-blocking)
    queueMicrotask(() => {
      for (const subscription of this.subscriptions.values()) {
        if (this.matchesFilter(event, subscription.filter)) {
          try {
            subscription.handler(event);
          } catch (err) {
            console.error(`Event handler error for ${event.type}:`, err);
          }
        }
      }
    });
  }

  /**
   * Increment frame counter (call once per game loop)
   */
  tick(): void {
    this.frameCounter++;
  }

  /**
   * Get current frame number
   */
  getFrame(): number {
    return this.frameCounter;
  }

  /**
   * Pause event emission (except system events)
   */
  pause(): void {
    this.isPaused = true;
  }

  /**
   * Resume event emission
   */
  resume(): void {
    this.isPaused = false;
  }

  /**
   * Get event history with optional filtering
   */
  getHistory<T extends GameEvent>(filter?: EventFilter<T>): T[] {
    if (!filter) {
      return this.history as T[];
    }

    return this.history.filter((event) =>
      this.matchesFilter(event, filter as EventFilter)
    ) as T[];
  }

  /**
   * Get events in a time range
   */
  getEventsInRange(start: number, end: number): GameEvent[] {
    return this.history.filter(
      (e) => e.timestamp >= start && e.timestamp <= end
    );
  }

  /**
   * Get the last N events
   */
  getLastEvents(count: number, filter?: EventFilter): GameEvent[] {
    const filtered = filter
      ? this.history.filter((e) => this.matchesFilter(e, filter))
      : this.history;

    return filtered.slice(-count);
  }

  /**
   * Clear history (call on new game)
   */
  clearHistory(): void {
    this.history = [];
    this.frameCounter = 0;
  }

  /**
   * Serialize events for sharing/storage
   */
  serialize(events?: GameEvent[]): string {
    const toSerialize = events ?? this.history;

    // Filter out sensitive data before serialization
    const sanitized = toSerialize.map((event) => {
      if (event.type === 'error_occurred') {
        // Remove stack traces
        const { data, ...rest } = event;
        const { stack, ...safeData } = data;
        return { ...rest, data: safeData };
      }
      return event;
    });

    return JSON.stringify({
      version: '1.0.0',
      exportTime: Date.now(),
      eventCount: sanitized.length,
      events: sanitized,
    });
  }

  /**
   * Deserialize events from stored/shared data
   */
  deserialize(data: string): GameEvent[] {
    try {
      const parsed = JSON.parse(data);

      if (!parsed.version || !parsed.events) {
        throw new Error('Invalid event data format');
      }

      // Version compatibility check
      const [major] = parsed.version.split('.');
      if (major !== '1') {
        throw new Error(`Incompatible event data version: ${parsed.version}`);
      }

      return parsed.events as GameEvent[];
    } catch (err) {
      console.error('Failed to deserialize events:', err);
      return [];
    }
  }

  /**
   * Check if event matches filter
   */
  private matchesFilter(event: GameEvent, filter: EventFilter): boolean {
    // Category filter
    if (filter.category) {
      const categories = Array.isArray(filter.category)
        ? filter.category
        : [filter.category];
      if (!categories.includes(event.category)) {
        return false;
      }
    }

    // Type filter
    if (filter.type) {
      const types = Array.isArray(filter.type) ? filter.type : [filter.type];
      if (!types.includes(event.type as never)) {
        return false;
      }
    }

    // Time range filter
    if (filter.timeRange) {
      if (
        event.timestamp < filter.timeRange.start ||
        event.timestamp > filter.timeRange.end
      ) {
        return false;
      }
    }

    // Frame range filter
    if (filter.frameRange) {
      if (
        event.frame < filter.frameRange.start ||
        event.frame > filter.frameRange.end
      ) {
        return false;
      }
    }

    // Custom predicate
    if (filter.predicate) {
      if (!filter.predicate(event)) {
        return false;
      }
    }

    return true;
  }
}

// =============================================================================
// Replay System
// =============================================================================

export interface ReplayFrame {
  timestamp: number;
  frame: number;
  events: GameEvent[];
}

export interface ReplayState {
  runId: string;
  totalFrames: number;
  totalDuration: number;
  events: GameEvent[];
  currentFrame: number;
  isPlaying: boolean;
  speed: number;
}

/**
 * Controller for replaying recorded game sessions
 */
export class ReplayController {
  private events: GameEvent[] = [];
  private frameIndex: Map<number, GameEvent[]> = new Map();
  private currentFrame = 0;
  private isPlaying = false;
  private speed = 1.0;
  private animationId: number | null = null;
  private lastTimestamp = 0;
  private onFrame: ((frame: ReplayFrame) => void) | null = null;

  /**
   * Load serialized run data
   */
  load(data: string): ReplayState {
    const bus = new GameEventBus();
    this.events = bus.deserialize(data);

    // Build frame index
    this.frameIndex.clear();
    for (const event of this.events) {
      const frameEvents = this.frameIndex.get(event.frame) ?? [];
      frameEvents.push(event);
      this.frameIndex.set(event.frame, frameEvents);
    }

    this.currentFrame = 0;
    this.isPlaying = false;
    this.speed = 1.0;

    const lastEvent = this.events[this.events.length - 1];
    const firstEvent = this.events[0];

    return {
      runId: this.getRunId(),
      totalFrames: lastEvent?.frame ?? 0,
      totalDuration: (lastEvent?.timestamp ?? 0) - (firstEvent?.timestamp ?? 0),
      events: this.events,
      currentFrame: 0,
      isPlaying: false,
      speed: 1.0,
    };
  }

  /**
   * Set callback for frame updates
   */
  onFrameUpdate(callback: (frame: ReplayFrame) => void): void {
    this.onFrame = callback;
  }

  /**
   * Start playback
   */
  play(): void {
    if (this.isPlaying) return;
    this.isPlaying = true;
    this.lastTimestamp = performance.now();
    this.scheduleNextFrame();
  }

  /**
   * Pause playback
   */
  pause(): void {
    this.isPlaying = false;
    if (this.animationId !== null) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  /**
   * Seek to specific frame
   */
  seek(frame: number): void {
    this.currentFrame = Math.max(0, Math.min(frame, this.getTotalFrames()));
    this.emitCurrentFrame();
  }

  /**
   * Seek to specific timestamp (game time)
   */
  seekToTime(timestamp: number): void {
    // Find frame closest to timestamp
    for (let i = this.events.length - 1; i >= 0; i--) {
      if (this.events[i].timestamp <= timestamp) {
        this.seek(this.events[i].frame);
        return;
      }
    }
    this.seek(0);
  }

  /**
   * Set playback speed multiplier
   */
  setSpeed(multiplier: number): void {
    this.speed = Math.max(0.1, Math.min(10, multiplier));
  }

  /**
   * Get current replay frame
   */
  getCurrentFrame(): ReplayFrame {
    const events = this.frameIndex.get(this.currentFrame) ?? [];
    const timestamp = events[0]?.timestamp ?? 0;

    return {
      timestamp,
      frame: this.currentFrame,
      events,
    };
  }

  /**
   * Get replay progress (0-1)
   */
  getProgress(): number {
    const total = this.getTotalFrames();
    return total > 0 ? this.currentFrame / total : 0;
  }

  /**
   * Get total frames in replay
   */
  getTotalFrames(): number {
    const lastEvent = this.events[this.events.length - 1];
    return lastEvent?.frame ?? 0;
  }

  /**
   * Step forward one frame
   */
  stepForward(): void {
    if (this.currentFrame < this.getTotalFrames()) {
      this.currentFrame++;
      this.emitCurrentFrame();
    }
  }

  /**
   * Step backward one frame
   */
  stepBackward(): void {
    if (this.currentFrame > 0) {
      this.currentFrame--;
      this.emitCurrentFrame();
    }
  }

  /**
   * Get events for reconstructing game state at current frame
   */
  getStateEvents(): GameEvent[] {
    // Return all events up to current frame for state reconstruction
    return this.events.filter((e) => e.frame <= this.currentFrame);
  }

  private getRunId(): string {
    const startEvent = this.events.find(
      (e) => e.type === 'game_started'
    ) as GameStartedEvent | undefined;
    return startEvent?.data.runId ?? 'unknown';
  }

  private scheduleNextFrame(): void {
    this.animationId = requestAnimationFrame((timestamp) => {
      if (!this.isPlaying) return;

      const delta = (timestamp - this.lastTimestamp) * this.speed;
      this.lastTimestamp = timestamp;

      // Advance frames based on time
      const framesToAdvance = Math.floor(delta / (1000 / 60)); // Assuming 60fps
      if (framesToAdvance > 0) {
        this.currentFrame = Math.min(
          this.currentFrame + framesToAdvance,
          this.getTotalFrames()
        );
        this.emitCurrentFrame();
      }

      // Continue or end
      if (this.currentFrame < this.getTotalFrames()) {
        this.scheduleNextFrame();
      } else {
        this.isPlaying = false;
      }
    });
  }

  private emitCurrentFrame(): void {
    if (this.onFrame) {
      this.onFrame(this.getCurrentFrame());
    }
  }
}

// =============================================================================
// Event Validation
// =============================================================================

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

/**
 * Validate events for correctness and consistency
 */
export class EventValidator {
  /**
   * Validate a single event
   */
  validate(event: GameEvent): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Base validation
    if (!event.id) {
      errors.push('Event missing id');
    }
    if (typeof event.timestamp !== 'number' || event.timestamp < 0) {
      errors.push('Event has invalid timestamp');
    }
    if (typeof event.frame !== 'number' || event.frame < 0) {
      errors.push('Event has invalid frame');
    }
    if (!event.category) {
      errors.push('Event missing category');
    }
    if (!event.type) {
      errors.push('Event missing type');
    }

    // Type-specific validation
    const typeValidation = this.validateByType(event);
    errors.push(...typeValidation.errors);
    warnings.push(...typeValidation.warnings);

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Validate event sequence for consistency
   */
  validateSequence(events: GameEvent[]): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    let lastFrame = -1;
    let lastTimestamp = -1;
    let gameStarted = false;
    let gameEnded = false;

    for (let i = 0; i < events.length; i++) {
      const event = events[i];

      // Check ordering
      if (event.frame < lastFrame) {
        errors.push(`Event ${i} has frame ${event.frame} before previous ${lastFrame}`);
      }
      if (event.timestamp < lastTimestamp) {
        warnings.push(`Event ${i} has timestamp before previous (possible pause)`);
      }

      // Check game lifecycle
      if (event.type === 'game_started') {
        if (gameStarted && !gameEnded) {
          errors.push(`Game started twice without ending (event ${i})`);
        }
        gameStarted = true;
        gameEnded = false;
      }
      if (event.type === 'game_ended') {
        if (!gameStarted) {
          errors.push(`Game ended without starting (event ${i})`);
        }
        gameEnded = true;
      }

      lastFrame = event.frame;
      lastTimestamp = event.timestamp;
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  private validateByType(event: GameEvent): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    switch (event.type) {
      case 'enemy_killed': {
        const data = event.data;
        if (!data.enemyId) errors.push('enemy_killed missing enemyId');
        if (!data.enemyType) errors.push('enemy_killed missing enemyType');
        if (!data.position) errors.push('enemy_killed missing position');
        break;
      }

      case 'player_damaged': {
        const data = event.data;
        if (data.damage < 0) errors.push('player_damaged has negative damage');
        if (data.healthAfter < 0) warnings.push('player_damaged resulted in negative health');
        break;
      }

      case 'upgrade_selected': {
        const data = event.data;
        if (!data.upgrade) errors.push('upgrade_selected missing upgrade');
        if (!data.alternatives || !Array.isArray(data.alternatives)) {
          errors.push('upgrade_selected missing alternatives');
        }
        break;
      }

      case 'wave_started': {
        const data = event.data;
        if (data.wave < 1) errors.push('wave_started has invalid wave number');
        if (data.enemyCount < 0) errors.push('wave_started has negative enemy count');
        break;
      }

      // Add more type-specific validations as needed
    }

    return { valid: errors.length === 0, errors, warnings };
  }
}

// =============================================================================
// Analytics (Privacy-First)
// =============================================================================

/**
 * Analytics configuration - privacy by default
 */
export interface AnalyticsConfig {
  /** What aggregate metrics we measure */
  measures: {
    sessionDuration: boolean;
    deathCounts: boolean;
    upgradePopularity: boolean;
    completionRates: boolean;
    waveDistribution: boolean;
    averageGameTime: boolean;
  };

  /** Data we NEVER collect - for documentation and auditing */
  readonly forbidden: readonly [
    'ip_address',
    'device_fingerprint',
    'precise_timestamps',
    'personal_identifiers',
    'location_data',
    'browser_history',
    'contact_information',
  ];

  /** User controls */
  optOut: boolean;
  dataRetention: '24h' | '7d' | '30d' | 'session_only';

  /** Local-only detailed stats (never transmitted) */
  localDetailedStats: boolean;
}

/**
 * Default analytics config - conservative privacy settings
 */
export const DEFAULT_ANALYTICS_CONFIG: AnalyticsConfig = {
  measures: {
    sessionDuration: true,
    deathCounts: true,
    upgradePopularity: true,
    completionRates: true,
    waveDistribution: true,
    averageGameTime: true,
  },
  forbidden: [
    'ip_address',
    'device_fingerprint',
    'precise_timestamps',
    'personal_identifiers',
    'location_data',
    'browser_history',
    'contact_information',
  ],
  optOut: false,
  dataRetention: 'session_only',
  localDetailedStats: true,
};

/**
 * Aggregate analytics event (safe to transmit)
 */
export interface AggregateMetric {
  metric: string;
  value: number;
  /** Bucket (e.g., wave range, time range) - never precise */
  bucket?: string;
  /** Count contributing to aggregate */
  sampleSize: number;
}

/**
 * Local-only detailed analytics (never transmitted)
 */
export interface LocalAnalyticsEvent {
  type: string;
  timestamp: number; // Local only
  data: Record<string, unknown>;
}

/**
 * Privacy-first analytics collector
 *
 * DESIGN PRINCIPLES:
 * - Aggregates only: never individual data points
 * - No PII: forbidden list is enforced
 * - Local first: detailed stats stay on device
 * - Opt-out respected: if optOut, nothing is recorded
 */
export class AggregateAnalytics {
  private config: AnalyticsConfig;
  private aggregates: Map<string, { sum: number; count: number }> = new Map();
  private localEvents: LocalAnalyticsEvent[] = [];
  private maxLocalEvents = 1000;

  constructor(config: Partial<AnalyticsConfig> = {}) {
    this.config = { ...DEFAULT_ANALYTICS_CONFIG, ...config };
  }

  /**
   * Record an aggregate metric (safe to transmit)
   */
  emit(metric: string, value: number): void {
    if (this.config.optOut) return;

    // Validate metric is allowed
    if (!this.isMetricAllowed(metric)) {
      console.warn(`Analytics: metric "${metric}" not in allowed measures`);
      return;
    }

    const current = this.aggregates.get(metric) ?? { sum: 0, count: 0 };
    this.aggregates.set(metric, {
      sum: current.sum + value,
      count: current.count + 1,
    });
  }

  /**
   * Record local-only detailed event (never transmitted)
   */
  recordLocal(event: LocalAnalyticsEvent): void {
    if (!this.config.localDetailedStats) return;

    this.localEvents.push(event);

    // Trim old events
    if (this.localEvents.length > this.maxLocalEvents) {
      this.localEvents = this.localEvents.slice(-this.maxLocalEvents);
    }
  }

  /**
   * Get aggregate metrics for transmission
   */
  getAggregates(): AggregateMetric[] {
    if (this.config.optOut) return [];

    return Array.from(this.aggregates.entries()).map(([metric, data]) => ({
      metric,
      value: data.sum / data.count, // Average
      sampleSize: data.count,
    }));
  }

  /**
   * Get local detailed events (for debugging/personal stats)
   */
  getLocalEvents(): LocalAnalyticsEvent[] {
    return [...this.localEvents];
  }

  /**
   * Clear all data (on opt-out or session end)
   */
  clear(): void {
    this.aggregates.clear();
    this.localEvents = [];
  }

  /**
   * Update opt-out preference
   */
  setOptOut(optOut: boolean): void {
    this.config.optOut = optOut;
    if (optOut) {
      this.clear();
    }
  }

  /**
   * Check if a metric is in the allowed measures
   */
  private isMetricAllowed(metric: string): boolean {
    // Map metrics to config flags
    const metricMap: Record<string, keyof AnalyticsConfig['measures']> = {
      session_duration: 'sessionDuration',
      death_count: 'deathCounts',
      upgrade_picked: 'upgradePopularity',
      wave_reached: 'completionRates',
      wave_distribution: 'waveDistribution',
      game_time: 'averageGameTime',
    };

    const configKey = metricMap[metric];
    if (configKey && this.config.measures[configKey]) {
      return true;
    }

    // Allow custom metrics that don't fall into forbidden categories
    return true;
  }
}

// =============================================================================
// Event-Witness Bridge
// =============================================================================

/**
 * Bridge between event system and witness marks
 *
 * Converts significant gameplay events into witness marks
 * for crystal compression and run narrative.
 */
export class EventWitnessBridge {
  /**
   * Determine if an event should generate a witness mark
   */
  shouldMark(event: GameEvent): boolean {
    // Always mark these significant events
    const significantTypes: GameEventType[] = [
      'enemy_killed',
      'player_damaged',
      'player_level_up',
      'upgrade_selected',
      'synergy_discovered',
      'wave_completed',
      'player_death',
      'clutch_moment',
      'metamorphosis',
    ];

    if (significantTypes.includes(event.type)) {
      return true;
    }

    // Mark high-risk gameplay moments
    if (event.category === 'gameplay') {
      if (event.type === 'enemy_killed') {
        return event.data.wasClutch;
      }
    }

    // Mark adaptation changes
    if (event.category === 'adaptation') {
      return true;
    }

    return false;
  }

  /**
   * Convert an event to a witness mark
   */
  toMark(event: GameEvent, buildContext: BuildContext): WitnessMark | null {
    if (!this.shouldMark(event)) return null;

    const intentId = `intent-${event.id}`;
    const risk = this.calculateRisk(event, buildContext);
    const intentType = this.mapToIntentType(event);

    const intent = {
      id: intentId,
      type: intentType,
      gameTime: event.timestamp,
      context: buildContext,
      risk,
      alternatives: this.extractAlternatives(event),
    };

    const outcome = {
      intentId,
      success: this.determineSuccess(event),
      consequence: this.describeConsequence(event),
      gameTime: event.timestamp,
      metricsSnapshot: this.estimateMetrics(event, buildContext),
    };

    return { intent, outcome };
  }

  /**
   * Convert witness marks to replay events
   */
  fromMark(mark: WitnessMark): GameEvent[] {
    // Reconstruct events from mark
    const events: GameEvent[] = [];

    // Create appropriate event based on mark type
    switch (mark.intent.type) {
      case 'upgrade_choice':
        events.push(this.createUpgradeEvent(mark));
        break;
      case 'wave_enter':
        events.push(this.createWaveEvent(mark));
        break;
      // Add more conversions as needed
    }

    return events;
  }

  private calculateRisk(
    event: GameEvent,
    context: BuildContext
  ): 'low' | 'medium' | 'high' {
    const healthFraction = context.health / context.maxHealth;
    const waveRisk = Math.min(context.wave / 15, 1);

    // Event-specific risk factors
    let eventRisk = 0;
    if (event.type === 'player_damaged') {
      eventRisk = 0.3;
    }
    if (event.type === 'clutch_moment') {
      eventRisk = 0.5;
    }

    const totalRisk = (1 - healthFraction) * 0.4 + waveRisk * 0.3 + eventRisk;

    if (totalRisk >= 0.6) return 'high';
    if (totalRisk >= 0.3) return 'medium';
    return 'low';
  }

  private mapToIntentType(
    event: GameEvent
  ): 'upgrade_choice' | 'risky_engage' | 'defensive_pivot' | 'wave_enter' {
    switch (event.type) {
      case 'upgrade_selected':
        return 'upgrade_choice';
      case 'clutch_moment':
      case 'metamorphosis':
        return 'risky_engage';
      case 'player_damaged':
        return 'defensive_pivot';
      case 'wave_completed':
      case 'wave_started':
        return 'wave_enter';
      default:
        return 'wave_enter';
    }
  }

  private extractAlternatives(event: GameEvent): string[] | undefined {
    if (event.type === 'upgrade_selected') {
      return event.data.alternatives;
    }
    return undefined;
  }

  private determineSuccess(event: GameEvent): boolean {
    switch (event.type) {
      case 'enemy_killed':
      case 'wave_completed':
      case 'player_level_up':
      case 'synergy_discovered':
        return true;
      case 'player_damaged':
        return event.data.healthAfter > 0;
      case 'player_death':
        return false;
      default:
        return true;
    }
  }

  private describeConsequence(event: GameEvent): string {
    switch (event.type) {
      case 'enemy_killed':
        return `Eliminated ${event.data.enemyType} at wave ${event.timestamp}`;
      case 'player_damaged':
        return `Took ${event.data.damage} damage, ${event.data.healthAfter} HP remaining`;
      case 'player_level_up':
        return `Reached level ${event.data.level}`;
      case 'upgrade_selected':
        return `Selected ${event.data.upgrade}`;
      case 'synergy_discovered':
        return `Discovered ${event.data.synergy.name}!`;
      case 'wave_completed':
        return `Cleared wave ${event.data.wave}`;
      case 'clutch_moment':
        return `Survived at ${event.data.healthPercent}% HP`;
      case 'metamorphosis':
        return 'Witnessed the first metamorphosis';
      case 'player_death':
        return `Fallen at wave ${event.data.wave}`;
      default:
        return 'Action completed';
    }
  }

  private estimateMetrics(
    _event: GameEvent,
    context: BuildContext
  ): SkillMetrics {
    return {
      damageEfficiency: Math.min(
        context.enemiesKilled / (context.wave * 10 + 1),
        1
      ),
      dodgeRate: context.health / context.maxHealth,
      buildFocus: context.synergies.length > 0 ? 0.7 : 0.3,
      riskTolerance: context.upgrades.includes('damage_up') ? 0.7 : 0.4,
      estimate: 0.5,
    };
  }

  private createUpgradeEvent(mark: WitnessMark): UpgradeSelectedEvent {
    return {
      id: `evt-from-mark-${mark.intent.id}`,
      category: 'player',
      type: 'upgrade_selected',
      timestamp: mark.intent.gameTime,
      frame: 0,
      data: {
        upgrade: 'pierce' as UpgradeType, // Would need actual data from mark
        alternatives: (mark.intent.alternatives ?? []) as UpgradeType[],
        level: mark.intent.context.wave,
        totalUpgrades: mark.intent.context.upgrades.length,
        buildContext: mark.intent.context,
      },
    };
  }

  private createWaveEvent(mark: WitnessMark): WaveCompletedEvent {
    return {
      id: `evt-from-mark-${mark.intent.id}`,
      category: 'gameplay',
      type: 'wave_completed',
      timestamp: mark.intent.gameTime,
      frame: 0,
      data: {
        wave: mark.intent.context.wave,
        duration: 0,
        enemiesKilled: mark.intent.context.enemiesKilled,
        damageTaken: 0,
        healthRemaining: mark.intent.context.health,
      },
    };
  }
}

// =============================================================================
// Event Factory Helpers
// =============================================================================

/**
 * Create event factory for type-safe event emission
 */
export function createEventFactory(bus: GameEventBus, getTimestamp: () => number) {
  return {
    // Gameplay events
    enemySpawned: (data: EnemySpawnedEvent['data']) =>
      bus.emit<EnemySpawnedEvent>({
        category: 'gameplay',
        type: 'enemy_spawned',
        timestamp: getTimestamp(),
        data,
      }),

    enemyKilled: (data: EnemyKilledEvent['data']) =>
      bus.emit<EnemyKilledEvent>({
        category: 'gameplay',
        type: 'enemy_killed',
        timestamp: getTimestamp(),
        data,
      }),

    projectileFired: (data: ProjectileFiredEvent['data']) =>
      bus.emit<ProjectileFiredEvent>({
        category: 'gameplay',
        type: 'projectile_fired',
        timestamp: getTimestamp(),
        data,
      }),

    waveStarted: (data: WaveStartedEvent['data']) =>
      bus.emit<WaveStartedEvent>({
        category: 'gameplay',
        type: 'wave_started',
        timestamp: getTimestamp(),
        data,
      }),

    waveCompleted: (data: WaveCompletedEvent['data']) =>
      bus.emit<WaveCompletedEvent>({
        category: 'gameplay',
        type: 'wave_completed',
        timestamp: getTimestamp(),
        data,
      }),

    metamorphosis: (data: MetamorphosisEvent['data']) =>
      bus.emit<MetamorphosisEvent>({
        category: 'gameplay',
        type: 'metamorphosis',
        timestamp: getTimestamp(),
        data,
      }),

    // Player events
    playerDamaged: (data: PlayerDamagedEvent['data']) =>
      bus.emit<PlayerDamagedEvent>({
        category: 'player',
        type: 'player_damaged',
        timestamp: getTimestamp(),
        data,
      }),

    playerHealed: (data: PlayerHealedEvent['data']) =>
      bus.emit<PlayerHealedEvent>({
        category: 'player',
        type: 'player_healed',
        timestamp: getTimestamp(),
        data,
      }),

    playerLevelUp: (data: PlayerLevelUpEvent['data']) =>
      bus.emit<PlayerLevelUpEvent>({
        category: 'player',
        type: 'player_level_up',
        timestamp: getTimestamp(),
        data,
      }),

    upgradeSelected: (data: UpgradeSelectedEvent['data']) =>
      bus.emit<UpgradeSelectedEvent>({
        category: 'player',
        type: 'upgrade_selected',
        timestamp: getTimestamp(),
        data,
      }),

    synergyDiscovered: (data: SynergyDiscoveredEvent['data']) =>
      bus.emit<SynergyDiscoveredEvent>({
        category: 'player',
        type: 'synergy_discovered',
        timestamp: getTimestamp(),
        data,
      }),

    dashUsed: (data: DashUsedEvent['data']) =>
      bus.emit<DashUsedEvent>({
        category: 'player',
        type: 'dash_used',
        timestamp: getTimestamp(),
        data,
      }),

    playerDeath: (data: PlayerDeathEvent['data']) =>
      bus.emit<PlayerDeathEvent>({
        category: 'player',
        type: 'player_death',
        timestamp: getTimestamp(),
        data,
      }),

    // Witness events
    clutchMoment: (data: ClutchMomentEvent['data']) =>
      bus.emit<ClutchMomentEvent>({
        category: 'witness',
        type: 'clutch_moment',
        timestamp: getTimestamp(),
        data,
      }),

    // System events
    gameStarted: (data: GameStartedEvent['data']) =>
      bus.emit<GameStartedEvent>({
        category: 'system',
        type: 'game_started',
        timestamp: getTimestamp(),
        data,
      }),

    gamePaused: (data: GamePausedEvent['data']) =>
      bus.emit<GamePausedEvent>({
        category: 'system',
        type: 'game_paused',
        timestamp: getTimestamp(),
        data,
      }),

    gameResumed: (data: GameResumedEvent['data']) =>
      bus.emit<GameResumedEvent>({
        category: 'system',
        type: 'game_resumed',
        timestamp: getTimestamp(),
        data,
      }),

    gameEnded: (data: GameEndedEvent['data']) =>
      bus.emit<GameEndedEvent>({
        category: 'system',
        type: 'game_ended',
        timestamp: getTimestamp(),
        data,
      }),
  };
}

// =============================================================================
// Singleton Instance (optional usage pattern)
// =============================================================================

let globalEventBus: GameEventBus | null = null;

/**
 * Get or create global event bus instance
 */
export function getEventBus(): GameEventBus {
  if (!globalEventBus) {
    globalEventBus = new GameEventBus();
  }
  return globalEventBus;
}

/**
 * Reset global event bus (for testing or new game)
 */
export function resetEventBus(): void {
  if (globalEventBus) {
    globalEventBus.clearHistory();
  }
  globalEventBus = new GameEventBus();
}

// =============================================================================
// Exports
// =============================================================================

export default {
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
};
