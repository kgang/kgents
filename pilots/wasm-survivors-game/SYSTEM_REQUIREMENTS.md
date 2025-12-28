# SYSTEM_REQUIREMENTS: WASM Survivors - Hornet Siege

> *"The infrastructure that makes the tragedy beautiful."*

**Version**: 1.0
**Status**: Draft
**Date**: 2025-12-28
**Parent**: `PROTO_SPEC.md`, `PROTO_SPEC_ENLIGHTENED.md`

---

## Overview

This document defines the **non-visual system requirements** for WASM Survivors: Hornet Siege. It covers infrastructure that must exist before any art, design, or style work begins.

**Scope Boundaries**:
- IN SCOPE: Asset pipelines, state modeling, adaptive systems, technical infrastructure
- OUT OF SCOPE: Visual style, color palettes, specific art assets, aesthetic decisions

---

## Table of Contents

1. [Professional Art Pipeline Requirements](#1-professional-art-pipeline-requirements)
2. [Creative/Art/Design Strategy Requirements](#2-creativeart-design-strategy-requirements)
3. [Player State Modeling](#3-player-state-modeling)
4. [Adaptive Mechanics System](#4-adaptive-mechanics-system)
5. [Technical Infrastructure](#5-technical-infrastructure)

---

## 1. Professional Art Pipeline Requirements

### 1.1 Asset Management System

The asset pipeline must support a professional art workflow where assets flow from creation tools to the game with minimal friction.

#### Asset Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CREATION TOOLS                                                             │
│  (Aseprite, Photoshop, Audacity, FL Studio, etc.)                          │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │ Export
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SOURCE ASSETS (art-repo, separate from main git)                          │
│  /source/sprites/*.aseprite                                                │
│  /source/audio/*.wav (uncompressed masters)                                │
│  /source/reference/*.psd                                                   │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │ Asset Pipeline (automated)
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PROCESSED ASSETS (tracked in manifest, committed to game repo)            │
│  /assets/sprites/*.png (optimized, power-of-2)                             │
│  /assets/audio/*.ogg (compressed, normalized)                              │
│  /assets/atlas/*.json (sprite sheet metadata)                              │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │ Build step
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RUNTIME ASSETS (in memory, loaded on demand)                              │
│  TextureAtlas, AudioBuffers, AnimationData                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Asset Registry

| Field | Type | Description |
|-------|------|-------------|
| `asset_id` | string | Unique identifier (e.g., `sprite.hornet.idle`) |
| `source_path` | string | Path in source repository |
| `processed_path` | string | Path in game repository |
| `version` | semver | Asset version for cache invalidation |
| `checksum` | sha256 | Content hash for integrity verification |
| `metadata` | object | Type-specific metadata (frame count, duration, etc.) |
| `placeholder_id` | string | Fallback asset ID until real asset arrives |

#### Pipeline Commands

```bash
# Process all assets from source to game repo
kg asset process --all

# Process single asset
kg asset process sprite.hornet.idle

# Validate asset manifest integrity
kg asset validate

# Generate placeholder report (what's missing real art)
kg asset placeholders

# Hot-reload changed assets in development
kg asset watch
```

### 1.2 Sprite Sheet Specifications

#### Sheet Format Requirements

| Property | Requirement | Rationale |
|----------|-------------|-----------|
| **Dimensions** | Power of 2 (256x256, 512x512, 1024x1024, 2048x2048) | GPU texture optimization |
| **Max Size** | 2048x2048 per sheet | WebGL compatibility floor |
| **Format** | PNG-8 (indexed) or PNG-32 (RGBA) | Lossless compression |
| **Packing** | TexturePacker JSON-Hash format | Industry standard, tool agnostic |
| **Padding** | 2px between frames | Prevent texture bleeding |
| **Trim** | Whitespace trimmed, original size stored | Reduce texture waste |

#### Animation Frame Requirements

| Entity Type | Frame Budget | Frame Rate | Required Animations |
|-------------|--------------|------------|---------------------|
| **Player (Hornet)** | 64 frames total | 12 fps | idle(4), move(8), attack(6), dash(4), hurt(3), death(8) |
| **Worker Bee** | 24 frames total | 10 fps | idle(4), move(4), attack(4), hurt(2), death(4) |
| **Soldier Bee** | 32 frames total | 12 fps | idle(4), move(4), charge(6), attack(6), hurt(2), death(6) |
| **Queen Bee** | 48 frames total | 8 fps | idle(6), summon(8), attack(8), phase_shift(12), death(12) |
| **Projectiles** | 8 frames each | 15 fps | travel(4), impact(4) |
| **Effects** | 16 frames max | 20 fps | spawn(4), hit(4), special(8) |

#### Sprite Sheet Manifest Schema

```typescript
interface SpriteSheetManifest {
  id: string;                    // e.g., "sheet.enemies.bees"
  version: string;               // semver
  texture: string;               // path to PNG
  frames: {
    [frameId: string]: {
      frame: { x: number; y: number; w: number; h: number };
      rotated: boolean;
      trimmed: boolean;
      spriteSourceSize: { x: number; y: number; w: number; h: number };
      sourceSize: { w: number; h: number };
    };
  };
  animations: {
    [animationId: string]: {
      frames: string[];          // ordered frame IDs
      frameDuration: number;     // ms per frame
      loop: boolean;
    };
  };
  meta: {
    app: string;                 // tool that generated this
    version: string;
    image: string;
    format: "RGBA8888" | "RGBA4444" | "RGB888";
    size: { w: number; h: number };
    scale: number;
  };
}
```

### 1.3 Color Palette Requirements

#### Palette Constraints

| Constraint | Value | Rationale |
|------------|-------|-----------|
| **Total Colors** | Max 64 per sheet | Indexed PNG-8 optimization |
| **Player Palette** | 8 colors (including transparent) | Readable at any zoom |
| **Enemy Palette** | 8 colors per enemy type | Visual distinction |
| **Effect Palette** | 16 colors (can blend) | Particle variety |
| **UI Palette** | 16 colors (separate sheet) | Accessibility compliance |

#### Accessibility Requirements

| Test | Requirement | Tool |
|------|-------------|------|
| **Contrast Ratio (Text)** | >= 4.5:1 (WCAG AA) | Color contrast analyzer |
| **Contrast Ratio (Interactive)** | >= 3:1 (WCAG AA) | Color contrast analyzer |
| **Color Blindness** | Distinguishable in Deuteranopia, Protanopia, Tritanopia | Coblis simulator |
| **Luminosity Variation** | >= 30% between adjacent game elements | Grayscale test |

#### Palette Registry Schema

```typescript
interface PaletteRegistry {
  palettes: {
    [paletteId: string]: {
      colors: string[];           // Hex values
      semantic: {
        [role: string]: number;   // Index into colors array
      };
    };
  };
  accessibility: {
    contrast_pairs: Array<{
      foreground: string;         // palette.role
      background: string;         // palette.role
      ratio: number;              // Measured contrast ratio
      wcag_level: "AA" | "AAA" | "FAIL";
    }>;
  };
}
```

### 1.4 Audio Asset Specifications

#### Audio Format Requirements

| Property | Source Format | Runtime Format | Rationale |
|----------|---------------|----------------|-----------|
| **SFX** | WAV 48kHz 24-bit | OGG Vorbis 44.1kHz ~128kbps | Size/quality balance |
| **Music** | WAV 48kHz 24-bit | OGG Vorbis 44.1kHz ~192kbps | Higher quality for loops |
| **Ambient** | WAV 48kHz 24-bit | OGG Vorbis 44.1kHz ~96kbps | Can be lower quality |

#### Audio Constraints

| Category | Max Duration | Max File Size | Loudness Target |
|----------|--------------|---------------|-----------------|
| **UI SFX** | 0.5s | 50KB | -18 LUFS |
| **Game SFX** | 2s | 150KB | -14 LUFS |
| **Impact SFX** | 0.3s | 30KB | -12 LUFS (peak allowed) |
| **Music Loop** | 180s | 4MB | -16 LUFS |
| **Ambient Loop** | 60s | 1MB | -24 LUFS |

#### Audio Manifest Schema

```typescript
interface AudioManifest {
  tracks: {
    [trackId: string]: {
      source: string;             // Path to source file
      runtime: string;            // Path to processed file
      category: "sfx" | "music" | "ambient" | "ui";
      duration_ms: number;
      loudness_lufs: number;
      loop: boolean;
      loop_start_ms?: number;     // For seamless loops
      loop_end_ms?: number;
      variants?: string[];        // Alternative sounds for variety
    };
  };
  banks: {
    [bankId: string]: string[];   // Track IDs in this bank (loaded together)
  };
}
```

### 1.5 Version Control for Art Assets

#### Repository Structure

```
# Main game repo (git, GitHub)
/kgents/pilots/wasm-survivors-game/
  /assets/                        # Processed assets only
    manifest.json                 # Asset registry
  /src/
  /PROTO_SPEC.md

# Art repo (git-lfs or dedicated, separate from main)
/wasm-survivors-art/
  /source/
    /sprites/*.aseprite
    /audio/*.wav
    /reference/*.psd
  /exports/                       # Human-reviewed exports
  pipeline.config.json            # Asset pipeline configuration
  CHANGELOG.md                    # Art changes log
```

#### Art Version Tracking

| Event | Action | Record |
|-------|--------|--------|
| **New Asset** | Artist exports to art-repo | Git commit + version bump |
| **Asset Update** | Artist re-exports | Git commit + version bump + changelog |
| **Pipeline Run** | Process art-repo -> game-repo | Manifest update + processed file commit |
| **Game Build** | Bundle processed assets | Build includes manifest checksum |

#### Pipeline Configuration

```json
{
  "source_repo": "git@github.com:org/wasm-survivors-art.git",
  "source_branch": "main",
  "output_dir": "../pilots/wasm-survivors-game/assets",
  "processors": {
    "sprites": {
      "input_glob": "source/sprites/**/*.aseprite",
      "output_format": "png",
      "atlas_format": "json-hash",
      "max_atlas_size": 2048,
      "padding": 2,
      "trim": true
    },
    "audio": {
      "input_glob": "source/audio/**/*.wav",
      "output_format": "ogg",
      "quality": 6,
      "normalize_lufs": -14
    }
  }
}
```

### 1.6 Hot-Reloading for Development

#### Requirements

| Requirement | Target | Notes |
|-------------|--------|-------|
| **Sprite Reload** | < 100ms | Individual sprite, no game restart |
| **Sheet Reload** | < 500ms | Full atlas, brief freeze acceptable |
| **Audio Reload** | < 200ms | Single track replacement |
| **Full Reload** | < 2s | All assets, triggered manually |

#### Hot-Reload Protocol

```typescript
interface HotReloadMessage {
  type: "asset_changed" | "asset_added" | "asset_removed";
  asset_id: string;
  asset_type: "sprite" | "animation" | "audio" | "palette";
  new_version: string;
  payload?: ArrayBuffer;          // Inline for small assets
  url?: string;                   // URL fetch for large assets
}

// Client-side handler
window.addEventListener("asset_changed", (msg: HotReloadMessage) => {
  switch (msg.asset_type) {
    case "sprite":
      assetManager.reloadSprite(msg.asset_id, msg.payload);
      break;
    case "audio":
      audioEngine.reloadTrack(msg.asset_id, msg.url);
      break;
  }
});
```

### 1.7 Placeholder System

Every asset must have a functional placeholder until real art arrives.

#### Placeholder Categories

| Category | Placeholder Type | Appearance |
|----------|------------------|------------|
| **Player** | Procedural shape | Orange hexagon with direction indicator |
| **Enemy (Worker)** | Procedural shape | Yellow circle with stripes |
| **Enemy (Soldier)** | Procedural shape | Yellow pentagon with stripes |
| **Enemy (Queen)** | Procedural shape | Large yellow hexagon, pulsing |
| **Projectiles** | Procedural shape | Small colored circles |
| **Effects** | Procedural particles | Colored squares, expanding/fading |
| **Audio** | Synthesized | Simple waveform (sine/square) |

#### Placeholder Requirements

| Requirement | Description |
|-------------|-------------|
| **Functional Equivalence** | Placeholder must have same hitbox, timing, and behavior |
| **Visual Distinction** | Each entity type must be visually distinguishable |
| **No Art Dependencies** | Placeholders generated procedurally, no external files |
| **Graceful Upgrade** | Swapping placeholder for real art requires no code changes |

#### Placeholder Registry

```typescript
interface PlaceholderRegistry {
  sprites: {
    [assetId: string]: {
      generator: "shape" | "text" | "pattern";
      params: {
        shape?: "circle" | "square" | "hexagon" | "pentagon";
        color?: string;
        size?: number;
        label?: string;           // Text overlay for debugging
        pattern?: string;         // e.g., "stripes", "dots"
      };
      hitbox: { w: number; h: number };
    };
  };
  audio: {
    [assetId: string]: {
      generator: "synth";
      params: {
        waveform: "sine" | "square" | "triangle" | "noise";
        frequency?: number;
        duration_ms: number;
        envelope: { attack: number; decay: number; sustain: number; release: number };
      };
    };
  };
}
```

---

## 2. Creative/Art/Design Strategy Requirements

### 2.1 Art Direction Document Structure

Every art direction document MUST contain the following sections:

#### Required Sections

| Section | Purpose | Format |
|---------|---------|--------|
| **Concept Statement** | One-paragraph emotional target | Prose, < 100 words |
| **Visual Metaphor** | Core visual language | Single sentence + 3-5 reference images |
| **Color Story** | Emotional progression through colors | Timeline with color samples |
| **Silhouette Test** | All entities recognizable as silhouettes | Black-on-white mockups |
| **Scale Reference** | Relative sizes of all entities | Single composite image |
| **Motion Philosophy** | How things move and feel | Prose + timing curves |
| **Contrast Map** | Visual contrast requirements | Grid: entity x background combinations |

#### Art Direction Schema

```typescript
interface ArtDirectionDocument {
  version: string;
  last_updated: string;
  author: string;

  concept: {
    statement: string;            // < 100 words
    keywords: string[];           // 5-10 emotional keywords
    anti_keywords: string[];      // What this is NOT
  };

  visual_metaphor: {
    core: string;                 // Single sentence
    references: Array<{
      url: string;
      relevance: string;          // What aspect to reference
    }>;
  };

  color_story: {
    phases: Array<{
      name: string;               // e.g., "early_game", "crisis"
      dominant_colors: string[];
      accent_colors: string[];
      mood: string;
    }>;
  };

  silhouettes: {
    [entityId: string]: {
      recognizable_at: number;    // Minimum pixel size for recognition
      distinctive_feature: string;
    };
  };

  scale: {
    reference_unit: number;       // Pixels per "unit"
    entities: {
      [entityId: string]: {
        width_units: number;
        height_units: number;
      };
    };
  };

  motion: {
    philosophy: string;
    timing_curves: {
      [curveId: string]: {
        description: string;
        bezier: [number, number, number, number];
      };
    };
  };
}
```

### 2.2 Style Guide Enforcement

#### Automated Style Checks

| Check | Tool | Threshold | Enforcement |
|-------|------|-----------|-------------|
| **Color Count** | Palette analyzer | <= spec per sheet | CI blocks merge |
| **Frame Count** | Asset validator | <= spec per entity | CI blocks merge |
| **File Size** | Size checker | <= spec per type | CI warns, does not block |
| **Naming Convention** | Regex validator | Must match pattern | CI blocks merge |
| **Contrast Ratio** | Accessibility analyzer | >= WCAG AA | CI warns, review required |

#### Style Validation Pipeline

```bash
# Run all style checks
kg style validate

# Output format
{
  "passed": false,
  "checks": [
    {
      "name": "color_count",
      "passed": true,
      "message": "All sheets within color budget"
    },
    {
      "name": "contrast_ratio",
      "passed": false,
      "message": "UI button text fails WCAG AA (ratio: 3.2:1, required: 4.5:1)",
      "violations": [
        { "element": "ui.button.primary", "ratio": 3.2, "required": 4.5 }
      ]
    }
  ]
}
```

### 2.3 Design Token System

Design tokens are the atomic units of visual design, defined as code.

#### Token Categories

| Category | Examples | Update Frequency |
|----------|----------|------------------|
| **Colors** | Primary, secondary, semantic colors | Rare (major updates) |
| **Spacing** | Grid units, margins, padding | Rare |
| **Timing** | Animation durations, easing curves | Moderate |
| **Typography** | Font sizes, line heights, weights | Rare |
| **Shadows** | Drop shadows, glows, outlines | Moderate |
| **Particles** | Spawn rates, lifetimes, velocities | Frequent (tuning) |

#### Token Schema

```typescript
// Design tokens as code - single source of truth
const DESIGN_TOKENS = {
  color: {
    // Semantic colors
    player: {
      body: "#FF6B35",           // Hornet orange
      accent: "#2E1503",         // Dark brown details
      glow: "#FFD23F",           // Attack effects
    },
    enemy: {
      bee_worker: "#F7DC6F",     // Worker yellow
      bee_soldier: "#F4D03F",    // Soldier gold
      bee_queen: "#D4AC0D",      // Queen amber
    },
    feedback: {
      damage_player: "#FF0000",
      damage_enemy: "#FFFFFF",
      heal: "#00FF00",
      xp: "#00BFFF",
    },
    ui: {
      health_full: "#00FF00",
      health_mid: "#FFFF00",
      health_low: "#FF0000",
      text_primary: "#FFFFFF",
      text_secondary: "#AAAAAA",
    },
  },

  timing: {
    // Animation durations (ms)
    instant: 0,
    fast: 100,
    normal: 200,
    slow: 400,
    dramatic: 800,

    // Easing curves (cubic-bezier)
    ease_out_expo: [0.19, 1, 0.22, 1],
    ease_in_out: [0.42, 0, 0.58, 1],
    bounce: [0.68, -0.55, 0.265, 1.55],

    // Game-specific timing
    hit_freeze: 50,              // Freeze frames on hit
    death_slow_mo: 500,          // Time slow on death
    level_up_pause: 300,         // Pause for level up
  },

  spacing: {
    grid_unit: 8,                // Base unit in pixels
    entity_padding: 2,           // Hitbox padding
    ui_margin: 16,
    ui_padding: 8,
  },

  particles: {
    hit_sparks: {
      count: { min: 5, max: 12 },
      lifetime: { min: 200, max: 400 },
      velocity: { min: 100, max: 300 },
      size: { min: 2, max: 6 },
    },
    death_burst: {
      count: { min: 20, max: 40 },
      lifetime: { min: 400, max: 800 },
      velocity: { min: 50, max: 200 },
      size: { min: 4, max: 12 },
    },
    xp_sparkle: {
      count: { min: 3, max: 8 },
      lifetime: { min: 300, max: 600 },
      velocity: { min: 20, max: 80 },
      size: { min: 2, max: 4 },
    },
  },
} as const;

// Type-safe access
type DesignTokens = typeof DESIGN_TOKENS;
```

#### Token Update Protocol

1. All token changes require PR review
2. Token changes auto-generate visual diff report
3. Token changes trigger full visual regression test
4. Tokens are versioned with the codebase

### 2.4 Theme Coherence Validation

Automated checks to ensure visual theme consistency.

#### Coherence Checks

| Check | Description | Automated |
|-------|-------------|-----------|
| **Palette Conformance** | All colors exist in defined palettes | Yes |
| **Timing Conformance** | All durations use token values | Yes |
| **Silhouette Distinction** | Entities distinguishable at 32px | Yes (image analysis) |
| **Contrast Minimum** | All text/interactive elements meet WCAG | Yes |
| **Animation Consistency** | Similar actions use similar timing | Partially (heuristic) |
| **Scale Consistency** | Entity sizes match scale reference | Yes |

#### Coherence Report Schema

```typescript
interface CoherenceReport {
  overall_score: number;          // 0-1
  checks: Array<{
    name: string;
    score: number;
    weight: number;
    violations: Array<{
      location: string;           // File or asset ID
      expected: string;
      actual: string;
      severity: "error" | "warning" | "info";
    }>;
  }>;
  recommendations: string[];
}
```

### 2.5 Asset Naming Conventions

#### Naming Pattern

```
{category}.{entity}.{variant}.{state}.{frame}

Examples:
  sprite.hornet.default.idle.01
  sprite.hornet.default.attack.03
  sprite.bee_worker.elite.death.05
  audio.sfx.hit.flesh.01
  audio.music.wave_5_to_8
```

#### Naming Rules

| Rule | Pattern | Example |
|------|---------|---------|
| **Lowercase only** | `[a-z0-9_]` | `sprite.hornet.idle` |
| **Underscore for spaces** | `_` | `bee_worker`, not `bee-worker` |
| **Category prefix** | `sprite\|audio\|ui\|effect` | `sprite.hornet` |
| **Frame numbers** | Two digits, zero-padded | `idle.01`, `idle.02` |
| **Variants** | `default\|elite\|mutant\|boss` | `sprite.bee.elite.attack` |

#### Naming Validation

```bash
# Validate all asset names
kg asset validate-names

# Output
{
  "valid": false,
  "errors": [
    {
      "asset": "Hornet_Idle_1.png",
      "expected_pattern": "sprite.hornet.default.idle.01",
      "violations": ["uppercase", "missing_category", "underscore_in_wrong_place"]
    }
  ]
}
```

### 2.6 Localization-Ready Text Rendering

All text must be renderable in any language from day one.

#### Text Requirements

| Requirement | Description |
|-------------|-------------|
| **No hardcoded strings** | All visible text comes from localization files |
| **Unicode support** | Full UTF-8 support, including CJK and RTL |
| **Dynamic sizing** | Text containers must accommodate 150% expansion |
| **Icon fallbacks** | Critical UI has icon backup for translation gaps |
| **String interpolation** | Support variables: `"Wave {wave_number}"` |

#### Localization Schema

```typescript
interface LocalizationSchema {
  locale: string;                 // e.g., "en-US", "ja-JP"
  strings: {
    // Namespaced by context
    ui: {
      wave_counter: string;       // "Wave {wave}"
      health_label: string;
      xp_label: string;
      retry_button: string;
    };
    gameplay: {
      upgrade_names: {
        [upgradeId: string]: string;
      };
      upgrade_descriptions: {
        [upgradeId: string]: string;
      };
      enemy_names: {
        [enemyId: string]: string;
      };
    };
    death_messages: {
      generic: string[];          // Random selection
      by_enemy: {
        [enemyId: string]: string[];
      };
    };
    crystal: {
      claim_templates: string[];
      pivot_descriptions: {
        [pivotType: string]: string;
      };
    };
  };
  formatting: {
    number_format: string;        // e.g., "1,234.56" vs "1.234,56"
    date_format: string;
    time_format: string;
  };
}
```

#### Text Rendering Pipeline

```
1. Code requests string by key: getText("ui.wave_counter", { wave: 5 })
2. Localization system looks up current locale
3. String template retrieved: "Wave {wave}"
4. Variables interpolated: "Wave 5"
5. Text rendered with appropriate font/direction
```

---

## 3. Player State Modeling

### 3.1 State Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  META-STATE (Player Identity)                                              │
│  Persists forever | Privacy-sensitive | Exportable                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  MACRO-STATE (Cross-Run)                                                   │
│  Persists across runs | Informs adaptation | Skill tracking                │
├─────────────────────────────────────────────────────────────────────────────┤
│  MICRO-STATE (Within-Run)                                                  │
│  Resets each run | High-frequency | Replay-capable                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Micro-State (Within a Run)

High-frequency state captured during gameplay. Enables replays, ghost systems, and within-run adaptation.

#### Position History

```typescript
interface PositionHistory {
  samples: Array<{
    tick: number;                 // Game tick (60/sec)
    position: { x: number; y: number };
    velocity: { x: number; y: number };
    facing: number;               // Radians
  }>;
  sampling_rate: number;          // Samples per second (default: 10)
  compression: "none" | "delta" | "bezier";
}

// Compression strategies:
// - none: Full data (for short runs, debugging)
// - delta: Store deltas from previous (90% size reduction typical)
// - bezier: Fit curves to paths (95% reduction, lossy but smooth replays)
```

#### Input History

```typescript
interface InputHistory {
  events: Array<{
    tick: number;
    type: "key_down" | "key_up" | "mouse_move" | "mouse_click";
    key?: string;                 // For keyboard
    position?: { x: number; y: number };  // For mouse
    button?: number;              // For mouse click
  }>;

  // Derived patterns (computed post-run)
  patterns: {
    dominant_direction: "up" | "down" | "left" | "right" | "mixed";
    input_frequency: number;      // Inputs per second
    direction_change_rate: number; // Direction changes per second
    dodge_direction_bias: {
      left: number;               // 0-1 probability
      right: number;
      up: number;
      down: number;
    };
  };
}
```

#### Damage Timeline

```typescript
interface DamageTimeline {
  events: Array<{
    tick: number;
    damage: number;
    source: {
      type: "enemy" | "projectile" | "environment" | "colossal";
      entity_id: string;
      attack_type: string;
    };
    player_state: {
      health_before: number;
      health_after: number;
      position: { x: number; y: number };
      was_dodging: boolean;
      recent_input: string;       // Last input before damage
    };
  }>;

  // Derived analytics
  analytics: {
    total_damage: number;
    damage_by_source: { [source: string]: number };
    damage_by_attack: { [attack: string]: number };
    average_time_between_hits: number;
    longest_no_damage_streak: number;
  };
}
```

#### Upgrade Selection History

```typescript
interface UpgradeHistory {
  selections: Array<{
    wave: number;
    tick: number;
    offered: string[];            // Upgrade IDs offered
    selected: string;             // Upgrade ID chosen
    selection_time_ms: number;    // Time to decide
    build_state: {
      upgrades_held: string[];
      principle_weights: PrincipleWeights;
    };
  }>;

  // Derived patterns
  patterns: {
    average_selection_time: number;
    selection_time_by_wave: number[];
    preference_vector: { [upgradeId: string]: number };  // Selection rate when offered
    never_selected: string[];     // Upgrades always passed
    always_selected: string[];    // Upgrades always taken when offered
  };
}
```

#### Near-Death Events (Clutch Moments)

```typescript
interface ClutchMoment {
  tick: number;
  health_low_point: number;       // Lowest health reached
  threat_count: number;           // Enemies nearby
  escape_method: "dodge" | "kill" | "heal" | "upgrade" | "luck";
  position_history: Array<{ x: number; y: number }>;  // Last 2 seconds
  duration_in_danger: number;     // Ticks below 20% health

  // Computed significance
  significance: number;           // 0-1, how close to death
  spectacle_worthy: boolean;      // Should this trigger slow-mo?
}

interface ClutchHistory {
  moments: ClutchMoment[];

  // Aggregates
  total_clutch_moments: number;
  average_clutch_health: number;
  clutch_survival_rate: number;   // % of near-deaths survived
}
```

#### Combo Chains

```typescript
interface ComboChain {
  start_tick: number;
  end_tick: number;
  kills: Array<{
    tick: number;
    enemy_type: string;
    position: { x: number; y: number };
  }>;
  max_multiplier: number;
  total_xp_gained: number;
  chain_breaker?: {
    tick: number;
    reason: "timeout" | "damage_taken" | "wave_end";
  };
}

interface ComboHistory {
  chains: ComboChain[];

  // Statistics
  longest_chain: number;
  highest_multiplier: number;
  average_chain_length: number;
  total_combo_xp: number;
}
```

#### Movement Patterns

```typescript
interface MovementPattern {
  // Classification
  style: "aggressive" | "defensive" | "kiting" | "stationary" | "erratic";
  confidence: number;             // 0-1

  // Metrics
  average_distance_to_enemies: number;
  time_moving: number;            // % of run spent moving
  direction_entropy: number;      // Higher = more random movement
  heat_map: number[][];           // Position frequency grid
  danger_zone_avoidance: number;  // How well player avoids high-threat areas

  // Behavioral indicators
  approaches_enemies: boolean;    // Moves toward threats
  circles_enemies: boolean;       // Kiting behavior
  retreats_when_damaged: boolean; // Defensive response
  camps_corners: boolean;         // Positional preference
}
```

### 3.3 Macro-State (Across Runs)

Persists across runs to track player improvement and inform adaptation.

#### Play Style Fingerprint

```typescript
interface PlayStyleFingerprint {
  player_id: string;              // Anonymous identifier
  runs_analyzed: number;
  last_updated: string;           // ISO timestamp

  // Core dimensions (0-1 each)
  dimensions: {
    aggression: number;           // 0=kiting, 1=facetanking
    risk_tolerance: number;       // 0=conservative, 1=greedy
    speed: number;                // 0=methodical, 1=rushing
    focus: number;                // 0=single-target, 1=AoE
    experimentation: number;      // 0=same builds, 1=variety
    precision: number;            // 0=spray, 1=targeted
  };

  // Derived classification
  archetype: string;              // e.g., "Aggressive Orbiter", "Careful Kiter"
  archetype_confidence: number;

  // Evolution tracking
  history: Array<{
    run_id: string;
    dimensions_snapshot: typeof dimensions;
    archetype: string;
  }>;
}
```

#### Skill Progression

```typescript
interface SkillProgression {
  // Improvement metrics (comparing run N to run 1)
  metrics: {
    survival_time: {
      baseline: number;           // First 5 runs average
      current: number;            // Last 5 runs average
      improvement_rate: number;   // % improvement
    };
    wave_reached: {
      baseline: number;
      current: number;
      improvement_rate: number;
    };
    damage_taken_per_wave: {
      baseline: number;
      current: number;
      improvement_rate: number;   // Negative is good
    };
    dodge_success_rate: {
      baseline: number;
      current: number;
      improvement_rate: number;
    };
    decision_speed: {
      baseline: number;           // Upgrade selection time
      current: number;
      improvement_rate: number;   // Negative is good
    };
  };

  // Skill curve (for visualization)
  curve: Array<{
    run_number: number;
    composite_skill: number;      // 0-1 normalized
  }>;

  // Learning events
  breakthroughs: Array<{
    run_number: number;
    skill: string;                // What improved
    before: number;
    after: number;
    likely_cause: string;         // e.g., "First pierce build"
  }>;
}
```

#### Preferred Upgrades

```typescript
interface UpgradePreferences {
  // Selection statistics
  stats: {
    [upgradeId: string]: {
      times_offered: number;
      times_selected: number;
      selection_rate: number;
      average_selection_wave: number;  // When in run is it typically taken
      synergies_discovered: string[];  // Other upgrades often taken with this
    };
  };

  // Inferred preferences
  preferences: {
    favorite_upgrades: string[];  // Top 3 by selection rate
    avoided_upgrades: string[];   // Bottom 3 by selection rate
    build_tendencies: string[];   // e.g., ["pierce_builds", "orbital_builds"]
  };

  // Recommendation data
  recommendations: {
    underexplored: string[];      // Upgrades rarely tried
    likely_to_enjoy: string[];    // Based on preference similarity
  };
}
```

#### Weakness Patterns

```typescript
interface WeaknessPatterns {
  // Death analysis
  death_causes: {
    [causeType: string]: {
      count: number;
      percentage: number;
      average_wave: number;       // When does this kill them
      improving: boolean;         // Is this happening less?
    };
  };

  // Specific weaknesses
  weaknesses: Array<{
    type: "enemy" | "attack" | "situation";
    identifier: string;           // e.g., "soldier_bee.charge"
    severity: number;             // 0-1
    evidence: string;             // Human-readable explanation
    suggested_counter: string;    // What would help
  }>;

  // Blind spots
  blind_spots: {
    direction: "up" | "down" | "left" | "right";  // Where attacks hit most
    timing: "early" | "mid" | "late";              // When in run
    state: string;                                  // e.g., "during_kiting"
  };
}
```

#### Session Patterns

```typescript
interface SessionPatterns {
  // Play schedule
  schedule: {
    typical_play_times: string[]; // Hour of day
    typical_days: string[];       // Days of week
    session_length_avg: number;   // Minutes
    runs_per_session_avg: number;
  };

  // Engagement metrics
  engagement: {
    sessions_this_week: number;
    sessions_this_month: number;
    longest_session: number;      // Minutes
    longest_gap: number;          // Days between sessions
    retry_rate: number;           // % immediate retry after death
  };

  // Fatigue detection
  fatigue_indicators: {
    performance_degradation: boolean;  // Getting worse during session
    session_abandonment_point: number; // Average run where they quit
    decision_time_increasing: boolean;
  };
}
```

#### Mastery Indicators Per Enemy Type

```typescript
interface EnemyMastery {
  enemies: {
    [enemyId: string]: {
      encounters: number;
      kills: number;
      deaths_caused_by: number;
      damage_taken_from: number;

      // Mastery score (0-1)
      mastery: number;

      // Specific skills
      dodge_rate: number;         // % of attacks dodged
      priority_awareness: number; // How quickly targeted
      pattern_recognition: number; // Consistency of response

      // Learning curve
      mastery_history: Array<{
        run_number: number;
        mastery_score: number;
      }>;
    };
  };

  // Aggregate
  overall_enemy_mastery: number;
  most_mastered: string;
  needs_practice: string;
}
```

### 3.4 Meta-State (Player Identity)

Permanent player data that represents their journey.

#### Amber Memories (Crystal Collection)

```typescript
interface AmberMemories {
  // The collection
  crystals: Array<{
    id: string;
    run_number: number;
    timestamp: string;

    // Run summary
    summary: {
      wave_reached: number;
      survival_time: number;
      death_cause: string;
      build_archetype: string;
      notable_moments: string[];
    };

    // Inheritance data
    inheritance: {
      parent_crystal?: string;    // If inherited from another crystal
      children: string[];         // Crystals that inherited from this
      inheritable_trait: string;  // The upgrade/trait this can pass on
    };

    // Social data
    sharing: {
      shared: boolean;
      share_code?: string;
      times_inherited: number;    // By other players
    };
  }>;

  // Statistics
  stats: {
    total_crystals: number;
    oldest_crystal: string;       // Timestamp
    most_inherited: string;       // Crystal ID
    lineage_depth: number;        // Longest inheritance chain
  };
}
```

#### Siege History

```typescript
interface SiegeHistory {
  // Overall statistics
  total_runs: number;
  total_play_time: number;        // Seconds
  total_bees_defeated: number;
  total_colossals_faced: number;
  total_colossals_defeated: number;

  // Best performances
  records: {
    highest_wave: {
      value: number;
      run_id: string;
      timestamp: string;
    };
    longest_survival: {
      value: number;              // Seconds
      run_id: string;
      timestamp: string;
    };
    most_kills: {
      value: number;
      run_id: string;
      timestamp: string;
    };
    highest_combo: {
      value: number;
      run_id: string;
      timestamp: string;
    };
  };

  // Compressed run history
  runs: Array<{
    id: string;
    timestamp: string;
    wave: number;
    duration: number;
    death_cause: string;
    crystal_id?: string;
  }>;
}
```

#### Milestones

```typescript
interface Milestones {
  achievements: Array<{
    id: string;
    name: string;
    description: string;
    unlocked: boolean;
    unlock_timestamp?: string;
    unlock_run?: string;

    // Achievement data
    progress: number;             // 0-1
    target?: number;              // For progress-based
    secret: boolean;              // Hidden until unlocked
  }>;

  // Examples:
  // { id: "first_blood", name: "First Blood", description: "Defeat your first bee" }
  // { id: "colossal_slayer", name: "Colossal Slayer", description: "Defeat THE TIDE" }
  // { id: "perfect_wave", name: "Untouchable", description: "Complete a wave without damage" }
  // { id: "inheritance_chain", name: "Dynasty", description: "Create a 5-generation crystal lineage" }
}
```

#### Unlockables

```typescript
interface Unlockables {
  items: Array<{
    id: string;
    type: "cosmetic" | "starting_bonus" | "mode" | "feature";
    name: string;
    description: string;

    // Unlock conditions
    unlocked: boolean;
    unlock_condition: {
      type: "milestone" | "runs" | "kills" | "special";
      requirement: string;
      progress: number;           // 0-1
    };

    // If unlocked
    equipped?: boolean;           // For cosmetics/bonuses
  }>;

  // Examples:
  // { id: "golden_stinger", type: "cosmetic", name: "Golden Stinger" }
  // { id: "hard_mode", type: "mode", name: "Nightmare Hive" }
  // { id: "ghost_replay", type: "feature", name: "Ghost Replays" }
}
```

---

## 4. Adaptive Mechanics System

### 4.1 Adaptation Philosophy

> *"The game adapts to you, and you know it. No hidden manipulation."*

**Core Principles**:
1. **Transparent**: Player can always see WHY the game adapted
2. **Fair**: Adaptation helps struggling players, challenges skilled ones
3. **Witnessed**: Every adaptation decision is marked and reviewable
4. **Bounded**: Adaptation has hard limits to prevent exploitation

### 4.2 Difficulty Adaptation

#### Spawn Rate Adjustment

```typescript
interface SpawnAdaptation {
  // Player skill estimate (from macro-state)
  player_skill: number;           // 0-1

  // Base spawn rates (from wave definition)
  base_rates: {
    [enemyType: string]: number;  // Enemies per second
  };

  // Adaptation formula
  adapted_rates: {
    [enemyType: string]: number;
  };

  // Formula:
  // adapted_rate = base_rate * skill_multiplier * performance_multiplier
  // skill_multiplier: 0.7 (low skill) to 1.3 (high skill)
  // performance_multiplier: 0.8 (struggling this run) to 1.2 (dominating this run)
}

function computeSpawnMultiplier(
  playerSkill: number,
  currentRunPerformance: number,
): number {
  // Skill affects base difficulty
  const skillFactor = 0.7 + (playerSkill * 0.6);  // 0.7 to 1.3

  // Current run performance rubber-bands
  const performanceFactor = 0.8 + (currentRunPerformance * 0.4);  // 0.8 to 1.2

  // Combined, clamped to reasonable bounds
  return Math.max(0.5, Math.min(1.5, skillFactor * performanceFactor));
}
```

#### Colossal Timing Adjustment

```typescript
interface ColossalTiming {
  // Base timing from spec
  base_metamorphosis_threshold: 20;  // seconds

  // Adaptation
  adapted_threshold: number;

  // Formula:
  // Skilled players: threshold reduced (they see Colossals sooner)
  // Struggling players: threshold extended (more time to prevent)

  // Bounds: 15s minimum, 30s maximum
}

function computeMetamorphosisThreshold(
  playerSkill: number,
  colossalMastery: number,       // Player's skill vs Colossals specifically
): number {
  const base = 20;

  // High skill = earlier Colossals (15s at max skill)
  // Low skill = later Colossals (30s at min skill)
  const skillAdjustment = (0.5 - playerSkill) * 10;  // -5 to +5 seconds

  // If player is bad at Colossals specifically, give more time
  const masteryAdjustment = (0.5 - colossalMastery) * 5;  // -2.5 to +2.5 seconds

  return Math.max(15, Math.min(30, base + skillAdjustment + masteryAdjustment));
}
```

#### Rubber Banding Rules

```typescript
interface RubberBandingRules {
  // Trigger conditions for "help"
  help_triggers: {
    health_below: 0.2;            // Help when below 20% health
    no_damage_dealt_for: 10;      // Seconds without killing
    deaths_this_session: 5;       // After 5 deaths, ease up
  };

  // Help effects
  help_effects: {
    spawn_rate_reduction: 0.3;    // 30% fewer spawns
    enemy_speed_reduction: 0.1;   // 10% slower enemies
    xp_drop_increase: 0.2;        // 20% more XP
    // Note: NO damage reduction (preserves skill expression)
  };

  // Trigger conditions for "challenge"
  challenge_triggers: {
    health_above: 0.8;            // Challenge when above 80% health
    kill_streak: 20;              // After 20 kills without damage
    wave_dominance: true;         // Completed last 3 waves at full health
  };

  // Challenge effects
  challenge_effects: {
    spawn_rate_increase: 0.2;     // 20% more spawns
    elite_chance_increase: 0.1;   // 10% more elites
    // Note: NO damage increase (fair challenge, not punishment)
  };
}
```

#### Rising Challenge Rules

```typescript
interface RisingChallenge {
  // For skilled players who "break" normal difficulty

  triggers: {
    consecutive_wave_10_plus: 3;  // 3 runs reaching wave 10+
    average_health_at_death: 0.5; // Dying with lots of health (not being pressured)
    colossal_defeat_rate: 0.8;    // Defeating 80%+ of Colossals
  };

  effects: {
    // Permanent difficulty increase for this player
    base_difficulty_tier: number; // 0, 1, 2, 3 (each adds challenge)

    tier_effects: {
      0: { spawn_multiplier: 1.0, elite_chance: 0.1 },
      1: { spawn_multiplier: 1.1, elite_chance: 0.15 },
      2: { spawn_multiplier: 1.2, elite_chance: 0.2 },
      3: { spawn_multiplier: 1.3, elite_chance: 0.25 },
    };
  };

  // Decay: if player struggles, tier decreases
  decay: {
    trigger: "3 consecutive deaths before wave 5";
    effect: "tier decreases by 1";
  };
}
```

### 4.3 Content Adaptation

#### Enemy Type Weighting

```typescript
interface EnemyWeighting {
  // Based on player weakness patterns

  // If player struggles with enemy type, spawn MORE of that type
  // (Counter-intuitive but forces learning)
  weakness_weight_boost: 1.3;     // 30% more of weakness types

  // If player has mastered enemy type, spawn fewer (it's boring now)
  mastery_weight_reduction: 0.7; // 30% fewer of mastered types

  // Implementation
  computeEnemyWeights(
    baseWeights: { [enemyId: string]: number },
    playerWeaknesses: WeaknessPatterns,
    playerMastery: EnemyMastery,
  ): { [enemyId: string]: number };
}
```

#### Upgrade Offering Weighting

```typescript
interface UpgradeOffering {
  // Upgrades offered are weighted by:
  // 1. Build coherence (synergies with current build)
  // 2. Weakness coverage (addresses player's weak points)
  // 3. Exploration bonus (upgrades rarely tried)

  weights: {
    synergy: 0.4;                 // 40% weight to build synergy
    weakness_coverage: 0.3;      // 30% to addressing weaknesses
    exploration: 0.2;            // 20% to variety
    random: 0.1;                 // 10% pure random
  };

  // Never offered:
  blacklist: {
    upgrades_taken_this_run: true;
    upgrades_player_never_picks: false;  // Still offer for exploration
  };

  // Guarantee:
  guarantee: {
    at_least_one_synergy: true;  // Always one "obvious" good pick
    at_least_one_new: true;      // Always one player hasn't tried much
  };
}
```

#### Arena Layout Adaptation

```typescript
interface ArenaAdaptation {
  // Arena hazards/features placed based on player tendencies

  // If player camps corners: add corner hazards
  // If player kites in circles: add obstacles in circle path
  // If player retreats too much: add back wall pressure

  layout_rules: Array<{
    trigger: PlayerTendency;
    effect: LayoutModification;
  }>;

  examples: [
    {
      trigger: "camps_corners",
      effect: "spawn_corner_hazards_wave_5_plus",
    },
    {
      trigger: "always_moves_right",
      effect: "spawn_obstacles_on_right_side",
    },
    {
      trigger: "retreats_when_damaged",
      effect: "add_pursuit_enemies_behind",
    },
  ];
}
```

### 4.4 Narrative Adaptation

#### History-Aware Text

```typescript
interface NarrativeAdaptation {
  // Text references player history

  death_messages: {
    // First death to enemy type
    first_death: "The {enemy_name} claims its first victim.";

    // Repeated deaths to same enemy
    repeated_death: [
      "The {enemy_name} again. You'll learn.",           // 2nd time
      "The {enemy_name} knows your weakness.",           // 3rd time
      "The {enemy_name} has your pattern memorized.",    // 4th+ time
    ];

    // Death to enemy you've mastered
    mastered_enemy_death: "Even masters fall. The {enemy_name} found an opening.";

    // Death by Colossal
    colossal_death: {
      first: "THE {colossal_name} emerges victorious. Now you know its power.";
      repeat: "THE {colossal_name} again. Its patterns are learnable.";
      after_defeating: "THE {colossal_name} claims revenge.";
    };
  };

  milestone_messages: {
    // Dynamic based on player history
    wave_record: "Wave {wave}. Your new personal best.";
    near_record: "Wave {wave}. Your record is {record}. One more push.";
    crushed_record: "Wave {wave}. You've surpassed yourself by {amount} waves.";
  };
}
```

#### Evolving Death Messages

```typescript
interface DeathMessageEvolution {
  // Messages that change based on death count to same cause

  evolution: {
    [causeId: string]: {
      deaths_1: string;           // First death
      deaths_2_3: string;         // Learning
      deaths_4_6: string;         // Struggling
      deaths_7_plus: string;      // Respect/acknowledgment
      after_mastery: string;      // If they eventually master it
    };
  };

  example: {
    "soldier_bee.charge": {
      deaths_1: "The soldier's charge catches you off-guard.",
      deaths_2_3: "The charge again. Watch for the wind-up.",
      deaths_4_6: "You know the charge is coming. Why aren't you moving?",
      deaths_7_plus: "The charge is your nemesis. But nemeses can be conquered.",
      after_mastery: "The charge that once terrified you. Look how far you've come.",
    },
  };
}
```

#### Milestone Celebrations

```typescript
interface MilestoneCelebration {
  // Celebrations that feel earned based on player journey

  celebrations: Array<{
    milestone_id: string;

    // Generic message
    generic: string;

    // Journey-aware messages
    journey_aware: {
      quick_achiever: string;     // Achieved faster than average
      slow_burn: string;          // Took many runs
      after_struggle: string;     // Achieved after many related failures
      unexpected: string;         // Achieved via unusual path
    };

    // Requirements for each variant
    variants: {
      quick_achiever: { runs_required_max: number };
      slow_burn: { runs_required_min: number };
      after_struggle: { related_failures_min: number };
      unexpected: { unusual_build: boolean };
    };
  }>;
}
```

### 4.5 Witness Integration

Every adaptation decision is marked and reviewable.

#### Adaptation Mark Schema

```typescript
interface AdaptationMark {
  timestamp: string;
  run_id: string;
  tick: number;

  adaptation_type:
    | "difficulty_spawn_rate"
    | "difficulty_colossal_timing"
    | "rubber_band_help"
    | "rubber_band_challenge"
    | "content_enemy_weight"
    | "content_upgrade_weight"
    | "arena_layout"
    | "narrative_message";

  // What triggered this adaptation
  trigger: {
    condition: string;            // Human-readable
    metrics: { [key: string]: number };
  };

  // What changed
  effect: {
    description: string;          // Human-readable
    before: { [key: string]: number };
    after: { [key: string]: number };
  };

  // Player can query: "Why did that happen?"
  explanation: string;
}
```

#### Transparency UI (Post-Run)

```typescript
interface AdaptationReview {
  // Available in crystal/post-run review

  run_adaptations: {
    total_adaptations: number;
    by_type: {
      [type: string]: number;
    };

    significant_moments: Array<{
      tick: number;
      description: string;        // "Spawn rate reduced by 20% (health critical)"
      player_state: string;       // "15% health, surrounded"
    }>;
  };

  // Player settings
  transparency_level: "full" | "summary" | "hidden";

  // If full: show all adaptations in timeline
  // If summary: show aggregate stats
  // If hidden: no adaptation info shown
}
```

---

## 5. Technical Infrastructure

### 5.1 Event System

All game events flow through a central, typed event bus.

#### Event Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  GAME SYSTEMS                                                               │
│  (Input, Physics, Spawn, Combat, Upgrade, etc.)                            │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ emit
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  EVENT BUS                                                                  │
│  - Type validation                                                          │
│  - Timestamp injection                                                      │
│  - Serialization                                                            │
│  - Replay buffer                                                            │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ broadcast
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌─────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  GAME SYSTEMS   │  │  WITNESS LAYER      │  │  REPLAY RECORDER    │
│  (subscribe)    │  │  (mark emission)    │  │  (serialization)    │
└─────────────────┘  └─────────────────────┘  └─────────────────────┘
```

#### Event Type Definitions

```typescript
// All game events extend base
interface GameEvent {
  type: string;
  tick: number;
  timestamp: number;              // Performance.now()
}

// Event categories
interface InputEvent extends GameEvent {
  type: "input.key_down" | "input.key_up" | "input.mouse_move";
  payload: {
    key?: string;
    position?: { x: number; y: number };
  };
}

interface SpawnEvent extends GameEvent {
  type: "spawn.enemy" | "spawn.projectile" | "spawn.effect";
  payload: {
    entity_id: string;
    entity_type: string;
    position: { x: number; y: number };
    properties: Record<string, unknown>;
  };
}

interface CombatEvent extends GameEvent {
  type: "combat.damage" | "combat.death" | "combat.heal";
  payload: {
    source_id: string;
    target_id: string;
    amount: number;
    damage_type?: string;
  };
}

interface UpgradeEvent extends GameEvent {
  type: "upgrade.offered" | "upgrade.selected";
  payload: {
    options?: string[];
    selected?: string;
    selection_time_ms?: number;
  };
}

interface WaveEvent extends GameEvent {
  type: "wave.start" | "wave.end" | "wave.colossal_spawn";
  payload: {
    wave_number: number;
    colossal_type?: string;
  };
}

// Union type for all events
type AnyGameEvent = InputEvent | SpawnEvent | CombatEvent | UpgradeEvent | WaveEvent;
```

#### Event Validation

```typescript
interface EventValidator {
  // Schema validation per event type
  schemas: Map<string, JSONSchema>;

  validate(event: AnyGameEvent): ValidationResult;
}

interface ValidationResult {
  valid: boolean;
  errors?: Array<{
    path: string;
    message: string;
  }>;
}
```

#### Event Replay

```typescript
interface EventReplaySystem {
  // Record events for replay
  record(event: AnyGameEvent): void;

  // Export events as serializable format
  export(): SerializedEventLog;

  // Import and replay events
  import(log: SerializedEventLog): void;
  replay(options: ReplayOptions): AsyncIterator<AnyGameEvent>;
}

interface SerializedEventLog {
  version: string;
  run_id: string;
  start_timestamp: string;
  events: AnyGameEvent[];

  // Metadata for reconstruction
  initial_state: GameState;
  random_seed: number;
}

interface ReplayOptions {
  speed: number;                  // 1.0 = normal, 2.0 = 2x, etc.
  start_tick?: number;
  end_tick?: number;
  filter?: (event: AnyGameEvent) => boolean;
}
```

### 5.2 State Persistence

#### Storage Tiers

| Tier | Data Type | Storage | Sync |
|------|-----------|---------|------|
| **Ephemeral** | Current run state | Memory only | Never |
| **Session** | Micro-state | IndexedDB | On run end |
| **Local** | Macro-state, preferences | IndexedDB | On change |
| **Cloud** | Meta-state, crystals | Server | On demand |

#### Persistence Schema

```typescript
interface PersistenceManager {
  // Ephemeral (memory)
  ephemeral: {
    currentRun: RunState;
    inputBuffer: InputEvent[];
  };

  // Session (IndexedDB, cleared on game close)
  session: {
    recentRuns: RunTrace[];       // Last 5 runs
    currentSession: SessionData;
  };

  // Local (IndexedDB, persists)
  local: {
    playerProfile: PlayStyleFingerprint;
    skillProgression: SkillProgression;
    preferences: PlayerPreferences;
    cachedCrystals: AmberMemories;
  };

  // Cloud (server-synced)
  cloud: {
    amberMemories: AmberMemories;
    siegeHistory: SiegeHistory;
    milestones: Milestones;
    unlockables: Unlockables;
  };
}
```

#### Conflict Resolution

```typescript
interface ConflictResolution {
  // When local and cloud diverge

  strategies: {
    // Crystals: merge (union of both)
    crystals: "merge";

    // Milestones: take most progress
    milestones: "max_progress";

    // Statistics: take highest values
    statistics: "max_value";

    // Preferences: take most recent
    preferences: "latest_timestamp";
  };

  // On conflict, show user summary
  reportConflict(
    local: PersistedData,
    cloud: PersistedData,
    resolution: PersistedData,
  ): ConflictReport;
}
```

#### Privacy Controls

```typescript
interface PrivacyControls {
  // Player-controlled sharing
  sharing: {
    crystals_shareable: boolean;  // Can others inherit my crystals?
    anonymous_analytics: boolean; // Contribute to aggregate data?
    public_profile: boolean;      // Show my siege history publicly?
  };

  // Data export/delete (GDPR compliance)
  dataRights: {
    exportAll(): Promise<FullDataExport>;
    deleteAll(): Promise<void>;
    deleteSpecific(categories: string[]): Promise<void>;
  };

  // What's never stored
  neverStored: [
    "real_name",
    "email",
    "ip_address",
    "precise_geolocation",
    "device_identifiers",
  ];
}
```

### 5.3 Analytics (Privacy-First)

#### What IS Measured (Aggregate Only)

```typescript
interface AggregateAnalytics {
  // Population-level metrics only
  // No individual player tracking

  gameplay: {
    average_wave_reached: number;
    average_run_duration: number;
    most_popular_upgrades: string[];
    most_lethal_enemies: string[];
    colossal_defeat_rate: number;
  };

  retention: {
    day_1_retention: number;      // % returning next day
    week_1_retention: number;
    median_sessions_per_week: number;
  };

  balance: {
    upgrade_selection_distribution: { [upgradeId: string]: number };
    death_cause_distribution: { [causeId: string]: number };
    build_archetype_distribution: { [archetype: string]: number };
  };
}
```

#### What is NEVER Measured

```typescript
interface AnalyticsBlacklist {
  // These are NEVER collected, logged, or transmitted

  never_collect: [
    "individual_player_behavior",   // No per-player tracking
    "session_timestamps",           // No "when did they play"
    "device_fingerprints",          // No device identification
    "network_information",          // No IP, no location
    "input_patterns",               // No keystroke analysis
    "system_information",           // No OS/browser fingerprinting
  ];

  // Enforcement
  audit_logging: true;              // All analytics calls logged
  quarterly_review: true;           // Manual review of what's collected
}
```

#### Opt-Out System

```typescript
interface AnalyticsOptOut {
  // Granular opt-out
  options: {
    aggregate_gameplay: boolean;   // Contribute to gameplay stats
    aggregate_balance: boolean;    // Contribute to balance stats
    aggregate_retention: boolean;  // Contribute to retention stats
    all: boolean;                  // Master switch
  };

  // What happens on opt-out
  onOptOut: {
    immediate_effect: true;        // No more data collected
    historical_delete: false;      // Past aggregate data cannot be removed (no individual link)
    notification: "Your data is no longer collected. Past aggregate contributions cannot be individually removed as they were never individually stored.";
  };
}
```

### 5.4 Performance Budgets

#### Frame Time Budgets

| System | Budget (ms) | Priority | Notes |
|--------|-------------|----------|-------|
| **Input Processing** | 1.0 | Critical | Must be instant |
| **Physics/Collision** | 3.0 | Critical | Spatial hash helps |
| **AI/Behavior** | 2.0 | High | Can skip frames if needed |
| **Rendering** | 8.0 | High | Main bottleneck |
| **Particles** | 2.0 | Medium | Can reduce count |
| **Audio** | 0.5 | Medium | Runs on separate thread |
| **Witness/Events** | 0.5 | Low | Non-blocking |
| **Analytics** | 0.1 | Lowest | Batched, off-frame |
| **TOTAL** | 16.6 | - | 60 FPS target |

#### Memory Budgets

| Category | Budget (MB) | Notes |
|----------|-------------|-------|
| **Textures** | 64 | Compressed, atlased |
| **Audio** | 32 | Streaming for music |
| **Game State** | 16 | Entity pool limits |
| **Event Buffer** | 8 | Rolling window |
| **UI** | 8 | DOM budget |
| **WASM Heap** | 64 | If using WASM |
| **TOTAL** | 192 | Target for low-end devices |

#### Asset Loading Budgets

| Phase | Time Budget | Strategy |
|-------|-------------|----------|
| **Initial Load** | < 3s | Essential assets only |
| **First Play** | < 1s | Preloaded during menu |
| **Wave Transition** | < 100ms | Preload next wave assets |
| **Hot Reload** | < 500ms | Single asset swap |

#### Network Budgets (If Online Features)

| Operation | Size Budget | Frequency |
|-----------|-------------|-----------|
| **Crystal Sync** | < 10KB per crystal | On run end |
| **Leaderboard Pull** | < 50KB | On menu open |
| **Weekly Seed** | < 5KB | Daily |
| **Analytics Batch** | < 1KB | Every 10 minutes max |

#### Performance Monitoring

```typescript
interface PerformanceMonitor {
  // Real-time budgets
  budgets: Map<string, { current: number; budget: number; violations: number }>;

  // Frame time tracking
  frameTime: {
    current: number;
    average: number;
    p95: number;
    violations: number;           // Frames over budget
  };

  // Memory tracking
  memory: {
    used: number;
    budget: number;
    trend: "stable" | "growing" | "shrinking";
  };

  // Alerts
  onBudgetViolation(system: string, callback: (data: ViolationData) => void): void;

  // Reports
  generateReport(): PerformanceReport;
}
```

---

## Appendix A: Data Flow Diagrams

### A.1 Player State Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  GAME LOOP (60 FPS)                                                         │
│                                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │  Input  │───▶│ Physics │───▶│ Combat  │───▶│ Render  │                  │
│  └────┬────┘    └────┬────┘    └────┬────┘    └─────────┘                  │
│       │              │              │                                       │
│       ▼              ▼              ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐               │
│  │  MICRO-STATE ACCUMULATOR                                │               │
│  │  (position history, input history, damage timeline)     │               │
│  └────────────────────────────┬────────────────────────────┘               │
│                               │                                             │
└───────────────────────────────┼─────────────────────────────────────────────┘
                                │ On run end
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  MACRO-STATE PROCESSOR                                                      │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ Style Fingerprint│  │ Skill Progression│  │ Weakness Patterns│          │
│  │ Update           │  │ Update           │  │ Update           │          │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘          │
│           │                     │                     │                     │
│           └─────────────────────┼─────────────────────┘                     │
│                                 │                                           │
│                                 ▼                                           │
│                    ┌───────────────────────┐                               │
│                    │ ADAPTATION SYSTEM     │                               │
│                    │ (next run parameters) │                               │
│                    └───────────────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                │ On milestone/unlock
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  META-STATE (Persisted)                                                     │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Amber        │  │ Siege        │  │ Milestones   │  │ Unlockables  │   │
│  │ Memories     │  │ History      │  │              │  │              │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### A.2 Asset Pipeline Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Artist's Tool  │────▶│  Source Repo    │────▶│  Asset Pipeline │
│  (Aseprite)     │     │  (git-lfs)      │     │  (kg asset)     │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌────────────────────────────────┼────────────────┐
                        ▼                                ▼                ▼
               ┌────────────────┐             ┌────────────────┐  ┌──────────────┐
               │ Sprite Packer  │             │ Audio Processor│  │ Palette      │
               │ (TexturePacker)│             │ (ffmpeg)       │  │ Validator    │
               └───────┬────────┘             └───────┬────────┘  └──────┬───────┘
                       │                              │                   │
                       ▼                              ▼                   ▼
               ┌────────────────┐             ┌────────────────┐  ┌──────────────┐
               │ /assets/atlas  │             │ /assets/audio  │  │ Validation   │
               │ *.png, *.json  │             │ *.ogg          │  │ Report       │
               └───────┬────────┘             └───────┬────────┘  └──────────────┘
                       │                              │
                       └──────────────┬───────────────┘
                                      ▼
                             ┌────────────────┐
                             │ Asset Manifest │
                             │ manifest.json  │
                             └───────┬────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ Dev Server   │ │ Production   │ │ Hot Reload   │
            │ (vite)       │ │ Build        │ │ (WebSocket)  │
            └──────────────┘ └──────────────┘ └──────────────┘
```

---

## Appendix B: Validation Checklist

Before any art production begins, verify:

- [ ] Asset pipeline is functional (`kg asset process --all` succeeds)
- [ ] Placeholder system renders all game entities
- [ ] Hot-reload works for sprites and audio
- [ ] Design tokens are defined and enforced
- [ ] Style validation passes (`kg style validate`)
- [ ] Event system captures all game events
- [ ] Replay system can record and playback a run
- [ ] Persistence works across browser sessions
- [ ] Performance budgets are met on target hardware
- [ ] Privacy controls are implemented and tested

---

*"The infrastructure that makes the tragedy beautiful. The systems that witness every fall."*
