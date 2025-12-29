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
| **Palette** | Aggressive orange/black (#CC5500) | Warm amber/gold (#D4920A) |
| **Silhouette** | Angular, predatory | Rounded, organic |
| **Animation** | Sharp, violent | Coordinated, purposeful |
| **Death** | Dignified collapse | Heroic sacrifice |

**The Tragedy**: The player is the monster. The bees are the heroes. Every sprite should remind the player of this truth.

---

## Color Palette (Distinct from Hornet)

### Primary Bee Colors

| Type | Primary | Secondary | Accent | Hex Values |
|------|---------|-----------|--------|------------|
| **Worker** | Worker Amber | Pollen Gold | Warm White | `#D4920A`, `#FFE066`, `#FFF8E7` |
| **Scout** | Faded Honey | Speed Cyan | Alert Yellow | `#E5B84A`, `#00D4FF`, `#FFD700` |
| **Guard** | Hardened Amber | Dark Umber | Armor Gold | `#B87A0A`, `#4A3000`, `#C4A000` |
| **Propolis** | Resin Gold | Deep Violet | Resin Sheen | `#A08020`, `#6B2D5B`, `#D4A5D4` |
| **Royal** | Royal Purple | Gold Leaf | Crown White | `#6B2D5B`, `#FFD700`, `#FFFFFF` |

### Formation/Coordination Colors

| Element | Color | Use |
|---------|-------|-----|
| Formation Glow Lines | `#FFD700` @ 40% | Connecting coordinated bees |
| Alarm Cascade | `#FF4444` -> `#FFD700` | Spreading pheromone alert |
| THE BALL Forming | `#FF6B6B` -> `#FF3300` | Heat buildup indicator |
| Pheromone Trail | `#D4920A` @ 30% | Scout marking paths |

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

    ****    <- Worker Amber head (#D4920A)
   ******   <- Body with subtle stripes
   **  **   <- Pollen Gold underbelly (#FFE066)
   ******
    ****    <- Stinger hint (1px darker)
     ..     <- Tiny legs (optional detail)

Key Features:
- Round, plump body
- Subtle golden glow
- 2 wing positions (up/down) for flutter
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

      v        <- Alert antenna (animated)
    ****       <- Streamlined head
   *****>      <- Elongated body, pointed rear
    ****       <- Speed lines (during chase)

Key Features:
- Triangular/wedge shape
- Antennae visibly "alert" (wiggling)
- Speed trails when moving fast
- Lighter coloring (faster = lighter visual weight)
```

#### Color Application

```
Primary: #E5B84A (faded honey)
Accent:  #00D4FF (cyan speed streaks, 40% opacity)
Alert:   #FFD700 (antenna glow when alarming)

Speed Lines: 3 trailing lines, #E5B84A @ 30%, 0.3s linger
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

     ********     <- Heavy head, armored
    **********    <- Broad thorax
   ************   <- Armored abdomen (2px darker plates)
   *|******|*     <- Armor lines (vertical)
   *|******|*
    **********
     ********     <- Reinforced rear

Key Features:
- Square/rectangular silhouette (NOT round)
- Visible "armor plating" lines
- Darker, earthier coloring
- Slower, more deliberate animations
```

#### Color Application

```
Primary:  #B87A0A (hardened amber)
Armor:    #4A3000 (dark umber plate lines)
Highlight: #C4A000 (gold trim on armor)

Armor Lines: 2px wide, #4A3000, vertical striping
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

       ^         <- Pointed top
      ***        <- Diamond body shape
     **#**       <- Dark purple core (projectile organ)
     *****
      ***        <- Visible resin drip
       v         <- Pointed bottom

Key Features:
- Diamond/rhombus shape (unique!)
- Visible "projectile organ" (darker center)
- Propolis drip animation (2px amber drop)
- Purple-tinted (different from gold Workers)
```

#### Color Application

```
Primary:  #A08020 (resin gold)
Core:     #6B2D5B (deep violet, projectile organ)
Drip:     #D4A5D4 (resin sheen, animated)
Projectile: #8E44AD with #D4920A sticky trail
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

       ********        <- Crown accent (#FFD700)
      **********
     ************      <- Royal purple body (#6B2D5B)
    **************     <- Gold trim edges
    ****xxxx****       <- Pattern (cross-hatch)
    **************
     ************
      **********
        ****           <- Powerful stinger

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

---

## Size Comparison Chart

```
                THE FIVE BEE TYPES (to scale)

Worker     Scout      Guard      Propolis     Royal

  *          >        ****        **         ********
 (*)        (>)      ******      ****       **********
                       **          *        ************
                       **                   ************
                                              ********
                                                ****

12px       14px       24px        16px         32px
(height)   (width)    (height)    (width)      (height)

Scale:  **** = 4px
```

---

## Visual Hierarchy Summary

### Instant Recognition Rules

```
RULE 1: Shape determines type
  Circle    -> Worker (basic)
  Triangle  -> Scout (fast)
  Square    -> Guard (tank)
  Diamond   -> Propolis (ranged)
  Octagon   -> Royal (elite)

RULE 2: Size indicates threat
  Small  -> can ignore briefly
  Medium -> address soon
  Large  -> address NOW

RULE 3: Color carries meaning
  Gold/amber -> standard bee
  Purple     -> ranged threat (dodge projectiles)
  Dark brown -> tank (prioritize or avoid)
  Gold crown -> boss (serious threat)

RULE 4: Animation signals state
  Normal flutter -> chasing
  Glow pulse    -> about to attack (MOVE)
  Dim + slow    -> recovering (ATTACK NOW)
  Formation line -> coordinating (BREAK IT UP)
```

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
