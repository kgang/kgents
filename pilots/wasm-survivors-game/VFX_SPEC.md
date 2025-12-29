# Hornet Siege: VFX Specification

**Status**: TRANSFORMATION SPEC - Make Every Effect CLIP-WORTHY
**Version**: 1.0.0
**Date**: 2025-12-28
**Voice**: "Make kills feel like PUNCHES. Make THE BALL clip-worthy. Make death DRAMATIC."

---

## Philosophy: NOT SUBTLE

> *"Every effect should POP. Every moment should be screenshot-worthy. Every death should be DRAMATIC."*

This is not a spec for tasteful minimalism. This is a spec for **SPECTACLE**.

**Design Principles**:
1. **READABLE**: Player must instantly understand what's happening
2. **IMPACTFUL**: Effects should create dopamine hits, not gentle feedback
3. **PERFORMANT**: Budget your particles ruthlessly (max 500 on screen)
4. **UNIQUE**: This should look like NOTHING ELSE in the genre

---

## Part I: THE BALL - The Signature Spectacle

> *"This is THE clip. This is what streamers will clip. This is what players will screenshot."*

THE BALL is the game's signature mechanic: bees surround the hornet, vibrate, raise temperature to 46C, cook the hornet alive. **Real biology. Real drama. Real spectacle.**

### 1.1 Phase Overview

| Phase | Duration | Visual Signature | Audio | Camera |
|-------|----------|------------------|-------|--------|
| **FORMING** | 10,000ms | Bees swirl into sphere, dashed outline | Buzz crescendo | Pull back 0.75x |
| **SILENCE** | 3,000ms | Perfect sphere, audio drops | SILENCE (dread) | Hold at 0.70x |
| **CONSTRICT** | 2,000ms | Sphere tightens, gap highlighted | Bass note, heartbeat | Focus on gap 0.85x |
| **COOKING** | Until death | Heat shimmer, temp glow | Crackle, sizzle | Tight 1.1x |

### 1.2 FORMING Phase (10,000ms)

**The Setup**: Bees coordinate and swirl into position around the player.

#### Visual Elements

```typescript
const BALL_FORMING_VFX = {
  // Sphere outline
  outline: {
    style: 'dashed',
    dashPattern: [10, 10],
    color: '#FFD700',          // Gold (coordination color)
    lineWidth: 2,
    opacity: 0.4 + progress * 0.4,  // Fade in as it forms
  },

  // Individual bee glow
  beeGlow: {
    color: '#FFB800',          // Amber
    radius: 8,
    pulseRate: 2,              // Hz
    pulseIntensity: 0.3,       // +/-30% size
    phaseOffset: 'per-bee',    // Desync for organic feel
  },

  // Formation lines (connect coordinating bees)
  formationLines: {
    color: '#FFD700',
    opacity: 0.3,
    width: 1.5,
    fadeTime: 150,
    minBees: 3,                // Only show when 3+ bees coordinating
    maxDistance: 150,          // Only connect close bees
    dashPattern: [5, 5],
  },

  // Swirl particles (bees in motion)
  swirlParticles: {
    count: 12,                 // Particles trailing behind each bee
    color: '#FFE066',          // Pollen gold
    size: 2,
    lifetime: 200,
    opacity: 0.6,
    fadeMode: 'linear',
  },

  // Coordination pulse (visual heartbeat)
  coordinationPulse: {
    interval: 1500,            // ms between pulses
    color: '#FFD700',
    ringStart: 0,
    ringEnd: 'currentRadius',
    duration: 500,
    easing: 'ease-out',
  },
};
```

#### Animation Sequence

```
0.0s - 2.0s:   ALERT
  - Scouts emit alarm pheromone (orange trail particles)
  - Screen edge gets subtle gold tint
  - First bees start drifting toward player

2.0s - 5.0s:   COORDINATION
  - Formation lines appear between nearby bees
  - Dashed circle outline becomes visible (grows from 0)
  - Buzz volume increases 30% -> 60%
  - Bees accelerate toward formation positions

5.0s - 8.0s:   ENCIRCLEMENT
  - Bees reach positions, start orbiting
  - Swirl particles at maximum
  - Formation lines fully visible
  - Outline solidifying (dash pattern shrinks)

8.0s - 10.0s: COMPLETION
  - Bees lock into final positions
  - All particles fade to preparation mode
  - Outline becomes solid
  - Screen darkens slightly (pre-silence)
```

### 1.3 SILENCE Phase (3,000ms)

**The Dread**: Everything goes quiet. This is the "oh no" moment.

```typescript
const BALL_SILENCE_VFX = {
  // Audio
  audio: {
    buzzVolume: 1.0 -> 0.0,      // Fade to SILENCE over 500ms
    silenceDuration: 2500,        // Pure dread
    bassNote: {
      startAt: 2500,              // 500ms before end
      frequency: 40,              // Hz (sub-bass)
      duration: 500,
    },
  },

  // Visual stillness
  stillness: {
    beeGlowPulse: 0.5,           // Slow to half speed
    particleCount: 0,             // Kill all particles
    outlineGlow: true,            // Add outer glow
    outlineGlowColor: '#FF8800',
    outlineGlowRadius: 8,
    outlineGlowPulse: 1.0,        // Hz (slow throb)
  },

  // Screen vignette (edges darken)
  vignette: {
    color: '#000000',
    innerRadius: 0.6,             // % of screen
    outerRadius: 1.0,
    opacity: 0.2 -> 0.4,          // Increase over phase
    easing: 'linear',
  },

  // Heat shimmer (subtle)
  heatShimmer: {
    intensity: 0.2,               // Subtle distortion
    frequency: 3.0,               // Hz
    amplitude: 2,                 // pixels
    area: 'within-ball-radius',
  },
};
```

### 1.4 CONSTRICT Phase (2,000ms)

**The Escape Window**: The sphere tightens. One gap remains. GET OUT.

```typescript
const BALL_CONSTRICT_VFX = {
  // Shrinking sphere
  sphere: {
    startRadius: 150,             // px
    endRadius: 80,                // px (tight)
    easing: 'ease-in-quad',
    color: '#FFD700' -> '#FF6600',  // Gold -> Orange
    lineWidth: 2 -> 4,
  },

  // THE ESCAPE GAP - Most important visual element
  escapeGap: {
    // Gap geometry
    startAngle: 60,               // degrees
    endAngle: 30,                 // degrees (shrinks)

    // Gap highlight
    highlightColor: '#00D4FF',    // Cyan (player color)
    highlightWidth: 6,
    glowRadius: 8,
    glowOpacity: 0.5,

    // Pulsing attention grab
    pulseRate: 5,                 // Hz (FAST - urgency!)
    pulseScale: 1.0 -> 1.3,

    // Arrow indicator
    arrow: {
      show: true,
      distance: 30,               // px outside sphere
      color: '#00D4FF',
      size: 15,
      pulseWithGap: true,
    },

    // Particle stream (guiding to gap)
    guidingParticles: {
      count: 5,                   // Per frame
      color: '#00D4FF',
      size: 3,
      speed: 200,                 // px/s
      lifetime: 400,
      path: 'toward-gap-center',
    },
  },

  // Temperature visualization
  temperature: {
    startTemp: 35,                // Celsius
    endTemp: 44,                  // Celsius (near death)

    // Inner glow (heat)
    innerGlow: {
      color: '#FF6600' -> '#FF3300',
      opacity: 0.1 -> 0.3,
      easing: 'linear',
    },

    // Heat shimmer (intensifying)
    shimmer: {
      intensity: 0.2 -> 0.5,
      frequency: 3 -> 6,          // Hz (faster as temp rises)
      amplitude: 2 -> 5,          // pixels
    },
  },

  // Bee behavior
  bees: {
    vibrationIntensity: 0.5 -> 1.0,
    glowColor: '#FFB800' -> '#FF4400',  // Amber -> Hot
    glowRadius: 8 -> 12,
  },

  // Camera
  camera: {
    focusOnGap: true,
    offset: 50,                   // px toward gap
    zoom: 0.85,
  },
};
```

### 1.5 COOKING Phase (Until Death)

**The End**: Player is trapped. Temperature rises. Death is inevitable.

```typescript
const BALL_COOKING_VFX = {
  // Audio (ASMR-level detail)
  audio: {
    sizzle: {
      volume: 0.4,
      pitch: 1.0 + random(0.1),
      loop: true,
    },
    crackle: {
      interval: 200 + random(100),
      volume: 0.3,
      pitch: 0.8 + random(0.4),
    },
    heartbeat: {
      rate: 80,                   // bpm (anxious)
      volume: 0.4 -> 0.8,         // Louder as health drops
      echo: true,
    },
  },

  // Heat visualization
  heat: {
    // Center glow
    centerGlow: {
      color: '#FF0000',
      radius: 40,
      opacity: 0.4,
      pulseRate: 2,               // Hz
    },

    // Temperature indicator
    tempBar: {
      position: 'above-ball',
      width: 100,
      height: 10,
      fillColor: '#FF3300',
      bgColor: '#333333',
      borderColor: '#FF6600',
      text: '${temp}C',
      textColor: '#FFFFFF',
      flashAt: 45,                // Flash when near lethal
    },

    // Shimmer (maximum)
    shimmer: {
      intensity: 0.6,
      frequency: 8,               // Hz
      amplitude: 6,               // pixels
    },

    // Screen burn (edges)
    screenBurn: {
      intensity: 0.3 + (temp - 44) / 20,
      color: '#FF0000',
      gradient: 'radial-from-ball-center',
    },
  },

  // Damage ticks
  damageTick: {
    interval: 500,                // ms
    damage: 8,                    // HP per tick

    // Visual feedback per tick
    flash: {
      color: '#FF0000',
      duration: 100,
      opacity: 0.3,
    },

    shake: {
      amplitude: 3,
      duration: 100,
    },

    particles: {
      count: 5,
      color: '#FF6600',
      size: 4,
      velocity: 100,
      spread: 360,
    },
  },

  // Bee frenzy
  bees: {
    vibrationMax: true,           // Maximum vibration
    glowColor: '#FF2200',         // Red-hot
    glowRadius: 15,
    trailLength: 20,              // Longer trails from vibration
    trailColor: '#FF4400',
  },
};
```

### 1.6 THE BALL Color Palette

```typescript
const BALL_COLORS = {
  // Phase-specific
  forming: {
    outline: '#FFD700',           // Gold
    beeGlow: '#FFB800',           // Amber
    formationLines: '#FFD700',    // Gold
    particles: '#FFE066',         // Pollen
  },

  silence: {
    outline: '#FF8800',           // Orange (warning)
    outlineGlow: '#FF6600',       // Deep orange
    vignette: '#000000',          // Black edges
  },

  constrict: {
    outline: '#FF6600',           // Orange -> Red
    outlineProgressed: '#FF3300', // Hot red
    escapeGap: '#00D4FF',         // Cyan (safety)
    escapeGapGlow: '#00D4FF80',   // Cyan transparent
    temperature: '#FF3300',       // Heat indicator
  },

  cooking: {
    centerGlow: '#FF0000',        // Red-hot
    beeGlow: '#FF2200',           // Molten
    screenBurn: '#FF000060',      // Red vignette
    damageFlash: '#FF0000',       // Pure red flash
  },
};
```

### 1.7 THE BALL Sound Design

```typescript
const BALL_AUDIO = {
  // Forming phase
  forming: {
    alarmPheromone: {
      trigger: 'scout-marks-player',
      frequency: { start: 400, end: 2000 },
      duration: 300,
      volume: 0.4,
    },
    buzzCrescendo: {
      volume: { start: 0.3, end: 0.8 },
      pitch: { start: 1.0, end: 1.2 },
      duration: 10000,
    },
    coordinationPulse: {
      interval: 1500,
      frequency: 150,
      duration: 200,
      volume: 0.2,
    },
  },

  // Silence phase (THE MOST IMPORTANT AUDIO MOMENT)
  silence: {
    fadeOut: {
      duration: 500,
      target: 0,
      easing: 'ease-out',
    },
    silenceDuration: 2500,        // PURE SILENCE - THE DREAD
    bassNote: {
      startAt: 2500,              // 500ms before end
      frequency: 40,              // Sub-bass
      duration: 500,
      volume: 0.8,
    },
  },

  // Constrict phase
  constrict: {
    heartbeat: {
      rate: 80,                   // bpm
      volume: 0.4,
      dub: true,                  // Dub-dub sound
    },
    tensionDrone: {
      frequency: 100,
      volume: 0.2,
      filter: 'lowpass',
    },
    escapeGapPing: {
      interval: 500,
      frequency: 880,             // A5
      duration: 100,
      volume: 0.3,
      panning: 'toward-gap',
    },
  },

  // Cooking phase
  cooking: {
    sizzle: {
      loop: true,
      volume: 0.4,
      filter: 'bandpass-2khz',
    },
    crackle: {
      interval: { min: 150, max: 300 },
      volume: 0.3,
      randomPitch: true,
    },
    heartbeatEscalating: {
      rate: { start: 80, increase: 5 },  // +5 bpm per second
      maxRate: 160,
      volume: { start: 0.4, end: 0.8 },
    },
  },
};
```

---

## Part II: Kill Effects

> *"Every kill should feel like a DOPAMINE HIT."*

### 2.1 Death Spiral (The Signature Kill Animation)

**The Moment**: 25 particles spiral down, 3 rotations, pollen explosion on impact.

```typescript
const DEATH_SPIRAL = {
  // Core parameters (from Appendix E)
  particles: {
    count: 25,                    // NOT 5. TWENTY-FIVE.
    color: '#FFE066',             // Pollen gold
    spread: 45,                   // degrees
    lifespan: 400,                // ms
    rotation: 3,                  // Full rotations during descent
  },

  // Particle behavior
  behavior: {
    // Initial burst (upward, then gravity pulls down)
    initialVelocity: {
      upward: -150 - random(100), // Burst UP first
      outward: 80 + random(60),   // Spray outward
    },

    gravity: 400 + random(100),   // Heavy for dramatic fall
    airResistance: 0.02,          // Slight drift

    // Rotation during descent
    rotationSpeed: (Math.PI * 2 * 3) / 0.4,  // 3 rotations over 400ms
    rotationDecay: 0.1,           // Slow slightly at end

    // Size variation
    sizeRange: [4, 8],            // px
    sizeDecay: 0.3,               // Shrink over lifetime

    // Fade
    alphaStart: 1.0,
    alphaEnd: 0,
    fadeEasing: 'ease-out-quad',
  },

  // Impact effect (when particles hit ground)
  impact: {
    pollenBurst: {
      count: 8,
      color: '#FFE066',
      size: 2,
      velocity: 60,
      spread: 360,
      lifespan: 200,
    },
  },
};
```

### 2.2 Honey Drip (Guard/Royal Deaths)

**The Viscera**: Amber honey drips and pools on the ground.

```typescript
const HONEY_DRIP = {
  // Drip particles
  drip: {
    count: 15,
    color: '#F4A300',             // Amber
    size: [3, 6],                 // px range

    // Physics
    initialVelocity: {
      upward: -50 - random(30),   // Small pop
      horizontal: random(40) - 20,
    },
    gravity: 200,                 // px/s^2
    horizontalDrag: 0.05,         // Thick honey feel

    lifespan: 800,                // ms (drip phase)
  },

  // Pool formation
  pool: {
    delay: 800,                   // After drip phase
    size: [8, 14],                // px
    color: '#F4A300',
    opacity: 0.7,
    fadeDelay: 400,               // Linger before fade
    fadeDuration: 1200,           // Slow fade
    easing: 'linear',
  },
};
```

### 2.3 Damage Flash (Chitin Fragments)

**The Impact**: Orange-to-red fragments explode outward.

```typescript
const DAMAGE_FLASH = {
  // Fragment particles
  fragments: {
    count: 10,
    colors: ['#FF6600', '#FF0000'],  // Alternate orange/red
    size: [5, 9],
    velocity: 225,                // px/s
    spread: 360,                  // Full circle

    // Timing
    flashDuration: 100,           // Full brightness
    fadeDuration: 200,            // Fade out

    // Physics
    deceleration: 0.08,           // Quick stop for impact feel
  },

  // Screen flash
  screenFlash: {
    color: '#FF6600',
    opacity: 0.2,
    duration: 50,
  },
};
```

### 2.4 Kill Tiers and Escalation

```typescript
const KILL_TIERS = {
  // Single kill (worker)
  single: {
    screenShake: { amplitude: 2, duration: 80 },
    freezeFrames: 0,
    particles: 'death_spiral',
    sound: 'kill',
    soundPitch: 1.0,
  },

  // Guard/significant kill
  significant: {
    screenShake: { amplitude: 5, duration: 150 },
    freezeFrames: 2,              // 33ms pause
    particles: ['death_spiral', 'honey_drip'],
    sound: 'kill',
    soundPitch: 0.7,              // Lower = heavier
  },

  // Multi-kill (3+ in 150ms window)
  multi: {
    screenShake: { amplitude: 6, duration: 120 },
    freezeFrames: 4,              // 66ms pause
    particles: 'enhanced_death_spiral',
    sound: 'multi_kill',
    announcer: 'MULTI KILL',
    announcerColor: '#FFD700',
  },

  // Massacre (5+ in 150ms window)
  massacre: {
    screenShake: { amplitude: 15, duration: 350 },
    freezeFrames: 6,              // 100ms pause
    particles: 'massacre_explosion',
    sound: 'massacre',
    announcer: 'M A S S A C R E',
    announcerColor: '#FF0000',
    chromatic: true,              // Brief chromatic aberration
  },

  // Boss/Royal kill
  boss: {
    screenShake: { amplitude: 14, duration: 300 },
    freezeFrames: 3,
    particles: ['death_spiral', 'honey_drip', 'boss_explosion'],
    sound: 'boss_kill',
    announcer: 'ROYAL GUARD ELIMINATED',
    announcerColor: '#3498DB',
    slowmo: { duration: 500, timeScale: 0.3 },
  },
};
```

### 2.5 Combo Crescendo

**The Build**: As combo builds, visuals intensify.

```typescript
const COMBO_CRESCENDO = {
  // Thresholds
  thresholds: {
    5:  { brightness: 1.2, saturation: 1.0, particleDensity: 1.0 },
    10: { brightness: 1.2, saturation: 1.3, particleDensity: 1.0 },
    20: { brightness: 1.3, saturation: 1.3, particleDensity: 2.0 },
    50: { brightness: 1.4, saturation: 1.5, particleDensity: 3.0, euphoria: true },
  },

  // Euphoria mode (50+ combo)
  euphoria: {
    screenPulse: true,
    pulseRate: 2,                 // Hz
    particleRainbow: true,        // Particles cycle colors
    screenGlow: '#FFD700',
    glowIntensity: 0.2,
    chromatic: 0.5,               // Subtle chromatic aberration
  },

  // Combo counter
  counter: {
    position: 'top-right',
    font: 'bold 24px sans-serif',
    color: '#FFFFFF',
    glowColor: 'combo-tier-color',
    scale: 1.0 + combo * 0.01,    // Grows with combo
    maxScale: 2.0,
    shakeOnKill: true,
  },
};
```

---

## Part III: Player Effects

### 3.1 Dash Trail

**The Motion**: After-images and speed lines convey velocity.

```typescript
const DASH_TRAIL = {
  // After-images
  afterImages: {
    count: 4,
    spacing: 10,                  // px between images
    opacity: [0.6, 0.4, 0.2, 0.1],
    fadeTime: 150,                // ms
    color: '#00D4FF',             // Player cyan
    scale: [1.0, 0.9, 0.8, 0.7],  // Shrinking trail
  },

  // Speed lines
  speedLines: {
    count: 8,
    length: 30,
    width: 2,
    color: '#00D4FF40',           // Semi-transparent
    spread: 30,                   // degrees from direction
    velocity: -300,               // Move backward relative to player
    lifespan: 100,
  },

  // Dash burst (at start of dash)
  burst: {
    count: 12,
    color: '#00D4FF',
    size: 3,
    velocity: 150,
    spread: 180,                  // Behind player
    lifespan: 150,
  },

  // Sound
  sound: {
    type: 'whoosh',
    pitch: 1.2,
    volume: 0.4,
  },
};
```

### 3.2 Mandible Strike

**The Attack**: White flash + crescent arc shows strike zone.

```typescript
const MANDIBLE_STRIKE = {
  // White flash (hit confirmation)
  flash: {
    color: '#FFFFFF',
    opacity: 0.8,
    duration: 50,                 // ms
    radius: 20,                   // px from strike point
  },

  // Crescent arc
  crescentArc: {
    color: '#00D4FF',
    width: 4,
    angle: 90,                    // degrees
    radius: 40,                   // px
    rotation: 'toward-target',
    duration: 150,                // ms
    fadeEasing: 'ease-out',
  },

  // Impact sparks
  sparks: {
    count: 6,
    color: '#FFFFFF',
    size: 2,
    velocity: 200,
    spread: 60,                   // In strike direction
    lifespan: 100,
  },

  // Sound
  sound: {
    type: 'slash',
    pitch: 1.0,
    volume: 0.5,
  },
};
```

### 3.3 Near-Miss Graze

**The Risk-Reward**: Cyan spark when you dodge by pixels.

```typescript
const GRAZE = {
  // Detection
  zone: 30,                       // px from enemy to trigger

  // Spark particles
  spark: {
    count: 8,
    color: '#00FFFF',             // Cyan
    size: 3,
    velocity: 120,
    spread: 180,                  // Away from enemy
    lifespan: 200,
  },

  // Chain counter
  chain: {
    textColor: '#00FFFF',
    textSize: 14,
    duration: 600,
    text: 'GRAZE x${count}',
    floatUp: 60,                  // px/s
  },

  // Bonus trigger (5 consecutive grazes)
  bonusTrigger: 5,
  bonus: {
    ring: {
      color: '#00FFFF',
      radius: 40,
      duration: 400,
    },
    text: '+10% DAMAGE',
    textDuration: 1000,
  },

  // Sound
  sound: {
    type: 'graze',
    pitch: 1.2 + chain * 0.05,    // Higher pitch with chain
    volume: 0.3,
  },
};
```

### 3.4 Hit Intake (Taking Damage)

**The Hurt**: Orange pulse + chitin fragments.

```typescript
const HIT_INTAKE = {
  // Screen flash
  screenFlash: {
    color: '#FF6600',
    opacity: 0.3,
    duration: 100,
  },

  // Player flash (invincibility blink)
  playerFlash: {
    color: '#FFFFFF',
    opacity: 0.8,
    blinkRate: 10,                // Hz during i-frames
    duration: 'invincibility-duration',
  },

  // Chitin fragments
  fragments: {
    count: 8,
    colors: ['#00D4FF', '#00B4E0', '#0094C0'],  // Player color variants
    size: [3, 6],
    velocity: 150,
    spread: 360,
    lifespan: 250,
  },

  // Screen shake
  shake: {
    amplitude: 8,
    duration: 200,
  },

  // Sound
  sound: {
    type: 'damage',
    pitch: 0.8,
    volume: 0.6,
  },
};
```

---

## Part IV: Screen Effects

### 4.1 Health Vignette

**The Warning**: Screen edges darken as health drops.

```typescript
const HEALTH_VIGNETTE = {
  thresholds: {
    // Above 50%: No vignette
    0.50: { intensity: 0, pulseRate: 0 },

    // 25-50%: Warning
    0.25: { intensity: 0.5, pulseRate: 1, color: '#FF6B00' },

    // 10-25%: Danger
    0.10: { intensity: 0.8, pulseRate: 2, color: '#FF4400' },

    // Below 10%: Critical
    0.00: { intensity: 1.0, pulseRate: 4, color: '#FF0000' },
  },

  // Vignette shape
  shape: {
    innerRadius: 0.5,             // % of screen
    outerRadius: 1.0,
    blur: 0.2,                    // Gradient softness
  },

  // Heartbeat effect at critical
  heartbeat: {
    below: 0.10,
    rate: 'sync-with-audio',
    intensityPulse: 0.2,          // +20% on beat
    audioSync: true,
  },
};
```

### 4.2 Freeze Frames

**The Emphasis**: Time stops for significant moments.

```typescript
const FREEZE_FRAMES = {
  // Frame counts (at 60fps)
  significant: 2,                 // 33ms - guard kills
  multi: 4,                       // 66ms - 3+ kills
  critical: 3,                    // 50ms - criticals/executes
  massacre: 6,                    // 100ms - 5+ kills (DRAMATIC)
  boss: 3,                        // 50ms - royal kills

  // Visual treatment during freeze
  treatment: {
    desaturation: 0.2,            // Slight desaturation
    contrast: 1.1,                // Slight contrast boost
    zoom: 1.02,                   // Micro-zoom
  },

  // Resume easing
  resumeEasing: 'ease-out',       // Smooth back to full speed
  resumeDuration: 100,            // ms
};
```

### 4.3 Screen Shake

**The Impact**: Camera shake for feedback.

```typescript
const SCREEN_SHAKE = {
  profiles: {
    workerKill:   { amplitude: 2,  duration: 80,  frequency: 60 },
    guardKill:    { amplitude: 5,  duration: 150, frequency: 60 },
    bossKill:     { amplitude: 14, duration: 300, frequency: 60 },
    playerHit:    { amplitude: 8,  duration: 200, frequency: 60 },
    multiKill:    { amplitude: 6,  duration: 120, frequency: 60 },
    massacre:     { amplitude: 15, duration: 350, frequency: 60 },
    ballLunge:    { amplitude: 6,  duration: 150, frequency: 60 },
    ballCooking:  { amplitude: 3,  duration: 100, frequency: 30 },
  },

  // Shake behavior
  behavior: {
    decay: 'linear',              // Intensity decay over duration
    direction: 'random',          // Random direction per frame
    maxConcurrent: 3,             // Max overlapping shakes
    combination: 'additive',      // How to combine concurrent shakes
  },
};
```

### 4.4 Wave Transition

**The Crescendo**: Visual fanfare for wave completion.

```typescript
const WAVE_TRANSITION = {
  // Wave complete banner
  banner: {
    text: 'WAVE ${wave} COMPLETE',
    font: 'bold 32px sans-serif',
    color: '#00FF88',
    position: 'center',
    fadeIn: 200,
    hold: 1000,
    fadeOut: 300,
    scale: 1.0 -> 1.2 -> 1.0,     // Pop effect
  },

  // Ring effect
  ring: {
    color: '#00FF88',
    startRadius: 0,
    endRadius: 250,
    duration: 400,
    lineWidth: 4,
    fadeStart: 0.6,               // Fade in last 40%
  },

  // Particles
  particles: {
    count: 20,
    color: '#00FF88',
    size: [4, 8],
    velocity: 200,
    spread: 360,
    lifespan: 600,
  },

  // Screen flash
  flash: {
    color: '#00FF88',
    opacity: 0.15,
    duration: 150,
  },

  // Sound
  sound: {
    type: 'wave_complete',
    volume: 0.6,
  },
};
```

---

## Part V: Telegraph System

> *"Every attack is telegraphed. Fair deaths only."*

### 5.1 Charging Glow (Pre-Attack)

```typescript
const CHARGING_GLOW = {
  // Core parameters (from Appendix E)
  color: '#FFD700',               // Gold
  duration: 500,                  // ms pre-attack
  pulseScale: 1.2,                // Max scale
  pulseRate: 100,                 // ms per pulse
  opacity: [0.4, 0.8],            // Min -> max

  // Phases
  phases: {
    // 0-50%: Outer glow forms
    early: {
      radius: 'entity + 4',
      opacity: 0.4,
      pulseRate: 200,
    },

    // 50-80%: Glow intensifies
    mid: {
      radius: 'entity + 6',
      opacity: 0.6,
      pulseRate: 150,
    },

    // 80-100%: Flash before attack
    late: {
      radius: 'entity + 8',
      opacity: 0.8,
      pulseRate: 50,
      innerRing: true,            // Bright inner ring
      innerRingColor: '#FFFFFF',
    },
  },
};
```

### 5.2 Formation Lines

**The Coordination**: Lines between coordinating enemies.

```typescript
const FORMATION_LINES = {
  color: '#FFD700',
  opacity: 0.4,
  width: 1.5,
  fadeTime: 150,                  // ms
  minBees: 3,                     // Only show when 3+ coordinating
  maxDistance: 150,               // Only connect nearby bees

  // Line style
  style: {
    dash: [5, 5],
    pulseOpacity: true,
    pulseRate: 2,                 // Hz
  },

  // Formation detected warning
  warning: {
    text: 'FORMATION DETECTED',
    color: '#FFD700',
    show: 'first-time-per-wave',
    duration: 1500,
  },
};
```

### 5.3 Stinger Extend (Kamikaze Warning)

**The Suicide Attack**: Visible stinger before kamikaze.

```typescript
const STINGER_EXTEND = {
  // Visual
  stinger: {
    length: 15,                   // px
    width: 3,
    color: '#6B2D5B',             // Venom purple
    glowColor: '#6B2D5B80',
    glowRadius: 4,
    extend: {
      duration: 300,              // ms
      easing: 'ease-out',
    },
  },

  // Trail
  trail: {
    color: '#6B2D5B',
    duration: 300,                // ms linger
    width: 3,
    fadeEasing: 'linear',
  },

  // Warning indicator
  warning: {
    text: '!',
    color: '#FF0000',
    position: 'above-enemy',
    offset: 20,                   // px
    font: 'bold 20px sans-serif',
    pulse: true,
    pulseRate: 4,                 // Hz
  },

  // Sound
  sound: {
    type: 'stinger_extend',
    pitch: 1.5,
    volume: 0.4,
  },
};
```

### 5.4 Lunge Windup

**THE BALL Attack**: Clear telegraph for formation lunge.

```typescript
const LUNGE_TELEGRAPH = {
  // Windup phase (600ms - very readable!)
  windup: {
    duration: 600,                // ms (was 350ms - now slower)

    // Charging ring
    ring: {
      color: '#FF4400',
      startRadius: 15,
      endRadius: 25,
      lineWidth: 3 -> 5,          // Thickens
      progress: 'arc-fill',       // Ring fills as charge progresses
    },

    // Inner glow
    glow: {
      color: '#FF6600',
      radius: 10 -> 15,
      opacity: 0 -> 0.4,
    },

    // Warning text
    warning: {
      text: '!',
      color: '#FFAA00' -> '#FF0000',
      font: 'bold 20px sans-serif',
      position: 'above-bee',
      offset: 20,
    },
  },

  // Attack phase (400ms - slower for counterplay)
  attack: {
    duration: 400,                // ms (was 150ms)

    // Trail
    trail: {
      color: '#FF0000',
      width: 6,
      opacity: 0.6,
      fadeOnReturn: true,
    },

    // Impact ring
    impactRing: {
      color: '#FF4444',
      radius: 15,
      pulse: true,
      pulseRate: 20,              // Hz (fast)
    },
  },

  // Return phase (300ms)
  return: {
    duration: 300,
    trailOpacity: 0.3,            // Faded trail
  },

  // Sound
  sound: {
    windup: { type: 'charge', pitch: 0.8, volume: 0.3 },
    attack: { type: 'lunge', pitch: 1.0, volume: 0.5 },
    hit: { type: 'impact', pitch: 0.7, volume: 0.6 },
  },
};
```

---

## Part VI: Performance Budget

> *"Beautiful AND performant. No compromises."*

### 6.1 Particle Limits

```typescript
const PERFORMANCE_BUDGET = {
  // Hard limits
  particles: {
    max: 500,                     // Never exceed
    target: 300,                  // Normal gameplay
    cull: 'oldest-first',         // When over limit
    minLifetime: 50,              // Never create particles < 50ms
  },

  // Per-frame limits
  perFrame: {
    particleSpawns: 50,           // Max new particles per frame
    particleUpdates: 500,         // Max updates per frame
    renderCalls: 1000,            // Max draw calls
  },

  // LOD (Level of Detail)
  lod: {
    high: { particleMultiplier: 1.0, effectQuality: 'full' },
    medium: { particleMultiplier: 0.6, effectQuality: 'reduced' },
    low: { particleMultiplier: 0.3, effectQuality: 'minimal' },
  },

  // Automatic quality scaling
  autoScale: {
    targetFPS: 60,
    scaleDownAt: 50,              // Drop quality below 50 fps
    scaleUpAt: 58,                // Restore quality above 58 fps
    cooldown: 2000,               // ms between adjustments
  },
};
```

### 6.2 Effect Priority

When at budget, prioritize these effects:

| Priority | Effect | Reason |
|----------|--------|--------|
| 1 | THE BALL visuals | Core mechanic - NEVER degrade |
| 2 | Kill death spiral | Core feedback - essential |
| 3 | Telegraph glows | Fairness - required |
| 4 | Screen shake | Feel - very cheap |
| 5 | Dash trail | Movement feedback |
| 6 | Combo particles | Enhancement |
| 7 | Ambient particles | Polish - first to cut |

---

## Part VII: Implementation Checklist

### Phase 1: THE BALL Polish (Week 1)

- [ ] Forming phase: coordination pulse, formation lines
- [ ] Silence phase: audio fade, screen vignette, stillness
- [ ] Constrict phase: escape gap highlight, arrow, temperature
- [ ] Cooking phase: heat shimmer, damage ticks, screen burn
- [ ] Camera: phase-appropriate zoom and focus
- [ ] Audio: full soundscape implementation

### Phase 2: Kill Juice (Week 2)

- [ ] Death spiral particles (25, 3 rotations)
- [ ] Honey drip for guard/royal
- [ ] Freeze frames on significant kills
- [ ] Screen shake profiles
- [ ] Kill tier detection (single/multi/massacre)
- [ ] Combo crescendo visuals

### Phase 3: Player Effects (Week 3)

- [ ] Dash trail (after-images + speed lines)
- [ ] Mandible strike arc
- [ ] Graze sparks
- [ ] Hit intake fragments
- [ ] Health vignette

### Phase 4: Telegraph System (Week 4)

- [ ] Charging glow (all phases)
- [ ] Formation lines
- [ ] Stinger extend
- [ ] Lunge windup (full sequence)
- [ ] Warning indicators

---

## Appendix A: Color Reference

```typescript
const VFX_COLORS = {
  // Player (Hornet)
  player: '#00D4FF',              // Electric cyan
  playerGlow: '#00D4FF80',
  playerTrail: '#00D4FF60',

  // Enemies (Bees)
  worker: '#F4A300',              // Honey amber
  scout: '#FFE066',               // Pollen gold
  guard: '#8B6914',               // Beeswax brown
  propolis: '#2A1F14',            // Propolis dark
  royal: '#6B2D5B',               // Royal purple

  // THE BALL
  ballForming: '#FFD700',         // Gold (coordination)
  ballSilence: '#FF8800',         // Orange (warning)
  ballConstrict: '#FF6600',       // Deep orange
  ballCooking: '#FF0000',         // Red (danger)
  ballEscapeGap: '#00D4FF',       // Cyan (safety)

  // Effects
  deathSpiral: '#FFE066',         // Pollen gold
  honeyDrip: '#F4A300',           // Amber
  damageFlash: ['#FF6600', '#FF0000'],
  graze: '#00FFFF',               // Cyan
  telegraph: '#FFD700',           // Gold
  stinger: '#6B2D5B',             // Venom purple

  // UI
  healthLow: '#FF6B00',           // Orange
  healthCritical: '#FF0000',      // Red
  waveComplete: '#00FF88',        // Green
  levelUp: '#FFD700',             // Gold
};
```

---

## Appendix B: Timing Reference

```typescript
const VFX_TIMING = {
  // THE BALL phases
  ball: {
    forming: 10000,               // 10 seconds
    silence: 3000,                // 3 seconds
    constrict: 2000,              // 2 seconds
    cookingTick: 500,             // Damage every 500ms
  },

  // Particles
  particles: {
    deathSpiral: 400,
    honeyDrip: 800,
    poolFade: 1200,
    damageFlash: 300,
    graze: 200,
  },

  // Screen effects
  screen: {
    freezeSignificant: 33,        // 2 frames
    freezeMulti: 66,              // 4 frames
    freezeMassacre: 100,          // 6 frames
    shakeDecay: 'linear',
  },

  // Telegraph
  telegraph: {
    chargingGlow: 500,
    lungeWindup: 600,             // RUN 037: Slower for readability
    lungeAttack: 400,             // RUN 037: Slower for counterplay
    lungeReturn: 300,
  },
};
```

---

## Appendix C: Sound Cues

```typescript
const VFX_SOUNDS = {
  // Kills
  kill: { volume: 0.5, pitchRange: [0.9, 1.1] },
  multiKill: { volume: 0.6, pitch: 1.2 },
  massacre: { volume: 0.8, pitch: 0.8 },
  bossKill: { volume: 0.7, pitch: 0.6 },

  // Player
  dash: { volume: 0.4, pitch: 1.2 },
  attack: { volume: 0.5, pitch: 1.0 },
  graze: { volume: 0.3, pitch: 'chain-dependent' },
  damage: { volume: 0.6, pitch: 0.8 },

  // THE BALL
  ballForming: { volume: 0.3 -> 0.8, pitch: 1.0 -> 1.2 },
  ballSilence: { volume: 0, duration: 2500 },
  ballBass: { volume: 0.8, pitch: 0.3 },
  ballCooking: { volume: 0.4, sizzle: true },
  heartbeat: { volume: 0.4 -> 0.8, rate: 80 -> 160 },

  // Telegraph
  chargingGlow: { volume: 0.3, pitch: 'charge-up' },
  lungeAttack: { volume: 0.5, pitch: 1.0 },
  lungeHit: { volume: 0.6, pitch: 0.7 },
};
```

---

*"Every effect should make players FEEL something. Not notice. FEEL."*

*"If it's not clip-worthy, it's not done."*

*"Make it POP. Make it PUNCH. Make it MEMORABLE."*

---

**Filed**: 2025-12-28
**Status**: Ready for Implementation
**Voice Check**: Daring, bold, creative, opinionated but not gaudy.
