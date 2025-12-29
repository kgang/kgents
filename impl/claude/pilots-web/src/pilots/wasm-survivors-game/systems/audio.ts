/**
 * Audio System with DEBUG API for PLAYER verification
 *
 * "Every kill should sound like biting into a perfect apple."
 * "THE BALL forming should create physical dread."
 * "Silence should be terrifying."
 *
 * AUDIO ARCHITECT TRANSFORMATION (Run 036):
 * - Layered kill sounds for ASMR satisfaction (3 layers per kill)
 * - TRUE SILENCE during THE BALL (no sound at all = DREAD)
 * - Multi-kill escalation with pitch/volume ramping
 * - Spatial audio (stereo panning based on position)
 *
 * Web Audio API with procedural sound generation.
 * No external audio files - all sounds synthesized.
 *
 * DEBUG API: Exposes audio state for automated testing via Playwright.
 */

import type { EnemyType, KillTier, BallPhaseType, Mood, Vector2 } from '../types';

// =============================================================================
// Audio Context Management
// =============================================================================

let audioContext: AudioContext | null = null;
let masterGain: GainNode | null = null;
let isAudioEnabled = false;

// =============================================================================
// LAYERED KILL SOUND SYSTEM (ASMR Crunch)
// =============================================================================

/**
 * Layered kill sound configuration.
 * THREE layers create ASMR satisfaction:
 * - Layer 1: CRUNCH (initial impact, noise-based)
 * - Layer 2: SNAP/SHELL (high-freq attack transient)
 * - Layer 3: DECAY/THUD (low-freq sustain)
 *
 * "Every kill should sound like biting into a perfect apple."
 */
interface SoundLayer {
  freqRange: [number, number];
  type: 'noise' | 'sine' | 'triangle' | 'sawtooth' | 'square';
  duration: number;
  volume: number;
}

interface KillSoundConfig {
  crunch: SoundLayer;
  snap?: SoundLayer;
  shell?: SoundLayer;
  splat?: SoundLayer;
  decay?: SoundLayer;
  thud?: SoundLayer;
  drip?: SoundLayer;
  harmonic?: SoundLayer;
  pitchVariation: [number, number];
  masterVolume: number;
}

export const KILL_SOUND_LAYERS: Record<EnemyType, KillSoundConfig> = {
  worker: {
    crunch: { freqRange: [300, 450], type: 'noise', duration: 0.05, volume: 0.4 },
    snap: { freqRange: [800, 1200], type: 'sine', duration: 0.02, volume: 0.3 },
    decay: { freqRange: [100, 150], type: 'triangle', duration: 0.12, volume: 0.2 },
    pitchVariation: [0.9, 1.1],
    masterVolume: 0.5,
  },
  scout: {
    crunch: { freqRange: [350, 500], type: 'noise', duration: 0.04, volume: 0.35 },
    snap: { freqRange: [900, 1400], type: 'sine', duration: 0.02, volume: 0.35 },
    decay: { freqRange: [120, 180], type: 'triangle', duration: 0.1, volume: 0.15 },
    pitchVariation: [0.95, 1.15],
    masterVolume: 0.45,
  },
  guard: {
    crunch: { freqRange: [150, 250], type: 'noise', duration: 0.08, volume: 0.5 },
    shell: { freqRange: [400, 600], type: 'sawtooth', duration: 0.04, volume: 0.4 },
    thud: { freqRange: [40, 70], type: 'sine', duration: 0.2, volume: 0.5 },
    pitchVariation: [0.85, 1.0],
    masterVolume: 0.7,
  },
  propolis: {
    crunch: { freqRange: [200, 350], type: 'noise', duration: 0.06, volume: 0.4 },
    splat: { freqRange: [100, 200], type: 'sawtooth', duration: 0.08, volume: 0.35 },
    drip: { freqRange: [60, 100], type: 'sine', duration: 0.25, volume: 0.3 },
    pitchVariation: [0.9, 1.05],
    masterVolume: 0.55,
  },
  royal: {
    crunch: { freqRange: [100, 200], type: 'noise', duration: 0.1, volume: 0.6 },
    shell: { freqRange: [300, 500], type: 'sawtooth', duration: 0.06, volume: 0.5 },
    thud: { freqRange: [30, 50], type: 'sine', duration: 0.3, volume: 0.6 },
    harmonic: { freqRange: [150, 250], type: 'sine', duration: 0.15, volume: 0.3 },
    pitchVariation: [0.8, 0.95],
    masterVolume: 0.8,
  },
  // Legacy type mappings (for backwards compatibility)
  basic: {
    crunch: { freqRange: [300, 450], type: 'noise', duration: 0.05, volume: 0.4 },
    snap: { freqRange: [800, 1200], type: 'sine', duration: 0.02, volume: 0.3 },
    decay: { freqRange: [100, 150], type: 'triangle', duration: 0.12, volume: 0.2 },
    pitchVariation: [0.9, 1.1],
    masterVolume: 0.5,
  },
  fast: {
    crunch: { freqRange: [350, 500], type: 'noise', duration: 0.04, volume: 0.35 },
    snap: { freqRange: [900, 1400], type: 'sine', duration: 0.02, volume: 0.35 },
    decay: { freqRange: [120, 180], type: 'triangle', duration: 0.1, volume: 0.15 },
    pitchVariation: [0.95, 1.15],
    masterVolume: 0.45,
  },
  tank: {
    crunch: { freqRange: [150, 250], type: 'noise', duration: 0.08, volume: 0.5 },
    shell: { freqRange: [400, 600], type: 'sawtooth', duration: 0.04, volume: 0.4 },
    thud: { freqRange: [40, 70], type: 'sine', duration: 0.2, volume: 0.5 },
    pitchVariation: [0.85, 1.0],
    masterVolume: 0.7,
  },
  boss: {
    crunch: { freqRange: [100, 200], type: 'noise', duration: 0.1, volume: 0.6 },
    shell: { freqRange: [300, 500], type: 'sawtooth', duration: 0.06, volume: 0.5 },
    thud: { freqRange: [30, 50], type: 'sine', duration: 0.3, volume: 0.6 },
    harmonic: { freqRange: [150, 250], type: 'sine', duration: 0.15, volume: 0.3 },
    pitchVariation: [0.8, 0.95],
    masterVolume: 0.8,
  },
  spitter: {
    crunch: { freqRange: [200, 350], type: 'noise', duration: 0.06, volume: 0.4 },
    splat: { freqRange: [100, 200], type: 'sawtooth', duration: 0.08, volume: 0.35 },
    drip: { freqRange: [60, 100], type: 'sine', duration: 0.25, volume: 0.3 },
    pitchVariation: [0.9, 1.05],
    masterVolume: 0.55,
  },
  colossal_tide: {
    crunch: { freqRange: [100, 200], type: 'noise', duration: 0.1, volume: 0.6 },
    shell: { freqRange: [300, 500], type: 'sawtooth', duration: 0.06, volume: 0.5 },
    thud: { freqRange: [30, 50], type: 'sine', duration: 0.3, volume: 0.6 },
    harmonic: { freqRange: [150, 250], type: 'sine', duration: 0.15, volume: 0.3 },
    pitchVariation: [0.8, 0.95],
    masterVolume: 0.8,
  },
};

// =============================================================================
// MULTI-KILL ESCALATION SYSTEM
// =============================================================================

/**
 * Multi-kill audio escalation.
 * Each consecutive kill sounds MORE satisfying.
 * "The dopamine hit should ESCALATE."
 */
export const MULTI_KILL_AUDIO = {
  pitchScale: 1.05,      // Each kill 5% higher
  maxPitch: 1.5,         // Cap at 50% higher
  volumeScale: 1.03,     // Each kill 3% louder
  maxVolume: 1.0,        // Cap at unity

  thresholds: {
    3: { type: 'harmonic' as const, interval: 1.5, volume: 0.2 },
    5: { type: 'sting' as const, freq: 1200, duration: 0.08, volume: 0.4 },
    8: { type: 'chord' as const, intervals: [1, 1.25, 1.5], duration: 0.15, volume: 0.5 },
    10: { type: 'fanfare' as const, notes: [400, 500, 600, 800], duration: 0.3, volume: 0.6 },
  },

  windowMs: 150,  // Kills within 150ms are "consecutive"
};

// =============================================================================
// SPATIAL AUDIO CONFIGURATION
// =============================================================================

export interface SpatialAudioConfig {
  playerPosition: Vector2;
  listenerRange: number;  // Max distance for audio (600px default)
}

let spatialConfig: SpatialAudioConfig | null = null;

/**
 * Set spatial audio configuration (call each frame with player position).
 */
export function setSpatialConfig(config: SpatialAudioConfig): void {
  spatialConfig = config;
}

/**
 * Get stereo panning position from source position.
 * @returns -1 (hard left) to 1 (hard right)
 */
export function getStereoPosition(sourcePosition: Vector2): number {
  if (!spatialConfig) return 0;
  const dx = sourcePosition.x - spatialConfig.playerPosition.x;
  return Math.max(-1, Math.min(1, dx / (spatialConfig.listenerRange / 2)));
}

/**
 * Get volume attenuation based on distance.
 * @returns 0 (silent) to 1 (full volume)
 */
export function getDistanceVolume(sourcePosition: Vector2): number {
  if (!spatialConfig) return 1;
  const dx = sourcePosition.x - spatialConfig.playerPosition.x;
  const dy = sourcePosition.y - spatialConfig.playerPosition.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  return Math.max(0, 1 - (dist / spatialConfig.listenerRange));
}

// =============================================================================
// THE BALL AUDIO PHASES (TRUE SILENCE)
// =============================================================================

/**
 * THE BALL audio phase configuration.
 * "THE BALL forming should create physical dread."
 * "Silence should be terrifying."
 */
export const BALL_AUDIO_PHASES = {
  forming: {
    buzz: {
      startVolume: 0.2,
      endVolume: 1.0,
      curve: 'exponential',
      startFreq: 100,
      endFreq: 400,
      duration: 10000,
    },
    heartbeat: {
      freq: 60,
      rate: 1.5,
      volume: 0.15,
      startTime: 5000,
    },
  },
  sphere: {
    buzz: { volume: 1.0, freq: 400, duration: 5000 },
    surround: { panSpeed: 0.5, enabled: true },
  },
  silence: {
    duration: 3000,
    // TRUE SILENCE - NO AUDIO AT ALL
    // This creates DREAD
  },
  constrict: {
    bassNote: { freq: 40, attack: 0.1, volume: 0.8, pitchRise: { start: 40, end: 80 } },
    crackle: { rate: 8, freqRange: [2000, 4000] as [number, number], volume: 0.3, randomness: 0.5 },
    duration: 2000,
  },
  death: {
    sizzle: { type: 'filteredNoise', filterFreq: 3000, filterQ: 1, duration: 2000 },
    respect: { freq: 50, duration: 0.5, volume: 0.4, delay: 1800 },
  },
};

// =============================================================================
// DEBUG: Audio Event Logging (for PLAYER verification)
// =============================================================================

interface AudioLogEntry {
  time: number;
  event: string;
  params: Record<string, unknown>;
}

const audioLog: AudioLogEntry[] = [];
const MAX_LOG_ENTRIES = 50;
let activeSoundCount = 0;

function logAudioEvent(event: string, params: Record<string, unknown> = {}): void {
  const entry: AudioLogEntry = {
    time: audioContext?.currentTime ?? Date.now() / 1000,
    event,
    params,
  };
  audioLog.push(entry);
  // Keep only the last MAX_LOG_ENTRIES
  if (audioLog.length > MAX_LOG_ENTRIES) {
    audioLog.shift();
  }
}

// Track active sounds for state reporting
function trackSoundStart(): void {
  activeSoundCount++;
}

function trackSoundEnd(): void {
  activeSoundCount = Math.max(0, activeSoundCount - 1);
}

// =============================================================================
// DEBUG: AnalyserNode for Level Detection
// =============================================================================

let analyser: AnalyserNode | null = null;
let analyserData: Uint8Array | null = null;

// =============================================================================
// DEBUG API Functions (exported for window exposure)
// =============================================================================

/**
 * Get current audio system state.
 * Returns context state, isEnabled, masterVolume, and active sound info.
 */
export function DEBUG_GET_AUDIO_STATE(): {
  contextState: string;
  isEnabled: boolean;
  masterVolume: number;
  activeSoundCount: number;
  sampleRate: number | null;
  analyserConnected: boolean;
} {
  return {
    contextState: audioContext?.state ?? 'not_initialized',
    isEnabled: isAudioEnabled,
    masterVolume: masterGain?.gain.value ?? 0,
    activeSoundCount,
    sampleRate: audioContext?.sampleRate ?? null,
    analyserConnected: analyser !== null,
  };
}

/**
 * Get current audio output level (0-255 scale).
 * Uses AnalyserNode to measure actual audio activity.
 * Returns 0 if no analyser or audio not playing.
 */
export function DEBUG_GET_AUDIO_LEVEL(): number {
  if (!analyser || !analyserData) return 0;

  analyser.getByteTimeDomainData(analyserData);

  // Calculate RMS (root mean square) level
  let sum = 0;
  for (let i = 0; i < analyserData.length; i++) {
    const value = (analyserData[i] - 128) / 128; // Normalize to -1 to 1
    sum += value * value;
  }
  const rms = Math.sqrt(sum / analyserData.length);

  // Scale to 0-255 (rms is typically 0-1)
  return Math.min(255, Math.round(rms * 255 * 2));
}

/**
 * Get the last N audio events (default 50, the max stored).
 * Each event includes timestamp, event name, and parameters.
 */
export function DEBUG_GET_AUDIO_LOG(): AudioLogEntry[] {
  return [...audioLog]; // Return a copy
}

/**
 * Clear the audio event log.
 * Useful for isolating events in specific test scenarios.
 */
export function DEBUG_CLEAR_AUDIO_LOG(): void {
  audioLog.length = 0;
}

// =============================================================================
// Initialization
// =============================================================================

/**
 * Initialize the audio context.
 * Must be called after user interaction (browser autoplay policy).
 */
export function initAudio(): boolean {
  if (audioContext) return true;

  try {
    audioContext = new AudioContext();
    masterGain = audioContext.createGain();
    masterGain.gain.value = 0.5; // Master volume

    // Set up AnalyserNode for level detection (DEBUG)
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    analyserData = new Uint8Array(analyser.frequencyBinCount);

    // Route: masterGain -> analyser -> destination
    masterGain.connect(analyser);
    analyser.connect(audioContext.destination);

    isAudioEnabled = true;
    logAudioEvent('init', { sampleRate: audioContext.sampleRate });
    return true;
  } catch (e) {
    console.warn('Audio initialization failed:', e);
    logAudioEvent('init_failed', { error: String(e) });
    return false;
  }
}

/**
 * Resume audio context (needed after user interaction).
 */
export function resumeAudio(): void {
  if (audioContext?.state === 'suspended') {
    audioContext.resume();
    logAudioEvent('resume', { previousState: 'suspended' });
  }
}

/**
 * Set master volume (0-1).
 */
export function setMasterVolume(volume: number): void {
  const clampedVolume = Math.max(0, Math.min(1, volume));
  if (masterGain) {
    masterGain.gain.value = clampedVolume;
    logAudioEvent('setMasterVolume', { volume: clampedVolume });
  }
}

// =============================================================================
// Sound Generators
// =============================================================================

/**
 * Create white noise for crunch sounds.
 * White noise is essential for ASMR-level kill satisfaction.
 */
function createWhiteNoise(
  ctx: AudioContext,
  duration: number,
): AudioBufferSourceNode {
  const bufferSize = Math.floor(ctx.sampleRate * duration);
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);

  for (let i = 0; i < bufferSize; i++) {
    data[i] = Math.random() * 2 - 1;
  }

  const source = ctx.createBufferSource();
  source.buffer = buffer;
  return source;
}

/**
 * Create filtered noise for sizzle/crackle sounds.
 */
function createFilteredNoise(
  ctx: AudioContext,
  duration: number,
  filterFreq: number,
  filterQ: number = 1,
): { source: AudioBufferSourceNode; filter: BiquadFilterNode } {
  const source = createWhiteNoise(ctx, duration);
  const filter = ctx.createBiquadFilter();
  filter.type = 'bandpass';
  filter.frequency.value = filterFreq;
  filter.Q.value = filterQ;
  source.connect(filter);
  return { source, filter };
}

/**
 * Get random frequency within a range.
 */
function getRandomFreq(range: [number, number]): number {
  return range[0] + Math.random() * (range[1] - range[0]);
}

/**
 * Get random pitch multiplier within a range.
 */
function getRandomPitch(range: [number, number]): number {
  return range[0] + Math.random() * (range[1] - range[0]);
}

/**
 * Create a stereo panner node for spatial audio.
 */
function createSpatialNode(
  ctx: AudioContext,
  sourcePosition?: Vector2,
): { panner: StereoPannerNode; distanceGain: GainNode } {
  const panner = ctx.createStereoPanner();
  const distanceGain = ctx.createGain();

  if (sourcePosition) {
    panner.pan.value = getStereoPosition(sourcePosition);
    distanceGain.gain.value = getDistanceVolume(sourcePosition);
  } else {
    panner.pan.value = 0;
    distanceGain.gain.value = 1;
  }

  panner.connect(distanceGain);
  return { panner, distanceGain };
}

/**
 * Create a quick noise burst (for crunch/impact sounds).
 * LEGACY: Kept for potential debugging/future use. Superseded by layered sounds.
 * @deprecated Use playSoundLayer with 'noise' type instead
 */
function _createNoiseOscillator(
  ctx: AudioContext,
  duration: number,
  frequency: number,
  type: OscillatorType = 'sawtooth',
): { oscillator: OscillatorNode; gain: GainNode } {
  const oscillator = ctx.createOscillator();
  const gain = ctx.createGain();

  oscillator.type = type;
  oscillator.frequency.value = frequency;

  gain.gain.setValueAtTime(0.3, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);

  oscillator.connect(gain);

  return { oscillator, gain };
}

// Suppress unused warning - kept for debugging
void _createNoiseOscillator;

/**
 * Create a buzz sound (for bee-related audio).
 */
function createBuzz(
  ctx: AudioContext,
  baseFreq: number,
  volume: number,
  duration: number,
): { oscillators: OscillatorNode[]; gains: GainNode[] } {
  // Create multiple oscillators for rich buzz
  const oscillators: OscillatorNode[] = [];
  const gains: GainNode[] = [];

  // Base frequency
  const osc1 = ctx.createOscillator();
  osc1.type = 'sawtooth';
  osc1.frequency.value = baseFreq;

  // Slight detune for richness
  const osc2 = ctx.createOscillator();
  osc2.type = 'sawtooth';
  osc2.frequency.value = baseFreq * 1.01;

  // Sub harmonic
  const osc3 = ctx.createOscillator();
  osc3.type = 'sine';
  osc3.frequency.value = baseFreq * 0.5;

  [osc1, osc2, osc3].forEach((osc) => {
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(volume * 0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);
    osc.connect(gain);
    oscillators.push(osc);
    gains.push(gain);
  });

  return { oscillators, gains };
}

// =============================================================================
// Game Event Sounds
// =============================================================================

/**
 * Play a single sound layer with proper envelope.
 */
function playSoundLayer(
  ctx: AudioContext,
  destination: AudioNode,
  layer: SoundLayer,
  pitchMult: number,
  volumeMult: number,
): void {
  const freq = getRandomFreq(layer.freqRange) * pitchMult;
  const duration = layer.duration;
  const volume = layer.volume * volumeMult;

  if (layer.type === 'noise') {
    // Use white noise for crunch
    const noise = createWhiteNoise(ctx, duration);
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();

    filter.type = 'lowpass';
    filter.frequency.value = freq * 2;  // Filter cutoff above fundamental

    gain.gain.setValueAtTime(volume, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(destination);
    noise.start();
    noise.stop(ctx.currentTime + duration);
  } else {
    // Use oscillator for tonal sounds
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = layer.type as OscillatorType;
    osc.frequency.value = freq;

    gain.gain.setValueAtTime(volume, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);

    osc.connect(gain);
    gain.connect(destination);
    osc.start();
    osc.stop(ctx.currentTime + duration);
  }
}

/**
 * Play bonus sound for multi-kill thresholds.
 */
function playBonusSound(
  ctx: AudioContext,
  destination: AudioNode,
  config: { type: string; [key: string]: unknown },
): void {
  switch (config.type) {
    case 'harmonic': {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = 600 * (config.interval as number);
      gain.gain.setValueAtTime(config.volume as number, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
      osc.connect(gain);
      gain.connect(destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.2);
      break;
    }
    case 'sting': {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = config.freq as number;
      gain.gain.setValueAtTime(config.volume as number, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + (config.duration as number));
      osc.connect(gain);
      gain.connect(destination);
      osc.start();
      osc.stop(ctx.currentTime + (config.duration as number));
      break;
    }
    case 'chord': {
      const intervals = config.intervals as number[];
      const duration = config.duration as number;
      const volume = config.volume as number;
      intervals.forEach((interval) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.value = 400 * interval;
        gain.gain.setValueAtTime(volume / intervals.length, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);
        osc.connect(gain);
        gain.connect(destination);
        osc.start();
        osc.stop(ctx.currentTime + duration);
      });
      break;
    }
    case 'fanfare': {
      const notes = config.notes as number[];
      const duration = config.duration as number;
      const volume = config.volume as number;
      notes.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const startTime = ctx.currentTime + i * 0.06;
        osc.type = 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0, startTime);
        gain.gain.linearRampToValueAtTime(volume, startTime + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.01, startTime + duration);
        osc.connect(gain);
        gain.connect(destination);
        osc.start(startTime);
        osc.stop(startTime + duration);
      });
      break;
    }
  }
}

/**
 * Play LAYERED kill sound with ASMR crunch.
 *
 * This is the TRANSFORMED kill sound:
 * - THREE layers playing simultaneously
 * - Pitch randomization for organic feel
 * - Multi-kill escalation (pitch/volume ramping)
 * - Spatial audio (stereo panning)
 *
 * "Every kill should sound like biting into a perfect apple."
 */
export function playLayeredKillSound(
  enemyType: EnemyType,
  tier: KillTier,
  comboCount: number = 1,
  sourcePosition?: Vector2,
): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;

  const ctx = audioContext;
  const config = KILL_SOUND_LAYERS[enemyType];

  logAudioEvent('playLayeredKillSound', { enemyType, tier, comboCount, spatial: !!sourcePosition });
  trackSoundStart();

  // Tier multipliers
  const tierMult = { single: 1, multi: 1.2, massacre: 1.5 }[tier];

  // Multi-kill escalation
  const pitchMult = Math.min(
    MULTI_KILL_AUDIO.maxPitch,
    Math.pow(MULTI_KILL_AUDIO.pitchScale, comboCount - 1),
  );
  const volumeMult = Math.min(
    MULTI_KILL_AUDIO.maxVolume,
    Math.pow(MULTI_KILL_AUDIO.volumeScale, comboCount - 1),
  ) * tierMult;

  // Random pitch variation for organic feel
  const pitchVariation = getRandomPitch(config.pitchVariation);
  const finalPitch = pitchMult * pitchVariation;

  // Create spatial audio node
  const { panner, distanceGain } = createSpatialNode(ctx, sourcePosition);
  distanceGain.connect(masterGain);

  // Create master gain for this kill
  const killGain = ctx.createGain();
  killGain.gain.value = config.masterVolume;
  killGain.connect(panner);

  // Play all layers simultaneously
  // Layer 1: CRUNCH (always present)
  playSoundLayer(ctx, killGain, config.crunch, finalPitch, volumeMult);

  // Layer 2: SNAP/SHELL/SPLAT (attack transient)
  if (config.snap) playSoundLayer(ctx, killGain, config.snap, finalPitch, volumeMult);
  if (config.shell) playSoundLayer(ctx, killGain, config.shell, finalPitch, volumeMult);
  if (config.splat) playSoundLayer(ctx, killGain, config.splat, finalPitch, volumeMult);

  // Layer 3: DECAY/THUD/DRIP (sustain)
  if (config.decay) playSoundLayer(ctx, killGain, config.decay, finalPitch, volumeMult);
  if (config.thud) playSoundLayer(ctx, killGain, config.thud, finalPitch, volumeMult);
  if (config.drip) playSoundLayer(ctx, killGain, config.drip, finalPitch, volumeMult);

  // Extra layer for royal enemies
  if (config.harmonic) playSoundLayer(ctx, killGain, config.harmonic, finalPitch, volumeMult);

  // Check multi-kill thresholds for bonus sounds
  const thresholds = MULTI_KILL_AUDIO.thresholds as Record<number, { type: string; [key: string]: unknown }>;
  if (thresholds[comboCount]) {
    playBonusSound(ctx, killGain, thresholds[comboCount]);
  }

  // Calculate max duration for cleanup
  const allDurations = [
    config.crunch.duration,
    config.snap?.duration ?? 0,
    config.shell?.duration ?? 0,
    config.splat?.duration ?? 0,
    config.decay?.duration ?? 0,
    config.thud?.duration ?? 0,
    config.drip?.duration ?? 0,
    config.harmonic?.duration ?? 0,
  ];
  const maxDuration = Math.max(...allDurations) * 1000;

  setTimeout(() => trackSoundEnd(), maxDuration);
}

/**
 * Play kill sound based on enemy type and kill tier.
 * LEGACY: Kept for backward compatibility, now calls playLayeredKillSound.
 */
export function playKillSound(enemyType: EnemyType, tier: KillTier): void {
  playLayeredKillSound(enemyType, tier, 1);
}

/**
 * Play damage taken sound.
 */
export function playDamageSound(): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;
  logAudioEvent('playDamageSound', {});
  trackSoundStart();

  const ctx = audioContext;

  // Sharp, attention-grabbing sound
  const osc = ctx.createOscillator();
  osc.type = 'square';
  osc.frequency.setValueAtTime(300, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + 0.1);

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.3, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start();
  osc.stop(ctx.currentTime + 0.15);

  setTimeout(() => trackSoundEnd(), 150);
}

/**
 * Play dash sound (whoosh).
 */
export function playDashSound(): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;
  logAudioEvent('playDashSound', {});
  trackSoundStart();

  const ctx = audioContext;

  // Whoosh = noise + pitch sweep
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(200, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 0.15);

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.15, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start();
  osc.stop(ctx.currentTime + 0.2);

  setTimeout(() => trackSoundEnd(), 200);
}

/**
 * Play XP collection sound (bright chime).
 */
export function playXPSound(): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;
  logAudioEvent('playXPSound', {});
  trackSoundStart();

  const ctx = audioContext;

  // Bright ascending chime
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(800, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.1);

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.1, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start();
  osc.stop(ctx.currentTime + 0.15);

  setTimeout(() => trackSoundEnd(), 150);
}

/**
 * Play level up sound (triumphant).
 */
export function playLevelUpSound(): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;
  logAudioEvent('playLevelUpSound', {});
  trackSoundStart();

  const ctx = audioContext;

  // Ascending arpeggio
  const notes = [400, 500, 600, 800];
  notes.forEach((freq, i) => {
    const osc = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = freq;

    const gain = ctx.createGain();
    const startTime = ctx.currentTime + i * 0.08;
    gain.gain.setValueAtTime(0, startTime);
    gain.gain.linearRampToValueAtTime(0.15, startTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.01, startTime + 0.2);

    osc.connect(gain);
    gain.connect(masterGain!);
    osc.start(startTime);
    osc.stop(startTime + 0.2);
  });

  setTimeout(() => trackSoundEnd(), 500);
}

// =============================================================================
// THE BALL Audio (TB-7: Audio Escalation)
// =============================================================================

let buzzOscillators: OscillatorNode[] = [];
let buzzGains: GainNode[] = [];
let currentBuzzVolume = 0;

/**
 * Start or update the coordination buzz.
 * Volume and pitch increase with coordination level.
 */
export function updateCoordinationBuzz(level: number): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;

  const targetVolume = Math.min(0.15, level * 0.015);

  // If buzz not playing and should be
  if (level > 2 && buzzOscillators.length === 0) {
    logAudioEvent('buzzStart', { level, targetVolume });
    const { oscillators, gains } = createBuzz(
      audioContext,
      100 + level * 10,
      targetVolume,
      10, // Long duration, we'll manage it
    );

    buzzOscillators = oscillators;
    buzzGains = gains;

    oscillators.forEach((osc, i) => {
      gains[i].connect(masterGain!);
      osc.start();
    });
    trackSoundStart();
  }

  // Update volume if playing
  buzzGains.forEach((gain) => {
    gain.gain.setTargetAtTime(targetVolume, audioContext!.currentTime, 0.1);
  });

  currentBuzzVolume = targetVolume;
}

/**
 * Stop all buzz sounds (for THE SILENCE).
 */
export function stopBuzz(): void {
  if (buzzOscillators.length > 0) {
    logAudioEvent('buzzStop', { oscillatorCount: buzzOscillators.length });
  }
  buzzOscillators.forEach((osc) => {
    try {
      osc.stop();
    } catch {
      // Ignore if already stopped
    }
  });
  if (buzzOscillators.length > 0) {
    trackSoundEnd();
  }
  buzzOscillators = [];
  buzzGains = [];
  currentBuzzVolume = 0;
}

/**
 * Play THE BALL phase audio.
 */
export function playBallPhaseAudio(phase: BallPhaseType): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;
  logAudioEvent('playBallPhaseAudio', { phase });

  const ctx = audioContext;

  switch (phase) {
    case 'forming':
      // Buzz crescendo handled by updateCoordinationBuzz
      break;

    case 'sphere':
      // Peak buzz - intensity increases
      updateCoordinationBuzz(10);
      break;

    case 'silence':
      // =====================================================================
      // TRUE SILENCE - The ASMR Transformation
      // =====================================================================
      // "Silence should be terrifying."
      //
      // This is THE critical audio design moment. The old code played an
      // "eerie tone" which DEFEATS THE PURPOSE. True silence after the
      // crescendo creates PHYSICAL DREAD. The absence of sound is the sound.
      //
      // NO EERIE TONE. NO DRONE. NOTHING. JUST SILENCE.
      // =====================================================================
      stopBuzz();
      stopAmbient();  // Also stop ambient - TOTAL SILENCE
      logAudioEvent('true_silence_start', { duration: BALL_AUDIO_PHASES.silence.duration });
      // We do NOT trackSoundStart() because there IS no sound
      // The silence itself is the experience
      break;

    case 'constrict': {
      // =====================================================================
      // ENHANCED CONSTRICT - Bass Drop + Cooking Crackle
      // =====================================================================
      // After TRUE SILENCE, this bass drop hits HARD.
      // Temperature-based pitch rise (40Hz -> 80Hz) as they cook you.
      // =====================================================================
      trackSoundStart();

      const config = BALL_AUDIO_PHASES.constrict;
      const now = ctx.currentTime;

      // Deep bass with pitch rise (temperature increasing)
      const bassOsc = ctx.createOscillator();
      bassOsc.type = 'sine';
      bassOsc.frequency.setValueAtTime(config.bassNote.pitchRise.start, now);
      bassOsc.frequency.exponentialRampToValueAtTime(
        config.bassNote.pitchRise.end,
        now + config.duration / 1000,
      );

      const bassGain = ctx.createGain();
      bassGain.gain.setValueAtTime(0, now);
      bassGain.gain.linearRampToValueAtTime(config.bassNote.volume, now + config.bassNote.attack);
      // Pulsing effect
      bassGain.gain.linearRampToValueAtTime(config.bassNote.volume * 0.6, now + 0.5);
      bassGain.gain.linearRampToValueAtTime(config.bassNote.volume, now + 1);
      bassGain.gain.linearRampToValueAtTime(config.bassNote.volume * 0.6, now + 1.5);
      bassGain.gain.linearRampToValueAtTime(config.bassNote.volume, now + 2);

      bassOsc.connect(bassGain);
      bassGain.connect(masterGain);
      bassOsc.start();
      bassOsc.stop(now + config.duration / 1000);

      // Cooking crackle (high-frequency bursts with randomness)
      const crackleCount = Math.floor(config.crackle.rate * (config.duration / 1000));
      for (let i = 0; i < crackleCount; i++) {
        const jitter = (Math.random() - 0.5) * config.crackle.randomness * 100;
        const delay = (i * (config.duration / crackleCount)) + jitter;

        setTimeout(() => {
          if (!audioContext || !masterGain) return;
          const { source, filter } = createFilteredNoise(
            audioContext,
            0.05,
            getRandomFreq(config.crackle.freqRange),
            2,
          );
          const crackleGain = audioContext.createGain();
          crackleGain.gain.setValueAtTime(config.crackle.volume, audioContext.currentTime);
          crackleGain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.05);

          filter.connect(crackleGain);
          crackleGain.connect(masterGain);
          source.start();
          source.stop(audioContext.currentTime + 0.05);
        }, Math.max(0, delay));
      }

      setTimeout(() => trackSoundEnd(), config.duration);
      break;
    }

    case 'death': {
      // =====================================================================
      // ENHANCED DEATH - Sizzle + Respect Pulse
      // =====================================================================
      // Filtered noise sizzle that fades to silence.
      // Ends with a single low "respect" pulse - dignified, not punishing.
      // =====================================================================
      trackSoundStart();

      const config = BALL_AUDIO_PHASES.death;
      const now = ctx.currentTime;

      // Sizzle sound (filtered white noise)
      const { source: sizzleSource, filter: sizzleFilter } = createFilteredNoise(
        ctx,
        config.sizzle.duration / 1000,
        config.sizzle.filterFreq,
        config.sizzle.filterQ,
      );

      const sizzleGain = ctx.createGain();
      sizzleGain.gain.setValueAtTime(0.5, now);
      sizzleGain.gain.exponentialRampToValueAtTime(0.01, now + config.sizzle.duration / 1000);

      sizzleFilter.connect(sizzleGain);
      sizzleGain.connect(masterGain);
      sizzleSource.start();
      sizzleSource.stop(now + config.sizzle.duration / 1000);

      // "Respect" pulse at the end - single low note
      setTimeout(() => {
        if (!audioContext || !masterGain) return;
        const respectOsc = audioContext.createOscillator();
        respectOsc.type = 'sine';
        respectOsc.frequency.value = config.respect.freq;

        const respectGain = audioContext.createGain();
        respectGain.gain.setValueAtTime(0, audioContext.currentTime);
        respectGain.gain.linearRampToValueAtTime(config.respect.volume, audioContext.currentTime + 0.1);
        respectGain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + config.respect.duration);

        respectOsc.connect(respectGain);
        respectGain.connect(masterGain);
        respectOsc.start();
        respectOsc.stop(audioContext.currentTime + config.respect.duration);
      }, config.respect.delay);

      setTimeout(() => trackSoundEnd(), config.sizzle.duration + 200);
      break;
    }
  }
}

// =============================================================================
// Death Audio
// =============================================================================

/**
 * Play death sound (dignified, not punishing).
 */
export function playDeathSound(): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;
  logAudioEvent('playDeathSound', {});
  trackSoundStart();

  stopBuzz();

  const ctx = audioContext;

  // Pure tone fade
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.value = 220; // A3 - mournful but dignified

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.2, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 2);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start();
  osc.stop(ctx.currentTime + 2);

  setTimeout(() => trackSoundEnd(), 2000);
}

// =============================================================================
// Mood-Based Ambient
// =============================================================================

let ambientOsc: OscillatorNode | null = null;
let ambientGain: GainNode | null = null;

/**
 * Stop ambient audio.
 * Used for TRUE SILENCE during THE BALL.
 */
export function stopAmbient(): void {
  if (ambientOsc) {
    logAudioEvent('stopAmbient', {});
    try {
      ambientOsc.stop();
    } catch {
      // Ignore if already stopped
    }
    ambientOsc = null;
    ambientGain = null;
    trackSoundEnd();
  }
}

/**
 * Set the mood-based ambient audio.
 */
export function setMoodAmbient(mood: Mood): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;
  logAudioEvent('setMoodAmbient', { mood });

  // Stop current ambient
  if (ambientOsc) {
    try {
      ambientOsc.stop();
    } catch {
      // Ignore
    }
    ambientOsc = null;
    ambientGain = null;
    trackSoundEnd();
  }

  const ctx = audioContext;

  // Create new ambient based on mood
  ambientOsc = ctx.createOscillator();
  ambientGain = ctx.createGain();
  trackSoundStart();

  switch (mood) {
    case 'god':
      ambientOsc.type = 'sine';
      ambientOsc.frequency.value = 80;
      ambientGain.gain.value = 0.02;
      break;

    case 'flow':
      ambientOsc.type = 'sine';
      ambientOsc.frequency.value = 100;
      ambientGain.gain.value = 0.03;
      break;

    case 'crisis':
      ambientOsc.type = 'sawtooth';
      ambientOsc.frequency.value = 60;
      ambientGain.gain.value = 0.04;
      break;

    case 'tragedy':
      ambientOsc.type = 'sine';
      ambientOsc.frequency.value = 50;
      ambientGain.gain.value = 0.05;
      break;

    case 'prey':
      ambientOsc.type = 'sine';
      ambientOsc.frequency.value = 120;
      ambientGain.gain.value = 0.03;
      break;
  }

  ambientOsc.connect(ambientGain);
  ambientGain.connect(masterGain);
  ambientOsc.start();
}

/**
 * Stop all audio.
 */
export function stopAllAudio(): void {
  logAudioEvent('stopAllAudio', {});
  stopBuzz();
  stopAmbient();
}

// =============================================================================
// Additional Sound Effects
// =============================================================================

/**
 * Play graze sound (near-miss reward).
 * Pitch increases with chain count for escalating satisfaction.
 */
export function playGrazeSound(chainCount: number = 1): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;

  const baseFreq = 1000;
  const pitchMult = 1.0 + (chainCount - 1) * 0.05;  // 5% higher per chain
  const freq = baseFreq * Math.min(pitchMult, 1.5);

  logAudioEvent('playGrazeSound', { chainCount, freq });
  trackSoundStart();

  const ctx = audioContext;
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.value = freq;

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.15, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.08);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start();
  osc.stop(ctx.currentTime + 0.08);

  setTimeout(() => trackSoundEnd(), 80);
}

/**
 * Play honey drip sound (for propolis death effect).
 */
export function playHoneyDripSound(): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;

  logAudioEvent('playHoneyDripSound', {});
  trackSoundStart();

  const ctx = audioContext;

  // Descending "bloop" for drip
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(400, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 0.15);

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0.2, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start();
  osc.stop(ctx.currentTime + 0.2);

  setTimeout(() => trackSoundEnd(), 200);
}

/**
 * Play freeze frame sound (time-stop impact).
 */
export function playFreezeFrameSound(type: 'significant' | 'multi' | 'critical' | 'massacre'): void {
  if (!audioContext || !masterGain || !isAudioEnabled) return;

  logAudioEvent('playFreezeFrameSound', { type });
  trackSoundStart();

  const ctx = audioContext;

  // Different intensity based on type
  const configs = {
    significant: { freq: 200, volume: 0.15, duration: 0.1 },
    multi: { freq: 150, volume: 0.2, duration: 0.15 },
    critical: { freq: 100, volume: 0.25, duration: 0.12 },
    massacre: { freq: 80, volume: 0.3, duration: 0.2 },
  };

  const config = configs[type];

  // Low "impact" thud
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.value = config.freq;

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(config.volume, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + config.duration);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start();
  osc.stop(ctx.currentTime + config.duration);

  setTimeout(() => trackSoundEnd(), config.duration * 1000);
}

// =============================================================================
// Audio State Interface (for game loop)
// =============================================================================

export interface AudioState {
  isEnabled: boolean;
  masterVolume: number;
  buzzVolume: number;
  currentMood: Mood | null;
  isSilent: boolean;  // NEW: True during THE BALL silence phase
}

export function getAudioState(): AudioState {
  return {
    isEnabled: isAudioEnabled,
    masterVolume: masterGain?.gain.value ?? 0,
    buzzVolume: currentBuzzVolume,
    currentMood: null, // Would need to track this
    isSilent: buzzOscillators.length === 0 && ambientOsc === null,
  };
}
