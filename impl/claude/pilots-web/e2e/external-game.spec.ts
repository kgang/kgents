/**
 * PLAYER External Game Calibration
 *
 * This test enables the PLAYER orchestrator to play external games
 * for taste calibration when no build is ready.
 *
 * Usage:
 *   GAME_URL="https://example.io/game" npx playwright test e2e/external-game.spec.ts --headed
 *
 * The PLAYER uses this to:
 * 1. Calibrate taste against the state of the art
 * 2. Research what works in competitor games
 * 3. Build vocabulary for feedback
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Configuration
const GAME_URL = process.env.GAME_URL || 'https://poncle.itch.io/vampire-survivors-demo';
const PLAY_DURATION_MS = parseInt(process.env.PLAY_DURATION || '300000'); // 5 minutes default
const CULTURE_LOG_PATH = process.env.CULTURE_LOG || path.join(__dirname, '..', '.player.culture.log.md');

/**
 * Generic input simulation for various game types
 */
async function playGame(page: Page, durationMs: number, gameType: 'arcade' | 'clicker' | 'exploration' = 'arcade') {
  const startTime = Date.now();
  const observations: string[] = [];

  const inputPatterns = {
    arcade: {
      movement: ['w', 'a', 's', 'd', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'],
      action: ['Space', 'z', 'x', 'c'],
      ui: ['Enter', 'Escape', '1', '2', '3'],
    },
    clicker: {
      movement: [],
      action: ['Space'],
      ui: ['Enter', '1', '2', '3'],
    },
    exploration: {
      movement: ['w', 'a', 's', 'd'],
      action: ['e', 'Space'],
      ui: ['Tab', 'i', 'm'],
    },
  };

  const pattern = inputPatterns[gameType];

  while (Date.now() - startTime < durationMs) {
    // Random input based on game type
    const rand = Math.random();

    if (rand < 0.7 && pattern.movement.length > 0) {
      const key = pattern.movement[Math.floor(Math.random() * pattern.movement.length)];
      await page.keyboard.press(key);
    } else if (rand < 0.9) {
      const key = pattern.action[Math.floor(Math.random() * pattern.action.length)];
      await page.keyboard.press(key);
    } else {
      const key = pattern.ui[Math.floor(Math.random() * pattern.ui.length)];
      await page.keyboard.press(key);
    }

    // Also try clicking (for games with mouse input)
    if (gameType === 'clicker' || Math.random() < 0.1) {
      await page.mouse.click(
        200 + Math.random() * 600,
        200 + Math.random() * 400
      );
    }

    await page.waitForTimeout(50 + Math.random() * 100);
  }

  return observations;
}

test.describe('PLAYER Taste Calibration', () => {
  test('play external game for calibration', async ({ page }) => {
    console.log(`Calibrating taste with: ${GAME_URL}`);
    console.log(`Duration: ${PLAY_DURATION_MS / 1000}s`);

    // Navigate to external game
    await page.goto(GAME_URL, { waitUntil: 'networkidle', timeout: 60000 });

    // Take initial screenshot
    const screenshotDir = path.join(__dirname, '..', 'screenshots', 'calibration');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    await page.screenshot({
      path: path.join(screenshotDir, `calibration-start-${Date.now()}.png`),
    });

    // Wait for game to be interactive (click to focus)
    await page.click('body');
    await page.waitForTimeout(1000);

    // Detect game type based on URL or content
    const gameType: 'arcade' | 'clicker' | 'exploration' = GAME_URL.includes('survivor')
      ? 'arcade'
      : GAME_URL.includes('clicker')
        ? 'clicker'
        : 'exploration';

    console.log(`Detected game type: ${gameType}`);

    // Play the game
    await playGame(page, PLAY_DURATION_MS, gameType);

    // Take final screenshot
    await page.screenshot({
      path: path.join(screenshotDir, `calibration-end-${Date.now()}.png`),
    });

    console.log(`Calibration session complete`);
  });

  test('compare against known good games', async ({ page }) => {
    // List of games known for good game feel
    const referenceGames = [
      { url: 'https://js13kgames.com/entries/2023/30', name: 'JS13k Winner' },
      // Add more reference games as needed
    ];

    for (const game of referenceGames) {
      console.log(`Testing: ${game.name}`);

      try {
        await page.goto(game.url, { waitUntil: 'networkidle', timeout: 30000 });
        await page.click('body');
        await playGame(page, 30000, 'arcade'); // 30 seconds each
      } catch (e) {
        console.log(`Skipping ${game.name}: ${e}`);
      }
    }
  });
});

test.describe('PLAYER Research Tools', () => {
  test('analyze game page for patterns', async ({ page }) => {
    await page.goto(GAME_URL, { waitUntil: 'networkidle', timeout: 60000 });

    // Analyze the page structure
    const analysis = await page.evaluate(() => {
      const canvas = document.querySelector('canvas');
      const audio = document.querySelectorAll('audio');
      const buttons = document.querySelectorAll('button');
      const modals = document.querySelectorAll('[role="dialog"]');

      return {
        hasCanvas: !!canvas,
        canvasSize: canvas ? { width: canvas.width, height: canvas.height } : null,
        audioElements: audio.length,
        buttonCount: buttons.length,
        hasModals: modals.length > 0,
        hasServiceWorker: 'serviceWorker' in navigator,
      };
    });

    console.log('Page analysis:', analysis);

    // Log observations
    const observation = `
## ${new Date().toISOString()}: Analyzed ${GAME_URL}

### Technical
- Canvas: ${analysis.hasCanvas ? `${analysis.canvasSize?.width}x${analysis.canvasSize?.height}` : 'None'}
- Audio elements: ${analysis.audioElements}
- Buttons: ${analysis.buttonCount}
- Modals: ${analysis.hasModals ? 'Yes' : 'No'}
- PWA: ${analysis.hasServiceWorker ? 'Yes' : 'No'}

### Observations
[PLAYER to fill in after analysis]
`;

    if (fs.existsSync(path.dirname(CULTURE_LOG_PATH))) {
      fs.appendFileSync(CULTURE_LOG_PATH, observation);
    }
  });

  test('capture reference screenshots', async ({ page }) => {
    await page.goto(GAME_URL, { waitUntil: 'networkidle', timeout: 60000 });

    const screenshotDir = path.join(__dirname, '..', 'screenshots', 'reference');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    // Capture full page
    await page.screenshot({
      path: path.join(screenshotDir, `reference-fullpage-${Date.now()}.png`),
      fullPage: true,
    });

    // Capture viewport
    await page.screenshot({
      path: path.join(screenshotDir, `reference-viewport-${Date.now()}.png`),
    });

    console.log(`Reference screenshots saved to ${screenshotDir}`);
  });
});
