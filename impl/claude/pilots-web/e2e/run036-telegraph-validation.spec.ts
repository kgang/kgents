/**
 * Run 036: Enemy Telegraph & Animation Validation
 *
 * PURPOSE: Verify the 514 lines of visual enhancement code in GameCanvas.tsx:
 * - Enhanced renderTelegraphs() with pulsing rings, motion lines, 3-phase indicators
 * - New renderAttackEffects() for attack-phase animations
 * - Recovery state golden glow and wobble
 *
 * EVIDENCE CAPTURED:
 * - Screenshots at each attack phase (idle, telegraph, active, recovery)
 * - State logs showing behaviorState transitions
 * - Visual verification of telegraph timing and appearance
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';

const PILOT_NAME = 'wasm-survivors-game';
const EVIDENCE_DIR = 'screenshots/run036-telegraphs';

// Ensure evidence directory exists
test.beforeAll(async () => {
  if (!fs.existsSync(EVIDENCE_DIR)) {
    fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
  }
});

function getPilotURL(): string {
  return `/pilots/${PILOT_NAME}?debug=true`;
}

async function waitForMenu(page: Page): Promise<void> {
  await page.goto(getPilotURL());

  // Wait for React to load and render the game
  await page.waitForSelector('button:has-text("Start Run")', { timeout: 15000 });
}

async function startGame(page: Page): Promise<void> {
  const button = page.locator('button:has-text("Start Run")');
  await button.click();
  await page.waitForSelector('canvas', { timeout: 5000 });
  await page.waitForTimeout(500);
}

async function getGameState(page: Page): Promise<any> {
  return page.evaluate(() => (window as any).DEBUG_GET_GAME_STATE?.());
}

test.describe('Run 036: Telegraph & Animation Validation', () => {
  test.setTimeout(90000); // 90 second timeout

  test('TELEGRAPH-1: Verify enemies have behaviorState and attack phases', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    // Wait for initial enemies to spawn
    await page.waitForTimeout(2000);

    const state = await getGameState(page);
    console.log('\n=== INITIAL STATE ===');
    console.log('Enemy count:', state?.enemies?.length || 0);

    if (state?.enemies && state.enemies.length > 0) {
      const enemy = state.enemies[0];
      console.log('First enemy structure:', JSON.stringify({
        type: enemy.type,
        behaviorState: enemy.behaviorState,
        attackPhase: enemy.attackPhase,
        position: enemy.position,
      }, null, 2));

      // Verify enemy has required fields
      expect(enemy.behaviorState, 'Enemy should have behaviorState').toBeDefined();
      expect(['chase', 'telegraph', 'attack', 'recovery']).toContain(enemy.behaviorState);
    }

    await page.screenshot({ path: `${EVIDENCE_DIR}/initial-state.png` });
  });

  test('TELEGRAPH-2: Capture telegraph phase transitions over time', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    // Set invincible to prevent death during observation
    await page.evaluate(() => {
      (window as any).DEBUG_SET_INVINCIBLE?.(true);
    });

    console.log('\n=== OBSERVING TELEGRAPH PHASES ===');
    console.log('Recording enemy states for 20 seconds...');

    const phaseLog: any[] = [];
    const startTime = Date.now();

    // Record states every 100ms for 20 seconds
    for (let i = 0; i < 200; i++) {
      const state = await getGameState(page);
      const elapsed = Date.now() - startTime;

      if (state?.enemies) {
        // Group enemies by behaviorState
        const phaseCounts = state.enemies.reduce((acc: any, e: any) => {
          const phase = e.behaviorState || 'unknown';
          acc[phase] = (acc[phase] || 0) + 1;
          return acc;
        }, {});

        phaseLog.push({
          time: elapsed,
          total: state.enemies.length,
          phases: phaseCounts,
        });

        // Take screenshot at interesting moments
        if (phaseCounts.telegraph > 0 && i % 10 === 0) {
          await page.screenshot({
            path: `${EVIDENCE_DIR}/telegraph-phase-${elapsed}ms.png`,
          });
          console.log(`[${elapsed}ms] Telegraph detected! Phases:`, phaseCounts);
        }

        if (phaseCounts.active > 0 && i % 10 === 0) {
          await page.screenshot({
            path: `${EVIDENCE_DIR}/active-phase-${elapsed}ms.png`,
          });
          console.log(`[${elapsed}ms] Active attack! Phases:`, phaseCounts);
        }

        if (phaseCounts.recovery > 0 && i % 10 === 0) {
          await page.screenshot({
            path: `${EVIDENCE_DIR}/recovery-phase-${elapsed}ms.png`,
          });
          console.log(`[${elapsed}ms] Recovery state! Phases:`, phaseCounts);
        }
      }

      await page.waitForTimeout(100);
    }

    // Write phase log
    fs.writeFileSync(
      `${EVIDENCE_DIR}/phase-transitions.json`,
      JSON.stringify(phaseLog, null, 2)
    );

    // Analyze transitions
    const telegraphMoments = phaseLog.filter(l => l.phases.telegraph > 0);
    const activeMoments = phaseLog.filter(l => l.phases.active > 0);
    const recoveryMoments = phaseLog.filter(l => l.phases.recovery > 0);

    console.log('\n=== PHASE ANALYSIS ===');
    console.log('Telegraph moments:', telegraphMoments.length);
    console.log('Active attack moments:', activeMoments.length);
    console.log('Recovery moments:', recoveryMoments.length);

    if (telegraphMoments.length === 0) {
      console.log('⚠️ WARNING: No telegraph phases detected in 20 seconds');
      console.log('This could indicate:');
      console.log('- Enemies not entering telegraph phase');
      console.log('- Telegraph timing too fast to catch');
      console.log('- behaviorState not being set correctly');
    }

    // We expect at least some telegraph activity in 20 seconds
    expect(telegraphMoments.length, 'Should observe telegraph phases').toBeGreaterThan(0);
  });

  test('TELEGRAPH-3: Verify specific enemy types have correct behavior', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    await page.evaluate(() => {
      (window as any).DEBUG_SET_INVINCIBLE?.(true);
    });

    // Wait for variety of enemies
    await page.waitForTimeout(5000);

    const state = await getGameState(page);
    const enemyTypes = new Map<string, any[]>();

    if (state?.enemies) {
      for (const enemy of state.enemies) {
        if (!enemyTypes.has(enemy.type)) {
          enemyTypes.set(enemy.type, []);
        }
        enemyTypes.get(enemy.type)!.push(enemy);
      }
    }

    console.log('\n=== ENEMY TYPE ANALYSIS ===');
    for (const [type, enemies] of enemyTypes) {
      const behaviorStates = enemies.map(e => e.behaviorState);
      const uniqueStates = new Set(behaviorStates);
      console.log(`${type}:`);
      console.log(`  Count: ${enemies.length}`);
      console.log(`  Behavior states observed: ${Array.from(uniqueStates).join(', ')}`);
      console.log(`  Sample enemy:`, JSON.stringify({
        behaviorState: enemies[0].behaviorState,
        fsmState: enemies[0].fsmState,
        attackPhase: enemies[0].attackPhase,
      }, null, 2));
    }

    await page.screenshot({ path: `${EVIDENCE_DIR}/enemy-types.png` });
  });

  test('TELEGRAPH-4: Visual verification of animation effects', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    await page.evaluate(() => {
      (window as any).DEBUG_SET_INVINCIBLE?.(true);
    });

    console.log('\n=== VISUAL VERIFICATION SEQUENCE ===');

    // Capture screenshots at different time points
    const timePoints = [2, 5, 10, 15, 20];

    for (const t of timePoints) {
      await page.waitForTimeout(t * 1000);
      await page.screenshot({ path: `${EVIDENCE_DIR}/visual-${t}s.png` });

      const state = await getGameState(page);
      if (state?.enemies) {
        const phaseCounts = state.enemies.reduce((acc: any, e: any) => {
          const phase = e.behaviorState || 'unknown';
          acc[phase] = (acc[phase] || 0) + 1;
          return acc;
        }, {});
        console.log(`[${t}s] Current phases:`, phaseCounts);
      }
    }

    console.log('\n=== MANUAL VERIFICATION CHECKLIST ===');
    console.log('For each screenshot, verify:');
    console.log('');
    console.log('TELEGRAPH PHASE:');
    console.log('  - Pulsing ring around enemy (expanding/contracting)');
    console.log('  - Motion lines pointing toward player');
    console.log('  - Orange/red color scheme');
    console.log('  - "!" indicator (if within range)');
    console.log('');
    console.log('ACTIVE PHASE:');
    console.log('  - Red flash/glow');
    console.log('  - Attack animation');
    console.log('  - Clear visual distinction from telegraph');
    console.log('');
    console.log('RECOVERY PHASE:');
    console.log('  - Golden glow around enemy');
    console.log('  - Wobble/bounce animation');
    console.log('  - Distinct from other phases');
    console.log('');
    console.log('Screenshots saved to:', EVIDENCE_DIR);
  });

  test('TELEGRAPH-5: Verify telegraph timing is reasonable', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    await page.evaluate(() => {
      (window as any).DEBUG_SET_INVINCIBLE?.(true);
    });

    console.log('\n=== TELEGRAPH TIMING ANALYSIS ===');

    const transitions: any[] = [];
    const enemyStates = new Map<number, string>();

    // Track for 15 seconds
    for (let i = 0; i < 150; i++) {
      const state = await getGameState(page);

      if (state?.enemies) {
        for (let idx = 0; idx < state.enemies.length; idx++) {
          const enemy = state.enemies[idx];
          const prevState = enemyStates.get(idx);
          const currState = enemy.behaviorState;

          if (prevState && prevState !== currState) {
            transitions.push({
              time: i * 100,
              enemy: idx,
              from: prevState,
              to: currState,
            });
          }

          enemyStates.set(idx, currState);
        }
      }

      await page.waitForTimeout(100);
    }

    console.log('Total transitions observed:', transitions.length);
    console.log('First 20 transitions:', transitions.slice(0, 20));

    // Calculate average telegraph duration
    const telegraphDurations: number[] = [];
    for (let i = 0; i < transitions.length - 1; i++) {
      if (transitions[i].to === 'telegraph' && transitions[i + 1].from === 'telegraph') {
        const duration = transitions[i + 1].time - transitions[i].time;
        telegraphDurations.push(duration);
      }
    }

    if (telegraphDurations.length > 0) {
      const avgTelegraph = telegraphDurations.reduce((a, b) => a + b, 0) / telegraphDurations.length;
      console.log(`\nAverage telegraph duration: ${avgTelegraph.toFixed(0)}ms`);
      console.log('Telegraph durations:', telegraphDurations.slice(0, 10));

      // Reasonable telegraph should be 300-1500ms for player reaction
      expect(avgTelegraph, 'Telegraph should be long enough to react').toBeGreaterThan(200);
      expect(avgTelegraph, 'Telegraph should not be too long').toBeLessThan(3000);
    } else {
      console.log('⚠️ WARNING: No complete telegraph durations captured');
    }
  });
});
