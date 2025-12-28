/**
 * PLAYER Standalone Game Test
 *
 * Tests games running on their own dev servers (not integrated into pilots-web).
 *
 * Usage:
 *   GAME_URL="http://localhost:3022" pnpm exec playwright test e2e/standalone-game.spec.ts --headed
 */

import { test, expect, Page } from '@playwright/test';

const GAME_URL = process.env.GAME_URL || 'http://localhost:3022';
const PLAY_DURATION_MS = parseInt(process.env.PLAY_DURATION || '30000'); // 30 seconds default

test.describe('Standalone Game Play Session', () => {
  test('play and measure', async ({ page }) => {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`PLAY SESSION: ${GAME_URL}`);
    console.log(`Duration: ${PLAY_DURATION_MS / 1000}s`);
    console.log(`${'='.repeat(60)}\n`);

    // Navigate to game
    await page.goto(GAME_URL);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);

    // Take initial screenshot
    await page.screenshot({ path: 'test-results/game-start.png' });
    console.log('Screenshot: test-results/game-start.png');

    // Play the game with WASD
    const stats = await playGame(page, PLAY_DURATION_MS);

    console.log(`\nPlay Stats:`);
    console.log(`  Inputs sent: ${stats.inputCount}`);
    console.log(`  Duration: ${stats.duration}ms`);

    // Take final screenshot
    await page.screenshot({ path: 'test-results/game-end.png' });
    console.log('Screenshot: test-results/game-end.png');

    console.log(`\n${'='.repeat(60)}`);
    console.log(`PLAY SESSION COMPLETE`);
    console.log(`${'='.repeat(60)}\n`);
  });

  test('measure input latency', async ({ page }) => {
    await page.goto(GAME_URL);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(500);

    // Measure latency for key events
    const latencies: number[] = [];

    for (let i = 0; i < 20; i++) {
      const latency = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          const start = performance.now();
          const handler = () => {
            resolve(performance.now() - start);
            document.removeEventListener('keydown', handler);
          };
          document.addEventListener('keydown', handler);
          document.dispatchEvent(new KeyboardEvent('keydown', { key: 'w', bubbles: true }));
          setTimeout(() => resolve(-1), 100);
        });
      });

      if (latency > 0) latencies.push(latency);
      await page.waitForTimeout(50);
    }

    const avg = latencies.reduce((a, b) => a + b, 0) / latencies.length;
    const max = Math.max(...latencies);

    console.log(`\nInput Latency:`);
    console.log(`  Average: ${avg.toFixed(2)}ms`);
    console.log(`  Max: ${max.toFixed(2)}ms`);
    console.log(`  Fun Floor target: < 16ms`);
    console.log(`  Result: ${avg < 16 ? 'PASS' : 'FAIL'}`);

    expect(avg).toBeLessThan(16);
  });

  test('measure frame rate', async ({ page }) => {
    await page.goto(GAME_URL);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(500);

    // Measure frames for 5 seconds
    const frameData = await page.evaluate(async () => {
      const times: number[] = [];
      let lastTime = performance.now();
      const duration = 5000;
      const startTime = performance.now();

      return new Promise<{ times: number[] }>((resolve) => {
        function measure() {
          const now = performance.now();
          times.push(now - lastTime);
          lastTime = now;

          if (now - startTime < duration) {
            requestAnimationFrame(measure);
          } else {
            resolve({ times });
          }
        }
        requestAnimationFrame(measure);
      });
    });

    const avg = frameData.times.reduce((a, b) => a + b, 0) / frameData.times.length;
    const fps = 1000 / avg;
    const dropped = frameData.times.filter(t => t > 33.33).length;

    console.log(`\nFrame Rate:`);
    console.log(`  Average: ${fps.toFixed(1)} FPS`);
    console.log(`  Frame time: ${avg.toFixed(2)}ms`);
    console.log(`  Dropped frames: ${dropped}/${frameData.times.length}`);
    console.log(`  Fun Floor target: 60 FPS`);
    console.log(`  Result: ${fps >= 55 ? 'PASS' : 'FAIL'}`);

    expect(fps).toBeGreaterThan(55);
  });
});

async function playGame(page: Page, durationMs: number): Promise<{ inputCount: number; duration: number }> {
  const startTime = Date.now();
  const movementKeys = ['w', 'a', 's', 'd'];
  let inputCount = 0;

  // Send continuous movement inputs
  while (Date.now() - startTime < durationMs) {
    const key = movementKeys[Math.floor(Math.random() * movementKeys.length)];
    await page.keyboard.press(key);
    inputCount++;

    // Check for game over (press R to restart)
    const gameOver = await page.evaluate(() => {
      return document.body.innerText.includes('GAME OVER') ||
             document.body.innerText.includes('Press R');
    }).catch(() => false);

    if (gameOver) {
      console.log('Game over detected, restarting...');
      await page.keyboard.press('r');
      await page.waitForTimeout(500);
    }

    // Small delay between inputs
    await page.waitForTimeout(50 + Math.random() * 50);
  }

  return { inputCount, duration: Date.now() - startTime };
}
