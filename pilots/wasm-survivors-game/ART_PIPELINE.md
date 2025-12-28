# WASM Survivors: Hornet Siege - Art Pipeline Specification

Version: 1.0 | Status: Draft | Last Updated: 2025-12-28

> *"The visual language must serve the game feel. Every pixel is feedback."*

## Overview

This document specifies the complete art asset pipeline for WASM Survivors: Hornet Siege. The game is a browser-based survivors-like where you play as a hornet raiding a bee colony. Assets must be optimized for 60fps Canvas/WebGL rendering via WASM.

**Current State**: The game uses procedurally generated graphics (colored geometric shapes) and Web Audio API synthesis. This pipeline enables a transition to authored sprites while preserving hot-swap capability during development.

---

## 1. Asset Organization

```
assets/
├── sprites/
│   ├── player/                    # Hornet player character
│   │   ├── hornet_idle.png
│   │   ├── hornet_move.png
│   │   ├── hornet_attack.png
│   │   ├── hornet_damage.png
│   │   ├── hornet_death.png
│   │   └── hornet_dash.png
│   ├── enemies/
│   │   ├── bee_worker/            # Basic enemy (Shambler)
│   │   ├── bee_scout/             # Fast enemy (Rusher)
│   │   ├── bee_soldier/           # Tank enemy
│   │   ├── bee_spitter/           # Ranged enemy (Spitter)
│   │   └── bee_queen/             # Boss enemy
│   ├── colossals/                 # Metamorphosis Colossal forms
│   │   ├── the_tide/              # Shambler Colossal
│   │   ├── the_rampage/           # Rusher Colossal
│   │   ├── the_artillery/         # Spitter Colossal
│   │   ├── the_fortress/          # Tank Colossal
│   │   └── the_legion/            # Swarm Colossal
│   ├── effects/
│   │   ├── particles/             # Death bursts, trails, impacts
│   │   ├── metamorphosis/         # Pulsing, threads, combination FX
│   │   ├── projectiles/           # Player bullets, enemy projectiles
│   │   └── environmental/         # Honey drips, pollen clouds
│   ├── ui/
│   │   ├── hud/                   # Health bars, XP bars, combo indicators
│   │   ├── menus/                 # Start screen, pause, game over
│   │   ├── upgrade_icons/         # 24x24 upgrade selection icons
│   │   └── indicators/            # Warnings, telegraphs, tutorials
│   └── environment/
│       ├── honeycomb/             # Tiling background elements
│       ├── hive/                  # Arena boundaries, entrance
│       └── props/                 # Wax cells, honey pools, etc.
├── atlases/                       # Packed sprite sheets (build output)
│   ├── player_atlas.png
│   ├── enemies_atlas.png
│   ├── effects_atlas.png
│   └── ui_atlas.png
├── audio/
│   ├── sfx/
│   │   ├── player/                # Hornet sounds
│   │   ├── enemies/               # Bee sounds per type
│   │   ├── combat/                # Hits, kills, damage
│   │   ├── ui/                    # Level up, menu clicks
│   │   └── environment/           # Ambient hive sounds
│   ├── music/
│   │   ├── menu_theme.ogg
│   │   ├── gameplay_loop.ogg
│   │   ├── boss_theme.ogg
│   │   └── colossal_theme.ogg
│   └── sprites/                   # Audio sprite bundles (build output)
│       └── sfx_bundle.json        # Howler.js sprite definition
├── fonts/
│   ├── game_ui.woff2              # Primary UI font
│   ├── game_ui.ttf                # Fallback
│   └── damage_numbers.woff2       # Bold font for combat text
└── data/
    ├── animations.json            # Animation frame definitions
    ├── atlas_map.json             # Sprite sheet coordinate map
    ├── audio_sprites.json         # Audio sprite timing data
    └── color_palettes.json        # Palette definitions
```

### Directory Conventions

| Directory | Contents | Build Output |
|-----------|----------|--------------|
| `sprites/` | Source PNG files, organized by category | Packed into `atlases/` |
| `atlases/` | Generated sprite sheets | Deployed directly |
| `audio/sfx/` | Individual sound files | Bundled into `audio/sprites/` |
| `audio/music/` | Full music tracks | Deployed directly (lazy-loaded) |
| `data/` | JSON configuration | Deployed directly |

---

## 2. Sprite Sheet Specifications

### 2.1 Size Requirements

All sprite dimensions MUST be powers of 2 for GPU texture optimization:

| Asset Type | Base Size | Animation Frames | Atlas Max |
|------------|-----------|------------------|-----------|
| Player (Hornet) | 64x64 | 4-8 per state | 512x512 |
| Basic Enemies | 32x32 | 4 per state | 512x512 |
| Elite Enemies | 48x48 | 4-6 per state | 512x512 |
| Colossals | 128x128 | 6-8 per state | 1024x1024 |
| Particles | 16x16 | 4-8 frames | 256x256 |
| UI Icons | 24x24 | 1 (static) | 256x256 |
| Upgrade Icons | 48x48 | 1 (static) | 256x256 |
| Background Tiles | 64x64 | 1 (static) | 512x512 |

### 2.2 Animation Frame Rates

Target: 60fps game loop. Animation frame rates are independent of game loop.

| Animation Type | Frame Rate | Reasoning |
|----------------|------------|-----------|
| Idle | 4 fps | Subtle breathing, low urgency |
| Move | 12 fps | Smooth locomotion |
| Attack | 16 fps | Snappy, responsive feedback |
| Damage | 20 fps | Quick flash, high visibility |
| Death | 12 fps | Satisfying, not rushed |
| Telegraph | 8 fps | Readable warning |
| Metamorphosis | 6 fps | Dramatic, building dread |

### 2.3 Naming Conventions

```
{entity}_{state}_{frame}.png

Examples:
  hornet_idle_01.png
  hornet_idle_02.png
  bee_worker_move_01.png
  particle_death_burst_01.png
  ui_upgrade_pierce.png
```

**Rules**:
- Lowercase only, underscores for separation
- Two-digit frame numbers, zero-padded (01, 02, ... 12)
- State names match code constants: `idle`, `move`, `attack`, `damage`, `death`, `dash`, `telegraph`
- No spaces, hyphens, or special characters

### 2.4 Export Format

- **Format**: PNG-24 with alpha transparency
- **Color Depth**: 32-bit RGBA
- **Compression**: Maximum PNG compression (pngquant recommended)
- **Background**: Transparent, not colored key
- **Anti-aliasing**: Disabled for pixel art, enabled for HD sprites

### 2.5 Atlas Packing Rules

1. **Padding**: 2px between sprites (prevents texture bleeding)
2. **Power of 2**: Final atlas dimensions must be powers of 2
3. **Max Size**: 2048x2048 per atlas (mobile GPU compatibility)
4. **Grouping**: Group by render layer (background, entities, effects, UI)
5. **Animation Strips**: Keep animation frames horizontally adjacent

**Build Tool**: Use TexturePacker, free-tex-packer, or custom script with `spritesheet-js`.

---

## 3. Placeholder System

Development proceeds with geometric placeholders until art is ready.

### 3.1 Geometric Placeholders

The current game renders entities as colored geometric shapes. This system is preserved as the fallback:

| Entity | Shape | Color | Current Code |
|--------|-------|-------|--------------|
| Player (Hornet) | Circle | `#00D4FF` (Electric Blue) | `COLORS.player` |
| Basic Enemy | Circle | `#FF3366` (Corrupted Red) | `COLORS.enemy` |
| Fast Enemy | Triangle | `#FF3366` | Custom draw |
| Spitter | Diamond | `#FF3366` | Custom draw |
| Tank | Square | `#FF3366` | Custom draw |
| Boss | Octagon | `#FF3366` | Custom draw |
| XP Orb | Circle | `#FFD700` (Golden) | `COLORS.xp` |

### 3.2 Placeholder Asset Files

When creating placeholder image files (for testing asset loading):

```
placeholder_{entity}_{state}.png

Examples:
  placeholder_hornet_idle.png
  placeholder_bee_worker_move.png
```

Placeholder files contain:
- Solid color matching the geometric fallback
- Simple shape outline (circle, triangle, etc.)
- "PH" text overlay for visibility
- Same dimensions as final sprite

### 3.3 Hot-Swap System

The asset loader supports runtime switching between placeholders and real art:

```typescript
interface SpriteLoader {
  // Attempts to load real sprite, falls back to placeholder
  load(entity: string, state: string): Promise<Sprite | Placeholder>;

  // Force placeholder mode (dev testing)
  setPlaceholderMode(enabled: boolean): void;

  // Check if using placeholder for entity
  isPlaceholder(entity: string): boolean;
}
```

**Implementation**:

```typescript
// In rendering code
const sprite = await spriteLoader.load('hornet', 'idle');

if (sprite.isPlaceholder) {
  // Draw geometric fallback
  drawGeometricHornet(ctx, position, radius);
} else {
  // Draw sprite
  ctx.drawImage(sprite.image, position.x, position.y);
}
```

### 3.4 Placeholder Indicator (Dev Mode)

When `DEV_MODE=true`:

- Placeholder entities have a magenta border (2px)
- Console logs which assets are placeholders at startup
- HUD shows "Placeholder Mode: X/Y assets loaded"

```typescript
if (DEV_MODE && sprite.isPlaceholder) {
  ctx.strokeStyle = '#FF00FF';
  ctx.lineWidth = 2;
  ctx.strokeRect(x, y, width, height);
}
```

---

## 4. Color Palette Management

### 4.1 Master Palette File

**Location**: `assets/data/color_palettes.json`

```json
{
  "version": "1.0",
  "palettes": {
    "default": {
      "name": "Hive Invasion",
      "colors": {
        "player_primary": "#00D4FF",
        "player_secondary": "#0099CC",
        "player_glow": "#66E5FF",

        "enemy_primary": "#FF3366",
        "enemy_secondary": "#CC1144",
        "enemy_glow": "#FF6688",

        "bee_worker": "#FFAA00",
        "bee_scout": "#FF8800",
        "bee_soldier": "#996600",
        "bee_spitter": "#FFCC00",
        "bee_queen": "#FFD700",

        "xp_primary": "#FFD700",
        "xp_glow": "#FFEE88",

        "health_full": "#00FF88",
        "health_mid": "#FFAA00",
        "health_low": "#FF3366",

        "crisis": "#FF8800",
        "warning": "#FFCC00",

        "metamorphosis_pulse_start": "#FF6B00",
        "metamorphosis_pulse_end": "#FF0000",
        "metamorphosis_threads": "#FF00FF",
        "colossal": "#880000",

        "background_calm": "#1a1a2e",
        "background_crisis": "#281a2e",
        "grid": "#252540"
      }
    },
    "colorblind_deuteranopia": {
      "name": "High Contrast (Deuteranopia)",
      "colors": {
        "player_primary": "#00BFFF",
        "enemy_primary": "#FF6600",
        "health_full": "#0066FF",
        "health_low": "#FF6600"
      }
    },
    "colorblind_protanopia": {
      "name": "High Contrast (Protanopia)",
      "colors": {
        "player_primary": "#00CCFF",
        "enemy_primary": "#FFCC00",
        "health_full": "#00CCFF",
        "health_low": "#FFCC00"
      }
    }
  }
}
```

### 4.2 Palette Enforcement

**Sprites**: Artists must use only colors from the active palette. Validation script runs during build:

```bash
# Validate sprite colors against palette
npm run validate:palette -- assets/sprites/
```

**Runtime**: The `PaletteManager` loads palette on startup and provides color constants:

```typescript
const palette = PaletteManager.load('default');
const playerColor = palette.get('player_primary');
```

### 4.3 Accessibility Requirements

The game MUST support at least three color modes:

| Mode | Target | Key Changes |
|------|--------|-------------|
| Default | Full color vision | Standard palette |
| Deuteranopia | Red-green colorblind | Blue vs Orange distinction |
| Protanopia | Red colorblind | Cyan vs Yellow distinction |

**Implementation**:
- Player and enemies must be distinguishable in all modes
- Health states (full/mid/low) must use distinct hues, not just saturation
- Metamorphosis effects use brightness + animation, not just hue shift

### 4.4 Theme Switching

Future-proofing for seasonal themes or unlockable palettes:

```typescript
// Settings menu
setPalette('halloween');  // Orange/purple/black
setPalette('neon');       // Cyberpunk colors
setPalette('classic');    // Original palette
```

Sprites remain unchanged; only runtime colors shift.

---

## 5. Audio Specifications

### 5.1 Format Requirements

| Format | Use Case | Fallback |
|--------|----------|----------|
| OGG Vorbis | Primary (all browsers) | MP3 |
| MP3 | Safari fallback | - |
| WAV | Source files only | Never deployed |

**Reasoning**: OGG has better compression and quality. MP3 for Safari which historically had OGG issues.

### 5.2 Sample Rates

| Type | Sample Rate | Bit Depth | Channels |
|------|-------------|-----------|----------|
| SFX | 44.1 kHz | 16-bit | Mono |
| Music | 44.1 kHz | 16-bit | Stereo |
| Voice (if any) | 22.05 kHz | 16-bit | Mono |

### 5.3 Volume Normalization

All audio files MUST be normalized to:
- **Peak**: -1 dBFS (prevent clipping)
- **LUFS**: -16 LUFS for SFX, -14 LUFS for music

Use `ffmpeg-normalize` or Audacity batch processing.

### 5.4 Sound Categories

```typescript
enum AudioCategory {
  SFX_PLAYER = 'sfx_player',      // Hornet actions
  SFX_ENEMY = 'sfx_enemy',        // Bee sounds
  SFX_COMBAT = 'sfx_combat',      // Hits, kills
  SFX_UI = 'sfx_ui',              // Level up, menus
  MUSIC = 'music',                // Background tracks
  AMBIENT = 'ambient',            // Hive ambiance
}
```

**Volume Defaults** (user-adjustable):

| Category | Default | Range |
|----------|---------|-------|
| SFX_PLAYER | 0.8 | 0-1 |
| SFX_ENEMY | 0.6 | 0-1 |
| SFX_COMBAT | 1.0 | 0-1 |
| SFX_UI | 0.7 | 0-1 |
| MUSIC | 0.4 | 0-1 |
| AMBIENT | 0.3 | 0-1 |

### 5.5 Looping Requirements

| Asset Type | Loop | Loop Points |
|------------|------|-------------|
| Music tracks | Yes | Seamless, metadata-defined |
| Ambient loops | Yes | Seamless |
| SFX (most) | No | - |
| SFX (continuous) | Yes | Machine guns, dash trails |

**Loop Point Metadata**: Include in `audio_sprites.json`:

```json
{
  "gameplay_loop": {
    "file": "music/gameplay_loop.ogg",
    "loopStart": 4.523,
    "loopEnd": 124.891,
    "intro": true
  }
}
```

### 5.6 Audio Sprite Support

Bundle multiple short SFX into a single file to reduce HTTP requests:

```json
// audio/sprites/sfx_bundle.json
{
  "src": ["sfx_bundle.ogg", "sfx_bundle.mp3"],
  "sprite": {
    "kill_pop": [0, 80],
    "damage_thump": [100, 100],
    "levelup": [220, 300],
    "synergy_chime": [540, 200],
    "wave_horn": [760, 400],
    "dash_whoosh": [1180, 150],
    "bass_drop": [1350, 500],
    "heartbeat": [1870, 400]
  }
}
```

**Alignment**: Each sprite starts on a 10ms boundary for clean cuts.

---

## 6. Asset Loading Strategy

### 6.1 Critical Assets (Blocking)

Must load before game can start:

```typescript
const CRITICAL_ASSETS = [
  'atlases/player_atlas.png',
  'atlases/effects_atlas.png',
  'audio/sprites/sfx_bundle.json',
  'data/animations.json',
  'data/color_palettes.json',
  'fonts/game_ui.woff2',
];
```

**Target**: Critical assets < 2MB total, < 3 seconds on 3G.

### 6.2 Lazy-Loaded Assets

Load during gameplay, triggered by game events:

| Trigger | Assets Loaded |
|---------|---------------|
| Wave 3 complete | `atlases/enemies_atlas.png` (elite variants) |
| First boss spawn | `audio/music/boss_theme.ogg` |
| First metamorphosis | `atlases/colossals/the_tide.png`, `audio/colossal_theme.ogg` |
| Pause menu | `atlases/ui_atlas.png` |

### 6.3 Asset Bundles

Group assets by game stage:

```typescript
const BUNDLES = {
  core: ['player', 'basic_enemies', 'effects', 'sfx'],
  wave_5: ['elite_enemies', 'spitter_projectiles'],
  wave_10: ['boss', 'boss_theme'],
  metamorphosis: ['colossals', 'colossal_theme', 'metamorphosis_fx'],
  ui: ['menus', 'upgrade_icons', 'crystal_view'],
};
```

### 6.4 Preloading Strategy

```typescript
// During loading screen
await loadBundle('core');
showStartScreen();

// During wave 1-2 gameplay (background)
preloadBundle('wave_5');

// When pulsing enemies first appear
preloadBundle('metamorphosis');
```

### 6.5 Loading Progress Feedback

Display loading progress with meaningful messages:

```
Loading core assets... [####----] 45%
Preparing hornet sprites...
Loading combat sounds...
Ready to raid!
```

**Requirements**:
- Progress bar updates at least every 100ms
- Show current asset name for files > 100KB
- Animate loading indicator (not frozen)
- Show total MB loaded / total MB

### 6.6 Error Handling

```typescript
interface AssetLoadError {
  asset: string;
  error: Error;
  fallback: 'placeholder' | 'skip' | 'fatal';
}

// Non-critical asset fails: use placeholder
onError('bee_scout_idle.png', { fallback: 'placeholder' });

// Critical asset fails: show error, retry option
onError('player_atlas.png', { fallback: 'fatal' });
```

**User-facing error**:

```
Failed to load game assets.
Check your connection and try again.
[Retry] [Report Bug]
```

---

## 7. Hot Reloading (Development)

### 7.1 File Watcher Integration

Use `chokidar` or Vite's built-in watcher:

```typescript
// dev-server.ts
import chokidar from 'chokidar';

const watcher = chokidar.watch('assets/**/*', {
  ignored: /node_modules/,
  persistent: true,
});

watcher.on('change', (path) => {
  if (path.endsWith('.png')) {
    broadcastReload({ type: 'sprite', path });
  } else if (path.endsWith('.ogg') || path.endsWith('.mp3')) {
    broadcastReload({ type: 'audio', path });
  } else if (path.endsWith('.json')) {
    broadcastReload({ type: 'data', path });
  }
});
```

### 7.2 Hot-Reloadable Assets

| Asset Type | Hot Reload | Notes |
|------------|------------|-------|
| Sprites (PNG) | Yes | Texture re-upload |
| Audio (OGG/MP3) | Yes | Sound re-cache |
| Animation JSON | Yes | Re-parse definitions |
| Palette JSON | Yes | Runtime color update |
| Atlas (packed) | No | Requires rebuild |
| Fonts | No | Requires page refresh |

### 7.3 Cache Busting

Development mode appends timestamp to asset URLs:

```typescript
const assetUrl = DEV_MODE
  ? `${path}?t=${Date.now()}`
  : `${path}?v=${BUILD_HASH}`;
```

Production uses content hash in filename:

```
player_atlas.a3f8b2c1.png
sfx_bundle.7d4e9f12.ogg
```

### 7.4 WebSocket Reload Notifications

```typescript
// Client
const ws = new WebSocket('ws://localhost:3001/hot-reload');

ws.onmessage = (event) => {
  const { type, path } = JSON.parse(event.data);

  switch (type) {
    case 'sprite':
      spriteCache.invalidate(path);
      break;
    case 'audio':
      audioCache.invalidate(path);
      break;
    case 'data':
      configCache.invalidate(path);
      break;
  }
};
```

**Visual feedback**: Flash screen edge green on successful hot reload.

---

## 8. Build Pipeline

### 8.1 Asset Processing Steps

```
Source Assets                 Build Steps                    Output
-------------                 -----------                    ------
sprites/*.png        -->      validate palette
                     -->      compress (pngquant)
                     -->      pack atlas (TexturePacker)  --> atlases/*.png
                     -->      generate atlas_map.json     --> data/atlas_map.json

audio/sfx/*.wav      -->      convert to OGG/MP3
                     -->      normalize levels
                     -->      bundle sprites             --> audio/sprites/*

audio/music/*.wav    -->      convert to OGG/MP3
                     -->      normalize levels           --> audio/music/*

data/*.json          -->      validate schema
                     -->      minify                     --> data/*.json
```

### 8.2 Build Commands

```bash
# Full build
npm run build:assets

# Individual steps
npm run assets:validate    # Check all assets against specs
npm run assets:sprites     # Process and pack sprites
npm run assets:audio       # Process audio files
npm run assets:compress    # Final compression pass
npm run assets:manifest    # Generate asset manifest
```

### 8.3 Optimization Targets

| Asset Type | Target Size | Tool |
|------------|-------------|------|
| Player atlas (512x512) | < 200KB | pngquant + oxipng |
| Enemy atlas (512x512) | < 300KB | pngquant + oxipng |
| Effects atlas (256x256) | < 100KB | pngquant + oxipng |
| SFX bundle | < 500KB | OGG q5 |
| Music track (3min) | < 2MB | OGG q6 |

**Total critical assets target**: < 2MB

### 8.4 Fingerprinting for Cache Control

```typescript
// asset-manifest.json
{
  "version": "1.0.0",
  "buildTime": "2025-12-28T00:00:00Z",
  "assets": {
    "atlases/player_atlas.png": {
      "hash": "a3f8b2c1",
      "size": 187432,
      "path": "atlases/player_atlas.a3f8b2c1.png"
    }
  }
}
```

### 8.5 Source vs Built Separation

```
project/
├── assets/              # Source assets (Git)
│   ├── sprites/         # Individual PNGs
│   └── audio/
│       └── sfx/         # WAV source files
├── public/
│   └── assets/          # Built assets (gitignored)
│       ├── atlases/     # Packed sprite sheets
│       └── audio/       # Compressed OGG/MP3
└── dist/                # Final deployment (gitignored)
```

### 8.6 CI/CD Integration

```yaml
# .github/workflows/build.yml
- name: Build Assets
  run: npm run build:assets

- name: Validate Asset Sizes
  run: npm run assets:check-budget

- name: Upload Artifacts
  uses: actions/upload-artifact@v3
  with:
    name: game-assets
    path: public/assets/
```

**Budget checks fail CI if**:
- Any single asset > 5MB
- Total critical assets > 2MB
- Missing required assets

---

## 9. Version Control

### 9.1 Large File Handling

Use Git LFS for binary assets:

```bash
# .gitattributes
*.png filter=lfs diff=lfs merge=lfs -text
*.ogg filter=lfs diff=lfs merge=lfs -text
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.ttf filter=lfs diff=lfs merge=lfs -text
*.woff2 filter=lfs diff=lfs merge=lfs -text
```

**Exclusions** (small, text-based):
- JSON config files
- Markdown documentation
- Build scripts

### 9.2 Asset Versioning Scheme

```
assets/v{major}/...

v1/sprites/player/hornet_idle.png
v2/sprites/player/hornet_idle.png  # Major visual overhaul
```

**When to bump version**:
- Major visual style change (v1 -> v2)
- Breaking animation changes
- New character redesign

### 9.3 Rollback Procedures

```bash
# Rollback single asset
git checkout HEAD~1 -- assets/sprites/player/hornet_idle.png

# Rollback entire sprite category
git checkout v1.2.3 -- assets/sprites/enemies/

# Full asset rollback
git checkout release/1.0.0 -- assets/
npm run build:assets
```

**Pre-rollback checklist**:
1. Verify target commit/tag exists
2. Check animation.json compatibility
3. Run asset validation after rollback
4. Test in dev before deploying

### 9.4 Artist Collaboration Workflow

```
1. Artist creates/updates assets in feature branch
   git checkout -b art/new-enemy-sprites

2. Validate locally
   npm run assets:validate

3. Create PR with visual diff
   - GitHub renders PNG diffs automatically
   - Include before/after GIFs for animations

4. Review checklist:
   [ ] Palette compliance
   [ ] Correct dimensions (power of 2)
   [ ] Animation frame counts match spec
   [ ] File naming convention
   [ ] Size budget compliance

5. Merge triggers CI build
   - Assets rebuilt and published
   - CDN cache invalidated
```

---

## 10. Bee/Hornet Specific Requirements

### 10.1 Hornet Player States

The player character (hornet raider) requires these animation states:

| State | Frames | Duration | Description |
|-------|--------|----------|-------------|
| `idle` | 4 | 1000ms loop | Subtle wing flutter, antenna twitch |
| `move` | 8 | 667ms loop | Wings blur, body tilts in direction |
| `attack` | 6 | 375ms | Stinger thrust, wings spread |
| `damage` | 3 | 150ms | Flash white, knockback pose |
| `death` | 8 | 667ms | Spiral fall, wing crumple |
| `dash` | 4 | 250ms | Motion blur, afterimage |

**Visual characteristics**:
- Electric blue glow (primary color `#00D4FF`)
- Sharp, angular thorax (aggressive silhouette)
- Visible stinger (weapon indicator)
- Transparent wings with blue iridescence

### 10.2 Bee Enemy States (Per Type)

#### Worker Bee (Basic/Shambler)

| State | Frames | Duration | Behavior |
|-------|--------|----------|----------|
| `idle` | 4 | 1000ms | Slow wing beat, non-threatening |
| `move` | 4 | 500ms | Wobbling flight toward player |
| `telegraph` | 4 | 400ms | Rear back, wings spread |
| `attack` | 4 | 250ms | Lunge forward |
| `damage` | 2 | 100ms | Flinch, tumble |
| `death` | 6 | 500ms | Pollen burst, crumple |

**Visual**: Fuzzy, round, yellow/black stripes, small stinger

#### Scout Bee (Fast/Rusher)

| State | Frames | Duration | Behavior |
|-------|--------|----------|----------|
| `idle` | 4 | 500ms | Rapid wing beat, twitchy |
| `move` | 6 | 300ms | Darting zigzag motion |
| `telegraph` | 3 | 300ms | Crouch, aim at player |
| `attack` | 4 | 200ms | Linear charge |
| `damage` | 2 | 80ms | Spin out |
| `death` | 4 | 333ms | Fast spiral |

**Visual**: Slender, elongated abdomen, orange tint, triangle silhouette

#### Soldier Bee (Tank)

| State | Frames | Duration | Behavior |
|-------|--------|----------|----------|
| `idle` | 4 | 1500ms | Heavy breathing, guard stance |
| `move` | 4 | 800ms | Slow, deliberate march |
| `telegraph` | 6 | 600ms | Raise arms, ground glow |
| `attack` | 4 | 400ms | Ground pound |
| `damage` | 2 | 150ms | Barely flinch |
| `death` | 8 | 800ms | Slow collapse, armor crack |

**Visual**: Bulky, armored plates, square silhouette, muted brown

#### Spitter Bee (Ranged)

| State | Frames | Duration | Behavior |
|-------|--------|----------|----------|
| `idle` | 4 | 800ms | Hover, tracking |
| `move` | 4 | 500ms | Strafe, maintain distance |
| `telegraph` | 4 | 500ms | Aim laser, glow buildup |
| `attack` | 4 | 300ms | Honey spit, recoil |
| `damage` | 2 | 100ms | Retreat gesture |
| `death` | 6 | 500ms | Explode in honey splash |

**Visual**: Elongated thorax, visible honey sac, diamond silhouette

#### Queen Bee (Boss)

| State | Frames | Duration | Behavior |
|-------|--------|----------|----------|
| `idle` | 6 | 1500ms | Regal hover, crown glow |
| `move` | 6 | 1000ms | Majestic glide |
| `telegraph` | 8 | 800ms | Wings spread, halo effect |
| `attack_summon` | 6 | 600ms | Raise scepter, spawn workers |
| `attack_beam` | 8 | 400ms | Royal jelly beam |
| `damage` | 4 | 200ms | Indignant recoil |
| `death` | 12 | 1200ms | Crown shatter, dramatic fall |

**Visual**: Large (2x other bees), golden crown, octagonal silhouette, royal purple accents

### 10.3 Colossal Formation Sprites

When enemies metamorphose, they combine into Colossals:

#### THE TIDE (Shambler Colossal)

- **Size**: 128x128
- **Visual**: Amorphous mass of merged worker bees, no distinct form
- **Animation**: Constant churning, bubbling surface
- **Color**: Deep crimson (`#880000`) with pulsing veins
- **States**: `advance`, `absorb`, `fission`, `gravity_pulse`

#### THE RAMPAGE (Rusher Colossal)

- **Size**: 128x128
- **Visual**: Streamlined, bullet-shaped mass of scouts
- **Animation**: Constant vibration, motion blur trails
- **Color**: Orange-red gradient, flame-like edges
- **States**: `charge`, `bounce`, `aftershock`, `redline`

#### THE ARTILLERY (Spitter Colossal)

- **Size**: 128x128
- **Visual**: Floating honey fortress, multiple turrets
- **Animation**: Turrets track independently, honey drips
- **Color**: Amber with purple energy cores
- **States**: `barrage`, `mortar`, `suppression`, `air_burst`

#### THE FORTRESS (Tank Colossal)

- **Size**: 128x128
- **Visual**: Hexagonal bunker made of soldier armor
- **Animation**: Plates shift, internal glow
- **Color**: Bronze with red warning lights
- **States**: `siege_mode`, `quake`, `magnetize`, `bunker`

#### THE LEGION (Swarm Colossal)

- **Size**: 128x128 (when combined), 16x16 (fragments)
- **Visual**: Cloud of coordinated micro-bees forming shapes
- **Animation**: Constantly reforming, shape-shifting
- **Color**: Yellow-black swarm with red "eyes"
- **States**: `unified`, `scatter`, `encircle`, `drone_strike`

### 10.4 Environmental Elements

| Element | Size | Description |
|---------|------|-------------|
| Honeycomb Wall | 64x64 tile | Arena boundary, hexagonal pattern |
| Honey Pool | 32x32 | Slow zone hazard, amber with ripples |
| Wax Cell | 16x16 | Destructible prop, golden |
| Pollen Cloud | 32x32 | Particle emitter, yellow puffs |
| Royal Chamber | 128x128 | Boss arena centerpiece |
| Hive Entrance | 64x64 | Spawn point, dark portal |

### 10.5 Particle Effects

| Effect | Frames | Use Case |
|--------|--------|----------|
| `death_burst` | 8 | Enemy death (matches enemy color) |
| `xp_collect` | 4 | XP orb collection (golden trail) |
| `damage_flash` | 2 | Player/enemy hit (white flash) |
| `heal_pulse` | 6 | Health regeneration (green glow) |
| `pheromone_trail` | 6 | Enemy coordination visual |
| `honey_drip` | 4 | Spitter attack residue |
| `stinger_impact` | 4 | Player attack hit |
| `metamorphosis_pulse` | 8 | Enemy pulsing state |
| `metamorphosis_thread` | 6 | Enemy seeking connection |
| `colossal_spawn` | 12 | Metamorphosis completion flash |

---

## Appendix A: Tool Recommendations

| Task | Recommended Tool | Alternative |
|------|------------------|-------------|
| Sprite Creation | Aseprite | Piskel, Pixelorama |
| Atlas Packing | TexturePacker | free-tex-packer, spritesheet-js |
| PNG Compression | pngquant + oxipng | TinyPNG |
| Audio Editing | Audacity | Adobe Audition |
| Audio Conversion | ffmpeg | SoX |
| Level Normalization | ffmpeg-normalize | Audacity batch |
| Font Conversion | FontForge | Transfonter |
| Animation Preview | Aseprite | LICEcap (GIF capture) |

---

## Appendix B: Quick Reference

### File Size Budgets

```
Total Critical: < 2MB
  - Player Atlas: < 200KB
  - Enemy Atlas: < 300KB
  - Effects Atlas: < 100KB
  - SFX Bundle: < 500KB
  - Data JSONs: < 50KB
  - Fonts: < 100KB

Per-Asset Limits:
  - Single Sprite: < 50KB
  - Single SFX: < 100KB
  - Music Track: < 2MB
```

### Naming Cheat Sheet

```
Sprites:  {entity}_{state}_{frame}.png
          hornet_idle_01.png
          bee_worker_move_03.png

Audio:    {category}_{name}.ogg
          sfx_kill_pop.ogg
          music_boss_theme.ogg

Data:     {type}_{scope}.json
          animations.json
          palette_colorblind.json
```

### Color Codes

```
Player:     #00D4FF (Electric Blue)
Enemy:      #FF3366 (Corrupted Red)
XP:         #FFD700 (Golden)
Health:     #00FF88 (Vitality Green)
Crisis:     #FF8800 (Warning Orange)
Colossal:   #880000 (Deep Crimson)
```

---

*Document maintained by: Art Pipeline Team*
*Last reviewed: 2025-12-28*
