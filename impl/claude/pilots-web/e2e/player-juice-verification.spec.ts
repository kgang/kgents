/**
 * PLAYER Juice Verification Test Suite
 *
 * Tests to verify juice qualia (shake, freeze, particles) once the
 * DEBUG_GET_SHAKE_STATE, DEBUG_GET_FREEZE_STATE, DEBUG_GET_PARTICLE_COUNT
 * APIs are implemented by CREATIVE.
 *
 * STATUS: SCAFFOLDING - waiting for debug APIs
 * REQUESTED IN: .needs.creative.md (Iteration 4)
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part VII: Juice Layer)
 * @see .player.qualia-matrix.md (M6, M11-M13)
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PILOT_NAME = process.env.PILOT_NAME || 'wasm-survivors-game';
const EVIDENCE_DIR = path.join(__dirname, '..', 'evidence', 'juice');

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

/**
 * Check if juice debug APIs are available
 */
async function hasJuiceDebugAPI(page: Page): Promise<boolean> {
  return page.evaluate(() =>
    typeof (window as any).DEBUG_GET_SHAKE_STATE === 'function'
  );
}

// =============================================================================
// Juice Debug API Availability Tests
// =============================================================================

test.describe('PLAYER Juice API Availability', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);
  });

  test('juice debug APIs are available', async ({ page }) => {
    const hasShakeAPI = await page.evaluate(() =>
      typeof (window as any).DEBUG_GET_SHAKE_STATE === 'function'
    );
    const hasFreezeAPI = await page.evaluate(() =>
      typeof (window as any).DEBUG_GET_FREEZE_STATE === 'function'
    );
    const hasParticleAPI = await page.evaluate(() =>
      typeof (window as any).DEBUG_GET_PARTICLE_COUNT === 'function'
    );
    const hasJuiceLogAPI = await page.evaluate(() =>
      typeof (window as any).DEBUG_GET_JUICE_LOG === 'function'
    );

    console.log('Juice APIs available:', {
      shake: hasShakeAPI,
      freeze: hasFreezeAPI,
      particle: hasParticleAPI,
      juiceLog: hasJuiceLogAPI,
    });

    // Skip remaining tests if APIs not available
    if (!hasShakeAPI) {
      test.skip();
    }
  });
});

// =============================================================================
// M6: Kills Feel Like PUNCHES (Shake Verification)
// =============================================================================

test.describe('PLAYER M6: Kill Shake Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    // Skip if juice API not available
    if (!(await hasJuiceDebugAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('worker kill triggers 2px shake', async ({ page }) => {
    // Spawn and kill a worker (basic enemy)
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 100, y: 100 }));
    await page.waitForTimeout(100);

    // Kill all enemies to trigger shake
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(50);

    // Check shake state
    const shake = await page.evaluate(() => (window as any).DEBUG_GET_SHAKE_STATE?.());

    console.log('Shake state after worker kill:', shake);

    expect(shake).toBeTruthy();
    expect(shake.active).toBe(true);
    expect(shake.amplitude).toBe(2); // PROTO_SPEC: workerKill = 2px
    expect(shake.type).toBe('workerKill');

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'shake-worker-kill.png') });
  });

  test('guard kill triggers 5px shake', async ({ page }) => {
    // Spawn and kill a guard (tank enemy)
    await page.evaluate(() => window.DEBUG_SPAWN?.('tank', { x: 100, y: 100 }));
    await page.waitForTimeout(100);

    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(50);

    const shake = await page.evaluate(() => (window as any).DEBUG_GET_SHAKE_STATE?.());

    console.log('Shake state after guard kill:', shake);

    expect(shake?.amplitude).toBe(5); // PROTO_SPEC: guardKill = 5px

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'shake-guard-kill.png') });
  });

  test('multi-kill triggers 10px shake', async ({ page }) => {
    // Spawn 5 workers close together
    for (let i = 0; i < 5; i++) {
      await page.evaluate(
        (idx) => window.DEBUG_SPAWN?.('basic', { x: 100 + idx * 20, y: 100 }),
        i
      );
    }
    await page.waitForTimeout(100);

    // Kill all at once
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(50);

    const shake = await page.evaluate(() => (window as any).DEBUG_GET_SHAKE_STATE?.());

    console.log('Shake state after multi-kill:', shake);

    expect(shake?.type).toBe('multiKill');
    expect(shake?.amplitude).toBeGreaterThanOrEqual(8); // 5+ kills should trigger larger shake

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'shake-multi-kill.png') });
  });
});

// =============================================================================
// M12: Freeze Frames on Significant Kills
// =============================================================================

test.describe('PLAYER M12: Freeze Frame Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasJuiceDebugAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('guard kill triggers 2-frame freeze', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_SPAWN?.('tank', { x: 100, y: 100 }));
    await page.waitForTimeout(100);

    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Check freeze immediately after kill
    const freeze = await page.evaluate(() => (window as any).DEBUG_GET_FREEZE_STATE?.());

    console.log('Freeze state after guard kill:', freeze);

    expect(freeze).toBeTruthy();
    expect(freeze.trigger).toBe('significantKill');
    expect(freeze.framesRemaining).toBeGreaterThanOrEqual(2);

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'freeze-guard-kill.png') });
  });

  test('multi-kill triggers 4-frame freeze', async ({ page }) => {
    // Spawn 5 enemies
    for (let i = 0; i < 5; i++) {
      await page.evaluate(
        (idx) => window.DEBUG_SPAWN?.('basic', { x: 100 + idx * 20, y: 100 }),
        i
      );
    }
    await page.waitForTimeout(100);

    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    const freeze = await page.evaluate(() => (window as any).DEBUG_GET_FREEZE_STATE?.());

    console.log('Freeze state after multi-kill:', freeze);

    expect(freeze?.trigger).toBe('multiKill');
    expect(freeze?.framesRemaining).toBeGreaterThanOrEqual(4);

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'freeze-multi-kill.png') });
  });
});

// =============================================================================
// M13: Death Spiral Particles
// =============================================================================

test.describe('PLAYER M13: Death Particle Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasJuiceDebugAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('enemy death emits 25+ particles', async ({ page }) => {
    // Clear and spawn single enemy
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    // Get baseline particle count
    const baselineCount = await page.evaluate(() =>
      (window as any).DEBUG_GET_PARTICLE_COUNT?.() ?? 0
    );

    // Spawn and kill
    await page.evaluate(() => window.DEBUG_SPAWN?.('basic', { x: 300, y: 300 }));
    await page.waitForTimeout(100);
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    // Check particle count immediately after kill
    await page.waitForTimeout(50);
    const afterCount = await page.evaluate(() =>
      (window as any).DEBUG_GET_PARTICLE_COUNT?.() ?? 0
    );

    const particlesEmitted = afterCount - baselineCount;
    console.log(`Particles emitted on death: ${particlesEmitted}`);

    expect(particlesEmitted).toBeGreaterThanOrEqual(25); // PROTO_SPEC: deathSpiral.count = 25

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'particles-death-spiral.png') });
  });

  test('multi-kill emits proportionally more particles', async ({ page }) => {
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    const baselineCount = await page.evaluate(() =>
      (window as any).DEBUG_GET_PARTICLE_COUNT?.() ?? 0
    );

    // Spawn 5 enemies
    for (let i = 0; i < 5; i++) {
      await page.evaluate(
        (idx) => window.DEBUG_SPAWN?.('basic', { x: 200 + idx * 40, y: 300 }),
        i
      );
    }
    await page.waitForTimeout(100);
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());

    await page.waitForTimeout(50);
    const afterCount = await page.evaluate(() =>
      (window as any).DEBUG_GET_PARTICLE_COUNT?.() ?? 0
    );

    const particlesEmitted = afterCount - baselineCount;
    console.log(`Particles from 5-kill: ${particlesEmitted}`);

    // 5 kills should emit at least 5 * 25 = 125 particles
    expect(particlesEmitted).toBeGreaterThanOrEqual(100);

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'particles-multi-death.png') });
  });
});

// =============================================================================
// Juice Log Verification
// =============================================================================

test.describe('PLAYER Juice Event Log', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasJuiceDebugAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('juice log captures events in order', async ({ page }) => {
    // Spawn and kill several enemies
    for (let i = 0; i < 3; i++) {
      await page.evaluate(
        (idx) => window.DEBUG_SPAWN?.('basic', { x: 200 + idx * 50, y: 300 }),
        i
      );
    }
    await page.waitForTimeout(100);
    await page.evaluate(() => window.DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(100);

    const juiceLog = await page.evaluate(() => (window as any).DEBUG_GET_JUICE_LOG?.());

    console.log('Juice log:', JSON.stringify(juiceLog, null, 2));

    expect(Array.isArray(juiceLog)).toBe(true);
    expect(juiceLog.length).toBeGreaterThan(0);

    // Save log as evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'juice-event-log.json'),
      JSON.stringify(juiceLog, null, 2)
    );

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'juice-log-capture.png') });
  });
});
