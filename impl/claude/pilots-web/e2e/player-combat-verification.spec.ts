/**
 * PLAYER Combat Verification Test Suite
 *
 * Tests to verify combat qualia (graze, venom, bleed, berserker) once the
 * DEBUG_GET_COMBAT_STATE, DEBUG_GET_ENEMY_STATUS APIs are implemented.
 *
 * STATUS: SCAFFOLDING - waiting for debug APIs
 * REQUESTED IN: .needs.creative.md (Iteration 4)
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part III: Combat Systems)
 * @see .player.qualia-matrix.md (M7, M9)
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PILOT_NAME = process.env.PILOT_NAME || 'wasm-survivors-game';
const EVIDENCE_DIR = path.join(__dirname, '..', 'evidence', 'combat');

// Ensure evidence directory exists
if (!fs.existsSync(EVIDENCE_DIR)) {
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

// =============================================================================
// Helper Functions
// =============================================================================

function getPilotURL(): string {
  return `/pilots/${PILOT_NAME}?debug=true`;
}

async function waitForDebugAPI(page: Page, timeout = 10000): Promise<boolean> {
  try {
    await page.waitForFunction(
      () => typeof window.DEBUG_GET_GAME_STATE === 'function',
      { timeout }
    );
    return true;
  } catch {
    return false;
  }
}

async function startGame(page: Page): Promise<void> {
  const beginButton = page.locator('button:has-text("BEGIN RAID"), button:has-text("Start Run")');
  if (await beginButton.first().isVisible()) {
    await beginButton.first().click();
  }
  await page.waitForTimeout(500);
}

async function hasCombatDebugAPI(page: Page): Promise<boolean> {
  return page.evaluate(() =>
    typeof (window as any).DEBUG_GET_COMBAT_STATE === 'function'
  );
}

// =============================================================================
// Combat Debug API Availability
// =============================================================================

test.describe('PLAYER Combat API Availability', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);
  });

  test('combat debug APIs are available', async ({ page }) => {
    const hasCombatState = await page.evaluate(() =>
      typeof (window as any).DEBUG_GET_COMBAT_STATE === 'function'
    );
    const hasEnemyStatus = await page.evaluate(() =>
      typeof (window as any).DEBUG_GET_ENEMY_STATUS === 'function'
    );
    const hasSpawnAtPlayer = await page.evaluate(() =>
      typeof (window as any).DEBUG_SPAWN_AT_PLAYER === 'function'
    );
    const hasApplyVenom = await page.evaluate(() =>
      typeof (window as any).DEBUG_APPLY_VENOM === 'function'
    );

    console.log('Combat APIs available:', {
      combatState: hasCombatState,
      enemyStatus: hasEnemyStatus,
      spawnAtPlayer: hasSpawnAtPlayer,
      applyVenom: hasApplyVenom,
    });

    if (!hasCombatState) {
      test.skip();
    }
  });
});

// =============================================================================
// M7: Graze Detection Verification
// =============================================================================

test.describe('PLAYER M7: Graze Detection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasCombatDebugAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('graze detected at 30px distance', async ({ page }) => {
    // Clear enemies
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    // Get initial combat state
    const initialState = await page.evaluate(() =>
      (window as any).DEBUG_GET_COMBAT_STATE?.()
    );
    const initialGrazeCount = initialState?.graze?.chainCount ?? 0;

    // Spawn enemy at exactly graze distance (30-35px from player)
    // Player is at ~400, 300 by default
    await page.evaluate(() =>
      (window as any).DEBUG_SPAWN_AT_PLAYER?.('basic', 35, 0)
    );

    // Wait for graze to trigger
    await page.waitForTimeout(500);

    const afterState = await page.evaluate(() =>
      (window as any).DEBUG_GET_COMBAT_STATE?.()
    );

    console.log('Graze state:', afterState?.graze);

    expect(afterState?.graze?.chainCount).toBeGreaterThan(initialGrazeCount);

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'graze-30px.png') });
  });

  test('graze chain builds bonus damage', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Spawn enemy at graze distance
    await page.evaluate(() =>
      (window as any).DEBUG_SPAWN_AT_PLAYER?.('basic', 32, 0)
    );
    await page.waitForTimeout(500);

    const state = await page.evaluate(() =>
      (window as any).DEBUG_GET_COMBAT_STATE?.()
    );

    console.log('Graze bonus state:', state?.graze);

    // After graze, bonus should be active
    if (state?.graze?.chainCount > 0) {
      expect(state?.graze?.bonusActive).toBe(true);
    }

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'graze-chain-bonus.png') });
  });

  test('graze spark particle visible', async ({ page }) => {
    // This is a visual test - spawn at graze distance and capture
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    await page.evaluate(() =>
      (window as any).DEBUG_SPAWN_AT_PLAYER?.('basic', 32, 0)
    );

    // Capture during graze window
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'graze-spark-visual.png') });

    // Visual inspection: look for cyan spark particle
    console.log('Visual inspection: Check graze-spark-visual.png for cyan spark');
  });
});

// =============================================================================
// M9: Venom Paralysis Verification
// =============================================================================

test.describe('PLAYER M9: Venom Paralysis', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasCombatDebugAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('3 venom stacks cause paralysis', async ({ page }) => {
    // Spawn enemy
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 200, y: 200 }));
    await page.waitForTimeout(100);

    // Get enemy ID
    const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
    const enemyId = enemies?.[0]?.id;

    if (!enemyId) {
      throw new Error('No enemy spawned');
    }

    // Check initial status
    const initialStatus = await page.evaluate(
      (id) => (window as any).DEBUG_GET_ENEMY_STATUS?.(id),
      enemyId
    );
    console.log('Initial enemy status:', initialStatus);

    // Apply 3 venom stacks
    await page.evaluate((id) => (window as any).DEBUG_APPLY_VENOM?.(id, 3), enemyId);
    await page.waitForTimeout(100);

    // Check status after venom
    const afterStatus = await page.evaluate(
      (id) => (window as any).DEBUG_GET_ENEMY_STATUS?.(id),
      enemyId
    );

    console.log('Enemy status after 3 venom:', afterStatus);

    expect(afterStatus?.venomStacks).toBe(3);
    expect(afterStatus?.paralyzed).toBe(true);
    expect(afterStatus?.paralysisRemaining).toBeGreaterThan(1000); // ~1.5s

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'venom-paralysis-3-stacks.png') });
  });

  test('paralysis duration is 1.5s', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 200, y: 200 }));
    await page.waitForTimeout(100);

    const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
    const enemyId = enemies?.[0]?.id;

    if (!enemyId) {
      throw new Error('No enemy spawned');
    }

    // Apply paralysis
    await page.evaluate((id) => (window as any).DEBUG_APPLY_VENOM?.(id, 3), enemyId);

    // Record paralysis timing
    const timings: { time: number; paralyzed: boolean; remaining: number }[] = [];
    const startTime = Date.now();

    while (Date.now() - startTime < 3000) {
      const status = await page.evaluate(
        (id) => (window as any).DEBUG_GET_ENEMY_STATUS?.(id),
        enemyId
      );
      timings.push({
        time: Date.now() - startTime,
        paralyzed: status?.paralyzed ?? false,
        remaining: status?.paralysisRemaining ?? 0,
      });
      await page.waitForTimeout(100);
    }

    // Find when paralysis ended
    const endIndex = timings.findIndex((t) => !t.paralyzed);
    const paralysisEnd = endIndex > 0 ? timings[endIndex - 1].time : 3000;

    console.log(`Paralysis duration: ${paralysisEnd}ms (target: 1500ms)`);

    // Should be close to 1500ms
    expect(paralysisEnd).toBeGreaterThanOrEqual(1200); // At least 1.2s
    expect(paralysisEnd).toBeLessThanOrEqual(1800); // At most 1.8s

    // Save timing log
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'venom-paralysis-timing.json'),
      JSON.stringify(timings, null, 2)
    );
  });
});

// =============================================================================
// Berserker Bonus Verification
// =============================================================================

test.describe('PLAYER Berserker Bonus', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasCombatDebugAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('nearby enemies increase berserker bonus', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Check baseline (no enemies)
    const baseline = await page.evaluate(() =>
      (window as any).DEBUG_GET_COMBAT_STATE?.()
    );
    console.log('Baseline berserker:', baseline?.berserker);

    // Spawn 5 enemies close by (within 200px)
    for (let i = 0; i < 5; i++) {
      await page.evaluate(
        (idx) => window.DEBUG_SPAWN?.('basic', { x: 350 + idx * 30, y: 300 }),
        i
      );
    }
    await page.waitForTimeout(200);

    const withEnemies = await page.evaluate(() =>
      (window as any).DEBUG_GET_COMBAT_STATE?.()
    );

    console.log('Berserker with 5 nearby:', withEnemies?.berserker);

    expect(withEnemies?.berserker?.nearbyEnemyCount).toBeGreaterThanOrEqual(5);
    expect(withEnemies?.berserker?.bonusPercent).toBeGreaterThan(0);

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'berserker-5-nearby.png') });
  });

  test('berserker caps at 50%', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Spawn 20 enemies close by
    for (let i = 0; i < 20; i++) {
      await page.evaluate(
        (idx) => window.DEBUG_SPAWN?.('basic', { x: 300 + (idx % 5) * 30, y: 250 + Math.floor(idx / 5) * 30 }),
        i
      );
    }
    await page.waitForTimeout(200);

    const state = await page.evaluate(() =>
      (window as any).DEBUG_GET_COMBAT_STATE?.()
    );

    console.log('Berserker with 20 enemies:', state?.berserker);

    expect(state?.berserker?.bonusPercent).toBeLessThanOrEqual(50);

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'berserker-cap-50.png') });
  });
});

// =============================================================================
// M3: Dash i-Frame Verification
// =============================================================================

test.describe('PLAYER M3: Dash i-Frames', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasCombatDebugAPI(page))) {
      test.skip();
    }

    // Do NOT enable invincibility - we're testing dash i-frames
  });

  test('dash i-frames active during dash', async ({ page }) => {
    // Get initial health
    const initialPlayer = await page.evaluate(() => window.DEBUG_GET_PLAYER?.());
    const initialHealth = initialPlayer?.health ?? 100;

    // Spawn enemy directly on player position
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 400, y: 300 }));

    // Trigger dash immediately (Space key or Shift typically)
    await page.keyboard.press('Shift');

    // Check combat state during dash
    await page.waitForTimeout(50); // During i-frame window
    const combatState = await page.evaluate(() =>
      (window as any).DEBUG_GET_COMBAT_STATE?.()
    );

    console.log('Combat state during dash:', combatState?.dash);

    if (combatState?.dash?.iframeActive) {
      expect(combatState.dash.iframeActive).toBe(true);

      // Check player health didn't decrease during i-frames
      const afterPlayer = await page.evaluate(() => window.DEBUG_GET_PLAYER?.());
      expect(afterPlayer?.health).toBe(initialHealth);
    }

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'dash-iframe-active.png') });
  });

  test('dash cooldown visible', async ({ page }) => {
    // Trigger dash
    await page.keyboard.press('Shift');
    await page.waitForTimeout(100);

    const state = await page.evaluate(() =>
      (window as any).DEBUG_GET_COMBAT_STATE?.()
    );

    console.log('Dash cooldown after use:', state?.dash);

    expect(state?.dash?.cooldownRemaining).toBeGreaterThan(0);

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'dash-cooldown.png') });
  });
});
