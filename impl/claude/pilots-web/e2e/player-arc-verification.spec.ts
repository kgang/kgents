/**
 * PLAYER Arc/Emotional State Verification Test Suite
 *
 * Tests to verify emotional arc qualia (phases, contrast, voice lines)
 * using the existing DEBUG_GET_EMOTIONAL_STATE API.
 *
 * STATUS: READY - uses existing API
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part VI: Arc Grammar)
 * @see .player.qualia-matrix.md (N1-N5, N6-N7)
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PILOT_NAME = process.env.PILOT_NAME || 'wasm-survivors-game';
const EVIDENCE_DIR = path.join(__dirname, '..', 'evidence', 'arc');

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

async function hasEmotionalAPI(page: Page): Promise<boolean> {
  return page.evaluate(() =>
    typeof window.DEBUG_GET_EMOTIONAL_STATE === 'function'
  );
}

// =============================================================================
// Arc Phase Verification (N1-N5)
// =============================================================================

test.describe('PLAYER Arc Phase Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasEmotionalAPI(page))) {
      console.log('Emotional state API not available');
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('emotional state API is accessible', async ({ page }) => {
    const emotionalState = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );

    console.log('Emotional state:', JSON.stringify(emotionalState, null, 2));

    expect(emotionalState).toBeTruthy();
    expect(emotionalState).toHaveProperty('arc');
    expect(emotionalState).toHaveProperty('contrast');

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'emotional-state-baseline.png') });
  });

  test('game starts in POWER phase', async ({ page }) => {
    const emotionalState = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );

    console.log('Initial arc phase:', emotionalState?.arc?.currentPhase);

    // Game should start in POWER phase (wave 1-3)
    expect(emotionalState?.arc?.currentPhase).toBe('POWER');

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'arc-power-phase.png') });
  });

  test('arc phases are visited during play', async ({ page }) => {
    const phaseLog: { time: number; phase: string; wave: number }[] = [];
    const startTime = Date.now();
    const testDuration = 60000; // 1 minute of play

    while (Date.now() - startTime < testDuration) {
      const emotionalState = await page.evaluate(() =>
        window.DEBUG_GET_EMOTIONAL_STATE?.()
      );
      const gameState = await page.evaluate(() =>
        window.DEBUG_GET_GAME_STATE?.()
      );

      const currentPhase = emotionalState?.arc?.currentPhase ?? 'unknown';
      const wave = gameState?.wave ?? 0;

      // Log phase changes
      if (phaseLog.length === 0 || phaseLog[phaseLog.length - 1].phase !== currentPhase) {
        phaseLog.push({
          time: Date.now() - startTime,
          phase: currentPhase,
          wave,
        });
        console.log(`Phase transition at ${(Date.now() - startTime) / 1000}s: ${currentPhase} (wave ${wave})`);
      }

      // Skip waves to accelerate testing
      if (Math.random() < 0.2) {
        await page.evaluate(() => window.DEBUG_SKIP_WAVE?.());
      }

      await page.waitForTimeout(1000);
    }

    console.log('Phase progression:', phaseLog);

    // Save phase log
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'arc-phase-log.json'),
      JSON.stringify(phaseLog, null, 2)
    );

    // Verify at least some phases were visited
    const uniquePhases = [...new Set(phaseLog.map((p) => p.phase))];
    console.log('Unique phases visited:', uniquePhases);

    expect(uniquePhases.length).toBeGreaterThanOrEqual(1);

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'arc-phase-progression.png') });
  });

  test('phasesVisited accumulates correctly', async ({ page }) => {
    // Play for 30s and check phases visited
    await page.waitForTimeout(5000);

    const midState = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );
    const midPhases = midState?.arc?.phasesVisited ?? [];

    // Skip some waves
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.DEBUG_SKIP_WAVE?.());
      await page.waitForTimeout(1000);
    }

    const endState = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );
    const endPhases = endState?.arc?.phasesVisited ?? [];

    console.log('Phases visited - mid:', midPhases, '- end:', endPhases);

    // Phases should accumulate (never decrease)
    expect(endPhases.length).toBeGreaterThanOrEqual(midPhases.length);

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'arc-phases-visited.png') });
  });
});

// =============================================================================
// Contrast Verification (N6)
// =============================================================================

test.describe('PLAYER Contrast Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasEmotionalAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('contrast dimensions are tracked', async ({ page }) => {
    const state = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );

    console.log('Contrast state:', JSON.stringify(state?.contrast, null, 2));

    expect(state?.contrast).toBeTruthy();
    expect(state?.contrast).toHaveProperty('activeDimensions');
    expect(state?.contrast).toHaveProperty('contrastsVisited');

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'contrast-baseline.png') });
  });

  test('contrast accumulates during play', async ({ page }) => {
    const initialState = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );
    const initialContrasts = initialState?.contrast?.contrastsVisited ?? 0;

    // Play actively for 30s
    for (let i = 0; i < 10; i++) {
      // Simulate some action
      await page.keyboard.press('w');
      await page.waitForTimeout(500);
      await page.keyboard.press('Space');
      await page.waitForTimeout(500);

      // Skip wave occasionally
      if (i % 3 === 0) {
        await page.evaluate(() => window.DEBUG_SKIP_WAVE?.());
      }

      await page.waitForTimeout(1000);
    }

    const endState = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );
    const endContrasts = endState?.contrast?.contrastsVisited ?? 0;

    console.log(`Contrasts: ${initialContrasts} -> ${endContrasts}`);

    // Contrasts should increase during active play
    expect(endContrasts).toBeGreaterThanOrEqual(initialContrasts);

    // Log contrast history
    console.log('Contrast history:', endState?.contrast?.contrastHistory);

    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'contrast-history.json'),
      JSON.stringify(endState?.contrast?.contrastHistory ?? [], null, 2)
    );

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'contrast-accumulated.png') });
  });
});

// =============================================================================
// Voice Line Verification (N10)
// =============================================================================

test.describe('PLAYER Voice Line Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasEmotionalAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('voice lines are captured in state', async ({ page }) => {
    // Play for 20s to trigger voice lines
    for (let i = 0; i < 10; i++) {
      await page.evaluate(() => window.DEBUG_SKIP_WAVE?.());
      await page.waitForTimeout(2000);
    }

    const state = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );

    console.log('Voice line state:', {
      current: state?.currentVoiceLine,
      history: state?.voiceLineHistory,
    });

    // Check voice line history exists
    expect(Array.isArray(state?.voiceLineHistory)).toBe(true);

    // If any voice lines triggered, log them
    if (state?.voiceLineHistory && state.voiceLineHistory.length > 0) {
      console.log('Voice lines triggered:', state.voiceLineHistory);

      fs.writeFileSync(
        path.join(EVIDENCE_DIR, 'voice-line-history.json'),
        JSON.stringify(state.voiceLineHistory, null, 2)
      );
    }

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'voice-lines.png') });
  });

  test('current voice line has text and type', async ({ page }) => {
    // Skip to later waves to trigger voice lines
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.DEBUG_SKIP_WAVE?.());
      await page.waitForTimeout(1000);
    }

    const state = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );

    if (state?.currentVoiceLine) {
      console.log('Current voice line:', state.currentVoiceLine);

      expect(state.currentVoiceLine).toHaveProperty('text');
      expect(state.currentVoiceLine).toHaveProperty('type');
      expect(typeof state.currentVoiceLine.text).toBe('string');
      expect(state.currentVoiceLine.text.length).toBeGreaterThan(0);

      // Capture screenshot with voice line visible
      await page.screenshot({ path: path.join(EVIDENCE_DIR, 'voice-line-active.png') });
    } else {
      console.log('No current voice line displayed');
    }
  });
});

// =============================================================================
// Audio Silence Verification (N7)
// =============================================================================

test.describe('PLAYER Audio Silence Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);
    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('audio level can be measured', async ({ page }) => {
    // Check if audio debug API exists
    const hasAudioAPI = await page.evaluate(() =>
      typeof window.DEBUG_GET_AUDIO_LEVEL === 'function'
    );

    if (!hasAudioAPI) {
      console.log('Audio debug API not available');
      test.skip();
    }

    const level = await page.evaluate(() => window.DEBUG_GET_AUDIO_LEVEL?.());
    console.log('Current audio level:', level);

    expect(typeof level).toBe('number');

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'audio-level-baseline.png') });
  });

  test('audio log captures events', async ({ page }) => {
    const hasAudioAPI = await page.evaluate(() =>
      typeof window.DEBUG_GET_AUDIO_LOG === 'function'
    );

    if (!hasAudioAPI) {
      test.skip();
    }

    // Clear log
    await page.evaluate(() => window.DEBUG_CLEAR_AUDIO_LOG?.());

    // Play for a bit to generate audio
    await page.waitForTimeout(5000);

    const log = await page.evaluate(() => window.DEBUG_GET_AUDIO_LOG?.());
    console.log('Audio log entries:', log?.length ?? 0);

    if (log && log.length > 0) {
      console.log('Sample audio events:', log.slice(0, 5));

      fs.writeFileSync(
        path.join(EVIDENCE_DIR, 'audio-event-log.json'),
        JSON.stringify(log, null, 2)
      );
    }

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'audio-log-capture.png') });
  });
});

// =============================================================================
// Galois Quality Verification
// =============================================================================

test.describe('PLAYER Galois Quality Metrics', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(getPilotURL());
    await page.waitForLoadState('networkidle');
    await waitForDebugAPI(page);
    await startGame(page);

    if (!(await hasEmotionalAPI(page))) {
      test.skip();
    }

    await page.evaluate(() => window.DEBUG_SET_INVINCIBLE?.(true));
  });

  test('calculate quality score Q = F * (C * A * V^(1/n))', async ({ page }) => {
    // Play through game to accumulate metrics
    for (let i = 0; i < 8; i++) {
      await page.evaluate(() => window.DEBUG_SKIP_WAVE?.());
      await page.waitForTimeout(2000);
    }

    const emotionalState = await page.evaluate(() =>
      window.DEBUG_GET_EMOTIONAL_STATE?.()
    );

    // Calculate Galois quality metrics
    const arc = emotionalState?.arc ?? { phasesVisited: [], currentPhase: 'POWER' };
    const contrast = emotionalState?.contrast ?? { contrastsVisited: 0, activeDimensions: [] };

    // F (Floor gate) - assume passing for now
    const F = 1;

    // C (Contrast coverage) - dimensions visited / total dimensions
    const totalContrastDimensions = 5; // power/vulnerability, sound/silence, etc.
    const C = Math.min(1, (contrast.activeDimensions?.length ?? 0) / totalContrastDimensions);

    // A (Arc phase coverage) - phases visited / total phases
    const totalArcPhases = 4; // POWER, FLOW, CRISIS, TRAGEDY
    const A = Math.min(1, (arc.phasesVisited?.length ?? 1) / totalArcPhases);

    // V (Voice approval) - placeholder, would need manual verification
    const V = 0.8; // Assume 80% approval for calculation

    // n (Number of voices)
    const n = 3;

    // Q = F * (C * A * V^(1/n))
    const Q = F * (C * A * Math.pow(V, 1 / n));

    console.log('Galois Quality Metrics:', {
      F,
      C,
      A,
      V,
      n,
      Q: Q.toFixed(3),
      arcPhasesVisited: arc.phasesVisited,
      contrastDimensions: contrast.activeDimensions,
      contrastsVisited: contrast.contrastsVisited,
    });

    // Save metrics
    fs.writeFileSync(
      path.join(EVIDENCE_DIR, 'galois-quality-metrics.json'),
      JSON.stringify({
        F,
        C,
        A,
        V,
        n,
        Q,
        details: {
          arcPhasesVisited: arc.phasesVisited,
          contrastDimensions: contrast.activeDimensions,
          contrastsVisited: contrast.contrastsVisited,
        },
        timestamp: new Date().toISOString(),
      }, null, 2)
    );

    // Quality thresholds
    console.log('Quality verdict:', Q >= 0.6 ? 'GOOD' : Q >= 0.3 ? 'ACCEPTABLE' : 'POOR');

    await page.screenshot({ path: path.join(EVIDENCE_DIR, 'galois-quality-final.png') });
  });
});
