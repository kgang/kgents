/**
 * WASM Survivors - KENT Fugue React Hook
 *
 * Integrates the K-E-N-T musical cryptogram fugue system with the game.
 * Provides real-time procedural counterpoint in C# minor.
 *
 * KENT = B# - F# - D# - A (two tritones - maximum tension!)
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  FugueStateData,
  FuguePhase,
  ScheduledNote,
  PercussionNote,
  VoiceRegister,
  createFugueState,
  updateKentFugue,
  KENT_SEMITONES,
  semitoneToFrequency,
} from '../systems/kent-fugue';
import {
  KentDrumPitchEngine,
  DrumPitchSet,
  MusicalPosition,
  GameState as PitchGameState,
  GamePhase as PitchGamePhase,
} from '../systems/kent-drum-pitch';

// =============================================================================
// WEB AUDIO SYNTHESIZER
// =============================================================================

interface VoiceSynth {
  oscillator: OscillatorNode | null;
  gain: GainNode;
  filter: BiquadFilterNode;
}

/**
 * Polyphonic synthesizer for fugue voices
 */
class FugueSynthesizer {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private compressor: DynamicsCompressorNode | null = null;
  private reverb: ConvolverNode | null = null;
  private reverbGain: GainNode | null = null;

  private voices: Map<VoiceRegister, VoiceSynth> = new Map();
  private scheduledNotes: Map<string, { osc: OscillatorNode; gain: GainNode }> = new Map();

  // KENT Drum Pitch Engine for surreal, emergent drum pitches
  private pitchEngine: KentDrumPitchEngine = new KentDrumPitchEngine();
  private currentPitches: DrumPitchSet = {};
  private musicalPosition: MusicalPosition = {
    beatPosition: 0,
    barPosition: 0,
    sixteenthPosition: 0,
    kentPosition: 0,
    beatInPhrase: 0,
    barInWave: 0,
    totalBars: 0,
  };

  async start(): Promise<boolean> {
    try {
      this.ctx = new AudioContext();

      // Master chain - KENT Fugue is THE music system, give it presence
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.value = 0.24; // 40% softer than game SFX (0.4 * 0.6)

      this.compressor = this.ctx.createDynamicsCompressor();
      this.compressor.threshold.value = -18;
      this.compressor.knee.value = 12;
      this.compressor.ratio.value = 4;
      this.compressor.attack.value = 0.003;
      this.compressor.release.value = 0.25;

      // Reverb
      this.reverb = await this.createReverb();
      this.reverbGain = this.ctx.createGain();
      this.reverbGain.gain.value = 0.25;

      // Connect master chain
      this.masterGain.connect(this.compressor);
      this.compressor.connect(this.ctx.destination);

      if (this.reverb) {
        this.masterGain.connect(this.reverb);
        this.reverb.connect(this.reverbGain);
        this.reverbGain.connect(this.ctx.destination);
      }

      // Create voice synths
      for (const register of ['soprano', 'alto', 'tenor', 'bass'] as VoiceRegister[]) {
        const gain = this.ctx.createGain();
        gain.gain.value = 0;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.value = this.getFilterFreqForVoice(register);
        filter.Q.value = 1;

        filter.connect(gain);
        gain.connect(this.masterGain);

        this.voices.set(register, {
          oscillator: null,
          gain,
          filter,
        });
      }

      return true;
    } catch (e) {
      console.error('Failed to start FugueSynthesizer:', e);
      return false;
    }
  }

  private getFilterFreqForVoice(register: VoiceRegister): number {
    switch (register) {
      case 'soprano': return 4000;
      case 'alto': return 3000;
      case 'tenor': return 2500;
      case 'bass': return 2000;
    }
  }

  private async createReverb(): Promise<ConvolverNode | null> {
    if (!this.ctx) return null;

    try {
      const reverb = this.ctx.createConvolver();
      const sampleRate = this.ctx.sampleRate;
      const length = sampleRate * 1.5; // 1.5 second reverb (cathedral-like)
      const impulse = this.ctx.createBuffer(2, length, sampleRate);

      for (let channel = 0; channel < 2; channel++) {
        const data = impulse.getChannelData(channel);
        for (let i = 0; i < length; i++) {
          // Exponential decay with early reflections
          const earlyReflection = i < sampleRate * 0.05 ? 0.5 : 0;
          data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, 1.5) + earlyReflection * (Math.random() * 2 - 1);
        }
      }

      reverb.buffer = impulse;
      return reverb;
    } catch {
      return null;
    }
  }

  /**
   * Get instrument timbre definition for each voice register.
   * Uses additive synthesis with proper harmonic series for rich, warm tones.
   *
   * HARMONIC SERIES ratios (fundamental = 1):
   * - String-like: strong odd harmonics (1, 3, 5, 7...)
   * - Wind-like: emphasis on fundamental with soft upper partials
   * - Brass-like: all harmonics present
   */
  private getTimbreForVoice(voice: VoiceRegister): {
    harmonics: { ratio: number; amplitude: number }[];
    vibratoRate: number;
    vibratoDepth: number;
    attackShape: 'soft' | 'medium' | 'sharp';
    octaveDouble: boolean;
    detuneAmount: number;
  } {
    switch (voice) {
      case 'bass':
        // Cello-like: warm, rich low end with prominent odd harmonics
        // TEXTURE BOOST: More harmonics and vibrato for expressive depth
        return {
          harmonics: [
            { ratio: 1, amplitude: 1.0 },      // Fundamental
            { ratio: 2, amplitude: 0.6 },      // Octave (boosted)
            { ratio: 3, amplitude: 0.45 },     // 5th above octave (boosted)
            { ratio: 4, amplitude: 0.3 },      // 2 octaves (boosted)
            { ratio: 5, amplitude: 0.2 },      // Major 3rd (boosted)
            { ratio: 6, amplitude: 0.15 },     // 5th (boosted)
            { ratio: 7, amplitude: 0.1 },      // Minor 7th (new)
            { ratio: 8, amplitude: 0.06 },     // 3 octaves (new)
            { ratio: 0.5, amplitude: 0.3 },    // Sub-octave for depth (boosted)
          ],
          vibratoRate: 4.5 + Math.random() * 1.5,
          vibratoDepth: 0.008,   // 2.6x vibrato (was 0.003)
          attackShape: 'soft',
          octaveDouble: true,
          detuneAmount: 6,       // 3x detune (was 2)
        };

      case 'tenor':
        // Viola/French horn hybrid: balanced, mellow
        // TEXTURE BOOST: Richer harmonic content and expressive vibrato
        return {
          harmonics: [
            { ratio: 1, amplitude: 1.0 },
            { ratio: 2, amplitude: 0.7 },      // Boosted
            { ratio: 3, amplitude: 0.5 },      // Boosted
            { ratio: 4, amplitude: 0.35 },     // Boosted
            { ratio: 5, amplitude: 0.25 },     // Boosted
            { ratio: 6, amplitude: 0.18 },     // Boosted
            { ratio: 7, amplitude: 0.12 },     // Boosted
            { ratio: 8, amplitude: 0.08 },     // New
            { ratio: 9, amplitude: 0.05 },     // New
          ],
          vibratoRate: 5.0 + Math.random() * 1.5,
          vibratoDepth: 0.01,    // 2.5x vibrato (was 0.004)
          attackShape: 'medium',
          octaveDouble: false,
          detuneAmount: 8,       // 2.7x detune (was 3)
        };

      case 'alto':
        // Clarinet-like: hollow, odd harmonics prominent
        // TEXTURE BOOST: Expressive vibrato, richer odd harmonics
        return {
          harmonics: [
            { ratio: 1, amplitude: 1.0 },
            { ratio: 3, amplitude: 0.65 },     // Odd harmonics stronger (boosted)
            { ratio: 5, amplitude: 0.45 },     // Boosted
            { ratio: 7, amplitude: 0.3 },      // Boosted
            { ratio: 9, amplitude: 0.18 },     // Boosted
            { ratio: 11, amplitude: 0.1 },     // New
            { ratio: 2, amplitude: 0.2 },      // Weak even harmonics (boosted)
            { ratio: 4, amplitude: 0.12 },     // Boosted
            { ratio: 6, amplitude: 0.06 },     // New
          ],
          vibratoRate: 5.5 + Math.random() * 1.8,
          vibratoDepth: 0.012,   // 2.4x vibrato (was 0.005)
          attackShape: 'medium',
          octaveDouble: false,
          detuneAmount: 10,      // 2.5x detune (was 4)
        };

      case 'soprano':
        // Flute/recorder-like: pure, fundamental-heavy
        // TEXTURE BOOST: More shimmer and breath in upper partials
        return {
          harmonics: [
            { ratio: 1, amplitude: 1.0 },      // Strong fundamental
            { ratio: 2, amplitude: 0.4 },      // Soft octave (boosted)
            { ratio: 3, amplitude: 0.25 },     // Gentle 5th (boosted)
            { ratio: 4, amplitude: 0.15 },     // Boosted
            { ratio: 5, amplitude: 0.1 },      // Boosted
            { ratio: 6, amplitude: 0.06 },     // New
            { ratio: 7, amplitude: 0.03 },     // New
          ],
          vibratoRate: 6.0 + Math.random() * 2,
          vibratoDepth: 0.014,   // 2.3x vibrato (was 0.006)
          attackShape: 'sharp',
          octaveDouble: false,
          detuneAmount: 12,      // 2.4x detune (was 5)
        };
    }
  }

  /**
   * Play a scheduled note with rich additive synthesis.
   * Creates warm, blending tones using multiple harmonics and subtle detuning.
   *
   * TIMING FIX: Notes are scheduled with a small lookahead buffer to prevent
   * audio glitches from late scheduling. The Web Audio API performs best when
   * notes are scheduled slightly ahead of the current time.
   */
  playNote(note: ScheduledNote): void {
    if (!this.ctx || !this.masterGain) return;

    const now = this.ctx.currentTime;
    // TIMING FIX: Add a small lookahead buffer to prevent clipping from late scheduling
    // This gives the audio system time to prepare oscillators before playback
    const LOOKAHEAD_TIME = 0.025; // 25ms buffer for smooth scheduling
    const startTime = now + LOOKAHEAD_TIME;
    const noteId = `${note.voice}-${startTime}-${Math.random()}`;
    const timbre = this.getTimbreForVoice(note.voice);

    // Master gain for this note
    const noteGain = this.ctx.createGain();
    noteGain.gain.setValueAtTime(0, startTime);

    // Gentle low-pass filter for warmth (removes harshness)
    const warmthFilter = this.ctx.createBiquadFilter();
    warmthFilter.type = 'lowpass';
    warmthFilter.frequency.value = this.getFilterFreqForVoice(note.voice);
    warmthFilter.Q.value = 0.7; // Low Q for smooth rolloff

    // High-pass to remove mud
    const clarityFilter = this.ctx.createBiquadFilter();
    clarityFilter.type = 'highpass';
    clarityFilter.frequency.value = note.voice === 'bass' ? 40 : 80;
    clarityFilter.Q.value = 0.5;

    // Envelope parameters based on articulation
    let attackTime: number;
    let sustainLevel: number;
    let releaseTime: number;

    switch (note.articulation) {
      case 'staccato':
        attackTime = 0.008;
        sustainLevel = 0.7;
        releaseTime = 0.08;
        break;
      case 'accent':
      case 'marcato':
        attackTime = 0.012;
        sustainLevel = 1.0;
        releaseTime = 0.12;
        break;
      case 'tenuto':
        attackTime = 0.05;
        sustainLevel = 0.9;
        releaseTime = 0.2;
        break;
      case 'legato':
      default:
        attackTime = 0.035;
        sustainLevel = 0.85;
        releaseTime = 0.15;
    }

    // Adjust attack based on timbre
    if (timbre.attackShape === 'soft') attackTime *= 1.5;
    if (timbre.attackShape === 'sharp') attackTime *= 0.6;

    const peakVelocity = note.velocity * 0.25; // 40% louder vs drums (was 0.18)
    const sustainVelocity = peakVelocity * sustainLevel;

    // ADSR envelope with smooth curves (using startTime for proper scheduling)
    noteGain.gain.setValueAtTime(0.0001, startTime);
    noteGain.gain.exponentialRampToValueAtTime(peakVelocity, startTime + attackTime);
    noteGain.gain.setValueAtTime(sustainVelocity, startTime + attackTime + 0.02);

    const releaseStart = note.articulation === 'staccato'
      ? startTime + note.duration * 0.4
      : startTime + note.duration - releaseTime;

    noteGain.gain.setValueAtTime(sustainVelocity, Math.max(startTime + attackTime + 0.03, releaseStart));
    noteGain.gain.exponentialRampToValueAtTime(0.0001, startTime + note.duration + 0.05);

    // Create shared vibrato LFO for all partials (humanizes the sound)
    const vibratoLFO = this.ctx.createOscillator();
    vibratoLFO.type = 'sine';
    vibratoLFO.frequency.value = timbre.vibratoRate;

    // Oscillators for each harmonic partial
    const oscillators: OscillatorNode[] = [];

    for (const partial of timbre.harmonics) {
      const osc = this.ctx.createOscillator();
      osc.type = 'sine'; // Pure sines for clean additive synthesis

      const partialFreq = note.frequency * partial.ratio;

      // Slight random detune for richness (±cents)
      const detuneCents = (Math.random() - 0.5) * timbre.detuneAmount * 2;
      osc.detune.value = detuneCents;
      osc.frequency.setValueAtTime(partialFreq, startTime);

      // Individual gain for this partial
      const partialGain = this.ctx.createGain();
      // Scale amplitude by harmonic number for natural rolloff
      const scaledAmplitude = partial.amplitude / (timbre.harmonics.length * 0.5);
      partialGain.gain.value = scaledAmplitude;

      // Connect vibrato to frequency (depth varies by partial)
      const vibratoGain = this.ctx.createGain();
      vibratoGain.gain.value = partialFreq * timbre.vibratoDepth * (1 / partial.ratio);
      vibratoLFO.connect(vibratoGain);
      vibratoGain.connect(osc.frequency);

      // Connect partial through filters
      osc.connect(partialGain);
      partialGain.connect(warmthFilter);

      osc.start(startTime);
      osc.stop(startTime + note.duration + 0.15);
      oscillators.push(osc);
    }

    // Octave doubling for bass (adds depth)
    if (timbre.octaveDouble && note.frequency > 60) {
      const subOsc = this.ctx.createOscillator();
      subOsc.type = 'sine';
      subOsc.frequency.setValueAtTime(note.frequency * 0.5, startTime);
      subOsc.detune.value = (Math.random() - 0.5) * 3;

      const subGain = this.ctx.createGain();
      subGain.gain.value = 0.15; // Subtle sub-octave

      subOsc.connect(subGain);
      subGain.connect(warmthFilter);

      subOsc.start(startTime);
      subOsc.stop(startTime + note.duration + 0.15);
      oscillators.push(subOsc);
    }

    // Start vibrato with slight delay (more natural)
    vibratoLFO.start(startTime + attackTime * 0.5);
    vibratoLFO.stop(startTime + note.duration + 0.1);

    // Connect filter chain
    warmthFilter.connect(clarityFilter);
    clarityFilter.connect(noteGain);
    noteGain.connect(this.masterGain);

    // Track for cleanup (just track first oscillator)
    this.scheduledNotes.set(noteId, { osc: oscillators[0], gain: noteGain });

    oscillators[0].onended = () => {
      this.scheduledNotes.delete(noteId);
    };
  }

  /**
   * Set master volume (KENT Fugue is THE music system)
   */
  setVolume(volume: number): void {
    if (this.masterGain && this.ctx) {
      this.masterGain.gain.setTargetAtTime(
        Math.max(0, Math.min(1, volume)) * 0.24, // 40% softer than game SFX
        this.ctx.currentTime,
        0.1
      );
    }
  }

  /**
   * Update musical position for the KENT Drum Pitch Engine
   */
  updateMusicalPosition(
    barNumber: number,
    sixteenthInBar: number,
    _tempo: number,
    _waveNumber: number
  ): void {
    const sixteenthsPerBeat = 4;

    this.musicalPosition = {
      beatPosition: (sixteenthInBar % sixteenthsPerBeat) / sixteenthsPerBeat,
      barPosition: sixteenthInBar / 16,
      sixteenthPosition: sixteenthInBar,
      kentPosition: Math.floor(sixteenthInBar / 4) % 4, // KENT position cycles every beat
      beatInPhrase: sixteenthInBar % 16, // 4-bar phrase
      barInWave: barNumber % 32,
      totalBars: barNumber,
    };
  }

  /**
   * Calculate drum pitches for the current musical context
   */
  calculateDrumPitches(
    drumType: PercussionNote['type'],
    gameIntensity: number,
    gamePhase: 'exploration' | 'combat' | 'crisis' | 'death',
    waveNumber: number
  ): void {
    const pitchGameState: PitchGameState = {
      intensity: gameIntensity,
      phase: gamePhase as PitchGamePhase,
      waveNumber,
    };

    // Create triggers based on drum type
    const triggers = {
      kick: drumType === 'kick',
      snare: drumType === 'snare',
      hihat: drumType === 'hihat',
      hihatOpenness: 0.3, // Default openness
      tom: drumType === 'tom' ? 1 as const : undefined, // Mid tom default
      crash: drumType === 'crash',
      ride: drumType === 'ride',
      beatsSinceLastSnare: 4,
    };

    this.currentPitches = this.pitchEngine.calculatePitches(
      pitchGameState,
      this.musicalPosition,
      triggers
    );
  }

  /**
   * Play a percussion note with AUDIBLE volume levels.
   * Dynamic Rock/Funk drums with crash and ride cymbal support.
   * TIMING FIX: Uses same lookahead buffer as melodic notes for consistency.
   */
  playPercussion(note: PercussionNote): void {
    if (!this.ctx || !this.masterGain) return;

    const now = this.ctx.currentTime;
    // TIMING FIX: Use consistent lookahead for percussion as well
    const LOOKAHEAD_TIME = 0.025; // 25ms buffer
    const startTime = now + LOOKAHEAD_TIME;

    // VOLUME BOOST: Percussion needs to cut through the mix
    // Ghost notes get reduced volume for dynamics
    const isGhost = (note as { ghost?: boolean }).ghost === true;
    const volumeMultiplier = isGhost ? 0.35 : 1.0;

    switch (note.type) {
      case 'kick': {
        // KENT-driven kick: breathes between tritone poles
        const kickPitch = this.currentPitches.kick;
        const startPitch = kickPitch?.startPitch ?? 100;
        const endPitch = kickPitch?.endPitch ?? 45;
        const subPitch = kickPitch?.subPitch ?? 30;
        const duration = kickPitch?.duration ?? note.duration;

        const osc = this.ctx.createOscillator();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(startPitch, startTime);
        osc.frequency.exponentialRampToValueAtTime(endPitch, startTime + duration * 0.8);

        // Sub oscillator at KENT-derived pitch
        const subOsc = this.ctx.createOscillator();
        subOsc.type = 'sine';
        subOsc.frequency.setValueAtTime(subPitch, startTime);

        // Click transient for attack
        const clickBuffer = this.ctx.createBuffer(1, this.ctx.sampleRate * 0.01, this.ctx.sampleRate);
        const clickData = clickBuffer.getChannelData(0);
        for (let i = 0; i < clickData.length; i++) {
          clickData[i] = (Math.random() * 2 - 1) * Math.exp(-i / (clickData.length * 0.1));
        }
        const click = this.ctx.createBufferSource();
        click.buffer = clickBuffer;
        const clickFilter = this.ctx.createBiquadFilter();
        clickFilter.type = 'bandpass';
        clickFilter.frequency.value = 3000;
        clickFilter.Q.value = 2;

        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(note.velocity * 1.785 * volumeMultiplier, startTime); // 30% softer
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

        const subGain = this.ctx.createGain();
        subGain.gain.setValueAtTime(note.velocity * 0.945 * volumeMultiplier, startTime); // 30% softer
        subGain.gain.exponentialRampToValueAtTime(0.001, startTime + duration * 1.2);

        const clickGain = this.ctx.createGain();
        clickGain.gain.setValueAtTime(note.velocity * 1.05 * volumeMultiplier, startTime); // 30% softer
        clickGain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.015);

        osc.connect(gain);
        subOsc.connect(subGain);
        click.connect(clickFilter);
        clickFilter.connect(clickGain);

        gain.connect(this.masterGain);
        subGain.connect(this.masterGain);
        clickGain.connect(this.masterGain);

        osc.start(startTime);
        subOsc.start(startTime);
        click.start(startTime);
        osc.stop(startTime + duration + 0.05);
        subOsc.stop(startTime + duration + 0.1);
        break;
      }

      case 'hihat': {
        // KENT-driven hi-hat: fibonacci-modulated shimmer field
        // FIX: Proper dissipation to prevent white noise buildup
        const hihatPitch = this.currentPitches.hihat;
        const centerFreq = Math.min(hihatPitch?.centerFrequency ?? 5000, 12000); // Cap frequency
        const shimmerFreq = hihatPitch?.shimmerFreq ?? 0.025;
        const shimmerDepth = Math.min(hihatPitch?.shimmerDepth ?? 0.045, 0.03); // Reduced max depth
        const bandwidth = hihatPitch?.bandwidth ?? 2000;

        const actualDuration = Math.max(0.08, note.duration * 1.5);
        const bufferSize = Math.ceil(this.ctx.sampleRate * actualDuration);
        const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = noiseBuffer.getChannelData(0);

        for (let i = 0; i < bufferSize; i++) {
          // Main envelope decay
          const decay = Math.exp(-i / (bufferSize * 0.35)); // Faster decay (was 0.45)
          // Shimmer has its own faster decay to prevent accumulation
          const shimmerDecay = Math.exp(-i / (bufferSize * 0.15));
          // KENT-driven procedural shimmer with randomized pitch drift
          const pitchDrift = shimmerFreq + Math.sin(i * 0.001) * 0.005; // Reduced drift range
          const shimmer = Math.sin(i * pitchDrift) * shimmerDepth * shimmerDecay;
          // Noise dominates, shimmer is subtle coloring
          const noise_val = (Math.random() * 2 - 1) * 0.85;
          const shimmer_val = shimmer * 0.15; // Shimmer at 15% mix
          data[i] = (noise_val + shimmer_val) * decay;
        }

        const noise = this.ctx.createBufferSource();
        noise.buffer = noiseBuffer;

        // KENT-derived center frequency
        const hpFilter = this.ctx.createBiquadFilter();
        hpFilter.type = 'highpass';
        hpFilter.frequency.value = Math.max(Math.min(centerFreq * 0.6, 8000), 4000);

        // KENT resonant peaks - reduced gain and capped Q to prevent feedback
        const peakFilter = this.ctx.createBiquadFilter();
        peakFilter.type = 'peaking';
        peakFilter.frequency.value = hihatPitch?.resonantPeaks?.[0]?.frequency ?? 8000;
        peakFilter.gain.value = 2; // Reduced from 4
        peakFilter.Q.value = Math.min(hihatPitch?.resonantPeaks?.[0]?.q ?? 2, 3); // Cap Q at 3

        const lpFilter = this.ctx.createBiquadFilter();
        lpFilter.type = 'lowpass';
        lpFilter.frequency.value = Math.min(centerFreq + bandwidth, 14000);

        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(note.velocity * 2.2 * volumeMultiplier, startTime);
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + actualDuration);

        noise.connect(hpFilter);
        hpFilter.connect(peakFilter);
        peakFilter.connect(lpFilter);
        lpFilter.connect(gain);
        gain.connect(this.masterGain);
        noise.start(startTime);
        noise.stop(startTime + actualDuration + 0.02);
        break;
      }

      case 'snare': {
        // KENT-driven snare: phase witness with memory-influenced pitch
        const snarePitch = this.currentPitches.snare;
        const bodyPitch = snarePitch?.bodyPitch ?? 200;
        const wirePitch = snarePitch?.wirePitch ?? 280;
        const pitchEnv = snarePitch?.pitchEnvelope;

        // Body (tonal component) at KENT-derived pitch
        const osc = this.ctx.createOscillator();
        osc.type = 'triangle';
        // Pitch envelope: slight rise during attack (impossible physics)
        const startBodyPitch = pitchEnv?.start ?? bodyPitch * 0.95;
        const endBodyPitch = pitchEnv?.end ?? bodyPitch;
        osc.frequency.setValueAtTime(startBodyPitch, startTime);
        osc.frequency.linearRampToValueAtTime(bodyPitch * 1.02, startTime + 0.02);
        osc.frequency.linearRampToValueAtTime(endBodyPitch, startTime + 0.08);

        const bodyGain = this.ctx.createGain();
        bodyGain.gain.setValueAtTime(note.velocity * 0.65 * volumeMultiplier, startTime);
        bodyGain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.12);

        // Snap (high-end transient)
        const snapBuffer = this.ctx.createBuffer(1, this.ctx.sampleRate * 0.02, this.ctx.sampleRate);
        const snapData = snapBuffer.getChannelData(0);
        for (let i = 0; i < snapData.length; i++) {
          snapData[i] = (Math.random() * 2 - 1) * Math.exp(-i / (snapData.length * 0.15));
        }
        const snap = this.ctx.createBufferSource();
        snap.buffer = snapBuffer;
        const snapFilter = this.ctx.createBiquadFilter();
        snapFilter.type = 'highpass';
        snapFilter.frequency.value = 2000;

        const snapGain = this.ctx.createGain();
        snapGain.gain.setValueAtTime(note.velocity * 0.35 * volumeMultiplier, startTime);
        snapGain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.04);

        // Snare wires at KENT tritone shimmer
        const wireBufferSize = this.ctx.sampleRate * 0.15;
        const wireBuffer = this.ctx.createBuffer(1, wireBufferSize, this.ctx.sampleRate);
        const wireData = wireBuffer.getChannelData(0);
        for (let i = 0; i < wireBufferSize; i++) {
          wireData[i] = (Math.random() * 2 - 1) * Math.exp(-i / (wireBufferSize * 0.4));
        }
        const wires = this.ctx.createBufferSource();
        wires.buffer = wireBuffer;

        const wireFilter = this.ctx.createBiquadFilter();
        wireFilter.type = 'bandpass';
        wireFilter.frequency.value = wirePitch * 12; // Wire shimmer at tritone
        wireFilter.Q.value = 1.5;

        const wireGain = this.ctx.createGain();
        wireGain.gain.setValueAtTime(note.velocity * 0.5 * volumeMultiplier, startTime);
        wireGain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.12);

        osc.connect(bodyGain);
        snap.connect(snapFilter);
        snapFilter.connect(snapGain);
        wires.connect(wireFilter);
        wireFilter.connect(wireGain);

        bodyGain.connect(this.masterGain);
        snapGain.connect(this.masterGain);
        wireGain.connect(this.masterGain);

        osc.start(startTime);
        snap.start(startTime);
        wires.start(startTime);
        osc.stop(startTime + 0.15);
        break;
      }

      case 'tom': {
        // KENT-driven tom: fibonacci spiral through KENT space
        const tomPitch = this.currentPitches.tom;
        const basePitch = tomPitch?.pitch ?? 150;
        const glissando = tomPitch?.glissandoEnvelope;
        const glissandoStart = glissando?.start ?? basePitch * 1.2;

        const osc = this.ctx.createOscillator();
        osc.type = 'sine';
        // Phantom glissando from previous tom (impossible technique)
        osc.frequency.setValueAtTime(glissandoStart, startTime);
        osc.frequency.exponentialRampToValueAtTime(basePitch * 0.5, startTime + note.duration * 0.6);

        // Harmonic follows KENT
        const harmOsc = this.ctx.createOscillator();
        harmOsc.type = 'triangle';
        harmOsc.frequency.setValueAtTime(basePitch * 0.8, startTime);
        harmOsc.frequency.exponentialRampToValueAtTime(basePitch * 0.4, startTime + note.duration * 0.5);

        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(note.velocity * 1.47 * volumeMultiplier, startTime); // 30% softer
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + note.duration);

        const harmGain = this.ctx.createGain();
        harmGain.gain.setValueAtTime(note.velocity * 0.175 * volumeMultiplier, startTime); // 30% softer
        harmGain.gain.exponentialRampToValueAtTime(0.001, startTime + note.duration * 0.8);

        // KENT sympathetic strings (subtle resonance at KENT frequencies)
        const sympathetic = tomPitch?.sympatheticStrings;
        if (sympathetic && sympathetic.length > 0) {
          const sympOsc = this.ctx.createOscillator();
          sympOsc.type = 'sine';
          sympOsc.frequency.value = sympathetic[0].frequency;
          const sympGain = this.ctx.createGain();
          sympGain.gain.setValueAtTime(sympathetic[0].level * 0.7 * note.velocity * volumeMultiplier, startTime); // 30% softer
          sympGain.gain.exponentialRampToValueAtTime(0.001, startTime + sympathetic[0].decay);
          sympOsc.connect(sympGain);
          sympGain.connect(this.masterGain);
          sympOsc.start(startTime);
          sympOsc.stop(startTime + sympathetic[0].decay + 0.1);
        }

        osc.connect(gain);
        harmOsc.connect(harmGain);
        gain.connect(this.masterGain);
        harmGain.connect(this.masterGain);

        osc.start(startTime);
        harmOsc.start(startTime);
        osc.stop(startTime + note.duration + 0.05);
        harmOsc.stop(startTime + note.duration + 0.05);
        break;
      }

      case 'crash': {
        // KENT-driven crash: void eruption releasing accumulated tension
        const crashPitch = this.currentPitches.crash;
        const centerPitch = crashPitch?.centerPitch ?? 1100;
        const pitchDrop = crashPitch?.pitchDrop ?? 200;
        const kentWeights = crashPitch?.partialWeights ?? [0.25, 0.25, 0.25, 0.25];
        const ringModFreq = crashPitch?.ringModFreq ?? 277;

        const bufferSize = Math.ceil(this.ctx.sampleRate * Math.max(0.5, note.duration));
        const noiseBuffer = this.ctx.createBuffer(2, bufferSize, this.ctx.sampleRate);

        // Stereo noise with KENT-weighted spectral content
        for (let channel = 0; channel < 2; channel++) {
          const data = noiseBuffer.getChannelData(channel);
          for (let i = 0; i < bufferSize; i++) {
            const decay = Math.exp(-i / (bufferSize * 0.4));
            // KENT-weighted harmonic shimmer
            const shimmer = kentWeights.reduce((acc, w, idx) => {
              return acc + Math.sin(i * 0.005 * (idx + 1)) * w;
            }, 0) * 0.3 + 1;
            data[i] = (Math.random() * 2 - 1) * decay * shimmer;
          }
        }

        const noise = this.ctx.createBufferSource();
        noise.buffer = noiseBuffer;

        // Ring modulation at dominant KENT frequency
        const ringMod = this.ctx.createOscillator();
        ringMod.type = 'sine';
        ringMod.frequency.value = ringModFreq;
        const ringGain = this.ctx.createGain();
        ringGain.gain.value = 0.15; // Subtle ring mod

        // Center frequency with pitch drop
        const hpFilter = this.ctx.createBiquadFilter();
        hpFilter.type = 'highpass';
        hpFilter.frequency.setValueAtTime(centerPitch * 0.3, startTime);

        const peakFilter = this.ctx.createBiquadFilter();
        peakFilter.type = 'peaking';
        peakFilter.frequency.setValueAtTime(centerPitch, startTime);
        peakFilter.frequency.exponentialRampToValueAtTime(
          centerPitch * Math.pow(2, -pitchDrop / 1200), // cents to ratio
          startTime + note.duration * 0.8
        );
        // REDUCED HARSHNESS: Lower peak gain and Q for smoother crash
        peakFilter.gain.value = 4; // Reduced from 8 dB
        peakFilter.Q.value = 1.0;  // Reduced from 1.5 - wider, smoother peak

        const gain = this.ctx.createGain();
        // REDUCED HARSHNESS: Lower overall crash volume
        gain.gain.setValueAtTime(note.velocity * 0.7 * volumeMultiplier, startTime); // Reduced from 1.2
        gain.gain.exponentialRampToValueAtTime(0.001, startTime + note.duration);

        // REDUCED HARSHNESS: Lowpass filter to tame harsh high frequencies
        const lpFilter = this.ctx.createBiquadFilter();
        lpFilter.type = 'lowpass';
        lpFilter.frequency.value = 6000; // Cut harsh highs above 6kHz
        lpFilter.Q.value = 0.5; // Gentle rolloff

        noise.connect(hpFilter);
        hpFilter.connect(peakFilter);
        ringMod.connect(ringGain);
        ringGain.connect(peakFilter.frequency); // FM on peak frequency
        peakFilter.connect(lpFilter);
        lpFilter.connect(gain);
        gain.connect(this.masterGain);

        noise.start(startTime);
        ringMod.start(startTime);
        noise.stop(startTime + note.duration + 0.1);
        ringMod.stop(startTime + note.duration + 0.1);
        break;
      }

      case 'ride': {
        // KENT-driven ride: phase accumulator with evolving pitch memory
        const ridePitch = this.currentPitches.ride;
        const bellPitch = ridePitch?.bellPitch ?? 2200;
        const bowPitch = ridePitch?.bowPitch ?? 1500;
        const pingFreq = ridePitch?.pingFrequency ?? 2200;
        const pingQ = ridePitch?.pingResonance ?? 20;
        const washCenter = ridePitch?.washCenter ?? 1800;

        const bufferSize = Math.ceil(this.ctx.sampleRate * Math.max(0.2, note.duration));
        const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = noiseBuffer.getChannelData(0);

        for (let i = 0; i < bufferSize; i++) {
          const decay = Math.exp(-i / (bufferSize * 0.5));
          // Harmonic content at KENT-derived frequency
          const harmonic = Math.sin(i * (bowPitch / this.ctx.sampleRate) * 2 * Math.PI) * 0.3;
          data[i] = ((Math.random() * 2 - 1) + harmonic) * decay;
        }

        const noise = this.ctx.createBufferSource();
        noise.buffer = noiseBuffer;

        const hpFilter = this.ctx.createBiquadFilter();
        hpFilter.type = 'highpass';
        hpFilter.frequency.value = bowPitch * 0.5;

        // KENT-derived ping resonance
        const pingFilter = this.ctx.createBiquadFilter();
        pingFilter.type = 'peaking';
        pingFilter.frequency.value = pingFreq;
        pingFilter.gain.value = 6;
        pingFilter.Q.value = pingQ / 10;

        // Wash center at accumulated pitch
        const washFilter = this.ctx.createBiquadFilter();
        washFilter.type = 'peaking';
        washFilter.frequency.value = washCenter;
        washFilter.gain.value = 3;
        washFilter.Q.value = 0.5;

        // Waveshaper for distortion
        const distortion = this.ctx.createWaveShaper();
        const curve = new Float32Array(256);
        for (let i = 0; i < 256; i++) {
          const x = (i / 128) - 1;
          curve[i] = Math.tanh(x * 2);
        }
        distortion.curve = curve;
        distortion.oversample = '2x';

        // Bell at KENT-derived pitch (tritone above kick)
        const bellOsc = this.ctx.createOscillator();
        bellOsc.type = 'triangle';
        bellOsc.frequency.value = bellPitch;

        const bellGain = this.ctx.createGain();
        bellGain.gain.setValueAtTime(note.velocity * 0.08 * volumeMultiplier, startTime);
        bellGain.gain.exponentialRampToValueAtTime(0.001, startTime + note.duration * 0.3);

        const noiseGain = this.ctx.createGain();
        noiseGain.gain.setValueAtTime(note.velocity * 0.8 * volumeMultiplier, startTime);
        noiseGain.gain.exponentialRampToValueAtTime(0.001, startTime + note.duration);

        // Chain with KENT resonances
        noise.connect(hpFilter);
        hpFilter.connect(pingFilter);
        pingFilter.connect(washFilter);
        washFilter.connect(distortion);
        distortion.connect(noiseGain);
        bellOsc.connect(bellGain);

        noiseGain.connect(this.masterGain);
        bellGain.connect(this.masterGain);

        noise.start(startTime);
        bellOsc.start(startTime);
        noise.stop(startTime + note.duration + 0.05);
        bellOsc.stop(startTime + note.duration * 0.5);
        break;
      }
    }
  }

  /**
   * Stop all sound
   */
  stop(): void {
    for (const { osc, gain } of this.scheduledNotes.values()) {
      if (this.ctx) {
        gain.gain.cancelScheduledValues(this.ctx.currentTime);
        gain.gain.setValueAtTime(gain.gain.value, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.1);
        osc.stop(this.ctx.currentTime + 0.15);
      }
    }
    this.scheduledNotes.clear();

    if (this.ctx) {
      this.ctx.close();
      this.ctx = null;
    }
  }

  isActive(): boolean {
    return this.ctx !== null && this.ctx.state === 'running';
  }
}

// =============================================================================
// REACT HOOK
// =============================================================================

/** Names for the 8 pre-generated KENT variations */
export const KENT_VARIATION_NAMES = [
  'Original Statement',
  'Tonal Answer',
  'Inversion',
  'Retrograde',
  'Augmentation',
  'Diminution',
  'Chromatic',
  'Sequence',
] as const;

export interface UseKentFugueResult {
  /** Start the fugue system (creates fresh state if not already running) */
  start: () => Promise<boolean>;

  /** Stop the fugue system */
  stop: () => void;

  /** Reset the fugue state to initial (call when game restarts) */
  reset: () => void;

  /** Update with game state each frame */
  update: (
    deltaTime: number,
    gameIntensity: number,
    gamePhase: 'exploration' | 'combat' | 'crisis' | 'death',
    waveNumber?: number  // NEW: wave-based voice progression
  ) => void;

  /** Set master volume (0-1) */
  setVolume: (volume: number) => void;

  /** Whether the system is running */
  isRunning: boolean;

  /** Current fugue phase */
  currentPhase: FuguePhase;

  /** Current tempo in BPM */
  tempo: number;

  /** The KENT motif frequencies for visualization */
  kentMotif: number[];

  /** Current dynamic arc phase */
  arcPhase: 'building' | 'climax' | 'resolving' | 'breathing';

  /** Global dynamic level (0-1) */
  globalDynamic: number;

  /** Current variation index (0-7) for the pre-generated KENT theme variations */
  currentVariation: number;

  /** Human-readable name of the current variation */
  currentVariationName: string;
}

export function useKentFugue(): UseKentFugueResult {
  const synthRef = useRef<FugueSynthesizer | null>(null);
  const stateRef = useRef<FugueStateData>(createFugueState());
  const [isRunning, setIsRunning] = useState(false);
  const [currentPhase, setCurrentPhase] = useState<FuguePhase>('silence');
  const [tempo, setTempo] = useState(72);
  const [arcPhase, setArcPhase] = useState<'building' | 'climax' | 'resolving' | 'breathing'>('breathing');
  const [globalDynamic, setGlobalDynamic] = useState(0.4);
  const [currentVariation, setCurrentVariation] = useState(0);

  // KENT motif frequencies for visualization
  const kentMotif = KENT_SEMITONES.map(s => semitoneToFrequency(s, 4));

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      synthRef.current?.stop();
    };
  }, []);

  /**
   * Reset the fugue state to initial values.
   * Call this when the game restarts to ensure fresh musical journey.
   * Does NOT stop the audio context - just resets musical state.
   */
  const reset = useCallback((): void => {
    // Create completely fresh fugue state
    stateRef.current = createFugueState();

    // Reset all UI state to initial values
    setCurrentPhase('silence');
    setTempo(72);
    setArcPhase('breathing');
    setGlobalDynamic(0.4);
    setCurrentVariation(0);

    console.log('[KENT Fugue] State reset for new game');
  }, []);

  const start = useCallback(async (): Promise<boolean> => {
    // If already running, just reset the state for a fresh musical journey
    if (synthRef.current?.isActive()) {
      reset();
      return true;
    }

    const synth = new FugueSynthesizer();
    const success = await synth.start();

    if (success) {
      synthRef.current = synth;
      stateRef.current = createFugueState();
      setIsRunning(true);
    }

    return success;
  }, [reset]);

  const stop = useCallback((): void => {
    synthRef.current?.stop();
    synthRef.current = null;
    setIsRunning(false);
    // Also reset state so next start is clean
    stateRef.current = createFugueState();
    setCurrentPhase('silence');
    setTempo(72);
    setArcPhase('breathing');
    setGlobalDynamic(0.4);
    setCurrentVariation(0);
  }, []);

  const update = useCallback((
    deltaTime: number,
    gameIntensity: number,
    gamePhase: 'exploration' | 'combat' | 'crisis' | 'death',
    waveNumber: number = 1  // NEW: wave-based voice progression
  ): void => {
    const synth = synthRef.current;
    if (!synth || !synth.isActive()) return;

    // Update fugue state with wave number
    const { newState, scheduledNotes, percussionNotes } = updateKentFugue(
      stateRef.current,
      deltaTime,
      gameIntensity,
      gamePhase,
      waveNumber
    );

    stateRef.current = newState;

    // Update musical position for KENT Drum Pitch Engine
    // Calculate bar and sixteenth from currentBeat
    const sixteenthsPerBeat = 4;
    const currentGlobalSixteenth = Math.floor(newState.currentBeat * sixteenthsPerBeat);
    const sixteenthInBar = currentGlobalSixteenth % 16;
    const barNumber = Math.floor(currentGlobalSixteenth / 16);
    synth.updateMusicalPosition(barNumber, sixteenthInBar, newState.tempo, waveNumber);

    // Schedule melodic notes for playback
    for (const note of scheduledNotes) {
      synth.playNote(note);
    }

    // Schedule percussion with KENT-derived pitches
    for (const percNote of percussionNotes) {
      // Calculate sublime, surreal pitches for this drum hit
      synth.calculateDrumPitches(percNote.type, gameIntensity, gamePhase, waveNumber);
      synth.playPercussion(percNote);
    }

    // Update React state (compare before setting to prevent infinite re-render)
    setCurrentPhase(prev => prev !== newState.phase ? newState.phase : prev);
    setTempo(prev => prev !== newState.tempo ? newState.tempo : prev);
    setArcPhase(prev => prev !== newState.arcPhase ? newState.arcPhase : prev);
    setGlobalDynamic(prev => prev !== newState.globalDynamic ? newState.globalDynamic : prev);
    setCurrentVariation(prev => prev !== newState.currentVariationIndex ? newState.currentVariationIndex : prev);
  }, []);

  const setVolume = useCallback((volume: number): void => {
    synthRef.current?.setVolume(volume);
  }, []);

  return {
    start,
    stop,
    reset,
    update,
    setVolume,
    isRunning,
    currentPhase,
    tempo,
    kentMotif,
    arcPhase,
    globalDynamic,
    currentVariation,
    currentVariationName: KENT_VARIATION_NAMES[currentVariation] || 'Unknown',
  };
}

export default useKentFugue;
