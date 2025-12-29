/**
 * Animation & Effects Verification Framework
 *
 * Run 034 ADDENDUM: Tools for PLAYER to verify animations, effects, and
 * interactive gameplay elements work correctly.
 *
 * This framework captures VIDEO, analyzes state transitions, and provides
 * frame-by-frame evidence for certification.
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

// Use environment variable for port, default to 3012
const PORT = process.env.GAME_PORT || '3012';
const GAME_URL = `http://localhost:${PORT}/pilots/wasm-survivors-game?debug=true`;
const EVIDENCE_DIR = 'screenshots/animation-evidence';

// Ensure evidence directory exists
test.beforeAll(async () => {
  if (!fs.existsSync(EVIDENCE_DIR)) {
    fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
  }
});

// Wait for game menu to load
async function waitForMenu(page: Page): Promise<void> {
  await page.goto(GAME_URL);
  await page.waitForSelector('button:has-text("BEGIN RAID")', { timeout: 10000 });
}

// Start game and wait for canvas
async function startGame(page: Page): Promise<void> {
  const button = page.locator('button:has-text("BEGIN RAID")');
  await button.click();
  await page.waitForSelector('canvas', { timeout: 5000 });
  await page.waitForTimeout(500); // Let initial enemies spawn
}

// Get game state via debug API
async function getGameState(page: Page): Promise<any> {
  return page.evaluate(() => (window as any).DEBUG_GET_GAME_STATE?.());
}

// Record state snapshots over time
async function recordStateTransitions(
  page: Page,
  durationMs: number,
  intervalMs: number = 16
): Promise<any[]> {
  const states: any[] = [];
  const startTime = Date.now();

  while (Date.now() - startTime < durationMs) {
    const state = await getGameState(page);
    if (state) {
      states.push({
        timestamp: Date.now() - startTime,
        player: {
          position: state.player?.position,
          velocity: state.player?.velocity,
          health: state.player?.health,
          invincible: state.player?.invincible,
          dash: state.player?.dash,
        },
        phase: state.phase,
        enemyCount: state.enemies?.length,
        ballPhase: state.ballPhase?.type,
      });
    }
    await page.waitForTimeout(intervalMs);
  }

  return states;
}

test.describe('Animation & Effects Verification', () => {
  test.describe.configure({ mode: 'serial' }); // Run tests in order
  test.setTimeout(120000); // 2 minute timeout

  test('VERIFY-1: Dash ghost trail renders during dash', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    // Pre-dash screenshot
    await page.screenshot({ path: `${EVIDENCE_DIR}/dash-1-pre.png` });

    // Move right to establish direction
    await page.keyboard.down('d');
    await page.waitForTimeout(200);

    // Capture state before dash
    const preDashState = await getGameState(page);
    console.log('Pre-dash state:', JSON.stringify(preDashState?.player?.dash, null, 2));

    // Trigger dash and capture IMMEDIATELY (during dash)
    await page.keyboard.down('Shift');
    await page.waitForTimeout(50); // 50ms into dash (should be mid-dash)

    // Capture mid-dash screenshot
    await page.screenshot({ path: `${EVIDENCE_DIR}/dash-2-mid.png` });

    // Capture state during dash
    const midDashState = await getGameState(page);
    console.log('Mid-dash state:', JSON.stringify(midDashState?.player?.dash, null, 2));

    // Release and capture end
    await page.keyboard.up('Shift');
    await page.keyboard.up('d');
    await page.waitForTimeout(100);
    await page.screenshot({ path: `${EVIDENCE_DIR}/dash-3-post.png` });

    const postDashState = await getGameState(page);
    console.log('Post-dash state:', JSON.stringify(postDashState?.player?.dash, null, 2));

    // VERIFICATION CHECKLIST:
    console.log('\n=== DASH VERIFICATION ===');
    console.log('1. Pre-dash isDashing:', preDashState?.player?.dash?.isDashing);
    console.log('2. Mid-dash isDashing:', midDashState?.player?.dash?.isDashing);
    console.log('3. Mid-dash iFramesActive:', midDashState?.player?.dash?.iFramesActive);
    console.log('4. Post-dash isDashing:', postDashState?.player?.dash?.isDashing);

    // Test assertions
    expect(midDashState?.player?.dash?.isDashing || preDashState?.player?.dash?.isDashing,
      'Dash should have been active at some point'
    ).toBe(true);

    console.log('\nScreenshots saved to:', EVIDENCE_DIR);
    console.log('MANUAL VERIFICATION REQUIRED:');
    console.log('- Check dash-2-mid.png for ghost trail (semi-transparent afterimages)');
    console.log('- Compare position change between dash-1-pre.png and dash-3-post.png');
  });

  test('VERIFY-2: Sprite rotation follows movement direction', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    const directions = [
      { key: 'd', name: 'right', expectedAngle: 0 },
      { key: 'w', name: 'up', expectedAngle: -Math.PI / 2 },
      { key: 'a', name: 'left', expectedAngle: Math.PI },
      { key: 's', name: 'down', expectedAngle: Math.PI / 2 },
    ];

    for (const dir of directions) {
      // Move in direction for 500ms
      await page.keyboard.down(dir.key);
      await page.waitForTimeout(500);

      // Get velocity to calculate expected rotation
      const state = await getGameState(page);
      const vx = state?.player?.velocity?.x || 0;
      const vy = state?.player?.velocity?.y || 0;
      const actualAngle = Math.atan2(vy, vx);

      // Screenshot
      await page.screenshot({
        path: `${EVIDENCE_DIR}/rotation-${dir.name}.png`,
      });

      console.log(`Direction ${dir.name}: velocity=(${vx.toFixed(1)}, ${vy.toFixed(1)}), angle=${(actualAngle * 180 / Math.PI).toFixed(1)}°`);

      await page.keyboard.up(dir.key);
      await page.waitForTimeout(100);
    }

    console.log('\n=== ROTATION VERIFICATION ===');
    console.log('MANUAL VERIFICATION REQUIRED:');
    console.log('- Check rotation-*.png files');
    console.log('- Hornet sprite should VISIBLY rotate toward movement direction');
    console.log('- Current code uses 0.3x multiplier — may be too subtle!');
    console.log('- If rotation not visible, this is a BUG (or bad design choice)');
  });

  test('VERIFY-3: Enemy attack telegraphs are visible', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    // Wait for enemies to spawn
    await page.waitForTimeout(2000);

    // Record state over 10 seconds to catch attack phases
    console.log('Recording enemy states for 10 seconds...');
    const states = await recordStateTransitions(page, 10000, 100);

    // Look for enemies in non-idle attack phases
    const attackingEnemies = new Set<string>();
    const attackPhases: any[] = [];

    for (const state of states) {
      const fullState = await page.evaluate(() => (window as any).DEBUG_GET_GAME_STATE?.());
      if (fullState?.enemies) {
        for (const enemy of fullState.enemies) {
          if (enemy.attackPhase !== 'idle') {
            attackingEnemies.add(enemy.type);
            attackPhases.push({
              timestamp: state.timestamp,
              type: enemy.type,
              attackPhase: enemy.attackPhase,
              fsmState: enemy.fsmState,
            });
          }
        }
      }
    }

    console.log('\n=== ATTACK TELEGRAPH VERIFICATION ===');
    console.log('Enemy types that entered attack phases:', Array.from(attackingEnemies));
    console.log('Attack phase transitions:', attackPhases.slice(0, 10)); // First 10

    // Capture final state
    await page.screenshot({ path: `${EVIDENCE_DIR}/telegraphs-final.png` });

    if (attackPhases.length === 0) {
      console.log('WARNING: No attack phases detected in 10 seconds');
      console.log('This could mean:');
      console.log('- Enemies are not attacking');
      console.log('- Attack system is broken');
      console.log('- Need longer observation time');
    }

    console.log('\nMANUAL VERIFICATION REQUIRED:');
    console.log('- Watch for orange "!" indicators above enemies');
    console.log('- Watch for red flash during active attack');
    console.log('- Watch for blue/grey recovery state');
  });

  test('VERIFY-4: Player takes damage from enemy contact', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    // Get initial health
    let initialState = await getGameState(page);
    const initialHealth = initialState?.player?.health || 100;
    console.log('Initial health:', initialHealth);

    // Stand still and let enemies hit us
    console.log('Standing still for 15 seconds to verify damage...');
    await page.screenshot({ path: `${EVIDENCE_DIR}/damage-1-start.png` });

    // Record health over time
    const healthLog: { time: number; health: number }[] = [];
    const startTime = Date.now();

    for (let i = 0; i < 150; i++) { // 15 seconds @ 100ms intervals
      await page.waitForTimeout(100);
      const state = await getGameState(page);
      const health = state?.player?.health || 0;
      healthLog.push({ time: Date.now() - startTime, health });

      if (health <= 0) {
        console.log('Player died at', Date.now() - startTime, 'ms');
        break;
      }
    }

    await page.screenshot({ path: `${EVIDENCE_DIR}/damage-2-end.png` });

    const finalHealth = healthLog[healthLog.length - 1]?.health || 0;
    const damageEvents = healthLog.filter((h, i) =>
      i > 0 && h.health < healthLog[i - 1].health
    );

    console.log('\n=== DAMAGE VERIFICATION ===');
    console.log('Initial health:', initialHealth);
    console.log('Final health:', finalHealth);
    console.log('Damage events:', damageEvents.length);
    console.log('Health transitions:', damageEvents.slice(0, 5));

    if (damageEvents.length === 0) {
      console.log('⚠️ WARNING: NO DAMAGE TAKEN IN 15 SECONDS');
      console.log('This is likely a CRITICAL BUG:');
      console.log('- Collision detection may be broken');
      console.log('- Enemy contact may not deal damage');
      console.log('- Player may be stuck in invincible state');
    } else {
      console.log('✓ Damage system appears to work');
      console.log(`Player took ${initialHealth - finalHealth} total damage`);
    }

    expect(damageEvents.length, 'Player should take damage when standing still').toBeGreaterThan(0);
  });

  test('VERIFY-5: THE BALL gap indicator is visible and usable', async ({ page }) => {
    await waitForMenu(page);
    await startGame(page);

    // Use debug API to force BALL formation
    console.log('Forcing BALL formation via debug API...');

    await page.evaluate(() => {
      (window as any).DEBUG_SET_INVINCIBLE?.(true); // Don't die during test
    });

    // Let some enemies spawn first
    await page.waitForTimeout(3000);

    // Force BALL
    const ballPhase = await page.evaluate(() => {
      return (window as any).DEBUG_FORCE_BALL?.();
    });

    console.log('Initial ball phase:', ballPhase);
    await page.screenshot({ path: `${EVIDENCE_DIR}/ball-1-forming.png` });

    // Advance through phases
    const phases = ['sphere', 'silence', 'constrict'];
    for (const phaseName of phases) {
      await page.waitForTimeout(1000);
      const nextPhase = await page.evaluate(() => {
        return (window as any).DEBUG_NEXT_BALL_PHASE?.();
      });
      console.log(`Advanced to: ${nextPhase?.type}`);
      await page.screenshot({ path: `${EVIDENCE_DIR}/ball-2-${nextPhase?.type || phaseName}.png` });
    }

    console.log('\n=== BALL GAP VERIFICATION ===');
    console.log('MANUAL VERIFICATION REQUIRED:');
    console.log('- Check ball-1-forming.png for initial formation');
    console.log('- Check ball-2-sphere.png for visible GREEN gap arc');
    console.log('- Check ball-2-silence.png for "THE SILENCE" label');
    console.log('- Check ball-2-constrict.png for shrinking gap + ESCAPE text');
    console.log('- Gap should be OBVIOUS and point toward escape route');
  });

  test('VERIFY-6: Full gameplay capture with video', async ({ page }) => {
    // This test captures extended gameplay for manual review
    await waitForMenu(page);
    await startGame(page);

    console.log('Recording 30 seconds of gameplay...');
    const stateLog: any[] = [];

    // Play with varied inputs
    for (let second = 0; second < 30; second++) {
      // Random movement
      const keys = ['w', 'a', 's', 'd'];
      const key = keys[Math.floor(Math.random() * keys.length)];

      await page.keyboard.down(key);

      // Occasional dash
      if (second % 3 === 0) {
        await page.keyboard.down('Shift');
        await page.waitForTimeout(100);
        await page.keyboard.up('Shift');
      }

      await page.waitForTimeout(900);
      await page.keyboard.up(key);

      // Log state
      const state = await getGameState(page);
      stateLog.push({
        second,
        health: state?.player?.health,
        killCount: state?.killCount,
        wave: state?.wave,
        enemyCount: state?.enemies?.length,
        phase: state?.phase,
        dashActive: state?.player?.dash?.isDashing,
      });

      // Screenshot every 5 seconds
      if (second % 5 === 0) {
        await page.screenshot({ path: `${EVIDENCE_DIR}/gameplay-${second}s.png` });
      }

      // Stop if dead
      if (state?.phase === 'dead') {
        console.log(`Player died at ${second} seconds`);
        break;
      }
    }

    // Final screenshot
    await page.screenshot({ path: `${EVIDENCE_DIR}/gameplay-final.png` });

    // Write state log
    fs.writeFileSync(
      `${EVIDENCE_DIR}/state-log.json`,
      JSON.stringify(stateLog, null, 2)
    );

    console.log('\n=== GAMEPLAY SUMMARY ===');
    console.log('State log written to:', `${EVIDENCE_DIR}/state-log.json`);
    console.log('Screenshots saved to:', EVIDENCE_DIR);
    console.log('\nFinal stats:');
    const finalState = stateLog[stateLog.length - 1];
    console.log('- Duration:', stateLog.length, 'seconds');
    console.log('- Final health:', finalState?.health);
    console.log('- Kill count:', finalState?.killCount);
    console.log('- Wave reached:', finalState?.wave);
    console.log('- Dash activations detected:', stateLog.filter(s => s.dashActive).length);
  });
});
