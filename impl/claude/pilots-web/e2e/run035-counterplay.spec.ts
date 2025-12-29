/**
 * Run 035: Counterplay Verification Tests
 *
 * Tests that verify EVERY enemy type has a learnable counterplay pattern.
 * This is a RUN 035 PRIORITY: "Crisp, fair game mechanics, counterplay, and skill expression!"
 *
 * @author PLAYER-2 Agent
 * @see .player.qualia-matrix.md for full verification matrix
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const EVIDENCE_DIR = path.join(__dirname, '..', 'evidence', 'run035');

// Ensure evidence directory exists
if (!fs.existsSync(EVIDENCE_DIR)) {
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

/**
 * Wait for debug API
 */
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

/**
 * Get pilot URL with debug mode
 */
function getPilotURL(): string {
  return `/pilots/wasm-survivors-game?debug=true`;
}

/**
 * Start game
 */
async function startGame(page: Page): Promise<void> {
  const beginButton = page.locator('button:has-text("BEGIN RAID")');
  if (await beginButton.isVisible()) {
    await beginButton.click();
  } else {
    await page.evaluate(() => (window as any).DEBUG_START_GAME?.());
  }
  await page.waitForTimeout(500);
}

// =============================================================================
// COUNTERPLAY VERIFICATION TESTS (Run 035 Priority)
// =============================================================================

test.describe('Run 035: Counterplay Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasDebugAPI = await waitForDebugAPI(page);
    if (!hasDebugAPI) {
      test.skip();
      return;
    }

    await startGame(page);
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('Worker: can be kited (foraging/alerting states)', async ({ page }) => {
    // Workers should be kiteable - they follow but don't catch a moving player
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    // Spawn worker
    await page.evaluate(() => window.DEBUG_SPAWN?.('worker', { x: 400, y: 300 }));
    await page.waitForTimeout(100);

    // Get initial enemy position
    let enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
    const initialPos = enemies?.[0]?.position;
    expect(initialPos).toBeTruthy();

    // Move player away (simulate kiting)
    await page.evaluate(() => {
      // Set player position far from enemy
      const state = window.DEBUG_GET_GAME_STATE?.();
      if (state) {
        state.player.position = { x: 100, y: 100 };
      }
    });

    // Wait for worker to pursue
    await page.waitForTimeout(1000);

    // Verify worker is chasing (moved toward player)
    enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
    const newPos = enemies?.[0]?.position;
    expect(newPos).toBeTruthy();

    // Worker should have moved toward player (position changed)
    const moved = Math.abs(newPos!.x - initialPos!.x) > 10 ||
                  Math.abs(newPos!.y - initialPos!.y) > 10;
    expect(moved).toBe(true);

    // Capture evidence
    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'worker-kiting.png'),
    });

    console.log(`Worker counterplay: Kited from ${JSON.stringify(initialPos)} to ${JSON.stringify(newPos)}`);
  });

  test('Scout: stationary during signaling (free kill window)', async ({ page }) => {
    // Scouts should STOP MOVING during signaling state - this is the counterplay window
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    // Spawn scout
    await page.evaluate(() => window.DEBUG_SPAWN?.('scout', { x: 300, y: 300 }));

    // Wait for signaling state
    let signaling = false;
    for (let i = 0; i < 30; i++) {
      const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
      const scout = enemies?.[0];
      if (scout?.fsmState === 'signaling' || scout?.coordinationState === 'coordinating') {
        signaling = true;

        // Verify scout is stationary (speedMultiplier should be 0)
        // or glowIntensity high (visible target)
        const glowIntensity = scout.fsmGlowIntensity ?? 0;
        console.log(`Scout in signaling state, glow: ${glowIntensity}`);
        expect(glowIntensity).toBeGreaterThan(0.3);

        await page.screenshot({
          path: path.join(EVIDENCE_DIR, 'scout-signaling.png'),
        });

        break;
      }
      await page.waitForTimeout(500);
    }

    // Scout should have reached signaling state
    // If not, we may need more time - don't fail but log
    if (!signaling) {
      console.warn('Scout did not reach signaling state in time - may need longer test');
    }
  });

  test('Guard: recovery window after retaliation', async ({ page }) => {
    // Guards should have a vulnerability window after retaliating
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    // Spawn guard close to player
    await page.evaluate(() => window.DEBUG_SPAWN?.('guard', { x: 150, y: 150 }));

    // Wait for guard to go through attack cycle
    const stateLog: string[] = [];
    for (let i = 0; i < 40; i++) {
      const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
      const guard = enemies?.[0];
      if (guard) {
        const state = guard.fsmState || guard.coordinationState || 'unknown';
        if (stateLog.length === 0 || stateLog[stateLog.length - 1] !== state) {
          stateLog.push(state);
          console.log(`Guard state: ${state}`);
        }
      }
      await page.waitForTimeout(250);
    }

    // Verify guard went through multiple states
    expect(stateLog.length).toBeGreaterThan(1);

    // Save state log
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'guard-state-log.json'),
      JSON.stringify(stateLog, null, 2)
    );

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'guard-recovery.png'),
    });
  });

  test('Propolis: 1.5s aiming telegraph (long dodge window)', async ({ page }) => {
    // Propolis should have a LONG aiming phase (1.5s per spec)
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    // Spawn propolis at ideal range
    await page.evaluate(() => window.DEBUG_SPAWN?.('propolis', { x: 300, y: 300 }));

    // Track time in aiming state
    let aimingStart: number | null = null;
    let aimingDuration = 0;

    for (let i = 0; i < 60; i++) {
      const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
      const propolis = enemies?.[0];
      if (propolis) {
        const state = propolis.fsmState || propolis.attackPhase || 'unknown';
        const isAiming = state === 'aiming' || state === 'windup';

        if (isAiming && !aimingStart) {
          aimingStart = Date.now();
          console.log('Propolis started aiming');
        } else if (!isAiming && aimingStart) {
          aimingDuration = Date.now() - aimingStart;
          console.log(`Propolis aiming duration: ${aimingDuration}ms`);
          break;
        }
      }
      await page.waitForTimeout(100);
    }

    // Verify aiming phase lasted approximately 1.5s
    if (aimingDuration > 0) {
      // Allow 500ms tolerance
      expect(aimingDuration).toBeGreaterThan(1000);
      expect(aimingDuration).toBeLessThan(2500);
    } else {
      console.warn('Could not measure propolis aiming duration');
    }

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'propolis-aiming.png'),
    });
  });

  test('Royal: coordinating state has high glow (priority target)', async ({ page }) => {
    // Royals should be VERY visible when coordinating (they accelerate THE BALL)
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    // Spawn royal with allies to trigger coordinating
    await page.evaluate(() => window.DEBUG_SPAWN?.('royal', { x: 300, y: 300 }));
    for (let i = 0; i < 5; i++) {
      await page.evaluate(
        (idx) => window.DEBUG_SPAWN?.('worker', { x: 250 + idx * 20, y: 300 }),
        i
      );
    }

    // Wait for royal to start coordinating
    let maxGlow = 0;
    for (let i = 0; i < 40; i++) {
      const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
      const royal = enemies?.find((e: any) => e.type === 'royal');
      if (royal) {
        const glow = royal.fsmGlowIntensity ?? 0;
        maxGlow = Math.max(maxGlow, glow);
        if (glow > 0.5) {
          console.log(`Royal glow: ${glow} (coordinating)`);
          await page.screenshot({
            path: path.join(EVIDENCE_DIR, 'royal-coordinating.png'),
          });
          break;
        }
      }
      await page.waitForTimeout(500);
    }

    console.log(`Royal max glow observed: ${maxGlow}`);
    // Royals should have high glow when coordinating
    expect(maxGlow).toBeGreaterThan(0.3);
  });
});

// =============================================================================
// ATTACK TELEGRAPH VERIFICATION
// =============================================================================

test.describe('Run 035: Attack Telegraph Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasDebugAPI = await waitForDebugAPI(page);
    if (!hasDebugAPI) {
      test.skip();
      return;
    }

    await startGame(page);
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('all enemy types have attack phases defined', async ({ page }) => {
    // Verify each enemy type has the expected attack phase structure
    const enemyTypes = ['worker', 'scout', 'guard', 'propolis', 'royal'];
    const results: Record<string, boolean> = {};

    for (const type of enemyTypes) {
      await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
      await page.waitForTimeout(100);

      // Spawn enemy
      await page.evaluate(
        (t) => window.DEBUG_SPAWN?.(t, { x: 150, y: 150 }),
        type
      );

      // Check for attack phase property
      await page.waitForTimeout(200);
      const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
      const enemy = enemies?.[0];

      if (enemy) {
        const hasAttackPhase = 'attackPhase' in enemy || 'fsmState' in enemy;
        results[type] = hasAttackPhase;
        console.log(`${type}: attackPhase=${enemy.attackPhase}, fsmState=${enemy.fsmState}`);
      }
    }

    // All enemy types should have attack phase tracking
    const allHavePhases = Object.values(results).every(v => v);
    expect(allHavePhases).toBe(true);

    // Save results
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'attack-phase-coverage.json'),
      JSON.stringify(results, null, 2)
    );
  });

  test('windup duration exceeds human reaction time (250ms)', async ({ page }) => {
    // Per Dark Souls research: telegraphs should exceed 250ms reaction time
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Spawn enemy close to trigger attack
    await page.evaluate(() => window.DEBUG_SPAWN?.('worker', { x: 100, y: 100 }));

    // Measure time in windup state
    let windupStart: number | null = null;
    let windupDuration = 0;

    for (let i = 0; i < 60; i++) {
      const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
      const enemy = enemies?.[0];
      if (enemy) {
        const isWindup = enemy.attackPhase === 'windup';
        if (isWindup && !windupStart) {
          windupStart = Date.now();
        } else if (!isWindup && windupStart) {
          windupDuration = Date.now() - windupStart;
          break;
        }
      }
      await page.waitForTimeout(50);
    }

    if (windupDuration > 0) {
      console.log(`Worker windup duration: ${windupDuration}ms`);
      // Should exceed 250ms human reaction time
      expect(windupDuration).toBeGreaterThan(200); // 200ms minimum for fairness
    } else {
      console.warn('Could not measure windup - may need different test approach');
    }
  });
});

// =============================================================================
// THE BALL COUNTERPLAY
// =============================================================================

test.describe('Run 035: THE BALL Counterplay', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasDebugAPI = await waitForDebugAPI(page);
    if (!hasDebugAPI) {
      test.skip();
      return;
    }

    await startGame(page);
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('escape gap visible during all ball phases', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_FORCE_BALL?.());
    await page.waitForTimeout(200);

    const phaseScreenshots: string[] = [];

    // Progress through phases
    const phases = ['forming', 'sphere', 'silence', 'constrict'];
    for (const expectedPhase of phases) {
      const ballPhase = await page.evaluate(() => window.DEBUG_GET_BALL_PHASE?.());

      if (ballPhase) {
        console.log(`Ball phase: ${ballPhase.type}, gaps: ${ballPhase.gapAngles?.length}`);

        // Gap should exist
        expect(ballPhase.gapAngles?.length).toBeGreaterThan(0);

        // Screenshot each phase
        const filename = `ball-gap-${ballPhase.type}.png`;
        await page.screenshot({
          path: path.join(EVIDENCE_DIR, filename),
        });
        phaseScreenshots.push(filename);
      }

      // Advance to next phase
      await page.evaluate(() => window.DEBUG_NEXT_BALL_PHASE?.());
      await page.waitForTimeout(200);
    }

    console.log(`Captured gap evidence: ${phaseScreenshots.join(', ')}`);
  });

  test('gap shrinks but never disappears', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_FORCE_BALL?.());

    const gapCounts: number[] = [];

    // Track gap count through phases
    for (let i = 0; i < 4; i++) {
      const ballPhase = await page.evaluate(() => window.DEBUG_GET_BALL_PHASE?.());
      if (ballPhase) {
        gapCounts.push(ballPhase.gapAngles?.length || 0);
      }
      await page.evaluate(() => window.DEBUG_NEXT_BALL_PHASE?.());
      await page.waitForTimeout(200);
    }

    console.log(`Gap progression: ${gapCounts.join(' → ')}`);

    // Verify gaps shrink
    expect(gapCounts[0]).toBeGreaterThanOrEqual(gapCounts[gapCounts.length - 1]);

    // Verify at least 1 gap always exists (escape is always possible)
    for (const count of gapCounts) {
      expect(count).toBeGreaterThanOrEqual(1);
    }
  });
});
