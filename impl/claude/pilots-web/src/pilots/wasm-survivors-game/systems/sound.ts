/**
 * WASM Survivors - Sound System (DD-5)
 *
 * Web Audio API procedural synthesis for game feedback.
 * All sounds generated on-the-fly, no file loading.
 *
 * Target: < 100ms latency from trigger to audible sound.
 *
 * Sounds:
 * - kill: short pop (80ms)
 * - damage: low thump (100ms)
 * - levelup: ascending arpeggio (300ms)
 * - synergy: shimmer chime (200ms)
 * - wave: horn sweep (400ms)
 * - dash: whoosh (150ms)
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

// =============================================================================
// Types
// =============================================================================

// DD-16: Added bassDrop and heartbeat for clutch moments
export type SoundId = 'kill' | 'damage' | 'levelup' | 'synergy' | 'wave' | 'dash' | 'bassDrop' | 'heartbeat';

export interface SoundEngine {
  play(sound: SoundId, options?: SoundOptions): void;
  setMasterVolume(volume: number): void;
  mute(): void;
  unmute(): void;
  isMuted(): boolean;
  isReady(): boolean;
}

export interface SoundOptions {
  volume?: number;  // 0-1, default 1
  pitch?: number;   // multiplier, default 1
}

// =============================================================================
// Sound Engine Factory
// =============================================================================

/**
 * Create a sound engine instance
 * Must be called after user interaction (click/keypress) due to autoplay policies
 */
export function createSoundEngine(): SoundEngine {
  let audioContext: AudioContext | null = null;
  let masterGain: GainNode | null = null;
  let muted = false;
  let masterVolume = 0.5;

  // Lazy initialization (requires user gesture)
  const ensureContext = (): boolean => {
    if (audioContext) return true;

    try {
      audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
      masterGain = audioContext.createGain();
      masterGain.gain.value = masterVolume;
      masterGain.connect(audioContext.destination);
      return true;
    } catch {
      console.warn('Web Audio API not available');
      return false;
    }
  };

  // Resume context if suspended (autoplay policy)
  const ensureRunning = async (): Promise<boolean> => {
    if (!audioContext) return false;
    if (audioContext.state === 'suspended') {
      try {
        await audioContext.resume();
      } catch {
        return false;
      }
    }
    return true;
  };

  return {
    play(sound: SoundId, options: SoundOptions = {}) {
      if (!ensureContext()) return;
      if (muted) return;
      ensureRunning();

      const ctx = audioContext!;
      const master = masterGain!;
      const volume = options.volume ?? 1;
      const pitch = options.pitch ?? 1;

      switch (sound) {
        case 'kill':
          playKillSound(ctx, master, volume, pitch);
          break;
        case 'damage':
          playDamageSound(ctx, master, volume);
          break;
        case 'levelup':
          playLevelUpSound(ctx, master, volume);
          break;
        case 'synergy':
          playSynergySound(ctx, master, volume);
          break;
        case 'wave':
          playWaveSound(ctx, master, volume);
          break;
        case 'dash':
          playDashSound(ctx, master, volume);
          break;
        // DD-16: Clutch moment sounds
        case 'bassDrop':
          playBassDropSound(ctx, master, volume);
          break;
        case 'heartbeat':
          playHeartbeatSound(ctx, master, volume);
          break;
      }
    },

    setMasterVolume(volume: number) {
      masterVolume = Math.max(0, Math.min(1, volume));
      if (masterGain) {
        masterGain.gain.value = masterVolume;
      }
    },

    mute() {
      muted = true;
    },

    unmute() {
      muted = false;
    },

    isMuted() {
      return muted;
    },

    isReady() {
      return audioContext !== null && audioContext.state === 'running';
    },
  };
}

// =============================================================================
// Sound Generators
// =============================================================================

/**
 * Kill sound: Short pop with white noise burst
 * Duration: ~80ms
 */
function playKillSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number,
  pitch: number
) {
  const now = ctx.currentTime;
  const duration = 0.08;

  // White noise burst
  const bufferSize = ctx.sampleRate * duration;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize); // Decay envelope
  }

  const noise = ctx.createBufferSource();
  noise.buffer = buffer;

  // Bandpass filter for pitched pop
  const filter = ctx.createBiquadFilter();
  filter.type = 'bandpass';
  filter.frequency.value = 800 * pitch;
  filter.Q.value = 2;

  // Gain envelope
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume * 0.4, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect
  noise.connect(filter);
  filter.connect(gain);
  gain.connect(output);

  noise.start(now);
  noise.stop(now + duration);
}

/**
 * Damage sound: Low frequency thump
 * Duration: ~100ms
 */
function playDamageSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 0.1;

  // Low sine oscillator
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(80, now);
  osc.frequency.exponentialRampToValueAtTime(40, now + duration);

  // Distortion for punch
  const distortion = ctx.createWaveShaper();
  distortion.curve = makeDistortionCurve(50);

  // Gain envelope
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume * 0.5, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect
  osc.connect(distortion);
  distortion.connect(gain);
  gain.connect(output);

  osc.start(now);
  osc.stop(now + duration);
}

/**
 * Level up sound: Ascending arpeggio (C-E-G)
 * Duration: ~300ms
 */
function playLevelUpSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const notes = [261.63, 329.63, 392.0]; // C4, E4, G4
  const noteDuration = 0.08;
  const noteGap = 0.05;

  notes.forEach((freq, i) => {
    const startTime = now + i * (noteDuration + noteGap);

    // Sawtooth oscillator for brighter sound
    const osc = ctx.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.value = freq;

    // Low-pass filter to smooth
    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 2000;

    // Gain envelope
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0, startTime);
    gain.gain.linearRampToValueAtTime(volume * 0.3, startTime + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.001, startTime + noteDuration);

    // Connect
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(output);

    osc.start(startTime);
    osc.stop(startTime + noteDuration);
  });
}

/**
 * Synergy sound: Shimmer chime with delay
 * Duration: ~200ms
 */
function playSynergySound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 0.2;

  // High frequency sine for shimmer
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(1200, now);
  osc.frequency.exponentialRampToValueAtTime(800, now + duration);

  // Second oscillator for shimmer effect
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(1400, now);
  osc2.frequency.exponentialRampToValueAtTime(900, now + duration);

  // Gain envelopes
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume * 0.2, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  const gain2 = ctx.createGain();
  gain2.gain.setValueAtTime(volume * 0.15, now);
  gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect
  osc.connect(gain);
  osc2.connect(gain2);
  gain.connect(output);
  gain2.connect(output);

  osc.start(now);
  osc2.start(now + 0.02); // Slight delay for shimmer
  osc.stop(now + duration);
  osc2.stop(now + duration + 0.02);
}

/**
 * Wave sound: Low horn sweep up
 * Duration: ~400ms
 */
function playWaveSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 0.4;

  // Low sine sweep
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(100, now);
  osc.frequency.exponentialRampToValueAtTime(200, now + duration * 0.3);
  osc.frequency.exponentialRampToValueAtTime(150, now + duration);

  // Harmonic for richness
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(200, now);
  osc2.frequency.exponentialRampToValueAtTime(400, now + duration * 0.3);
  osc2.frequency.exponentialRampToValueAtTime(300, now + duration);

  // Gain envelopes
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0, now);
  gain.gain.linearRampToValueAtTime(volume * 0.3, now + 0.05);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  const gain2 = ctx.createGain();
  gain2.gain.setValueAtTime(0, now);
  gain2.gain.linearRampToValueAtTime(volume * 0.15, now + 0.05);
  gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect
  osc.connect(gain);
  osc2.connect(gain2);
  gain.connect(output);
  gain2.connect(output);

  osc.start(now);
  osc2.start(now);
  osc.stop(now + duration);
  osc2.stop(now + duration);
}

/**
 * Dash sound: Filtered noise whoosh
 * Duration: ~150ms
 */
function playDashSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 0.15;

  // White noise
  const bufferSize = ctx.sampleRate * duration;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = Math.random() * 2 - 1;
  }

  const noise = ctx.createBufferSource();
  noise.buffer = buffer;

  // Sweeping highpass filter for whoosh
  const filter = ctx.createBiquadFilter();
  filter.type = 'highpass';
  filter.frequency.setValueAtTime(500, now);
  filter.frequency.exponentialRampToValueAtTime(2000, now + duration * 0.3);
  filter.frequency.exponentialRampToValueAtTime(800, now + duration);
  filter.Q.value = 1;

  // Gain envelope
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0, now);
  gain.gain.linearRampToValueAtTime(volume * 0.3, now + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect
  noise.connect(filter);
  filter.connect(gain);
  gain.connect(output);

  noise.start(now);
  noise.stop(now + duration);
}

// =============================================================================
// DD-16: Clutch Moment Sounds
// =============================================================================

/**
 * Bass drop sound: Deep sub-bass with pitch drop
 * Duration: ~500ms
 * Used for full/medium clutch moments
 */
function playBassDropSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 0.5;

  // Deep sub-bass oscillator
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(80, now);
  osc.frequency.exponentialRampToValueAtTime(30, now + duration);

  // Second oscillator for harmonic richness
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(160, now);
  osc2.frequency.exponentialRampToValueAtTime(60, now + duration);

  // Heavy distortion for impact
  const distortion = ctx.createWaveShaper();
  distortion.curve = makeDistortionCurve(100);

  // Low-pass filter to keep it rumbly
  const filter = ctx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.value = 150;
  filter.Q.value = 0.7;

  // Gain envelope - hit hard, decay slow
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume * 0.8, now);
  gain.gain.exponentialRampToValueAtTime(volume * 0.6, now + 0.05);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  const gain2 = ctx.createGain();
  gain2.gain.setValueAtTime(volume * 0.3, now);
  gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect
  osc.connect(distortion);
  distortion.connect(filter);
  filter.connect(gain);
  gain.connect(output);

  osc2.connect(gain2);
  gain2.connect(output);

  osc.start(now);
  osc2.start(now);
  osc.stop(now + duration);
  osc2.stop(now + duration);
}

/**
 * Heartbeat sound: Double thump like a heart
 * Duration: ~400ms
 * Used for critical health state
 */
function playHeartbeatSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;

  // First thump (lub)
  playHeartbeatThump(ctx, output, volume * 0.8, now);

  // Second thump (dub) - slightly quieter, after 150ms
  playHeartbeatThump(ctx, output, volume * 0.6, now + 0.15);
}

function playHeartbeatThump(
  ctx: AudioContext,
  output: GainNode,
  volume: number,
  startTime: number
) {
  const duration = 0.1;

  // Low sine for the thump
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(50, startTime);
  osc.frequency.exponentialRampToValueAtTime(30, startTime + duration);

  // Gain envelope - sharp attack, quick decay
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0, startTime);
  gain.gain.linearRampToValueAtTime(volume * 0.6, startTime + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

  // Connect
  osc.connect(gain);
  gain.connect(output);

  osc.start(startTime);
  osc.stop(startTime + duration);
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Create a distortion curve for the waveshaper
 */
function makeDistortionCurve(amount: number): Float32Array {
  const samples = 256;
  const curve = new Float32Array(samples);
  const deg = Math.PI / 180;

  for (let i = 0; i < samples; i++) {
    const x = (i * 2) / samples - 1;
    curve[i] = ((3 + amount) * x * 20 * deg) / (Math.PI + amount * Math.abs(x));
  }

  return curve;
}

// =============================================================================
// Singleton Instance
// =============================================================================

let soundEngineInstance: SoundEngine | null = null;

/**
 * Get the singleton sound engine instance
 */
export function getSoundEngine(): SoundEngine {
  if (!soundEngineInstance) {
    soundEngineInstance = createSoundEngine();
  }
  return soundEngineInstance;
}

export default getSoundEngine;
