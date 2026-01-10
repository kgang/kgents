/**
 * HORNET SOUND IDENTITY - The Sonic DNA of Hornet Siege
 *
 * "The hornet's name is written in the music."
 *
 * =============================================================================
 * DESIGN PHILOSOPHY: What Makes This Game Sound Unique
 * =============================================================================
 *
 * Most games use stock sounds. We synthesize EVERYTHING from sine waves.
 * This creates a cohesive, otherworldly soundscape that's impossible to
 * replicate - the audio equivalent of a painter mixing their own pigments.
 *
 * CORE IDENTITY PILLARS:
 *
 * 1. THE SWARM IS ALIVE
 *    - Individual bees have voices (micro-oscillators)
 *    - Swarm emergent behavior creates macro-textures
 *    - Coordination states change the "chord" of the swarm
 *    - THE BALL has a terrifying harmonic signature
 *
 * 2. HORROR THROUGH BIOLOGY
 *    - Real hornet wing frequency: 100-200Hz (fundamental)
 *    - Japanese giant hornet "click": 800-1200Hz warning
 *    - Thermal shock (real death mechanism): pitch rises with temperature
 *    - The silence before constriction is the most terrifying moment
 *
 * 3. THE KENT MOTIF PERVADES EVERYTHING
 *    - B#→F#→D#→A (two tritones) appears in:
 *      * THE BALL's fundamental frequencies
 *      * Kill stinger intervals
 *      * Crisis drone chord
 *      * Death melody
 *
 * 4. PROCEDURAL = UNPREDICTABLE = DREAD
 *    - No sound plays exactly the same way twice
 *    - Players can never fully "learn" the audio cues
 *    - Keeps the lizard brain alert
 *
 * =============================================================================
 * SWARM SYNTHESIS ARCHITECTURE
 * =============================================================================
 *
 * Each bee contributes a micro-oscillator to the swarm texture:
 *
 * BEE VOICE = fundamental + harmonics + formant
 *           = [100-200Hz base] + [2x, 3x, 5x overtones] + [resonant filter]
 *
 * SWARM = Σ(bee voices) + spatial panning + emergent beating
 *
 * The swarm creates EMERGENT harmonics through beating frequencies:
 * - 10 bees at 100Hz ± 5Hz random detune = rich buzzing texture
 * - As bees coordinate, detune narrows = more "focused" sound
 * - THE BALL = perfect unison = terrifying pure tone
 *
 * =============================================================================
 * THE BALL HORROR ARC
 * =============================================================================
 *
 * Phase          Audio Signature                              Terror Level
 * ─────────────────────────────────────────────────────────────────────────
 * FORMING        Scattered → converging buzz, rising pitch      ████░░░░░░
 * SPHERE         Perfect unison, sub-bass rumble                ██████░░░░
 * SILENCE        Near-total silence, player heartbeat only      ████████░░
 * CONSTRICT      Rising pitch, temperature → frequency          ██████████
 * DEATH          The KENT motif plays, then silence             GAME OVER
 *
 * =============================================================================
 * FREQUENCY MAPPINGS (Real Hornet Biology)
 * =============================================================================
 *
 * Japanese Giant Hornet (Vespa mandarinia):
 * - Wing beat fundamental: 100-150 Hz (larger hornets = lower)
 * - First harmonic: 200-300 Hz
 * - "Click" warning sound: 800-1200 Hz (mandible strike)
 * - Pheromone alarm response: Swarm pitch rises 10-20%
 *
 * Thermal Ball Death (Real Phenomenon):
 * - Honeybees surround hornet and vibrate to raise temperature
 * - Lethal temperature: 47°C (116°F)
 * - In-game: We REVERSE this - the HORNETS cook the PLAYER
 * - Pitch rises logarithmically with "temperature" (game intensity)
 *
 * =============================================================================
 */

import {
  CSHARP_MINOR_FREQUENCIES,
  KENT_SEMITONES,
} from './kent-fugue';

// =============================================================================
// CONSTANTS: The Sonic DNA
// =============================================================================

/**
 * Base frequencies for bee synthesis
 * Mapped to bee types and KENT cipher
 */
export const BEE_FREQUENCIES = {
  // Worker bees: middle range
  worker: {
    fundamental: 185.00,  // F#3 (KENT[E] = F#)
    formant: 600,
    harmonicDecay: 0.6,
  },
  // Scout bees: higher, more aggressive
  scout: {
    fundamental: 220.00,  // A3 (KENT[T] = A)
    formant: 900,
    harmonicDecay: 0.5,
  },
  // Guard bees: deeper, menacing
  guard: {
    fundamental: 138.59,  // C#3 (tonic)
    formant: 400,
    harmonicDecay: 0.7,
  },
  // Propolis bees: sticky, buzzy
  propolis: {
    fundamental: 155.56,  // D#3 (KENT[N] = D#)
    formant: 500,
    harmonicDecay: 0.65,
  },
  // Royal bees: the boss, very low
  royal: {
    fundamental: 261.63,  // B#3 (KENT[K] = B#)
    formant: 800,
    harmonicDecay: 0.55,
  },
};

/**
 * THE BALL phases mapped to audio characteristics
 */
export const BALL_AUDIO_PHASES = {
  forming: {
    detuneRange: 30,      // cents - scattered sound
    volumeBase: 0.3,
    pitchMultiplier: 1.0,
    silenceAmount: 0,
    heartbeatRate: 0,     // BPM
  },
  sphere: {
    detuneRange: 5,       // almost unison - terrifying
    volumeBase: 0.5,
    pitchMultiplier: 1.1,
    silenceAmount: 0,
    heartbeatRate: 80,
  },
  silence: {
    detuneRange: 0,
    volumeBase: 0.02,     // near silence
    pitchMultiplier: 1.0,
    silenceAmount: 0.95,
    heartbeatRate: 120,   // panicked heartbeat
  },
  constrict: {
    detuneRange: 2,       // perfect unison = maximum dread
    volumeBase: 0.7,
    pitchMultiplier: 1.5, // rising pitch = rising temperature
    silenceAmount: 0,
    heartbeatRate: 160,
  },
  death: {
    detuneRange: 0,
    volumeBase: 0.8,
    pitchMultiplier: 2.0, // frequency doubles at death
    silenceAmount: 0,
    heartbeatRate: 200,   // then stops
  },
};

/**
 * Horror intervals - dissonances that trigger primal fear
 */
export const HORROR_INTERVALS = {
  tritone: Math.pow(2, 6/12),        // The devil's interval
  minorSecond: Math.pow(2, 1/12),    // Maximum dissonance
  minorNinth: Math.pow(2, 13/12),    // Extended horror
  sharpEleven: Math.pow(2, 18/12),   // Lydian tension
};

/**
 * KENT motif as frequency multipliers from C#
 */
export const KENT_FREQ_MULTIPLIERS = KENT_SEMITONES.map(
  semitone => Math.pow(2, semitone / 12)
);

// =============================================================================
// TYPES
// =============================================================================

export type BeeType = 'worker' | 'scout' | 'guard' | 'propolis' | 'royal';
export type BallPhaseType = 'forming' | 'sphere' | 'silence' | 'constrict' | 'death';

export interface SwarmState {
  beeCount: number;
  beeTypes: Map<BeeType, number>;  // count per type
  coordinationLevel: number;       // 0-1, how organized the swarm is
  averageDistanceToPlayer: number;
  ballPhase: BallPhaseType | null;
  temperature: number;             // 0-1, THE BALL's heat
}

export interface BeeVoice {
  id: string;
  type: BeeType;
  oscillator: OscillatorNode;
  harmonics: OscillatorNode[];
  gain: GainNode;
  filter: BiquadFilterNode;
  panner: StereoPannerNode;
  baseFrequency: number;
  currentDetune: number;
}

export interface SwarmAudioConfig {
  maxVoices: number;          // CPU budget for oscillators
  voicePooling: boolean;      // Reuse voices for efficiency
  spatialAudio: boolean;      // Position-based panning
  emergentBeating: boolean;   // Allow beating frequencies
  kentMotifIntegration: boolean;
}

// =============================================================================
// SWARM SYNTHESIS ENGINE
// =============================================================================

/**
 * BeeSwarmSynthesizer
 *
 * Creates emergent swarm audio from individual bee voices.
 * The magic: slight detuning between voices creates organic "beating"
 * that sounds like a real swarm without any samples.
 */
export class BeeSwarmSynthesizer {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private compressor: DynamicsCompressorNode | null = null;
  private voices: Map<string, BeeVoice> = new Map();
  private voicePool: BeeVoice[] = [];

  private config: SwarmAudioConfig = {
    maxVoices: 24,            // 24 concurrent bee voices
    voicePooling: true,
    spatialAudio: true,
    emergentBeating: true,
    kentMotifIntegration: true,
  };

  // Current state stored for debugging/future use
  private currentState: SwarmState = {
    beeCount: 0,
    beeTypes: new Map(),
    coordinationLevel: 0,
    averageDistanceToPlayer: 1000,
    ballPhase: null,
    temperature: 0,
  };

  /** Get current swarm state (for debugging) */
  getState(): SwarmState {
    return this.currentState;
  }

  /**
   * Initialize the audio context and master chain
   */
  initialize(ctx: AudioContext): void {
    this.ctx = ctx;

    // Master gain
    this.masterGain = ctx.createGain();
    this.masterGain.gain.value = 0.3;

    // Compressor to tame swarm dynamics
    this.compressor = ctx.createDynamicsCompressor();
    this.compressor.threshold.value = -20;
    this.compressor.knee.value = 10;
    this.compressor.ratio.value = 4;
    this.compressor.attack.value = 0.005;
    this.compressor.release.value = 0.1;

    // Chain: voices → compressor → master → destination
    this.compressor.connect(this.masterGain);
    this.masterGain.connect(ctx.destination);

    // Pre-create voice pool
    if (this.config.voicePooling) {
      this.initializeVoicePool();
    }
  }

  /**
   * Pre-create oscillator voices for pooling
   */
  private initializeVoicePool(): void {
    if (!this.ctx) return;

    for (let i = 0; i < this.config.maxVoices; i++) {
      const voice = this.createVoice(`pool_${i}`, 'worker');
      voice.gain.gain.value = 0; // Silent until needed
      this.voicePool.push(voice);
    }
  }

  /**
   * Create a single bee voice with harmonics
   */
  private createVoice(id: string, type: BeeType): BeeVoice {
    if (!this.ctx || !this.compressor) {
      throw new Error('Audio context not initialized');
    }

    const beeConfig = BEE_FREQUENCIES[type];

    // Main oscillator (fundamental)
    const oscillator = this.ctx.createOscillator();
    oscillator.type = 'sawtooth'; // Rich in harmonics
    oscillator.frequency.value = beeConfig.fundamental;

    // Harmonic overtones (2x, 3x, 5x for organic texture)
    const harmonics: OscillatorNode[] = [];
    const harmonicRatios = [2, 3, 5];

    for (const ratio of harmonicRatios) {
      const harmonic = this.ctx.createOscillator();
      harmonic.type = 'sine';
      harmonic.frequency.value = beeConfig.fundamental * ratio;
      harmonics.push(harmonic);
    }

    // Formant filter (shapes the "vowel" of the buzz)
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = beeConfig.formant;
    filter.Q.value = 2;

    // Spatial panner
    const panner = this.ctx.createStereoPanner();
    panner.pan.value = 0;

    // Voice gain
    const gain = this.ctx.createGain();
    gain.gain.value = 0.1;

    // Connect: oscillator → filter → gain → panner → compressor
    oscillator.connect(filter);
    for (let i = 0; i < harmonics.length; i++) {
      const harmonicGain = this.ctx.createGain();
      harmonicGain.gain.value = 0.1 * Math.pow(beeConfig.harmonicDecay, i + 1);
      harmonics[i].connect(harmonicGain);
      harmonicGain.connect(filter);
    }
    filter.connect(gain);
    gain.connect(panner);
    panner.connect(this.compressor);

    // Start oscillators
    oscillator.start();
    harmonics.forEach(h => h.start());

    return {
      id,
      type,
      oscillator,
      harmonics,
      gain,
      filter,
      panner,
      baseFrequency: beeConfig.fundamental,
      currentDetune: 0,
    };
  }

  /**
   * Update swarm state from game state
   * This is the main interface - call every frame
   */
  updateSwarmState(state: SwarmState): void {
    this.currentState = state;

    if (!this.ctx || !this.masterGain) return;

    const now = this.ctx.currentTime;

    // Calculate target voice count based on bee count
    const targetVoices = Math.min(
      Math.ceil(state.beeCount / 10), // 1 voice per 10 bees
      this.config.maxVoices
    );

    // Adjust active voices
    this.adjustVoiceCount(targetVoices);

    // Update each voice based on swarm state
    this.voices.forEach((voice, _id) => {
      this.updateVoice(voice, state, now);
    });

    // Update master volume based on distance
    const distanceFactor = Math.max(0, 1 - state.averageDistanceToPlayer / 800);
    const ballFactor = state.ballPhase ? BALL_AUDIO_PHASES[state.ballPhase].volumeBase : 0.3;
    this.masterGain.gain.setTargetAtTime(
      distanceFactor * ballFactor,
      now,
      0.1
    );
  }

  /**
   * Adjust the number of active voices
   */
  private adjustVoiceCount(targetCount: number): void {
    const currentCount = this.voices.size;

    if (targetCount > currentCount) {
      // Add voices from pool
      for (let i = currentCount; i < targetCount && this.voicePool.length > 0; i++) {
        const voice = this.voicePool.pop()!;
        const beeType = this.selectBeeTypeForVoice();
        voice.type = beeType;
        voice.baseFrequency = BEE_FREQUENCIES[beeType].fundamental;
        voice.gain.gain.value = 0.1;
        this.voices.set(voice.id, voice);
      }
    } else if (targetCount < currentCount) {
      // Return voices to pool
      const toRemove = currentCount - targetCount;
      const voiceArray = Array.from(this.voices.values());
      for (let i = 0; i < toRemove; i++) {
        const voice = voiceArray[i];
        voice.gain.gain.value = 0;
        this.voices.delete(voice.id);
        this.voicePool.push(voice);
      }
    }
  }

  /**
   * Select bee type based on current swarm composition
   */
  private selectBeeTypeForVoice(): BeeType {
    const types: BeeType[] = ['worker', 'scout', 'guard', 'propolis', 'royal'];
    const weights = [0.5, 0.2, 0.15, 0.1, 0.05]; // worker-heavy

    const r = Math.random();
    let cumulative = 0;
    for (let i = 0; i < types.length; i++) {
      cumulative += weights[i];
      if (r < cumulative) return types[i];
    }
    return 'worker';
  }

  /**
   * Update a single voice based on swarm state
   */
  private updateVoice(voice: BeeVoice, state: SwarmState, now: number): void {
    const beeConfig = BEE_FREQUENCIES[voice.type];

    // Calculate detune based on coordination level
    // High coordination = less detune = more terrifying unison
    let detuneRange = 50 * (1 - state.coordinationLevel);

    // Ball phase overrides
    if (state.ballPhase) {
      detuneRange = BALL_AUDIO_PHASES[state.ballPhase].detuneRange;
    }

    // Apply random detune within range (creates beating)
    const targetDetune = (Math.random() - 0.5) * detuneRange;
    voice.oscillator.detune.setTargetAtTime(targetDetune, now, 0.2);

    // Pitch shift based on temperature (THE BALL heat death)
    let pitchMultiplier = 1;
    if (state.ballPhase && state.temperature > 0) {
      // Logarithmic pitch rise with temperature
      pitchMultiplier = 1 + Math.log2(1 + state.temperature);
    }
    if (state.ballPhase) {
      pitchMultiplier *= BALL_AUDIO_PHASES[state.ballPhase].pitchMultiplier;
    }

    const targetFreq = beeConfig.fundamental * pitchMultiplier;
    voice.oscillator.frequency.setTargetAtTime(targetFreq, now, 0.3);

    // Update harmonics
    const harmonicRatios = [2, 3, 5];
    voice.harmonics.forEach((harmonic, i) => {
      harmonic.frequency.setTargetAtTime(
        targetFreq * harmonicRatios[i],
        now,
        0.3
      );
    });

    // Update formant filter based on "aggression"
    const aggression = state.ballPhase ? 0.8 : state.coordinationLevel * 0.5;
    const targetFormant = beeConfig.formant * (1 + aggression);
    voice.filter.frequency.setTargetAtTime(targetFormant, now, 0.2);
  }

  /**
   * Play THE BALL's silence phase - the most terrifying moment
   * Near-total silence with just the player's heartbeat
   */
  playSilencePhase(heartbeatCallback: () => void): void {
    if (!this.ctx || !this.masterGain) return;

    const now = this.ctx.currentTime;

    // Fade swarm to near-silence
    this.masterGain.gain.setTargetAtTime(0.02, now, 0.5);

    // All voices to perfect unison (eerie)
    this.voices.forEach(voice => {
      voice.oscillator.detune.setTargetAtTime(0, now, 0.3);
      voice.gain.gain.setTargetAtTime(0.02, now, 0.3);
    });

    // Start heartbeat
    const heartbeatInterval = 60000 / BALL_AUDIO_PHASES.silence.heartbeatRate;
    const heartbeatTimer = setInterval(() => {
      heartbeatCallback();
    }, heartbeatInterval);

    // Stop after 3 seconds (silence phase duration)
    setTimeout(() => {
      clearInterval(heartbeatTimer);
    }, 3000);
  }

  /**
   * Play the KENT motif as the death knell
   */
  playKentDeathMotif(): void {
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    const baseFreq = CSHARP_MINOR_FREQUENCIES['C#3'];

    // Play K-E-N-T as descending horror
    const kentNotes = KENT_FREQ_MULTIPLIERS.map(mult => baseFreq * mult);
    const noteDuration = 0.8;

    kentNotes.forEach((freq, i) => {
      const osc = this.ctx!.createOscillator();
      const gain = this.ctx!.createGain();

      osc.type = 'sawtooth';
      osc.frequency.value = freq;

      gain.gain.setValueAtTime(0, now + i * noteDuration);
      gain.gain.linearRampToValueAtTime(0.4, now + i * noteDuration + 0.1);
      gain.gain.linearRampToValueAtTime(0, now + (i + 1) * noteDuration);

      osc.connect(gain);
      gain.connect(this.ctx!.destination);

      osc.start(now + i * noteDuration);
      osc.stop(now + (i + 1) * noteDuration + 0.1);
    });
  }

  /**
   * Clean up all audio resources
   */
  dispose(): void {
    this.voices.forEach(voice => {
      voice.oscillator.stop();
      voice.harmonics.forEach(h => h.stop());
    });
    this.voicePool.forEach(voice => {
      voice.oscillator.stop();
      voice.harmonics.forEach(h => h.stop());
    });
    this.voices.clear();
    this.voicePool = [];
  }
}

// =============================================================================
// HORROR AUDIO LAYERS
// =============================================================================

/**
 * HorrorDrone
 *
 * A terrifying sub-bass drone that triggers primal fear.
 * Uses the KENT intervals (tritones) for maximum dread.
 */
export class HorrorDrone {
  private ctx: AudioContext | null = null;
  private oscillators: OscillatorNode[] = [];
  // Individual gains for per-drone control
  private gains: GainNode[] = [];
  private masterGain: GainNode | null = null;

  /** Get individual drone gains (for advanced control) */
  getDroneGains(): GainNode[] {
    return this.gains;
  }
  private filter: BiquadFilterNode | null = null;
  private lfo: OscillatorNode | null = null;

  initialize(ctx: AudioContext): void {
    this.ctx = ctx;

    // Master gain
    this.masterGain = ctx.createGain();
    this.masterGain.gain.value = 0;

    // Low-pass filter for sub-bass emphasis
    this.filter = ctx.createBiquadFilter();
    this.filter.type = 'lowpass';
    this.filter.frequency.value = 200;
    this.filter.Q.value = 1;

    // Create tritone drones (the devil's interval)
    const baseFreq = 55; // A1 - sub-bass
    const tritoneFreq = baseFreq * HORROR_INTERVALS.tritone;

    // First drone: base note
    const osc1 = ctx.createOscillator();
    osc1.type = 'sine';
    osc1.frequency.value = baseFreq;

    const gain1 = ctx.createGain();
    gain1.gain.value = 0.5;

    osc1.connect(gain1);
    gain1.connect(this.filter);

    // Second drone: tritone above
    const osc2 = ctx.createOscillator();
    osc2.type = 'sine';
    osc2.frequency.value = tritoneFreq;

    const gain2 = ctx.createGain();
    gain2.gain.value = 0.4;

    osc2.connect(gain2);
    gain2.connect(this.filter);

    // Third drone: minor second for maximum dissonance
    const osc3 = ctx.createOscillator();
    osc3.type = 'sine';
    osc3.frequency.value = baseFreq * HORROR_INTERVALS.minorSecond;

    const gain3 = ctx.createGain();
    gain3.gain.value = 0.3;

    osc3.connect(gain3);
    gain3.connect(this.filter);

    // LFO for pulsing dread
    this.lfo = ctx.createOscillator();
    this.lfo.type = 'sine';
    this.lfo.frequency.value = 0.5; // Slow pulse

    const lfoGain = ctx.createGain();
    lfoGain.gain.value = 0.1;

    this.lfo.connect(lfoGain);
    lfoGain.connect(this.masterGain.gain);

    // Final chain
    this.filter.connect(this.masterGain);
    this.masterGain.connect(ctx.destination);

    this.oscillators = [osc1, osc2, osc3];
    this.gains = [gain1, gain2, gain3];

    // Start everything
    this.oscillators.forEach(osc => osc.start());
    this.lfo.start();
  }

  /**
   * Set horror intensity (0-1)
   */
  setIntensity(intensity: number): void {
    if (!this.masterGain || !this.ctx) return;

    const now = this.ctx.currentTime;
    this.masterGain.gain.setTargetAtTime(intensity * 0.3, now, 0.5);

    // Increase filter frequency with intensity (brighter = more urgent)
    if (this.filter) {
      this.filter.frequency.setTargetAtTime(
        200 + intensity * 300,
        now,
        0.3
      );
    }

    // LFO speeds up with intensity
    if (this.lfo) {
      this.lfo.frequency.setTargetAtTime(
        0.5 + intensity * 2,
        now,
        0.2
      );
    }
  }

  dispose(): void {
    this.oscillators.forEach(osc => osc.stop());
    if (this.lfo) this.lfo.stop();
  }
}

/**
 * Heartbeat synthesizer for THE BALL's silence phase
 */
export class HeartbeatSynth {
  private ctx: AudioContext | null = null;

  initialize(ctx: AudioContext): void {
    this.ctx = ctx;
  }

  /**
   * Play a single heartbeat
   * @param _bpm Current heart rate (used by caller for timing, not internally)
   * @param intensity Panic level (affects pitch and attack)
   */
  playBeat(_bpm: number, intensity: number = 0.5): void {
    if (!this.ctx) return;

    const now = this.ctx.currentTime;

    // Two-part heartbeat: "lub-dub"
    const baseFreq = 60 + intensity * 40; // Higher pitch when panicked

    // "Lub" (first sound)
    const lub = this.ctx.createOscillator();
    lub.type = 'sine';
    lub.frequency.setValueAtTime(baseFreq, now);
    lub.frequency.exponentialRampToValueAtTime(baseFreq * 0.5, now + 0.15);

    const lubGain = this.ctx.createGain();
    lubGain.gain.setValueAtTime(0, now);
    lubGain.gain.linearRampToValueAtTime(0.3 + intensity * 0.2, now + 0.02);
    lubGain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);

    lub.connect(lubGain);
    lubGain.connect(this.ctx.destination);

    lub.start(now);
    lub.stop(now + 0.2);

    // "Dub" (second sound) - slightly delayed
    const dubDelay = 0.1 + (1 - intensity) * 0.05; // Closer together when panicked

    const dub = this.ctx.createOscillator();
    dub.type = 'sine';
    dub.frequency.setValueAtTime(baseFreq * 0.8, now + dubDelay);
    dub.frequency.exponentialRampToValueAtTime(baseFreq * 0.4, now + dubDelay + 0.12);

    const dubGain = this.ctx.createGain();
    dubGain.gain.setValueAtTime(0, now + dubDelay);
    dubGain.gain.linearRampToValueAtTime(0.2 + intensity * 0.15, now + dubDelay + 0.02);
    dubGain.gain.exponentialRampToValueAtTime(0.001, now + dubDelay + 0.12);

    dub.connect(dubGain);
    dubGain.connect(this.ctx.destination);

    dub.start(now + dubDelay);
    dub.stop(now + dubDelay + 0.15);
  }
}

// =============================================================================
// HIVE AMBIENCE
// =============================================================================

/**
 * HiveAmbience
 *
 * Environmental soundscape of the hive:
 * - Low rumble of thousands of wings
 * - Occasional "click" warnings
 * - Spatial depth (sounds coming from all around)
 */
export class HiveAmbience {
  private ctx: AudioContext | null = null;
  private noiseNode: AudioBufferSourceNode | null = null;
  private noiseGain: GainNode | null = null;
  private rumbleOsc: OscillatorNode | null = null;
  private rumbleGain: GainNode | null = null;
  private filter: BiquadFilterNode | null = null;

  initialize(ctx: AudioContext): void {
    this.ctx = ctx;

    // Create filtered noise (distant swarm)
    const noiseBuffer = this.createNoiseBuffer(2);
    this.noiseNode = ctx.createBufferSource();
    this.noiseNode.buffer = noiseBuffer;
    this.noiseNode.loop = true;

    this.noiseGain = ctx.createGain();
    this.noiseGain.gain.value = 0;

    // Bandpass filter to shape noise into "swarm" texture
    this.filter = ctx.createBiquadFilter();
    this.filter.type = 'bandpass';
    this.filter.frequency.value = 400;
    this.filter.Q.value = 2;

    this.noiseNode.connect(this.filter);
    this.filter.connect(this.noiseGain);
    this.noiseGain.connect(ctx.destination);

    // Low rumble oscillator (hive vibration)
    this.rumbleOsc = ctx.createOscillator();
    this.rumbleOsc.type = 'sine';
    this.rumbleOsc.frequency.value = 40; // Sub-bass rumble

    this.rumbleGain = ctx.createGain();
    this.rumbleGain.gain.value = 0;

    this.rumbleOsc.connect(this.rumbleGain);
    this.rumbleGain.connect(ctx.destination);

    // Start sources
    this.noiseNode.start();
    this.rumbleOsc.start();
  }

  /**
   * Create a buffer of white/pink noise
   */
  private createNoiseBuffer(seconds: number): AudioBuffer {
    if (!this.ctx) throw new Error('No audio context');

    const sampleRate = this.ctx.sampleRate;
    const samples = sampleRate * seconds;
    const buffer = this.ctx.createBuffer(2, samples, sampleRate);

    for (let channel = 0; channel < 2; channel++) {
      const data = buffer.getChannelData(channel);
      for (let i = 0; i < samples; i++) {
        // Pink-ish noise (more low frequencies)
        data[i] = (Math.random() * 2 - 1) * 0.5;
      }
    }

    return buffer;
  }

  /**
   * Set ambience intensity based on swarm proximity
   */
  setIntensity(intensity: number): void {
    if (!this.ctx || !this.noiseGain || !this.rumbleGain) return;

    const now = this.ctx.currentTime;

    this.noiseGain.gain.setTargetAtTime(intensity * 0.15, now, 0.5);
    this.rumbleGain.gain.setTargetAtTime(intensity * 0.2, now, 0.5);

    // Filter opens up with intensity
    if (this.filter) {
      this.filter.frequency.setTargetAtTime(
        400 + intensity * 800,
        now,
        0.3
      );
    }
  }

  /**
   * Play a hornet "click" warning sound
   */
  playWarningClick(): void {
    if (!this.ctx) return;

    const now = this.ctx.currentTime;

    // High-frequency click (mandible strike)
    const click = this.ctx.createOscillator();
    click.type = 'square';
    click.frequency.setValueAtTime(1000, now);
    click.frequency.exponentialRampToValueAtTime(800, now + 0.05);

    const clickGain = this.ctx.createGain();
    clickGain.gain.setValueAtTime(0, now);
    clickGain.gain.linearRampToValueAtTime(0.3, now + 0.005);
    clickGain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

    // High-pass filter for "click" character
    const clickFilter = this.ctx.createBiquadFilter();
    clickFilter.type = 'highpass';
    clickFilter.frequency.value = 600;

    click.connect(clickFilter);
    clickFilter.connect(clickGain);
    clickGain.connect(this.ctx.destination);

    click.start(now);
    click.stop(now + 0.1);
  }

  dispose(): void {
    if (this.noiseNode) this.noiseNode.stop();
    if (this.rumbleOsc) this.rumbleOsc.stop();
  }
}

// =============================================================================
// MASTER ORCHESTRATOR
// =============================================================================

/**
 * HornetSoundIdentity
 *
 * The master controller that coordinates all audio systems
 * to create the unique sonic identity of Hornet Siege.
 */
export class HornetSoundIdentity {
  private ctx: AudioContext | null = null;

  // Sub-systems
  public swarm: BeeSwarmSynthesizer;
  public horror: HorrorDrone;
  public heartbeat: HeartbeatSynth;
  public ambience: HiveAmbience;

  // State
  private isInitialized = false;
  private currentBallPhase: BallPhaseType | null = null;

  constructor() {
    this.swarm = new BeeSwarmSynthesizer();
    this.horror = new HorrorDrone();
    this.heartbeat = new HeartbeatSynth();
    this.ambience = new HiveAmbience();
  }

  /**
   * Initialize all audio systems
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    this.ctx = new AudioContext();

    // Initialize all sub-systems
    this.swarm.initialize(this.ctx);
    this.horror.initialize(this.ctx);
    this.heartbeat.initialize(this.ctx);
    this.ambience.initialize(this.ctx);

    this.isInitialized = true;
  }

  /**
   * Update from game state - call every frame
   */
  update(gameState: {
    beeCount: number;
    coordinationLevel: number;
    distanceToPlayer: number;
    ballPhase: BallPhaseType | null;
    temperature: number;
    playerHealth: number;
  }): void {
    if (!this.isInitialized) return;

    // Update swarm synthesis
    this.swarm.updateSwarmState({
      beeCount: gameState.beeCount,
      beeTypes: new Map([['worker', gameState.beeCount]]),
      coordinationLevel: gameState.coordinationLevel,
      averageDistanceToPlayer: gameState.distanceToPlayer,
      ballPhase: gameState.ballPhase,
      temperature: gameState.temperature,
    });

    // Update horror drone based on health/danger
    const dangerLevel = (1 - gameState.playerHealth) +
                        gameState.coordinationLevel * 0.5 +
                        (gameState.ballPhase ? 0.3 : 0);
    this.horror.setIntensity(Math.min(1, dangerLevel));

    // Update ambience
    const proximityFactor = Math.max(0, 1 - gameState.distanceToPlayer / 600);
    this.ambience.setIntensity(proximityFactor);

    // Handle ball phase transitions
    if (gameState.ballPhase !== this.currentBallPhase) {
      this.onBallPhaseChange(gameState.ballPhase);
      this.currentBallPhase = gameState.ballPhase;
    }
  }

  /**
   * Handle THE BALL phase transitions
   */
  private onBallPhaseChange(newPhase: BallPhaseType | null): void {
    if (!newPhase) return;

    switch (newPhase) {
      case 'silence':
        // The most terrifying moment - near silence
        this.swarm.playSilencePhase(() => {
          this.heartbeat.playBeat(120, 0.7);
        });
        break;

      case 'death':
        // Play the KENT death motif
        this.swarm.playKentDeathMotif();
        break;

      case 'forming':
        // Warning clicks
        this.ambience.playWarningClick();
        setTimeout(() => this.ambience.playWarningClick(), 500);
        setTimeout(() => this.ambience.playWarningClick(), 800);
        break;
    }
  }

  /**
   * Clean up all resources
   */
  dispose(): void {
    this.swarm.dispose();
    this.horror.dispose();
    this.ambience.dispose();

    if (this.ctx) {
      this.ctx.close();
    }

    this.isInitialized = false;
  }
}

// =============================================================================
// EXPORTS
// =============================================================================

export default HornetSoundIdentity;
