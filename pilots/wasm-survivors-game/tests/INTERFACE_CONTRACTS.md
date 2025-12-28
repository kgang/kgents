# Interface Contracts — WASM Survivors

> *"The proof IS the test. The spec IS the truth."*

These contracts define the interfaces that implementation must satisfy.
All systems in BUILD phase must pass these contracts.

---

## Run 025-026 Contracts (PASSED)

See archived contracts in Run 026. All Fun Floor requirements met:
- DD-1 through DD-15: Complete
- Input latency: 0.10ms (target: <16ms) ✅
- Frame rate: 120 FPS (target: 60) ✅
- Restart time: 503ms (target: <3000ms) ✅
- Fun Floor: 11/11 ✅

---

## Run 027 Contracts — Transcendence Layer

### DD-16: Clutch Moment System

```typescript
interface ClutchState {
  active: boolean;
  timeScale: number;        // 0.2 = 5x slow motion
  zoomFactor: number;       // 1.3 = 30% zoom
  bassDropTriggered: boolean;
  durationMs: number;
  elapsed: number;
}

interface ClutchMomentConfig {
  timeScale: number;
  zoomFactor: number;
  bassDrop: boolean;
  durationMs: number;
}

function checkClutchMoment(
  healthFraction: number,
  threatCount: number
): ClutchMomentConfig | null;

function applyClutchState(
  gameState: GameState,
  clutchConfig: ClutchMomentConfig,
  deltaTime: number
): GameState;
```

**Trigger Conditions** (from juice.ts):
- Full clutch: healthFraction < 0.15 AND threats > 3
- Medium clutch: healthFraction < 0.25 AND threats > 5
- Critical: healthFraction < 0.10

**Contract Tests**:

| Test | Input | Expected | Spec Law |
|------|-------|----------|----------|
| `clutch-trigger-full` | health=10%, threats=4 | timeScale=0.2, zoom=1.3, bass=true | S3 |
| `clutch-trigger-medium` | health=20%, threats=6 | timeScale=1.0, zoom=1.2, bass=true | S3 |
| `clutch-trigger-critical` | health=5%, threats=1 | timeScale=0.3, zoom=1.0, bass=false | S3 |
| `clutch-no-trigger` | health=50%, threats=2 | null | S3 |
| `clutch-duration` | clutch active | Returns to normal after durationMs | S3 |
| `clutch-bass-plays` | bassDrop=true | Sound engine plays bass drop | S3 |

---

### DD-17: Combo Crescendo

```typescript
interface ComboVisualState {
  comboCount: number;
  brightness: number;      // 1.0 base, 1.2 at combo 5+
  saturation: number;      // 1.0 base, 1.3 at combo 10+
  particleDensity: number; // 1.0 base, 2.0 at combo 20+
  euphoriaMode: boolean;   // true at combo 50+
}

function getComboVisuals(combo: number): ComboVisualState;
```

**Scaling Rules**:
- Combo 0-4: Base visuals (1.0, 1.0, 1.0, false)
- Combo 5-9: brightness=1.2
- Combo 10-19: saturation=1.3
- Combo 20-49: particleDensity=2.0
- Combo 50+: euphoriaMode=true (all maxed)

**Contract Tests**:

| Test | Input | Expected | Spec Law |
|------|-------|----------|----------|
| `combo-base` | combo=0 | brightness=1.0 | S2 |
| `combo-bright` | combo=5 | brightness=1.2 | S2 |
| `combo-saturate` | combo=10 | saturation=1.3 | S2 |
| `combo-dense` | combo=20 | particleDensity=2.0 | S2 |
| `combo-euphoria` | combo=50 | euphoriaMode=true | S2 |
| `combo-reset-on-damage` | take damage | combo resets to 0 | S2 |

---

### DD-18: Death Narrative

```typescript
interface DeathNarrative {
  killedBy: EnemyType;
  survivalTime: number;
  enemiesKilled: number;
  buildIdentity: string;
  waveReached: number;
  synergiesDiscovered: string[];
  upgradesTaken: UpgradeType[];
}

function generateDeathNarrative(state: GameState): DeathNarrative;
```

**Contract Tests**:

| Test | Input | Expected | Spec Law |
|------|-------|----------|----------|
| `death-shows-killer` | killed by tank | killedBy='tank' displayed | E3 |
| `death-shows-time` | 45 seconds | "0:45" displayed | E3 |
| `death-shows-kills` | 23 kills | "23 enemies defeated" | E3 |
| `death-shows-build` | pierce+multishot | "Build: Shotgun Drill" | E3 |
| `death-shows-wave` | wave 5 | "Wave 5" displayed | E3 |
| `death-shows-synergies` | 2 synergies | Synergy names listed | E3 |

---

### DD-19: Wave Victory Fanfare

```typescript
interface WaveTransition {
  phase: 'triumph' | 'silence' | 'storm';
  duration: number;
  spawningDisabled: boolean;
}

interface WaveTransitionConfig {
  triumphDuration: number;  // 2 seconds of celebration
  silenceDuration: number;  // 2-4 seconds of calm
  stormDelay: number;       // 1 second warning
}

function processWaveTransition(
  wave: number,
  phaseElapsed: number
): WaveTransition;
```

**Transition Flow**:
1. Wave complete → TRIUMPH (2s): Fanfare, particles, stats
2. TRIUMPH → SILENCE (2-4s): No spawns, calm music
3. SILENCE → STORM (after delay): Enemies spawn, music intensifies

**Contract Tests**:

| Test | Input | Expected | Spec Law |
|------|-------|----------|----------|
| `wave-triumph-phase` | wave ends | phase='triumph' for 2s | C1 |
| `wave-silence-phase` | triumph ends | phase='silence', spawningDisabled=true | C1, C5 |
| `wave-storm-phase` | silence ends | phase='storm', spawningDisabled=false | C1 |
| `wave-fanfare-sound` | triumph starts | Sound engine plays wave fanfare | C1 |
| `wave-silence-audio` | silence phase | Music volume reduces | C5 |

---

### DD-20: Health Vignette

```typescript
interface HealthVignette {
  intensity: number;  // 0.0 = none, 1.0 = full danger
  color: string;      // Red at low health
  pulseRate: number;  // Hz of pulse animation
}

function getHealthVignette(healthFraction: number): HealthVignette;
```

**Scaling Rules**:
- health > 50%: intensity=0 (no vignette)
- health 25-50%: intensity = (0.5 - health) * 2, pulseRate=1Hz
- health < 25%: intensity = (0.25 - health) * 4, pulseRate=2Hz
- health < 10%: intensity=1.0, pulseRate=4Hz (critical)

**Contract Tests**:

| Test | Input | Expected | Spec Law |
|------|-------|----------|----------|
| `vignette-none` | health=75% | intensity=0 | C4 |
| `vignette-mild` | health=40% | intensity=0.2, pulse=1Hz | C4 |
| `vignette-danger` | health=20% | intensity=0.6, pulse=2Hz | C4 |
| `vignette-critical` | health=5% | intensity=1.0, pulse=4Hz | C4 |
| `vignette-render` | intensity>0 | Red overlay renders at screen edge | C4 |

---

## Integration Tests

### Transcendence Integration

| Test | Description | Spec Laws |
|------|-------------|-----------|
| `transcend-clutch-vignette` | Low health triggers both clutch AND vignette | S3, C4 |
| `transcend-combo-death` | High combo → death shows combo in narrative | S2, E3 |
| `transcend-wave-synergy` | New wave + synergy = double fanfare | C1, U3 |
| `transcend-full-arc` | Wave 1→10 shows HOPE→FLOW→CRISIS→TRIUMPH | E1 |

### Emotional Arc Test

```typescript
// The ultimate test: Does the game follow the emotional arc?
// Wave 1-2: HOPE — brightness baseline
// Wave 3-4: FLOW — combo system engaged, saturation up
// Wave 5-6: CHALLENGE — threats increase, occasional vignette
// Wave 7-8: CRISIS — frequent clutch moments, high vignette
// Wave 9-10: TRIUMPH or GRIEF — either euphoria or clear death
```

---

## Verification Commands

```bash
# Run Run 027 contract tests
npm run test:contracts -- --grep "DD-16\|DD-17\|DD-18\|DD-19\|DD-20"

# Run specific system tests
npm run test:contracts -- --grep "clutch"
npm run test:contracts -- --grep "combo"
npm run test:contracts -- --grep "vignette"

# Run transcendence integration
npm run test:transcendence
```

---

*Updated: Run 027, Iteration 3*
*Source: PROTO_SPEC.md + .outline.md*
