/**
 * WASM Survivors - Sound Engine Hook (ASMR Audio Transformation)
 *
 * React hook for integrating the ASMR audio system into game components.
 * Handles initialization and provides memoized sound triggers.
 *
 * Run 036 TRANSFORMATION:
 * - Replaced playKill() with layered 3-sound ASMR crunch
 * - Added TRUE SILENCE support during THE BALL formation
 * - Added spatial audio based on enemy position (stereo panning)
 * - Multi-kill escalation with pitch/volume ramping
 * - Graze sound on near-miss events
 *
 * "Every kill should sound like biting into a perfect apple."
 *
 * @see systems/audio.ts
 */

import { useCallback, useEffect, useRef } from 'react';
import type { EnemyType, KillTier, BallPhaseType, Mood, Vector2 } from '../types';
import {
  initAudio,
  resumeAudio,
  setMasterVolume,
  setSpatialConfig,
  playLayeredKillSound,
  playDamageSound,
  playEnemyHitSound,
  playDashSound,
  playXPSound,
  playLevelUpSound,
  playGrazeSound,
  playBallPhaseAudio,
  updateCoordinationBuzz,
  stopBuzz,
  stopAmbient,
  stopAllAudio,
  setMoodAmbient,
  playDeathSound,
  playHoneyDripSound,
  playFreezeFrameSound,
  getAudioState,
  resetAudioSystem,
  // THE BALL audio sequencing (Run 049: Audio Integration)
  fadeOutAllAudio,
  playBassDropSound,
  startIntenseMusic,
  fadeToNormalMusic,
  // Debug exports
  DEBUG_GET_AUDIO_STATE,
  DEBUG_GET_AUDIO_LEVEL,
  DEBUG_GET_AUDIO_LOG,
  DEBUG_CLEAR_AUDIO_LOG,
} from '../systems/audio';
// Legacy sound engine for non-ASMR sounds
import { getSoundEngine, type SoundEngine, type SoundId, type SoundOptions } from '../systems/sound';

export interface UseSoundEngineResult {
  /** Play a sound effect (legacy interface) */
  play: (sound: SoundId, options?: SoundOptions) => void;
  /**
   * Play LAYERED kill sound with ASMR crunch (Run 036 Transformation)
   * @param enemyType - The bee type for sound configuration
   * @param tier - Kill tier (single/multi/massacre) for audio escalation
   * @param comboCount - Consecutive kill count for pitch/volume ramping
   * @param position - Enemy position for spatial audio (stereo panning)
   */
  playKill: (
    enemyType: EnemyType,
    tier?: KillTier,
    comboCount?: number,
    position?: Vector2
  ) => void;
  /**
   * Play enemy hit sound (player damages enemy, not a kill)
   * @param damage - Amount of damage dealt (affects volume)
   * @param position - Enemy position for spatial audio
   */
  playEnemyHit: (damage?: number, position?: Vector2) => void;
  /** Play damage sound (player takes damage) */
  playDamage: () => void;
  /** Play level up fanfare */
  playLevelUp: () => void;
  /** Play synergy discovery chime */
  playSynergy: () => void;
  /** Play wave complete horn */
  playWave: () => void;
  /** Play dash whoosh */
  playDash: () => void;
  /** Play XP collection sound */
  playXP: () => void;
  /**
   * Play graze sound (near-miss reward)
   * @param chainCount - Number of consecutive grazes for pitch escalation
   */
  playGraze: (chainCount?: number) => void;
  /**
   * Set TRUE SILENCE for THE BALL formation
   * @param enabled - When true, stops ALL audio for maximum dread
   */
  setTrueSilence: (enabled: boolean) => void;
  /**
   * Update spatial audio config (call each frame with player position)
   */
  updateSpatialConfig: (playerPosition: Vector2, listenerRange?: number) => void;
  /**
   * Play THE BALL phase audio
   * @param phase - Ball phase type (forming/sphere/silence/constrict/death)
   */
  playBallPhase: (phase: BallPhaseType) => void;
  /**
   * Update coordination buzz volume (for THE BALL formation)
   * @param level - Coordination level (0-10)
   */
  updateBuzz: (level: number) => void;
  /**
   * Set mood-based ambient audio
   */
  setMood: (mood: Mood) => void;
  /** Play death sound (dignified, not punishing) */
  playDeath: () => void;
  /** Play honey drip sound (propolis death effect) */
  playHoneyDrip: () => void;
  /** Play freeze frame sound (time-stop impact) */
  playFreezeFrame: (type: 'significant' | 'multi' | 'critical' | 'massacre') => void;
  // =========================================================================
  // THE BALL Audio Sequencing (Run 049: Audio Integration)
  // =========================================================================
  /**
   * Fade out all audio (for forming phase transition to silence)
   * @param durationMs - Fade duration in milliseconds (default: 500ms)
   */
  fadeOutAudio: (durationMs?: number) => void;
  /**
   * Play bass drop sound - THE BALL's signature "THOOM"
   * Used at constrict phase start after silence for maximum impact
   */
  playBassDrop: () => void;
  /**
   * Start intense music (for constrict phase)
   * Uses maximum coordination buzz intensity
   */
  startIntense: () => void;
  /**
   * Fade back to normal music (for dissipating phase)
   * @param durationMs - Fade duration in milliseconds (default: 1000ms)
   */
  fadeToNormal: (durationMs?: number) => void;
  /**
   * Start low health heartbeat loop
   * Plays heartbeat sound at ~1.5 second intervals while active.
   * Call when health drops below 30% threshold.
   */
  startHeartbeatLoop: () => void;
  /**
   * Stop low health heartbeat loop
   * Call when health goes above 30% threshold or player dies.
   */
  stopHeartbeatLoop: () => void;
  /** Check if heartbeat loop is currently playing */
  isHeartbeatPlaying: boolean;
  /** Mute all sounds */
  mute: () => void;
  /** Unmute sounds */
  unmute: () => void;
  /** Check if muted */
  isMuted: boolean;
  /** Check if in TRUE SILENCE mode */
  isSilent: boolean;
  /**
   * Reset the entire audio system.
   * Call before starting a new game to prevent audio carry-over.
   * Fixes the "ambient bee buzzing carry-over" bug.
   */
  resetAudio: () => void;
}

/**
 * Hook to use the ASMR audio system in React components
 *
 * Run 036 TRANSFORMATION: Now uses layered audio.ts for ASMR-quality sounds.
 * Legacy sound.ts is still available for non-ASMR sounds.
 *
 * Initialization happens on first user interaction (autoplay policy).
 *
 * "Every kill should sound like biting into a perfect apple."
 */
// Low health heartbeat interval in milliseconds (~1.5 seconds between lub-dub)
const HEARTBEAT_INTERVAL_MS = 1500;
// Volume for heartbeat (noticeable but not overwhelming)
const HEARTBEAT_VOLUME = 0.5;

export function useSoundEngine(): UseSoundEngineResult {
  // Legacy engine for sounds not yet in audio.ts
  const legacyEngineRef = useRef<SoundEngine | null>(null);
  const mutedRef = useRef<boolean>(false);
  const silentRef = useRef<boolean>(false);
  const audioInitializedRef = useRef<boolean>(false);

  // Low health heartbeat loop state
  const heartbeatIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const heartbeatPlayingRef = useRef<boolean>(false);

  // Initialize both audio systems on mount
  useEffect(() => {
    // Legacy engine for backward compatibility
    legacyEngineRef.current = getSoundEngine();

    // Initialize ASMR audio system
    audioInitializedRef.current = initAudio();

    // Expose debug API for Playwright testing
    if (typeof window !== 'undefined') {
      (window as unknown as Record<string, unknown>).DEBUG_GET_AUDIO_STATE = DEBUG_GET_AUDIO_STATE;
      (window as unknown as Record<string, unknown>).DEBUG_GET_AUDIO_LEVEL = DEBUG_GET_AUDIO_LEVEL;
      (window as unknown as Record<string, unknown>).DEBUG_GET_AUDIO_LOG = DEBUG_GET_AUDIO_LOG;
      (window as unknown as Record<string, unknown>).DEBUG_CLEAR_AUDIO_LOG = DEBUG_CLEAR_AUDIO_LOG;
    }

    // Cleanup
    return () => {
      stopAllAudio();
      // Clean up heartbeat interval if running
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
        heartbeatPlayingRef.current = false;
      }
    };
  }, []);

  // Resume audio on user interaction (autoplay policy)
  useEffect(() => {
    const handleUserInteraction = () => {
      if (audioInitializedRef.current) {
        resumeAudio();
      }
    };

    window.addEventListener('click', handleUserInteraction, { once: true });
    window.addEventListener('keydown', handleUserInteraction, { once: true });

    return () => {
      window.removeEventListener('click', handleUserInteraction);
      window.removeEventListener('keydown', handleUserInteraction);
    };
  }, []);

  // Legacy play for sounds not in audio.ts
  const play = useCallback((sound: SoundId, options?: SoundOptions) => {
    if (mutedRef.current || silentRef.current) return;
    legacyEngineRef.current?.play(sound, options);
  }, []);

  /**
   * ASMR Kill Sound (Run 036 Transformation)
   *
   * THREE layers create ASMR satisfaction:
   * - Layer 1: CRUNCH (initial impact, noise-based)
   * - Layer 2: SNAP/SHELL (high-freq attack transient)
   * - Layer 3: DECAY/THUD (low-freq sustain)
   *
   * Plus: spatial audio, multi-kill escalation, pitch variation
   */
  const playKill = useCallback((
    enemyType: EnemyType,
    tier: KillTier = 'single',
    comboCount: number = 1,
    position?: Vector2
  ) => {
    if (mutedRef.current || silentRef.current) return;
    playLayeredKillSound(enemyType, tier, comboCount, position);
  }, []);

  const playDamage = useCallback(() => {
    if (mutedRef.current || silentRef.current) return;
    playDamageSound();
  }, []);

  /**
   * Enemy Hit Sound (non-lethal damage to enemy)
   * Satisfying impact with volume scaled by damage.
   */
  const playEnemyHit = useCallback((damage: number = 10, position?: Vector2) => {
    if (mutedRef.current || silentRef.current) return;
    playEnemyHitSound(damage, position);
  }, []);

  const playLevelUp = useCallback(() => {
    if (mutedRef.current || silentRef.current) return;
    playLevelUpSound();
  }, []);

  // Legacy synergy sound (not yet in audio.ts)
  const playSynergy = useCallback(() => {
    if (mutedRef.current || silentRef.current) return;
    legacyEngineRef.current?.play('synergy');
  }, []);

  // Legacy wave sound (not yet in audio.ts)
  const playWave = useCallback(() => {
    if (mutedRef.current || silentRef.current) return;
    legacyEngineRef.current?.play('wave');
  }, []);

  const playDash = useCallback(() => {
    if (mutedRef.current || silentRef.current) return;
    playDashSound();
  }, []);

  const playXP = useCallback(() => {
    if (mutedRef.current || silentRef.current) return;
    playXPSound();
  }, []);

  /**
   * Graze sound (near-miss reward)
   * Pitch increases with chain count for satisfying escalation.
   */
  const playGraze = useCallback((chainCount: number = 1) => {
    if (mutedRef.current || silentRef.current) return;
    playGrazeSound(chainCount);
  }, []);

  /**
   * TRUE SILENCE for THE BALL formation
   *
   * "Silence should be terrifying."
   *
   * When enabled, stops ALL audio - no ambient, no buzz, nothing.
   * The absence of sound creates physical dread.
   */
  const setTrueSilence = useCallback((enabled: boolean) => {
    silentRef.current = enabled;
    if (enabled) {
      stopBuzz();
      stopAmbient();
    }
  }, []);

  /**
   * Update spatial audio config
   * Call each frame with player position for stereo panning.
   */
  const updateSpatialConfig = useCallback((playerPosition: Vector2, listenerRange: number = 600) => {
    setSpatialConfig({ playerPosition, listenerRange });
  }, []);

  /**
   * THE BALL phase audio
   * Each phase has distinct audio treatment:
   * - forming: buzz crescendo
   * - sphere: peak buzz
   * - silence: TRUE SILENCE (dread)
   * - constrict: bass drop + cooking crackle
   * - death: sizzle + respect pulse
   */
  const playBallPhase = useCallback((phase: BallPhaseType) => {
    if (mutedRef.current) return;
    playBallPhaseAudio(phase);
    // TRUE SILENCE is handled inside playBallPhaseAudio for 'silence' phase
  }, []);

  /**
   * Update coordination buzz (for THE BALL formation)
   */
  const updateBuzz = useCallback((level: number) => {
    if (mutedRef.current || silentRef.current) return;
    updateCoordinationBuzz(level);
  }, []);

  /**
   * Set mood-based ambient audio
   */
  const setMood = useCallback((mood: Mood) => {
    if (mutedRef.current || silentRef.current) return;
    setMoodAmbient(mood);
  }, []);

  /**
   * Death sound (dignified, not punishing)
   */
  const playDeath = useCallback(() => {
    if (mutedRef.current) return; // Play even in silence (death overrides)
    playDeathSound();
  }, []);

  /**
   * Honey drip sound (propolis death effect)
   */
  const playHoneyDrip = useCallback(() => {
    if (mutedRef.current || silentRef.current) return;
    playHoneyDripSound();
  }, []);

  /**
   * Freeze frame sound (time-stop impact)
   */
  const playFreezeFrame = useCallback((type: 'significant' | 'multi' | 'critical' | 'massacre') => {
    if (mutedRef.current || silentRef.current) return;
    playFreezeFrameSound(type);
  }, []);

  // ===========================================================================
  // THE BALL Audio Sequencing (Run 049: Audio Integration)
  // ===========================================================================

  /**
   * Fade out all audio for THE BALL forming phase.
   * Creates anticipation before the terrifying silence.
   */
  const fadeOutAudio = useCallback((durationMs: number = 500) => {
    if (mutedRef.current) return;
    fadeOutAllAudio(durationMs);
    silentRef.current = true;  // Mark as silent for other sounds
  }, []);

  /**
   * Play bass drop sound - THE BALL's signature "THOOM"
   * Hits hard after 3 seconds of complete silence.
   */
  const playBassDrop = useCallback(() => {
    if (mutedRef.current) return;
    silentRef.current = false;  // End silence mode
    playBassDropSound();
  }, []);

  /**
   * Start intense music for constrict phase.
   * Maximum coordination buzz - temperature rising, danger escalating.
   */
  const startIntense = useCallback(() => {
    if (mutedRef.current) return;
    silentRef.current = false;  // End silence mode
    startIntenseMusic();
  }, []);

  /**
   * Fade back to normal music when THE BALL dissipates.
   * Tension release - they survived (or escaped).
   */
  const fadeToNormal = useCallback((durationMs: number = 1000) => {
    if (mutedRef.current) return;
    silentRef.current = false;
    fadeToNormalMusic(durationMs);
  }, []);

  /**
   * Start low health heartbeat loop
   *
   * Plays a heartbeat sound every ~1.5 seconds to warn the player they're in danger.
   * The heartbeat uses the legacy sound engine's 'heartbeat' sound which produces
   * a "lub-dub" pattern with minor 2nd unease.
   *
   * Call when health drops below 30% threshold.
   */
  const startHeartbeatLoop = useCallback(() => {
    // Don't start if already playing, muted, or in silence mode
    if (heartbeatPlayingRef.current || mutedRef.current || silentRef.current) return;

    // Play first heartbeat immediately
    legacyEngineRef.current?.play('heartbeat', { volume: HEARTBEAT_VOLUME });

    // Set up interval for subsequent heartbeats
    heartbeatIntervalRef.current = setInterval(() => {
      // Check conditions each beat (mute/silence could change)
      if (mutedRef.current || silentRef.current) {
        // Stop the loop if muted/silenced
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
          heartbeatIntervalRef.current = null;
          heartbeatPlayingRef.current = false;
        }
        return;
      }
      legacyEngineRef.current?.play('heartbeat', { volume: HEARTBEAT_VOLUME });
    }, HEARTBEAT_INTERVAL_MS);

    heartbeatPlayingRef.current = true;
  }, []);

  /**
   * Stop low health heartbeat loop
   *
   * Call when health goes above 30% threshold or player dies.
   */
  const stopHeartbeatLoop = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
    heartbeatPlayingRef.current = false;
  }, []);

  const mute = useCallback(() => {
    legacyEngineRef.current?.mute();
    setMasterVolume(0);
    mutedRef.current = true;
  }, []);

  const unmute = useCallback(() => {
    legacyEngineRef.current?.unmute();
    setMasterVolume(0.5);
    mutedRef.current = false;
  }, []);

  // Reset the entire audio system (fixes bee buzz carry-over bug)
  const resetAudio = useCallback(() => {
    resetAudioSystem();
  }, []);

  return {
    play,
    playKill,
    playEnemyHit,
    playDamage,
    playLevelUp,
    playSynergy,
    playWave,
    playDash,
    playXP,
    playGraze,
    setTrueSilence,
    updateSpatialConfig,
    playBallPhase,
    updateBuzz,
    setMood,
    playDeath,
    playHoneyDrip,
    playFreezeFrame,
    // THE BALL audio sequencing (Run 049)
    fadeOutAudio,
    playBassDrop,
    startIntense,
    fadeToNormal,
    startHeartbeatLoop,
    stopHeartbeatLoop,
    isHeartbeatPlaying: heartbeatPlayingRef.current,
    mute,
    unmute,
    isMuted: mutedRef.current,
    isSilent: getAudioState().isSilent,
    resetAudio,
  };
}

export default useSoundEngine;
