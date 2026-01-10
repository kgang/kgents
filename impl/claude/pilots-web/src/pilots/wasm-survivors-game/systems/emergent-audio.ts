/**
 * WASM Survivors - Emergent Generative Audio System
 *
 * Inspired by Winifred Phillips' adaptive game music architecture.
 *
 * FIVE LAYERS OF EMERGENT AUDIO:
 * 1. AMBIENT DRONE - Continuous texture that shifts with mood
 * 2. RHYTHMIC PULSE - Heartbeat-like tempo that scales with intensity
 * 3. MELODIC FRAGMENTS - Short motifs triggered by game events
 * 4. STINGERS & HITS - Impact sounds with ASMR layering
 * 5. SPATIAL AUDIO - Positional sound with distance attenuation
 *
 * CORE PRINCIPLES (Phillips-style):
 * - Vertical layering: Layers add/remove based on intensity
 * - Horizontal resequencing: Smooth transitions between states
 * - Harmonic memory: Tonal continuity across events
 * - Adaptive mixing: Context-aware volume balancing
 *
 * @see https://winifredphillips.wpcomstaging.com/
 */

// =============================================================================
// TYPES & INTERFACES
// =============================================================================

export type GamePhase = 'exploration' | 'combat' | 'crisis' | 'death';
export type AudioMood = 'calm' | 'tense' | 'crisis' | 'death';

export interface Vector2 {
  x: number;
  y: number;
}

export interface GameAudioState {
  phase: GamePhase;
  intensity: number;        // 0-1, computed from game state
  playerHealth: number;     // 0-1 fraction
  enemyCount: number;
  waveNumber: number;
  ballPhase: 'none' | 'forming' | 'sphere' | 'silence' | 'constrict' | 'death';
  playerPosition: Vector2;
  recentKills: number;      // Kills in last 2 seconds
  comboCount: number;
}

export interface HarmonicMemory {
  lastFrequencies: number[];  // Last 5 played root frequencies
  currentKey: number;         // Current harmonic center (Hz)
  tension: number;            // 0-1, accumulated unresolved tension
  lastEventTime: number;
}

// Musical intervals (frequency ratios)
const INTERVALS = {
  UNISON: 1,
  MINOR_2ND: 16/15,      // ~1.067 - tension, dissonance
  MAJOR_2ND: 9/8,        // 1.125 - mild tension
  MINOR_3RD: 6/5,        // 1.2 - sad, dark
  MAJOR_3RD: 5/4,        // 1.25 - happy, bright
  PERFECT_4TH: 4/3,      // ~1.333 - suspended, open
  TRITONE: 45/32,        // ~1.414 - devil's interval, dread
  PERFECT_5TH: 3/2,      // 1.5 - power, stability
  MINOR_6TH: 8/5,        // 1.6 - dark richness
  MAJOR_6TH: 5/3,        // ~1.667 - warm
  MINOR_7TH: 9/5,        // 1.8 - jazzy, unresolved
  MAJOR_7TH: 15/8,       // 1.875 - leading tone tension
  OCTAVE: 2,
};

// C minor pentatonic scale frequencies (dark, moody)
const C_MINOR_PENTATONIC = [
  130.81,  // C3
  155.56,  // Eb3
  196.00,  // G3
  233.08,  // Bb3
  261.63,  // C4
  311.13,  // Eb4
  392.00,  // G4
  466.16,  // Bb4
  523.25,  // C5
];

// =============================================================================
// LAYER 1: AMBIENT DRONE
// =============================================================================

/**
 * Continuous ambient texture that evolves with game mood.
 * Uses detuned oscillators with LFO modulation for organic movement.
 */
export class AmbientDroneLayer {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private oscillators: OscillatorNode[] = [];
  private gains: GainNode[] = [];
  private filter: BiquadFilterNode | null = null;
  private lfo: OscillatorNode | null = null;
  private lfoGain: GainNode | null = null;

  private currentMood: AudioMood = 'calm';
  private targetVolume = 0.15;
  private isRunning = false;

  // Mood configurations
  private moodConfigs: Record<AudioMood, {
    baseFreq: number;
    detuneSpread: number;
    filterCutoff: number;
    filterQ: number;
    lfoRate: number;
    lfoDepth: number;
    volume: number;
    intervals: number[];
  }> = {
    calm: {
      baseFreq: 65.41,      // C2
      detuneSpread: 3,      // cents
      filterCutoff: 800,
      filterQ: 0.5,
      lfoRate: 0.1,         // Hz
      lfoDepth: 20,         // cents
      volume: 0.12,
      intervals: [INTERVALS.UNISON, INTERVALS.PERFECT_5TH, INTERVALS.OCTAVE],
    },
    tense: {
      baseFreq: 73.42,      // D2
      detuneSpread: 8,
      filterCutoff: 1200,
      filterQ: 1,
      lfoRate: 0.3,
      lfoDepth: 40,
      volume: 0.15,
      intervals: [INTERVALS.UNISON, INTERVALS.MINOR_3RD, INTERVALS.PERFECT_5TH],
    },
    crisis: {
      baseFreq: 77.78,      // Eb2
      detuneSpread: 15,
      filterCutoff: 2000,
      filterQ: 2,
      lfoRate: 0.8,
      lfoDepth: 80,
      volume: 0.18,
      intervals: [INTERVALS.UNISON, INTERVALS.TRITONE, INTERVALS.MINOR_7TH],
    },
    death: {
      baseFreq: 55.00,      // A1
      detuneSpread: 2,
      filterCutoff: 400,
      filterQ: 0.3,
      lfoRate: 0.05,
      lfoDepth: 10,
      volume: 0.08,
      intervals: [INTERVALS.UNISON, INTERVALS.MINOR_3RD],
    },
  };

  start(audioContext: AudioContext, destination: AudioNode): void {
    if (this.isRunning) return;

    this.ctx = audioContext;
    this.isRunning = true;

    // Create master gain
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0;
    this.masterGain.connect(destination);

    // Create low-pass filter
    this.filter = this.ctx.createBiquadFilter();
    this.filter.type = 'lowpass';
    this.filter.frequency.value = 800;
    this.filter.Q.value = 0.5;
    this.filter.connect(this.masterGain);

    // Create LFO for organic movement
    this.lfo = this.ctx.createOscillator();
    this.lfo.type = 'sine';
    this.lfo.frequency.value = 0.1;

    this.lfoGain = this.ctx.createGain();
    this.lfoGain.gain.value = 20;

    this.lfo.connect(this.lfoGain);
    this.lfo.start();

    // Create oscillators for the drone
    this.createOscillators('calm');

    // Fade in
    this.masterGain.gain.setTargetAtTime(
      this.moodConfigs.calm.volume,
      this.ctx.currentTime,
      0.5
    );
  }

  private createOscillators(mood: AudioMood): void {
    if (!this.ctx || !this.filter || !this.lfoGain) return;

    // Clean up existing oscillators
    this.oscillators.forEach(osc => {
      try { osc.stop(); } catch {}
    });
    this.oscillators = [];
    this.gains = [];

    const config = this.moodConfigs[mood];

    config.intervals.forEach((interval, i) => {
      const osc = this.ctx!.createOscillator();
      osc.type = i === 0 ? 'sine' : 'triangle';
      osc.frequency.value = config.baseFreq * interval;

      // Add slight detune for richness
      osc.detune.value = (Math.random() - 0.5) * config.detuneSpread * 2;

      // Connect LFO to detune for organic movement
      this.lfoGain!.connect(osc.detune);

      const gain = this.ctx!.createGain();
      gain.gain.value = i === 0 ? 0.6 : 0.3; // Root louder than harmonics

      osc.connect(gain);
      gain.connect(this.filter!);
      osc.start();

      this.oscillators.push(osc);
      this.gains.push(gain);
    });
  }

  setMood(mood: AudioMood, transitionTime: number = 2): void {
    if (!this.ctx || !this.filter || !this.lfo || !this.lfoGain || !this.masterGain) return;
    if (mood === this.currentMood) return;

    const config = this.moodConfigs[mood];
    const now = this.ctx.currentTime;

    // Crossfade filter
    this.filter.frequency.setTargetAtTime(config.filterCutoff, now, transitionTime / 3);
    this.filter.Q.setTargetAtTime(config.filterQ, now, transitionTime / 3);

    // Crossfade LFO
    this.lfo.frequency.setTargetAtTime(config.lfoRate, now, transitionTime / 2);
    this.lfoGain.gain.setTargetAtTime(config.lfoDepth, now, transitionTime / 2);

    // Crossfade volume
    this.masterGain.gain.setTargetAtTime(config.volume, now, transitionTime / 3);

    // Recreate oscillators with new intervals (after brief crossfade)
    setTimeout(() => {
      this.createOscillators(mood);
    }, transitionTime * 500);

    this.currentMood = mood;
  }

  setVolume(volume: number): void {
    if (!this.masterGain || !this.ctx) return;
    this.targetVolume = Math.max(0, Math.min(1, volume));
    this.masterGain.gain.setTargetAtTime(
      this.targetVolume * this.moodConfigs[this.currentMood].volume,
      this.ctx.currentTime,
      0.1
    );
  }

  stop(): void {
    if (!this.isRunning) return;

    this.oscillators.forEach(osc => {
      try { osc.stop(); } catch {}
    });
    if (this.lfo) {
      try { this.lfo.stop(); } catch {}
    }

    this.oscillators = [];
    this.gains = [];
    this.isRunning = false;
  }
}

// =============================================================================
// LAYER 2: RHYTHMIC PULSE
// =============================================================================

/**
 * Heartbeat-like pulse that syncs to game tempo.
 * Intensity scales BPM, volume, and filter brightness.
 */
export class RhythmicPulseLayer {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private compressor: DynamicsCompressorNode | null = null;

  private currentBPM = 70;
  private targetBPM = 70;
  private intensity = 0;
  private isRunning = false;
  private nextBeatTime = 0;
  private schedulerInterval: ReturnType<typeof setInterval> | null = null;

  // Pulse configuration
  private config = {
    minBPM: 60,
    maxBPM: 160,
    baseVolume: 0.2,
    maxVolume: 0.4,
    lubFreq: 50,      // Low "lub"
    dubFreq: 40,      // Lower "dub"
    lubDubDelay: 0.15, // Seconds between lub and dub
  };

  start(audioContext: AudioContext, destination: AudioNode): void {
    if (this.isRunning) return;

    this.ctx = audioContext;
    this.isRunning = true;

    // Create compressor for punch
    this.compressor = this.ctx.createDynamicsCompressor();
    this.compressor.threshold.value = -12;
    this.compressor.knee.value = 6;
    this.compressor.ratio.value = 4;
    this.compressor.attack.value = 0.003;
    this.compressor.release.value = 0.1;
    this.compressor.connect(destination);

    // Create master gain
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = this.config.baseVolume;
    this.masterGain.connect(this.compressor);

    this.nextBeatTime = this.ctx.currentTime;

    // Start scheduler
    this.schedulerInterval = setInterval(() => this.scheduler(), 25);
  }

  private scheduler(): void {
    if (!this.ctx || !this.isRunning) return;

    // Interpolate BPM toward target
    this.currentBPM += (this.targetBPM - this.currentBPM) * 0.05;

    const beatInterval = 60 / this.currentBPM;
    const lookahead = 0.1; // Schedule 100ms ahead

    while (this.nextBeatTime < this.ctx.currentTime + lookahead) {
      this.playBeat(this.nextBeatTime);
      this.nextBeatTime += beatInterval;
    }
  }

  private playBeat(time: number): void {
    if (!this.ctx || !this.masterGain) return;

    const volume = this.config.baseVolume +
      (this.config.maxVolume - this.config.baseVolume) * this.intensity;

    // "Lub" - primary beat
    this.playThump(time, this.config.lubFreq, volume);

    // "Dub" - secondary beat (quieter)
    this.playThump(time + this.config.lubDubDelay, this.config.dubFreq, volume * 0.7);
  }

  private playThump(time: number, freq: number, volume: number): void {
    if (!this.ctx || !this.masterGain) return;

    // Sine oscillator for the thump
    const osc = this.ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freq, time);
    osc.frequency.exponentialRampToValueAtTime(freq * 0.5, time + 0.1);

    // Sharp envelope
    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0, time);
    gain.gain.linearRampToValueAtTime(volume, time + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.15);

    // Add sub-bass layer for physical feel
    const subOsc = this.ctx.createOscillator();
    subOsc.type = 'sine';
    subOsc.frequency.value = 30;

    const subGain = this.ctx.createGain();
    subGain.gain.setValueAtTime(0, time);
    subGain.gain.linearRampToValueAtTime(volume * 0.5 * this.intensity, time + 0.02);
    subGain.gain.exponentialRampToValueAtTime(0.001, time + 0.2);

    osc.connect(gain);
    gain.connect(this.masterGain);

    subOsc.connect(subGain);
    subGain.connect(this.masterGain);

    osc.start(time);
    osc.stop(time + 0.2);
    subOsc.start(time);
    subOsc.stop(time + 0.25);
  }

  setIntensity(intensity: number): void {
    this.intensity = Math.max(0, Math.min(1, intensity));
    this.targetBPM = this.config.minBPM +
      (this.config.maxBPM - this.config.minBPM) * this.intensity;
  }

  triggerAccent(): void {
    if (!this.ctx || !this.masterGain) return;

    // Extra punch on next beat
    const now = this.ctx.currentTime;
    this.playThump(now, 60, this.config.maxVolume * 1.5);
  }

  stop(): void {
    if (!this.isRunning) return;

    if (this.schedulerInterval) {
      clearInterval(this.schedulerInterval);
      this.schedulerInterval = null;
    }

    this.isRunning = false;
  }
}

// =============================================================================
// LAYER 3: MELODIC FRAGMENTS
// =============================================================================

/**
 * Short melodic motifs triggered by game events.
 * Uses pentatonic scale for guaranteed consonance.
 */
export class MelodicFragmentLayer {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private _reverb: ConvolverNode | null = null; // Reserved for future reverb implementation
  private reverbGain: GainNode | null = null;
  private dryGain: GainNode | null = null;

  private isRunning = false;
  private activeVoices = 0;
  private maxVoices = 8;
  private lastPlayTime = 0;
  private minInterval = 0.1; // Min time between motifs

  // Motif definitions (scale degrees, durations, volumes)
  private motifs: Record<string, Array<{ degree: number; duration: number; volume: number }>> = {
    kill: [
      { degree: 0, duration: 0.08, volume: 0.8 },
      { degree: 2, duration: 0.08, volume: 0.6 },
      { degree: 4, duration: 0.12, volume: 0.4 },
    ],
    damage: [
      { degree: 3, duration: 0.1, volume: 0.7 },
      { degree: 1, duration: 0.15, volume: 0.5 },
    ],
    levelup: [
      { degree: 0, duration: 0.1, volume: 0.6 },
      { degree: 2, duration: 0.1, volume: 0.7 },
      { degree: 4, duration: 0.1, volume: 0.8 },
      { degree: 5, duration: 0.2, volume: 0.9 },
    ],
    ball: [
      { degree: 0, duration: 0.3, volume: 0.5 },
      { degree: -1, duration: 0.3, volume: 0.6 }, // Tritone below (index -1 = tritone)
    ],
    swarm: [
      { degree: 0, duration: 0.05, volume: 0.4 },
      { degree: 1, duration: 0.05, volume: 0.4 },
      { degree: 0, duration: 0.05, volume: 0.4 },
    ],
  };

  start(audioContext: AudioContext, destination: AudioNode): void {
    if (this.isRunning) return;

    this.ctx = audioContext;
    this.isRunning = true;

    // Create master gain
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0.3;

    // Create dry/wet mix for reverb
    this.dryGain = this.ctx.createGain();
    this.dryGain.gain.value = 0.7;
    this.dryGain.connect(destination);

    this.reverbGain = this.ctx.createGain();
    this.reverbGain.gain.value = 0.3;
    this.reverbGain.connect(destination);

    // Reserved: _reverb will be used when convolution reverb is implemented
    void this._reverb;

    // Create simple reverb using delay feedback
    this.createSimpleReverb();

    this.masterGain.connect(this.dryGain);
  }

  private createSimpleReverb(): void {
    if (!this.ctx || !this.reverbGain) return;

    // Simple delay-based reverb (no ConvolverNode needed)
    const delay1 = this.ctx.createDelay(0.5);
    delay1.delayTime.value = 0.1;

    const delay2 = this.ctx.createDelay(0.5);
    delay2.delayTime.value = 0.2;

    const feedback = this.ctx.createGain();
    feedback.gain.value = 0.3;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 3000;

    // Connect reverb chain
    if (this.masterGain) {
      this.masterGain.connect(delay1);
      delay1.connect(filter);
      filter.connect(feedback);
      feedback.connect(delay2);
      delay2.connect(this.reverbGain);
      delay2.connect(delay1); // Feedback loop
    }
  }

  playMotif(type: keyof typeof this.motifs, rootFreq?: number): void {
    if (!this.ctx || !this.masterGain || !this.isRunning) return;
    if (this.activeVoices >= this.maxVoices) return;

    const now = this.ctx.currentTime;
    if (now - this.lastPlayTime < this.minInterval) return;
    this.lastPlayTime = now;

    const motif = this.motifs[type];
    if (!motif) return;

    // Use provided root or pick from scale
    const root = rootFreq || C_MINOR_PENTATONIC[Math.floor(Math.random() * 5)];

    let time = now;
    motif.forEach((note) => {
      // Calculate frequency from scale degree
      let freq: number;
      if (note.degree === -1) {
        // Special case: tritone for ball motif
        freq = root * INTERVALS.TRITONE;
      } else {
        const octave = Math.floor(note.degree / 5);
        const degree = note.degree % 5;
        freq = C_MINOR_PENTATONIC[degree] * Math.pow(2, octave);
        // Adjust to match root
        freq = freq * (root / C_MINOR_PENTATONIC[0]);
      }

      // Add slight random variation
      freq *= 1 + (Math.random() - 0.5) * 0.02;

      this.playNote(time, freq, note.duration, note.volume);
      time += note.duration * 0.8; // Slight overlap
    });
  }

  private playNote(time: number, freq: number, duration: number, volume: number): void {
    if (!this.ctx || !this.masterGain) return;

    this.activeVoices++;

    // Sine + triangle blend for mellow tone
    const osc1 = this.ctx.createOscillator();
    osc1.type = 'sine';
    osc1.frequency.value = freq;

    const osc2 = this.ctx.createOscillator();
    osc2.type = 'triangle';
    osc2.frequency.value = freq;

    const gain1 = this.ctx.createGain();
    gain1.gain.value = 0.6;

    const gain2 = this.ctx.createGain();
    gain2.gain.value = 0.3;

    // ADSR envelope
    const envelope = this.ctx.createGain();
    envelope.gain.setValueAtTime(0, time);
    envelope.gain.linearRampToValueAtTime(volume * 0.3, time + 0.01); // Attack
    envelope.gain.linearRampToValueAtTime(volume * 0.2, time + duration * 0.3); // Decay
    envelope.gain.setValueAtTime(volume * 0.2, time + duration * 0.7); // Sustain
    envelope.gain.exponentialRampToValueAtTime(0.001, time + duration); // Release

    osc1.connect(gain1);
    osc2.connect(gain2);
    gain1.connect(envelope);
    gain2.connect(envelope);
    envelope.connect(this.masterGain);

    osc1.start(time);
    osc2.start(time);
    osc1.stop(time + duration);
    osc2.stop(time + duration);

    // Decrement voice count after note ends
    setTimeout(() => {
      this.activeVoices = Math.max(0, this.activeVoices - 1);
    }, duration * 1000 + 100);
  }

  setVolume(volume: number): void {
    if (!this.masterGain || !this.ctx) return;
    this.masterGain.gain.setTargetAtTime(
      Math.max(0, Math.min(1, volume)) * 0.3,
      this.ctx.currentTime,
      0.1
    );
  }

  stop(): void {
    this.isRunning = false;
    this.activeVoices = 0;
  }
}

// =============================================================================
// LAYER 4: STINGERS & HITS
// =============================================================================

/**
 * Impact sounds with ASMR-style layering.
 * Crunch + Snap + Thud for satisfying kills.
 */
export class StingerLayer {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private compressor: DynamicsCompressorNode | null = null;

  private isRunning = false;

  start(audioContext: AudioContext, destination: AudioNode): void {
    if (this.isRunning) return;

    this.ctx = audioContext;
    this.isRunning = true;

    // Create compressor for punch
    this.compressor = this.ctx.createDynamicsCompressor();
    this.compressor.threshold.value = -6;
    this.compressor.ratio.value = 8;
    this.compressor.attack.value = 0.001;
    this.compressor.release.value = 0.1;
    this.compressor.connect(destination);

    // Create master gain
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0.5;
    this.masterGain.connect(this.compressor);
  }

  /**
   * Play layered kill sound (ASMR crunch)
   */
  playKill(intensity: number = 1, pitch: number = 1): void {
    if (!this.ctx || !this.masterGain) return;

    const now = this.ctx.currentTime;
    const vol = 0.3 * intensity;

    // Layer 1: CRUNCH (noise burst)
    this.playCrunch(now, vol, pitch);

    // Layer 2: SNAP (high transient)
    this.playSnap(now + 0.005, vol * 0.7, pitch);

    // Layer 3: THUD (low body)
    this.playThud(now + 0.01, vol * 0.5, pitch);
  }

  private playCrunch(time: number, volume: number, pitch: number): void {
    if (!this.ctx || !this.masterGain) return;

    const duration = 0.08;
    const bufferSize = this.ctx.sampleRate * duration;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);

    // Create noise with decay
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;

    // Bandpass filter for crunch character
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.value = 800 * pitch;
    filter.Q.value = 2;

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(volume, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + duration);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);

    noise.start(time);
    noise.stop(time + duration);
  }

  private playSnap(time: number, volume: number, pitch: number): void {
    if (!this.ctx || !this.masterGain) return;

    const duration = 0.04;

    // High sine for snap
    const osc = this.ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(2000 * pitch, time);
    osc.frequency.exponentialRampToValueAtTime(800 * pitch, time + duration);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(volume, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + duration);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start(time);
    osc.stop(time + duration);
  }

  private playThud(time: number, volume: number, pitch: number): void {
    if (!this.ctx || !this.masterGain) return;

    const duration = 0.1;

    // Low sine for body
    const osc = this.ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(100 * pitch, time);
    osc.frequency.exponentialRampToValueAtTime(50 * pitch, time + duration);

    // Add slight distortion
    const distortion = this.ctx.createWaveShaper();
    distortion.curve = this.makeDistortionCurve(20);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(volume, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + duration);

    osc.connect(distortion);
    distortion.connect(gain);
    gain.connect(this.masterGain);

    osc.start(time);
    osc.stop(time + duration);
  }

  /**
   * Play damage stinger
   */
  playDamage(intensity: number = 1): void {
    if (!this.ctx || !this.masterGain) return;

    const now = this.ctx.currentTime;
    const vol = 0.25 * intensity;

    // Dissonant minor 2nd interval
    const osc1 = this.ctx.createOscillator();
    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(80, now);
    osc1.frequency.exponentialRampToValueAtTime(40, now + 0.1);

    const osc2 = this.ctx.createOscillator();
    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(80 * INTERVALS.MINOR_2ND, now);
    osc2.frequency.exponentialRampToValueAtTime(40 * INTERVALS.MINOR_2ND, now + 0.1);

    const gain1 = this.ctx.createGain();
    gain1.gain.setValueAtTime(vol, now);
    gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.1);

    const gain2 = this.ctx.createGain();
    gain2.gain.setValueAtTime(vol * 0.5, now);
    gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.1);

    osc1.connect(gain1);
    osc2.connect(gain2);
    gain1.connect(this.masterGain);
    gain2.connect(this.masterGain);

    osc1.start(now);
    osc2.start(now);
    osc1.stop(now + 0.15);
    osc2.stop(now + 0.15);
  }

  /**
   * Play level up fanfare
   */
  playLevelUp(): void {
    if (!this.ctx || !this.masterGain) return;

    const now = this.ctx.currentTime;
    const notes = [261.63, 329.63, 392.00, 523.25]; // C, E, G, C (octave)

    notes.forEach((freq, i) => {
      const time = now + i * 0.1;

      const osc = this.ctx!.createOscillator();
      osc.type = 'triangle';
      osc.frequency.value = freq;

      const gain = this.ctx!.createGain();
      gain.gain.setValueAtTime(0, time);
      gain.gain.linearRampToValueAtTime(0.2, time + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, time + 0.3);

      osc.connect(gain);
      gain.connect(this.masterGain!);

      osc.start(time);
      osc.stop(time + 0.35);
    });
  }

  private makeDistortionCurve(amount: number): Float32Array {
    const samples = 256;
    const curve = new Float32Array(samples);
    const deg = Math.PI / 180;

    for (let i = 0; i < samples; i++) {
      const x = (i * 2) / samples - 1;
      curve[i] = ((3 + amount) * x * 20 * deg) / (Math.PI + amount * Math.abs(x));
    }

    return curve;
  }

  setVolume(volume: number): void {
    if (!this.masterGain || !this.ctx) return;
    this.masterGain.gain.setTargetAtTime(
      Math.max(0, Math.min(1, volume)) * 0.5,
      this.ctx.currentTime,
      0.05
    );
  }

  stop(): void {
    this.isRunning = false;
  }
}

// =============================================================================
// LAYER 5: SPATIAL AUDIO
// =============================================================================

/**
 * Positional audio with stereo panning and distance attenuation.
 */
export class SpatialAudioLayer {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;

  private isRunning = false;
  private listenerPosition: Vector2 = { x: 0, y: 0 };
  private listenerRange = 600; // Pixels for full attenuation

  start(audioContext: AudioContext, destination: AudioNode): void {
    if (this.isRunning) return;

    this.ctx = audioContext;
    this.isRunning = true;

    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0.4;
    this.masterGain.connect(destination);
  }

  setListenerPosition(position: Vector2): void {
    this.listenerPosition = position;
  }

  setListenerRange(range: number): void {
    this.listenerRange = range;
  }

  /**
   * Play a sound at a world position with spatial effects
   */
  playAtPosition(
    type: 'buzz' | 'hit' | 'alert',
    position: Vector2,
    intensity: number = 1
  ): void {
    if (!this.ctx || !this.masterGain) return;

    // Calculate distance and pan
    const dx = position.x - this.listenerPosition.x;
    const dy = position.y - this.listenerPosition.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Pan: -1 (left) to +1 (right)
    const pan = Math.max(-1, Math.min(1, dx / (this.listenerRange / 2)));

    // Volume attenuation (inverse square with floor)
    const attenuation = Math.max(0.1, 1 / (1 + distance / (this.listenerRange / 3)));
    const volume = 0.3 * intensity * attenuation;

    // Filter cutoff based on distance (far = muffled)
    const filterCutoff = 20000 - (distance / this.listenerRange) * 18000;

    // Create spatial chain
    const panner = this.ctx.createStereoPanner();
    panner.pan.value = pan;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = Math.max(500, filterCutoff);

    const gain = this.ctx.createGain();
    gain.gain.value = volume;

    // Connect chain
    filter.connect(panner);
    panner.connect(gain);
    gain.connect(this.masterGain);

    // Play sound based on type
    switch (type) {
      case 'buzz':
        this.playBuzz(filter, 0.2);
        break;
      case 'hit':
        this.playHit(filter, 0.1);
        break;
      case 'alert':
        this.playAlert(filter, 0.15);
        break;
    }
  }

  private playBuzz(destination: AudioNode, duration: number): void {
    if (!this.ctx) return;

    const osc = this.ctx.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.value = 180 + Math.random() * 40;

    const gain = this.ctx.createGain();
    const now = this.ctx.currentTime;
    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc.connect(gain);
    gain.connect(destination);

    osc.start(now);
    osc.stop(now + duration);
  }

  private playHit(destination: AudioNode, duration: number): void {
    if (!this.ctx) return;

    const bufferSize = this.ctx.sampleRate * duration;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);

    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;

    const now = this.ctx.currentTime;
    noise.connect(destination);
    noise.start(now);
    noise.stop(now + duration);
  }

  private playAlert(destination: AudioNode, duration: number): void {
    if (!this.ctx) return;

    const osc = this.ctx.createOscillator();
    osc.type = 'sine';
    const now = this.ctx.currentTime;
    osc.frequency.setValueAtTime(600, now);
    osc.frequency.exponentialRampToValueAtTime(1200, now + duration);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc.connect(gain);
    gain.connect(destination);

    osc.start(now);
    osc.stop(now + duration);
  }

  stop(): void {
    this.isRunning = false;
  }
}

// =============================================================================
// MASTER ORCHESTRATOR
// =============================================================================

/**
 * Master Audio Orchestrator - Ties all layers together.
 *
 * Manages adaptive mixing based on game state.
 * Implements harmonic memory for tonal coherence.
 * Dispatches game events to appropriate layers.
 */
export class EmergentAudioOrchestrator {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private limiter: DynamicsCompressorNode | null = null;

  // Layers
  private ambientDrone: AmbientDroneLayer;
  private rhythmicPulse: RhythmicPulseLayer;
  private melodicFragments: MelodicFragmentLayer;
  private stingers: StingerLayer;
  private spatialAudio: SpatialAudioLayer;

  // State
  private isRunning = false;
  private currentPhase: GamePhase = 'exploration';
  private intensity = 0;
  private harmonicMemory: HarmonicMemory = {
    lastFrequencies: [],
    currentKey: C_MINOR_PENTATONIC[0],
    tension: 0,
    lastEventTime: 0,
  };

  // Configuration
  private config = {
    maxHarmonicMemory: 5,
    tensionDecayRate: 0.1, // per second
    phaseTransitionTime: 2, // seconds
  };

  constructor() {
    this.ambientDrone = new AmbientDroneLayer();
    this.rhythmicPulse = new RhythmicPulseLayer();
    this.melodicFragments = new MelodicFragmentLayer();
    this.stingers = new StingerLayer();
    this.spatialAudio = new SpatialAudioLayer();
  }

  /**
   * Initialize the orchestrator with an AudioContext
   */
  async start(): Promise<boolean> {
    if (this.isRunning) return true;

    try {
      this.ctx = new (window.AudioContext || (window as any).webkitAudioContext)();

      if (this.ctx.state === 'suspended') {
        await this.ctx.resume();
      }

      // Create master limiter
      this.limiter = this.ctx.createDynamicsCompressor();
      this.limiter.threshold.value = -3;
      this.limiter.knee.value = 6;
      this.limiter.ratio.value = 12;
      this.limiter.attack.value = 0.001;
      this.limiter.release.value = 0.1;
      this.limiter.connect(this.ctx.destination);

      // Create master gain
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.value = 0.7;
      this.masterGain.connect(this.limiter);

      // Start all layers
      this.ambientDrone.start(this.ctx, this.masterGain);
      this.rhythmicPulse.start(this.ctx, this.masterGain);
      this.melodicFragments.start(this.ctx, this.masterGain);
      this.stingers.start(this.ctx, this.masterGain);
      this.spatialAudio.start(this.ctx, this.masterGain);

      this.isRunning = true;
      return true;
    } catch (e) {
      console.warn('EmergentAudioOrchestrator: Failed to start', e);
      return false;
    }
  }

  /**
   * Update with current game state (call each frame)
   */
  update(state: GameAudioState): void {
    if (!this.isRunning || !this.ctx) return;

    // Compute intensity from game state
    this.intensity = this.computeIntensity(state);

    // Determine phase
    const newPhase = this.determinePhase(state);
    if (newPhase !== this.currentPhase) {
      this.transitionToPhase(newPhase);
    }

    // Update layers
    this.rhythmicPulse.setIntensity(this.intensity);
    this.spatialAudio.setListenerPosition(state.playerPosition);

    // Decay harmonic tension
    const now = this.ctx.currentTime;
    const elapsed = now - this.harmonicMemory.lastEventTime;
    this.harmonicMemory.tension = Math.max(
      0,
      this.harmonicMemory.tension - this.config.tensionDecayRate * elapsed
    );
    this.harmonicMemory.lastEventTime = now;
  }

  private computeIntensity(state: GameAudioState): number {
    // Weighted combination of factors
    const healthFactor = 1 - state.playerHealth;
    const enemyFactor = Math.min(1, state.enemyCount / 50);
    const killFactor = Math.min(1, state.recentKills / 10);
    const waveFactor = Math.min(1, state.waveNumber / 10);
    const ballFactor = state.ballPhase !== 'none' ? 0.5 : 0;

    return Math.min(1,
      healthFactor * 0.3 +
      enemyFactor * 0.25 +
      killFactor * 0.2 +
      waveFactor * 0.1 +
      ballFactor * 0.15
    );
  }

  private determinePhase(state: GameAudioState): GamePhase {
    if (state.ballPhase === 'death') return 'death';
    if (state.ballPhase !== 'none') return 'crisis';
    if (state.playerHealth < 0.3) return 'crisis';
    if (state.enemyCount > 20 || this.intensity > 0.6) return 'combat';
    return 'exploration';
  }

  private transitionToPhase(phase: GamePhase): void {
    this.currentPhase = phase;

    // Map game phase to audio mood
    const moodMap: Record<GamePhase, AudioMood> = {
      exploration: 'calm',
      combat: 'tense',
      crisis: 'crisis',
      death: 'death',
    };

    this.ambientDrone.setMood(moodMap[phase], this.config.phaseTransitionTime);

    // Adjust layer volumes based on phase
    switch (phase) {
      case 'exploration':
        this.ambientDrone.setVolume(1);
        this.rhythmicPulse.setIntensity(0.2);
        this.melodicFragments.setVolume(0.5);
        this.stingers.setVolume(0.3);
        break;
      case 'combat':
        this.ambientDrone.setVolume(0.6);
        this.rhythmicPulse.setIntensity(0.6);
        this.melodicFragments.setVolume(0.7);
        this.stingers.setVolume(0.6);
        break;
      case 'crisis':
        this.ambientDrone.setVolume(0.3);
        this.rhythmicPulse.setIntensity(1);
        this.melodicFragments.setVolume(0.4);
        this.stingers.setVolume(0.8);
        break;
      case 'death':
        this.ambientDrone.setVolume(0.5);
        this.rhythmicPulse.setIntensity(0);
        this.melodicFragments.setVolume(0.3);
        this.stingers.setVolume(0.2);
        break;
    }
  }

  // =========================================================================
  // EVENT DISPATCHERS
  // =========================================================================

  /**
   * Call when enemy is killed
   */
  onKill(position: Vector2, comboCount: number = 1): void {
    if (!this.isRunning) return;

    const pitch = 1 + (comboCount - 1) * 0.05;
    const intensity = Math.min(1, 0.5 + comboCount * 0.1);

    this.stingers.playKill(intensity, pitch);
    this.melodicFragments.playMotif('kill', this.getSuggestedFrequency());
    this.rhythmicPulse.triggerAccent();
    this.spatialAudio.playAtPosition('hit', position, intensity);

    // Update harmonic memory
    this.recordFrequency(this.harmonicMemory.currentKey);
  }

  /**
   * Call when player takes damage
   */
  onDamage(amount: number): void {
    if (!this.isRunning) return;

    const intensity = Math.min(1, amount / 50);
    this.stingers.playDamage(intensity);
    this.melodicFragments.playMotif('damage');

    // Increase tension
    this.harmonicMemory.tension = Math.min(1, this.harmonicMemory.tension + 0.2);
  }

  /**
   * Call when player levels up
   */
  onLevelUp(): void {
    if (!this.isRunning) return;

    this.stingers.playLevelUp();
    this.melodicFragments.playMotif('levelup');

    // Reset tension (reward)
    this.harmonicMemory.tension = Math.max(0, this.harmonicMemory.tension - 0.5);
  }

  /**
   * Call when THE BALL phase changes
   */
  onBallPhase(phase: GameAudioState['ballPhase']): void {
    if (!this.isRunning) return;

    if (phase === 'forming' || phase === 'sphere') {
      this.melodicFragments.playMotif('ball');
    }
  }

  /**
   * Play spatial sound at enemy position
   */
  onEnemySound(position: Vector2, type: 'buzz' | 'alert' = 'buzz'): void {
    if (!this.isRunning) return;
    this.spatialAudio.playAtPosition(type, position, this.intensity);
  }

  // =========================================================================
  // HARMONIC MEMORY
  // =========================================================================

  private recordFrequency(freq: number): void {
    this.harmonicMemory.lastFrequencies.push(freq);
    if (this.harmonicMemory.lastFrequencies.length > this.config.maxHarmonicMemory) {
      this.harmonicMemory.lastFrequencies.shift();
    }

    // Shift key based on recent frequencies
    if (this.harmonicMemory.lastFrequencies.length >= 3) {
      const avg = this.harmonicMemory.lastFrequencies.reduce((a, b) => a + b, 0) /
        this.harmonicMemory.lastFrequencies.length;

      // Find nearest scale tone
      let nearest = C_MINOR_PENTATONIC[0];
      let nearestDist = Infinity;
      for (const tone of C_MINOR_PENTATONIC) {
        const dist = Math.abs(tone - avg);
        if (dist < nearestDist) {
          nearestDist = dist;
          nearest = tone;
        }
      }
      this.harmonicMemory.currentKey = nearest;
    }
  }

  /**
   * Get a frequency that harmonizes with recent sounds
   */
  private getSuggestedFrequency(): number {
    const base = this.harmonicMemory.currentKey;

    // Choose interval based on tension
    if (this.harmonicMemory.tension > 0.7) {
      // High tension: use tritone or minor 2nd
      return base * (Math.random() > 0.5 ? INTERVALS.TRITONE : INTERVALS.MINOR_2ND);
    } else if (this.harmonicMemory.tension > 0.4) {
      // Medium tension: use minor 3rd or minor 7th
      return base * (Math.random() > 0.5 ? INTERVALS.MINOR_3RD : INTERVALS.MINOR_7TH);
    } else {
      // Low tension: use perfect 5th or octave
      return base * (Math.random() > 0.5 ? INTERVALS.PERFECT_5TH : INTERVALS.OCTAVE);
    }
  }

  // =========================================================================
  // CONTROL
  // =========================================================================

  setMasterVolume(volume: number): void {
    if (!this.masterGain || !this.ctx) return;
    this.masterGain.gain.setTargetAtTime(
      Math.max(0, Math.min(1, volume)),
      this.ctx.currentTime,
      0.1
    );
  }

  stop(): void {
    if (!this.isRunning) return;

    this.ambientDrone.stop();
    this.rhythmicPulse.stop();
    this.melodicFragments.stop();
    this.stingers.stop();
    this.spatialAudio.stop();

    if (this.ctx) {
      this.ctx.close();
      this.ctx = null;
    }

    this.isRunning = false;
  }

  isActive(): boolean {
    return this.isRunning;
  }

  getIntensity(): number {
    return this.intensity;
  }

  getCurrentPhase(): GamePhase {
    return this.currentPhase;
  }

  getHarmonicTension(): number {
    return this.harmonicMemory.tension;
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

let orchestratorInstance: EmergentAudioOrchestrator | null = null;

/**
 * Get the singleton emergent audio orchestrator
 */
export function getEmergentAudioOrchestrator(): EmergentAudioOrchestrator {
  if (!orchestratorInstance) {
    orchestratorInstance = new EmergentAudioOrchestrator();
  }
  return orchestratorInstance;
}

/**
 * Start the emergent audio system
 */
export async function startEmergentAudio(): Promise<boolean> {
  return getEmergentAudioOrchestrator().start();
}

/**
 * Stop the emergent audio system
 */
export function stopEmergentAudio(): void {
  if (orchestratorInstance) {
    orchestratorInstance.stop();
    orchestratorInstance = null;
  }
}

export default getEmergentAudioOrchestrator;
