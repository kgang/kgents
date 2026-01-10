/**
 * KENT Drum Pitch Engine
 *
 * Sublime, surreal, emergent drum pitches that transcend human capability.
 * Every drum resonates with the KENT cryptogram: B# - F# - D# - A (two tritones).
 *
 * "The KENT cryptogram doesn't just guide melody - it IS the resonant
 * structure of the entire sonic universe."
 */

// =============================================================================
// CONSTANTS: THE KENT FREQUENCY LATTICE
// =============================================================================

// Base frequency: C# (our tonic in C# minor)
export const KENT_BASE_FREQ = 277.18;

// KENT semitones from the cryptogram
export const KENT_SEMITONES = [0, 6, 3, 9] as const;

// KENT frequency ratios (semitone → ratio)
export const KENT_RATIOS = KENT_SEMITONES.map(s => Math.pow(2, s / 12));
// [1.0, 1.4142, 1.1892, 1.6818]

// The fundamental frequencies of KENT
export const KENT_FREQUENCIES = KENT_RATIOS.map(r => KENT_BASE_FREQ * r);
// [277.18, 391.99, 329.63, 466.16]

// Golden ratio for fibonacci/spiral calculations
const PHI = 1.618033988749;
const GOLDEN_ANGLE = 2 * Math.PI / (PHI * PHI); // ~137.5 degrees

// Fibonacci sequence for hi-hat modulation
const FIB = [1, 1, 2, 3, 5, 8, 13, 21];

// Prime numbers for harmonic emphasis
const PRIMES = [2, 3, 5, 7, 11, 13];

// =============================================================================
// TYPES
// =============================================================================

export type GamePhase = 'exploration' | 'combat' | 'crisis' | 'death';

export interface MusicalPosition {
  beatPosition: number;      // 0-1 within current beat
  barPosition: number;       // 0-1 within current bar
  sixteenthPosition: number; // 0-15 within bar
  kentPosition: number;      // 0-3 current KENT sequence position
  beatInPhrase: number;      // 0-15 for 4-bar phrase
  barInWave: number;         // bar number within current wave
  totalBars: number;         // total bars played
}

export interface GameState {
  intensity: number;         // 0-1
  phase: GamePhase;
  waveNumber: number;
}

export interface DrumTriggers {
  kick?: boolean;
  snare?: boolean;
  hihat?: boolean;
  hihatOpenness?: number;    // 0 = closed, 1 = open
  tom?: 0 | 1 | 2;          // high, mid, floor
  crash?: boolean;
  ride?: boolean;
  isPhaseTransition?: boolean;
  beatsSinceLastSnare?: number;
}

// Pitch envelope for continuous glides
export interface PitchEnvelope {
  start: number;
  end: number;
  duration: number;
  curve: 'linear' | 'exponential' | 'logarithmic';
}

// Kick drum pitch result
export interface KickPitch {
  startPitch: number;
  endPitch: number;
  duration: number;
  subPitch: number;
  // Micro-glide during sustain
  sustainGlide: {
    rate: number;    // semitones per second
    range: number;   // max range
  };
}

// Snare drum pitch result
export interface SnarePitch {
  bodyPitch: number;
  wirePitch: number;         // tritone shimmer
  pitchEnvelope: PitchEnvelope;
  // Prime harmonic emphasis
  harmonicEmphasis: Array<{
    ratio: number;
    gain: number;
    detune: number;          // cents
  }>;
}

// Hi-hat pitch result
export interface HiHatPitch {
  centerFrequency: number;
  bandwidth: number;
  shimmerFreq: number;       // procedural shimmer frequency
  shimmerDepth: number;      // shimmer amplitude
  // Resonant peaks at KENT intervals
  resonantPeaks: Array<{
    frequency: number;
    q: number;
    gain: number;
  }>;
}

// Tom pitch result
export interface TomPitch {
  pitch: number;
  glissandoEnvelope: PitchEnvelope;
  // Sympathetic ringing at KENT harmonics
  sympatheticStrings: Array<{
    frequency: number;
    decay: number;
    level: number;
  }>;
}

// Crash pitch result
export interface CrashPitch {
  centerPitch: number;
  pitchDrop: number;         // cents drop during decay
  // Weighted partials from KENT history
  partialWeights: number[];  // weights for each KENT frequency
  ringModFreq: number;       // ring modulation frequency
}

// Ride pitch result
export interface RidePitch {
  bellPitch: number;
  bowPitch: number;
  pingFrequency: number;
  pingResonance: number;
  washCenter: number;
  washBandwidth: number;
}

// Complete drum pitch set
export interface DrumPitchSet {
  kick?: KickPitch;
  snare?: SnarePitch;
  hihat?: HiHatPitch;
  tom?: TomPitch;
  crash?: CrashPitch;
  ride?: RidePitch;
}

// =============================================================================
// PHASE-SPECIFIC BEHAVIORS
// =============================================================================

interface DrumPitchBehavior {
  kickOctaveRange: number;
  snarePitchVariance: number;
  hihatFormantSpeed: number;
  tomSpiralSpeed: number;
  crashTensionMultiplier: number;
  rideAccumulatorSpeed: number;
}

const PHASE_BEHAVIORS: Record<GamePhase, DrumPitchBehavior> = {
  exploration: {
    kickOctaveRange: 1,
    snarePitchVariance: 0.2,
    hihatFormantSpeed: 0.5,
    tomSpiralSpeed: 0.5,
    crashTensionMultiplier: 0.5,
    rideAccumulatorSpeed: 1.0
  },
  combat: {
    kickOctaveRange: 1.5,
    snarePitchVariance: 0.4,
    hihatFormantSpeed: 1.0,
    tomSpiralSpeed: 1.0,
    crashTensionMultiplier: 1.0,
    rideAccumulatorSpeed: 1.5
  },
  crisis: {
    kickOctaveRange: 2,
    snarePitchVariance: 0.7,
    hihatFormantSpeed: 2.0,
    tomSpiralSpeed: PHI,
    crashTensionMultiplier: 2.0,
    rideAccumulatorSpeed: 2.0
  },
  death: {
    kickOctaveRange: 3,
    snarePitchVariance: 1.0,
    hihatFormantSpeed: 0.1,
    tomSpiralSpeed: 0.1,
    crashTensionMultiplier: 3.0,
    rideAccumulatorSpeed: 0.1
  }
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function findNearestKentIndex(freq: number): number {
  let octaveNormalized = freq;
  while (octaveNormalized > KENT_BASE_FREQ * 2) octaveNormalized /= 2;
  while (octaveNormalized < KENT_BASE_FREQ) octaveNormalized *= 2;

  let nearestIdx = 0;
  let nearestDist = Infinity;

  KENT_FREQUENCIES.forEach((kentFreq, i) => {
    const dist = Math.abs(Math.log2(octaveNormalized / kentFreq));
    if (dist < nearestDist) {
      nearestDist = dist;
      nearestIdx = i;
    }
  });

  return nearestIdx;
}

// =============================================================================
// INDIVIDUAL DRUM PITCH CALCULATORS
// =============================================================================

/**
 * KICK: The Tritone Oscillator
 * Breathes between tritone poles with impossible continuous pitch contours
 */
function calculateKickPitch(
  beatPosition: number,
  barPosition: number,
  intensity: number,
  waveNumber: number,
  phase: GamePhase
): KickPitch {
  const behavior = PHASE_BEHAVIORS[phase];

  // Which tritone pair dominates (alternates every 2 bars)
  const tritoneIndex = Math.floor(barPosition * 2) % 2;
  const pair = tritoneIndex === 0
    ? [KENT_FREQUENCIES[0], KENT_FREQUENCIES[1]]   // B# <-> F#
    : [KENT_FREQUENCIES[2], KENT_FREQUENCIES[3]];  // D# <-> A

  // Golden ratio phase determines position between poles
  const goldenPhase = (beatPosition * PHI) % 1;

  // Base pitch interpolates between tritone poles
  const basePitch = lerp(pair[0], pair[1], goldenPhase);

  // Sub-octave descent: more intense = deeper drop
  const octaveDepth = behavior.kickOctaveRange * (0.5 + intensity * 0.5);
  const attackPitch = basePitch * Math.pow(2, octaveDepth / 2);
  const releasePitch = basePitch / 4; // Sub-bass settle

  // Sub oscillator follows wave number (deeper subs in later waves)
  const subPitch = releasePitch / (1 + waveNumber * 0.1);

  return {
    startPitch: attackPitch,
    endPitch: releasePitch,
    duration: 0.15 + (0.1 * (1 - intensity)),
    subPitch,
    sustainGlide: {
      rate: Math.sin(barPosition * Math.PI * 2) * 0.5,
      range: intensity * 2
    }
  };
}

/**
 * SNARE: The Phase Witness
 * Marks transitions with memory-influenced pitch
 */
function calculateSnarePitch(
  kentPosition: number,
  beatsSinceLastSnare: number,
  intensity: number,
  previousSnarePitch: number,
  phase: GamePhase
): SnarePitch {
  const behavior = PHASE_BEHAVIORS[phase];

  // Current KENT frequency as base
  const currentKent = KENT_FREQUENCIES[kentPosition % 4];

  // Memory interpolation: closer hits = more connection
  const memoryDecay = Math.exp(-beatsSinceLastSnare / 2);
  const basePitch = lerp(
    currentKent,
    previousSnarePitch,
    memoryDecay * behavior.snarePitchVariance
  );

  // Prime harmonic emphasis for otherworldly pitched noise
  const harmonicEmphasis = PRIMES.map((p, i) => ({
    ratio: p,
    gain: Math.pow(0.7, i) * (1 + intensity * 0.5),
    detune: KENT_SEMITONES[(kentPosition + i) % 4] * 2
  }));

  // Wire pitch at tritone (KENT[1] ratio)
  const wirePitch = basePitch * KENT_RATIOS[1];

  return {
    bodyPitch: basePitch,
    wirePitch,
    harmonicEmphasis,
    pitchEnvelope: {
      start: basePitch * 0.95,
      end: basePitch,
      duration: 0.12,
      curve: 'exponential'
    }
  };
}

/**
 * HI-HAT: The Shimmer Field
 * Higher harmonic dimension with fibonacci-driven evolution
 */
function calculateHiHatPitch(
  currentKickPitch: number,
  openness: number,
  sixteenthPosition: number,
  intensity: number,
  phase: GamePhase
): HiHatPitch {
  const behavior = PHASE_BEHAVIORS[phase];

  // 8th partial of kick for harmonic coherence
  const baseCenter = currentKickPitch * 8;

  // Fibonacci modulation of center frequency
  const fibIndex = sixteenthPosition % FIB.length;
  const fibModulation = FIB[fibIndex] / 21;

  // Center frequency spans 2 octaves based on fibonacci
  const centerFreq = baseCenter * (1 + fibModulation);

  // Resonant peaks at KENT intervals - capped Q to prevent feedback
  const resonantPeaks = KENT_RATIOS.map((ratio, i) => ({
    frequency: Math.min(centerFreq * ratio, 12000),
    q: Math.min(5 + (intensity * 5), 8), // Capped Q for stability
    gain: Math.pow(0.7, i) // Gentler gain curve
  }));

  // Openness affects bandwidth
  const bandwidth = lerp(200, 4000, openness);

  // Procedural shimmer: randomized pitch drift with dissipation limits
  // Frequency varies with position and intensity, but capped to prevent feedback
  const shimmerBase = 0.02 + Math.sin(sixteenthPosition * 0.4) * 0.005; // Reduced range
  const shimmerFreq = Math.min(shimmerBase * (1 + intensity * behavior.hihatFormantSpeed * 0.5), 0.04);
  const shimmerDepth = Math.min(0.03 * (0.5 + intensity * 0.3), 0.025); // Capped low

  return {
    centerFrequency: centerFreq,
    bandwidth,
    shimmerFreq,
    shimmerDepth,
    resonantPeaks
  };
}

/**
 * TOM: The Fibonacci Spiral
 * Traverses KENT space via golden ratio
 */
function calculateTomPitch(
  tomState: TomState,
  tomIndex: 0 | 1 | 2,
  _beatInPhrase: number,
  waveNumber: number,
  intensity: number,
  phase: GamePhase
): { pitch: TomPitch; newState: TomState } {
  const behavior = PHASE_BEHAVIORS[phase];

  // Base pitches for each tom
  const TOM_BASE_PITCHES = [
    KENT_BASE_FREQ * 2,      // High tom: octave above
    KENT_BASE_FREQ * 1.5,    // Mid tom: perfect fifth
    KENT_BASE_FREQ           // Floor tom: fundamental
  ];

  // Golden spiral through KENT space
  const spiralSpeed = behavior.tomSpiralSpeed;
  const newAngle = tomState.spiralAngle + GOLDEN_ANGLE * spiralSpeed;

  // Map spiral to KENT position
  const kentFloat = (newAngle / (Math.PI / 2)) % 4;
  const kentLow = Math.floor(kentFloat);
  const kentHigh = (kentLow + 1) % 4;
  const kentLerp = kentFloat - kentLow;

  // Interpolate between KENT frequencies
  const kentPitch = lerp(
    KENT_FREQUENCIES[kentLow],
    KENT_FREQUENCIES[kentHigh],
    kentLerp
  );

  // Combine with tom base pitch
  const basePitch = TOM_BASE_PITCHES[tomIndex];
  const targetPitch = basePitch * (kentPitch / KENT_BASE_FREQ);

  // Pitch space expands over waves
  const expansionFactor = 1 + (waveNumber - 1) * 0.1;
  const expandedPitch = basePitch + (targetPitch - basePitch) * expansionFactor;

  // Phantom glissando from previous pitch
  const glissandoStart = lerp(tomState.lastPitch, expandedPitch, 0.3);

  // Sympathetic strings at KENT harmonics
  const sympatheticStrings = KENT_FREQUENCIES.map((f, i) => ({
    frequency: f * Math.pow(2, tomIndex),
    decay: 0.5 - (i * 0.1),
    level: 0.15
  }));

  return {
    pitch: {
      pitch: expandedPitch,
      glissandoEnvelope: {
        start: glissandoStart,
        end: expandedPitch,
        duration: 0.05,
        curve: 'exponential'
      },
      sympatheticStrings
    },
    newState: {
      spiralAngle: newAngle,
      lastPitch: expandedPitch,
      accumulator: tomState.accumulator + intensity
    }
  };
}

/**
 * CRASH: The Void Eruption
 * Releases accumulated tritone tension
 */
function calculateCrashPitch(
  recentKentHistory: number[],
  _isPhaseTransition: boolean,
  _intensity: number,
  timeSinceLastCrash: number,
  phase: GamePhase
): CrashPitch {
  const behavior = PHASE_BEHAVIORS[phase];

  // Spectral memory: weights from recent KENT history
  const kentWeights = [0, 0, 0, 0];
  recentKentHistory.forEach((pos, i) => {
    const recency = Math.exp(-i / 4);
    kentWeights[pos % 4] += recency;
  });

  // Normalize weights
  const totalWeight = kentWeights.reduce((a, b) => a + b, 0) || 1;
  const normalizedWeights = kentWeights.map(w => w / totalWeight);

  // Center pitch weighted by KENT gravity
  const centerPitch = KENT_FREQUENCIES.reduce((acc, freq, i) => {
    return acc + freq * normalizedWeights[i];
  }, 0) * 4; // 2 octaves up

  // Tension release: longer time = more dramatic
  const tensionFactor = Math.min(timeSinceLastCrash / 8, 2) * behavior.crashTensionMultiplier;
  const pitchDrop = tensionFactor * 200;

  // Ring modulation at dominant KENT frequency
  const dominantKentIndex = normalizedWeights.indexOf(Math.max(...normalizedWeights));
  const ringModFreq = KENT_FREQUENCIES[dominantKentIndex];

  return {
    centerPitch,
    pitchDrop,
    partialWeights: normalizedWeights,
    ringModFreq
  };
}

/**
 * RIDE: The Phase Accumulator
 * Continuous witness of musical evolution
 */
function calculateRidePitch(
  rideState: RideState,
  currentKentPosition: number,
  _barInWave: number,
  totalBars: number,
  intensity: number,
  phase: GamePhase
): { pitch: RidePitch; newState: RideState } {
  const behavior = PHASE_BEHAVIORS[phase];

  // Phase accumulation
  const phaseIncrement = (2 * Math.PI) / 64 * behavior.rideAccumulatorSpeed;
  const newPhase = rideState.phaseAccumulator + phaseIncrement;

  // Base pitch
  const basePitch = KENT_BASE_FREQ * 6;

  // Phase modulation
  const phaseModulation = Math.sin(newPhase) * 0.1;

  // KENT gravity: pitch pulled toward most-visited frequencies
  const visits = [...rideState.kentVisits];
  visits[currentKentPosition]++;

  const totalVisits = visits.reduce((a, b) => a + b, 0);
  const kentGravity = KENT_FREQUENCIES.reduce((acc, freq, i) => {
    const weight = visits[i] / totalVisits;
    return acc + freq * weight;
  }, 0);

  // Blend with gravity over time
  const gravityBlend = Math.min(totalBars / 100, 0.5);
  const modulatedPitch = basePitch * (1 + phaseModulation);
  const gravitatedPitch = lerp(modulatedPitch, kentGravity * 6, gravityBlend);

  // Bell vs bow
  const bellPitch = gravitatedPitch * 1.5;
  const bowPitch = gravitatedPitch * 0.75;

  // Intensity ceiling
  const newPeakIntensity = Math.max(rideState.peakIntensity, intensity);
  const ceilingExpansion = 1 + newPeakIntensity * 0.2;

  return {
    pitch: {
      bellPitch: bellPitch * ceilingExpansion,
      bowPitch,
      pingFrequency: KENT_FREQUENCIES[currentKentPosition] * 8,
      pingResonance: 20 + intensity * 30,
      washCenter: gravitatedPitch,
      washBandwidth: 500 + intensity * 1000
    },
    newState: {
      phaseAccumulator: newPhase,
      kentVisits: visits,
      peakIntensity: newPeakIntensity
    }
  };
}

// =============================================================================
// STATE INTERFACES
// =============================================================================

interface TomState {
  spiralAngle: number;
  lastPitch: number;
  accumulator: number;
}

interface RideState {
  phaseAccumulator: number;
  kentVisits: number[];
  peakIntensity: number;
}

// =============================================================================
// MASTER PITCH ENGINE
// =============================================================================

export class KentDrumPitchEngine {
  private tomState: TomState;
  private rideState: RideState;
  private previousSnarePitch: number;
  private recentKentHistory: number[];
  private lastCrashTime: number;
  private lastKickPitch: number;

  constructor() {
    this.tomState = {
      spiralAngle: Math.random() * Math.PI * 2, // Randomized start
      lastPitch: KENT_BASE_FREQ,
      accumulator: 0
    };
    this.rideState = {
      phaseAccumulator: Math.random() * Math.PI * 2,
      kentVisits: [1, 1, 1, 1], // Start with even distribution
      peakIntensity: 0
    };
    this.previousSnarePitch = KENT_FREQUENCIES[0];
    this.recentKentHistory = [0, 1, 2, 3]; // Initial history
    this.lastCrashTime = 0;
    this.lastKickPitch = KENT_FREQUENCIES[0] / 2;
  }

  /**
   * Calculate pitches for all triggered drums with cross-drum coherence
   */
  calculatePitches(
    gameState: GameState,
    musicalPosition: MusicalPosition,
    drumTriggers: DrumTriggers
  ): DrumPitchSet {
    const { intensity, phase, waveNumber } = gameState;
    const {
      beatPosition, barPosition, sixteenthPosition,
      kentPosition, beatInPhrase, barInWave, totalBars
    } = musicalPosition;

    // Update KENT history
    if (this.recentKentHistory[0] !== kentPosition) {
      this.recentKentHistory.unshift(kentPosition);
      if (this.recentKentHistory.length > 16) {
        this.recentKentHistory.pop();
      }
    }

    const result: DrumPitchSet = {};

    // Calculate kick first (other drums reference it)
    if (drumTriggers.kick) {
      result.kick = calculateKickPitch(
        beatPosition, barPosition, intensity, waveNumber, phase
      );
      this.lastKickPitch = result.kick.endPitch;
    }

    if (drumTriggers.snare) {
      result.snare = calculateSnarePitch(
        kentPosition,
        drumTriggers.beatsSinceLastSnare ?? 4,
        intensity,
        this.previousSnarePitch,
        phase
      );
      this.previousSnarePitch = result.snare.bodyPitch;
    }

    if (drumTriggers.hihat) {
      result.hihat = calculateHiHatPitch(
        this.lastKickPitch,
        drumTriggers.hihatOpenness ?? 0,
        sixteenthPosition,
        intensity,
        phase
      );
    }

    if (drumTriggers.tom !== undefined) {
      const tomResult = calculateTomPitch(
        this.tomState,
        drumTriggers.tom,
        beatInPhrase,
        waveNumber,
        intensity,
        phase
      );
      result.tom = tomResult.pitch;
      this.tomState = tomResult.newState;
    }

    if (drumTriggers.crash) {
      const timeSinceLastCrash = totalBars - this.lastCrashTime;
      result.crash = calculateCrashPitch(
        this.recentKentHistory,
        drumTriggers.isPhaseTransition ?? false,
        intensity,
        timeSinceLastCrash,
        phase
      );
      this.lastCrashTime = totalBars;
    }

    if (drumTriggers.ride) {
      const rideResult = calculateRidePitch(
        this.rideState,
        kentPosition,
        barInWave,
        totalBars,
        intensity,
        phase
      );
      result.ride = rideResult.pitch;
      this.rideState = rideResult.newState;
    }

    // Apply cross-drum resonance
    this.applyResonance(result);

    return result;
  }

  /**
   * Cross-drum resonance matrix for harmonic coherence
   */
  private applyResonance(drums: DrumPitchSet): void {
    if (!drums.kick) return;

    const kickFundamental = drums.kick.endPitch;
    const kickKentIndex = findNearestKentIndex(kickFundamental);

    // Hi-hat shimmer coherent with kick
    if (drums.hihat) {
      drums.hihat.centerFrequency = kickFundamental * 8;
    }

    // Snare body quantized to nearest KENT
    if (drums.snare) {
      const kentInfluence = 0.3;
      drums.snare.bodyPitch = lerp(
        drums.snare.bodyPitch,
        KENT_FREQUENCIES[kickKentIndex],
        kentInfluence
      );
    }

    // Tom avoids kick fundamental (tritone away if too close)
    if (drums.tom) {
      const kickAvoidMin = kickFundamental * Math.pow(2, -3/12);
      const kickAvoidMax = kickFundamental * Math.pow(2, 3/12);

      if (drums.tom.pitch > kickAvoidMin && drums.tom.pitch < kickAvoidMax) {
        drums.tom.pitch = kickFundamental * KENT_RATIOS[1]; // Tritone away
      }
    }

    // Ride bell at tritone above kick for maximum tension
    if (drums.ride) {
      drums.ride.bellPitch = kickFundamental * KENT_RATIOS[1] * 4;
    }
  }

  /**
   * Get current engine state for debugging/visualization
   */
  getState(): {
    tomSpiralAngle: number;
    ridePhase: number;
    kentHistory: number[];
  } {
    return {
      tomSpiralAngle: this.tomState.spiralAngle,
      ridePhase: this.rideState.phaseAccumulator,
      kentHistory: [...this.recentKentHistory]
    };
  }
}

// =============================================================================
// SINGLETON INSTANCE FOR GLOBAL USE
// =============================================================================

let globalEngine: KentDrumPitchEngine | null = null;

export function getKentDrumPitchEngine(): KentDrumPitchEngine {
  if (!globalEngine) {
    globalEngine = new KentDrumPitchEngine();
  }
  return globalEngine;
}

export function resetKentDrumPitchEngine(): void {
  globalEngine = new KentDrumPitchEngine();
}
