# The KENT Fugue in C♯ Minor: A Theoretical Derivation

> *"The hornet's name is written in the music."*

This document derives the theoretical foundation of the KENT Fugue system as implemented in the WASM Survivors game. The system generates real-time procedural counterpoint using Kent's name as the intervallic DNA—a musical cryptogram in the tradition of Bach's B-A-C-H motif.

---

## I. The Cipher: Name → Semitones

The KENT cryptogram converts each letter to a semitone value using alphabet position modulo 12:

```
Letter → Position → mod 12 → Semitone → Note

K →  11  →  11  →  11  →  B♯ (leading tone)
E →   5  →   5  →   5  →  F♯ (subdominant)
N →  14  →   2  →   2  →  D♯ (supertonic)
T →  20  →   8  →   8  →  A  (submediant)
```

**The KENT Motif**: `B♯ - F♯ - D♯ - A` (semitones: `[11, 5, 2, 8]`)

---

## II. The Devil's Interval: Two Tritones

The intervals between consecutive KENT notes reveal the subject's dark character:

```
K → E:  11 → 5  = -6 semitones = TRITONE (descending)
E → N:   5 → 2  = -3 semitones = minor 3rd (descending)
N → T:   2 → 8  = +6 semitones = TRITONE (ascending)
```

**The diabolus in musica appears TWICE**. This isn't coincidence—it's the intervallic signature of tension, of survival horror, of something *wrong*.

| Interval | Name | Character |
|----------|------|-----------|
| Tritone | "Devil's interval" | Maximum harmonic tension |
| Minor 3rd | Lament bass | Melancholy, descent |
| Tritone | Double devil | Climactic dissonance |

The subject doesn't just *contain* tritones—it's *built from* them. KENT's name literally spells maximum musical tension.

---

## III. The Tonal Foundation: C♯ Minor

**Base frequency**: C♯4 = 277.18 Hz

**C♯ Harmonic Minor scale** (semitones from tonic):
```
C♯   D♯   E    F♯   G♯   A    B♯
0    2    3    5    7    8    11
```

The raised 7th (B♯ instead of B) creates the leading tone—the very note that begins KENT. The name starts on the pitch that *most wants to resolve* to the tonic.

### Why C♯ Minor?

1. **Historical weight**: Bach's C♯ minor fugue (WTC I), Beethoven's Moonlight Sonata, Chopin's Fantaisie-Impromptu
2. **Technical gravitas**: Five sharps demand attention
3. **Chromatic richness**: The harmonic minor's augmented second (A → B♯) enables the exotic intervals KENT requires
4. **The leading tone**: B♯ (Kent's first note) sits a half-step below the tonic—maximum pull toward resolution

---

## IV. The Subject: KENT Realized

The fugue subject elaborates the raw KENT semitones into a musical statement:

```typescript
const KENT_SUBJECT: FugueNote[] = [
  // K - The announcement (B♯ / leading tone)
  { semitone: 11, duration: 0.75, velocity: 0.9, articulation: 'accent' },

  // E - Tritone descent to F♯ (the devil's interval!)
  { semitone: 5, duration: 0.5, velocity: 0.8, articulation: 'legato' },

  // N - Minor 3rd down to D♯
  { semitone: 2, duration: 0.5, velocity: 0.75, articulation: 'legato' },

  // T - Tritone leap to A (second devil's interval!)
  { semitone: 8, duration: 0.75, velocity: 0.85, articulation: 'tenuto' },

  // Resolution: chromatic descent to G♯ (dominant)
  { semitone: 7, duration: 0.25, velocity: 0.7, articulation: 'legato' },

  // Final resolution to C♯ (tonic)
  { semitone: 0, duration: 1.0, velocity: 0.9, articulation: 'tenuto' },
];
```

### Rhythmic Analysis

```
Beat:    1        2        3        4
         ♩.       ♩   ♩    ♩.       ♩   ♩
         K        E   N    T        →   C♯
         B♯       F♯  D♯   A        G♯  [tonic]

Contour: ┐───┐────┐────┘───┐───────────┘
         high  ↘    ↘   ↗     descent to tonic
```

The subject:
1. **Opens on the leading tone** (B♯) — maximum yearning
2. **Falls by tritone** — destabilizing
3. **Continues descent** — minor 3rd deepens
4. **Leaps by tritone** — crisis point
5. **Resolves chromatically** — G♯ → C♯ = dominant to tonic

---

## V. The Eight Transformations

The fugue system pre-generates eight variations of the KENT theme, each a classical fugue technique:

| Index | Transformation | Description | Function |
|-------|----------------|-------------|----------|
| 0 | **Original** | The statement as written | Dux (leader) |
| 1 | **Tonal Answer** | Transposed to dominant (G♯), with tonal adjustments | Comes (follower) |
| 2 | **Inversion** | Intervals flipped: rises become falls | Mirror image |
| 3 | **Retrograde** | Played backwards | Time reversal |
| 4 | **Augmentation** | Durations doubled | Expansion |
| 5 | **Diminution** | Durations halved | Compression |
| 6 | **Chromatic** | Color tones added | Intensification |
| 7 | **Sequence** | Repeated at different pitch levels | Episode material |

### Tonal vs. Real Answer

In a proper fugue, the **answer** transposes to the dominant but adjusts certain intervals:

```typescript
// If subject starts on tonic (C♯), answer starts on dominant (G♯)
// If subject goes TO dominant, answer returns TO tonic

Subject:  B♯ → F♯ → D♯ → A → G♯ → C♯  (in C♯ minor)
Answer:   F♯ → C♯ → A  → E → D♯ → G♯  (in G♯ minor, adjusted)
```

This maintains harmonic coherence while transposing the melodic content.

### Inversion

Intervals flip around an axis (default: C♯):

```
Original:  B♯(+11) → F♯(+5) → D♯(+2) → A(+8)
Inverted:  D♯(-11) → A♯(-5) → F♯(-2) → E(-8)
           (mod 12: D♯ → G♯ → F♯ → E)
```

The inverted KENT still contains tritones—the devil's interval is symmetric!

---

## VI. The Countersubject

The countersubject provides contrapuntal complement to the subject:

```typescript
const KENT_COUNTERSUBJECT: FugueNote[] = [
  // Contrary motion: starts low while subject is high
  { semitone: 0, duration: 0.5, velocity: 0.6 },   // C# (held)
  { semitone: 0, duration: 0.25, velocity: 0.55 }, // C# continued

  // Rising while subject descends
  { semitone: 2, duration: 0.5, velocity: 0.65 },  // D#
  { semitone: 3, duration: 0.5, velocity: 0.7 },   // E
  { semitone: 5, duration: 0.5, velocity: 0.75 },  // F#

  // Rhythmic counterpoint (fills gaps in subject)
  { semitone: 7, duration: 0.25, velocity: 0.6 },  // G# staccato
  { semitone: 5, duration: 0.25, velocity: 0.55 }, // F# staccato
  { semitone: 7, duration: 0.25, velocity: 0.6 },  // G# staccato
  { semitone: 8, duration: 0.25, velocity: 0.65 }, // A staccato

  // Resolution (arrives at dominant as subject resolves to tonic)
  { semitone: 7, duration: 1.0, velocity: 0.7 },   // G#
];
```

**Design Principles**:
1. **Contrary motion**: When subject descends, countersubject ascends
2. **Rhythmic complementation**: Short notes where subject has long, vice versa
3. **Harmonic resolution**: Countersubject ends on dominant (G♯) as subject ends on tonic (C♯) = perfect authentic cadence

---

## VII. The KENT Drum Pitch Engine

Beyond the fugue voices, KENT governs the entire percussion system:

### The Frequency Lattice

```typescript
const KENT_BASE_FREQ = 277.18;  // C♯
const KENT_SEMITONES = [0, 6, 3, 9];  // Normalized for drums
const KENT_RATIOS = KENT_SEMITONES.map(s => Math.pow(2, s / 12));
// [1.0, 1.4142, 1.1892, 1.6818]

const KENT_FREQUENCIES = KENT_RATIOS.map(r => KENT_BASE_FREQ * r);
// [277.18, 391.99, 329.63, 466.16]
```

### Per-Instrument Behavior

| Drum | KENT Principle | Behavior |
|------|----------------|----------|
| **Kick** | Tritone Oscillator | Breathes between tritone poles (B♯↔F♯ or D♯↔A) |
| **Snare** | Phase Witness | Memory-influenced pitch from previous hits |
| **Hi-hat** | Shimmer Field | Fibonacci-modulated center frequency |
| **Tom** | Fibonacci Spiral | Golden ratio traversal through KENT space |
| **Crash** | Void Eruption | Releases accumulated tritone tension |
| **Ride** | Phase Accumulator | Evolving pitch memory across the track |

### The Kick: Tritone Oscillator

```typescript
// Which tritone pair dominates (alternates every 2 bars)
const tritoneIndex = Math.floor(barPosition * 2) % 2;
const pair = tritoneIndex === 0
  ? [KENT_FREQUENCIES[0], KENT_FREQUENCIES[1]]   // B♯ ↔ F♯
  : [KENT_FREQUENCIES[2], KENT_FREQUENCIES[3]];  // D♯ ↔ A

// Golden ratio phase determines position between poles
const goldenPhase = (beatPosition * PHI) % 1;
const basePitch = lerp(pair[0], pair[1], goldenPhase);
```

The kick drum *breathes* between tritone poles, never settling, always in tension.

### Cross-Drum Resonance

All drums are harmonically linked:

```typescript
// Hi-hat shimmer coherent with kick (8th partial)
drums.hihat.centerFrequency = kickFundamental * 8;

// Snare body quantized to nearest KENT
drums.snare.bodyPitch = lerp(snare.bodyPitch, KENT_FREQUENCIES[kentIdx], 0.3);

// Tom avoids kick fundamental (moves tritone away if too close)
if (tom.pitch too close to kick) {
  tom.pitch = kickFundamental * KENT_RATIOS[1]; // Tritone
}

// Ride bell at tritone above kick for maximum tension
drums.ride.bellPitch = kickFundamental * KENT_RATIOS[1] * 4;
```

---

## VIII. Fugue Phases & Game States

The fugue evolves through classical phases, mapped to game intensity:

| Phase | Musical Function | Game Context |
|-------|------------------|--------------|
| `silence` | Rest | Pre-game, death |
| `exposition_1` | Subject enters alone | Exploration begins |
| `exposition_2` | Answer enters | Tension building |
| `exposition_3` | Third voice + countersubject | Combat initiated |
| `exposition_4` | Full texture | Intense combat |
| `episode` | Sequence/development | Wave transition |
| `development` | Fragmentation, stretto | Crisis mode |
| `pedal_point` | Dominant pedal | Boss approach |
| `stretto` | Overlapping entries | Maximum intensity |
| `coda` | Resolution | Victory/respite |

### Dynamic Mapping

```typescript
// Intensity → Voices
if (intensity < 0.3) return 1 voice (solo subject)
if (intensity < 0.5) return 2 voices (subject + answer)
if (intensity < 0.7) return 3 voices (add countersubject)
return 4 voices (full fugue)

// Intensity → Tempo
baseTempo = 72 BPM
tempo = baseTempo + (intensity * 48)  // 72-120 BPM
```

---

## IX. The Hypnotic Foundation: Chant Ostinatos

Beneath the fugue, hypnotic patterns create trance-like grounding:

### Tonic Pedal

```
Beat:  1        2        3        4
       C♯───────C♯  C♯   G♯  C♯   C♯
       (drone)  (pulse)  (lift)  (breath)
```

### Meditative Chant

```
Bar 1: C♯ → D♯ → E──────→ D♯ → C♯──────
Bar 2: C♯ → B────→ C♯──────→ D♯ → C♯──────
       (rising)     (falling mirror)
```

These patterns create a **hypnotic, prayer-like quality**—the "+40% chantingness" parameter in the code.

---

## X. Synthesis Implementation

The actual synthesizer uses **additive synthesis** with voice-specific timbres:

| Voice | Character | Harmonics | Vibrato |
|-------|-----------|-----------|---------|
| **Bass** | Cello-like | Sub-octave + odds | 4.5 Hz, deep |
| **Tenor** | Viola/horn | Balanced | 5.0 Hz, moderate |
| **Alto** | Clarinet-like | Strong odds | 5.5 Hz, expressive |
| **Soprano** | Flute-like | Fundamental-heavy | 6.0 Hz, shimmer |

Each voice creates its own timbre through harmonic ratios:

```typescript
// Bass harmonics (cello-like)
harmonics: [
  { ratio: 1, amplitude: 1.0 },    // Fundamental
  { ratio: 2, amplitude: 0.6 },    // Octave
  { ratio: 3, amplitude: 0.45 },   // 5th above octave
  { ratio: 0.5, amplitude: 0.3 },  // Sub-octave for depth
  // ...
]
```

---

## XI. Philosophical Implications

### The Name as Musical DNA

The KENT cryptogram doesn't just encode a melody—it generates an entire musical universe:

- **Melodic DNA**: The subject's intervals
- **Harmonic gravity**: The tritone relationships
- **Rhythmic character**: The tension/resolution patterns
- **Timbral coherence**: Cross-voice resonance

### Identity as Polyphony

A fugue multiplies one idea across voices, registers, keys. The subject is always KENT. But:

- KENT as soprano ≠ KENT as bass
- KENT in C♯ minor ≠ KENT in G♯ minor
- KENT alone ≠ KENT in stretto

**Identity is not a note. Identity is the relationships between instances of the motif.**

### The Generative Principle

> *"Spec is compression; design should generate implementation."*

The KENT fugue embodies this principle:
- **Spec**: Four letters (K-E-N-T)
- **Compression**: Cipher (letter → semitone)
- **Generation**: From four semitones, an infinite fugue unfolds

Given the name, the cipher, and the laws of counterpoint, the music writes itself.

---

## XII. Summary: The KENT Canon

| Element | Value | Derivation |
|---------|-------|------------|
| **Cipher** | Position mod 12 | Alphabet index |
| **Subject** | B♯-F♯-D♯-A | KENT → [11,5,2,8] |
| **Key** | C♯ minor | B♯ = leading tone |
| **Character** | Two tritones | K→E, N→T = ±6 semitones |
| **Answer** | Tonal (G♯ minor) | Classical fugue form |
| **Countersubject** | Contrary motion | Complementary line |
| **Drum lattice** | [277, 392, 330, 466] Hz | KENT frequencies |

---

> *"The proof IS the decision. The mark IS the witness."*
>
> *The name IS the music.*

---

## Appendix: Quick Reference

### The KENT Motif

```
  Semitones:    11      5       2       8
  Notes:        B♯      F♯      D♯      A
  Intervals:        -6      -3      +6
                  tritone  m3    tritone
```

### C♯ Harmonic Minor

```
Degree:   1    2    3    4    5    6    7
Note:     C♯   D♯   E    F♯   G♯   A    B♯
Semi:     0    2    3    5    7    8    11
```

### The Transformations

```
Original:       B♯  F♯  D♯  A   G♯  C♯
Tonal Answer:   F♯  C♯  A   E   D♯  G♯
Inversion:      D♯  G♯  F♯  E   ...
Retrograde:     C♯  G♯  A   D♯  F♯  B♯
Augmentation:   B♯────────  F♯────────  ...
Diminution:     B♯ F♯ D♯ A G♯ C♯ (fast)
```

---

*Filed: 2025-01-17*
*Source: `impl/claude/pilots-web/src/pilots/wasm-survivors-game/systems/kent-fugue.ts`*
*Status: Derived from implementation. Ready for video production.*
