/**
 * PROCEDURAL FUGUE GENERATION SYSTEM - C# Minor
 *
 * A Baroque-inspired counterpoint engine for WASM Survivors game audio.
 * Generates 4-voice fugues with real-time subject generation based on game state.
 *
 * "The counterpoint is the architecture. The fugue is the cathedral."
 *
 * MUSICAL THEORY FOUNDATIONS:
 * - C# minor key (parallel to C major procedural-audio.ts)
 * - 4 voices: Soprano, Alto, Tenor, Bass (Bach SATB model)
 * - Subject/Answer/Countersubject structure
 * - Species counterpoint rules for interval validation
 * - Stretto and episode generation for climactic moments
 *
 * GAME STATE MAPPING:
 * - POWER phase: Bold, confident subjects (stepwise + octave leaps)
 * - FLOW phase: Flowing, sequential subjects (scalar runs)
 * - CRISIS phase: Fragmented, urgent subjects (short notes, chromatic)
 * - THE BALL: Augmented subjects (stretched, ominous, tritones)
 *
 * MARIMBA SYNTHESIS:
 * - Attack: Sharp initial transient (noise + sine burst)
 * - Body: Fundamental + harmonics 2, 3, 4 (decreasing amplitude)
 * - Decay: Exponential falloff (300-500ms)
 * - Smoothing: Slight portamento between notes (20-50ms glide)
 * - Resonance: Sympathetic vibration of nearby notes
 *
 * @see procedural-audio.ts for the C major procedural system
 */

// =============================================================================
// C# MINOR SCALE DEFINITION
// =============================================================================

/**
 * C# Natural Minor scale frequencies
 * C#4 = 277.18 Hz (middle octave)
 *
 * Scale degrees: C# D# E F# G# A B C#
 * Intervals:     1  2  b3 4  5  b6 b7 8
 *
 * Harmonic minor (raised 7th) used for dominant functions:
 * C# D# E F# G# A B# C#
 */
export const C_SHARP_MINOR_SCALE = {
  // Bass range (C#2 - C#4)
  Cs2: 69.30,
  Ds2: 77.78,
  E2: 82.41,
  Fs2: 92.50,
  Gs2: 103.83,
  A2: 110.00,
  B2: 123.47,
  Cs3: 138.59,
  Ds3: 155.56,
  E3: 164.81,
  Fs3: 185.00,
  Gs3: 207.65,
  A3: 220.00,
  B3: 246.94,

  // Tenor/Alto range (C#4 - C#5)
  Cs4: 277.18,
  Ds4: 311.13,
  E4: 329.63,
  Fs4: 369.99,
  Gs4: 415.30,
  A4: 440.00,
  B4: 493.88,

  // Soprano range (C#5 - C#6)
  Cs5: 554.37,
  Ds5: 622.25,
  E5: 659.26,
  Fs5: 739.99,
  Gs5: 830.61,
  A5: 880.00,
  B5: 987.77,
  Cs6: 1108.73,

  // Harmonic minor raised 7th (B#)
  Bs4: 523.25, // Enharmonic to C5, but functionally B#
  Bs5: 1046.50,
} as const;

/**
 * Scale degrees as array for procedural selection
 * Octave-normalized (divide by 2^n to get desired octave)
 */
export const MINOR_SCALE_DEGREES = [
  C_SHARP_MINOR_SCALE.Cs4, // 1 - tonic
  C_SHARP_MINOR_SCALE.Ds4, // 2 - supertonic
  C_SHARP_MINOR_SCALE.E4,  // b3 - mediant (minor)
  C_SHARP_MINOR_SCALE.Fs4, // 4 - subdominant
  C_SHARP_MINOR_SCALE.Gs4, // 5 - dominant
  C_SHARP_MINOR_SCALE.A4,  // b6 - submediant
  C_SHARP_MINOR_SCALE.B4,  // b7 - subtonic
];

// =============================================================================
// COUNTERPOINT INTERVAL DEFINITIONS
// =============================================================================

/**
 * Perfect consonances - stable, restful
 * Used for strong beats, cadences, beginnings/endings
 */
export const PERFECT_CONSONANCES = {
  unison: 1,
  perfectFifth: 3 / 2,   // 1.5
  octave: 2,
} as const;

/**
 * Imperfect consonances - pleasant, flowing
 * Used for weak beats, middle of phrases
 */
export const IMPERFECT_CONSONANCES = {
  minorThird: 6 / 5,     // 1.2 - characteristic of minor key
  majorThird: 5 / 4,     // 1.25 - for dominant chords
  minorSixth: 8 / 5,     // 1.6
  majorSixth: 5 / 3,     // 1.667
} as const;

/**
 * Dissonances - tension, must resolve
 * Used for passing tones, suspensions, emphasis
 */
export const DISSONANCES = {
  minorSecond: 16 / 15,  // 1.067 - sharp tension
  majorSecond: 9 / 8,    // 1.125 - mild tension
  tritone: 45 / 32,      // 1.406 - devil's interval (THE BALL)
  minorSeventh: 16 / 9,  // 1.778 - unresolved
  majorSeventh: 15 / 8,  // 1.875 - leading tone tension
} as const;

/**
 * All consonant intervals for counterpoint validation
 */
export const ALL_CONSONANCES = {
  ...PERFECT_CONSONANCES,
  ...IMPERFECT_CONSONANCES,
} as const;

// =============================================================================
// VOICE RANGE DEFINITIONS
// =============================================================================

/**
 * Voice type enumeration
 */
export type VoiceType = 'soprano' | 'alto' | 'tenor' | 'bass';

/**
 * Voice range configuration
 * Each voice has a defined frequency range for proper spacing
 */
export interface VoiceRange {
  low: number;
  high: number;
  preferred: number; // Middle of comfortable range
}

export const VOICE_RANGES: Record<VoiceType, VoiceRange> = {
  soprano: {
    low: C_SHARP_MINOR_SCALE.Cs5,
    high: C_SHARP_MINOR_SCALE.Cs6,
    preferred: C_SHARP_MINOR_SCALE.Gs5,
  },
  alto: {
    low: C_SHARP_MINOR_SCALE.Gs4,
    high: C_SHARP_MINOR_SCALE.Gs5,
    preferred: C_SHARP_MINOR_SCALE.Ds5,
  },
  tenor: {
    low: C_SHARP_MINOR_SCALE.Cs4,
    high: C_SHARP_MINOR_SCALE.Cs5,
    preferred: C_SHARP_MINOR_SCALE.Gs4,
  },
  bass: {
    low: C_SHARP_MINOR_SCALE.Cs2,
    high: C_SHARP_MINOR_SCALE.Cs4,
    preferred: C_SHARP_MINOR_SCALE.Gs3,
  },
};

// =============================================================================
// FUGUE STRUCTURE TYPES
// =============================================================================

/**
 * A single note in a fugue voice
 */
export interface FugueNote {
  pitch: number;        // Frequency in Hz
  scaleDegree: number;  // 0-7 within octave
  startTime: number;    // Seconds from bar start
  duration: number;     // Seconds
  velocity: number;     // 0-1 amplitude
  articulation: 'legato' | 'staccato' | 'marcato' | 'tenuto';
}

/**
 * A melodic phrase (subject, answer, or countersubject)
 */
export interface FuguePhrase {
  notes: FugueNote[];
  durationBars: number;
  totalDuration: number; // Seconds
}

/**
 * Game phase for subject generation
 */
export type GamePhaseType = 'power' | 'flow' | 'crisis' | 'ball';

/**
 * Subject generation configuration based on game phase
 */
export interface SubjectConfig {
  phase: GamePhaseType;
  noteDensity: 'sparse' | 'medium' | 'dense';
  intervalPattern: 'stepwise' | 'leaping' | 'mixed' | 'fragmented';
  rhythmicCharacter: 'steady' | 'syncopated' | 'urgent' | 'augmented';
  tempo: number; // BPM
  barsLength: 2 | 3 | 4;
}

/**
 * Configuration for each game phase
 */
export const PHASE_CONFIGS: Record<GamePhaseType, SubjectConfig> = {
  power: {
    phase: 'power',
    noteDensity: 'medium',
    intervalPattern: 'mixed',
    rhythmicCharacter: 'steady',
    tempo: 90,
    barsLength: 4,
  },
  flow: {
    phase: 'flow',
    noteDensity: 'dense',
    intervalPattern: 'stepwise',
    rhythmicCharacter: 'syncopated',
    tempo: 100,
    barsLength: 4,
  },
  crisis: {
    phase: 'crisis',
    noteDensity: 'dense',
    intervalPattern: 'fragmented',
    rhythmicCharacter: 'urgent',
    tempo: 120,
    barsLength: 2,
  },
  ball: {
    phase: 'ball',
    noteDensity: 'sparse',
    intervalPattern: 'leaping',
    rhythmicCharacter: 'augmented',
    tempo: 60,
    barsLength: 4,
  },
};

/**
 * Voice state for real-time management
 */
export interface FugueVoice {
  type: VoiceType;
  active: boolean;
  currentNote: FugueNote | null;
  noteQueue: FugueNote[];
  lastPitch: number;
  entryTime: number;     // When this voice entered
  currentPhrase: 'subject' | 'answer' | 'countersubject' | 'free' | 'rest';
}

/**
 * Complete fugue state
 */
export interface FugueState {
  voices: Record<VoiceType, FugueVoice>;
  subject: FuguePhrase | null;
  answer: FuguePhrase | null;
  countersubject: FuguePhrase | null;
  currentBar: number;
  tempo: number;
  gamePhase: GamePhaseType;
  inStretto: boolean;
  density: number;       // 0-1, scales with enemy count
  lastUpdateTime: number;
}

// =============================================================================
// MARIMBA SYNTHESIS CONFIGURATION
// =============================================================================

/**
 * Marimba timbre parameters
 */
export interface MarimbaConfig {
  attackNoiseLevel: number;    // 0-1 noise burst amplitude
  attackNoiseDuration: number; // ms
  attackSineBurst: number;     // 0-1 initial sine burst
  harmonics: number[];         // Relative amplitudes [fund, h2, h3, h4]
  decayTime: number;           // ms for 60dB decay
  portamentoTime: number;      // ms for pitch glide
  resonanceDecay: number;      // ms for sympathetic resonance
  resonanceLevel: number;      // 0-1 amplitude of sympathetic notes
}

export const MARIMBA_DEFAULT: MarimbaConfig = {
  attackNoiseLevel: 0.15,
  attackNoiseDuration: 8,
  attackSineBurst: 0.3,
  harmonics: [1.0, 0.4, 0.2, 0.1],
  decayTime: 400,
  portamentoTime: 30,
  resonanceDecay: 600,
  resonanceLevel: 0.08,
};

/**
 * Phase-specific marimba variations
 */
export const MARIMBA_PHASE_OVERRIDES: Partial<Record<GamePhaseType, Partial<MarimbaConfig>>> = {
  power: {
    attackSineBurst: 0.4,
    harmonics: [1.0, 0.5, 0.25, 0.12],
    decayTime: 500,
  },
  crisis: {
    attackNoiseLevel: 0.25,
    decayTime: 250,
    portamentoTime: 15,
  },
  ball: {
    attackNoiseLevel: 0.08,
    decayTime: 800,
    resonanceLevel: 0.15,
    resonanceDecay: 1000,
  },
};

// =============================================================================
// COUNTERPOINT VALIDATION FUNCTIONS
// =============================================================================

/**
 * Calculate interval ratio between two frequencies
 */
export function getIntervalRatio(lower: number, upper: number): number {
  if (lower <= 0 || upper <= 0) return 1;
  // Normalize to within one octave
  let ratio = upper / lower;
  while (ratio >= 2) ratio /= 2;
  while (ratio < 1) ratio *= 2;
  return ratio;
}

/**
 * Check if an interval is consonant
 */
export function isConsonant(ratio: number): boolean {
  const tolerance = 0.02; // 2% tolerance for tuning
  const consonantRatios = Object.values(ALL_CONSONANCES);

  for (const consonant of consonantRatios) {
    if (Math.abs(ratio - consonant) < tolerance) {
      return true;
    }
  }
  return false;
}

/**
 * Check if an interval is a perfect consonance
 */
export function isPerfectConsonance(ratio: number): boolean {
  const tolerance = 0.02;
  const perfectRatios = Object.values(PERFECT_CONSONANCES);

  for (const perfect of perfectRatios) {
    if (Math.abs(ratio - perfect) < tolerance) {
      return true;
    }
  }
  return false;
}

/**
 * Detect parallel fifths or octaves (FORBIDDEN in counterpoint)
 *
 * Parallel motion: both voices move in the same direction by the same interval
 * Parallel 5ths/8ves create a hollow, archaic sound that breaks voice independence
 */
export function hasParallelPerfect(
  voice1Prev: number,
  voice1Curr: number,
  voice2Prev: number,
  voice2Curr: number,
): boolean {
  // Get previous and current intervals
  const prevRatio = getIntervalRatio(
    Math.min(voice1Prev, voice2Prev),
    Math.max(voice1Prev, voice2Prev),
  );
  const currRatio = getIntervalRatio(
    Math.min(voice1Curr, voice2Curr),
    Math.max(voice1Curr, voice2Curr),
  );

  // Check if both are perfect consonances
  if (!isPerfectConsonance(prevRatio) || !isPerfectConsonance(currRatio)) {
    return false;
  }

  // Check if same interval type (parallel)
  const tolerance = 0.02;
  if (Math.abs(prevRatio - currRatio) > tolerance) {
    return false;
  }

  // Check if parallel motion (both voices same direction)
  const voice1Direction = Math.sign(voice1Curr - voice1Prev);
  const voice2Direction = Math.sign(voice2Curr - voice2Prev);

  return voice1Direction === voice2Direction && voice1Direction !== 0;
}

/**
 * Check for voice crossing (lower voice goes above higher voice)
 */
export function hasVoiceCrossing(
  upperVoicePitch: number,
  lowerVoicePitch: number,
): boolean {
  return lowerVoicePitch > upperVoicePitch;
}

/**
 * Determine motion type between two voice pairs
 */
export type MotionType = 'parallel' | 'similar' | 'contrary' | 'oblique';

export function getMotionType(
  voice1Prev: number,
  voice1Curr: number,
  voice2Prev: number,
  voice2Curr: number,
): MotionType {
  const direction1 = Math.sign(voice1Curr - voice1Prev);
  const direction2 = Math.sign(voice2Curr - voice2Prev);

  if (direction1 === 0 && direction2 === 0) {
    return 'oblique'; // Both stationary
  }
  if (direction1 === 0 || direction2 === 0) {
    return 'oblique'; // One stationary
  }
  if (direction1 === direction2) {
    // Same direction
    const interval1 = Math.abs(voice1Curr - voice1Prev);
    const interval2 = Math.abs(voice2Curr - voice2Prev);
    if (Math.abs(interval1 - interval2) < 10) { // Similar interval size
      return 'parallel';
    }
    return 'similar';
  }
  return 'contrary'; // Opposite directions
}

/**
 * Validate a counterpoint move between two voices
 * Returns validation result with reason if invalid
 */
export interface CounterpointValidation {
  valid: boolean;
  reason?: string;
  motionType: MotionType;
  intervalRatio: number;
}

export function validateCounterpointMove(
  voice1Prev: number,
  voice1Curr: number,
  voice2Prev: number,
  voice2Curr: number,
  isStrongBeat: boolean,
): CounterpointValidation {
  const motionType = getMotionType(voice1Prev, voice1Curr, voice2Prev, voice2Curr);
  const intervalRatio = getIntervalRatio(
    Math.min(voice1Curr, voice2Curr),
    Math.max(voice1Curr, voice2Curr),
  );

  // Check for parallel fifths/octaves
  if (hasParallelPerfect(voice1Prev, voice1Curr, voice2Prev, voice2Curr)) {
    return {
      valid: false,
      reason: 'Parallel perfect consonance (fifths or octaves)',
      motionType,
      intervalRatio,
    };
  }

  // Check for voice crossing
  if (hasVoiceCrossing(voice1Curr, voice2Curr)) {
    return {
      valid: false,
      reason: 'Voice crossing detected',
      motionType,
      intervalRatio,
    };
  }

  // Strong beats should use consonant intervals
  if (isStrongBeat && !isConsonant(intervalRatio)) {
    return {
      valid: false,
      reason: 'Dissonance on strong beat without preparation',
      motionType,
      intervalRatio,
    };
  }

  // Dissonances on weak beats must be approached/left stepwise
  if (!isConsonant(intervalRatio) && !isStrongBeat) {
    // This would require checking approach/departure - simplified for now
    // In full implementation, check that dissonance is a passing tone
  }

  return {
    valid: true,
    motionType,
    intervalRatio,
  };
}

// =============================================================================
// SUBJECT GENERATION ALGORITHM
// =============================================================================

/**
 * Generate a fugue subject based on game phase
 */
export function generateSubject(config: SubjectConfig): FuguePhrase {
  const beatsPerBar = 4;
  const beatDuration = 60 / config.tempo; // Seconds per beat
  const barDuration = beatsPerBar * beatDuration;
  const totalDuration = config.barsLength * barDuration;

  const notes: FugueNote[] = [];
  let currentTime = 0;
  let currentPitch: number = C_SHARP_MINOR_SCALE.Cs4; // Start on tonic

  // Determine note count based on density
  const noteCountMap = {
    sparse: Math.floor(config.barsLength * 2),
    medium: Math.floor(config.barsLength * 4),
    dense: Math.floor(config.barsLength * 6),
  };
  const targetNoteCount = noteCountMap[config.noteDensity];

  // Generate notes
  for (let i = 0; i < targetNoteCount && currentTime < totalDuration; i++) {
    // Calculate duration based on rhythmic character
    let duration: number;
    switch (config.rhythmicCharacter) {
      case 'steady':
        duration = beatDuration;
        break;
      case 'syncopated':
        duration = beatDuration * (Math.random() > 0.5 ? 0.75 : 1.25);
        break;
      case 'urgent':
        duration = beatDuration * (0.25 + Math.random() * 0.5);
        break;
      case 'augmented':
        duration = beatDuration * 2;
        break;
    }

    // Ensure we don't exceed total duration
    if (currentTime + duration > totalDuration) {
      duration = totalDuration - currentTime;
    }

    // Calculate next pitch based on interval pattern
    let intervalSemitones: number;
    switch (config.intervalPattern) {
      case 'stepwise':
        intervalSemitones = Math.random() > 0.5 ? 1 : 2; // Minor/major 2nd
        if (Math.random() > 0.7) intervalSemitones = -intervalSemitones;
        break;
      case 'leaping':
        intervalSemitones = Math.random() > 0.5 ? 5 : 7; // 4th or 5th
        if (Math.random() > 0.5) intervalSemitones = -intervalSemitones;
        break;
      case 'mixed':
        if (Math.random() > 0.6) {
          intervalSemitones = Math.random() > 0.5 ? 5 : 7;
        } else {
          intervalSemitones = Math.random() > 0.5 ? 1 : 2;
        }
        if (Math.random() > 0.5) intervalSemitones = -intervalSemitones;
        break;
      case 'fragmented':
        // Chromatic, unpredictable
        intervalSemitones = Math.floor(Math.random() * 12) - 6;
        break;
    }

    // Calculate new pitch (semitone = multiply by 2^(1/12))
    const semitoneRatio = Math.pow(2, intervalSemitones / 12);
    let newPitch = currentPitch * semitoneRatio;

    // Keep within tenor range for subject
    const tenorRange = VOICE_RANGES.tenor;
    if (newPitch < tenorRange.low) newPitch = tenorRange.low;
    if (newPitch > tenorRange.high) newPitch = tenorRange.high;

    // Snap to scale degree
    newPitch = snapToScale(newPitch);
    const newDegree = getScaleDegreeIndex(newPitch);

    // Determine articulation
    let articulation: FugueNote['articulation'];
    if (i === 0 || i === targetNoteCount - 1) {
      articulation = 'tenuto';
    } else if (config.rhythmicCharacter === 'urgent') {
      articulation = 'staccato';
    } else if (config.rhythmicCharacter === 'augmented') {
      articulation = 'legato';
    } else {
      articulation = Math.random() > 0.7 ? 'marcato' : 'legato';
    }

    // Velocity based on metric position
    const isStrongBeat = (currentTime / beatDuration) % 1 < 0.1;
    const velocity = isStrongBeat ? 0.8 + Math.random() * 0.2 : 0.5 + Math.random() * 0.3;

    notes.push({
      pitch: newPitch,
      scaleDegree: newDegree,
      startTime: currentTime,
      duration,
      velocity,
      articulation,
    });

    currentTime += duration;
    currentPitch = newPitch;
  }

  return {
    notes,
    durationBars: config.barsLength,
    totalDuration,
  };
}

/**
 * Generate answer (subject transposed to dominant - G#)
 * In tonal fugue, answer is at the 5th (dominant)
 */
export function generateAnswer(subject: FuguePhrase): FuguePhrase {
  const dominantRatio = PERFECT_CONSONANCES.perfectFifth; // 1.5

  const notes: FugueNote[] = subject.notes.map((note) => ({
    ...note,
    pitch: note.pitch * dominantRatio,
    // Adjust scale degree (5 semitones up = dominant)
    scaleDegree: (note.scaleDegree + 4) % 7,
  }));

  return {
    notes,
    durationBars: subject.durationBars,
    totalDuration: subject.totalDuration,
  };
}

/**
 * Generate countersubject (melodic complement to subject)
 * Should create good counterpoint when played against subject
 */
export function generateCountersubject(subject: FuguePhrase): FuguePhrase {
  const notes: FugueNote[] = [];

  // For each subject note, create a counterpoint note
  for (let i = 0; i < subject.notes.length; i++) {
    const subjectNote = subject.notes[i];

    // Choose interval that creates good counterpoint
    // Prefer contrary motion
    const prevSubjectNote = i > 0 ? subject.notes[i - 1] : null;
    const subjectMovingUp = prevSubjectNote && subjectNote.pitch > prevSubjectNote.pitch;

    // Move in contrary motion
    let intervalRatio: number;
    if (Math.random() > 0.3) {
      // Use imperfect consonance (more interesting)
      const imperfect = Object.values(IMPERFECT_CONSONANCES);
      intervalRatio = imperfect[Math.floor(Math.random() * imperfect.length)];
    } else {
      // Use perfect consonance (more stable)
      intervalRatio = PERFECT_CONSONANCES.perfectFifth;
    }

    // Determine direction (contrary to subject)
    let counterPitch: number;
    if (subjectMovingUp) {
      // Subject going up, counter goes down
      counterPitch = subjectNote.pitch / intervalRatio;
    } else {
      // Subject going down or static, counter goes up
      counterPitch = subjectNote.pitch * intervalRatio;
    }

    // Snap to scale and adjust to alto range
    counterPitch = snapToScale(counterPitch);
    const altoRange = VOICE_RANGES.alto;
    if (counterPitch < altoRange.low) counterPitch *= 2;
    if (counterPitch > altoRange.high) counterPitch /= 2;

    notes.push({
      pitch: counterPitch,
      scaleDegree: getScaleDegreeIndex(counterPitch),
      startTime: subjectNote.startTime,
      duration: subjectNote.duration,
      velocity: subjectNote.velocity * 0.85, // Slightly softer
      articulation: subjectNote.articulation,
    });
  }

  return {
    notes,
    durationBars: subject.durationBars,
    totalDuration: subject.totalDuration,
  };
}

// =============================================================================
// SCALE UTILITY FUNCTIONS
// =============================================================================

/**
 * Snap a frequency to the nearest C# minor scale degree
 */
export function snapToScale(freq: number): number {
  // Get all scale frequencies across octaves
  const scaleFreqs: number[] = [];
  for (let octave = -2; octave <= 2; octave++) {
    const multiplier = Math.pow(2, octave);
    for (const baseFreq of MINOR_SCALE_DEGREES) {
      scaleFreqs.push(baseFreq * multiplier);
    }
  }

  // Find closest
  let closest = scaleFreqs[0];
  let minDiff = Math.abs(freq - closest);

  for (const scaleFreq of scaleFreqs) {
    const diff = Math.abs(freq - scaleFreq);
    if (diff < minDiff) {
      minDiff = diff;
      closest = scaleFreq;
    }
  }

  return closest;
}

/**
 * Get scale degree index (0-6) for a frequency
 */
export function getScaleDegreeIndex(freq: number): number {
  // Normalize to reference octave
  let normalized = freq;
  const refLow = MINOR_SCALE_DEGREES[0];
  const refHigh = MINOR_SCALE_DEGREES[0] * 2;

  while (normalized < refLow) normalized *= 2;
  while (normalized >= refHigh) normalized /= 2;

  // Find closest degree
  let closestDegree = 0;
  let minDiff = Math.abs(normalized - MINOR_SCALE_DEGREES[0]);

  for (let i = 1; i < MINOR_SCALE_DEGREES.length; i++) {
    const diff = Math.abs(normalized - MINOR_SCALE_DEGREES[i]);
    if (diff < minDiff) {
      minDiff = diff;
      closestDegree = i;
    }
  }

  return closestDegree;
}

/**
 * Get frequency for a scale degree in a specific octave
 */
export function getScaleFrequency(degree: number, octaveOffset: number = 0): number {
  const wrappedDegree = ((degree % 7) + 7) % 7;
  return MINOR_SCALE_DEGREES[wrappedDegree] * Math.pow(2, octaveOffset);
}

// =============================================================================
// STRETTO GENERATION
// =============================================================================

/**
 * Generate stretto entries (overlapping voice entries for climax)
 * Stretto creates tension by having voices enter before the previous one finishes
 */
export function generateStrettoEntries(
  subject: FuguePhrase,
  voiceCount: number,
  overlapRatio: number, // 0.5 = voices enter halfway through previous
): FugueNote[][] {
  const entries: FugueNote[][] = [];
  const voiceOrder: VoiceType[] = ['bass', 'tenor', 'alto', 'soprano'];
  const entryDelay = subject.totalDuration * overlapRatio;

  for (let i = 0; i < voiceCount; i++) {
    const voiceType = voiceOrder[i % voiceOrder.length];
    const range = VOICE_RANGES[voiceType];

    // Transpose subject to appropriate range
    const octaveShift = Math.log2(range.preferred / VOICE_RANGES.tenor.preferred);
    const transposition = Math.pow(2, Math.round(octaveShift));

    const voiceNotes: FugueNote[] = subject.notes.map((note) => ({
      ...note,
      pitch: snapToScale(note.pitch * transposition),
      startTime: note.startTime + (i * entryDelay),
      velocity: note.velocity * (1 - i * 0.1), // Slightly decrease with each entry
    }));

    entries.push(voiceNotes);
  }

  return entries;
}

// =============================================================================
// EPISODE GENERATION
// =============================================================================

/**
 * Generate episode (transitional passage between subject entries)
 * Episodes use sequences and modulation to connect structural sections
 */
export function generateEpisode(
  durationBars: number,
  tempo: number,
  sourcePhrase: FuguePhrase,
): FuguePhrase {
  const beatDuration = 60 / tempo;
  const barDuration = 4 * beatDuration;
  const totalDuration = durationBars * barDuration;

  // Take a motif from the source phrase (first few notes)
  const motifLength = Math.min(4, sourcePhrase.notes.length);
  const motif = sourcePhrase.notes.slice(0, motifLength);

  const notes: FugueNote[] = [];
  let currentTime = 0;
  let sequenceNumber = 0;

  while (currentTime < totalDuration) {
    // Sequence the motif (repeat at different pitch levels)
    const sequenceOffset = sequenceNumber * 2; // Step up by 2nds
    const transposition = Math.pow(2, sequenceOffset / 12);

    for (const motifNote of motif) {
      if (currentTime + motifNote.duration > totalDuration) break;

      notes.push({
        ...motifNote,
        pitch: snapToScale(motifNote.pitch * transposition),
        scaleDegree: (motifNote.scaleDegree + sequenceOffset) % 7,
        startTime: currentTime,
        velocity: motifNote.velocity * 0.7, // Episodes are softer
      });

      currentTime += motifNote.duration;
    }

    sequenceNumber++;

    // Add slight gap between sequences
    currentTime += beatDuration * 0.5;
  }

  return {
    notes,
    durationBars,
    totalDuration,
  };
}

// =============================================================================
// MARIMBA SYNTHESIS (WEB AUDIO API)
// =============================================================================

let audioContext: AudioContext | null = null;
let masterGain: GainNode | null = null;
let currentConfig: MarimbaConfig = { ...MARIMBA_DEFAULT };

/**
 * Initialize the fugue audio system
 */
export function initFugueAudio(ctx: AudioContext, master: GainNode): void {
  audioContext = ctx;
  masterGain = master;
}

/**
 * Set marimba configuration based on game phase
 */
export function setFuguePhase(phase: GamePhaseType): void {
  currentConfig = {
    ...MARIMBA_DEFAULT,
    ...MARIMBA_PHASE_OVERRIDES[phase],
  };
}

/**
 * Create a marimba note with proper timbre synthesis
 *
 * Marimba characteristics:
 * 1. Sharp attack transient from mallet strike
 * 2. Fundamental + tuned harmonics (bars are specifically shaped)
 * 3. Exponential decay (no sustain)
 * 4. Sympathetic resonance from nearby bars
 */
export function playMarimbaNote(
  note: FugueNote,
  config: MarimbaConfig = currentConfig,
): void {
  if (!audioContext || !masterGain) return;

  const ctx = audioContext;
  const now = ctx.currentTime;
  const startTime = now + note.startTime;

  // Create output gain for this note
  const noteGain = ctx.createGain();
  noteGain.gain.setValueAtTime(0, startTime);
  noteGain.connect(masterGain);

  // ==========================================================================
  // LAYER 1: Attack Transient (mallet strike)
  // ==========================================================================
  const attackDuration = config.attackNoiseDuration / 1000;

  // Noise burst for initial impact
  const noiseBufferSize = Math.floor(ctx.sampleRate * attackDuration);
  const noiseBuffer = ctx.createBuffer(1, noiseBufferSize, ctx.sampleRate);
  const noiseData = noiseBuffer.getChannelData(0);
  for (let i = 0; i < noiseBufferSize; i++) {
    // Envelope the noise
    const envelope = 1 - (i / noiseBufferSize);
    noiseData[i] = (Math.random() * 2 - 1) * envelope;
  }

  const noiseSource = ctx.createBufferSource();
  noiseSource.buffer = noiseBuffer;

  // Filter noise to match fundamental frequency
  const noiseFilter = ctx.createBiquadFilter();
  noiseFilter.type = 'bandpass';
  noiseFilter.frequency.value = note.pitch * 2;
  noiseFilter.Q.value = 3;

  const noiseGain = ctx.createGain();
  noiseGain.gain.setValueAtTime(config.attackNoiseLevel * note.velocity, startTime);
  noiseGain.gain.exponentialRampToValueAtTime(0.001, startTime + attackDuration);

  noiseSource.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(noteGain);
  noiseSource.start(startTime);
  noiseSource.stop(startTime + attackDuration);

  // Initial sine burst (attack click)
  const attackOsc = ctx.createOscillator();
  attackOsc.type = 'sine';
  attackOsc.frequency.value = note.pitch * 4; // High harmonic

  const attackOscGain = ctx.createGain();
  attackOscGain.gain.setValueAtTime(config.attackSineBurst * note.velocity, startTime);
  attackOscGain.gain.exponentialRampToValueAtTime(0.001, startTime + attackDuration * 0.5);

  attackOsc.connect(attackOscGain);
  attackOscGain.connect(noteGain);
  attackOsc.start(startTime);
  attackOsc.stop(startTime + attackDuration);

  // ==========================================================================
  // LAYER 2: Harmonic Content (tuned bar resonance)
  // ==========================================================================
  const decayDuration = config.decayTime / 1000;
  const totalDuration = Math.max(note.duration, decayDuration);

  // Fundamental + harmonics
  for (let h = 0; h < config.harmonics.length; h++) {
    const harmonic = h + 1;
    const harmonicFreq = note.pitch * harmonic;
    const harmonicAmp = config.harmonics[h] * note.velocity;

    if (harmonicAmp < 0.01) continue; // Skip inaudible

    const osc = ctx.createOscillator();
    osc.type = h === 0 ? 'sine' : 'triangle'; // Fundamental sine, harmonics triangle
    osc.frequency.value = harmonicFreq;

    const oscGain = ctx.createGain();
    // Attack
    oscGain.gain.setValueAtTime(0, startTime);
    oscGain.gain.linearRampToValueAtTime(harmonicAmp, startTime + 0.002);
    // Decay (exponential for marimba character)
    const decayRate = 1 + h * 0.5; // Higher harmonics decay faster
    oscGain.gain.exponentialRampToValueAtTime(
      0.001,
      startTime + totalDuration / decayRate,
    );

    osc.connect(oscGain);
    oscGain.connect(noteGain);
    osc.start(startTime);
    osc.stop(startTime + totalDuration);
  }

  // ==========================================================================
  // LAYER 3: Sympathetic Resonance
  // ==========================================================================
  // Nearby scale notes ring sympathetically
  const resonanceFreqs = [
    note.pitch * IMPERFECT_CONSONANCES.minorThird, // Minor 3rd below
    note.pitch * PERFECT_CONSONANCES.perfectFifth, // 5th above
  ];

  for (const resFreq of resonanceFreqs) {
    const resOsc = ctx.createOscillator();
    resOsc.type = 'sine';
    resOsc.frequency.value = snapToScale(resFreq);

    const resGain = ctx.createGain();
    const resDuration = config.resonanceDecay / 1000;
    resGain.gain.setValueAtTime(0, startTime);
    // Delayed start for resonance
    resGain.gain.setValueAtTime(0, startTime + 0.02);
    resGain.gain.linearRampToValueAtTime(
      config.resonanceLevel * note.velocity,
      startTime + 0.05,
    );
    resGain.gain.exponentialRampToValueAtTime(0.001, startTime + resDuration);

    resOsc.connect(resGain);
    resGain.connect(noteGain);
    resOsc.start(startTime);
    resOsc.stop(startTime + resDuration);
  }

  // ==========================================================================
  // Master envelope
  // ==========================================================================
  noteGain.gain.linearRampToValueAtTime(1, startTime + 0.003);
  // Articulation
  switch (note.articulation) {
    case 'staccato':
      noteGain.gain.exponentialRampToValueAtTime(0.001, startTime + note.duration * 0.5);
      break;
    case 'marcato':
      noteGain.gain.setValueAtTime(1, startTime + note.duration * 0.3);
      noteGain.gain.exponentialRampToValueAtTime(0.001, startTime + note.duration);
      break;
    case 'tenuto':
      noteGain.gain.setValueAtTime(1, startTime + note.duration * 0.9);
      noteGain.gain.exponentialRampToValueAtTime(0.001, startTime + note.duration * 1.1);
      break;
    case 'legato':
    default:
      noteGain.gain.setValueAtTime(1, startTime + note.duration * 0.7);
      noteGain.gain.exponentialRampToValueAtTime(0.001, startTime + totalDuration);
  }
}

/**
 * Play a complete fugue phrase
 */
export function playFuguePhrase(phrase: FuguePhrase): void {
  for (const note of phrase.notes) {
    playMarimbaNote(note);
  }
}

// =============================================================================
// REAL-TIME VOICE MANAGEMENT
// =============================================================================

/**
 * Create initial fugue state
 */
export function createFugueState(phase: GamePhaseType): FugueState {
  const config = PHASE_CONFIGS[phase];

  const createVoice = (type: VoiceType): FugueVoice => ({
    type,
    active: false,
    currentNote: null,
    noteQueue: [],
    lastPitch: VOICE_RANGES[type].preferred,
    entryTime: 0,
    currentPhrase: 'rest',
  });

  return {
    voices: {
      soprano: createVoice('soprano'),
      alto: createVoice('alto'),
      tenor: createVoice('tenor'),
      bass: createVoice('bass'),
    },
    subject: null,
    answer: null,
    countersubject: null,
    currentBar: 0,
    tempo: config.tempo,
    gamePhase: phase,
    inStretto: false,
    density: 0.5,
    lastUpdateTime: 0,
  };
}

/**
 * Update fugue state based on game events
 */
export function updateFugueState(
  state: FugueState,
  currentTime: number,
  events: {
    killCount?: number;
    waveTransition?: boolean;
    comboActive?: boolean;
    enemyCount?: number;
  },
): FugueState {
  const deltaTime = currentTime - state.lastUpdateTime;
  const beatDuration = 60 / state.tempo;
  const barDuration = 4 * beatDuration;

  // Update current bar
  const elapsedBars = deltaTime / barDuration;
  const newBar = state.currentBar + elapsedBars;

  // Generate subject if needed
  if (!state.subject) {
    const config = PHASE_CONFIGS[state.gamePhase];
    state.subject = generateSubject(config);
    state.answer = generateAnswer(state.subject);
    state.countersubject = generateCountersubject(state.subject);
  }

  // Voice entry logic
  // Classic fugue: Tenor -> Alto -> Soprano -> Bass
  const voiceOrder: VoiceType[] = ['tenor', 'alto', 'soprano', 'bass'];
  const subjectBars = state.subject?.durationBars ?? 4;

  for (let i = 0; i < voiceOrder.length; i++) {
    const voiceType = voiceOrder[i];
    const voice = state.voices[voiceType];
    const entryBar = i * subjectBars;

    // Check if voice should enter
    if (!voice.active && newBar >= entryBar && voice.noteQueue.length === 0) {
      // Activate voice
      voice.active = true;
      voice.entryTime = currentTime;

      // Assign appropriate phrase
      if (i === 0) {
        // First voice gets subject
        voice.currentPhrase = 'subject';
        if (state.subject) {
          voice.noteQueue = [...state.subject.notes];
        }
      } else if (i === 1 || i === 3) {
        // Second and fourth get answer
        voice.currentPhrase = 'answer';
        if (state.answer) {
          voice.noteQueue = transposeToVoiceRange(state.answer.notes, voiceType);
        }
      } else {
        // Third gets subject again
        voice.currentPhrase = 'subject';
        if (state.subject) {
          voice.noteQueue = transposeToVoiceRange(state.subject.notes, voiceType);
        }
      }

      // If countersubject is available and previous voice is done, add it
      if (i > 0 && state.countersubject) {
        const prevVoice = state.voices[voiceOrder[i - 1]];
        if (prevVoice.noteQueue.length === 0) {
          prevVoice.currentPhrase = 'countersubject';
          prevVoice.noteQueue = transposeToVoiceRange(
            state.countersubject.notes,
            voiceOrder[i - 1],
          );
        }
      }
    }
  }

  // Trigger stretto on wave transitions (climactic moment)
  if (events.waveTransition && !state.inStretto) {
    state.inStretto = true;
    if (state.subject) {
      const strettoEntries = generateStrettoEntries(state.subject, 4, 0.3);
      voiceOrder.forEach((voiceType, i) => {
        if (strettoEntries[i]) {
          state.voices[voiceType].noteQueue = transposeToVoiceRange(
            strettoEntries[i],
            voiceType,
          );
        }
      });
    }
  }

  // Update density based on enemy count
  if (events.enemyCount !== undefined) {
    state.density = Math.min(1, events.enemyCount / 50);
  }

  // Play notes from queues
  for (const voiceType of voiceOrder) {
    const voice = state.voices[voiceType];
    if (voice.noteQueue.length > 0) {
      const note = voice.noteQueue[0];
      if (currentTime >= voice.entryTime + note.startTime) {
        playMarimbaNote(note);
        voice.currentNote = note;
        voice.lastPitch = note.pitch;
        voice.noteQueue.shift();
      }
    } else if (voice.active && voice.currentPhrase !== 'rest') {
      // Voice finished, generate free counterpoint or rest
      voice.currentPhrase = 'rest';
    }
  }

  return {
    ...state,
    currentBar: newBar % (subjectBars * 4), // Loop after exposition
    lastUpdateTime: currentTime,
  };
}

/**
 * Transpose notes to fit a voice range
 */
function transposeToVoiceRange(notes: FugueNote[], voiceType: VoiceType): FugueNote[] {
  const range = VOICE_RANGES[voiceType];

  return notes.map((note) => {
    let transposedPitch = note.pitch;

    // Shift octaves until in range
    while (transposedPitch < range.low) transposedPitch *= 2;
    while (transposedPitch > range.high) transposedPitch /= 2;

    return {
      ...note,
      pitch: snapToScale(transposedPitch),
    };
  });
}

// =============================================================================
// GAME EVENT TRIGGERS
// =============================================================================

/**
 * Trigger a voice entry on game event (kill, combo milestone)
 */
export function triggerVoiceEntry(
  state: FugueState,
  voiceType: VoiceType,
  phrase: FuguePhrase,
): void {
  const voice = state.voices[voiceType];
  voice.active = true;
  voice.entryTime = audioContext?.currentTime ?? 0;
  voice.noteQueue = transposeToVoiceRange(phrase.notes, voiceType);
  voice.currentPhrase = 'free';
}

/**
 * Trigger stretto for wave/combo climax
 */
export function triggerStretto(state: FugueState, intensity: number): void {
  if (!state.subject) return;

  const overlapRatio = 0.5 - (intensity * 0.3); // More overlap = more intense
  const strettoEntries = generateStrettoEntries(state.subject, 4, overlapRatio);
  const voiceOrder: VoiceType[] = ['bass', 'tenor', 'alto', 'soprano'];

  voiceOrder.forEach((voiceType, i) => {
    if (strettoEntries[i]) {
      triggerVoiceEntry(state, voiceType, {
        notes: strettoEntries[i],
        durationBars: state.subject!.durationBars,
        totalDuration: state.subject!.totalDuration,
      });
    }
  });

  state.inStretto = true;
}

/**
 * Play a single climactic note in all voices (for massacre/boss kill)
 */
export function playFugueClimaxChord(degree: number = 0): void {
  if (!audioContext || !masterGain) return;

  const voiceTypes: VoiceType[] = ['bass', 'tenor', 'alto', 'soprano'];

  voiceTypes.forEach((voiceType, i) => {
    const range = VOICE_RANGES[voiceType];
    const octave = Math.floor(Math.log2(range.preferred / MINOR_SCALE_DEGREES[0]));

    const note: FugueNote = {
      pitch: getScaleFrequency(degree, octave),
      scaleDegree: degree,
      startTime: i * 0.02, // Slight stagger for richness
      duration: 1.5,
      velocity: 0.9,
      articulation: 'tenuto',
    };

    playMarimbaNote(note, {
      ...currentConfig,
      decayTime: 1000,
      resonanceLevel: 0.15,
    });
  });
}

// =============================================================================
// EXPORT DEFAULT
// =============================================================================

export default {
  // Scale and interval constants
  C_SHARP_MINOR_SCALE,
  MINOR_SCALE_DEGREES,
  PERFECT_CONSONANCES,
  IMPERFECT_CONSONANCES,
  DISSONANCES,
  VOICE_RANGES,
  PHASE_CONFIGS,

  // Counterpoint validation
  getIntervalRatio,
  isConsonant,
  isPerfectConsonance,
  hasParallelPerfect,
  hasVoiceCrossing,
  getMotionType,
  validateCounterpointMove,

  // Subject generation
  generateSubject,
  generateAnswer,
  generateCountersubject,
  generateStrettoEntries,
  generateEpisode,

  // Scale utilities
  snapToScale,
  getScaleDegreeIndex,
  getScaleFrequency,

  // Audio synthesis
  initFugueAudio,
  setFuguePhase,
  playMarimbaNote,
  playFuguePhrase,

  // State management
  createFugueState,
  updateFugueState,
  triggerVoiceEntry,
  triggerStretto,
  playFugueClimaxChord,

  // Marimba config
  MARIMBA_DEFAULT,
  MARIMBA_PHASE_OVERRIDES,
};
