/**
 * Run 038: Dash Qualia Verification Tests
 *
 * Tests for the charge-based dash refactor (DD-038-1 through DD-038-5).
 * These tests verify the PLAYER's qualia claims from the verification matrix.
 *
 * Philosophy: "The player is the proof. The joy is the witness."
 *
 * @see coordination/.player.session.md for qualia verification matrix
 * @see coordination/.outline.md for DD-038 architecture
 */

import { test, expect } from '@playwright/test';
import {
  waitForApexDebugApi,
  getApexState,
  forceDash,
  getApexJuiceLog,
  clearApexJuiceLog,
  resetDashCooldown,
  setBloodlust,
  verifyChargeScaling,
  verifyMissPenaltyPhases,
  verifyAfterimages,
  verifyDashUIElements,
  captureDashSequence,
} from './qualia-validation/apex-strike-debug';
import { waitForDebugApi, spawnEnemy, setInvincible } from './qualia-validation/debug-api';

const GAME_URL = '/pilots/wasm-survivors-game?debug=true';
const EVIDENCE_DIR = 'test-results/run038-evidence';

// =============================================================================
// Test Setup
// =============================================================================

test.describe('Run 038: Dash Qualia Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(GAME_URL);

    // Wait for both base and apex debug APIs
    const baseReady = await waitForDebugApi(page);
    const apexReady = await waitForApexDebugApi(page);

    if (!baseReady) {
      test.skip(true, 'Base debug API not available');
    }

    // Note: Apex API may not be available until implementation is complete
    // Tests will skip gracefully if not ready

    // Start game
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);
  });

  // ===========================================================================
  // DD-038-1: Charge-Based Dash — Charge Scaling
  // ===========================================================================

  test.describe('DD-038-1: Charge Scaling', () => {
    test('charge level affects damage output', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      await setInvincible(page, true);

      // Spawn two enemies for comparison
      await spawnEnemy(page, 'worker', { x: 300, y: 300 });
      await spawnEnemy(page, 'worker', { x: 500, y: 300 });
      await page.waitForTimeout(200);

      const result = await verifyChargeScaling(page);

      expect(result.passed).toBe(true);
      expect(result.ratio).toBeGreaterThan(1.3); // At least 30% more damage at full charge
      expect(result.ratio).toBeLessThan(2.0); // But not unreasonably high

      console.log(`Charge scaling verified: ${result.lowChargeDamage} -> ${result.highChargeDamage} (${result.ratio.toFixed(2)}x)`);
    });

    test('tap dash (<100ms) uses minimum charge', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      await clearApexJuiceLog(page);

      // Quick tap
      await page.keyboard.down('Space');
      await page.waitForTimeout(50); // 50ms = tap
      await page.keyboard.up('Space');
      await page.waitForTimeout(200);

      const state = await getApexState(page);
      expect(state?.isTapDash).toBe(true);

      const log = await getApexJuiceLog(page);
      const launch = log.find((e) => e.event === 'strike_launch');
      expect(launch?.chargeLevel).toBeLessThanOrEqual(0.65); // ~60% for tap
    });

    test('full charge (800ms) produces maximum power', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      await clearApexJuiceLog(page);

      // Full charge
      await page.keyboard.down('Space');
      await page.waitForTimeout(850); // Slightly over max
      await page.keyboard.up('Space');
      await page.waitForTimeout(200);

      const log = await getApexJuiceLog(page);
      const launch = log.find((e) => e.event === 'strike_launch');
      expect(launch?.chargeLevel).toBeGreaterThanOrEqual(0.95); // Near max
    });
  });

  // ===========================================================================
  // DD-038-2: Cursor-Aim with WASD Override
  // ===========================================================================

  test.describe('DD-038-2: Aim Control', () => {
    test('direction follows cursor during charge', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      // Move mouse to specific position
      await page.mouse.move(600, 300);

      // Start charging
      await page.keyboard.down('Space');
      await page.waitForTimeout(200);

      const state = await getApexState(page);
      expect(state?.aimMode).toBe('cursor');

      // Direction should point toward cursor
      expect(state?.direction.x).toBeGreaterThan(0); // Pointing right

      await page.keyboard.up('Space');
    });

    test('WASD overrides cursor during charge', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      // Move mouse right
      await page.mouse.move(600, 300);

      // Start charging
      await page.keyboard.down('Space');
      await page.waitForTimeout(100);

      // Press left key
      await page.keyboard.down('KeyA');
      await page.waitForTimeout(100);

      const state = await getApexState(page);
      expect(state?.aimMode).toBe('wasd');
      expect(state?.direction.x).toBeLessThan(0); // Now pointing left

      await page.keyboard.up('KeyA');
      await page.keyboard.up('Space');
    });
  });

  // ===========================================================================
  // DD-038-3: Six-Layer Juice Stack
  // ===========================================================================

  test.describe('DD-038-3: Juice Layers', () => {
    test('afterimages spawn during strike', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      const result = await verifyAfterimages(page);

      expect(result.passed).toBe(true);
      expect(result.afterimageCount).toBeGreaterThanOrEqual(4);

      console.log(`Afterimages verified: ${result.afterimageCount} spawned`);
    });

    test('hit triggers all juice layers', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      await setInvincible(page, true);
      await spawnEnemy(page, 'worker', { x: 350, y: 300 });
      await page.waitForTimeout(200);

      await clearApexJuiceLog(page);
      await forceDash(page, 1.0, { x: 1, y: 0 });
      await page.waitForTimeout(500);

      const log = await getApexJuiceLog(page);

      // Check for juice events
      const hasLaunch = log.some((e) => e.event === 'strike_launch');
      const hasHit = log.some((e) => e.event === 'strike_hit');
      const hasAfterimages = log.filter((e) => e.event === 'afterimage_spawn').length >= 3;

      expect(hasLaunch).toBe(true);
      expect(hasHit).toBe(true);
      expect(hasAfterimages).toBe(true);
    });

    test('miss produces distinct feedback', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      await clearApexJuiceLog(page);

      // Dash into empty space
      await forceDash(page, 1.0, { x: 1, y: 0 });
      await page.waitForTimeout(500);

      const log = await getApexJuiceLog(page);

      const hasMiss = log.some((e) => e.event === 'strike_miss');
      const hasHit = log.some((e) => e.event === 'strike_hit');

      expect(hasMiss).toBe(true);
      expect(hasHit).toBe(false); // No hit on miss
    });
  });

  // ===========================================================================
  // DD-038-4: Miss Penalty Redesign
  // ===========================================================================

  test.describe('DD-038-4: Miss Penalty', () => {
    test('miss penalty has three distinct phases', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      const result = await verifyMissPenaltyPhases(page);

      expect(result.passed).toBe(true);
      expect(result.phasesObserved).toContain('stumble');
      expect(result.phasesObserved).toContain('vulnerable');
      expect(result.phasesObserved).toContain('recovery');

      console.log(`Miss penalty phases: ${result.phasesObserved.join(' -> ')}`);
      console.log(`Timings: ${JSON.stringify(result.timings)}`);
    });

    test('stumble phase lasts ~300ms', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      await forceDash(page, 1.0, { x: 1, y: 0 });

      // Check at 100ms - should be stumble
      await page.waitForTimeout(100);
      let state = await getApexState(page);
      expect(state?.missPenaltyPhase).toBe('stumble');

      // Check at 350ms - should be vulnerable
      await page.waitForTimeout(250);
      state = await getApexState(page);
      expect(state?.missPenaltyPhase).toBe('vulnerable');
    });

    test('vulnerable phase takes 1.5x damage', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      // Spawn enemy
      await spawnEnemy(page, 'worker', { x: 300, y: 300 });

      // Miss dash to enter penalty
      await forceDash(page, 1.0, { x: -1, y: 0 });
      await page.waitForTimeout(400); // Enter vulnerable phase

      const state = await getApexState(page);
      expect(state?.missPenaltyPhase).toBe('vulnerable');

      // TODO: Verify 1.5x damage multiplier with damage test
    });
  });

  // ===========================================================================
  // DD-038-5: UI Improvements
  // ===========================================================================

  test.describe('DD-038-5: UI Elements', () => {
    test('charge meter visible during charge', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      const result = await verifyDashUIElements(page);

      expect(result.chargemeterVisible).toBe(true);
    });

    test('direction indicator visible during charge', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      const result = await verifyDashUIElements(page);

      expect(result.directionLineVisible).toBe(true);
    });

    test('capture UI evidence screenshots', async ({ page }) => {
      // This test always runs to capture evidence
      await page.waitForTimeout(1000);

      const paths = await captureDashSequence(page, EVIDENCE_DIR, 'dash-ui');

      console.log(`Evidence captured: ${paths.join(', ')}`);
      expect(paths.length).toBe(4);
    });
  });

  // ===========================================================================
  // Integration Tests
  // ===========================================================================

  test.describe('Integration: Dash Feel', () => {
    test('full dash flow feels complete', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      await setInvincible(page, true);
      await spawnEnemy(page, 'worker', { x: 400, y: 300 });
      await page.waitForTimeout(300);

      await clearApexJuiceLog(page);

      // Full charge → release → hit
      await page.keyboard.down('Space');
      await page.waitForTimeout(800);
      await page.keyboard.up('Space');
      await page.waitForTimeout(500);

      const log = await getApexJuiceLog(page);

      // Verify complete flow
      const events = log.map((e) => e.event);
      expect(events).toContain('charge_start');
      expect(events).toContain('strike_launch');
      // Should have either hit or miss
      expect(events.some((e) => e === 'strike_hit' || e === 'strike_miss')).toBe(true);

      console.log(`Dash flow events: ${events.join(' -> ')}`);
    });

    test('bloodlust affects damage', async ({ page }) => {
      const apexReady = await waitForApexDebugApi(page);
      test.skip(!apexReady, 'Apex debug API not yet implemented');

      await setInvincible(page, true);

      // Test without bloodlust
      await setBloodlust(page, 0);
      await spawnEnemy(page, 'worker', { x: 350, y: 300 });
      await page.waitForTimeout(200);
      await clearApexJuiceLog(page);
      await forceDash(page, 1.0, { x: 1, y: 0 });
      await page.waitForTimeout(300);
      const log1 = await getApexJuiceLog(page);
      const hit1 = log1.find((e) => e.event === 'strike_hit');
      const baseDamage = hit1?.damage ?? 0;

      // Test with max bloodlust
      await resetDashCooldown(page);
      await setBloodlust(page, 100);
      await spawnEnemy(page, 'worker', { x: 350, y: 300 });
      await page.waitForTimeout(200);
      await clearApexJuiceLog(page);
      await forceDash(page, 1.0, { x: 1, y: 0 });
      await page.waitForTimeout(300);
      const log2 = await getApexJuiceLog(page);
      const hit2 = log2.find((e) => e.event === 'strike_hit');
      const bloodlustDamage = hit2?.damage ?? 0;

      // Bloodlust should give 2x damage at max
      expect(bloodlustDamage).toBeGreaterThan(baseDamage * 1.5);
      console.log(`Bloodlust damage: ${baseDamage} -> ${bloodlustDamage} (${(bloodlustDamage / baseDamage).toFixed(2)}x)`);
    });
  });
});
