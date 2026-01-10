/**
 * useFugueEngine - React Hook for Procedural Fugue Audio
 *
 * Integrates the fugue generation system with the game loop.
 * Manages voice entries, stretto triggers, and phase transitions
 * based on game state.
 *
 * "The fugue responds to the game. The game becomes music."
 *
 * USAGE:
 * ```tsx
 * const { isActive, setPhase, triggerKill } = useFugueEngine({
 *   enabled: true,
 *   masterVolume: 0.5,
 * });
 *
 * // In game loop:
 * if (killHappened) {
 *   triggerKill(comboCount);
 * }
 * ```
 */

import { useRef, useCallback, useEffect } from 'react';
import type { GamePhaseType, FugueState, FugueNote } from '../systems/fugue';
import {
  createFugueState,
  updateFugueState,
  setFuguePhase,
  initFugueAudio,
  triggerStretto,
  playMarimbaNote,
  generateSubject,
  PHASE_CONFIGS,
  MINOR_SCALE_DEGREES,
  getScaleFrequency,
  snapToScale,
  playFugueClimaxChord,
} from '../systems/fugue';

// =============================================================================
// TYPES
// =============================================================================

export interface FugueEngineConfig {
  enabled: boolean;
  masterVolume: number;
  initialPhase?: GamePhaseType;
}

export interface FugueEngineState {
  isActive: boolean;
  currentPhase: GamePhaseType;
  voicesActive: number;
  currentBar: number;
  inStretto: boolean;
}

export interface FugueEngineAPI {
  // State
  state: FugueEngineState;

  // Controls
  start: () => void;
  stop: () => void;
  setPhase: (phase: GamePhaseType) => void;

  // Game event triggers
  triggerKill: (comboCount: number) => void;
  triggerWaveStart: (waveNumber: number) => void;
  triggerWaveEnd: () => void;
  triggerComboMilestone: (milestone: number) => void;
  triggerBallForming: () => void;
  triggerBallComplete: () => void;
  triggerDeath: () => void;

  // Update (call each frame)
  update: (deltaTime: number, enemyCount: number) => void;
}

// =============================================================================
// CONSTANTS
// =============================================================================

/**
 * Combo milestones that trigger musical events
 */
const COMBO_MILESTONES = [5, 10, 20, 50, 100];

/**
 * Kill to voice mapping
 * Different kill counts trigger different voice responses
 * @internal Reserved for future voice system integration
 */
const _KILL_VOICE_MAP = {
  single: 'tenor',    // Single kill - melodic response
  double: 'alto',     // Double kill - harmonic addition
  triple: 'soprano',  // Triple kill - upper register flourish
  multi: 'bass',      // 4+ kills - bass foundation
} as const;
void _KILL_VOICE_MAP;

// =============================================================================
// HOOK IMPLEMENTATION
// =============================================================================

export function useFugueEngine(config: FugueEngineConfig): FugueEngineAPI {
  // Audio context refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const masterGainRef = useRef<GainNode | null>(null);

  // Fugue state
  const fugueStateRef = useRef<FugueState | null>(null);
  const isActiveRef = useRef(false);
  const currentPhaseRef = useRef<GamePhaseType>(config.initialPhase ?? 'flow');

  // Timing
  const lastUpdateTimeRef = useRef(0);
  const startTimeRef = useRef(0);

  // Pending events queue
  const pendingEventsRef = useRef<Array<{
    type: 'kill' | 'wave' | 'combo' | 'ball' | 'death';
    value: number;
    time: number;
  }>>([]);

  // ==========================================================================
  // INITIALIZATION
  // ==========================================================================

  useEffect(() => {
    if (!config.enabled) return;

    // Initialize audio context on first user interaction
    const initAudio = () => {
      if (audioContextRef.current) return;

      try {
        audioContextRef.current = new AudioContext();
        masterGainRef.current = audioContextRef.current.createGain();
        masterGainRef.current.gain.value = config.masterVolume;
        masterGainRef.current.connect(audioContextRef.current.destination);

        // Initialize fugue audio system
        initFugueAudio(audioContextRef.current, masterGainRef.current);
        setFuguePhase(currentPhaseRef.current);

        // Create initial fugue state
        fugueStateRef.current = createFugueState(currentPhaseRef.current);
      } catch (e) {
        console.warn('Fugue audio initialization failed:', e);
      }
    };

    // Listen for user interaction to init
    const handleInteraction = () => {
      initAudio();
      document.removeEventListener('click', handleInteraction);
      document.removeEventListener('keydown', handleInteraction);
    };

    document.addEventListener('click', handleInteraction);
    document.addEventListener('keydown', handleInteraction);

    return () => {
      document.removeEventListener('click', handleInteraction);
      document.removeEventListener('keydown', handleInteraction);

      // Cleanup audio
      if (audioContextRef.current?.state !== 'closed') {
        audioContextRef.current?.close();
      }
    };
  }, [config.enabled, config.masterVolume]);

  // ==========================================================================
  // VOLUME CONTROL
  // ==========================================================================

  useEffect(() => {
    if (masterGainRef.current) {
      masterGainRef.current.gain.value = config.masterVolume;
    }
  }, [config.masterVolume]);

  // ==========================================================================
  // CORE CONTROLS
  // ==========================================================================

  const start = useCallback(() => {
    if (!audioContextRef.current) return;

    isActiveRef.current = true;
    startTimeRef.current = audioContextRef.current.currentTime;
    lastUpdateTimeRef.current = startTimeRef.current;

    // Resume audio context if suspended
    if (audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume();
    }

    // Initialize fresh fugue state
    fugueStateRef.current = createFugueState(currentPhaseRef.current);
  }, []);

  const stop = useCallback(() => {
    isActiveRef.current = false;
    pendingEventsRef.current = [];
  }, []);

  const setPhase = useCallback((phase: GamePhaseType) => {
    currentPhaseRef.current = phase;
    setFuguePhase(phase);

    // Generate new subject for the phase
    if (fugueStateRef.current) {
      const config = PHASE_CONFIGS[phase];
      const newSubject = generateSubject(config);
      fugueStateRef.current.subject = newSubject;
      fugueStateRef.current.gamePhase = phase;
      fugueStateRef.current.tempo = config.tempo;
    }
  }, []);

  // ==========================================================================
  // GAME EVENT TRIGGERS
  // ==========================================================================

  /**
   * Trigger a musical response to a kill
   * Combo count determines intensity and voice selection
   */
  const triggerKill = useCallback((comboCount: number) => {
    if (!isActiveRef.current || !audioContextRef.current) return;

    const now = audioContextRef.current.currentTime;

    // Determine response intensity
    let intensity = Math.min(1, comboCount / 20);

    // Select scale degree based on combo (ascend through scale)
    const degree = comboCount % 7;
    const octaveBoost = Math.floor(comboCount / 7);

    // Quick melodic response note
    const baseOctave = comboCount <= 10 ? 0 : octaveBoost;
    const pitch = getScaleFrequency(degree, baseOctave);

    // Shorter notes for higher combos (more urgent)
    const duration = Math.max(0.05, 0.15 - (comboCount * 0.005));

    const killNote: FugueNote = {
      pitch: snapToScale(pitch),
      scaleDegree: degree,
      startTime: 0,
      duration,
      velocity: 0.4 + (intensity * 0.4),
      articulation: comboCount > 10 ? 'staccato' : 'marcato',
    };

    playMarimbaNote(killNote);

    // Add harmonic reinforcement for higher combos
    if (comboCount >= 3) {
      // Perfect fifth above
      const fifthNote: FugueNote = {
        ...killNote,
        pitch: snapToScale(pitch * 1.5),
        velocity: killNote.velocity * 0.6,
        startTime: 0.01,
      };
      playMarimbaNote(fifthNote);
    }

    if (comboCount >= 5) {
      // Octave below for weight
      const bassNote: FugueNote = {
        ...killNote,
        pitch: snapToScale(pitch / 2),
        velocity: killNote.velocity * 0.5,
        startTime: 0.02,
        articulation: 'tenuto',
      };
      playMarimbaNote(bassNote);
    }

    // Queue event for state update
    pendingEventsRef.current.push({
      type: 'kill',
      value: comboCount,
      time: now,
    });
  }, []);

  /**
   * Trigger wave start - new subject introduction
   */
  const triggerWaveStart = useCallback((waveNumber: number) => {
    if (!isActiveRef.current || !audioContextRef.current) return;

    const now = audioContextRef.current.currentTime;

    // Determine phase based on wave difficulty
    let phase: GamePhaseType = 'flow';
    if (waveNumber >= 15) phase = 'crisis';
    else if (waveNumber >= 8) phase = 'power';

    setPhase(phase);

    // Play ascending scale flourish
    const startDegree = 0;
    const noteCount = Math.min(4, 2 + Math.floor(waveNumber / 5));

    for (let i = 0; i < noteCount; i++) {
      const note: FugueNote = {
        pitch: getScaleFrequency(startDegree + i, i > 3 ? 1 : 0),
        scaleDegree: (startDegree + i) % 7,
        startTime: i * 0.08,
        duration: 0.12,
        velocity: 0.6 + (i * 0.1),
        articulation: i === noteCount - 1 ? 'tenuto' : 'legato',
      };
      playMarimbaNote(note);
    }

    pendingEventsRef.current.push({
      type: 'wave',
      value: waveNumber,
      time: now,
    });
  }, [setPhase]);

  /**
   * Trigger wave end - stretto climax
   */
  const triggerWaveEnd = useCallback(() => {
    if (!isActiveRef.current || !fugueStateRef.current) return;

    // Trigger stretto for wave completion
    triggerStretto(fugueStateRef.current, 0.8);
  }, []);

  /**
   * Trigger combo milestone celebration
   */
  const triggerComboMilestone = useCallback((milestone: number) => {
    if (!isActiveRef.current) return;

    // Find milestone index for intensity
    const milestoneIndex = COMBO_MILESTONES.indexOf(milestone);
    if (milestoneIndex === -1) return;

    // Calculate intensity based on milestone (used for future chord complexity)
    const _intensity = (milestoneIndex + 1) / COMBO_MILESTONES.length;
    void _intensity;

    // Play climactic chord
    playFugueClimaxChord(0); // Tonic chord

    // For higher milestones, add delayed resolution
    if (milestoneIndex >= 2) {
      setTimeout(() => {
        playFugueClimaxChord(4); // Dominant chord
      }, 300);

      setTimeout(() => {
        playFugueClimaxChord(0); // Return to tonic
      }, 600);
    }

    pendingEventsRef.current.push({
      type: 'combo',
      value: milestone,
      time: audioContextRef.current?.currentTime ?? 0,
    });
  }, []);

  /**
   * Trigger THE BALL formation - ominous subject
   */
  const triggerBallForming = useCallback(() => {
    if (!isActiveRef.current) return;

    setPhase('ball');

    // Low ominous drone
    const droneNote: FugueNote = {
      pitch: MINOR_SCALE_DEGREES[0] / 4, // Very low C#
      scaleDegree: 0,
      startTime: 0,
      duration: 3,
      velocity: 0.4,
      articulation: 'tenuto',
    };
    playMarimbaNote(droneNote);

    // Tritone dissonance
    const tritoneNote: FugueNote = {
      pitch: (MINOR_SCALE_DEGREES[0] / 4) * 1.414, // Tritone above
      scaleDegree: 3,
      startTime: 0.5,
      duration: 2,
      velocity: 0.3,
      articulation: 'legato',
    };
    playMarimbaNote(tritoneNote);

    pendingEventsRef.current.push({
      type: 'ball',
      value: 0, // Forming
      time: audioContextRef.current?.currentTime ?? 0,
    });
  }, [setPhase]);

  /**
   * Trigger THE BALL complete - silence then collapse
   */
  const triggerBallComplete = useCallback(() => {
    if (!isActiveRef.current) return;

    // Mark for silence in update loop
    pendingEventsRef.current.push({
      type: 'ball',
      value: 1, // Complete
      time: audioContextRef.current?.currentTime ?? 0,
    });
  }, []);

  /**
   * Trigger death - mournful descending line
   */
  const triggerDeath = useCallback(() => {
    if (!isActiveRef.current) return;

    stop();

    // Descending minor scale (A minor relative)
    const deathNotes: FugueNote[] = [
      { pitch: MINOR_SCALE_DEGREES[5], scaleDegree: 5, startTime: 0, duration: 0.6, velocity: 0.6, articulation: 'tenuto' },
      { pitch: MINOR_SCALE_DEGREES[4], scaleDegree: 4, startTime: 0.5, duration: 0.6, velocity: 0.5, articulation: 'tenuto' },
      { pitch: MINOR_SCALE_DEGREES[2], scaleDegree: 2, startTime: 1.0, duration: 0.6, velocity: 0.4, articulation: 'tenuto' },
      { pitch: MINOR_SCALE_DEGREES[0], scaleDegree: 0, startTime: 1.5, duration: 1.5, velocity: 0.3, articulation: 'tenuto' },
    ];

    for (const note of deathNotes) {
      playMarimbaNote({
        ...note,
        pitch: snapToScale(note.pitch / 2), // Octave down for gravity
      });
    }
  }, [stop]);

  // ==========================================================================
  // UPDATE LOOP
  // ==========================================================================

  const update = useCallback((_deltaTime: number, enemyCount: number) => {
    void _deltaTime; // Reserved for future tempo-based calculations
    if (!isActiveRef.current || !audioContextRef.current || !fugueStateRef.current) return;

    const currentTime = audioContextRef.current.currentTime;

    // Process pending events
    const events = {
      killCount: 0,
      waveTransition: false,
      comboActive: false,
      enemyCount,
    };

    for (const event of pendingEventsRef.current) {
      switch (event.type) {
        case 'kill':
          events.killCount = event.value;
          break;
        case 'wave':
          events.waveTransition = true;
          break;
        case 'combo':
          events.comboActive = true;
          break;
      }
    }
    pendingEventsRef.current = [];

    // Update fugue state
    fugueStateRef.current = updateFugueState(
      fugueStateRef.current,
      currentTime,
      events,
    );

    lastUpdateTimeRef.current = currentTime;
  }, []);

  // ==========================================================================
  // STATE GETTER
  // ==========================================================================

  const getState = useCallback((): FugueEngineState => {
    const state = fugueStateRef.current;
    if (!state) {
      return {
        isActive: false,
        currentPhase: currentPhaseRef.current,
        voicesActive: 0,
        currentBar: 0,
        inStretto: false,
      };
    }

    const voicesActive = Object.values(state.voices).filter(v => v.active).length;

    return {
      isActive: isActiveRef.current,
      currentPhase: state.gamePhase,
      voicesActive,
      currentBar: Math.floor(state.currentBar),
      inStretto: state.inStretto,
    };
  }, []);

  // ==========================================================================
  // RETURN API
  // ==========================================================================

  return {
    state: getState(),
    start,
    stop,
    setPhase,
    triggerKill,
    triggerWaveStart,
    triggerWaveEnd,
    triggerComboMilestone,
    triggerBallForming,
    triggerBallComplete,
    triggerDeath,
    update,
  };
}

export default useFugueEngine;
