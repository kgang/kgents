# HORNET SPRITE SPECIFICATION

## Executive Summary

**Sprite Size**: 48x48 pixels (recommended over 32x32)

*Rationale*: At 32x32, the mandibles become indistinct blobs. 48x48 gives us 6 extra pixels per axis to sell the APEX PREDATOR silhouette - enough to make the mandibles read as distinct pincers, not a smudge. The hornet should dominate screen presence anyway.

**Palette**: 10 colors total

```
PRIMARY BODY:
#FF6B00 - Hornet Orange (thorax, head highlights)
#CC5500 - Burnt Orange (body shading)
#993D00 - Deep Orange (dark body bands)

DARK STRUCTURE:
#1A1A1A - Venom Black (legs, mandibles, antennae)
#2D1F3D - Bruise Purple (black shading - the "purple tint")
#0D0D0D - Void Black (deepest shadows)

ACCENTS:
#FFD700 - Warning Yellow (eyes, threat markings)
#FFE55C - Pale Yellow (eye gleam, mandible edge)

WINGS:
#4A6B8C - Wing Blue (semi-transparent feel)
#2A3B4C - Wing Shadow

OUTLINE:
#3D2914 - Shadow Comb (selective outline)
```

---

## 1. SPRITE SHEET LAYOUT

### Overall Grid: 384 x 288 pixels (8 columns x 6 rows of 48x48 cells)

```
ROW 0: IDLE (4 frames) + IDLE_AGGRO (4 frames)
ROW 1: MOVE_DOWN (4) + MOVE_UP (4)
ROW 2: MOVE_LEFT (4) + MOVE_RIGHT (4)
ROW 3: ATTACK (6 frames: wind-up, strike, HOLD, recover x3)
ROW 4: DASH (4 frames) + DASH_RECOVER (2) + HIT (2)
ROW 5: DEATH (6 frames)
```

### Frame Breakdown

**IDLE** (4 frames, loops)
- Frame 0: Neutral stance, mandibles slightly parted
- Frame 1: Thorax expands (breathing), wings micro-twitch
- Frame 2: Mandibles click together (signature)
- Frame 3: Return to neutral, antenna flick

**IDLE_AGGRO** (4 frames, triggers when enemies nearby)
- Same as idle but mandibles open wider
- Head turns slightly toward nearest threat
- Wings buzz faster (more blur)

**MOVE** (4 frames per direction)
- Diagonal movement uses left/right sprites
- Body tilts into movement direction
- Wing blur INTENSIFIES during movement
- Legs tucked underneath (flight mode)

**ATTACK** (6 frames)
- F0: Wind-up - head rears back, mandibles WIDE open
- F1: Strike - full extension, mandibles forward
- F2-3: HOLD - mandibles clamped (this is the kill moment)
- F4-5: Recover - smooth retraction, dripping venom pixel

**DASH** (4 frames + 2 recover)
- F0-1: Blur/streak effect - body elongates horizontally
- F2-3: Motion lines, near-invisible wings
- F4-5: Momentum recovery, slight overshoot bounce

**DEATH** (6 frames - DIGNIFIED, not pathetic)
- F0: Impact stagger, but STILL STANDING
- F1: One wing crumples, mandibles STILL OPEN in defiance
- F2-3: Controlled descent - falling like a warrior, not flopping
- F4: Ground impact, legs curl (biological accuracy)
- F5: Final - still, but pose retains dignity. Eyes last to fade.

---

## 2. KEY VISUAL FEATURES

### MANDIBLES (The Signature)

The mandibles are EVERYTHING. They must:
- Be visible in EVERY pose
- Take up 8-10 pixels of the face width
- Have a distinct "pincer" shape, not a rounded mouth
- Gleam with a single yellow highlight pixel on each

**Animation Note**: Mandibles should NEVER fully close during idle. Always a gap. The hornet is always ready.

### WINGS (Motion Blur Circles)

**Static poses**: Wings rendered as elongated ovals, semi-transparent blue
**Moving/hovering**: Wings become BLUR CIRCLES - two overlapping ellipses with dithered edges

**Implementation**: 50% opacity overlay, 2-frame oscillation between blur positions

### BODY SHAPE (Silhouette Priority)

The silhouette must read as "HORNET" from any angle in 0.1 seconds.

**Key proportions**:
- HEAD: Large, 30% of body width (to fit mandibles)
- THORAX: Muscular hump, highest point of sprite
- ABDOMEN: Tapered, ends in stinger point (subtle)
- WAIST: Distinct "wasp waist" - 2px pinch between thorax and abdomen

### WHAT MAKES THIS NOT A GENERIC INSECT

1. **COLOR BLOCKING**: Distinct orange/black BANDS on abdomen (3 bands minimum)
2. **EYE SHAPE**: Large, kidney-shaped, not circular. PREDATOR eyes.
3. **MANDIBLE PROMINENCE**: They jut FORWARD from the head, not underneath
4. **BODY MASS**: Thicc. This isn't a delicate creature. It has WEIGHT.
5. **STANCE**: Slight forward lean, even in idle. Always advancing.

---

## 3. CHARACTER PERSONALITY IN PIXELS

### SWAGGER Conveyance

**Idle Animation Personality**:
- Frame 2's mandible click is the key - it's a *threat display*, like cracking knuckles
- Antenna movement is SLOW and deliberate, not twitchy
- The breathing animation expands the thorax UP, not out - a power pose
- Head occasionally tilts, as if sizing up prey

**Micro-animations that sell it**:
- 1-pixel weight shift side to side (too cool to stand still)
- Eye gleam pixel blinks independently from body animation
- Wing blur pulses with "engine idle" rhythm

### APEX PREDATOR Conveyance

**Visual Hierarchy**:
- Hornet sprite is 20% larger than bee sprites (if bees are 32x32, hornet is 48x48)
- Orange reads as "DANGER" against the honeycomb brown environment
- Attack animation has IMPACT FRAMES - 1 frame of white flash on contact

**Movement Philosophy**:
- Never rushed, never panicked
- Turn animations are SMOOTH (no instant direction changes)
- Dash is the only "fast" movement - and it's terrifying

**Death Animation Philosophy**:
- The hornet doesn't flail. Doesn't beg.
- Falls forward if possible - died attacking
- Final frame: eyes still visible, mandibles still parted
- Message: "I lost. But I was magnificent."

---

## 4. ASCII/TEXT MOCKUP

### IDLE POSE (Front-facing)

```
           \ | /
            \|/           <- Antennae (curved outward)
         .--===--.
        /  O   O  \       <- Eyes (WARNING YELLOW, large)
       |    ___    |      <- Head outline
       |   /   \   |
      [===]     [===]     <- MANDIBLES (prominent, open)
        \   ▓▓▓   /       <- Face/mouth area
    ~~~~ \_______/ ~~~~   <- Wing blur (~~~)
    ~~~~  |█████|  ~~~~   <- Thorax (powerhouse)
     ~~~  |▓▓▓▓▓|  ~~~    <- Thorax shading
          |  █  |         <- Waist (PINCHED)
         /█▓█▓█▓\         <- Abdomen (banded)
        / ▓█▓█▓█ \
        \  ▓█▓█  /
         \  ▼  /          <- Stinger (subtle)
          `---´
```

### ATTACK POSE (Strike Frame - F1)

```
           \ | /
            \|/
         .--===--.
        /  ◉   ◉  \       <- Eyes WIDE, intense
       |    ___    |
       |   /   \   |
   [=====>     <=====]    <- MANDIBLES EXTENDED FORWARD
        \   ▓▓▓   /
    ~~~~ \_______/ ~~~~
    ~~~~  |█████|  ~~~~   <- Body LUNGES forward (offset 2px)
     ~~~  |▓▓▓▓▓|  ~~~
          |  █  |
         /█▓█▓█▓\
        / ▓█▓█▓█ \
        \  ▓█▓█  /
         \  ▼  /
          `---´
```

### DEATH POSE (Final Frame - F5)

```
                              <- Antennae droop but don't break
         .--===--.
        /  ○   ○  \       <- Eyes dimmed (not closed - DIGNITY)
       |    ___    |
       |   /   \   |
      [===]     [===]     <- Mandibles STILL PARTED (defiant)
        \   ░░░   /       <- Face grayed
         \_______/        <- No wing blur (wings folded)
          |░░░░░|
          |░░░░░|    ____ <- Ground line
          |  ░  |___/
         _|░░░░░|_        <- Legs curled (biological)
        / ░░░░░░░ \       <- Abdomen still has form
        \   ░░   /
         \     /          <- Stinger relaxed
          `===´
```

---

## 5. ANIMATION NOTES

### Timing Table

| Animation | Frames | MS/Frame | Total MS | Loop? | Easing |
|-----------|--------|----------|----------|-------|--------|
| IDLE | 4 | 250 | 1000 | Yes | ease-in-out |
| IDLE_AGGRO | 4 | 200 | 800 | Yes | ease-in-out |
| MOVE | 4 | 100 | 400 | Yes | linear |
| ATTACK | 6 | 50/50/100/100/75/75 | 450 | No | custom |
| DASH | 4+2 | 40/40/40/40/60/60 | 280 | No | ease-out |
| HIT | 2 | 100 | 200 | No | ease-out |
| DEATH | 6 | 150/150/200/200/300/400 | 1400 | No | ease-in |

### Attack Animation Detail

```
ATTACK TIMING BREAKDOWN:

F0 (50ms):  WIND-UP    - Head rears back, mandibles OPEN
            Easing: ease-out (quick start)
            Sound: "swoosh" anticipation

F1 (50ms):  STRIKE     - Full forward lunge, mandibles EXTEND
            Easing: linear (FAST)
            Sound: "snap"
            VFX: 2px white impact lines

F2-3 (100ms each): HOLD - Mandibles CLAMPED
            Easing: none (static hold)
            Sound: sustained "crunch"
            VFX: Single red pixel (venom/damage)
            CRITICAL: This is when damage applies

F4 (75ms):  RECOVER-1  - Begin retraction
            Easing: ease-in
            Sound: none

F5 (75ms):  RECOVER-2  - Return to idle-ready
            Easing: ease-out
            Sound: satisfied "click"
            VFX: Single drip pixel falls from mandible
```

### Special Effects Layer

**Wing Blur Effect**:
- Separate sprite layer, rendered BEHIND body
- Oscillates between two positions (every 50ms in idle, every 25ms in move)
- Color: #4A6B8C at 50% opacity
- Dithering on edges (checkerboard pattern)

**Mandible Gleam**:
- Single pixel of #FFE55C on upper mandible edge
- Appears for 1 frame during CLICK (idle F2) and STRIKE (attack F1)
- Subtle but sells the "sharp" read

**Eye Glow**:
- Eyes are #FFD700 base
- During IDLE_AGGRO and ATTACK, eyes get 1px #FFFFFF center
- Creates "predator tracking" feel

---

## Implementation Notes

### For the Renderer

1. **Layer Order** (back to front):
   - Shadow (dark ellipse under sprite)
   - Wing blur (separate animated overlay)
   - Body sprite
   - Effect layer (gleams, particles)

2. **Direction Handling**:
   - 8-directional input maps to 4 sprite directions
   - Diagonals use left/right sprites with body tilt offset
   - NEVER flip sprites - mandibles must stay consistent

3. **Hitbox Note**:
   - Visual sprite is 48x48
   - Hitbox should be 32x32, centered on thorax
   - Mandibles extend BEYOND hitbox (attack range visual)

### Color Palette Application

```
BODY MAPPING:
- Thorax top: #FF6B00 (Hornet Orange)
- Thorax shadow: #CC5500 (Burnt Orange)
- Abdomen bands: Alternating #FF6B00, #1A1A1A, #FF6B00, #1A1A1A
- Band shadows: #993D00, #2D1F3D respectively
- Legs/Antennae: #1A1A1A with #2D1F3D shading
- Mandibles: #1A1A1A base, #FFE55C edge highlight, #0D0D0D inner shadow
- Eyes: #FFD700 fill, #FFE55C gleam pixel, #3D2914 outline

ENVIRONMENT CONTRAST:
- Honeycomb background: Browns, golds
- Hornet Orange will POP against this
- Venom Black provides grounding
- Warning Yellow eyes will TRACK across screen (player always knows where they are)
```

---

## The Swagger Checklist

Before finalizing any sprite, verify:

- [ ] Mandibles visible and OPEN (or clearly about to be)
- [ ] Silhouette reads as "BIG HORNET" not "generic bug"
- [ ] Weight shift present (never static, never symmetrical)
- [ ] Eyes convey intent (not vacant)
- [ ] Animation has SNAP, not mush
- [ ] Death maintains dignity
- [ ] Color palette enforced (no drift)
- [ ] This hornet knows the score and hunts anyway

---

*"The hornet doesn't hope to win. It knows. The sprite should know too."*

**Filed**: 2025-12-28
**Status**: Design Specification v1.0
