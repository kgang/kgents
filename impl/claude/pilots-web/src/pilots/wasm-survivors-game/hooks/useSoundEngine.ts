/**
 * WASM Survivors - Sound Engine Hook
 *
 * React hook for integrating the sound engine into game components.
 * Handles initialization and provides memoized sound triggers.
 *
 * @see systems/sound.ts
 */

import { useCallback, useEffect, useRef } from 'react';
import { getSoundEngine, type SoundEngine, type SoundId, type SoundOptions } from '../systems/sound';

export interface UseSoundEngineResult {
  /** Play a sound effect */
  play: (sound: SoundId, options?: SoundOptions) => void;
  /** Play kill sound with pitch variation based on enemy type (DD-24: added spitter, DD-030-4: added colossal_tide) */
  playKill: (enemyType: 'basic' | 'fast' | 'tank' | 'boss' | 'spitter' | 'colossal_tide') => void;
  /** Play damage sound */
  playDamage: () => void;
  /** Play level up fanfare */
  playLevelUp: () => void;
  /** Play synergy discovery chime */
  playSynergy: () => void;
  /** Play wave complete horn */
  playWave: () => void;
  /** Play dash whoosh */
  playDash: () => void;
  /** Mute all sounds */
  mute: () => void;
  /** Unmute sounds */
  unmute: () => void;
  /** Check if muted */
  isMuted: boolean;
}

/**
 * Hook to use the sound engine in React components
 *
 * The sound engine is lazily initialized on first sound play
 * (requires user interaction due to autoplay policies).
 */
export function useSoundEngine(): UseSoundEngineResult {
  const engineRef = useRef<SoundEngine | null>(null);
  const mutedRef = useRef<boolean>(false);

  // Initialize engine ref on mount
  useEffect(() => {
    engineRef.current = getSoundEngine();
  }, []);

  const play = useCallback((sound: SoundId, options?: SoundOptions) => {
    engineRef.current?.play(sound, options);
  }, []);

  const playKill = useCallback((enemyType: 'basic' | 'fast' | 'tank' | 'boss' | 'spitter' | 'colossal_tide') => {
    // Vary pitch based on enemy type for variety (DD-24: added spitter, DD-030-4: added colossal_tide)
    const pitchMap: Record<string, number> = {
      basic: 1.0,
      fast: 1.2,
      tank: 0.7,
      boss: 0.5,
      spitter: 1.1,
      colossal_tide: 0.4,  // Very deep rumble for THE TIDE
    };
    const volumeMap: Record<string, number> = {
      basic: 0.8,
      fast: 0.7,
      tank: 1.0,
      boss: 1.0,
      spitter: 0.9,
      colossal_tide: 1.0,  // Full volume for THE TIDE death
    };
    engineRef.current?.play('kill', {
      pitch: pitchMap[enemyType],
      volume: volumeMap[enemyType],
    });
  }, []);

  const playDamage = useCallback(() => {
    engineRef.current?.play('damage');
  }, []);

  const playLevelUp = useCallback(() => {
    engineRef.current?.play('levelup');
  }, []);

  const playSynergy = useCallback(() => {
    engineRef.current?.play('synergy');
  }, []);

  const playWave = useCallback(() => {
    engineRef.current?.play('wave');
  }, []);

  const playDash = useCallback(() => {
    engineRef.current?.play('dash');
  }, []);

  const mute = useCallback(() => {
    engineRef.current?.mute();
    mutedRef.current = true;
  }, []);

  const unmute = useCallback(() => {
    engineRef.current?.unmute();
    mutedRef.current = false;
  }, []);

  return {
    play,
    playKill,
    playDamage,
    playLevelUp,
    playSynergy,
    playWave,
    playDash,
    mute,
    unmute,
    isMuted: mutedRef.current,
  };
}

export default useSoundEngine;
