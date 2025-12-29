# HORNET SIEGE: Art Style Guide

## 1. STYLE STATEMENT

**Ukiyo-e meets arcade brutalism.** Hard edges, flat color planes, deliberate asymmetry. Every sprite reads like a woodblock print stamped onto a CRT monitor—precise linework, no anti-aliasing, shadows that carve form like ink strokes. This is the aesthetic of a nature documentary filmed in 1987 and converted to 16-bit.

We reject the Disney bee. We reject the chibi hornet. These are insects rendered with the gravity of predator and prey—anatomically respectful, emotionally resonant, uncomfortably beautiful.

---

## 2. PIXEL ART SPECS

| Element | Resolution | Colors | Notes |
|---------|------------|--------|-------|
| **Player (Hornet)** | 32x32 | 6 max | Largest sprite, commands attention |
| **Worker Bee** | 16x16 | 4 max | Swarm density requires simplicity |
| **Scout Bee** | 16x16 | 4 max | Elongated silhouette |
| **Guard Bee** | 20x20 | 5 max | Bulkier frame, shield-like abdomen |
| **Propolis Bee** | 16x16 | 4 max | Trailing particles use separate sprites |
| **Royal Guard** | 24x24 | 6 max | Only exception: touches of Royal Purple |
| **Projectiles** | 8x8 | 2-3 | Stinger, propolis glob, pheromone burst |
| **Effects** | Variable | 3 max | Particle systems stay restrained |

### Animation Frame Counts

| Action | Frames | Loop |
|--------|--------|------|
| Idle | 4 | Yes |
| Walk/Fly | 6 | Yes |
| Attack windup | 3 | No |
| Attack strike | 2 | No |
| Hit reaction | 2 | No |
| Death | 5 | No (hold last) |
| Special ability | 4-6 | No |

**Frame rate**: 12 FPS for gameplay, 8 FPS for idle (slightly dreamy quality).

---

## 3. PLAYER PALETTE: The Hornet

The hornet is WARM but DARK. It absorbs light; it doesn't reflect cute.

| Role | Hex | Name | Usage |
|------|-----|------|-------|
| **Primary** | `#CC5500` | Burnt Amber | Thorax, head, main body mass |
| **Secondary** | `#1A1A1A` | Venom Black | Stripes, legs, antennae |
| **Highlight** | `#FF8C00` | Strike Orange | Upper edges, attack frames |
| **Shadow** | `#662200` | Dried Blood | Underside, depth carving |
| **Eyes** | `#FFE066` | Pollen Gold | 2x2 pixels max, unblinking |
| **Mandible Accent** | `#FF3300` | Threat Red | Only visible during attack |

**Key insight**: The hornet should feel like it's emerging from shadow. Body mass is predominantly dark with orange breaking through—not the reverse.

---

## 4. ENEMY PALETTES

### Worker Bee (Basic)
The expendable. Sympathetic but not precious.

| Role | Hex | Name |
|------|-----|------|
| Primary | `#D4920A` | Worker Amber |
| Secondary | `#1F1A14` | Chitin Dark |
| Highlight | `#FFE066` | Pollen Gold |
| Shadow | `#6B4E14` | Hive Shadow |

### Scout Bee (Fast)
Leaner, paler—looks like it's been flying too long.

| Role | Hex | Name |
|------|-----|------|
| Primary | `#E5B84A` | Faded Honey |
| Secondary | `#2A2A2A` | Trail Black |
| Highlight | `#FFF3C4` | Nectar Glow |
| Shadow | `#8B6914` | Beeswax Brown |

### Guard Bee (Tanky)
Darker, denser. Abdomen reads as armor plating.

| Role | Hex | Name |
|------|-----|------|
| Primary | `#B87A0A` | Hardened Amber |
| Secondary | `#141414` | Fortress Black |
| Highlight | `#F4A300` | Honey Amber |
| Shadow | `#3D2914` | Shadow Comb |
| Accent | `#5C4A1F` | Shield Brown (abdomen edge) |

### Propolis Bee (Ranged)
Sticky, resinous. Slightly green undertone suggests chemical payload.

| Role | Hex | Name |
|------|-----|------|
| Primary | `#A08020` | Resin Gold |
| Secondary | `#2A1F14` | Propolis Dark |
| Highlight | `#C9A830` | Sap Gleam |
| Shadow | `#3D2E14` | Tar Shadow |
| Projectile | `#5C4A20` | Glob Brown |

### Royal Guard (Elite)
The ONLY bee type with purple. This is sacred hierarchy, not decoration.

| Role | Hex | Name |
|------|-----|------|
| Primary | `#C98A0A` | Sovereign Amber |
| Secondary | `#1A1A1A` | Venom Black |
| Highlight | `#FFD700` | Warning Yellow |
| Shadow | `#4A1A3A` | Royal Shadow |
| **Elite Accent** | `#6B2D5B` | Royal Purple (EDGE ONLY) |

**Royal Purple rule**: 2-4 pixels maximum. Wing tips. Eye highlight. Abdomen stripe terminus. Never fill areas.

---

## 5. VISUAL HIERARCHY

### What POPS (Foreground)
1. **Player hornet** — Largest, warmest orange, always reads first
2. **Attack telegraphs** — Brief flash frames in Warning Yellow (#FFD700)
3. **Damage numbers/effects** — Pure white (#FFFFFF) or Strike Orange
4. **Elite enemies** — Royal Purple accents pull eye

### What RECEDES (Background)
1. **Honeycomb environment** — Beeswax Brown (#8B6914) and Shadow Comb (#3D2914)
2. **Worker bee swarms** — Desaturated, smaller, pattern becomes texture
3. **Ambient particles** — Pollen Gold at 50% density, drifting

### Danger vs Safety Signaling

| Signal | Visual Treatment |
|--------|------------------|
| **DANGER** | Red undertones, Warning Yellow flashes, increased contrast |
| **SAFETY** | Nectar Glow (#FFF3C4) wash, softer shadows, slower particle drift |
| **IMMINENT DEATH** | Screen edges vignette with Propolis Dark, heartbeat flash |
| **PLAYER POWER** | Strike Orange intensifies, mandibles visible, larger silhouette |
| **OVERWHELM** | Bee density increases, individual sprites lose definition into mass |

### The Colony Wins (Visual Progression)

As the inevitable approaches:
- Background honeycomb becomes more geometric, more ordered
- Bee swarm loses individual identity, becomes texture/pattern
- Player hornet's highlights dim, shadows deepen
- Final moments: hornet sprite SHRINKS relative to swarm density

---

## 6. ANTI-PATTERNS (The Forbidden)

### 1. NO CARTOON EYES
Insects have compound eyes. Two dots is lazy. One highlight pixel on a dark mass, or nothing. Googly eyes kill tension instantly.

### 2. NO SOFT GRADIENTS
This is pixel art, not airbrushed mobile game slop. Dithering is acceptable. Smooth gradients are not. Every color transition should be DELIBERATE.

### 3. NO SYMMETRY ADDICTION
Real insects are asymmetric in motion. Idle frames can be balanced; action frames should have weight shift, lean, torque. A perfectly symmetrical attack sprite looks like clipart.

### 4. NO PURPLE DEMOCRACY
Royal Purple is EARNED. If every enemy has purple accents "because it looks cool," we've destroyed the hierarchy. Guard it jealously. When Royal Guards appear, purple should feel like a violation.

### 5. NO OUTLINE UNIFORMITY
Black outlines everywhere flattens depth. Use selective outlining:
- Hard Propolis Dark (#2A1F14) outline on player (separation from chaos)
- NO outline on worker bees (they're meant to blur into swarm)
- Partial outline on elites (bottom and shadow-side only)

### 6. NO CUTE DEATH ANIMATIONS
Bees don't go "poof" with sparkles. They drop. They crumple. The hornet doesn't explode—it's overwhelmed, subsumed, absorbed into the mass. Death is weight, not whimsy.

---

## IMPLEMENTATION NOTES

### Sprite Sheet Organization
```
/assets/sprites/
  /hornet/
    idle-4f.png
    fly-6f.png
    attack-5f.png
    hit-2f.png
    death-5f.png
  /bees/
    worker/
    scout/
    guard/
    propolis/
    royal-guard/
  /effects/
    hit-spark-3f.png
    propolis-glob-2f.png
    pheromone-burst-4f.png
```

### Color Verification
Before implementing any sprite, verify against palette:
1. Sample all colors
2. Match to hex codes above
3. Count total colors (must not exceed spec)
4. Check that Royal Purple appears ONLY on Royal Guard

### The Mirror Test
Every sprite should pass: *"Does this feel like a nature documentary tragedy, or a mobile game cash grab?"*

If the answer is the latter, redraw.

---

*"Daring, bold, creative, opinionated but not gaudy."*

**Filed**: 2025-12-28
**Status**: Design Specification v1.0
