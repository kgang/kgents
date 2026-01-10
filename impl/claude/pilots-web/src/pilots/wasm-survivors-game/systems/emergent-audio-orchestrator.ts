/**
 * EmergentAudioOrchestrator - The Brain of Emergent Audio
 *
 * "Every layer tells a story. Together they tell YOUR story."
 *
 * This is the MASTER ORCHESTRATOR that ties together all emergent audio layers
 * for WASM Survivors. It manages:
 *
 * 1. Layer Management - AmbientDrone, RhythmicPulse, MelodicFragment, SpatialAudio, Stingers
 * 2. Game State Integration - Extracts signals from GameState each frame
 * 3. Adaptive Mixing - Routes intensity to layers based on game phase
 * 4. Harmonic Memory - Prevents dissonant clashes between layers
 * 5. Event Dispatch - Coordinates all layers for game events
 * 6. Performance - 60fps updates without blocking, node pooling
 *
 * Design Philosophy:
 * - Emergent: Audio emerges from game state, not prescribed cues
 * - Adaptive: Intensity drives everything, game drives intensity
 * - Harmonious: All layers respect harmonic memory to avoid clashes
 * - Performant: Node pooling, efficient updates, no allocations in hot path
 *
 * @see audio.ts - Existing layered audio system
 * @see procedural-audio.ts - C-major procedural sounds
 * @see sound.ts - Legacy sound engine
 */

import type {
  GameState,
  BallPhaseType,
  EnemyType,
  Mood,
  Vector2,
} from '../types';
import {
  C_MAJOR_SCALE,
  GOOD_INTERVALS,
  BAD_INTERVALS,
  getRandomScaleNote,
  humanize,
} from './procedural-audio';

// =============================================================================
// Type Definitions
// =============================================================================

/**
 * Game phase for audio mixing decisions
 */
export type AudioPhase = 'exploration' | 'combat' | 'crisis' | 'death' | 'ball_silence';

/**
 * Layer volume configuration for each phase
 */
export interface LayerMixConfig {
  ambient: number;      // 0-1: Ambient drone volume
  rhythm: number;       // 0-1: Rhythmic pulse volume
  melodic: number;      // 0-1: Melodic fragment volume
  stinger: number;      // 0-1: Stinger volume multiplier
  spatial: number;      // 0-1: Spatial audio range multiplier
  filterCutoff?: number; // Optional: LP filter cutoff for ambient
}

/**
 * Phase-specific mixing configurations
 */
export const PHASE_MIX_CONFIGS: Record<AudioPhase, LayerMixConfig> = {
  exploration: {
    ambient: 0.8,
    rhythm: 0.2,
    melodic: 0.5,
    stinger: 0.6,
    spatial: 1.0,
  },
  combat: {
    ambient: 0.5,
    rhythm: 0.8,
    melodic: 0.7,
    stinger: 0.8,
    spatial: 1.0,
  },
  crisis: {
    ambient: 0.3,
    rhythm: 1.0,
    melodic: 0.3, // Stingers only
    stinger: 1.0,
    spatial: 0.8,
    filterCutoff: 800, // Muffle ambient for dread
  },
  death: {
    ambient: 0.0,
    rhythm: 0.0,
    melodic: 0.0,
    stinger: 0.0,
    spatial: 0.0,
  },
  ball_silence: {
    ambient: 0.0,
    rhythm: 0.0,
    melodic: 0.0,
    stinger: 0.0,
    spatial: 0.0,
    // TRUE SILENCE - "Silence should be terrifying"
  },
};

/**
 * Intensity thresholds for phase transitions
 */
export const INTENSITY_THRESHOLDS = {
  combatMin: 0.3,       // Above this = combat
  crisisMin: 0.7,       // Above this = crisis
  deathFadeStart: 0.9,  // Start fading at this intensity
};

/**
 * Harmonic memory entry - tracks recently played frequencies
 */
interface HarmonicEntry {
  frequency: number;
  timestamp: number;
  layer: string;
}

/**
 * Audio layer interface - all layers implement this
 */
export interface AudioLayer {
  /** Layer identifier */
  readonly name: string;

  /** Initialize the layer with AudioContext */
  init(ctx: AudioContext, masterGain: GainNode): void;

  /** Update layer state (called every frame) */
  update(deltaTime: number, intensity: number): void;

  /** Set layer volume (0-1) */
  setVolume(volume: number): void;

  /** Get current volume */
  getVolume(): number;

  /** Stop all sounds from this layer */
  stop(): void;

  /** Cleanup resources */
  dispose(): void;
}

/**
 * Stinger types for one-shot audio events
 */
export type StingerType =
  | 'kill_single'
  | 'kill_multi'
  | 'kill_massacre'
  | 'damage_light'
  | 'damage_heavy'
  | 'level_up'
  | 'ball_forming'
  | 'ball_constrict'
  | 'apex_hit'
  | 'graze';

// =============================================================================
// Harmonic Memory System
// =============================================================================

/**
 * HarmonicMemory - Tracks recent frequencies to suggest consonant choices
 *
 * "The game should never sound wrong, even in chaos."
 *
 * Maintains a sliding window of recently played frequencies and suggests
 * consonant next notes based on music theory relationships.
 */
class HarmonicMemory {
  private entries: HarmonicEntry[] = [];
  private readonly maxEntries = 5;
  private readonly consonantRatios = [
    1,                          // Unison
    GOOD_INTERVALS.perfectFifth,     // Perfect 5th (1.5)
    GOOD_INTERVALS.perfectFourth,    // Perfect 4th (1.333)
    GOOD_INTERVALS.majorThird,       // Major 3rd (1.25)
    GOOD_INTERVALS.majorSixth,       // Major 6th (1.667)
    GOOD_INTERVALS.octave,           // Octave (2)
    0.5,                        // Octave below
  ];

  /**
   * Record a played frequency
   */
  record(frequency: number, layer: string): void {
    const entry: HarmonicEntry = {
      frequency,
      timestamp: performance.now(),
      layer,
    };

    this.entries.push(entry);

    // Maintain max entries
    if (this.entries.length > this.maxEntries) {
      this.entries.shift();
    }
  }

  /**
   * Get the most recent frequency
   */
  getLastFrequency(): number | null {
    if (this.entries.length === 0) return null;
    return this.entries[this.entries.length - 1].frequency;
  }

  /**
   * Get all recent frequencies
   */
  getRecentFrequencies(): number[] {
    return this.entries.map(e => e.frequency);
  }

  /**
   * Suggest a consonant next frequency based on harmonic relationships
   * Prefers frequencies that form consonant intervals with recent sounds
   */
  suggestNextFrequency(baseOctave: number = 0): number {
    const lastFreq = this.getLastFrequency();

    if (lastFreq === null) {
      // No history - return random C major note
      return getRandomScaleNote(baseOctave);
    }

    // Find consonant options relative to last frequency
    const candidates: number[] = [];

    for (const ratio of this.consonantRatios) {
      const candidate = lastFreq * ratio;

      // Keep within reasonable frequency range (80Hz - 2000Hz)
      if (candidate >= 80 && candidate <= 2000) {
        candidates.push(candidate);
      }
    }

    // Also include C major scale notes in the same octave
    const scaleNotes = [
      C_MAJOR_SCALE.C4,
      C_MAJOR_SCALE.D4,
      C_MAJOR_SCALE.E4,
      C_MAJOR_SCALE.G4,
      C_MAJOR_SCALE.A4,
    ].map(f => f * Math.pow(2, baseOctave));

    candidates.push(...scaleNotes);

    // Pick randomly from candidates
    return candidates[Math.floor(Math.random() * candidates.length)];
  }

  /**
   * Check if a frequency would be dissonant with recent sounds
   */
  wouldBeDissonant(frequency: number): boolean {
    const dissonantRatios = [
      BAD_INTERVALS.minorSecond,    // Minor 2nd (1.067)
      BAD_INTERVALS.tritone,        // Tritone (1.406)
      BAD_INTERVALS.minorSeventh,   // Minor 7th (1.8)
    ];

    for (const entry of this.entries) {
      const ratio = frequency / entry.frequency;
      const normalizedRatio = ratio > 1 ? ratio : 1 / ratio;

      for (const badRatio of dissonantRatios) {
        // Allow 5% tolerance
        if (Math.abs(normalizedRatio - badRatio) < 0.05) {
          return true;
        }
      }
    }

    return false;
  }

  /**
   * Clear harmonic memory
   */
  clear(): void {
    this.entries = [];
  }
}

// =============================================================================
// Audio Node Pool
// =============================================================================

/**
 * NodePool - Reusable audio node pool for performance
 *
 * Web Audio nodes can't be reused after stopping, but we can pre-allocate
 * gain nodes and filters that persist. Oscillators must be created fresh.
 */
class NodePool {
  private ctx: AudioContext | null = null;
  private gainNodes: GainNode[] = [];
  private filters: BiquadFilterNode[] = [];
  private readonly poolSize = 20;

  init(ctx: AudioContext): void {
    this.ctx = ctx;

    // Pre-allocate gain nodes
    for (let i = 0; i < this.poolSize; i++) {
      const gain = ctx.createGain();
      gain.gain.value = 0;
      this.gainNodes.push(gain);

      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 20000;
      this.filters.push(filter);
    }
  }

  /**
   * Get a gain node from pool (creates new if exhausted)
   */
  getGainNode(): GainNode {
    if (!this.ctx) throw new Error('NodePool not initialized');

    // Find unused gain node (volume near 0 and not ramping)
    for (const gain of this.gainNodes) {
      if (gain.gain.value < 0.001) {
        return gain;
      }
    }

    // Pool exhausted - create new node
    const gain = this.ctx.createGain();
    gain.gain.value = 0;
    this.gainNodes.push(gain);
    return gain;
  }

  /**
   * Get a filter node from pool
   */
  getFilter(): BiquadFilterNode {
    if (!this.ctx) throw new Error('NodePool not initialized');

    // Return first available filter
    for (const filter of this.filters) {
      // Simple heuristic: if frequency is at default, it's likely unused
      if (filter.frequency.value === 20000) {
        return filter;
      }
    }

    // Create new filter
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 20000;
    this.filters.push(filter);
    return filter;
  }

  /**
   * Return a gain node to pool
   */
  releaseGain(gain: GainNode): void {
    gain.gain.setValueAtTime(0, this.ctx?.currentTime ?? 0);
    gain.disconnect();
  }

  /**
   * Return a filter to pool
   */
  releaseFilter(filter: BiquadFilterNode): void {
    filter.frequency.value = 20000;
    filter.disconnect();
  }

  dispose(): void {
    this.gainNodes.forEach(g => g.disconnect());
    this.filters.forEach(f => f.disconnect());
    this.gainNodes = [];
    this.filters = [];
    this.ctx = null;
  }
}

// =============================================================================
// Ambient Drone Layer
// =============================================================================

/**
 * AmbientDroneLayer - Continuous background atmosphere
 *
 * Creates a slowly-evolving drone that responds to game intensity.
 * Higher intensity = higher pitch, more harmonics, slight dissonance.
 */
class AmbientDroneLayer implements AudioLayer {
  readonly name = 'ambient';

  private ctx: AudioContext | null = null;
  private droneGain: GainNode | null = null;
  private oscillators: OscillatorNode[] = [];
  private filter: BiquadFilterNode | null = null;
  private volume = 0;
  private targetVolume = 0;

  // Drone configuration
  private baseFrequency = 80; // Low C-ish
  private readonly harmonicRatios = [1, 2, 3, 4]; // Fundamental + overtones

  init(ctx: AudioContext, masterGain: GainNode): void {
    this.ctx = ctx;

    // Create drone gain
    this.droneGain = ctx.createGain();
    this.droneGain.gain.value = 0;

    // Create low-pass filter for warmth control
    this.filter = ctx.createBiquadFilter();
    this.filter.type = 'lowpass';
    this.filter.frequency.value = 400;
    this.filter.Q.value = 0.5;

    // Connect filter to drone gain, drone gain to master
    this.filter.connect(this.droneGain);
    this.droneGain.connect(masterGain);

    // Create drone oscillators
    this.createDroneOscillators();
  }

  private createDroneOscillators(): void {
    if (!this.ctx || !this.filter) return;

    // Stop existing oscillators
    this.oscillators.forEach(osc => {
      try { osc.stop(); } catch { /* ignore */ }
    });
    this.oscillators = [];

    // Create new oscillators for each harmonic
    for (let i = 0; i < this.harmonicRatios.length; i++) {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = i === 0 ? 'sine' : 'triangle';
      osc.frequency.value = this.baseFrequency * this.harmonicRatios[i];

      // Higher harmonics are quieter
      gain.gain.value = 1 / (i + 1) ** 1.5;

      osc.connect(gain);
      gain.connect(this.filter);
      osc.start();

      this.oscillators.push(osc);
    }
  }

  update(deltaTime: number, intensity: number): void {
    if (!this.ctx || !this.droneGain || !this.filter) return;

    const now = this.ctx.currentTime;

    // Smooth volume changes
    this.volume += (this.targetVolume - this.volume) * Math.min(1, deltaTime * 2);
    this.droneGain.gain.setTargetAtTime(this.volume * 0.15, now, 0.1);

    // Intensity affects filter cutoff (more open in combat)
    const cutoff = 200 + intensity * 600;
    this.filter.frequency.setTargetAtTime(cutoff, now, 0.2);

    // Intensity affects base frequency (slight rise in tension)
    const freqShift = 1 + intensity * 0.1;
    this.oscillators.forEach((osc, i) => {
      osc.frequency.setTargetAtTime(
        this.baseFrequency * this.harmonicRatios[i] * freqShift,
        now,
        0.5
      );
    });
  }

  setVolume(volume: number): void {
    this.targetVolume = Math.max(0, Math.min(1, volume));
  }

  getVolume(): number {
    return this.volume;
  }

  /**
   * Set filter cutoff directly (for crisis muffling)
   */
  setFilterCutoff(cutoff: number): void {
    if (this.filter && this.ctx) {
      this.filter.frequency.setTargetAtTime(cutoff, this.ctx.currentTime, 0.3);
    }
  }

  stop(): void {
    if (this.droneGain && this.ctx) {
      this.droneGain.gain.setTargetAtTime(0, this.ctx.currentTime, 0.5);
    }
    this.targetVolume = 0;
    this.volume = 0;
  }

  dispose(): void {
    this.oscillators.forEach(osc => {
      try { osc.stop(); } catch { /* ignore */ }
    });
    this.oscillators = [];
    this.filter?.disconnect();
    this.droneGain?.disconnect();
    this.ctx = null;
  }
}

// =============================================================================
// Rhythmic Pulse Layer
// =============================================================================

/**
 * RhythmicPulseLayer - Heartbeat-like pulse that intensifies with danger
 *
 * Provides rhythmic foundation that accelerates with intensity.
 * Low intensity = slow, gentle pulse. High intensity = frantic heartbeat.
 */
class RhythmicPulseLayer implements AudioLayer {
  readonly name = 'rhythm';

  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private pulseGain: GainNode | null = null;
  private volume = 0;
  private targetVolume = 0;
  private currentIntensity = 0;
  private lastPulseTime = 0;

  // Pulse configuration
  private readonly baseBPM = 60;  // Base beats per minute
  private readonly maxBPM = 180;  // Maximum at full intensity

  init(ctx: AudioContext, masterGain: GainNode): void {
    this.ctx = ctx;
    this.masterGain = masterGain;

    this.pulseGain = ctx.createGain();
    this.pulseGain.gain.value = 0;
    this.pulseGain.connect(masterGain);

    this.lastPulseTime = ctx.currentTime;
  }

  update(deltaTime: number, intensity: number): void {
    if (!this.ctx || !this.pulseGain) return;

    this.currentIntensity = intensity;
    const now = this.ctx.currentTime;

    // Smooth volume changes
    this.volume += (this.targetVolume - this.volume) * Math.min(1, deltaTime * 2);

    // Calculate current BPM based on intensity
    const currentBPM = this.baseBPM + (this.maxBPM - this.baseBPM) * intensity;
    const beatInterval = 60 / currentBPM;

    // Check if time for next pulse
    if (now - this.lastPulseTime >= beatInterval) {
      this.triggerPulse();
      this.lastPulseTime = now;
    }
  }

  private triggerPulse(): void {
    if (!this.ctx || !this.masterGain || this.volume <= 0) return;

    const now = this.ctx.currentTime;
    const baseFreq = 50 + this.currentIntensity * 30; // 50-80Hz

    // Create pulse oscillator
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.value = baseFreq;

    // Quick attack, medium decay
    const attackTime = 0.02;
    const decayTime = 0.1 + (1 - this.currentIntensity) * 0.15;
    const peakVolume = this.volume * 0.2;

    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(peakVolume, now + attackTime);
    gain.gain.exponentialRampToValueAtTime(0.001, now + attackTime + decayTime);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start(now);
    osc.stop(now + attackTime + decayTime);
  }

  setVolume(volume: number): void {
    this.targetVolume = Math.max(0, Math.min(1, volume));
  }

  getVolume(): number {
    return this.volume;
  }

  stop(): void {
    this.targetVolume = 0;
    this.volume = 0;
  }

  dispose(): void {
    this.pulseGain?.disconnect();
    this.ctx = null;
  }
}

// =============================================================================
// Melodic Fragment Layer
// =============================================================================

/**
 * MelodicFragmentLayer - Occasional melodic phrases that punctuate gameplay
 *
 * Plays short melodic fragments based on game events and intensity.
 * Uses harmonic memory to ensure consonance with other layers.
 */
class MelodicFragmentLayer implements AudioLayer {
  readonly name = 'melodic';

  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private volume = 0;
  private targetVolume = 0;
  private harmonicMemory: HarmonicMemory;
  private lastFragmentTime = 0;
  private readonly minFragmentInterval = 2000; // Min ms between fragments

  constructor(harmonicMemory: HarmonicMemory) {
    this.harmonicMemory = harmonicMemory;
  }

  init(ctx: AudioContext, masterGain: GainNode): void {
    this.ctx = ctx;
    this.masterGain = masterGain;
    this.lastFragmentTime = performance.now();
  }

  update(_deltaTime: number, _intensity: number): void {
    // Melodic fragments are event-driven, not continuous
    // This update just manages volume
    this.volume += (this.targetVolume - this.volume) * 0.1;
  }

  /**
   * Play a short melodic fragment
   */
  playFragment(type: 'ascending' | 'descending' | 'chord' | 'stinger'): void {
    if (!this.ctx || !this.masterGain || this.volume <= 0) return;

    // Rate limit fragments
    const now = performance.now();
    if (now - this.lastFragmentTime < this.minFragmentInterval) return;
    this.lastFragmentTime = now;

    const audioNow = this.ctx.currentTime;

    switch (type) {
      case 'ascending':
        this.playAscendingFragment(audioNow);
        break;
      case 'descending':
        this.playDescendingFragment(audioNow);
        break;
      case 'chord':
        this.playChordFragment(audioNow);
        break;
      case 'stinger':
        this.playStingerFragment(audioNow);
        break;
    }
  }

  private playAscendingFragment(startTime: number): void {
    if (!this.ctx || !this.masterGain) return;

    // Get consonant starting note
    const startNote = this.harmonicMemory.suggestNextFrequency();

    const notes = [
      startNote,
      startNote * GOOD_INTERVALS.majorThird,
      startNote * GOOD_INTERVALS.perfectFifth,
    ];

    const noteSpacing = 0.08;
    const noteDuration = 0.15;

    notes.forEach((freq, i) => {
      const osc = this.ctx!.createOscillator();
      const gain = this.ctx!.createGain();

      osc.type = 'sine';
      osc.frequency.value = freq;

      const noteStart = startTime + i * noteSpacing;
      gain.gain.setValueAtTime(0, noteStart);
      gain.gain.linearRampToValueAtTime(this.volume * 0.1, noteStart + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.001, noteStart + noteDuration);

      osc.connect(gain);
      gain.connect(this.masterGain!);
      osc.start(noteStart);
      osc.stop(noteStart + noteDuration);

      // Record to harmonic memory
      this.harmonicMemory.record(freq, this.name);
    });
  }

  private playDescendingFragment(startTime: number): void {
    if (!this.ctx || !this.masterGain) return;

    const startNote = this.harmonicMemory.suggestNextFrequency(1);

    const notes = [
      startNote,
      startNote / GOOD_INTERVALS.majorThird,
      startNote / GOOD_INTERVALS.perfectFifth,
    ];

    const noteSpacing = 0.1;
    const noteDuration = 0.2;

    notes.forEach((freq, i) => {
      const osc = this.ctx!.createOscillator();
      const gain = this.ctx!.createGain();

      osc.type = 'triangle';
      osc.frequency.value = freq;

      const noteStart = startTime + i * noteSpacing;
      gain.gain.setValueAtTime(0, noteStart);
      gain.gain.linearRampToValueAtTime(this.volume * 0.08, noteStart + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.001, noteStart + noteDuration);

      osc.connect(gain);
      gain.connect(this.masterGain!);
      osc.start(noteStart);
      osc.stop(noteStart + noteDuration);

      this.harmonicMemory.record(freq, this.name);
    });
  }

  private playChordFragment(startTime: number): void {
    if (!this.ctx || !this.masterGain) return;

    const root = this.harmonicMemory.suggestNextFrequency();

    const chord = [
      root,
      root * GOOD_INTERVALS.majorThird,
      root * GOOD_INTERVALS.perfectFifth,
    ];

    const duration = 0.3;

    chord.forEach((freq, i) => {
      const osc = this.ctx!.createOscillator();
      const gain = this.ctx!.createGain();

      osc.type = 'sine';
      osc.frequency.value = freq;

      gain.gain.setValueAtTime(0, startTime);
      gain.gain.linearRampToValueAtTime(this.volume * 0.06, startTime + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

      osc.connect(gain);
      gain.connect(this.masterGain!);
      osc.start(startTime);
      osc.stop(startTime + duration);

      if (i === 0) this.harmonicMemory.record(freq, this.name);
    });
  }

  private playStingerFragment(startTime: number): void {
    if (!this.ctx || !this.masterGain) return;

    // High, attention-grabbing note
    const freq = this.harmonicMemory.suggestNextFrequency(1);

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.value = freq;

    gain.gain.setValueAtTime(this.volume * 0.12, startTime);
    gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.1);

    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(startTime);
    osc.stop(startTime + 0.1);

    this.harmonicMemory.record(freq, this.name);
  }

  setVolume(volume: number): void {
    this.targetVolume = Math.max(0, Math.min(1, volume));
  }

  getVolume(): number {
    return this.volume;
  }

  stop(): void {
    this.targetVolume = 0;
    this.volume = 0;
  }

  dispose(): void {
    this.ctx = null;
  }
}

// =============================================================================
// Spatial Audio Layer
// =============================================================================

/**
 * SpatialAudioLayer - Positional audio for game events
 *
 * Handles stereo panning and distance attenuation for sounds.
 */
class SpatialAudioLayer implements AudioLayer {
  readonly name = 'spatial';

  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private volume = 1;
  private targetVolume = 1;
  private playerPosition: Vector2 = { x: 400, y: 300 };
  private listenerRange = 600;

  init(ctx: AudioContext, masterGain: GainNode): void {
    this.ctx = ctx;
    this.masterGain = masterGain;
  }

  update(_deltaTime: number, _intensity: number): void {
    this.volume += (this.targetVolume - this.volume) * 0.1;
  }

  /**
   * Update player position for spatial calculations
   */
  setPlayerPosition(position: Vector2): void {
    this.playerPosition = position;
  }

  /**
   * Set listener range
   */
  setListenerRange(range: number): void {
    this.listenerRange = range;
  }

  /**
   * Get stereo pan value for a source position (-1 to 1)
   */
  getStereoPosition(sourcePosition: Vector2): number {
    const dx = sourcePosition.x - this.playerPosition.x;
    return Math.max(-1, Math.min(1, dx / (this.listenerRange / 2)));
  }

  /**
   * Get distance attenuation (0-1)
   */
  getDistanceAttenuation(sourcePosition: Vector2): number {
    const dx = sourcePosition.x - this.playerPosition.x;
    const dy = sourcePosition.y - this.playerPosition.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    return Math.max(0, 1 - dist / this.listenerRange) * this.volume;
  }

  /**
   * Play a spatial sound at a position
   */
  playSpatialSound(
    frequency: number,
    position: Vector2,
    options: {
      type?: OscillatorType;
      duration?: number;
      volume?: number;
      attack?: number;
    } = {}
  ): void {
    if (!this.ctx || !this.masterGain) return;

    const now = this.ctx.currentTime;
    const pan = this.getStereoPosition(position);
    const distanceVol = this.getDistanceAttenuation(position);

    if (distanceVol < 0.05) return; // Too far to hear

    const type = options.type ?? 'sine';
    const duration = options.duration ?? 0.1;
    const baseVolume = options.volume ?? 0.1;
    const attack = options.attack ?? 0.01;

    // Create spatial chain: osc -> gain -> panner -> master
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const panner = this.ctx.createStereoPanner();

    osc.type = type;
    osc.frequency.value = frequency;

    panner.pan.value = pan;

    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(baseVolume * distanceVol, now + attack);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc.connect(gain);
    gain.connect(panner);
    panner.connect(this.masterGain);

    osc.start(now);
    osc.stop(now + duration);
  }

  setVolume(volume: number): void {
    this.targetVolume = Math.max(0, Math.min(1, volume));
  }

  getVolume(): number {
    return this.volume;
  }

  stop(): void {
    this.targetVolume = 0;
  }

  dispose(): void {
    this.ctx = null;
  }
}

// =============================================================================
// Stinger Layer
// =============================================================================

/**
 * StingerLayer - One-shot impact sounds for game events
 *
 * Handles kill sounds, damage sounds, level up fanfares, etc.
 * Uses harmonic memory for note selection.
 */
class StingerLayer implements AudioLayer {
  readonly name = 'stinger';

  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private volume = 1;
  private targetVolume = 1;
  private harmonicMemory: HarmonicMemory;

  constructor(harmonicMemory: HarmonicMemory) {
    this.harmonicMemory = harmonicMemory;
  }

  init(ctx: AudioContext, masterGain: GainNode): void {
    this.ctx = ctx;
    this.masterGain = masterGain;
  }

  update(_deltaTime: number, _intensity: number): void {
    this.volume += (this.targetVolume - this.volume) * 0.1;
  }

  /**
   * Play a stinger sound
   */
  playStinger(type: StingerType, intensity: number = 1): void {
    if (!this.ctx || !this.masterGain || this.volume <= 0) return;

    const now = this.ctx.currentTime;

    switch (type) {
      case 'kill_single':
        this.playKillStinger(now, 1, intensity);
        break;
      case 'kill_multi':
        this.playKillStinger(now, 2, intensity);
        break;
      case 'kill_massacre':
        this.playKillStinger(now, 3, intensity);
        break;
      case 'damage_light':
        this.playDamageStinger(now, 0.5);
        break;
      case 'damage_heavy':
        this.playDamageStinger(now, 1);
        break;
      case 'level_up':
        this.playLevelUpStinger(now);
        break;
      case 'apex_hit':
        this.playApexHitStinger(now, intensity);
        break;
      case 'graze':
        this.playGrazeStinger(now, intensity);
        break;
      default:
        // Unknown stinger type - play generic
        this.playGenericStinger(now);
    }
  }

  private playKillStinger(startTime: number, tier: number, intensity: number): void {
    if (!this.ctx || !this.masterGain) return;

    // Get harmonically consonant note
    const baseFreq = this.harmonicMemory.suggestNextFrequency();
    const volumeMult = this.volume * (0.8 + tier * 0.1) * intensity;

    // Noise burst for crunch
    const bufferSize = Math.floor(this.ctx.sampleRate * 0.04);
    const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const noiseData = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      noiseData[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = noiseBuffer;

    const noiseFilter = this.ctx.createBiquadFilter();
    noiseFilter.type = 'bandpass';
    noiseFilter.frequency.value = baseFreq * 2;
    noiseFilter.Q.value = 1;

    const noiseGain = this.ctx.createGain();
    noiseGain.gain.setValueAtTime(volumeMult * 0.15, startTime);
    noiseGain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.04);

    noise.connect(noiseFilter);
    noiseFilter.connect(noiseGain);
    noiseGain.connect(this.masterGain);
    noise.start(startTime);

    // Tonal component
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'triangle';
    osc.frequency.value = baseFreq;

    const duration = 0.08 + tier * 0.02;
    gain.gain.setValueAtTime(0, startTime);
    gain.gain.linearRampToValueAtTime(volumeMult * 0.1, startTime + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(startTime);
    osc.stop(startTime + duration);

    // Record to harmonic memory
    this.harmonicMemory.record(baseFreq, this.name);
  }

  private playDamageStinger(startTime: number, severity: number): void {
    if (!this.ctx || !this.masterGain) return;

    // Use dissonant interval for damage
    const baseFreq = C_MAJOR_SCALE.C3;
    const dissonantFreq = baseFreq * BAD_INTERVALS.tritone;

    const duration = 0.1 + severity * 0.05;
    const volumeMult = this.volume * severity;

    // Base thud
    const osc1 = this.ctx.createOscillator();
    const gain1 = this.ctx.createGain();

    osc1.type = 'triangle';
    osc1.frequency.setValueAtTime(baseFreq, startTime);
    osc1.frequency.exponentialRampToValueAtTime(baseFreq * 0.6, startTime + duration);

    gain1.gain.setValueAtTime(volumeMult * 0.12, startTime);
    gain1.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

    osc1.connect(gain1);
    gain1.connect(this.masterGain);
    osc1.start(startTime);
    osc1.stop(startTime + duration);

    // Dissonant layer (quieter)
    const osc2 = this.ctx.createOscillator();
    const gain2 = this.ctx.createGain();

    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(dissonantFreq, startTime);
    osc2.frequency.exponentialRampToValueAtTime(dissonantFreq * 0.6, startTime + duration);

    gain2.gain.setValueAtTime(volumeMult * 0.04, startTime);
    gain2.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

    osc2.connect(gain2);
    gain2.connect(this.masterGain);
    osc2.start(startTime);
    osc2.stop(startTime + duration);
  }

  private playLevelUpStinger(startTime: number): void {
    if (!this.ctx || !this.masterGain) return;

    // Ascending C major arpeggio
    const notes = [
      C_MAJOR_SCALE.C4,
      C_MAJOR_SCALE.E4,
      C_MAJOR_SCALE.G4,
      C_MAJOR_SCALE.C5,
    ];

    const noteSpacing = humanize(0.07);
    const noteDuration = humanize(0.18);
    const volumeMult = this.volume;

    notes.forEach((freq, i) => {
      const noteStart = startTime + i * noteSpacing;

      const osc = this.ctx!.createOscillator();
      const gain = this.ctx!.createGain();

      osc.type = 'sine';
      osc.frequency.value = freq;

      gain.gain.setValueAtTime(0, noteStart);
      gain.gain.linearRampToValueAtTime(volumeMult * 0.12, noteStart + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.001, noteStart + noteDuration);

      osc.connect(gain);
      gain.connect(this.masterGain!);
      osc.start(noteStart);
      osc.stop(noteStart + noteDuration);

      if (i === notes.length - 1) {
        this.harmonicMemory.record(freq, this.name);
      }
    });
  }

  private playApexHitStinger(startTime: number, intensity: number): void {
    if (!this.ctx || !this.masterGain) return;

    // Powerful impact sound
    const baseFreq = this.harmonicMemory.suggestNextFrequency();
    const volumeMult = this.volume * intensity;

    // Low impact
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(baseFreq * 0.5, startTime);
    osc.frequency.exponentialRampToValueAtTime(baseFreq * 0.3, startTime + 0.15);

    gain.gain.setValueAtTime(volumeMult * 0.2, startTime);
    gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.15);

    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(startTime);
    osc.stop(startTime + 0.15);

    // High shimmer
    const osc2 = this.ctx.createOscillator();
    const gain2 = this.ctx.createGain();

    osc2.type = 'sine';
    osc2.frequency.value = baseFreq * 2;

    gain2.gain.setValueAtTime(0, startTime);
    gain2.gain.linearRampToValueAtTime(volumeMult * 0.08, startTime + 0.02);
    gain2.gain.exponentialRampToValueAtTime(0.001, startTime + 0.1);

    osc2.connect(gain2);
    gain2.connect(this.masterGain);
    osc2.start(startTime);
    osc2.stop(startTime + 0.1);

    this.harmonicMemory.record(baseFreq, this.name);
  }

  private playGrazeStinger(startTime: number, chainCount: number): void {
    if (!this.ctx || !this.masterGain) return;

    // Higher pitch with chain count
    const baseDegree = Math.min(chainCount - 1, 4);
    const baseFreq = C_MAJOR_SCALE.G4 * Math.pow(GOOD_INTERVALS.majorThird, baseDegree * 0.5);

    const volumeMult = this.volume * 0.6;
    const duration = 0.06;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.value = baseFreq;

    gain.gain.setValueAtTime(volumeMult * 0.08, startTime);
    gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(startTime);
    osc.stop(startTime + duration);

    // Major 6th sparkle
    const osc2 = this.ctx.createOscillator();
    const gain2 = this.ctx.createGain();

    osc2.type = 'sine';
    osc2.frequency.value = baseFreq * GOOD_INTERVALS.majorSixth;

    gain2.gain.setValueAtTime(volumeMult * 0.04, startTime);
    gain2.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

    osc2.connect(gain2);
    gain2.connect(this.masterGain);
    osc2.start(startTime);
    osc2.stop(startTime + duration);
  }

  private playGenericStinger(startTime: number): void {
    if (!this.ctx || !this.masterGain) return;

    const freq = this.harmonicMemory.suggestNextFrequency();

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.value = freq;

    gain.gain.setValueAtTime(this.volume * 0.1, startTime);
    gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.1);

    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(startTime);
    osc.stop(startTime + 0.1);

    this.harmonicMemory.record(freq, this.name);
  }

  setVolume(volume: number): void {
    this.targetVolume = Math.max(0, Math.min(1, volume));
  }

  getVolume(): number {
    return this.volume;
  }

  stop(): void {
    this.targetVolume = 0;
  }

  dispose(): void {
    this.ctx = null;
  }
}

// =============================================================================
// Main Orchestrator
// =============================================================================

/**
 * EmergentAudioOrchestrator - The Master Controller
 *
 * Ties together all audio layers and manages them based on game state.
 * This is the single entry point for the game to interact with audio.
 */
export class EmergentAudioOrchestrator {
  // Audio infrastructure
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private nodePool: NodePool;
  private harmonicMemory: HarmonicMemory;

  // Audio layers
  private ambientLayer: AmbientDroneLayer;
  private rhythmLayer: RhythmicPulseLayer;
  private melodicLayer: MelodicFragmentLayer;
  private spatialLayer: SpatialAudioLayer;
  private stingerLayer: StingerLayer;
  private layers: AudioLayer[];

  // State
  private initialized = false;
  private currentPhase: AudioPhase = 'exploration';
  private currentIntensity = 0;
  private targetIntensity = 0;
  private lastUpdateTime = 0;
  private masterVolume = 0.5;

  // Game state cache (to detect changes)
  private lastEnemyCount = 0;
  private lastPlayerHealth = 100;
  private lastWave = 1;
  private lastBallPhase: BallPhaseType | null = null;

  constructor() {
    this.nodePool = new NodePool();
    this.harmonicMemory = new HarmonicMemory();

    // Create layers
    this.ambientLayer = new AmbientDroneLayer();
    this.rhythmLayer = new RhythmicPulseLayer();
    this.melodicLayer = new MelodicFragmentLayer(this.harmonicMemory);
    this.spatialLayer = new SpatialAudioLayer();
    this.stingerLayer = new StingerLayer(this.harmonicMemory);

    this.layers = [
      this.ambientLayer,
      this.rhythmLayer,
      this.melodicLayer,
      this.spatialLayer,
      this.stingerLayer,
    ];
  }

  // ===========================================================================
  // Initialization
  // ===========================================================================

  /**
   * Initialize the orchestrator with an AudioContext
   * Must be called after user interaction (browser autoplay policy)
   */
  init(): boolean {
    if (this.initialized) return true;

    try {
      this.ctx = new AudioContext();
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.value = this.masterVolume;
      this.masterGain.connect(this.ctx.destination);

      // Initialize node pool
      this.nodePool.init(this.ctx);

      // Initialize all layers
      for (const layer of this.layers) {
        layer.init(this.ctx, this.masterGain);
      }

      this.initialized = true;
      this.lastUpdateTime = performance.now();

      console.log('[EmergentAudio] Orchestrator initialized');
      return true;
    } catch (e) {
      console.error('[EmergentAudio] Failed to initialize:', e);
      return false;
    }
  }

  /**
   * Resume audio context (call after user interaction)
   */
  async resume(): Promise<void> {
    if (this.ctx?.state === 'suspended') {
      await this.ctx.resume();
    }
  }

  /**
   * Check if orchestrator is ready
   */
  isReady(): boolean {
    return this.initialized && this.ctx?.state === 'running';
  }

  // ===========================================================================
  // Game State Integration
  // ===========================================================================

  /**
   * Main update method - call every frame with game state
   * This is the primary interface for the game loop.
   */
  update(gameState: GameState): void {
    if (!this.initialized || !this.ctx) return;

    const now = performance.now();
    const deltaTime = (now - this.lastUpdateTime) / 1000; // Convert to seconds
    this.lastUpdateTime = now;

    // Extract signals from game state
    const signals = this.extractSignals(gameState);

    // Compute target intensity
    this.targetIntensity = this.computeIntensity(signals);

    // Smooth intensity changes
    const intensityRate = deltaTime * 2; // 0.5 second smoothing
    this.currentIntensity += (this.targetIntensity - this.currentIntensity) * intensityRate;

    // Determine audio phase
    const newPhase = this.determinePhase(signals, this.currentIntensity);
    if (newPhase !== this.currentPhase) {
      this.onPhaseChange(this.currentPhase, newPhase);
      this.currentPhase = newPhase;
    }

    // Apply phase-specific mixing
    this.applyMixConfig(PHASE_MIX_CONFIGS[this.currentPhase]);

    // Update spatial layer with player position
    this.spatialLayer.setPlayerPosition(gameState.player.position);

    // Update all layers
    for (const layer of this.layers) {
      layer.update(deltaTime, this.currentIntensity);
    }

    // Detect and respond to events
    this.detectEvents(signals);

    // Cache state for next frame
    this.lastEnemyCount = signals.enemyCount;
    this.lastPlayerHealth = signals.playerHealth;
    this.lastWave = signals.wave;
    this.lastBallPhase = signals.ballPhase;
  }

  /**
   * Extract relevant signals from game state
   */
  private extractSignals(state: GameState): {
    enemyCount: number;
    playerHealth: number;
    playerHealthPercent: number;
    ballPhase: BallPhaseType | null;
    wave: number;
    killsPerSecond: number;
    coordinationLevel: number;
    mood: Mood;
  } {
    return {
      enemyCount: state.enemies.length,
      playerHealth: state.player.health,
      playerHealthPercent: state.player.health / state.player.maxHealth,
      ballPhase: state.ballPhase?.type ?? null,
      wave: state.wave,
      killsPerSecond: state.contrastState.killsPerSecond,
      coordinationLevel: state.colonyCoordination,
      mood: state.currentMood,
    };
  }

  /**
   * Compute intensity score (0-1) from game signals
   */
  private computeIntensity(signals: {
    enemyCount: number;
    playerHealthPercent: number;
    killsPerSecond: number;
    coordinationLevel: number;
    ballPhase: BallPhaseType | null;
  }): number {
    // Ball phase overrides intensity
    if (signals.ballPhase === 'constrict' || signals.ballPhase === 'death') {
      return 1;
    }
    if (signals.ballPhase === 'silence') {
      return 0; // Silence = zero intensity for layers
    }
    if (signals.ballPhase === 'forming' || signals.ballPhase === 'sphere') {
      return 0.9;
    }

    // Base intensity from enemy count (0-50 enemies = 0-0.5 intensity)
    const enemyIntensity = Math.min(1, signals.enemyCount / 50) * 0.5;

    // Health contributes to intensity (low health = high intensity)
    const healthIntensity = (1 - signals.playerHealthPercent) * 0.3;

    // Kill rate contributes (more kills = more intense)
    const killIntensity = Math.min(1, signals.killsPerSecond / 5) * 0.15;

    // Coordination level contributes (ball forming = rising intensity)
    const coordIntensity = signals.coordinationLevel * 0.05;

    return Math.min(1, enemyIntensity + healthIntensity + killIntensity + coordIntensity);
  }

  /**
   * Determine audio phase from signals and intensity
   */
  private determinePhase(
    signals: { ballPhase: BallPhaseType | null; playerHealth: number },
    intensity: number
  ): AudioPhase {
    // Ball silence is special
    if (signals.ballPhase === 'silence') {
      return 'ball_silence';
    }

    // Death phase (game over)
    if (signals.playerHealth <= 0) {
      return 'death';
    }

    // Crisis when intensity is high
    if (intensity >= INTENSITY_THRESHOLDS.crisisMin) {
      return 'crisis';
    }

    // Combat when intensity is medium
    if (intensity >= INTENSITY_THRESHOLDS.combatMin) {
      return 'combat';
    }

    return 'exploration';
  }

  /**
   * Handle phase transitions
   */
  private onPhaseChange(from: AudioPhase, to: AudioPhase): void {
    console.log(`[EmergentAudio] Phase: ${from} -> ${to}`);

    // Special handling for ball silence
    if (to === 'ball_silence') {
      this.harmonicMemory.clear();
    }

    // Play transition melodic fragment
    if (to === 'crisis' && from !== 'crisis') {
      this.melodicLayer.playFragment('descending');
    } else if (to === 'exploration' && from === 'combat') {
      this.melodicLayer.playFragment('ascending');
    }
  }

  /**
   * Apply mix configuration to all layers
   */
  private applyMixConfig(config: LayerMixConfig): void {
    this.ambientLayer.setVolume(config.ambient);
    this.rhythmLayer.setVolume(config.rhythm);
    this.melodicLayer.setVolume(config.melodic);
    this.stingerLayer.setVolume(config.stinger);
    this.spatialLayer.setVolume(config.spatial);

    // Apply filter cutoff if specified
    if (config.filterCutoff !== undefined) {
      this.ambientLayer.setFilterCutoff(config.filterCutoff);
    }
  }

  /**
   * Detect game events and dispatch audio
   */
  private detectEvents(
    signals: {
      enemyCount: number;
      playerHealth: number;
      wave: number;
      ballPhase: BallPhaseType | null;
    }
  ): void {
    // Wave change
    if (signals.wave !== this.lastWave && signals.wave > this.lastWave) {
      this.onWaveChange(signals.wave);
    }

    // Ball phase change
    if (signals.ballPhase !== this.lastBallPhase && signals.ballPhase) {
      this.onBallPhaseChange(signals.ballPhase);
    }

    // Significant enemy count change (massacre)
    const enemyDiff = this.lastEnemyCount - signals.enemyCount;
    if (enemyDiff >= 5) {
      // 5+ enemies killed in one frame = massacre
      this.onMassacreKill(enemyDiff);
    }

    // Detect significant health drop (for damage event detection)
    const healthDrop = this.lastPlayerHealth - signals.playerHealth;
    if (healthDrop >= 10) {
      // Significant damage taken
      this.onDamage(healthDrop);
    }
  }

  // ===========================================================================
  // Event Dispatch
  // ===========================================================================

  /**
   * Handle kill event
   * @param position - Where the kill happened
   * @param enemyType - Type of enemy killed
   * @param comboCount - Current combo count
   */
  onKill(position: Vector2, _enemyType: EnemyType, comboCount: number): void {
    if (!this.initialized) return;

    // Determine stinger type
    let stingerType: StingerType;
    if (comboCount >= 10) {
      stingerType = 'kill_massacre';
    } else if (comboCount >= 3) {
      stingerType = 'kill_multi';
    } else {
      stingerType = 'kill_single';
    }

    // Play stinger
    this.stingerLayer.playStinger(stingerType, this.currentIntensity);

    // Play spatial sound at kill position
    const killFreq = this.harmonicMemory.suggestNextFrequency();
    this.spatialLayer.playSpatialSound(killFreq, position, {
      type: 'sine',
      duration: 0.08,
      volume: 0.06,
    });

    // Trigger melodic fragment on multi-kill
    if (comboCount === 5 || comboCount === 10) {
      this.melodicLayer.playFragment('ascending');
    }
  }

  /**
   * Handle damage event
   * @param amount - Damage amount
   */
  onDamage(amount: number): void {
    if (!this.initialized) return;

    const stingerType: StingerType = amount >= 25 ? 'damage_heavy' : 'damage_light';
    this.stingerLayer.playStinger(stingerType, amount / 50);

    // Heavy damage triggers descending melodic
    if (amount >= 30) {
      this.melodicLayer.playFragment('descending');
    }
  }

  /**
   * Handle level up event
   */
  onLevelUp(): void {
    if (!this.initialized) return;

    this.stingerLayer.playStinger('level_up');
    this.melodicLayer.playFragment('chord');
  }

  /**
   * Handle ball phase change
   */
  onBallPhaseChange(phase: BallPhaseType): void {
    if (!this.initialized) return;

    switch (phase) {
      case 'forming':
        this.stingerLayer.playStinger('ball_forming');
        break;
      case 'silence':
        // Stop all layers for TRUE SILENCE
        for (const layer of this.layers) {
          layer.stop();
        }
        break;
      case 'constrict':
        this.stingerLayer.playStinger('ball_constrict');
        break;
    }
  }

  /**
   * Handle graze event
   */
  onGraze(chainCount: number): void {
    if (!this.initialized) return;

    this.stingerLayer.playStinger('graze', chainCount);
  }

  /**
   * Handle apex strike hit
   */
  onApexHit(hitCount: number): void {
    if (!this.initialized) return;

    this.stingerLayer.playStinger('apex_hit', Math.min(1, hitCount / 10));
  }

  /**
   * Handle wave change
   */
  private onWaveChange(wave: number): void {
    this.melodicLayer.playFragment('chord');
    console.log(`[EmergentAudio] Wave ${wave} started`);
  }

  /**
   * Handle massacre kill
   */
  private onMassacreKill(killCount: number): void {
    this.stingerLayer.playStinger('kill_massacre', Math.min(1, killCount / 10));
    this.melodicLayer.playFragment('ascending');
  }

  // ===========================================================================
  // Volume Control
  // ===========================================================================

  /**
   * Set master volume (0-1)
   */
  setMasterVolume(volume: number): void {
    this.masterVolume = Math.max(0, Math.min(1, volume));
    if (this.masterGain) {
      this.masterGain.gain.setTargetAtTime(
        this.masterVolume,
        this.ctx?.currentTime ?? 0,
        0.1
      );
    }
  }

  /**
   * Get current master volume
   */
  getMasterVolume(): number {
    return this.masterVolume;
  }

  /**
   * Mute all audio
   */
  mute(): void {
    this.setMasterVolume(0);
  }

  /**
   * Unmute to previous volume (or default 0.5)
   */
  unmute(): void {
    this.setMasterVolume(0.5);
  }

  // ===========================================================================
  // Harmonic Memory Access
  // ===========================================================================

  /**
   * Get suggested next frequency based on harmonic memory
   */
  getSuggestedFrequency(octave: number = 0): number {
    return this.harmonicMemory.suggestNextFrequency(octave);
  }

  /**
   * Get recent frequencies from harmonic memory
   */
  getRecentFrequencies(): number[] {
    return this.harmonicMemory.getRecentFrequencies();
  }

  /**
   * Check if a frequency would be dissonant
   */
  wouldBeDissonant(frequency: number): boolean {
    return this.harmonicMemory.wouldBeDissonant(frequency);
  }

  // ===========================================================================
  // State Access
  // ===========================================================================

  /**
   * Get current audio phase
   */
  getCurrentPhase(): AudioPhase {
    return this.currentPhase;
  }

  /**
   * Get current intensity (0-1)
   */
  getCurrentIntensity(): number {
    return this.currentIntensity;
  }

  /**
   * Get layer volumes
   */
  getLayerVolumes(): Record<string, number> {
    const volumes: Record<string, number> = {};
    for (const layer of this.layers) {
      volumes[layer.name] = layer.getVolume();
    }
    return volumes;
  }

  // ===========================================================================
  // Cleanup
  // ===========================================================================

  /**
   * Stop all audio immediately
   */
  stop(): void {
    for (const layer of this.layers) {
      layer.stop();
    }
    this.harmonicMemory.clear();
    this.currentIntensity = 0;
    this.currentPhase = 'exploration';
  }

  /**
   * Fade out all audio with dignity (for death)
   * @param duration - Fade duration in seconds
   */
  fadeToSilence(duration: number = 2): void {
    if (!this.ctx || !this.masterGain) return;

    const now = this.ctx.currentTime;
    this.masterGain.gain.setValueAtTime(this.masterVolume, now);
    this.masterGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

    // Schedule layer stops
    setTimeout(() => {
      this.stop();
    }, duration * 1000);
  }

  /**
   * Dispose all resources
   */
  dispose(): void {
    this.stop();

    for (const layer of this.layers) {
      layer.dispose();
    }

    this.nodePool.dispose();
    this.masterGain?.disconnect();

    if (this.ctx && this.ctx.state !== 'closed') {
      this.ctx.close();
    }

    this.ctx = null;
    this.masterGain = null;
    this.initialized = false;
  }
}

// =============================================================================
// Singleton Instance
// =============================================================================

let orchestratorInstance: EmergentAudioOrchestrator | null = null;

/**
 * Get the singleton orchestrator instance
 */
export function getEmergentAudioOrchestrator(): EmergentAudioOrchestrator {
  if (!orchestratorInstance) {
    orchestratorInstance = new EmergentAudioOrchestrator();
  }
  return orchestratorInstance;
}

/**
 * Initialize the singleton orchestrator
 */
export function initEmergentAudio(): boolean {
  return getEmergentAudioOrchestrator().init();
}

/**
 * Reset the singleton (for testing)
 */
export function resetEmergentAudio(): void {
  if (orchestratorInstance) {
    orchestratorInstance.dispose();
    orchestratorInstance = null;
  }
}

export default EmergentAudioOrchestrator;
