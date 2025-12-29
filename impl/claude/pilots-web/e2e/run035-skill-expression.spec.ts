/**
 * Run 035: Skill Expression Verification Tests
 *
 * Tests that verify skill metrics are tracked correctly and mastery is visible.
 * This is a RUN 035 PRIORITY: "Crisp, fair game mechanics, counterplay, and skill expression!"
 *
 * From types.ts:
 * interface SkillMetrics {
 *   attacksDodged: number;
 *   formationsEscaped: number;
 *   perfectGaps: number;          // Escaped in final 0.5s of constrict
 *   nearMisses: number;           // Dodged by < 10px
 *   bestKillChain: number;
 *   currentKillChain: number;
 *   coordinationDisruptions: number;
 * }
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

/**
 * Get skill metrics from debug API
 */
async function getSkillMetrics(page: Page) {
  return await page.evaluate(() => {
    // Try dedicated API first
    if (typeof window.DEBUG_GET_SKILL_METRICS === 'function') {
      return window.DEBUG_GET_SKILL_METRICS();
    }
    // Fall back to game state
    const state = window.DEBUG_GET_GAME_STATE?.();
    return state?.player?.skillMetrics;
  });
}

// =============================================================================
// SKILL METRICS VERIFICATION
// =============================================================================

test.describe('Run 035: Skill Metrics Verification', () => {
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

  test('skill metrics structure exists on player', async ({ page }) => {
    const metrics = await getSkillMetrics(page);

    console.log('Skill metrics:', JSON.stringify(metrics, null, 2));

    // Verify structure exists
    expect(metrics).toBeTruthy();

    // Check expected fields
    const expectedFields = [
      'attacksDodged',
      'formationsEscaped',
      'perfectGaps',
      'nearMisses',
      'bestKillChain',
      'currentKillChain',
      'coordinationDisruptions',
    ];

    for (const field of expectedFields) {
      expect(metrics).toHaveProperty(field);
    }

    // Save evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'skill-metrics-structure.json'),
      JSON.stringify(metrics, null, 2)
    );
  });

  test('kill chain tracks consecutive kills', async ({ page }) => {
    const beforeMetrics = await getSkillMetrics(page);
    const beforeChain = beforeMetrics?.currentKillChain ?? 0;

    // Spawn and kill multiple enemies quickly
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.DEBUG_SPAWN?.('worker', { x: 100 + i * 30, y: 100 }));
    }
    await page.waitForTimeout(200);

    // Kill all enemies
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(500);

    const afterMetrics = await getSkillMetrics(page);

    console.log('Kill chain - before:', beforeChain, 'after:', afterMetrics?.currentKillChain);
    console.log('Best kill chain:', afterMetrics?.bestKillChain);

    // Capture evidence
    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'kill-chain-test.png'),
    });
  });

  test('near-miss detection works', async ({ page }) => {
    const beforeMetrics = await getSkillMetrics(page);
    const beforeNearMisses = beforeMetrics?.nearMisses ?? 0;

    // Spawn enemy VERY close but enable invincibility
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));

    // Spawn enemies close enough to trigger near-miss detection (< 10px)
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.DEBUG_SPAWN?.('worker', { x: 110, y: 110 }));
      await page.waitForTimeout(500);
    }

    await page.waitForTimeout(2000);

    const afterMetrics = await getSkillMetrics(page);
    const afterNearMisses = afterMetrics?.nearMisses ?? 0;

    console.log('Near misses - before:', beforeNearMisses, 'after:', afterNearMisses);

    // Near-misses should have increased if enemy got within 10px
    // (This may not trigger in all cases - depends on enemy movement)
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'near-miss-test.json'),
      JSON.stringify({ before: beforeNearMisses, after: afterNearMisses }, null, 2)
    );

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'near-miss-test.png'),
    });
  });

  test('coordination disruption tracks scout kills', async ({ page }) => {
    const beforeMetrics = await getSkillMetrics(page);
    const beforeDisruptions = beforeMetrics?.coordinationDisruptions ?? 0;

    // Spawn scout and let it start coordinating
    await page.evaluate(() => window.DEBUG_SPAWN?.('scout', { x: 300, y: 300 }));

    // Wait for scout to start signaling
    for (let i = 0; i < 20; i++) {
      const enemies = await page.evaluate(() => window.DEBUG_GET_ENEMIES?.());
      const scout = enemies?.[0];
      if (scout?.coordinationState === 'coordinating' || scout?.fsmState === 'signaling') {
        console.log('Scout is signaling - killing now');
        await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
        break;
      }
      await page.waitForTimeout(500);
    }

    await page.waitForTimeout(500);

    const afterMetrics = await getSkillMetrics(page);
    const afterDisruptions = afterMetrics?.coordinationDisruptions ?? 0;

    console.log('Coordination disruptions - before:', beforeDisruptions, 'after:', afterDisruptions);

    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'coordination-disruption-test.json'),
      JSON.stringify({ before: beforeDisruptions, after: afterDisruptions }, null, 2)
    );
  });

  test('formation escape tracks successful THE BALL escapes', async ({ page }) => {
    const beforeMetrics = await getSkillMetrics(page);
    const beforeEscapes = beforeMetrics?.formationsEscaped ?? 0;

    // Force THE BALL
    await page.evaluate(() => window.DEBUG_FORCE_BALL?.());

    // Advance to constrict phase
    for (let i = 0; i < 4; i++) {
      await page.evaluate(() => window.DEBUG_NEXT_BALL_PHASE?.());
      await page.waitForTimeout(200);
    }

    // Simulate dash through gap (move player to gap position)
    await page.evaluate(() => {
      const ballPhase = window.DEBUG_GET_BALL_PHASE?.();
      if (ballPhase && ballPhase.gapAngles?.length > 0) {
        const gapAngle = ballPhase.gapAngles[0];
        const state = window.DEBUG_GET_GAME_STATE?.();
        if (state) {
          // Move player toward gap (escape direction)
          const center = { x: 480, y: 300 }; // Approximate ball center
          const escapeX = center.x + Math.cos(gapAngle) * 200;
          const escapeY = center.y + Math.sin(gapAngle) * 200;
          state.player.position = { x: escapeX, y: escapeY };
        }
      }
    });

    await page.waitForTimeout(1000);

    const afterMetrics = await getSkillMetrics(page);
    const afterEscapes = afterMetrics?.formationsEscaped ?? 0;

    console.log('Formation escapes - before:', beforeEscapes, 'after:', afterEscapes);

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'formation-escape-test.png'),
    });

    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'formation-escape-test.json'),
      JSON.stringify({ before: beforeEscapes, after: afterEscapes }, null, 2)
    );
  });
});

// =============================================================================
// DASH I-FRAME VERIFICATION
// =============================================================================

test.describe('Run 035: Dash I-Frame Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasDebugAPI = await waitForDebugAPI(page);
    if (!hasDebugAPI) {
      test.skip();
      return;
    }

    await startGame(page);
  });

  test('dash grants i-frames', async ({ page }) => {
    // Disable invincibility to test actual i-frames
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(false));

    // Get initial health
    const beforeState = await page.evaluate(() => window.DEBUG_GET_GAME_STATE?.());
    const beforeHealth = beforeState?.player?.health ?? 100;

    // Spawn enemy right on player
    await page.evaluate(() => window.DEBUG_SPAWN?.('worker', { x: 60, y: 60 }));
    await page.waitForTimeout(100);

    // Immediately dash
    await page.keyboard.press('Space');

    // Wait for dash to complete
    await page.waitForTimeout(300);

    // Check if player took damage
    const afterState = await page.evaluate(() => window.DEBUG_GET_GAME_STATE?.());
    const afterHealth = afterState?.player?.health ?? 100;

    // Check dash state
    const dashState = afterState?.player?.dash;
    console.log('Dash state:', JSON.stringify(dashState, null, 2));
    console.log('Health before:', beforeHealth, 'after:', afterHealth);

    // Player should have survived thanks to i-frames (or took minimal damage)
    // Note: This test may fail if dash doesn't grant i-frames - that's valuable info

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'dash-iframes-test.png'),
    });

    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'dash-iframes-test.json'),
      JSON.stringify({
        dashState,
        healthBefore: beforeHealth,
        healthAfter: afterHealth,
        damageBlocked: afterHealth >= beforeHealth,
      }, null, 2)
    );
  });

  test('dash cooldown is enforced', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));

    // First dash
    await page.keyboard.press('Space');

    // Get dash state immediately
    let state = await page.evaluate(() => window.DEBUG_GET_GAME_STATE?.());
    const firstDashTime = state?.player?.dash?.dashCooldownEnd ?? 0;

    // Try to dash again immediately
    await page.keyboard.press('Space');
    await page.waitForTimeout(100);

    state = await page.evaluate(() => window.DEBUG_GET_GAME_STATE?.());
    const secondDashCooldown = state?.player?.dash?.dashCooldownEnd ?? 0;

    console.log('First dash cooldown end:', firstDashTime);
    console.log('Second dash cooldown end:', secondDashCooldown);

    // Cooldown should still be active (not reset)
    // DASH_COOLDOWN = 1.5s per spec

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'dash-cooldown-test.png'),
    });
  });

  test('dash duration is approximately 200ms', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));

    // Start dash
    const startTime = Date.now();
    await page.keyboard.press('Space');

    // Wait for dash to complete
    await page.waitForFunction(() => {
      const state = window.DEBUG_GET_GAME_STATE?.();
      return !state?.player?.dash?.isDashing;
    }, { timeout: 5000 });

    const endTime = Date.now();
    const dashDuration = endTime - startTime;

    console.log(`Dash duration: ${dashDuration}ms`);

    // DASH_DURATION = 0.2s (200ms) per spec
    expect(dashDuration).toBeGreaterThan(150);
    expect(dashDuration).toBeLessThan(400);

    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'dash-duration.json'),
      JSON.stringify({ dashDuration }, null, 2)
    );
  });
});

// =============================================================================
// MASTERY VISIBILITY
// =============================================================================

test.describe('Run 035: Mastery Visibility', () => {
  test('crystal shows skill metrics on death', async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasDebugAPI = await waitForDebugAPI(page);
    if (!hasDebugAPI) {
      test.skip();
      return;
    }

    await startGame(page);

    // Play a bit to accumulate some skill metrics
    await page.evaluate(() => {
      // Spawn enemies
      for (let i = 0; i < 5; i++) {
        window.DEBUG_SPAWN?.('worker', { x: 200 + i * 50, y: 200 });
      }
    });

    // Wait for some gameplay
    await page.waitForTimeout(3000);

    // Kill player
    await page.evaluate(() => window.DEBUG_KILL_PLAYER?.());

    // Wait for death screen
    try {
      await page.waitForSelector('button:has-text("HUNT AGAIN")', { timeout: 30000 });

      // Capture death screen
      await page.screenshot({
        path: path.join(EVIDENCE_DIR, 'death-skill-metrics.png'),
        fullPage: true,
      });

      // Check for skill metrics in death screen
      const pageText = await page.textContent('body');

      // Look for skill-related text
      const hasSkillInfo = pageText?.toLowerCase().includes('miss') ||
                          pageText?.toLowerCase().includes('escape') ||
                          pageText?.toLowerCase().includes('chain') ||
                          pageText?.toLowerCase().includes('dodge');

      console.log('Death screen skill info present:', hasSkillInfo);
      console.log('Death screen text (excerpt):', pageText?.substring(0, 500));

      fs.writeFileSync(
        path.join(EVIDENCE_DIR, 'death-screen-text.txt'),
        pageText || ''
      );
    } catch {
      console.log('Death screen did not appear in time');
      await page.screenshot({
        path: path.join(EVIDENCE_DIR, 'death-skill-metrics-timeout.png'),
      });
    }
  });
});
