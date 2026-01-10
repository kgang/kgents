/**
 * WASM Survivors - Emergent Audio Hook
 *
 * React hook for integrating the emergent generative audio system
 * with game components. Provides a clean interface for all audio events.
 *
 * USAGE:
 * ```tsx
 * const audio = useEmergentAudio();
 *
 * // Start on user interaction
 * useEffect(() => {
 *   const handleClick = () => audio.start();
 *   window.addEventListener('click', handleClick, { once: true });
 *   return () => window.removeEventListener('click', handleClick);
 * }, [audio]);
 *
 * // Update each frame
 * useEffect(() => {
 *   audio.update(gameState);
 * }, [gameState, audio]);
 *
 * // Dispatch events
 * audio.onKill(position, comboCount);
 * audio.onDamage(amount);
 * audio.onLevelUp();
 * ```
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  EmergentAudioOrchestrator,
  getEmergentAudioOrchestrator,
  startEmergentAudio,
  stopEmergentAudio,
  type GameAudioState,
  type GamePhase,
  type Vector2,
} from '../systems/emergent-audio';

export interface UseEmergentAudioResult {
  /** Start the emergent audio system (call on user interaction) */
  start: () => Promise<boolean>;

  /** Stop and cleanup the audio system */
  stop: () => void;

  /** Update with current game state (call each frame) */
  update: (state: GameAudioState) => void;

  /** Dispatch kill event */
  onKill: (position: Vector2, comboCount?: number) => void;

  /** Dispatch damage event */
  onDamage: (amount: number) => void;

  /** Dispatch level up event */
  onLevelUp: () => void;

  /** Dispatch ball phase change */
  onBallPhase: (phase: GameAudioState['ballPhase']) => void;

  /** Play spatial enemy sound */
  onEnemySound: (position: Vector2, type?: 'buzz' | 'alert') => void;

  /** Set master volume (0-1) */
  setVolume: (volume: number) => void;

  /** Whether the audio system is running */
  isRunning: boolean;

  /** Current game phase as detected by audio */
  currentPhase: GamePhase;

  /** Current intensity level (0-1) */
  intensity: number;

  /** Current harmonic tension (0-1) */
  harmonicTension: number;
}

/**
 * Hook to use the emergent audio system in React components.
 *
 * The system must be started after a user interaction (click/keypress)
 * due to browser autoplay policies.
 *
 * "Audio is not just feedback - it's a layer of the game itself."
 */
export function useEmergentAudio(): UseEmergentAudioResult {
  const orchestratorRef = useRef<EmergentAudioOrchestrator | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [currentPhase, setCurrentPhase] = useState<GamePhase>('exploration');
  const [intensity, setIntensity] = useState(0);
  const [harmonicTension, setHarmonicTension] = useState(0);

  // Initialize orchestrator reference
  useEffect(() => {
    orchestratorRef.current = getEmergentAudioOrchestrator();

    return () => {
      // Cleanup on unmount
      stopEmergentAudio();
    };
  }, []);

  // Start the audio system
  const start = useCallback(async (): Promise<boolean> => {
    const success = await startEmergentAudio();
    setIsRunning(success);
    return success;
  }, []);

  // Stop the audio system
  const stop = useCallback((): void => {
    stopEmergentAudio();
    setIsRunning(false);
  }, []);

  // Update with game state
  const update = useCallback((state: GameAudioState): void => {
    const orchestrator = orchestratorRef.current;
    if (!orchestrator || !orchestrator.isActive()) return;

    orchestrator.update(state);

    // Update exposed state only if values changed (prevent infinite re-render loop)
    const newPhase = orchestrator.getCurrentPhase();
    const newIntensity = orchestrator.getIntensity();
    const newTension = orchestrator.getHarmonicTension();

    setCurrentPhase(prev => prev !== newPhase ? newPhase : prev);
    setIntensity(prev => Math.abs(prev - newIntensity) > 0.01 ? newIntensity : prev);
    setHarmonicTension(prev => Math.abs(prev - newTension) > 0.01 ? newTension : prev);
  }, []);

  // Event dispatchers
  const onKill = useCallback((position: Vector2, comboCount: number = 1): void => {
    orchestratorRef.current?.onKill(position, comboCount);
  }, []);

  const onDamage = useCallback((amount: number): void => {
    orchestratorRef.current?.onDamage(amount);
  }, []);

  const onLevelUp = useCallback((): void => {
    orchestratorRef.current?.onLevelUp();
  }, []);

  const onBallPhase = useCallback((phase: GameAudioState['ballPhase']): void => {
    orchestratorRef.current?.onBallPhase(phase);
  }, []);

  const onEnemySound = useCallback((position: Vector2, type: 'buzz' | 'alert' = 'buzz'): void => {
    orchestratorRef.current?.onEnemySound(position, type);
  }, []);

  const setVolume = useCallback((volume: number): void => {
    orchestratorRef.current?.setMasterVolume(volume);
  }, []);

  return {
    start,
    stop,
    update,
    onKill,
    onDamage,
    onLevelUp,
    onBallPhase,
    onEnemySound,
    setVolume,
    isRunning,
    currentPhase,
    intensity,
    harmonicTension,
  };
}

// =============================================================================
// HELPER: Convert GameState to GameAudioState
// =============================================================================

import type { GameState } from '../types';

/**
 * Convert full game state to audio-relevant state.
 * Use this in your game loop to feed the audio system.
 */
export function gameStateToAudioState(
  gameState: GameState,
  recentKills: number = 0,
  comboCount: number = 0
): GameAudioState {
  // Map ball phase - gameState.ballPhase is BallPhase | null
  let ballPhase: GameAudioState['ballPhase'] = 'none';
  if (gameState.ballPhase) {
    const phase = gameState.ballPhase.type;
    if (phase === 'forming') ballPhase = 'forming';
    else if (phase === 'sphere') ballPhase = 'sphere';
    else if (phase === 'silence') ballPhase = 'silence';
    else if (phase === 'constrict') ballPhase = 'constrict';
    else if (phase === 'death') ballPhase = 'death';
  }

  // Determine intensity-based phase
  const healthFraction = gameState.player.health / gameState.player.maxHealth;
  const enemyCount = gameState.enemies.length;

  let phase: GamePhase = 'exploration';
  if (ballPhase === 'death') {
    phase = 'death';
  } else if (ballPhase !== 'none' || healthFraction < 0.3) {
    phase = 'crisis';
  } else if (enemyCount > 20 || recentKills > 5) {
    phase = 'combat';
  }

  return {
    phase,
    intensity: 0, // Computed by orchestrator
    playerHealth: healthFraction,
    enemyCount,
    waveNumber: gameState.wave,
    ballPhase,
    playerPosition: gameState.player.position,
    recentKills,
    comboCount,
  };
}

export default useEmergentAudio;
