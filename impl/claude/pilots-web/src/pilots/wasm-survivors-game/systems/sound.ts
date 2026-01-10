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
// NEW: Added alarmPheromone and ballForming for JUICE Appendix E
// Graze: Sharp tick sound for near-miss, pitch increases with chain
// Apex Strike: charge, swing, hit, miss, powerup sounds
export type SoundId =
  | 'kill' | 'damage' | 'levelup' | 'synergy' | 'wave' | 'dash'
  | 'bassDrop' | 'heartbeat'
  | 'alarmPheromone' | 'ballForming' | 'ballSilence' | 'massacre'
  | 'graze'
  | 'charge' | 'swing' | 'hit' | 'miss' | 'powerup';

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
        // NEW: Appendix E JUICE audio cues
        case 'alarmPheromone':
          playAlarmPheromoneSound(ctx, master, volume);
          break;
        case 'ballForming':
          playBallFormingSound(ctx, master, volume);
          break;
        case 'ballSilence':
          playBallSilenceSound(ctx, master, volume);
          break;
        case 'massacre':
          playMassacreSound(ctx, master, volume);
          break;
        case 'graze':
          playGrazeSound(ctx, master, volume, pitch);
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
 * Kill sound: Short pop with white noise burst + minor 7th tonal layer
 * Duration: ~80ms
 * Musical: Minor 7th interval (ratio 9/5 = 1.8) adds jazzy richness
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

  // Connect noise path
  noise.connect(filter);
  filter.connect(gain);
  gain.connect(output);

  // Musical: Add minor 7th tonal layer for richness (ratio 9/5 = 1.8)
  const baseFreq = 200 * pitch;
  const minor7thFreq = baseFreq * 1.8; // Minor 7th interval

  // Base tone
  const oscBase = ctx.createOscillator();
  oscBase.type = 'sine';
  oscBase.frequency.value = baseFreq;

  // Minor 7th tone
  const oscMinor7th = ctx.createOscillator();
  oscMinor7th.type = 'sine';
  oscMinor7th.frequency.value = minor7thFreq;

  // Tonal gain (quieter than noise, 30% of main volume)
  const tonalGain = ctx.createGain();
  tonalGain.gain.setValueAtTime(volume * 0.12, now);
  tonalGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  const minor7thGain = ctx.createGain();
  minor7thGain.gain.setValueAtTime(volume * 0.08, now); // Even quieter
  minor7thGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  oscBase.connect(tonalGain);
  oscMinor7th.connect(minor7thGain);
  tonalGain.connect(output);
  minor7thGain.connect(output);

  noise.start(now);
  oscBase.start(now);
  oscMinor7th.start(now);
  noise.stop(now + duration);
  oscBase.stop(now + duration);
  oscMinor7th.stop(now + duration);
}

/**
 * Damage sound: Soft thump with minor 2nd dissonance
 * Duration: ~100ms
 * Musical: Minor 2nd interval (ratio 16/15 ~ 1.067) creates tension
 * Run 038: Reduced distortion and volume for softer feel
 */
function playDamageSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 0.1;

  // Low sine oscillator (base 80Hz) - no distortion for cleaner sound
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(80, now);
  osc.frequency.exponentialRampToValueAtTime(40, now + duration);

  // Minor 2nd oscillator (85Hz - creates tension without harshness)
  const oscMinor2nd = ctx.createOscillator();
  oscMinor2nd.type = 'sine';
  oscMinor2nd.frequency.setValueAtTime(80 * (16 / 15), now); // ~85.3Hz
  oscMinor2nd.frequency.exponentialRampToValueAtTime(40 * (16 / 15), now + duration);

  // Mild distortion (reduced from 50 to 15)
  const distortion = ctx.createWaveShaper();
  distortion.curve = makeDistortionCurve(15);

  const distortion2 = ctx.createWaveShaper();
  distortion2.curve = makeDistortionCurve(15);

  // Gain envelope for main oscillator (reduced from 0.5 to 0.25)
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume * 0.25, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Gain envelope for minor 2nd (reduced proportionally)
  const gainMinor2nd = ctx.createGain();
  gainMinor2nd.gain.setValueAtTime(volume * 0.1, now);
  gainMinor2nd.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect main path
  osc.connect(distortion);
  distortion.connect(gain);
  gain.connect(output);

  // Connect minor 2nd path
  oscMinor2nd.connect(distortion2);
  distortion2.connect(gainMinor2nd);
  gainMinor2nd.connect(output);

  osc.start(now);
  oscMinor2nd.start(now);
  osc.stop(now + duration);
  oscMinor2nd.stop(now + duration);
}

/**
 * Level up sound: Ascending arpeggio (C-E-G-Bb dominant 7th)
 * Duration: ~400ms
 * Musical: C7 chord (dominant 7th) is more satisfying than simple major triad
 */
function playLevelUpSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  // C4, E4, G4, Bb4 - Dominant 7th chord for satisfying resolution tension
  const notes = [261.63, 329.63, 392.0, 466.16];
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
 * Bass drop sound: Deep sub-bass with pitch drop + tritone dissonance
 * Duration: ~500ms
 * Used for full/medium clutch moments
 * Musical: Tritone (ratio 45/32 ~ 1.414) adds unstable, dreadful tension
 */
function playBassDropSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 0.5;

  // Deep sub-bass oscillator (80Hz -> 30Hz)
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(80, now);
  osc.frequency.exponentialRampToValueAtTime(30, now + duration);

  // Second oscillator for harmonic richness (octave above)
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(160, now);
  osc2.frequency.exponentialRampToValueAtTime(60, now + duration);

  // Tritone oscillator (113Hz -> 42Hz) - devil's interval for dread
  const oscTritone = ctx.createOscillator();
  oscTritone.type = 'sine';
  oscTritone.frequency.setValueAtTime(80 * (45 / 32), now); // ~112.5Hz
  oscTritone.frequency.exponentialRampToValueAtTime(30 * (45 / 32), now + duration); // ~42Hz

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

  // Tritone gain (40% of main for supporting dissonance)
  const gainTritone = ctx.createGain();
  gainTritone.gain.setValueAtTime(volume * 0.32, now);
  gainTritone.gain.exponentialRampToValueAtTime(volume * 0.24, now + 0.05);
  gainTritone.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect main path
  osc.connect(distortion);
  distortion.connect(filter);
  filter.connect(gain);
  gain.connect(output);

  // Connect harmonic
  osc2.connect(gain2);
  gain2.connect(output);

  // Connect tritone
  oscTritone.connect(gainTritone);
  gainTritone.connect(output);

  osc.start(now);
  osc2.start(now);
  oscTritone.start(now);
  osc.stop(now + duration);
  osc2.stop(now + duration);
  oscTritone.stop(now + duration);
}

/**
 * Heartbeat sound: Double thump like a heart with minor 2nd unease
 * Duration: ~400ms
 * Used for critical health state
 * Musical: Minor 2nd (ratio 16/15 ~ 1.067) offset creates wobble/beating effect
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

  // Low sine for the thump (base 50Hz)
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(50, startTime);
  osc.frequency.exponentialRampToValueAtTime(30, startTime + duration);

  // Minor 2nd oscillator (53Hz) - slightly offset for beating/wobble
  const oscMinor2nd = ctx.createOscillator();
  oscMinor2nd.type = 'sine';
  oscMinor2nd.frequency.setValueAtTime(50 * (16 / 15), startTime + 0.005); // ~53Hz, slightly delayed
  oscMinor2nd.frequency.exponentialRampToValueAtTime(30 * (16 / 15), startTime + duration);

  // Gain envelope - sharp attack, quick decay
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0, startTime);
  gain.gain.linearRampToValueAtTime(volume * 0.6, startTime + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

  // Minor 2nd gain (40% of main for unease)
  const gainMinor2nd = ctx.createGain();
  gainMinor2nd.gain.setValueAtTime(0, startTime + 0.005);
  gainMinor2nd.gain.linearRampToValueAtTime(volume * 0.24, startTime + 0.015);
  gainMinor2nd.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

  // Connect
  osc.connect(gain);
  oscMinor2nd.connect(gainMinor2nd);
  gain.connect(output);
  gainMinor2nd.connect(output);

  osc.start(startTime);
  oscMinor2nd.start(startTime + 0.005); // Slight offset for wobble
  osc.stop(startTime + duration);
  oscMinor2nd.stop(startTime + duration + 0.005);
}

// =============================================================================
// NEW: Appendix E JUICE Audio Cues
// =============================================================================

/**
 * Alarm Pheromone Sound: Rising frequency sweep with tritone layer
 * "freqStart: 400Hz -> freqEnd: 2000Hz over 300ms"
 * Plays when scouts alert the colony
 * Musical: Tritone (ratio 45/32 ~ 1.414) adds unstable, warning tension
 */
function playAlarmPheromoneSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 0.3; // 300ms

  // Rising frequency sweep (400Hz -> 2000Hz)
  const osc = ctx.createOscillator();
  osc.type = 'sawtooth';
  osc.frequency.setValueAtTime(400, now);
  osc.frequency.exponentialRampToValueAtTime(2000, now + duration);

  // Second oscillator for richness
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(450, now);
  osc2.frequency.exponentialRampToValueAtTime(2200, now + duration);

  // Tritone oscillator (566Hz -> 2828Hz) - devil's interval for warning
  const oscTritone = ctx.createOscillator();
  oscTritone.type = 'sine';
  oscTritone.frequency.setValueAtTime(400 * (45 / 32), now); // ~566Hz
  oscTritone.frequency.exponentialRampToValueAtTime(2000 * (45 / 32), now + duration); // ~2828Hz

  // Band-pass filter for bee-like buzz quality
  const filter = ctx.createBiquadFilter();
  filter.type = 'bandpass';
  filter.frequency.setValueAtTime(800, now);
  filter.frequency.exponentialRampToValueAtTime(1500, now + duration);
  filter.Q.value = 2;

  // Gain envelope - urgent attack
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(0, now);
  gain.gain.linearRampToValueAtTime(volume * 0.4, now + 0.02);
  gain.gain.setValueAtTime(volume * 0.4, now + duration * 0.7);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  const gain2 = ctx.createGain();
  gain2.gain.setValueAtTime(volume * 0.2, now);
  gain2.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Tritone gain (35% of main for supporting warning dissonance)
  const gainTritone = ctx.createGain();
  gainTritone.gain.setValueAtTime(0, now);
  gainTritone.gain.linearRampToValueAtTime(volume * 0.14, now + 0.02);
  gainTritone.gain.setValueAtTime(volume * 0.14, now + duration * 0.7);
  gainTritone.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Connect main path
  osc.connect(filter);
  filter.connect(gain);
  gain.connect(output);

  // Connect richness layer
  osc2.connect(gain2);
  gain2.connect(output);

  // Connect tritone layer
  oscTritone.connect(gainTritone);
  gainTritone.connect(output);

  osc.start(now);
  osc2.start(now);
  oscTritone.start(now);
  osc.stop(now + duration);
  osc2.stop(now + duration);
  oscTritone.stop(now + duration);
}

/**
 * Ball Forming Sound: Building buzz crescendo
 * "buzzVolume: 0.3 -> buzzPeak: 1.0"
 * Creates mounting dread as THE BALL forms
 */
function playBallFormingSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 2.0; // Long crescendo

  // Multi-layered buzz
  const frequencies = [150, 180, 210]; // Chord of buzzes
  const oscillators: OscillatorNode[] = [];
  const gains: GainNode[] = [];

  frequencies.forEach((freq, i) => {
    const osc = ctx.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(freq, now);
    // Slight pitch rise for tension
    osc.frequency.exponentialRampToValueAtTime(freq * 1.2, now + duration);

    // Tremolo for vibration feel
    const tremolo = ctx.createGain();
    const tremoloOsc = ctx.createOscillator();
    tremoloOsc.type = 'sine';
    tremoloOsc.frequency.value = 30 + i * 5; // Different rates

    tremoloOsc.connect(tremolo.gain);
    tremolo.gain.setValueAtTime(0.7, now);

    const gain = ctx.createGain();
    // Crescendo from quiet to loud
    gain.gain.setValueAtTime(volume * 0.1, now);
    gain.gain.linearRampToValueAtTime(volume * 0.3, now + duration);

    osc.connect(tremolo);
    tremolo.connect(gain);
    gain.connect(output);

    tremoloOsc.start(now);
    tremoloOsc.stop(now + duration);
    osc.start(now);
    osc.stop(now + duration);

    oscillators.push(osc);
    gains.push(gain);
  });
}

/**
 * Ball Silence Sound: Sudden cut to eerie low drone
 * "silenceDuration: 3000ms of dread"
 * The moment before THE BALL constricts
 */
function playBallSilenceSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 3.0; // 3 seconds of dread

  // Very low sub-bass drone
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.value = 30; // Sub-bass rumble

  // Subtle tremolo for unease
  const tremoloOsc = ctx.createOscillator();
  tremoloOsc.type = 'sine';
  tremoloOsc.frequency.value = 2; // Slow pulse

  const tremoloGain = ctx.createGain();
  tremoloOsc.connect(tremoloGain.gain);
  tremoloGain.gain.setValueAtTime(0.8, now);

  // Very quiet - this is about absence
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume * 0.15, now);
  gain.gain.setValueAtTime(volume * 0.15, now + duration * 0.8);
  gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc.connect(tremoloGain);
  tremoloGain.connect(gain);
  gain.connect(output);

  tremoloOsc.start(now);
  osc.start(now);
  tremoloOsc.stop(now + duration);
  osc.stop(now + duration);
}

/**
 * Massacre Sound: Triumphant multi-layer impact with harmonic richness
 * Plays on 5+ simultaneous kills - "DOPAMINE HIT"
 * Musical: Perfect 5th (3/2 = 1.5) for power + Minor 7th (9/5 = 1.8) for satisfaction
 */
function playMassacreSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number
) {
  const now = ctx.currentTime;
  const duration = 0.4;

  // Low bass punch (80Hz base)
  const bassOsc = ctx.createOscillator();
  bassOsc.type = 'sine';
  bassOsc.frequency.setValueAtTime(80, now);
  bassOsc.frequency.exponentialRampToValueAtTime(40, now + duration);

  // Perfect 5th layer (120Hz) - stable, powerful
  const fifthOsc = ctx.createOscillator();
  fifthOsc.type = 'sine';
  fifthOsc.frequency.setValueAtTime(80 * 1.5, now); // 120Hz
  fifthOsc.frequency.exponentialRampToValueAtTime(40 * 1.5, now + duration); // 60Hz

  // Minor 7th layer (144Hz) - jazzy satisfaction
  const minor7thOsc = ctx.createOscillator();
  minor7thOsc.type = 'sine';
  minor7thOsc.frequency.setValueAtTime(80 * 1.8, now); // 144Hz
  minor7thOsc.frequency.exponentialRampToValueAtTime(40 * 1.8, now + duration); // 72Hz

  const bassGain = ctx.createGain();
  bassGain.gain.setValueAtTime(volume * 0.7, now);
  bassGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // 5th gain (40% of bass for powerful support)
  const fifthGain = ctx.createGain();
  fifthGain.gain.setValueAtTime(volume * 0.28, now);
  fifthGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Minor 7th gain (30% of bass for color)
  const minor7thGain = ctx.createGain();
  minor7thGain.gain.setValueAtTime(volume * 0.21, now);
  minor7thGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

  // Distorted impact
  const distortion = ctx.createWaveShaper();
  distortion.curve = makeDistortionCurve(80);

  // White noise burst for crunch
  const bufferSize = ctx.sampleRate * 0.1;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
  }

  const noise = ctx.createBufferSource();
  noise.buffer = buffer;

  const noiseGain = ctx.createGain();
  noiseGain.gain.setValueAtTime(volume * 0.3, now);
  noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);

  // High shimmer (reward sound)
  const shimmerOsc = ctx.createOscillator();
  shimmerOsc.type = 'sine';
  shimmerOsc.frequency.value = 1200;

  const shimmerGain = ctx.createGain();
  shimmerGain.gain.setValueAtTime(0, now);
  shimmerGain.gain.linearRampToValueAtTime(volume * 0.15, now + 0.05);
  shimmerGain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);

  // Connect bass path (through distortion)
  bassOsc.connect(distortion);
  distortion.connect(bassGain);
  bassGain.connect(output);

  // Connect harmonic layers (clean, not distorted)
  fifthOsc.connect(fifthGain);
  fifthGain.connect(output);

  minor7thOsc.connect(minor7thGain);
  minor7thGain.connect(output);

  // Connect noise and shimmer
  noise.connect(noiseGain);
  noiseGain.connect(output);

  shimmerOsc.connect(shimmerGain);
  shimmerGain.connect(output);

  // Start all oscillators
  bassOsc.start(now);
  fifthOsc.start(now);
  minor7thOsc.start(now);
  noise.start(now);
  shimmerOsc.start(now);

  // Stop all oscillators
  bassOsc.stop(now + duration);
  fifthOsc.stop(now + duration);
  minor7thOsc.stop(now + duration);
  noise.stop(now + 0.1);
  shimmerOsc.stop(now + 0.3);
}

/**
 * Graze Sound: Sharp tick for near-miss
 * Duration: ~50ms
 * Pitch increases with chain count for satisfying escalation
 */
function playGrazeSound(
  ctx: AudioContext,
  output: GainNode,
  volume: number,
  pitch: number
) {
  const now = ctx.currentTime;
  const duration = 0.05; // Very short tick

  // High sine oscillator for sharp tick
  const osc = ctx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(1600 * pitch, now);
  osc.frequency.exponentialRampToValueAtTime(1200 * pitch, now + duration);

  // Second harmonic for richness
  const osc2 = ctx.createOscillator();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(2400 * pitch, now);
  osc2.frequency.exponentialRampToValueAtTime(1800 * pitch, now + duration);

  // Gain envelope - sharp attack, quick decay
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(volume * 0.35, now);
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
  osc2.start(now);
  osc.stop(now + duration);
  osc2.stop(now + duration);
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
