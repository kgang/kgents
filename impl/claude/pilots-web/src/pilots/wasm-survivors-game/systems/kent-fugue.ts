/**
 * WASM Survivors - KENT Fugue System
 *
 * A procedural fugue generator in C# minor using the K-E-N-T motif
 * as the subject's intervallic DNA, similar to Bach's B-A-C-H motif.
 *
 * KENT CIPHER (letter position → semitones from C#):
 *   K = 11 → B# (leading tone, enharmonic C)
 *   E = 5  → F# (subdominant)
 *   N = 14 mod 12 = 2 → D# (supertonic)
 *   T = 20 mod 12 = 8 → A (submediant)
 *
 * KENT INTERVALS:
 *   K→E: Tritone descent (6 semitones) - "diabolus in musica"
 *   E→N: Minor 3rd descent (3 semitones)
 *   N→T: Tritone descent (6 semitones) - double devil!
 *
 * This creates a dark, chromatic subject perfect for survival horror.
 *
 * "The hornet's name is written in the music."
 */

// =============================================================================
// C# MINOR: ABSOLUTE PITCH FOUNDATION
// =============================================================================

/**
 * C# minor absolute frequencies (Hz) for all octaves
 * C#4 = 277.18 Hz (middle C#)
 */
export const CSHARP_MINOR_FREQUENCIES = {
  // Octave 2 (bass)
  'C#2': 69.30, 'D#2': 77.78, 'E2': 82.41, 'F#2': 92.50, 'G#2': 103.83, 'A2': 110.00, 'B2': 123.47, 'B#2': 130.81,
  // Octave 3 (tenor)
  'C#3': 138.59, 'D#3': 155.56, 'E3': 164.81, 'F#3': 185.00, 'G#3': 207.65, 'A3': 220.00, 'B3': 246.94, 'B#3': 261.63,
  // Octave 4 (alto)
  'C#4': 277.18, 'D#4': 311.13, 'E4': 329.63, 'F#4': 369.99, 'G#4': 415.30, 'A4': 440.00, 'B4': 493.88, 'B#4': 523.25,
  // Octave 5 (soprano)
  'C#5': 554.37, 'D#5': 622.25, 'E5': 659.25, 'F#5': 739.99, 'G#5': 830.61, 'A5': 880.00, 'B5': 987.77, 'B#5': 1046.50,
};

/**
 * C# Harmonic Minor scale in semitones from C#
 * C# D# E F# G# A B#
 * 0  2  3 5  7  8 11
 */
export const CSHARP_HARMONIC_MINOR = [0, 2, 3, 5, 7, 8, 11];

/**
 * Scale degree names for reference
 */
export const SCALE_DEGREE_NAMES = [
  'tonic',      // 0: C#
  'supertonic', // 1: D#
  'mediant',    // 2: E
  'subdominant',// 3: F#
  'dominant',   // 4: G#
  'submediant', // 5: A
  'leading',    // 6: B# (raised 7th)
];

// =============================================================================
// THE KENT MOTIF: Musical Cryptogram
// =============================================================================

/**
 * KENT letter-to-semitone cipher
 * Each letter's alphabet position mod 12 gives semitones from C#
 */
export const KENT_CIPHER = {
  K: 11, // 11th letter → 11 semitones → B# (leading tone)
  E: 5,  // 5th letter  → 5 semitones  → F# (subdominant)
  N: 2,  // 14th letter → 14 mod 12 = 2 → D# (supertonic)
  T: 8,  // 20th letter → 20 mod 12 = 8 → A (submediant)
};

/**
 * The KENT motif as semitones from C#
 * Creates two tritones - maximum tension!
 */
export const KENT_SEMITONES = [
  KENT_CIPHER.K, // B# (11)
  KENT_CIPHER.E, // F# (5)
  KENT_CIPHER.N, // D# (2)
  KENT_CIPHER.T, // A  (8)
];

/**
 * KENT intervals (semitone distances between consecutive notes)
 */
export const KENT_INTERVALS = [
  KENT_CIPHER.E - KENT_CIPHER.K, // K→E: -6 (tritone down)
  KENT_CIPHER.N - KENT_CIPHER.E, // E→N: -3 (minor 3rd down)
  KENT_CIPHER.T - KENT_CIPHER.N, // N→T: +6 (tritone up)
];

// =============================================================================
// STOCHASTIC GENERATION PARAMETERS
// =============================================================================

/**
 * Probability weights for spontaneous variation
 * These inject randomness while staying in C# minor
 */
export const STOCHASTIC_CONFIG = {
  // Note emission probability (0-1) - higher = more notes play
  // Increased to ensure continuous melodic flow - must be high for dense texture
  baseEmissionProbability: 0.92,  // 92% of notes play (was 75% - still too sparse!)

  // Probability of adding random rest before a note - keep very low for density
  restInsertionProbability: 0.05,  // Reduced from 0.15 - rests made it too thin

  // Probability of pitch variation (neighbor tones, passing tones)
  pitchVariationProbability: 0.2,  // Slightly reduced for clearer theme

  // Probability of rhythmic variation (stretch/compress)
  rhythmVariationProbability: 0.25,

  // Probability of spontaneous ornamentation
  ornamentProbability: 0.1,  // Reduced - too much ornamentation obscures theme

  // Probability of octave displacement
  octaveDisplacementProbability: 0.08,

  // Probability of dynamic variation
  dynamicVariationProbability: 0.3,

  // Bass drone probability (long held notes)
  bassDroneProbability: 0.5,

  // Minimum duration for bass notes (in beats)
  minBassDuration: 2.0,

  // Maximum random rest duration (in beats)
  maxRestDuration: 2.0,  // Reduced from 3.0
};

/**
 * Apply stochastic pitch variation within C# minor
 */
export function applyPitchVariation(semitone: number, variationAmount: number = 0.25): number {
  if (Math.random() > variationAmount) return semitone;

  // Choose a variation type
  const variationType = Math.random();

  if (variationType < 0.4) {
    // Upper neighbor (step up then back)
    const upperNeighbor = findNearestScaleTone(semitone + 1);
    return upperNeighbor;
  } else if (variationType < 0.8) {
    // Lower neighbor
    const lowerNeighbor = findNearestScaleTone(semitone - 1);
    return lowerNeighbor;
  } else {
    // Random scale tone
    const scaleTone = CSHARP_HARMONIC_MINOR[Math.floor(Math.random() * CSHARP_HARMONIC_MINOR.length)];
    return scaleTone;
  }
}

/**
 * Find the nearest tone in C# harmonic minor
 */
export function findNearestScaleTone(semitone: number): number {
  const normalized = ((semitone % 12) + 12) % 12;

  // Find closest scale tone
  let closest = CSHARP_HARMONIC_MINOR[0];
  let minDistance = 12;

  for (const scaleTone of CSHARP_HARMONIC_MINOR) {
    const distance = Math.min(
      Math.abs(normalized - scaleTone),
      Math.abs(normalized - scaleTone + 12),
      Math.abs(normalized - scaleTone - 12)
    );
    if (distance < minDistance) {
      minDistance = distance;
      closest = scaleTone;
    }
  }

  return closest;
}

/**
 * Apply rhythmic variation
 */
export function applyRhythmVariation(duration: number, variationAmount: number = 0.3): number {
  if (Math.random() > variationAmount) return duration;

  // Stretch or compress by up to 50%
  const factor = 0.5 + Math.random() * 1.0; // 0.5x to 1.5x
  return duration * factor;
}

/**
 * Generate a spontaneous ornament
 */
export function generateOrnament(baseSemitone: number, duration: number): FugueNote[] {
  const ornamentType = Math.random();

  if (ornamentType < 0.3) {
    // Mordent (quick upper neighbor)
    return [
      { semitone: baseSemitone, duration: duration * 0.6, velocity: 0.7, articulation: 'legato' },
      { semitone: findNearestScaleTone(baseSemitone + 2), duration: duration * 0.15, velocity: 0.5, articulation: 'staccato' },
      { semitone: baseSemitone, duration: duration * 0.25, velocity: 0.65, articulation: 'legato' },
    ];
  } else if (ornamentType < 0.6) {
    // Turn (upper-main-lower-main)
    const upper = findNearestScaleTone(baseSemitone + 2);
    const lower = findNearestScaleTone(baseSemitone - 1);
    const noteDur = duration * 0.25;
    return [
      { semitone: upper, duration: noteDur, velocity: 0.6, articulation: 'legato' },
      { semitone: baseSemitone, duration: noteDur, velocity: 0.65, articulation: 'legato' },
      { semitone: lower, duration: noteDur, velocity: 0.55, articulation: 'legato' },
      { semitone: baseSemitone, duration: noteDur, velocity: 0.7, articulation: 'tenuto' },
    ];
  } else {
    // Passing tone run
    const direction = Math.random() > 0.5 ? 1 : -1;
    const notes: FugueNote[] = [];
    const runLength = 2 + Math.floor(Math.random() * 3);
    const noteDur = duration / runLength;

    for (let i = 0; i < runLength; i++) {
      notes.push({
        semitone: findNearestScaleTone(baseSemitone + direction * i),
        duration: noteDur,
        velocity: 0.5 + (i / runLength) * 0.3,
        articulation: i === runLength - 1 ? 'tenuto' : 'legato',
      });
    }
    return notes;
  }
}

/**
 * Generate a random rest
 */
export function generateRandomRest(maxDuration: number = STOCHASTIC_CONFIG.maxRestDuration): FugueNote {
  const duration = 0.5 + Math.random() * (maxDuration - 0.5);
  return {
    semitone: -1, // Special value indicating rest
    duration,
    velocity: 0,
    articulation: 'legato',
  };
}

/**
 * Decide whether to emit a note based on sparsity
 */
export function shouldEmitNote(intensity: number): boolean {
  // Higher intensity = more notes
  const adjustedProbability = STOCHASTIC_CONFIG.baseEmissionProbability + intensity * 0.4;
  return Math.random() < adjustedProbability;
}

// =============================================================================
// PITCH UTILITIES
// =============================================================================

/**
 * Convert semitones from C# to frequency
 */
export function semitoneToFrequency(semitone: number, octave: number = 4): number {
  const baseFreq = 277.18; // C#4
  const totalSemitones = semitone + (octave - 4) * 12;
  return baseFreq * Math.pow(2, totalSemitones / 12);
}

/**
 * Convert scale degree (0-6) to semitones using harmonic minor
 */
export function degreeToSemitone(degree: number): number {
  const normalizedDegree = ((degree % 7) + 7) % 7;
  const octaveOffset = Math.floor(degree / 7) * 12;
  return CSHARP_HARMONIC_MINOR[normalizedDegree] + octaveOffset;
}

/**
 * Convert scale degree to frequency
 */
export function degreeToFrequency(degree: number, octave: number = 4): number {
  return semitoneToFrequency(degreeToSemitone(degree), octave);
}

/**
 * Get the interval in semitones between two scale degrees
 */
export function intervalBetweenDegrees(from: number, to: number): number {
  return degreeToSemitone(to) - degreeToSemitone(from);
}

// =============================================================================
// FUGUE NOTE DEFINITION
// =============================================================================

export interface FugueNote {
  /** Semitones from C# (0-11, can extend beyond for octave shifts) */
  semitone: number;
  /** Duration in beats (1 = quarter note) */
  duration: number;
  /** Velocity/dynamics (0-1) */
  velocity: number;
  /** Articulation style */
  articulation: 'legato' | 'staccato' | 'accent' | 'tenuto' | 'marcato';
  /** Optional: tied to next note */
  tied?: boolean;
}

// =============================================================================
// THE KENT SUBJECT: Core Fugue Theme
// =============================================================================

/**
 * The KENT fugue subject - built from the K-E-N-T intervals
 * with rhythmic elaboration for musical interest.
 *
 * Structure:
 * 1. K (B#) - accented, announces the subject
 * 2. E (F#) - tritone leap down, creates tension
 * 3. N (D#) - continues descent, builds momentum
 * 4. T (A) - tritone leap, dramatic climax
 * 5. Resolution back to tonic region
 */
export const KENT_SUBJECT: FugueNote[] = [
  // K - The announcement (B# / leading tone)
  { semitone: 11, duration: 0.75, velocity: 0.9, articulation: 'accent' },

  // E - Tritone descent to F# (the devil's interval!)
  { semitone: 5, duration: 0.5, velocity: 0.8, articulation: 'legato' },

  // N - Minor 3rd down to D#
  { semitone: 2, duration: 0.5, velocity: 0.75, articulation: 'legato' },

  // T - Tritone leap to A (second devil's interval!)
  { semitone: 8, duration: 0.75, velocity: 0.85, articulation: 'tenuto' },

  // Resolution: chromatic descent to G# (dominant)
  { semitone: 7, duration: 0.25, velocity: 0.7, articulation: 'legato' },

  // Final resolution to C# (tonic)
  { semitone: 0, duration: 1.0, velocity: 0.9, articulation: 'tenuto' },
];

/**
 * Extended KENT subject with full rhythmic development
 */
export const KENT_SUBJECT_EXTENDED: FugueNote[] = [
  // Opening: K announcement with pickup
  { semitone: 7, duration: 0.25, velocity: 0.6, articulation: 'legato' },  // G# pickup
  { semitone: 11, duration: 0.75, velocity: 0.9, articulation: 'marcato' }, // K (B#)

  // E - dramatic tritone descent
  { semitone: 5, duration: 0.5, velocity: 0.85, articulation: 'accent' },   // E (F#)
  { semitone: 5, duration: 0.25, velocity: 0.7, articulation: 'staccato' }, // F# repeated

  // N - continuation with neighbor tone
  { semitone: 3, duration: 0.25, velocity: 0.65, articulation: 'legato' },  // E (neighbor)
  { semitone: 2, duration: 0.5, velocity: 0.8, articulation: 'tenuto' },    // N (D#)

  // T - climactic tritone
  { semitone: 8, duration: 0.75, velocity: 0.9, articulation: 'marcato' },  // T (A)

  // Resolution phrase
  { semitone: 7, duration: 0.25, velocity: 0.7, articulation: 'legato' },   // G#
  { semitone: 5, duration: 0.25, velocity: 0.65, articulation: 'legato' },  // F#
  { semitone: 3, duration: 0.25, velocity: 0.6, articulation: 'legato' },   // E
  { semitone: 2, duration: 0.25, velocity: 0.65, articulation: 'legato' },  // D#
  { semitone: 0, duration: 1.0, velocity: 0.9, articulation: 'tenuto' },    // C# (tonic)
];

// =============================================================================
// SUBJECT TRANSFORMATIONS (True Fugue Techniques)
// =============================================================================

/**
 * Create the TONAL ANSWER (subject in the dominant, G# minor)
 * In a proper fugue, the answer transposes to the dominant but adjusts
 * certain intervals to stay within the key.
 */
export function createTonalAnswer(subject: FugueNote[]): FugueNote[] {
  return subject.map((note, index) => {
    // Transpose up a perfect 5th (7 semitones)
    let transposed = note.semitone + 7;

    // Tonal adjustment: if the subject starts on tonic, answer starts on dominant
    // and if subject goes to dominant, answer returns to tonic
    if (index === 0 && note.semitone === 0) {
      transposed = 7; // Start on G# (dominant)
    }
    if (note.semitone === 7) {
      transposed = 0; // G# in subject becomes C# in answer
    }

    return {
      ...note,
      semitone: ((transposed % 12) + 12) % 12,
      velocity: note.velocity * 0.95, // Slightly softer
    };
  });
}

/**
 * Create the REAL ANSWER (exact transposition)
 */
export function createRealAnswer(subject: FugueNote[], transposeSemitones: number = 7): FugueNote[] {
  return subject.map(note => ({
    ...note,
    semitone: ((note.semitone + transposeSemitones) % 12 + 12) % 12,
  }));
}

/**
 * Create INVERSION (intervals flipped)
 * Rising intervals become falling, and vice versa
 */
export function createInversion(subject: FugueNote[], axis: number = 0): FugueNote[] {
  return subject.map(note => ({
    ...note,
    semitone: ((axis - (note.semitone - axis)) % 12 + 12) % 12,
  }));
}

/**
 * Create RETROGRADE (played backwards)
 */
export function createRetrograde(subject: FugueNote[]): FugueNote[] {
  return [...subject].reverse().map(note => ({ ...note }));
}

/**
 * Create RETROGRADE INVERSION (backwards and flipped)
 */
export function createRetrogradeInversion(subject: FugueNote[], axis: number = 0): FugueNote[] {
  return createRetrograde(createInversion(subject, axis));
}

/**
 * Create AUGMENTATION (rhythmic values doubled)
 */
export function createAugmentation(subject: FugueNote[], factor: number = 2): FugueNote[] {
  return subject.map(note => ({
    ...note,
    duration: note.duration * factor,
    velocity: note.velocity * 0.9, // Augmentation often played more legato
  }));
}

/**
 * Create DIMINUTION (rhythmic values halved)
 */
export function createDiminution(subject: FugueNote[], factor: number = 2): FugueNote[] {
  return subject.map(note => ({
    ...note,
    duration: note.duration / factor,
    velocity: Math.min(1, note.velocity * 1.1), // Diminution often more energetic
    articulation: 'staccato', // Faster notes typically detached
  }));
}

/**
 * Create STRETTO entry (subject starting at different point)
 */
export function createStrettoEntry(subject: FugueNote[], startIndex: number = 0): FugueNote[] {
  return subject.slice(startIndex);
}

// =============================================================================
// COUNTERSUBJECT
// =============================================================================

/**
 * The countersubject - designed to work contrapuntally with the subject.
 * Uses contrary motion and complementary rhythm.
 */
export const KENT_COUNTERSUBJECT: FugueNote[] = [
  // Contrary motion: starts low while subject is high
  { semitone: 0, duration: 0.5, velocity: 0.6, articulation: 'legato' },   // C# (held)
  { semitone: 0, duration: 0.25, velocity: 0.55, articulation: 'legato' }, // C# continued

  // Rising while subject descends
  { semitone: 2, duration: 0.5, velocity: 0.65, articulation: 'legato' },  // D#
  { semitone: 3, duration: 0.5, velocity: 0.7, articulation: 'legato' },   // E
  { semitone: 5, duration: 0.5, velocity: 0.75, articulation: 'legato' },  // F#

  // Rhythmic counterpoint (fills gaps in subject)
  { semitone: 7, duration: 0.25, velocity: 0.6, articulation: 'staccato' }, // G#
  { semitone: 5, duration: 0.25, velocity: 0.55, articulation: 'staccato' },// F#
  { semitone: 7, duration: 0.25, velocity: 0.6, articulation: 'staccato' }, // G#
  { semitone: 8, duration: 0.25, velocity: 0.65, articulation: 'staccato' },// A

  // Resolution (arrives at dominant as subject resolves to tonic)
  { semitone: 7, duration: 1.0, velocity: 0.7, articulation: 'tenuto' },   // G#
];

// =============================================================================
// FREE COUNTERPOINT GENERATORS
// =============================================================================

/**
 * Generate a free counterpoint line based on harmonic constraints
 */
export function generateFreeCounterpoint(
  targetLength: number,
  harmonicRoot: number,
  tension: number,
  direction: 'ascending' | 'descending' | 'wave' = 'wave'
): FugueNote[] {
  const notes: FugueNote[] = [];
  let currentPitch = harmonicRoot;
  let totalDuration = 0;

  while (totalDuration < targetLength) {
    // Choose interval based on tension
    const consonantIntervals = [0, 3, 4, 5, 7, 8, 9]; // Consonances
    const dissonantIntervals = [1, 2, 6, 10, 11];     // Dissonances

    const intervals = tension > 0.6
      ? [...consonantIntervals, ...dissonantIntervals]
      : consonantIntervals;

    const interval = intervals[Math.floor(Math.random() * intervals.length)];

    // Apply direction
    let nextPitch: number;
    if (direction === 'ascending') {
      nextPitch = currentPitch + interval;
    } else if (direction === 'descending') {
      nextPitch = currentPitch - interval;
    } else {
      // Wave: alternate directions
      nextPitch = currentPitch + (Math.random() > 0.5 ? interval : -interval);
    }

    // Keep in reasonable range
    nextPitch = ((nextPitch % 12) + 12) % 12;

    // Choose duration
    const durations = tension > 0.5
      ? [0.25, 0.25, 0.5]  // Faster when tense
      : [0.5, 0.75, 1.0];  // Slower when calm

    const duration = durations[Math.floor(Math.random() * durations.length)];

    notes.push({
      semitone: nextPitch,
      duration,
      velocity: 0.5 + Math.random() * 0.3,
      articulation: duration < 0.5 ? 'staccato' : 'legato',
    });

    currentPitch = nextPitch;
    totalDuration += duration;
  }

  return notes;
}

/**
 * Generate a sequence pattern (common in fugue episodes)
 */
export function generateSequence(
  motif: FugueNote[],
  repetitions: number,
  transposition: number // Semitones to transpose each repetition
): FugueNote[] {
  const result: FugueNote[] = [];

  for (let i = 0; i < repetitions; i++) {
    const transposedMotif = motif.map(note => ({
      ...note,
      semitone: ((note.semitone + transposition * i) % 12 + 12) % 12,
      velocity: note.velocity * (1 - i * 0.05), // Slight diminuendo
    }));
    result.push(...transposedMotif);
  }

  return result;
}

// =============================================================================
// COUNTERPOINT RULES
// =============================================================================

/**
 * Check if an interval (in semitones) is consonant
 */
export function isConsonantInterval(semitones: number): boolean {
  const normalized = ((semitones % 12) + 12) % 12;
  // Perfect consonances: unison, 5th, octave
  // Imperfect consonances: 3rds, 6ths
  return [0, 3, 4, 7, 8, 9].includes(normalized);
}

/**
 * Check for parallel fifths between two voice movements
 */
export function hasParallelFifths(
  voice1From: number, voice1To: number,
  voice2From: number, voice2To: number
): boolean {
  const interval1 = ((voice1From - voice2From) % 12 + 12) % 12;
  const interval2 = ((voice1To - voice2To) % 12 + 12) % 12;
  return interval1 === 7 && interval2 === 7;
}

/**
 * Check for parallel octaves between two voice movements
 */
export function hasParallelOctaves(
  voice1From: number, voice1To: number,
  voice2From: number, voice2To: number
): boolean {
  const interval1 = ((voice1From - voice2From) % 12 + 12) % 12;
  const interval2 = ((voice1To - voice2To) % 12 + 12) % 12;
  return interval1 === 0 && interval2 === 0;
}

/**
 * Check voice leading quality (prefer stepwise motion)
 */
export function getVoiceLeadingQuality(fromPitch: number, toPitch: number): number {
  const interval = Math.abs(toPitch - fromPitch);
  if (interval <= 2) return 1.0;   // Step: excellent
  if (interval <= 4) return 0.8;   // Third: good
  if (interval <= 7) return 0.5;   // Up to fifth: acceptable
  return 0.2;                       // Larger: less ideal
}

/**
 * Find the best next pitch that follows counterpoint rules
 */
export function findBestCounterpointPitch(
  currentPitch: number,
  otherVoicePitch: number,
  previousOtherPitch: number,
  preferredDirection: 'up' | 'down' | 'any' = 'any',
  tension: number = 0.3
): number {
  const candidates: { pitch: number; score: number }[] = [];

  // Try all pitches in the octave
  for (let i = -6; i <= 6; i++) {
    const candidatePitch = ((currentPitch + i) % 12 + 12) % 12;

    let score = 0;

    // Check consonance with other voice
    const interval = Math.abs(candidatePitch - otherVoicePitch);
    if (isConsonantInterval(interval)) {
      score += 10;
    } else if (tension > 0.5) {
      score += 5; // Dissonance acceptable when tense
    }

    // Check for parallel fifths/octaves
    if (hasParallelFifths(currentPitch, candidatePitch, previousOtherPitch, otherVoicePitch)) {
      score -= 20; // Heavy penalty
    }
    if (hasParallelOctaves(currentPitch, candidatePitch, previousOtherPitch, otherVoicePitch)) {
      score -= 20;
    }

    // Prefer contrary motion
    const otherDirection = otherVoicePitch - previousOtherPitch;
    const ourDirection = candidatePitch - currentPitch;
    if ((otherDirection > 0 && ourDirection < 0) || (otherDirection < 0 && ourDirection > 0)) {
      score += 5; // Contrary motion bonus
    }

    // Voice leading quality
    score += getVoiceLeadingQuality(currentPitch, candidatePitch) * 5;

    // Direction preference
    if (preferredDirection === 'up' && candidatePitch > currentPitch) score += 2;
    if (preferredDirection === 'down' && candidatePitch < currentPitch) score += 2;

    candidates.push({ pitch: candidatePitch, score });
  }

  // Sort by score and return best
  candidates.sort((a, b) => b.score - a.score);
  return candidates[0].pitch;
}

// =============================================================================
// VOICE STATE
// =============================================================================

export type VoiceRegister = 'soprano' | 'alto' | 'tenor' | 'bass';

export interface VoiceState {
  register: VoiceRegister;
  octave: number;
  currentPitch: number;      // Semitones from C#
  previousPitch: number;
  material: FugueNote[];     // Current notes to play
  materialIndex: number;     // Position in material
  beatOffset: number;        // When this voice enters (for stretto)
  isActive: boolean;
  role: 'subject' | 'answer' | 'countersubject' | 'free';
}

export const VOICE_OCTAVES: Record<VoiceRegister, number> = {
  soprano: 5,
  alto: 4,
  tenor: 3,
  bass: 2,
};

export function createVoiceState(register: VoiceRegister): VoiceState {
  return {
    register,
    octave: VOICE_OCTAVES[register],
    currentPitch: 0,
    previousPitch: 0,
    material: [],
    materialIndex: 0,
    beatOffset: 0,
    isActive: false,
    role: 'free',
  };
}

// =============================================================================
// FUGUE STATE MACHINE
// =============================================================================

export type FuguePhase =
  | 'silence'          // No music
  | 'exposition_1'     // First voice enters with subject
  | 'exposition_2'     // Second voice: answer, first voice: countersubject
  | 'exposition_3'     // Third voice: subject, others: counterpoint
  | 'exposition_4'     // Fourth voice: answer, full texture
  | 'episode'          // Sequential/modulatory passage
  | 'development'      // Subject in new keys, transformations
  | 'stretto'          // Overlapping subject entries
  | 'pedal_point'      // Sustained bass, building climax
  | 'recapitulation'   // Subject returns in tonic
  | 'coda';            // Final cadence

// =============================================================================
// MUSICAL JOURNEY SYSTEM (Grand Opening + Evolution)
// =============================================================================

/**
 * Journey phase - governs the macro musical structure
 * Each run starts with a bold 32-bar Grand Opening that everything evolves from
 */
export type JourneyPhase =
  | 'grand_opening'        // Bold 32-bar introduction establishing KENT theme
  | 'exploration'          // Expanding from opening, answering phrases
  | 'development'          // Transformation, fragmentation, tension
  | 'recapitulation_arc';  // Returns to opening material, homecoming

/**
 * Captures the opening's character for later reference
 */
export interface OpeningSignature {
  /** Which variation was used for the solo announcement */
  announcementVariation: number;
  /** Key coloring established in opening */
  keyColoring: KeyColoring;
  /** Peak dynamic level reached */
  peakDynamic: number;
  /** Tempo established (before game intensity modifies it) */
  establishedTempo: number;
  /** Beat when opening completed */
  completedAtBeat: number;
}

/**
 * A memorable moment the music can reference
 */
export interface NarrativeBeat {
  type: 'opening_complete' | 'first_stretto' | 'harmonic_climax' | 'quiet_moment' | 'full_texture';
  sectionNumber: number;
  beat: number;
  intensity: number;
}

export interface FugueStateData {
  phase: FuguePhase;
  phaseProgress: number;     // 0-1
  phaseDuration: number;     // In beats

  voices: Record<VoiceRegister, VoiceState>;

  // Timing
  tempo: number;             // BPM
  currentBeat: number;
  beatsPerMeasure: number;

  // Harmonic context
  currentHarmony: number;    // Root in semitones (0 = C#, 7 = G#, etc.)
  harmonicTension: number;   // 0-1

  // Subject tracking
  subjectEntryCount: number;
  lastSubjectVoice: VoiceRegister | null;

  // Game-driven parameters
  intensity: number;
  gamePhase: 'exploration' | 'combat' | 'crisis' | 'death';

  // Wave-based progression (NEW)
  waveNumber: number;        // Current game wave

  // Musical narrative dynamics (NEW)
  dynamicArc: number;        // 0-1 where in the dynamic arc we are
  arcPhase: 'building' | 'climax' | 'resolving' | 'breathing';
  globalDynamic: number;     // 0-1 overall volume modifier for musical shaping

  // Pre-generated variation tracking (NEW)
  currentVariationIndex: number;  // 0-7, which KENT variation is currently playing
  lastVariationIndex: number | null;  // Previous variation for avoiding repetition

  // Multi-bar percussion structure (NEW)
  percussion: {
    measureCount: number;        // Total measures since percussion started
    barPosition8: number;        // Position within 8-bar phrase (0-7)
    barPosition16: number;       // Position within 16-bar section (0-15)
    barPosition32: number;       // Position within 32-bar cycle (0-31)
    section: 'A' | 'B';          // A/B section for 16-bar variation
    style: 'rock' | 'funk';      // Current drum style
    fillCooldown: number;        // Beats until next fill is allowed
    lastFillBar: number;         // Bar when last fill occurred
    // TIMING FIX: Track which 16th notes have been played to prevent skipping
    lastPlayedSixteenth: number; // Last global 16th note index played
  };

  // Nested phrase structure for orchestration (8/16/32 bar levels)
  phraseState: {
    bar8Position: number;        // Position within 8-bar phrase (0-7)
    bar16Position: number;       // Position within 16-bar period (0-15)
    bar32Position: number;       // Position within 32-bar section (0-31)
    totalBars: number;           // Total bars played
    theme8: 'neutral' | 'ornamented' | 'legato' | 'staccato' | 'chromatic' | 'sparse' | 'dense' | 'modal' | 'sequential' | 'dramatic';
    theme16: 'neutral' | 'ornamented' | 'legato' | 'staccato' | 'chromatic' | 'sparse' | 'dense' | 'modal' | 'sequential' | 'dramatic';
    theme32: 'neutral' | 'ornamented' | 'legato' | 'staccato' | 'chromatic' | 'sparse' | 'dense' | 'modal' | 'sequential' | 'dramatic';
    keyColoring: 'natural' | 'harmonic' | 'melodic' | 'dorian' | 'phrygian' | 'neapolitan';
    phraseContour8: number;      // 0-1 dynamic arc position in 8-bar phrase
    phraseContour16: number;     // 0-1 dynamic arc position in 16-bar period
    phraseContour32: number;     // 0-1 dynamic arc position in 32-bar section
    phraseTension: number;       // 0-1 combined phrase tension
    currentRunLength: number;    // Notes in current melodic run
    runDirection: 'ascending' | 'descending' | 'none';
  };

  // === MUSICAL JOURNEY TRACKING (Grand Opening + Evolution) ===

  /** Overall journey phase - governs macro structure starting with bold opening */
  journeyPhase: JourneyPhase;

  /** Section number within journey (0 = Grand Opening, 1+ = subsequent sections) */
  sectionNumber: number;

  /** Total 32-bar sections completed since game start */
  totalSectionsCompleted: number;

  /** Opening signature - captured during grand opening for later reference */
  openingSignature: OpeningSignature | null;

  /** How far from "home" harmonically (0 = tonic, higher = more distant) */
  harmonicDistance: number;

  /** Narrative beats - memorable moments the music can reference */
  narrativeBeats: NarrativeBeat[];

  /** Opening phase (0-3) for choreographed voice entries during grand opening */
  openingPhase: 0 | 1 | 2 | 3;

  /** Whether percussion is muted (true during early grand opening) */
  percussionMuted: boolean;
}

// =============================================================================
// MARKOV TRANSITION MATRIX
// =============================================================================

type TransitionMatrix = Record<FuguePhase, Record<FuguePhase, number>>;

/**
 * Base transition probabilities for fugue phases
 * Modified for sparser beginnings with more silence and breathing room
 */
const BASE_TRANSITIONS: TransitionMatrix = {
  silence: {
    silence: 0,             // NEVER stay silent - always start playing!
    exposition_1: 0.7,      // Usually start the fugue
    exposition_2: 0,
    exposition_3: 0,
    exposition_4: 0,
    episode: 0.2,           // Can start with episode (gentler entry)
    development: 0,
    stretto: 0,
    pedal_point: 0.1,       // Can start with bass drone
    recapitulation: 0,
    coda: 0,
  },
  exposition_1: {
    silence: 0,             // NEVER go silent - keep the music flowing!
    exposition_1: 0.3,      // Can repeat with variation
    exposition_2: 0.5,      // Usually progress to add second voice
    exposition_3: 0,
    exposition_4: 0,
    episode: 0.15,          // Can go to episode
    development: 0,
    stretto: 0,
    pedal_point: 0.05,
    recapitulation: 0,
    coda: 0,
  },
  exposition_2: {
    silence: 0,             // NEVER go silent
    exposition_1: 0.1,      // Can return to simpler texture
    exposition_2: 0.1,
    exposition_3: 0.6,
    exposition_4: 0,
    episode: 0.2,
    development: 0,
    stretto: 0,
    pedal_point: 0,
    recapitulation: 0,
    coda: 0,
  },
  exposition_3: {
    silence: 0,
    exposition_1: 0,
    exposition_2: 0,
    exposition_3: 0.1,
    exposition_4: 0.6,
    episode: 0.3,
    development: 0,
    stretto: 0,
    pedal_point: 0,
    recapitulation: 0,
    coda: 0,
  },
  exposition_4: {
    silence: 0,
    exposition_1: 0,
    exposition_2: 0,
    exposition_3: 0,
    exposition_4: 0.1,
    episode: 0.5,
    development: 0.3,
    stretto: 0.1,
    pedal_point: 0,
    recapitulation: 0,
    coda: 0,
  },
  episode: {
    silence: 0,             // NEVER go silent
    exposition_1: 0.1,      // Can return to exposition
    exposition_2: 0,
    exposition_3: 0,
    exposition_4: 0,
    episode: 0.3,
    development: 0.35,
    stretto: 0.15,
    pedal_point: 0.05,
    recapitulation: 0.05,
    coda: 0,
  },
  development: {
    silence: 0,
    exposition_1: 0,
    exposition_2: 0,
    exposition_3: 0,
    exposition_4: 0,
    episode: 0.3,
    development: 0.3,
    stretto: 0.25,
    pedal_point: 0.1,
    recapitulation: 0.05,
    coda: 0,
  },
  stretto: {
    silence: 0,
    exposition_1: 0,
    exposition_2: 0,
    exposition_3: 0,
    exposition_4: 0,
    episode: 0.1,
    development: 0.1,
    stretto: 0.4,
    pedal_point: 0.2,
    recapitulation: 0.15,
    coda: 0.05,
  },
  pedal_point: {
    silence: 0,
    exposition_1: 0,
    exposition_2: 0,
    exposition_3: 0,
    exposition_4: 0,
    episode: 0.05,
    development: 0.05,
    stretto: 0.3,
    pedal_point: 0.2,
    recapitulation: 0.25,
    coda: 0.15,
  },
  recapitulation: {
    silence: 0,
    exposition_1: 0,
    exposition_2: 0,
    exposition_3: 0,
    exposition_4: 0,
    episode: 0.1,
    development: 0,
    stretto: 0.1,
    pedal_point: 0.1,
    recapitulation: 0.3,
    coda: 0.4,
  },
  coda: {
    silence: 0,             // NEVER go silent - loop back to playing!
    exposition_1: 0.5,      // Fresh start with new variation
    exposition_2: 0.1,
    exposition_3: 0,
    exposition_4: 0,
    episode: 0.1,
    development: 0,
    stretto: 0,
    pedal_point: 0.1,
    recapitulation: 0,
    coda: 0.2,
  },
};

/**
 * Modify transitions based on game state
 */
export function computeTransitions(
  base: TransitionMatrix,
  intensity: number,
  gamePhase: FugueStateData['gamePhase']
): TransitionMatrix {
  const modified = JSON.parse(JSON.stringify(base)) as TransitionMatrix;

  // High intensity: more stretto, less silence
  if (intensity > 0.6) {
    for (const from of Object.keys(modified) as FuguePhase[]) {
      modified[from].stretto = (modified[from].stretto || 0) * (1 + intensity);
      modified[from].silence = (modified[from].silence || 0) * (1 - intensity);
      modified[from].episode = (modified[from].episode || 0) * (1 - intensity * 0.5);
    }
  }

  // Crisis: force stretto and pedal
  if (gamePhase === 'crisis') {
    for (const from of Object.keys(modified) as FuguePhase[]) {
      modified[from].stretto = (modified[from].stretto || 0) * 2;
      modified[from].pedal_point = (modified[from].pedal_point || 0) * 1.5;
    }
  }

  // Death: force coda
  if (gamePhase === 'death') {
    for (const from of Object.keys(modified) as FuguePhase[]) {
      modified[from].coda = (modified[from].coda || 0) * 3;
      modified[from].silence = (modified[from].silence || 0) * 2;
    }
  }

  // Normalize
  for (const from of Object.keys(modified) as FuguePhase[]) {
    const sum = Object.values(modified[from]).reduce((a, b) => a + b, 0);
    if (sum > 0) {
      for (const to of Object.keys(modified[from]) as FuguePhase[]) {
        modified[from][to] /= sum;
      }
    }
  }

  return modified;
}

/**
 * Sample next phase from transition matrix
 */
export function sampleNextPhase(
  current: FuguePhase,
  matrix: TransitionMatrix
): FuguePhase {
  const probs = matrix[current];
  const rand = Math.random();
  let cumulative = 0;

  for (const [phase, prob] of Object.entries(probs)) {
    cumulative += prob;
    if (rand < cumulative) {
      return phase as FuguePhase;
    }
  }

  return 'exposition_1'; // Fallback
}

// =============================================================================
// FUGUE STATE INITIALIZATION
// =============================================================================

export function createFugueState(): FugueStateData {
  // === GRAND OPENING: Start with solo alto voice announcing KENT theme ===
  // Only alto is active initially - other voices enter during the 32-bar opening
  const altoVoice = createVoiceState('alto');
  altoVoice.material = [...KENT_SUBJECT]; // Clone the subject for bold opening
  altoVoice.isActive = true;
  altoVoice.role = 'subject';

  // Bass voice is prepared but NOT active during opening phase 0
  const bassVoice = createVoiceState('bass');
  bassVoice.material = [
    { semitone: 0, duration: 2, velocity: 0.5, articulation: 'tenuto' as const },  // C# (tonic)
    { semitone: 7, duration: 2, velocity: 0.45, articulation: 'legato' as const }, // G# (dominant)
    { semitone: 0, duration: 2, velocity: 0.5, articulation: 'tenuto' as const },  // C# return
  ];
  bassVoice.isActive = false; // Will enter at opening phase 3
  bassVoice.role = 'free';

  return {
    phase: 'exposition_1',      // Start with first voice announcing theme
    phaseProgress: 0,
    phaseDuration: 8,

    voices: {
      soprano: createVoiceState('soprano'),  // Enters at phase 1 or 2
      alto: altoVoice,                       // Active NOW - announces KENT theme
      tenor: createVoiceState('tenor'),      // Enters at phase 1 or 2
      bass: bassVoice,                       // Enters at phase 3
    },

    // GRAND OPENING: Slower, more majestic tempo (60 BPM = Andante Maestoso)
    tempo: 60,
    currentBeat: 0,
    beatsPerMeasure: 4,

    currentHarmony: 0,          // C# (tonic)
    harmonicTension: 0.2,

    subjectEntryCount: 1,       // Alto has entered
    lastSubjectVoice: 'alto',

    intensity: 0.35,
    gamePhase: 'exploration',

    waveNumber: 1,

    // Start with breathing room
    dynamicArc: 0,
    arcPhase: 'breathing',
    globalDynamic: 0.4,

    // Start with original KENT statement
    currentVariationIndex: 0,
    lastVariationIndex: null,

    // Percussion - MUTED during grand opening (phases 0-1)
    percussion: {
      measureCount: 0,
      barPosition8: 0,
      barPosition16: 0,
      barPosition32: 0,
      section: 'A',
      style: 'rock',
      fillCooldown: 0,
      lastFillBar: -8,
      lastPlayedSixteenth: -1,
    },

    phraseState: {
      bar8Position: 0,
      bar16Position: 0,
      bar32Position: 0,
      totalBars: 0,
      theme8: 'neutral',
      theme16: 'neutral',
      theme32: 'dramatic',  // Grand opening uses dramatic theme at 32-bar level
      keyColoring: 'harmonic',
      phraseContour8: 0,
      phraseContour16: 0,
      phraseContour32: 0,
      phraseTension: 0.3,
      currentRunLength: 0,
      runDirection: 'none',
    },

    // === MUSICAL JOURNEY - Start with Grand Opening ===
    journeyPhase: 'grand_opening',
    sectionNumber: 0,              // Section 0 = Grand Opening
    totalSectionsCompleted: 0,
    openingSignature: null,        // Will be captured when opening completes
    harmonicDistance: 0,           // Start at home (tonic)
    narrativeBeats: [],
    openingPhase: 0,               // Phase 0: Solo announcement
    percussionMuted: false,        // START WITH DRUMS IMMEDIATELY (was true)
  };
}

// =============================================================================
// WAVE-BASED VOICE SELECTION (NEW)
// =============================================================================

/**
 * Determine target voice count based on wave number and intensity.
 *
 * MUSICAL NARRATIVE:
 * - Waves 1-2: Sparse intro (1 voice, occasionally 2)
 * - Waves 3-4: Building texture (2-3 voices)
 * - Waves 5+: Full ensemble possible (3-4 voices)
 *
 * Bass is ALWAYS included when >= 2 voices for harmonic foundation.
 */
export function getTargetVoiceCount(waveNumber: number, intensity: number, phase: FuguePhase): number {
  // Base count from wave progression
  let baseCount: number;
  if (waveNumber <= 2) {
    baseCount = 1;  // Sparse intro
  } else if (waveNumber <= 4) {
    baseCount = 2;  // Building
  } else if (waveNumber <= 6) {
    baseCount = 3;  // Rich texture
  } else {
    baseCount = 4;  // Full ensemble
  }

  // Intensity can add voices (but not exceed 4)
  const intensityBonus = Math.floor(intensity * 1.5);
  let targetCount = Math.min(4, baseCount + intensityBonus);

  // Phase overrides
  if (phase === 'silence') return 0;
  if (phase === 'exposition_1') return 1;  // Always single voice for first exposition
  if (phase === 'stretto') return Math.max(3, targetCount);  // Stretto needs density
  if (phase === 'coda') return Math.min(4, targetCount + 1);  // Coda is full

  // Wave 1-2 ceiling
  if (waveNumber <= 2) {
    targetCount = Math.min(2, targetCount);
  }

  return targetCount;
}

/**
 * Select which voices should be active, with bass-first priority.
 *
 * VOICE PRIORITY (for multi-voice):
 * 1. Bass - ALWAYS first (harmonic foundation)
 * 2. Tenor - Second priority (fills low-mid)
 * 3. Alto - Third (mid range)
 * 4. Soprano - Last (melody, but not always needed)
 *
 * This creates a bottom-up texture that grounds the harmony.
 */
export function selectActiveVoices(targetCount: number, lastSubjectVoice: VoiceRegister | null): VoiceRegister[] {
  if (targetCount <= 0) return [];
  if (targetCount === 1) {
    // Single voice: prefer variety, but weight toward lower voices
    const singleVoiceWeights: [VoiceRegister, number][] = [
      ['bass', 0.35],    // Bass can sing subject
      ['tenor', 0.30],   // Tenor is nice for melody
      ['alto', 0.25],    // Alto for middle ground
      ['soprano', 0.10], // Soprano less common alone
    ];

    // Avoid repeating last subject voice
    const filtered = lastSubjectVoice
      ? singleVoiceWeights.filter(([v]) => v !== lastSubjectVoice)
      : singleVoiceWeights;

    const total = filtered.reduce((sum, [, w]) => sum + w, 0);
    let rand = Math.random() * total;
    for (const [voice, weight] of filtered) {
      rand -= weight;
      if (rand <= 0) return [voice];
    }
    return ['tenor']; // Fallback
  }

  // Multi-voice: Bass is ALWAYS included
  const voices: VoiceRegister[] = ['bass'];

  // Add remaining voices in priority order
  const remaining: VoiceRegister[] = ['tenor', 'alto', 'soprano'];

  // Shuffle remaining slightly for variety, but keep general priority
  for (let i = remaining.length - 1; i > 0; i--) {
    if (Math.random() < 0.3) { // 30% chance to swap
      const j = Math.floor(Math.random() * (i + 1));
      [remaining[i], remaining[j]] = [remaining[j], remaining[i]];
    }
  }

  // Add voices up to target count
  for (const voice of remaining) {
    if (voices.length >= targetCount) break;
    voices.push(voice);
  }

  return voices;
}

// =============================================================================
// DYNAMIC ARC SYSTEM (NEW)
// =============================================================================

/**
 * Update the dynamic arc based on phase progression.
 *
 * MUSICAL NARRATIVE ARC:
 * - breathing: Soft, spacious, contemplative (pp-p)
 * - building: Gradual crescendo (p-mf)
 * - climax: Peak intensity (f-ff)
 * - resolving: Diminuendo, unwinding (mf-p)
 *
 * Arc shapes the globalDynamic which modifies all note velocities.
 */
export function updateDynamicArc(state: FugueStateData): { arcPhase: FugueStateData['arcPhase']; globalDynamic: number; dynamicArc: number } {
  const { phase, phaseProgress, intensity, waveNumber } = state;

  // Determine arc phase from fugue phase
  let arcPhase: FugueStateData['arcPhase'];
  let baseDynamic: number;

  switch (phase) {
    case 'silence':
      arcPhase = 'breathing';
      baseDynamic = 0.2;
      break;
    case 'exposition_1':
      arcPhase = 'building';
      baseDynamic = 0.4 + phaseProgress * 0.1;
      break;
    case 'exposition_2':
    case 'exposition_3':
      arcPhase = 'building';
      baseDynamic = 0.5 + phaseProgress * 0.15;
      break;
    case 'exposition_4':
      arcPhase = 'building';
      baseDynamic = 0.65 + phaseProgress * 0.1;
      break;
    case 'episode':
      arcPhase = 'breathing';
      baseDynamic = 0.5 + Math.sin(phaseProgress * Math.PI) * 0.15; // Gentle wave
      break;
    case 'development':
      arcPhase = 'building';
      baseDynamic = 0.6 + phaseProgress * 0.2;
      break;
    case 'stretto':
      arcPhase = 'climax';
      baseDynamic = 0.8 + intensity * 0.2;
      break;
    case 'pedal_point':
      arcPhase = 'climax';
      baseDynamic = 0.75 + phaseProgress * 0.15;
      break;
    case 'recapitulation':
      arcPhase = 'resolving';
      baseDynamic = 0.7 - phaseProgress * 0.15;
      break;
    case 'coda':
      arcPhase = 'resolving';
      baseDynamic = 0.6 - phaseProgress * 0.3; // Final fade
      break;
    default:
      arcPhase = 'breathing';
      baseDynamic = 0.4;
  }

  // Wave-based scaling: later waves can be louder overall
  const waveScale = Math.min(1.2, 0.8 + waveNumber * 0.05);
  const globalDynamic = Math.min(1, baseDynamic * waveScale);

  // Dynamic arc tracks overall musical energy (0-1)
  const dynamicArc = (state.dynamicArc + 0.01) % 1; // Slowly cycles

  return { arcPhase, globalDynamic, dynamicArc };
}

// =============================================================================
// PERCUSSION SYSTEM - Consistent Beat with Structural Fills
// =============================================================================

/**
 * DESIGN PHILOSOPHY:
 * - Base beat is 100% CONSISTENT - NO random variations during normal playing
 * - Procedural elements ONLY at structural boundaries (8/16/32 bars)
 * - Fills are RECOGNIZABLE musical patterns, not algorithmic noise
 * - Style changes ONLY at 16-bar boundaries (A section = rock, B section = funk)
 *
 * FILL STRUCTURE:
 * - 8-bar: Quick 2-beat snare buildup (subtle, marks the phrase)
 * - 16-bar: Classic 1-bar fill (snare build → tom descent → crash)
 * - 32-bar: Epic 2-bar fill (full tom cascade → massive crash)
 */

export interface PercussionNote {
  type: 'kick' | 'snare' | 'hihat' | 'tom' | 'crash' | 'ride';
  startTime: number;
  velocity: number;
  duration: number;
  ghost?: boolean;
}

/**
 * SYNCOPATED ROCK PATTERN - Infectious groove with off-beat energy and surprises
 *
 * Enhanced version with:
 * - Anticipation kicks (playing on "and" before the beat)
 * - Strategic pauses (every 4th bar drops kick on beat 1)
 * - Hi-hat variations (open hats, ride substitutions, barks)
 * - Displacement techniques (slightly shifted backbeats, polymetric hints)
 * - Micro-pauses (occasional 16th note silence for tension)
 *
 * Each bar is slightly different while maintaining the overall feel.
 * Pattern creates a "pocket" feel that keeps the listener guessing.
 */
/**
 * DRIVING PATTERN - Four-on-the-floor with subtle procedural variation
 *
 * Inspired by trance/deep house - hypnotic, driving, simple.
 * - Kick on every beat (four-on-the-floor)
 * - Snare/clap on 2 and 4
 * - Consistent hi-hats with subtle dynamics
 * - Procedural variation through: open hats, velocity humanization, occasional extras
 */
function getRockPattern(
  sixteenthPosition: number,
  measureNum: number = 0
): { type: PercussionNote['type']; velocity: number; ghost?: boolean }[] {
  const notes: { type: PercussionNote['type']; velocity: number; ghost?: boolean }[] = [];

  // Procedural variation seeds
  const barVariation = measureNum % 4;
  const phrasePosition = measureNum % 8;
  const seed = (measureNum * 1.618033988749 + sixteenthPosition * 0.414213562373) % 1;

  // === KICK: Four-on-the-floor (positions 0, 4, 8, 12) ===
  const isKickPosition = sixteenthPosition % 4 === 0;
  if (isKickPosition) {
    // Beat 1 strongest, others slightly softer
    const kickVel = sixteenthPosition === 0 ? 0.95 : 0.85;
    notes.push({ type: 'kick', velocity: kickVel });
  }

  // Subtle offbeat kick on certain bars (deep house flavor)
  if (barVariation === 2 && sixteenthPosition === 10) {
    notes.push({ type: 'kick', velocity: 0.6 });
  }

  // === SNARE/CLAP: Backbeat on 2 and 4 (positions 4, 12) ===
  if (sixteenthPosition === 4 || sixteenthPosition === 12) {
    notes.push({ type: 'snare', velocity: 0.9 });
  }

  // === HI-HAT: Driving 8th notes with procedural dynamics ===
  const is8thNote = sixteenthPosition % 2 === 0;

  if (is8thNote) {
    // Open hat on offbeats for certain bars (positions 2, 6, 10, 14)
    const isOffbeat = sixteenthPosition % 4 === 2;
    const openHatBars = [1, 3]; // Open hats on bars 1 and 3 of each 4-bar phrase
    const useOpenHat = isOffbeat && openHatBars.includes(barVariation) && (sixteenthPosition === 6 || sixteenthPosition === 14);

    if (useOpenHat) {
      notes.push({ type: 'ride', velocity: 0.55 + seed * 0.1 });
    } else {
      // Closed hat with humanized velocity
      const baseVel = isOffbeat ? 0.5 : 0.65;
      const humanize = (seed - 0.5) * 0.06;
      notes.push({ type: 'hihat', velocity: baseVel + humanize });
    }
  }

  // Add 16th note hi-hats on every other phrase for energy buildup
  if (phrasePosition >= 6 && sixteenthPosition % 2 === 1) {
    notes.push({ type: 'hihat', velocity: 0.35 + seed * 0.1 });
  }

  return notes;
}

/**
 * TRAP PATTERN - 808-style with hi-hat rolls and sparse kicks
 *
 * Inspired by trap/electronic - heavy, spacious, rhythmic hi-hats.
 * - Sparse 808-style kicks with sub-bass weight
 * - Snare/clap on 2 and 4
 * - Rolling hi-hats (16th notes) with velocity waves
 * - Procedural variation through: hi-hat patterns, kick placement, rolls
 */
function getFunkPattern(
  sixteenthPosition: number,
  measureNum: number = 0
): { type: PercussionNote['type']; velocity: number; ghost?: boolean }[] {
  const notes: { type: PercussionNote['type']; velocity: number; ghost?: boolean }[] = [];

  // Procedural variation
  const barVariation = measureNum % 4;
  const phrasePosition = measureNum % 8;
  const seed = (measureNum * 1.618033988749 + sixteenthPosition * 0.414213562373) % 1;

  // === KICK: Sparse 808-style pattern ===
  // Different kick patterns per bar, all simple and driving
  const kickPatterns: Record<number, number[]> = {
    0: [0, 10],           // Classic trap: 1 and "and of 3"
    1: [0, 6, 10],        // Add "and of 2"
    2: [0, 14],           // 1 and anticipation
    3: [0, 10, 14],       // Fuller pattern
  };

  const currentKicks = kickPatterns[barVariation];
  if (currentKicks.includes(sixteenthPosition)) {
    const kickVel = sixteenthPosition === 0 ? 0.95 : 0.8;
    notes.push({ type: 'kick', velocity: kickVel });
  }

  // === SNARE: Clean backbeat on 2 and 4 ===
  if (sixteenthPosition === 4 || sixteenthPosition === 12) {
    notes.push({ type: 'snare', velocity: 0.9 });
  }

  // === HI-HAT: Rolling 16th notes with velocity waves ===
  // Every 16th note gets a hi-hat for that rolling trap feel

  // Velocity pattern creates a "wave" through the bar
  // Accents on downbeats and upbeats, softer on "e" and "a"
  let hatVel: number;
  const beatPosition = sixteenthPosition % 4;

  if (beatPosition === 0) {
    hatVel = 0.7;  // Downbeat
  } else if (beatPosition === 2) {
    hatVel = 0.55; // Upbeat
  } else {
    hatVel = 0.35; // "e" and "a" - softer for roll feel
  }

  // Humanize with seed
  hatVel += (seed - 0.5) * 0.08;

  // Open hat accents on offbeats (every other bar)
  const useOpenHat = (barVariation === 1 || barVariation === 3) &&
                     (sixteenthPosition === 6 || sixteenthPosition === 14);

  if (useOpenHat) {
    notes.push({ type: 'ride', velocity: 0.5 + seed * 0.1 });
  } else {
    notes.push({ type: 'hihat', velocity: Math.max(0.25, Math.min(0.75, hatVel)) });
  }

  // Hi-hat roll buildup on last 2 bars of each 8-bar phrase
  // Triplet feel by adding extra hats
  if (phrasePosition >= 6 && sixteenthPosition % 2 === 1 && seed > 0.5) {
    notes.push({ type: 'hihat', velocity: 0.25 + seed * 0.1 });
  }

  return notes;
}

/**
 * 4-BAR FILL: Simple snare buildup
 *
 * Keeps the driving feel, just adds energy on beat 4.
 * Beats 1-3: Normal groove
 * Beat 4: Snare hits building to downbeat
 */
function get4BarFill(
  sixteenthPosition: number
): { type: PercussionNote['type']; velocity: number; ghost?: boolean }[] {
  if (sixteenthPosition < 12) {
    // Beats 1-3: Normal driving groove
    return getRockPattern(sixteenthPosition);
  }

  // Beat 4: Quick snare buildup
  const notes: { type: PercussionNote['type']; velocity: number; ghost?: boolean }[] = [];
  const vel = 0.6 + ((sixteenthPosition - 12) / 4) * 0.35;
  notes.push({ type: 'snare', velocity: vel });
  notes.push({ type: 'hihat', velocity: 0.5 });

  return notes;
}

/**
 * 8-BAR FILL: Snare roll buildup
 *
 * Driving buildup with increasing intensity.
 * Beats 1-2: Normal groove
 * Beats 3-4: Snare 16ths building in velocity
 */
function get8BarFill(
  sixteenthPosition: number
): { type: PercussionNote['type']; velocity: number }[] {
  if (sixteenthPosition < 8) {
    // Beats 1-2: Normal groove
    return getRockPattern(sixteenthPosition);
  }

  // Beats 3-4: Building snare roll
  const notes: { type: PercussionNote['type']; velocity: number }[] = [];
  const vel = 0.5 + ((sixteenthPosition - 8) / 8) * 0.45;
  notes.push({ type: 'snare', velocity: vel });

  // Keep kick on beats
  if (sixteenthPosition === 8 || sixteenthPosition === 12) {
    notes.push({ type: 'kick', velocity: 0.85 });
  }

  // Hi-hat continues
  if (sixteenthPosition % 2 === 0) {
    notes.push({ type: 'hihat', velocity: 0.5 });
  }

  return notes;
}

/**
 * 16-BAR FILL: Full bar snare roll with crash
 *
 * Big energy fill - snare roll through entire bar.
 * All 4 beats: Snare 16ths building to crash
 */
function get16BarFill(
  sixteenthPosition: number
): { type: PercussionNote['type']; velocity: number }[] {
  const notes: { type: PercussionNote['type']; velocity: number }[] = [];

  // Full bar snare roll, building intensity
  const vel = 0.45 + (sixteenthPosition / 16) * 0.5;
  notes.push({ type: 'snare', velocity: vel });

  // Kick on every beat for driving power
  if (sixteenthPosition % 4 === 0) {
    notes.push({ type: 'kick', velocity: 0.85 });
  }

  // Crash anticipation on 15
  if (sixteenthPosition === 15) {
    notes.push({ type: 'crash', velocity: 0.7 });
  }

  return notes;
}

/**
 * 32-BAR FILL: Epic 2-bar buildup
 *
 * Simple but powerful - snare roll building over 2 bars.
 * BAR 1 (fillPhase = 0): Snare roll starting soft
 * BAR 2 (fillPhase = 1): Snare roll reaching max + crash
 */
function get32BarFill(
  sixteenthPosition: number,
  fillPhase: 0 | 1
): { type: PercussionNote['type']; velocity: number; ghost?: boolean }[] {
  const notes: { type: PercussionNote['type']; velocity: number; ghost?: boolean }[] = [];

  // Global position across both bars (0-31)
  const globalPos = fillPhase * 16 + sixteenthPosition;

  // Snare roll building over 2 bars
  const vel = 0.35 + (globalPos / 32) * 0.6;
  notes.push({ type: 'snare', velocity: vel });

  // Kick on every beat for driving power
  if (sixteenthPosition % 4 === 0) {
    notes.push({ type: 'kick', velocity: 0.8 + (globalPos / 32) * 0.2 });
  }

  // Crash on downbeat of bar 1 and anticipation on final 16th
  if (fillPhase === 0 && sixteenthPosition === 0) {
    notes.push({ type: 'crash', velocity: 0.7 });
  }
  if (fillPhase === 1 && sixteenthPosition === 15) {
    notes.push({ type: 'crash', velocity: 0.9 });
  }

  return notes;
}

/**
 * Update percussion bar tracking when entering a new measure.
 * Style changes ONLY at 16-bar boundaries (deterministic, not random).
 */
export function updatePercussionBarPosition(state: FugueStateData): FugueStateData['percussion'] {
  const perc = state.percussion;
  const newMeasure = perc.measureCount + 1;

  const newBar8 = newMeasure % 8;
  const newBar16 = newMeasure % 16;
  const newBar32 = newMeasure % 32;

  // Section (A/B) determines style - changes at 16-bar boundary ONLY
  const newSection: 'A' | 'B' = newBar16 < 8 ? 'A' : 'B';

  // Style is DETERMINISTIC: A = rock, B = funk (based on intensity threshold)
  // High intensity (>0.5) → B section becomes funk
  // Low intensity → stays rock even in B section
  const newStyle: 'rock' | 'funk' =
    newSection === 'B' && state.intensity > 0.5 ? 'funk' : 'rock';

  return {
    measureCount: newMeasure,
    barPosition8: newBar8,
    barPosition16: newBar16,
    barPosition32: newBar32,
    section: newSection,
    style: newStyle,
    fillCooldown: Math.max(0, perc.fillCooldown - 1),
    lastFillBar: perc.lastFillBar,
    lastPlayedSixteenth: perc.lastPlayedSixteenth, // Preserve timing tracker
  };
}

/**
 * Generate percussion with CONSISTENT base patterns and STRUCTURED fills.
 *
 * TIMING FIX: Uses discrete 16th note tracking to ensure EVERY note plays.
 * The old approach used continuous timing windows that could miss notes.
 *
 * CONSISTENCY RULES:
 * - Rock pattern is IDENTICAL every bar (no random variations)
 * - Funk pattern is IDENTICAL every bar (including ghost notes)
 * - Style changes ONLY at 16-bar boundaries
 * - Fills ONLY at 8/16/32 bar boundaries
 *
 * Returns notes AND the updated lastPlayedSixteenth for state tracking.
 */
export function generatePercussion(
  state: FugueStateData,
  currentTime: number,
  beatDuration: number
): { notes: PercussionNote[]; newLastSixteenth: number } {
  const notes: PercussionNote[] = [];
  const perc = state.percussion;

  // Skip during silent phases
  if (state.phase === 'silence' || state.phase === 'coda') {
    return { notes, newLastSixteenth: perc.lastPlayedSixteenth };
  }

  // Skip during grand opening when percussion is muted
  // This allows the fugue subject to breathe in its initial statement
  if (state.percussionMuted) {
    return { notes, newLastSixteenth: perc.lastPlayedSixteenth };
  }

  // Normal time: 4 subdivisions per beat (16th note grid)
  // Pattern positions 0-15 span one full measure (4 beats)
  const sixteenthsPerBeat = 4; // Normal time - 16th note grid
  const sixteenthsPerMeasure = state.beatsPerMeasure * sixteenthsPerBeat; // 16 per measure
  const currentGlobalSixteenth = Math.floor(state.currentBeat * sixteenthsPerBeat);

  // Track which 16th notes need to play
  const lastPlayed = perc.lastPlayedSixteenth;
  let newLastSixteenth = lastPlayed;

  // If first update, start from current position
  const startSixteenth = lastPlayed < 0 ? currentGlobalSixteenth : lastPlayed + 1;

  // Don't try to catch up too many notes (max 16, prevents audio overload)
  const endSixteenth = Math.min(currentGlobalSixteenth, startSixteenth + 15);

  // Nothing new to play
  if (startSixteenth > currentGlobalSixteenth) {
    return { notes, newLastSixteenth };
  }

  // Velocity and duration params
  const baseVelocity = 0.8 + state.intensity * 0.2; // Boosted for presence
  const dynamicMod = 0.8 + state.globalDynamic * 0.2;
  const sixteenthDuration = beatDuration / 4; // Normal 16th note duration

  // Emit notes for each 16th we've passed
  for (let sixteenthIdx = startSixteenth; sixteenthIdx <= endSixteenth; sixteenthIdx++) {
    // Pattern position (0-15) - one full measure at normal time
    const sixteenthPosition = sixteenthIdx % 16;

    // Which measure is this 16th in? (16 subdivisions per measure at normal time)
    const measureNum = Math.floor(sixteenthIdx / sixteenthsPerMeasure);

    // Calculate bar positions for structural fills
    const barInPhrase4 = measureNum % 4;
    const barInPhrase8 = measureNum % 8;
    const barInPhrase16 = measureNum % 16;
    const barInPhrase32 = measureNum % 32;

    // Determine structural position
    const isLastBar4 = barInPhrase4 === 3;  // Every 4 bars
    const isLastBar8 = barInPhrase8 === 7;  // Every 8 bars
    const isLastBar16 = barInPhrase16 === 15;
    const isLastBar32 = barInPhrase32 === 31;
    const isSecondToLastBar32 = barInPhrase32 === 30;

    // Get pattern for this 16th note
    let patternNotes: { type: PercussionNote['type']; velocity: number; ghost?: boolean }[];
    let fillType: string | null = null;

    // FILL SELECTION - HIERARCHICAL (bigger fills override smaller ones)
    // This ensures you ALWAYS hear the musical structure
    if (isLastBar32 || isSecondToLastBar32) {
      // 32-bar epic fill (2 bars) - THE BIG ONE
      const fillPhase = isSecondToLastBar32 ? 0 : 1;
      patternNotes = get32BarFill(sixteenthPosition, fillPhase as 0 | 1);
      fillType = `32-bar-phase${fillPhase}`;
    } else if (isLastBar16) {
      // 16-bar fill - ALWAYS plays
      patternNotes = get16BarFill(sixteenthPosition);
      fillType = '16-bar';
    } else if (isLastBar8) {
      // 8-bar fill - ALWAYS plays
      patternNotes = get8BarFill(sixteenthPosition);
      fillType = '8-bar';
    } else if (isLastBar4) {
      // 4-bar mini-fill - quick accent every 4 bars (~16 seconds at 60 BPM)
      patternNotes = get4BarFill(sixteenthPosition);
      fillType = '4-bar';
    } else {
      // NORMAL PATTERN - syncopated groove with procedural variation
      // Pass measureNum so patterns can evolve over time
      if (perc.style === 'funk') {
        patternNotes = getFunkPattern(sixteenthPosition, measureNum);
      } else {
        patternNotes = getRockPattern(sixteenthPosition, measureNum);
      }
    }

    // Debug: Log when fills start (only on first 16th of fill)
    if (fillType && sixteenthPosition === 0) {
      console.log(`🥁 FILL: ${fillType} | measure=${measureNum} | bar4=${barInPhrase4} | bar8=${barInPhrase8}`);
    }

    // Calculate exact time for this 16th note
    // (offset from currentTime based on how far behind we are)
    const offsetSixteenths = sixteenthIdx - currentGlobalSixteenth;
    const noteTime = currentTime + (offsetSixteenths * sixteenthDuration);

    // Convert to PercussionNote objects
    for (const pNote of patternNotes) {
      const velocity = pNote.velocity * baseVelocity * dynamicMod * (pNote.ghost ? 0.4 : 1.0);

      let duration: number;
      switch (pNote.type) {
        case 'kick': duration = sixteenthDuration * 2; break;
        case 'snare': duration = pNote.ghost ? sixteenthDuration * 0.5 : sixteenthDuration * 1.5; break;
        case 'hihat': duration = sixteenthDuration * 0.8; break;
        case 'tom': duration = sixteenthDuration * 2.5; break;
        case 'crash': duration = beatDuration * 4; break;
        case 'ride': duration = sixteenthDuration * 1.5; break;
        default: duration = sixteenthDuration;
      }

      notes.push({
        type: pNote.type,
        startTime: noteTime,
        velocity: Math.min(1.0, velocity),
        duration,
        ghost: pNote.ghost,
      });
    }

    // CRASH on beat 1 of new sections
    if (sixteenthPosition === 0 && measureNum > 0) {
      // Crash after 32-bar fill (new section)
      if (barInPhrase32 === 0) {
        notes.push({
          type: 'crash',
          startTime: noteTime,
          velocity: 0.95 * dynamicMod,
          duration: beatDuration * 4,
        });
      }
      // Crash after 16-bar fill (if not also a 32-bar boundary)
      else if (barInPhrase16 === 0 && state.intensity > 0.4) {
        notes.push({
          type: 'crash',
          startTime: noteTime,
          velocity: 0.7 * dynamicMod,
          duration: beatDuration * 3,
        });
      }
    }

    newLastSixteenth = sixteenthIdx;
  }

  return { notes, newLastSixteenth };
}

// =============================================================================
// PHRASE STRUCTURE SYSTEM: Nested 8/16/32 Bar Orchestration
// =============================================================================
//
// Musical phrases are hierarchically nested:
// - 8-bar "Sentence": Basic musical thought with a small arc
// - 16-bar "Period": Statement + Response with medium arc
// - 32-bar "Section": Complete musical journey with large arc
//
// Each level can have an "Orchestration Theme" that colors the passage:
// - Ornamented: More trills, turns, and embellishments
// - Legato: Long flowing lines, connected phrases
// - Staccato: Detached, rhythmic energy
// - Chromatic: Added passing tones, color notes
// - Sparse: Fewer notes, more space
// - Dense: More voices, thicker texture
// - Modal: Borrowed chords, mode mixture
// - Sequential: Rising/falling patterns
// =============================================================================

/**
 * Orchestration themes that can flavor a phrase
 */
export type OrchestrationTheme =
  | 'neutral'      // No special coloring
  | 'ornamented'   // More trills, mordents, turns
  | 'legato'       // Long flowing lines
  | 'staccato'     // Detached, percussive
  | 'chromatic'    // Added passing tones
  | 'sparse'       // Fewer notes, more rests
  | 'dense'        // More voices, thick texture
  | 'modal'        // Mode mixture, borrowed chords
  | 'sequential'   // Rising/falling sequences
  | 'dramatic';    // Wide dynamics, sforzando

/**
 * Key coloring modes for modal inflections
 */
export type KeyColoring =
  | 'natural'      // Pure C# minor
  | 'harmonic'     // Raised 7th (B#)
  | 'melodic'      // Raised 6th and 7th ascending
  | 'dorian'       // Raised 6th (A#)
  | 'phrygian'     // Lowered 2nd (D natural)
  | 'neapolitan';  // Lowered 2nd for Neapolitan chord

/**
 * Phrase state tracking nested structures
 */
export interface PhraseState {
  // Position within each level (0-based)
  bar8Position: number;    // 0-7 within 8-bar phrase
  bar16Position: number;   // 0-15 within 16-bar period
  bar32Position: number;   // 0-31 within 32-bar section

  // Total counts
  totalBars: number;

  // Current orchestration themes at each level
  theme8: OrchestrationTheme;   // Theme for current 8-bar phrase
  theme16: OrchestrationTheme;  // Theme for current 16-bar period
  theme32: OrchestrationTheme;  // Theme for current 32-bar section

  // Key coloring
  keyColoring: KeyColoring;

  // Dynamic contour tracking
  phraseContour8: number;   // 0-1 position in 8-bar dynamic arc
  phraseContour16: number;  // 0-1 position in 16-bar dynamic arc
  phraseContour32: number;  // 0-1 position in 32-bar dynamic arc

  // Phrase-level tension (separate from game-driven tension)
  phraseTension: number;    // 0-1 musical tension within phrase

  // Run/sequence tracking
  currentRunLength: number; // How many notes in current run
  runDirection: 'ascending' | 'descending' | 'none';

  // === CONTRAST SYSTEM: Creates musical breathing room ===
  contrastEvent: ContrastEvent | null;  // Active contrast moment
  contrastCooldown: number;             // Bars until next contrast allowed
  lastContrastBar: number;              // When last contrast occurred
}

/**
 * Contrast events create moments of musical interest and breathing room.
 * These thin the texture and provide contrast to busy passages.
 */
export type ContrastEvent =
  | 'subito_piano'      // Sudden drop to soft - all voices soften dramatically
  | 'solo_breath'       // Only one voice plays for 2-4 bars
  | 'sustained_chord'   // Voices hold long notes instead of activity
  | 'call_response'     // Voices alternate instead of overlapping
  | 'register_shift'    // All voices move to high or low register
  | 'thinning'          // Reduce to 2 voices maximum
  | 'silence_beat';     // Brief pause before tutti

/**
 * Create initial phrase state
 */
export function createPhraseState(): PhraseState {
  return {
    bar8Position: 0,
    bar16Position: 0,
    bar32Position: 0,
    totalBars: 0,
    theme8: 'neutral',
    theme16: 'neutral',
    theme32: 'neutral',
    keyColoring: 'harmonic',
    phraseContour8: 0,
    phraseContour16: 0,
    phraseContour32: 0,
    phraseTension: 0.3,
    currentRunLength: 0,
    runDirection: 'none',
    contrastEvent: null,
    contrastCooldown: 0,
    lastContrastBar: -16, // Allow contrast from the start
  };
}

/**
 * Possibly trigger a contrast event at phrase boundaries.
 * Contrast creates breathing room and musical interest.
 *
 * IMPORTANT: Check largest boundaries first (32 → 16 → 8) because
 * a 32-bar boundary is also a 16-bar and 8-bar boundary.
 */
export function maybeGenerateContrast(
  state: PhraseState,
  intensity: number
): ContrastEvent | null {
  // Don't trigger if on cooldown
  if (state.contrastCooldown > 0) return null;

  // Contrast chances at different phrase boundaries
  // Higher intensity = more contrast (need breathing room when busy)
  const contrastChance = intensity > 0.6 ? 0.25 : 0.15;

  // 32-bar boundary: dramatic contrast moments (CHECK FIRST!)
  if (state.bar32Position === 0 && Math.random() < contrastChance * 1.5) {
    const events: ContrastEvent[] = ['silence_beat', 'register_shift', 'solo_breath', 'subito_piano'];
    return events[Math.floor(Math.random() * events.length)];
  }

  // 16-bar boundary: medium contrast moments (check second)
  if (state.bar16Position === 0 && Math.random() < contrastChance) {
    const events: ContrastEvent[] = ['subito_piano', 'solo_breath', 'sustained_chord', 'thinning'];
    return events[Math.floor(Math.random() * events.length)];
  }

  // 8-bar boundary: small contrast moments (check last)
  if (state.bar8Position === 0 && Math.random() < contrastChance * 0.5) {
    const events: ContrastEvent[] = ['thinning', 'call_response'];
    return events[Math.floor(Math.random() * events.length)];
  }

  return null;
}

/**
 * Get contrast modifiers that affect note generation.
 * Returns multipliers and flags for the current contrast state.
 */
export function getContrastModifiers(contrast: ContrastEvent | null): {
  velocityMult: number;      // Multiply velocity
  restChanceMult: number;    // Multiply rest insertion chance
  maxVoices: number;         // Maximum simultaneous voices
  durationMult: number;      // Multiply duration
  soloVoice: VoiceRegister | null;  // If set, only this voice plays
} {
  if (!contrast) {
    return {
      velocityMult: 1.0,
      restChanceMult: 1.0,
      maxVoices: 4,
      durationMult: 1.0,
      soloVoice: null,
    };
  }

  switch (contrast) {
    case 'subito_piano':
      return {
        velocityMult: 0.4,      // Much softer
        restChanceMult: 1.5,    // More rests
        maxVoices: 4,
        durationMult: 1.2,      // Slightly longer notes
        soloVoice: null,
      };

    case 'solo_breath':
      // Randomly select which voice solos
      const soloVoices: VoiceRegister[] = ['soprano', 'alto', 'tenor', 'bass'];
      return {
        velocityMult: 0.8,
        restChanceMult: 0.5,    // Fewer rests for solo voice
        maxVoices: 1,
        durationMult: 1.3,
        soloVoice: soloVoices[Math.floor(Math.random() * soloVoices.length)],
      };

    case 'sustained_chord':
      return {
        velocityMult: 0.7,
        restChanceMult: 0.3,    // Almost no rests - sustained notes
        maxVoices: 4,
        durationMult: 2.5,      // Very long notes
        soloVoice: null,
      };

    case 'call_response':
      return {
        velocityMult: 0.9,
        restChanceMult: 2.0,    // More rests create alternation
        maxVoices: 2,           // Only 2 voices at a time
        durationMult: 1.0,
        soloVoice: null,
      };

    case 'register_shift':
      return {
        velocityMult: 0.85,
        restChanceMult: 1.2,
        maxVoices: 3,
        durationMult: 1.1,
        soloVoice: null,
      };

    case 'thinning':
      return {
        velocityMult: 0.75,
        restChanceMult: 2.5,    // Much more rests
        maxVoices: 2,           // Only 2 voices
        durationMult: 1.4,
        soloVoice: null,
      };

    case 'silence_beat':
      return {
        velocityMult: 0.3,      // Almost silent
        restChanceMult: 4.0,    // Heavy rest insertion
        maxVoices: 1,
        durationMult: 0.5,
        soloVoice: null,
      };

    default:
      return {
        velocityMult: 1.0,
        restChanceMult: 1.0,
        maxVoices: 4,
        durationMult: 1.0,
        soloVoice: null,
      };
  }
}

/**
 * Select an orchestration theme based on position and context
 *
 * PHRASE STRUCTURE LOGIC:
 * - 8-bar: Small decisions, ornament vs clean
 * - 16-bar: Medium decisions, texture changes
 * - 32-bar: Large decisions, key/mode changes
 */
export function selectOrchestrationTheme(
  level: 8 | 16 | 32,
  position: number,
  intensity: number,
  gamePhase: FugueStateData['gamePhase'],
  previousTheme: OrchestrationTheme
): OrchestrationTheme {
  // Theme weights based on context
  // REBALANCED: Reduced neutral dominance (was 23%), boosted underused themes
  const weights: Record<OrchestrationTheme, number> = {
    neutral: 6,       // Reduced from 10 - was too dominant, causing bland passages
    ornamented: 6,    // Slightly boosted - more musical interest
    legato: 7,        // Slightly reduced from 8
    staccato: 5,
    chromatic: 5,     // Boosted from 4 - chromatic color adds interest
    sparse: 5,        // Reduced from 6 - balance with dense
    dense: 5,         // Boosted from 4 - match sparse
    modal: 5,         // Boosted from 3 - was critically underselected
    sequential: 7,    // Boosted from 6 - runs are musically valuable
    dramatic: 5,      // Boosted from 3 - was critically underselected
  };

  // Modify weights based on intensity
  if (intensity > 0.7) {
    weights.dense *= 2;
    weights.staccato *= 1.5;
    weights.dramatic *= 2;
    weights.sparse *= 0.3;
  } else if (intensity < 0.3) {
    weights.sparse *= 2;
    weights.legato *= 1.5;
    weights.dense *= 0.3;
    weights.dramatic *= 0.3;
  }

  // Modify based on game phase
  if (gamePhase === 'crisis') {
    weights.chromatic *= 2;
    weights.dramatic *= 2.5;
    weights.staccato *= 1.5;
  } else if (gamePhase === 'exploration') {
    weights.legato *= 1.5;
    weights.sparse *= 1.5;
    weights.ornamented *= 1.2;
  } else if (gamePhase === 'combat') {
    weights.staccato *= 1.5;
    weights.sequential *= 1.5;
    weights.dense *= 1.3;
  }

  // Position within phrase affects theme
  // First half: more neutral, last half: more dramatic
  const phraseProgress = position / (level - 1);
  if (phraseProgress > 0.6) {
    weights.dramatic *= 1.5;
    weights.dense *= 1.3;
  }
  if (phraseProgress < 0.3) {
    weights.sparse *= 1.3;
    weights.neutral *= 1.5;
  }

  // Avoid repeating same theme (unless neutral)
  if (previousTheme !== 'neutral') {
    weights[previousTheme] *= 0.3;
  }

  // Level-specific preferences
  if (level === 8) {
    // 8-bar: favor ornament/articulation changes
    weights.ornamented *= 1.5;
    weights.staccato *= 1.3;
    weights.legato *= 1.3;
  } else if (level === 16) {
    // 16-bar: favor texture changes
    weights.dense *= 1.3;
    weights.sparse *= 1.3;
    weights.sequential *= 1.5;
  } else {
    // 32-bar: favor harmonic/modal changes
    weights.chromatic *= 1.5;
    weights.modal *= 2;
    weights.dramatic *= 1.5;
  }

  // Weighted random selection
  const total = Object.values(weights).reduce((a, b) => a + b, 0);
  let rand = Math.random() * total;

  for (const [theme, weight] of Object.entries(weights)) {
    rand -= weight;
    if (rand <= 0) {
      return theme as OrchestrationTheme;
    }
  }

  return 'neutral';
}

/**
 * Select key coloring for a 32-bar section
 */
export function selectKeyColoring(
  intensity: number,
  gamePhase: FugueStateData['gamePhase'],
  previousColoring: KeyColoring
): KeyColoring {
  const weights: Record<KeyColoring, number> = {
    natural: 8,
    harmonic: 15,    // Default home key
    melodic: 6,
    dorian: 4,
    phrygian: 3,
    neapolitan: 2,
  };

  // Crisis/high intensity: more chromatic color
  if (intensity > 0.6 || gamePhase === 'crisis') {
    weights.phrygian *= 2;
    weights.neapolitan *= 2;
    weights.harmonic *= 0.7;
  }

  // Low intensity: more diatonic
  if (intensity < 0.3) {
    weights.natural *= 2;
    weights.melodic *= 1.5;
    weights.phrygian *= 0.5;
  }

  // Avoid same coloring twice
  if (previousColoring !== 'harmonic') {
    weights[previousColoring] *= 0.3;
  }

  // Weighted selection
  const total = Object.values(weights).reduce((a, b) => a + b, 0);
  let rand = Math.random() * total;

  for (const [coloring, weight] of Object.entries(weights)) {
    rand -= weight;
    if (rand <= 0) {
      return coloring as KeyColoring;
    }
  }

  return 'harmonic';
}

/**
 * Calculate phrase contour (dynamic arc position) for a given level
 *
 * TENSION CURVES:
 * - 8-bar: build 5 bars, peak bar 6, release 2 bars
 * - 16-bar: build 10 bars, peak bars 11-12, release 4 bars
 * - 32-bar: build 20 bars, peak bars 21-24, release 8 bars
 */
export function calculatePhraseContour(position: number, level: 8 | 16 | 32): number {
  // FIX: Use continuous bell-curve approach for smooth tension arcs
  // Previous 8-bar implementation had 0.8→1.0 discontinuity at position 5

  if (level === 8) {
    // 8-bar: Symmetric bell curve with peak at position 5
    // Continuous: pos 0→0, pos 4→0.8, pos 5→1.0, pos 6→0.8, pos 7→0.6
    const peak = 5;
    const distance = Math.abs(position - peak);
    return Math.max(0, 1.0 - distance * 0.2);
  } else if (level === 16) {
    // 16-bar: Gradual build, sustained peak, gradual release
    if (position < 10) {
      return (position / 10) * 0.9;   // Rise to 0.9
    } else if (position < 12) {
      return 0.9 + ((position - 10) / 2) * 0.1;  // Peak climb to 1.0
    } else {
      return 1.0 - ((position - 12) / 4);  // Gradual fall
    }
  } else {
    // 32-bar: Long build, extended peak, long release
    if (position < 20) {
      return (position / 20) * 0.85;   // Rise to 0.85
    } else if (position < 24) {
      return 0.85 + ((position - 20) / 4) * 0.15;  // Peak climb to 1.0
    } else {
      return 1.0 - ((position - 24) / 8);  // Long fall
    }
  }
}

/**
 * Update phrase state when crossing bar boundaries
 */
export function updatePhraseState(
  state: PhraseState,
  intensity: number,
  gamePhase: FugueStateData['gamePhase']
): PhraseState {
  const newState = { ...state };

  // Advance positions
  newState.bar8Position = (state.bar8Position + 1) % 8;
  newState.bar16Position = (state.bar16Position + 1) % 16;
  newState.bar32Position = (state.bar32Position + 1) % 32;
  newState.totalBars = state.totalBars + 1;

  // Update contours
  newState.phraseContour8 = calculatePhraseContour(newState.bar8Position, 8);
  newState.phraseContour16 = calculatePhraseContour(newState.bar16Position, 16);
  newState.phraseContour32 = calculatePhraseContour(newState.bar32Position, 32);

  // Calculate phrase tension from weighted contours
  // 32-bar has most weight, 8-bar least
  newState.phraseTension =
    newState.phraseContour8 * 0.2 +
    newState.phraseContour16 * 0.3 +
    newState.phraseContour32 * 0.5;

  // === CONTRAST SYSTEM: Manage contrast events ===
  // Decrement cooldown
  if (newState.contrastCooldown > 0) {
    newState.contrastCooldown--;
  }

  // End active contrast after its duration (typically 2-4 bars)
  if (state.contrastEvent !== null) {
    const barsSinceContrast = newState.totalBars - state.lastContrastBar;
    const contrastDuration = getContrastDuration(state.contrastEvent);
    if (barsSinceContrast >= contrastDuration) {
      newState.contrastEvent = null;
    }
  }

  // Maybe trigger new contrast at phrase boundaries
  if (state.contrastEvent === null) {
    const newContrast = maybeGenerateContrast(newState, intensity);
    if (newContrast) {
      newState.contrastEvent = newContrast;
      newState.lastContrastBar = newState.totalBars;
      // Set cooldown: 8-16 bars before next contrast allowed
      newState.contrastCooldown = 8 + Math.floor(Math.random() * 8);
    }
  }

  // Select new themes at phrase boundaries
  if (newState.bar8Position === 0) {
    // New 8-bar phrase - select new theme
    newState.theme8 = selectOrchestrationTheme(8, 0, intensity, gamePhase, state.theme8);
  }

  if (newState.bar16Position === 0) {
    // New 16-bar period - select new theme
    newState.theme16 = selectOrchestrationTheme(16, 0, intensity, gamePhase, state.theme16);
  }

  if (newState.bar32Position === 0) {
    // New 32-bar section - select new theme AND key coloring
    newState.theme32 = selectOrchestrationTheme(32, 0, intensity, gamePhase, state.theme32);
    newState.keyColoring = selectKeyColoring(intensity, gamePhase, state.keyColoring);
  }

  return newState;
}

/**
 * Get duration in bars for each contrast type
 */
function getContrastDuration(contrast: ContrastEvent): number {
  switch (contrast) {
    case 'silence_beat': return 1;      // Very brief
    case 'subito_piano': return 2;      // Quick effect
    case 'thinning': return 3;          // Short thinning
    case 'call_response': return 4;     // Medium duration
    case 'solo_breath': return 4;       // Let solo voice breathe
    case 'sustained_chord': return 4;   // Hold the moment
    case 'register_shift': return 2;    // Quick shift
    default: return 2;
  }
}

/**
 * Get the active orchestration theme, with priority to higher-level themes
 */
export function getActiveTheme(phraseState: PhraseState): OrchestrationTheme {
  // Priority: 32-bar > 16-bar > 8-bar
  if (phraseState.theme32 !== 'neutral') return phraseState.theme32;
  if (phraseState.theme16 !== 'neutral') return phraseState.theme16;
  if (phraseState.theme8 !== 'neutral') return phraseState.theme8;
  return 'neutral';
}

/**
 * Get the KENT variation index for a journey section
 *
 * The journey follows a narrative arc:
 * - Section 0: Grand opening - pure original statement
 * - Section 1-2: Exploration - tonal answer, sequences
 * - Section 3-4: Development - inversions, retrogrades, chromatic
 * - Section 5+: Recapitulation - returns to original with increasing frequency
 *
 * Variation indices:
 *   0: Original, 1: Tonal Answer, 2: Inversion, 3: Retrograde,
 *   4: Augmentation, 5: Diminution, 6: Chromatic, 7: Sequence
 */
export function getJourneyVariation(sectionNumber: number): number {
  // Grand opening: pure original statement
  if (sectionNumber === 0) return 0;

  // Exploration phase: answer and sequence
  if (sectionNumber === 1) return 1; // Tonal Answer
  if (sectionNumber === 2) return 7; // Sequence

  // Development phase: increasing complexity
  if (sectionNumber === 3) return 2; // Inversion
  if (sectionNumber === 4) {
    // Alternate between retrograde and diminution
    return Math.random() < 0.5 ? 3 : 5;
  }

  // Recapitulation arc: return to original with variations
  // Each section has increasing probability of returning to original
  const recapSection = sectionNumber - 5;
  const originalProbability = Math.min(0.3 + recapSection * 0.15, 0.8);

  if (Math.random() < originalProbability) {
    return 0; // Return to original
  }

  // Otherwise cycle through all variations
  const cycle = [1, 7, 2, 6, 3, 5, 4]; // Ordered by increasing intensity
  return cycle[recapSection % cycle.length];
}

/**
 * Apply key coloring to a semitone
 */
export function applyKeyColoring(semitone: number, coloring: KeyColoring): number {
  const normalized = ((semitone % 12) + 12) % 12;

  switch (coloring) {
    case 'natural':
      // Pure natural minor (no raised 7th)
      if (normalized === 11) return 10; // B# -> B
      return semitone;

    case 'harmonic':
      // Standard harmonic minor (raised 7th)
      return semitone; // Already in harmonic minor

    case 'melodic':
      // Melodic minor ascending (raised 6th and 7th)
      if (normalized === 8) return 9; // A -> A#
      return semitone;

    case 'dorian':
      // Dorian mode (raised 6th)
      if (normalized === 8) return 9; // A -> A#
      if (normalized === 11) return 10; // B# -> B
      return semitone;

    case 'phrygian':
      // Phrygian (lowered 2nd)
      if (normalized === 2) return 1; // D# -> D
      return semitone;

    case 'neapolitan':
      // Neapolitan (lowered 2nd, used for bII chord)
      if (normalized === 2) return 1; // D# -> D
      return semitone;

    default:
      return semitone;
  }
}

/**
 * Apply orchestration theme modifiers to a note
 */
export interface ThemeModifiers {
  velocityMod: number;      // Multiply velocity
  durationMod: number;      // Multiply duration
  ornamentChance: number;   // Override ornament probability
  restChance: number;       // Chance to insert rest
  runChance: number;        // Chance to start a run
  articulationOverride: FugueNote['articulation'] | null;
}

export function getThemeModifiers(
  theme: OrchestrationTheme,
  phraseContour: number,
  intensity: number
): ThemeModifiers {
  // === CONSECUTIVE VOICE TEXTURE ===
  // Base duration is 1.2x for harmonic overlap. Rest chances reduced
  // to favor more continuous melodic lines with voices singing together.
  const base: ThemeModifiers = {
    velocityMod: 1.0,
    durationMod: 1.2,             // 20% longer by default for overlap
    ornamentChance: STOCHASTIC_CONFIG.ornamentProbability * 0.6,  // Reduced ornamentation
    restChance: 0.05,             // 5% base rest chance - more consecutive notes
    runChance: 0.06,              // Reduced run chance (was 0.1)
    articulationOverride: null,
  };

  switch (theme) {
    case 'ornamented':
      base.ornamentChance = 0.25;  // Ornamentation (reduced from 0.35)
      base.durationMod = 1.05;     // Slightly shorter to fit ornaments
      base.runChance = 0.12;       // Reduced runs (was 0.2)
      base.restChance = 0.07;      // Light rests between ornaments
      break;

    case 'legato':
      base.durationMod = 1.4;      // 40% longer - rich sustained harmonies
      base.articulationOverride = 'legato';
      base.ornamentChance = 0.03;  // Very few ornaments
      base.restChance = 0.03;      // Very few rests - continuous singing
      break;

    case 'staccato':
      base.durationMod = 0.75;     // Short but not too clipped
      base.articulationOverride = 'staccato';
      base.velocityMod = 1.1;      // Slightly louder
      base.ornamentChance = 0.01;  // Almost no ornaments
      base.restChance = 0.1;       // Some space between staccato notes
      break;

    case 'chromatic':
      base.ornamentChance = 0.15;  // Reduced (was 0.25)
      base.runChance = 0.15;       // Reduced (was 0.25)
      base.durationMod = 1.25;     // Slight extra sustain
      base.restChance = 0.04;      // Continuous chromatic lines
      break;

    case 'sparse':
      base.restChance = 0.25;      // Sparse still has rests (reduced from 0.35)
      base.velocityMod = 0.85;     // Softer
      base.durationMod = 1.5;      // Very long held notes
      base.ornamentChance = 0.02;  // Almost no ornaments
      break;

    case 'dense':
      base.restChance = 0.02;      // Very dense - almost no rests
      base.velocityMod = 1.15;     // Louder
      base.durationMod = 1.0;      // Normal
      base.ornamentChance = 0.12;  // Reduced (was 0.2)
      break;

    case 'modal':
      base.ornamentChance = 0.1;   // Reduced (was 0.15)
      base.durationMod = 1.3;      // Modal themes benefit from sustain
      base.restChance = 0.06;      // Light rests for modal color
      break;

    case 'sequential':
      base.runChance = 0.25;       // Reduced sequences (was 0.4)
      base.ornamentChance = 0.05;  // Reduced (was 0.08)
      base.durationMod = 1.1;
      base.restChance = 0.04;      // Continuous sequences
      break;

    case 'dramatic':
      // Apply phrase contour to velocity
      base.velocityMod = 0.7 + phraseContour * 0.5;  // 0.7 to 1.2
      base.ornamentChance = 0.15 * phraseContour;    // Reduced (was 0.2)
      base.durationMod = 1.2 + phraseContour * 0.2;
      base.restChance = 0.04 * (1 - phraseContour);  // Very few rests
      base.articulationOverride = phraseContour > 0.7 ? 'marcato' : null;
      break;

    default:
      // Neutral: continuous with minimal rests
      break;
  }

  // Apply intensity scaling to velocity
  base.velocityMod *= (0.7 + intensity * 0.4);

  return base;
}

/**
 * Generate a melodic run (ascending or descending scale passage)
 */
export function generateMelodicRun(
  startSemitone: number,
  direction: 'ascending' | 'descending',
  length: number,
  keyColoring: KeyColoring,
  baseDuration: number
): FugueNote[] {
  const notes: FugueNote[] = [];
  const step = direction === 'ascending' ? 1 : -1;

  let currentSemitone = startSemitone;
  const noteDuration = baseDuration / length;

  for (let i = 0; i < length; i++) {
    // Move by scale step
    currentSemitone = findNearestScaleTone(currentSemitone + step * 2);
    currentSemitone = applyKeyColoring(currentSemitone, keyColoring);

    // Crescendo for ascending, diminuendo for descending
    const velocityProgress = direction === 'ascending'
      ? 0.5 + (i / length) * 0.4
      : 0.9 - (i / length) * 0.3;

    notes.push({
      semitone: currentSemitone,
      duration: noteDuration,
      velocity: velocityProgress,
      articulation: i === length - 1 ? 'tenuto' : 'legato',
    });
  }

  return notes;
}

/**
 * Generate an extended ornament based on theme
 */
export function generateExtendedOrnament(
  baseSemitone: number,
  duration: number,
  theme: OrchestrationTheme,
  keyColoring: KeyColoring
): FugueNote[] {
  // Apply key coloring
  const coloredSemitone = applyKeyColoring(baseSemitone, keyColoring);

  if (theme === 'ornamented') {
    // Trill with turn
    const upper = findNearestScaleTone(coloredSemitone + 2);
    const lower = findNearestScaleTone(coloredSemitone - 1);
    const trillDur = duration * 0.1;
    return [
      { semitone: coloredSemitone, duration: trillDur, velocity: 0.7, articulation: 'legato' },
      { semitone: upper, duration: trillDur, velocity: 0.6, articulation: 'legato' },
      { semitone: coloredSemitone, duration: trillDur, velocity: 0.65, articulation: 'legato' },
      { semitone: upper, duration: trillDur, velocity: 0.55, articulation: 'legato' },
      { semitone: coloredSemitone, duration: trillDur, velocity: 0.6, articulation: 'legato' },
      { semitone: upper, duration: trillDur, velocity: 0.55, articulation: 'legato' },
      { semitone: coloredSemitone, duration: trillDur, velocity: 0.6, articulation: 'legato' },
      { semitone: lower, duration: trillDur, velocity: 0.5, articulation: 'legato' },
      { semitone: coloredSemitone, duration: trillDur * 2, velocity: 0.75, articulation: 'tenuto' },
    ];
  } else if (theme === 'chromatic') {
    // Chromatic passing tones
    const notes: FugueNote[] = [];
    const chromaticDur = duration / 5;
    for (let i = -2; i <= 2; i++) {
      notes.push({
        semitone: coloredSemitone + i,
        duration: chromaticDur,
        velocity: 0.5 + Math.abs(i === 0 ? 0.3 : 0),
        articulation: 'legato',
      });
    }
    return notes;
  } else {
    // Default ornament
    return generateOrnament(coloredSemitone, duration);
  }
}

// =============================================================================
// VOICE ASSIGNMENT FOR EACH PHASE
// =============================================================================

/**
 * Get the current KENT variation based on state and phase.
 * Uses the pre-generated variations (0-7) for musical variety.
 *
 * @internal - Called by assignVoiceMaterial
 */
function getCurrentVariation(state: FugueStateData): FugueNote[] {
  // Lazy import to avoid circular reference (KENT_VARIATIONS defined later)
  // At runtime, these are all available
  const variations = [
    KENT_VARIATION_0_ORIGINAL,
    KENT_VARIATION_1_TONAL_ANSWER,
    KENT_VARIATION_2_INVERSION,
    KENT_VARIATION_3_RETROGRADE,
    KENT_VARIATION_4_AUGMENTATION,
    KENT_VARIATION_5_DIMINUTION,
    KENT_VARIATION_6_CHROMATIC,
    KENT_VARIATION_7_SEQUENCE,
  ];

  const idx = Math.max(0, Math.min(7, state.currentVariationIndex));
  return variations[idx] || variations[0];
}

/**
 * Select the next variation based on intensity, phase, and avoid repetition.
 * Returns variation index (0-7).
 *
 * @internal - Called by assignVoiceMaterial
 */
function selectNextVariation(
  intensity: number,
  phase: FuguePhase,
  lastIndex: number | null
): number {
  // Variation suitability based on phase and intensity
  const phaseToVariations: Record<FuguePhase, number[]> = {
    silence: [0, 4],           // Original or augmentation
    exposition_1: [0, 4],      // Clear statement
    exposition_2: [1, 0],      // Tonal answer
    exposition_3: [0, 6],      // Original or chromatic
    exposition_4: [1, 7],      // Answer or sequence
    episode: [6, 7, 2],        // Chromatic, sequence, or inversion
    development: [2, 3, 5, 6], // Transformations
    stretto: [5, 0, 1],        // Diminution for speed
    pedal_point: [4, 3],       // Augmentation or retrograde
    recapitulation: [0, 7],    // Return to original or sequence
    coda: [4, 0],              // Majestic ending
  };

  const preferredVariations = phaseToVariations[phase] || [0, 1, 2];

  // Filter by intensity range
  const variationIntensityRanges: Record<number, [number, number]> = {
    0: [0.2, 0.7],  // Original
    1: [0.3, 0.8],  // Tonal answer
    2: [0.2, 0.6],  // Inversion
    3: [0.3, 0.7],  // Retrograde
    4: [0.1, 0.5],  // Augmentation
    5: [0.6, 1.0],  // Diminution
    6: [0.3, 0.7],  // Chromatic
    7: [0.4, 0.9],  // Sequence
  };

  // Score each variation
  const candidates: { idx: number; score: number }[] = [];

  for (let i = 0; i < 8; i++) {
    let score = 0;

    // Prefer phase-appropriate variations
    if (preferredVariations.includes(i)) {
      score += 15;
    }

    // Check intensity range
    const [minI, maxI] = variationIntensityRanges[i] || [0, 1];
    if (intensity >= minI && intensity <= maxI) {
      score += 10;
    }

    // Avoid repeating last variation
    if (i === lastIndex) {
      score -= 25;
    }

    // Small random factor
    score += Math.random() * 5;

    candidates.push({ idx: i, score });
  }

  candidates.sort((a, b) => b.score - a.score);
  return candidates[0].idx;
}

/**
 * Assign material to voices based on current phase.
 * Now uses pre-generated KENT variations for musical variety.
 */
export function assignVoiceMaterial(
  state: FugueStateData,
  phase: FuguePhase
): FugueStateData {
  const newState = { ...state };
  const voices = { ...state.voices };

  // Select a new variation for this phase
  const nextVariationIdx = selectNextVariation(
    state.intensity,
    phase,
    state.lastVariationIndex
  );
  newState.lastVariationIndex = state.currentVariationIndex;
  newState.currentVariationIndex = nextVariationIdx;

  // Get the current variation's notes
  const currentVariation = getCurrentVariation(newState);

  // Reset voices
  for (const register of Object.keys(voices) as VoiceRegister[]) {
    voices[register] = {
      ...voices[register],
      material: [],
      materialIndex: 0,
      isActive: false,
      beatOffset: 0,
    };
  }

  switch (phase) {
    case 'exposition_1':
      // Alto enters with subject - use selected variation
      // DENSITY FIX: Even in exposition_1, add bass for harmonic foundation
      voices.alto = {
        ...voices.alto,
        material: currentVariation,
        isActive: true,
        role: 'subject',
        beatOffset: 0,
      };
      // Bass provides harmonic foundation from the start (minimum 2 voices)
      voices.bass = {
        ...voices.bass,
        material: [
          { semitone: 0, duration: 4, velocity: 0.5, articulation: 'tenuto' },  // C# pedal
          { semitone: 7, duration: 2, velocity: 0.45, articulation: 'legato' }, // G# (dominant)
          { semitone: 0, duration: 2, velocity: 0.5, articulation: 'tenuto' },  // C# return
        ],
        isActive: true,
        role: 'free',
        beatOffset: 0,
      };
      newState.subjectEntryCount = 1;
      newState.lastSubjectVoice = 'alto';
      break;

    case 'exposition_2':
      // Soprano enters with answer, alto continues with countersubject
      // DENSITY FIX: Add bass for harmonic foundation (minimum 2 voices with bass priority)
      voices.soprano = {
        ...voices.soprano,
        material: createTonalAnswer(currentVariation),
        isActive: true,
        role: 'answer',
        beatOffset: 0,
      };
      voices.alto = {
        ...voices.alto,
        material: KENT_COUNTERSUBJECT,
        isActive: true,
        role: 'countersubject',
        beatOffset: 0,
      };
      // Bass provides harmonic foundation
      voices.bass = {
        ...voices.bass,
        material: [
          { semitone: 7, duration: 3, velocity: 0.5, articulation: 'tenuto' },  // G# (dominant for answer)
          { semitone: 5, duration: 2, velocity: 0.45, articulation: 'legato' }, // F# (subdominant)
          { semitone: 0, duration: 3, velocity: 0.55, articulation: 'tenuto' }, // C# (tonic)
        ],
        isActive: true,
        role: 'free',
        beatOffset: 0,
      };
      newState.subjectEntryCount = 2;
      newState.lastSubjectVoice = 'soprano';
      break;

    case 'exposition_3':
      // Tenor enters with subject, others continue
      // DENSITY FIX: Always include bass for harmonic foundation
      voices.tenor = {
        ...voices.tenor,
        material: currentVariation,
        isActive: true,
        role: 'subject',
        beatOffset: 0,
      };
      voices.soprano = {
        ...voices.soprano,
        material: generateFreeCounterpoint(4, 7, state.harmonicTension, 'wave'),
        isActive: true,
        role: 'free',
      };
      voices.alto = {
        ...voices.alto,
        material: KENT_COUNTERSUBJECT,
        isActive: true,
        role: 'countersubject',
      };
      // Bass provides harmonic foundation
      voices.bass = {
        ...voices.bass,
        material: [
          { semitone: 0, duration: 2, velocity: 0.5, articulation: 'tenuto' },  // C# (tonic)
          { semitone: 5, duration: 2, velocity: 0.45, articulation: 'legato' }, // F# (subdominant)
          { semitone: 7, duration: 2, velocity: 0.5, articulation: 'tenuto' },  // G# (dominant)
          { semitone: 0, duration: 2, velocity: 0.55, articulation: 'tenuto' }, // C# (return)
        ],
        isActive: true,
        role: 'free',
        beatOffset: 0,
      };
      newState.subjectEntryCount = 3;
      newState.lastSubjectVoice = 'tenor';
      break;

    case 'exposition_4':
      // Bass enters with answer, full 4-voice texture
      voices.bass = {
        ...voices.bass,
        material: createTonalAnswer(currentVariation),
        isActive: true,
        role: 'answer',
        beatOffset: 0,
      };
      voices.tenor = {
        ...voices.tenor,
        material: KENT_COUNTERSUBJECT,
        isActive: true,
        role: 'countersubject',
      };
      voices.alto = {
        ...voices.alto,
        material: generateFreeCounterpoint(4, 0, state.harmonicTension, 'ascending'),
        isActive: true,
        role: 'free',
      };
      voices.soprano = {
        ...voices.soprano,
        material: generateFreeCounterpoint(4, 7, state.harmonicTension, 'descending'),
        isActive: true,
        role: 'free',
      };
      newState.subjectEntryCount = 4;
      newState.lastSubjectVoice = 'bass';
      break;

    case 'episode':
      // Sequential passage - use chromatic or sequence variation
      // DENSITY FIX: Always include bass for harmonic foundation
      const episodeVariation = newState.currentVariationIndex === 6 || newState.currentVariationIndex === 7
        ? currentVariation
        : KENT_VARIATION_7_SEQUENCE;

      voices.soprano = {
        ...voices.soprano,
        material: episodeVariation,
        isActive: true,
        role: 'free',
      };
      voices.alto = {
        ...voices.alto,
        material: generateSequence(KENT_SUBJECT.slice(0, 4), 3, -2),
        isActive: true,
        role: 'free',
        beatOffset: 1, // Canon offset
      };
      // Bass always active for harmonic foundation
      voices.bass = {
        ...voices.bass,
        material: [
          { semitone: 0, duration: 3, velocity: 0.5, articulation: 'tenuto' },  // C# pedal
          { semitone: 7, duration: 3, velocity: 0.45, articulation: 'legato' }, // G# (dominant)
        ],
        isActive: true,
        role: 'free',
        beatOffset: 0,
      };
      // Tenor joins at higher intensity for fuller texture
      if (state.intensity > 0.3) {  // Lowered threshold from 0.5
        voices.tenor = {
          ...voices.tenor,
          material: generateFreeCounterpoint(6, 5, state.harmonicTension, 'wave'),
          isActive: true,
          role: 'free',
        };
      }
      break;

    case 'development':
      // Subject transformations - use the selected variation directly
      // DENSITY FIX: Always include bass + at least one other voice
      // (variations already include inversion, retrograde, etc.)
      const devVoice = state.lastSubjectVoice === 'soprano' ? 'tenor' :
                       state.lastSubjectVoice === 'alto' ? 'bass' :
                       state.lastSubjectVoice === 'tenor' ? 'soprano' : 'alto';

      voices[devVoice] = {
        ...voices[devVoice],
        material: currentVariation,
        isActive: true,
        role: 'subject',
      };

      // Add counterpoint
      const cpVoice = devVoice === 'soprano' ? 'alto' : 'soprano';
      voices[cpVoice] = {
        ...voices[cpVoice],
        material: KENT_COUNTERSUBJECT,
        isActive: true,
        role: 'countersubject',
      };

      // DENSITY FIX: Always add bass if not already the devVoice
      if (devVoice !== 'bass') {
        voices.bass = {
          ...voices.bass,
          material: [
            { semitone: 0, duration: 3, velocity: 0.5, articulation: 'tenuto' },  // C# pedal
            { semitone: 5, duration: 2, velocity: 0.45, articulation: 'legato' }, // F# (subdominant)
            { semitone: 7, duration: 2, velocity: 0.5, articulation: 'tenuto' },  // G# (dominant)
            { semitone: 0, duration: 3, velocity: 0.55, articulation: 'tenuto' }, // C# (return)
          ],
          isActive: true,
          role: 'free',
          beatOffset: 0,
        };
      }

      newState.lastSubjectVoice = devVoice;
      break;

    case 'stretto':
      // All voices enter with subject in quick succession
      // Use diminution variation for stretto if available
      const strettoVariation = newState.currentVariationIndex === 5
        ? currentVariation
        : KENT_VARIATION_5_DIMINUTION;

      const strettoDelay = Math.max(0.5, 2 - state.intensity * 1.5);

      voices.soprano = {
        ...voices.soprano,
        material: strettoVariation,
        isActive: true,
        role: 'subject',
        beatOffset: 0,
      };
      voices.alto = {
        ...voices.alto,
        material: createTonalAnswer(strettoVariation),
        isActive: true,
        role: 'answer',
        beatOffset: strettoDelay,
      };
      voices.tenor = {
        ...voices.tenor,
        material: strettoVariation,
        isActive: true,
        role: 'subject',
        beatOffset: strettoDelay * 2,
      };
      voices.bass = {
        ...voices.bass,
        material: createTonalAnswer(strettoVariation),
        isActive: true,
        role: 'answer',
        beatOffset: strettoDelay * 3,
      };
      break;

    case 'pedal_point':
      // Bass holds tonic pedal, upper voices use augmentation for majesty
      const pedalVariation = newState.currentVariationIndex === 4
        ? currentVariation
        : KENT_VARIATION_4_AUGMENTATION;

      voices.bass = {
        ...voices.bass,
        material: [
          { semitone: 0, duration: 8, velocity: 0.7, articulation: 'tenuto' }, // Long C#
        ],
        isActive: true,
        role: 'free',
      };
      voices.tenor = {
        ...voices.tenor,
        material: createDiminution(KENT_SUBJECT),
        isActive: true,
        role: 'subject',
      };
      voices.alto = {
        ...voices.alto,
        material: createInversion(KENT_COUNTERSUBJECT),
        isActive: true,
        role: 'countersubject',
      };
      voices.soprano = {
        ...voices.soprano,
        material: pedalVariation,
        isActive: true,
        role: 'subject',
        beatOffset: 1,
      };
      break;

    case 'recapitulation':
      // Subject returns triumphantly - use original or sequence
      const recapVariation = newState.currentVariationIndex === 0 || newState.currentVariationIndex === 7
        ? currentVariation
        : KENT_VARIATION_0_ORIGINAL;

      voices.soprano = {
        ...voices.soprano,
        material: recapVariation.map(n => ({ ...n, velocity: Math.min(1, n.velocity * 1.2) })),
        isActive: true,
        role: 'subject',
      };
      voices.alto = {
        ...voices.alto,
        material: KENT_COUNTERSUBJECT,
        isActive: true,
        role: 'countersubject',
      };
      voices.tenor = {
        ...voices.tenor,
        material: generateFreeCounterpoint(4, 0, 0.3, 'wave'),
        isActive: true,
        role: 'free',
      };
      voices.bass = {
        ...voices.bass,
        material: generateFreeCounterpoint(4, 0, 0.2, 'descending'),
        isActive: true,
        role: 'free',
      };
      break;

    case 'coda':
      // Final cadence: V - I
      voices.soprano = {
        ...voices.soprano,
        material: [
          { semitone: 11, duration: 1, velocity: 0.8, articulation: 'legato' }, // B# (leading tone)
          { semitone: 0, duration: 2, velocity: 0.9, articulation: 'tenuto' },  // C# (tonic)
        ],
        isActive: true,
        role: 'free',
      };
      voices.alto = {
        ...voices.alto,
        material: [
          { semitone: 7, duration: 1, velocity: 0.7, articulation: 'legato' },  // G#
          { semitone: 7, duration: 2, velocity: 0.75, articulation: 'tenuto' }, // G# (stays)
        ],
        isActive: true,
        role: 'free',
      };
      voices.tenor = {
        ...voices.tenor,
        material: [
          { semitone: 2, duration: 1, velocity: 0.65, articulation: 'legato' }, // D#
          { semitone: 3, duration: 2, velocity: 0.7, articulation: 'tenuto' },  // E
        ],
        isActive: true,
        role: 'free',
      };
      voices.bass = {
        ...voices.bass,
        material: [
          { semitone: 7, duration: 1, velocity: 0.8, articulation: 'accent' },  // G# (dominant)
          { semitone: 0, duration: 2, velocity: 0.9, articulation: 'tenuto' },  // C# (tonic)
        ],
        isActive: true,
        role: 'free',
      };
      break;

    case 'silence':
    default:
      // All voices silent
      break;
  }

  newState.voices = voices;
  return newState;
}

// =============================================================================
// PHASE DURATION CALCULATION
// =============================================================================

export function calculatePhaseDuration(phase: FuguePhase, intensity: number): number {
  const baseDurations: Record<FuguePhase, number> = {
    silence: 2,
    exposition_1: 4,
    exposition_2: 4,
    exposition_3: 4,
    exposition_4: 4,
    episode: 6,
    development: 6,
    stretto: 4,
    pedal_point: 8,
    recapitulation: 6,
    coda: 4,
  };

  const base = baseDurations[phase];

  // Higher intensity = shorter phases (more changes)
  const intensityModifier = 1 - intensity * 0.3;

  return base * intensityModifier;
}

// =============================================================================
// SCHEDULED NOTE FOR AUDIO
// =============================================================================

export interface ScheduledNote {
  frequency: number;
  startTime: number;
  duration: number;
  velocity: number;
  articulation: FugueNote['articulation'];
  voice: VoiceRegister;
}

// =============================================================================
// MAIN UPDATE FUNCTION
// =============================================================================

export function updateKentFugue(
  state: FugueStateData,
  deltaTime: number,
  gameIntensity: number,
  gamePhase: FugueStateData['gamePhase'],
  waveNumber: number = 1  // NEW: wave-based voice progression
): { newState: FugueStateData; scheduledNotes: ScheduledNote[]; percussionNotes: PercussionNote[] } {
  let newState = { ...state };
  const scheduledNotes: ScheduledNote[] = [];

  // Update game-driven parameters
  newState.intensity = gameIntensity;
  newState.gamePhase = gamePhase;
  newState.waveNumber = waveNumber;

  // Update dynamic arc (musical narrative shaping)
  const arcUpdate = updateDynamicArc(newState);
  newState.arcPhase = arcUpdate.arcPhase;
  newState.globalDynamic = arcUpdate.globalDynamic;
  newState.dynamicArc = arcUpdate.dynamicArc;

  // Slower base tempo: 48-96 BPM (much more contemplative)
  // Only speeds up significantly in crisis/combat
  const baseTempoForPhase = gamePhase === 'death' ? 36 :
                            gamePhase === 'crisis' ? 72 :
                            gamePhase === 'combat' ? 60 : 48;
  newState.tempo = baseTempoForPhase + gameIntensity * 48;

  const beatDuration = 60 / newState.tempo;
  const deltaBeat = deltaTime / beatDuration;

  // Advance beat
  const prevBeat = newState.currentBeat;
  newState.currentBeat += deltaBeat;
  newState.phaseProgress += deltaBeat / newState.phaseDuration;

  // Update percussion bar tracking when crossing measure boundaries
  const prevMeasure = Math.floor(prevBeat / newState.beatsPerMeasure);
  const currMeasure = Math.floor(newState.currentBeat / newState.beatsPerMeasure);
  if (currMeasure > prevMeasure) {
    newState.percussion = updatePercussionBarPosition(newState);

    // Update phrase structure for orchestration (8/16/32 bar levels)
    newState.phraseState = updatePhraseState(
      newState.phraseState as PhraseState,
      gameIntensity,
      gamePhase
    );

    // === GRAND OPENING: Choreographed voice entries ===
    if (newState.journeyPhase === 'grand_opening') {
      const openingBar = newState.phraseState.totalBars;

      // Phase 0 → 1: Second voice enters at bar 8 (answer voice)
      if (openingBar >= 8 && newState.openingPhase === 0) {
        newState.openingPhase = 1;
        // Soprano enters with tonal answer
        newState.voices.soprano = {
          ...newState.voices.soprano,
          material: createTonalAnswer([...KENT_SUBJECT]),
          isActive: true,
          role: 'answer',
          beatOffset: newState.currentBeat,
        };
        newState.subjectEntryCount = 2;
        newState.lastSubjectVoice = 'soprano';
        // Tempo increases slightly
        newState.tempo = 66;
      }

      // Phase 1 → 2: Third voice enters at bar 16
      if (openingBar >= 16 && newState.openingPhase === 1) {
        newState.openingPhase = 2;
        // Tenor enters with subject
        newState.voices.tenor = {
          ...newState.voices.tenor,
          material: [...KENT_SUBJECT],
          isActive: true,
          role: 'subject',
          beatOffset: newState.currentBeat,
        };
        newState.subjectEntryCount = 3;
        newState.lastSubjectVoice = 'tenor';
        // Light percussion begins
        newState.percussionMuted = false;
        newState.tempo = 72;
      }

      // Phase 2 → 3: Full texture at bar 24
      if (openingBar >= 24 && newState.openingPhase === 2) {
        newState.openingPhase = 3;
        // Bass enters with authority
        newState.voices.bass = {
          ...newState.voices.bass,
          material: [
            { semitone: 0, duration: 2, velocity: 0.7, articulation: 'accent' },
            { semitone: 7, duration: 1.5, velocity: 0.6, articulation: 'tenuto' },
            { semitone: 5, duration: 1.5, velocity: 0.55, articulation: 'legato' },
            { semitone: 0, duration: 3, velocity: 0.75, articulation: 'accent' },
          ],
          isActive: true,
          role: 'free',
          beatOffset: newState.currentBeat,
        };
        newState.subjectEntryCount = 4;
        newState.tempo = 78;
      }

      // Opening complete at bar 32: Capture signature and transition
      if (openingBar >= 32 && newState.journeyPhase === 'grand_opening') {
        // Capture opening signature for future reference
        newState.openingSignature = {
          announcementVariation: newState.currentVariationIndex,
          keyColoring: newState.phraseState.keyColoring,
          peakDynamic: newState.globalDynamic,
          establishedTempo: newState.tempo,
          completedAtBeat: newState.currentBeat,
        };

        // Record narrative beat
        newState.narrativeBeats.push({
          type: 'opening_complete',
          sectionNumber: 0,
          beat: newState.currentBeat,
          intensity: newState.intensity,
        });

        // Transition to exploration
        newState.journeyPhase = 'exploration';
        newState.sectionNumber = 1;
        newState.totalSectionsCompleted = 1;

        console.log('🎵 GRAND OPENING COMPLETE - KENT theme established');
      }
    }

    // === JOURNEY SECTION TRANSITIONS (after opening) ===
    if (newState.journeyPhase !== 'grand_opening') {
      const totalBars = newState.phraseState.totalBars;
      const newSection = Math.floor(totalBars / 32);

      if (newSection > newState.sectionNumber) {
        newState.sectionNumber = newSection;
        newState.totalSectionsCompleted = newSection;

        // Update journey phase based on section
        if (newSection <= 2) {
          newState.journeyPhase = 'exploration';
        } else if (newSection <= 4) {
          newState.journeyPhase = 'development';
        } else {
          newState.journeyPhase = 'recapitulation_arc';
        }

        // Select variation based on journey position
        newState.currentVariationIndex = getJourneyVariation(newSection);
      }
    }
  }

  // Check for phase transition
  if (newState.phaseProgress >= 1.0) {
    const transitions = computeTransitions(BASE_TRANSITIONS, gameIntensity, gamePhase);
    const nextPhase = sampleNextPhase(newState.phase, transitions);

    newState.phase = nextPhase;
    newState.phaseProgress = 0;
    newState.phaseDuration = calculatePhaseDuration(nextPhase, gameIntensity);

    // Assign new material to voices
    newState = assignVoiceMaterial(newState, nextPhase);
  }

  // Current time for scheduling
  const currentTime = newState.currentBeat * beatDuration;

  // Generate percussion (quiet, textural)
  // TIMING FIX: Now uses discrete 16th note tracking to prevent skipped notes
  const percResult = generatePercussion(newState, currentTime, beatDuration);
  const percussionNotes = percResult.notes;

  // Update the lastPlayedSixteenth tracker in state
  newState.percussion = {
    ...newState.percussion,
    lastPlayedSixteenth: percResult.newLastSixteenth,
  };

  // Generate scheduled notes for active voices (with stochastic processing)

  // === SPONTANEOUS BASS DRONE ===
  // Occasionally emit a long, low bass drone in C# minor regardless of phase
  if (Math.random() < STOCHASTIC_CONFIG.bassDroneProbability * deltaTime * 0.5) {
    const bassVoice = newState.voices.bass;
    if (!bassVoice.isActive || bassVoice.material.length === 0) {
      // Choose a bass drone note: tonic (0), dominant (7), or subdominant (5)
      const droneNotes = [0, 7, 5, 0]; // Weight tonic
      const droneSemitone = droneNotes[Math.floor(Math.random() * droneNotes.length)];
      const droneDuration = STOCHASTIC_CONFIG.minBassDuration + Math.random() * 4;

      scheduledNotes.push({
        frequency: semitoneToFrequency(droneSemitone, 2), // Bass octave
        startTime: currentTime,
        duration: droneDuration * beatDuration,
        velocity: 0.6 + Math.random() * 0.3, // 3x boost (was 0.2-0.3, now 0.6-0.9)
        articulation: 'tenuto',
        voice: 'bass',
      });
    }
  }

  // === GET PHRASE ORCHESTRATION CONTEXT ===
  // Theme modifiers color notes based on 8/16/32 bar structure
  const phraseState = newState.phraseState as PhraseState;
  const activeTheme = getActiveTheme(phraseState);
  const themeModifiers = getThemeModifiers(
    activeTheme,
    phraseState.phraseTension,
    gameIntensity
  );

  // === CONTRAST MODIFIERS: Create breathing room ===
  const contrastMods = getContrastModifiers(phraseState.contrastEvent);

  // Track active voices to respect maxVoices
  let activeVoiceCount = 0;
  const voiceOrder: VoiceRegister[] = ['bass', 'tenor', 'alto', 'soprano']; // Priority order

  for (const register of voiceOrder) {
    const voice = newState.voices[register];
    if (!voice.isActive || voice.material.length === 0) continue;

    // === CONTRAST: Limit simultaneous voices ===
    if (activeVoiceCount >= contrastMods.maxVoices) continue;

    // === CONTRAST: Solo voice filter ===
    if (contrastMods.soloVoice && register !== contrastMods.soloVoice) continue;

    activeVoiceCount++;

    const voiceStartTime = voice.beatOffset * beatDuration;
    if (currentTime < voiceStartTime) continue; // Voice hasn't entered yet

    // Check if we need to schedule the next note
    const localTime = currentTime - voiceStartTime;

    // === FIX: Reset material when exhausted (loop the phrase) ===
    // Use current state (may have been updated if we caught up through missed notes)
    const currentVoice = newState.voices[register];
    if (currentVoice.materialIndex >= currentVoice.material.length) {
      // Voice has played all its notes - regenerate with variation!
      // Get current variation for fresh material
      const currentVariation = KENT_VARIATIONS[newState.currentVariationIndex] || KENT_SUBJECT;

      // Assign new material based on voice role
      let newMaterial: FugueNote[];
      if (currentVoice.role === 'subject') {
        newMaterial = [...currentVariation];
      } else if (currentVoice.role === 'answer') {
        newMaterial = createTonalAnswer(currentVariation);
      } else if (currentVoice.role === 'countersubject') {
        newMaterial = [...KENT_COUNTERSUBJECT];
      } else {
        // Free voice - generate counterpoint
        newMaterial = generateFreeCounterpoint(4, 0, newState.harmonicTension, 'wave');
      }

      newState.voices[register] = {
        ...currentVoice,
        material: newMaterial,
        materialIndex: 0,
        beatOffset: newState.currentBeat, // Reset timing to now
        isActive: true, // Ensure voice stays active!
      };
      continue; // Will pick up on next update
    }

    let noteStartTime = 0;

    for (let i = 0; i < voice.material.length; i++) {
      const note = voice.material[i];

      // Skip rest notes (semitone = -1)
      if (note.semitone === -1) {
        noteStartTime += note.duration * beatDuration;
        continue;
      }

      const noteEndTime = noteStartTime + note.duration * beatDuration;

      // Get the CURRENT materialIndex (may have been updated in previous iterations)
      const currentMaterialIndex = newState.voices[register].materialIndex;

      // BUG FIX: If we've passed a note's window entirely, advance materialIndex
      // This prevents voices from getting "stuck" when update intervals are too long
      if (i === currentMaterialIndex && localTime >= noteEndTime) {
        // We missed this note - advance to next
        newState.voices[register] = {
          ...newState.voices[register],
          materialIndex: i + 1,
          previousPitch: newState.voices[register].currentPitch,
          currentPitch: note.semitone,
        };
        noteStartTime = noteEndTime;
        // Don't break - continue checking if next note is also past
        continue;
      }

      // TIMING FIX: Only schedule if this is the EXACT note we should play next (i === materialIndex)
      // and we're within its time window. This prevents duplicate scheduling across frames.
      if (localTime >= noteStartTime && localTime < noteEndTime && i === currentMaterialIndex) {

        // === ALL VOICES ALWAYS PLAY ===
        // Music should be continuous and rich. No stochastic gating.
        // Removed: shouldEmitNote gate and random rest insertion
        // This ensures the KENT fugue is always audible and present.

        // === APPLY KEY COLORING (from phrase orchestration) ===
        let finalSemitone = applyKeyColoring(note.semitone, phraseState.keyColoring);

        // === APPLY PITCH VARIATION ===
        if (Math.random() < STOCHASTIC_CONFIG.pitchVariationProbability) {
          finalSemitone = applyPitchVariation(finalSemitone, STOCHASTIC_CONFIG.pitchVariationProbability);
        }

        // === APPLY OCTAVE DISPLACEMENT ===
        let octaveOffset = 0;
        if (Math.random() < STOCHASTIC_CONFIG.octaveDisplacementProbability) {
          octaveOffset = Math.random() > 0.5 ? 1 : -1;
          // Clamp to reasonable range
          if (voice.octave + octaveOffset < 2) octaveOffset = 0;
          if (voice.octave + octaveOffset > 6) octaveOffset = 0;
        }

        // === APPLY RHYTHM VARIATION (with theme + contrast modifiers) ===
        let finalDuration = note.duration * beatDuration * themeModifiers.durationMod * contrastMods.durationMult;
        if (Math.random() < STOCHASTIC_CONFIG.rhythmVariationProbability) {
          finalDuration = applyRhythmVariation(note.duration, STOCHASTIC_CONFIG.rhythmVariationProbability) * beatDuration * themeModifiers.durationMod * contrastMods.durationMult;
        }

        // === APPLY DYNAMIC VARIATION (with theme + contrast modifiers) ===
        let finalVelocity = note.velocity * themeModifiers.velocityMod * contrastMods.velocityMult;
        if (Math.random() < STOCHASTIC_CONFIG.dynamicVariationProbability) {
          // Vary velocity by ±30%
          const velMod = 0.7 + Math.random() * 0.6;
          finalVelocity = Math.min(1, Math.max(0.2, finalVelocity * velMod));
        }

        // === BASS & LOW FREQUENCY BOOST ===
        // Lower voices need significant boost for audibility
        if (register === 'bass') {
          finalVelocity *= 12.0;  // 2x boost (was 6.0)
        } else if (register === 'tenor') {
          finalVelocity *= 6.75;  // 1.5x boost (was 4.5)
        }

        // === APPLY THEME ARTICULATION OVERRIDE ===
        const finalArticulation = themeModifiers.articulationOverride || note.articulation;

        // === CONTRAST-AWARE REST INSERTION ===
        // Rest chance is multiplied by contrast modifier for breathing room
        // Base rest is higher to reduce oversaturation
        const effectiveRestChance = themeModifiers.restChance * contrastMods.restChanceMult;
        if (Math.random() < effectiveRestChance) {
          // Skip this note (insert rest), but still advance state
          // IMPORTANT: Keep currentPitch unchanged to preserve voice leading continuity
          newState.voices[register] = {
            ...voice,
            materialIndex: i + 1,
            previousPitch: voice.currentPitch,
            currentPitch: voice.currentPitch, // Preserve pitch during rest (was: finalSemitone - BUG)
          };
          break;
        }

        // === THEME-BASED MELODIC RUN ===
        // Sequential/ornamented themes can trigger scale runs
        if (Math.random() < themeModifiers.runChance && finalDuration > 0.4) {
          // Generate a melodic run instead of single note
          const runDirection = Math.random() > 0.5 ? 'ascending' : 'descending';
          const runLength = 3 + Math.floor(Math.random() * 4); // 3-6 notes
          const runNotes = generateMelodicRun(
            finalSemitone,
            runDirection,
            runLength,
            phraseState.keyColoring,
            finalDuration / beatDuration
          );
          let runStartTime = currentTime;
          for (const runNote of runNotes) {
            scheduledNotes.push({
              frequency: semitoneToFrequency(runNote.semitone, voice.octave + octaveOffset),
              startTime: runStartTime,
              duration: runNote.duration * beatDuration,
              velocity: runNote.velocity * finalVelocity,
              articulation: runNote.articulation,
              voice: register,
            });
            runStartTime += runNote.duration * beatDuration;
          }
        }
        // === THEME-AWARE ORNAMENTATION ===
        else if (Math.random() < themeModifiers.ornamentChance && finalDuration > 0.3) {
          // Replace single note with theme-appropriate ornament
          const ornament = generateExtendedOrnament(
            finalSemitone,
            finalDuration / beatDuration,
            activeTheme,
            phraseState.keyColoring
          );
          let ornamentStartTime = currentTime;
          for (const ornNote of ornament) {
            scheduledNotes.push({
              frequency: semitoneToFrequency(ornNote.semitone, voice.octave + octaveOffset),
              startTime: ornamentStartTime,
              duration: ornNote.duration * beatDuration,
              velocity: ornNote.velocity * finalVelocity,
              articulation: ornNote.articulation,
              voice: register,
            });
            ornamentStartTime += ornNote.duration * beatDuration;
          }
        } else {
          // Normal note with variations applied
          scheduledNotes.push({
            frequency: semitoneToFrequency(finalSemitone, voice.octave + octaveOffset),
            startTime: currentTime,
            duration: finalDuration,
            velocity: finalVelocity,
            articulation: finalArticulation,
            voice: register,
          });
        }

        // Update voice state
        newState.voices[register] = {
          ...voice,
          materialIndex: i + 1,
          previousPitch: voice.currentPitch,
          currentPitch: finalSemitone,
        };
        break;
      }

      noteStartTime = noteEndTime;
    }
  }

  // Apply globalDynamic AND phrase tension for coherent multi-level musical arc
  // Phrase tension (0-1) adds subtle dynamic shaping based on 8/16/32 bar position
  const phraseDynamicMod = 0.85 + phraseState.phraseTension * 0.3; // Range: 0.85-1.15
  for (const note of scheduledNotes) {
    note.velocity *= newState.globalDynamic * phraseDynamicMod;
    // Clamp velocity to valid range
    note.velocity = Math.min(1, Math.max(0.1, note.velocity));
  }

  return { newState, scheduledNotes, percussionNotes };
}

// =============================================================================
// PRE-GENERATED KENT THEME VARIATIONS
// =============================================================================

/**
 * 8 Pre-generated variations on the K-E-N-T theme.
 * Each variation is 6-18 seconds long (5-15 beats at ~48 BPM).
 *
 * These provide musical variety without runtime generation overhead,
 * and ensure coherent thematic development throughout the game.
 *
 * VARIATION INDEX:
 * 0 - Original: The statement (clear, confident)
 * 1 - Tonal Answer: Dominant transposition (responsive)
 * 2 - Inversion: Intervals flipped (introspective)
 * 3 - Retrograde: Time reversed (mysterious)
 * 4 - Augmentation: Stretched (majestic, contemplative)
 * 5 - Diminution: Compressed (energetic, urgent)
 * 6 - Chromatic Embellishment: Added passing tones (expressive)
 * 7 - Sequence: Theme in sequence (building tension)
 */

/**
 * VARIATION 0: Original Statement
 * The KENT theme as a clear, confident statement.
 * Duration: ~8 beats (10 seconds at 48 BPM)
 */
export const KENT_VARIATION_0_ORIGINAL: FugueNote[] = [
  // K - Announce with authority
  { semitone: 11, duration: 1.0, velocity: 0.85, articulation: 'accent' },

  // E - Tritone descent
  { semitone: 5, duration: 0.75, velocity: 0.8, articulation: 'legato' },

  // N - Continue the descent
  { semitone: 2, duration: 0.75, velocity: 0.75, articulation: 'legato' },

  // T - Second tritone
  { semitone: 8, duration: 1.0, velocity: 0.85, articulation: 'tenuto' },

  // Resolution phrase
  { semitone: 7, duration: 0.5, velocity: 0.7, articulation: 'legato' },
  { semitone: 5, duration: 0.5, velocity: 0.65, articulation: 'legato' },
  { semitone: 3, duration: 0.5, velocity: 0.6, articulation: 'legato' },
  { semitone: 2, duration: 0.5, velocity: 0.65, articulation: 'legato' },
  { semitone: 0, duration: 1.5, velocity: 0.9, articulation: 'tenuto' },

  // Brief rest
  { semitone: -1, duration: 1.0, velocity: 0, articulation: 'legato' },
];

/**
 * VARIATION 1: Tonal Answer
 * KENT theme transposed to the dominant (G# minor region).
 * Creates call-and-response with the original.
 * Duration: ~9 beats (11 seconds at 48 BPM)
 */
export const KENT_VARIATION_1_TONAL_ANSWER: FugueNote[] = [
  // Dominant-based K (F#)
  { semitone: 6, duration: 1.0, velocity: 0.8, articulation: 'accent' },

  // E in dominant (C#)
  { semitone: 0, duration: 0.75, velocity: 0.75, articulation: 'legato' },

  // N in dominant (A#/Bb)
  { semitone: 10, duration: 0.75, velocity: 0.7, articulation: 'legato' },

  // T in dominant (E)
  { semitone: 3, duration: 1.0, velocity: 0.8, articulation: 'tenuto' },

  // Different resolution - to dominant
  { semitone: 2, duration: 0.5, velocity: 0.65, articulation: 'legato' },
  { semitone: 0, duration: 0.5, velocity: 0.6, articulation: 'legato' },
  { semitone: 11, duration: 0.5, velocity: 0.65, articulation: 'legato' },
  { semitone: 7, duration: 1.5, velocity: 0.85, articulation: 'tenuto' },

  // Connecting passage back
  { semitone: 5, duration: 0.5, velocity: 0.55, articulation: 'legato' },
  { semitone: 3, duration: 0.5, velocity: 0.5, articulation: 'legato' },
  { semitone: 2, duration: 0.5, velocity: 0.55, articulation: 'legato' },
  { semitone: 0, duration: 1.0, velocity: 0.7, articulation: 'tenuto' },
];

/**
 * VARIATION 2: Inversion
 * KENT intervals flipped - rising where original falls.
 * Creates an introspective, questioning mood.
 * Duration: ~10 beats (12.5 seconds at 48 BPM)
 */
export const KENT_VARIATION_2_INVERSION: FugueNote[] = [
  // Start on tonic (axis of inversion)
  { semitone: 0, duration: 0.5, velocity: 0.65, articulation: 'legato' },

  // K inverted - B# becomes D# (mirror around C#)
  { semitone: 1, duration: 1.0, velocity: 0.8, articulation: 'accent' },

  // E inverted - F# becomes G# (tritone UP instead of down)
  { semitone: 7, duration: 0.75, velocity: 0.75, articulation: 'legato' },

  // N inverted - D# becomes A
  { semitone: 10, duration: 0.75, velocity: 0.7, articulation: 'legato' },

  // T inverted - A becomes E
  { semitone: 4, duration: 1.0, velocity: 0.8, articulation: 'tenuto' },

  // Inverted resolution (ascending)
  { semitone: 5, duration: 0.5, velocity: 0.65, articulation: 'legato' },
  { semitone: 7, duration: 0.5, velocity: 0.7, articulation: 'legato' },
  { semitone: 8, duration: 0.5, velocity: 0.7, articulation: 'legato' },
  { semitone: 11, duration: 0.5, velocity: 0.75, articulation: 'legato' },
  { semitone: 0, duration: 1.5, velocity: 0.85, articulation: 'tenuto' },

  // Descending tail
  { semitone: 11, duration: 0.5, velocity: 0.6, articulation: 'legato' },
  { semitone: 8, duration: 0.5, velocity: 0.55, articulation: 'legato' },
  { semitone: 7, duration: 1.0, velocity: 0.65, articulation: 'tenuto' },
];

/**
 * VARIATION 3: Retrograde
 * KENT played backwards - mysterious, unwinding quality.
 * Duration: ~9 beats (11 seconds at 48 BPM)
 */
export const KENT_VARIATION_3_RETROGRADE: FugueNote[] = [
  // Start from the end: tonic
  { semitone: 0, duration: 1.0, velocity: 0.7, articulation: 'tenuto' },

  // Ascending resolution (reversed)
  { semitone: 2, duration: 0.5, velocity: 0.65, articulation: 'legato' },
  { semitone: 3, duration: 0.5, velocity: 0.6, articulation: 'legato' },
  { semitone: 5, duration: 0.5, velocity: 0.65, articulation: 'legato' },
  { semitone: 7, duration: 0.5, velocity: 0.7, articulation: 'legato' },

  // T-N-E-K reversed
  { semitone: 8, duration: 1.0, velocity: 0.8, articulation: 'tenuto' },
  { semitone: 2, duration: 0.75, velocity: 0.75, articulation: 'legato' },
  { semitone: 5, duration: 0.75, velocity: 0.8, articulation: 'legato' },
  { semitone: 11, duration: 1.0, velocity: 0.85, articulation: 'accent' },

  // Mystery tail
  { semitone: 0, duration: 0.5, velocity: 0.5, articulation: 'legato' },
  { semitone: 7, duration: 0.5, velocity: 0.55, articulation: 'legato' },
  { semitone: 0, duration: 1.0, velocity: 0.6, articulation: 'tenuto' },
];

/**
 * VARIATION 4: Augmentation
 * KENT theme stretched - majestic, contemplative.
 * Duration: ~15 beats (18+ seconds at 48 BPM)
 */
export const KENT_VARIATION_4_AUGMENTATION: FugueNote[] = [
  // K - Long, sustained announcement
  { semitone: 11, duration: 2.0, velocity: 0.75, articulation: 'tenuto' },

  // E - Slow tritone descent
  { semitone: 5, duration: 1.5, velocity: 0.7, articulation: 'legato' },

  // N - Contemplative continuation
  { semitone: 2, duration: 1.5, velocity: 0.65, articulation: 'legato' },

  // T - Long held climax
  { semitone: 8, duration: 2.0, velocity: 0.75, articulation: 'tenuto' },

  // Slow resolution
  { semitone: 7, duration: 1.0, velocity: 0.6, articulation: 'legato' },
  { semitone: 5, duration: 1.0, velocity: 0.55, articulation: 'legato' },
  { semitone: 3, duration: 1.0, velocity: 0.5, articulation: 'legato' },
  { semitone: 2, duration: 1.0, velocity: 0.55, articulation: 'legato' },
  { semitone: 0, duration: 3.0, velocity: 0.8, articulation: 'tenuto' },
];

/**
 * VARIATION 5: Diminution
 * KENT theme compressed - energetic, urgent.
 * Duration: ~5 beats (6 seconds at 48 BPM)
 */
export const KENT_VARIATION_5_DIMINUTION: FugueNote[] = [
  // K - Quick, punchy
  { semitone: 11, duration: 0.375, velocity: 0.9, articulation: 'staccato' },

  // E - Rapid descent
  { semitone: 5, duration: 0.25, velocity: 0.85, articulation: 'staccato' },

  // N - Continue momentum
  { semitone: 2, duration: 0.25, velocity: 0.8, articulation: 'staccato' },

  // T - Sharp accent
  { semitone: 8, duration: 0.375, velocity: 0.9, articulation: 'accent' },

  // Quick resolution run
  { semitone: 7, duration: 0.125, velocity: 0.7, articulation: 'staccato' },
  { semitone: 5, duration: 0.125, velocity: 0.65, articulation: 'staccato' },
  { semitone: 3, duration: 0.125, velocity: 0.6, articulation: 'staccato' },
  { semitone: 2, duration: 0.125, velocity: 0.65, articulation: 'staccato' },
  { semitone: 0, duration: 0.5, velocity: 0.85, articulation: 'accent' },

  // Second pass (varied)
  { semitone: 11, duration: 0.25, velocity: 0.85, articulation: 'staccato' },
  { semitone: 8, duration: 0.25, velocity: 0.8, articulation: 'staccato' },
  { semitone: 5, duration: 0.25, velocity: 0.75, articulation: 'staccato' },
  { semitone: 2, duration: 0.25, velocity: 0.7, articulation: 'staccato' },
  { semitone: 0, duration: 0.75, velocity: 0.9, articulation: 'tenuto' },

  // Brief rest
  { semitone: -1, duration: 0.5, velocity: 0, articulation: 'legato' },
];

/**
 * VARIATION 6: Chromatic Embellishment
 * KENT theme with passing tones and neighbor notes.
 * More expressive, romantic character.
 * Duration: ~12 beats (15 seconds at 48 BPM)
 */
export const KENT_VARIATION_6_CHROMATIC: FugueNote[] = [
  // Pickup to K
  { semitone: 10, duration: 0.25, velocity: 0.5, articulation: 'legato' },
  { semitone: 11, duration: 1.0, velocity: 0.85, articulation: 'accent' },

  // K to E with chromatic passing tone (A)
  { semitone: 8, duration: 0.25, velocity: 0.6, articulation: 'legato' },
  { semitone: 7, duration: 0.25, velocity: 0.55, articulation: 'legato' },
  { semitone: 6, duration: 0.25, velocity: 0.5, articulation: 'legato' },
  { semitone: 5, duration: 0.75, velocity: 0.8, articulation: 'legato' },

  // E with lower neighbor
  { semitone: 4, duration: 0.25, velocity: 0.5, articulation: 'legato' },
  { semitone: 5, duration: 0.25, velocity: 0.55, articulation: 'legato' },

  // E to N with passing tone
  { semitone: 3, duration: 0.25, velocity: 0.55, articulation: 'legato' },
  { semitone: 2, duration: 0.75, velocity: 0.75, articulation: 'legato' },

  // N with upper neighbor
  { semitone: 3, duration: 0.25, velocity: 0.5, articulation: 'legato' },
  { semitone: 2, duration: 0.25, velocity: 0.55, articulation: 'legato' },

  // N to T (tritone) with chromatic approach
  { semitone: 5, duration: 0.25, velocity: 0.6, articulation: 'legato' },
  { semitone: 7, duration: 0.25, velocity: 0.65, articulation: 'legato' },
  { semitone: 8, duration: 1.0, velocity: 0.85, articulation: 'tenuto' },

  // Chromatic resolution
  { semitone: 7, duration: 0.25, velocity: 0.6, articulation: 'legato' },
  { semitone: 6, duration: 0.25, velocity: 0.55, articulation: 'legato' },
  { semitone: 5, duration: 0.25, velocity: 0.55, articulation: 'legato' },
  { semitone: 4, duration: 0.25, velocity: 0.5, articulation: 'legato' },
  { semitone: 3, duration: 0.25, velocity: 0.5, articulation: 'legato' },
  { semitone: 2, duration: 0.25, velocity: 0.55, articulation: 'legato' },
  { semitone: 1, duration: 0.25, velocity: 0.5, articulation: 'legato' },
  { semitone: 0, duration: 1.5, velocity: 0.9, articulation: 'tenuto' },

  // Final chromatic flourish
  { semitone: 11, duration: 0.25, velocity: 0.45, articulation: 'legato' },
  { semitone: 0, duration: 1.0, velocity: 0.7, articulation: 'tenuto' },
];

/**
 * VARIATION 7: Sequential Development
 * KENT theme stated, then sequenced through different pitch levels.
 * Builds tension through repetition and transposition.
 * Duration: ~14 beats (17.5 seconds at 48 BPM)
 */
export const KENT_VARIATION_7_SEQUENCE: FugueNote[] = [
  // First statement (original)
  { semitone: 11, duration: 0.5, velocity: 0.75, articulation: 'accent' },
  { semitone: 5, duration: 0.375, velocity: 0.7, articulation: 'legato' },
  { semitone: 2, duration: 0.375, velocity: 0.65, articulation: 'legato' },
  { semitone: 8, duration: 0.5, velocity: 0.75, articulation: 'tenuto' },

  // Brief connector
  { semitone: 7, duration: 0.25, velocity: 0.5, articulation: 'legato' },

  // Second statement (down a step - A instead of B#)
  { semitone: 8, duration: 0.5, velocity: 0.7, articulation: 'accent' },
  { semitone: 2, duration: 0.375, velocity: 0.65, articulation: 'legato' },
  { semitone: 11, duration: 0.375, velocity: 0.6, articulation: 'legato' },
  { semitone: 5, duration: 0.5, velocity: 0.7, articulation: 'tenuto' },

  // Connector
  { semitone: 3, duration: 0.25, velocity: 0.5, articulation: 'legato' },

  // Third statement (down another step - G#)
  { semitone: 7, duration: 0.5, velocity: 0.65, articulation: 'accent' },
  { semitone: 1, duration: 0.375, velocity: 0.6, articulation: 'legato' },
  { semitone: 10, duration: 0.375, velocity: 0.55, articulation: 'legato' },
  { semitone: 4, duration: 0.5, velocity: 0.65, articulation: 'tenuto' },

  // Building intensity
  { semitone: 2, duration: 0.25, velocity: 0.55, articulation: 'legato' },

  // Fourth statement (climax - back to original, louder)
  { semitone: 11, duration: 0.75, velocity: 0.9, articulation: 'marcato' },
  { semitone: 5, duration: 0.5, velocity: 0.85, articulation: 'legato' },
  { semitone: 2, duration: 0.5, velocity: 0.8, articulation: 'legato' },
  { semitone: 8, duration: 0.75, velocity: 0.9, articulation: 'marcato' },

  // Full resolution
  { semitone: 7, duration: 0.375, velocity: 0.7, articulation: 'legato' },
  { semitone: 5, duration: 0.375, velocity: 0.65, articulation: 'legato' },
  { semitone: 3, duration: 0.375, velocity: 0.6, articulation: 'legato' },
  { semitone: 2, duration: 0.375, velocity: 0.65, articulation: 'legato' },
  { semitone: 0, duration: 2.0, velocity: 0.9, articulation: 'tenuto' },
];

/**
 * Collection of all KENT variations for easy access.
 * Index 0-7 corresponds to variation type.
 */
export const KENT_VARIATIONS: FugueNote[][] = [
  KENT_VARIATION_0_ORIGINAL,
  KENT_VARIATION_1_TONAL_ANSWER,
  KENT_VARIATION_2_INVERSION,
  KENT_VARIATION_3_RETROGRADE,
  KENT_VARIATION_4_AUGMENTATION,
  KENT_VARIATION_5_DIMINUTION,
  KENT_VARIATION_6_CHROMATIC,
  KENT_VARIATION_7_SEQUENCE,
];

/**
 * Variation metadata for intelligent selection.
 */
export interface VariationMetadata {
  name: string;
  character: 'confident' | 'responsive' | 'introspective' | 'mysterious' | 'majestic' | 'urgent' | 'expressive' | 'building';
  durationBeats: number;
  intensityRange: [number, number]; // Suitable intensity range (0-1)
  bestForPhases: FuguePhase[];
}

export const KENT_VARIATION_METADATA: VariationMetadata[] = [
  {
    name: 'Original Statement',
    character: 'confident',
    durationBeats: 8,
    intensityRange: [0.2, 0.7],
    bestForPhases: ['exposition_1', 'recapitulation'],
  },
  {
    name: 'Tonal Answer',
    character: 'responsive',
    durationBeats: 9,
    intensityRange: [0.3, 0.8],
    bestForPhases: ['exposition_2', 'exposition_4', 'development'],
  },
  {
    name: 'Inversion',
    character: 'introspective',
    durationBeats: 10,
    intensityRange: [0.2, 0.6],
    bestForPhases: ['development', 'episode'],
  },
  {
    name: 'Retrograde',
    character: 'mysterious',
    durationBeats: 9,
    intensityRange: [0.3, 0.7],
    bestForPhases: ['development', 'pedal_point'],
  },
  {
    name: 'Augmentation',
    character: 'majestic',
    durationBeats: 15,
    intensityRange: [0.1, 0.5],
    bestForPhases: ['exposition_1', 'pedal_point', 'coda'],
  },
  {
    name: 'Diminution',
    character: 'urgent',
    durationBeats: 5,
    intensityRange: [0.6, 1.0],
    bestForPhases: ['stretto', 'development'],
  },
  {
    name: 'Chromatic Embellishment',
    character: 'expressive',
    durationBeats: 12,
    intensityRange: [0.3, 0.7],
    bestForPhases: ['episode', 'development', 'recapitulation'],
  },
  {
    name: 'Sequential Development',
    character: 'building',
    durationBeats: 14,
    intensityRange: [0.4, 0.9],
    bestForPhases: ['episode', 'stretto', 'recapitulation'],
  },
];

/**
 * Select the best variation for the current game state.
 * Returns the variation index (0-7).
 */
export function selectVariation(
  intensity: number,
  phase: FuguePhase,
  lastVariationIndex: number | null
): number {
  // Find suitable variations based on intensity and phase
  const candidates: { index: number; score: number }[] = [];

  for (let i = 0; i < KENT_VARIATION_METADATA.length; i++) {
    const meta = KENT_VARIATION_METADATA[i];
    let score = 0;

    // Check intensity range
    if (intensity >= meta.intensityRange[0] && intensity <= meta.intensityRange[1]) {
      score += 10;
    } else {
      // Still consider but with penalty
      const distanceFromRange = Math.min(
        Math.abs(intensity - meta.intensityRange[0]),
        Math.abs(intensity - meta.intensityRange[1])
      );
      score -= distanceFromRange * 5;
    }

    // Check phase compatibility
    if (meta.bestForPhases.includes(phase)) {
      score += 15;
    }

    // Avoid repeating the last variation
    if (i === lastVariationIndex) {
      score -= 20;
    }

    // Small random factor for variety
    score += Math.random() * 5;

    candidates.push({ index: i, score });
  }

  // Sort by score and pick the best
  candidates.sort((a, b) => b.score - a.score);
  return candidates[0].index;
}

/**
 * Get the duration of a variation in beats.
 */
export function getVariationDuration(variationIndex: number): number {
  const variation = KENT_VARIATIONS[variationIndex];
  return variation.reduce((sum, note) => sum + note.duration, 0);
}

// =============================================================================
// ALIASES FOR CONVENIENCE
// =============================================================================

// Re-export with shorter names for convenience
export { KENT_SUBJECT as SUBJECT, KENT_COUNTERSUBJECT as COUNTERSUBJECT };
