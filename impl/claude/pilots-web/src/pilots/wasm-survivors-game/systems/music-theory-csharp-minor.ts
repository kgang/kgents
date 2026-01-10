/**
 * C# Minor Musical Framework
 *
 * A dark, dramatic, introspective harmonic palette for WASM Survivors.
 *
 * "Beethoven's Moonlight Sonata key - the color of midnight contemplation."
 *
 * Properties:
 * - Scale: C#, D#, E, F#, G#, A, B, C#
 * - Relative major: E major
 * - Key signature: 4 sharps (F#, C#, G#, D#)
 * - Parallel major: C# major (7 sharps - enharmonic to Db major)
 * - Character: Dark, dramatic, introspective, powerful
 *
 * Historical usage:
 * - Beethoven: Piano Sonata No. 14 "Moonlight" (Op. 27, No. 2)
 * - Chopin: Fantaisie-Impromptu (Op. 66)
 * - Rachmaninoff: Prelude in C# minor (Op. 3, No. 2)
 *
 * @see https://en.wikipedia.org/wiki/C-sharp_minor
 */

// =============================================================================
// PHYSICAL CONSTANTS
// =============================================================================

/**
 * A4 = 440 Hz (ISO 16 standard pitch)
 * All frequencies derived via equal temperament: f = 440 * 2^((n-69)/12)
 * where n is the MIDI note number
 */
export const A4_HZ = 440;

/**
 * Semitone ratio in equal temperament
 * Each semitone = 2^(1/12) = 1.0594630943592953
 */
export const SEMITONE_RATIO = Math.pow(2, 1 / 12);

/**
 * Convert MIDI note number to frequency
 * MIDI 69 = A4 = 440 Hz
 */
export function midiToFreq(midi: number): number {
  return A4_HZ * Math.pow(2, (midi - 69) / 12);
}

/**
 * Convert frequency to nearest MIDI note
 */
export function freqToMidi(freq: number): number {
  return Math.round(12 * Math.log2(freq / A4_HZ) + 69);
}

/**
 * Transpose frequency by semitones
 */
export function transpose(freq: number, semitones: number): number {
  return freq * Math.pow(SEMITONE_RATIO, semitones);
}

/**
 * Transpose frequency by octaves
 */
export function transposeOctave(freq: number, octaves: number): number {
  return freq * Math.pow(2, octaves);
}

// =============================================================================
// C# MINOR SCALE FREQUENCIES
// =============================================================================

/**
 * C# Minor Natural Scale - All Octaves
 *
 * Scale degrees:
 * 1 (i)   - C# - Tonic (root, home)
 * 2 (ii)  - D# - Supertonic
 * 3 (III) - E  - Mediant (relative major)
 * 4 (iv)  - F# - Subdominant
 * 5 (v/V) - G# - Dominant
 * 6 (VI)  - A  - Submediant
 * 7 (VII) - B  - Subtonic (natural minor)
 * 8 (i)   - C# - Octave
 */
export const CS_MINOR = {
  // Octave 1 (very low, sub-bass - use sparingly)
  Cs1: 34.65,   // C#1 - MIDI 25
  Ds1: 38.89,   // D#1 - MIDI 27
  E1: 41.20,    // E1  - MIDI 28
  Fs1: 46.25,   // F#1 - MIDI 30
  Gs1: 51.91,   // G#1 - MIDI 32
  A1: 55.00,    // A1  - MIDI 33
  B1: 61.74,    // B1  - MIDI 35

  // Octave 2 (bass register)
  Cs2: 69.30,   // C#2 - MIDI 37 - Deep bass root
  Ds2: 77.78,   // D#2 - MIDI 39
  E2: 82.41,    // E2  - MIDI 40 - Relative major root
  Fs2: 92.50,   // F#2 - MIDI 42
  Gs2: 103.83,  // G#2 - MIDI 44 - Dominant bass
  A2: 110.00,   // A2  - MIDI 45
  B2: 123.47,   // B2  - MIDI 47

  // Octave 3 (low-mid register) - PRIMARY BASS RANGE
  Cs3: 138.59,  // C#3 - MIDI 49 - Main bass root
  Ds3: 155.56,  // D#3 - MIDI 51
  E3: 164.81,   // E3  - MIDI 52
  Fs3: 185.00,  // F#3 - MIDI 54 - Subdominant bass
  Gs3: 207.65,  // G#3 - MIDI 56 - Dominant
  A3: 220.00,   // A3  - MIDI 57 - A below middle C
  B3: 246.94,   // B3  - MIDI 59

  // Octave 4 (middle register) - PRIMARY MELODIC RANGE
  Cs4: 277.18,  // C#4 - MIDI 61 - Main melodic root
  Ds4: 311.13,  // D#4 - MIDI 63
  E4: 329.63,   // E4  - MIDI 64 - Relative major
  Fs4: 369.99,  // F#4 - MIDI 66 - Subdominant
  Gs4: 415.30,  // G#4 - MIDI 68 - Dominant
  A4: 440.00,   // A4  - MIDI 69 - Concert A
  B4: 493.88,   // B4  - MIDI 71

  // Octave 5 (high register) - BRIGHT/SHIMMER RANGE
  Cs5: 554.37,  // C#5 - MIDI 73 - High root
  Ds5: 622.25,  // D#5 - MIDI 75
  E5: 659.26,   // E5  - MIDI 76
  Fs5: 739.99,  // F#5 - MIDI 78
  Gs5: 830.61,  // G#5 - MIDI 80
  A5: 880.00,   // A5  - MIDI 81
  B5: 987.77,   // B5  - MIDI 83

  // Octave 6 (very high - sparkle/chime)
  Cs6: 1108.73, // C#6 - MIDI 85
  Ds6: 1244.51, // D#6 - MIDI 87
  E6: 1318.51,  // E6  - MIDI 88
  Fs6: 1479.98, // F#6 - MIDI 90
  Gs6: 1661.22, // G#6 - MIDI 92
  A6: 1760.00,  // A6  - MIDI 93
  B6: 1975.53,  // B6  - MIDI 95
} as const;

/**
 * Scale degrees as arrays for procedural selection
 */
export const CS_MINOR_SCALE_DEGREES = {
  // Full octave (8 notes including octave)
  octave3: [CS_MINOR.Cs3, CS_MINOR.Ds3, CS_MINOR.E3, CS_MINOR.Fs3, CS_MINOR.Gs3, CS_MINOR.A3, CS_MINOR.B3, CS_MINOR.Cs4],
  octave4: [CS_MINOR.Cs4, CS_MINOR.Ds4, CS_MINOR.E4, CS_MINOR.Fs4, CS_MINOR.Gs4, CS_MINOR.A4, CS_MINOR.B4, CS_MINOR.Cs5],
  octave5: [CS_MINOR.Cs5, CS_MINOR.Ds5, CS_MINOR.E5, CS_MINOR.Fs5, CS_MINOR.Gs5, CS_MINOR.A5, CS_MINOR.B5, CS_MINOR.Cs6],

  // Bass range (playable bass notes)
  bass: [CS_MINOR.Cs2, CS_MINOR.Cs3, CS_MINOR.E2, CS_MINOR.E3, CS_MINOR.Gs2, CS_MINOR.Gs3],

  // Melodic range (most useful for melodies)
  melodic: [CS_MINOR.Cs4, CS_MINOR.Ds4, CS_MINOR.E4, CS_MINOR.Fs4, CS_MINOR.Gs4, CS_MINOR.A4, CS_MINOR.B4, CS_MINOR.Cs5],

  // Pentatonic minor (C#, E, F#, G#, B) - always sounds good
  pentatonic: [CS_MINOR.Cs4, CS_MINOR.E4, CS_MINOR.Fs4, CS_MINOR.Gs4, CS_MINOR.B4],
  pentatonicBass: [CS_MINOR.Cs3, CS_MINOR.E3, CS_MINOR.Fs3, CS_MINOR.Gs3, CS_MINOR.B3],

  // Root notes across octaves
  roots: [CS_MINOR.Cs1, CS_MINOR.Cs2, CS_MINOR.Cs3, CS_MINOR.Cs4, CS_MINOR.Cs5, CS_MINOR.Cs6],
} as const;

// =============================================================================
// HARMONIC INTERVALS
// =============================================================================

/**
 * Musical intervals as frequency ratios
 * These are Just Intonation ratios (pure harmonics)
 * For equal temperament, use the semitone-based transpose() function
 */
export const INTERVALS = {
  // Perfect consonances (most stable)
  unison: 1,                    // 0 semitones - same note
  octave: 2,                    // 12 semitones - perfect unity
  perfectFifth: 3 / 2,          // 7 semitones (1.5) - POWER
  perfectFourth: 4 / 3,         // 5 semitones (1.333) - stable

  // Imperfect consonances (pleasant)
  majorThird: 5 / 4,            // 4 semitones (1.25) - bright, happy
  minorThird: 6 / 5,            // 3 semitones (1.2) - sad, dark
  majorSixth: 5 / 3,            // 9 semitones (1.667) - warm
  minorSixth: 8 / 5,            // 8 semitones (1.6) - bittersweet

  // Dissonances (tension)
  minorSecond: 16 / 15,         // 1 semitone (1.067) - grinding pain
  majorSecond: 9 / 8,           // 2 semitones (1.125) - mild tension
  tritone: Math.sqrt(2),        // 6 semitones (1.414) - DREAD, devil's interval
  minorSeventh: 9 / 5,          // 10 semitones (1.8) - unresolved, jazzy
  majorSeventh: 15 / 8,         // 11 semitones (1.875) - longing

  // Equal temperament tritone (exact)
  tritoneET: Math.pow(2, 6 / 12), // 1.4142... - equal temperament tritone
} as const;

/**
 * Categorized intervals for procedural sound design
 */
export const POWER_INTERVALS = [
  INTERVALS.unison,
  INTERVALS.perfectFifth,
  INTERVALS.octave,
] as const;

export const DARK_INTERVALS = [
  INTERVALS.minorThird,
  INTERVALS.minorSixth,
  INTERVALS.minorSeventh,
] as const;

export const TENSION_INTERVALS = [
  INTERVALS.minorSecond,
  INTERVALS.tritone,
  INTERVALS.majorSeventh,
] as const;

export const RESOLUTION_INTERVALS = [
  INTERVALS.perfectFifth,
  INTERVALS.perfectFourth,
  INTERVALS.majorThird,
] as const;

// =============================================================================
// CHORD DEFINITIONS
// =============================================================================

/**
 * Chord voicings in C# minor
 *
 * Roman numeral analysis:
 * i   = C#m  (C#-E-G#)    - Tonic minor
 * ii* = D#dim (D#-F#-A)   - Diminished supertonic
 * III = E    (E-G#-B)     - Relative major
 * iv  = F#m  (F#-A-C#)    - Subdominant minor
 * v   = G#m  (G#-B-D#)    - Minor dominant (natural minor)
 * V   = G#   (G#-B#-D#)   - Major dominant (harmonic minor)
 * VI  = A    (A-C#-E)     - Submediant major
 * VII = B    (B-D#-F#)    - Subtonic major
 * vii* = B#dim (B#-D#-F##) - Diminished leading tone (harmonic minor)
 */

/**
 * Core chord frequencies (octave 3-4 voicings)
 */
export const CHORDS = {
  // i - Tonic: C# minor (home, grounded, dark power)
  i: {
    root: CS_MINOR.Cs3,
    frequencies: [CS_MINOR.Cs3, CS_MINOR.E3, CS_MINOR.Gs3],
    extension: [CS_MINOR.Cs3, CS_MINOR.E3, CS_MINOR.Gs3, CS_MINOR.B3], // add7
    character: 'home, grounded, dark confidence',
  },

  // iv - Subdominant: F# minor (movement, melancholy)
  iv: {
    root: CS_MINOR.Fs3,
    frequencies: [CS_MINOR.Fs3, CS_MINOR.A3, CS_MINOR.Cs4],
    extension: [CS_MINOR.Fs3, CS_MINOR.A3, CS_MINOR.Cs4, CS_MINOR.E4], // add7
    character: 'movement, deepening emotion, momentum',
  },

  // V - Dominant: G# major (tension seeking resolution)
  V: {
    root: CS_MINOR.Gs3,
    // G# major = G#, B#(C), D#
    frequencies: [CS_MINOR.Gs3, transpose(CS_MINOR.Gs3, 4), CS_MINOR.Ds4],
    extension: [CS_MINOR.Gs3, transpose(CS_MINOR.Gs3, 4), CS_MINOR.Ds4, CS_MINOR.Fs4], // dominant 7
    character: 'tension, yearning for home, powerful pull',
  },

  // v - Minor dominant: G# minor (softer dominant, natural minor)
  v: {
    root: CS_MINOR.Gs3,
    frequencies: [CS_MINOR.Gs3, CS_MINOR.B3, CS_MINOR.Ds4],
    character: 'gentle tension, introspective',
  },

  // VI - Submediant: A major (bright contrast, hope)
  VI: {
    root: CS_MINOR.A3,
    frequencies: [CS_MINOR.A3, transpose(CS_MINOR.A3, 4), CS_MINOR.E4],
    character: 'brightness within darkness, bittersweet hope',
  },

  // III - Mediant: E major (relative major, resolution)
  III: {
    root: CS_MINOR.E3,
    frequencies: [CS_MINOR.E3, CS_MINOR.Gs3, CS_MINOR.B3],
    character: 'relative major, light within shadow, resolution',
  },

  // VII - Subtonic: B major (bright, dramatic)
  VII: {
    root: CS_MINOR.B3,
    frequencies: [CS_MINOR.B3, CS_MINOR.Ds4, CS_MINOR.Fs4],
    character: 'dramatic lift, anticipation',
  },

  // ii* - Diminished: D# diminished (unstable, transitional)
  iio: {
    root: CS_MINOR.Ds3,
    frequencies: [CS_MINOR.Ds3, CS_MINOR.Fs3, CS_MINOR.A3],
    character: 'unstable, desperate, seeking resolution',
  },

  // Neapolitan (bII) - D major (transcendence, otherworldly)
  N: {
    root: transpose(CS_MINOR.Cs3, 1), // D natural
    frequencies: [
      transpose(CS_MINOR.Cs3, 1),     // D
      transpose(CS_MINOR.Cs3, 5),     // F#
      transpose(CS_MINOR.Cs3, 8),     // A
    ],
    character: 'transcendence, otherworldly, death/rebirth',
  },

  // Picardy Third - C# major (triumph, transcendence)
  I: {
    root: CS_MINOR.Cs3,
    frequencies: [
      CS_MINOR.Cs3,
      transpose(CS_MINOR.Cs3, 4),     // E# (F natural)
      CS_MINOR.Gs3,
    ],
    character: 'triumph over darkness, transcendent joy',
  },
} as const;

// =============================================================================
// GAME PHASE CHORD PROGRESSIONS
// =============================================================================

/**
 * Emotional mapping for game phases
 * Each phase has associated chords, intervals, and sonic character
 */
export const PHASE_HARMONICS = {
  /**
   * POWER PHASE - Dominant, confident
   * Player is strong, enemies are weak
   * Chord: i (C#m) - grounded in home key
   * Character: Dark confidence, controlled power
   */
  power: {
    primaryChord: CHORDS.i,
    secondaryChord: CHORDS.V,
    progression: [CHORDS.i, CHORDS.V, CHORDS.i],
    intervals: POWER_INTERVALS,
    rootNote: CS_MINOR.Cs3,
    character: 'confident, grounded, dark mastery',
  },

  /**
   * FLOW PHASE - Momentum, engagement
   * Player is in the zone, rhythmic gameplay
   * Chord: iv-i (F#m to C#m) - gentle movement
   * Character: Melancholic momentum, graceful motion
   */
  flow: {
    primaryChord: CHORDS.iv,
    secondaryChord: CHORDS.i,
    progression: [CHORDS.iv, CHORDS.i, CHORDS.iv, CHORDS.i],
    intervals: [...DARK_INTERVALS, INTERVALS.perfectFifth],
    rootNote: CS_MINOR.Fs3,
    character: 'momentum, melancholic grace, engaged focus',
  },

  /**
   * CRISIS PHASE - Tension building
   * Player is in danger, health low
   * Chord: vii*-V (diminished to dominant) - building tension
   * Character: Desperate, unstable, seeking escape
   */
  crisis: {
    primaryChord: CHORDS.iio,
    secondaryChord: CHORDS.V,
    progression: [CHORDS.iio, CHORDS.V, CHORDS.iio, CHORDS.V],
    intervals: TENSION_INTERVALS,
    rootNote: CS_MINOR.Ds3,
    character: 'desperate, unstable, heart-pounding',
  },

  /**
   * TRAGEDY PHASE - Death, transcendence
   * Player has died, dignified end
   * Chord: Neapolitan (D major) - otherworldly transcendence
   * Or Picardy Third (C# major) - triumph through death
   * Character: Transcendent, peaceful darkness
   */
  tragedy: {
    primaryChord: CHORDS.N,
    secondaryChord: CHORDS.I,
    progression: [CHORDS.i, CHORDS.N, CHORDS.V, CHORDS.I],
    intervals: [INTERVALS.minorThird, INTERVALS.perfectFifth, INTERVALS.majorThird],
    rootNote: CS_MINOR.Cs3,
    character: 'transcendence, dignified end, peaceful release',
  },

  /**
   * DREAD PHASE - THE BALL forming
   * Ultimate danger, primal fear
   * Chord: Tritone relationships - maximum instability
   * Character: Unstable, primal dread, inevitable doom
   */
  dread: {
    primaryChord: CHORDS.iio,
    secondaryChord: {
      // Tritone substitute chord (G natural, enharmonic)
      root: transpose(CS_MINOR.Cs4, 6), // G natural
      frequencies: [
        transpose(CS_MINOR.Cs4, 6),      // G
        transpose(CS_MINOR.Cs4, 10),     // B
        transpose(CS_MINOR.Cs4, 13),     // D#
      ],
      character: 'ultimate instability, tritone dread',
    },
    progression: [CHORDS.i, CHORDS.iio],
    intervals: [INTERVALS.tritone, INTERVALS.minorSecond],
    rootNote: CS_MINOR.Cs3,
    character: 'primal dread, inevitable doom, THE BALL',
  },
} as const;

// =============================================================================
// PROCEDURAL SOUND DESIGN INTERVALS
// =============================================================================

/**
 * Sound effect interval mappings
 * Each game event uses specific intervals for consistent emotional response
 */
export const SOUND_INTERVALS = {
  /**
   * KILL - Power, satisfaction
   * Perfect 5th (C# to G#) = stable power
   */
  kill: {
    primary: INTERVALS.perfectFifth,
    secondary: INTERVALS.octave,
    baseNote: CS_MINOR.Cs4,
    character: 'satisfying crunch, dark triumph',
  },

  /**
   * DAMAGE - Pain, warning
   * Minor 2nd (C# to D) = dissonant grinding
   */
  damage: {
    primary: INTERVALS.minorSecond,
    secondary: INTERVALS.tritone,
    baseNote: CS_MINOR.Cs3,
    character: 'grinding pain, urgent warning',
  },

  /**
   * LEVEL UP - Achievement, growth
   * Ascending C#m arpeggio with resolution
   */
  levelUp: {
    primary: INTERVALS.minorThird,
    secondary: INTERVALS.perfectFifth,
    baseNote: CS_MINOR.Cs4,
    arpeggio: [CS_MINOR.Cs4, CS_MINOR.E4, CS_MINOR.Gs4, CS_MINOR.Cs5],
    character: 'dark triumph, earned power',
  },

  /**
   * COMBO BUILDING - Escalating satisfaction
   * Rising scale degrees with increasing intensity
   */
  combo: {
    primary: INTERVALS.perfectFourth,
    secondary: INTERVALS.perfectFifth,
    scaleProgression: CS_MINOR_SCALE_DEGREES.pentatonic,
    character: 'escalating momentum, building power',
  },

  /**
   * GRAZE - Near miss, exciting danger
   * High register minor 6th - bittersweet close call
   */
  graze: {
    primary: INTERVALS.minorSixth,
    secondary: INTERVALS.minorThird,
    baseNote: CS_MINOR.Cs5,
    character: 'close call, exhilarating danger',
  },

  /**
   * XP COLLECT - Small reward
   * Quick chime on pentatonic
   */
  xp: {
    primary: INTERVALS.majorThird,
    secondary: INTERVALS.perfectFifth,
    baseNote: CS_MINOR.E5, // Relative major brightness
    character: 'small satisfaction, collected power',
  },

  /**
   * DASH - Movement, speed
   * Ascending whoosh through scale
   */
  dash: {
    primary: INTERVALS.perfectFourth,
    secondary: INTERVALS.perfectFifth,
    baseNote: CS_MINOR.Gs3,
    character: 'swift motion, controlled velocity',
  },

  /**
   * THE BALL - Ultimate dread
   * Tritone (C# to G natural) = devil's interval
   * This creates maximum instability and dread
   */
  theBall: {
    primary: INTERVALS.tritone,
    secondary: INTERVALS.minorSecond,
    baseNote: CS_MINOR.Cs2, // Deep, ominous bass
    character: 'primal dread, inevitable doom',
  },

  /**
   * DEATH - Dignified end
   * Descending to Neapolitan, resolving to Picardy
   */
  death: {
    primary: INTERVALS.minorThird,
    secondary: INTERVALS.perfectFifth,
    baseNote: CS_MINOR.Cs4,
    progression: [CS_MINOR.A4, CS_MINOR.E4, CS_MINOR.Cs4],
    character: 'dignified end, peaceful transcendence',
  },
} as const;

// =============================================================================
// BEETHOVEN TECHNIQUES
// =============================================================================

/**
 * Sforzando (sf, sfz) - Sudden accent
 * Sharp attack with immediate decay
 */
export const SFORZANDO = {
  attackTime: 0.005,      // 5ms attack (very fast)
  decayTime: 0.1,         // 100ms decay
  sustainLevel: 0.3,      // Drop to 30% after attack
  releaseTime: 0.2,       // 200ms release
  volumeMultiplier: 1.5,  // 50% louder than normal
} as const;

/**
 * Dramatic rest durations (silence as tension)
 * Used between phrases for dramatic effect
 */
export const DRAMATIC_RESTS = {
  breath: 0.15,           // 150ms - brief pause
  caesura: 0.3,           // 300ms - dramatic break
  lunga: 0.5,             // 500ms - long pause
  fermata: 0.8,           // 800ms - held silence
} as const;

/**
 * Tremolo configuration
 * Rapid oscillation for building intensity
 */
export const TREMOLO = {
  slowRate: 4,            // 4 Hz - gentle trembling
  mediumRate: 8,          // 8 Hz - building tension
  fastRate: 12,           // 12 Hz - intense vibration
  extremeRate: 16,        // 16 Hz - maximum intensity
  depth: 0.3,             // 30% volume modulation
} as const;

/**
 * Octave doubling for power
 * Play notes with their octave for fullness
 */
export function getOctaveDoubling(freq: number): number[] {
  return [freq, freq * 2];
}

/**
 * Power chord voicing (root + 5th + octave)
 */
export function getPowerChord(root: number): number[] {
  return [root, root * INTERVALS.perfectFifth, root * 2];
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Get random note from C# minor scale
 */
export function getRandomScaleNote(octave: 3 | 4 | 5 = 4): number {
  const scale = CS_MINOR_SCALE_DEGREES[`octave${octave}`];
  return scale[Math.floor(Math.random() * scale.length)];
}

/**
 * Get random note from C# minor pentatonic
 */
export function getRandomPentatonicNote(useBass: boolean = false): number {
  const scale = useBass
    ? CS_MINOR_SCALE_DEGREES.pentatonicBass
    : CS_MINOR_SCALE_DEGREES.pentatonic;
  return scale[Math.floor(Math.random() * scale.length)];
}

/**
 * Get scale degree by number (1-7, 8 = octave)
 * @param degree 1 = root (C#), 2 = D#, 3 = E, etc.
 * @param octave Base octave (3, 4, or 5)
 */
export function getScaleDegree(degree: number, octave: 3 | 4 | 5 = 4): number {
  const scale = CS_MINOR_SCALE_DEGREES[`octave${octave}`];
  // Normalize to 0-7 range
  const normalizedDegree = ((degree - 1) % 8 + 8) % 8;
  return scale[normalizedDegree];
}

/**
 * Get random interval from category
 */
export function getRandomPowerInterval(): number {
  return POWER_INTERVALS[Math.floor(Math.random() * POWER_INTERVALS.length)];
}

export function getRandomDarkInterval(): number {
  return DARK_INTERVALS[Math.floor(Math.random() * DARK_INTERVALS.length)];
}

export function getRandomTensionInterval(): number {
  return TENSION_INTERVALS[Math.floor(Math.random() * TENSION_INTERVALS.length)];
}

/**
 * Add humanization (slight randomness) to value
 */
export function humanize(value: number, variance: number = 0.05): number {
  return value * (1 + (Math.random() - 0.5) * 2 * variance);
}

/**
 * Pick random element from array
 */
export function pickRandom<T>(arr: readonly T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * Build an ascending arpeggio from chord
 */
export function buildArpeggio(
  chord: readonly number[],
  octaves: number = 1
): number[] {
  const result: number[] = [];
  for (let oct = 0; oct < octaves; oct++) {
    for (const note of chord) {
      result.push(note * Math.pow(2, oct));
    }
  }
  return result;
}

/**
 * Build a descending line from starting note
 */
export function buildDescendingLine(
  startNote: number,
  steps: number,
  octave: 3 | 4 | 5 = 4
): number[] {
  const scale = CS_MINOR_SCALE_DEGREES[`octave${octave}`];
  const startIndex = scale.findIndex(n => Math.abs(n - startNote) < 1);
  const result: number[] = [];

  for (let i = 0; i < steps; i++) {
    const index = (startIndex - i % scale.length + scale.length) % scale.length;
    const octaveOffset = Math.floor((startIndex - i) / scale.length);
    result.push(scale[index] * Math.pow(2, -octaveOffset));
  }

  return result;
}

// =============================================================================
// WAVEFORM RECOMMENDATIONS
// =============================================================================

/**
 * Waveform types for different emotional contexts
 */
export const WAVEFORMS = {
  // Dark/powerful - sine for depth, triangle for warmth
  power: ['sine', 'triangle'] as OscillatorType[],

  // Tense/harsh - sawtooth for edge, square for bite
  tension: ['sawtooth', 'square'] as OscillatorType[],

  // Soft/melancholic - sine for purity, triangle for gentleness
  melancholy: ['sine', 'triangle'] as OscillatorType[],

  // Neutral/melodic - all types available
  neutral: ['sine', 'triangle', 'sawtooth'] as OscillatorType[],
} as const;

// =============================================================================
// COMPLETE FREQUENCY REFERENCE TABLE
// =============================================================================

/**
 * Complete note reference with MIDI numbers
 * For debugging and documentation
 */
export const NOTE_REFERENCE = {
  'C#1': { freq: 34.65, midi: 25 },
  'D#1': { freq: 38.89, midi: 27 },
  'E1': { freq: 41.20, midi: 28 },
  'F#1': { freq: 46.25, midi: 30 },
  'G#1': { freq: 51.91, midi: 32 },
  'A1': { freq: 55.00, midi: 33 },
  'B1': { freq: 61.74, midi: 35 },
  'C#2': { freq: 69.30, midi: 37 },
  'D#2': { freq: 77.78, midi: 39 },
  'E2': { freq: 82.41, midi: 40 },
  'F#2': { freq: 92.50, midi: 42 },
  'G#2': { freq: 103.83, midi: 44 },
  'A2': { freq: 110.00, midi: 45 },
  'B2': { freq: 123.47, midi: 47 },
  'C#3': { freq: 138.59, midi: 49 },
  'D#3': { freq: 155.56, midi: 51 },
  'E3': { freq: 164.81, midi: 52 },
  'F#3': { freq: 185.00, midi: 54 },
  'G#3': { freq: 207.65, midi: 56 },
  'A3': { freq: 220.00, midi: 57 },
  'B3': { freq: 246.94, midi: 59 },
  'C#4': { freq: 277.18, midi: 61 },
  'D#4': { freq: 311.13, midi: 63 },
  'E4': { freq: 329.63, midi: 64 },
  'F#4': { freq: 369.99, midi: 66 },
  'G#4': { freq: 415.30, midi: 68 },
  'A4': { freq: 440.00, midi: 69 },
  'B4': { freq: 493.88, midi: 71 },
  'C#5': { freq: 554.37, midi: 73 },
  'D#5': { freq: 622.25, midi: 75 },
  'E5': { freq: 659.26, midi: 76 },
  'F#5': { freq: 739.99, midi: 78 },
  'G#5': { freq: 830.61, midi: 80 },
  'A5': { freq: 880.00, midi: 81 },
  'B5': { freq: 987.77, midi: 83 },
  'C#6': { freq: 1108.73, midi: 85 },
} as const;

// =============================================================================
// DEFAULT EXPORT
// =============================================================================

export default {
  // Constants
  A4_HZ,
  SEMITONE_RATIO,
  CS_MINOR,
  CS_MINOR_SCALE_DEGREES,
  INTERVALS,
  CHORDS,
  PHASE_HARMONICS,
  SOUND_INTERVALS,

  // Categories
  POWER_INTERVALS,
  DARK_INTERVALS,
  TENSION_INTERVALS,
  RESOLUTION_INTERVALS,
  WAVEFORMS,

  // Beethoven techniques
  SFORZANDO,
  DRAMATIC_RESTS,
  TREMOLO,

  // Functions
  midiToFreq,
  freqToMidi,
  transpose,
  transposeOctave,
  getRandomScaleNote,
  getRandomPentatonicNote,
  getScaleDegree,
  getRandomPowerInterval,
  getRandomDarkInterval,
  getRandomTensionInterval,
  humanize,
  pickRandom,
  getOctaveDoubling,
  getPowerChord,
  buildArpeggio,
  buildDescendingLine,

  // Reference
  NOTE_REFERENCE,
};
