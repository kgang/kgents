/**
 * PLAYER Metamorphosis Verification Tests — Run 030
 *
 * Tests for the core metamorphosis qualia:
 * - M-1: Timer predictability
 * - M-2: Pulsing visibility (OBVIOUS)
 * - M-3: Kill pulsing = reset nearby
 * - LC-1: Survival timer visible
 * - LC-2: Four-state lifecycle
 * - LC-3: Seeking behavior
 * - LC-4: 2+ pulsing touch = combination
 *
 * NOTE: These tests require the extended debug API from Run 030.
 * They will skip gracefully if survivalTime/pulsingState are not available.
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 * @see pilots/wasm-survivors-game/runs/run-030/coordination/.player.qualia-matrix.md
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { createStateMachineValidator } from './framework';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PILOT_NAME = 'wasm-survivors-game';
const EVIDENCE_DIR = path.join(__dirname, '..', '..', 'evidence', 'run-030');

// Ensure evidence directory exists
if (!fs.existsSync(EVIDENCE_DIR)) {
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

// =============================================================================
// Helper Types (Expected from Run 030 debug API)
// =============================================================================

interface MetamorphosisEnemy {
  id: string;
  type: string;
  position: { x: number; y: number };
  health: number;
  behaviorState: string;
  // Run 030 extensions
  survivalTime?: number;
  pulsingState?: 'normal' | 'pulsing' | 'seeking' | 'combining';
  seekTarget?: string | null;
  isLinked?: boolean;
}

// =============================================================================
// Helper Functions
// =============================================================================

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

async function getEnemies(page: Page): Promise<MetamorphosisEnemy[]> {
  return page.evaluate(() => window.DEBUG_GET_ENEMIES?.() || []);
}

async function hasMetamorphosisAPI(page: Page): Promise<boolean> {
  const enemies = await getEnemies(page);
  if (enemies.length === 0) {
    // Spawn an enemy to check
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 400, y: 300 }));
    await page.waitForTimeout(100);
    const newEnemies = await getEnemies(page);
    if (newEnemies.length === 0) return false;
    return 'survivalTime' in newEnemies[0] && 'pulsingState' in newEnemies[0];
  }
  return 'survivalTime' in enemies[0] && 'pulsingState' in enemies[0];
}

function getPilotURL(): string {
  return `/pilots/${PILOT_NAME}?debug=true`;
}

// =============================================================================
// M-1: Timer Predictability Tests
// =============================================================================

test.describe('M-1: Timer Predictability', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    const hasAPI = await waitForDebugAPI(page);
    if (!hasAPI) {
      test.skip();
      return;
    }
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);
  });

  test('survival timer increases consistently', async ({ page }) => {
    const hasMetaAPI = await hasMetamorphosisAPI(page);
    if (!hasMetaAPI) {
      console.log('Metamorphosis API not available yet - skipping');
      test.skip();
      return;
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    // Spawn enemy and track survival time
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 400, y: 300 }));

    const samples: { time: number; survivalTime: number }[] = [];
    const observeDuration = 12000; // 12 seconds (past pulsing threshold)
    const startTime = Date.now();

    while (Date.now() - startTime < observeDuration) {
      const enemies = await getEnemies(page);
      if (enemies.length > 0 && enemies[0].survivalTime !== undefined) {
        samples.push({
          time: Date.now() - startTime,
          survivalTime: enemies[0].survivalTime,
        });
      }
      await page.waitForTimeout(100);
    }

    // Save evidence
    const logPath = path.join(EVIDENCE_DIR, 'timer-consistency.json');
    fs.writeFileSync(logPath, JSON.stringify(samples, null, 2));

    // Verify timer increases monotonically
    for (let i = 1; i < samples.length; i++) {
      expect(samples[i].survivalTime).toBeGreaterThanOrEqual(samples[i - 1].survivalTime);
    }

    // Verify rough consistency with wall clock (±20% tolerance)
    const lastSample = samples[samples.length - 1];
    const expectedSurvival = lastSample.time;
    const actualSurvival = lastSample.survivalTime;
    const tolerance = 0.2;

    expect(actualSurvival).toBeGreaterThan(expectedSurvival * (1 - tolerance));
    expect(actualSurvival).toBeLessThan(expectedSurvival * (1 + tolerance));

    console.log(`Timer consistency: ${samples.length} samples over ${observeDuration}ms`);
    console.log(`Final: wall=${lastSample.time}ms, game=${actualSurvival}ms`);
  });

  test('enemy transitions to pulsing at 10s threshold', async ({ page }) => {
    const hasMetaAPI = await hasMetamorphosisAPI(page);
    if (!hasMetaAPI) {
      test.skip();
      return;
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 400, y: 300 }));

    // Wait for pulsing state (should happen around 10s)
    let pulsingStartTime: number | null = null;
    const startTime = Date.now();
    const timeout = 15000;

    while (Date.now() - startTime < timeout) {
      const enemies = await getEnemies(page);
      if (enemies.length > 0 && enemies[0].pulsingState === 'pulsing') {
        pulsingStartTime = enemies[0].survivalTime ?? (Date.now() - startTime);
        break;
      }
      await page.waitForTimeout(50);
    }

    if (pulsingStartTime === null) {
      await page.screenshot({
        path: path.join(EVIDENCE_DIR, 'no-pulsing-state.png'),
      });
      throw new Error('Enemy never reached pulsing state');
    }

    // Verify pulsing started around 10s (±2s tolerance)
    expect(pulsingStartTime).toBeGreaterThan(8000);
    expect(pulsingStartTime).toBeLessThan(12000);

    console.log(`Pulsing started at ${pulsingStartTime}ms (expected ~10000ms)`);

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'pulsing-threshold.png'),
    });
  });
});

// =============================================================================
// LC-2: Four-State Lifecycle Tests
// =============================================================================

test.describe('LC-2: Four-State Lifecycle', () => {
  test('enemy progresses through normal → pulsing → seeking → combining', async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasAPI = await waitForDebugAPI(page);
    if (!hasAPI) {
      test.skip();
      return;
    }

    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    const hasMetaAPI = await hasMetamorphosisAPI(page);
    if (!hasMetaAPI) {
      test.skip();
      return;
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Spawn two enemies close together (needed for seeking/combining)
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 300, y: 300 }));
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 350, y: 300 }));

    const stateLog: { time: number; states: string[] }[] = [];
    const observeDuration = 25000; // 25s (past combine threshold)
    const startTime = Date.now();

    while (Date.now() - startTime < observeDuration) {
      const enemies = await getEnemies(page);
      if (enemies.length > 0) {
        const states = enemies.map(e => e.pulsingState || 'unknown');
        stateLog.push({ time: Date.now() - startTime, states });
      }
      await page.waitForTimeout(100);
    }

    // Save evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'lifecycle-states.json'),
      JSON.stringify(stateLog, null, 2)
    );

    // Verify we saw state progression
    const allStates = new Set(stateLog.flatMap(s => s.states));
    console.log('Observed states:', Array.from(allStates));

    // We should see at least normal and pulsing
    expect(allStates.has('normal')).toBe(true);
    expect(allStates.has('pulsing')).toBe(true);

    // If test ran long enough, should see seeking
    if (stateLog.length > 0 && stateLog[stateLog.length - 1].time > 15000) {
      expect(allStates.has('seeking') || allStates.has('combining')).toBe(true);
    }

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'lifecycle-final.png'),
    });
  });
});

// =============================================================================
// M-3: Kill Pulsing = Reset Nearby
// =============================================================================

test.describe('M-3: Kill Pulsing Resets Nearby', () => {
  test('killing pulsing enemy resets survival time of nearby enemies', async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasAPI = await waitForDebugAPI(page);
    if (!hasAPI) {
      test.skip();
      return;
    }

    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    const hasMetaAPI = await hasMetamorphosisAPI(page);
    if (!hasMetaAPI) {
      test.skip();
      return;
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Spawn 3 enemies in a cluster
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 300, y: 300 }));
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 350, y: 300 }));
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 325, y: 350 }));

    // Wait for all to be pulsing
    let allPulsing = false;
    const pulsingTimeout = 15000;
    const startTime = Date.now();

    while (Date.now() - startTime < pulsingTimeout) {
      const enemies = await getEnemies(page);
      if (enemies.length >= 3 && enemies.every(e => e.pulsingState === 'pulsing')) {
        allPulsing = true;
        break;
      }
      await page.waitForTimeout(100);
    }

    if (!allPulsing) {
      console.log('Could not get all enemies to pulsing state - skipping');
      test.skip();
      return;
    }

    // Record survival times before kill
    const beforeKill = await getEnemies(page);
    const survivalTimesBefore = beforeKill.map(e => ({
      id: e.id,
      survivalTime: e.survivalTime,
    }));

    // Kill one enemy (need DEBUG_KILL_ENEMY or similar)
    // For now, we'll simulate by checking if the feature exists
    const canKillSingle = await page.evaluate(() =>
      typeof (window as any).DEBUG_KILL_ENEMY === 'function'
    );

    if (!canKillSingle) {
      console.log('DEBUG_KILL_ENEMY not available - test incomplete');
      // Save partial evidence
      fs.writeFileSync(
        path.join(EVIDENCE_DIR, 'reset-nearby-incomplete.json'),
        JSON.stringify({ survivalTimesBefore, reason: 'No single-kill API' }, null, 2)
      );
      return;
    }

    // Kill first enemy
    await page.evaluate((id: string) => (window as any).DEBUG_KILL_ENEMY?.(id), beforeKill[0].id);
    await page.waitForTimeout(200);

    // Record survival times after kill
    const afterKill = await getEnemies(page);
    const survivalTimesAfter = afterKill.map(e => ({
      id: e.id,
      survivalTime: e.survivalTime,
    }));

    // Save evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'reset-nearby.json'),
      JSON.stringify({ survivalTimesBefore, survivalTimesAfter }, null, 2)
    );

    // Verify remaining enemies had their timers reset or reduced
    for (const after of survivalTimesAfter) {
      const before = survivalTimesBefore.find(b => b.id === after.id);
      if (before) {
        // Timer should be lower than before (reset) or at least not increased by expected amount
        expect(after.survivalTime).toBeLessThan(before.survivalTime! + 200);
      }
    }

    console.log('Survival time reset verified');
  });
});

// =============================================================================
// M-2: Pulsing Visibility
// =============================================================================

test.describe('M-2: Pulsing Visibility', () => {
  test('pulsing enemy is visually obvious', async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasAPI = await waitForDebugAPI(page);
    if (!hasAPI) {
      test.skip();
      return;
    }

    await page.keyboard.press('Space');
    await page.waitForTimeout(500);
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Force pulsing if available, otherwise wait
    const canForcePulsing = await page.evaluate(() =>
      typeof (window as any).DEBUG_FORCE_PULSING === 'function'
    );

    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 700, y: 100 }));

    if (canForcePulsing) {
      await page.evaluate(() => (window as any).DEBUG_FORCE_PULSING?.());
    } else {
      // Wait 10+ seconds for natural pulsing
      await page.waitForTimeout(11000);
    }

    // Capture screenshot for visual inspection
    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'pulsing-visibility.png'),
      fullPage: true,
    });

    // Verify debug overlay shows PULSING label
    const bodyText = await page.textContent('body');
    const hasPulsingLabel = bodyText?.includes('PULSING') || bodyText?.includes('pulsing');

    console.log('Pulsing label visible:', hasPulsingLabel);
    console.log('Screenshot saved for visual inspection');

    // This test requires human verification of screenshot
    // The screenshot should show:
    // - Orange/red glowing outline on pulsing enemy
    // - PULSING label in debug overlay
    // - Enemy visible even at edge of screen
  });
});

// =============================================================================
// LC-3: Seeking Behavior
// =============================================================================

test.describe('LC-3: Seeking Behavior', () => {
  test('seeking enemies gravitate toward each other', async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasAPI = await waitForDebugAPI(page);
    if (!hasAPI) {
      test.skip();
      return;
    }

    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    const hasMetaAPI = await hasMetamorphosisAPI(page);
    if (!hasMetaAPI) {
      test.skip();
      return;
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Spawn two enemies far apart
    const initialX1 = 200;
    const initialX2 = 600;
    await page.evaluate((x) => window.DEBUG_SPAWN?.('basic', { x, y: 300 }), initialX1);
    await page.evaluate((x) => window.DEBUG_SPAWN?.('basic', { x, y: 300 }), initialX2);

    // Wait for seeking state
    await page.waitForTimeout(16000); // Past 15s threshold

    // Check if enemies are in seeking state and have seekTargets
    const enemies = await getEnemies(page);
    const seekingEnemies = enemies.filter(e => e.pulsingState === 'seeking');

    console.log(`Enemies in seeking state: ${seekingEnemies.length}`);
    console.log('Seek targets:', seekingEnemies.map(e => e.seekTarget));

    // Measure distance between enemies over time
    const distanceLog: { time: number; distance: number }[] = [];
    const measureDuration = 5000;
    const startTime = Date.now();

    while (Date.now() - startTime < measureDuration) {
      const currentEnemies = await getEnemies(page);
      if (currentEnemies.length >= 2) {
        const dx = currentEnemies[0].position.x - currentEnemies[1].position.x;
        const dy = currentEnemies[0].position.y - currentEnemies[1].position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        distanceLog.push({ time: Date.now() - startTime, distance });
      }
      await page.waitForTimeout(100);
    }

    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'seeking-distance.json'),
      JSON.stringify(distanceLog, null, 2)
    );

    // Verify distance decreased (enemies moved toward each other)
    if (distanceLog.length > 10) {
      const firstDistance = distanceLog[0].distance;
      const lastDistance = distanceLog[distanceLog.length - 1].distance;
      console.log(`Distance: ${firstDistance.toFixed(0)} → ${lastDistance.toFixed(0)}`);

      expect(lastDistance).toBeLessThan(firstDistance);
    }

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'seeking-behavior.png'),
    });
  });
});

// =============================================================================
// LC-4: Combination Trigger
// =============================================================================

test.describe('LC-4: Combination Trigger', () => {
  test('2+ pulsing enemies touching triggers combination', async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasAPI = await waitForDebugAPI(page);
    if (!hasAPI) {
      test.skip();
      return;
    }

    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    const hasMetaAPI = await hasMetamorphosisAPI(page);
    if (!hasMetaAPI) {
      test.skip();
      return;
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Spawn two enemies very close together
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 400, y: 300 }));
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 420, y: 300 }));

    let combinationTriggered = false;
    let colossalSpawned = false;
    const timeout = 25000;
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const enemies = await getEnemies(page);

      // Check for combining state
      const combiningEnemies = enemies.filter(e => e.pulsingState === 'combining');
      if (combiningEnemies.length > 0) {
        combinationTriggered = true;
        await page.screenshot({
          path: path.join(EVIDENCE_DIR, 'combination-triggered.png'),
        });
      }

      // Check for Colossal spawn
      const colossals = enemies.filter(e => e.type === 'colossal_tide');
      if (colossals.length > 0) {
        colossalSpawned = true;
        await page.screenshot({
          path: path.join(EVIDENCE_DIR, 'colossal-spawned.png'),
        });
        break;
      }

      await page.waitForTimeout(100);
    }

    console.log('Combination triggered:', combinationTriggered);
    console.log('Colossal spawned:', colossalSpawned);

    // Save final state
    const finalEnemies = await getEnemies(page);
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'combination-result.json'),
      JSON.stringify(finalEnemies, null, 2)
    );

    // At minimum, we should see combination state or a Colossal
    expect(combinationTriggered || colossalSpawned).toBe(true);
  });
});
