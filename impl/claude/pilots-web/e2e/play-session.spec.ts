/**
 * PLAYER Play Session Test
 *
 * This test enables the PLAYER orchestrator to actually play the game
 * via headless browser, capturing video and screenshots for feedback.
 *
 * Usage:
 *   npx playwright test e2e/play-session.spec.ts --headed --video=on
 *
 * The PLAYER orchestrator uses this to:
 * 1. Experience the build as a real player would
 * 2. Measure input latency and performance
 * 3. Capture evidence for feedback
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Configuration - adjust per pilot
const PILOT_NAME = process.env.PILOT_NAME || 'wasm-survivors';
const PLAY_DURATION_MS = parseInt(process.env.PLAY_DURATION || '180000'); // 3 minutes default
const SCREENSHOT_DIR = path.join(__dirname, '..', 'screenshots');

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

/**
 * Simulate random player inputs for arcade-style games
 */
async function simulateRandomInputs(page: Page, durationMs: number) {
  const startTime = Date.now();
  const movementKeys = ['w', 'a', 's', 'd', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'];
  const actionKeys = ['Space', '1', '2', '3', 'Enter'];

  let inputCount = 0;
  let modalCount = 0;

  while (Date.now() - startTime < durationMs) {
    // Random movement (80% of inputs)
    if (Math.random() < 0.8) {
      const key = movementKeys[Math.floor(Math.random() * movementKeys.length)];
      await page.keyboard.press(key);
    } else {
      // Occasional action key
      const key = actionKeys[Math.floor(Math.random() * actionKeys.length)];
      await page.keyboard.press(key);
    }
    inputCount++;

    // Check for modal dialogs (level-up, death, etc.)
    const modal = await page.locator('[role="dialog"], [data-testid="upgrade-picker"], [data-testid="death-screen"]').first();
    if (await modal.isVisible().catch(() => false)) {
      modalCount++;
      // Make a selection
      await page.keyboard.press('1');
      await page.waitForTimeout(100);
    }

    // Small delay between inputs (simulates human reaction time)
    await page.waitForTimeout(50 + Math.random() * 50);
  }

  return { inputCount, modalCount, durationMs: Date.now() - startTime };
}

test.describe('PLAYER Play Session', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the pilot
    await page.goto(`/pilots/${PILOT_NAME}`);
    // Wait for initial render
    await page.waitForLoadState('networkidle');
  });

  test('play one full run', async ({ page }) => {
    console.log(`Starting play session for ${PILOT_NAME}`);
    console.log(`Duration: ${PLAY_DURATION_MS / 1000}s`);

    // Take initial screenshot
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, `${PILOT_NAME}-start-${Date.now()}.png`),
    });

    // Start the game (most games use Space to start)
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    // Play the game
    const stats = await simulateRandomInputs(page, PLAY_DURATION_MS);

    console.log(`Play session complete:`);
    console.log(`  Inputs: ${stats.inputCount}`);
    console.log(`  Modals encountered: ${stats.modalCount}`);
    console.log(`  Duration: ${stats.durationMs}ms`);

    // Take final screenshot
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, `${PILOT_NAME}-end-${Date.now()}.png`),
    });

    // Log to coordination file if running in kgents context
    const feedbackPath = process.env.COORDINATION_DIR
      ? path.join(process.env.COORDINATION_DIR, '.player.feedback.md')
      : null;

    if (feedbackPath) {
      const feedback = `
## Play Session: ${new Date().toISOString()}

### Stats
- Pilot: ${PILOT_NAME}
- Duration: ${stats.durationMs / 1000}s
- Inputs: ${stats.inputCount}
- Modals: ${stats.modalCount}

### Evidence
- Start screenshot: ${PILOT_NAME}-start-*.png
- End screenshot: ${PILOT_NAME}-end-*.png
- Video: test-results/video.webm (if --video=on)

### Observations
[PLAYER to fill in after reviewing video]
`;
      fs.appendFileSync(feedbackPath, feedback);
    }
  });

  test('capture gameplay video', async ({ page }, testInfo) => {
    // This test specifically captures video for review
    // Run with: npx playwright test --grep "capture gameplay video" --video=on

    await page.keyboard.press('Space');

    // Play for configured duration
    await simulateRandomInputs(page, PLAY_DURATION_MS);

    // Video will be automatically saved by Playwright
    console.log(`Video will be saved to: ${testInfo.outputDir}`);
  });

  test('capture key moments', async ({ page }) => {
    // This test captures screenshots at key moments

    await page.keyboard.press('Space');
    await page.waitForTimeout(1000);

    // Capture at regular intervals
    const intervalMs = 10000; // Every 10 seconds
    const intervals = Math.floor(PLAY_DURATION_MS / intervalMs);

    for (let i = 0; i < intervals; i++) {
      await simulateRandomInputs(page, intervalMs);
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${PILOT_NAME}-moment-${i}-${Date.now()}.png`),
      });
      console.log(`Captured moment ${i + 1}/${intervals}`);
    }
  });
});

test.describe('PLAYER Metrics', () => {
  test('measure input latency', async ({ page }) => {
    await page.goto(`/pilots/${PILOT_NAME}`);
    await page.waitForLoadState('networkidle');

    // Start the game
    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    // Measure latency for multiple inputs
    const latencies: number[] = [];

    for (let i = 0; i < 10; i++) {
      const latency = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          const start = performance.now();

          const handler = () => {
            resolve(performance.now() - start);
            document.removeEventListener('keydown', handler);
          };

          document.addEventListener('keydown', handler);
          document.dispatchEvent(new KeyboardEvent('keydown', { key: 'w', bubbles: true }));
        });
      });

      latencies.push(latency);
      await page.waitForTimeout(100);
    }

    const avgLatency = latencies.reduce((a, b) => a + b, 0) / latencies.length;
    const maxLatency = Math.max(...latencies);

    console.log(`Input latency (avg): ${avgLatency.toFixed(2)}ms`);
    console.log(`Input latency (max): ${maxLatency.toFixed(2)}ms`);

    // 60fps budget is 16.67ms
    expect(avgLatency).toBeLessThan(16);
    expect(maxLatency).toBeLessThan(32); // Allow some spikes
  });

  test('measure frame rate', async ({ page }) => {
    await page.goto(`/pilots/${PILOT_NAME}`);
    await page.waitForLoadState('networkidle');

    await page.keyboard.press('Space');
    await page.waitForTimeout(500);

    // Measure frame rate over 5 seconds
    const frameData = await page.evaluate(async () => {
      const frames: number[] = [];
      let lastTime = performance.now();

      return new Promise<{ fps: number; minFps: number; dropped: number }>((resolve) => {
        let frameCount = 0;
        const targetDuration = 5000;
        const startTime = performance.now();

        function measureFrame() {
          const now = performance.now();
          const delta = now - lastTime;
          frames.push(delta);
          lastTime = now;
          frameCount++;

          if (now - startTime < targetDuration) {
            requestAnimationFrame(measureFrame);
          } else {
            const avgDelta = frames.reduce((a, b) => a + b, 0) / frames.length;
            const fps = 1000 / avgDelta;
            const minFps = 1000 / Math.max(...frames);
            const dropped = frames.filter((d) => d > 33).length; // >30fps threshold

            resolve({ fps, minFps, dropped });
          }
        }

        requestAnimationFrame(measureFrame);
      });
    });

    console.log(`Average FPS: ${frameData.fps.toFixed(1)}`);
    console.log(`Minimum FPS: ${frameData.minFps.toFixed(1)}`);
    console.log(`Dropped frames: ${frameData.dropped}`);

    expect(frameData.fps).toBeGreaterThan(55); // Target 60fps
    expect(frameData.dropped).toBeLessThan(10); // Allow some drops
  });
});
