/**
 * WASM Survivors - Procedural Fugue & Counterpoint System
 *
 * A Markov chain-driven music generation system in C# minor that creates
 * real-time fugue-style counterpoint based on game state hyperparameters.
 *
 * "The hornet hunts to Bach. The bees die to counterpoint."
 *
 * MUSICAL ARCHITECTURE:
 * - Key: C# minor (dark, intense, perfect for survival horror)
 * - Form: Fugue-inspired with subject/answer/countersubject
 * - Voices: Up to 4 independent melodic lines
 * - Transitions: Markov chain between musical phases
 *
 * HYPERPARAMETERS (all 0-1):
 * - intensity: tempo, note density, dynamics
 * - tension: dissonance level, harmonic rhythm
 * - momentum: rhythmic drive, syncopation
 * - voiceDensity: active voice count
 * - registralSpread: pitch range width
 * - ornamentation: melodic embellishment
 *
 * @see https://en.wikipedia.org/wiki/Fugue
 * @see emergent-audio.ts for integration layer
 */

// =============================================================================
// MUSIC THEORY: C# MINOR FOUNDATION
// =============================================================================

/**
 * C# minor scale frequencies (C#4 = 277.18 Hz as tonic)
 * Using equal temperament: f = 277.18 * 2^(semitones/12)
 */
export const CSHARP_MINOR = {
  // Base frequency (C#4)
  tonic: 277.18,

  // Scale degrees in semitones from root
  scales: {
    natural: [0, 2, 3, 5, 7, 8, 10],      // C# D# E F# G# A B
    harmonic: [0, 2, 3, 5, 7, 8, 11],     // C# D# E F# G# A B# (raised 7th)
    melodicUp: [0, 2, 3, 5, 7, 9, 11],    // C# D# E F# G# A# B# (ascending)
    melodicDown: [0, 2, 3, 5, 7, 8, 10],  // Natural minor descending
  },

  // Chord voicings (semitones from root)
  chords: {
    i:    [0, 3, 7],      // C#m - tonic
    iM7:  [0, 3, 7, 11],  // C#mM7 - tonic with leading tone
    ii:   [2, 5, 8],      // D#dim - supertonic diminished
    III:  [3, 7, 10],     // E - mediant major
    iv:   [5, 8, 0],      // F#m - subdominant
    v:    [7, 10, 2],     // G#m - dominant minor (natural)
    V:    [7, 11, 2],     // G# - dominant major (harmonic)
    V7:   [7, 11, 2, 5],  // G#7 - dominant seventh
    VI:   [8, 0, 3],      // A - submediant
    VII:  [10, 2, 5],     // B - subtonic (natural)
    viio: [11, 2, 5],     // B#dim - leading tone diminished
  },

  // Characteristic intervals for fugue subject
  intervals: {
    unison: 0,
    minorSecond: 1,
    majorSecond: 2,
    minorThird: 3,
    majorThird: 4,
    perfectFourth: 5,
    tritone: 6,        // The "diabolus in musica" - tension!
    perfectFifth: 7,
    minorSixth: 8,
    majorSixth: 9,
    minorSeventh: 10,
    majorSeventh: 11,
    octave: 12,
  },
};

/**
 * Convert scale degree to frequency
 * Returns a safe default frequency (C#4) if inputs are invalid
 */
export function degreeToFreq(degree: number, octaveOffset: number = 0): number {
  // Guard against NaN/Infinity inputs
  if (!Number.isFinite(degree)) {
    console.warn('degreeToFreq: invalid degree', degree);
    return CSHARP_MINOR.tonic; // Return tonic as fallback
  }
  if (!Number.isFinite(octaveOffset)) {
    octaveOffset = 0;
  }

  const normalizedDegree = ((degree % 7) + 7) % 7; // Handle negative degrees
  const semitones = CSHARP_MINOR.scales.harmonic[normalizedDegree];

  // Guard against undefined semitones (shouldn't happen but be safe)
  if (semitones === undefined) {
    console.warn('degreeToFreq: undefined semitones for degree', degree);
    return CSHARP_MINOR.tonic;
  }

  const octave = Math.floor(degree / 7) + octaveOffset;
  const freq = CSHARP_MINOR.tonic * Math.pow(2, (semitones + octave * 12) / 12);

  // Final sanity check
  if (!Number.isFinite(freq) || freq <= 0) {
    console.warn('degreeToFreq: computed invalid frequency', freq);
    return CSHARP_MINOR.tonic;
  }

  return freq;
}

/**
 * Convert semitone offset to frequency
 */
export function semitoneToFreq(semitone: number, octaveOffset: number = 0): number {
  return CSHARP_MINOR.tonic * Math.pow(2, (semitone + octaveOffset * 12) / 12);
}

// =============================================================================
// FUGUE SUBJECT DEFINITIONS
// =============================================================================

/**
 * A melodic motif with rhythm and articulation
 */
export interface Note {
  degree: number;        // Scale degree (0-6 within octave, can extend)
  duration: number;      // In beats (1 = quarter note)
  velocity: number;      // 0-1 dynamics
  articulation: 'legato' | 'staccato' | 'accent' | 'tenuto';
}

/**
 * The fugue subject - the main theme that gets developed
 * In C# minor, starting on the tonic
 */
export const FUGUE_SUBJECT: Note[] = [
  // Opening gesture: C# - B# - C# (neighbor tone)
  { degree: 0, duration: 0.5, velocity: 0.9, articulation: 'accent' },
  { degree: 6, duration: 0.25, velocity: 0.7, articulation: 'legato' },  // B (leading tone)
  { degree: 0, duration: 0.25, velocity: 0.8, articulation: 'legato' },

  // Rising line: E - F# - G#
  { degree: 2, duration: 0.5, velocity: 0.75, articulation: 'legato' },
  { degree: 3, duration: 0.5, velocity: 0.8, articulation: 'legato' },
  { degree: 4, duration: 0.75, velocity: 0.85, articulation: 'tenuto' },

  // Dramatic leap down and resolution
  { degree: 1, duration: 0.25, velocity: 0.7, articulation: 'staccato' },  // D#
  { degree: 0, duration: 1.0, velocity: 0.9, articulation: 'tenuto' },     // C# resolution
];

/**
 * The answer - subject transposed to dominant (G# minor, 5th up)
 * In a real fugue, the answer is "tonal" - adjusted to maintain key
 */
export const FUGUE_ANSWER: Note[] = FUGUE_SUBJECT.map(note => ({
  ...note,
  degree: note.degree + 4, // Transpose up a 5th (4 scale degrees)
}));

/**
 * Countersubject - accompaniment that works contrapuntally with subject
 * Moves in contrary motion, fills rhythmic gaps
 */
export const COUNTERSUBJECT: Note[] = [
  // Sustained note while subject begins
  { degree: 4, duration: 1.0, velocity: 0.6, articulation: 'legato' },  // G#

  // Descending line against ascending subject
  { degree: 3, duration: 0.5, velocity: 0.65, articulation: 'legato' },
  { degree: 2, duration: 0.5, velocity: 0.6, articulation: 'legato' },
  { degree: 1, duration: 0.5, velocity: 0.55, articulation: 'legato' },

  // Rhythmic counterpoint
  { degree: 0, duration: 0.25, velocity: 0.7, articulation: 'staccato' },
  { degree: 2, duration: 0.25, velocity: 0.6, articulation: 'staccato' },
  { degree: 1, duration: 0.5, velocity: 0.65, articulation: 'legato' },
  { degree: 0, duration: 0.5, velocity: 0.7, articulation: 'tenuto' },
];

/**
 * Free counterpoint fragments for episodes
 */
export const EPISODE_FRAGMENTS: Note[][] = [
  // Sequence pattern 1: descending thirds
  [
    { degree: 4, duration: 0.25, velocity: 0.6, articulation: 'legato' },
    { degree: 2, duration: 0.25, velocity: 0.55, articulation: 'legato' },
    { degree: 3, duration: 0.25, velocity: 0.6, articulation: 'legato' },
    { degree: 1, duration: 0.25, velocity: 0.55, articulation: 'legato' },
  ],
  // Sequence pattern 2: ascending steps
  [
    { degree: 0, duration: 0.5, velocity: 0.65, articulation: 'staccato' },
    { degree: 1, duration: 0.5, velocity: 0.7, articulation: 'staccato' },
    { degree: 2, duration: 0.5, velocity: 0.75, articulation: 'staccato' },
    { degree: 3, duration: 0.5, velocity: 0.8, articulation: 'accent' },
  ],
  // Pedal tone pattern
  [
    { degree: 0, duration: 0.25, velocity: 0.5, articulation: 'staccato' },
    { degree: 0, duration: 0.25, velocity: 0.5, articulation: 'staccato' },
    { degree: 0, duration: 0.25, velocity: 0.5, articulation: 'staccato' },
    { degree: 0, duration: 0.25, velocity: 0.6, articulation: 'accent' },
  ],
];

// =============================================================================
// MARKOV PHASE SYSTEM
// =============================================================================

/**
 * Musical phases in the fugue structure
 */
export type MusicPhase =
  | 'exposition'      // Subject introduced in each voice
  | 'development'     // Subject fragments, sequences, modulation
  | 'stretto'         // Overlapping subject entries (climax)
  | 'episode'         // Free counterpoint, sequential passages
  | 'pedal'           // Sustained bass, building tension
  | 'recapitulation'  // Return to subject in tonic
  | 'coda'            // Final cadential gesture
  | 'silence';        // Rest, breath

/**
 * Game-driven hyperparameters that influence the Markov chain
 */
export interface MusicHyperparameters {
  intensity: number;        // 0-1: tempo, density, dynamics
  tension: number;          // 0-1: dissonance, harmonic rhythm
  momentum: number;         // 0-1: rhythmic drive, forward motion
  voiceDensity: number;     // 0-1: how many voices active
  registralSpread: number;  // 0-1: pitch range width
  ornamentation: number;    // 0-1: melodic embellishment
  chaosLevel: number;       // 0-1: randomness in choices
}

/**
 * Default hyperparameters for exploration phase
 */
export const DEFAULT_HYPERPARAMETERS: MusicHyperparameters = {
  intensity: 0.3,
  tension: 0.2,
  momentum: 0.4,
  voiceDensity: 0.3,
  registralSpread: 0.5,
  ornamentation: 0.2,
  chaosLevel: 0.1,
};

/**
 * Base transition probabilities between music phases
 * Modified at runtime by hyperparameters
 */
const BASE_TRANSITIONS: Record<MusicPhase, Record<MusicPhase, number>> = {
  exposition: {
    exposition: 0.3,     // Continue exposition in other voices
    development: 0.35,   // Move to development
    stretto: 0.05,       // Rare early stretto
    episode: 0.2,        // Transition episode
    pedal: 0.05,
    recapitulation: 0.0,
    coda: 0.0,
    silence: 0.05,
  },
  development: {
    exposition: 0.05,
    development: 0.4,    // Continue developing
    stretto: 0.2,        // Build to stretto
    episode: 0.25,       // More episodes
    pedal: 0.05,
    recapitulation: 0.05,
    coda: 0.0,
    silence: 0.0,
  },
  stretto: {
    exposition: 0.0,
    development: 0.15,
    stretto: 0.35,       // Continue stretto intensity
    episode: 0.1,
    pedal: 0.15,
    recapitulation: 0.2,
    coda: 0.05,
    silence: 0.0,
  },
  episode: {
    exposition: 0.1,
    development: 0.3,
    stretto: 0.15,
    episode: 0.25,
    pedal: 0.1,
    recapitulation: 0.1,
    coda: 0.0,
    silence: 0.0,
  },
  pedal: {
    exposition: 0.05,
    development: 0.1,
    stretto: 0.35,       // Pedal often leads to climax
    episode: 0.1,
    pedal: 0.2,
    recapitulation: 0.15,
    coda: 0.05,
    silence: 0.0,
  },
  recapitulation: {
    exposition: 0.1,
    development: 0.1,
    stretto: 0.15,
    episode: 0.1,
    pedal: 0.1,
    recapitulation: 0.25,
    coda: 0.2,
    silence: 0.0,
  },
  coda: {
    exposition: 0.0,
    development: 0.0,
    stretto: 0.05,
    episode: 0.0,
    pedal: 0.1,
    recapitulation: 0.0,
    coda: 0.35,
    silence: 0.5,        // Coda leads to silence
  },
  silence: {
    exposition: 0.6,     // New beginning
    development: 0.1,
    stretto: 0.0,
    episode: 0.15,
    pedal: 0.1,
    recapitulation: 0.05,
    coda: 0.0,
    silence: 0.0,
  },
};

/**
 * Modify transition probabilities based on hyperparameters
 */
export function computeTransitionMatrix(
  base: Record<MusicPhase, Record<MusicPhase, number>>,
  params: MusicHyperparameters
): Record<MusicPhase, Record<MusicPhase, number>> {
  const modified: Record<MusicPhase, Record<MusicPhase, number>> = {} as any;

  for (const from of Object.keys(base) as MusicPhase[]) {
    modified[from] = { ...base[from] };

    // High intensity increases stretto probability
    if (params.intensity > 0.6) {
      modified[from].stretto = (modified[from].stretto || 0) * (1 + params.intensity);
      modified[from].episode = (modified[from].episode || 0) * (1 - params.intensity * 0.5);
    }

    // High tension increases pedal and dissonant phases
    if (params.tension > 0.5) {
      modified[from].pedal = (modified[from].pedal || 0) * (1 + params.tension);
      modified[from].silence = (modified[from].silence || 0) * (1 - params.tension);
    }

    // High momentum reduces silence, increases development
    if (params.momentum > 0.5) {
      modified[from].development = (modified[from].development || 0) * (1 + params.momentum * 0.5);
      modified[from].silence = (modified[from].silence || 0) * (1 - params.momentum);
    }

    // Low intensity increases episodes and silence
    if (params.intensity < 0.3) {
      modified[from].episode = (modified[from].episode || 0) * 1.5;
      modified[from].silence = (modified[from].silence || 0) * 1.5;
      modified[from].stretto = (modified[from].stretto || 0) * 0.3;
    }

    // Chaos adds randomness
    if (params.chaosLevel > 0.5) {
      for (const to of Object.keys(modified[from]) as MusicPhase[]) {
        modified[from][to] += (Math.random() - 0.5) * params.chaosLevel * 0.3;
        modified[from][to] = Math.max(0, modified[from][to]);
      }
    }

    // Normalize probabilities
    const sum = Object.values(modified[from]).reduce((a, b) => a + b, 0);
    if (sum > 0) {
      for (const to of Object.keys(modified[from]) as MusicPhase[]) {
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
  current: MusicPhase,
  matrix: Record<MusicPhase, Record<MusicPhase, number>>
): MusicPhase {
  const probs = matrix[current];
  const rand = Math.random();
  let cumulative = 0;

  for (const [phase, prob] of Object.entries(probs)) {
    cumulative += prob;
    if (rand < cumulative) {
      return phase as MusicPhase;
    }
  }

  return 'exposition'; // Fallback
}

// =============================================================================
// VOICE SYSTEM
// =============================================================================

/**
 * Voice register ranges (in octave offsets from middle C#)
 */
export const VOICE_REGISTERS = {
  soprano: { low: 1, high: 2 },   // C#5 - C#6
  alto: { low: 0, high: 1 },      // C#4 - C#5
  tenor: { low: -1, high: 0 },    // C#3 - C#4
  bass: { low: -2, high: -1 },    // C#2 - C#3
};

export type VoiceName = keyof typeof VOICE_REGISTERS;

/**
 * State of a single voice in the fugue
 */
export interface VoiceState {
  name: VoiceName;
  active: boolean;
  currentMaterial: 'subject' | 'answer' | 'countersubject' | 'free' | 'rest';
  noteIndex: number;           // Position in current material
  octaveOffset: number;        // Register adjustment
  rhythmMultiplier: number;    // For augmentation/diminution
  lastPitch: number;           // For smooth voice leading
  scheduledNotes: ScheduledNote[];
}

export interface ScheduledNote {
  frequency: number;
  startTime: number;
  duration: number;
  velocity: number;
  articulation: Note['articulation'];
  voiceName: VoiceName;
}

/**
 * Create initial voice state
 */
export function createVoiceState(name: VoiceName): VoiceState {
  const register = VOICE_REGISTERS[name];
  return {
    name,
    active: false,
    currentMaterial: 'rest',
    noteIndex: 0,
    octaveOffset: (register.low + register.high) / 2,
    rhythmMultiplier: 1.0,
    lastPitch: degreeToFreq(0, (register.low + register.high) / 2),
    scheduledNotes: [],
  };
}

// =============================================================================
// COUNTERPOINT RULES
// =============================================================================

/**
 * Check if two simultaneous pitches form a consonance
 * In Baroque counterpoint: unison, 3rd, 5th, 6th, octave are consonant
 */
export function isConsonant(freq1: number, freq2: number): boolean {
  const ratio = freq1 > freq2 ? freq1 / freq2 : freq2 / freq1;
  const semitones = Math.round(12 * Math.log2(ratio)) % 12;

  // Consonant intervals in semitones
  const consonances = [0, 3, 4, 7, 8, 9, 12]; // unison, m3, M3, P5, m6, M6, octave
  return consonances.includes(semitones);
}

/**
 * Check for parallel fifths/octaves (forbidden in strict counterpoint)
 */
export function hasParallelFifthsOrOctaves(
  voice1Prev: number, voice1Curr: number,
  voice2Prev: number, voice2Curr: number
): boolean {
  const prevInterval = Math.abs(Math.round(12 * Math.log2(voice1Prev / voice2Prev))) % 12;
  const currInterval = Math.abs(Math.round(12 * Math.log2(voice1Curr / voice2Curr))) % 12;

  // Both are fifths (7 semitones) or octaves (0 semitones)
  const isFifth = (i: number) => i === 7;
  const isOctave = (i: number) => i === 0;

  return (isFifth(prevInterval) && isFifth(currInterval)) ||
         (isOctave(prevInterval) && isOctave(currInterval));
}

/**
 * Get notes that avoid parallel motion issues
 */
export function getContraryMotionNote(
  fixedVoicePrev: number,
  fixedVoiceCurr: number,
  movingVoicePrev: number,
  targetDegrees: number[],
  octaveOffset: number
): number {
  const fixedDirection = fixedVoiceCurr - fixedVoicePrev;

  // Prefer contrary motion
  const preferDescending = fixedDirection > 0;

  // Find best note from target degrees
  let bestNote = degreeToFreq(targetDegrees[0], octaveOffset);
  let bestScore = -Infinity;

  for (const degree of targetDegrees) {
    const freq = degreeToFreq(degree, octaveOffset);
    let score = 0;

    // Prefer consonance
    if (isConsonant(freq, fixedVoiceCurr)) score += 10;

    // Prefer contrary motion
    const direction = freq - movingVoicePrev;
    if ((preferDescending && direction < 0) || (!preferDescending && direction > 0)) {
      score += 5;
    }

    // Avoid parallel fifths/octaves
    if (!hasParallelFifthsOrOctaves(fixedVoicePrev, fixedVoiceCurr, movingVoicePrev, freq)) {
      score += 8;
    }

    // Prefer small intervals (smooth voice leading)
    const interval = Math.abs(freq - movingVoicePrev);
    score -= interval / 100; // Penalize large leaps

    if (score > bestScore) {
      bestScore = score;
      bestNote = freq;
    }
  }

  return bestNote;
}

// =============================================================================
// PROCEDURAL FUGUE ENGINE
// =============================================================================

/**
 * Full state of the procedural music system
 */
export interface FugueState {
  // Current musical phase
  phase: MusicPhase;
  phaseProgress: number;        // 0-1 progress through current phase
  phaseDuration: number;        // Duration of current phase in beats

  // Voice states
  voices: Record<VoiceName, VoiceState>;

  // Timing
  tempo: number;                // BPM
  currentBeat: number;          // Absolute beat position
  beatsPerMeasure: number;      // Time signature (usually 4)

  // Hyperparameters
  params: MusicHyperparameters;

  // Transition matrix (computed from params)
  transitionMatrix: Record<MusicPhase, Record<MusicPhase, number>>;

  // Harmonic state
  currentChord: keyof typeof CSHARP_MINOR.chords;
  harmonicRhythm: number;       // Beats per chord change

  // Generation state
  lastGenerationTime: number;
  generationLookahead: number;  // Seconds to generate ahead
}

/**
 * Create initial fugue state
 */
export function createFugueState(params: MusicHyperparameters = DEFAULT_HYPERPARAMETERS): FugueState {
  return {
    phase: 'silence',
    phaseProgress: 0,
    phaseDuration: 4,

    voices: {
      soprano: createVoiceState('soprano'),
      alto: createVoiceState('alto'),
      tenor: createVoiceState('tenor'),
      bass: createVoiceState('bass'),
    },

    tempo: 80, // Starts moderate, adjusts with intensity
    currentBeat: 0,
    beatsPerMeasure: 4,

    params,
    transitionMatrix: computeTransitionMatrix(BASE_TRANSITIONS, params),

    currentChord: 'i',
    harmonicRhythm: 4,

    lastGenerationTime: 0,
    generationLookahead: 2.0,
  };
}

/**
 * Update hyperparameters and recompute transition matrix
 */
export function updateHyperparameters(
  state: FugueState,
  newParams: Partial<MusicHyperparameters>
): FugueState {
  const params = { ...state.params, ...newParams };

  // Tempo scales with intensity: 60-140 BPM
  const tempo = 60 + params.intensity * 80;

  return {
    ...state,
    params,
    tempo,
    transitionMatrix: computeTransitionMatrix(BASE_TRANSITIONS, params),
  };
}

/**
 * Determine how many voices should be active based on voiceDensity
 */
function getActiveVoiceCount(params: MusicHyperparameters): number {
  const density = params.voiceDensity;
  if (density < 0.2) return 1;
  if (density < 0.4) return 2;
  if (density < 0.7) return 3;
  return 4;
}

/**
 * Get the material (notes) for a given phase and voice
 */
function getMaterialForPhase(
  phase: MusicPhase,
  voice: VoiceName,
  voiceIndex: number,
  params: MusicHyperparameters
): { notes: Note[]; material: VoiceState['currentMaterial'] } {
  switch (phase) {
    case 'exposition':
      // Traditional fugue exposition: voices enter one by one with subject/answer
      if (voiceIndex === 0) {
        return { notes: FUGUE_SUBJECT, material: 'subject' };
      } else if (voiceIndex === 1) {
        return { notes: FUGUE_ANSWER, material: 'answer' };
      } else if (voiceIndex === 2) {
        return { notes: COUNTERSUBJECT, material: 'countersubject' };
      } else {
        return { notes: FUGUE_SUBJECT, material: 'subject' };
      }

    case 'stretto':
      // All voices play subject in quick succession (overlapping)
      return { notes: FUGUE_SUBJECT, material: 'subject' };

    case 'development':
      // Mix of subject fragments and free counterpoint
      if (Math.random() < 0.5 + params.tension * 0.3) {
        // Use subject fragment (first half)
        return { notes: FUGUE_SUBJECT.slice(0, 4), material: 'subject' };
      } else {
        return { notes: COUNTERSUBJECT, material: 'countersubject' };
      }

    case 'episode':
      // Free sequential passages
      const fragmentIdx = Math.floor(Math.random() * EPISODE_FRAGMENTS.length);
      return { notes: EPISODE_FRAGMENTS[fragmentIdx], material: 'free' };

    case 'pedal':
      // Bass holds pedal tone, upper voices move freely
      if (voice === 'bass') {
        // Long pedal tone on tonic
        return {
          notes: [{ degree: 0, duration: 4, velocity: 0.7, articulation: 'tenuto' }],
          material: 'free'
        };
      } else {
        return { notes: EPISODE_FRAGMENTS[1], material: 'free' };
      }

    case 'recapitulation':
      // Return to subject in tonic
      return { notes: FUGUE_SUBJECT, material: 'subject' };

    case 'coda':
      // Final cadential figure
      return {
        notes: [
          { degree: 4, duration: 0.5, velocity: 0.8, articulation: 'legato' }, // V
          { degree: 0, duration: 2.0, velocity: 0.9, articulation: 'tenuto' }, // I
        ],
        material: 'free'
      };

    case 'silence':
    default:
      return { notes: [], material: 'rest' };
  }
}

/**
 * Apply ornamentation to a note based on hyperparameters
 */
function applyOrnamentation(
  note: Note,
  params: MusicHyperparameters,
  prevDegree: number | null
): Note[] {
  if (Math.random() > params.ornamentation) {
    return [note];
  }

  // Different ornaments based on context
  const ornamentType = Math.random();

  if (ornamentType < 0.3 && note.duration >= 0.5) {
    // Trill (rapid alternation with upper neighbor)
    const trillCount = Math.floor(note.duration / 0.125);
    const notes: Note[] = [];
    for (let i = 0; i < trillCount; i++) {
      notes.push({
        degree: i % 2 === 0 ? note.degree : note.degree + 1,
        duration: 0.125,
        velocity: note.velocity * (i % 2 === 0 ? 1 : 0.85),
        articulation: 'legato',
      });
    }
    return notes;
  }

  if (ornamentType < 0.6 && prevDegree !== null) {
    // Mordent (quick lower/upper neighbor)
    return [
      { ...note, duration: note.duration * 0.7 },
      { degree: note.degree - 1, duration: note.duration * 0.15, velocity: note.velocity * 0.8, articulation: 'legato' },
      { degree: note.degree, duration: note.duration * 0.15, velocity: note.velocity * 0.9, articulation: 'legato' },
    ];
  }

  if (ornamentType < 0.8 && prevDegree !== null) {
    // Passing tone from previous note
    const direction = note.degree > prevDegree ? 1 : -1;
    return [
      { degree: prevDegree + direction, duration: note.duration * 0.25, velocity: note.velocity * 0.7, articulation: 'legato' },
      { ...note, duration: note.duration * 0.75 },
    ];
  }

  // No ornamentation applied
  return [note];
}

/**
 * Generate scheduled notes for a voice
 */
function generateVoiceNotes(
  voice: VoiceState,
  material: Note[],
  startBeat: number,
  tempo: number,
  params: MusicHyperparameters
): ScheduledNote[] {
  const beatDuration = 60 / tempo;
  const notes: ScheduledNote[] = [];

  let currentBeat = startBeat;
  let prevDegree: number | null = null;

  for (const note of material) {
    // Apply augmentation/diminution based on params
    const rhythmMult = voice.rhythmMultiplier * (1 + (params.tension - 0.5) * 0.3);
    // Note: duration computed inline in note generation below

    // Apply ornamentation
    const ornamentedNotes = applyOrnamentation(note, params, prevDegree);

    for (const ornNote of ornamentedNotes) {
      const frequency = degreeToFreq(ornNote.degree, voice.octaveOffset);

      notes.push({
        frequency,
        startTime: currentBeat * beatDuration,
        duration: ornNote.duration * rhythmMult * beatDuration,
        velocity: ornNote.velocity * (0.7 + params.intensity * 0.3),
        articulation: ornNote.articulation,
        voiceName: voice.name,
      });

      currentBeat += ornNote.duration * rhythmMult;
      prevDegree = ornNote.degree;
    }
  }

  return notes;
}

/**
 * Main update function - advances the fugue state and generates notes
 */
export function updateFugueState(
  state: FugueState,
  _currentTime: number, // Reserved for future timing sync
  deltaTime: number
): { newState: FugueState; newNotes: ScheduledNote[] } {
  const beatDuration = 60 / state.tempo;
  const deltaBeat = deltaTime / beatDuration;

  let newState = { ...state };
  const newNotes: ScheduledNote[] = [];

  // Advance beat position
  newState.currentBeat += deltaBeat;
  newState.phaseProgress += deltaBeat / newState.phaseDuration;

  // Check for phase transition
  if (newState.phaseProgress >= 1.0) {
    // Sample next phase from Markov chain
    const nextPhase = sampleNextPhase(newState.phase, newState.transitionMatrix);

    // Determine phase duration based on phase type and params
    let phaseDuration = 4; // Default 4 beats
    switch (nextPhase) {
      case 'exposition':
        phaseDuration = 8 + Math.floor(newState.params.voiceDensity * 8);
        break;
      case 'stretto':
        phaseDuration = 4 + Math.floor(newState.params.intensity * 4);
        break;
      case 'pedal':
        phaseDuration = 8 + Math.floor(newState.params.tension * 8);
        break;
      case 'silence':
        phaseDuration = 2 + Math.floor((1 - newState.params.momentum) * 4);
        break;
      default:
        phaseDuration = 4 + Math.floor(Math.random() * 4);
    }

    newState = {
      ...newState,
      phase: nextPhase,
      phaseProgress: 0,
      phaseDuration,
    };

    // Assign material to voices for new phase
    const activeCount = getActiveVoiceCount(newState.params);
    const voiceNames: VoiceName[] = ['soprano', 'alto', 'tenor', 'bass'];

    // Activate voices based on density
    let voiceIndex = 0;
    for (const name of voiceNames) {
      const voice = newState.voices[name];
      const shouldBeActive = voiceIndex < activeCount;

      if (shouldBeActive && nextPhase !== 'silence') {
        const { notes, material } = getMaterialForPhase(
          nextPhase,
          name,
          voiceIndex,
          newState.params
        );

        // Apply stretto offset (voices enter at different times)
        const strettoOffset = nextPhase === 'stretto'
          ? voiceIndex * (1 + (1 - newState.params.intensity) * 2)
          : voiceIndex * 4; // Standard 4-beat entries in exposition

        // Generate notes for this voice
        const voiceNotes = generateVoiceNotes(
          voice,
          notes,
          newState.currentBeat + strettoOffset,
          newState.tempo,
          newState.params
        );

        newNotes.push(...voiceNotes);

        newState.voices[name] = {
          ...voice,
          active: true,
          currentMaterial: material,
          noteIndex: 0,
          scheduledNotes: voiceNotes,
        };
      } else {
        newState.voices[name] = {
          ...voice,
          active: false,
          currentMaterial: 'rest',
          scheduledNotes: [],
        };
      }

      voiceIndex++;
    }
  }

  return { newState, newNotes };
}

// =============================================================================
// CHORD PROGRESSION SYSTEM
// =============================================================================

/**
 * Common chord progressions in C# minor for different moods
 */
export const CHORD_PROGRESSIONS = {
  // Standard minor key progression
  standard: ['i', 'iv', 'VII', 'III', 'VI', 'ii', 'V', 'i'] as const,

  // Darker, more tense
  dark: ['i', 'viio', 'III', 'iv', 'i', 'V', 'VI', 'V'] as const,

  // Building tension
  tension: ['i', 'iv', 'V', 'V', 'V', 'V', 'V', 'i'] as const,

  // Baroque-style circle of fifths
  baroque: ['i', 'iv', 'VII', 'III', 'VI', 'ii', 'V', 'i'] as const,

  // Chromatic descent
  chromatic: ['i', 'VII', 'VI', 'v', 'iv', 'III', 'ii', 'i'] as const,
};

/**
 * Get next chord based on current state and hyperparameters
 */
export function getNextChord(
  currentChord: keyof typeof CSHARP_MINOR.chords,
  params: MusicHyperparameters
): keyof typeof CSHARP_MINOR.chords {
  // Select progression based on tension
  let progression: readonly (keyof typeof CSHARP_MINOR.chords)[];
  if (params.tension > 0.7) {
    progression = CHORD_PROGRESSIONS.tension;
  } else if (params.tension > 0.4) {
    progression = CHORD_PROGRESSIONS.dark;
  } else {
    progression = CHORD_PROGRESSIONS.standard;
  }

  // Find current position and move to next
  const currentIndex = progression.indexOf(currentChord as any);
  const nextIndex = (currentIndex + 1) % progression.length;

  // Add some randomness based on chaos level
  if (Math.random() < params.chaosLevel) {
    return progression[Math.floor(Math.random() * progression.length)];
  }

  return progression[nextIndex];
}

// =============================================================================
// WEB AUDIO INTEGRATION
// =============================================================================

/**
 * Synthesizer voice for playing notes
 */
export class FugueVoice {
  private ctx: AudioContext;
  private masterGain: GainNode;
  private activeOscillators: Map<number, { osc: OscillatorNode; gain: GainNode }> = new Map();

  constructor(ctx: AudioContext, masterGain: GainNode) {
    this.ctx = ctx;
    this.masterGain = masterGain;
  }

  /**
   * Play a scheduled note
   *
   * TIMBRE IMPROVEMENTS (2025-01):
   * - Warmer sound: sine+triangle blend instead of harsh sawtooth
   * - Gentler attacks: longer attack times reduce "crash" sound
   * - Lower filter cutoff: removes harsh high frequencies
   * - More consonant: slight detuning for chorus warmth without dissonance
   */
  playNote(note: ScheduledNote, baseTime: number): void {
    // Validate all numeric values to prevent AudioParam errors
    if (!Number.isFinite(note.frequency) || note.frequency <= 0) {
      console.warn('playNote: skipping note with invalid frequency', note.frequency);
      return;
    }
    if (!Number.isFinite(note.startTime) || !Number.isFinite(note.duration) || note.duration <= 0) {
      console.warn('playNote: skipping note with invalid timing', note.startTime, note.duration);
      return;
    }
    if (!Number.isFinite(note.velocity)) {
      note.velocity = 0.5; // Default velocity
    }
    if (!Number.isFinite(baseTime)) {
      console.warn('playNote: invalid baseTime', baseTime);
      return;
    }

    const startTime = baseTime + note.startTime;
    const endTime = startTime + note.duration;

    // Additional timing validation
    if (!Number.isFinite(startTime) || !Number.isFinite(endTime) || endTime <= startTime) {
      console.warn('playNote: invalid computed timing', startTime, endTime);
      return;
    }

    // === WARM TIMBRE: Sine + Triangle blend (no harsh sawtooth) ===
    // Primary oscillator: sine wave for pure, warm fundamental
    const oscSine = this.ctx.createOscillator();
    oscSine.type = 'sine';
    oscSine.frequency.setValueAtTime(note.frequency, startTime);

    // Secondary oscillator: triangle for gentle harmonic content
    const oscTriangle = this.ctx.createOscillator();
    oscTriangle.type = 'triangle';
    oscTriangle.frequency.setValueAtTime(note.frequency, startTime);
    // Slight detune for warmth/chorus effect (3 cents = subtle)
    oscTriangle.detune.setValueAtTime(3, startTime);

    // Mix gains: 60% sine (warm) + 40% triangle (gentle harmonics)
    const sineGain = this.ctx.createGain();
    sineGain.gain.value = 0.6;
    const triangleGain = this.ctx.createGain();
    triangleGain.gain.value = 0.4;

    // Add gentle vibrato for longer notes (slower, subtler than before)
    if (note.duration > 0.4) {
      const vibratoDepth = 2; // Hz (reduced from 3)
      const vibratoRate = 4;  // Hz (reduced from 5)
      const lfo = this.ctx.createOscillator();
      const lfoGain = this.ctx.createGain();
      lfo.frequency.value = vibratoRate;
      lfoGain.gain.value = vibratoDepth;
      lfo.connect(lfoGain);
      lfoGain.connect(oscSine.frequency);
      lfoGain.connect(oscTriangle.frequency);
      // Delayed vibrato onset for more natural sound
      lfo.start(startTime + 0.15);
      lfo.stop(endTime);
    }

    // === GENTLER ENVELOPE: Longer attacks, smoother release ===
    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0, startTime);

    // Attack times increased by ~2x for smoother onset (reduces "crash")
    const attackTime = note.articulation === 'staccato' ? 0.025 :
                       note.articulation === 'accent' ? 0.015 :
                       0.04; // Much gentler default attack
    gain.gain.linearRampToValueAtTime(note.velocity * 0.28, startTime + attackTime);

    // Sustain and release - longer release for smoother decay
    const sustainLevel = note.articulation === 'staccato' ? 0.5 : 0.85;
    const releaseStart = note.articulation === 'staccato'
      ? startTime + note.duration * 0.5
      : endTime - 0.08; // Slightly earlier release start for smoother fade

    gain.gain.setValueAtTime(note.velocity * 0.28 * sustainLevel, releaseStart);
    // Longer release time for smoother decay
    gain.gain.exponentialRampToValueAtTime(0.001, endTime + 0.05);

    // === WARMER FILTER: Lower cutoff, gentler resonance ===
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    // Reduced cutoff: 1200-2700 Hz (was 2000-5000 Hz) - removes harsh highs
    filter.frequency.setValueAtTime(1200 + note.velocity * 1500, startTime);
    filter.Q.value = 0.7; // Lower Q = less resonant peak = smoother

    // Connect: both oscillators through mixer to filter to envelope
    oscSine.connect(sineGain);
    oscTriangle.connect(triangleGain);
    sineGain.connect(filter);
    triangleGain.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);

    oscSine.start(startTime);
    oscTriangle.start(startTime);
    oscSine.stop(endTime + 0.15);
    oscTriangle.stop(endTime + 0.15);

    // Cleanup
    const noteId = Math.random();
    this.activeOscillators.set(noteId, { osc: oscSine, gain });

    oscSine.onended = () => {
      this.activeOscillators.delete(noteId);
    };
  }

  /**
   * Stop all active notes
   */
  stopAll(): void {
    const now = this.ctx.currentTime;
    for (const { osc, gain } of this.activeOscillators.values()) {
      gain.gain.cancelScheduledValues(now);
      gain.gain.setValueAtTime(gain.gain.value, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
      osc.stop(now + 0.15);
    }
    this.activeOscillators.clear();
  }
}

/**
 * Main orchestrator for the procedural fugue system
 */
export class ProceduralFugueEngine {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private compressor: DynamicsCompressorNode | null = null;
  private reverb: ConvolverNode | null = null;

  private voices: Map<VoiceName, FugueVoice> = new Map();
  private state: FugueState;
  private isRunning = false;

  constructor(initialParams: MusicHyperparameters = DEFAULT_HYPERPARAMETERS) {
    this.state = createFugueState(initialParams);
  }

  /**
   * Start the audio engine
   */
  async start(): Promise<boolean> {
    try {
      this.ctx = new AudioContext();

      // Master output chain
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.value = 0.4;

      this.compressor = this.ctx.createDynamicsCompressor();
      this.compressor.threshold.value = -20;
      this.compressor.knee.value = 10;
      this.compressor.ratio.value = 4;

      // Create reverb (simple delay-based for now)
      this.reverb = await this.createReverb();

      // Connect chain
      this.masterGain.connect(this.compressor);
      this.compressor.connect(this.ctx.destination);

      // WARMTH IMPROVEMENT: Increased reverb for richer, more pleasant sound
      if (this.reverb) {
        const reverbGain = this.ctx.createGain();
        reverbGain.gain.value = 0.35; // Increased from 0.2 for warmer ambiance
        this.masterGain.connect(this.reverb);
        this.reverb.connect(reverbGain);
        reverbGain.connect(this.ctx.destination);
      }

      // Create voices
      for (const name of ['soprano', 'alto', 'tenor', 'bass'] as VoiceName[]) {
        this.voices.set(name, new FugueVoice(this.ctx, this.masterGain));
      }

      this.isRunning = true;

      return true;
    } catch (e) {
      console.error('Failed to start ProceduralFugueEngine:', e);
      return false;
    }
  }

  /**
   * Create warm reverb using convolution
   *
   * WARMTH IMPROVEMENTS (2025-01):
   * - Longer reverb tail (2.5s) for cathedral-like ambiance
   * - Smoother exponential decay (1.5 power instead of 2)
   * - High-frequency damping for warmer, less harsh tail
   * - Reduced noise intensity for cleaner reverb
   */
  private async createReverb(): Promise<ConvolverNode | null> {
    if (!this.ctx) return null;

    try {
      const reverb = this.ctx.createConvolver();

      // Generate impulse response
      const sampleRate = this.ctx.sampleRate;
      const length = Math.floor(sampleRate * 2.5); // 2.5 second reverb (increased for warmth)
      const impulse = this.ctx.createBuffer(2, length, sampleRate);

      for (let channel = 0; channel < 2; channel++) {
        const data = impulse.getChannelData(channel);
        for (let i = 0; i < length; i++) {
          const progress = i / length;

          // WARMTH: Smoother exponential decay (1.5 power instead of 2)
          const decay = Math.pow(1 - progress, 1.5);

          // WARMTH: High-frequency damping - apply lowpass filter effect
          // Later samples have less high-frequency content (warmer tail)
          const hfDamping = 1 - progress * 0.6; // Gradually reduce HF

          // Reduced noise amplitude for cleaner reverb
          const noise = (Math.random() * 2 - 1) * 0.8;

          data[i] = noise * decay * hfDamping;
        }
      }

      reverb.buffer = impulse;
      return reverb;
    } catch (e) {
      console.warn('Failed to create reverb:', e);
      return null;
    }
  }

  /**
   * Stop the engine
   */
  stop(): void {
    this.isRunning = false;

    for (const voice of this.voices.values()) {
      voice.stopAll();
    }

    if (this.ctx) {
      this.ctx.close();
      this.ctx = null;
    }
  }

  /**
   * Update hyperparameters from game state
   */
  setHyperparameters(params: Partial<MusicHyperparameters>): void {
    this.state = updateHyperparameters(this.state, params);
  }

  /**
   * Main update loop - call this each frame
   */
  update(deltaTime: number): void {
    if (!this.isRunning || !this.ctx) return;

    const currentTime = this.ctx.currentTime;

    // Update fugue state and get new notes to schedule
    const { newState, newNotes } = updateFugueState(
      this.state,
      currentTime,
      deltaTime
    );

    this.state = newState;

    // Schedule notes for each voice
    for (const note of newNotes) {
      const voice = this.voices.get(note.voiceName);
      if (voice) {
        voice.playNote(note, currentTime);
      }
    }
  }

  /**
   * Get current state for debugging/visualization
   */
  getState(): FugueState {
    return this.state;
  }

  /**
   * Check if engine is active
   */
  isActive(): boolean {
    return this.isRunning;
  }

  /**
   * Set master volume
   */
  setVolume(volume: number): void {
    if (this.masterGain) {
      this.masterGain.gain.setValueAtTime(
        Math.max(0, Math.min(1, volume)) * 0.4,
        this.ctx?.currentTime || 0
      );
    }
  }
}

// =============================================================================
// GAME STATE TO HYPERPARAMETERS MAPPING
// =============================================================================

/**
 * Convert game state to music hyperparameters
 */
export function gameStateToHyperparameters(
  playerHealth: number,      // 0-1
  enemyCount: number,
  waveNumber: number,
  recentKills: number,
  comboCount: number,
  ballPhase: 'none' | 'forming' | 'sphere' | 'silence' | 'constrict' | 'death'
): MusicHyperparameters {
  // Base intensity from enemy count and wave
  let intensity = Math.min(1, (enemyCount / 30) + (waveNumber / 20));

  // Tension from health and ball phase
  let tension = 1 - playerHealth;
  if (ballPhase !== 'none') {
    tension = Math.max(tension, 0.7);
    if (ballPhase === 'constrict') tension = 0.9;
    if (ballPhase === 'death') tension = 1.0;
  }

  // Momentum from recent activity
  const momentum = Math.min(1, (recentKills / 10) + (comboCount / 5));

  // Voice density scales with wave progression
  const voiceDensity = Math.min(1, 0.3 + waveNumber * 0.1);

  // Ornamentation increases as player does well
  const ornamentation = Math.min(1, comboCount * 0.15 + (playerHealth > 0.7 ? 0.2 : 0));

  // Chaos when things get hectic
  const chaosLevel = ballPhase !== 'none' ? 0.4 : Math.min(0.5, enemyCount / 50);

  return {
    intensity,
    tension,
    momentum,
    voiceDensity,
    registralSpread: 0.5 + tension * 0.3,
    ornamentation,
    chaosLevel,
  };
}

// =============================================================================
// SINGLETON & EXPORTS
// =============================================================================

let fugueEngineInstance: ProceduralFugueEngine | null = null;

export function getProceduralFugueEngine(): ProceduralFugueEngine {
  if (!fugueEngineInstance) {
    fugueEngineInstance = new ProceduralFugueEngine();
  }
  return fugueEngineInstance;
}

export async function startProceduralFugue(): Promise<boolean> {
  const engine = getProceduralFugueEngine();
  return engine.start();
}

export function stopProceduralFugue(): void {
  if (fugueEngineInstance) {
    fugueEngineInstance.stop();
  }
}

export default ProceduralFugueEngine;
