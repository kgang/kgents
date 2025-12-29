# Bee Sprites Specification: Hornet Siege

> *"These are the heroes of their story. They fight for their home. They always win."*

**Status**: Design Specification
**Version**: 1.0.0
**Date**: 2025-12-28
**Cross-Reference**: PROTO_SPEC.md S6, 03-visual-audio.md

---

## Design Philosophy

The bees are not mindless fodder. They are **DEFENDERS** of their civilization. The player (the giant hornet) is the INVADER. This framing must be visually evident:

| Aspect | Hornet (Player) | Bees (Enemies) |
|--------|-----------------|----------------|
| **Palette** | Aggressive orange/black (#FF6B00) | Warm amber/gold (#F4A300) |
| **Silhouette** | Angular, predatory | Rounded, organic |
| **Animation** | Sharp, violent | Coordinated, purposeful |
| **Death** | Dignified collapse | Heroic sacrifice |

**The Tragedy**: The player is the monster. The bees are the heroes. Every sprite should remind the player of this truth.

---

## Color Palette (Distinct from Hornet Orange)

### Primary Bee Colors

| Type | Primary | Secondary | Accent | Hex Values |
|------|---------|-----------|--------|------------|
| **Worker** | Honey Amber | Pollen Gold | Warm White | `#F4A300`, `#FFE066`, `#FFF8E7` |
| **Scout** | Light Amber | Speed Cyan | Alert Yellow | `#F9B208`, `#00D4FF`, `#FFD700` |
| **Guard** | Beeswax Brown | Dark Umber | Armor Gold | `#8B6914`, `#4A3000`, `#C4A000` |
| **Propolis** | Purple-Amber | Deep Violet | Resin Sheen | `#9B59B6`, `#6B2D5B`, `#D4A5D4` |
| **Royal** | Royal Purple | Gold Leaf | Crown White | `#6B2D5B`, `#FFD700`, `#FFFFFF` |

### Formation/Coordination Colors

| Element | Color | Use |
|---------|-------|-----|
| Formation Glow Lines | `#FFD700` @ 40% | Connecting coordinated bees |
| Alarm Cascade | `#FF4444` → `#FFD700` | Spreading pheromone alert |
| THE BALL Forming | `#FF6B6B` → `#FF3300` | Heat buildup indicator |
| Pheromone Trail | `#F4A300` @ 30% | Scout marking paths |

---

## The Five Bee Types

### 1. WORKER BEE (Basic)

> *"The backbone of the colony. Individually weak, collectively unstoppable."*

#### Specifications

| Property | Value | Notes |
|----------|-------|-------|
| **Sprite Size** | 12x12 px (body) | Smallest unit |
| **Collision Radius** | 8 px | Tight hitbox |
| **Shape** | Circle/Oval | Simple, readable |
| **HP** | Low (3-5 hits) | Numbers game |
| **Speed** | Medium (80 px/s) | Swarm movement |

#### Visual Breakdown

```
WORKER BEE - 12x12px body

    ████    ← Honey Amber head (#F4A300)
   ██████   ← Body with subtle stripes
   ██  ██   ← Pollen Gold underbelly (#FFE066)
   ██████
    ████    ← Stinger hint (1px darker)
     ▪▪     ← Tiny legs (optional detail)

Key Features:
- Round, plump body
- Subtle golden glow
- 2 wing positions (up/down) for flutter
```

#### ASCII Size Comparison (Proportional)

```
Worker:  (·)
Scout:   (·>)
Guard:   [■■]
Propolis: <◊>
Royal:   《★》
```

#### Color Application

```
         ┌─ FFF8E7 (highlight, 2px)
         │  ┌─ F4A300 (body, main fill)
         │  │  ┌─ DAA520 (shadow/stripe)
         ▼  ▼  ▼
    [H][B][S]  (cross-section)
```

#### Animation Frames

| Animation | Frames | Duration | Notes |
|-----------|--------|----------|-------|
| **Idle** | 2 | 200ms loop | Wing flutter |
| **Chase** | 4 | 100ms loop | Fast wing + forward lean |
| **Telegraph** | 3 | 400ms total | Glow + pullback |
| **Attack** | 2 | 100ms | Lunge forward |
| **Recovery** | 2 | 400ms | Slower flutter, dimmed |
| **Death** | 5 | 600ms | Spiral descent + pollen burst |

#### Death Animation Detail

```
Frame 1 (0ms):    ●      Hit flash (white overlay)
Frame 2 (100ms):  ◐      Begin rotation
Frame 3 (250ms):  ○╮     Spin + descend
Frame 4 (400ms):  ·╯     Shrinking + trail
Frame 5 (600ms):  ★      Pollen burst (5-8 particles)

Particle: #FFE066, 3px, 400ms lifetime, radial spread
```

---

### 2. SCOUT BEE (Fast)

> *"The colony's eyes. They see you. They tell the others."*

#### Specifications

| Property | Value | Notes |
|----------|-------|-------|
| **Sprite Size** | 14x10 px (body) | Elongated for speed |
| **Collision Radius** | 6 px | Smaller than Worker |
| **Shape** | Triangle/Wedge | Speed silhouette |
| **HP** | Very Low (2-3 hits) | Fragile but fast |
| **Speed** | Fast (150 px/s) | Fastest bee type |

#### Visual Breakdown

```
SCOUT BEE - 14x10px body

      ▼        ← Alert antenna (animated)
    ▄▄▄▄       ← Streamlined head
   ▀█████▶    ← Elongated body, pointed rear
    ▀▀▀▀       ← Speed lines (during chase)

Key Features:
- Triangular/wedge shape
- Antennae visibly "alert" (wiggling)
- Speed trails when moving fast
- Lighter coloring (faster = lighter visual weight)
```

#### Color Application

```
Primary: #F9B208 (lighter amber)
Accent:  #00D4FF (cyan speed streaks, 40% opacity)
Alert:   #FFD700 (antenna glow when alarming)

Speed Lines: 3 trailing lines, #F9B208 @ 30%, 0.3s linger
```

#### Distinguishing Features

1. **Triangle Shape**: Instantly different from round Worker
2. **Speed Lines**: 3 cyan streaks trailing behind when chasing
3. **Alert State**: Antenna glow + ripple when triggering pheromone
4. **Erratic Movement**: Zigzag path, not straight line

#### Animation Frames

| Animation | Frames | Duration | Notes |
|-----------|--------|----------|-------|
| **Idle** | 3 | 150ms loop | Antenna twitch |
| **Chase** | 4 | 80ms loop | Blur effect + streaks |
| **Alert** | 6 | 500ms | Pheromone release pulse |
| **Telegraph** | 2 | 300ms | Quick wind-up |
| **Attack** | 3 | 80ms | Fast dash |
| **Death** | 4 | 400ms | Quick spiral, fewer particles |

#### Pheromone Alert Visual

```
Alert Trigger (when Scout spots player):

Frame 1:  ◯      Scout pauses
Frame 2:  (◯)    Ring appears (#FFD700 @ 50%)
Frame 3: ((◯))   Ring expands (100px radius)
Frame 4:(((◯)))  Ring fades, nearby bees glow briefly

Other bees within 100px: +20% speed for 3s
Visual: Golden pulse spreads from Scout
```

---

### 3. GUARD BEE (Tank)

> *"The colony's shield. They don't chase. They hold the line."*

#### Specifications

| Property | Value | Notes |
|----------|-------|-------|
| **Sprite Size** | 20x24 px (body) | Visibly larger |
| **Collision Radius** | 14 px | Big hitbox |
| **Shape** | Square/Rectangle | Blocky = tanky |
| **HP** | High (10-15 hits) | Takes punishment |
| **Speed** | Slow (40 px/s) | Deliberate movement |

#### Visual Breakdown

```
GUARD BEE - 20x24px body

     ████████     ← Heavy head, armored
    ██████████    ← Broad thorax
   ████████████   ← Armored abdomen (2px darker plates)
   █│██████│█     ← Armor lines (vertical)
   █│██████│█
    ██████████
     ████████     ← Reinforced rear

Key Features:
- Square/rectangular silhouette (NOT round)
- Visible "armor plating" lines
- Darker, earthier coloring
- Slower, more deliberate animations
```

#### Color Application

```
Primary:  #8B6914 (beeswax brown)
Armor:    #4A3000 (dark umber plate lines)
Highlight: #C4A000 (gold trim on armor)

Armor Lines: 2px wide, #4A3000, vertical striping
```

#### Distinguishing Features

1. **Square Shape**: Unmistakably different from round/triangle
2. **Armor Lines**: 2 vertical stripes on body (like carapace plates)
3. **Size**: 1.5x larger than Worker
4. **Stance**: Faces player, doesn't turn sideways

#### Animation Frames

| Animation | Frames | Duration | Notes |
|-----------|--------|----------|-------|
| **Idle** | 2 | 400ms loop | Slow sway, grounded |
| **Chase** | 4 | 200ms loop | Heavy stomp feel |
| **Telegraph** | 4 | 500ms | Red glow, expanding |
| **Attack** | 4 | 300ms | Ground pound AOE |
| **Recovery** | 3 | 800ms | Visibly winded |
| **Death** | 6 | 800ms | Crumple + armor scatter |

#### Death Animation Detail

```
Frame 1 (0ms):    [■]     Flash white
Frame 2 (150ms):  [┘]     Armor plates separate
Frame 3 (300ms):  |╲╱|    Fragments scatter
Frame 4 (500ms):   ╱╲     Body crumples
Frame 5 (650ms):   ══     Flattens
Frame 6 (800ms):   ··     Dissolve to amber mist

Particles: 4-6 armor fragments (#4A3000),
           8-10 amber mist (#F4A300 @ 50%)
```

---

### 4. PROPOLIS BEE (Ranged)

> *"The colony's alchemist. Sticky death from a distance."*

#### Specifications

| Property | Value | Notes |
|----------|-------|-------|
| **Sprite Size** | 16x16 px (body) | Medium, distinctive |
| **Collision Radius** | 10 px | Standard |
| **Shape** | Diamond/Rhombus | Unique silhouette |
| **HP** | Medium (5-8 hits) | Glass cannon |
| **Speed** | Medium (60 px/s) | Prefers distance |

#### Visual Breakdown

```
PROPOLIS BEE - 16x16px body

       ▲         ← Pointed top
      ◆◆◆        ← Diamond body shape
     ◆◆█◆◆       ← Dark purple core (projectile organ)
     ◆◆◆◆◆
      ◆◆◆        ← Visible resin drip
       ▼         ← Pointed bottom

Key Features:
- Diamond/rhombus shape (unique!)
- Visible "projectile organ" (darker center)
- Propolis drip animation (2px amber drop)
- Purple-tinted (different from gold Workers)
```

#### Color Application

```
Primary:  #9B59B6 (purple-amber)
Core:     #6B2D5B (deep violet, projectile organ)
Drip:     #D4A5D4 (resin sheen, animated)
Projectile: #8E44AD with #F4A300 sticky trail

The purple tint makes them INSTANTLY recognizable
```

#### Distinguishing Features

1. **Diamond Shape**: No other bee is a rhombus
2. **Purple Tint**: Only purple-ish bee (all others are gold/brown)
3. **Drip Animation**: Constant propolis drip from body
4. **Projectile Indicator**: Glows brighter before firing

#### Animation Frames

| Animation | Frames | Duration | Notes |
|-----------|--------|----------|-------|
| **Idle** | 3 | 250ms loop | Drip formation cycle |
| **Chase** | 3 | 150ms loop | Strafe-like movement |
| **Aim** | 4 | 400ms | Purple glow intensifies |
| **Fire** | 3 | 100ms | Projectile release |
| **Recovery** | 3 | 1500ms | Long cooldown, dim |
| **Death** | 5 | 600ms | Sticky explosion |

#### Projectile Specification

```
PROPOLIS GLOB - 8x8px

  ██
 ████   ← Purple glob (#8E44AD)
  ██    ← Amber trail (#F4A300 @ 50%)

Speed: 200 px/s
Damage: 10
Effect: 2s slow (50% speed reduction)
Lifetime: 3s
Trail: Sticky residue lingers 0.5s
```

#### Death Animation Detail

```
Frame 1 (0ms):    ◆     Flash purple
Frame 2 (100ms):  ◈     Crack lines appear
Frame 3 (250ms):  ┼     Splatter pattern
Frame 4 (400ms):  ∙∙∙   Glob fragments
Frame 5 (600ms):  ~~~   Sticky pool (fades over 2s)

Sticky Pool: #8E44AD @ 40%, 30px radius, 2s linger
Any bee walking over: no effect
Player walking over: 30% slow for 0.5s
```

---

### 5. ROYAL GUARD (Elite/Boss)

> *"The Queen's chosen. They anchor THE BALL. They end the siege."*

#### Specifications

| Property | Value | Notes |
|----------|-------|-------|
| **Sprite Size** | 28x32 px (body) | Largest bee |
| **Collision Radius** | 18 px | Boss-sized |
| **Shape** | Octagon | Regal, complex |
| **HP** | Very High (20-30 hits) | Mini-boss |
| **Speed** | Variable (60-100 px/s) | Phase-dependent |

#### Visual Breakdown

```
ROYAL GUARD - 28x32px body

       ████████        ← Crown accent (#FFD700)
      ▀████████▀
     ████████████      ← Royal purple body (#6B2D5B)
    ██████████████     ← Gold trim edges
    ████╳╳╳╳╳╳████     ← Pattern (cross-hatch)
    ██████████████
     ████████████
      ▄████████▄
        ████           ← Powerful stinger

Key Features:
- Octagon shape (8 sides = royalty)
- Crown/tiara accent on head
- Gold trim on all edges
- Cross-hatch pattern on body
- Dramatically larger than all others
```

#### Color Application

```
Primary:  #6B2D5B (royal purple)
Crown:    #FFD700 (gold leaf)
Trim:     #FFD700 (gold edge, 2px)
Pattern:  #4A1A4A (darker purple cross-hatch)
Eyes:     #FF0000 (red, menacing)

The gold crown makes them unmistakable even at distance
```

#### Distinguishing Features

1. **Octagon Shape**: Complex = dangerous
2. **Gold Crown**: Visible from anywhere on screen
3. **SIZE**: 2.3x larger than Worker
4. **Red Eyes**: Only bee with colored eyes
5. **BALL Anchor**: Always center of formations

#### Animation Frames

| Animation | Frames | Duration | Notes |
|-----------|--------|----------|-------|
| **Idle** | 4 | 300ms loop | Royal sway, crown glint |
| **Chase** | 6 | 150ms loop | Wings + body undulation |
| **Telegraph** | 6 | 600ms | Multi-phase indicator |
| **Combo Phase 1** | 4 | ~130ms | Charge toward player |
| **Combo Phase 2** | 4 | ~130ms | AOE ground pound |
| **Combo Phase 3** | 4 | ~160ms | Projectile spray |
| **Recovery** | 3 | 500ms | Brief vulnerable |
| **Death** | 8 | 1200ms | Dramatic demise |

#### THE BALL Anchor Role

```
When Royal Guard triggers THE BALL:

1. FORMATION CALL
   - Royal emits golden pulse (200px radius)
   - All bees within range receive command
   - Formation lines appear (#FFD700, 1.5px, 40%)

2. SPHERE FORMING
   - Royal moves to player's position
   - Other bees orbit Royal, forming sphere
   - Royal at center, radiating authority

3. CONSTRICTION
   - Royal controls shrink rate
   - Heat emanates from Royal position
   - Temperature indicator appears on Royal

Visual: Royal Guard has aura during THE BALL phases
Aura: #FF3300 → #FF0000 as temperature rises
```

#### Death Animation Detail

```
Frame 1 (0ms):     《★》   Crown flash
Frame 2 (150ms):   《!》   Shock
Frame 3 (300ms):   《╳》   Damage pattern
Frame 4 (500ms):    ◇◇◇    Crown separates
Frame 5 (700ms):    ○⚔○    Body splits
Frame 6 (900ms):    ✦✦✦    Fragment scatter
Frame 7 (1050ms):   ・・・  Particle cascade
Frame 8 (1200ms):   ★      Final golden burst

Particles: 15-20 gold fragments, 10-15 purple mist
Crown: Falls separately, lands and fades (trophy feel)
```

---

## Size Comparison Chart

```
                    THE FIVE BEE TYPES (to scale)

    Worker     Scout      Guard      Propolis     Royal

      ●          ▶        ████        ◆◆         ████████
     (●)        (▶)      ██████      ◆◆◆◆       ██████████
                           ██          ◆        ████████████
                           ██                   ████████████
                                                  ████████
                                                    ████

    12px       14px       24px        16px         32px
    (height)   (width)    (height)    (width)      (height)

    Scale:  ████ = 4px
```

### Collision Radius Overlay

```
          Worker   Scout   Guard   Propolis   Royal
Radius:     8px     6px    14px      10px     18px
Visual:     (·)     (>)    [██]       <◊>     《★》

Note: Scout has smallest hitbox (speed tradeoff)
      Guard has largest hitbox relative to sprite
```

---

## Formation Visuals

### Coordination Glow Lines

```
FORMATION LINES SPECIFICATION

Color: #FFD700 (gold)
Width: 1.5px
Opacity: 40%
Trigger: 3+ bees within 60px of each other
Animation: Subtle pulse (0.8s period)

Example (5 bees coordinating):

          ●
         /|\
        ● | ●
         \|/
          ●----●

Lines connect centroid to each participant
```

### THE BALL Formation

```
THE BALL PHASES - Visual Progression

Phase 1: FORMING (10s)
         ●   ●
       ●       ●       Bees spread around player
          ╋           Player (hornet) in center
       ●       ●       Gaps visible (escape routes)
         ●   ●

Phase 2: SPHERE (3s)
       ● ● ● ●
      ●   ╋   ●        Gap narrows to ~45 degrees
       ● ● ● ●         Green arc shows escape route

Phase 3: SILENCE (3s)
      ● ● ● ● ●        Near-complete sphere
      ●   ╋   ●        One gap remaining (green)
      ● ● ● ● ●        Sound drops to nothing

Phase 4: CONSTRICT (2s)
       ●●●●●●
       ●  ╋ ●          Sphere shrinks
       ●●●●●●          Temperature rises (#FF3300 glow)

Phase 5: DEATH
        ████
        █╳█            Complete sphere, no escape
        ████           Heat kills player
```

### Formation Glow Implementation

```typescript
interface FormationLine {
  from: Vector2;       // Bee position
  to: Vector2;         // Centroid or neighbor
  color: string;       // '#FFD700'
  opacity: number;     // 0.4
  width: number;       // 1.5
  pulse: number;       // 0-1 for animation
}

// Line appears when:
// - 3+ bees within 60px
// - Coordination state is 'coordinating' or 'ball'
// - Lines connect each bee to formation centroid

// Pulse animation:
// opacity = 0.3 + sin(time * PI / 400) * 0.1
// (oscillates between 0.3 and 0.5)
```

---

## Animation Implementation Guide

### Wing Animation (All Types)

```typescript
// Shared wing rendering for all bee types
function drawWings(ctx: CanvasRenderingContext2D,
                   x: number, y: number,
                   radius: number,
                   time: number,
                   type: BeeType) {

  const wingSpeed = {
    worker: 60,    // Hz
    scout: 90,     // Faster wings
    guard: 40,     // Slower, powerful
    propolis: 55,
    royal: 50      // Regal pace
  };

  const phase = Math.sin(time * wingSpeed[type] / 1000 * Math.PI * 2);
  const wingOffset = phase * radius * 0.3;

  // Semi-transparent wing blur
  ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
  ctx.beginPath();
  ctx.ellipse(
    x - radius * 0.8,
    y + wingOffset,
    radius * 0.6,
    radius * 0.2,
    0, 0, Math.PI * 2
  );
  ctx.ellipse(
    x + radius * 0.8,
    y - wingOffset,
    radius * 0.6,
    radius * 0.2,
    0, 0, Math.PI * 2
  );
  ctx.fill();
}
```

### Death Particle System

```typescript
interface DeathParticles {
  worker: {
    type: 'pollen_burst',
    count: 8,
    color: '#FFE066',
    spread: 45,       // degrees
    lifespan: 400,    // ms
    rotation: 3       // full rotations
  },
  scout: {
    type: 'quick_scatter',
    count: 5,
    color: '#F9B208',
    spread: 60,
    lifespan: 300,
    rotation: 2
  },
  guard: {
    type: 'armor_shatter',
    count: 12,
    color: ['#8B6914', '#4A3000'],
    spread: 90,
    lifespan: 600,
    fragments: true
  },
  propolis: {
    type: 'sticky_splat',
    count: 10,
    color: '#9B59B6',
    spread: 120,
    lifespan: 500,
    lingers: true,    // leaves pool
    poolDuration: 2000
  },
  royal: {
    type: 'royal_demise',
    count: 20,
    color: ['#6B2D5B', '#FFD700'],
    spread: 360,
    lifespan: 800,
    crownDrop: true   // special crown particle
  }
}
```

---

## Visual Hierarchy Summary

### Instant Recognition Rules

```
RULE 1: Shape determines type
  Circle    → Worker (basic)
  Triangle  → Scout (fast)
  Square    → Guard (tank)
  Diamond   → Propolis (ranged)
  Octagon   → Royal (elite)

RULE 2: Size indicates threat
  Small  → can ignore briefly
  Medium → address soon
  Large  → address NOW

RULE 3: Color carries meaning
  Gold/amber → standard bee
  Purple     → ranged threat (dodge projectiles)
  Dark brown → tank (prioritize or avoid)
  Gold crown → boss (serious threat)

RULE 4: Animation signals state
  Normal flutter → chasing
  Glow pulse    → about to attack (MOVE)
  Dim + slow    → recovering (ATTACK NOW)
  Formation line → coordinating (BREAK IT UP)
```

### Screen Readability

```
At any moment, player should be able to:

1. COUNT threats by size (big = priority)
2. IDENTIFY types by shape (no squinting)
3. PREDICT attacks by glow (telegraph visible)
4. UNDERSTAND coordination by lines (formation forming)

If any of these fail → design needs revision
```

---

## Implementation Checklist

### Phase 1: Base Sprites

- [ ] Worker: Circle body, basic wing flutter
- [ ] Scout: Triangle body, speed lines
- [ ] Guard: Square body, armor lines
- [ ] Propolis: Diamond body, drip animation
- [ ] Royal: Octagon body, crown accent

### Phase 2: State Animations

- [ ] Chase animations (all types)
- [ ] Telegraph animations (type-specific glow)
- [ ] Attack animations (type-specific motion)
- [ ] Recovery animations (dimmed, vulnerable)

### Phase 3: Death Sequences

- [ ] Worker: Spiral + pollen burst
- [ ] Scout: Quick scatter
- [ ] Guard: Armor shatter + crumple
- [ ] Propolis: Sticky explosion + pool
- [ ] Royal: Dramatic demise + crown drop

### Phase 4: Formation Visuals

- [ ] Glow lines between coordinating bees
- [ ] THE BALL phase visuals (forming → sphere → silence → constrict)
- [ ] Heat shimmer effect during constriction
- [ ] Royal Guard aura during BALL leadership

### Phase 5: Polish

- [ ] Wing blur consistency across types
- [ ] Color palette harmony verification
- [ ] Size hierarchy screen test
- [ ] Animation timing feel check

---

## Anti-Requirements (What NOT to Do)

| Avoid | Why | Instead |
|-------|-----|---------|
| Cute cartoon bees | Undermines tragedy | Dignified defenders |
| Identical silhouettes | Unreadable in swarm | Distinct shapes |
| Same size enemies | No visual hierarchy | Clear size progression |
| Generic bug colors | Forgettable | Warm amber palette |
| Minecraft blocky style | Doesn't fit tone | Smooth pixel art |
| Instant death disappear | No ceremony | Death animations |
| Silent coordination | Invisible threat | Glow lines + audio |

---

## Reference: Current Implementation

The current GameCanvas.tsx uses these shapes (confirmed):

```typescript
switch (enemy.type) {
  case 'basic':
  case 'worker':
    ctx.arc(x, y, radius, 0, Math.PI * 2);  // Circle
    break;
  case 'fast':
  case 'scout':
    drawTriangle(ctx, x, y, radius);         // Triangle
    break;
  case 'spitter':
  case 'propolis':
    drawDiamond(ctx, x, y, radius);          // Diamond
    break;
  case 'tank':
  case 'guard':
    ctx.rect(...);                           // Square
    break;
  case 'boss':
  case 'royal':
    drawOctagon(ctx, x, y, radius);          // Octagon
    break;
}
```

This spec VALIDATES and EXTENDS the current approach.

---

## Voice Anchor

> *"These are the heroes of their story. Design them with dignity."*

Every sprite decision should pass this test:

- Does this make the bees feel like DEFENDERS?
- Would I root for them if I saw them in a nature documentary?
- Does the player understand these are the PROTAGONISTS of another story?

The bees always win. The sprites should show why they deserve to.

---

*"You are the apex predator. They are the civilization. When they form THE BALL, you will understand: the colony always wins. And it should."*

**Filed**: 2025-12-28
**Author**: Creative Design Session
**Next**: Implementation in GameCanvas.tsx per Phase 1-5 checklist

