/**
 * Procedural Audio System - C Major Based
 *
 * All sounds derive from C major scale with categorized intervals:
 * - GOOD: Consonant intervals (major 3rd, perfect 5th, major 6th, octave)
 * - BAD: Dissonant intervals (minor 2nd, tritone, minor 7th)
 *
 * Semantic categories use these intervals with procedural variation:
 * - Note selection within scale
 * - Interval stacking from category
 * - Timing/envelope variation
 * - Waveform selection
 *
 * "Every sound tells you if things are going well or poorly."
 */

// =============================================================================
// C Major Scale Definition
// =============================================================================

/**
 * C Major scale frequencies (C4 = middle C)
 * C4, D4, E4, F4, G4, A4, B4, C5
 */
export const C_MAJOR_SCALE = {
  C4: 261.63,
  D4: 293.66,
  E4: 329.63,
  F4: 349.23,
  G4: 392.00,
  A4: 440.00,
  B4: 493.88,
  C5: 523.25,
  // Extended range
  C3: 130.81,
  G3: 196.00,
  C6: 1046.50,
} as const;

/**
 * Scale degrees for procedural selection
 */
export const SCALE_DEGREES = [
  C_MAJOR_SCALE.C4,
  C_MAJOR_SCALE.D4,
  C_MAJOR_SCALE.E4,
  C_MAJOR_SCALE.F4,
  C_MAJOR_SCALE.G4,
  C_MAJOR_SCALE.A4,
  C_MAJOR_SCALE.B4,
  C_MAJOR_SCALE.C5,
];

// =============================================================================
// Interval Categories
// =============================================================================

/**
 * GOOD intervals - consonant, pleasant, rewarding
 * Used for: kills, XP, level up, success states
 */
export const GOOD_INTERVALS = {
  unison: 1,
  majorThird: 5 / 4,      // 1.25 - bright, happy
  perfectFourth: 4 / 3,   // 1.333 - stable
  perfectFifth: 3 / 2,    // 1.5 - powerful, open
  majorSixth: 5 / 3,      // 1.667 - warm, sweet
  octave: 2,              // 2.0 - complete, full
} as const;

/**
 * BAD intervals - dissonant, tense, warning
 * Used for: damage, danger, failure states
 */
export const BAD_INTERVALS = {
  minorSecond: 16 / 15,   // 1.067 - grinding, tense
  tritone: 45 / 32,       // 1.406 - unstable, dread (devil's interval)
  minorSeventh: 9 / 5,    // 1.8 - unresolved, anxious
} as const;

/**
 * Get a random interval from a category
 */
export function getRandomGoodInterval(): number {
  const intervals = Object.values(GOOD_INTERVALS);
  return intervals[Math.floor(Math.random() * intervals.length)];
}

export function getRandomBadInterval(): number {
  const intervals = Object.values(BAD_INTERVALS);
  return intervals[Math.floor(Math.random() * intervals.length)];
}

/**
 * Get a random note from C major scale
 */
export function getRandomScaleNote(octaveOffset: number = 0): number {
  const note = SCALE_DEGREES[Math.floor(Math.random() * SCALE_DEGREES.length)];
  return note * Math.pow(2, octaveOffset);
}

/**
 * Get specific scale degree (0-7 = C to C)
 */
export function getScaleDegree(degree: number, octaveOffset: number = 0): number {
  const wrappedDegree = ((degree % 8) + 8) % 8;
  return SCALE_DEGREES[wrappedDegree] * Math.pow(2, octaveOffset);
}

// =============================================================================
// Procedural Variation Helpers
// =============================================================================

/**
 * Add slight randomness to a value (for humanization)
 */
export function humanize(value: number, variance: number = 0.05): number {
  return value * (1 + (Math.random() - 0.5) * 2 * variance);
}

/**
 * Pick random element from array
 */
function pickRandom<T>(arr: readonly T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * Waveform types for variation
 */
export const GOOD_WAVEFORMS: OscillatorType[] = ['sine', 'triangle'];
export const BAD_WAVEFORMS: OscillatorType[] = ['sawtooth', 'square'];
export const NEUTRAL_WAVEFORMS: OscillatorType[] = ['sine', 'triangle', 'sawtooth'];

// =============================================================================
// Sound Category Types
// =============================================================================

export type SoundCategory = 'good' | 'bad' | 'neutral';

export interface ProceduralSoundConfig {
  category: SoundCategory;
  baseNote?: number;        // Override random note selection
  layerCount?: number;      // Number of harmonic layers (1-3)
  duration?: number;        // Base duration in seconds
  attack?: number;          // Attack time in seconds
  volume?: number;          // Base volume (0-1)
  ascending?: boolean;      // For arpeggios
  spatialPosition?: { x: number; y: number };
}

// =============================================================================
// Core Procedural Sound Generator
// =============================================================================

let audioContext: AudioContext | null = null;
let masterGain: GainNode | null = null;

/**
 * Initialize procedural audio system
 */
export function initProceduralAudio(ctx: AudioContext, master: GainNode): void {
  audioContext = ctx;
  masterGain = master;
}

/**
 * Generate a procedural "good" sound
 * Uses consonant intervals, pleasant waveforms
 */
export function playGoodSound(config: Partial<ProceduralSoundConfig> = {}): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  const baseNote = config.baseNote ?? getRandomScaleNote();
  const layerCount = config.layerCount ?? (Math.random() > 0.5 ? 2 : 1);
  const duration = humanize(config.duration ?? 0.15);
  const attack = config.attack ?? 0.01;
  const volume = config.volume ?? 0.12;
  const waveform = pickRandom(GOOD_WAVEFORMS);

  // Layer 1: Base note
  const osc1 = ctx.createOscillator();
  osc1.type = waveform;
  osc1.frequency.value = baseNote;

  const gain1 = ctx.createGain();
  gain1.gain.setValueAtTime(0, now);
  gain1.gain.linearRampToValueAtTime(volume, now + attack);
  gain1.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc1.connect(gain1);
  gain1.connect(masterGain);
  osc1.start(now);
  osc1.stop(now + duration);

  // Layer 2: Consonant interval (if layered)
  if (layerCount >= 2) {
    const interval = getRandomGoodInterval();
    const osc2 = ctx.createOscillator();
    osc2.type = 'sine'; // Harmonics always sine for clarity
    osc2.frequency.value = baseNote * interval;

    const gain2 = ctx.createGain();
    gain2.gain.setValueAtTime(0, now);
    gain2.gain.linearRampToValueAtTime(volume * 0.4, now + attack);
    gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc2.connect(gain2);
    gain2.connect(masterGain);
    osc2.start(now);
    osc2.stop(now + duration);
  }
}

/**
 * Generate a procedural "bad" sound
 * Uses dissonant intervals, harsher waveforms
 */
export function playBadSound(config: Partial<ProceduralSoundConfig> = {}): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  // Bad sounds use lower notes for weight
  const baseNote = config.baseNote ?? getRandomScaleNote(-1);
  const layerCount = config.layerCount ?? 2;
  const duration = humanize(config.duration ?? 0.12);
  const attack = config.attack ?? 0.005;
  const volume = config.volume ?? 0.15;
  const waveform = pickRandom(BAD_WAVEFORMS);

  // Layer 1: Base note with descending pitch
  const osc1 = ctx.createOscillator();
  osc1.type = waveform;
  osc1.frequency.setValueAtTime(baseNote, now);
  osc1.frequency.exponentialRampToValueAtTime(baseNote * 0.7, now + duration);

  const gain1 = ctx.createGain();
  gain1.gain.setValueAtTime(0, now);
  gain1.gain.linearRampToValueAtTime(volume, now + attack);
  gain1.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc1.connect(gain1);
  gain1.connect(masterGain);
  osc1.start(now);
  osc1.stop(now + duration);

  // Layer 2: Dissonant interval
  if (layerCount >= 2) {
    const interval = getRandomBadInterval();
    const osc2 = ctx.createOscillator();
    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(baseNote * interval, now);
    osc2.frequency.exponentialRampToValueAtTime(baseNote * interval * 0.7, now + duration);

    const gain2 = ctx.createGain();
    gain2.gain.setValueAtTime(0, now);
    gain2.gain.linearRampToValueAtTime(volume * 0.3, now + attack);
    gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc2.connect(gain2);
    gain2.connect(masterGain);
    osc2.start(now);
    osc2.stop(now + duration);
  }
}

// =============================================================================
// Semantic Sound Functions (with procedural variation)
// =============================================================================

/**
 * KILL SOUND - Good, satisfying crunch
 * Procedural: Random note from pentatonic subset + perfect 5th
 */
export function playProceduralKill(intensity: number = 1): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  // Use C major pentatonic for kills (C, D, E, G, A) - always sounds good
  const pentatonic = [C_MAJOR_SCALE.C4, C_MAJOR_SCALE.D4, C_MAJOR_SCALE.E4, C_MAJOR_SCALE.G4, C_MAJOR_SCALE.A4];
  const baseNote = pickRandom(pentatonic) * (0.5 + intensity * 0.5);

  const duration = humanize(0.08 + intensity * 0.04);
  const volume = 0.12 + intensity * 0.08;

  // Layer 1: Impact (noise burst)
  const bufferSize = Math.floor(ctx.sampleRate * 0.04);
  const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const noiseData = noiseBuffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    noiseData[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
  }

  const noise = ctx.createBufferSource();
  noise.buffer = noiseBuffer;

  const noiseFilter = ctx.createBiquadFilter();
  noiseFilter.type = 'lowpass';
  noiseFilter.frequency.value = baseNote * 4;

  const noiseGain = ctx.createGain();
  noiseGain.gain.setValueAtTime(volume * 0.6, now);
  noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);

  noise.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(masterGain);
  noise.start(now);

  // Layer 2: Tonal (perfect 5th for power)
  const osc = ctx.createOscillator();
  osc.type = 'triangle';
  osc.frequency.value = baseNote;

  const oscGain = ctx.createGain();
  oscGain.gain.setValueAtTime(0, now);
  oscGain.gain.linearRampToValueAtTime(volume * 0.4, now + 0.01);
  oscGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc.connect(oscGain);
  oscGain.connect(masterGain);
  osc.start(now);
  osc.stop(now + duration);

  // Layer 3: Fifth harmonic (optional, for bigger kills)
  if (intensity > 0.5) {
    const osc5th = ctx.createOscillator();
    osc5th.type = 'sine';
    osc5th.frequency.value = baseNote * GOOD_INTERVALS.perfectFifth;

    const gain5th = ctx.createGain();
    gain5th.gain.setValueAtTime(0, now);
    gain5th.gain.linearRampToValueAtTime(volume * 0.2, now + 0.01);
    gain5th.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc5th.connect(gain5th);
    gain5th.connect(masterGain);
    osc5th.start(now);
    osc5th.stop(now + duration);
  }
}

/**
 * DAMAGE SOUND - Bad, warning thud
 * Procedural: Low note + tritone or minor 2nd
 */
export function playProceduralDamage(severity: number = 0.5): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  // Low C for weight, or G for variation
  const baseNote = Math.random() > 0.5 ? C_MAJOR_SCALE.C3 : C_MAJOR_SCALE.G3;
  const interval = pickRandom([BAD_INTERVALS.minorSecond, BAD_INTERVALS.tritone]);

  const duration = humanize(0.1 + severity * 0.05);
  const volume = 0.12 + severity * 0.08;

  // Layer 1: Base thud (triangle for softness)
  const osc1 = ctx.createOscillator();
  osc1.type = 'triangle';
  osc1.frequency.setValueAtTime(baseNote, now);
  osc1.frequency.exponentialRampToValueAtTime(baseNote * 0.6, now + duration);

  const gain1 = ctx.createGain();
  gain1.gain.setValueAtTime(volume, now);
  gain1.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc1.connect(gain1);
  gain1.connect(masterGain);
  osc1.start(now);
  osc1.stop(now + duration);

  // Layer 2: Dissonant interval
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(baseNote * interval, now);
  osc2.frequency.exponentialRampToValueAtTime(baseNote * interval * 0.6, now + duration);

  const gain2 = ctx.createGain();
  gain2.gain.setValueAtTime(volume * 0.25, now);
  gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc2.connect(gain2);
  gain2.connect(masterGain);
  osc2.start(now);
  osc2.stop(now + duration);
}

/**
 * XP COLLECT SOUND - Good, bright chime
 * Procedural: Random high note from scale + major 3rd or 6th
 */
export function playProceduralXP(): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  // High notes for brightness (E, G, A, C5 - the "happy" notes)
  const happyNotes = [C_MAJOR_SCALE.E4, C_MAJOR_SCALE.G4, C_MAJOR_SCALE.A4, C_MAJOR_SCALE.C5];
  const baseNote = pickRandom(happyNotes);
  const interval = pickRandom([GOOD_INTERVALS.majorThird, GOOD_INTERVALS.majorSixth]);

  const duration = humanize(0.1);
  const volume = 0.08;

  // Quick ascending pitch for "pickup" feel
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(baseNote * 0.9, now);
  osc.frequency.exponentialRampToValueAtTime(baseNote, now + 0.02);

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0, now);
  gain.gain.linearRampToValueAtTime(volume, now + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start(now);
  osc.stop(now + duration);

  // Harmonic sparkle
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(baseNote * interval * 0.9, now);
  osc2.frequency.exponentialRampToValueAtTime(baseNote * interval, now + 0.02);

  const gain2 = ctx.createGain();
  gain2.gain.setValueAtTime(0, now);
  gain2.gain.linearRampToValueAtTime(volume * 0.4, now + 0.01);
  gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc2.connect(gain2);
  gain2.connect(masterGain);
  osc2.start(now);
  osc2.stop(now + duration);
}

/**
 * LEVEL UP SOUND - Good, triumphant ascending arpeggio
 * Procedural: C major arpeggio with random starting inversion
 */
export function playProceduralLevelUp(): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  // C major chord tones (C, E, G) in different inversions
  const inversions = [
    [C_MAJOR_SCALE.C4, C_MAJOR_SCALE.E4, C_MAJOR_SCALE.G4, C_MAJOR_SCALE.C5],  // Root
    [C_MAJOR_SCALE.E4, C_MAJOR_SCALE.G4, C_MAJOR_SCALE.C5, C_MAJOR_SCALE.E4 * 2],  // 1st
    [C_MAJOR_SCALE.G3, C_MAJOR_SCALE.C4, C_MAJOR_SCALE.E4, C_MAJOR_SCALE.G4],  // 2nd
  ];

  const arpeggio = pickRandom(inversions);
  const noteSpacing = humanize(0.07);
  const noteDuration = humanize(0.18);
  const volume = 0.12;

  arpeggio.forEach((freq, i) => {
    const noteStart = now + i * noteSpacing;

    // Main note
    const osc = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = freq;

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0, noteStart);
    gain.gain.linearRampToValueAtTime(volume, noteStart + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.001, noteStart + noteDuration);

    osc.connect(gain);
    gain.connect(masterGain!);
    osc.start(noteStart);
    osc.stop(noteStart + noteDuration);

    // Perfect 5th above for richness
    const osc5th = ctx.createOscillator();
    osc5th.type = 'sine';
    osc5th.frequency.value = freq * GOOD_INTERVALS.perfectFifth;

    const gain5th = ctx.createGain();
    gain5th.gain.setValueAtTime(0, noteStart);
    gain5th.gain.linearRampToValueAtTime(volume * 0.3, noteStart + 0.015);
    gain5th.gain.exponentialRampToValueAtTime(0.001, noteStart + noteDuration);

    osc5th.connect(gain5th);
    gain5th.connect(masterGain!);
    osc5th.start(noteStart);
    osc5th.stop(noteStart + noteDuration);
  });
}

/**
 * DASH SOUND - Neutral, whoosh with scale-based pitch
 * Procedural: Ascending pitch through scale degrees
 */
export function playProceduralDash(): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  // Start on random scale degree, sweep up
  const startDegree = Math.floor(Math.random() * 4); // 0-3
  const startNote = getScaleDegree(startDegree);
  const endNote = getScaleDegree(startDegree + 3); // Up a 4th

  const duration = humanize(0.15);
  const volume = 0.1;

  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(startNote, now);
  osc.frequency.exponentialRampToValueAtTime(endNote, now + duration * 0.7);

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start(now);
  osc.stop(now + duration);

  // Octave above for shimmer
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(startNote * 2, now);
  osc2.frequency.exponentialRampToValueAtTime(endNote * 2, now + duration * 0.7);

  const gain2 = ctx.createGain();
  gain2.gain.setValueAtTime(volume * 0.2, now);
  gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc2.connect(gain2);
  gain2.connect(masterGain);
  osc2.start(now);
  osc2.stop(now + duration);
}

/**
 * GRAZE SOUND - Exciting near-miss, good undertone
 * Procedural: Quick note with major 6th (exciting but safe)
 */
export function playProceduralGraze(chainCount: number = 1): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  // Pitch rises with chain count (excitement builds)
  const baseDegree = Math.min(chainCount - 1, 4);
  const baseNote = getScaleDegree(baseDegree, 1); // Octave up for brightness

  const duration = humanize(0.06);
  // Run 038: 40% quieter (was 0.1 base, now 0.06)
  const volume = 0.06 + Math.min(chainCount * 0.012, 0.06);

  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.value = baseNote;

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start(now);
  osc.stop(now + duration);

  // Major 6th for "close call but safe" feel
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.value = baseNote * GOOD_INTERVALS.majorSixth;

  const gain2 = ctx.createGain();
  gain2.gain.setValueAtTime(volume * 0.35, now);
  gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc2.connect(gain2);
  gain2.connect(masterGain);
  osc2.start(now);
  osc2.stop(now + duration);
}

/**
 * ENEMY HIT SOUND - Neutral/satisfying impact
 * Procedural: Low thud + noise, slight good interval
 */
export function playProceduralEnemyHit(damage: number = 10): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  // Scale note based on damage (more damage = higher impact)
  const damageNorm = Math.min(damage / 50, 1);
  const baseNote = C_MAJOR_SCALE.C3 * (1 + damageNorm * 0.5);

  const duration = humanize(0.05);
  const volume = 0.08 + damageNorm * 0.06;

  // Quick thud
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(baseNote, now);
  osc.frequency.exponentialRampToValueAtTime(baseNote * 0.5, now + duration);

  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start(now);
  osc.stop(now + duration);

  // Noise burst for texture
  const bufferSize = Math.floor(ctx.sampleRate * 0.02);
  const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const noiseData = noiseBuffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    noiseData[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
  }

  const noise = ctx.createBufferSource();
  noise.buffer = noiseBuffer;

  const noiseFilter = ctx.createBiquadFilter();
  noiseFilter.type = 'bandpass';
  noiseFilter.frequency.value = 600 + damage * 10;
  noiseFilter.Q.value = 2;

  const noiseGain = ctx.createGain();
  noiseGain.gain.setValueAtTime(volume * 0.3, now);
  noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.02);

  noise.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(masterGain);
  noise.start(now);
}

/**
 * DEATH SOUND - Somber, dignified
 * Procedural: Descending line from A minor feel (relative minor of C major)
 */
export function playProceduralDeath(): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;

  // A minor (relative minor of C major) - melancholic but related
  const notes = [C_MAJOR_SCALE.A4, C_MAJOR_SCALE.E4, C_MAJOR_SCALE.C4];
  const noteSpacing = 0.4;
  const noteDuration = 0.8;
  const volume = 0.15;

  notes.forEach((freq, i) => {
    const noteStart = now + i * noteSpacing;

    const osc = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = freq;

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0, noteStart);
    gain.gain.linearRampToValueAtTime(volume, noteStart + 0.05);
    gain.gain.exponentialRampToValueAtTime(0.001, noteStart + noteDuration);

    osc.connect(gain);
    gain.connect(masterGain!);
    osc.start(noteStart);
    osc.stop(noteStart + noteDuration);
  });
}

// =============================================================================
// Export All
// =============================================================================

export default {
  // Constants
  C_MAJOR_SCALE,
  SCALE_DEGREES,
  GOOD_INTERVALS,
  BAD_INTERVALS,

  // Helpers
  getRandomGoodInterval,
  getRandomBadInterval,
  getRandomScaleNote,
  getScaleDegree,
  humanize,

  // Generic sounds
  playGoodSound,
  playBadSound,

  // Semantic sounds
  playProceduralKill,
  playProceduralDamage,
  playProceduralXP,
  playProceduralLevelUp,
  playProceduralDash,
  playProceduralGraze,
  playProceduralEnemyHit,
  playProceduralDeath,

  // Init
  initProceduralAudio,
};
