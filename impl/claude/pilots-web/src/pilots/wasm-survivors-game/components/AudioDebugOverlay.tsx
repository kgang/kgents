/**
 * Audio Debug Overlay
 *
 * Visualizes and controls the KENT fugue system.
 * Activate with ?debug=audio in the URL.
 *
 * Shows:
 * - KENT motif visualization (B# - F# - D# - A)
 * - Current fugue phase and voice activity
 * - Real-time piano roll
 * - Hyperparameter controls
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useKentFugue } from '../hooks/useKentFugue';
import {
  KENT_CIPHER,
  KENT_SEMITONES,
  KENT_SUBJECT,
  KENT_SUBJECT_EXTENDED,
  KENT_COUNTERSUBJECT,
  semitoneToFrequency,
  createTonalAnswer,
  createInversion,
  createRetrograde,
  createAugmentation,
  FugueNote,
  FuguePhase,
} from '../systems/kent-fugue';

// =============================================================================
// TYPES
// =============================================================================

interface PlayedNote {
  frequency: number;
  voice: string;
  startTime: number;
  duration: number;
  semitone: number;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const NOTE_NAMES = ['C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'B#'];

const VOICE_COLORS: Record<string, string> = {
  soprano: '#FF6B6B',  // Red
  alto: '#4ECDC4',     // Teal
  tenor: '#FFE66D',    // Yellow
  bass: '#95E1D3',     // Mint
};

const PHASE_DESCRIPTIONS: Record<FuguePhase, string> = {
  silence: 'Silence - waiting to begin',
  exposition_1: 'Exposition I - Alto introduces the KENT subject',
  exposition_2: 'Exposition II - Soprano answers, Alto countersubject',
  exposition_3: 'Exposition III - Tenor enters with subject',
  exposition_4: 'Exposition IV - Bass completes the exposition',
  episode: 'Episode - Sequential development',
  development: 'Development - Subject transformations',
  stretto: 'Stretto - Overlapping entries (climax!)',
  pedal_point: 'Pedal Point - Bass holds tonic',
  recapitulation: 'Recapitulation - Subject returns',
  coda: 'Coda - Final cadence',
};

// =============================================================================
// MINI SYNTHESIZER FOR PREVIEW
// =============================================================================

class PreviewSynth {
  private ctx: AudioContext | null = null;
  private masterGain: GainNode | null = null;

  async init(): Promise<void> {
    if (this.ctx) return;
    this.ctx = new AudioContext();
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0.3; // 40% softer than game SFX
    this.masterGain.connect(this.ctx.destination);
  }

  playNote(frequency: number, duration: number = 0.3): void {
    if (!this.ctx || !this.masterGain) return;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sawtooth';
    osc.frequency.value = frequency;

    const now = this.ctx.currentTime;
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(0.3, now + 0.02);
    gain.gain.setValueAtTime(0.25, now + duration * 0.7);
    gain.gain.exponentialRampToValueAtTime(0.001, now + duration);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start(now);
    osc.stop(now + duration + 0.1);
  }

  // === DRUM SOUNDS ===

  playKick(): void {
    if (!this.ctx || !this.masterGain) return;
    const now = this.ctx.currentTime;

    // Main body oscillator
    const osc = this.ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(100, now);
    osc.frequency.exponentialRampToValueAtTime(45, now + 0.15);

    // Sub oscillator
    const subOsc = this.ctx.createOscillator();
    subOsc.type = 'sine';
    subOsc.frequency.setValueAtTime(50, now);

    // Click transient
    const clickBuffer = this.ctx.createBuffer(1, this.ctx.sampleRate * 0.01, this.ctx.sampleRate);
    const clickData = clickBuffer.getChannelData(0);
    for (let i = 0; i < clickData.length; i++) {
      clickData[i] = (Math.random() * 2 - 1) * Math.exp(-i / (clickData.length * 0.1));
    }
    const click = this.ctx.createBufferSource();
    click.buffer = clickBuffer;

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(1.785, now); // 30% softer
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);

    const subGain = this.ctx.createGain();
    subGain.gain.setValueAtTime(0.945, now); // 30% softer
    subGain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

    const clickGain = this.ctx.createGain();
    clickGain.gain.setValueAtTime(1.05, now); // 30% softer
    clickGain.gain.exponentialRampToValueAtTime(0.001, now + 0.015);

    osc.connect(gain);
    subOsc.connect(subGain);
    click.connect(clickGain);
    gain.connect(this.masterGain);
    subGain.connect(this.masterGain);
    clickGain.connect(this.masterGain);

    osc.start(now);
    subOsc.start(now);
    click.start(now);
    osc.stop(now + 0.25);
    subOsc.stop(now + 0.3);
  }

  playSnare(): void {
    if (!this.ctx || !this.masterGain) return;
    const now = this.ctx.currentTime;

    // Noise for body
    const noiseBuffer = this.ctx.createBuffer(1, this.ctx.sampleRate * 0.15, this.ctx.sampleRate);
    const noiseData = noiseBuffer.getChannelData(0);
    for (let i = 0; i < noiseData.length; i++) {
      noiseData[i] = (Math.random() * 2 - 1) * Math.exp(-i / (noiseData.length * 0.3));
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = noiseBuffer;

    const noiseFilter = this.ctx.createBiquadFilter();
    noiseFilter.type = 'highpass';
    noiseFilter.frequency.value = 1000;

    // Tone for attack
    const osc = this.ctx.createOscillator();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(200, now);
    osc.frequency.exponentialRampToValueAtTime(100, now + 0.05);

    const noiseGain = this.ctx.createGain();
    noiseGain.gain.setValueAtTime(0.7, now);
    noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);

    const toneGain = this.ctx.createGain();
    toneGain.gain.setValueAtTime(0.5, now);
    toneGain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

    noise.connect(noiseFilter);
    noiseFilter.connect(noiseGain);
    noiseGain.connect(this.masterGain);
    osc.connect(toneGain);
    toneGain.connect(this.masterGain);

    noise.start(now);
    osc.start(now);
    noise.stop(now + 0.2);
    osc.stop(now + 0.1);
  }

  playHihat(): void {
    if (!this.ctx || !this.masterGain) return;
    const now = this.ctx.currentTime;

    const duration = 0.12;
    const noiseBuffer = this.ctx.createBuffer(1, this.ctx.sampleRate * duration, this.ctx.sampleRate);
    const noiseData = noiseBuffer.getChannelData(0);
    for (let i = 0; i < noiseData.length; i++) {
      // Main decay
      const decay = Math.exp(-i / (noiseData.length * 0.3));
      // Shimmer has its own faster decay to prevent accumulation
      const shimmerDecay = Math.exp(-i / (noiseData.length * 0.15));
      const pitchDrift = 0.025 + Math.sin(i * 0.001) * 0.005;
      const shimmer = Math.sin(i * pitchDrift) * 0.03 * shimmerDecay;
      // Noise dominates, shimmer is subtle
      const noise_val = (Math.random() * 2 - 1) * 0.85;
      const shimmer_val = shimmer * 0.15;
      noiseData[i] = (noise_val + shimmer_val) * decay;
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = noiseBuffer;

    const hpFilter = this.ctx.createBiquadFilter();
    hpFilter.type = 'highpass';
    hpFilter.frequency.value = 5000;

    // Reduced gain and Q to prevent feedback
    const peakFilter = this.ctx.createBiquadFilter();
    peakFilter.type = 'peaking';
    peakFilter.frequency.value = 8000;
    peakFilter.gain.value = 2;
    peakFilter.Q.value = 2;

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(1.6, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);

    noise.connect(hpFilter);
    hpFilter.connect(peakFilter);
    peakFilter.connect(gain);
    gain.connect(this.masterGain);

    noise.start(now);
    noise.stop(now + duration + 0.05);
  }

  playTom(): void {
    if (!this.ctx || !this.masterGain) return;
    const now = this.ctx.currentTime;

    const osc = this.ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(150, now);
    osc.frequency.exponentialRampToValueAtTime(80, now + 0.2);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(1.47, now); // 30% softer
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start(now);
    osc.stop(now + 0.35);
  }

  playCrash(): void {
    if (!this.ctx || !this.masterGain) return;
    const now = this.ctx.currentTime;

    const noiseBuffer = this.ctx.createBuffer(2, this.ctx.sampleRate * 1.5, this.ctx.sampleRate);
    for (let channel = 0; channel < 2; channel++) {
      const data = noiseBuffer.getChannelData(channel);
      for (let i = 0; i < data.length; i++) {
        const decay = Math.exp(-i / (data.length * 0.4));
        const shimmer = Math.sin(i * 0.005) * 0.1 + 1;
        data[i] = (Math.random() * 2 - 1) * decay * shimmer;
      }
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = noiseBuffer;

    const hpFilter = this.ctx.createBiquadFilter();
    hpFilter.type = 'highpass';
    hpFilter.frequency.value = 1500;

    const peakFilter = this.ctx.createBiquadFilter();
    peakFilter.type = 'peaking';
    peakFilter.frequency.value = 5000;
    peakFilter.gain.value = 8;
    peakFilter.Q.value = 1.5;

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(1.0, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 1.5);

    noise.connect(hpFilter);
    hpFilter.connect(peakFilter);
    peakFilter.connect(gain);
    gain.connect(this.masterGain);

    noise.start(now);
    noise.stop(now + 1.6);
  }

  playRide(): void {
    if (!this.ctx || !this.masterGain) return;
    const now = this.ctx.currentTime;

    const noiseBuffer = this.ctx.createBuffer(1, this.ctx.sampleRate * 0.4, this.ctx.sampleRate);
    const noiseData = noiseBuffer.getChannelData(0);
    for (let i = 0; i < noiseData.length; i++) {
      // Add harmonic content for grit
      const harmonic = Math.sin(i * 0.02) * 0.3;
      noiseData[i] = ((Math.random() * 2 - 1) + harmonic) * Math.exp(-i / (noiseData.length * 0.5));
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = noiseBuffer;

    // Lower high-pass for more body
    const hpFilter = this.ctx.createBiquadFilter();
    hpFilter.type = 'highpass';
    hpFilter.frequency.value = 2500;

    // Mid boost for grit
    const midBoost = this.ctx.createBiquadFilter();
    midBoost.type = 'peaking';
    midBoost.frequency.value = 3500;
    midBoost.gain.value = 6;
    midBoost.Q.value = 1;

    // Waveshaper distortion
    const distortion = this.ctx.createWaveShaper();
    const curve = new Float32Array(256);
    for (let i = 0; i < 256; i++) {
      const x = (i / 128) - 1;
      curve[i] = Math.tanh(x * 2);
    }
    distortion.curve = curve;

    // Reduced bell - just a hint
    const bellOsc = this.ctx.createOscillator();
    bellOsc.type = 'triangle';
    bellOsc.frequency.value = 2200;

    const noiseGain = this.ctx.createGain();
    noiseGain.gain.setValueAtTime(0.7, now);
    noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

    const bellGain = this.ctx.createGain();
    bellGain.gain.setValueAtTime(0.05, now);
    bellGain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);

    noise.connect(hpFilter);
    hpFilter.connect(midBoost);
    midBoost.connect(distortion);
    distortion.connect(noiseGain);
    noiseGain.connect(this.masterGain);
    bellOsc.connect(bellGain);
    bellGain.connect(this.masterGain);

    noise.start(now);
    bellOsc.start(now);
    noise.stop(now + 0.5);
    bellOsc.stop(now + 0.4);
  }

  playMotif(notes: FugueNote[], octave: number = 4, tempo: number = 120): void {
    if (!this.ctx) return;

    const beatDuration = 60 / tempo;
    let time = 0;

    for (const note of notes) {
      const freq = semitoneToFrequency(note.semitone, octave);
      const duration = note.duration * beatDuration;

      setTimeout(() => {
        this.playNote(freq, duration);
      }, time * 1000);

      time += duration;
    }
  }

  stop(): void {
    if (this.ctx) {
      this.ctx.close();
      this.ctx = null;
    }
  }
}

// =============================================================================
// KENT MOTIF DISPLAY
// =============================================================================

function KentMotifDisplay({ onPlayNote }: { onPlayNote: (semitone: number) => void }) {
  return (
    <div className="bg-gray-900 rounded-lg p-4 mb-4">
      <h3 className="text-amber-400 font-bold mb-2">K-E-N-T Motif</h3>
      <p className="text-gray-400 text-xs mb-3">
        Letter → Semitone → Note (Two tritones - the devil's intervals!)
      </p>

      <div className="flex gap-2 justify-center">
        {(['K', 'E', 'N', 'T'] as const).map((letter, i) => {
          const semitone = KENT_SEMITONES[i];
          const noteName = NOTE_NAMES[semitone];
          const isTritoneBefore = i > 0 && Math.abs(KENT_SEMITONES[i] - KENT_SEMITONES[i-1]) === 6;

          return (
            <div key={letter} className="flex flex-col items-center">
              {i > 0 && (
                <div className={`text-xs mb-1 ${isTritoneBefore ? 'text-red-500 font-bold' : 'text-gray-500'}`}>
                  {isTritoneBefore ? '♯6' : `${Math.abs(KENT_SEMITONES[i] - KENT_SEMITONES[i-1])}`}
                </div>
              )}
              <button
                onClick={() => onPlayNote(semitone)}
                className="w-16 h-16 rounded-lg bg-gray-800 hover:bg-gray-700 border-2 border-amber-500 flex flex-col items-center justify-center transition-all hover:scale-105"
              >
                <span className="text-2xl font-bold text-amber-400">{letter}</span>
                <span className="text-xs text-gray-400">{noteName}</span>
              </button>
              <span className="text-xs text-gray-500 mt-1">{semitone} st</span>
            </div>
          );
        })}
      </div>

      <div className="mt-3 text-center text-xs text-gray-500">
        K({KENT_CIPHER.K}) → E({KENT_CIPHER.E}) → N({KENT_CIPHER.N}) → T({KENT_CIPHER.T})
      </div>
    </div>
  );
}

// =============================================================================
// PIANO ROLL VISUALIZATION
// =============================================================================

function PianoRoll({
  playedNotes,
  width = 400,
  height = 200
}: {
  playedNotes: PlayedNote[];
  width?: number;
  height?: number;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);

    // Draw piano keys on left
    const keyWidth = 30;
    const noteHeight = height / 12;

    for (let i = 0; i < 12; i++) {
      const y = (11 - i) * noteHeight;
      const isBlack = [1, 3, 6, 8, 10].includes(i);

      ctx.fillStyle = isBlack ? '#333' : '#555';
      ctx.fillRect(0, y, keyWidth - 2, noteHeight - 1);

      // Note name
      ctx.fillStyle = '#888';
      ctx.font = '8px monospace';
      ctx.fillText(NOTE_NAMES[i], 2, y + noteHeight - 3);
    }

    // Draw grid
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 12; i++) {
      const y = i * noteHeight;
      ctx.beginPath();
      ctx.moveTo(keyWidth, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Draw played notes
    const now = Date.now();
    const visibleDuration = 4000; // 4 seconds visible

    for (const note of playedNotes) {
      const age = now - note.startTime;
      if (age > visibleDuration) continue;

      const x = keyWidth + ((visibleDuration - age) / visibleDuration) * (width - keyWidth);
      const y = (11 - (note.semitone % 12)) * noteHeight;
      const noteWidth = (note.duration * 1000 / visibleDuration) * (width - keyWidth);

      ctx.fillStyle = VOICE_COLORS[note.voice] || '#fff';
      ctx.globalAlpha = Math.max(0.3, 1 - age / visibleDuration);
      ctx.fillRect(x, y + 2, Math.max(noteWidth, 4), noteHeight - 4);
      ctx.globalAlpha = 1;
    }

    // Draw current time line
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(width - 2, 0);
    ctx.lineTo(width - 2, height);
    ctx.stroke();

  }, [playedNotes, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="rounded-lg"
    />
  );
}

// =============================================================================
// VOICE ACTIVITY DISPLAY
// =============================================================================

function VoiceActivity({
  activeVoices
}: {
  activeVoices: Record<string, { active: boolean; role: string; pitch: number }>
}) {
  return (
    <div className="grid grid-cols-4 gap-2 mb-4">
      {(['soprano', 'alto', 'tenor', 'bass'] as const).map(voice => {
        const info = activeVoices[voice];
        const isActive = info?.active;

        return (
          <div
            key={voice}
            className={`p-2 rounded-lg text-center transition-all ${
              isActive ? 'bg-gray-700' : 'bg-gray-900'
            }`}
            style={{
              borderLeft: `3px solid ${VOICE_COLORS[voice]}`,
              opacity: isActive ? 1 : 0.5
            }}
          >
            <div className="text-xs font-bold capitalize" style={{ color: VOICE_COLORS[voice] }}>
              {voice}
            </div>
            <div className="text-xs text-gray-400">
              {info?.role || 'rest'}
            </div>
            {isActive && info?.pitch !== undefined && (
              <div className="text-xs text-gray-500">
                {NOTE_NAMES[info.pitch % 12]}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// PARAMETER SLIDERS
// =============================================================================

function ParameterSlider({
  label,
  value,
  onChange,
  min = 0,
  max = 1,
  step = 0.01,
  color = '#FFD700'
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
  color?: string;
}) {
  return (
    <div className="flex items-center gap-2 mb-2">
      <span className="text-xs text-gray-400 w-20">{label}</span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="flex-1 h-2 rounded-lg appearance-none cursor-pointer"
        style={{
          background: `linear-gradient(to right, ${color} ${value * 100}%, #333 ${value * 100}%)`
        }}
      />
      <span className="text-xs text-gray-500 w-10 text-right">
        {value.toFixed(2)}
      </span>
    </div>
  );
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function AudioDebugOverlay() {
  const kentFugue = useKentFugue();
  const [isPlaying, setIsPlaying] = useState(false);
  const [intensity, setIntensity] = useState(0.3);
  const [gamePhase, setGamePhase] = useState<'exploration' | 'combat' | 'crisis' | 'death'>('exploration');
  const [playedNotes, setPlayedNotes] = useState<PlayedNote[]>([]);
  const [activeVoices] = useState<Record<string, { active: boolean; role: string; pitch: number }>>({
    soprano: { active: false, role: 'rest', pitch: 0 },
    alto: { active: false, role: 'rest', pitch: 0 },
    tenor: { active: false, role: 'rest', pitch: 0 },
    bass: { active: false, role: 'rest', pitch: 0 },
  });

  const previewSynthRef = useRef<PreviewSynth | null>(null);
  const animationRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(performance.now());

  // Initialize preview synth
  useEffect(() => {
    previewSynthRef.current = new PreviewSynth();
    return () => {
      previewSynthRef.current?.stop();
    };
  }, []);

  // Animation loop for fugue updates
  useEffect(() => {
    if (!isPlaying || !kentFugue.isRunning) return;

    const update = () => {
      const now = performance.now();
      const deltaTime = (now - lastTimeRef.current) / 1000;
      lastTimeRef.current = now;

      kentFugue.update(deltaTime, intensity, gamePhase);

      // Clean old notes from visualization
      setPlayedNotes(prev => prev.filter(n => Date.now() - n.startTime < 5000));

      animationRef.current = requestAnimationFrame(update);
    };

    animationRef.current = requestAnimationFrame(update);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, kentFugue, intensity, gamePhase]);

  // Start/stop controls
  const handleStart = useCallback(async () => {
    await previewSynthRef.current?.init();
    const success = await kentFugue.start();
    if (success) {
      setIsPlaying(true);
      lastTimeRef.current = performance.now();
    }
  }, [kentFugue]);

  const handleStop = useCallback(() => {
    kentFugue.stop();
    setIsPlaying(false);
  }, [kentFugue]);

  // Play individual note
  const handlePlayNote = useCallback(async (semitone: number) => {
    await previewSynthRef.current?.init();
    const freq = semitoneToFrequency(semitone, 4);
    previewSynthRef.current?.playNote(freq, 0.5);

    setPlayedNotes(prev => [...prev, {
      frequency: freq,
      voice: 'preview',
      startTime: Date.now(),
      duration: 0.5,
      semitone,
    }]);
  }, []);

  // Play motif variations
  const handlePlayMotif = useCallback(async (type: string) => {
    await previewSynthRef.current?.init();

    let notes: FugueNote[];
    switch (type) {
      case 'subject':
        notes = KENT_SUBJECT;
        break;
      case 'extended':
        notes = KENT_SUBJECT_EXTENDED;
        break;
      case 'answer':
        notes = createTonalAnswer(KENT_SUBJECT);
        break;
      case 'inversion':
        notes = createInversion(KENT_SUBJECT);
        break;
      case 'retrograde':
        notes = createRetrograde(KENT_SUBJECT);
        break;
      case 'augmentation':
        notes = createAugmentation(KENT_SUBJECT);
        break;
      case 'countersubject':
        notes = KENT_COUNTERSUBJECT;
        break;
      default:
        notes = KENT_SUBJECT;
    }

    previewSynthRef.current?.playMotif(notes, 4, 100);

    // Add to visualization
    let time = 0;
    const beatDuration = 60 / 100;
    for (const note of notes) {
      const startTime = Date.now() + time * 1000;
      setTimeout(() => {
        setPlayedNotes(prev => [...prev, {
          frequency: semitoneToFrequency(note.semitone, 4),
          voice: type,
          startTime,
          duration: note.duration * beatDuration,
          semitone: note.semitone,
        }]);
      }, time * 1000);
      time += note.duration * beatDuration;
    }
  }, []);

  return (
    <div className="fixed top-4 right-4 w-96 bg-gray-950/95 border border-amber-500/30 rounded-xl p-4 text-white shadow-2xl z-50 max-h-[90vh] overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-amber-400">🎼 KENT Fugue Debug</h2>
          <p className="text-xs text-gray-500">C# Minor • Two Tritones</p>
        </div>
        <div className="flex gap-2">
          {!isPlaying ? (
            <button
              onClick={handleStart}
              className="px-3 py-1 bg-green-600 hover:bg-green-500 rounded text-sm font-bold"
            >
              ▶ Start
            </button>
          ) : (
            <button
              onClick={handleStop}
              className="px-3 py-1 bg-red-600 hover:bg-red-500 rounded text-sm font-bold"
            >
              ⏹ Stop
            </button>
          )}
        </div>
      </div>

      {/* KENT Motif Display */}
      <KentMotifDisplay onPlayNote={handlePlayNote} />

      {/* Current Phase */}
      <div className="bg-gray-900 rounded-lg p-3 mb-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-400">Current Phase</span>
          <span className="text-xs text-amber-400">{kentFugue.tempo} BPM</span>
        </div>
        <div className="text-sm font-bold text-white">
          {kentFugue.currentPhase}
        </div>
        <div className="text-xs text-gray-500">
          {PHASE_DESCRIPTIONS[kentFugue.currentPhase]}
        </div>
      </div>

      {/* Voice Activity */}
      <div className="mb-4">
        <h3 className="text-xs text-gray-400 mb-2">Voice Activity</h3>
        <VoiceActivity activeVoices={activeVoices} />
      </div>

      {/* Piano Roll */}
      <div className="mb-4">
        <h3 className="text-xs text-gray-400 mb-2">Piano Roll</h3>
        <PianoRoll playedNotes={playedNotes} width={360} height={150} />
      </div>

      {/* Motif Buttons */}
      <div className="mb-4">
        <h3 className="text-xs text-gray-400 mb-2">Play Transformations</h3>
        <div className="grid grid-cols-4 gap-1">
          {[
            { id: 'subject', label: 'Subject' },
            { id: 'extended', label: 'Extended' },
            { id: 'answer', label: 'Answer' },
            { id: 'countersubject', label: 'Counter' },
            { id: 'inversion', label: 'Invert' },
            { id: 'retrograde', label: 'Retro' },
            { id: 'augmentation', label: 'Augment' },
          ].map(({ id, label }) => (
            <button
              key={id}
              onClick={() => handlePlayMotif(id)}
              className="px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs"
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Drum Sounds */}
      <div className="mb-4">
        <h3 className="text-xs text-gray-400 mb-2">🥁 Drum Sounds</h3>
        <div className="grid grid-cols-3 gap-2">
          {[
            { id: 'kick', label: 'Kick', emoji: '🦵', color: 'bg-red-900 hover:bg-red-800' },
            { id: 'snare', label: 'Snare', emoji: '🪘', color: 'bg-orange-900 hover:bg-orange-800' },
            { id: 'hihat', label: 'Hi-Hat', emoji: '🔔', color: 'bg-yellow-900 hover:bg-yellow-800' },
            { id: 'tom', label: 'Tom', emoji: '🥁', color: 'bg-green-900 hover:bg-green-800' },
            { id: 'crash', label: 'Crash', emoji: '💥', color: 'bg-blue-900 hover:bg-blue-800' },
            { id: 'ride', label: 'Ride', emoji: '🛎️', color: 'bg-purple-900 hover:bg-purple-800' },
          ].map(({ id, label, emoji, color }) => (
            <button
              key={id}
              onClick={async () => {
                await previewSynthRef.current?.init();
                switch (id) {
                  case 'kick': previewSynthRef.current?.playKick(); break;
                  case 'snare': previewSynthRef.current?.playSnare(); break;
                  case 'hihat': previewSynthRef.current?.playHihat(); break;
                  case 'tom': previewSynthRef.current?.playTom(); break;
                  case 'crash': previewSynthRef.current?.playCrash(); break;
                  case 'ride': previewSynthRef.current?.playRide(); break;
                }
              }}
              className={`px-3 py-2 ${color} rounded text-sm font-medium flex items-center justify-center gap-1`}
            >
              <span>{emoji}</span>
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Parameters */}
      <div className="bg-gray-900 rounded-lg p-3 mb-4">
        <h3 className="text-xs text-gray-400 mb-3">Hyperparameters</h3>

        <ParameterSlider
          label="Intensity"
          value={intensity}
          onChange={setIntensity}
          color="#FF6B6B"
        />

        <div className="mt-3">
          <span className="text-xs text-gray-400">Game Phase</span>
          <div className="grid grid-cols-4 gap-1 mt-1">
            {(['exploration', 'combat', 'crisis', 'death'] as const).map(phase => (
              <button
                key={phase}
                onClick={() => setGamePhase(phase)}
                className={`px-2 py-1 rounded text-xs capitalize ${
                  gamePhase === phase
                    ? 'bg-amber-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {phase}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="text-xs text-gray-500">
        <div className="flex gap-3 flex-wrap">
          {Object.entries(VOICE_COLORS).map(([voice, color]) => (
            <div key={voice} className="flex items-center gap-1">
              <div className="w-2 h-2 rounded" style={{ backgroundColor: color }} />
              <span className="capitalize">{voice}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-800 text-center">
        <p className="text-xs text-gray-600">
          "The hornet's name is written in the music"
        </p>
      </div>
    </div>
  );
}

export default AudioDebugOverlay;
