# PLAYER Verification Infrastructure Plan

> *"A player who cannot see cannot judge. A player who cannot judge must build eyes."*

**Created**: 2025-12-27
**Status**: PLANNING → EXECUTION
**Owner**: PLAYER (but implemented by CREATIVE/ADVERSARIAL)

---

## The Problem

In Run 028, PLAYER failed to verify DD-21 qualia claims because:

1. **No debug mode** — Couldn't see enemy behavior states
2. **No spawn controls** — Couldn't test specific enemy types on demand
3. **No targeted screenshots** — Random screenshots rarely caught the right moments
4. **Passive waiting** — PLAYER waited for evidence instead of building tools to capture it

**Result**: "⚠️ Can't verify" in feedback — unacceptable.

---

## The Solution Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: PLAYER VERIFICATION TESTS                                           │
│   e2e/player-verification.spec.ts — Tests that USE the infrastructure       │
│   Evidence capture, qualia validation, automated verification               │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: DEBUG OVERLAY (VISUAL)                                              │
│   ?debug=true URL param activates visual debug mode                         │
│   Enemy states, telegraph timers, hitboxes, damage sources                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ LAYER 1: DEBUG API (PROGRAMMATIC)                                            │
│   window.DEBUG_* functions for Playwright access                            │
│   Get state, spawn entities, control game, trigger events                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ FOUNDATION: CHEAT COMMANDS (KEYBOARD)                                        │
│   1-5 spawn enemies, I invincibility, N next wave, K kill all, L level up  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component 1: Debug API (Window Functions)

**Location**: `impl/claude/pilots-web/src/lib/debug-api.ts`

### Interface

```typescript
// Type definitions for the debug API
interface DebugAPI {
  // State inspection
  GET_GAME_STATE(): GameState | null;
  GET_ENEMIES(): Enemy[];
  GET_PLAYER(): Player | null;
  GET_LAST_DAMAGE(): DamageEvent | null;
  GET_TELEGRAPHS(): TelegraphData[];

  // Control
  SPAWN(type: EnemyType, position: { x: number; y: number }): Enemy;
  SET_INVINCIBLE(enabled: boolean): void;
  SKIP_WAVE(): void;
  KILL_ALL_ENEMIES(): void;
  LEVEL_UP(): void;
  SET_HEALTH(value: number): void;

  // Events
  ON_DEATH(callback: (info: DeathInfo) => void): void;
  ON_LEVEL_UP(callback: (level: number) => void): void;
  ON_ENEMY_TELEGRAPH(callback: (enemy: Enemy) => void): void;
}

// Exposed on window
declare global {
  interface Window {
    DEBUG_GET_GAME_STATE: () => GameState | null;
    DEBUG_GET_ENEMIES: () => Enemy[];
    DEBUG_GET_PLAYER: () => Player | null;
    DEBUG_GET_LAST_DAMAGE: () => DamageEvent | null;
    DEBUG_GET_TELEGRAPHS: () => TelegraphData[];
    DEBUG_SPAWN: (type: string, position: { x: number; y: number }) => Enemy;
    DEBUG_SET_INVINCIBLE: (enabled: boolean) => void;
    DEBUG_SKIP_WAVE: () => void;
    DEBUG_KILL_ALL_ENEMIES: () => void;
    DEBUG_LEVEL_UP: () => void;
    DEBUG_SET_HEALTH: (value: number) => void;
  }
}
```

### Implementation Notes

- Only initialized when `?debug=true` in URL
- Must have access to game state (via React context or global store)
- Functions should be synchronous where possible for Playwright reliability
- Return copies, not references (prevent mutation)

---

## Component 2: Debug Overlay (Visual)

**Location**: `impl/claude/pilots-web/src/pilots/*/components/DebugOverlay.tsx`

### Features

1. **Enemy State Labels**
   - Floating text above each enemy: "CHASE", "TELEGRAPH", "ATTACK", "RECOVERY"
   - Color-coded: Green (chase), Yellow (telegraph), Red (attack), Blue (recovery)

2. **Telegraph Timer Bars**
   - Progress bar showing telegraph duration remaining
   - Visible radius indicator for AoE attacks

3. **Hitbox Visualization**
   - Player hitbox (green circle)
   - Enemy hitboxes (red circles)
   - Attack hitboxes during attack state (orange)

4. **Damage Source Indicator**
   - Arrow pointing to last damage source
   - Text showing attack type and damage
   - Persists for 2 seconds after damage

5. **Game State Panel** (top-left corner)
   - Current wave
   - Enemy count by type
   - Player state (health, upgrades, invincibility)
   - FPS counter
   - Invincibility indicator

### Activation

```tsx
// In pilot's index.tsx
const searchParams = new URLSearchParams(window.location.search);
const debugMode = searchParams.get('debug') === 'true';

return (
  <>
    <GameCanvas ... />
    {debugMode && <DebugOverlay gameState={gameState} />}
  </>
);
```

---

## Component 3: Cheat Commands (Keyboard)

**Location**: `impl/claude/pilots-web/src/pilots/*/hooks/useDebugControls.ts`

### Key Bindings (Debug Mode Only)

| Key | Action | Notes |
|-----|--------|-------|
| `1` | Spawn basic enemy at cursor | Shambler |
| `2` | Spawn fast enemy at cursor | Rusher |
| `3` | Spawn tank enemy at cursor | Tank |
| `4` | Spawn spitter enemy at cursor | Spitter |
| `5` | Spawn boss enemy at cursor | Boss |
| `I` | Toggle invincibility | Visual indicator shows when active |
| `N` | Skip to next wave | Clears current enemies |
| `K` | Kill all enemies | Instant clear |
| `L` | Instant level up | Shows upgrade picker |
| `H` | Full heal | Reset health to max |
| `T` | Toggle hitbox display | Independent of overlay |
| `P` | Pause/unpause | Time stops |

### Implementation

```typescript
// useDebugControls.ts
export function useDebugControls(
  gameState: GameState,
  dispatch: (action: GameAction) => void
) {
  useEffect(() => {
    if (!isDebugMode()) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't capture if in input field
      if (e.target instanceof HTMLInputElement) return;

      switch (e.key) {
        case '1': dispatch({ type: 'DEBUG_SPAWN', enemyType: 'basic' }); break;
        case '2': dispatch({ type: 'DEBUG_SPAWN', enemyType: 'fast' }); break;
        // ... etc
        case 'i':
        case 'I': dispatch({ type: 'DEBUG_TOGGLE_INVINCIBLE' }); break;
        // ... etc
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [dispatch]);
}
```

---

## Component 4: PLAYER Verification Tests

**Location**: `impl/claude/pilots-web/e2e/player-verification.spec.ts`

### Test Categories

#### A. Basic Qualia Tests

```typescript
test.describe('PLAYER Qualia Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`/pilots/${PILOT_NAME}?debug=true`);
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);
  });

  test('enemy types are visually distinct', async ({ page }) => {
    // Spawn one of each type
    const types = ['basic', 'fast', 'tank', 'spitter', 'boss'];
    for (let i = 0; i < types.length; i++) {
      await page.evaluate(
        ([type, x]) => window.DEBUG_SPAWN(type, { x, y: 300 }),
        [types[i], 100 + i * 100]
      );
    }

    await page.screenshot({
      path: 'evidence/enemy-variety.png',
      fullPage: true,
    });

    // Verify all types exist
    const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES());
    const uniqueTypes = new Set(enemies.map(e => e.type));
    expect(uniqueTypes.size).toBe(5);
  });

  test('telegraphs are visible', async ({ page }) => {
    // Enable invincibility to survive
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE(true));

    // Spawn enemy near player
    await page.evaluate(() =>
      window.DEBUG_SPAWN('basic', { x: 100, y: 100 })
    );

    // Wait for telegraph state
    await page.waitForFunction(
      () => window.DEBUG_GET_ENEMIES()?.some(e => e.behaviorState === 'telegraph'),
      { timeout: 10000 }
    );

    // Capture during telegraph
    await page.screenshot({ path: 'evidence/telegraph-active.png' });

    // Verify telegraph data exists
    const telegraphs = await page.evaluate(() => window.DEBUG_GET_TELEGRAPHS());
    expect(telegraphs.length).toBeGreaterThan(0);
  });

  test('death attribution is specific', async ({ page }) => {
    // Spawn specific enemy type
    await page.evaluate(() =>
      window.DEBUG_SPAWN('fast', { x: 50, y: 50 })
    );

    // Wait for death
    await page.waitForSelector('[data-testid="death-overlay"]', {
      timeout: 30000,
    });

    // Capture death screen
    await page.screenshot({ path: 'evidence/death-attribution.png' });

    // Verify attribution
    const lastDamage = await page.evaluate(() => window.DEBUG_GET_LAST_DAMAGE());
    expect(lastDamage).toBeTruthy();
    expect(lastDamage?.attackType).toBeTruthy();
    expect(lastDamage?.attackType).not.toBe('contact'); // Should be specific
  });
});
```

#### B. Evidence Capture Tests

```typescript
test.describe('PLAYER Evidence Capture', () => {
  test('capture all enemy telegraphs', async ({ page }) => {
    await page.goto(`/pilots/${PILOT_NAME}?debug=true`);
    await page.keyboard.press('Space');
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE(true));

    const enemyTypes = ['basic', 'fast', 'tank', 'spitter', 'boss'];

    for (const type of enemyTypes) {
      // Clear existing enemies
      await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES());
      await page.waitForTimeout(100);

      // Spawn specific type
      await page.evaluate(
        (t) => window.DEBUG_SPAWN(t, { x: 200, y: 200 }),
        type
      );

      // Wait for telegraph
      await page.waitForFunction(
        () => window.DEBUG_GET_ENEMIES()?.some(e => e.behaviorState === 'telegraph'),
        { timeout: 10000 }
      );

      // Capture
      await page.screenshot({
        path: `evidence/telegraph-${type}.png`,
      });
    }
  });

  test('capture upgrade synergies', async ({ page }) => {
    await page.goto(`/pilots/${PILOT_NAME}?debug=true`);
    await page.keyboard.press('Space');
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE(true));

    // Level up multiple times
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.DEBUG_LEVEL_UP());
      await page.waitForSelector('[data-testid="upgrade-picker"]');
      await page.screenshot({ path: `evidence/upgrade-${i}.png` });
      await page.keyboard.press('1'); // Pick first option
      await page.waitForTimeout(500);
    }

    // Capture final build
    await page.screenshot({ path: 'evidence/final-build.png' });
  });
});
```

#### C. Regression Tests

```typescript
test.describe('PLAYER Regression Tests', () => {
  test('attackType is passed to death screen', async ({ page }) => {
    // This test would have caught the Run 028 bug
    await page.goto(`/pilots/${PILOT_NAME}?debug=true`);
    await page.keyboard.press('Space');

    // Spawn fast enemy (should show "SPEEDER CHARGE" on death)
    await page.evaluate(() =>
      window.DEBUG_SPAWN('fast', { x: 50, y: 50 })
    );

    await page.waitForSelector('[data-testid="death-overlay"]', {
      timeout: 30000,
    });

    // Check that death screen has specific attribution
    const deathCause = await page.textContent('[data-testid="death-cause"]');
    expect(deathCause).toContain('SPEEDER');
    expect(deathCause).not.toBe('SWARM');
  });
});
```

---

## Implementation Plan

### Phase 1: Debug API (Foundation)

**Files to Create/Modify**:
- `src/lib/debug-api.ts` — Debug API implementation
- `src/lib/debug-types.ts` — TypeScript interfaces
- `src/pilots/wasm-survivors-game/index.tsx` — Wire up debug API

**Estimated Time**: 1-2 hours

### Phase 2: Cheat Commands

**Files to Create/Modify**:
- `src/pilots/wasm-survivors-game/hooks/useDebugControls.ts` — Keyboard handler
- `src/pilots/wasm-survivors-game/index.tsx` — Integrate hook

**Estimated Time**: 1 hour

### Phase 3: Debug Overlay

**Files to Create/Modify**:
- `src/pilots/wasm-survivors-game/components/DebugOverlay.tsx` — Visual overlay
- `src/pilots/wasm-survivors-game/index.tsx` — Conditional render

**Estimated Time**: 2 hours

### Phase 4: PLAYER Verification Tests

**Files to Create/Modify**:
- `e2e/player-verification.spec.ts` — Test suite

**Estimated Time**: 1-2 hours

---

## Success Criteria

1. **Debug API works**:
   ```bash
   # In browser console with ?debug=true
   window.DEBUG_GET_ENEMIES()  // Returns enemy array
   window.DEBUG_SPAWN('fast', {x: 100, y: 100})  // Spawns enemy
   ```

2. **Cheat commands work**:
   - Press `1` → Enemy spawns
   - Press `I` → Invincibility toggles
   - Press `N` → Wave advances

3. **Debug overlay shows**:
   - Enemy state labels visible
   - Telegraph timers visible
   - Hitboxes visible when toggled

4. **Tests pass**:
   ```bash
   npx playwright test e2e/player-verification.spec.ts
   ```

5. **Evidence captured**:
   - `evidence/` folder contains screenshots for all qualia claims

---

## Integration with PLAYER Orchestrator

After implementation, PLAYER can:

1. **During BUILD (4-7)**: Request these tools, verify they work
2. **During WITNESS (8-10)**: Use tools to capture evidence for ALL claims

**No more "⚠️ Can't verify"** — every claim is either:
- ✅ Verified with evidence
- ❌ Failed with specific reason
- 🚫 BLOCKER filed (tools don't work)

---

## Generalization

This infrastructure is **pilot-agnostic**. The same pattern applies to:

- Any game pilot with entities and state
- Any pilot with visual qualia claims
- Any pilot needing PLAYER verification

The debug API and overlay patterns can be extracted to:
- `src/lib/debug-api.ts` — Generic debug utilities
- `src/components/DebugOverlay.tsx` — Generic overlay component
- `e2e/player-verification-base.ts` — Base test utilities

---

*Plan ready for execution. Delegate to sub-agents.*
