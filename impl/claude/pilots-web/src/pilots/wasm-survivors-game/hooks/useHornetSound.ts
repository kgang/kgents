/**
 * WASM Survivors - Hornet Sound Identity React Hook
 *
 * Integrates the unique bee/hornet sonic identity with the game.
 * Works alongside useKentFugue for a complete audio experience.
 *
 * FOUR AUDIO LAYERS:
 * 1. Swarm Synthesis - Emergent bee voices from oscillators
 * 2. Horror Drone - Sub-bass tritone dread
 * 3. Heartbeat - Player's panicked heart during THE BALL
 * 4. Hive Ambience - Environmental swarm texture
 *
 * "The hornet's name is written in the music."
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  HornetSoundIdentity,
  BallPhaseType,
} from '../systems/hornet-sound-identity';
import type { Enemy, GameState, BallPhase } from '../types';

// =============================================================================
// TYPES
// =============================================================================

export interface HornetSoundConfig {
  enabled: boolean;
  swarmVolume: number;      // 0-1
  horrorVolume: number;     // 0-1
  ambienceVolume: number;   // 0-1
  heartbeatEnabled: boolean;
}

export interface UseHornetSoundReturn {
  // State
  isInitialized: boolean;
  isPlaying: boolean;
  currentPhase: BallPhaseType | null;

  // Controls
  initialize: () => Promise<boolean>;
  start: () => void;
  stop: () => void;
  update: (gameState: GameState) => void;

  // Direct triggers
  playWarningClick: () => void;
  playDeathMotif: () => void;
  playHeartbeat: (bpm: number, intensity: number) => void;

  // Configuration
  setConfig: (config: Partial<HornetSoundConfig>) => void;
}

// =============================================================================
// DEFAULT CONFIG
// =============================================================================

const DEFAULT_CONFIG: HornetSoundConfig = {
  enabled: true,
  swarmVolume: 0.6,
  horrorVolume: 0.5,
  ambienceVolume: 0.4,
  heartbeatEnabled: true,
};

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Calculate swarm coordination level from enemy states
 */
function calculateCoordinationLevel(enemies: Enemy[]): number {
  if (enemies.length === 0) return 0;

  const coordinatingCount = enemies.filter(
    e => e.coordinationState === 'coordinating' || e.coordinationState === 'ball'
  ).length;

  return coordinatingCount / enemies.length;
}

/**
 * Calculate average distance from enemies to a point
 */
function calculateAverageDistance(
  enemies: Enemy[],
  targetX: number,
  targetY: number
): number {
  if (enemies.length === 0) return 1000;

  const totalDistance = enemies.reduce((sum, enemy) => {
    const dx = enemy.position.x - targetX;
    const dy = enemy.position.y - targetY;
    return sum + Math.sqrt(dx * dx + dy * dy);
  }, 0);

  return totalDistance / enemies.length;
}

/**
 * Map game ball phase to sound system ball phase
 */
function mapBallPhase(ballPhase: BallPhase | null): BallPhaseType | null {
  if (!ballPhase) return null;
  return ballPhase.type;
}

// =============================================================================
// HOOK IMPLEMENTATION
// =============================================================================

export function useHornetSound(): UseHornetSoundReturn {
  // State
  const [isInitialized, setIsInitialized] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentPhase, setCurrentPhase] = useState<BallPhaseType | null>(null);
  const [config, setConfigState] = useState<HornetSoundConfig>(DEFAULT_CONFIG);

  // Refs
  const soundIdentityRef = useRef<HornetSoundIdentity | null>(null);
  const lastUpdateRef = useRef<number>(0);
  const updateIntervalMs = 50; // Update audio 20 times per second

  // Initialize the sound system
  const initialize = useCallback(async (): Promise<boolean> => {
    if (isInitialized) return true;

    try {
      const soundIdentity = new HornetSoundIdentity();
      await soundIdentity.initialize();
      soundIdentityRef.current = soundIdentity;
      setIsInitialized(true);
      return true;
    } catch (error) {
      console.error('[HornetSound] Failed to initialize:', error);
      return false;
    }
  }, [isInitialized]);

  // Start audio playback
  const start = useCallback(() => {
    if (!isInitialized || isPlaying) return;
    setIsPlaying(true);
  }, [isInitialized, isPlaying]);

  // Stop audio playback
  const stop = useCallback(() => {
    if (!isPlaying) return;
    setIsPlaying(false);
  }, [isPlaying]);

  // Update from game state
  const update = useCallback((gameState: GameState) => {
    if (!isInitialized || !isPlaying || !config.enabled) return;

    const now = performance.now();
    if (now - lastUpdateRef.current < updateIntervalMs) return;
    lastUpdateRef.current = now;

    const soundIdentity = soundIdentityRef.current;
    if (!soundIdentity) return;

    // Extract audio-relevant data from game state
    const enemies = gameState.enemies || [];
    const player = gameState.player;
    const ballPhase = mapBallPhase(gameState.ballPhase || null);

    // Calculate swarm metrics
    const coordinationLevel = calculateCoordinationLevel(enemies);
    const distanceToPlayer = player
      ? calculateAverageDistance(enemies, player.position.x, player.position.y)
      : 1000;

    // Calculate temperature for THE BALL
    let temperature = 0;
    if (gameState.ballPhase) {
      if (gameState.ballPhase.temperature !== undefined) {
        temperature = gameState.ballPhase.temperature / 47; // Normalize to 0-1 (47°C = lethal)
      } else if (gameState.ballPhase.progress !== undefined) {
        temperature = gameState.ballPhase.progress;
      }
    }

    // Update sound system
    soundIdentity.update({
      beeCount: enemies.length,
      coordinationLevel,
      distanceToPlayer,
      ballPhase,
      temperature,
      playerHealth: player ? player.health / player.maxHealth : 1,
    });

    // Track phase changes
    if (ballPhase !== currentPhase) {
      setCurrentPhase(ballPhase);
    }
  }, [isInitialized, isPlaying, config.enabled, currentPhase]);

  // Direct trigger: Warning click
  const playWarningClick = useCallback(() => {
    if (!soundIdentityRef.current) return;
    soundIdentityRef.current.ambience.playWarningClick();
  }, []);

  // Direct trigger: Death motif
  const playDeathMotif = useCallback(() => {
    if (!soundIdentityRef.current) return;
    soundIdentityRef.current.swarm.playKentDeathMotif();
  }, []);

  // Direct trigger: Heartbeat
  const playHeartbeat = useCallback((bpm: number, intensity: number) => {
    if (!soundIdentityRef.current || !config.heartbeatEnabled) return;
    soundIdentityRef.current.heartbeat.playBeat(bpm, intensity);
  }, [config.heartbeatEnabled]);

  // Configuration update
  const setConfig = useCallback((newConfig: Partial<HornetSoundConfig>) => {
    setConfigState(prev => ({ ...prev, ...newConfig }));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (soundIdentityRef.current) {
        soundIdentityRef.current.dispose();
        soundIdentityRef.current = null;
      }
    };
  }, []);

  return {
    isInitialized,
    isPlaying,
    currentPhase,
    initialize,
    start,
    stop,
    update,
    playWarningClick,
    playDeathMotif,
    playHeartbeat,
    setConfig,
  };
}

// =============================================================================
// INTEGRATION HELPER: Combine with Kent Fugue
// =============================================================================

/**
 * Coordination layer between HornetSound and KentFugue
 *
 * This ensures the two systems complement rather than clash:
 * - During normal play: Fugue is melodic, swarm is textural
 * - During THE BALL: Both systems converge on horror
 * - During death: Fugue plays KENT motif, swarm falls silent
 */
export interface AudioCoordinator {
  phase: 'ambient' | 'tension' | 'horror' | 'death';
  fugueIntensity: number;
  swarmIntensity: number;
  horrorIntensity: number;
}

export function calculateAudioCoordination(
  gameState: GameState
): AudioCoordinator {
  const player = gameState.player;
  const enemies = gameState.enemies || [];
  const ballPhase = gameState.ballPhase;

  // Calculate base danger level
  const healthFactor = player ? 1 - (player.health / player.maxHealth) : 0;
  const densityFactor = Math.min(1, enemies.length / 100);
  const coordinationLevel = calculateCoordinationLevel(enemies);

  // Determine phase
  let phase: AudioCoordinator['phase'] = 'ambient';
  if (ballPhase?.type === 'death') {
    phase = 'death';
  } else if (ballPhase) {
    phase = 'horror';
  } else if (healthFactor > 0.5 || coordinationLevel > 0.5) {
    phase = 'tension';
  }

  // Calculate intensities
  switch (phase) {
    case 'ambient':
      return {
        phase,
        fugueIntensity: 0.8,
        swarmIntensity: densityFactor * 0.4,
        horrorIntensity: 0,
      };

    case 'tension':
      return {
        phase,
        fugueIntensity: 0.6,
        swarmIntensity: densityFactor * 0.6,
        horrorIntensity: (healthFactor + coordinationLevel) * 0.3,
      };

    case 'horror':
      return {
        phase,
        fugueIntensity: 0.3,  // Fugue quiets during THE BALL
        swarmIntensity: 0.9,
        horrorIntensity: 0.8,
      };

    case 'death':
      return {
        phase,
        fugueIntensity: 1.0,  // KENT death motif plays loud
        swarmIntensity: 0.1,  // Swarm fades
        horrorIntensity: 0.5,
      };
  }
}

export default useHornetSound;
