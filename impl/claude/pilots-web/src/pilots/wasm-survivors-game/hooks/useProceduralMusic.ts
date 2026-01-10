/**
 * WASM Survivors - Procedural Music Hook
 *
 * React hook for the Markov-driven fugue system.
 * Provides real-time counterpoint in C# minor based on game state.
 *
 * USAGE:
 * ```tsx
 * const music = useProceduralMusic();
 *
 * // Start on user interaction (required for Web Audio API)
 * const handleStart = () => music.start();
 *
 * // Update each frame with game state
 * useEffect(() => {
 *   music.updateFromGameState({
 *     playerHealth,
 *     enemyCount,
 *     waveNumber,
 *     recentKills,
 *     comboCount,
 *     ballPhase,
 *   });
 * }, [gameState]);
 *
 * // Manual hyperparameter control
 * music.setIntensity(0.8);
 * music.setTension(0.6);
 * ```
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  ProceduralFugueEngine,
  getProceduralFugueEngine,
  startProceduralFugue,
  stopProceduralFugue,
  gameStateToHyperparameters,
  type MusicHyperparameters,
  type MusicPhase,
  type FugueState,
} from '../systems/procedural-music';

export interface GameMusicState {
  playerHealth: number;      // 0-1
  enemyCount: number;
  waveNumber: number;
  recentKills: number;
  comboCount: number;
  ballPhase: 'none' | 'forming' | 'sphere' | 'silence' | 'constrict' | 'death';
}

export interface UseProceduralMusicResult {
  /** Start the procedural music system (requires user interaction) */
  start: () => Promise<boolean>;

  /** Stop and cleanup the music system */
  stop: () => void;

  /** Update from full game state (auto-computes hyperparameters) */
  updateFromGameState: (state: GameMusicState) => void;

  /** Direct hyperparameter control */
  setHyperparameters: (params: Partial<MusicHyperparameters>) => void;

  /** Set individual parameters */
  setIntensity: (value: number) => void;
  setTension: (value: number) => void;
  setMomentum: (value: number) => void;
  setVoiceDensity: (value: number) => void;
  setChaos: (value: number) => void;

  /** Set master volume (0-1) */
  setVolume: (volume: number) => void;

  /** Whether the music system is running */
  isRunning: boolean;

  /** Current music phase */
  currentPhase: MusicPhase;

  /** Current hyperparameters */
  hyperparameters: MusicHyperparameters;

  /** Full fugue state for debugging */
  fugueState: FugueState | null;
}

/**
 * Hook to use the procedural fugue music system in React components.
 */
export function useProceduralMusic(): UseProceduralMusicResult {
  const engineRef = useRef<ProceduralFugueEngine | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [currentPhase, setCurrentPhase] = useState<MusicPhase>('silence');
  const [hyperparameters, setHyperparametersState] = useState<MusicHyperparameters>({
    intensity: 0.3,
    tension: 0.2,
    momentum: 0.4,
    voiceDensity: 0.3,
    registralSpread: 0.5,
    ornamentation: 0.2,
    chaosLevel: 0.1,
  });
  const [fugueState, setFugueState] = useState<FugueState | null>(null);

  // Animation frame for continuous updates
  const frameRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(0);

  // Initialize engine reference
  useEffect(() => {
    engineRef.current = getProceduralFugueEngine();

    return () => {
      // Cleanup on unmount
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
      stopProceduralFugue();
    };
  }, []);

  // Animation loop for updating the fugue engine
  const updateLoop = useCallback((time: number) => {
    if (!engineRef.current?.isActive()) return;

    const deltaTime = lastTimeRef.current ? (time - lastTimeRef.current) / 1000 : 0.016;
    lastTimeRef.current = time;

    // Update the fugue engine
    engineRef.current.update(deltaTime);

    // Update state for React (compare before setting to prevent infinite re-render)
    const state = engineRef.current.getState();
    setCurrentPhase(prev => prev !== state.phase ? state.phase : prev);
    setFugueState(prev => prev !== state ? state : prev);

    // Continue loop
    frameRef.current = requestAnimationFrame(updateLoop);
  }, []);

  // Start the music system
  const start = useCallback(async (): Promise<boolean> => {
    const success = await startProceduralFugue();
    setIsRunning(success);

    if (success) {
      lastTimeRef.current = 0;
      frameRef.current = requestAnimationFrame(updateLoop);
    }

    return success;
  }, [updateLoop]);

  // Stop the music system
  const stop = useCallback((): void => {
    if (frameRef.current) {
      cancelAnimationFrame(frameRef.current);
      frameRef.current = 0;
    }
    stopProceduralFugue();
    setIsRunning(false);
  }, []);

  // Update from game state
  const updateFromGameState = useCallback((state: GameMusicState): void => {
    const engine = engineRef.current;
    if (!engine || !engine.isActive()) return;

    const params = gameStateToHyperparameters(
      state.playerHealth,
      state.enemyCount,
      state.waveNumber,
      state.recentKills,
      state.comboCount,
      state.ballPhase
    );

    engine.setHyperparameters(params);
    setHyperparametersState(params);
  }, []);

  // Direct hyperparameter control
  const setHyperparameters = useCallback((params: Partial<MusicHyperparameters>): void => {
    const engine = engineRef.current;
    if (!engine) return;

    engine.setHyperparameters(params);
    setHyperparametersState(prev => ({ ...prev, ...params }));
  }, []);

  // Individual parameter setters
  const setIntensity = useCallback((value: number): void => {
    setHyperparameters({ intensity: Math.max(0, Math.min(1, value)) });
  }, [setHyperparameters]);

  const setTension = useCallback((value: number): void => {
    setHyperparameters({ tension: Math.max(0, Math.min(1, value)) });
  }, [setHyperparameters]);

  const setMomentum = useCallback((value: number): void => {
    setHyperparameters({ momentum: Math.max(0, Math.min(1, value)) });
  }, [setHyperparameters]);

  const setVoiceDensity = useCallback((value: number): void => {
    setHyperparameters({ voiceDensity: Math.max(0, Math.min(1, value)) });
  }, [setHyperparameters]);

  const setChaos = useCallback((value: number): void => {
    setHyperparameters({ chaosLevel: Math.max(0, Math.min(1, value)) });
  }, [setHyperparameters]);

  // Volume control
  const setVolume = useCallback((volume: number): void => {
    engineRef.current?.setVolume(volume);
  }, []);

  return {
    start,
    stop,
    updateFromGameState,
    setHyperparameters,
    setIntensity,
    setTension,
    setMomentum,
    setVoiceDensity,
    setChaos,
    setVolume,
    isRunning,
    currentPhase,
    hyperparameters,
    fugueState,
  };
}

export default useProceduralMusic;
