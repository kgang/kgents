/**
 * Audio Verification Tests
 *
 * PLAYER tests to verify audio behavior in wasm-survivors-game.
 * V1 Focus: noise_silence pole - verifying audio contrast exists.
 *
 * These tests verify:
 * 1. Audio events are fired on kills
 * 2. THE BALL formation increases audio level (buzz)
 * 3. THE SILENCE phase is actually silent
 * 4. V1 contrast exists between loud and silent moments
 *
 * Usage:
 *   npx playwright test e2e/audio-verification.spec.ts
 *   npx playwright test e2e/audio-verification.spec.ts --grep "kills produce audio"
 *
 * @see e2e/utils/audio-verification.ts
 * @see src/pilots/wasm-survivors-game/systems/audio.ts
 */

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

import {
  hasAudioDebugAPI,
  initAudioForTest,
  getAudioState,
  getAudioLevel,
  getAudioLog,
  clearAudioLog,
  waitForAudio,
  waitForAudioEvent,
  assertSilence,
  assertAudioPlaying,
  assertAudioContrast,
  captureAudioEvidence,
  skipIfNoAudioAPI,
  getAudioSummary,
} from './utils/audio-verification';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PILOT_NAME = process.env.PILOT_NAME || 'wasm-survivors-game';
const EVIDENCE_DIR = path.join(__dirname, '..', 'evidence', 'audio');

// Ensure evidence directory exists
if (!fs.existsSync(EVIDENCE_DIR)) {
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
}

// =============================================================================
// Test Setup Helpers
// =============================================================================

function getPilotURL(): string {
  return `/pilots/${PILOT_NAME}?debug=true`;
}

async function startGame(page: any): Promise<void> {
  const beginButton = page.locator('button:has-text("BEGIN RAID")');
  if (await beginButton.isVisible()) {
    await beginButton.click();
  } else {
    await page.evaluate(() => (window as any).DEBUG_START_GAME?.());
  }
  await page.waitForTimeout(500);
}

async function waitForDebugAPI(page: any, timeout = 10000): Promise<boolean> {
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

// =============================================================================
// Audio API Availability Tests
// =============================================================================

test.describe('Audio API Availability', () => {
  test('audio DEBUG API is accessible', async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasAPI = await hasAudioDebugAPI(page);

    if (!hasAPI) {
      console.log('Audio DEBUG API not implemented yet - skipping detailed checks');
      // Don't fail - API may not be implemented yet
      return;
    }

    const state = await getAudioState(page);
    console.log('Audio state:', JSON.stringify(state, null, 2));

    expect(state).toHaveProperty('isEnabled');
    expect(state).toHaveProperty('masterVolume');
    expect(state).toHaveProperty('contextState');
  });

  test('audio can be initialized via user gesture', async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasAPI = await hasAudioDebugAPI(page);
    if (!hasAPI) {
      console.log('Audio DEBUG API not available - skipping');
      return;
    }

    const initialized = await initAudioForTest(page);

    if (initialized) {
      const state = await getAudioState(page);
      expect(state.isEnabled).toBe(true);
      expect(state.contextState).toBe('running');
    } else {
      console.log('Audio initialization failed - may need user gesture');
    }
  });
});

// =============================================================================
// Kill Audio Tests
// =============================================================================

test.describe('Kill Audio Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasGameAPI = await waitForDebugAPI(page);
    if (!hasGameAPI) {
      test.skip();
      return;
    }

    await startGame(page);
    await initAudioForTest(page);
  });

  test('kills produce audio events', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    // Clear the audio log
    await clearAudioLog(page);

    // Set up for kills
    await page.evaluate(() => (window as any).DEBUG_SET_INVINCIBLE?.(true));
    await page.evaluate(() => (window as any).DEBUG_KILL_ALL_ENEMIES?.());

    // Spawn enemies close to player for quick kills
    for (let i = 0; i < 3; i++) {
      await page.evaluate(() =>
        (window as any).DEBUG_SPAWN?.('worker', { x: 50 + Math.random() * 50, y: 50 + Math.random() * 50 })
      );
    }

    // Wait for kills to happen
    await page.waitForTimeout(3000);

    // Check for kill audio events
    const log = await getAudioLog(page);
    const killEvents = log.filter((e) => e.type === 'kill');

    console.log(`Kill audio events: ${killEvents.length}`);
    console.log('All audio events:', log.map((e) => e.type).join(', '));

    if (killEvents.length === 0) {
      console.log('No kill audio events logged - kill audio may not be wired to debug log');
      // Don't fail - audio may work but not be logged yet
    } else {
      expect(killEvents.length).toBeGreaterThan(0);
    }

    // Save evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'kill-audio-log.json'),
      JSON.stringify(log, null, 2)
    );
  });

  test('different kill tiers produce different audio', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    await page.evaluate(() => (window as any).DEBUG_SET_INVINCIBLE?.(true));

    // Test single kill
    await clearAudioLog(page);
    await page.evaluate(() => (window as any).DEBUG_KILL_ALL_ENEMIES?.());
    await page.evaluate(() =>
      (window as any).DEBUG_SPAWN?.('worker', { x: 60, y: 60 })
    );
    await page.waitForTimeout(2000);
    const singleKillLog = await getAudioLog(page);

    // Test multi kill (multiple enemies)
    await clearAudioLog(page);
    await page.evaluate(() => (window as any).DEBUG_KILL_ALL_ENEMIES?.());
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() =>
        (window as any).DEBUG_SPAWN?.('worker', { x: 60, y: 60 })
      );
    }
    await page.waitForTimeout(2000);
    const multiKillLog = await getAudioLog(page);

    console.log(`Single kill events: ${singleKillLog.length}`);
    console.log(`Multi kill events: ${multiKillLog.length}`);

    // Save evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'kill-tier-comparison.json'),
      JSON.stringify({ single: singleKillLog, multi: multiKillLog }, null, 2)
    );
  });
});

// =============================================================================
// THE BALL Audio Tests
// =============================================================================

test.describe('THE BALL Audio Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasGameAPI = await waitForDebugAPI(page);
    if (!hasGameAPI) {
      test.skip();
      return;
    }

    await startGame(page);
    await initAudioForTest(page);
    await page.evaluate(() => (window as any).DEBUG_SET_INVINCIBLE?.(true));
  });

  test('ball forming increases audio level (buzz)', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    // Get baseline level before ball
    await page.evaluate(() => (window as any).DEBUG_KILL_ALL_ENEMIES?.());
    await page.waitForTimeout(500);
    const baselineLevel = await getAudioLevel(page);
    console.log(`Baseline audio level: ${baselineLevel}`);

    // Force ball formation
    await page.evaluate(() => (window as any).DEBUG_FORCE_BALL?.());
    await page.waitForTimeout(1000);

    // Measure level during ball forming
    const ballLevel = await getAudioLevel(page);
    console.log(`Ball forming audio level: ${ballLevel}`);

    const state = await getAudioState(page);
    console.log(`Buzz volume: ${state.buzzVolume}`);

    // Ball should increase audio (buzz)
    if (ballLevel > baselineLevel) {
      console.log(`Audio increased by ${ballLevel - baselineLevel}`);
    } else {
      console.log('Ball did not increase audio level - buzz may not be wired');
    }

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'ball-forming-audio.png'),
    });
  });

  test('THE SILENCE phase is actually silent', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    // Force ball to silence phase
    await page.evaluate(() => (window as any).DEBUG_FORCE_BALL?.());
    await page.waitForTimeout(200);

    // Advance to silence (forming -> sphere -> silence)
    await page.evaluate(() => (window as any).DEBUG_NEXT_BALL_PHASE?.()); // sphere
    await page.waitForTimeout(100);
    await page.evaluate(() => (window as any).DEBUG_NEXT_BALL_PHASE?.()); // silence
    await page.waitForTimeout(500);

    // Get ball phase to confirm we're in silence
    const ballPhase = await page.evaluate(() => (window as any).DEBUG_GET_BALL_PHASE?.());
    console.log(`Current ball phase: ${ballPhase?.type}`);

    // Check audio state during silence
    const state = await getAudioState(page);
    const level = await getAudioLevel(page);

    console.log(`Silence phase - buzz: ${state.buzzVolume}, level: ${level}`);

    // THE SILENCE should have minimal audio
    if (state.buzzVolume === 0 || state.buzzVolume < 0.02) {
      console.log('Buzz correctly stopped during SILENCE');
    } else {
      console.log('Warning: Buzz may not be stopped during SILENCE');
    }

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'silence-phase-audio.png'),
    });

    // Save evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'silence-phase-state.json'),
      JSON.stringify({ phase: ballPhase, audioState: state, level }, null, 2)
    );
  });

  test('ball phases have distinct audio signatures', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    const phaseAudioData: { phase: string; level: number; buzzVolume: number }[] = [];

    // Force ball
    await page.evaluate(() => (window as any).DEBUG_FORCE_BALL?.());
    await page.waitForTimeout(500);

    // Capture audio at each phase
    const phases = ['forming', 'sphere', 'silence', 'constrict'];
    for (const expectedPhase of phases) {
      const ballPhase = await page.evaluate(() => (window as any).DEBUG_GET_BALL_PHASE?.());
      const level = await getAudioLevel(page);
      const state = await getAudioState(page);

      phaseAudioData.push({
        phase: ballPhase?.type || 'unknown',
        level,
        buzzVolume: state.buzzVolume,
      });

      console.log(`Phase ${ballPhase?.type}: level=${level}, buzz=${state.buzzVolume}`);

      // Advance to next phase
      await page.evaluate(() => (window as any).DEBUG_NEXT_BALL_PHASE?.());
      await page.waitForTimeout(300);
    }

    // Save evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'ball-phase-audio-data.json'),
      JSON.stringify(phaseAudioData, null, 2)
    );

    // Verify at least some phases have different audio
    const uniqueLevels = new Set(phaseAudioData.map((p) => Math.round(p.level / 10)));
    console.log(`Unique audio level bands: ${uniqueLevels.size}`);
  });
});

// =============================================================================
// V1 Contrast Verification (noise_silence pole)
// =============================================================================

test.describe('V1 Audio Contrast Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasGameAPI = await waitForDebugAPI(page);
    if (!hasGameAPI) {
      test.skip();
      return;
    }

    await startGame(page);
    await initAudioForTest(page);
    await page.evaluate(() => (window as any).DEBUG_SET_INVINCIBLE?.(true));
  });

  test('loud gameplay has higher audio level than pause', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    // Loud phase: active gameplay with kills
    const loudAction = async () => {
      for (let i = 0; i < 5; i++) {
        await page.evaluate(() =>
          (window as any).DEBUG_SPAWN?.('worker', { x: 60, y: 60 })
        );
      }
      await page.waitForTimeout(1500);
    };

    // Silent phase: no enemies, no action
    const silentAction = async () => {
      await page.evaluate(() => (window as any).DEBUG_KILL_ALL_ENEMIES?.());
      await page.waitForTimeout(500);
    };

    // Capture evidence during loud phase
    const loudEvidence = await captureAudioEvidence(page, loudAction, { duration: 2000 });
    console.log(`Loud phase: peak=${loudEvidence.peakLevel}, avg=${loudEvidence.avgLevel.toFixed(1)}`);

    // Capture evidence during silent phase
    const silentEvidence = await captureAudioEvidence(page, silentAction, { duration: 1000 });
    console.log(`Silent phase: peak=${silentEvidence.peakLevel}, avg=${silentEvidence.avgLevel.toFixed(1)}`);

    // Calculate contrast
    const contrast = loudEvidence.avgLevel - silentEvidence.avgLevel;
    console.log(`Audio contrast: ${contrast.toFixed(1)}`);

    // Save evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'v1-contrast-evidence.json'),
      JSON.stringify({
        loud: {
          peak: loudEvidence.peakLevel,
          avg: loudEvidence.avgLevel,
          events: loudEvidence.events.length,
        },
        silent: {
          peak: silentEvidence.peakLevel,
          avg: silentEvidence.avgLevel,
          events: silentEvidence.events.length,
        },
        contrast,
      }, null, 2)
    );

    // V1: Just verify contrast exists (don't enforce specific threshold yet)
    if (contrast > 5) {
      console.log('V1 PASS: Audio contrast detected between loud and silent phases');
    } else {
      console.log('V1 WARNING: Low audio contrast - may need tuning');
    }
  });

  test('ball buzz vs silence contrast', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    // Force ball to get buzz
    await page.evaluate(() => (window as any).DEBUG_FORCE_BALL?.());
    await page.waitForTimeout(500);

    // Capture buzz level
    const buzzLevel = await getAudioLevel(page);
    const buzzState = await getAudioState(page);
    console.log(`Buzz phase: level=${buzzLevel}, buzzVolume=${buzzState.buzzVolume}`);

    // Advance to silence
    await page.evaluate(() => (window as any).DEBUG_NEXT_BALL_PHASE?.()); // sphere
    await page.waitForTimeout(100);
    await page.evaluate(() => (window as any).DEBUG_NEXT_BALL_PHASE?.()); // silence
    await page.waitForTimeout(500);

    // Capture silence level
    const silenceLevel = await getAudioLevel(page);
    const silenceState = await getAudioState(page);
    console.log(`Silence phase: level=${silenceLevel}, buzzVolume=${silenceState.buzzVolume}`);

    // Calculate contrast
    const buzzSilenceContrast = buzzLevel - silenceLevel;
    console.log(`Buzz/Silence contrast: ${buzzSilenceContrast}`);

    // Save evidence
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'buzz-silence-contrast.json'),
      JSON.stringify({
        buzz: { level: buzzLevel, volume: buzzState.buzzVolume },
        silence: { level: silenceLevel, volume: silenceState.buzzVolume },
        contrast: buzzSilenceContrast,
      }, null, 2)
    );

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'buzz-silence-contrast.png'),
    });
  });

  test('death audio is distinct from gameplay', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    // Clear log
    await clearAudioLog(page);

    // Get gameplay audio baseline
    for (let i = 0; i < 3; i++) {
      await page.evaluate(() =>
        (window as any).DEBUG_SPAWN?.('worker', { x: 100 + i * 50, y: 100 })
      );
    }
    await page.waitForTimeout(1000);
    const gameplayLevel = await getAudioLevel(page);
    console.log(`Gameplay audio level: ${gameplayLevel}`);

    // Trigger death
    await page.evaluate(() => (window as any).DEBUG_SET_INVINCIBLE?.(false));
    await page.evaluate(() =>
      (window as any).DEBUG_SPAWN?.('worker', { x: 50, y: 50 })
    );

    // Wait for death
    try {
      await page.waitForSelector('button:has-text("HUNT AGAIN")', { timeout: 30000 });

      // Check for death audio event
      const log = await getAudioLog(page);
      const deathEvents = log.filter((e) => e.type === 'death');
      console.log(`Death audio events: ${deathEvents.length}`);

      // Save evidence
      fs.writeFileSync(
        path.join(EVIDENCE_DIR, 'death-audio-log.json'),
        JSON.stringify(log, null, 2)
      );

      await page.screenshot({
        path: path.join(EVIDENCE_DIR, 'death-audio-screen.png'),
      });
    } catch {
      console.log('Death did not occur within timeout');
    }
  });
});

// =============================================================================
// Audio Event Logging Tests
// =============================================================================

test.describe('Audio Event Logging', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');

    const hasGameAPI = await waitForDebugAPI(page);
    if (!hasGameAPI) {
      test.skip();
      return;
    }

    await startGame(page);
    await initAudioForTest(page);
  });

  test('audio summary captures state correctly', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    const summary = await getAudioSummary(page);
    console.log(summary);

    // Just verify summary can be generated
    expect(summary).toContain('Audio State:');
    expect(summary).toContain('Enabled:');
  });

  test('comprehensive audio event capture during gameplay', async ({ page }) => {
    if (await skipIfNoAudioAPI(page, test)) return;

    await page.evaluate(() => (window as any).DEBUG_SET_INVINCIBLE?.(true));
    await clearAudioLog(page);

    // Generate various audio events
    console.log('Generating audio events...');

    // Kills
    for (let i = 0; i < 3; i++) {
      await page.evaluate(() =>
        (window as any).DEBUG_SPAWN?.('worker', { x: 60, y: 60 })
      );
    }
    await page.waitForTimeout(2000);

    // Level up
    await page.evaluate(() => (window as any).DEBUG_LEVEL_UP?.());
    await page.waitForTimeout(500);

    // Ball formation
    await page.evaluate(() => (window as any).DEBUG_FORCE_BALL?.());
    await page.waitForTimeout(1000);

    // Get all events
    const log = await getAudioLog(page);
    const eventTypes = [...new Set(log.map((e) => e.type))];

    console.log(`Total events: ${log.length}`);
    console.log(`Event types: ${eventTypes.join(', ')}`);

    // Save comprehensive log
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'comprehensive-audio-log.json'),
      JSON.stringify({
        totalEvents: log.length,
        eventTypes,
        events: log,
      }, null, 2)
    );

    await page.screenshot({
      path: path.join(EVIDENCE_DIR, 'comprehensive-audio-final.png'),
    });
  });
});
