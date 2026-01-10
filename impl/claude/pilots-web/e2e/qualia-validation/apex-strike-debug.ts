/**
 * Apex Strike Debug API Helpers — Run 038
 *
 * Helpers for verifying the charge-based dash refactor (DD-038-1 through DD-038-5).
 * Extends the base debug-api.ts with dash-specific functions.
 *
 * Philosophy: "A player who cannot see cannot judge. These tools give the PLAYER eyes."
 *
 * @see coordination/.player.session.md for qualia verification matrix
 * @see coordination/.outline.md for DD-038 architecture
 */

import type { Page } from '@playwright/test';

// =============================================================================
// Types for Apex Strike v2 (Run 038)
// =============================================================================

export type ApexPhase =
  | 'idle'
  | 'charging'
  | 'striking'
  | 'stumble'      // DD-038-4: Miss penalty phase 1
  | 'vulnerable'   // DD-038-4: Miss penalty phase 2
  | 'recovery';    // DD-038-4: Miss penalty phase 3

export type AimMode = 'cursor' | 'wasd';

export interface ApexState {
  /** Current state machine phase */
  phase: ApexPhase;

  /** Charge level 0.0-1.0 (DD-038-1) */
  chargeLevel: number;

  /** Time charging in ms */
  chargeTime: number;

  /** Was this a tap dash (<100ms)? */
  isTapDash: boolean;

  /** Current aim source (DD-038-2) */
  aimMode: AimMode;

  /** Locked direction (normalized) */
  direction: { x: number; y: number };

  /** Bloodlust meter 0-100 */
  bloodlust: number;

  /** Cooldown remaining in ms */
  cooldownRemaining: number;

  /** Current miss penalty phase if any (DD-038-4) */
  missPenaltyPhase: 'stumble' | 'vulnerable' | 'recovery' | null;

  /** Miss penalty timer remaining in ms */
  missPenaltyTimer: number;
}

export interface ApexJuiceEvent {
  event:
    | 'charge_start'
    | 'charge_update'
    | 'charge_full'
    | 'strike_launch'
    | 'strike_hit'
    | 'strike_kill'
    | 'strike_miss'
    | 'afterimage_spawn'
    | 'chain_available'
    | 'chain_start';
  timestamp: number;
  chargeLevel?: number;
  direction?: { x: number; y: number };
  enemyId?: string;
  damage?: number;
  position?: { x: number; y: number };
}

// =============================================================================
// Window API Extensions (Expected from useDebugAPI.ts)
// =============================================================================

declare global {
  interface Window {
    // Apex Strike state query
    DEBUG_GET_APEX_STATE?: () => ApexState | null;

    // Force dash at specific charge level
    DEBUG_FORCE_DASH?: (chargeLevel: number, direction?: { x: number; y: number }) => void;

    // Apex juice event log
    DEBUG_GET_APEX_JUICE_LOG?: () => ApexJuiceEvent[];
    DEBUG_CLEAR_APEX_LOG?: () => void;

    // Utility controls
    DEBUG_RESET_DASH_COOLDOWN?: () => void;
    DEBUG_SET_BLOODLUST?: (value: number) => void;
  }
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Wait for apex strike debug API to be available
 */
export async function waitForApexDebugApi(page: Page, timeout = 5000): Promise<boolean> {
  try {
    await page.waitForFunction(
      () => typeof window.DEBUG_GET_APEX_STATE === 'function',
      { timeout }
    );
    return true;
  } catch {
    return false;
  }
}

/**
 * Get current apex strike state
 */
export async function getApexState(page: Page): Promise<ApexState | null> {
  return page.evaluate(() => window.DEBUG_GET_APEX_STATE?.() ?? null);
}

/**
 * Force a dash at specific charge level
 */
export async function forceDash(
  page: Page,
  chargeLevel: number,
  direction?: { x: number; y: number }
): Promise<void> {
  await page.evaluate(
    ({ level, dir }) => window.DEBUG_FORCE_DASH?.(level, dir),
    { level: chargeLevel, dir: direction }
  );
}

/**
 * Get apex juice event log
 */
export async function getApexJuiceLog(page: Page): Promise<ApexJuiceEvent[]> {
  return page.evaluate(() => window.DEBUG_GET_APEX_JUICE_LOG?.() ?? []);
}

/**
 * Clear apex juice log
 */
export async function clearApexJuiceLog(page: Page): Promise<void> {
  await page.evaluate(() => window.DEBUG_CLEAR_APEX_LOG?.());
}

/**
 * Reset dash cooldown
 */
export async function resetDashCooldown(page: Page): Promise<void> {
  await page.evaluate(() => window.DEBUG_RESET_DASH_COOLDOWN?.());
}

/**
 * Set bloodlust level
 */
export async function setBloodlust(page: Page, value: number): Promise<void> {
  await page.evaluate((v) => window.DEBUG_SET_BLOODLUST?.(v), value);
}

// =============================================================================
// Qualia Verification Helpers
// =============================================================================

/**
 * DD-038-1: Verify charge level affects power
 * Quality bar: 60% vs 100% should feel DIFFERENT
 */
export async function verifyChargeScaling(page: Page): Promise<{
  passed: boolean;
  lowChargeDamage: number;
  highChargeDamage: number;
  ratio: number;
}> {
  // Clear log and get baseline
  await clearApexJuiceLog(page);

  // Force 60% charge dash
  await forceDash(page, 0.6, { x: 1, y: 0 });
  await page.waitForTimeout(500);
  const log1 = await getApexJuiceLog(page);
  const hit1 = log1.find((e) => e.event === 'strike_hit');
  const lowDamage = hit1?.damage ?? 0;

  // Reset and force 100% charge dash
  await resetDashCooldown(page);
  await clearApexJuiceLog(page);
  await forceDash(page, 1.0, { x: 1, y: 0 });
  await page.waitForTimeout(500);
  const log2 = await getApexJuiceLog(page);
  const hit2 = log2.find((e) => e.event === 'strike_hit');
  const highDamage = hit2?.damage ?? 0;

  const ratio = highDamage / Math.max(lowDamage, 1);

  return {
    passed: ratio >= 1.4 && ratio <= 1.8, // Expect ~1.67x (100/60)
    lowChargeDamage: lowDamage,
    highChargeDamage: highDamage,
    ratio,
  };
}

/**
 * DD-038-4: Verify miss penalty has three distinct phases
 * Quality bar: Stumble → Vulnerable → Recovery should be felt
 */
export async function verifyMissPenaltyPhases(page: Page): Promise<{
  passed: boolean;
  phasesObserved: string[];
  timings: { phase: string; timeMs: number }[];
}> {
  const phasesObserved: string[] = [];
  const timings: { phase: string; timeMs: number }[] = [];

  // Force a miss (dash into empty space)
  await forceDash(page, 1.0, { x: 1, y: 0 });
  const startTime = Date.now();

  // Sample state every 50ms for 2 seconds
  for (let i = 0; i < 40; i++) {
    await page.waitForTimeout(50);
    const state = await getApexState(page);
    const phase = state?.missPenaltyPhase ?? state?.phase ?? 'unknown';

    if (!phasesObserved.includes(phase) && phase !== 'unknown' && phase !== 'idle') {
      phasesObserved.push(phase);
      timings.push({ phase, timeMs: Date.now() - startTime });
    }
  }

  // Should see all three phases in order
  const expectedOrder = ['stumble', 'vulnerable', 'recovery'];
  const passed =
    phasesObserved.length >= 3 &&
    expectedOrder.every((phase, i) => phasesObserved[i] === phase);

  return { passed, phasesObserved, timings };
}

/**
 * DD-038-3: Verify afterimages spawn during strike
 * Quality bar: 5 afterimages should spawn during strike
 */
export async function verifyAfterimages(page: Page): Promise<{
  passed: boolean;
  afterimageCount: number;
  positions: { x: number; y: number }[];
}> {
  await clearApexJuiceLog(page);

  // Force full charge dash
  await forceDash(page, 1.0, { x: 1, y: 0 });
  await page.waitForTimeout(300); // Wait for strike to complete

  const log = await getApexJuiceLog(page);
  const afterimages = log.filter((e) => e.event === 'afterimage_spawn');

  return {
    passed: afterimages.length >= 4, // At least 4 of 5 expected
    afterimageCount: afterimages.length,
    positions: afterimages.map((e) => e.position ?? { x: 0, y: 0 }),
  };
}

/**
 * DD-038-5: Verify UI elements are visible
 * Quality bar: Charge meter, direction indicator, cooldown visible
 */
export async function verifyDashUIElements(page: Page): Promise<{
  passed: boolean;
  chargemeterVisible: boolean;
  directionLineVisible: boolean;
  cooldownVisible: boolean;
}> {
  // Start charging (hold space)
  await page.keyboard.down('Space');
  await page.waitForTimeout(200);

  // Check for UI elements (selectors TBD by CREATIVE)
  const chargeMeter = await page.$('[data-testid="charge-meter"]');
  const directionLine = await page.$('[data-testid="direction-indicator"]');

  await page.keyboard.up('Space');
  await page.waitForTimeout(100);

  // Check cooldown indicator after dash
  const cooldown = await page.$('[data-testid="cooldown-indicator"]');

  const chargemeterVisible = chargeMeter !== null;
  const directionLineVisible = directionLine !== null;
  const cooldownVisible = cooldown !== null;

  return {
    passed: chargemeterVisible && directionLineVisible,
    chargemeterVisible,
    directionLineVisible,
    cooldownVisible,
  };
}

// =============================================================================
// Evidence Capture
// =============================================================================

/**
 * Capture dash sequence for evidence
 */
export async function captureDashSequence(
  page: Page,
  outputDir: string,
  name: string
): Promise<string[]> {
  const paths: string[] = [];

  // Before charge
  await page.screenshot({ path: `${outputDir}/${name}-1-before.png` });
  paths.push(`${outputDir}/${name}-1-before.png`);

  // During charge
  await page.keyboard.down('Space');
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${outputDir}/${name}-2-charging.png` });
  paths.push(`${outputDir}/${name}-2-charging.png`);

  // At release
  await page.keyboard.up('Space');
  await page.waitForTimeout(50);
  await page.screenshot({ path: `${outputDir}/${name}-3-strike.png` });
  paths.push(`${outputDir}/${name}-3-strike.png`);

  // After strike
  await page.waitForTimeout(200);
  await page.screenshot({ path: `${outputDir}/${name}-4-after.png` });
  paths.push(`${outputDir}/${name}-4-after.png`);

  return paths;
}
